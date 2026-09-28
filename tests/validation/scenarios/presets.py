"""Matrix presets: recall, rename."""

from tools.validate.model import (
    CommandSent,
    Device,
    DeviceUnchanged,
    Hub,
    NoCommand,
    Response,
    Scenario,
    WsEvent,
    act,
)

from ._paths import CONTROL, DEVICE_SETTINGS, HUB_CORE, WEB_CORE, WEB_DRAWERS

# Seed presets: 3 = "PS5" -> [6] * 8. Hub-side names (tests/e2e/fixtures/data/device_settings.json):
# 1 "Apple TV Everywhere", 2 "Shield Night", 3-8 "Preset N".

SCENARIOS = [
    Scenario(
        id="presets.recall",
        title="Recall preset 3; the matrix applies its stored routing",
        features=("F-MTX-003",),
        client_features={"api": ("F-API-007", "F-API-035"), "browser": ("F-UI-005",)},
        clients=("api", "browser"),
        writes=("routing",),
        action=act("preset_recall", preset=3),
        expect=(
            Response(status=200),
            Device("routing", equals=[6] * 8),
            DeviceUnchanged(allow=("outputs[*].source", "routing")),
            CommandSent("preset set", {"index": 3}, count=1),
            WsEvent("preset_recall", {"preset": 3}),
        ),
        observe=("Do the displays now show the sources stored in preset 3?",),
        covers=(*HUB_CORE, *CONTROL, *WEB_CORE, *WEB_DRAWERS),
    ),
    Scenario(
        id="presets.rename",
        title="Rename preset 4; the new name is served by the API and nothing reaches the matrix",
        features=("F-MTX-005",),
        client_features={"api": ("F-API-037",), "browser": ("F-UI-006",)},
        clients=("api", "browser"),
        action=act("preset_rename", preset=4, name="Validation Night"),
        expect=(
            Response(status=200),
            Hub("/api/presets", "data.presets[3].name", equals="Validation Night"),
            WsEvent("device_settings", {"type": "preset", "number": 4, "name": "Validation Night"}),
            NoCommand("*"),
            DeviceUnchanged(),
        ),
        cleanup=(act("preset_rename", preset=4, name="Preset 4"),),
        covers=(*HUB_CORE, *DEVICE_SETTINGS, *WEB_CORE, *WEB_DRAWERS),
        notes="Preset names are hub-side (device settings); the matrix keeps its own names.",
    ),
    Scenario(
        id="presets.save_custom_mapping",
        title="Save a custom mapping (output 1 = input 8) into preset 6; the live routing is put back",
        features=("F-DOM-034",),
        client_features={"api": ("F-API-008",)},
        writes=("presets", "routing"),
        sim_state={"outputs": {"0": {"source": 3}}},
        action=act("request", method="POST", path="/api/preset/6/save", json={"routing": {"1": 8}}),
        expect=(
            Response(status=200, json={"success": True, "data": {"preset": 6}}),
            Device("presets[5].routing[0]", equals=8),
            Device("outputs[0].source", equals=3),
            # the matrix can only save its live routing: route, save, route back (DI-4)
            CommandSent("video switch", {"source": [1, 8]}, count=1),
            CommandSent("preset save", {"index": 6}, count=1),
            CommandSent("video switch", {"source": [1, 3]}, count=1),
            CommandSent("video switch", count=2),
            DeviceUnchanged(allow=("presets[5].*",)),
        ),
        observe=("Does output 1 show the same source as before the save?",),
        covers=(*HUB_CORE, *CONTROL, *DEVICE_SETTINGS),
        notes="API-14: the routing to restore is read fresh from the matrix under a lock; only the "
              "outputs the mapping changed are routed back.",
    ),
]
