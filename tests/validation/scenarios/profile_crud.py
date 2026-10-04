"""Profile CRUD and surface settings on disposable hub data.

Readback is a separate REST request. No scenario recalls a profile or changes
the matrix. Storage reload, UI rendering and layout reconciliation are outside
this API baseline; existing findings remain open.
"""

from tools.validate.model import DeviceUnchanged, Hub, NoCommand, NoProtocolWarnings, Response, Scenario, act

from ._paths import HUB_CORE, PROFILES

_COVERS = (*HUB_CORE, *PROFILES, "src/_file_io.py", "tests/validation/scenarios/profile_crud.py")
_ID = "validation_crud"
_PATH = f"/api/profile/{_ID}"
_BASE = {"id": _ID, "name": "Validation Profile", "icon": "V",
         "outputs": {"1": {"input": 2, "enabled": True, "audio_mute": False}}}
_CREATE = act("request", method="POST", path="/api/profile", json=_BASE)
_DELETE = act("request", method="DELETE", path=_PATH)


def _case(sid, method, path, payload=None, *, data=None, checks=(), setup=(_CREATE,),
          cleanup=(_DELETE,), status=200, surface=False, failure=False):
    return Scenario(
        id=f"profile_crud.{sid}", title=f"Profile CRUD/surface: {sid}",
        features=("F-DOM-006" if surface else "F-DOM-001", "F-API-019"), targets=("sim",),
        kind="failure" if status != 200 or failure else "happy",
        setup=setup, cleanup=cleanup,
        action=act("request", method=method, path=path, **({"json": payload} if payload is not None else {})),
        expect=(Response(status=status, json={"success": status == 200, **({"data": data} if data else {})}),
                *checks, NoCommand("*"), DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
    )


SCENARIOS = [
    _case("create_defaults", "POST", "/api/profile", _BASE, setup=(),
          data={"id": _ID, "name": "Validation Profile", "outputs": _BASE["outputs"]},
          checks=(Hub(_PATH, "data.outputs", equals=_BASE["outputs"]),
                  Hub(_PATH, "data.macros", equals=[]), Hub(_PATH, "data.favorite", equals=False),
                  Hub(_PATH, "data.dashboard_visible", equals=False))),
    _case("replace_existing", "POST", "/api/profile",
          {**_BASE, "name": "Replacement", "outputs": {"8": {"input": 8}}},
          data={"name": "Replacement", "outputs": {"8": {"input": 8, "enabled": True, "audio_mute": False}}},
          checks=(Hub(_PATH, "data.name", equals="Replacement"),
                  Hub(_PATH, "data.outputs", equals={"8": {"input": 8, "enabled": True, "audio_mute": False}}))),
    _case("edit_metadata", "PUT", _PATH, {"name": "Edited", "icon": "E", "unexpected": "ignored"},
          data={"name": "Edited", "icon": "E"},
          checks=(Hub(_PATH, "data.name", equals="Edited"), Hub(_PATH, "data.icon", equals="E"),
                  Hub(_PATH, "data.outputs", equals=_BASE["outputs"]))),
    _case("edit_outputs", "PUT", _PATH,
          {"outputs": {"8": {"input": 1, "enabled": False, "audio_mute": True, "hdr_mode": 2, "hdcp_mode": 3}}},
          checks=(Hub(_PATH, "data.outputs", equals={"8": {"input": 1, "enabled": False,
                                                    "audio_mute": True, "hdr_mode": 2, "hdcp_mode": 3}}),)),
    _case("edit_assignments", "PUT", _PATH,
          {"macros": ["macro_tv_on"], "power_on_macro": "macro_tv_on", "power_off_macro": "macro_all_off",
           "cec_config": {"nav_targets": ["input:2"], "volume_targets": ["output:8"], "auto_resolved": False}},
          checks=(Hub(_PATH, "data.macros", equals=["macro_tv_on"]),
                  Hub(_PATH, "data.power_on_macro", equals="macro_tv_on"),
                  Hub(_PATH, "data.power_off_macro", equals="macro_all_off"),
                  Hub(_PATH, "data.cec_config.nav_targets", equals=["input:2"]),
                  Hub(_PATH, "data.cec_config.volume_targets", equals=["output:8"]),
                  Hub(_PATH, "data.cec_config.auto_resolved", equals=False))),
    _case("clear_assignments", "PUT", _PATH,
          {"macros": [], "power_on_macro": None, "power_off_macro": None},
          setup=(_CREATE, act("request", method="PUT", path=_PATH, json={
              "macros": ["macro_tv_on"], "power_on_macro": "macro_tv_on", "power_off_macro": "macro_all_off"})),
          checks=(Hub(_PATH, "data.macros", equals=[]),
                  Hub(f"{_PATH}/macros", "data.power_on_macro", equals=None),
                  Hub(f"{_PATH}/macros", "data.power_off_macro", equals=None))),
    _case("delete", "DELETE", _PATH, data={"deleted": _ID}, cleanup=(),
          checks=(Hub(_PATH, "success", equals=False, status=404),)),
    _case("get_missing", "GET", "/api/profile/validation_missing", status=404, setup=(), cleanup=()),
    _case("edit_missing", "PUT", "/api/profile/validation_missing", {"name": "Missing"},
          status=404, setup=(), cleanup=()),
    _case("delete_missing", "DELETE", "/api/profile/validation_missing", status=404, setup=(), cleanup=()),
    _case("edit_unknown_only", "PUT", _PATH, {"unexpected": "ignored"}, status=400,
          checks=(Hub(_PATH, "data.name", equals=_BASE["name"]),)),
    _case("edit_empty", "PUT", _PATH, {}, status=400,
          checks=(Hub(_PATH, "data.outputs", equals=_BASE["outputs"]),)),
]

for port in range(1, 9):
    outputs = {str(port): {"input": port, "enabled": port % 2 == 1, "audio_mute": port % 2 == 0,
                           "hdr_mode": 1, "hdcp_mode": 3}}
    SCENARIOS.append(_case(f"create_port_{port}", "POST", "/api/profile", {**_BASE, "outputs": outputs},
                           setup=(), data={"outputs": outputs}, checks=(Hub(_PATH, "data.outputs", equals=outputs),)))

for sid, payload in (("missing_id", {"name": "Invalid", "outputs": {"1": {"input": 1}}}),
                     ("missing_name", {"id": _ID, "outputs": {"1": {"input": 1}}}),
                     ("missing_outputs", {"id": _ID, "name": "Invalid"}),
                     ("missing_input", {**_BASE, "outputs": {"1": {"enabled": True}}}),
                     ("output_zero", {**_BASE, "outputs": {"0": {"input": 1}}}),
                     ("output_nine", {**_BASE, "outputs": {"9": {"input": 1}}}),
                     ("input_zero", {**_BASE, "outputs": {"1": {"input": 0}}}),
                     ("input_nine", {**_BASE, "outputs": {"1": {"input": 9}}})):
    SCENARIOS.append(_case(f"create_reject_{sid}", "POST", "/api/profile", payload, status=400,
                           setup=(), cleanup=(), checks=(Hub(_PATH, "success", equals=False, status=404),)))

for endpoint, field in (("favorite", "favorite"), ("dashboard", "dashboard_visible")):
    for method in ("POST", "PUT"):
        for desired in (False, True):
            initial = not desired
            SCENARIOS.append(_case(f"{endpoint}_{method.lower()}_{str(desired).lower()}", method,
                                   f"{_PATH}/{endpoint}", {field: desired} if method == "PUT" else None,
                                   surface=True, data={"id": _ID, field: desired},
                                   setup=(_CREATE, act("request", method="PUT", path=_PATH, json={field: initial})),
                                   checks=(Hub(_PATH, f"data.{field}", equals=desired),)))
    SCENARIOS.append(_case(f"{endpoint}_missing_field", "PUT", f"{_PATH}/{endpoint}", {},
                           surface=True, status=400, checks=(Hub(_PATH, f"data.{field}", equals=False),)))
    for method in ("POST", "PUT"):
        SCENARIOS.append(_case(f"{endpoint}_{method.lower()}_missing", method,
                               f"/api/profile/validation_missing/{endpoint}", {field: True},
                               surface=True, status=404, setup=(), cleanup=()))

SCENARIOS.extend([
    _case("pin_edit", "PUT", _PATH, {"pinned": False, "pin_order": 7}, surface=True,
          checks=(Hub(_PATH, "data.pinned", equals=False), Hub(_PATH, "data.pin_order", equals=7))),
    _case("reorder", "POST", "/api/profiles/reorder",
          {"profiles": [{"id": _ID, "pinned": True, "pin_order": 6}]}, surface=True,
          data={"updated": [_ID], "errors": None},
          checks=(Hub(_PATH, "data.pinned", equals=True), Hub(_PATH, "data.pin_order", equals=6))),
    _case("reorder_partial", "POST", "/api/profiles/reorder",
          {"profiles": [{"id": "validation_missing", "pin_order": 0}, {"pin_order": 1},
                        {"id": _ID, "pinned": False, "pin_order": 5}]}, surface=True,
          data={"updated": [_ID], "errors": ["Profile 'validation_missing' not found", "Missing profile id"]},
          checks=(Hub(_PATH, "data.pinned", equals=False), Hub(_PATH, "data.pin_order", equals=5))),
    _case("reorder_empty", "POST", "/api/profiles/reorder", {"profiles": []}, surface=True, status=400,
          checks=(Hub(_PATH, "data.pin_order", equals=3),)),
])

_CEC = {"nav_targets": ["input:2"], "playback_targets": [], "volume_targets": ["output:8"],
        "power_on_targets": [], "power_off_targets": [], "auto_resolved": False}
SCENARIOS.append(_case("create_assignments", "POST", "/api/profile",
                       {**_BASE, "cec_config": _CEC, "macros": ["macro_tv_on"],
                        "power_on_macro": "macro_tv_on", "power_off_macro": "macro_all_off"}, setup=(),
                       checks=(Hub(_PATH, "data.cec_config", equals=_CEC),
                               Hub(_PATH, "data.macros", equals=["macro_tv_on"]),
                               Hub(_PATH, "data.power_on_macro", equals="macro_tv_on"),
                               Hub(_PATH, "data.power_off_macro", equals="macro_all_off"))))

# Fixture favorites occupy orders 0 and 1. New favorites are ordered by
# pin_order, then case-insensitive name, independently of creation order.
_ORDERED = [("validation_order_z", "Zebra", 5), ("validation_order_b", "beta", 4),
            ("validation_order_a", "Alpha", 4)]
_FAVORITES_SETUP = tuple(action for pid, name, order in _ORDERED for action in (
    act("request", method="POST", path="/api/profile", json={**_BASE, "id": pid, "name": name}),
    act("request", method="PUT", path=f"/api/profile/{pid}", json={"favorite": True, "pin_order": order}),
))
_FAVORITES_CLEANUP = tuple(act("request", method="DELETE", path=f"/api/profile/{pid}")
                           for pid, _, _ in _ORDERED)
SCENARIOS.append(_case("favorite_list_order", "GET", "/api/profiles/favorites", surface=True,
                       setup=_FAVORITES_SETUP, cleanup=_FAVORITES_CLEANUP,
                       checks=tuple(Hub("/api/profiles/favorites", f"data.profiles[{i}].id", equals=pid)
                                    for i, pid in enumerate(("movie_night", "game_day", "validation_order_a",
                                                             "validation_order_b", "validation_order_z"))) + (
                           Hub("/api/profiles/favorites", "data.profiles[5].favorite", absent_or_false=True),)))
SCENARIOS.append(_case("favorite_list_exclusion", "GET", "/api/profiles/favorites", surface=True,
                       checks=(Hub("/api/profiles/favorites", "data.profiles[0].id", equals="movie_night"),
                               Hub("/api/profiles/favorites", "data.profiles[1].id", equals="game_day"),
                               Hub("/api/profiles/favorites", "data.profiles[2].favorite", absent_or_false=True),
                               Hub(_PATH, "data.favorite", equals=False))))

# API-22: scaler mode (API value 1-5, device_codes.SCALER_MODES) and ARC are
# saved and read back on create and edit; invalid values are refused.
for method in ("POST", "PUT"):
    outputs = {"1": {"input": 2, "enabled": True, "audio_mute": False, "scaler_mode": 4, "arc": True}}
    SCENARIOS.append(_case(f"{method.lower()}_scaler_arc", method,
                           "/api/profile" if method == "POST" else _PATH,
                           {**_BASE, "outputs": outputs} if method == "POST" else {"outputs": outputs},
                           setup=() if method == "POST" else (_CREATE,),
                           data={"outputs": outputs},
                           checks=(Hub(_PATH, "data.outputs", equals=outputs),)))
    for sid, bad in (("scaler_invalid", {"scaler_mode": 6}), ("arc_invalid", {"arc": "on"})):
        invalid = {"1": {"input": 2, **bad}}
        SCENARIOS.append(_case(f"{method.lower()}_{sid}", method,
                               "/api/profile" if method == "POST" else _PATH,
                               {**_BASE, "outputs": invalid} if method == "POST" else {"outputs": invalid},
                               setup=() if method == "POST" else (_CREATE,),
                               cleanup=() if method == "POST" else (_DELETE,), status=400,
                               checks=(Hub(_PATH, "success", equals=False, status=404),) if method == "POST"
                               else (Hub(_PATH, "data.outputs", equals=_BASE["outputs"]),)))
