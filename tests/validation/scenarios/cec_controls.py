"""HTTP CEC tables, automatic enablement and explicit per-port flags.

Literal captured/device-web tables are independent of production constants.
Frame receipt proves software dispatch; physical source/display effects are V4.
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

from ._paths import CEC, HUB_CORE

_COVERS = (*HUB_CORE, *CEC, "src/device_codes.py", "tests/validation/scenarios/cec_controls.py")
_STATUS = "/api/status/cec"
_WARM = (act("request", method="GET", path=_STATUS),)
_INPUT = (
    ("power_on", 1, "F-CEC-001"), ("power_off", 2, "F-CEC-001"),
    ("up", 3, "F-CEC-002"), ("left", 4, "F-CEC-002"), ("select", 5, "F-CEC-002"),
    ("right", 6, "F-CEC-002"), ("menu", 7, "F-CEC-002"), ("down", 8, "F-CEC-002"),
    ("back", 9, "F-CEC-002"), ("previous", 10, "F-CEC-003"), ("play", 11, "F-CEC-003"),
    ("next", 12, "F-CEC-003"), ("rewind", 13, "F-CEC-003"), ("pause", 14, "F-CEC-003"),
    ("fast_forward", 15, "F-CEC-003"), ("stop", 16, "F-CEC-003"),
    ("mute", 17, "F-CEC-004"), ("volume_down", 18, "F-CEC-004"), ("volume_up", 19, "F-CEC-004"),
)
_OUTPUT = (
    ("power_on", 0, "F-CEC-005"), ("power_off", 1, "F-CEC-005"),
    ("mute", 2, "F-CEC-006"), ("volume_down", 3, "F-CEC-006"), ("volume_up", 4, "F-CEC-006"),
    ("active", 5, "F-API-015"),
)


def _flags(kind, port, initial):
    inputs = [0, 1, 0, 1, 1, 0, 1, 0]
    outputs = [1, 0, 1, 0, 0, 1, 0, 1]
    (inputs if kind == "input" else outputs)[port - 1] = initial
    state = {"inputs": {str(i): {"cec_enabled": n} for i, n in enumerate(inputs)},
             "outputs": {str(i): {"cec_enabled": n} for i, n in enumerate(outputs)}}
    return state, inputs, outputs


def _raw(inputs, outputs):
    return {"inputindex": inputs, "outputindex": outputs}


SCENARIOS = []

# Every table entry on every port; only the disabled target flag may change.
for kind, table in (("input", _INPUT), ("output", _OUTPUT)):
    for port in range(1, 9):
        idx = port - 1
        field = f"{kind}s[{idx}].cec_enabled"
        for command, code, feature in table:
            state, inputs, outputs = _flags(kind, port, 0)
            (inputs if kind == "input" else outputs)[idx] = 1
            features = tuple(dict.fromkeys((feature, "F-CEC-007", "F-API-015")))
            event = ((WsEvent("cec_command", {"type": kind, "port": port, "command": command}),)
                     if command in ("power_on", "power_off") else ())
            SCENARIOS.append(Scenario(
                id=f"cec_controls.{kind}_{port}_{command}",
                title=f"HTTP CEC {kind} {port}: {command}, auto-enable only that target",
                features=features, targets=("sim",), writes=("cec", "physical"),
                sim_state=state, setup=_WARM,
                action=act(f"cec_{kind}", **{kind: port, "command": command.upper() if port == 8 else command}),
                expect=(Response(status=200, json={"success": True, "data": {kind: port, "command": command}}),
                        CommandSent("set cec index", _raw(inputs, outputs), count=1),
                        CommandSent("cec command", {"object": int(kind == "output"),
                                    "port": [int(i == idx) for i in range(8)], "index": code}, count=1),
                        Device(field, equals=1), Hub(_STATUS, "data.raw.inputindex", equals=inputs),
                        Hub(_STATUS, "data.raw.outputindex", equals=outputs),
                        DeviceUnchanged(allow=(field,)), NoProtocolWarnings(), *event),
                covers=_COVERS,
                notes="Refresh the enable cache from the seeded matrix before dispatch. HTTP frames only; no physical effect claim.",
            ))

        state, inputs, outputs = _flags(kind, port, 1)
        SCENARIOS.append(Scenario(
            id=f"cec_controls.{kind}_{port}_already_enabled",
            title=f"CEC {kind} {port}: pre-enabled target sends one frame without an enable write",
            features=("F-CEC-007", "F-API-015"), targets=("sim",), writes=("physical",),
            sim_state=state, setup=_WARM,
            action=act(f"cec_{kind}", **{kind: port, "command": "power_on"}),
            expect=(Response(status=200, json={"success": True}), NoCommand("set cec index"),
                    CommandSent("cec command", {"object": int(kind == "output"),
                                "port": [int(i == idx) for i in range(8)], "index": int(kind == "input")}, count=1),
                    DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
        ))

        for enabled in (False, True):
            state, inputs, outputs = _flags(kind, port, int(not enabled))
            (inputs if kind == "input" else outputs)[idx] = int(enabled)
            SCENARIOS.append(Scenario(
                id=f"cec_controls.{kind}_{port}_enable_{int(enabled)}",
                title=f"Explicit CEC {kind} {port}: enabled={enabled}, preserve all other flags",
                features=("F-CEC-008", "F-API-016"), targets=("sim",), writes=("cec",),
                sim_state=state, setup=_WARM,
                action=act("request", method="POST", path=f"/api/cec/{kind}/{port}/enable", json={"enabled": enabled}),
                expect=(Response(status=200, json={"success": True, "data": {
                            "port_type": kind, "port": port, "cec_enabled": enabled}}),
                        CommandSent("get cec status"), CommandSent("set cec index", _raw(inputs, outputs), count=1),
                        NoCommand("cec command"), Device(field, equals=int(enabled)),
                        Hub(_STATUS, f"data.cec_config.{kind}s[{idx}].cec_enabled", equals=enabled),
                        Hub(_STATUS, "data.raw.inputindex", equals=inputs),
                        Hub(_STATUS, "data.raw.outputindex", equals=outputs),
                        DeviceUnchanged(allow=(field,)), NoProtocolWarnings()), covers=_COVERS,
            ))

    state, inputs, outputs = _flags(kind, 8, 0)
    (inputs if kind == "input" else outputs)[7] = 1
    SCENARIOS.append(Scenario(
        id=f"cec_controls.{kind}_enable_default", title=f"CEC {kind}: omitted enabled defaults to true",
        features=("F-CEC-008", "F-API-016"), targets=("sim",), writes=("cec",), sim_state=state,
        action=act("request", method="POST", path=f"/api/cec/{kind}/8/enable", json={}),
        expect=(Response(status=200, json={"success": True, "data": {"cec_enabled": True}}),
                CommandSent("set cec index", _raw(inputs, outputs), count=1),
                Device(f"{kind}s[7].cec_enabled", equals=1),
                DeviceUnchanged(allow=(f"{kind}s[7].cec_enabled",)), NoProtocolWarnings()), covers=_COVERS,
    ))

    for port in (0, 9, "invalid"):
        SCENARIOS.append(Scenario(
            id=f"cec_controls.{kind}_command_port_{port}", title=f"CEC {kind}: reject port {port}",
            features=("F-API-015",), targets=("sim",), kind="failure",
            action=act("request", method="POST", path=f"/api/cec/{kind}/{port}/power_on"),
            expect=(Response(status=400, json={"success": False}), NoCommand(),
                    NoCommand("cec command"), NoCommand("set cec index"),
                    DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
        ))
    for port in (0, 9):
        SCENARIOS.append(Scenario(
            id=f"cec_controls.{kind}_enable_port_{port}", title=f"CEC {kind} enable: reject port {port}",
            features=("F-CEC-008", "F-API-016"), targets=("sim",), kind="failure",
            action=act("request", method="POST", path=f"/api/cec/{kind}/{port}/enable", json={"enabled": True}),
            expect=(Response(status=400, json={"success": False}), NoCommand(),
                    NoCommand("cec command"), NoCommand("set cec index"),
                    DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
        ))

    state, inputs, outputs = _flags(kind, 8, 1)
    SCENARIOS.append(Scenario(
        id=f"cec_controls.{kind}_command_refused", title=f"CEC {kind}: refused power frame reports failure without event",
        features=("F-API-015",), targets=("sim",), kind="failure", sim_state=state, setup=_WARM,
        faults={"reject_writes": True}, action=act(f"cec_{kind}", **{kind: 8, "command": "power_on"}),
        expect=(Response(status=500, json={"success": False}), NoCommand("set cec index"),
                CommandSent("cec command", {"object": int(kind == "output"), "port": [0]*7+[1],
                            "index": int(kind == "input")}, count=1),
                NoWsEvent("cec_command"), DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
        notes="CEC frames are non-idempotent and are not retried after a refusal; no success event is announced.",
    ))
    state, inputs, outputs = _flags(kind, 8, 0)
    (inputs if kind == "input" else outputs)[7] = 1
    SCENARIOS.append(Scenario(
        id=f"cec_controls.{kind}_enable_refused", title=f"CEC {kind}: refused enable preserves every flag",
        features=("F-CEC-008", "F-API-016"), targets=("sim",), kind="failure", sim_state=state,
        faults={"reject_writes": True},
        action=act("request", method="POST", path=f"/api/cec/{kind}/8/enable", json={"enabled": True}),
        expect=(Response(status=500, json={"success": False}),
                CommandSent("set cec index", _raw(inputs, outputs), count=2), NoCommand("cec command"),
                DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
    ))

for kind, command in (("input", "active"), ("input", "unknown"), ("output", "up"),
                      ("output", "play"), ("output", "unknown")):
    SCENARIOS.append(Scenario(
        id=f"cec_controls.{kind}_unsupported_{command}", title=f"CEC {kind}: reject unsupported {command}",
        features=("F-API-015",), targets=("sim",), kind="failure",
        action=act(f"cec_{kind}", **{kind: 8, "command": command}),
        expect=(Response(status=400, json={"success": False}), NoCommand(),
                NoCommand("cec command"), NoCommand("set cec index"),
                DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
    ))

for sid, inputs, outputs in (("off", [0]*8, [0]*8), ("on", [1]*8, [1]*8),
                             ("mixed", [0, 1]*4, [1, 0]*4)):
    state = {"inputs": {str(i): {"cec_enabled": n} for i, n in enumerate(inputs)},
             "outputs": {str(i): {"cec_enabled": n} for i, n in enumerate(outputs)}}
    checks = tuple(Hub(_STATUS, f"data.cec_config.{kind}s[{i}].cec_enabled", equals=bool(n))
                   for kind, flags in (("input", inputs), ("output", outputs)) for i, n in enumerate(flags))
    SCENARIOS.append(Scenario(
        id=f"cec_controls.status_{sid}", title=f"CEC status: raw and formatted arrays ({sid})",
        features=("F-CEC-009", "F-API-004"), targets=("sim",), sim_state=state,
        action=act("request", method="GET", path=_STATUS),
        expect=(Response(status=200, json={"success": True, "data": {"raw": _raw(inputs, outputs)}}),
                CommandSent("get cec status"), *checks, NoCommand(),
                DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
    ))

SCENARIOS.append(Scenario(
    id="cec_controls.status_unavailable", title="CEC status: failed matrix read reports failure",
    features=("F-CEC-009", "F-API-004"), targets=("sim",), kind="failure",
    faults={"http_status": 500, "comheads": ["get cec status"]},
    action=act("request", method="GET", path=_STATUS),
    expect=(Response(status=500, json={"success": False}), CommandSent("get cec status"),
            NoCommand(), DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
))
