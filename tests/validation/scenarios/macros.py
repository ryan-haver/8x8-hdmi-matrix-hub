"""CEC macros (``POST /api/cec/macro/{id}/execute``): each step reaches the matrix as a CEC frame.

Macros come from tests/e2e/fixtures/data/cec_macros.json: ``macro_volume_up``
sends VOLUME_UP three times to the soundbar on output 2 (display CEC table,
BE-14: index 4 = volume up).
"""

from tools.validate.model import CommandSent, DeviceUnchanged, Response, Scenario, act

from ._paths import HUB_CORE

SCENARIOS = [
    Scenario(
        id="macros.run_volume_up",
        title="Run macro 'Soundbar Volume +3': three volume-up frames to output 2",
        features=("F-DOM-020",),
        writes=("physical",),
        action=act("request", method="POST", path="/api/cec/macro/macro_volume_up/execute"),
        expect=(
            Response(status=200, json={"success": True, "data": {"steps_executed": 3}}),
            CommandSent("cec command", {"object": 1, "port": [0, 1, 0, 0, 0, 0, 0, 0], "index": 4}, count=3),
            DeviceUnchanged(),
        ),
        observe=("Did the soundbar volume go up three steps?",),
        covers=(*HUB_CORE, "src/cec_macros.py", "src/rest_api/macros.py"),
        notes="VAL-02: in modular mode every macro failed with 'CEC sender not configured'.",
    ),
]
