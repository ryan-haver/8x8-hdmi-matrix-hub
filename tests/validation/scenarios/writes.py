"""Simulator-only saved-write contracts; storage refusals are regression tested in pytest.

Run against disposable fixture data: creation, registration and deletion leave
hub data changed. Device writes are restored by the runner's simulator reset.
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

from ._paths import CEC, DEVICE_SETTINGS, HUB_CORE, PROFILES, SHORTCUTS

_USER = "user.a1b2c3d4e5f6"
_PREFS = {"pinnedTabs": ["profiles", "matrix"], "tabOrder": ["profiles", "matrix", "dashboard", "inputs", "outputs"]}
_THEME = {
    "presets": [{"id": f"preset-{i}", "name": f"Saved {i}", "primaryH": i * 20, "secondaryH": i * 30}
                for i in range(1, 5)],
    "activePresetIndex": 2, "cardOpacity": 0.6, "hoverPreference": "secondary",
}


def _write(sid, feature, method, path, payload, expected, covers, *, checks=(), setup=(), cleanup=(),
           status=200, device=(), allow=()):
    return Scenario(
        id=f"writes.{sid}",
        title=f"{method} {path}: correct response and saved/device readback",
        features=(feature,), targets=("sim",),
        action=act("request", method=method, path=path, json=payload),
        setup=setup, cleanup=cleanup,
        expect=(Response(status=status, json={"success": True, "error": None, "data": expected}),
                *checks, *device, *(() if device else (NoCommand("*"),)),
                DeviceUnchanged(allow=allow), NoProtocolWarnings()),
        covers=(*HUB_CORE, *covers, "src/_file_io.py"),
        notes="Disposable simulator and hub data. Pytest additionally proves disk reload and storage-failure behavior.",
    )


SCENARIOS = [
    _write("cec_output_enable", "F-API-016", "POST", "/api/cec/output/8/enable", {"enabled": True},
           {"port_type": "output", "port": 8, "cec_enabled": True}, CEC,
           checks=(Hub("/api/status/cec", "data.cec_config.outputs[7].cec_enabled", equals=True),),
           device=(Device("outputs[7].cec_enabled", equals=1), CommandSent("set cec index", count=1)),
           allow=("outputs[7].cec_enabled",)),
    _write("input_settings", "F-API-017", "POST", "/api/device-settings/input/8",
           {"name": "Saved source"}, {"input": 8, "name": "Saved source"}, DEVICE_SETTINGS,
           checks=(Hub("/api/device-settings", "data.inputs.8.name", equals="Saved source"),),
           cleanup=(act("request", method="POST", path="/api/device-settings/input/8", json={"name": "Input 8"}),)),
    _write("output_settings", "F-API-017", "POST", "/api/device-settings/output/8",
           {"name": "Saved room"}, {"output": 8, "name": "Saved room"}, DEVICE_SETTINGS,
           checks=(Hub("/api/device-settings", "data.outputs.8.name", equals="Saved room"),),
           cleanup=(act("request", method="POST", path="/api/device-settings/output/8", json={"name": "Output 8"}),)),
    _write("bulk_settings", "F-API-017", "POST", "/api/device-settings",
           {"inputs": {"8": {"name": "Bulk source"}}, "outputs": {"8": {"name": "Bulk room"}}},
           {"updated_inputs": [8], "updated_outputs": [8], "errors": None}, DEVICE_SETTINGS,
           checks=(Hub("/api/device-settings/input/8", "data.name", equals="Bulk source"),
                   Hub("/api/device-settings/output/8", "data.name", equals="Bulk room")),
           cleanup=(act("request", method="POST", path="/api/device-settings", json={
               "inputs": {"8": {"name": "Input 8"}}, "outputs": {"8": {"name": "Output 8"}},
           }),)),
    _write("preset_name", "F-API-017", "POST", "/api/device-settings/preset/8/name", {"name": "Evening"},
           {"preset": 8, "name": "Evening"}, DEVICE_SETTINGS,
           checks=(Hub("/api/device-settings", "data.presets.8.name", equals="Evening"),),
           cleanup=(act("request", method="POST", path="/api/device-settings/preset/8/name", json={"name": "Preset 8"}),)),
    _write("output_name", "F-API-018", "POST", "/api/output/8/name", {"name": "Living Room"},
           {"output": 8, "name": "Living Room"}, DEVICE_SETTINGS,
           checks=(Hub("/api/status", "data.output_names.8", equals="Living Room"),),
           device=(Device("outputs[7].name", equals="Living Room"), CommandSent("set output name", count=1)),
           allow=("outputs[7].name",)),
    _write("profile_cec", "F-API-019", "PUT", "/api/profile/movie_night/cec",
           {"cec_config": {"nav_targets": ["input:5"], "volume_targets": ["output:8"], "auto_resolved": False}},
           {"profile_id": "movie_night", "cec_config": {"nav_targets": ["input:5"], "volume_targets": ["output:8"]}},
           PROFILES, checks=(Hub("/api/profile/movie_night/cec", "data.cec_config.nav_targets", equals=["input:5"]),),
           cleanup=(act("request", method="PUT", path="/api/profile/movie_night/cec", json={"cec_config": {
               "nav_targets": ["input:2"], "playback_targets": ["input:2"], "volume_targets": ["output:2"],
               "power_on_targets": ["input:2", "output:1"], "power_off_targets": ["input:2", "output:1"],
               "auto_resolved": False,
           }}),)),
    _write("profile_macros", "F-API-019", "PUT", "/api/profile/movie_night/macros",
           {"macros": ["macro_all_off"], "power_on_macro": None, "power_off_macro": "macro_all_off"},
           {"profile_id": "movie_night", "macros": ["macro_all_off"], "power_on_macro": None,
            "power_off_macro": "macro_all_off"}, PROFILES,
           checks=(Hub("/api/profile/movie_night/macros", "data.power_on_macro", equals=None),
                   Hub("/api/profile/movie_night", "data.power_off_macro", equals="macro_all_off")),
           cleanup=(act("request", method="PUT", path="/api/profile/movie_night/macros", json={
               "macros": ["macro_tv_on"], "power_on_macro": "macro_tv_on", "power_off_macro": "macro_all_off",
           }),)),
    _write("profile_reorder", "F-API-019", "POST", "/api/profiles/reorder",
           {"profiles": [{"id": "game_day", "pinned": True, "pin_order": 0},
                         {"id": "movie_night", "pinned": False, "pin_order": 1}]},
           {"updated": ["game_day", "movie_night"], "errors": None}, PROFILES,
           checks=(Hub("/api/profile/game_day", "data.pin_order", equals=0),
                   Hub("/api/profile/movie_night", "data.pinned", equals=False)),
           cleanup=(act("request", method="POST", path="/api/profiles/reorder", json={"profiles": [
               {"id": "game_day", "pinned": True, "pin_order": 1},
               {"id": "movie_night", "pinned": True, "pin_order": 0},
           ]}),)),
    _write("shortcut_create", "F-API-024", "POST", "/api/shortcuts",
           {"name": "Saved action", "type": "route_all_to_output", "params": {"input": 5, "output": 8}},
           {"label": "Saved action", "builtin": False, "type": "route_all_to_output", "params": {"input": 5, "output": 8}},
           SHORTCUTS, status=201),
    _write("shortcut_update", "F-API-024", "PUT", f"/api/shortcuts/{_USER}",
           {"label": "Evening action", "icon": "tv"}, {"label": "Evening action", "icon": "tv"}, SHORTCUTS,
           checks=(Hub(f"/api/shortcuts/{_USER}", "data.label", equals="Evening action"),),
           cleanup=(act("request", method="PUT", path=f"/api/shortcuts/{_USER}", json={"label": "Shield → TV", "icon": "📺"}),)),
    _write("shortcut_favorite", "F-API-024", "POST", f"/api/shortcuts/{_USER}/favorite", {},
           {"favorite": True}, SHORTCUTS,
           setup=(act("request", method="PUT", path=f"/api/shortcuts/{_USER}", json={"favorite": False}),),
           checks=(Hub(f"/api/shortcuts/{_USER}", "data.favorite", equals=True),)),
    _write("shortcut_dashboard", "F-API-024", "POST", f"/api/shortcuts/{_USER}/dashboard", {},
           {"dashboard_visible": True}, SHORTCUTS,
           setup=(act("request", method="PUT", path=f"/api/shortcuts/{_USER}", json={"dashboard_visible": False}),),
           checks=(Hub(f"/api/shortcuts/{_USER}", "data.dashboard_visible", equals=True),)),
    _write("shortcut_reorder", "F-API-024", "PUT", "/api/shortcuts/reorder",
           {"ordered_ids": [_USER, "builtin.one_to_one"]}, {"reordered": True, "count": 2}, SHORTCUTS,
           checks=(Hub(f"/api/shortcuts/{_USER}", "data.order", equals=0),
                   Hub("/api/shortcuts/builtin.one_to_one", "data.order", equals=1)),
           cleanup=(act("request", method="PUT", path=f"/api/shortcuts/{_USER}", json={"order": 30}),)),
    _write("shortcut_execute", "F-API-024", "POST", "/api/shortcuts/route_all_to_output/execute",
           {"params": {"input": 7, "output": 8}}, {"success": True}, SHORTCUTS,
           device=(Device("outputs[7].source", equals=7), CommandSent("video switch", {"source": [8, 7]}, count=1)),
           allow=("outputs[7].source", "routing")),
    _write("themes", "F-API-026", "PUT", "/api/themes", _THEME, _THEME, ("src/rest_api/themes.py",),
           checks=(Hub("/api/themes", "data", equals=_THEME),)),
    _write("themes_reset", "F-API-026", "POST", "/api/themes/reset", {},
           {"activePresetIndex": 0, "cardOpacity": 0.8, "hoverPreference": "primary"}, ("src/rest_api/themes.py",),
           setup=(act("request", method="PUT", path="/api/themes", json=_THEME),),
           checks=(Hub("/api/themes", "data.presets[0].name", equals="Tron Classic"),)),
    _write("ui_preferences", "F-API-026", "PUT", "/api/ui/preferences", _PREFS, _PREFS, ("src/rest_api/ui.py",),
           checks=(Hub("/api/ui/preferences", "data", equals=_PREFS),),
           cleanup=(act("request", method="PUT", path="/api/ui/preferences", json={
               "pinnedTabs": ["matrix", "dashboard", "inputs", "outputs", "profiles"],
               "tabOrder": ["matrix", "dashboard", "inputs", "outputs", "profiles"],
           }),)),
    _write("connection_test", "F-API-027", "POST", "/api/settings/test-connection", {},
           {"connected": True}, ("src/rest_api/settings.py",),
           checks=(Hub("/api/settings", "data.connected", equals=True),)),
    _write("flic_register", "F-API-028", "POST", "/api/integrations/flic/register",
           {"buttons": [{"bdaddr": "80:e4:da:70:00:01", "name": "Renamed", "serial": "BG12-A00001"}]},
           {"count": 2}, ("src/rest_api/integrations.py", "src/persistence.py"),
           checks=(Hub("/api/integrations/flic/buttons", "data.buttons[0].name", equals="Renamed"),),
           cleanup=(act("request", method="POST", path="/api/integrations/flic/register", json={
               "buttons": [{"bdaddr": "80:e4:da:70:00:01", "name": "Couch Button", "serial": "BG12-A00001"}],
           }),)),
    Scenario(
        id="writes.shortcut_delete_builtin", title="Built-in shortcut deletion is refused without changing the device",
        features=("F-API-024",), targets=("sim",), kind="failure",
        action=act("request", method="DELETE", path="/api/shortcuts/builtin.one_to_one"),
        expect=(Response(status=400, json={"success": False, "error": "Built-in shortcuts cannot be deleted"}),
                Hub("/api/shortcuts/builtin.one_to_one", "data.builtin", equals=True),
                NoCommand("*"), DeviceUnchanged(), NoProtocolWarnings()),
        covers=(*HUB_CORE, *SHORTCUTS),
        notes="Successful user shortcut deletion and disk reload are covered by tests/sim/test_sim_rest_writes.py.",
    ),
]
