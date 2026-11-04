"""
Settings endpoints for backend configuration.
"""

import asyncio
import ipaddress
import logging
import os
import re
import socket

from aiohttp import web

from orei_matrix import Events, default_telnet_port

from .utils import (
    _json_response,
    get_matrix_device,
    safe_error_message,
)

_LOG = logging.getLogger("rest_api.settings")

_ALLOWED_MATRIX_NETWORKS = tuple(ipaddress.ip_network(cidr) for cidr in (
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16", "fc00::/7",
    "192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24",
))
_HOSTNAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$")
_LEGACY_IP_RE = re.compile(r"(?:0x[0-9a-f]+|[0-9]+)(?:\.(?:0x[0-9a-f]+|[0-9]+))*", re.IGNORECASE)


def _is_allowed_address(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Every DNS answer must meet this policy, including mapped IPv4 addresses."""
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
        addr = addr.ipv4_mapped
    if addr.is_loopback or addr.is_link_local or addr.is_unspecified or addr.is_multicast:
        return False
    if addr in ipaddress.ip_network("169.254.0.0/16"):
        return False
    if any(addr in network for network in _ALLOWED_MATRIX_NETWORKS):
        return True
    return os.environ.get("ALLOW_PUBLIC_MATRIX_HOST", "").lower() == "true" and addr.is_global


async def _is_safe_host(host: str, port: int) -> bool:
    """Resolve first, then reject the host if any returned address is unsafe."""
    if not host or "://" in host or "/" in host:
        return False
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        if not _HOSTNAME_RE.fullmatch(host) or _LEGACY_IP_RE.fullmatch(host):
            return False
        try:
            answers = await asyncio.get_running_loop().getaddrinfo(
                host, port, type=socket.SOCK_STREAM,
            )
            addresses = [ipaddress.ip_address(answer[4][0]) for answer in answers]
        except (OSError, ValueError):
            return False
    return bool(addresses) and all(_is_allowed_address(addr) for addr in addresses)


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
        host_value = body.get("host", "")
        host = host_value.strip() if isinstance(host_value, str) else ""
        port = body.get("port", 443)
        # BE-32: the Telnet port belongs to this matrix; without one the default applies
        # (OREI_TELNET_PORT, else 23), not the previous matrix's port.
        telnet_port = body.get("telnet_port")

        if not host:
            return _json_response(False, error="Host is required", status=400)
        if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
            return _json_response(False, error="port must be a port number (1-65535)", status=400)
        if telnet_port is not None and (
            isinstance(telnet_port, bool) or not isinstance(telnet_port, int) or not 1 <= telnet_port <= 65535
        ):
            return _json_response(False, error="telnet_port must be a port number (1-65535)", status=400)

        # Validate host to prevent SSRF attacks
        if not await _is_safe_host(host, port):
            return _json_response(False, error="Invalid host address", status=400)

        # Update the matrix device host
        old_host = matrix_device.host
        old_port = matrix_device.port
        password = body.get("password")
        if host != old_host and isinstance(getattr(matrix_device, "password", None), str) and matrix_device.password:
            if not isinstance(password, str) or not password:
                return _json_response(False, error="Password is required when changing the matrix host", status=400)

        _LOG.info(f"Updating matrix host from {old_host}:{old_port} to {host}:{port}")

        from .utils import get_runtime
        runtime = get_runtime()
        if runtime is not None:
            from hub.runtime.config import MatrixAddress
            result = await runtime.reconfigure(MatrixAddress(
                host, port, telnet_port, body.get("user"), password if isinstance(password, str) else None))
            connected = result.success and result.connected
            return _json_response(True, {
                "host": host, "port": port,
                "telnet_port": telnet_port if telnet_port is not None else default_telnet_port(),
                "connected": connected,
                "message": f"Matrix host updated to {host}:{port}"
                + (" - Connected!" if connected else " - Connection failed"),
            })

        # Disconnect from old host
        try:
            await matrix_device.disconnect()
        except Exception as e:
            _LOG.warning(f"Error disconnecting from old host: {e}")

        # Update host configuration
        matrix_device.host = host
        matrix_device.port = port
        if host != old_host and isinstance(password, str) and password:
            matrix_device.password = password
        matrix_device.telnet_port = telnet_port if telnet_port is not None else default_telnet_port()

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
                "telnet_port": matrix_device.telnet_port,
                "connected": connected,
                "message": f"Matrix host updated to {host}:{port}"
                + (" - Connected!" if connected else " - Connection failed"),
            },
        )

    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "Error setting matrix host"), status=500)


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
        # FIX (F13.2): return success=False with status 503 instead of
        # success=True with connected=False on exception.
        return _json_response(
            False,
            {
                "connected": False,
                "host": matrix_device.host if matrix_device else None,
                "error": safe_error_message(e, "Error testing matrix connection"),
            },
            status=503,
        )
