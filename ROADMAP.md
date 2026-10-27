# Roadmap

## Available now: PipeWire workaround

Version 0.1.0 packages the author's working microphone/media mixer as a command
line tool. It includes a read-only connection check, dependency errors, duplicate
instance protection, and normal shutdown cleanup. Broader call/device testing
is still needed.

## Planned: work on the Firefox limitation

The current scope is publishing the existing PipeWire workaround. Native Firefox
implementation and further live testing are deferred until the author resumes
that work; there is no scheduled implementation date.

The existing upstream tracker is
[Mozilla issue 1541425 — Implement audio capture for getDisplayMedia](https://bugzilla.mozilla.org/show_bug.cgi?id=1541425).
Mozilla classifies this as an enhancement. This tool is a workaround, not a
Firefox patch, and no upstream implementation or acceptance date is promised.

Possible future steps, when Firefox work resumes:

1. Add the documented WhatsApp/YouTube/Reels use case to the existing issue.
2. Review Firefox capture code and ongoing work with maintainers.
3. Agree on a small Linux audio-capture prototype with explicit user selection.
4. Test microphone/media separation, permission handling, and echo prevention.
5. Submit an upstream patch if the design is accepted for implementation.

## Tool improvements

- Explicit playback-source selection rather than automatic broad mixing.
- Independent microphone/media volume controls.
- Wider tests across Bluetooth devices, browsers, and Linux distributions.
- Choose a license and publish the repository before calling it an open-source release.
