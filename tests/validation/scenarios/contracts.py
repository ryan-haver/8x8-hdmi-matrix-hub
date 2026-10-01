"""Focused read-only REST contracts, including saved values and device readback.

Evidence proves these reads and error cases, not the write routes sharing a
feature ID. Fixture-specific expectations are intentionally simulator-only.
"""

from tools.validate.model import DeviceUnchanged, Hub, NoCommand, NoProtocolWarnings, Response, Scenario, act

from ._paths import CEC, DEVICE_SETTINGS, HUB_CORE, OUTPUTS, SHORTCUTS

_DATA = "tests/e2e/fixtures/data"


def _read(sid, feature, path, expected, covers, *, status=200, checks=()):
    return Scenario(
        id=f"contracts.{sid}",
        title=f"GET {path}: HTTP {status}, correct read contract and unchanged matrix",
        kind="happy" if status == 200 else "failure",
        features=(feature,),
        targets=("sim",),
        action=act("request", method="GET", path=path),
        expect=(
            Response(status=status, json={"success": status == 200, **expected}),
            *checks,
            NoCommand("*"),
            DeviceUnchanged(),
            NoProtocolWarnings(),
        ),
        covers=(*HUB_CORE, *covers),
        notes="Read-only contract proof; other routes grouped under this feature ID require separate scenarios.",
    )


SCENARIOS = [
    _read("cec_status", "F-API-004", "/api/status/cec", {"error": None}, CEC,
          checks=tuple(
              Hub("/api/status/cec", f"data.cec_config.{kind}[{i}].cec_enabled", equals=i in enabled)
              for kind, enabled in (("inputs", {1, 4, 5}), ("outputs", {0, 1})) for i in range(8)
          )),
    _read("cables", "F-API-004", "/api/status/cables", {"data": {"telnetAvailable": True}, "error": None}, OUTPUTS,
          checks=tuple(
              Hub("/api/status/cables", f"data.{kind}[{i}].cableConnected", equals=i in connected)
              for kind, connected in (("inputs", {0, 1, 3, 4, 5, 6}), ("outputs", {0, 1})) for i in range(8)
          )),
    _read("cec_input_catalog", "F-API-016", "/api/cec/commands/input",
          {"data": {"device_type": "input"}, "error": None}, CEC,
          checks=(Hub("/api/cec/commands/input", "data.by_category.navigation[0].command", equals="UP"),)),
    _read("cec_output_catalog", "F-API-016", "/api/cec/commands/output",
          {"data": {"device_type": "output", "total_commands": 6,
                    "commands": ["POWER_ON", "POWER_OFF", "MUTE", "VOLUME_UP", "VOLUME_DOWN", "ACTIVE"]}, "error": None}, CEC),
    _read("cec_invalid_type", "F-API-016", "/api/cec/commands/nope",
          {"data": None, "error": "Type must be 'input' or 'output'"}, CEC, status=400),
    _read("device_settings", "F-API-017", "/api/device-settings",
          {"data": {"version": 2, "inputs": {"1": {"name": "PS3", "icon": "ps3"}},
                    "outputs": {"2": {"name": "Soundbar", "icon": "soundbar"}},
                    "favorite_presets": [1, 2], "dashboard_presets": [2]}, "error": None},
          (*DEVICE_SETTINGS, f"{_DATA}/device_settings.json")),
    _read("input_settings", "F-API-017", "/api/device-settings/input/1",
          {"data": {"input": 1, "name": "PS3", "icon": "ps3", "color": None}, "error": None},
          (*DEVICE_SETTINGS, f"{_DATA}/device_settings.json")),
    _read("output_settings", "F-API-017", "/api/device-settings/output/2",
          {"data": {"output": 2, "name": "Soundbar", "icon": "soundbar", "color": None}, "error": None},
          (*DEVICE_SETTINGS, f"{_DATA}/device_settings.json")),
    _read("invalid_input_settings", "F-API-017", "/api/device-settings/input/0",
          {"data": None, "error": "Input must be 1-8"}, DEVICE_SETTINGS, status=400),
    _read("invalid_output_settings", "F-API-017", "/api/device-settings/output/9",
          {"data": None, "error": "Output must be 1-8"}, DEVICE_SETTINGS, status=400),
    _read("shortcut_favorites", "F-API-024", "/api/shortcuts/favorites", {"error": None},
          (*SHORTCUTS, f"{_DATA}/system_shortcuts.json"),
          checks=(Hub("/api/shortcuts/favorites", "data.shortcuts[0].key", equals="route_all_to_output"),
                  Hub("/api/shortcuts/favorites", "data.shortcuts[0].favorite", equals=True))),
    _read("shortcut_dashboard", "F-API-024", "/api/shortcuts/dashboard", {"error": None},
          (*SHORTCUTS, f"{_DATA}/system_shortcuts.json"),
          checks=(Hub("/api/shortcuts/dashboard", "data.shortcuts[0].key", equals="power_off_all"),
                  Hub("/api/shortcuts/dashboard", "data.shortcuts[0].dashboard_visible", equals=True))),
    _read("shortcut_alias", "F-API-024", "/api/shortcuts/builtin.one_to_one",
          {"data": {"key": "route_one_to_one", "id": "builtin.one_to_one", "enabled": True}, "error": None}, SHORTCUTS),
    _read("shortcut_unknown", "F-API-024", "/api/shortcuts/nope",
          {"data": None, "error": "Shortcut 'nope' not found"}, SHORTCUTS, status=404),
    _read("themes", "F-API-026", "/api/themes",
          {"data": {"activePresetIndex": 0, "cardOpacity": 0.8, "hoverPreference": "primary"}, "error": None},
          ("src/rest_api/themes.py", "src/persistence.py", f"{_DATA}/themes.json"),
          checks=(Hub("/api/themes", "data.presets[0].name", equals="Tron Classic"),)),
    _read("ui_preferences", "F-API-026", "/api/ui/preferences",
          {"data": {"pinnedTabs": ["matrix", "dashboard", "inputs", "outputs", "profiles"],
                    "tabOrder": ["matrix", "dashboard", "inputs", "outputs", "profiles"]}, "error": None},
          ("src/rest_api/ui.py", "src/persistence.py", f"{_DATA}/ui_preferences.json")),
    _read("settings", "F-API-027", "/api/settings", {"data": {"connected": True}, "error": None},
          ("src/rest_api/settings.py",)),
    _read("system_info", "F-API-014", "/api/system/info",
          {"data": {"rest_api_version": "2.10.0"}, "error": None}, ("src/rest_api/system.py", "src/persistence.py")),
    _read("storage", "F-API-014", "/api/system/storage",
          {"data": {"data_dir_exists": True, "config_dir_exists": True}, "error": None},
          ("src/rest_api/system.py", "src/persistence.py")),
    _read("flic_buttons", "F-API-028", "/api/integrations/flic/buttons",
          {"data": {"buttons": [
              {"bdaddr": "80:e4:da:70:00:01", "name": "Couch Button", "serial": "BG12-A00001"},
              {"bdaddr": "80:e4:da:70:00:02", "name": "Kitchen Button", "serial": "BG12-A00002"},
          ]}, "error": None}, ("src/rest_api/integrations.py", "src/persistence.py", f"{_DATA}/flic_buttons.json")),
]
