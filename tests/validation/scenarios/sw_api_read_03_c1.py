"""F-API-040: a device-side output rename reaches the hub's real /ws observer.

The simulator state patch models another controller, not a hub rename POST.
The positive event check precedes all hub readback, so a REST refresh cannot
create the event being measured. Disposable polling settings are recorded.
"""

from tools.validate.model import Device, DeviceUnchanged, Hub, NoCommand, NoWsEvent, Scenario, WsEvent, act

from ._paths import HUB_CORE, STATUS

NAME = "Den TV"
POLL = 0.5
QUIET_WINDOW = 1.5  # three configured poll intervals

SCENARIOS = [
    Scenario(
        id="sw_api_read_03_c1.output_name_change",
        title="An output renamed on the device is announced with its exact port and name",
        features=("F-API-040",),
        clients=("api",),
        targets=("sim",),
        action=act("device_change", patch={"outputs": {"0": {"name": NAME}}}),
        expect=(
            WsEvent("output_name_change", {"output": 1, "name": NAME}, timeout=5),
            NoWsEvent("routing_change", timeout=QUIET_WINDOW),
            Device("outputs[0].name", equals=NAME),
            DeviceUnchanged(allow=("outputs[0].name",)),
            NoCommand(),
            NoCommand("set output name"),
            NoCommand("video switch"),
            Hub("/api/status", "data.output_names.1", equals=NAME),
        ),
        hub_env={"STATUS_POLL_INTERVAL": str(POLL), "OREI_STATUS_CACHE_TTL": "0"},
        covers=(*HUB_CORE, *STATUS, "tools/validate/runner.py",
                "tests/validation/scenarios/sw_api_read_03_c1.py"),
        notes="API/sim V2 only. Device patch, autonomous hub poll, then WS observation before REST readback.",
    ),
]
