"""Matrix REST status/readback and input cycling on disposable simulator state.

Port metadata, signals and cables are simulated; physical detection and real
Flic/client behavior remain hardware/client proof. Preset reads are separate.
"""

from tools.validate.model import (
    CommandSent,
    Device,
    DeviceUnchanged,
    Hub,
    NoCommand,
    NoProtocolWarnings,
    NoWsEvent,
    Response,
    Scenario,
    WsEvent,
    act,
)

from ._paths import CONTROL, HUB_CORE, OUTPUTS, STATUS

_CORE = (*HUB_CORE, "tests/validation/scenarios/matrix_status.py")
_READ = (*_CORE, *STATUS, *OUTPUTS, "src/rest_api/audio.py", "src/device_codes.py")
_CYCLE = (*_CORE, *CONTROL, *STATUS)


def _read(sid, feature, path, data, state, *, checks=(), covers=_READ):
    # Response matches dictionaries by subset, but compares lists exactly.
    # Check selected port fields explicitly; leave raw arrays as exact reads.
    fields = tuple(
        Hub(path, f"data.{kind}[{idx}].{key}", equals=value)
        for kind, ports in data.items() if isinstance(ports, list) and ports and isinstance(ports[0], dict)
        for idx, port in enumerate(ports) for key, value in port.items()
    )
    body = {key: value for key, value in data.items()
            if not (isinstance(value, list) and value and isinstance(value[0], dict))}
    return Scenario(
        id=f"status.{sid}", title=f"{sid}: API reads seeded matrix state without a write",
        features=(feature,), targets=("sim",), sim_state=state,
        action=act("request", method="GET", path=path),
        expect=(Response(status=200, json={"success": True, "data": body}),
                *fields, *checks, NoCommand("*"), DeviceUnchanged(), NoProtocolWarnings()),
        covers=covers,
    )


SCENARIOS = []

for sid, routes in (("routing_mixed", [8, 7, 6, 5, 4, 3, 2, 1]),
                    ("routing_one_to_one", list(range(1, 9))),
                    ("routing_all_1", [1] * 8), ("routing_all_8", [8] * 8)):
    names = {str(i): f"Read Source {i}" for i in range(1, 9)}
    output_names = {str(i): f"Read Display {i}" for i in range(1, 9)}
    state = {"inputs": {str(i): {"name": names[str(i + 1)]} for i in range(8)},
             "outputs": {str(i): {"source": routes[i], "name": output_names[str(i + 1)]} for i in range(8)}}
    SCENARIOS.append(_read(sid, "F-MTX-024", "/api/status",
                           {"connected": True, "routing": {str(i + 1): v for i, v in enumerate(routes)},
                            "outputs": routes, "input_names": names, "output_names": output_names}, state,
                           checks=(Device("routing", equals=routes),)))

for port in range(1, 9):
    idx = port - 1
    for value in (0, 1):
        signals = [i % 2 for i in range(8)]
        signals[idx] = value
        cables = [1 - v for v in signals]  # A cable and an active signal are distinct fields.
        state = {"inputs": {str(i): {"signal": signals[i], "cable": cables[i]} for i in range(8)}}
        expected = [{"number": i + 1, "signalActive": bool(signals[i]), "inactive": not signals[i],
                     "cableConnected": bool(cables[i]), "sourceDetected": bool(cables[i])} for i in range(8)]
        SCENARIOS.append(_read(f"signal_{port}_{value}", "F-MTX-025", "/api/status/inputs",
                               {"inputs": expected, "raw": {"inactive": signals}, "telnetAvailable": True}, state,
                               checks=(Device(f"inputs[{idx}].signal", equals=value),)))

        connected = [i % 2 for i in range(8)]
        connected[idx] = value
        state = {"outputs": {str(i): {"connected": connected[i], "stream": 1 - connected[i]} for i in range(8)}}
        expected = [{"number": i + 1, "connected": bool(connected[i]), "cableConnected": bool(connected[i]),
                     "enabled": not connected[i]} for i in range(8)]
        SCENARIOS.append(_read(f"display_{port}_{value}", "F-MTX-027", "/api/status/outputs",
                               {"outputs": expected, "raw": {"allconnect": connected}, "telnetAvailable": True}, state,
                               checks=(Device(f"outputs[{idx}].connected", equals=value),)))

for sid, cables in (("none", [0] * 8), ("all", [1] * 8),
                    ("alternating", [0, 1] * 4), ("reverse", [1, 0] * 4)):
    outputs = [1 - v for v in cables]
    state = {"inputs": {str(i): {"cable": cables[i], "signal": 1 - cables[i]} for i in range(8)},
             "outputs": {str(i): {"connected": outputs[i]} for i in range(8)}}
    SCENARIOS.append(_read(f"cables_{sid}", "F-MTX-026", "/api/status/cables",
                           {"telnetAvailable": True,
                            "inputs": [{"number": i + 1, "cableConnected": bool(cables[i])} for i in range(8)],
                            "outputs": [{"number": i + 1, "cableConnected": bool(outputs[i])} for i in range(8)]}, state))

for dhcp in (0, 1):
    device = {"model": "BK-808", "firmware_version": "V1.10.01", "web_version": "V2.00.03",
              "hostname": f"readback-{dhcp}", "mac_address": "02:11:22:33:44:55",
              "ip_address": f"192.0.2.{20 + dhcp}", "netmask": "255.255.255.0", "gateway": "192.0.2.1",
              "dhcp": dhcp, "telnet_port": 2323, "tcp_port": 9000}
    SCENARIOS.append(_read(f"device_dhcp_{dhcp}", "F-MTX-028", "/api/status/device",
                           {"device": {"model": "BK-808", "firmware_version": "V1.10.01", "web_version": "V2.00.03",
                                       "hostname": device["hostname"], "mac_address": device["mac_address"],
                                       "ip_address": device["ip_address"], "subnet": device["netmask"],
                                       "gateway": device["gateway"], "dhcp": bool(dhcp),
                                       "telnet_port": 2323, "tcp_port": 9000}}, {"device": device},
                           checks=(Hub("/api/status/device", "data.raw.network.dhcp", equals=dhcp),)))
for power in (0, 1):
    system = {"power": power, "beep": power, "panel_lock": 1 - power, "lcd_timeout": power * 4, "baudrate": 6}
    raw = {"power": power, "beep": power, "lock": 1 - power, "mode": power * 4, "baudrate": 6}
    SCENARIOS.append(_read(f"system_power_{power}", "F-MTX-028", "/api/status/system",
                           {"power": "on" if power else "off", "beep_enabled": bool(power),
                            "panel_locked": not power, "mode": power * 4, "baudrate": 6, "raw": raw},
                           {"system": system}))
SCENARIOS.append(_read("runtime_info", "F-MTX-028", "/api/system/info", {"rest_api_version": "2.10.0"}, None,
                       covers=(*_CORE, "src/rest_api/system.py", "src/persistence.py")))

for direction in ("next", "previous"):
    for output in range(1, 9):
        for current in range(1, 9):
            target = current % 8 + 1 if direction == "next" else (current - 2) % 8 + 1
            idx = output - 1
            SCENARIOS.append(Scenario(
                id=f"status.cycle_{direction}_{output}_{current}",
                title=f"Cycle output {output} {direction}: input {current} becomes {target}",
                features=("F-MTX-029",), targets=("sim",), writes=("routing",),
                sim_state={"outputs": {str(idx): {"source": current}}},
                action=act("request", method="POST", path=f"/api/input/{direction}?output={output}"),
                expect=(Response(status=200, json={"success": True, "data": {
                    "previous_input": current, "current_input": target, "output": output}}),
                        CommandSent("video switch", {"source": [output, target]}, count=1),
                        Device(f"outputs[{idx}].source", equals=target),
                        DeviceUnchanged(allow=(f"outputs[{idx}].source", f"routing[{idx}]")),
                        Hub("/api/status", f"data.routing.{output}", equals=target),
                        WsEvent("routing_change", {"output": output, "input": target}), NoProtocolWarnings()),
                covers=_CYCLE,
            ))
    current, target = (8, 1) if direction == "next" else (1, 8)
    SCENARIOS.append(Scenario(
        id=f"status.cycle_{direction}_default", title=f"Cycle {direction} defaults to output 1 and wraps around",
        features=("F-MTX-029",), targets=("sim",), writes=("routing",),
        sim_state={"outputs": {"0": {"source": current}}},
        action=act("request", method="POST", path=f"/api/input/{direction}"),
        expect=(Response(status=200, json={"success": True, "data": {
            "previous_input": current, "current_input": target, "output": 1}}),
                CommandSent("video switch", {"source": [1, target]}, count=1),
                Device("outputs[0].source", equals=target),
                DeviceUnchanged(allow=("outputs[0].source", "routing[0]")), NoProtocolWarnings()),
        covers=_CYCLE,
    ))
    for output in ("0", "9", "invalid"):
        SCENARIOS.append(Scenario(
            id=f"status.cycle_{direction}_invalid_{output}", title=f"Cycle {direction} rejects output {output} without writing",
            features=("F-MTX-029",), targets=("sim",), kind="failure",
            action=act("request", method="POST", path=f"/api/input/{direction}?output={output}"),
            expect=(Response(status=400, json={"success": False}), NoCommand("*"),
                    DeviceUnchanged(), NoProtocolWarnings()), covers=_CYCLE,
        ))
    SCENARIOS.append(Scenario(
        id=f"status.cycle_{direction}_refused", title=f"Cycle {direction}: refusal preserves the route and reports failure",
        features=("F-MTX-029",), targets=("sim",), kind="failure",
        sim_state={"outputs": {"7": {"source": current}}}, faults={"reject_writes": True},
        action=act("request", method="POST", path=f"/api/input/{direction}?output=8"),
        expect=(Response(status=500, json={"success": False}),
                CommandSent("video switch", {"source": [8, target]}, count=2),
                DeviceUnchanged(), NoWsEvent("routing_change", timeout=0.2), NoProtocolWarnings()),
        covers=_CYCLE,
    ))
