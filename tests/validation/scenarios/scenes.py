"""Scenes (``/api/v2/scenes``): run profile, macro and shortcut steps; overrides; passcodes; honest results.

Scenes come from tests/e2e/fixtures/data/scenes.json:

* ``scene_movienight01``: macro ``macro_tv_on`` (CEC power on to output 1, then
  input 2), profile ``movie_night`` (input 2 -> outputs 1-2, HDR 1 / HDCP 3 on
  output 1, mutes output 2, quick-access macro ``macro_tv_on``) with an
  override that leaves output 2's mute alone, then shortcut ``preset_recall_2``
  (preset 2 = input 5 everywhere).
* ``scene_kidslocked`` (passcode 1234): profile ``kids_gaming`` (input 6 ->
  output 1), then shortcut ``route_all_to_output`` with input 6 / output 1.
* ``scene_goodnight01``: shortcut ``mute_all_audio``, then macro
  ``macro_all_off`` (CEC power off to inputs 1, 2, 6 and outputs 1, 2).

Scenarios that need another step list edit ``scene_goodnight01`` in ``setup``
and put it back in ``cleanup`` (a created scene gets a random id).

CEC tables (BE-14): displays (object 1) 0 = on, 1 = off; sources (object 0) 1 = on, 2 = off.
"""

from tools.validate.model import (
    ClientState,
    CommandGap,
    CommandSent,
    Device,
    DeviceUnchanged,
    Hub,
    NoCommand,
    Response,
    Scenario,
    WsEvent,
    act,
)

from ._paths import HUB_CORE, SCENES, WEB_CORE, WEB_RUN


def _port(n: int) -> list[int]:
    return [1 if i == n else 0 for i in range(1, 9)]


def _execute(scene_id: str, **body):
    return act("request", method="POST", path=f"/api/v2/scenes/{scene_id}/execute", json=body or None)


def _edit_goodnight(**body):
    return act("request", method="PUT", path="/api/v2/scenes/scene_goodnight01", json=body)


#: scene_goodnight01 as the fixture stores it
_RESTORE_GOODNIGHT = _edit_goodnight(
    name="Good Night",
    steps=[{"type": "system_action", "id": "mute_all_audio"}, {"type": "macro", "id": "macro_all_off"}],
    overrides={},
)

SCENARIOS = [
    Scenario(
        id="scenes.run_profile_macro_preset",
        title="Run 'Movie Night': one explicit macro, profile state with an override, then preset recall",
        features=("F-DOM-011", "F-DOM-012", "F-DOM-014"),
        clients=("api", "browser"),
        writes=("routing", "outputs", "physical"),
        sim_state={"outputs": {"0": {"hdr": 2, "hdcp": 1}}},
        action=act("scene_run", scene_id="scene_movienight01"),
        expect=(
            Response(status=200, json={"success": True, "data": {"steps_completed": 3, "total_steps": 3}}),
            # profile step: HDR 1 (API) = device code 0, HDCP 3 on output 1
            Device("outputs[0].hdr", equals=0),
            Device("outputs[0].hdcp", equals=3),
            CommandSent("video switch", {"source": [1, 2]}, count=1),
            CommandSent("video switch", {"source": [2, 2]}, count=1),
            # the scene overrides output 2's mute: left as it was, never sent
            Device("outputs[1].audio_mute", equals=0),
            CommandSent("set output audio mute", {"mute": [2, 1]}, count=0),
            # DI-11: only the explicit scene macro sends CEC, never the profile's macros
            CommandSent("cec command", {"object": 1, "port": _port(1), "index": 0}, count=1),
            CommandSent("cec command", {"object": 0, "port": _port(2), "index": 1}, count=1),
            # last step: preset 2
            CommandSent("preset set", {"index": 2}, count=1),
            Device("routing", equals=[5] * 8),
            DeviceUnchanged(allow=("outputs[*].source", "routing", "outputs[0].hdr", "outputs[0].hdcp")),
            Hub("/api/v2/scenes/scene_movienight01/history", "data.execution_history[-1].status", equals="success"),
            Hub("/api/profile/movie_night/execution-log", "data.log[-1].scene_id", equals="scene_movienight01"),
        ),
        observe=("Did the TV and the Apple TV power on, and do the displays now show preset 2 (input 5)?",),
        covers=(*HUB_CORE, *SCENES),
        notes="DI-11/VAL-07: the profile applies recall's state but runs no macros; CEC is sent exactly once.",
    ),
    Scenario(
        id="scenes.run_protected",
        title="Run the protected scene 'Kids' with its passcode: profile and route-shortcut steps apply",
        features=("F-DOM-011", "F-DOM-015"),
        # browser: its dashboard card, answering the passcode prompt (UI-01)
        client_features={"browser": ("F-UI-008",)},
        clients=("api", "browser"),
        writes=("routing", "outputs"),
        sim_state={"outputs": {"0": {"source": 1}}},
        action=act("scene_run", scene_id="scene_kidslocked", passcode="1234"),
        expect=(
            Response(status=200, json={"success": True, "data": {"steps_completed": 2, "total_steps": 2}}),
            Device("outputs[0].source", equals=6),
            CommandSent("video switch", {"source": [1, 6]}, count=2),
            DeviceUnchanged(allow=("outputs[0].source", "routing")),
            ClientState("toast.success", equals="Scene executed", clients=("browser",)),
        ),
        observe=("Does the display on output 1 now show the source on input 6?",),
        covers=(*HUB_CORE, *SCENES, "src/password.py", *WEB_CORE, *WEB_RUN),
        notes="API-01: both steps called OreiMatrix.switch(), which does not exist.",
    ),
    Scenario(
        id="scenes.run_needs_passcode",
        title="A protected scene does nothing without its passcode",
        kind="failure",
        features=("F-DOM-015",),
        action=_execute("scene_kidslocked"),
        expect=(
            Response(status=403, json={"success": False, "data": {"error": "passcode_required"}}),
            NoCommand("*"),
            DeviceUnchanged(),
        ),
        covers=(*HUB_CORE, *SCENES, "src/password.py"),
    ),
    Scenario(
        id="scenes.run_shortcut_and_macro",
        title="Run 'Good Night': mute every output, then the CEC power-off macro",
        features=("F-DOM-012",),
        writes=("outputs", "physical"),
        action=_execute("scene_goodnight01"),
        expect=(
            Response(status=200, json={"success": True, "data": {"steps_completed": 2}}),
            Device("outputs[0].audio_mute", equals=1),
            Device("outputs[7].audio_mute", equals=1),
            CommandSent("set output audio mute", count=8),
            CommandSent("cec command", {"object": 0, "port": _port(1), "index": 2}, count=1),
            CommandSent("cec command", {"object": 0, "port": _port(2), "index": 2}, count=1),
            CommandSent("cec command", {"object": 0, "port": _port(6), "index": 2}, count=1),
            CommandSent("cec command", {"object": 1, "port": _port(1), "index": 1}, count=1),
            CommandSent("cec command", {"object": 1, "port": _port(2), "index": 1}, count=1),
            DeviceUnchanged(allow=("outputs[*].audio_mute", "outputs[*].cec_enabled", "inputs[*].cec_enabled")),
        ),
        observe=("Are all outputs muted, and did the TV, soundbar and sources on inputs 1, 2, 6 power off?",),
        covers=(*HUB_CORE, *SCENES),
        notes="VAL-02: macro steps failed with 'CEC sender not configured' in modular mode.",
    ),
    Scenario(
        id="scenes.override_leaves_setting",
        title="A scene override leaves that setting alone (input on output 1, mute on output 3)",
        features=("F-DOM-014",),
        writes=("routing", "outputs"),
        sim_state={"outputs": {"0": {"source": 7}}},
        setup=(_edit_goodnight(
            steps=[{"type": "profile", "id": "game_day"}],
            overrides={"game_day": {"1": {"input": True}, "3": {"audio_mute": True}}},
        ),),
        action=_execute("scene_goodnight01"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("outputs[0].source", equals=7),
            Device("outputs[1].source", equals=5),
            Device("outputs[2].source", equals=5),
            Device("outputs[2].audio_mute", equals=0),
            CommandSent("video switch", {"source": [1, 5]}, count=0),
            CommandSent("video switch", {"source": [1, 1]}, count=0),
            CommandSent("set output audio mute", {"mute": [3, 1]}, count=0),
            DeviceUnchanged(allow=("outputs[1].source", "outputs[2].source", "routing")),
        ),
        cleanup=(_RESTORE_GOODNIGHT,),
        observe=("Does output 1 still show what it showed before, while outputs 2 and 3 now show input 5?",),
        covers=(*HUB_CORE, *SCENES),
        notes="API-04: an input override routed Input 1 (overrides reset settings to defaults).",
    ),
    Scenario(
        id="scenes.edit_with_profile_step",
        title="Edit a scene to run a profile (profiles exist on the hub); the new steps are saved",
        features=("F-DOM-010",),
        action=_edit_goodnight(steps=[{"type": "profile", "id": "game_day"}, {"type": "macro", "id": "macro_all_off"}]),
        expect=(
            Response(status=200, json={"success": True}),
            Hub("/api/v2/scenes/scene_goodnight01", "data.scene.steps[0].id", equals="game_day"),
            NoCommand("*"),
            DeviceUnchanged(),
        ),
        cleanup=(_RESTORE_GOODNIGHT,),
        covers=(*HUB_CORE, *SCENES),
        notes="API-05: every create/update with profile steps answered 500 ('dict' object has no attribute 'id').",
    ),
    Scenario(
        id="scenes.invalid_edit_rejected",
        title="An invalid scene edit is rejected and leaves the scene as it was",
        kind="failure",
        features=("F-DOM-010",),
        action=_edit_goodnight(name="", icon="X"),
        expect=(
            Response(status=400, json={"success": False}),
            Hub("/api/v2/scenes/scene_goodnight01", "data.scene.name", equals="Good Night"),
            Hub("/api/v2/scenes/scene_goodnight01", "data.scene.icon", equals="🌙"),
            NoCommand("*"),
        ),
        covers=(*HUB_CORE, *SCENES),
        notes="API-13: update_scene changed the scene in memory before validating it.",
    ),
    Scenario(
        id="scenes.partial_failure",
        title="A scene with a failing step answers 207 with per-step results and records the error",
        kind="failure",
        features=("F-DOM-011", "F-DOM-017"),
        # browser: Settings drawer, Scenes tab; the partial run is reported (VAL-11: it showed nothing)
        client_features={"api": ("F-API-041",), "browser": ("F-UI-027",)},
        clients=("api", "browser"),
        writes=("outputs",),
        setup=(_edit_goodnight(
            steps=[{"type": "system_action", "id": "mute_all_audio"}, {"type": "profile", "id": "no_such_profile"}],
        ),),
        action=act("scene_run", scene_id="scene_goodnight01"),
        expect=(
            Response(status=207, json={"success": False, "data": {"steps_completed": 1, "total_steps": 2}}),
            ClientState("toast.warning", equals='"Good Night" ran partly: 1 of 2 steps succeeded', clients=("browser",)),
            Device("outputs[0].audio_mute", equals=1),
            WsEvent("scene_execution_error", {"scene_id": "scene_goodnight01", "steps_completed": 1}),
            Hub("/api/v2/scenes/scene_goodnight01/history", "data.execution_history[-1].status", equals="error"),
            DeviceUnchanged(allow=("outputs[*].audio_mute",)),
        ),
        cleanup=(_RESTORE_GOODNIGHT,),
        covers=(*HUB_CORE, *SCENES, "src/rest_api/websocket.py", *WEB_CORE, *WEB_RUN),
        notes="API-08: a scene whose steps failed answered 200 success:true. VAL-11: the UI showed nothing for a 207.",
    ),
    Scenario(
        id="scenes.run_rejected",
        title="The matrix refuses every write: the scene answers 500 and nothing changed",
        kind="failure",
        features=("F-DOM-012",),
        targets=("sim",),
        faults={"reject_writes": True},
        action=_execute("scene_goodnight01"),
        expect=(
            Response(status=500, json={"success": False, "data": {"steps_completed": 0}}),
            DeviceUnchanged(),
        ),
        covers=(*HUB_CORE, *SCENES),
    ),
    Scenario(
        id="scenes.disabled_output_state",
        title="Scene profile step routes a disabled output and turns its stream off, exactly like recall",
        features=("F-DOM-011",), clients=("api", "browser"),
        writes=("routing", "outputs"),
        setup=(_edit_goodnight(steps=[{"type": "profile", "id": "retro_hour"}], overrides={}),),
        action=act("scene_run", scene_id="scene_goodnight01"),
        expect=(Response(status=200), Device("outputs[1].source", equals=7), Device("outputs[1].stream", equals=0),
                CommandSent("tx stream", {"out": [2, 0]}, count=1), NoCommand("cec command")),
        cleanup=(_RESTORE_GOODNIGHT,), covers=(*HUB_CORE, *SCENES, *WEB_CORE, *WEB_RUN),
        observe=("Does output 1 show input 7 while output 2's video stream is off?",),
    ),
    Scenario(
        id="scenes.enabled_override",
        title="A stream-state override leaves a disabled output on while still applying its routing",
        features=("F-DOM-014",), clients=("api", "browser"),
        writes=("routing", "outputs"),
        setup=(_edit_goodnight(steps=[{"type": "profile", "id": "retro_hour"}],
                              overrides={"retro_hour": {"2": {"enabled": True}}}),),
        action=act("scene_run", scene_id="scene_goodnight01"),
        expect=(Response(status=200), Device("outputs[1].source", equals=7), Device("outputs[1].stream", equals=1),
                CommandSent("tx stream", {"out": [2, 0]}, count=0)),
        cleanup=(_RESTORE_GOODNIGHT,), covers=(*HUB_CORE, *SCENES, *WEB_CORE, *WEB_RUN),
        observe=("Do both outputs 1 and 2 show input 7, with output 2's stream still on?",),
    ),
    Scenario(
        id="scenes.wait_between_actions",
        title="A half-second scene wait separates beep-off and a routing action on the device",
        features=("F-DOM-013",), clients=("api", "browser"), writes=("system", "routing"),
        setup=(_edit_goodnight(steps=[{"type": "system_action", "id": "beep_off"},
                                     {"type": "wait", "params": {"seconds": 0.5}},
                                     {"type": "system_action", "id": "route_all_to_output",
                                      "params": {"input": 6, "output": 1}}]),),
        action=act("scene_run", scene_id="scene_goodnight01"),
        expect=(Response(status=200), Device("outputs[0].source", equals=6), Device("system.beep", equals=0),
                CommandGap("set beep", "video switch", 0.5)),
        cleanup=(_RESTORE_GOODNIGHT,), covers=(*HUB_CORE, *SCENES, *WEB_CORE, *WEB_RUN),
        observe=("Did routing change to input 6 after the beep setting and half-second wait?",),
    ),
    Scenario(
        id="scenes.wait_edit",
        title="Add and save a half-second wait using the scene editor",
        features=("F-DOM-013",), clients=("api", "browser"),
        setup=(_edit_goodnight(steps=[], overrides={}),),
        action=act("scene_wait_edit", scene_id="scene_goodnight01", seconds=0.5,
                   steps=[{"type": "wait", "id": "", "params": {"seconds": 0.5}}]),
        expect=(Response(status=200), Hub("/api/v2/scenes/scene_goodnight01", "data.scene.steps",
                 equals=[{"type": "wait", "id": "", "params": {"seconds": 0.5}}]), NoCommand("*")),
        cleanup=(_RESTORE_GOODNIGHT,),
        covers=(*HUB_CORE, *SCENES, *WEB_CORE, "web/js/components/scene-editor.js", *WEB_RUN),
    ),
    Scenario(
        id="scenes.conflicts_visible",
        title="The scene editor displays the actual differing profile settings, including mute defaults",
        features=("F-DOM-016",), clients=("api", "browser"),
        setup=(_edit_goodnight(steps=[{"type": "profile", "id": "movie_night"},
                                     {"type": "profile", "id": "game_day"}], overrides={}),),
        action=act("scene_conflicts", scene_id="scene_goodnight01"),
        expect=(Response(status=200, json={"data": {"has_conflicts": True}}),
                ClientState("scene.conflict_count", equals=3, clients=("browser",)),
                ClientState("scene.values", equals=["= 2", "= 5", "= 2", "= 5", "= true", "= false"],
                            clients=("browser",)), NoCommand("*"), DeviceUnchanged()),
        cleanup=(_RESTORE_GOODNIGHT,),
        covers=(*HUB_CORE, *SCENES, *WEB_CORE, "web/js/components/scene-editor.js", *WEB_RUN),
    ),
    Scenario(
        id="scenes.macro_continues_after_refusal",
        title="A scene macro with continue_on_error sends the later CEC commands after one refused target",
        features=("F-DOM-012", "F-DOM-020"), clients=("api", "browser"), targets=("sim",),
        faults={"reject_writes": True, "reject_write_count": 1, "comheads": ["cec command"]},
        setup=(_edit_goodnight(steps=[{"type": "macro", "id": "macro_all_off"}]),),
        action=act("scene_run", scene_id="scene_goodnight01"),
        expect=(Response(status=500), CommandSent("cec command", count=5),
                CommandSent("cec command", {"object": 1, "port": _port(2), "index": 1}, count=1),
                Hub("/api/v2/scenes/scene_goodnight01/history", "data.execution_history[-1].status", equals="error")),
        cleanup=(_RESTORE_GOODNIGHT,), covers=(*HUB_CORE, *SCENES, *WEB_CORE, *WEB_RUN),
    ),
    Scenario(
        id="scenes.macro_stops_after_refusal",
        title="A scene macro with the default stop policy sends no later command after a refusal",
        features=("F-DOM-020",), clients=("api", "browser"), targets=("sim",),
        faults={"reject_writes": True, "reject_write_count": 1, "comheads": ["cec command"]},
        setup=(_edit_goodnight(steps=[{"type": "macro", "id": "macro_tv_on"}]),),
        action=act("scene_run", scene_id="scene_goodnight01"),
        expect=(Response(status=500), CommandSent("cec command", count=1),
                CommandSent("cec command", {"object": 0, "port": _port(2), "index": 1}, count=0)),
        cleanup=(_RESTORE_GOODNIGHT,), covers=(*HUB_CORE, *SCENES, *WEB_CORE, *WEB_RUN),
    ),
    Scenario(
        id="scenes.run_unknown",
        title="Running a scene that does not exist is a 404, not a 200",
        kind="failure",
        features=("F-DOM-011",),
        action=_execute("scene_nope"),
        expect=(
            Response(status=404, json={"success": False}),
            NoCommand("*"),
            DeviceUnchanged(),
        ),
        covers=(*HUB_CORE, *SCENES),
    ),
]

# API-29: a scene's profile step applies the same scaler/ARC state as recall (DI-11);
# an override of either leaves it alone, and differing values are reported as conflicts.
_SA = {"id": "validation_scene_sa", "name": "Scene SA", "icon": "S",
       "outputs": {"1": {"input": 3, "scaler_mode": 5, "arc": True}, "2": {"input": 4, "scaler_mode": 1}}}
_SB = {"id": "validation_scene_sb", "name": "Scene SB", "icon": "S",
       "outputs": {"1": {"input": 3, "scaler_mode": 4, "arc": False}}}
_DEL_SA = act("request", method="DELETE", path="/api/profile/validation_scene_sa")
_DEL_SB = act("request", method="DELETE", path="/api/profile/validation_scene_sb")
SCENARIOS += [
    Scenario(
        id="scenes.profile_step_scaler_arc",
        title="A scene's profile step applies the profile's scaler and ARC like recall (API-29)",
        features=("F-DOM-011",),
        writes=("routing", "outputs"),
        sim_state={"outputs": {"0": {"scaler": 0, "arc": 0}, "1": {"scaler": 3}}},
        setup=(act("request", method="POST", path="/api/profile", json=_SA),
               _edit_goodnight(steps=[{"type": "profile", "id": "validation_scene_sa"}], overrides={})),
        action=_execute("scene_goodnight01"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("outputs[0].scaler", equals=4, timeout=2),  # API 5 (audio only) -> device 4
            Device("outputs[0].arc", equals=1, timeout=2),
            Device("outputs[1].scaler", equals=0, timeout=2),  # API 1 (passthrough) -> device 0
            CommandSent("set video scaler", {"scaler": [1, 4]}, count=1),
            CommandSent("set video scaler", {"scaler": [2, 0]}, count=1),
            CommandSent("set arc", {"arc": [1, 1]}, count=1),
            CommandSent("set arc", {"arc": [2, 0]}, count=0),  # output 2 has no saved ARC
        ),
        cleanup=(_RESTORE_GOODNIGHT, _DEL_SA),
        observe=("Does output 1 now pass audio only with ARC on, and output 2 pass video through?",),
        covers=(*HUB_CORE, *SCENES),
    ),
    Scenario(
        id="scenes.override_leaves_scaler_arc",
        title="Scene overrides of scaler and ARC leave both alone on that output (API-29)",
        features=("F-DOM-014",),
        writes=("routing", "outputs"),
        sim_state={"outputs": {"0": {"scaler": 2, "arc": 0}, "1": {"scaler": 3}}},
        setup=(act("request", method="POST", path="/api/profile", json=_SA),
               _edit_goodnight(steps=[{"type": "profile", "id": "validation_scene_sa"}],
                               overrides={"validation_scene_sa": {"1": {"scaler": True, "arc": True}}})),
        action=_execute("scene_goodnight01"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("outputs[1].scaler", equals=0, timeout=2),
            Device("outputs[0].scaler", equals=2),
            Device("outputs[0].arc", equals=0),
            CommandSent("set video scaler", {"scaler": [1, 4]}, count=0),
            CommandSent("set arc", {"arc": [1, 1]}, count=0),
        ),
        cleanup=(_RESTORE_GOODNIGHT, _DEL_SA),
        observe=("Does output 1 keep its video mode and ARC setting while output 2 passes video through?",),
        covers=(*HUB_CORE, *SCENES),
    ),
    Scenario(
        id="scenes.conflicts_scaler_arc",
        title="Scene validation reports differing scaler and ARC values across profile steps (API-29)",
        features=("F-DOM-016",),
        setup=(act("request", method="POST", path="/api/profile", json=_SA),
               act("request", method="POST", path="/api/profile", json=_SB),
               _edit_goodnight(steps=[{"type": "profile", "id": "validation_scene_sa"},
                                      {"type": "profile", "id": "validation_scene_sb"}], overrides={})),
        action=act("request", method="POST", path="/api/v2/scenes/scene_goodnight01/validate"),
        expect=(
            Response(status=200, json={"success": True, "data": {"conflicts": [
                {"output": 1, "setting": "scaler", "profiles": [
                    {"id": "validation_scene_sa", "name": "Scene SA", "value": 5},
                    {"id": "validation_scene_sb", "name": "Scene SB", "value": 4}]},
                {"output": 1, "setting": "arc", "profiles": [
                    {"id": "validation_scene_sa", "name": "Scene SA", "value": True},
                    {"id": "validation_scene_sb", "name": "Scene SB", "value": False}]},
            ]}}),
            NoCommand("*"),
            DeviceUnchanged(),
        ),
        cleanup=(_RESTORE_GOODNIGHT, _DEL_SA, _DEL_SB),
        covers=(*HUB_CORE, *SCENES),
    ),
]
