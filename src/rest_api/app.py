"""
REST API Application Factory and Server.

Creates and configures the aiohttp web application with all routes.
"""

import logging
from typing import Optional
from aiohttp import web

from .utils import rate_limit_middleware, API_VERSION

# Import handlers from all modules
from .core import (
    handle_health, handle_info, handle_status, handle_presets,
    handle_inputs, handle_outputs, handle_set_input_name, handle_set_output_name,
)
from .control import (
    handle_preset, handle_preset_save, handle_switch,
    handle_power_on, handle_power_off,
    handle_input_next, handle_input_previous, handle_output_source,
)
from .outputs import (
    handle_full_status, handle_output_status, handle_input_status,
    handle_cable_status, handle_edid_status,
    handle_output_enable, handle_output_hdcp, handle_output_hdr,
    handle_output_scaler, handle_output_arc, handle_output_mute,
    handle_edid_modes, handle_set_input_edid,
)
from .cec import (
    handle_cec_commands, handle_cec_commands_by_type,
    handle_cec_input, handle_cec_output,
    handle_cec_status, handle_cec_capabilities,
    handle_input_capabilities, handle_output_capabilities,
    handle_cec_enable_input, handle_cec_enable_output,
)
from .audio import (
    handle_ext_audio_status, handle_ext_audio_modes,
    handle_set_ext_audio_mode, handle_set_ext_audio_enable,
    handle_set_ext_audio_source,
    handle_system_status, handle_device_info,
    handle_set_beep, handle_set_panel_lock, handle_system_reboot,
    handle_lcd_timeout_modes, handle_set_lcd_timeout,
)
from .scenes import (
    handle_list_scenes, handle_get_scene, handle_create_scene,
    handle_delete_scene, handle_recall_scene, handle_save_current_as_scene,
    handle_scene_cec_config, handle_auto_resolve_cec,
)
from .profiles import (
    handle_list_profiles, handle_get_profile, handle_create_profile,
    handle_update_profile, handle_delete_profile, handle_recall_profile,
    handle_profile_cec_config, handle_profile_macros, handle_reorder_profiles,
)
from .macros import (
    handle_list_macros, handle_get_macro, handle_create_macro,
    handle_update_macro, handle_delete_macro,
    handle_execute_macro, handle_test_macro,
)
from .static import (
    handle_web_ui, handle_kiosk_ui, handle_static_file, handle_api_root,
)
from .websocket import handle_websocket
from .device_settings import (
    handle_get_device_settings, handle_bulk_update_settings,
    handle_get_input_settings, handle_set_input_settings,
    handle_get_output_settings, handle_set_output_settings,
    init_device_settings,
)
from .settings import (
    handle_get_settings, handle_set_matrix_host, handle_test_matrix_connection,
)
from .themes import (
    handle_get_themes, handle_put_themes, handle_reset_themes,
)

_LOG = logging.getLogger("rest_api.app")


def create_rest_app() -> web.Application:
    """Create and configure the REST API application."""
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
    
    # Scenes
    app.router.add_get("/api/scenes", handle_list_scenes)
    app.router.add_get("/api/scene/{scene_id}", handle_get_scene)
    app.router.add_post("/api/scene", handle_create_scene)
    app.router.add_delete("/api/scene/{scene_id}", handle_delete_scene)
    app.router.add_post("/api/scene/{scene_id}/recall", handle_recall_scene)
    app.router.add_post("/api/scene/save-current", handle_save_current_as_scene)
    
    # Scene CEC Configuration
    app.router.add_get("/api/scene/{scene_id}/cec", handle_scene_cec_config)
    app.router.add_post("/api/scene/{scene_id}/cec", handle_scene_cec_config)
    app.router.add_put("/api/scene/{scene_id}/cec", handle_scene_cec_config)
    app.router.add_post("/api/scene/{scene_id}/cec/auto-resolve", handle_auto_resolve_cec)
    
    # Profiles
    app.router.add_get("/api/profiles", handle_list_profiles)
    app.router.add_get("/api/profile/{profile_id}", handle_get_profile)
    app.router.add_post("/api/profile", handle_create_profile)
    app.router.add_put("/api/profile/{profile_id}", handle_update_profile)
    app.router.add_delete("/api/profile/{profile_id}", handle_delete_profile)
    app.router.add_post("/api/profile/{profile_id}/recall", handle_recall_profile)
    app.router.add_get("/api/profile/{profile_id}/cec", handle_profile_cec_config)
    app.router.add_post("/api/profile/{profile_id}/cec", handle_profile_cec_config)
    app.router.add_put("/api/profile/{profile_id}/cec", handle_profile_cec_config)
    app.router.add_get("/api/profile/{profile_id}/macros", handle_profile_macros)
    app.router.add_post("/api/profile/{profile_id}/macros", handle_profile_macros)
    app.router.add_put("/api/profile/{profile_id}/macros", handle_profile_macros)
    app.router.add_post("/api/profiles/reorder", handle_reorder_profiles)
    
    # CEC Macros
    app.router.add_get("/api/cec/macros", handle_list_macros)
    app.router.add_get("/api/cec/macro/{macro_id}", handle_get_macro)
    app.router.add_post("/api/cec/macro", handle_create_macro)
    app.router.add_put("/api/cec/macro/{macro_id}", handle_update_macro)
    app.router.add_delete("/api/cec/macro/{macro_id}", handle_delete_macro)
    app.router.add_post("/api/cec/macro/{macro_id}/execute", handle_execute_macro)
    app.router.add_post("/api/cec/macro/{macro_id}/test", handle_test_macro)
    
    # Device Settings (persistent names, icons, colors)
    app.router.add_get("/api/device-settings", handle_get_device_settings)
    app.router.add_post("/api/device-settings", handle_bulk_update_settings)
    app.router.add_get("/api/device-settings/input/{input}", handle_get_input_settings)
    app.router.add_post("/api/device-settings/input/{input}", handle_set_input_settings)
    app.router.add_get("/api/device-settings/output/{output}", handle_get_output_settings)
    app.router.add_post("/api/device-settings/output/{output}", handle_set_output_settings)
    
    # Initialize device settings storage
    init_device_settings()
    
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
        self.app: Optional[web.Application] = None
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
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
