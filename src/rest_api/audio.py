"""
Audio and system control endpoints.

Handles external audio matrix, system settings (beep, panel lock, LCD), and device info.
"""

import logging

from aiohttp import web

from .utils import _json_response, get_matrix_device, safe_error_message
from .validation import (
    BadRequestError,
    optional_bool,
    parse_json_object,
    require_field,
    validate_bool,
    validate_int,
    validate_port,
)

_LOG = logging.getLogger("rest_api.audio")


# =============================================================================
# External Audio (Ext-Audio) Endpoints
# =============================================================================


async def handle_ext_audio_status(request: web.Request) -> web.Response:
    """Get external audio matrix status."""
    matrix_device = get_matrix_device()

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

        status = await matrix_device.get_ext_audio_status()
        if status:
            outputs = []
            mode = status.get("mode", 0)
            for i in range(1, 9):
                idx = i - 1
                outputs.append(
                    {
                        "number": i,
                        "enabled": status.get("allout", [])[idx] == 1 if idx < len(status.get("allout", [])) else False,
                        "source": status.get("allsource", [])[idx] if idx < len(status.get("allsource", [])) else None,
                    }
                )
            return _json_response(
                True,
                {
                    "mode": mode,
                    "mode_name": OreiMatrix.get_ext_audio_mode_name(mode),
                    "outputs": outputs,
                    "raw": status,
                },
            )
        else:
            return _json_response(False, error="Failed to get ext-audio status", status=500)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "getting ext-audio status"), status=500)


async def handle_ext_audio_modes(request: web.Request) -> web.Response:
    """Get available ext-audio modes."""
    try:
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))
        from orei_matrix import OreiMatrix

        modes = OreiMatrix.get_ext_audio_modes()
        return _json_response(True, {"modes": modes})
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "getting ext-audio modes"), status=500)


async def handle_set_ext_audio_mode(request: web.Request) -> web.Response:
    """Set external audio routing mode."""
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

        data = await parse_json_object(request)
        mode = validate_int(require_field(data, "mode"), "mode", minimum=0, maximum=2, message="Invalid mode (0-2)")

        result = await matrix_device.set_ext_audio_mode(mode)

        if result:
            mode_name = OreiMatrix.get_ext_audio_mode_name(mode)
            return _json_response(
                True,
                {
                    "mode": mode,
                    "mode_name": mode_name,
                },
            )
        else:
            return _json_response(False, error="Failed to set ext-audio mode", status=500)
    except BadRequestError as exc:
        return exc.response()
    except ValueError:
        return _json_response(False, error="Invalid mode value", status=400)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting ext-audio mode"), status=500)


async def handle_set_ext_audio_enable(request: web.Request) -> web.Response:
    """Enable or disable ext-audio on a specific output."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)

    try:
        output_num = int(request.match_info.get("output", 0))
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Invalid output number (1-8)", status=400)

        data = await parse_json_object(request)
        enabled = validate_bool(require_field(data, "enabled"), "enabled")

        result = await matrix_device.set_ext_audio_enable(output_num, enabled)

        if result:
            return _json_response(
                True,
                {
                    "output": output_num,
                    "enabled": enabled,
                },
            )
        else:
            return _json_response(False, error="Failed to set ext-audio enable", status=500)
    except BadRequestError as exc:
        return exc.response()
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting ext-audio enable"), status=500)


async def handle_set_ext_audio_source(request: web.Request) -> web.Response:
    """Set audio source for a specific ext-audio output."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)

    try:
        output_num = int(request.match_info.get("output", 0))
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Invalid output number (1-8)", status=400)

        data = await parse_json_object(request)
        input_num = validate_port(require_field(data, "input"), message="Invalid input number (1-8)")

        result = await matrix_device.set_ext_audio_source(output_num, input_num)

        if result:
            return _json_response(
                True,
                {
                    "output": output_num,
                    "input": input_num,
                },
            )
        else:
            return _json_response(False, error="Failed to set ext-audio source", status=500)
    except BadRequestError as exc:
        return exc.response()
    except ValueError:
        return _json_response(False, error="Invalid output or input number", status=400)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting ext-audio source"), status=500)


# =============================================================================
# System Control Endpoints
# =============================================================================


async def handle_system_status(request: web.Request) -> web.Response:
    """Get system settings status."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)

    try:
        status = await matrix_device.get_system_status()
        if status:
            return _json_response(
                True,
                {
                    "power": "on" if status.get("power") == 1 else "off",
                    "beep_enabled": status.get("beep") == 1,
                    "panel_locked": status.get("lock") == 1,
                    "mode": status.get("mode"),
                    "baudrate": status.get("baudrate"),
                    "raw": status,
                },
            )
        else:
            return _json_response(False, error="Failed to get system status", status=500)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "getting system status"), status=500)


async def handle_device_info(request: web.Request) -> web.Response:
    """Get device/firmware information."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)

    try:
        info = await matrix_device.get_device_info()
        network = await matrix_device.get_network_info()

        device = {}
        if info:
            device.update(
                {
                    "model": info.get("model"),
                    "firmware_version": info.get("version"),
                    "web_version": info.get("webversion"),
                    "hostname": info.get("hostname"),
                    "mac_address": info.get("macaddress"),
                }
            )
        if network:
            device.update(
                {
                    "ip_address": network.get("ipaddress"),
                    "subnet": network.get("subnet"),
                    "gateway": network.get("gateway"),
                    "dhcp": network.get("dhcp") == 1,
                    "telnet_port": network.get("telnetport"),
                    "tcp_port": network.get("tcpport"),
                }
            )

        return _json_response(True, {"device": device, "raw": {"status": info, "network": network}})
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "getting device info"), status=500)


async def handle_set_beep(request: web.Request) -> web.Response:
    """Enable or disable system beep."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)

    try:
        data = await parse_json_object(request)
        enabled = optional_bool(data, "enabled", True)

        _LOG.info(f"REST API: Setting beep to {'enabled' if enabled else 'disabled'}")
        success = await matrix_device.set_beep(enabled)

        if success:
            return _json_response(
                True, {"beep_enabled": enabled, "message": f"Beep {'enabled' if enabled else 'disabled'}"}
            )
        else:
            return _json_response(False, error="Failed to set beep", status=500)
    except BadRequestError as exc:
        return exc.response()
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting beep"), status=500)


async def handle_set_panel_lock(request: web.Request) -> web.Response:
    """Lock or unlock front panel."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)

    try:
        data = await parse_json_object(request)
        locked = optional_bool(data, "locked", True)

        _LOG.info(f"REST API: Setting panel lock to {'locked' if locked else 'unlocked'}")
        success = await matrix_device.set_panel_lock(locked)

        if success:
            return _json_response(
                True, {"panel_locked": locked, "message": f"Panel {'locked' if locked else 'unlocked'}"}
            )
        else:
            return _json_response(False, error="Failed to set panel lock", status=500)
    except BadRequestError as exc:
        return exc.response()
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting panel lock"), status=500)


async def handle_system_reboot(request: web.Request) -> web.Response:
    """Reboot the matrix."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)

    try:
        _LOG.warning("REST API: Initiating system reboot")
        success = await matrix_device.system_reboot()

        if success:
            return _json_response(True, {"message": "Reboot initiated. Connection will be lost."})
        else:
            return _json_response(False, error="Failed to initiate reboot", status=500)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "rebooting system"), status=500)


async def handle_lcd_timeout_modes(request: web.Request) -> web.Response:
    """Get available LCD timeout modes."""
    try:
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent))
        from orei_matrix import OreiMatrix

        modes = OreiMatrix.get_lcd_timeout_modes()
        return _json_response(True, {"modes": modes})
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "getting LCD timeout modes"), status=500)


async def handle_set_lcd_timeout(request: web.Request) -> web.Response:
    """Set LCD display timeout."""
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

        data = await parse_json_object(request)
        mode = validate_int(require_field(data, "mode"), "mode", minimum=0, maximum=4, message="Invalid mode (0-4)")

        result = await matrix_device.set_lcd_timeout(mode)

        if result:
            mode_name = OreiMatrix.get_lcd_timeout_name(mode)
            return _json_response(
                True,
                {
                    "mode": mode,
                    "mode_name": mode_name,
                },
            )
        else:
            return _json_response(False, error="Failed to set LCD timeout", status=500)
    except BadRequestError as exc:
        return exc.response()
    except ValueError:
        return _json_response(False, error="Invalid mode value", status=400)
    except Exception as e:
        return _json_response(False, error=safe_error_message(e, "setting LCD timeout"), status=500)
