# Testing v0.1.0

## Checked on 27 October 2026

- Four automated tests passed: snapshot updates/deletions, failed graph reads,
  read-only check behavior, and missing dependency handling.
- Wheel build passed; isolated virtual-environment installation and installed
  command help/version checks passed.
- Live `--check` could not connect to PipeWire in the restricted agent environment:
  `can't connect: Operation not permitted`. This is not a successful live test.
- The author previously reported successful calls using the original script.
  The packaged version still needs the desktop test below.

## Desktop call test

Run in a normal terminal in the logged-in Ubuntu desktop, without sudo:

```sh
cd /home/adnan/Desktop/whatsapp-audio
python3 mixer.py --check
python3 mixer.py
```

1. Connect the Bluetooth device and start a WhatsApp video call in Firefox.
2. Confirm the terminal detects a call (`Calls=1`, or another positive count).
3. Share the screen and play YouTube. Ask the participant to confirm both your
   speech and video audio are audible.
4. Repeat with Instagram Reels. Check for distortion and whether the participant
   hears their own voice echoed back.
5. Stop playback; confirm your microphone still works.
6. Press Ctrl+C; confirm voice still works and media is no longer sent through
   this helper. Verify the virtual WhatsApp Mix source disappears.

The helper includes eligible playback from other apps, so pause unrelated audio.
It does not detect screen-sharing state: stopping screen sharing alone does not
stop media mixing. Run only one instance. Record any failing step and terminal
output (remove private media titles before sharing logs).

Live results: deferred. The author clarified that the success report referred
to remembered use of the original helper, not a new test of this release.
