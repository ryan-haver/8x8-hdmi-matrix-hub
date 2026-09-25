"""Failure paths: an unreachable matrix and invalid input.

"Failure paths are features too" (VALIDATION_PLAN §1.5): the hub must report a
failed command as failed and must not present state it does not have.
"""

from tools.validate.model import Device, DeviceUnchanged, Hub, NoCommand, Response, Scenario, WsEvent, act

from ._paths import CONTROL, HUB_CORE, STATUS

SCENARIOS = [
    Scenario(
        id="failures.unreachable_switch",
        title="Matrix unreachable (connections dropped): routing fails visibly, no fabricated state",
        kind="failure",
        features=("F-REL-009",),
        targets=("sim",),
        faults={"drop_http": True},
        action=act("route", input=3, output=1),
        expect=(
            Response(min_status=500, json={"success": False}),
            Device("outputs[0].source", equals=2),
            DeviceUnchanged(),
            WsEvent("switch_failed", {"input": 3}),
            Hub("/api/health", "data.matrix.connected", equals=False, finding="BE-04"),
            Hub("/api/status", "success", equals=False, status=None, finding="VAL-04",
                note="must not answer 200 with connected=true and default names while the matrix is unreachable"),
        ),
        restart_after=True,
        covers=(*HUB_CORE, *CONTROL, *STATUS, "src/rest_api/core.py"),
    ),
    Scenario(
        id="failures.bad_input",
        title="Routing to input 9 is rejected before anything reaches the matrix",
        kind="failure",
        features=("F-API-022",),
        action=act("request", method="POST", path="/api/switch", json={"input": 9, "output": 1}),
        expect=(
            Response(status=400, json={"success": False}),
            NoCommand("*"),
            DeviceUnchanged(),
        ),
        covers=(*HUB_CORE, *CONTROL),
    ),
]
