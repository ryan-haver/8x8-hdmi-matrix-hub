"""Opt-in Telnet CEC frames and ambiguous interrupted acknowledgements.

Healthy acknowledgements follow the simulator's documented HIL assumption.
No physical CEC effect is simulated or claimed.
"""

from tools.validate.model import (
    CommandSent,
    Device,
    DeviceUnchanged,
    NoCommand,
    NoProtocolWarnings,
    Response,
    Scenario,
    act,
)

from ._paths import CEC, HUB_CORE

_COVERS = (*HUB_CORE, *CEC, "src/_telnet_proto.py", "src/device_codes.py",
           "tests/validation/scenarios/cec_telnet.py")
_INPUT = (("power_on", "on"), ("power_off", "off"), ("up", "up"), ("left", "left"),
          ("select", "enter"), ("right", "right"), ("menu", "menu"), ("down", "down"), ("back", "back"),
          ("previous", "previous"), ("play", "play"), ("next", "next"), ("rewind", "rew"),
          ("pause", "pause"), ("fast_forward", "ff"), ("stop", "stop"),
          ("mute", "mute"), ("volume_down", "vol-"), ("volume_up", "vol+"))
_OUTPUT = (("power_on", "on"), ("power_off", "off"), ("mute", "mute"),
           ("volume_down", "vol-"), ("volume_up", "vol+"), ("active", "active"))
_WARM = (act("request", method="GET", path="/api/status/cec"),)

SCENARIOS = []
for kind, table in (("input", _INPUT), ("output", _OUTPUT)):
    prefix = "s cec in" if kind == "input" else "s cec hdmi out"
    for port in range(1, 9):
        idx = port - 1
        for command, word in table:
            inputs, outputs = [0, 1]*4, [1, 0]*4
            (inputs if kind == "input" else outputs)[idx] = 0
            state = {"inputs": {str(i): {"cec_enabled": n} for i, n in enumerate(inputs)},
                     "outputs": {str(i): {"cec_enabled": n} for i, n in enumerate(outputs)}}
            (inputs if kind == "input" else outputs)[idx] = 1
            field = f"{kind}s[{idx}].cec_enabled"
            SCENARIOS.append(Scenario(
                id=f"cec_telnet.{kind}_{port}_{command}", title=f"Telnet CEC {kind} {port}: {command} -> {word}",
                features=("F-CEC-010", "F-CEC-007", "F-API-015"), targets=("sim",), writes=("cec", "physical"),
                sim_state=state, setup=_WARM,
                action=act(f"cec_{kind}", **{kind: port, "command": command}),
                expect=(Response(status=200, json={"success": True}),
                        CommandSent("set cec index", {"inputindex": inputs, "outputindex": outputs}, count=1),
                        CommandSent(f"{prefix} {port} {word}", channel="telnet", count=1),
                        NoCommand("cec command"), Device(field, equals=1),
                        DeviceUnchanged(allow=(field,)), NoProtocolWarnings()), covers=_COVERS,
                notes="Requires OREI_USE_TELNET_CEC=true and a ready Telnet link. Enable flags use HTTP; CEC dispatch uses Telnet only.",
            ))

# Desired behavior after an ambiguous acknowledgement: surface failure instead
# of resending a non-idempotent volume step. C0 records the actual outcome.
for kind in ("input", "output"):
    prefix = "s cec in" if kind == "input" else "s cec hdmi out"
    SCENARIOS.append(Scenario(
        id=f"cec_telnet.{kind}_interrupted_volume", title=f"Telnet CEC {kind}: interrupted reply must not duplicate volume",
        features=("F-CEC-010", "F-API-015"), targets=("sim",), kind="failure", writes=("physical",),
        sim_state={"inputs": {"7": {"cec_enabled": 1}}, "outputs": {"7": {"cec_enabled": 1}}}, setup=_WARM,
        faults={"telnet_close_mid_command": True, "telnet_fault_count": 1},
        action=act(f"cec_{kind}", **{kind: 8, "command": "volume_up"}),
        expect=(Response(status=500, json={"success": False}, finding="BE-37"),
                CommandSent(f"{prefix} 8 vol+", channel="telnet", count=1), NoCommand("cec command", finding="BE-37"),
                NoCommand("set cec index"), DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
        notes="The simulator processes the Telnet command before truncating its reply. A second HTTP frame is an ambiguous resend; physical duplicate volume effects require hardware observation.",
    ))
