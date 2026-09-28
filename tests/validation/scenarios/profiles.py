"""Profiles: recall applies routing, output settings and the power-on macro; PIN protection; CEC auto-resolve.

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
    Hub,
    NoCommand,
    Response,
    Scenario,
    act,
)

from ._paths import HUB_CORE, PROFILES

# movie_night's CEC config as the fixture stores it (restored after auto-resolve rewrites it)
_MOVIE_NIGHT_CEC = {
    "nav_targets": ["input:2"], "playback_targets": ["input:2"], "volume_targets": ["output:2"],
    "power_on_targets": ["input:2", "output:1"], "power_off_targets": ["input:2", "output:1"], "auto_resolved": False,
}

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
        sim_state={"outputs": {"0": {"hdcp": 1, "hdr": 2}}},
        action=act("profile_recall", profile_id="movie_night"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("outputs[1].source", equals=2),
            Device("outputs[1].audio_mute", equals=1, timeout=2),
            # the profile's API HDR 1 (passthrough) is device code 0 (HIL-02)
            Device("outputs[0].hdr", equals=0, timeout=1),
            Device("outputs[0].hdcp", equals=3, timeout=1),
            CommandSent("set output audio mute", {"mute": [2, 1]}, count=1),
            CommandSent("set hdr conversion", {"hdr": [1, 0]}, count=1),
            CommandSent("tx hdcp", {"hdcp": [1, 3]}, count=1),
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
            # displays use the output CEC table: power on = index 0 (BE-14)
            CommandSent("cec command", {"object": 1, "port": [1, 0, 0, 0, 0, 0, 0, 0], "index": 0}, count=1),
            CommandSent("cec command", {"object": 0, "port": [0, 1, 0, 0, 0, 0, 0, 0], "index": 1}, count=1),
            Response(json={"data": {"power_on_macro": {"success": True}}}),
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
    Scenario(
        id="profiles.recall_rejected",
        title="The matrix refuses every write: recall answers 500 and names the failed outputs",
        kind="failure",
        features=("F-DOM-002",),
        targets=("sim",),
        faults={"reject_writes": True},
        action=act("profile_recall", profile_id="game_day"),
        expect=(
            Response(status=500, json={"success": False, "data": {"failed_outputs": [1, 2, 3], "applied": []}}),
            Device("outputs[0].source", equals=2),
            DeviceUnchanged(),
        ),
        covers=(*HUB_CORE, *PROFILES),
        notes="API-08: recall used to answer 200 success:true when every output failed.",
    ),
    Scenario(
        id="profiles.cec_auto_resolve",
        title="Auto-resolve a profile's CEC targets from its routing and the matrix's output status",
        features=("F-DOM-007",),
        action=act("request", method="POST", path="/api/scene/movie_night/cec/auto-resolve"),
        expect=(
            Response(status=200, json={"success": True, "data": {
                "auto_resolved": True,
                "nav_targets": ["input_2"],
                "playback_targets": ["input_2"],
                # output 2 is the audio-only soundbar (scaler device code 4) in the seed state
                "volume_targets": ["output_2"],
                "power_on_targets": ["input_2", "output_1", "output_2"],
                "power_off_targets": ["output_1", "output_2"],
            }}),
            Hub("/api/profile/movie_night/cec", "data.cec_config.volume_targets", equals=["output_2"]),
            NoCommand("*"),
            DeviceUnchanged(),
        ),
        cleanup=(act("request", method="PUT", path="/api/profile/movie_night/cec", json=_MOVIE_NIGHT_CEC),),
        covers=(*HUB_CORE, *PROFILES, "src/rest_api/scenes.py", "src/cec_resolver.py", "src/cec_commands.py"),
        notes="API-23: the endpoint called the resolver with the wrong arguments and always answered 500.",
    ),
]
