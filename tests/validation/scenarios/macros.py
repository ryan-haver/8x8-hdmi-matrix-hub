"""CEC macros (``POST /api/cec/macro/{id}/execute``): each step reaches the matrix as a CEC frame.

Macros come from tests/e2e/fixtures/data/cec_macros.json: ``macro_volume_up``
sends VOLUME_UP three times to the soundbar on output 2 (display CEC table,
BE-14: index 4 = volume up).
"""

from tools.validate.model import ClientState, CommandSent, DeviceUnchanged, Response, Scenario, act

from ._paths import HUB_CORE, WEB_CORE

_COVERS = (*HUB_CORE, "src/cec_macros.py", "src/rest_api/macros.py", *WEB_CORE,
           "web/js/components/dashboard-card-picker.js", "web/js/utils/dashboard-manager.js",
           "web/js/components/dashboard-cards/renderers.js", "src/rest_api/dashboard_layout.py",
           "web/js/components/toast.js")

SCENARIOS = [
    Scenario(
        id="macros.run_volume_up",
        title="Run macro 'Soundbar Volume +3': three volume-up frames to output 2",
        features=("F-DOM-020",),
        clients=("api", "browser"),
        writes=("physical",),
        action=act("macro_run", macro_id="macro_volume_up"),
        expect=(
            Response(status=200, json={"success": True, "data": {"steps_executed": 3}}),
            CommandSent("cec command", {"object": 1, "port": [0, 1, 0, 0, 0, 0, 0, 0], "index": 4}, count=3),
            CommandSent("cec command", count=3),
            DeviceUnchanged(),
            ClientState("toast.success", equals="Macro executed", clients=("browser",)),
        ),
        observe=("Did the soundbar volume go up three steps?",),
        covers=_COVERS,
        notes="VAL-02: in modular mode every macro failed with 'CEC sender not configured'.",
    ),
    Scenario(
        id="macros.run_rejected",
        title="A refused CEC macro shows an error and stops before later steps",
        kind="failure",
        features=("F-DOM-020",),
        clients=("api", "browser"),
        targets=("sim",),
        faults={"reject_writes": True},
        action=act("macro_run", macro_id="macro_volume_up"),
        expect=(
            Response(status=500, json={"success": False}),
            CommandSent("cec command", count=1),
            DeviceUnchanged(),
            ClientState("toast.error", equals="Error: Execution failed", clients=("browser",)),
            ClientState("toast.success", equals=None, clients=("browser",)),
        ),
        covers=_COVERS,
    ),
]
