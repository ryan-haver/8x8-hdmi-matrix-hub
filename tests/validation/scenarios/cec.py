"""CEC: the exact frame the matrix receives for a source and a display command.

CEC frames over HTTP: ``{"comhead": "cec command", "object": 0|1 (input|output),
"port": [8 flags], "index": n}``. Sources (object 0) use the 19-command table
(``OreiMatrix.CEC_COMMAND_MAP``: 1 power on, 2 power off, ..., 19 volume up);
displays (object 1) use the device web interface's 0-based output table
(``OreiMatrix.CEC_OUTPUT_COMMAND_MAP``: 0 power on, 1 power off, 2 mute,
3 volume down, 4 volume up, 5 active; BE-14, VAL-03). The physical effect (the
TV turning on) is only proven on hardware (V4).
"""

from tools.validate.model import (
    CommandSent,
    Device,
    DeviceUnchanged,
    NoProtocolWarnings,
    Response,
    Scenario,
    WsEvent,
    act,
)

from ._paths import CEC, HUB_CORE

SCENARIOS = [
    Scenario(
        id="cec.input_power_on",
        title="CEC power-on to the source on input 1 (CEC disabled there: the hub enables it first)",
        features=("F-CEC-001", "F-CEC-007"),
        client_features={"api": ("F-API-015",)},
        writes=("cec",),
        targets=("sim", "hardware"),
        action=act("cec_input", input=1, command="power_on"),
        expect=(
            Response(status=200),
            CommandSent("set cec index", {"inputindex": [1, 1, 0, 0, 1, 1, 0, 0]}, count=1),
            CommandSent("cec command", {"object": 0, "port": [1, 0, 0, 0, 0, 0, 0, 0], "index": 1}, count=1),
            NoProtocolWarnings(),
            Device("inputs[0].cec_enabled", equals=1),
            DeviceUnchanged(allow=("inputs[0].cec_enabled",)),
        ),
        observe=("Did the source on input 1 power on?",),
        covers=(*HUB_CORE, *CEC),
        notes="Hardware runs change the CEC enable flags; the restore puts them back with the array form (HIL-10).",
    ),
    Scenario(
        id="cec.output_power_on",
        title="CEC power-on to the display on output 1 (TV)",
        features=("F-CEC-005",),
        client_features={"api": ("F-API-015", "F-API-038")},
        writes=("physical",),
        action=act("cec_output", output=1, command="power_on"),
        expect=(
            Response(status=200),
            CommandSent("cec command", {"object": 1, "port": [1, 0, 0, 0, 0, 0, 0, 0], "index": 0}, count=1),
            NoProtocolWarnings(),
            WsEvent("cec_command", {"type": "output", "port": 1, "command": "power_on"}),
            DeviceUnchanged(),
        ),
        observe=("Did the TV on output 1 turn on?",),
        covers=(*HUB_CORE, *CEC),
        notes="BE-14: output table from the device web interface (power on = 0); a V4 run proves it.",
    ),
    Scenario(
        id="cec.output_volume_up",
        title="CEC volume-up to the display on output 2 (soundbar)",
        features=("F-CEC-006",),
        client_features={"api": ("F-API-015",)},
        writes=("physical",),
        action=act("cec_output", output=2, command="volume_up"),
        expect=(
            Response(status=200),
            CommandSent("cec command", {"object": 1, "port": [0, 1, 0, 0, 0, 0, 0, 0], "index": 4}, count=1),
            NoProtocolWarnings(),
            DeviceUnchanged(),
        ),
        observe=("Did the soundbar on output 2 raise its volume by one step?",),
        covers=(*HUB_CORE, *CEC),
        notes="Output table index 4 = volume up (device web interface; VAL-03, BE-14).",
    ),
]
