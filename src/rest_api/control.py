"""
Control endpoints for preset, switch, and power operations.
"""

import asyncio
import json
import logging

from aiohttp import web

from .utils import _json_response, get_input_names, get_matrix_device, require_connected, safe_error_message
from .websocket import broadcast_status_update

_LOG = logging.getLogger("rest_api.control")

# Default output for input cycling (can be overridden via query param)
DEFAULT_CYCLE_OUTPUT = 1

# Per-output locks for input cycling. Without these, two concurrent
# /api/input/next requests for the same output can both read the same
# ``current_input`` and both compute the same ``next_input`` — the
# second press effectively becomes a no-op.
_cycle_locks: dict[int, asyncio.Lock] = {
    i: asyncio.Lock() for i in range(1, 10)
}


@require_connected
async def handle_preset(request: web.Request) -> web.Response:
    """Recall a preset."""
    matrix_device = get_matrix_device()

    try:
        preset_num = int(request.match_info["preset"])
        if preset_num < 1 or preset_num > 8:
            return _json_response(False, error="Preset must be 1-8", status=400)

        _LOG.info(f"REST API: Recalling preset {preset_num}")

        # Optimistic update - broadcast before command for instant UI feedback
        await broadcast_status_update("preset_recall", {"preset": preset_num, "optimistic": True})

        success = await matrix_device.recall_preset(preset_num)

        if success:
            return _json_response(
                True,
                {
                    "preset": preset_num,
                    "name": f"Preset {preset_num}",
                    "message": f"Preset {preset_num} activated",
                },
            )
        else:
            # Send corrective broadcast so WebSocket clients can revert the
            # optimistic state — otherwise the UI shows a preset as active
            # when the matrix never actually switched.
            await broadcast_status_update(
                "preset_recall_failed", {"preset": preset_num}
            )
            return _json_response(False, error=f"Failed to recall preset {preset_num}", status=500)
    except ValueError:
        return _json_response(False, error="Invalid preset number", status=400)
    except Exception as e:
        _LOG.exception(f"Error recalling preset: {e}")
        return _json_response(False, error=safe_error_message(e, "recalling preset"), status=500)


async def handle_switch(request: web.Request) -> web.Response:
    """Route an input to an output, or to all outputs if output is not specified."""
    matrix_device = get_matrix_device()

    if matrix_device is None:
        return _json_response(False, error="Matrix device not configured", status=503)

    if not matrix_device.connected:
        return _json_response(False, error="Matrix not connected", status=503)

    try:
        data = await request.json()
        # Check for unknown fields
        allowed_fields = {"input", "output"}
        extra = set(data.keys()) - allowed_fields
        if extra:
            return _json_response(False, error=f"Unknown fields: {sorted(extra)}", status=400)
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
            await broadcast_status_update(
                "switch_all", {"input": input_num, "outputs": list(range(1, 9)), "optimistic": True}
            )

            success = await matrix_device.switch_input_to_all(input_num)

            if success:
                return _json_response(
                    True,
                    {
                        "input": input_num,
                        "output": "all",
                        "message": f"Input {input_num} routed to all outputs",
                    },
                )
            else:
                # Corrective broadcast so UI reverts optimistic state.
                await broadcast_status_update(
                    "switch_all_failed", {"input": input_num}
                )
                return _json_response(False, error="Failed to switch routing", status=500)

        # Single output routing
        output_num = int(output_num)

        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)

        _LOG.info(f"REST API: Switching input {input_num} to output {output_num}")

        # Optimistic update
        await broadcast_status_update("switch", {"input": input_num, "output": output_num, "optimistic": True})

        success = await matrix_device.switch_input(input_num, output_num)

        if success:
            return _json_response(
                True,
                {
                    "input": input_num,
                    "output": output_num,
                    "message": f"Input {input_num} routed to output {output_num}",
                },
            )
        else:
            # Corrective broadcast so UI reverts optimistic state.
            await broadcast_status_update(
                "switch_failed", {"input": input_num, "output": output_num}
            )
            return _json_response(False, error="Failed to switch routing", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.exception(f"Error switching: {e}")
        return _json_response(False, error=safe_error_message(e, "switching routing"), status=500)


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
        _LOG.exception(f"Error powering on: {e}")
        return _json_response(False, error=safe_error_message(e, "powering on"), status=500)


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
        _LOG.exception(f"Error powering off: {e}")
        return _json_response(False, error=safe_error_message(e, "powering off"), status=500)


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

        # Serialize cycling operations per-output so two concurrent
        # /api/input/next requests for the same output see the updated
        # current_input on the second request (otherwise both compute
        # the same next_input and the second press is a no-op).
        async with _cycle_locks[output_num]:
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
            return _json_response(
                True,
                {
                    "previous_input": current_input,
                    "current_input": next_input,
                    "input_name": input_name,
                    "output": output_num,
                    "message": f"Switched to {input_name} on output {output_num}",
                },
            )
        else:
            return _json_response(False, error="Failed to switch input", status=500)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.exception(f"Error cycling to next input: {e}")
        return _json_response(False, error=safe_error_message(e, "cycling to next input"), status=500)


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

        # Serialize cycling operations per-output (see handle_input_next).
        async with _cycle_locks[output_num]:
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
            return _json_response(
                True,
                {
                    "previous_input": current_input,
                    "current_input": prev_input,
                    "input_name": input_name,
                    "output": output_num,
                    "message": f"Switched to {input_name} on output {output_num}",
                },
            )
        else:
            return _json_response(False, error="Failed to switch input", status=500)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.exception(f"Error cycling to previous input: {e}")
        return _json_response(False, error=safe_error_message(e, "cycling to previous input"), status=500)


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
            return _json_response(
                True,
                {
                    "output": output_num,
                    "input": input_num,
                    "input_name": input_name,
                    "message": f"Output {output_num} now showing {input_name}",
                },
            )
        else:
            return _json_response(False, error="Failed to set output source", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid output/input number", status=400)
    except Exception as e:
        _LOG.exception(f"Error setting output source: {e}")
        return _json_response(False, error=safe_error_message(e, "setting output source"), status=500)


@require_connected
async def handle_preset_save(request: web.Request) -> web.Response:
    """Save current routing or a custom routing mapping to a preset."""
    matrix_device = get_matrix_device()

    try:
        preset_num = int(request.match_info["preset"])
        if preset_num < 1 or preset_num > 8:
            return _json_response(False, error="Preset must be 1-8", status=400)

        # Check if we have a custom routing body
        custom_routing = None
        if request.can_read_body:
            try:
                body = await request.json()
                custom_routing = body.get("routing")
            except Exception:
                pass

        if custom_routing:
            # Validate routing
            parsed_routing = {}
            for out_s, in_s in custom_routing.items():
                try:
                    out_num = int(out_s)
                    in_num = int(in_s)
                    if not (1 <= out_num <= 8 and 1 <= in_num <= 8):
                        return _json_response(False, error="Outputs and inputs must be 1-8", status=400)
                    parsed_routing[out_num] = in_num
                except (ValueError, TypeError):
                    return _json_response(False, error="Invalid output/input format", status=400)

            # Get current active routing to restore later
            raw_status = await matrix_device.get_status()
            routing_array = raw_status.get("routing", [])
            original_routing = {i + 1: src for i, src in enumerate(routing_array[:8]) if src is not None}

            _LOG.info(f"REST API: Applying temporary routing to save to preset {preset_num}")

            success = False
            # Wrap apply-save-restore in try/finally so the original routing
            # is ALWAYS restored, even if switch_input() or save_preset() raises
            # mid-sequence. Without this, an exception during step 1 leaves the
            # matrix with the temporary routing instead of the user's original.
            try:
                # 1. Switch to new routing
                for out_num, in_num in parsed_routing.items():
                    await matrix_device.switch_input(in_num, out_num)

                # 2. Save preset
                success = await matrix_device.save_preset(preset_num)
            finally:
                # 3. Restore original routing (always, even on exception)
                for out_num, in_num in original_routing.items():
                    try:
                        await matrix_device.switch_input(in_num, out_num)
                    except Exception as restore_err:
                        _LOG.error(
                            f"Failed to restore routing for output {out_num}: {restore_err}"
                        )

            if success:
                from .device_settings import set_preset_routing
                set_preset_routing(preset_num, parsed_routing)
                return _json_response(
                    True,
                    {
                        "preset": preset_num,
                        "routing": parsed_routing,
                        "message": f"Custom routing saved to preset {preset_num}",
                    },
                )
            else:
                return _json_response(False, error=f"Failed to save preset {preset_num}", status=500)
        else:
            # Save current routing as-is
            _LOG.info(f"REST API: Saving current routing to preset {preset_num}")
            success = await matrix_device.save_preset(preset_num)

            if success:
                try:
                    raw_status = await matrix_device.get_status()
                    routing_array = raw_status.get("routing", [])
                    current_routing = {i + 1: src for i, src in enumerate(routing_array[:8]) if src is not None}
                    from .device_settings import set_preset_routing
                    set_preset_routing(preset_num, current_routing)
                except Exception as ex:
                    _LOG.warning(f"Could not save current routing to device settings cache: {ex}")

                return _json_response(
                    True,
                    {
                        "preset": preset_num,
                        "message": f"Current routing saved to preset {preset_num}",
                    },
                )
            else:
                return _json_response(False, error=f"Failed to save preset {preset_num}", status=500)

    except ValueError:
        return _json_response(False, error="Invalid preset number", status=400)
    except Exception as e:
        _LOG.exception(f"Error saving preset: {e}")
        return _json_response(False, error=safe_error_message(e, "saving preset"), status=500)
