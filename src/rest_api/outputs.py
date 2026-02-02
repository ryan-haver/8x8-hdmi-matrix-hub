"""
Output control and status endpoints.

Handles output settings: enable/disable, HDCP, HDR, scaler, ARC, mute.
Also includes extended status endpoints.
"""

import json
import logging
from aiohttp import web

from .utils import _json_response, get_matrix_device, get_input_names, get_output_names
from .websocket import broadcast_status_update

_LOG = logging.getLogger("rest_api.outputs")


# =============================================================================
# Extended Status Endpoints
# =============================================================================

async def handle_full_status(request: web.Request) -> web.Response:
    """Get comprehensive matrix status from all status endpoints."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        status = await matrix_device.get_full_status()
        return _json_response(True, status)
    except Exception as e:
        _LOG.error(f"Error getting full status: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_output_status(request: web.Request) -> web.Response:
    """Get detailed output/display status including connection detection."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        status = await matrix_device.get_output_status()
        if status:
            # Get cable status from Telnet if available
            cable_status = await matrix_device.get_all_cable_status()
            cable_outputs = cable_status.get("outputs", {})
            
            # Parse into a more friendly format
            output_names = await matrix_device.get_output_names()
            outputs = []
            for i in range(1, 9):
                idx = i - 1
                is_connected = status.get("allconnect", [])[idx] == 1 if idx < len(status.get("allconnect", [])) else False
                cable_connected = cable_outputs.get(i)
                
                outputs.append({
                    "number": i,
                    "name": output_names.get(i, f"Output {i}"),
                    "connected": is_connected,
                    "cableConnected": cable_connected,
                    "enabled": status.get("allout", [])[idx] == 1 if idx < len(status.get("allout", [])) else False,
                    "muted": status.get("allaudiomute", [])[idx] == 1 if idx < len(status.get("allaudiomute", [])) else False,
                    "hdcp": status.get("allhdcp", [])[idx] if idx < len(status.get("allhdcp", [])) else None,
                    "hdr": status.get("allhdr", [])[idx] if idx < len(status.get("allhdr", [])) else None,
                    "scaler": status.get("allscaler", [])[idx] if idx < len(status.get("allscaler", [])) else None,
                    "arc": status.get("allarc", [])[idx] == 1 if idx < len(status.get("allarc", [])) else False,
                })
            return _json_response(True, {
                "outputs": outputs, 
                "raw": status,
                "telnetAvailable": matrix_device.telnet_connected
            })
        else:
            return _json_response(False, error="Failed to get output status", status=500)
    except Exception as e:
        _LOG.error(f"Error getting output status: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_input_status(request: web.Request) -> web.Response:
    """Get detailed input status including signal and cable detection."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        status = await matrix_device.get_input_status()
        cable_status = await matrix_device.get_all_cable_status()
        cable_inputs = cable_status.get("inputs", {})
        
        if status:
            inactive_arr = status.get("inactive", [])
            edid_arr = status.get("edid", [])
            # Use actual names from matrix response, not cached defaults
            inname_arr = status.get("inname", [])
            
            inputs = []
            for i in range(1, 9):
                idx = i - 1
                has_signal = inactive_arr[idx] == 1 if idx < len(inactive_arr) else False
                source_detected = cable_inputs.get(i)
                # Get name from matrix response, fall back to default
                name = inname_arr[idx] if idx < len(inname_arr) else f"Input {i}"
                
                inputs.append({
                    "number": i,
                    "name": name,
                    "inactive": not has_signal,
                    "signalActive": has_signal,
                    "cableConnected": source_detected,
                    "sourceDetected": source_detected,
                    "edid": edid_arr[idx] if idx < len(edid_arr) else None,
                })
            return _json_response(True, {
                "inputs": inputs, 
                "raw": status,
                "telnetAvailable": matrix_device.telnet_connected
            })
        else:
            return _json_response(False, error="Failed to get input status", status=500)
    except Exception as e:
        _LOG.error(f"Error getting input status: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_cable_status(request: web.Request) -> web.Response:
    """Get cable connection status for all inputs and outputs via Telnet."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    if not matrix_device.telnet_connected:
        return _json_response(False, error="Telnet not connected - cable detection unavailable", status=503)
    
    try:
        cable_status = await matrix_device.get_all_cable_status()
        input_names_dict = await matrix_device.get_all_input_names()
        output_names_dict = await matrix_device.get_output_names()
        
        inputs = []
        for i in range(1, 9):
            connected = cable_status.get("inputs", {}).get(i)
            inputs.append({
                "number": i,
                "name": input_names_dict.get(i, f"Input {i}"),
                "cableConnected": connected,
            })
        
        outputs = []
        for i in range(1, 9):
            connected = cable_status.get("outputs", {}).get(i)
            outputs.append({
                "number": i,
                "name": output_names_dict.get(i, f"Output {i}"),
                "cableConnected": connected,
            })
        
        return _json_response(True, {
            "inputs": inputs,
            "outputs": outputs,
            "telnetAvailable": True
        })
    except Exception as e:
        _LOG.error(f"Error getting cable status: {e}")
        return _json_response(False, error=str(e), status=500)


# =============================================================================
# EDID Endpoints
# =============================================================================

async def handle_edid_status(request: web.Request) -> web.Response:
    """Get EDID configuration status for all inputs."""
    matrix_device = get_matrix_device()
    input_names = get_input_names()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        # Import OreiMatrix for static method access
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from orei_matrix import OreiMatrix
        
        status = await matrix_device.get_edid_status()
        if status:
            inputs = []
            for i in range(1, 9):
                idx = i - 1
                edid_value = status.get("edid", [])[idx] if idx < len(status.get("edid", [])) else None
                inputs.append({
                    "number": i,
                    "name": input_names.get(i, f"Input {i}"),
                    "edid_mode": edid_value,
                    "edid_mode_name": OreiMatrix.get_edid_mode_name(edid_value) if edid_value else None,
                })
            return _json_response(True, {"inputs": inputs, "raw": status})
        else:
            return _json_response(False, error="Failed to get EDID status", status=500)
    except Exception as e:
        _LOG.error(f"Error getting EDID status: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_edid_modes(request: web.Request) -> web.Response:
    """Get available EDID modes."""
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from orei_matrix import OreiMatrix
        
        modes = OreiMatrix.get_edid_modes()
        return _json_response(True, {"modes": modes})
    except Exception as e:
        _LOG.error(f"Error getting EDID modes: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_set_input_edid(request: web.Request) -> web.Response:
    """Set EDID mode for a specific input."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from orei_matrix import OreiMatrix
        
        input_num = int(request.match_info.get("input", 0))
        if input_num < 1 or input_num > 8:
            return _json_response(False, error="Invalid input number (1-8)", status=400)
        
        data = await request.json()
        mode = data.get("mode")
        
        if mode is None:
            return _json_response(False, error="Missing 'mode' parameter", status=400)
        
        mode = int(mode)
        
        # Check if this is a copy-from-output mode (15-22)
        if 15 <= mode <= 22:
            output_num = mode - 14
            result = await matrix_device.copy_edid_from_output(input_num, output_num)
        else:
            result = await matrix_device.set_input_edid(input_num, mode)
        
        if result:
            mode_name = OreiMatrix.get_edid_mode_name(mode)
            return _json_response(True, {
                "input": input_num,
                "mode": mode,
                "mode_name": mode_name,
            })
        else:
            return _json_response(False, error="Failed to set EDID mode", status=500)
    except ValueError:
        return _json_response(False, error="Invalid input or mode value", status=400)
    except Exception as e:
        _LOG.error(f"Error setting EDID for input: {e}")
        return _json_response(False, error=str(e), status=500)


# =============================================================================
# Output Control Endpoints
# =============================================================================

async def handle_output_enable(request: web.Request) -> web.Response:
    """Enable or disable output video stream."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        output_num = int(request.match_info["output"])
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        data = await request.json()
        enabled = data.get("enabled", True)
        
        _LOG.info(f"REST API: Setting output {output_num} stream to {'enabled' if enabled else 'disabled'}")
        success = await matrix_device.set_output_enable(output_num, enabled)
        
        if success:
            return _json_response(True, {
                "output": output_num,
                "enabled": enabled,
                "message": f"Output {output_num} stream {'enabled' if enabled else 'disabled'}"
            })
        else:
            return _json_response(False, error=f"Failed to set output {output_num} stream", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.error(f"Error setting output enable: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_output_hdcp(request: web.Request) -> web.Response:
    """Set HDCP mode for an output."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        output_num = int(request.match_info["output"])
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        data = await request.json()
        mode = data.get("mode")
        if mode is None or mode < 1 or mode > 5:
            return _json_response(False, error="mode must be 1-5 (1=HDCP1.4, 2=HDCP2.2, 3=Follow Sink, 4=Follow Source, 5=User)", status=400)
        
        mode_names = {1: "HDCP 1.4", 2: "HDCP 2.2", 3: "Follow Sink", 4: "Follow Source", 5: "User Mode"}
        _LOG.info(f"REST API: Setting output {output_num} HDCP to mode {mode} ({mode_names.get(mode)})")
        success = await matrix_device.set_output_hdcp(output_num, mode)
        
        if success:
            return _json_response(True, {
                "output": output_num,
                "hdcp_mode": mode,
                "hdcp_mode_name": mode_names.get(mode),
                "message": f"Output {output_num} HDCP set to {mode_names.get(mode)}"
            })
        else:
            return _json_response(False, error=f"Failed to set output {output_num} HDCP", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.error(f"Error setting output HDCP: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_output_hdr(request: web.Request) -> web.Response:
    """Set HDR mode for an output."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        output_num = int(request.match_info["output"])
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        data = await request.json()
        mode = data.get("mode")
        if mode is None or mode < 1 or mode > 3:
            return _json_response(False, error="mode must be 1-3 (1=Passthrough, 2=HDR→SDR, 3=Auto)", status=400)
        
        mode_names = {1: "Passthrough", 2: "HDR to SDR", 3: "Auto"}
        _LOG.info(f"REST API: Setting output {output_num} HDR to mode {mode} ({mode_names.get(mode)})")
        success = await matrix_device.set_output_hdr(output_num, mode)
        
        if success:
            return _json_response(True, {
                "output": output_num,
                "hdr_mode": mode,
                "hdr_mode_name": mode_names.get(mode),
                "message": f"Output {output_num} HDR set to {mode_names.get(mode)}"
            })
        else:
            return _json_response(False, error=f"Failed to set output {output_num} HDR", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.error(f"Error setting output HDR: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_output_scaler(request: web.Request) -> web.Response:
    """Set scaler mode for an output."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        output_num = int(request.match_info["output"])
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        data = await request.json()
        mode = data.get("mode")
        if mode is None or mode < 1 or mode > 5:
            return _json_response(False, error="mode must be 1-5 (1=Passthrough, 2=8K→4K, 3=8K/4K→1080p, 4=Auto, 5=Audio Only)", status=400)
        
        mode_names = {1: "Passthrough", 2: "8K to 4K", 3: "8K/4K to 1080p", 4: "Auto", 5: "Audio Only"}
        _LOG.info(f"REST API: Setting output {output_num} scaler to mode {mode} ({mode_names.get(mode)})")
        success = await matrix_device.set_output_scaler(output_num, mode)
        
        if success:
            return _json_response(True, {
                "output": output_num,
                "scaler_mode": mode,
                "scaler_mode_name": mode_names.get(mode),
                "message": f"Output {output_num} scaler set to {mode_names.get(mode)}"
            })
        else:
            return _json_response(False, error=f"Failed to set output {output_num} scaler", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.error(f"Error setting output scaler: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_output_arc(request: web.Request) -> web.Response:
    """Enable or disable ARC for an output."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        output_num = int(request.match_info["output"])
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        data = await request.json()
        enabled = data.get("enabled", True)
        
        _LOG.info(f"REST API: Setting output {output_num} ARC to {'enabled' if enabled else 'disabled'}")
        success = await matrix_device.set_output_arc(output_num, enabled)
        
        if success:
            return _json_response(True, {
                "output": output_num,
                "arc_enabled": enabled,
                "message": f"Output {output_num} ARC {'enabled' if enabled else 'disabled'}"
            })
        else:
            return _json_response(False, error=f"Failed to set output {output_num} ARC", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.error(f"Error setting output ARC: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_output_mute(request: web.Request) -> web.Response:
    """Mute or unmute audio for an output."""
    matrix_device = get_matrix_device()
    
    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)
    
    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)
    
    try:
        output_num = int(request.match_info["output"])
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)
        
        data = await request.json()
        muted = data.get("muted", True)
        
        _LOG.info(f"REST API: Setting output {output_num} audio to {'muted' if muted else 'unmuted'}")
        
        # Optimistic update
        await broadcast_status_update("audio_mute", {
            "output": output_num,
            "muted": muted,
            "optimistic": True
        })
        
        success = await matrix_device.set_output_audio_mute(output_num, muted)
        
        if success:
            return _json_response(True, {
                "output": output_num,
                "audio_muted": muted,
                "message": f"Output {output_num} audio {'muted' if muted else 'unmuted'}"
            })
        else:
            return _json_response(False, error=f"Failed to set output {output_num} audio mute", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.error(f"Error setting output mute: {e}")
        return _json_response(False, error=str(e), status=500)
