"""Built-in shortcuts (``POST /api/system-shortcuts/{key}/execute``): the matrix does what the shortcut says.

Seed state (tools/simulator/states/default.json): routing 2,2,1,1,5,6,1,1;
power on; beep on; panel unlocked; LCD code 3 (30 s); preset 3 = input 6
everywhere. The shortcut labels come from tests/e2e/fixtures/data/system_shortcuts.json.
"""

from tools.validate.model import CommandSent, Device, DeviceUnchanged, Hub, NoCommand, Response, Scenario, act

from ._paths import CONTROL, HUB_CORE, SHORTCUTS


def _run(key: str, **params):
    return act("request", method="POST", path=f"/api/system-shortcuts/{key}/execute", json={"params": params})


_COVERS = (*HUB_CORE, *SHORTCUTS)

SCENARIOS = [
    Scenario(
        id="shortcuts.route_input_to_output",
        title="Shortcut 'All → Out 1' with input 3 / output 2: output 2 shows input 3",
        features=("F-DOM-023",),
        writes=("routing",),
        action=_run("route_all_to_output", input=3, output=2),
        expect=(
            Response(status=200, json={"success": True}),
            Device("outputs[1].source", equals=3),
            CommandSent("video switch", {"source": [2, 3]}, count=1),
            DeviceUnchanged(allow=("outputs[1].source", "routing")),
        ),
        observe=("Does the display on output 2 now show the source on input 3?",),
        covers=_COVERS,
        notes="API-01: route shortcuts called OreiMatrix.switch(), which does not exist.",
    ),
    Scenario(
        id="shortcuts.route_one_to_one",
        title="Shortcut '1:1 Mapping': output N shows input N",
        features=("F-DOM-023",),
        writes=("routing",),
        action=_run("route_one_to_one"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("routing", equals=[1, 2, 3, 4, 5, 6, 7, 8]),
            CommandSent("video switch", count=8),
            DeviceUnchanged(allow=("outputs[*].source", "routing")),
        ),
        observe=("Does each display show the source on the input with its own number?",),
        covers=_COVERS,
    ),
    Scenario(
        id="shortcuts.power_off_all",
        title="Shortcut 'Power Off All': the matrix goes to standby with one command",
        features=("F-DOM-024",),
        writes=("power",),
        action=_run("power_off_all"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("system.power", equals=0),
            CommandSent("set poweronoff", {"power": 0}, count=1),
        ),
        observe=("Is the matrix now in standby?",),
        covers=_COVERS,
        notes="API-06: the power-off was sent eight times.",
    ),
    Scenario(
        id="shortcuts.mute_all",
        title="Shortcut 'Mute All Audio': every output is muted",
        features=("F-DOM-025",),
        writes=("outputs",),
        action=_run("mute_all_audio"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("outputs[0].audio_mute", equals=1),
            Device("outputs[1].audio_mute", equals=1),
            Device("outputs[7].audio_mute", equals=1),
            CommandSent("set output audio mute", count=8),
            DeviceUnchanged(allow=("outputs[*].audio_mute",)),
        ),
        observe=("Is the audio on every output muted?",),
        covers=_COVERS,
    ),
    Scenario(
        id="shortcuts.unmute_all",
        title="Shortcut 'Unmute All Audio': every output is unmuted",
        features=("F-DOM-025",),
        writes=("outputs",),
        sim_state={"outputs": {str(i): {"audio_mute": 1} for i in range(8)}},
        action=_run("unmute_all_audio"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("outputs[0].audio_mute", equals=0),
            Device("outputs[7].audio_mute", equals=0),
            CommandSent("set output audio mute", count=8),
            DeviceUnchanged(allow=("outputs[*].audio_mute",)),
        ),
        observe=("Is the audio on every output playing again?",),
        covers=_COVERS,
    ),
    Scenario(
        id="shortcuts.mute_rejected",
        title="The matrix refuses the mute: the shortcut reports the failure (500)",
        kind="failure",
        features=("F-DOM-025",),
        targets=("sim",),
        faults={"reject_writes": True},
        action=_run("mute_all_audio"),
        expect=(
            Response(status=500, json={"success": False, "data": {"failed_outputs": [1, 2, 3, 4, 5, 6, 7, 8]}}),
            DeviceUnchanged(),
        ),
        covers=_COVERS,
        notes="API-08: the matrix's answers were ignored and every shortcut reported success.",
    ),
    Scenario(
        id="shortcuts.preset_recall",
        title="Shortcut 'Preset 3': the matrix applies preset 3",
        features=("F-DOM-026",),
        writes=("routing",),
        action=_run("preset_recall_3"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("routing", equals=[6] * 8),
            CommandSent("preset set", {"index": 3}, count=1),
            DeviceUnchanged(allow=("outputs[*].source", "routing")),
        ),
        observe=("Do the displays now show the sources stored in preset 3?",),
        covers=(*_COVERS, *CONTROL),
    ),
    Scenario(
        id="shortcuts.beep_off",
        title="Shortcut 'Beep Off': the matrix stops beeping",
        features=("F-DOM-027",),
        writes=("system",),
        action=_run("beep_off"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("system.beep", equals=0),
            CommandSent("set beep", {"beep": 0}, count=1),
            DeviceUnchanged(allow=("system.beep",)),
        ),
        observe=("Does a front-panel button press now make no beep?",),
        covers=_COVERS,
    ),
    Scenario(
        id="shortcuts.panel_lock",
        title="Shortcut 'Panel Lock On': the front panel is locked",
        features=("F-DOM-027",),
        writes=("system",),
        action=_run("panel_lock_on"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("system.panel_lock", equals=1),
            CommandSent("set panel lock", {"lock": 1}, count=1),
            DeviceUnchanged(allow=("system.panel_lock",)),
        ),
        observe=("Do the front-panel buttons now do nothing?",),
        covers=_COVERS,
    ),
    Scenario(
        id="shortcuts.lcd_15s",
        title="Shortcut 'LCD: 15s' (key lcd_timeout_10s): the LCD turns off after 15 s",
        features=("F-DOM-028",),
        writes=("system",),
        action=_run("lcd_timeout_10s"),
        expect=(
            Response(status=200, json={"success": True}),
            # device LCD codes: 0 off, 1 always on, 2/3/4 = 15/30/60 s (API-07)
            Device("system.lcd_timeout", equals=2),
            CommandSent("set lcd on time", {"lcd on time": 2}, count=1),
            Hub("/api/system-shortcuts/lcd_timeout_10s", "data.label", equals="LCD: 15s"),
            DeviceUnchanged(allow=("system.lcd_timeout",)),
        ),
        observe=("Does the front-panel LCD turn off about 15 seconds after the last button press?",),
        covers=_COVERS,
        notes="API-07: owner-approved label change; the key stays lcd_timeout_10s for saved pins and Flic buttons.",
    ),
    Scenario(
        id="shortcuts.unknown",
        title="Executing a shortcut that does not exist is a 404 and nothing reaches the matrix",
        kind="failure",
        features=("F-DOM-023",),
        action=_run("nope"),
        expect=(
            Response(status=404, json={"success": False}),
            NoCommand("*"),
        ),
        covers=_COVERS,
    ),
]
