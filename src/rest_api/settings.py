"""
Settings endpoints for backend configuration.
"""

import ipaddress
import logging
import re

from aiohttp import web

from orei_matrix import Events

from .utils import (
    _json_response,
    get_matrix_device,
)

_LOG = logging.getLogger("rest_api.settings")

# Blocklist of addresses that must never be used as matrix hosts.
_SSRF_BLOCKED = {
    "0.0.0.0",
    "127.0.0.1",
    "::1",
    "169.254.169.254",  # AWS metadata / cloud metadata services
}
_SSRF_BLOCKED_CIDRS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fe80::/10"),
]
_HOSTNAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$")


def _is_safe_host(host: str) -> bool:
    """Reject hosts that could be used for SSRF attacks."""
    host = host.strip()
    if not host:
        return False

    # Prevent URL schemes from being injected.
    if "://" in host or "/" in host:
        return False

    # IPv4 / IPv6 direct check.
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        pass  # Not an IP — validate hostname.
    else:
        if str(addr) in _SSRF_BLOCKED:
            return False
        for net in _SSRF_BLOCKED_CIDRS:
            if addr in net:
                return False
        return True

    # Hostname validation (must be a valid FQDN).
    if not _HOSTNAME_RE.fullmatch(host):
        return False
    return True


async def handle_get_settings(request: web.Request) -> web.Response:
    """Get current backend settings."""
    matrix_device = get_matrix_device()

    settings = {
        "matrix_host": matrix_device.host if matrix_device else None,
        "matrix_port": matrix_device.port if matrix_device else 23,
        "connected": matrix_device.connected if matrix_device else False,
    }

    return _json_response(True, settings)


async def handle_set_matrix_host(request: web.Request) -> web.Response:
    """Set the matrix host address (reconfigures backend connection)."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    try:
        body = await request.json()
        host = body.get("host", "").strip()
        port = body.get("port", 443)

        if not host:
            return _json_response(False, error="Host is required", status=400)

        # Validate host to prevent SSRF attacks
        if not _is_safe_host(host):
            return _json_response(False, error="Invalid host address", status=400)

        # Update the matrix device host
        old_host = matrix_device.host
        old_port = matrix_device.port

        _LOG.info(f"Updating matrix host from {old_host}:{old_port} to {host}:{port}")

        # Disconnect from old host
        try:
            await matrix_device.disconnect()
        except Exception as e:
            _LOG.warning(f"Error disconnecting from old host: {e}")

        # Update host configuration
        matrix_device.host = host
        matrix_device.port = port

        # Emit configuration changed event to reset any reconnection tasks
        matrix_device.events.emit(Events.CONFIG_CHANGED)

        # Try to connect to new host
        try:
            await matrix_device.connect()
            connected = matrix_device.connected
        except Exception as e:
            _LOG.warning(f"Failed to connect to new host: {e}")
            connected = False

        return _json_response(
            True,
            {
                "host": host,
                "port": port,
                "connected": connected,
                "message": f"Matrix host updated to {host}:{port}"
                + (" - Connected!" if connected else " - Connection failed"),
            },
        )

    except Exception as e:
        _LOG.exception(f"Error setting matrix host: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_test_matrix_connection(request: web.Request) -> web.Response:
    """Test connection to the currently configured matrix."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    try:
        # Try to get device info as a connection test
        if not matrix_device.connected:
            await matrix_device.connect()

        if matrix_device.connected:
            device_info = await matrix_device.get_device_info()
            return _json_response(
                True,
                {
                    "connected": True,
                    "host": matrix_device.host,
                    "port": matrix_device.port,
                    "model": device_info.get("model", "Unknown") if device_info else "Unknown",
                    "firmware_version": device_info.get("version", "") if device_info else "",
                },
            )
        else:
            # FIX (F13.2): return success=False with status 503 instead of
            # success=True with connected=False. Previously monitoring tools
            # checking HTTP 200 → "OK" missed the failed connection.
            return _json_response(
                False,
                {
                    "connected": False,
                    "host": matrix_device.host,
                    "port": matrix_device.port,
                    "error": "Connection failed",
                },
                status=503,
            )

    except Exception as e:
        _LOG.exception(f"Error testing matrix connection: {e}")
        # FIX (F13.2): return success=False with status 503 instead of
        # success=True with connected=False on exception.
        return _json_response(
            False,
            {
                "connected": False,
                "host": matrix_device.host if matrix_device else None,
                "error": str(e),
            },
            status=503,
        )
