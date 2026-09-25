"""Profiles: recall applies routing, output settings and the power-on macro; PIN protection.

Profiles come from tests/e2e/fixtures/data/profiles.json (copied into every
validation hub): ``game_day`` routes input 5 to outputs 1-3 and mutes output 3;
``movie_night`` routes input 2 to outputs 1-2, sets HDR 1 / HDCP 3 on output 1,
mutes output 2 and runs the ``macro_tv_on`` power-on macro (CEC power on to
output 1, then input 2); ``kids_gaming`` is protected with passcode 1234.
"""

from tools.validate.model import (
    CommandSent,
    Device,
    DeviceUnchanged,
    NoCommand,
    Response,
    Scenario,
    act,
)

from ._paths import HUB_CORE, PROFILES

SCENARIOS = [
    Scenario(
        id="profiles.recall_routing",
        title="Recall profile 'Game Day': outputs 1-3 show input 5",
        features=("F-DOM-002",),
        writes=("routing", "outputs"),
        action=act("profile_recall", profile_id="game_day"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("outputs[0].source", equals=5),
            Device("outputs[1].source", equals=5),
            Device("outputs[2].source", equals=5),
            DeviceUnchanged(allow=("outputs[0].*", "outputs[1].*", "outputs[2].*", "routing")),
            CommandSent("video switch", {"source": [3, 5]}, count=1),
        ),
        observe=("Do the displays on outputs 1-3 now show the source on input 5?",),
        covers=(*HUB_CORE, *PROFILES),
    ),
    Scenario(
        id="profiles.recall_output_settings",
        title="Recall profile 'Movie Night': HDR, HDCP and audio mute are applied",
        features=("F-DOM-003",),
        writes=("routing", "outputs"),
        sim_state={"outputs": {"0": {"hdcp": 1}}},
        action=act("profile_recall", profile_id="movie_night"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("outputs[1].source", equals=2),
            Device("outputs[1].audio_mute", equals=1, timeout=2, finding="VAL-01"),
            Device("outputs[0].hdr", equals=1, timeout=1, finding="VAL-01"),
            Device("outputs[0].hdcp", equals=3, timeout=1, finding="VAL-01"),
            CommandSent("set output mute", {"output": 2, "mute": 1}, finding="VAL-01"),
        ),
        observe=("Is output 2 muted and does output 1 show HDR content as SDR/HDR per the profile?",),
        covers=(*HUB_CORE, *PROFILES),
    ),
    Scenario(
        id="profiles.recall_power_macro",
        title="Recall profile 'Movie Night': its power-on macro sends CEC power-on to the TV and Apple TV",
        features=("F-DOM-004",),
        writes=("routing", "outputs", "physical"),
        action=act("profile_recall", profile_id="movie_night"),
        expect=(
            Response(status=200, json={"success": True}),
            CommandSent("cec command", {"object": 1, "port": [1, 0, 0, 0, 0, 0, 0, 0], "index": 1},
                        finding="VAL-02"),
            CommandSent("cec command", {"object": 0, "port": [0, 1, 0, 0, 0, 0, 0, 0], "index": 1},
                        finding="VAL-02"),
            Response(json={"data": {"power_on_macro": {"success": True}}}, finding="VAL-02"),
        ),
        observe=("Did the TV on output 1 and the Apple TV on input 2 power on?",),
        covers=(*HUB_CORE, *PROFILES, "src/cec_macros.py"),
    ),
    Scenario(
        id="profiles.recall_needs_passcode",
        title="A passcode-protected profile is not applied without its passcode",
        kind="failure",
        features=("F-DOM-005",),
        action=act("profile_recall", profile_id="kids_gaming"),
        expect=(
            Response(status=403, json={"success": False, "data": {"error": "passcode_required"}}),
            NoCommand("*"),
            DeviceUnchanged(),
        ),
        covers=(*HUB_CORE, *PROFILES, "src/password.py"),
    ),
]
