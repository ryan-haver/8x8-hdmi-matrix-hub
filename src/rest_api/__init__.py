"""
REST API Package for OREI HDMI Matrix Integration.

This package provides a modular REST API for controlling the OREI BK-808 8x8 HDMI Matrix.
"""

# Import utils (has no circular dependencies)
from .utils import (
    API_VERSION,
    set_matrix_device,
    set_input_names,
    set_output_names,
    set_scene_manager,
    set_profile_manager,
    set_macro_manager,
    get_matrix_device,
    get_input_names,
    get_output_names,
    get_scene_manager,
    get_profile_manager,
    get_macro_manager,
    rate_limit_middleware,
    # Aliases for backward compatibility
    update_input_names,
    update_output_names,
    set_macro_cec_sender,
)

# Import WebSocket broadcast function
from .websocket import broadcast_status_update

# Import device settings functions
from .device_settings import (
    init_device_settings,
    get_device_settings,
    get_input_setting,
    get_output_setting,
    set_input_setting,
    set_output_setting,
)

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


def create_rest_app():
    """Create and configure the REST API application."""
    from .app import create_rest_app as _create_rest_app
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
    # WebSocket
    "broadcast_status_update",
    # Device Settings
    "init_device_settings",
    "get_device_settings",
    "get_input_setting",
    "get_output_setting",
    "set_input_setting",
    "set_output_setting",
    # App factory and server
    "create_rest_app",
    "RestApiServer",
]
