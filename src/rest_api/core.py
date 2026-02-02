"""
Core health and status endpoints.
"""

import logging
from aiohttp import web

from .utils import (
    _json_response,
    get_matrix_device,
    get_input_names,
    get_output_names,
    _save_names_to_config,
)

_LOG = logging.getLogger("rest_api.core")

# API Version
API_VERSION = "2.10.0"


async def handle_health(request: web.Request) -> web.Response:
    """Health check endpoint."""
    return _json_response(True, {"status": "healthy", "service": "orei-hdmi-matrix", "api_version": API_VERSION})


async def handle_info(request: web.Request) -> web.Response:
    """Get API and matrix info for the Web UI."""
    matrix_device = get_matrix_device()
    
    info = {
        "api_version": API_VERSION,
        "service": "orei-hdmi-matrix",
        "input_count": 8,
        "output_count": 8,
    }
    
    if matrix_device is not None:
        info["matrix_host"] = matrix_device.host
        info["matrix_port"] = matrix_device.port
        info["connected"] = matrix_device.connected
        
        if matrix_device.connected:
            try:
                device_info = await matrix_device.get_device_info()
                if device_info:
                    info["model"] = device_info.get("model", "BK-808")
                    info["firmware_version"] = device_info.get("version", "")
            except Exception as e:
                _LOG.warning(f"Could not get device info: {e}")
    
    return _json_response(True, info)


async def handle_status(request: web.Request) -> web.Response:
    """Get full matrix status formatted for Web UI."""
    matrix_device = get_matrix_device()
    input_names = get_input_names()
    output_names = get_output_names()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        raw_status = await matrix_device.get_status()
        
        # Format for Web UI consumption
        status = {
            "connected": raw_status.get("connected", True),
            "host": raw_status.get("host", matrix_device.host),
        }
        
        # Routing: convert array to map {output: input}
        routing_array = raw_status.get("routing", [])
        if routing_array:
            routing_array = routing_array[:8] if len(routing_array) > 8 else routing_array
            status["routing"] = {i + 1: src for i, src in enumerate(routing_array)}
            status["outputs"] = routing_array
        
        # Input names: prefer our cache, then matrix names, then default
        result_input_names = {}
        matrix_input_names = raw_status.get("input_names", [])
        for i in range(1, 9):
            if i in input_names and input_names[i]:
                result_input_names[i] = input_names[i]
            elif i - 1 < len(matrix_input_names) and matrix_input_names[i - 1]:
                result_input_names[i] = matrix_input_names[i - 1]
            else:
                result_input_names[i] = f"Input {i}"
        status["input_names"] = result_input_names
        
        # Output names: prefer our cache, then matrix names, then default
        result_output_names = {}
        matrix_output_names = raw_status.get("output_names", [])
        for i in range(1, 9):
            if i in output_names and output_names[i]:
                result_output_names[i] = output_names[i]
            elif i - 1 < len(matrix_output_names) and matrix_output_names[i - 1]:
                result_output_names[i] = matrix_output_names[i - 1]
            else:
                result_output_names[i] = f"Output {i}"
        status["output_names"] = result_output_names
        
        # Preset names
        preset_names = raw_status.get("preset_names", [])
        status["preset_names"] = {i + 1: name for i, name in enumerate(preset_names)} if preset_names else {}
        
        return _json_response(True, status)
    except Exception as e:
        _LOG.error(f"Error getting status: {e}", exc_info=True)
        return _json_response(False, error=str(e), status=500)


async def handle_presets(request: web.Request) -> web.Response:
    """Get all presets with their names."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    try:
        # Get preset names from matrix status
        preset_names = []
        if matrix_device.connected:
            try:
                status = await matrix_device.get_status()
                preset_names = status.get("preset_names", [])
            except Exception as e:
                _LOG.warning(f"Could not get preset names from matrix: {e}")
        
        presets = []
        for i in range(1, 9):
            name = preset_names[i - 1] if i - 1 < len(preset_names) and preset_names[i - 1] else f"Preset {i}"
            presets.append({
                "number": i,
                "name": name,
                "endpoint": f"/api/preset/{i}",
                "save_endpoint": f"/api/preset/{i}/save",
            })
        return _json_response(True, {"presets": presets})
    except Exception as e:
        _LOG.error(f"Error getting presets: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_inputs(request: web.Request) -> web.Response:
    """Get all inputs with their names."""
    matrix_device = get_matrix_device()
    input_names = get_input_names()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    try:
        inputs = []
        for i in range(1, 9):
            inputs.append({
                "number": i,
                "name": input_names.get(i, f"Input {i}"),
                "cec_endpoint": f"/api/cec/input/{i}",
            })
        return _json_response(True, {"inputs": inputs})
    except Exception as e:
        _LOG.error(f"Error getting inputs: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_outputs(request: web.Request) -> web.Response:
    """Get all outputs with their names."""
    matrix_device = get_matrix_device()
    output_names = get_output_names()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    try:
        outputs = []
        for i in range(1, 9):
            if i in output_names and output_names[i]:
                name = output_names[i]
            elif matrix_device.connected:
                status = await matrix_device.get_video_status()
                if status and "alloutputname" in status and i - 1 < len(status["alloutputname"]):
                    name = status["alloutputname"][i - 1] or f"Output {i}"
                else:
                    name = f"Output {i}"
            else:
                name = f"Output {i}"
            
            outputs.append({
                "number": i,
                "name": name,
                "cec_endpoint": f"/api/cec/output/{i}",
            })
        return _json_response(True, {"outputs": outputs})
    except Exception as e:
        _LOG.error(f"Error getting outputs: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_set_input_name(request: web.Request) -> web.Response:
    """Set the name of an input (sends to matrix and updates local cache)."""
    from .utils import _input_names
    
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    try:
        input_num = int(request.match_info["input"])
        if not 1 <= input_num <= 8:
            return _json_response(False, error="Input must be between 1 and 8", status=400)
    except (ValueError, KeyError):
        return _json_response(False, error="Invalid input number", status=400)
    
    try:
        body = await request.json()
        name = body.get("name", "").strip()
        if not name:
            return _json_response(False, error="Name is required", status=400)
        if len(name) > 32:
            return _json_response(False, error="Name cannot exceed 32 characters", status=400)
        
        # Send to matrix device
        if matrix_device.connected:
            success = await matrix_device.set_input_name(input_num, name)
            if not success:
                return _json_response(False, error="Failed to set name on matrix", status=500)
        
        # Update local cache
        _input_names[input_num] = name
        _LOG.info(f"Input {input_num} renamed to: {name}")
        
        # Persist to config file
        _save_names_to_config()
        
        return _json_response(True, {
            "input": input_num,
            "name": name,
            "message": f"Input {input_num} renamed to '{name}'"
        })
    except Exception as e:
        _LOG.error(f"Error setting input name: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_set_output_name(request: web.Request) -> web.Response:
    """Set the name of an output (sends to matrix and updates local cache)."""
    from .utils import _output_names
    
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    try:
        output_num = int(request.match_info["output"])
        if not 1 <= output_num <= 8:
            return _json_response(False, error="Output must be between 1 and 8", status=400)
    except (ValueError, KeyError):
        return _json_response(False, error="Invalid output number", status=400)
    
    try:
        body = await request.json()
        name = body.get("name", "").strip()
        if not name:
            return _json_response(False, error="Name is required", status=400)
        if len(name) > 32:
            return _json_response(False, error="Name cannot exceed 32 characters", status=400)
        
        # Send to matrix device
        if matrix_device.connected:
            success = await matrix_device.set_output_name(output_num, name)
            if not success:
                return _json_response(False, error="Failed to set name on matrix", status=500)
        
        # Update local cache
        _output_names[output_num] = name
        _LOG.info(f"Output {output_num} renamed to: {name}")
        
        # Persist to config file
        _save_names_to_config()
        
        return _json_response(True, {
            "output": output_num,
            "name": name,
            "message": f"Output {output_num} renamed to '{name}'"
        })
    except Exception as e:
        _LOG.error(f"Error setting output name: {e}")
        return _json_response(False, error=str(e), status=500)
