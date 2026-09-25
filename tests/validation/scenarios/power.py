"""Matrix power: standby and wake."""

from tools.validate.model import CommandSent, Device, DeviceUnchanged, Hub, Response, Scenario, act

from ._paths import CONTROL, HUB_CORE

SCENARIOS = [
    Scenario(
        id="power.standby",
        title="Put the matrix in standby",
        features=("F-MTX-006",),
        client_features={"api": ("F-API-009",)},
        writes=("power",),
        action=act("matrix_power", on=False),
        expect=(
            Response(status=200),
            Device("system.power", equals=0),
            DeviceUnchanged(allow=("system.power",)),
            CommandSent("set poweronoff", {"power": 0}, count=1),
            Hub("/api/status/system", "data.power", equals="off"),
        ),
        observe=("Is the matrix front panel now in standby?",),
        covers=(*HUB_CORE, *CONTROL, "src/rest_api/audio.py"),
    ),
    Scenario(
        id="power.wake",
        title="Wake the matrix from standby",
        features=("F-MTX-006",),
        client_features={"api": ("F-API-009",)},
        writes=("power",),
        sim_state={"system": {"power": 0}},
        action=act("matrix_power", on=True),
        expect=(
            Response(status=200),
            Device("system.power", equals=1),
            DeviceUnchanged(allow=("system.power",)),
            CommandSent("set poweronoff", {"power": 1}, count=1),
            Hub("/api/status/system", "data.power", equals="on"),
        ),
        observe=("Is the matrix now on (front panel lit, outputs active)?",),
        covers=(*HUB_CORE, *CONTROL, "src/rest_api/audio.py"),
    ),
]
