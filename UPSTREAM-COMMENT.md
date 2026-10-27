# Draft comment for Mozilla issue 1541425

Destination: https://bugzilla.mozilla.org/show_bug.cgi?id=1541425

Not submitted. The text below describes the author's reported experience;
the research assistant did not independently reproduce the call.

---

An affected use case: sharing YouTube videos and Instagram Reels with a friend
during WhatsApp video calls in Firefox on Ubuntu.

My microphone audio was audible to the other participant, but the video/Reels
audio was not audible while I shared my screen. A Bluetooth audio device was
connected. I expected to be able to share media audio along with my voice.

I worked around this using a Python helper with PipeWire's pw-loopback and
pw-link. It creates a virtual microphone, mixes physical microphone and playback
streams into it, and routes that source to WhatsApp's recording stream. With
this workaround, my friend could hear the media as well as my voice.

This appears consistent with the missing getDisplayMedia audio functionality
tracked here. I have not inspected WhatsApp's capture request or run an isolated
getDisplayMedia reproduction, so I am reporting the affected workflow rather
than claiming a new root cause or regression.

The inspected system is Ubuntu 24.04.2 with PipeWire libraries 1.0.5. The installed
Firefox Snap currently reports version 158.0; the version at the time of the
original incident was not recorded. The selected screen-share surface and any
audio-sharing control state were not recorded either.

An optional, explicit way to share media audio while retaining microphone audio
would remove the need for manually managing a virtual microphone for this use
case.
