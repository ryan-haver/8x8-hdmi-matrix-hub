"""REST output modes and EDID selection, with independent simulator readback.

These prove software command shapes and device codes. Physical video, HDCP,
HDR/scaling, ARC and display EDID negotiation still require HIL-09 proof.
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

from ._paths import HUB_CORE, OUTPUTS

_COVERS = (*HUB_CORE, *OUTPUTS, "src/device_codes.py", "tests/validation/scenarios/output_settings.py")


def _invalid(sid, feature, path, body):
    return Scenario(
        id=f"settings.{sid}", title=f"{sid}: reject invalid request before writing to the device",
        features=(feature,), targets=("sim",), kind="failure",
        action=act("request", method="POST", path=path, json=body),
        expect=(Response(status=400, json={"success": False}), NoCommand("*"),
                DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
    )


def _refused(sid, feature, path, body, command, payload, state):
    return Scenario(
        id=f"settings.{sid}", title=f"{sid}: report device refusal and preserve all settings",
        features=(feature,), targets=("sim",), kind="failure",
        sim_state=state, faults={"reject_writes": True},
        action=act("request", method="POST", path=path, json=body),
        expect=(Response(status=500, json={"success": False}),
                CommandSent(command, payload, count=2), DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
        notes="Persistent result=0 refusal causes one re-login/retry, then HTTP failure.",
    )


SCENARIOS = []

# Explicit REST value/device code pairs, independent of production translators.
# endpoint, feature, device field, request/response/status fields, command key, raw read array, pairs
_OUTPUT_MODES = (
    ("enable", "F-MTX-008", "stream", "enabled", "enabled", "enabled", "tx stream", "out", "allout",
     ((False, 0), (True, 1))),
    ("hdcp", "F-MTX-009", "hdcp", "mode", "hdcp_mode", "hdcp", "tx hdcp", "hdcp", "allhdcp",
     ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))),
    ("hdr", "F-MTX-010", "hdr", "mode", "hdr_mode", "hdr", "set hdr conversion", "hdr", "allhdr",
     ((1, 0), (2, 1), (3, 2))),
    ("scaler", "F-MTX-011", "scaler", "mode", "scaler_mode", "scaler", "set video scaler", "scaler",
     "allscaler", ((1, 0), (2, 1), (3, 2), (4, 3), (5, 4))),
    ("arc", "F-MTX-012", "arc", "enabled", "arc_enabled", "arc", "set arc", "arc", "allarc",
     ((False, 0), (True, 1))),
)

for endpoint, feature, field, parameter, response, hub_field, command, key, raw, pairs in _OUTPUT_MODES:
    path = f"/api/output/8/{endpoint}"
    for value, device_code in pairs:
        before = next(code for _, code in pairs if code != device_code)
        SCENARIOS.append(Scenario(
            id=f"settings.{endpoint}_{int(value)}", title=f"Output 8 {endpoint}: REST {value} becomes device {device_code}",
            features=(feature,), targets=("sim",), writes=("outputs",),
            sim_state={"outputs": {"7": {field: before}}},
            action=act("request", method="POST", path=path, json={parameter: value}),
            expect=(
                Response(status=200, json={"success": True, "data": {"output": 8, response: value}}),
                Device(f"outputs[7].{field}", equals=device_code),
                CommandSent(command, {key: [8, device_code]}, count=1),
                Hub("/api/status/outputs", f"data.outputs[7].{hub_field}", equals=value),
                Hub("/api/status/outputs", f"data.raw.{raw}[7]", equals=device_code),
                DeviceUnchanged(allow=(f"outputs[7].{field}",)), NoProtocolWarnings(),
            ),
            covers=_COVERS,
        ))
    value, device_code = pairs[-1]
    before = next(code for _, code in pairs if code != device_code)
    SCENARIOS.append(_refused(f"{endpoint}_refused", feature, path, {parameter: value}, command,
                             {key: [8, device_code]}, {"outputs": {"7": {field: before}}}))
    for port in (0, 9):
        SCENARIOS.append(_invalid(f"{endpoint}_port_{port}", feature, f"/api/output/{port}/{endpoint}",
                                  {parameter: value}))
    if parameter == "mode":
        for mode in (0, len(pairs) + 1):
            SCENARIOS.append(_invalid(f"{endpoint}_invalid_{mode}", feature, path, {"mode": mode}))
        SCENARIOS.append(_invalid(f"{endpoint}_missing_mode", feature, path, {}))

_EDID_PATH = "/api/input/8/edid"


def _edid(sid, feature, body, mode, *, copy_output=None):
    state = {"inputs": {"7": {"edid": 36 if mode == 12 else 12}}}
    if copy_output is not None:
        state["outputs"] = {str(copy_output - 1): {"connected": 1}}
    return Scenario(
        id=f"settings.{sid}", title=f"Input 8 EDID: {body} selects device mode {mode}",
        features=(feature,), targets=("sim",), writes=("inputs",), sim_state=state,
        action=act("request", method="POST", path=_EDID_PATH, json=body),
        expect=(Response(status=200, json={"success": True, "data": {"input": 8, "mode": mode}}),
                Device("inputs[7].edid", equals=mode), CommandSent("set edid", {"edid": [8, mode]}, count=1),
                Hub("/api/status/edid", "data.inputs[7].edid_mode", equals=mode),
                NoCommand("copy edid"), NoCommand("set input edid"),
                DeviceUnchanged(allow=("inputs[7].edid",)), NoProtocolWarnings()),
        covers=_COVERS,
        notes="Selection code only: user EDID bytes and physical display negotiation need hardware proof.",
    )


# Built-in boundary/representative selections and a user EDID slot.
for mode in (1, 12, 36, 39):
    SCENARIOS.append(_edid(f"edid_mode_{mode}", "F-MTX-013", {"mode": mode}, mode))
for output in range(1, 9):
    SCENARIOS.append(_edid(f"edid_copy_output_{output}", "F-MTX-014", {"copy_from_output": output},
                           39 + output, copy_output=output))

for sid, path, body in (
    ("edid_input_0", "/api/input/0/edid", {"mode": 12}),
    ("edid_input_9", "/api/input/9/edid", {"mode": 12}),
    ("edid_mode_0", _EDID_PATH, {"mode": 0}),
    ("edid_mode_48", _EDID_PATH, {"mode": 48}),
    ("edid_missing_mode", _EDID_PATH, {}),
):
    SCENARIOS.append(_invalid(sid, "F-MTX-013", path, body))
for output in (0, 9):
    SCENARIOS.append(_invalid(f"edid_copy_invalid_{output}", "F-MTX-014", _EDID_PATH,
                              {"copy_from_output": output}))
SCENARIOS.extend([
    _refused("edid_refused", "F-MTX-013", _EDID_PATH, {"mode": 12}, "set edid", {"edid": [8, 12]},
             {"inputs": {"7": {"edid": 36}}}),
    _refused("edid_copy_refused", "F-MTX-014", _EDID_PATH, {"copy_from_output": 8},
             "set edid", {"edid": [8, 47]},
             {"inputs": {"7": {"edid": 36}}, "outputs": {"7": {"connected": 1}}}),
])
