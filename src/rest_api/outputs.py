"""
Output control and status endpoints.

Handles output settings: enable/disable, HDCP, HDR, scaler, ARC, mute.
Also includes extended status endpoints.
"""

import logging

from aiohttp import web

from device_codes import (
    EDID_MODES,
    HDCP_MODES,
    HDR_MODES,
    SCALER_MODES,
    edid_copy_from_output,
    hdr_from_device,
    scaler_from_device,
)

from .utils import _json_response, get_input_names, get_matrix_device, safe_error_message
from .validation import BadRequestError, optional_bool, parse_json_object, validate_int, validate_port

_LOG = logging.getLogger("rest_api.outputs")


def _mode_from(data: dict, modes: dict, error: str) -> int:
    """Return the body's ``mode`` if it is one of ``modes``; anything else (missing, a bool, a list) is a 400."""
    mode = validate_int(data.get("mode"), "mode", minimum=min(modes), maximum=max(modes), message=error)
    if mode not in modes:
        raise BadRequestError(error)
    return mode


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
        return _json_response(False, error=safe_error_message(e, "getting full status"), status=500)


async def handle_output_status(request: web.Request) -> web.Response:
    """Get detailed output/display status including connection detection."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)

    try:
        is_cached = hasattr(matrix_device, "_output_status_cache") and isinstance(matrix_device._output_status_cache, dict)

        status = await matrix_device.get_output_status()

        if is_cached:
            from .core import schedule_background_refresh

            schedule_background_refresh(matrix_device)  # deduplicated (API-11)

        if status:
            # Get cable status from Telnet if available
            cable_outputs = {}
            try:
                cable_status = await matrix_device.get_all_cable_status()
                cable_outputs = cable_status.get("outputs", {})
            except Exception as e:
                _LOG.warning(f"Failed to get cable status for outputs: {e}")

            # Parse into a more friendly format
            output_names = await matrix_device.get_output_names()
            outputs = []
            for i in range(1, 9):
                idx = i - 1
                is_connected = (
                    status.get("allconnect", [])[idx] == 1 if idx < len(status.get("allconnect", [])) else False
                )
                cable_connected = cable_outputs.get(i)

                outputs.append(
                    {
                        "number": i,
                        "name": output_names.get(i, f"Output {i}"),
                        "connected": is_connected,
                        "cableConnected": cable_connected,
                        "enabled": status.get("allout", [])[idx] == 1 if idx < len(status.get("allout", [])) else False,
                        "muted": status.get("allaudiomute", [])[idx] == 1
                        if idx < len(status.get("allaudiomute", []))
                        else False,
                        "hdcp": status.get("allhdcp", [])[idx] if idx < len(status.get("allhdcp", [])) else None,
                        # API values (HDR 1-3, scaler 1-5), what the setters take (HIL-02)
                        "hdr": hdr_from_device(status.get("allhdr", [])[idx])
                        if idx < len(status.get("allhdr", []))
                        else None,
                        "scaler": scaler_from_device(status.get("allscaler", [])[idx])
                        if idx < len(status.get("allscaler", []))
                        else None,
                        "arc": status.get("allarc", [])[idx] == 1 if idx < len(status.get("allarc", [])) else False,
                    }
                )
            return _json_response(
                True, {"outputs": outputs, "raw": status, "telnetAvailable": matrix_device.telnet_connected}
            )
        else:
            return _json_response(False, error="Failed to get output status", status=500)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "getting output status"), status=500)


async def handle_input_status(request: web.Request) -> web.Response:
    """Get detailed input status including signal and cable detection."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)

    try:
        is_cached = hasattr(matrix_device, "_input_status_cache") and matrix_device._input_status_cache is not None

        status = await matrix_device.get_input_status()

        if is_cached:
            from .core import schedule_background_refresh

            schedule_background_refresh(matrix_device)  # deduplicated (API-11)

        # Get cable status from Telnet if available
        cable_inputs = {}
        try:
            cable_status = await matrix_device.get_all_cable_status()
            cable_inputs = cable_status.get("inputs", {})
        except Exception as e:
            _LOG.warning(f"Failed to get cable status for inputs: {e}")

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

                inputs.append(
                    {
                        "number": i,
                        "name": name,
                        "inactive": not has_signal,
                        "signalActive": has_signal,
                        "cableConnected": source_detected,
                        "sourceDetected": source_detected,
                        "edid": edid_arr[idx] if idx < len(edid_arr) else None,
                    }
                )
            return _json_response(
                True, {"inputs": inputs, "raw": status, "telnetAvailable": matrix_device.telnet_connected}
            )
        else:
            return _json_response(False, error="Failed to get input status", status=500)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "getting input status"), status=500)


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
        is_cached = hasattr(matrix_device, "_cable_status_cache") and matrix_device._cable_status_cache is not None

        cable_status = await matrix_device.get_all_cable_status()

        if is_cached:
            from .core import schedule_background_refresh

            schedule_background_refresh(matrix_device)  # deduplicated (API-11)

        input_names_dict = await matrix_device.get_all_input_names()
        output_names_dict = await matrix_device.get_output_names()

        inputs = []
        for i in range(1, 9):
            connected = cable_status.get("inputs", {}).get(i)
            inputs.append(
                {
                    "number": i,
                    "name": input_names_dict.get(i, f"Input {i}"),
                    "cableConnected": connected,
                }
            )

        outputs = []
        for i in range(1, 9):
            connected = cable_status.get("outputs", {}).get(i)
            outputs.append(
                {
                    "number": i,
                    "name": output_names_dict.get(i, f"Output {i}"),
                    "cableConnected": connected,
                }
            )

        return _json_response(True, {"inputs": inputs, "outputs": outputs, "telnetAvailable": True})
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "getting cable status"), status=500)


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
                inputs.append(
                    {
                        "number": i,
                        "name": input_names.get(i, f"Input {i}"),
                        "edid_mode": edid_value,
                        "edid_mode_name": OreiMatrix.get_edid_mode_name(edid_value) if edid_value else None,
                    }
                )
            return _json_response(True, {"inputs": inputs, "raw": status})
        else:
            return _json_response(False, error="Failed to get EDID status", status=500)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "getting EDID status"), status=500)


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
        return _json_response(False, error=safe_error_message(e, "getting EDID modes"), status=500)


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

        data = await parse_json_object(request)
        mode = data.get("mode")
        copy_from = data.get("copy_from_output")

        if mode is None and copy_from is None:
            return _json_response(False, error="Missing 'mode' parameter", status=400)

        # EDID ids are the device's own (1-47, GET /api/edid/modes). Copying
        # a display's EDID is id 39 + output (40-47); ``copy_from_output`` is
        # a shortcut for it. The old 15-22 "copy" ids were wrong (BE-25):
        # 15-22 are built-in HDR EDIDs on the device.
        if copy_from is not None:
            output_num = validate_port(copy_from, message="copy_from_output must be 1-8")
            mode = edid_copy_from_output(output_num)
            result = await matrix_device.copy_edid_from_output(input_num, output_num)
        else:
            mode = _mode_from(data, EDID_MODES, f"mode must be {min(EDID_MODES)}-{max(EDID_MODES)} (see /api/edid/modes)")
            result = await matrix_device.set_input_edid(input_num, mode)

        if result:
            mode_name = OreiMatrix.get_edid_mode_name(mode)
            return _json_response(
                True,
                {
                    "input": input_num,
                    "mode": mode,
                    "mode_name": mode_name,
                },
            )
        else:
            return _json_response(False, error="Failed to set EDID mode", status=500)
    except BadRequestError as exc:
        return exc.response()
    except ValueError:
        return _json_response(False, error="Invalid input or mode value", status=400)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting EDID for input"), status=500)


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

        data = await parse_json_object(request)
        enabled = optional_bool(data, "enabled", True)

        _LOG.info(f"REST API: Setting output {output_num} stream to {'enabled' if enabled else 'disabled'}")
        success = await matrix_device.set_output_enable(output_num, enabled)

        if success:
            return _json_response(
                True,
                {
                    "output": output_num,
                    "enabled": enabled,
                    "message": f"Output {output_num} stream {'enabled' if enabled else 'disabled'}",
                },
            )
        else:
            return _json_response(False, error=f"Failed to set output {output_num} stream", status=500)
    except BadRequestError as exc:
        return exc.response()
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting output enable"), status=500)


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

        data = await parse_json_object(request)
        mode = _mode_from(data, HDCP_MODES, "mode must be 1-5 (1=HDCP1.4, 2=HDCP2.2, 3=Follow Sink, 4=Follow Source, 5=User)")

        mode_names = HDCP_MODES
        _LOG.info(f"REST API: Setting output {output_num} HDCP to mode {mode} ({mode_names.get(mode)})")
        success = await matrix_device.set_output_hdcp(output_num, mode)

        if success:
            return _json_response(
                True,
                {
                    "output": output_num,
                    "hdcp_mode": mode,
                    "hdcp_mode_name": mode_names.get(mode),
                    "message": f"Output {output_num} HDCP set to {mode_names.get(mode)}",
                },
            )
        else:
            return _json_response(False, error=f"Failed to set output {output_num} HDCP", status=500)
    except BadRequestError as exc:
        return exc.response()
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting output HDCP"), status=500)


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

        data = await parse_json_object(request)
        mode = _mode_from(data, HDR_MODES, "mode must be 1-3 (1=Passthrough, 2=HDR→SDR, 3=Auto)")

        mode_names = HDR_MODES
        _LOG.info(f"REST API: Setting output {output_num} HDR to mode {mode} ({mode_names.get(mode)})")
        success = await matrix_device.set_output_hdr(output_num, mode)

        if success:
            return _json_response(
                True,
                {
                    "output": output_num,
                    "hdr_mode": mode,
                    "hdr_mode_name": mode_names.get(mode),
                    "message": f"Output {output_num} HDR set to {mode_names.get(mode)}",
                },
            )
        else:
            return _json_response(False, error=f"Failed to set output {output_num} HDR", status=500)
    except BadRequestError as exc:
        return exc.response()
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting output HDR"), status=500)


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

        data = await parse_json_object(request)
        mode = _mode_from(data, SCALER_MODES, "mode must be 1-5 (1=Passthrough, 2=8K→4K, 3=8K/4K→1080p, 4=Auto, 5=Audio Only)")

        mode_names = SCALER_MODES
        _LOG.info(f"REST API: Setting output {output_num} scaler to mode {mode} ({mode_names.get(mode)})")
        success = await matrix_device.set_output_scaler(output_num, mode)

        if success:
            return _json_response(
                True,
                {
                    "output": output_num,
                    "scaler_mode": mode,
                    "scaler_mode_name": mode_names.get(mode),
                    "message": f"Output {output_num} scaler set to {mode_names.get(mode)}",
                },
            )
        else:
            return _json_response(False, error=f"Failed to set output {output_num} scaler", status=500)
    except BadRequestError as exc:
        return exc.response()
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting output scaler"), status=500)


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

        data = await parse_json_object(request)
        enabled = optional_bool(data, "enabled", True)

        _LOG.info(f"REST API: Setting output {output_num} ARC to {'enabled' if enabled else 'disabled'}")
        success = await matrix_device.set_output_arc(output_num, enabled)

        if success:
            return _json_response(
                True,
                {
                    "output": output_num,
                    "arc_enabled": enabled,
                    "message": f"Output {output_num} ARC {'enabled' if enabled else 'disabled'}",
                },
            )
        else:
            return _json_response(False, error=f"Failed to set output {output_num} ARC", status=500)
    except BadRequestError as exc:
        return exc.response()
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting output ARC"), status=500)


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

        data = await parse_json_object(request)
        muted = optional_bool(data, "muted", True)

        _LOG.info(f"REST API: Setting output {output_num} audio to {'muted' if muted else 'unmuted'}")

        # audio_mute is announced by the hub's event stream once the matrix reports the change
        # (docs/api/WEBSOCKET.md), not before the command is sent (API-09).
        success = await matrix_device.set_output_audio_mute(output_num, muted)

        if success:
            return _json_response(
                True,
                {
                    "output": output_num,
                    "audio_muted": muted,
                    "message": f"Output {output_num} audio {'muted' if muted else 'unmuted'}",
                },
            )
        else:
            return _json_response(False, error=f"Failed to set output {output_num} audio mute", status=500)
    except BadRequestError as exc:
        return exc.response()
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting output mute"), status=500)
