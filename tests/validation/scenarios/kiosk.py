"""Kiosk (``/kiosk``): the routing wizard applies routing and the output options as chosen.

Browser client only (the ``kiosk_route`` intent drives web/kiosk.html). Before
WP-E1 (UI-23) Apply sent ``{mute}`` / ``{enable}`` where the hub reads
``muted`` / ``enabled`` (default true), so every target was muted and got ARC
on whatever the checkboxes said, and the HDR "Auto" value (0) was rejected.

Output option values are the hub's API values; the device codes the simulator
stores differ for HDR and scaler (``src/device_codes.py``): HDR API 3 "auto" =
device 2, scaler API 4 "auto" = device 3.
"""

from tools.validate.model import ClientState, CommandSent, Device, DeviceUnchanged, Scenario, act

from ._paths import CONTROL, HUB_CORE, KIOSK, OUTPUTS, STATUS

SCENARIOS = [
    Scenario(
        id="kiosk.route_all_apply",
        title="Kiosk: route input 5 to all outputs with the wizard's defaults (audio on, ARC off, auto modes)",
        features=("F-KIO-003",),
        clients=("browser",),
        writes=("routing", "outputs"),
        # output 1 muted and ARC on before: Apply with both boxes unchecked turns both off
        sim_state={"outputs": {"0": {"audio_mute": 1, "arc": 1}}},
        action=act("kiosk_route", input=5, output="all", mute=False, arc=False),
        expect=(
            *(Device(f"outputs[{i}].source", equals=5) for i in range(8)),
            Device("outputs[0].audio_mute", equals=0),
            Device("outputs[0].arc", equals=0),
            Device("outputs[7].hdcp", equals=3),
            Device("outputs[7].hdr", equals=2),
            Device("outputs[7].scaler", equals=3),
            CommandSent("set output audio mute", {"mute": [1, 0]}, count=1),
            CommandSent("set arc", {"arc": [1, 0]}, count=1),
            CommandSent("set hdr conversion", {"hdr": [8, 2]}, count=1),
            ClientState("toast.success", equals="Routing and output parameters applied"),
        ),
        observe=("Do all displays show the source on input 5, with sound?",),
        covers=(*HUB_CORE, *CONTROL, *OUTPUTS, *STATUS, *KIOSK),
        notes="UI-23: Apply muted every output and turned ARC on (wrong body keys), and HDR 'Auto' (0) was rejected.",
    ),
    Scenario(
        id="kiosk.route_one_muted",
        title="Kiosk: route input 3 to output 3 with 'Mute output audio' checked; only output 3 changes",
        features=("F-KIO-002",),
        clients=("browser",),
        writes=("routing", "outputs"),
        action=act("kiosk_route", input=3, output=3, mute=True, arc=False),
        expect=(
            Device("outputs[2].source", equals=3),
            Device("outputs[2].audio_mute", equals=1),
            CommandSent("set output audio mute", {"mute": [3, 1]}, count=1),
            DeviceUnchanged(allow=("outputs[2].*", "routing")),
            ClientState("toast.success", equals="Routing and output parameters applied"),
        ),
        observe=("Does the display on output 3 show input 3 with the sound muted?",),
        covers=(*HUB_CORE, *CONTROL, *OUTPUTS, *STATUS, *KIOSK),
        notes="UI-23: 'Mute output audio' unchecked muted the output anyway; checked was the only way to get what you asked for.",
    ),
]
