# Upstream assessment

## Research update — 27 October 2026

Conclusion after user clarification: the user reports Firefox on Ubuntu,
WhatsApp video calling with screen sharing, working voice audio, and absent
YouTube/Reels audio at the remote end. A Bluetooth device was connected. The
user confirms that this project's mixer resolved the media-audio problem.
This closely matches Mozilla's existing screen-capture audio enhancement;
there is no evidence of a kernel or Bluetooth defect. The precise API request
was not inspected, so attribution is a strong match rather than an isolated
technical reproduction. See UPSTREAM-COMMENT.md for a ready-to-post account.

Primary-source findings:

1. Mozilla bug 1541425, "Implement audio capture for getDisplayMedia", is open
   and classified as an enhancement. Its original reproduction uses Firefox on
   Ubuntu and receives no audio track from a screen-capture request. If this is
   the user's Firefox screen-sharing case, prefer the existing issue rather
   than creating a duplicate:
   https://bugzilla.mozilla.org/show_bug.cgi?id=1541425
2. MDN documents that display-capture audio depends on browser support and the
   selected surface. Asking for audio does not guarantee an audio track:
   https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getDisplayMedia
3. Google's current Meet help distinguishes Chrome-tab sharing from window or
   desktop sharing. It lists macOS 14.2 or Windows 11 and newer as requirements
   for the latter's audio sharing. This establishes a related platform
   limitation in Meet, not proof of WhatsApp's exact behavior:
   https://support.google.com/meet/answer/16581830?hl=en-GB
4. WhatsApp announced screen sharing with audio on 13 June 2024, and its newer
   web-calling announcement includes screen sharing. Neither announcement
   establishes audio sharing support for every Linux/browser/surface combination:
   https://blog.whatsapp.com/better-calling-across-desktop-and-mobile
   https://blog.whatsapp.com/introducing-web-calling-on-whatsapp-plus-more-new-updates
5. XDG Desktop Portal has an existing Audio portal design discussion. It concerns
   broader permissions and integration; it is not a confirmed match for this
   incident or a reason to file a new portal defect:
   https://github.com/flatpak/xdg-desktop-portal/discussions/1142

Chromium's historical system-audio feature request also surfaced in search:
https://issues.chromium.org/issues/40606364
Direct access returned a sign-in page, so its current status was not verified.
Do not infer current Linux support from old comments in that issue.

### Recommended destination

- Ordinary microphone call, without explicit media sharing: absence of a direct
  desktop-audio feed is not by itself a defect. Request optional media sharing
  from the calling app if needed.
- Firefox screen-share audio: evaluate against Mozilla 1541425 above; subscribe
  or add a new, useful reproduction if applicable.
- Audio sharing explicitly enabled, but failing only in WhatsApp: contact
  WhatsApp with client/version, selected surface, and reproduction. Official
  support offers a Web and Desktop category:
  https://www.whatsapp.com/contact/?subject=messenger
- Failure in a minimal browser capture example as well as WhatsApp: investigate
  that browser's tracker before attributing it to Ubuntu/PipeWire.
- PipeWire or kernel report: only after an independent reproduction isolates
  failure in that component. The present script is insufficient evidence.

### Minimal comparison to resolve ownership

With this mixer stopped, record whether the ordinary microphone works. In a
video call, try sharing a browser tab with audio enabled, then a window or whole
screen if available. Record missing controls separately from enabled controls
that produce silence. Repeat the same surface in a browser screen-capture demo
or another calling app. Record browser version, installation type, session type
(Wayland/X11), and the result for each case. Do not label unperformed tests as
failures. These tests require an interactive desktop and call participant and
were not performed during this research.

Suggested report title, after verification:
"[Browser/version] on Ubuntu: [tab/window/desktop] sharing has no audio in WhatsApp"

Suggested report content:
- Environment: Ubuntu 24.04.2; PipeWire libraries 1.0.5 (locally inspected).
- Browser/client and version: [required].
- Share surface and audio checkbox state: [required].
- Reproduction and observed/expected results: [required].
- Ordinary mic and comparison-app results: [required].
- Workaround: temporary PipeWire virtual source mixing microphone and playback;
  whether it succeeds in this exact reproduction: [confirm].
- Question: is this combination supported, a known limitation, or a regression?

No upstream submission was made.

The code implements microphone-plus-media routing for WhatsApp. That alone is
not evidence of a Linux kernel defect, nor of a problem affecting every Ubuntu
user. PipeWire explicitly supports virtual sources using its loopback module:
https://docs.pipewire.org/page_module_loopback.html

Working hypothesis, consistent with the clarified symptom: this helper
addresses a missing or inconvenient application audio-sharing workflow.
Publishing a small optional utility is a plausible route. An application feature
request is appropriate if the client does not offer the desired sharing control.

## Evidence needed before filing a defect

- Exact symptom and expected behavior, including whether an explicit audio-share
  feature was enabled or whether ordinary microphone input was being used.
- WhatsApp client or browser name/version and installation method.
- Minimal reproduction without this helper, and whether other calling apps fail.
- Ubuntu, PipeWire, WirePlumber, and kernel versions; audio-device details only
  if relevant to the failure.
- Whether a manually configured virtual source also fails, plus the exact error.

If a reproducible failure is isolated to PipeWire, its official site links its
issue tracker: https://www.pipewire.org/

For a defect in an Ubuntu package, follow Ubuntu's reporting instructions and
use `ubuntu-bug <affected-package>` after identifying the component:
https://help.ubuntu.com/community/ReportingBugs

No report has been submitted. The user's account is sufficient for an impact
comment on the existing Mozilla issue, but does not establish a new defect.
The older script and current
script also differ in JSON snapshot parsing and unnamed browser-stream handling;
those changes are clues, not independently reproduced upstream bugs.
