"""
Settings endpoints for backend configuration.
"""

import logging
from aiohttp import web

from .utils import (
    _json_response,
    get_matrix_device,
    _config_file,
)

_LOG = logging.getLogger("rest_api.settings")


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
        port = body.get("port", 23)
        
        if not host:
            return _json_response(False, error="Host is required", status=400)
        
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
        
        # Try to connect to new host
        try:
            await matrix_device.connect()
            connected = matrix_device.connected
        except Exception as e:
            _LOG.warning(f"Failed to connect to new host: {e}")
            connected = False
        
        return _json_response(True, {
            "host": host,
            "port": port,
            "connected": connected,
            "message": f"Matrix host updated to {host}:{port}" + (" - Connected!" if connected else " - Connection failed")
        })
        
    except Exception as e:
        _LOG.error(f"Error setting matrix host: {e}")
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
            return _json_response(True, {
                "connected": True,
                "host": matrix_device.host,
                "port": matrix_device.port,
                "model": device_info.get("model", "Unknown") if device_info else "Unknown",
                "firmware_version": device_info.get("version", "") if device_info else "",
            })
        else:
            return _json_response(True, {
                "connected": False,
                "host": matrix_device.host,
                "port": matrix_device.port,
                "error": "Connection failed",
            })
            
    except Exception as e:
        _LOG.error(f"Error testing matrix connection: {e}")
        return _json_response(True, {
            "connected": False,
            "host": matrix_device.host if matrix_device else None,
            "error": str(e),
        })
