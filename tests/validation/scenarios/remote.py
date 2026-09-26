"""Remote 3 (Unfolded Circle integration) flows, driven by the scripted Remote (``uc`` client, WP-B1).

The hub runs as it ships with the integration enabled (``run.py`` legacy mode,
``src/driver.py``); the ``uc`` client connects to the integration WebSocket,
subscribes every entity and sends the entity command a Remote user triggers.
Effects are read back from the device, like every other scenario. The deeper
protocol and lifecycle checks (standby, outages, setup, renames) live in
``tests/uc`` (pytest, same harness).

Entity ids: ``docs/audits/UC_INTEGRATION_AUDIT.md`` §3 and ``tests/uc/golden/entities.json``.
"""

from tools.validate.model import CommandSent, Device, DeviceUnchanged, NoCommand, Response, Scenario, act

from ._paths import CEC, HUB_CORE, UC_DRIVER

# Seed (tools/simulator/states/default.json): routing [2, 2, 1, 1, 5, 6, 1, 1]; input 6 "PS5";
# preset 3 = [6] * 8; CEC enabled on outputs 1-2; the matrix is on.

UC = ("uc",)

SCENARIOS = [
    Scenario(
        id="remote.select_source",
        title="Remote: choose PS5 (input 6) as the source of output 1 (media player select_source)",
        features=("F-UC-008", "F-MTX-001"),
        clients=UC,
        writes=("routing",),
        action=act("route", input=6, output=1),
        expect=(
            Response(status=200),
            Device("outputs[0].source", equals=6),
            DeviceUnchanged(allow=("outputs[0].source", "routing[0]")),
            CommandSent("video switch", {"source": [1, 6]}, count=1),
        ),
        observe=("Does the display on output 1 now show the source connected to input 6?",),
        covers=(*HUB_CORE, *UC_DRIVER),
    ),
    Scenario(
        id="remote.preset_button",
        title="Remote: press the preset 3 button; the matrix applies preset 3",
        features=("F-UC-004", "F-MTX-003"),
        clients=UC,
        writes=("routing",),
        action=act("preset_recall", preset=3),
        expect=(
            Response(status=200),
            Device("routing", equals=[6] * 8),
            DeviceUnchanged(allow=("outputs[*].source", "routing")),
            CommandSent("preset set", {"index": 3}, count=1),
        ),
        observe=("Do the displays now show the sources stored in preset 3?",),
        covers=(*HUB_CORE, *UC_DRIVER),
    ),
    Scenario(
        id="remote.matrix_preset_command",
        title="Remote: PRESET_2 on the matrix remote entity (activity / macro step)",
        features=("F-UC-005",),
        clients=UC,
        writes=("routing",),
        action=act("uc_command", entity_id="remote.orei_matrix", cmd_id="send_cmd", params={"command": "PRESET_2"}),
        expect=(
            Response(status=200),
            Device("routing", equals=[5] * 8),
            CommandSent("preset set", {"index": 2}, count=1),
        ),
        observe=("Do the displays now show the sources stored in preset 2?",),
        covers=(*HUB_CORE, *UC_DRIVER),
    ),
    Scenario(
        id="remote.output_cec_power_on",
        title="Remote: POWER_ON on the output 1 CEC remote (send_cmd) reaches the TV as a CEC frame",
        features=("F-UC-007", "F-CEC-005"),
        clients=UC,
        writes=("physical",),
        action=act("cec_output", output=1, command="power_on"),
        expect=(
            Response(status=200),
            CommandSent("cec command", {"object": 1, "port": [1, 0, 0, 0, 0, 0, 0, 0], "index": 0}, count=1),
            DeviceUnchanged(),
        ),
        observe=("Did the TV on output 1 turn on?",),
        covers=(*HUB_CORE, *UC_DRIVER, *CEC),
        notes="Display table (BE-14): power on = 0. Index 1, what the hub sent before WP-A4 part 2, is power off.",
    ),
    Scenario(
        id="remote.input_cec_command",
        title="Remote: PLAY on the input 2 CEC remote (send_cmd) reaches the source as a CEC frame",
        features=("F-UC-006",),
        clients=UC,
        writes=("physical",),
        action=act("cec_input", input=2, command="play"),
        expect=(
            Response(status=200),
            CommandSent("cec command", {"object": 0, "port": [0, 1, 0, 0, 0, 0, 0, 0], "index": 11}, count=1),
        ),
        observe=("Did the source on input 2 start playing?",),
        covers=(*HUB_CORE, *UC_DRIVER, *CEC),
    ),
    Scenario(
        id="remote.output_cec_on",
        title="Remote: the `on` command of the output 1 CEC remote (activity power-on step)",
        kind="failure",
        features=("F-UC-007",),
        clients=UC,
        writes=("physical",),
        action=act("uc_command", entity_id="remote.output_1_cec", cmd_id="on"),
        expect=(
            Response(status=200, finding="UC-01",
                     note="the driver raises AttributeError and ucapi closes the Remote's WebSocket (1011)"),
            CommandSent("cec command", {"object": 1, "port": [1, 0, 0, 0, 0, 0, 0, 0], "index": 0}, count=1,
                        finding="UC-01"),
        ),
        observe=("Did the TV on output 1 turn on, and does the Remote still show the integration as connected?",),
        covers=(*HUB_CORE, *UC_DRIVER, *CEC),
    ),
    Scenario(
        id="remote.media_player_volume",
        title="Remote: volume up on the output 2 media player sends CEC volume up to that display",
        features=("F-UC-009",),
        clients=UC,
        writes=("physical",),
        action=act("uc_command", entity_id="media_player.output_2", cmd_id="volume_up"),
        expect=(
            Response(status=200),
            CommandSent("cec command", {"object": 1, "port": [0, 1, 0, 0, 0, 0, 0, 0], "index": 4}, count=1),
            DeviceUnchanged(),
        ),
        observe=("Did the soundbar on output 2 raise its volume by one step?",),
        covers=(*HUB_CORE, *UC_DRIVER, *CEC),
        notes="Display table (BE-14): volume up = 4 (the source table's 19 is not a display command).",
    ),
    Scenario(
        id="remote.power_switch_off",
        title="Remote: turn the matrix power switch off; the matrix goes to standby",
        features=("F-UC-010", "F-MTX-006"),
        clients=UC,
        writes=("power",),
        action=act("matrix_power", on=False),
        expect=(
            Response(status=200),
            Device("system.power", equals=0),
            DeviceUnchanged(allow=("system.power",)),
            CommandSent("set poweronoff", {"power": 0}, count=1),
        ),
        observe=("Is the matrix front panel now in standby?",),
        covers=(*HUB_CORE, *UC_DRIVER),
    ),
    Scenario(
        id="remote.unknown_source",
        title="Remote: a source name that is not in the list is rejected and nothing is switched",
        kind="failure",
        features=("F-UC-008",),
        clients=UC,
        targets=("sim", "hardware"),
        action=act("uc_command", entity_id="media_player.output_1", cmd_id="select_source",
                   params={"source": "No Such Input"}),
        expect=(
            Response(status=400),
            NoCommand("*"),
            DeviceUnchanged(),
        ),
        covers=(*HUB_CORE, *UC_DRIVER),
    ),
]
