"""
REST API Application Factory and Server.

Creates and configures the aiohttp web application with all routes.
"""

import logging
from pathlib import Path

from aiohttp import web

from persistence import get_data_dir

from .audio import (
    handle_device_info,
    handle_ext_audio_modes,
    handle_ext_audio_status,
    handle_lcd_timeout_modes,
    handle_set_beep,
    handle_set_ext_audio_enable,
    handle_set_ext_audio_mode,
    handle_set_ext_audio_source,
    handle_set_lcd_timeout,
    handle_set_panel_lock,
    handle_system_reboot,
    handle_system_status,
)
from .cec import (
    handle_cec_capabilities,
    handle_cec_commands,
    handle_cec_commands_by_type,
    handle_cec_enable_input,
    handle_cec_enable_output,
    handle_cec_input,
    handle_cec_output,
    handle_cec_status,
    handle_input_capabilities,
    handle_output_capabilities,
)
from .control import (
    handle_input_next,
    handle_input_previous,
    handle_output_source,
    handle_power_off,
    handle_power_on,
    handle_preset,
    handle_preset_save,
    handle_switch,
)

# Import handlers from all modules
from .core import (
    handle_health,
    handle_info,
    handle_inputs,
    handle_outputs,
    handle_presets,
    handle_set_input_name,
    handle_set_output_name,
    handle_status,
)
from .dashboard_layout import (
    handle_add_card,
    handle_get_layout,
    handle_remove_card,
    handle_replace_layout,
)
from .device_settings import (
    handle_bulk_update_settings,
    handle_get_dashboard_presets,
    handle_get_device_settings,
    handle_get_favorite_presets,
    handle_get_input_settings,
    handle_get_output_settings,
    handle_set_dashboard_presets,
    handle_set_favorite_presets,
    handle_set_input_settings,
    handle_set_output_settings,
    handle_set_preset_name,
    handle_toggle_dashboard_preset,
    handle_toggle_favorite_preset,
    init_device_settings,
)
from .macros import (
    handle_create_macro,
    handle_delete_macro,
    handle_execute_macro,
    handle_get_macro,
    handle_list_favorite_macros,
    handle_list_macros,
    handle_test_macro,
    handle_toggle_macro_dashboard,
    handle_toggle_macro_favorite,
    handle_update_macro,
)
from .outputs import (
    handle_cable_status,
    handle_edid_modes,
    handle_edid_status,
    handle_full_status,
    handle_input_status,
    handle_output_arc,
    handle_output_enable,
    handle_output_hdcp,
    handle_output_hdr,
    handle_output_mute,
    handle_output_scaler,
    handle_output_status,
    handle_set_input_edid,
)
from .profiles import (
    handle_create_profile,
    handle_delete_profile,
    handle_get_profile,
    handle_list_favorite_profiles,
    handle_list_profiles,
    handle_profile_cec_config,
    handle_profile_execution_log,
    handle_profile_macros,
    handle_recall_profile,
    handle_reorder_profiles,
    handle_set_profile_dashboard,
    handle_set_profile_favorite,
    handle_toggle_profile_dashboard,
    handle_toggle_profile_favorite,
    handle_update_profile,
)
from .scenes import (
    handle_auto_resolve_cec as _handle_auto_resolve_cec_p7,
)
from .scenes import (
    handle_create_scene as _handle_create_scene_p7,
)
from .scenes import (
    handle_delete_scene as _handle_delete_scene_p7,
)
from .scenes import (
    handle_get_scene as _handle_get_scene_p7,
)
from .scenes import (
    handle_list_scenes as _handle_list_scenes_p7,
)
from .scenes import (
    handle_recall_scene as _handle_recall_scene_p7,
)
from .scenes import (
    handle_save_current_as_scene as _handle_save_current_as_scene_p7,
)
from .scenes import (
    handle_scene_cec_config as _handle_scene_cec_config_p7,
)
from .scenes_v2 import (
    handle_add_step,
    handle_clear_override,
    handle_execute_scene,
    handle_remove_step,
    handle_scene_history,
    handle_set_override,
    handle_update_scene,
    handle_validate_scene,
)
from .scenes_v2 import (
    handle_create_scene as handle_create_scene_v2,
)
from .scenes_v2 import (
    handle_delete_scene as handle_delete_scene_v2,
)
from .scenes_v2 import (
    handle_get_scene as handle_get_scene_v2,
)
from .scenes_v2 import (
    handle_list_scenes as handle_list_scenes_v2,
)
from .scenes_v2 import (
    set_phase8_scene_manager as _set_phase8_scene_manager,
)
from .settings import (
    handle_get_settings,
    handle_set_matrix_host,
    handle_test_matrix_connection,
)
from .static import (
    handle_api_root,
    handle_kiosk_ui,
    handle_static_file,
    handle_web_ui,
)
from .system import (
    handle_get_info,
    handle_get_storage,
)
from .system_shortcuts import (
    handle_create_shortcut,
    handle_delete_shortcut,
    handle_execute_shortcut,
    handle_get_shortcut,
    handle_list_dashboard_shortcuts,
    handle_list_favorite_shortcuts,
    handle_list_shortcuts,
    handle_reorder_shortcuts,
    handle_toggle_dashboard,
    handle_toggle_favorite,
    handle_update_shortcut,
)
from .themes import (
    handle_get_themes,
    handle_put_themes,
    handle_reset_themes,
    init_themes,
)
from .ui import (
    handle_get_ui_preferences,
    handle_set_ui_preferences,
    init_ui_preferences,
)
from .utils import API_VERSION, rate_limit_middleware
from .websocket import handle_websocket

_LOG = logging.getLogger("rest_api.app")


def create_rest_app(data_dir: Path | None = None) -> web.Application:
    """Create and configure the REST API application.

    :param data_dir: Optional explicit persistent data directory. When omitted,
        the directory is resolved from environment variables by
        :func:`persistence.get_data_dir` (priority: ``MATRIX_DATA_DIR``,
        then ``UC_CONFIG_HOME``, then local ``<project_root>/data``).
    """
    if data_dir is None:
        data_dir = get_data_dir()
    data_dir = Path(data_dir).resolve()

    app = web.Application(middlewares=[rate_limit_middleware])

    # Add CORS middleware for browser-based clients
    @web.middleware
    async def cors_middleware(request: web.Request, handler):
        if request.method == "OPTIONS":
            response = web.Response()
        else:
            response = await handler(request)

        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    app.middlewares.append(cors_middleware)

    # Web UI routes (serve before API routes)
    app.router.add_get("/ui", handle_web_ui)
    app.router.add_get("/ui/", handle_web_ui)
    app.router.add_get("/kiosk", handle_kiosk_ui)
    app.router.add_get("/kiosk/", handle_kiosk_ui)
    app.router.add_get("/css/{path:.*}", handle_static_file)
    app.router.add_get("/js/{path:.*}", handle_static_file)
    app.router.add_get("/assets/{path:.*}", handle_static_file)

    # Register API routes
    app.router.add_get("/", handle_api_root)
    app.router.add_get("/api", handle_api_root)

    # Health & Basic Status
    app.router.add_get("/api/health", handle_health)
    app.router.add_get("/api/info", handle_info)
    app.router.add_get("/api/status", handle_status)
    app.router.add_get("/api/presets", handle_presets)
    app.router.add_get("/api/inputs", handle_inputs)
    app.router.add_post("/api/input/{input}/name", handle_set_input_name)
    app.router.add_get("/api/outputs", handle_outputs)
    app.router.add_post("/api/output/{output}/name", handle_set_output_name)

    # Extended Status
    app.router.add_get("/api/status/full", handle_full_status)
    app.router.add_get("/api/status/outputs", handle_output_status)
    app.router.add_get("/api/status/inputs", handle_input_status)
    app.router.add_get("/api/status/cables", handle_cable_status)
    app.router.add_get("/api/status/edid", handle_edid_status)
    app.router.add_get("/api/status/cec", handle_cec_status)
    app.router.add_get("/api/status/system", handle_system_status)
    app.router.add_get("/api/status/device", handle_device_info)

    # EDID Management
    app.router.add_get("/api/edid/modes", handle_edid_modes)
    app.router.add_post("/api/input/{input}/edid", handle_set_input_edid)

    # Control
    app.router.add_post("/api/preset/{preset}", handle_preset)
    app.router.add_post("/api/switch", handle_switch)
    app.router.add_post("/api/power/on", handle_power_on)
    app.router.add_post("/api/power/off", handle_power_off)

    # Input Cycling
    app.router.add_post("/api/input/next", handle_input_next)
    app.router.add_post("/api/input/previous", handle_input_previous)
    app.router.add_post("/api/output/{output}/source", handle_output_source)

    # System Control
    app.router.add_post("/api/system/beep", handle_set_beep)
    app.router.add_post("/api/system/panel_lock", handle_set_panel_lock)
    app.router.add_post("/api/system/reboot", handle_system_reboot)
    app.router.add_get("/api/system/lcd/modes", handle_lcd_timeout_modes)
    app.router.add_post("/api/system/lcd", handle_set_lcd_timeout)

    # Persistent storage introspection (for verifying volume mounts)
    app.router.add_get("/api/system/storage", handle_get_storage)
    app.router.add_get("/api/system/info", handle_get_info)

    # Unified Shortcuts (Phase 8 Consolidated & Phase 7 Backward Compat)
    for prefix in ("/api/shortcuts", "/api/system-shortcuts"):
        app.router.add_get(prefix, handle_list_shortcuts)
        app.router.add_post(prefix, handle_create_shortcut)
        app.router.add_get(f"{prefix}/favorites", handle_list_favorite_shortcuts)
        app.router.add_get(f"{prefix}/dashboard", handle_list_dashboard_shortcuts)
        app.router.add_put(f"{prefix}/reorder", handle_reorder_shortcuts)
        app.router.add_get(f"{prefix}/{{key}}", handle_get_shortcut)
        app.router.add_put(f"{prefix}/{{key}}", handle_update_shortcut)
        app.router.add_delete(f"{prefix}/{{key}}", handle_delete_shortcut)
        app.router.add_post(f"{prefix}/{{key}}/favorite", handle_toggle_favorite)
        app.router.add_post(f"{prefix}/{{key}}/dashboard", handle_toggle_dashboard)
        app.router.add_post(f"{prefix}/{{key}}/execute", handle_execute_shortcut)

    # Dashboard Layout (Phase 7) — server-backed card ordering
    app.router.add_get("/api/dashboard/layout", handle_get_layout)
    app.router.add_put("/api/dashboard/layout", handle_replace_layout)
    app.router.add_post("/api/dashboard/cards", handle_add_card)
    app.router.add_delete("/api/dashboard/cards", handle_remove_card)

    # Advanced Output Control
    app.router.add_post("/api/output/{output}/enable", handle_output_enable)
    app.router.add_post("/api/output/{output}/hdcp", handle_output_hdcp)
    app.router.add_post("/api/output/{output}/hdr", handle_output_hdr)
    app.router.add_post("/api/output/{output}/scaler", handle_output_scaler)
    app.router.add_post("/api/output/{output}/arc", handle_output_arc)
    app.router.add_post("/api/output/{output}/mute", handle_output_mute)

    # CEC Control
    app.router.add_get("/api/cec/commands", handle_cec_commands)
    app.router.add_get("/api/cec/commands/{type}", handle_cec_commands_by_type)
    app.router.add_get("/api/cec/capabilities", handle_cec_capabilities)
    app.router.add_get("/api/cec/input/{input}/capabilities", handle_input_capabilities)
    app.router.add_get("/api/cec/output/{output}/capabilities", handle_output_capabilities)
    # CEC enable must be registered BEFORE the generic command routes
    app.router.add_post("/api/cec/input/{port}/enable", handle_cec_enable_input)
    app.router.add_post("/api/cec/output/{port}/enable", handle_cec_enable_output)
    app.router.add_post("/api/cec/input/{input}/{command}", handle_cec_input)
    app.router.add_post("/api/cec/output/{output}/{command}", handle_cec_output)

    # Preset Management
    app.router.add_post("/api/preset/{preset}/save", handle_preset_save)

    # External Audio
    app.router.add_get("/api/status/ext-audio", handle_ext_audio_status)
    app.router.add_get("/api/ext-audio/modes", handle_ext_audio_modes)
    app.router.add_post("/api/ext-audio/mode", handle_set_ext_audio_mode)
    app.router.add_post("/api/ext-audio/{output}/enable", handle_set_ext_audio_enable)
    app.router.add_post("/api/ext-audio/{output}/source", handle_set_ext_audio_source)

    # Scenes (Phase 7 backward compat — aliased to avoid collision)
    app.router.add_get("/api/scenes", _handle_list_scenes_p7)
    app.router.add_get("/api/scene/{scene_id}", _handle_get_scene_p7)
    app.router.add_post("/api/scene", _handle_create_scene_p7)
    app.router.add_delete("/api/scene/{scene_id}", _handle_delete_scene_p7)
    app.router.add_post("/api/scene/{scene_id}/recall", _handle_recall_scene_p7)
    app.router.add_post("/api/scene/save-current", _handle_save_current_as_scene_p7)

    # Scene CEC Configuration (Phase 7 backward compat)
    app.router.add_get("/api/scene/{scene_id}/cec", _handle_scene_cec_config_p7)
    app.router.add_post("/api/scene/{scene_id}/cec", _handle_scene_cec_config_p7)
    app.router.add_put("/api/scene/{scene_id}/cec", _handle_scene_cec_config_p7)
    app.router.add_post("/api/scene/{scene_id}/cec/auto-resolve", _handle_auto_resolve_cec_p7)

    # Profiles
    app.router.add_get("/api/profiles", handle_list_profiles)
    app.router.add_get("/api/profile/{profile_id}", handle_get_profile)
    app.router.add_post("/api/profile", handle_create_profile)
    app.router.add_put("/api/profile/{profile_id}", handle_update_profile)
    app.router.add_delete("/api/profile/{profile_id}", handle_delete_profile)
    app.router.add_post("/api/profile/{profile_id}/recall", handle_recall_profile)
    app.router.add_get("/api/profile/{profile_id}/cec", handle_profile_cec_config)
    app.router.add_get("/api/profile/{profile_id}/execution-log", handle_profile_execution_log)
    app.router.add_post("/api/profile/{profile_id}/cec", handle_profile_cec_config)
    app.router.add_put("/api/profile/{profile_id}/cec", handle_profile_cec_config)
    app.router.add_get("/api/profile/{profile_id}/macros", handle_profile_macros)
    app.router.add_post("/api/profile/{profile_id}/macros", handle_profile_macros)
    app.router.add_put("/api/profile/{profile_id}/macros", handle_profile_macros)
    app.router.add_post("/api/profiles/reorder", handle_reorder_profiles)

    # Profile surface-visibility (Phase 7: favorite + dashboard)
    app.router.add_get("/api/profiles/favorites", handle_list_favorite_profiles)
    app.router.add_post("/api/profile/{profile_id}/favorite", handle_toggle_profile_favorite)
    app.router.add_put("/api/profile/{profile_id}/favorite", handle_set_profile_favorite)
    app.router.add_post("/api/profile/{profile_id}/dashboard", handle_toggle_profile_dashboard)
    app.router.add_put("/api/profile/{profile_id}/dashboard", handle_set_profile_dashboard)

    # CEC Macros
    app.router.add_get("/api/cec/macros", handle_list_macros)
    app.router.add_get("/api/cec/macro/{macro_id}", handle_get_macro)
    app.router.add_post("/api/cec/macro", handle_create_macro)
    app.router.add_put("/api/cec/macro/{macro_id}", handle_update_macro)
    app.router.add_delete("/api/cec/macro/{macro_id}", handle_delete_macro)
    app.router.add_post("/api/cec/macro/{macro_id}/execute", handle_execute_macro)
    app.router.add_post("/api/cec/macro/{macro_id}/test", handle_test_macro)

    # Macro surface-visibility (Phase 7: favorite + dashboard)
    app.router.add_get("/api/cec/macros/favorites", handle_list_favorite_macros)
    app.router.add_post("/api/cec/macro/{macro_id}/favorite", handle_toggle_macro_favorite)
    app.router.add_post("/api/cec/macro/{macro_id}/dashboard", handle_toggle_macro_dashboard)

    # Device Settings (persistent names, icons, colors)
    app.router.add_get("/api/device-settings", handle_get_device_settings)
    app.router.add_post("/api/device-settings", handle_bulk_update_settings)
    app.router.add_get("/api/device-settings/input/{input}", handle_get_input_settings)
    app.router.add_post("/api/device-settings/input/{input}", handle_set_input_settings)
    app.router.add_get("/api/device-settings/output/{output}", handle_get_output_settings)
    app.router.add_post("/api/device-settings/output/{output}", handle_set_output_settings)
    app.router.add_post("/api/device-settings/preset/{preset}/name", handle_set_preset_name)

    # Hardware-preset surface-visibility (Phase 7: favorite + dashboard)
    app.router.add_get("/api/device-settings/favorite-presets", handle_get_favorite_presets)
    app.router.add_put("/api/device-settings/favorite-presets", handle_set_favorite_presets)
    app.router.add_post("/api/device-settings/favorite-presets/{preset}/toggle", handle_toggle_favorite_preset)
    app.router.add_get("/api/device-settings/dashboard-presets", handle_get_dashboard_presets)
    app.router.add_put("/api/device-settings/dashboard-presets", handle_set_dashboard_presets)
    app.router.add_post("/api/device-settings/dashboard-presets/{preset}/toggle", handle_toggle_dashboard_preset)

    # Phase 8: Unified Scene (grouping of Profiles + System Actions)
    app.router.add_get("/api/v2/scenes", handle_list_scenes_v2)
    app.router.add_post("/api/v2/scenes", handle_create_scene_v2)
    app.router.add_get("/api/v2/scenes/{scene_id}", handle_get_scene_v2)
    app.router.add_put("/api/v2/scenes/{scene_id}", handle_update_scene)
    app.router.add_delete("/api/v2/scenes/{scene_id}", handle_delete_scene_v2)
    app.router.add_post("/api/v2/scenes/{scene_id}/execute", handle_execute_scene)
    app.router.add_get("/api/v2/scenes/{scene_id}/history", handle_scene_history)
    app.router.add_post("/api/v2/scenes/{scene_id}/validate", handle_validate_scene)
    app.router.add_put("/api/v2/scenes/{scene_id}/override", handle_set_override)
    app.router.add_delete("/api/v2/scenes/{scene_id}/override", handle_clear_override)
    app.router.add_post("/api/v2/scenes/{scene_id}/steps", handle_add_step)
    app.router.add_delete("/api/v2/scenes/{scene_id}/steps/{index}", handle_remove_step)

    # Initialize persistent storage modules. All three share the same
    # ``data_dir`` which is resolved from ``MATRIX_DATA_DIR``,
    # ``UC_CONFIG_HOME``, or the local ``<project_root>/data`` default.
    # See :mod:`persistence` for resolution details.
    init_device_settings(data_dir)
    init_themes(data_dir)
    init_ui_preferences(data_dir)

    # Phase 8: Initialize Scene Manager and inject into scenes_v2
    from scene_manager import SceneManager as Phase8SceneManager

    phase8_sm = Phase8SceneManager(data_dir)
    _set_phase8_scene_manager(phase8_sm)
    _LOG.info("Phase 8 SceneManager initialized with %d scenes", len(phase8_sm.list_scenes()))

    _LOG.info(f"Persistent storage initialized at {data_dir}")

    # WebSocket for real-time updates
    app.router.add_get("/ws", handle_websocket)

    # Backend Settings (matrix host configuration)
    app.router.add_get("/api/settings", handle_get_settings)
    app.router.add_post("/api/settings/matrix-host", handle_set_matrix_host)
    app.router.add_post("/api/settings/test-connection", handle_test_matrix_connection)

    # Theme Settings (user UI theme preferences)
    app.router.add_get("/api/themes", handle_get_themes)
    app.router.add_put("/api/themes", handle_put_themes)
    app.router.add_post("/api/themes/reset", handle_reset_themes)

    # UI Preferences Settings
    app.router.add_get("/api/ui/preferences", handle_get_ui_preferences)
    app.router.add_put("/api/ui/preferences", handle_set_ui_preferences)

    _LOG.info(f"REST API v{API_VERSION} application created with all routes registered")
    return app


class RestApiServer:
    """REST API server wrapper for integration with the main driver."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        """
        Initialize the REST API server.

        :param host: Host to bind to (default: 0.0.0.0 for all interfaces)
        :param port: Port to listen on (default: 8080)
        """
        self.host = host
        self.port = port
        self.app: web.Application | None = None
        self.runner: web.AppRunner | None = None
        self.site: web.TCPSite | None = None
        self._running = False

    async def start(self):
        """Start the REST API server."""
        if self._running:
            _LOG.warning("REST API server is already running")
            return

        try:
            self.app = create_rest_app()
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()

            self.site = web.TCPSite(self.runner, self.host, self.port)
            await self.site.start()

            self._running = True
            _LOG.info(f"✓ REST API server started on http://{self.host}:{self.port}")
            _LOG.info(f"  API docs: http://{self.host}:{self.port}/api")
        except Exception as e:
            _LOG.error(f"Failed to start REST API server: {e}")
            raise

    async def stop(self):
        """Stop the REST API server."""
        if not self._running:
            return

        try:
            if self.runner:
                await self.runner.cleanup()
            self._running = False
            _LOG.info("REST API server stopped")
        except Exception as e:
            _LOG.warning(f"Error stopping REST API server: {e}")

    @property
    def running(self) -> bool:
        """Check if server is running."""
        return self._running
