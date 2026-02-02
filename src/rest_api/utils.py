"""
Shared utilities for REST API.

Contains rate limiting, response helpers, and shared state.
"""

import json
import logging
import os
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Optional, Set

from aiohttp import web

# Support both package and direct imports
import sys
from pathlib import Path

# Ensure src/ directory is in path for sibling imports
_src_dir = Path(__file__).parent.parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

try:
    from config import SceneManager, ProfileManager
    from orei_matrix import OreiMatrix
    from cec_macros import MacroManager
except ImportError as e:
    # Log and continue with optional typing
    import logging
    logging.getLogger("rest_api").warning(f"Could not import manager classes: {e}")
    SceneManager = None  # type: ignore
    ProfileManager = None  # type: ignore
    OreiMatrix = None  # type: ignore
    MacroManager = None  # type: ignore

# API Version
API_VERSION = "2.10.0"

_LOG = logging.getLogger("rest_api")

# Web UI directory
_WEB_DIR = Path(__file__).parent.parent.parent / "web"

# Security configuration
# Set TRUST_PROXY_HEADERS=true if running behind a trusted reverse proxy
TRUST_PROXY_HEADERS = os.environ.get("TRUST_PROXY_HEADERS", "false").lower() == "true"

# =============================================================================
# Shared State (module-level variables)
# =============================================================================

# Reference to the matrix device (set by driver.py)
_matrix_device: Optional[OreiMatrix] = None
_input_names: dict[int, str] = {}  # Physical HDMI input port names (1-8)
_output_names: dict[int, str] = {}  # Physical HDMI output port names (1-8)
_config_file: Optional[Path] = None  # Path to config file for persistence
_scene_manager: Optional[SceneManager] = None  # Scene manager
_profile_manager: Optional[ProfileManager] = None  # Profile manager
_macro_manager: Optional[MacroManager] = None  # Macro manager

# WebSocket client connections
_ws_clients: Set[web.WebSocketResponse] = set()

# =============================================================================
# Rate Limiting
# =============================================================================

RATE_LIMIT_REQUESTS = 60  # Max requests per window
RATE_LIMIT_WINDOW = 10.0  # Window size in seconds
RATE_LIMIT_MAX_TRACKED_IPS = 10000  # Maximum unique IPs to track
_rate_limit_tracker: dict[str, list[float]] = defaultdict(list)
_rate_limit_last_cleanup = time.time()


def _cleanup_stale_rate_limits():
    """Remove stale entries from rate limit tracker to prevent memory exhaustion."""
    global _rate_limit_last_cleanup
    now = time.time()
    
    # Only run cleanup every 60 seconds
    if now - _rate_limit_last_cleanup < 60:
        return
    
    _rate_limit_last_cleanup = now
    window_start = now - RATE_LIMIT_WINDOW
    
    # Remove IPs with no recent activity
    stale_ips = [
        ip for ip, timestamps in _rate_limit_tracker.items()
        if not timestamps or max(timestamps) <= window_start
    ]
    
    for ip in stale_ips:
        del _rate_limit_tracker[ip]
    
    # If still too many, remove oldest entries
    if len(_rate_limit_tracker) > RATE_LIMIT_MAX_TRACKED_IPS:
        # Sort by most recent activity and keep only the most active
        sorted_ips = sorted(
            _rate_limit_tracker.items(),
            key=lambda x: max(x[1]) if x[1] else 0,
            reverse=True
        )
        _rate_limit_tracker.clear()
        for ip, timestamps in sorted_ips[:RATE_LIMIT_MAX_TRACKED_IPS]:
            _rate_limit_tracker[ip] = timestamps
    
    if stale_ips:
        _LOG.debug(f"Cleaned up {len(stale_ips)} stale rate limit entries")


def _check_rate_limit(client_ip: str) -> bool:
    """
    Check if a client has exceeded the rate limit.
    
    Uses a sliding window algorithm to track requests.
    
    :param client_ip: Client IP address
    :return: True if request is allowed, False if rate limited
    """
    # Periodically clean up stale entries
    _cleanup_stale_rate_limits()
    
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    
    # Clean up old timestamps
    _rate_limit_tracker[client_ip] = [
        ts for ts in _rate_limit_tracker[client_ip] if ts > window_start
    ]
    
    # Check if under limit
    if len(_rate_limit_tracker[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Record this request
    _rate_limit_tracker[client_ip].append(now)
    return True


def reset_rate_limiter():
    """Reset the rate limiter (for testing purposes)."""
    global _rate_limit_tracker
    _rate_limit_tracker.clear()


def _get_client_ip(request: web.Request) -> str:
    """
    Get client IP from request.
    
    Only trusts X-Forwarded-For header if TRUST_PROXY_HEADERS is enabled,
    to prevent IP spoofing and rate limit bypass attacks.
    """
    # Only check forwarded headers if explicitly trusted
    if TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
    
    # Fall back to peer address (direct connection)
    transport = request.transport
    if transport is not None:
        peername = transport.get_extra_info("peername")
        if peername:
            return peername[0]
    
    return "unknown"


# =============================================================================
# Response Helper
# =============================================================================

def _json_response(success: bool, data: Any = None, error: Optional[str] = None, status: int = 200) -> web.Response:
    """Create a standardized JSON response."""
    return web.json_response(
        {
            "success": success,
            "data": data,
            "error": error,
        },
        status=status,
    )


# =============================================================================
# Configuration Functions
# =============================================================================

def set_matrix_device(
    device, 
    input_names: Optional[dict[int, str]] = None, 
    output_names: Optional[dict[int, str]] = None,
    config_file: Optional[Path] = None,
    config_dir: Optional[str] = None
):
    """Set the matrix device reference for API handlers."""
    global _matrix_device, _input_names, _output_names, _config_file, _scene_manager, _profile_manager, _macro_manager
    _matrix_device = device
    if input_names:
        _input_names = input_names.copy()
    if output_names:
        _output_names = output_names.copy()
    if config_file:
        _config_file = config_file
    # Initialize managers with config directory
    if config_dir:
        _scene_manager = SceneManager(config_dir)
        _profile_manager = ProfileManager(config_dir)
        _macro_manager = MacroManager(config_dir)
    else:
        _scene_manager = SceneManager()
        _profile_manager = ProfileManager()
        _macro_manager = MacroManager()


def update_input_names(input_names: dict[int, str]):
    """Update input names cache."""
    global _input_names
    _input_names = input_names.copy()


def update_output_names(output_names: dict[int, str]):
    """Update output names cache."""
    global _output_names
    _output_names = output_names.copy()


def _save_names_to_config():
    """
    Save current input and output names to config file.
    Called when names are changed via the web UI.
    """
    if _config_file is None:
        _LOG.warning("Cannot save names: config file path not set")
        return False
    
    try:
        # Load existing config
        config = {}
        if _config_file.exists():
            with open(_config_file, "r") as f:
                config = json.load(f)
        
        # Update names (convert int keys to strings for JSON)
        config["input_names"] = {str(k): v for k, v in _input_names.items()}
        config["output_names"] = {str(k): v for k, v in _output_names.items()}
        
        # Save back
        with open(_config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        _LOG.info(f"Saved port names to {_config_file}")
        return True
    except Exception as e:
        _LOG.error(f"Failed to save port names: {e}")
        return False


def set_macro_cec_sender(sender):
    """Set the CEC sender function for macro execution."""
    if _macro_manager is not None:
        _macro_manager.set_cec_sender(sender)


# =============================================================================
# Accessor Functions (for use by other modules)
# =============================================================================

def get_matrix_device() -> Optional[OreiMatrix]:
    """Get the matrix device reference."""
    return _matrix_device


def get_input_names() -> dict[int, str]:
    """Get input names mapping."""
    return _input_names


def get_output_names() -> dict[int, str]:
    """Get output names mapping."""
    return _output_names


def get_scene_manager() -> Optional[SceneManager]:
    """Get the scene manager."""
    return _scene_manager


def get_profile_manager() -> Optional[ProfileManager]:
    """Get the profile manager."""
    return _profile_manager


def get_macro_manager() -> Optional[MacroManager]:
    """Get the macro manager."""
    return _macro_manager


def get_ws_clients() -> Set[web.WebSocketResponse]:
    """Get WebSocket client set."""
    return _ws_clients


def get_web_dir() -> Path:
    """Get the web UI directory path."""
    return _WEB_DIR


# =============================================================================
# Middleware
# =============================================================================

@web.middleware
async def rate_limit_middleware(request: web.Request, handler):
    """Rate limiting middleware for API requests.
    
    Excludes:
    - Static files (CSS, JS, assets, images)
    - Web UI pages (/ui, /kiosk, /)
    - WebSocket connections
    - Health check endpoint
    """
    path = request.path
    
    # Skip rate limiting for non-API paths
    # Static files and UI pages should never be rate limited
    if (path == "/ws" or 
        path == "/" or
        path.startswith("/ui") or
        path.startswith("/kiosk") or
        path.startswith("/css/") or
        path.startswith("/js/") or
        path.startswith("/assets/") or
        path.startswith("/api/health") or
        path.endswith(".ico") or
        path.endswith(".svg") or
        path.endswith(".png") or
        path.endswith(".jpg") or
        path.endswith(".webp")):
        return await handler(request)
    
    client_ip = _get_client_ip(request)
    
    if not _check_rate_limit(client_ip):
        _LOG.warning(f"Rate limit exceeded for {client_ip}")
        return _json_response(
            False,
            error="Rate limit exceeded. Please slow down.",
            status=429
        )
    
    return await handler(request)


# =============================================================================
# Function Aliases (for __init__.py backward compatibility)
# =============================================================================

# Alias: set_input_names -> update_input_names
set_input_names = update_input_names

# Alias: set_output_names -> update_output_names  
set_output_names = update_output_names


def set_scene_manager(manager):
    """Set the scene manager reference."""
    global _scene_manager
    _scene_manager = manager


def set_profile_manager(manager):
    """Set the profile manager reference."""
    global _profile_manager
    _profile_manager = manager


def set_macro_manager(manager):
    """Set the macro manager reference."""
    global _macro_manager
    _macro_manager = manager
