"""
CEC control endpoints.

Handles CEC commands to input and output devices.
"""

import logging
from aiohttp import web

from .utils import _json_response, get_matrix_device, get_input_names
from .websocket import broadcast_status_update

_LOG = logging.getLogger("rest_api.cec")


async def handle_cec_input(request: web.Request) -> web.Response:
    """Send CEC command to an input device."""
    matrix_device = get_matrix_device()
    input_names = get_input_names()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        input_num = int(request.match_info["input"])
        command = request.match_info["command"].lower()
        
        if input_num < 1 or input_num > 8:
            return _json_response(False, error="Input must be 1-8", status=400)
        
        # Use the unified send_cec method
        if command.upper() not in matrix_device.CEC_COMMAND_MAP:
            available = ", ".join(sorted(k.lower() for k in matrix_device.CEC_COMMAND_MAP.keys()))
            return _json_response(False, error=f"Unknown command '{command}'. Available: {available}", status=400)
        
        input_name = input_names.get(input_num, f"Input {input_num}")
        _LOG.info(f"REST API: CEC {command} to input {input_num} ({input_name})")
        
        # Optimistic update for power commands
        if command in ("power_on", "power_off"):
            await broadcast_status_update("cec_command", {
                "type": "input",
                "port": input_num,
                "command": command,
                "name": input_name,
                "optimistic": True
            })
        
        success = await matrix_device.send_cec(command, input_num, is_output=False)
        
        if success:
            return _json_response(True, {
                "input": input_num,
                "name": input_name,
                "command": command,
                "message": f"CEC {command} sent to {input_name}",
            })
        else:
            return _json_response(False, error=f"Failed to send CEC {command}", status=500)
    except ValueError:
        return _json_response(False, error="Invalid input number", status=400)
    except Exception as e:
        _LOG.error(f"Error sending CEC command: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_cec_output(request: web.Request) -> web.Response:
    """Send CEC command to an output device (TV)."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        output_num = int(request.match_info["output"])
        command = request.match_info["command"].lower()
        
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        # Use the unified send_cec method
        if command.upper() not in matrix_device.CEC_COMMAND_MAP:
            available = ", ".join(sorted(k.lower() for k in matrix_device.CEC_COMMAND_MAP.keys()))
            return _json_response(False, error=f"Unknown command '{command}'. Available: {available}", status=400)
        
        _LOG.info(f"REST API: CEC {command} to output {output_num}")
        
        # Optimistic update for power commands
        if command in ("power_on", "power_off"):
            await broadcast_status_update("cec_command", {
                "type": "output",
                "port": output_num,
                "command": command,
                "optimistic": True
            })
        
        success = await matrix_device.send_cec(command, output_num, is_output=True)
        
        if success:
            return _json_response(True, {
                "output": output_num,
                "command": command,
                "message": f"CEC {command} sent to output {output_num}",
            })
        else:
            return _json_response(False, error=f"Failed to send CEC {command}", status=500)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.error(f"Error sending CEC command: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_cec_commands(request: web.Request) -> web.Response:
    """List available CEC commands."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        # Return static list if no device
        commands = ["power_on", "power_off", "up", "down", "left", "right", "select", 
                   "menu", "back", "play", "pause", "stop", "volume_up", "volume_down", "mute"]
        return _json_response(True, {
            "input_commands": commands,
            "output_commands": commands,
            "usage": {
                "input": "POST /api/cec/input/{1-8}/{command}",
                "output": "POST /api/cec/output/{1-8}/{command}",
            }
        })
    
    commands = sorted(k.lower() for k in matrix_device.CEC_COMMAND_MAP.keys())
    return _json_response(True, {
        "input_commands": commands,
        "output_commands": commands,
        "usage": {
            "input": "POST /api/cec/input/{1-8}/{command}",
            "output": "POST /api/cec/output/{1-8}/{command}",
        }
    })


async def handle_cec_status(request: web.Request) -> web.Response:
    """Get CEC configuration status."""
    matrix_device = get_matrix_device()
    input_names = get_input_names()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        status = await matrix_device.get_cec_status()
        if status:
            cec_config = {
                "inputs": [],
                "outputs": [],
            }
            for i in range(1, 9):
                idx = i - 1
                cec_config["inputs"].append({
                    "number": i,
                    "name": input_names.get(i, f"Input {i}"),
                    "cec_enabled": status.get("inputindex", [])[idx] == 1 if idx < len(status.get("inputindex", [])) else False,
                })
                cec_config["outputs"].append({
                    "number": i,
                    "cec_enabled": status.get("outputindex", [])[idx] == 1 if idx < len(status.get("outputindex", [])) else False,
                })
            return _json_response(True, {"cec_config": cec_config, "raw": status})
        else:
            return _json_response(False, error="Failed to get CEC status", status=500)
    except Exception as e:
        _LOG.error(f"Error getting CEC status: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_cec_capabilities(request: web.Request) -> web.Response:
    """Get CEC capabilities for all input and output devices."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        capabilities = await matrix_device.get_all_capabilities()
        if capabilities:
            return _json_response(True, {
                "capabilities": capabilities,
                "summary": {
                    "audio_only_outputs": [
                        o["output_num"] for o in capabilities["outputs"] 
                        if o.get("is_audio_only")
                    ],
                    "arc_enabled_outputs": [
                        o["output_num"] for o in capabilities["outputs"] 
                        if o.get("arc_enabled")
                    ],
                    "connected_outputs": [
                        o["output_num"] for o in capabilities["outputs"] 
                        if o.get("connected")
                    ],
                    "signal_detected_inputs": [
                        i["input_num"] for i in capabilities["inputs"] 
                        if i.get("signal_detected")
                    ],
                }
            })
        else:
            return _json_response(False, error="Failed to get capabilities", status=500)
    except Exception as e:
        _LOG.error(f"Error getting CEC capabilities: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_input_capabilities(request: web.Request) -> web.Response:
    """Get CEC capabilities for a specific input device."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        input_num = int(request.match_info.get("input", 0))
        if input_num < 1 or input_num > 8:
            return _json_response(False, error="Input must be 1-8", status=400)
        
        capabilities = await matrix_device.get_input_capabilities(input_num)
        if capabilities:
            return _json_response(True, {"capabilities": capabilities})
        else:
            return _json_response(False, error="Failed to get input capabilities", status=500)
    except ValueError:
        return _json_response(False, error="Invalid input number", status=400)
    except Exception as e:
        _LOG.error(f"Error getting input capabilities: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_output_capabilities(request: web.Request) -> web.Response:
    """Get CEC capabilities for a specific output device."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        output_num = int(request.match_info.get("output", 0))
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        capabilities = await matrix_device.get_output_capabilities(output_num)
        if capabilities:
            return _json_response(True, {"capabilities": capabilities})
        else:
            return _json_response(False, error="Failed to get output capabilities", status=500)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.error(f"Error getting output capabilities: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_cec_commands_by_type(request: web.Request) -> web.Response:
    """Get supported CEC commands for a device type (input or output)."""
    try:
        device_type = request.match_info.get("type", "input")
        
        # Import from parent package
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        if device_type == "input":
            from cec_commands import INPUT_CEC_COMMANDS, CEC_CATEGORIES
            commands = INPUT_CEC_COMMANDS
        elif device_type == "output":
            from cec_commands import OUTPUT_CEC_COMMANDS, CEC_CATEGORIES
            commands = OUTPUT_CEC_COMMANDS
        else:
            return _json_response(False, error="Type must be 'input' or 'output'", status=400)
        
        # Group commands by category
        by_category = {}
        for cmd_name, cmd_info in commands.items():
            category = cmd_info.get("category", "other")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append({
                "command": cmd_name,
                "description": cmd_info.get("description", ""),
                "index": cmd_info.get("index"),
            })
        
        return _json_response(True, {
            "device_type": device_type,
            "commands": list(commands.keys()),
            "by_category": by_category,
            "total_commands": len(commands),
        })
    except Exception as e:
        _LOG.error(f"Error getting CEC commands by type: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_cec_enable(request: web.Request) -> web.Response:
    """Enable or disable CEC for a port."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        port_type = request.match_info["port_type"]  # "input" or "output"
        port_num = int(request.match_info["port"])
        
        if port_type not in ("input", "output"):
            return _json_response(False, error="port_type must be 'input' or 'output'", status=400)
        if port_num < 1 or port_num > 8:
            return _json_response(False, error="Port must be 1-8", status=400)
        
        data = await request.json()
        enabled = data.get("enabled", True)
        
        _LOG.info(f"REST API: Setting CEC for {port_type} {port_num} to {'enabled' if enabled else 'disabled'}")
        success = await matrix_device.set_cec_enable(port_type, port_num, enabled)
        
        if success:
            return _json_response(True, {
                "port_type": port_type,
                "port": port_num,
                "cec_enabled": enabled,
                "message": f"CEC for {port_type} {port_num} {'enabled' if enabled else 'disabled'}"
            })
        else:
            return _json_response(False, error=f"Failed to set CEC for {port_type} {port_num}", status=500)
    except Exception as e:
        _LOG.error(f"Error setting CEC enable: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_cec_enable_input(request: web.Request) -> web.Response:
    """Enable or disable CEC for an input port."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        port_num = int(request.match_info["port"])
        if port_num < 1 or port_num > 8:
            return _json_response(False, error="Port must be 1-8", status=400)
        
        data = await request.json()
        enabled = data.get("enabled", True)
        
        _LOG.info(f"REST API: Setting CEC for input {port_num} to {'enabled' if enabled else 'disabled'}")
        success = await matrix_device.set_cec_enable("input", port_num, enabled)
        
        if success:
            return _json_response(True, {
                "port_type": "input",
                "port": port_num,
                "cec_enabled": enabled,
                "message": f"CEC for input {port_num} {'enabled' if enabled else 'disabled'}"
            })
        else:
            return _json_response(False, error=f"Failed to set CEC for input {port_num}", status=500)
    except Exception as e:
        _LOG.error(f"Error setting CEC enable: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_cec_enable_output(request: web.Request) -> web.Response:
    """Enable or disable CEC for an output port."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        port_num = int(request.match_info["port"])
        if port_num < 1 or port_num > 8:
            return _json_response(False, error="Port must be 1-8", status=400)
        
        data = await request.json()
        enabled = data.get("enabled", True)
        
        _LOG.info(f"REST API: Setting CEC for output {port_num} to {'enabled' if enabled else 'disabled'}")
        success = await matrix_device.set_cec_enable("output", port_num, enabled)
        
        if success:
            return _json_response(True, {
                "port_type": "output",
                "port": port_num,
                "cec_enabled": enabled,
                "message": f"CEC for output {port_num} {'enabled' if enabled else 'disabled'}"
            })
        else:
            return _json_response(False, error=f"Failed to set CEC for output {port_num}", status=500)
    except Exception as e:
        _LOG.error(f"Error setting CEC enable: {e}")
        return _json_response(False, error=str(e), status=500)
