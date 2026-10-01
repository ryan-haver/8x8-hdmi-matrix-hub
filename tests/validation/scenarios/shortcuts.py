"""Built-in shortcuts (``POST /api/system-shortcuts/{key}/execute``): the matrix does what the shortcut says.

Seed state (tools/simulator/states/default.json): routing 2,2,1,1,5,6,1,1;
power on; beep on; panel unlocked; LCD code 3 (30 s); preset 3 = input 6
everywhere. The shortcut labels come from tests/e2e/fixtures/data/system_shortcuts.json.
"""

from tools.validate.model import (
    ClientState,
    CommandSent,
    Device,
    DeviceUnchanged,
    Hub,
    NoCommand,
    Response,
    Scenario,
    act,
)

from ._paths import CONTROL, HUB_CORE, SHORTCUTS, WEB_CORE


def _run(key: str, **params):
    return act("shortcut_run", key=key, params=params)


_COVERS = (*HUB_CORE, *SHORTCUTS, *WEB_CORE,
           "web/js/components/side-nav-drawer.js", "web/js/components/shortcuts-drawer.js",
           "web/js/components/toast.js")

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
        clients=("api", "browser"),
        writes=("routing",),
        action=_run("route_one_to_one"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("routing", equals=[1, 2, 3, 4, 5, 6, 7, 8]),
            CommandSent("video switch", count=8),
            DeviceUnchanged(allow=("outputs[*].source", "routing")),
            ClientState("toast.success", equals="Shortcut executed", clients=("browser",)),
        ),
        observe=("Does each display show the source on the input with its own number?",),
        covers=_COVERS,
    ),
    Scenario(
        id="shortcuts.power_off_all",
        title="Shortcut 'Power Off All': the matrix goes to standby with one command",
        features=("F-DOM-024",),
        clients=("api", "browser"),
        writes=("power",),
        action=_run("power_off_all"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("system.power", equals=0),
            CommandSent("set poweronoff", {"power": 0}, count=1),
            ClientState("toast.success", equals="Shortcut executed", clients=("browser",)),
        ),
        observe=("Is the matrix now in standby?",),
        covers=_COVERS,
        notes="API-06: the power-off was sent eight times.",
    ),
    Scenario(
        id="shortcuts.mute_all",
        title="Shortcut 'Mute All Audio': every output is muted",
        features=("F-DOM-025",),
        clients=("api", "browser"),
        writes=("outputs",),
        action=_run("mute_all_audio"),
        expect=(
            Response(status=200, json={"success": True}),
            *(Device(f"outputs[{i}].audio_mute", equals=1) for i in range(8)),
            CommandSent("set output audio mute", count=8),
            DeviceUnchanged(allow=("outputs[*].audio_mute",)),
            ClientState("toast.success", equals="Shortcut executed", clients=("browser",)),
        ),
        observe=("Is the audio on every output muted?",),
        covers=_COVERS,
    ),
    Scenario(
        id="shortcuts.unmute_all",
        title="Shortcut 'Unmute All Audio': every output is unmuted",
        features=("F-DOM-025",),
        clients=("api", "browser"),
        writes=("outputs",),
        sim_state={"outputs": {str(i): {"audio_mute": 1} for i in range(8)}},
        action=_run("unmute_all_audio"),
        expect=(
            Response(status=200, json={"success": True}),
            *(Device(f"outputs[{i}].audio_mute", equals=0) for i in range(8)),
            CommandSent("set output audio mute", count=8),
            DeviceUnchanged(allow=("outputs[*].audio_mute",)),
            ClientState("toast.success", equals="Shortcut executed", clients=("browser",)),
        ),
        observe=("Is the audio on every output playing again?",),
        covers=_COVERS,
    ),
    Scenario(
        id="shortcuts.mute_rejected",
        title="The matrix refuses the mute: the shortcut reports the failure (500)",
        kind="failure",
        features=("F-DOM-025",),
        clients=("api", "browser"),
        targets=("sim",),
        faults={"reject_writes": True},
        action=_run("mute_all_audio"),
        expect=(
            Response(status=500, json={"success": False, "data": {"failed_outputs": [1, 2, 3, 4, 5, 6, 7, 8]}}),
            DeviceUnchanged(),
            ClientState("toast.error", equals="Failed to execute shortcut", clients=("browser",)),
            ClientState("toast.success", equals=None, clients=("browser",)),
        ),
        covers=_COVERS,
        notes="API-08: the matrix's answers were ignored and every shortcut reported success.",
    ),
    Scenario(
        id="shortcuts.preset_recall",
        title="Shortcut 'Preset 3': the matrix applies preset 3",
        features=("F-DOM-026",),
        clients=("api", "browser"),
        writes=("routing",),
        action=_run("preset_recall_3"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("routing", equals=[6] * 8),
            CommandSent("preset set", {"index": 3}, count=1),
            DeviceUnchanged(allow=("outputs[*].source", "routing")),
            ClientState("toast.success", equals="Shortcut executed", clients=("browser",)),
        ),
        observe=("Do the displays now show the sources stored in preset 3?",),
        covers=(*_COVERS, *CONTROL),
    ),
    Scenario(
        id="shortcuts.beep_off",
        title="Shortcut 'Beep Off': the matrix stops beeping",
        features=("F-DOM-027",),
        clients=("api", "browser"),
        writes=("system",),
        action=_run("beep_off"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("system.beep", equals=0),
            CommandSent("set beep", {"beep": 0}, count=1),
            DeviceUnchanged(allow=("system.beep",)),
            ClientState("toast.success", equals="Shortcut executed", clients=("browser",)),
        ),
        observe=("Does a front-panel button press now make no beep?",),
        covers=_COVERS,
    ),
    Scenario(
        id="shortcuts.panel_lock",
        title="Shortcut 'Panel Lock On': the front panel is locked",
        features=("F-DOM-027",),
        clients=("api", "browser"),
        writes=("system",),
        action=_run("panel_lock_on"),
        expect=(
            Response(status=200, json={"success": True}),
            Device("system.panel_lock", equals=1),
            CommandSent("set panel lock", {"lock": 1}, count=1),
            DeviceUnchanged(allow=("system.panel_lock",)),
            ClientState("toast.success", equals="Shortcut executed", clients=("browser",)),
        ),
        observe=("Do the front-panel buttons now do nothing?",),
        covers=_COVERS,
    ),
    Scenario(
        id="shortcuts.lcd_15s",
        title="Shortcut 'LCD: 15s' (key lcd_timeout_10s): the LCD turns off after 15 s",
        features=("F-DOM-028",),
        clients=("api", "browser"),
        writes=("system",),
        action=_run("lcd_timeout_10s"),
        expect=(
            Response(status=200, json={"success": True}),
            # device LCD codes: 0 off, 1 always on, 2/3/4 = 15/30/60 s (API-07)
            Device("system.lcd_timeout", equals=2),
            CommandSent("set lcd on time", {"lcd on time": 2}, count=1),
            Hub("/api/system-shortcuts/lcd_timeout_10s", "data.label", equals="LCD: 15s"),
            DeviceUnchanged(allow=("system.lcd_timeout",)),
            ClientState("toast.success", equals="Shortcut executed", clients=("browser",)),
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


# Each mode starts from a different device value: readback proves a transition,
# rather than accepting a no-op whose precondition already matched the target.
_SYSTEM_MODES = (
    ("beep_on", "beep_on", "F-DOM-027", "beep", 0, 1, "set beep", "beep", "Beep On",
     "Does a front-panel button press now make a beep?"),
    ("panel_unlock", "panel_lock_off", "F-DOM-027", "panel_lock", 1, 0, "set panel lock", "lock",
     "Panel Lock Off", "Do the front-panel buttons respond again?"),
    ("lcd_off", "lcd_timeout_off", "F-DOM-028", "lcd_timeout", 3, 0, "set lcd on time", "lcd on time",
     "LCD: Off", "Is the front-panel LCD off?"),
    ("lcd_always_on", "lcd_timeout_always_on", "F-DOM-028", "lcd_timeout", 3, 1, "set lcd on time", "lcd on time",
     "LCD: Always On", "Does the front-panel LCD stay on for more than 60 seconds?"),
    ("lcd_30s", "lcd_timeout_30s", "F-DOM-028", "lcd_timeout", 1, 3, "set lcd on time", "lcd on time",
     "LCD: 30s", "Does the front-panel LCD turn off about 30 seconds after the last button press?"),
    ("lcd_60s", "lcd_timeout_60s", "F-DOM-028", "lcd_timeout", 3, 4, "set lcd on time", "lcd on time",
     "LCD: 60s", "Does the front-panel LCD turn off about 60 seconds after the last button press?"),
)

for sid, key, feature, field, before, after, command, argument, label, question in _SYSTEM_MODES:
    SCENARIOS.append(Scenario(
        id=f"shortcuts.{sid}",
        title=f"Shortcut '{label}': change {field} from {before} to device code {after}",
        features=(feature,),
        clients=("api", "browser"),
        writes=("system",),
        sim_state={"system": {field: before}},
        action=_run(key),
        expect=(
            Response(status=200, json={"success": True}),
            Device(f"system.{field}", equals=after),
            CommandSent(command, {argument: after}, count=1),
            DeviceUnchanged(allow=(f"system.{field}",)),
            ClientState("toast.success", equals="Shortcut executed", clients=("browser",)),
        ),
        observe=(question,),
        covers=_COVERS,
        notes=("Proves the stored LCD device code; physical timing requires the hardware observation."
               if field == "lcd_timeout" else ""),
    ))

for sid, key, feature, command, arguments in (
    ("beep_rejected", "beep_off", "F-DOM-027", "set beep", {"beep": 0}),
    ("panel_lock_rejected", "panel_lock_on", "F-DOM-027", "set panel lock", {"lock": 1}),
    ("lcd_rejected", "lcd_timeout_always_on", "F-DOM-028", "set lcd on time", {"lcd on time": 1}),
):
    SCENARIOS.append(Scenario(
        id=f"shortcuts.{sid}",
        title=f"The matrix refuses '{key}': unchanged settings and failure feedback",
        kind="failure",
        features=(feature,),
        clients=("api", "browser"),
        targets=("sim",),
        faults={"reject_writes": True},
        action=_run(key),
        expect=(
            Response(status=500, json={"success": False}),
            # _send_command treats result=0 as a possible expired session:
            # one re-login and one retry, then reports the persistent refusal.
            CommandSent(command, arguments, count=2),
            DeviceUnchanged(),
            ClientState("toast.error", equals="Failed to execute shortcut", clients=("browser",)),
            ClientState("toast.success", equals=None, clients=("browser",)),
        ),
        covers=_COVERS,
    ))

SCENARIOS.append(Scenario(
    id="shortcuts.disabled_reboot",
    title="The fixture's disabled reboot shortcut is refused before any matrix command",
    kind="failure",
    features=("F-DOM-027",),
    clients=("api", "browser"),
    targets=("sim",),
    action=_run("system_reboot"),
    expect=(
        Response(status=400, json={"success": False}),
        NoCommand("*"),
        NoCommand("reboot"),
        DeviceUnchanged(),
        ClientState("toast.error", equals="Failed to execute shortcut", clients=("browser",)),
        ClientState("toast.success", equals=None, clients=("browser",)),
    ),
    covers=(*_COVERS, "tests/e2e/fixtures/data/system_shortcuts.json"),
    notes="Proves the disabled guard only; an enabled reboot and reconnection remain unproven.",
))
