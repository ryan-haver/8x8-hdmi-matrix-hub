"""Home Assistant flows, driven through a real Home Assistant container (``ha`` client, WP-D1).

The ``ha`` client starts ``homeassistant/home-assistant`` with
``custom_components/hdmi_matrix`` installed, onboards it through its HTTP API,
and adds the hub with the integration's config flow (``ha.config_flow``, the
first scenario). Every other scenario acts the way a Home Assistant user does
(select an option, press a button, turn a switch, call a service) and checks
two things: the device state read back from the simulator, and what Home
Assistant itself shows afterwards (``ClientState``).

The component's polling interval is set to 5 s through its options flow in
``ha.config_flow``, so changes made behind Home Assistant's back (a signal, an
unplugged display) show within a few seconds.

Seed (tools/simulator/states/default.json): routing [2, 2, 1, 1, 5, 6, 1, 1];
inputs PS3, AppleTV, Computer, Switch, Shield, PS5, Analogue, Input 8 (signal on
2, 5, 6); outputs 1 (TV) and 2 (Soundbar) connected; preset 2 = [5] * 8,
preset 3 = [6] * 8; the matrix is on, nothing is muted, every stream is on.
"""

from tools.validate.model import (
    ClientState,
    CommandSent,
    Device,
    DeviceUnchanged,
    NoCommand,
    Response,
    Scenario,
    act,
)

from ._paths import CEC, CONTROL, HA_COMPONENT, HUB_CORE, OUTPUTS, STATUS

HA = ("ha",)
#: Hub code the component reads and writes through.
HA_HUB = (*HUB_CORE, *CONTROL, *STATUS, *OUTPUTS, "src/rest_api/audio.py", *HA_COMPONENT)

SCENARIOS = [
    Scenario(
        id="ha.config_flow",
        title="Home Assistant: add the hub with the config flow; one device, entities show the matrix state",
        features=("F-HA-001", "F-HA-015", "F-HA-017"),
        clients=HA,
        action=act("ha_config_flow", options={"scan_interval": 5}),
        expect=(
            Response(status=200),
            ClientState("entry.state", equals="loaded"),
            ClientState("device.manufacturer", equals="OREI"),
            ClientState("device.model", equals="BK-808"),
            ClientState("device.sw_version", equals="V1.10.01"),
            ClientState("device.name", equals="HDMI Matrix"),
            ClientState("select.output_1_source@friendly_name", equals="HDMI Matrix Output 1 (TV) source"),
            # HA-02, HA-03 at V3: the seed routing and power as Home Assistant shows them.
            ClientState("select.output_1_source", equals="AppleTV"),
            ClientState("select.output_6_source", equals="PS5"),
            ClientState("switch.power", equals="on"),
            ClientState("log.errors", equals=0),
            NoCommand("*"),
            DeviceUnchanged(),
        ),
        covers=(*HA_HUB, "src/rest_api/core.py"),
    ),
    Scenario(
        id="ha.select_source",
        title="Home Assistant: choose PS5 as the source of output 1 (select entity)",
        features=("F-HA-002", "F-MTX-001"),
        clients=HA,
        writes=("routing",),
        action=act("route", input=6, output=1),
        expect=(
            Response(status=200),
            Device("outputs[0].source", equals=6),
            DeviceUnchanged(allow=("outputs[0].source", "routing[0]")),
            CommandSent("video switch", {"source": [1, 6]}, count=1),
            ClientState("select.output_1_source", before="AppleTV", equals="PS5"),
        ),
        observe=("Does the display on output 1 now show the source connected to input 6?",),
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.power_off",
        title="Home Assistant: turn the matrix power switch off; the matrix goes to standby",
        features=("F-HA-003", "F-MTX-006"),
        clients=HA,
        writes=("power",),
        action=act("matrix_power", on=False),
        expect=(
            Response(status=200),
            Device("system.power", equals=0),
            DeviceUnchanged(allow=("system.power",)),
            CommandSent("set poweronoff", {"power": 0}, count=1),
            ClientState("switch.power", before="on", equals="off"),
        ),
        observe=("Is the matrix front panel now in standby?",),
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.power_on",
        title="Home Assistant: turn the matrix power switch on from standby",
        features=("F-HA-003", "F-MTX-006"),
        clients=HA,
        writes=("power",),
        sim_state={"system": {"power": 0}},
        action=act("matrix_power", on=True),
        expect=(
            Response(status=200),
            Device("system.power", equals=1),
            CommandSent("set poweronoff", {"power": 1}, count=1),
            ClientState("switch.power", before="off", equals="on"),
        ),
        observe=("Is the matrix on again (front panel lit)?",),
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.mute_switch",
        title="Home Assistant: turn on the output 2 mute switch; the soundbar's audio is muted",
        features=("F-HA-004", "F-MTX-007"),
        clients=HA,
        writes=("outputs",),
        action=act("output_mute", output=2, muted=True),
        expect=(
            Response(status=200),
            Device("outputs[1].audio_mute", equals=1),
            DeviceUnchanged(allow=("outputs[1].audio_mute",)),
            CommandSent("set output audio mute", {"mute": [2, 1]}, count=1),
            ClientState("switch.output_2_mute", before="off", equals="on"),
        ),
        observe=("Is the audio on output 2 now muted?",),
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.stream_switch",
        title="Home Assistant: turn off the output 3 stream switch; the output is disabled",
        features=("F-HA-005",),
        clients=HA,
        writes=("outputs",),
        action=act("output_setting", output=3, setting="enable", body={"enabled": False}),
        expect=(
            Response(status=200),
            Device("outputs[2].stream", equals=0),
            DeviceUnchanged(allow=("outputs[2].stream",)),
            CommandSent("tx stream", {"out": [3, 0]}, count=1),
            ClientState("switch.output_3_stream", before="on", equals="off"),
        ),
        observe=("Is output 3 now dark (stream disabled)?",),
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.preset_button",
        title="Home Assistant: press the preset 3 button; the matrix applies preset 3",
        features=("F-HA-006", "F-MTX-003"),
        clients=HA,
        writes=("routing",),
        action=act("preset_recall", preset=3),
        expect=(
            Response(status=200),
            Device("routing", equals=[6] * 8),
            DeviceUnchanged(allow=("outputs[*].source", "routing")),
            CommandSent("preset set", {"index": 3}, count=1),
            ClientState("select.output_1_source", before="AppleTV", equals="PS5"),
        ),
        observe=("Do the displays now show the sources stored in preset 3?",),
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.service_recall_preset",
        title="Home Assistant: hdmi_matrix.recall_preset (preset 2, targeted at the config entry)",
        features=("F-HA-010", "F-HA-018"),
        clients=HA,
        writes=("routing",),
        action=act("ha_service", domain="hdmi_matrix", service="recall_preset", data={"preset": 2}, target="entry"),
        expect=(
            Response(status=200),
            Device("routing", equals=[5] * 8),
            CommandSent("preset set", {"index": 2}, count=1),
            ClientState("select.output_1_source", before="AppleTV", equals="Shield"),
        ),
        observe=("Do the displays now show the sources stored in preset 2?",),
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.service_switch_input",
        title="Home Assistant: hdmi_matrix.switch_input (input 5 to output 2, targeted at the device)",
        features=("F-HA-011", "F-HA-018"),
        clients=HA,
        writes=("routing",),
        action=act("ha_service", domain="hdmi_matrix", service="switch_input", data={"output": 2, "input": 5},
                   target="device"),
        expect=(
            Response(status=200),
            Device("outputs[1].source", equals=5),
            DeviceUnchanged(allow=("outputs[1].source", "routing[1]")),
            CommandSent("video switch", {"source": [2, 5]}, count=1),
            ClientState("select.output_2_source", before="AppleTV", equals="Shield"),
        ),
        observe=("Does the display on output 2 now show the source connected to input 5?",),
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.service_cec_display",
        title="Home Assistant: hdmi_matrix.send_cec_command power_on to the TV on output 1",
        features=("F-HA-012", "F-CEC-005"),
        clients=HA,
        writes=("physical",),
        action=act("cec_output", output=1, command="power_on"),
        expect=(
            Response(status=200),
            CommandSent("cec command", {"object": 1, "port": [1, 0, 0, 0, 0, 0, 0, 0], "index": 0}, count=1),
            DeviceUnchanged(),
        ),
        observe=("Did the TV on output 1 turn on?",),
        covers=(*HA_HUB, *CEC),
    ),
    Scenario(
        id="ha.service_cec_source",
        title="Home Assistant: hdmi_matrix.send_cec_command play to the source on input 2",
        features=("F-HA-012",),
        clients=HA,
        writes=("physical",),
        action=act("cec_input", input=2, command="play"),
        expect=(
            Response(status=200),
            CommandSent("cec command", {"object": 0, "port": [0, 1, 0, 0, 0, 0, 0, 0], "index": 11}, count=1),
        ),
        observe=("Did the source on input 2 start playing?",),
        covers=(*HA_HUB, *CEC),
    ),
    Scenario(
        id="ha.service_cec_invalid",
        title="Home Assistant: a source-only CEC command sent to a display is rejected, nothing is sent",
        kind="failure",
        features=("F-HA-012",),
        clients=HA,
        action=act("ha_service", domain="hdmi_matrix", service="send_cec_command",
                   data={"port_type": "output", "port_num": 1, "command": "play"}),
        expect=(
            Response(status=400),
            NoCommand("*"),
            DeviceUnchanged(),
        ),
        covers=(*HA_HUB, *CEC),
    ),
    Scenario(
        id="ha.input_signal",
        title="Home Assistant: a source on input 3 starts sending video; its signal sensor turns on",
        features=("F-HA-008", "F-HA-013"),
        clients=HA,
        targets=("sim",),
        action=act("device_change", event={"type": "signal", "port": 3, "present": True}),
        expect=(
            Device("inputs[2].signal", equals=1),
            ClientState("binary_sensor.input_3_signal", before="off", equals="on"),
        ),
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.display_unplugged",
        title="Home Assistant: the TV on output 1 is unplugged; its display sensor turns off",
        features=("F-HA-009", "F-HA-013"),
        clients=HA,
        targets=("sim",),
        action=act("device_change", event={"type": "cable", "port_type": "output", "port": 1, "connected": False}),
        expect=(
            Device("outputs[0].connected", equals=0),
            ClientState("binary_sensor.output_1_connected", before="on", equals="off"),
        ),
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.matrix_unreachable",
        title="Home Assistant: the matrix stops answering; the entities go unavailable and a switch fails visibly",
        kind="failure",
        features=("F-HA-013",),
        clients=HA,
        targets=("sim",),
        faults={"drop_http": True},
        action=act("output_mute", output=1, muted=True),
        expect=(
            Response(status=500),
            Device("outputs[0].audio_mute", equals=0),
            DeviceUnchanged(),
            ClientState("switch.output_1_mute", equals="unavailable", timeout=60),
            ClientState("select.output_1_source", equals="unavailable", timeout=30),
        ),
        restart_after=True,
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.reconfigure",
        title="Home Assistant: reconfigure the entry with the hub's IP address; it reloads and keeps working",
        features=("F-HA-016",),
        clients=HA,
        targets=("sim",),
        action=act("ha_reconfigure", host="ip"),
        expect=(
            Response(status=200),
            ClientState("entry.state", equals="loaded"),
            ClientState("select.output_1_source", equals="AppleTV"),
            NoCommand("*"),
        ),
        covers=HA_HUB,
    ),
    Scenario(
        id="ha.reboot_button",
        title="Home Assistant: press the Reboot button; the matrix restarts",
        features=("F-HA-007",),
        clients=HA,
        targets=("sim",),
        writes=("system",),
        action=act("ha_service", domain="button", service="press", data={}, entity="button.reboot"),
        expect=(
            Response(status=200),
            CommandSent("reboot", channel="telnet"),
        ),
        restart_after=True,
        covers=(*HA_HUB, "src/telnet_client.py"),
        notes="Last: the simulator is offline for a few seconds after the reboot.",
    ),
]
