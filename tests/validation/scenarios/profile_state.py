"""CEC configuration, scene-produced profile history and capture-current state.

Disposable simulator/data only. Run with OREI_STATUS_CACHE_TTL=0 to make device
read faults observable and CEC capability decisions use current metadata.
"""

from tools.validate.model import (
    CommandSent,
    Device,
    DeviceUnchanged,
    Hub,
    NoCommand,
    NoProtocolWarnings,
    Response,
    Scenario,
    act,
)

from ._paths import HUB_CORE, PROFILES, SCENES

_COVERS = tuple(dict.fromkeys((*HUB_CORE, *PROFILES, *SCENES, "src/rest_api/scenes.py",
                             "src/cec_resolver.py", "src/cec_commands.py", "src/device_codes.py",
                             "src/_file_io.py", "tests/validation/scenarios/profile_state.py")))
_ID = "validation_state"
_PROFILE = f"/api/profile/{_ID}"
_BASE = {"id": _ID, "name": "State Profile", "icon": "S", "outputs": {"1": {"input": 5}}}
_CREATE = act("request", method="POST", path="/api/profile", json=_BASE)
_DELETE = act("request", method="DELETE", path=_PROFILE)
_EMPTY = {"nav_targets": [], "playback_targets": [], "volume_targets": [], "power_on_targets": [],
          "power_off_targets": [], "auto_resolved": True}
_MANUAL = {"nav_targets": ["input:1", "input:8"], "playback_targets": ["input:8"],
           "volume_targets": ["output:1", "output:8"], "power_on_targets": ["input:8", "output:1"],
           "power_off_targets": ["output:8"], "auto_resolved": False}


def _case(sid, feature, method, path, payload=None, *, data=None, checks=(), setup=(_CREATE,),
          cleanup=(_DELETE,), status=200, state=None, faults=None, api="F-API-019", expect=None, writes=()):
    return Scenario(
        id=f"profile_state.{sid}", title=f"Profile state: {sid}", features=(feature, api), targets=("sim",),
        kind="failure" if faults or status != 200 else "happy", sim_state=state, faults=faults,
        setup=setup, cleanup=cleanup, writes=writes,
        action=act("request", method=method, path=path, **({"json": payload} if payload is not None else {})),
        expect=expect if expect is not None else (
            Response(status=status, json={"success": status == 200, **({"data": data} if data is not None else {})}),
            *checks, NoCommand("*"), NoCommand("cec command"), DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
    )


SCENARIOS = []
for alias in ("profile", "scene"):
    path = f"/api/{alias}/{_ID}/cec"
    api = "F-API-019" if alias == "profile" else "F-API-020"
    for method in ("POST", "PUT"):
        for sid, payload, expected in (("manual", _MANUAL, _MANUAL), ("empty", {}, _EMPTY),
                                       ("wrapped", {"cec_config": {"volume_targets": ["output:8"]}},
                                        {**_EMPTY, "volume_targets": ["output:8"]})):
            SCENARIOS.append(_case(f"cec_{alias}_{method.lower()}_{sid}", "F-DOM-007", method, path, payload,
                                   api=api, data={"profile_id": _ID, "cec_config": expected},
                                   checks=(Hub(f"{_PROFILE}/cec", "data.cec_config", equals=expected),)))
        invalid = [(key, {key: "invalid"}) for key in _EMPTY if key.endswith("_targets")]
        invalid += [("auto_type", {"auto_resolved": 1}), ("unknown_key", {"unknown": []}),
                    ("target_type", {"volume_targets": [8]}), ("config_type", {"cec_config": []})]
        for sid, payload in invalid:
            SCENARIOS.append(_case(f"cec_{alias}_{method.lower()}_reject_{sid}", "F-DOM-007", method, path,
                                   payload, api=api, status=400,
                                   setup=(_CREATE, act("request", method="PUT", path=f"{_PROFILE}/cec", json=_MANUAL)),
                                   checks=(Hub(f"{_PROFILE}/cec", "data.cec_config", equals=_MANUAL),)))
        SCENARIOS.append(_case(f"cec_{alias}_{method.lower()}_missing", "F-DOM-007", method,
                               f"/api/{alias}/validation_missing/cec", {}, api=api, status=404, setup=(), cleanup=()))
    SCENARIOS.append(_case(f"cec_{alias}_get_default", "F-DOM-007", "GET", path, api=api,
                           data={"profile_id": _ID, "cec_config": _EMPTY},
                           checks=(Hub(f"{_PROFILE}/cec", "data.cec_config", equals=_EMPTY),)))
    SCENARIOS.append(_case(f"cec_{alias}_get_saved", "F-DOM-007", "GET", path, api=api,
                           setup=(_CREATE, act("request", method="PUT", path=f"{_PROFILE}/cec", json=_MANUAL)),
                           data={"profile_id": _ID, "cec_config": _MANUAL}))
    SCENARIOS.append(_case(f"cec_{alias}_get_missing", "F-DOM-007", "GET",
                           f"/api/{alias}/validation_missing/cec", api=api, status=404, setup=(), cleanup=()))

for port in range(1, 9):
    config = {"nav_targets": [f"input:{port}"], "playback_targets": [f"input:{port}"],
              "volume_targets": [f"output:{port}"], "power_on_targets": [f"input:{port}", f"output:{port}"],
              "power_off_targets": [f"output:{port}"], "auto_resolved": False}
    SCENARIOS.append(_case(f"cec_targets_port_{port}", "F-DOM-007", "PUT", f"{_PROFILE}/cec", config,
                           checks=(Hub(f"{_PROFILE}/cec", "data.cec_config", equals=config),)))


def _resolve(sid, outputs, metadata, inputs, active, volume):
    expected = {"nav_targets": [f"input_{min(inputs)}"] if inputs else [],
                "playback_targets": [f"input_{min(inputs)}"] if inputs else [],
                "volume_targets": [f"output_{p}" for p in volume],
                "power_on_targets": [f"input_{p}" for p in inputs] + [f"output_{p}" for p in active],
                "power_off_targets": [f"output_{p}" for p in active], "auto_resolved": True}
    state = {"outputs": {str(p - 1): {"scaler": 0, "arc": 0, "connected": 1, **metadata.get(p, {})}
                         for p in range(1, 9)}}
    return _case(f"resolve_{sid}", "F-DOM-007", "POST", f"/api/scene/{_ID}/cec/auto-resolve", api="F-API-020",
                 state=state, setup=(act("request", method="POST", path="/api/profile",
                                         json={**_BASE, "outputs": outputs, "cec_config": _MANUAL}),),
                 data=expected, checks=(Hub(f"{_PROFILE}/cec", "data.cec_config", equals=expected),))

_OUTPUTS = {"1": {"input": 5}, "2": {"input": 3}, "8": {"input": 1, "enabled": False}}
for sid, metadata, volume in (
    ("audio_priority", {1: {"arc": 1}, 2: {"scaler": 4}}, [2]),
    ("multiple_audio", {1: {"scaler": 4}, 2: {"scaler": 4}}, [1, 2]),
    ("arc_priority", {2: {"arc": 1}}, [2]),
    ("default", {}, [1]),
    ("disconnected_audio", {2: {"scaler": 4, "connected": 0}}, [1]),
    ("all_disconnected", {1: {"connected": 0}, 2: {"connected": 0, "scaler": 4}}, [2]),
):
    SCENARIOS.append(_resolve(sid, _OUTPUTS, metadata, [3, 5], [1, 2], volume))
SCENARIOS.append(_resolve("all_disabled", {"1": {"input": 5, "enabled": False}}, {}, [], [], []))
for port in range(1, 9):
    SCENARIOS.append(_resolve(f"port_{port}", {str(port): {"input": port}}, {port: {"scaler": 4}},
                              [port], [port], [port]))
SCENARIOS.append(_case("resolve_missing", "F-DOM-007", "POST", "/api/scene/validation_missing/cec/auto-resolve",
                       api="F-API-020", status=404, setup=(), cleanup=()))

_SCENE = "/api/v2/scenes/scene_goodnight01"
_EDIT_SCENE = act("request", method="PUT", path=_SCENE,
                  json={"name": "First History", "steps": [{"type": "profile", "id": _ID}], "overrides": {}})
_RUN_SCENE = act("request", method="POST", path=f"{_SCENE}/execute")
_RESTORE_SCENE = act("request", method="PUT", path=_SCENE, json={"name": "Good Night", "overrides": {},
                     "steps": [{"type": "system_action", "id": "mute_all_audio"},
                               {"type": "macro", "id": "macro_all_off"}]})
_LOG = f"{_PROFILE}/execution-log"
SCENARIOS.extend([
    _case("history_empty", "F-DOM-008", "GET", _LOG, data={"profile_id": _ID, "count": 0, "log": []}),
    _case("history_missing", "F-DOM-008", "GET", "/api/profile/validation_missing/execution-log",
          status=404, setup=(), cleanup=()),
    _case("history_read_after_scene", "F-DOM-008", "GET", _LOG,
          setup=(_CREATE, _EDIT_SCENE, _RUN_SCENE), cleanup=(_RESTORE_SCENE, _DELETE), data={"count": 1},
          checks=(Hub(_LOG, "data.log[0].scene_id", equals="scene_goodnight01"),
                  Hub(_LOG, "data.log[0].scene_name", equals="First History"),
                  Hub(_LOG, "data.log[0].status", equals="success"), Hub(_LOG, "data.log[0].error", equals=None),
                  Hub(_LOG, "data.log[0].timestamp", not_equals=""))),
])
_SUCCESS_CHECKS = (Response(status=200, json={"success": True}), Hub(_LOG, "data.count", equals=1),
                   Hub(_LOG, "data.log[0].status", equals="success"),
                   Hub(_LOG, "data.log[0].scene_name", equals="First History"),
                   Hub(_LOG, "data.log[0].error", equals=None), Device("outputs[0].source", equals=5),
                   CommandSent("video switch", {"source": [1, 5]}, count=1),
                   NoCommand("cec command"), DeviceUnchanged(allow=("outputs[0].source", "routing")),
                   NoProtocolWarnings())
SCENARIOS.append(_case("history_success", "F-DOM-008", "POST", f"{_SCENE}/execute",
                       setup=(_CREATE, _EDIT_SCENE), cleanup=(_RESTORE_SCENE, _DELETE),
                       expect=_SUCCESS_CHECKS, writes=("routing", "outputs")))
SCENARIOS.append(_case("history_order", "F-DOM-008", "POST", f"{_SCENE}/execute",
                       setup=(_CREATE, _EDIT_SCENE, _RUN_SCENE,
                              act("request", method="PUT", path=_SCENE, json={"name": "Second History"})),
                       cleanup=(_RESTORE_SCENE, _DELETE), writes=("routing", "outputs"),
                       expect=(Response(status=200, json={"success": True}), Hub(_LOG, "data.count", equals=2),
                               Hub(_LOG, "data.log[0].scene_name", equals="First History"),
                               Hub(_LOG, "data.log[1].scene_name", equals="Second History"),
                               Hub(_LOG, "data.log[1].status", equals="success"),
                               DeviceUnchanged(), NoCommand("cec command"), NoProtocolWarnings())))
SCENARIOS.append(_case("history_failure", "F-DOM-008", "POST", f"{_SCENE}/execute", faults={"reject_writes": True},
                       setup=(_CREATE, _EDIT_SCENE), cleanup=(_RESTORE_SCENE, _DELETE),
                       expect=(Response(status=500, json={"success": False}), Hub(_LOG, "data.count", equals=1),
                               Hub(_LOG, "data.log[0].status", equals="error"),
                               Hub(_LOG, "data.log[0].error", not_equals=""),
                               Hub(_LOG, "data.log[0].scene_name", equals="First History"),
                               DeviceUnchanged(), NoCommand("cec command"), NoProtocolWarnings())))

for pattern in range(8):
    state, expected = {"outputs": {}}, {}
    for port in range(1, 9):
        source = (port + pattern - 1) % 8 + 1
        mute, hdr, hdcp = (port + pattern) % 2, (port + pattern) % 3, (port + pattern) % 3 + 1
        state["outputs"][str(port - 1)] = {"source": source, "stream": 1, "audio_mute": mute,
                                           "hdr": hdr, "hdcp": hdcp}
        expected[str(port)] = {"input": source, "enabled": True, "audio_mute": bool(mute),
                               "hdr_mode": hdr + 1, "hdcp_mode": hdcp}
    SCENARIOS.append(_case(f"capture_pattern_{pattern}", "F-DOM-009", "POST", "/api/scene/save-current",
                           {"id": _ID, "name": "Captured Routing", "icon": "C"}, api="F-API-020", state=state,
                           setup=(), data={"id": _ID, "name": "Captured Routing", "icon": "C", "outputs": expected},
                           checks=(Hub(_PROFILE, "data.outputs", equals=expected),)))
SCENARIOS.append(_case("capture_defaults", "F-DOM-009", "POST", "/api/scene/save-current", {"id": _ID},
                       api="F-API-020", setup=(), data={"id": _ID, "name": "Captured Scene", "icon": "\U0001f4fa"},
                       checks=(Hub(_PROFILE, "data.name", equals="Captured Scene"),)))
for read in ("video", "output"):
    SCENARIOS.append(_case(f"capture_{read}_read_failure", "F-DOM-009", "POST", "/api/scene/save-current",
                           {"id": _ID}, api="F-API-020", setup=(), faults={"http_status": 500,
                           "comheads": [f"get {read} status"]}, expect=(
                               Response(status=502, json={"success": False}),
                               Hub(_PROFILE, "success", equals=False, status=404),
                               NoCommand("*"), NoCommand("cec command"), DeviceUnchanged(), NoProtocolWarnings())))

_ALIAS = f"/api/scene/{_ID}"
SCENARIOS.extend([
    _case("alias_create", "F-DOM-001", "POST", "/api/scene", _BASE, api="F-API-020", setup=(),
          data={"id": _ID, "name": _BASE["name"]}, checks=(Hub(_PROFILE, "data.name", equals=_BASE["name"]),)),
    _case("alias_get", "F-DOM-001", "GET", _ALIAS, api="F-API-020", data={"id": _ID, "name": _BASE["name"]}),
    _case("alias_list", "F-DOM-001", "GET", "/api/scenes", api="F-API-020",
          checks=(Hub("/api/scenes", "data.scenes[4].id", equals=_ID),
                  Hub("/api/profiles", "data.profiles[4].id", equals=_ID))),
    _case("alias_delete", "F-DOM-001", "DELETE", _ALIAS, api="F-API-020", cleanup=(),
          data={"deleted": _ID}, checks=(Hub(_PROFILE, "success", equals=False, status=404),)),
    _case("alias_recall", "F-DOM-002", "POST", f"{_ALIAS}/recall", api="F-API-020", writes=("routing", "outputs"),
          expect=(Response(status=200, json={"success": True, "data": {"scene": _BASE["name"]}}),
                  Device("outputs[0].source", equals=5), CommandSent("video switch", {"source": [1, 5]}, count=1),
                  NoCommand("cec command"), DeviceUnchanged(allow=("outputs[0].source", "routing")),
                  NoProtocolWarnings())),
    _case("alias_create_invalid", "F-DOM-001", "POST", "/api/scene", {"id": _ID}, api="F-API-020",
          status=400, setup=(), cleanup=(), checks=(Hub(_PROFILE, "success", equals=False, status=404),)),
])
for method, suffix in (("GET", ""), ("DELETE", ""), ("POST", "/recall")):
    SCENARIOS.append(_case(f"alias_{method.lower()}_missing", "F-DOM-001", method,
                           f"/api/scene/validation_missing{suffix}", api="F-API-020", status=404, setup=(), cleanup=()))
