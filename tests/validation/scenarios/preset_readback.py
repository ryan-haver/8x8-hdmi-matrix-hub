"""The preset catalog reads each slot from the matrix (BE-36).

``GET /api/presets`` reads every slot with Telnet ``r preset N`` (cached for
OREI_STATUS_CACHE_TTL, expired by writes and forced status reads) and marks
it ``routing_source: "matrix"``. Slots changed behind the hub's back and the
full slot a custom save stores are therefore reported as stored.
"""

from tools.validate.model import (
    CommandSent,
    Device,
    DeviceUnchanged,
    Hub,
    NoCommand,
    NoProtocolWarnings,
    Response,
    Scenario,
    act,
)

from ._paths import CONTROL, DEVICE_SETTINGS, HUB_CORE

_COVERS = (*HUB_CORE, *CONTROL, *DEVICE_SETTINGS, "src/persistence.py",
           "tests/validation/scenarios/preset_readback.py")

SCENARIOS = []

for slot in range(1, 9):
    idx = slot - 1
    routes = [(i + slot) % 8 + 1 for i in range(8)]
    mapping = {str(i + 1): value for i, value in enumerate(routes)}
    path = f"data.presets[{idx}].routing"
    SCENARIOS.append(Scenario(
        id=f"preset_read.device_slot_{slot}",
        title=f"Preset {slot} has independent device routes: the catalog reads the stored slot (BE-36)",
        features=("F-MTX-030",), targets=("sim",),
        sim_state={"presets": {str(idx): {"routing": routes, "saved": True}}},
        action=act("request", method="GET", path="/api/presets"),
        expect=(Response(status=200, json={"success": True}), Device(f"presets[{idx}].routing", equals=routes),
                Hub("/api/presets", path, equals=mapping),
                Hub("/api/presets", f"data.presets[{idx}].routing_source", equals="matrix"),
                CommandSent(f"r preset {slot}", channel="telnet", count=1),
                NoCommand("preset get"), NoCommand("get routing status"), NoCommand("*"),
                DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
        notes="The independently seeded device slot differs from the fixture's empty/partial hub copy; "
              "the catalog reports the device slot.",
    ))
    SCENARIOS.append(Scenario(
        id=f"preset_read.saved_current_{slot}", title=f"Preset {slot}: catalog reads the full mapping saved by the hub",
        features=("F-MTX-004", "F-API-008"), targets=("sim",),
        sim_state={"outputs": {str(i): {"source": value} for i, value in enumerate(routes)}},
        setup=(act("request", method="POST", path=f"/api/preset/{slot}/save", json={}),),
        action=act("request", method="GET", path="/api/presets"),
        expect=(Response(status=200, json={"success": True}),
                Device(f"presets[{idx}].routing", equals=routes),
                Device(f"presets[{idx}].saved", equals=True), Hub("/api/presets", path, equals=mapping),
                Hub("/api/presets", f"data.presets[{idx}].routing_source", equals="matrix"),
                Hub("/api/device-settings", f"data.presets.{slot}.routing", equals=mapping),
                CommandSent(f"r preset {slot}", channel="telnet", count=1), NoCommand("*"),
                DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
        notes="The setup saves the device slot and the hub copy; the save expires the preset cache, so the "
              "read action queries each slot once and writes nothing.",
    ))
    actual = [8, *routes[1:]]
    full = {str(i + 1): value for i, value in enumerate(actual)}
    SCENARIOS.append(Scenario(
        id=f"preset_read.saved_partial_{slot}", title=f"Preset {slot}: catalog reports the full slot a custom save stored",
        features=("F-DOM-034", "F-API-008"), targets=("sim",),
        sim_state={"outputs": {str(i): {"source": value} for i, value in enumerate(routes)}},
        setup=(act("request", method="POST", path=f"/api/preset/{slot}/save", json={"routing": {"1": 8}}),),
        action=act("request", method="GET", path="/api/presets"),
        expect=(Response(status=200, json={"success": True}),
                Device(f"presets[{idx}].routing", equals=actual), Device("routing", equals=routes),
                Hub("/api/presets", path, equals=full),
                Hub("/api/presets", f"data.presets[{idx}].routing_source", equals="matrix"),
                Hub("/api/device-settings", f"data.presets.{slot}.routing", equals=full),
                CommandSent(f"r preset {slot}", channel="telnet", count=1), NoCommand("*"),
                DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
        notes="A custom save of output 1 stores the whole live routing on the matrix; the catalog and the "
              "hub's fallback copy report all eight outputs, not only the submitted one.",
    ))
