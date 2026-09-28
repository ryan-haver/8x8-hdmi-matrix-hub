"""Kiosk (``/kiosk``): the routing wizard and protected profiles.

Browser client only (``kiosk_route`` and ``profile_recall`` with ``via="kiosk"``
drive web/kiosk.html).

* Routing wizard: before WP-E1 (UI-23) Apply sent ``{mute}`` / ``{enable}``
  where the hub reads ``muted`` / ``enabled`` (default true), so every target
  was muted and got ARC on, and it always wrote HDCP/HDR/scaler with the
  wizard's defaults (HDR "Auto" was 0 and rejected). Owner decision 2026-09-27
  (UI-46): Apply changes the routing; an output option is sent only when the
  user changed its control, so route-all leaves the audio-only soundbar
  (output 2, scaler device code 4) alone.
* Protected profiles: owner decision 2026-09-27 (UI-48): the kiosk asks for the
  passcode on its PIN pad and retries with it; a wrong one is "Invalid passcode".
"""

from tools.validate.model import ClientState, CommandSent, Device, DeviceUnchanged, NoCommand, Response, Scenario, act

from ._paths import CONTROL, HUB_CORE, KIOSK, OUTPUTS, PROFILES, STATUS

#: The output setting commands the wizard can send (HIL-09 command set).
_OUTPUT_SETTINGS = ("tx hdcp", "set hdr conversion", "set video scaler", "set arc", "set output audio mute")

SCENARIOS = [
    Scenario(
        id="kiosk.route_all_apply",
        title="Kiosk: route input 5 to all outputs without touching the options; only the routing changes",
        features=("F-KIO-003",),
        clients=("browser",),
        writes=("routing",),
        # output 1 muted, output 2 (soundbar, audio-only scaler) with ARC on: both must stay as they are
        sim_state={"outputs": {"0": {"audio_mute": 1}, "1": {"arc": 1}}},
        action=act("kiosk_route", input=5, output="all", mute=False, arc=False),
        expect=(
            *(Device(f"outputs[{i}].source", equals=5) for i in range(8)),
            Device("outputs[1].scaler", equals=4),
            Device("outputs[1].arc", equals=1),
            Device("outputs[0].audio_mute", equals=1),
            DeviceUnchanged(allow=("outputs[*].source", "routing")),
            *(NoCommand(c) for c in _OUTPUT_SETTINGS),
            ClientState("toast.success", equals="Routing applied"),
        ),
        observe=("Do all displays show the source on input 5, and does the soundbar still play audio?",),
        covers=(*HUB_CORE, *CONTROL, *OUTPUTS, *STATUS, *KIOSK),
        notes="UI-23: Apply muted every output and turned ARC on (wrong body keys). UI-46: it also rewrote "
              "HDCP/HDR/scaler with its defaults on every target (the soundbar lost its audio-only scaler).",
    ),
    Scenario(
        id="kiosk.route_one_muted",
        title="Kiosk: route input 3 to output 3 with 'Mute output audio' checked; only that is sent",
        features=("F-KIO-002",),
        clients=("browser",),
        writes=("routing", "outputs"),
        action=act("kiosk_route", input=3, output=3, mute=True, arc=False),
        expect=(
            Device("outputs[2].source", equals=3),
            Device("outputs[2].audio_mute", equals=1),
            CommandSent("set output audio mute", {"mute": [3, 1]}, count=1),
            *(NoCommand(c) for c in _OUTPUT_SETTINGS if c != "set output audio mute"),
            DeviceUnchanged(allow=("outputs[2].source", "outputs[2].audio_mute", "routing")),
            ClientState("toast.success", equals="Routing and output parameters applied"),
        ),
        observe=("Does the display on output 3 show input 3 with the sound muted?",),
        covers=(*HUB_CORE, *CONTROL, *OUTPUTS, *STATUS, *KIOSK),
        notes="UI-23: 'Mute output audio' unchecked muted the output anyway. UI-46: only changed options are sent.",
    ),
    Scenario(
        id="kiosk.profile_with_passcode",
        title="Kiosk: run the protected profile 'Kids Gaming' by entering its passcode on the PIN pad",
        features=("F-KIO-008", "F-DOM-005"),
        clients=("browser",),
        writes=("routing", "outputs"),
        sim_state={"outputs": {"0": {"source": 1}}},
        action=act("profile_recall", profile_id="kids_gaming", name="Kids Gaming", passcode="1234", via="kiosk"),
        expect=(
            Response(status=200),
            Device("outputs[0].source", equals=6),
            CommandSent("video switch", {"source": [1, 6]}, count=1),
            DeviceUnchanged(allow=("outputs[0].*", "routing")),
            ClientState("toast.success", equals="Profile activated"),
        ),
        observe=("Does the display on output 1 now show the source on input 6?",),
        covers=(*HUB_CORE, *PROFILES, "src/password.py", *KIOSK),
        notes="UI-48: the kiosk had no passcode prompt (it showed 'Failed: null').",
    ),
    Scenario(
        id="kiosk.profile_wrong_passcode",
        title="Kiosk: a wrong passcode applies nothing and the kiosk says 'Invalid passcode'",
        kind="failure",
        features=("F-KIO-008", "F-DOM-005"),
        clients=("browser",),
        action=act("profile_recall", profile_id="kids_gaming", name="Kids Gaming", passcode="9999", via="kiosk"),
        expect=(
            Response(status=403),
            NoCommand("*"),
            DeviceUnchanged(),
            ClientState("toast.error", equals="Invalid passcode"),
        ),
        covers=(*HUB_CORE, *PROFILES, "src/password.py", *KIOSK),
    ),
]
