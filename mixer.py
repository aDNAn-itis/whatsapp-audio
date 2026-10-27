#!/usr/bin/env python3
"""Temporary WhatsApp-only mic/media mix. Stop restores the physical microphone."""
import argparse
import fcntl
import json
import os
import shutil
import sys
import signal
import subprocess as sp
import time

running = True
owned = set()
call_stream_serials = set()

def run(*args):
    return sp.run(args, stdout=sp.PIPE, stderr=sp.PIPE, text=True, timeout=5)

def snapshot():
    # pw-dump can append change batches while its initial snapshot is emitted.
    result = run('pw-dump')
    if result.returncode:
        raise RuntimeError('Cannot read PipeWire: ' + result.stderr.strip())
    raw = result.stdout
    decoder = json.JSONDecoder()
    objects = {}
    def merge(old, new):
        for key, value in new.items():
            if isinstance(value, dict) and isinstance(old.get(key), dict):
                merge(old[key], value)
            else:
                old[key] = value
    while raw.strip():
        batch, end = decoder.raw_decode(raw.lstrip())
        raw = raw.lstrip()[end:]
        for obj in batch:
            ident = obj['id']
            if 'info' in obj and obj['info'] is None:
                objects.pop(ident, None)
            elif ident in objects:
                merge(objects[ident], obj)
            else:
                objects[ident] = obj
    return list(objects.values())

def props(obj):
    return obj.get('info', {}).get('props', obj.get('props', {}))

def stopped(*_):
    global running
    running = False

def ports_for(objects, node, direction):
    return [o for o in objects if o['type'].endswith(':Port') and
            str(props(o).get('node.id')) == str(node['id']) and
            props(o).get('port.direction') == direction]

def pairs(objects, source, dest):
    result = set()
    for out in ports_for(objects, source, 'out'):
        oc = props(out).get('audio.channel', '')
        for inp in ports_for(objects, dest, 'in'):
            ic = props(inp).get('audio.channel', '')
            if oc == ic or oc == 'MONO' or ic == 'MONO':
                result.add((out['id'], inp['id']))
    return result

def is_call(p):
    return 'whatsapp' in (p.get('media.name', '') + ' ' + p.get('application.name', '')).lower()

def get_state():
    objects = snapshot()
    nodes = [o for o in objects if o['type'].endswith(':Node')]
    links = {(int(props(o)['link.output.port']), int(props(o)['link.input.port'])): o['id']
             for o in objects if o['type'].endswith(':Link')}
    calls = [n for n in nodes if props(n).get('media.class') == 'Stream/Input/Audio' and is_call(props(n)) and not props(n).get('node.name', '').startswith('whatsapp_mix')]
    physical = [n for n in nodes if props(n).get('media.class') == 'Audio/Source' and
                props(n).get('node.name', '').startswith(('alsa_input.', 'bluez_input.'))]
    default_name = None
    for o in objects:
        if o['type'].endswith(':Metadata') and props(o).get('metadata.name') == 'default':
            for m in o.get('metadata', []):
                if m.get('key') == 'default.audio.source':
                    v = m.get('value', {})
                    default_name = (json.loads(v) if isinstance(v, str) else v).get('name')
    mic = next((n for n in physical if props(n).get('node.name') == default_name), None)
    if mic is None:
        mic = next((n for n in physical if 'Digital Microphone' in props(n).get('node.description', '')), None)
    if mic is None and physical:
        mic = physical[0]
    return objects, nodes, links, calls, mic

def link(pair):
    result = run('pw-link', str(pair[0]), str(pair[1]))
    if result.returncode:
        print('Link failed:', pair, result.stderr.strip(), flush=True)
    return result.returncode == 0

def unlink(pair):
    run('pw-link', '-d', str(pair[0]), str(pair[1]))

def mix():
    global running
    running = True
    owned.clear()
    call_stream_serials.clear()
    signal.signal(signal.SIGTERM, stopped)
    signal.signal(signal.SIGINT, stopped)
    mixer = sp.Popen([
        'pw-loopback', '--name=whatsapp-mix', '-c', '2', '-m', '[ FL FR ]',
        '--capture-props=node.name=whatsapp_mix_input node.description="WhatsApp Mix Bus" node.autoconnect=false node.passive=false audio.position=[FL FR]',
        '--playback-props=media.class=Audio/Source node.name=whatsapp_mix node.description="WhatsApp Mix" node.virtual=true node.autoconnect=false audio.position=[MONO] priority.session=0'
    ])
    last_summary = None
    try:
        while running:
            if mixer.poll() is not None:
                raise RuntimeError('Audio mixer exited')
            try:
                objects, nodes, links, calls, mic = get_state()
                bus = next((n for n in nodes if props(n).get('node.name') == 'whatsapp_mix_input'), None)
                source = next((n for n in nodes if props(n).get('node.name') == 'whatsapp_mix'), None)
                if bus is None or source is None:
                    time.sleep(.5)
                    continue
                desired = set()
                media = []
                live_serials = {props(n).get('object.serial') for n in nodes} - {None}
                call_stream_serials.intersection_update(live_serials)
                call_stream_serials.update(props(n).get('object.serial') for n in nodes
                                           if is_call(props(n)) and props(n).get('object.serial') is not None)
                if calls:
                    if mic:
                        desired |= pairs(objects, mic, bus)
                    for n in nodes:
                        p = props(n)
                        # Reels may have no tab title: include generic browser media.
                        # Remember identified call streams even if their titles change.
                        if p.get('media.class') != 'Stream/Output/Audio' or is_call(p) or p.get('object.serial') in call_stream_serials:
                            continue
                        if p.get('media.role', '').lower() in ('communication', 'phone', 'notification'):
                            continue
                        if p.get('application.name', '').startswith(('speech-dispatcher', 'ZOOM')):
                            continue
                        desired |= pairs(objects, n, bus)
                        media.append(p.get('media.name', str(n['id'])))
                    for call in calls:
                        desired |= pairs(objects, source, call)
                        # Remove stale direct links from the previous helper and mic.
                        call_ports = {p['id'] for p in ports_for(objects, call, 'in')}
                        for pair in list(links):
                            if pair[1] in call_ports and pair not in desired:
                                unlink(pair)
                for pair in owned - desired:
                    if pair in links:
                        unlink(pair)
                owned &= desired
                for pair in desired - set(links):
                    if link(pair):
                        owned.add(pair)
                summary = (len(calls), props(mic).get('node.description') if mic else None, tuple(media))
                if summary != last_summary:
                    print('Calls=%s; microphone=%s; media=%s' % summary, flush=True)
                    last_summary = summary
            except (ValueError, KeyError, sp.TimeoutExpired) as exc:
                print('Retry:', exc, flush=True)
            time.sleep(1)
    finally:
        # Restore only WhatsApp input streams; leave other applications untouched.
        try:
            objects, nodes, links, calls, mic = get_state()
            for pair in owned:
                if pair in links:
                    unlink(pair)
            if mic:
                for call in calls:
                    for pair in pairs(objects, mic, call):
                        link(pair)
        finally:
            mixer.terminate()
            try:
                mixer.wait(timeout=5)
            except sp.TimeoutExpired:
                mixer.kill()
                mixer.wait()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Mix microphone and playing media into WhatsApp calls using PipeWire.",
        epilog="Shares eligible playback during calls, even without screen sharing. Ctrl+C stops.")
    parser.add_argument('--version', action='version', version='whatsapp-audio 0.1.0')
    parser.add_argument('--check', action='store_true',
                        help='check dependencies and PipeWire connection without changing audio')
    args = parser.parse_args(argv)
    missing = [name for name in ('pw-dump', 'pw-link', 'pw-loopback')
               if shutil.which(name) is None]
    if missing:
        print('Missing commands: ' + ', '.join(missing) +
              '. Install your distribution’s PipeWire tools.', file=sys.stderr)
        return 1
    try:
        objects, nodes, links, calls, mic = get_state()
        if args.check:
            print('PipeWire connection OK; calls=%d; physical microphone=%s' %
                  (len(calls), props(mic).get('node.description', 'available') if mic else 'not found'))
            return 0
        runtime = os.environ.get('XDG_RUNTIME_DIR')
        if not runtime or not os.path.isdir(runtime) or os.stat(runtime).st_uid != os.getuid():
            raise RuntimeError('Run from your desktop session with XDG_RUNTIME_DIR set.')
        with open(os.path.join(runtime, 'whatsapp-audio.lock'), 'w') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError('Another copy of whatsapp-audio is already running.')
            if any(props(n).get('node.name') in ('whatsapp_mix', 'whatsapp_mix_input') for n in nodes):
                raise RuntimeError('An existing WhatsApp mixer was found. Stop it before starting another.')
            print('Sharing microphone + eligible playback during WhatsApp calls. Ctrl+C stops.', flush=True)
            mix()
    except (OSError, RuntimeError, ValueError, KeyError, sp.TimeoutExpired) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
