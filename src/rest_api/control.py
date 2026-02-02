"""
Control endpoints for preset, switch, and power operations.
"""

import json
import logging
from aiohttp import web

from .utils import _json_response, get_matrix_device, get_input_names
from .websocket import broadcast_status_update

_LOG = logging.getLogger("rest_api.control")

# Default output for input cycling (can be overridden via query param)
DEFAULT_CYCLE_OUTPUT = 1


async def handle_preset(request: web.Request) -> web.Response:
    """Recall a preset."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        preset_num = int(request.match_info["preset"])
        if preset_num < 1 or preset_num > 8:
            return _json_response(False, error="Preset must be 1-8", status=400)
        
        _LOG.info(f"REST API: Recalling preset {preset_num}")
        
        # Optimistic update - broadcast before command for instant UI feedback
        await broadcast_status_update("preset_recall", {
            "preset": preset_num,
            "optimistic": True
        })
        
        success = await matrix_device.recall_preset(preset_num)
        
        if success:
            return _json_response(True, {
                "preset": preset_num,
                "name": f"Preset {preset_num}",
                "message": f"Preset {preset_num} activated",
            })
        else:
            return _json_response(False, error=f"Failed to recall preset {preset_num}", status=500)
    except ValueError:
        return _json_response(False, error="Invalid preset number", status=400)
    except Exception as e:
        _LOG.error(f"Error recalling preset: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_switch(request: web.Request) -> web.Response:
    """Route an input to an output, or to all outputs if output is not specified."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        data = await request.json()
        input_num = data.get("input")
        output_num = data.get("output")
        
        if input_num is None:
            return _json_response(False, error="'input' is required", status=400)
        
        input_num = int(input_num)
        
        if input_num < 1 or input_num > 8:
            return _json_response(False, error="Input must be 1-8", status=400)
        
        # If output is not specified, route to ALL outputs
        if output_num is None:
            _LOG.info(f"REST API: Switching input {input_num} to ALL outputs")
            
            # Optimistic update
            await broadcast_status_update("switch_all", {
                "input": input_num,
                "outputs": list(range(1, 9)),
                "optimistic": True
            })
            
            success = await matrix_device.switch_input_to_all(input_num)
            
            if success:
                return _json_response(True, {
                    "input": input_num,
                    "output": "all",
                    "message": f"Input {input_num} routed to all outputs",
                })
            else:
                return _json_response(False, error="Failed to switch routing", status=500)
        
        # Single output routing
        output_num = int(output_num)
        
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        _LOG.info(f"REST API: Switching input {input_num} to output {output_num}")
        
        # Optimistic update
        await broadcast_status_update("switch", {
            "input": input_num,
            "output": output_num,
            "optimistic": True
        })
        
        success = await matrix_device.switch_input(input_num, output_num)
        
        if success:
            return _json_response(True, {
                "input": input_num,
                "output": output_num,
                "message": f"Input {input_num} routed to output {output_num}",
            })
        else:
            return _json_response(False, error="Failed to switch routing", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.error(f"Error switching: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_power_on(request: web.Request) -> web.Response:
    """Power on the matrix."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        _LOG.info("REST API: Powering on matrix")
        success = await matrix_device.power_on()
        
        if success:
            return _json_response(True, {"message": "Matrix powered on"})
        else:
            return _json_response(False, error="Failed to power on matrix", status=500)
    except Exception as e:
        _LOG.error(f"Error powering on: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_power_off(request: web.Request) -> web.Response:
    """Power off the matrix."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        _LOG.info("REST API: Powering off matrix")
        success = await matrix_device.power_off()
        
        if success:
            return _json_response(True, {"message": "Matrix powered off"})
        else:
            return _json_response(False, error="Failed to power off matrix", status=500)
    except Exception as e:
        _LOG.error(f"Error powering off: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_input_next(request: web.Request) -> web.Response:
    """Cycle to the next input on the specified output (default: output 1)."""
    matrix_device = get_matrix_device()
    input_names = get_input_names()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        # Get output from query param, default to 1
        output_num = int(request.query.get("output", DEFAULT_CYCLE_OUTPUT))
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        # Get current input for this output
        current_input = await matrix_device.get_current_input_for_output(output_num)
        if current_input is None:
            current_input = 1
        
        # Calculate next input (wrap around 8 -> 1)
        next_input = (current_input % 8) + 1
        
        input_name = input_names.get(next_input, f"Input {next_input}")
        _LOG.info(f"REST API: Cycling to next input {next_input} ({input_name}) on output {output_num}")
        
        success = await matrix_device.switch_input(next_input, output_num)
        
        if success:
            return _json_response(True, {
                "previous_input": current_input,
                "current_input": next_input,
                "input_name": input_name,
                "output": output_num,
                "message": f"Switched to {input_name} on output {output_num}",
            })
        else:
            return _json_response(False, error="Failed to switch input", status=500)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.error(f"Error cycling to next input: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_input_previous(request: web.Request) -> web.Response:
    """Cycle to the previous input on the specified output (default: output 1)."""
    matrix_device = get_matrix_device()
    input_names = get_input_names()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        # Get output from query param, default to 1
        output_num = int(request.query.get("output", DEFAULT_CYCLE_OUTPUT))
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        # Get current input for this output
        current_input = await matrix_device.get_current_input_for_output(output_num)
        if current_input is None:
            current_input = 1
        
        # Calculate previous input (wrap around 1 -> 8)
        prev_input = ((current_input - 2) % 8) + 1
        
        input_name = input_names.get(prev_input, f"Input {prev_input}")
        _LOG.info(f"REST API: Cycling to previous input {prev_input} ({input_name}) on output {output_num}")
        
        success = await matrix_device.switch_input(prev_input, output_num)
        
        if success:
            return _json_response(True, {
                "previous_input": current_input,
                "current_input": prev_input,
                "input_name": input_name,
                "output": output_num,
                "message": f"Switched to {input_name} on output {output_num}",
            })
        else:
            return _json_response(False, error="Failed to switch input", status=500)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.error(f"Error cycling to previous input: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_output_source(request: web.Request) -> web.Response:
    """Set the input source for a specific output."""
    matrix_device = get_matrix_device()
    input_names = get_input_names()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        output_num = int(request.match_info["output"])
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        data = await request.json()
        input_num = data.get("input")
        
        if input_num is None:
            return _json_response(False, error="'input' is required in body", status=400)
        
        input_num = int(input_num)
        if input_num < 1 or input_num > 8:
            return _json_response(False, error="Input must be 1-8", status=400)
        
        input_name = input_names.get(input_num, f"Input {input_num}")
        _LOG.info(f"REST API: Setting output {output_num} source to input {input_num} ({input_name})")
        
        success = await matrix_device.switch_input(input_num, output_num)
        
        if success:
            return _json_response(True, {
                "output": output_num,
                "input": input_num,
                "input_name": input_name,
                "message": f"Output {output_num} now showing {input_name}",
            })
        else:
            return _json_response(False, error="Failed to set output source", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid output/input number", status=400)
    except Exception as e:
        _LOG.error(f"Error setting output source: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_preset_save(request: web.Request) -> web.Response:
    """Save current routing to a preset."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        preset_num = int(request.match_info["preset"])
        if preset_num < 1 or preset_num > 8:
            return _json_response(False, error="Preset must be 1-8", status=400)
        
        _LOG.info(f"REST API: Saving current routing to preset {preset_num}")
        success = await matrix_device.save_preset(preset_num)
        
        if success:
            return _json_response(True, {
                "preset": preset_num,
                "message": f"Current routing saved to preset {preset_num}",
            })
        else:
            return _json_response(False, error=f"Failed to save preset {preset_num}", status=500)
    except ValueError:
        return _json_response(False, error="Invalid preset number", status=400)
    except Exception as e:
        _LOG.error(f"Error saving preset: {e}")
        return _json_response(False, error=str(e), status=500)
