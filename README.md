# WhatsApp audio mixer for PipeWire

Experimental command-line tool (v0.1.0) for sending microphone audio and playing media into a
WhatsApp call on a Linux desktop using PipeWire. It creates a temporary virtual
source and updates audio links while it runs. No Python packages are required.

## Why this exists

During a WhatsApp video call in Firefox on Ubuntu, the author could speak to a
friend while screen sharing, but the friend could not hear YouTube videos or
Instagram Reels. A Bluetooth audio device was connected. The author reports
that this helper made both voice and media audible.

This closely matches Firefox's known missing screen-capture audio feature:
[Mozilla issue 1541425](https://bugzilla.mozilla.org/show_bug.cgi?id=1541425).
It is not evidence of a Bluetooth or Linux kernel defect. The workaround sends
media through the call's microphone input; it does not add native screen-share
audio support to Firefox. Call noise suppression may affect music quality.

## Run

Requires Python 3, a running PipeWire user session, and `pw-dump`, `pw-link`, and
`pw-loopback` on PATH. Run as your normal desktop user, not with sudo:

```sh
python3 mixer.py --check
python3 mixer.py
```

Or install the command in a virtual environment:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/whatsapp-audio --check
.venv/bin/whatsapp-audio
```

`--help` lists options; `--version` prints the release version. `--check` reads
the PipeWire graph without changing routing. Startup checks required commands
and rejects duplicate mixers. No root access or permanent audio configuration
changes are needed. Run tests with `python3 -m unittest -v`.

Start a WhatsApp call and play the media you want to share. The terminal reports
the detected calls, selected microphone, and included media. `Calls=0` means no
WhatsApp recording stream was recognized. The helper looks for `whatsapp` in
the stream's media or application name; clients that expose generic names may
not work.

Press Ctrl+C to stop. The helper attempts to remove its links, reconnect detected
WhatsApp inputs to the physical microphone, and stop the virtual source. Abrupt
termination cannot guarantee cleanup. Run only one copy at a time.

## What gets shared

While a recognized call is active, the helper includes the selected physical
microphone and eligible playback streams from other apps, including generic
browser streams. This is not a per-tab or per-app sharing selector: unrelated
audio may be transmitted too. Close or pause audio you do not want to share.

Recognized WhatsApp playback, streams marked communication/phone/notification,
and certain speech-dispatcher/ZOOM streams are excluded. These are name/metadata
heuristics, not a guarantee against call echo or unwanted audio. Use headphones
and test with another participant before relying on it.

The default physical microphone is preferred, with fallback device selection.
Audio is mixed to a mono virtual source. There are no independent volume controls
or limiter; adjust application and microphone levels if the mix distorts.

## Status

This is an existing personal prototype, documented for evaluation. The inspected
environment reports Ubuntu 24.04.2 LTS and PipeWire libraries 1.0.5. This does not
establish compatibility with all Ubuntu installations, browsers, or WhatsApp
clients. No live call or cross-device test was performed during this review.

The script does not save recordings, but terminal output can contain media titles.
Review logs before sharing them. A public release still needs live-call testing,
an explicit license, and a publishing destination. The author has confirmed a
successful personal call test; wider compatibility has not been established.

This helper shares eligible audio whenever a detected call is active, even if
screen sharing is stopped. Stop the helper with Ctrl+C to stop this routing.

See [REPORTING.md](REPORTING.md) for the upstream assessment.

## Our plan for Firefox

Firefox's native screen-share audio limitation is tracked in
[Mozilla issue 1541425](https://bugzilla.mozilla.org/show_bug.cgi?id=1541425).
We are publishing this workaround now. Work on a native Firefox solution and
further live testing will happen later, when the author resumes that effort.
See [ROADMAP.md](ROADMAP.md). No Firefox fix has been implemented or accepted.
