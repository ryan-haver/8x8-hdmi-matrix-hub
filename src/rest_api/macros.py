"""
CEC Macro management endpoints.

Handles macro CRUD, execution, and testing.
"""

import json
import logging
import re

from aiohttp import web

from .utils import _json_response, get_macro_manager

_LOG = logging.getLogger("rest_api.macros")

# Whitelist of valid CEC commands. Any other command string would be sent
# verbatim to the matrix and could trigger unintended actions.
VALID_INPUT_CEC_COMMANDS = frozenset({
    "POWER_ON", "POWER_OFF",
    "UP", "DOWN", "LEFT", "RIGHT", "SELECT", "MENU", "BACK",
    "PLAY", "PAUSE", "STOP", "REWIND", "FAST_FORWARD",
    "PREVIOUS", "NEXT",
    "VOLUME_UP", "VOLUME_DOWN", "MUTE",
})
VALID_OUTPUT_CEC_COMMANDS = frozenset({
    "POWER_ON", "POWER_OFF",
    "MUTE", "VOLUME_UP", "VOLUME_DOWN", "ACTIVE",
})

# Target format: "input_1" .. "input_8" or "output_1" .. "output_8".
VALID_TARGET_RE = re.compile(r"^(input|output)_([1-8])$")

# Limits that prevent DoS via huge payloads.
MAX_NAME_LEN = 200
MAX_DESCRIPTION_LEN = 2000
MAX_STEPS = 100
MAX_TARGETS_PER_STEP = 16
MAX_DELAY_MS = 60_000  # 60s per step delay max


def _validate_macro_text(name, description, *, name_required: bool) -> str | None:
    """Return an error string for an invalid macro name or description, else None.

    Shared by create (POST) and edit (PUT) so both enforce the same limits
    (API-28: PUT used to accept descriptions over MAX_DESCRIPTION_LEN).
    ``name_required`` is True on create; on edit an omitted name is kept.
    """
    if name_required and not name:
        return "Missing 'name' parameter"
    if name is not None:
        if not isinstance(name, str):
            return "'name' must be a string"
        if len(name) > MAX_NAME_LEN:
            return f"Name exceeds {MAX_NAME_LEN} characters"
    if isinstance(description, str) and len(description) > MAX_DESCRIPTION_LEN:
        return f"Description exceeds {MAX_DESCRIPTION_LEN} characters"
    return None


def _validate_macro_steps(steps):
    """Return an error string if invalid, else None. Pure function for reuse."""
    if not isinstance(steps, list):
        return "steps must be an array"
    if len(steps) == 0:
        return "Missing 'steps' parameter"
    if len(steps) > MAX_STEPS:
        return f"Max {MAX_STEPS} steps per macro (got {len(steps)})"
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            return f"Step {i + 1}: must be an object"
        cmd = step.get("command")
        if cmd is None:
            return f"Step {i + 1} missing 'command'"
        if not isinstance(cmd, str):
            return f"Step {i + 1}: 'command' must be a string"
        cmd_upper = cmd.upper()
        is_input_cmd = cmd_upper in VALID_INPUT_CEC_COMMANDS
        is_output_cmd = cmd_upper in VALID_OUTPUT_CEC_COMMANDS
        if not is_input_cmd and not is_output_cmd:
            return (
                f"Step {i + 1}: unknown command '{cmd}'. "
                f"Valid input commands: {sorted(VALID_INPUT_CEC_COMMANDS)}. "
                f"Valid output commands: {sorted(VALID_OUTPUT_CEC_COMMANDS)}."
            )
        targets = step.get("targets")
        if not isinstance(targets, list) or not targets:
            return f"Step {i + 1}: missing or empty 'targets'"
        if len(targets) > MAX_TARGETS_PER_STEP:
            return f"Step {i + 1}: max {MAX_TARGETS_PER_STEP} targets per step"
        for target in targets:
            if not isinstance(target, str) or not VALID_TARGET_RE.match(target):
                return (
                    f"Step {i + 1}: invalid target '{target}'. "
                    f"Must be 'input_N' or 'output_N' with N=1-8."
                )
            target_type = target.split("_")[0]
            if target_type == "input" and not is_input_cmd:
                return f"Step {i + 1}: command '{cmd}' cannot target inputs"
            if target_type == "output" and not is_output_cmd:
                return f"Step {i + 1}: command '{cmd}' cannot target outputs"
        delay = step.get("delay_ms", 0)
        if not isinstance(delay, int) or isinstance(delay, bool) or delay < 0 or delay > MAX_DELAY_MS:
            return f"Step {i + 1}: delay_ms must be integer 0-{MAX_DELAY_MS}"
    return None


async def handle_list_macros(request: web.Request) -> web.Response:
    """List all saved CEC macros."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macros = macro_manager.list_macros()
        return _json_response(True, {"macros": macros})
    except Exception as e:
        _LOG.exception(f"Error listing macros: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_get_macro(request: web.Request) -> web.Response:
    """Get details of a specific macro."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)

        macro = macro_manager.get_macro(macro_id)
        if macro is None:
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)

        return _json_response(True, macro.to_dict())
    except Exception as e:
        _LOG.exception(f"Error getting macro: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_create_macro(request: web.Request) -> web.Response:
    """Create a new CEC macro."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        data = await request.json()

        name = data.get("name")
        steps = data.get("steps", [])
        icon = data.get("icon", "⚡")
        description = data.get("description", "")
        macro_id = data.get("id")

        text_error = _validate_macro_text(name, description, name_required=True)
        if text_error:
            return _json_response(False, error=text_error, status=400)

        # Comprehensive validation: command whitelist, targets format,
        # command/target type matching, delay range, max step count.
        step_error = _validate_macro_steps(steps)
        if step_error:
            return _json_response(False, error=step_error, status=400)

        macro = macro_manager.create_macro(
            name=name,
            steps=steps,
            icon=icon,
            description=description,
            macro_id=macro_id,
        )
        _LOG.info(f"Macro '{name}' ({macro.id}) created")

        return _json_response(True, macro.to_dict())
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.exception(f"Error creating macro: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_update_macro(request: web.Request) -> web.Response:
    """Update an existing CEC macro."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)

        data = await request.json()

        name = data.get("name")
        steps = data.get("steps")
        icon = data.get("icon")
        description = data.get("description")

        # The same name/description limits as create (API-28).
        text_error = _validate_macro_text(name, description, name_required=False)
        if text_error:
            return _json_response(False, error=text_error, status=400)

        # Comprehensive validation of new steps if provided
        if steps is not None:
            step_error = _validate_macro_steps(steps)
            if step_error:
                return _json_response(False, error=step_error, status=400)

        macro = macro_manager.update_macro(
            macro_id=macro_id,
            name=name,
            steps=steps,
            icon=icon,
            description=description,
        )

        if macro is None:
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)

        _LOG.info(f"Macro '{macro_id}' updated")
        return _json_response(True, macro.to_dict())
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.exception(f"Error updating macro: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_delete_macro(request: web.Request) -> web.Response:
    """Delete a CEC macro."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)

        if macro_manager.delete_macro(macro_id):
            _LOG.info(f"Macro '{macro_id}' deleted")
            return _json_response(True, {"deleted": macro_id})
        else:
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)
    except Exception as e:
        _LOG.exception(f"Error deleting macro: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_execute_macro(request: web.Request) -> web.Response:
    """Execute a CEC macro."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)

        if not macro_manager.get_macro(macro_id):
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)

        # Parse optional timeout_s parameter from request body
        data = await request.json() if request.can_read_body else {}
        timeout_s = data.get("timeout_s")
        if timeout_s is not None:
            if not isinstance(timeout_s, (int, float)) or timeout_s <= 0:
                return _json_response(False, error="timeout_s must be a positive number", status=400)

        result = await macro_manager.execute_macro(macro_id, timeout_s=timeout_s if timeout_s is not None else 300.0)

        if result.get("success"):
            return _json_response(True, result)
        else:
            return _json_response(False, error=result.get("error", "Execution failed"), status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON", status=400)
    except Exception as e:
        _LOG.exception(f"Error executing macro: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_test_macro(request: web.Request) -> web.Response:
    """Test/validate a CEC macro without executing (dry run)."""
    macro_manager = get_macro_manager()

    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)

    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)

        if not macro_manager.get_macro(macro_id):
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)

        result = await macro_manager.test_macro(macro_id)

        return _json_response(True, result)
    except Exception as e:
        _LOG.exception(f"Error testing macro: {e}")
        return _json_response(False, error=str(e), status=500)


# =============================================================================
# Phase 7: Macro surface-visibility endpoints (favorite + dashboard)
# =============================================================================


async def handle_list_favorite_macros(request: web.Request) -> web.Response:
    """GET /api/cec/macros/favorites — list macros marked as favorites."""
    macro_manager = get_macro_manager()
    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)
    try:
        macros = macro_manager.list_favorites()
        return _json_response(
            True,
            {
                "macros": [m.to_dict() for m in macros],
            },
        )
    except Exception as e:
        _LOG.exception(f"Error listing favorite macros: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_toggle_macro_favorite(request: web.Request) -> web.Response:
    """POST /api/cec/macro/{id}/favorite — toggle favorite flag."""
    macro_manager = get_macro_manager()
    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)
    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)
        macro = macro_manager.toggle_favorite(macro_id)
        if macro is None:
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)
        return _json_response(
            True,
            {
                "id": macro.id,
                "favorite": macro.favorite,
            },
        )
    except Exception as e:
        _LOG.exception(f"Error toggling macro favorite: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_toggle_macro_dashboard(request: web.Request) -> web.Response:
    """POST /api/cec/macro/{id}/dashboard — toggle dashboard-visible flag."""
    macro_manager = get_macro_manager()
    if macro_manager is None:
        return _json_response(False, error="Macro manager not initialized", status=503)
    try:
        macro_id = request.match_info.get("macro_id", "")
        if not macro_id:
            return _json_response(False, error="Macro ID required", status=400)
        macro = macro_manager.toggle_dashboard_visible(macro_id)
        if macro is None:
            return _json_response(False, error=f"Macro '{macro_id}' not found", status=404)
        return _json_response(
            True,
            {
                "id": macro.id,
                "dashboard_visible": macro.dashboard_visible,
            },
        )
    except Exception as e:
        _LOG.exception(f"Error toggling macro dashboard flag: {e}")
        return _json_response(False, error=str(e), status=500)
