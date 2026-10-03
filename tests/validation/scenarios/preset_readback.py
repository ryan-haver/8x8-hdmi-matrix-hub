"""Hub-saved preset mappings versus independently changed device slots.

BE-36 intentionally fails: the catalog never reads a changed device preset.
Passing cache reads prove save/cache behavior, not F-MTX-030 device readback.
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
        title=f"Preset {slot} has independent device routes: catalog should read the stored slot (BE-36)",
        features=("F-MTX-030",), targets=("sim",), kind="failure",
        sim_state={"presets": {str(idx): {"routing": routes, "saved": True}}},
        action=act("request", method="GET", path="/api/presets"),
        expect=(Response(status=200, json={"success": True}), Device(f"presets[{idx}].routing", equals=routes),
                Hub("/api/presets", path, equals=mapping, finding="BE-36"),
                CommandSent(f"r preset {slot}", channel="telnet", finding="BE-36"),
                NoCommand("preset get"), NoCommand("get routing status"), NoCommand("*"),
                DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
        notes="Known gap: the independently seeded device slot differs from the fixture's empty/partial hub cache.",
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
                Hub("/api/device-settings", f"data.presets.{slot}.routing", equals=mapping),
                NoCommand(f"r preset {slot}"), NoCommand("*"), DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
        notes="The setup saves the device and hub cache. Read action alone sends no preset query or write.",
    ))
    actual = [8, *routes[1:]]
    SCENARIOS.append(Scenario(
        id=f"preset_read.saved_partial_{slot}", title=f"Preset {slot}: custom save retains a partial hub mapping and full device routes",
        features=("F-DOM-034", "F-API-008"), targets=("sim",),
        sim_state={"outputs": {str(i): {"source": value} for i, value in enumerate(routes)}},
        setup=(act("request", method="POST", path=f"/api/preset/{slot}/save", json={"routing": {"1": 8}}),),
        action=act("request", method="GET", path="/api/presets"),
        expect=(Response(status=200, json={"success": True}),
                Device(f"presets[{idx}].routing", equals=actual), Device("routing", equals=routes),
                Hub("/api/presets", path, equals={"1": 8}),
                Hub("/api/device-settings", f"data.presets.{slot}.routing", equals={"1": 8}),
                NoCommand(f"r preset {slot}"), NoCommand("*"), DeviceUnchanged(), NoProtocolWarnings()),
        covers=_COVERS,
        notes="Custom save stores a full slot on the matrix but the catalog returns only the user-supplied mapping.",
    ))
