"""Opt-in Telnet CEC frames and ambiguous interrupted acknowledgements.

Healthy acknowledgements follow the simulator's documented HIL assumption.
No physical CEC effect is simulated or claimed.
"""

from dataclasses import replace

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

# BE-37: after an ambiguous acknowledgement the hub reports failure instead of
# resending the non-idempotent volume step over HTTP.
for kind in ("input", "output"):
    prefix = "s cec in" if kind == "input" else "s cec hdmi out"
    SCENARIOS.append(Scenario(
        id=f"cec_telnet.{kind}_interrupted_volume", title=f"Telnet CEC {kind}: interrupted reply must not duplicate volume",
        features=("F-CEC-010", "F-API-015"), targets=("sim",), kind="failure", writes=("physical",),
        sim_state={"inputs": {"7": {"cec_enabled": 1}}, "outputs": {"7": {"cec_enabled": 1}}}, setup=_WARM,
        faults={"telnet_close_mid_command": True, "telnet_fault_count": 1},
        action=act(f"cec_{kind}", **{kind: 8, "command": "volume_up"}),
        expect=(Response(status=500, json={"success": False}),
                CommandSent(f"{prefix} 8 vol+", channel="telnet", count=1), NoCommand("cec command"),
                NoCommand("set cec index"), DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
        notes="The simulator processes the Telnet command before truncating its reply. A second HTTP frame is an ambiguous resend; physical duplicate volume effects require hardware observation.",
    ))

# BE-38: power on/off set a state, so after the same interrupted reply they may be sent again over
# HTTP (orei_matrix.CEC_SAFE_TO_RESEND); the request succeeds with one Telnet and one HTTP frame.
for kind, command, word, index in (("input", "power_on", "on", 1), ("input", "power_off", "off", 2),
                                   ("output", "power_on", "on", 0), ("output", "power_off", "off", 1)):
    prefix = "s cec in" if kind == "input" else "s cec hdmi out"
    SCENARIOS.append(Scenario(
        id=f"cec_telnet.{kind}_interrupted_{command}", title=f"Telnet CEC {kind}: interrupted {command} is sent again over HTTP",
        features=("F-CEC-010", "F-API-015"), targets=("sim",), kind="failure", writes=("physical",),
        sim_state={"inputs": {"7": {"cec_enabled": 1}}, "outputs": {"7": {"cec_enabled": 1}}}, setup=_WARM,
        faults={"telnet_close_mid_command": True, "telnet_fault_count": 1},
        action=act(f"cec_{kind}", **{kind: 8, "command": command}),
        expect=(Response(status=200, json={"success": True}),
                CommandSent(f"{prefix} 8 {word}", channel="telnet", count=1),
                CommandSent("cec command", {"object": 1 if kind == "output" else 0, "port": [0] * 7 + [1],
                                            "index": index}, count=1),
                NoCommand("set cec index"), DeviceUnchanged(), NoProtocolWarnings()), covers=_COVERS,
        notes="Power on/off are idempotent, so the HTTP frame after a lost Telnet answer is harmless (BE-38).",
    ))

# TST-19: the standard CI run also includes HTTP-only CEC scenarios. Declare
# this family's opt-in instead of depending on the invoking shell's environment.
SCENARIOS = [replace(sc, hub_env={"OREI_USE_TELNET_CEC": "true"}) for sc in SCENARIOS]
