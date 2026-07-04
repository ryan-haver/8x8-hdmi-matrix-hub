"""
Shared utilities for REST API.

Contains rate limiting, response helpers, and shared state.
"""

from __future__ import annotations

import asyncio
import ipaddress
import json
import logging
import os

# Support both package and direct imports
import sys
import time
import uuid as _uuid
from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

from aiohttp import web

if TYPE_CHECKING:
    from cec_macros import MacroManager
    from config import ProfileManager, SceneManager
    from dashboard_layout import DashboardLayoutManager
    from system_shortcuts import SystemShortcutManager

# Ensure src/ directory is in path for sibling imports
_src_dir = Path(__file__).parent.parent
if str(_src_dir) not in sys.path:
    sys.path.insert(0, str(_src_dir))

_LOG = logging.getLogger("rest_api")

# OreiMatrix is always needed - critical import that should fail fast
from orei_matrix import OreiMatrix


# Lazy import helpers for manager classes to avoid circular import risk
def _get_scene_manager(config_dir):
    """Get SceneManager instance with lazy import."""
    from config import SceneManager

    return SceneManager(config_dir)


def _get_profile_manager(config_dir):
    """Get ProfileManager instance with lazy import."""
    from config import ProfileManager

    return ProfileManager(config_dir)


def _get_macro_manager(config_dir):
    """Get MacroManager instance with lazy import."""
    from cec_macros import MacroManager

    return MacroManager(config_dir)


def _get_dashboard_layout_manager(data_dir):
    """Get DashboardLayoutManager instance with lazy import."""
    from dashboard_layout import DashboardLayoutManager

    return DashboardLayoutManager(data_dir)


def _get_system_shortcut_manager(data_dir):
    """Get SystemShortcutManager instance with lazy import."""
    from system_shortcuts import SystemShortcutManager

    return SystemShortcutManager(data_dir)


def _get_data_dir():
    """Get data directory with lazy import."""
    from persistence import get_data_dir

    return get_data_dir()


# API Version
API_VERSION = "2.10.0"

# Web UI directory
_WEB_DIR = Path(__file__).parent.parent.parent / "web"

# Security configuration
# Set TRUST_PROXY_HEADERS=true if running behind a trusted reverse proxy
TRUST_PROXY_HEADERS = os.environ.get("TRUST_PROXY_HEADERS", "false").lower() == "true"


def safe_error_message(exc, context: str) -> str:
    """
    Log full exception with stack trace, return sanitized message.

    Returns a client-safe error string with a correlation ID so
    internal details (hostnames, firmware versions, stack traces)
    are never leaked to API consumers.
    """
    correlation_id = _uuid.uuid4().hex[:8]
    _LOG.exception("[%s] %s: %s", correlation_id, context, exc)
    return f"Internal server error (ref: {correlation_id})"


# =============================================================================
# Shared State (module-level variables)
# =============================================================================

# Reference to the matrix device (set by driver.py)
_matrix_device: OreiMatrix | None = None
_input_names: dict[int, str] = {}  # Physical HDMI input port names (1-8)
_output_names: dict[int, str] = {}  # Physical HDMI output port names (1-8)
_config_file: Path | None = None  # Path to config file for persistence
_scene_manager: SceneManager | None = None  # Scene manager
_profile_manager: ProfileManager | None = None  # Profile manager
_macro_manager: MacroManager | None = None  # Macro manager
_system_shortcut_manager: SystemShortcutManager | None = None  # System shortcuts
_dashboard_layout_manager: DashboardLayoutManager | None = None  # Dashboard layout

# WebSocket client connections
_ws_clients: set[web.WebSocketResponse] = set()

# =============================================================================
# Concurrency Primitives
# =============================================================================
# Async locks protecting concurrent access to module-level shared state.
# Without these, concurrent REST handlers / WebSocket / polling tasks can
# trigger ``RuntimeError: dictionary changed size during iteration`` or
# torn-read data corruption.

_state_lock = asyncio.Lock()          # Protects _matrix_device, _input_names,
                                      # _output_names, _config_file, and
                                      # all *_manager globals.
_ws_clients_lock = asyncio.Lock()    # Protects _ws_clients set.
_rate_limit_lock = asyncio.Lock()     # Protects _rate_limit_tracker dict.

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
        ip for ip, timestamps in _rate_limit_tracker.items() if not timestamps or max(timestamps) <= window_start
    ]

    for ip in stale_ips:
        del _rate_limit_tracker[ip]

    # If still too many, remove oldest entries
    if len(_rate_limit_tracker) > RATE_LIMIT_MAX_TRACKED_IPS:
        # Sort by most recent activity and keep only the most active
        sorted_ips = sorted(_rate_limit_tracker.items(), key=lambda x: max(x[1]) if x[1] else 0, reverse=True)
        _rate_limit_tracker.clear()
        for ip, timestamps in sorted_ips[:RATE_LIMIT_MAX_TRACKED_IPS]:
            _rate_limit_tracker[ip] = timestamps

    if stale_ips:
        _LOG.debug(f"Cleaned up {len(stale_ips)} stale rate limit entries")


async def _check_rate_limit(client_ip: str) -> bool:
    """
    Check if a client has exceeded the rate limit.

    Uses a sliding window algorithm to track requests. Thread-safe via
    ``_rate_limit_lock`` — concurrent requests for different IPs can proceed
    but the cleanup-and-update sequence is atomic.

    :param client_ip: Client IP address
    :return: True if request is allowed, False if rate limited
    """
    async with _rate_limit_lock:
        # Periodically clean up stale entries
        _cleanup_stale_rate_limits()

        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW

        # Reject immediately if at capacity and this IP is new — prevents
        # unbounded growth from a single flood source consuming all slots.
        if (
            client_ip not in _rate_limit_tracker
            and len(_rate_limit_tracker) >= RATE_LIMIT_MAX_TRACKED_IPS
        ):
            return False

        # Clean up old timestamps for this IP
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


def _parse_trusted_proxies() -> list:
    """Parse TRUSTED_PROXY_IPS into a list of ipaddress networks."""
    raw = os.environ.get("TRUSTED_PROXY_IPS", "")
    if not raw:
        return []
    networks = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            networks.append(ipaddress.ip_network(item, strict=False))
        except ValueError:
            _LOG.warning("Invalid TRUSTED_PROXY_IPS entry: %s", item)
    return networks


def _get_client_ip(request: web.Request) -> str:
    """
    Get client IP from request.

    Only trusts X-Forwarded-For header if TRUST_PROXY_HEADERS is enabled,
    to prevent IP spoofing and rate limit bypass attacks.
    """
    # Only check forwarded headers if explicitly trusted
    if TRUST_PROXY_HEADERS:
        transport = request.transport
        if transport is not None:
            peername = transport.get_extra_info("peername")
            if peername:
                peer_ip = peername[0]
                trusted = _parse_trusted_proxies()
                # Check if peer is in trusted proxy list
                if trusted:
                    try:
                        peer_addr = ipaddress.ip_address(peer_ip)
                        if any(peer_addr in net for net in trusted):
                            forwarded = request.headers.get("X-Forwarded-For")
                            if forwarded:
                                # Take rightmost untrusted IP (standard practice)
                                for ip_str in reversed(forwarded.split(",")):
                                    ip_str = ip_str.strip()
                                    try:
                                        ip_addr = ipaddress.ip_address(ip_str)
                                        if not any(ip_addr in net for net in trusted):
                                            return ip_str
                                    except ValueError:
                                        pass
                    except ValueError:
                        pass
                else:
                    # No trusted IPs configured — trust X-Forwarded-For (legacy behavior)
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


def _json_response(success: bool, data: Any = None, error: str | None = None, status: int = 200) -> web.Response:
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
# Decorator: Reduce boilerplate in REST handlers
# =============================================================================


def require_connected(func):
    """
    Decorator that ensures the matrix device is configured and connected.

    Replaces the common boilerplate in REST handlers:
        matrix_device = get_matrix_device()
        if matrix_device is None:
            return _json_response(False, error="Matrix device not configured", status=503)
        if not matrix_device.connected:
            return _json_response(False, error="Matrix not connected", status=503)

    Usage:
        @require_connected
        async def handle_status(request: web.Request) -> web.Response:
            matrix_device = get_matrix_device()  # Guaranteed to be connected
            ...

    :param func: Async REST handler that uses get_matrix_device() to access the matrix
    :return: Wrapped handler that pre-checks connection state
    """
    from functools import wraps

    @wraps(func)
    async def wrapper(request: web.Request) -> web.Response:
        matrix_device = get_matrix_device()
        if matrix_device is None:
            return _json_response(success=False, error="Matrix device not configured", status=503)
        if not matrix_device.connected:
            return _json_response(success=False, error="Matrix not connected", status=503)
        # TOCTOU mitigation: the connection can drop between the check above
        # and the handler execution. Catch connection-related exceptions and
        # convert them to a proper 503 rather than letting them propagate
        # as 500 Internal Server Error.
        import aiohttp
        try:
            return await func(request)
        except (aiohttp.ClientError, ConnectionError, TimeoutError, OSError) as exc:
            _LOG.warning(f"Matrix connection lost during {func.__name__}: {exc}")
            return _json_response(
                success=False,
                error="Matrix connection lost",
                status=503,
            )

    return wrapper


# =============================================================================
# Configuration Functions
# =============================================================================


def set_matrix_device(
    device,
    input_names: dict[int, str] | None = None,
    output_names: dict[int, str] | None = None,
    config_file: Path | None = None,
    config_dir: str | None = None,
    data_dir: str | Path | None = None,
):
    """Set the matrix device reference for API handlers.

    Called during driver initialization before any REST handlers run,
    so no async lock is needed — all writes happen before the event
    loop starts serving requests.

    :param data_dir: Persistent data directory (defaults to
        ``persistence.get_data_dir()`` which honors ``MATRIX_DATA_DIR``
        and ``UC_CONFIG_HOME`` env vars). Used by Phase 7 managers
        (system shortcuts, dashboard layout).
    """
    global _matrix_device, _input_names, _output_names, _config_file
    global _scene_manager, _profile_manager, _macro_manager
    global _system_shortcut_manager, _dashboard_layout_manager
    _matrix_device = device
    if input_names:
        _input_names = input_names.copy()
    if output_names:
        _output_names = output_names.copy()
    if config_file:
        _config_file = config_file
    # Initialize managers with config directory (using lazy imports)
    if config_dir:
        _scene_manager = _get_scene_manager(config_dir)
        _profile_manager = _get_profile_manager(config_dir)
        _macro_manager = _get_macro_manager(config_dir)
    else:
        _scene_manager = _get_scene_manager(str(_get_data_dir()))
        _profile_manager = _get_profile_manager(str(_get_data_dir()))
        _macro_manager = _get_macro_manager(str(_get_data_dir()))
    # Phase 7 managers live in the persistent data directory, not config.
    # When data_dir is not explicitly passed, resolve it from env vars.
    if data_dir is None:
        data_dir = str(_get_data_dir())
    _system_shortcut_manager = _get_system_shortcut_manager(data_dir)
    _dashboard_layout_manager = _get_dashboard_layout_manager(data_dir)


async def update_input_names(input_names: dict[int, str]):
    """Update input names cache (thread-safe)."""
    global _input_names
    async with _state_lock:
        _input_names = input_names.copy()


async def update_output_names(output_names: dict[int, str]):
    """Update output names cache (thread-safe)."""
    global _output_names
    async with _state_lock:
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
            with open(_config_file) as f:
                config = json.load(f)

        # Update names (convert int keys to strings for JSON)
        config["input_names"] = {str(k): v for k, v in _input_names.items()}
        config["output_names"] = {str(k): v for k, v in _output_names.items()}

        # Save back atomically
        from _file_io import atomic_write_json
        atomic_write_json(_config_file, config)

        _LOG.info(f"Saved port names to {_config_file}")
        return True
    except Exception as e:
        _LOG.exception(f"Failed to save port names: {e}")
        return False


def set_macro_cec_sender(sender):
    """Set the CEC sender function for macro execution."""
    if _macro_manager is not None:
        _macro_manager.set_cec_sender(sender)


# =============================================================================
# Accessor Functions (for use by other modules)
# =============================================================================


def get_matrix_device() -> OreiMatrix | None:
    """Get the matrix device reference."""
    return _matrix_device


def get_input_names() -> dict[int, str]:
    """Get input names mapping."""
    return _input_names.copy()


def get_output_names() -> dict[int, str]:
    """Get output names mapping."""
    return _output_names.copy()


def get_scene_manager() -> SceneManager | None:
    """Get the scene manager."""
    return _scene_manager


def get_profile_manager() -> ProfileManager | None:
    """Get the profile manager."""
    return _profile_manager


def get_macro_manager() -> MacroManager | None:
    """Get the macro manager."""
    return _macro_manager


def get_system_shortcut_manager() -> SystemShortcutManager | None:
    """Get the system shortcut manager."""
    return _system_shortcut_manager


def get_dashboard_layout_manager() -> DashboardLayoutManager | None:
    """Get the dashboard layout manager."""
    return _dashboard_layout_manager


def get_ws_clients() -> set[web.WebSocketResponse]:
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
    if (
        path == "/ws"
        or path == "/"
        or path.startswith("/ui")
        or path.startswith("/kiosk")
        or path.startswith("/css/")
        or path.startswith("/js/")
        or path.startswith("/assets/")
        or path.startswith("/api/health")
        or path.endswith(".ico")
        or path.endswith(".svg")
        or path.endswith(".png")
        or path.endswith(".jpg")
        or path.endswith(".webp")
    ):
        return await handler(request)

    client_ip = _get_client_ip(request)

    if not await _check_rate_limit(client_ip):
        _LOG.warning(f"Rate limit exceeded for {client_ip}")
        return _json_response(False, error="Rate limit exceeded. Please slow down.", status=429)

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


def set_system_shortcut_manager(manager):
    """Set the system shortcut manager reference."""
    global _system_shortcut_manager
    _system_shortcut_manager = manager


def set_dashboard_layout_manager(manager):
    """Set the dashboard layout manager reference."""
    global _dashboard_layout_manager
    _dashboard_layout_manager = manager
