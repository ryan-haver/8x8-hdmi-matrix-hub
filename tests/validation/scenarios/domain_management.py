"""Scene and macro management on disposable fixture data, without execution.

Scene creation generates an ID; its complete object is read via the list API.
The final scene deletion consumes a fixture. Run the sorted selection on fresh
data; the created scene lives only in that disposable volume. Other edits are
restored and temporary macros are deleted. Restart/storage failures and UI
rendering are outside this baseline.
"""

from dataclasses import replace

from tools.validate.model import DeviceUnchanged, Hub, NoCommand, NoProtocolWarnings, Response, Scenario, act

from ._paths import HUB_CORE, SCENES
from .profile_state import SCENARIOS as PROFILE_STATE

_COVERS = tuple(dict.fromkeys((*HUB_CORE, *SCENES, "src/rest_api/macros.py", "src/_file_io.py",
                             "tests/validation/scenarios/domain_management.py")))
_MID = "validation_macro_manage"
_MACRO = f"/api/cec/macro/{_MID}"
_STEP = {"command": "POWER_ON", "targets": ["input_1", "output_8"], "delay_ms": 0}
_MBASE = {"id": _MID, "name": "Management Macro", "icon": "M", "description": "Base", "steps": [_STEP]}
_MCREATE = act("request", method="POST", path="/api/cec/macro", json=_MBASE)
_MDELETE = act("request", method="DELETE", path=_MACRO)


def _case(sid, features, method, path, payload=None, *, setup=(), cleanup=(), status=200, data=None, checks=()):
    return Scenario(
        id=f"domain_manage.{sid}", title=f"Domain management: {sid}", features=features, targets=("sim",),
        kind="failure" if status != 200 or any(c.finding for c in checks) else "happy",
        setup=setup, cleanup=cleanup,
        action=act("request", method=method, path=path, **({"json": payload} if payload is not None else {})),
        expect=(Response(status=status, json={"success": status < 300, **({"data": data} if data else {})}),
                *checks, NoCommand("*"), NoCommand("cec command"), DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
    )


def _macro(sid, method, path=_MACRO, payload=None, *, feature="F-DOM-019", **kwargs):
    kwargs.setdefault("setup", (_MCREATE,))
    kwargs.setdefault("cleanup", (_MDELETE,))
    return _case(f"macro_{sid}", (feature, "F-API-023"), method, path, payload, **kwargs)


SCENARIOS = [
    _macro("create", "POST", "/api/cec/macro", _MBASE, setup=(), data=_MBASE,
           checks=(Hub(_MACRO, "data.steps", equals=[_STEP]), Hub(_MACRO, "data.name", equals=_MBASE["name"]))),
    _macro("get", "GET", data=_MBASE),
    _macro("replace", "POST", "/api/cec/macro", {**_MBASE, "name": "Replacement"},
           checks=(Hub(_MACRO, "data.name", equals="Replacement"), Hub(_MACRO, "data.steps", equals=[_STEP]))),
    _macro("edit_metadata", "PUT", payload={"name": "Edited", "icon": "E", "description": "Edited description"},
           checks=(Hub(_MACRO, "data.name", equals="Edited"), Hub(_MACRO, "data.icon", equals="E"),
                   Hub(_MACRO, "data.description", equals="Edited description"), Hub(_MACRO, "data.steps", equals=[_STEP]))),
    _macro("edit_steps", "PUT", payload={"steps": [{"command": "ACTIVE", "targets": ["output_8"], "delay_ms": 123}]},
           checks=(Hub(_MACRO, "data.steps", equals=[{"command": "ACTIVE", "targets": ["output_8"], "delay_ms": 123}]),)),
    _macro("delete", "DELETE", cleanup=(), data={"deleted": _MID},
           checks=(Hub(_MACRO, "success", equals=False, status=404),)),
]

_BAD = [
    ("name_type", {"name": 4}), ("name_long", {"name": "N" * 201}),
    ("steps_type", {"steps": {}}), ("steps_empty", {"steps": []}),
    ("step_type", {"steps": [1]}), ("command_missing", {"steps": [{"targets": ["input_1"]}]}),
    ("command_type", {"steps": [{**_STEP, "command": 4}]}),
    ("command_unknown", {"steps": [{**_STEP, "command": "REBOOT"}]}),
    ("targets_empty", {"steps": [{**_STEP, "targets": []}]}),
    ("targets_type", {"steps": [{**_STEP, "targets": "input_1"}]}),
    ("target_zero", {"steps": [{**_STEP, "targets": ["input_0"]}]}),
    ("target_nine", {"steps": [{**_STEP, "targets": ["output_9"]}]}),
    ("target_colon", {"steps": [{**_STEP, "targets": ["input:1"]}]}),
    ("target_type", {"steps": [{**_STEP, "targets": [1]}]}),
    ("input_command_on_output", {"steps": [{"command": "UP", "targets": ["output_1"]}]}),
    ("output_command_on_input", {"steps": [{"command": "ACTIVE", "targets": ["input_1"]}]}),
    ("steps_limit", {"steps": [_STEP] * 101}),
    ("targets_limit", {"steps": [{**_STEP, "targets": ["input_1"] * 17}]}),
]
_BAD += [(f"delay_{sid}", {"steps": [{**_STEP, "delay_ms": delay}]})
         for sid, delay in (("negative", -1), ("long", 60001), ("boolean", True), ("float", 1.5))]
for method in ("POST", "PUT"):
    for sid, bad in _BAD:
        create = method == "POST"
        checks = (Hub(_MACRO, "success", equals=False, status=404),) if create else (
            Hub(_MACRO, "data.name", equals=_MBASE["name"]), Hub(_MACRO, "data.steps", equals=[_STEP]))
        SCENARIOS.append(_macro(f"{method.lower()}_reject_{sid}", method,
                               "/api/cec/macro" if create else _MACRO, {**_MBASE, **bad},
                               status=400, setup=() if create else (_MCREATE,), cleanup=() if create else (_MDELETE,),
                               checks=checks))
SCENARIOS.append(_macro("create_description_long", "POST", "/api/cec/macro",
                        {**_MBASE, "description": "D" * 2001}, status=400, setup=(), cleanup=(),
                        checks=(Hub(_MACRO, "success", equals=False, status=404),)))
SCENARIOS.append(Scenario(
    id="domain_manage.macro_update_description_long", title="Macro update refuses an over-limit description",
    features=("F-DOM-019", "F-API-023"), targets=("sim",), kind="failure", setup=(_MCREATE,), cleanup=(_MDELETE,),
    action=act("request", method="PUT", path=_MACRO, json={"description": "D" * 2001}),
    expect=(Response(status=400, json={"success": False}),
            Hub(_MACRO, "data.description", equals="Base"), NoCommand("*"),
            NoCommand("cec command"), DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
))
for sid, body in (("name_boundary", {"name": "N" * 200}), ("description_boundary", {"description": "D" * 2000}),
                  ("steps_boundary", {"steps": [_STEP] * 100}),
                  ("targets_boundary", {"steps": [{**_STEP, "targets": [f"{kind}_{p}" for kind in ("input", "output")
                                                                             for p in range(1, 9)]}]}),
                  ("delay_boundary", {"steps": [{**_STEP, "delay_ms": 60000}]}),
                  ("lowercase_command", {"steps": [{**_STEP, "command": "power_on"}]})):
    field = next(iter(body))
    SCENARIOS.append(_macro(f"create_{sid}", "POST", "/api/cec/macro", {**_MBASE, **body}, setup=(),
                            checks=(Hub(_MACRO, f"data.{field}", equals=body[field]),)))
for method in ("GET", "PUT", "DELETE"):
    SCENARIOS.append(_macro(f"{method.lower()}_missing", method, "/api/cec/macro/validation_missing",
                            {} if method == "PUT" else None, status=404, setup=(), cleanup=()))

_COMMANDS = ["POWER_ON", "POWER_OFF", "UP", "DOWN", "LEFT", "RIGHT", "SELECT", "MENU", "BACK", "PLAY",
             "PAUSE", "STOP", "REWIND", "FAST_FORWARD", "PREVIOUS", "NEXT", "VOLUME_UP", "VOLUME_DOWN", "MUTE"]
_ALL_STEPS = [{"command": c, "targets": ["input_8"], "delay_ms": 0} for c in _COMMANDS]
_ALL_STEPS += [{"command": c, "targets": ["output_8"], "delay_ms": 0}
               for c in ("POWER_ON", "POWER_OFF", "MUTE", "VOLUME_UP", "VOLUME_DOWN", "ACTIVE")]
_ALL_STEPS[-1]["delay_ms"] = 1500
SCENARIOS.append(_macro("all_commands", "POST", "/api/cec/macro", {**_MBASE, "steps": _ALL_STEPS}, setup=(),
                        checks=(Hub(_MACRO, "data.steps", equals=_ALL_STEPS),)))
SCENARIOS.append(_macro("dry_run", "POST", f"{_MACRO}/test", feature="F-DOM-021",
                        setup=(act("request", method="POST", path="/api/cec/macro", json={**_MBASE, "steps": _ALL_STEPS}),),
                        data={"success": True, "macro_id": _MID, "step_count": 25, "issues": [],
                              "estimated_duration_ms": 1500}, checks=(Hub(_MACRO, "data.steps", equals=_ALL_STEPS),)))
SCENARIOS.append(_macro("dry_run_missing", "POST", "/api/cec/macro/validation_missing/test",
                        feature="F-DOM-021", status=404, setup=(), cleanup=()))
for endpoint, field in (("favorite", "favorite"), ("dashboard", "dashboard_visible")):
    for desired in (True, False):
        setup = (_MCREATE,) if desired else (_MCREATE, act("request", method="POST", path=f"{_MACRO}/{endpoint}"))
        SCENARIOS.append(_macro(f"{endpoint}_{str(desired).lower()}", "POST", f"{_MACRO}/{endpoint}",
                                feature="F-DOM-022", setup=setup, data={"id": _MID, field: desired},
                                checks=(Hub(_MACRO, f"data.{field}", equals=desired),)))
    SCENARIOS.append(_macro(f"{endpoint}_missing", "POST", f"/api/cec/macro/validation_missing/{endpoint}",
                            feature="F-DOM-022", status=404, setup=(), cleanup=()))
SCENARIOS.append(_macro("favorite_list", "GET", "/api/cec/macros/favorites", feature="F-DOM-022",
                        setup=(_MCREATE, act("request", method="POST", path=f"{_MACRO}/favorite")),
                        checks=(Hub("/api/cec/macros/favorites", "data.macros[0].id", equals=_MID),
                                Hub("/api/cec/macros/favorites", "data.macros[1].id", equals="macro_volume_up"),
                                Hub("/api/cec/macros/favorites", "data.macros[2].id", equals="macro_tv_on"),
                                Hub("/api/cec/macros/favorites", "data.macros[3].favorite", absent_or_false=True))))

_SCENE = "/api/v2/scenes/scene_goodnight01"
_STEPS = [{"type": "system_action", "id": "mute_all_audio"}, {"type": "macro", "id": "macro_all_off"}]
_RESTORE = act("request", method="PUT", path=_SCENE, json={"name": "Good Night", "icon": "\U0001f319",
                 "steps": _STEPS, "overrides": {}, "favorite": False, "dashboard_visible": False, "dashboard_order": 2})


def _scene(sid, method, path=_SCENE, payload=None, **kwargs):
    kwargs.setdefault("setup", (_RESTORE,))
    kwargs.setdefault("cleanup", (_RESTORE,))
    return _case(f"scene_{sid}", ("F-DOM-010", "F-API-021"), method, path, payload, **kwargs)


SCENARIOS.append(_scene("a_list", "GET", "/api/v2/scenes", setup=(), cleanup=(), data={"count": 3},
                        checks=(Hub(_SCENE, "data.scene.name", equals="Good Night"),)))
_BAD_SCENE = [
    ("body_type", []), ("name_empty", {"name": ""}), ("steps_type", {"steps": {}}),
    ("step_type", {"steps": [1]}), ("unknown_type", {"steps": [{"type": "unknown", "id": "x"}]}),
    ("missing_id", {"steps": [{"type": "profile"}]}),
    ("duplicate_profile", {"steps": [{"type": "profile", "id": "game_day"}] * 2}),
    ("protected_profile", {"steps": [{"type": "profile", "id": "kids_gaming"}]}),
]
_BAD_SCENE += [(f"wait_{sid}", {"steps": [{"type": "wait", "params": {"seconds": seconds}}]})
               for sid, seconds in (("short", 0), ("long", 31), ("boolean", True), ("string", "1"))]
for sid, body in _BAD_SCENE:
    SCENARIOS.append(_scene(f"b_create_reject_{sid}", "POST", "/api/v2/scenes", body, status=400, setup=(), cleanup=(),
                            checks=(Hub("/api/v2/scenes", "data.count", equals=3),)))
    payload = body if isinstance(body, list) else {"name": "Attempted edit", **body}
    SCENARIOS.append(_scene(f"d_update_reject_{sid}", "PUT", payload=payload, status=400,
                            checks=(Hub(_SCENE, "data.scene.name", equals="Good Night"),
                                    Hub(_SCENE, "data.scene.steps", equals=_STEPS))))
_MIXED = [{"type": "profile", "id": "game_day"}, {"type": "macro", "id": "macro_tv_on"},
          {"type": "system_action", "id": "mute_all_audio"}, {"type": "wait", "id": "", "params": {"seconds": 0.5}}]
SCENARIOS.append(_scene("c_create", "POST", "/api/v2/scenes", {"name": "Management Created Scene", "icon": "C",
                        "steps": _MIXED}, setup=(), cleanup=(), status=201,
                        data={"scene": {"name": "Management Created Scene", "steps": _MIXED}},
                        checks=(Hub("/api/v2/scenes", "data.count", equals=4),
                                Hub("/api/v2/scenes", "data.scenes[1].name", equals="Management Created Scene"),
                                Hub("/api/v2/scenes", "data.scenes[1].steps", equals=_MIXED))))
SCENARIOS.append(_scene("d_edit", "PUT", payload={"name": "Edited Scene", "icon": "E", "steps": _MIXED,
                        "favorite": True, "dashboard_visible": True, "dashboard_order": 7},
                        checks=(Hub(_SCENE, "data.scene.name", equals="Edited Scene"),
                                Hub(_SCENE, "data.scene.steps", equals=_MIXED),
                                Hub(_SCENE, "data.scene.favorite", equals=True),
                                Hub(_SCENE, "data.scene.dashboard_visible", equals=True),
                                Hub(_SCENE, "data.scene.dashboard_order", equals=7))))
for sid, step in (("profile", {"type": "profile", "id": "game_day"}),
                  ("wait_min", {"type": "wait", "id": "", "params": {"seconds": 0.5}}),
                  ("wait_max", {"type": "wait", "id": "", "params": {"seconds": 30}})):
    SCENARIOS.append(_scene(f"e_add_{sid}", "POST", f"{_SCENE}/steps", step,
                            checks=(Hub(_SCENE, "data.scene.steps", equals=_STEPS + [step]),)))
SCENARIOS.append(_scene("e_add_protected", "POST", f"{_SCENE}/steps", {"type": "profile", "id": "kids_gaming"},
                        status=400, checks=(Hub(_SCENE, "data.scene.steps", equals=_STEPS),)))
SCENARIOS.append(_scene("f_remove", "DELETE", f"{_SCENE}/steps/0",
                        checks=(Hub(_SCENE, "data.scene.steps", equals=[_STEPS[1]]),)))
for index in (-1, 2, "invalid"):
    SCENARIOS.append(_scene(f"f_remove_invalid_{str(index).replace('-', 'negative_')}", "DELETE",
                            f"{_SCENE}/steps/{index}", status=400,
                            checks=(Hub(_SCENE, "data.scene.steps", equals=_STEPS),)))
_OVERRIDE = {"profile_id": "game_day", "output_num": 1, "setting_key": "input", "disabled": True}
SCENARIOS.append(_scene("g_override", "PUT", f"{_SCENE}/override", _OVERRIDE,
                        checks=(Hub(_SCENE, "data.scene.overrides", equals={"game_day": {"1": {"input": True}}}),)))
SCENARIOS.append(_scene("g_override_clear", "DELETE", f"{_SCENE}/override", _OVERRIDE,
                        setup=(_RESTORE, act("request", method="PUT", path=f"{_SCENE}/override", json=_OVERRIDE)),
                        checks=(Hub(_SCENE, "data.scene.overrides", equals={}),)))
for sid, bad in (("zero", {"output_num": 0}), ("nine", {"output_num": 9}), ("key", {"setting_key": "unknown"})):
    SCENARIOS.append(_scene(f"g_override_reject_{sid}", "PUT", f"{_SCENE}/override", {**_OVERRIDE, **bad},
                            status=400, checks=(Hub(_SCENE, "data.scene.overrides", equals={}),)))
for method in ("GET", "PUT", "DELETE"):
    SCENARIOS.append(_scene(f"h_{method.lower()}_missing", method, "/api/v2/scenes/validation_missing",
                            {} if method == "PUT" else None, status=404, setup=(), cleanup=()))
SCENARIOS.append(_scene("z_delete", "DELETE", cleanup=(), data={"deleted": "scene_goodnight01"},
                        checks=(Hub(_SCENE, "success", equals=False, status=404),
                                Hub("/api/v2/scenes/scene_movienight01", "data.scene.name", equals="Movie Night"))))

# Reuse proven legacy contracts with an explicit domain-feature tag. Preserve
# their original source paths and give these new records distinct IDs.
for suffix in ("list", "recall"):
    original = next(s for s in PROFILE_STATE if s.id == f"profile_state.alias_{suffix}")
    SCENARIOS.append(replace(original, id=f"domain_manage.legacy_{suffix}",
                             features=("F-DOM-018", "F-API-020"), covers=(*original.covers,
                             "tests/validation/scenarios/domain_management.py")))
