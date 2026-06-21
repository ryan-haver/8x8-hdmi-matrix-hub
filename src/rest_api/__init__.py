"""
REST API Package for OREI HDMI Matrix Integration.

This package provides a modular REST API for controlling the OREI BK-808 8x8 HDMI Matrix.
"""

# Import utils (has no circular dependencies)
# Import device settings functions
from .device_settings import (
    get_device_settings,
    get_input_setting,
    get_output_setting,
    get_preset_setting,
    init_device_settings,
    set_input_setting,
    set_output_setting,
    set_preset_routing,
)
from .themes import (
    init_themes,
)
from .ui import (
    init_ui_preferences,
)
from .utils import (
    API_VERSION,
    get_input_names,
    get_macro_manager,
    get_matrix_device,
    get_output_names,
    get_profile_manager,
    get_scene_manager,
    rate_limit_middleware,
    reset_rate_limiter,
    set_input_names,
    set_macro_cec_sender,
    set_macro_manager,
    set_matrix_device,
    set_output_names,
    set_profile_manager,
    set_scene_manager,
    # Aliases for backward compatibility
    update_input_names,
    update_output_names,
)

# Import WebSocket broadcast function
from .websocket import broadcast_status_update


# Lazy import for RestApiServer to avoid circular dependencies
def _get_rest_api_server():
    from .app import RestApiServer

    return RestApiServer


# Create a class proxy for RestApiServer
class RestApiServer:
    """REST API Server (lazy import wrapper for backward compatibility)."""

    _real_class = None

    def __new__(cls, *args, **kwargs):
        if cls._real_class is None:
            from .app import RestApiServer as _RestApiServer

            cls._real_class = _RestApiServer
        return cls._real_class(*args, **kwargs)


def create_rest_app(data_dir=None):
    """Create and configure the REST API application.

    :param data_dir: Optional explicit persistent data directory. When omitted,
        the directory is resolved from environment variables by
        :func:`persistence.get_data_dir`.
    """
    from pathlib import Path

    from .app import create_rest_app as _create_rest_app

    if data_dir is not None:
        import os

        resolved = str(Path(data_dir).resolve())
        # Set BOTH env vars so ProfileManager/MacroManager (which use
        # UC_CONFIG_HOME or HOME) and SystemShortcutManager/DashboardManager
        # (which use MATRIX_DATA_DIR via persistence) see the same path.
        os.environ["MATRIX_DATA_DIR"] = resolved
        os.environ["UC_CONFIG_HOME"] = resolved
    return _create_rest_app()


# Re-export for backward compatibility with driver.py
__all__ = [
    # Version
    "API_VERSION",
    # State setters
    "set_matrix_device",
    "set_input_names",
    "set_output_names",
    "set_scene_manager",
    "set_profile_manager",
    "set_macro_manager",
    # State getters
    "get_matrix_device",
    "get_input_names",
    "get_output_names",
    "get_scene_manager",
    "get_profile_manager",
    "get_macro_manager",
    # Aliases for driver.py backward compatibility
    "update_input_names",
    "update_output_names",
    "set_macro_cec_sender",
    # Middleware
    "rate_limit_middleware",
    "reset_rate_limiter",
    # WebSocket
    "broadcast_status_update",
    # Device Settings
    "init_device_settings",
    "get_device_settings",
    "get_input_setting",
    "get_output_setting",
    "get_preset_setting",
    "set_input_setting",
    "set_output_setting",
    "set_preset_routing",
    # Theme & UI Preferences (persistent storage init)
    "init_themes",
    "init_ui_preferences",
    # App factory and server
    "create_rest_app",
    "RestApiServer",
]
