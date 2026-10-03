"""Direct matrix controls: stored device effects, refusals and request boundaries.

Simulator-only: names and presets change disposable state. Front-panel settings
prove device codes, not audible beeps, physical button behavior or LCD timing.
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

from ._paths import CONTROL, DEVICE_SETTINGS, HUB_CORE

_CORE = (*HUB_CORE, "tests/validation/scenarios/matrix_controls.py")
_NAMES = (*_CORE, *DEVICE_SETTINGS, "src/persistence.py")
_SYSTEM = (*_CORE, "src/rest_api/audio.py")
_PRESET = (*_CORE, *CONTROL, *DEVICE_SETTINGS)
_ROUTING = [8, 7, 6, 5, 4, 3, 2, 1]


def _invalid(sid, feature, path, body, error, covers):
    return Scenario(
        id=f"matrix.{sid}", title=f"{sid}: invalid request sends no device write",
        features=(feature,), targets=("sim",), kind="failure",
        action=act("request", method="POST", path=path, json=body),
        expect=(Response(status=400, json={"success": False, "error": error}),
                NoCommand("*"), DeviceUnchanged(), NoProtocolWarnings()),
        covers=covers,
    )


def _refused(sid, feature, path, body, command, payload, covers, *, sim_state=None):
    return Scenario(
        id=f"matrix.{sid}", title=f"{sid}: device refusal returns failure and preserves state",
        features=(feature,), targets=("sim",), kind="failure",
        faults={"reject_writes": True},
        sim_state=sim_state,
        action=act("request", method="POST", path=path, json=body),
        expect=(Response(status=500, json={"success": False}),
                # result=0 triggers one re-login/retry before persistent refusal.
                CommandSent(command, payload, count=2), DeviceUnchanged(), NoProtocolWarnings()),
        covers=covers,
    )


SCENARIOS = [
    Scenario(
        id="matrix.save_current_preset", title="Save all eight current routes to preset 7 without rerouting",
        features=("F-MTX-004",), targets=("sim",), writes=("presets",),
        sim_state={"outputs": {str(i): {"source": source} for i, source in enumerate(_ROUTING)},
                   "presets": {"6": {"routing": [1] * 8, "saved": False}}},
        action=act("request", method="POST", path="/api/preset/7/save", json={}),
        expect=(
            Response(status=200, json={"success": True, "data": {"preset": 7}}),
            Device("presets[6].routing", equals=_ROUTING), Device("presets[6].saved", equals=True),
            Device("routing", equals=_ROUTING), CommandSent("preset save", {"index": 7}, count=1),
            NoCommand("video switch"), DeviceUnchanged(allow=("presets[6].routing", "presets[6].saved")),
            Hub("/api/device-settings", "data.presets.7.routing",
                equals={str(i + 1): source for i, source in enumerate(_ROUTING)}),
            NoProtocolWarnings(),
        ),
        covers=_PRESET,
    ),
    _invalid("preset_invalid_slot", "F-MTX-004", "/api/preset/9/save", {}, "Preset must be 1-8", _PRESET),
    _refused("preset_refused", "F-MTX-004", "/api/preset/7/save", {}, "preset save", {"index": 7}, _PRESET),
]

for kind, feature, array in (("input", "F-MTX-022", "inputs"), ("output", "F-MTX-023", "outputs")):
    path = f"/api/{kind}/8/name"
    command = f"set {kind} name"
    for sid, name in (("name", "Validation Source" if kind == "input" else "Validation Room"),
                      ("name_limit", "N" * 32)):
        SCENARIOS.append(Scenario(
            id=f"matrix.{kind}_{sid}", title=f"Rename {kind} 8 on the device ({len(name)} characters)",
            features=(feature,), targets=("sim",), writes=(array,),
            action=act("request", method="POST", path=path, json={"name": name}),
            expect=(Response(status=200, json={"success": True, "data": {kind: 8, "name": name}}),
                    Device(f"{array}[7].name", equals=name),
                    CommandSent(command, {"index": 8, "name": name}, count=1),
                    Hub("/api/status", f"data.{kind}_names.8", equals=name),
                    DeviceUnchanged(allow=(f"{array}[7].name",)), NoProtocolWarnings()),
            cleanup=(act("request", method="POST", path=path, json={"name": f"{kind.title()} 8"}),),
            covers=_NAMES,
        ))
    SCENARIOS.extend([
        _invalid(f"{kind}_blank_name", feature, path, {"name": "  "}, "Name is required", _NAMES),
        _invalid(f"{kind}_long_name", feature, path, {"name": "N" * 33},
                 "Name cannot exceed 32 characters", _NAMES),
        _invalid(f"{kind}_invalid_port", feature, f"/api/{kind}/9/name", {"name": "Invalid"},
                 f"{kind.title()} must be between 1 and 8", _NAMES),
        _refused(f"{kind}_name_refused", feature, path, {"name": "Refused"}, command,
                 {"index": 8, "name": "Refused"}, _NAMES),
    ])

for field, feature, endpoint, parameter, response, command, argument in (
    ("beep", "F-MTX-018", "beep", "enabled", "beep_enabled", "set beep", "beep"),
    ("panel_lock", "F-MTX-019", "panel_lock", "locked", "panel_locked", "set panel lock", "lock"),
):
    path = f"/api/system/{endpoint}"
    for value in (False, True):
        SCENARIOS.append(Scenario(
            id=f"matrix.{field}_{'on' if value else 'off'}", title=f"Set {field} to {value} through REST",
            features=(feature,), targets=("sim",), writes=("system",),
            sim_state={"system": {field: int(not value)}},
            action=act("request", method="POST", path=path, json={parameter: value}),
            expect=(Response(status=200, json={"success": True, "data": {response: value}}),
                    Device(f"system.{field}", equals=int(value)),
                    CommandSent(command, {argument: int(value)}, count=1),
                    Hub("/api/status/system", f"data.{response}", equals=value),
                    DeviceUnchanged(allow=(f"system.{field}",)), NoProtocolWarnings()),
            covers=_SYSTEM,
        ))
    SCENARIOS.append(_refused(f"{field}_refused", feature, path, {parameter: True},
                             command, {argument: 1}, _SYSTEM, sim_state={"system": {field: 0}}))

for mode in range(5):
    SCENARIOS.append(Scenario(
        id=f"matrix.lcd_mode_{mode}", title=f"Store LCD device code {mode} through REST",
        features=("F-MTX-020",), targets=("sim",), writes=("system",),
        sim_state={"system": {"lcd_timeout": (mode + 1) % 5}},
        action=act("request", method="POST", path="/api/system/lcd", json={"mode": mode}),
        expect=(Response(status=200, json={"success": True, "data": {"mode": mode}}),
                Device("system.lcd_timeout", equals=mode),
                CommandSent("set lcd on time", {"lcd on time": mode}, count=1),
                Hub("/api/status/system", "data.mode", equals=mode),
                DeviceUnchanged(allow=("system.lcd_timeout",)), NoProtocolWarnings()),
        covers=_SYSTEM,
        notes="Proves the device code; physical LCD behavior and timing remain HIL-09 / hardware proof.",
    ))
SCENARIOS.extend([
    _invalid("lcd_invalid_mode", "F-MTX-020", "/api/system/lcd", {"mode": 5}, "Invalid mode (0-4)", _SYSTEM),
    _invalid("lcd_missing_mode", "F-MTX-020", "/api/system/lcd", {}, "Missing 'mode' parameter", _SYSTEM),
    _refused("lcd_refused", "F-MTX-020", "/api/system/lcd", {"mode": 1},
             "set lcd on time", {"lcd on time": 1}, _SYSTEM),
])
