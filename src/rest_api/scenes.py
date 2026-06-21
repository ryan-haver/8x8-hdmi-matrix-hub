"""
Scene REST endpoints — Phase 7 compatibility shim.

This module is kept for backward compatibility. All scene endpoints
delegate to the Profile handlers since Scene and Profile are the same
underlying concept (Profile was introduced as the new name; Scene is
the legacy alias).

The ``/api/scene/*`` routes continue to work so existing clients and
saved automations don't break, but new code should target the
``/api/profile/*`` routes which are the canonical names.

Endpoints exposed:

- GET    /api/scenes                       — alias for /api/profiles
- GET    /api/scene/{scene_id}             — alias for /api/profile/{profile_id}
- POST   /api/scene                        — alias for /api/profile
- DELETE /api/scene/{scene_id}             — alias for /api/profile/{profile_id}
- POST   /api/scene/{scene_id}/recall      — alias for /api/profile/{profile_id}/recall
- POST   /api/scene/save-current           — capture current matrix state as a new profile
- GET/POST/PUT /api/scene/{scene_id}/cec   — alias for /api/profile/{profile_id}/cec
- POST   /api/scene/{scene_id}/cec/auto-resolve — alias for /api/profile/{profile_id}/cec/auto-resolve
"""

import json
import logging
import uuid

from aiohttp import web

from .profiles import (
    handle_create_profile,
    handle_delete_profile,
    handle_get_profile,
    handle_list_profiles,
    handle_profile_cec_config,
    handle_recall_profile,
)

_LOG = logging.getLogger("rest_api.scenes")

# =============================================================================
# Profile handler aliases with URL-key normalization
# =============================================================================
#
# The scene routes are registered as ``/api/scene/{scene_id}/...`` so
# ``request.match_info`` carries ``scene_id`` rather than the
# ``profile_id`` that the underlying profile handlers expect. Each
# wrapper below copies the key before delegating. ``handle_list_scenes``
# and ``handle_create_scene`` don't need normalization (the former
# lists all profiles, the latter reads the id from the JSON body).


def _alias_with_id_key(handler):
    """Return an async wrapper that copies scene_id into profile_id before calling ``handler``."""

    async def wrapper(request: web.Request) -> web.Response:
        if "profile_id" not in request.match_info and "scene_id" in request.match_info:
            request.match_info["profile_id"] = request.match_info["scene_id"]
        return await handler(request)

    wrapper.__name__ = getattr(handler, "__name__", "alias")
    return wrapper


def _clone_response_with_renamed_key(response: web.Response, key_map: dict[str, str]) -> web.Response:
    """Clone ``response`` with JSON body keys renamed per ``key_map``.

    aiohttp Response bodies are bytes; we re-parse, rename, and emit a new
    Response so the body shape matches what the legacy /api/scene/*
    callers expect (e.g. ``scenes`` instead of ``profiles``).
    """
    try:
        payload = json.loads(response.body)
    except (ValueError, TypeError):
        return response
    if isinstance(payload, dict) and "data" in payload and isinstance(payload["data"], dict):
        for old_key, new_key in key_map.items():
            if old_key in payload["data"]:
                payload["data"][new_key] = payload["data"].pop(old_key)
    new_body = json.dumps(payload).encode("utf-8")
    # Strip Content-Type from the cloned headers — web.Response would
    # raise "passing both Content-Type header and content_type" otherwise.
    headers = {k: v for k, v in response.headers.items() if k.lower() != "content-type"}
    return web.Response(
        body=new_body,
        status=response.status,
        content_type="application/json",
        headers=headers,
    )


async def handle_list_scenes(request: web.Request) -> web.Response:
    """Alias for ``handle_list_profiles`` that renames ``profiles`` → ``scenes``."""
    response = await handle_list_profiles(request)
    return _clone_response_with_renamed_key(response, {"profiles": "scenes"})


handle_create_scene = handle_create_profile
handle_get_scene = _alias_with_id_key(handle_get_profile)
handle_delete_scene = _alias_with_id_key(handle_delete_profile)


async def handle_recall_scene(request: web.Request) -> web.Response:
    """Alias for ``handle_recall_profile`` that normalizes the URL key and
    renames the response ``profile`` field to ``scene`` for backward compat.
    """
    if "profile_id" not in request.match_info and "scene_id" in request.match_info:
        request.match_info["profile_id"] = request.match_info["scene_id"]
    response = await handle_recall_profile(request)
    return _clone_response_with_renamed_key(response, {"profile": "scene"})


async def handle_scene_cec_config(request: web.Request) -> web.Response:
    """Alias for ``handle_profile_cec_config`` that normalizes the URL key."""
    if "profile_id" not in request.match_info and "scene_id" in request.match_info:
        request.match_info["profile_id"] = request.match_info["scene_id"]
    return await handle_profile_cec_config(request)


# =============================================================================
# Handlers without a direct profile equivalent — kept as compatibility shims.
# =============================================================================


async def handle_save_current_as_scene(request: web.Request) -> web.Response:
    """POST /api/scene/save-current — capture current matrix state as a new profile.

    Body: ``{"name": "Movie Night", "icon": "🎬"}``

    Reads the current routing from the matrix device and persists it as
    a new Profile via the same code path the regular create endpoint uses.
    """
    from .utils import _json_response, get_matrix_device, get_profile_manager

    profile_manager = get_profile_manager()
    matrix_device = get_matrix_device()

    if profile_manager is None:
        return _json_response(False, error="Profile manager not initialized", status=503)
    if matrix_device is None:
        return _json_response(False, error="Matrix device not available", status=503)

    try:
        body = await request.json()
        name = body.get("name", "Captured Scene")
        icon = body.get("icon", "📺")
        # Accept an explicit id from the request body for testability
        # and for clients that want stable references.
        profile_id = body.get("id") or f"scene_{uuid.uuid4().hex[:8]}"

        # Get current routing for all outputs. The matrix device exposes
        # this via ``get_output_status()`` which returns arrays
        # (``allsource``, ``allout``, ``allaudiomute``, ``allhdr``,
        # ``allhdcp``) indexed by position; fall back to
        # ``get_full_status()`` if the richer dataclass API is available.
        outputs: dict[int, dict] = {}
        try:
            if hasattr(matrix_device, "get_output_status"):
                status = await matrix_device.get_output_status()
                if isinstance(status, dict):
                    allsource = status.get("allsource", [])
                    allout = status.get("allout", [])
                    allaudiomute = status.get("allaudiomute", [])
                    allhdr = status.get("allhdr", [])
                    allhdcp = status.get("allhdcp", [])
                    # ``allout`` is indexed by position (i+1 = output number).
                    # The value at each position is just the output index
                    # echoed back; we use position+1 as the canonical key.
                    for i in range(len(allout)):
                        try:
                            outputs[i + 1] = {
                                "input": int(allsource[i]) if i < len(allsource) else 1,
                                "enabled": True,
                                "audio_mute": bool(allaudiomute[i]) if i < len(allaudiomute) else False,
                                "hdr_mode": int(allhdr[i]) if i < len(allhdr) else None,
                                "hdcp_mode": int(allhdcp[i]) if i < len(allhdcp) else None,
                            }
                        except (TypeError, ValueError, IndexError):
                            continue
            elif hasattr(matrix_device, "get_full_status"):
                full = await matrix_device.get_full_status()
                raw_outputs = getattr(full, "outputs", {}) or {}
                for out_num, out_data in raw_outputs.items():
                    try:
                        out_n = int(out_num)
                    except (TypeError, ValueError):
                        continue
                    if isinstance(out_data, dict):
                        outputs[out_n] = {
                            "input": int(out_data.get("input", 1)),
                            "enabled": bool(out_data.get("enabled", True)),
                            "audio_mute": bool(out_data.get("audio_mute", False)),
                            "hdr_mode": out_data.get("hdr_mode"),
                            "hdcp_mode": out_data.get("hdcp_mode"),
                        }
        except Exception as exc:
            return _json_response(
                False,
                error=f"Failed to read matrix status: {exc}",
                status=502,
            )

        profile = profile_manager.create_profile(
            profile_id=profile_id,
            name=name,
            outputs=outputs,
            icon=icon,
        )
        return _json_response(True, profile.to_dict(), status=200)
    except json.JSONDecodeError:
        from .utils import _json_response as _jr

        return _jr(False, error="Invalid JSON body", status=400)
    except Exception as exc:
        from .utils import _json_response as _jr

        _LOG.error("Error saving current as scene: %s", exc)
        return _jr(False, error=str(exc), status=500)


async def handle_auto_resolve_cec(request: web.Request) -> web.Response:
    """POST /api/scene/{scene_id}/cec/auto-resolve — alias for the profile endpoint.

    For Phase 7, this just delegates to the standard CEC config update
    with ``auto_resolved=True``. The richer resolver (formerly
    cec_resolver.resolve_scene_cec_config) is invoked when present.
    """
    from .utils import _json_response, get_profile_manager

    profile_manager = get_profile_manager()
    if profile_manager is None:
        return _json_response(False, error="Profile manager not initialized", status=503)

    try:
        scene_id = request.match_info.get("scene_id", "")
        if not scene_id:
            return _json_response(False, error="Scene id required", status=400)

        profile = profile_manager.get_profile(scene_id)
        if profile is None:
            return _json_response(False, error=f"Scene '{scene_id}' not found", status=404)

        # Best-effort: try the cec_resolver if available, otherwise fall back
        # to the default CecConfig with auto_resolved=True.
        try:
            from cec_resolver import resolve_scene_cec_config  # type: ignore

            resolved = resolve_scene_cec_config(profile)
            profile_manager.update_profile(scene_id, cec_config=resolved.to_dict())
            return _json_response(True, resolved.to_dict())
        except ImportError:
            # Fallback: just enable auto-resolve flag on the existing/default config
            profile.cec_config = profile.ensure_cec_config()
            profile.cec_config.auto_resolved = True
            profile_manager.update_profile(scene_id, cec_config=profile.cec_config.to_dict())
            return _json_response(True, profile.cec_config.to_dict())
    except Exception as exc:
        _LOG.error("Error auto-resolving CEC config: %s", exc)
        return _json_response(False, error=str(exc), status=500)
