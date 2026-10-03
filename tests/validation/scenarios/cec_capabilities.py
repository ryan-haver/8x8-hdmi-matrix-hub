"""CEC catalogues and capabilities from independent matrix metadata.

Device scaler 4 means audio-only; physical detection and scaler writes remain
hardware proof. Literal command lists keep the read oracle independent.
"""

from tools.validate.model import DeviceUnchanged, Hub, NoCommand, NoProtocolWarnings, Response, Scenario, act

from ._paths import CEC, HUB_CORE

_COVERS = (*HUB_CORE, *CEC, "src/device_codes.py", "tests/validation/scenarios/cec_capabilities.py")
_INPUT = ["POWER_ON", "POWER_OFF", "UP", "DOWN", "LEFT", "RIGHT", "SELECT", "MENU", "BACK",
          "PLAY", "PAUSE", "STOP", "PREVIOUS", "NEXT", "REWIND", "FAST_FORWARD",
          "VOLUME_UP", "VOLUME_DOWN", "MUTE"]
_OUTPUT = ["POWER_ON", "POWER_OFF", "MUTE", "VOLUME_DOWN", "VOLUME_UP", "ACTIVE"]
_INPUT_REGISTRY = ["POWER_ON", "POWER_OFF", "UP", "LEFT", "SELECT", "RIGHT", "DOWN", "PLAY", "PAUSE", "STOP",
                   "REWIND", "FAST_FORWARD", "PREVIOUS", "NEXT", "VOLUME_UP", "VOLUME_DOWN", "MUTE", "MENU", "BACK"]
_OUTPUT_REGISTRY = ["POWER_ON", "POWER_OFF", "MUTE", "VOLUME_UP", "VOLUME_DOWN", "ACTIVE"]


def _input(port, signal, cec):
    return {"input_num": port, "name": f"Capability Source {port}", "signal_detected": bool(signal),
            "cec_enabled": bool(cec), "supported_cec_commands": _INPUT}


def _output(port, scaler, connected, stream, arc, cec):
    return {"output_num": port, "name": f"Capability Display {port}", "connected": bool(connected),
            "stream_enabled": bool(stream), "is_audio_only": scaler == 4, "arc_enabled": bool(arc),
            "cec_enabled": bool(cec), "scaler_mode": scaler, "supported_cec_commands": _OUTPUT}


def _read(sid, path, data, state=None, checks=()):
    return Scenario(
        id=f"cec_caps.{sid}", title=f"CEC capabilities/catalog: {sid}",
        features=("F-CEC-011", "F-API-016"), targets=("sim",), sim_state=state,
        action=act("request", method="GET", path=path),
        expect=(Response(status=200, json={"success": True, "data": data}), *checks,
                NoCommand(), NoCommand("cec command"), NoCommand("set cec index"),
                DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
    )


SCENARIOS = [
    _read("command_catalog", "/api/cec/commands", {
        "input_commands": sorted(n.lower() for n in _INPUT),
        "output_commands": sorted(n.lower() for n in _OUTPUT),
        "usage": {"input": "POST /api/cec/input/{1-8}/{command}",
                  "output": "POST /api/cec/output/{1-8}/{command}"}}),
    _read("input_catalog", "/api/cec/commands/input", {
        "device_type": "input", "commands": _INPUT_REGISTRY, "total_commands": 19},
        checks=(Hub("/api/cec/commands/input", "data.by_category.navigation[0].command", equals="UP"),
                Hub("/api/cec/commands/input", "data.by_category.playback[0].command", equals="PLAY"),
                Hub("/api/cec/commands/input", "data.by_category.volume[0].command", equals="VOLUME_UP"))),
    _read("output_catalog", "/api/cec/commands/output", {
        "device_type": "output", "commands": _OUTPUT_REGISTRY, "total_commands": 6},
        checks=(Hub("/api/cec/commands/output", "data.by_category.power[0].command", equals="POWER_ON"),
                Hub("/api/cec/commands/output", "data.by_category.volume[0].command", equals="MUTE"),
                Hub("/api/cec/commands/output", "data.by_category.source[0].command", equals="ACTIVE"))),
]

for port in range(1, 9):
    idx = str(port - 1)
    for signal in (0, 1):
        for cec in (0, 1):
            state = {"inputs": {idx: {"name": f"Capability Source {port}", "signal": signal, "cec_enabled": cec}}}
            SCENARIOS.append(_read(f"input_{port}_signal_{signal}_cec_{cec}",
                                   f"/api/cec/input/{port}/capabilities",
                                   {"capabilities": _input(port, signal, cec)}, state))
    # Every raw scaler code on every output, with both values of every flag.
    for scaler, flags in ((0, (0, 0, 0, 0)), (1, (1, 1, 1, 1)),
                          (2, (1, 0, 1, 0)), (3, (0, 1, 0, 1)), (4, (port % 2,)*4)):
        connected, stream, arc, cec = flags
        state = {"outputs": {idx: {"name": f"Capability Display {port}", "scaler": scaler,
                                  "connected": connected, "stream": stream, "arc": arc, "cec_enabled": cec}}}
        SCENARIOS.append(_read(f"output_{port}_scaler_{scaler}", f"/api/cec/output/{port}/capabilities",
                               {"capabilities": _output(port, scaler, *flags)}, state))

for pattern in range(3):
    inputs, outputs, state = [], [], {"inputs": {}, "outputs": {}}
    for port in range(1, 9):
        signal = (port + pattern) % 2
        cec_in = 1 - signal
        scaler = 4 if pattern == 0 else 0 if pattern == 1 else (port - 1) % 5
        connected = signal
        stream = 1 - signal
        arc = int((port + pattern) % 3 == 0)
        cec_out = int((port + pattern) % 3 == 1)
        state["inputs"][str(port - 1)] = {"name": f"Capability Source {port}", "signal": signal,
                                         "cec_enabled": cec_in}
        state["outputs"][str(port - 1)] = {"name": f"Capability Display {port}", "scaler": scaler,
                                          "connected": connected, "stream": stream, "arc": arc, "cec_enabled": cec_out}
        inputs.append(_input(port, signal, cec_in))
        outputs.append(_output(port, scaler, connected, stream, arc, cec_out))
    summary = {"audio_only_outputs": [o["output_num"] for o in outputs if o["is_audio_only"]],
               "arc_enabled_outputs": [o["output_num"] for o in outputs if o["arc_enabled"]],
               "connected_outputs": [o["output_num"] for o in outputs if o["connected"]],
               "signal_detected_inputs": [i["input_num"] for i in inputs if i["signal_detected"]]}
    SCENARIOS.append(_read(f"all_pattern_{pattern}", "/api/cec/capabilities",
                           {"capabilities": {"inputs": inputs, "outputs": outputs}, "summary": summary}, state))

for kind in ("input", "output"):
    for port in (0, 9, "invalid"):
        SCENARIOS.append(Scenario(
            id=f"cec_caps.{kind}_invalid_{port}", title=f"CEC {kind} capabilities: reject port {port}",
            features=("F-CEC-011", "F-API-016"), targets=("sim",), kind="failure",
            action=act("request", method="GET", path=f"/api/cec/{kind}/{port}/capabilities"),
            expect=(Response(status=400, json={"success": False}), NoCommand(),
                    DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
        ))
SCENARIOS.append(Scenario(
    id="cec_caps.invalid_catalog", title="CEC catalogue: reject unknown device type",
    features=("F-CEC-011", "F-API-016"), targets=("sim",), kind="failure",
    action=act("request", method="GET", path="/api/cec/commands/invalid"),
    expect=(Response(status=400, json={"success": False}), NoCommand(),
            DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
))
for sid, path in (("input", "/api/cec/input/8/capabilities"), ("output", "/api/cec/output/8/capabilities"),
                  ("all", "/api/cec/capabilities")):
    SCENARIOS.append(Scenario(
        id=f"cec_caps.{sid}_read_unavailable", title=f"CEC {sid} capabilities: failed CEC read reports failure",
        features=("F-CEC-011", "F-API-016"), targets=("sim",), kind="failure",
        faults={"http_status": 500, "comheads": ["get cec status"]},
        action=act("request", method="GET", path=path),
        expect=(Response(status=500, json={"success": False}), NoCommand(),
                DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
    ))
