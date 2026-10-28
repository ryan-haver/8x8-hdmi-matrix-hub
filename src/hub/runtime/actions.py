"""Shared execution entry and surface-specific compatibility projections."""

from contextlib import asynccontextmanager
from contextvars import ContextVar
from functools import wraps

# Per-task readback of a cycle performed by the bool-returning provider. REST
# consumes this immediately; no observation is shared with another request.
_cycle_observation: ContextVar[tuple[int, int] | None] = ContextVar("cycle_observation", default=None)


async def run_action_envelope(runtime, kind, action_id, *, passcode=None):
    """Integration envelope; REST handlers retain their historical bodies."""
    result = await runtime.run_action(kind, action_id, passcode=passcode)
    if kind == "scene" and "scene_id" in result.data:
        runtime.notify_catalog_changed()
    return {**result.to_response_dict(), "status": result.status_code}


async def run_rest_action(kind, action_id, *, passcode=None, params=None):
    from rest_api.utils import get_action_runner, get_runtime

    runtime = get_runtime()
    if runtime is not None:
        result = await runtime.run_action(kind, action_id, passcode=passcode, params=params)
        if kind == "scene" and "scene_id" in result.data:
            runtime.notify_catalog_changed()
        return result
    return await get_action_runner().run(kind, action_id, passcode=passcode, params=params)


def pin_response(result):
    """Project existing item PIN errors, including the lockout header."""
    from rest_api.utils import _json_response

    if result.status_code not in (403, 429):
        return None
    data = {"error": result.code, f"{result.kind}_id": result.action_id}
    if result.kind == "scene":
        data["requires_scene_passcode"] = True
    error = None
    if result.status_code == 429:
        seconds = result.data["retry_after"]
        data["retry_after"] = seconds
        error = f"Too many wrong passcodes; try again in {seconds} s"
    if result.kind == "scene":
        from aiohttp import web

        body = {"success": False, "data": data}
        if error is not None:
            body["error"] = error
        response = web.json_response(body, status=result.status_code)
    else:
        response = _json_response(False, data, error=error, status=result.status_code)
    if result.status_code == 429:
        response.headers["Retry-After"] = str(result.data["retry_after"])
    return response


def catalog_changes(handler):
    """Invalidate shared catalogs after a successful REST catalog mutation."""
    @wraps(handler)
    async def changed(*args, **kwargs):
        response = await handler(*args, **kwargs)
        if response.status < 300 and args[0].method != "GET":
            from rest_api.utils import get_runtime

            runtime = get_runtime()
            if runtime is not None:
                runtime.notify_catalog_changed()
        return response
    return changed


@asynccontextmanager
async def command_operation():
    """Keep compound REST operations in the runtime's tracked transaction."""
    from rest_api.utils import get_runtime

    runtime = get_runtime()
    if runtime is None:
        yield
    else:
        async with runtime.operation():
            yield


async def direct_command(method, *args):
    """Use the runtime provider, with legacy standalone compatibility."""
    from rest_api.utils import get_matrix_device, get_runtime

    runtime = get_runtime()
    if runtime is not None:
        # Enablement is an existing protocol operation outside the frozen typed
        # provider surface, using the same runtime transaction and client.
        if method == "set_cec_enable":
            return await runtime.protocol(method, *args)
        return await getattr(runtime.commands, method)(*args)
    matrix = get_matrix_device()
    if method == "switch":
        input_num, output_num = args
        if output_num is None:
            return await matrix.switch_input_to_all(input_num)
        return await matrix.switch_input(input_num, output_num)
    if method == "power":
        return await (matrix.power_on() if args[0] else matrix.power_off())
    if method == "send_cec":
        kind, port, command = args
        return await matrix.send_cec(command, port, is_output=kind == "output")
    return await getattr(matrix, method)(*args)
