"""
Device Settings - Persistent storage for device customizations.

Handles storage of:
- Custom device names
- Device icons
- Device colors/branding
- Per-device metadata
"""

import json
import logging
from pathlib import Path

from aiohttp import web

from persistence import ensure_data_dir, get_data_dir, migrate_legacy_file

from .utils import _json_response
from .websocket import broadcast_status_update

_LOG = logging.getLogger("rest_api.device_settings")

# Storage file location (resolved from persistent data dir at init time)
_SETTINGS_FILE = "device_settings.json"
_settings_path: Path | None = None
_settings_cache: dict = {}


# =============================================================================
# Settings Storage
# =============================================================================


def init_device_settings(data_dir: Path | None = None):
    """Initialize device settings with the data directory path.

    :param data_dir: Explicit data directory (defaults to ``persistence.get_data_dir()``
                     which honors ``MATRIX_DATA_DIR`` and ``UC_CONFIG_HOME`` env vars).
    """
    global _settings_path, _settings_cache

    if data_dir is None:
        data_dir = get_data_dir()

    # Ensure directory exists, then migrate any legacy file.
    ensure_data_dir(data_dir)
    target = data_dir / _SETTINGS_FILE
    migrate_legacy_file(target, _SETTINGS_FILE)

    _settings_path = target
    _load_settings()
    _LOG.info(f"Device settings initialized from {_settings_path}")


def _load_settings():
    """Load settings from disk into memory cache."""
    global _settings_cache

    if _settings_path is None or not _settings_path.exists():
        _settings_cache = _get_default_settings()
        return

    try:
        with open(_settings_path, encoding="utf-8") as f:
            _settings_cache = json.load(f)
        _LOG.debug(f"Loaded device settings from {_settings_path}")
    except Exception as e:
        _LOG.exception(f"Error loading device settings: {e}")
        _settings_cache = _get_default_settings()


def _save_settings():
    """Save settings cache to disk."""
    if _settings_path is None:
        _LOG.warning("Cannot save settings: path not initialized")
        return False

    try:
        # Ensure directory exists
        _settings_path.parent.mkdir(parents=True, exist_ok=True)

        from _file_io import atomic_write_json

        atomic_write_json(_settings_path, _settings_cache)

        _LOG.debug(f"Saved device settings to {_settings_path}")
        return True
    except Exception as e:
        _LOG.exception(f"Error saving device settings: {e}")
        return False


def _get_default_settings() -> dict:
    """Return default settings structure."""
    return {
        "version": 2,
        "inputs": {
            str(i): {
                "name": f"Input {i}",
                "icon": None,
                "color": None,
            }
            for i in range(1, 9)
        },
        "outputs": {
            str(i): {
                "name": f"Output {i}",
                "icon": None,
                "color": None,
            }
            for i in range(1, 9)
        },
        # Phase 7: Preset surface-visibility flags. Presets are hardware-fixed
        # (the matrix only has 8) so they can't carry their own fields — we
        # track which preset numbers the user has favorited or pinned to the
        # dashboard as small lists here.
        "favorite_presets": [],
        "dashboard_presets": [],
        "presets": {str(i): {"name": f"Preset {i}"} for i in range(1, 9)},
    }


# =============================================================================
# Accessor Functions
# =============================================================================


def get_device_settings() -> dict:
    """Get all device settings."""
    if not _settings_cache:
        _load_settings()
    return _settings_cache


def get_input_setting(input_num: int) -> dict:
    """Get settings for a specific input."""
    settings = get_device_settings()
    return settings.get("inputs", {}).get(
        str(input_num),
        {
            "name": f"Input {input_num}",
            "icon": None,
            "color": None,
        },
    )


def get_output_setting(output_num: int) -> dict:
    """Get settings for a specific output."""
    settings = get_device_settings()
    return settings.get("outputs", {}).get(
        str(output_num),
        {
            "name": f"Output {output_num}",
            "icon": None,
            "color": None,
        },
    )


def set_input_setting(
    input_num: int, name: str | None = None, icon: str | None = None, color: str | None = None
) -> bool:
    """Update settings for a specific input."""
    global _settings_cache

    if "inputs" not in _settings_cache:
        _settings_cache["inputs"] = {}

    key = str(input_num)
    if key not in _settings_cache["inputs"]:
        _settings_cache["inputs"][key] = {"name": f"Input {input_num}", "icon": None, "color": None}

    if name is not None:
        _settings_cache["inputs"][key]["name"] = name
    if icon is not None:
        _settings_cache["inputs"][key]["icon"] = icon
    if color is not None:
        _settings_cache["inputs"][key]["color"] = color

    return _save_settings()


def set_output_setting(
    output_num: int, name: str | None = None, icon: str | None = None, color: str | None = None
) -> bool:
    """Update settings for a specific output."""
    global _settings_cache

    if "outputs" not in _settings_cache:
        _settings_cache["outputs"] = {}

    key = str(output_num)
    if key not in _settings_cache["outputs"]:
        _settings_cache["outputs"][key] = {"name": f"Output {output_num}", "icon": None, "color": None}

    if name is not None:
        _settings_cache["outputs"][key]["name"] = name
    if icon is not None:
        _settings_cache["outputs"][key]["icon"] = icon
    if color is not None:
        _settings_cache["outputs"][key]["color"] = color

    return _save_settings()


def get_preset_setting(preset_num: int) -> dict:
    """Get settings for a specific preset (custom name)."""
    settings = get_device_settings()
    return settings.get("presets", {}).get(str(preset_num), {"name": f"Preset {preset_num}"})


def set_preset_name(preset_num: int, name: str) -> bool:
    """Update custom name for a preset."""
    global _settings_cache
    if "presets" not in _settings_cache:
        _settings_cache["presets"] = {}
    key = str(preset_num)
    if key not in _settings_cache["presets"]:
        _settings_cache["presets"][key] = {}
    _settings_cache["presets"][key]["name"] = name
    return _save_settings()


def set_preset_routing(preset_num: int, routing: dict[int, int]) -> bool:
    """Update custom routing for a preset."""
    global _settings_cache
    if "presets" not in _settings_cache:
        _settings_cache["presets"] = {}
    key = str(preset_num)
    if key not in _settings_cache["presets"]:
        _settings_cache["presets"][key] = {"name": f"Preset {preset_num}"}
    _settings_cache["presets"][key]["routing"] = {str(k): v for k, v in routing.items()}
    return _save_settings()


# =============================================================================
# Phase 7: Preset surface-visibility helpers
# =============================================================================
#
# Hardware presets are fixed at 8 slots on the matrix itself, so we can't
# attach fields to them directly. Instead, the user-facing lists live in
# device_settings.json and are updated through these helpers.

_VALID_PRESET_RANGE = range(1, 9)


def _coerce_preset_list(raw) -> list[int]:
    """Coerce arbitrary input to a sorted, deduped list of valid preset numbers."""
    if not isinstance(raw, list):
        return []
    out: set[int] = set()
    for item in raw:
        try:
            n = int(item)
        except (TypeError, ValueError):
            continue
        if n in _VALID_PRESET_RANGE:
            out.add(n)
    return sorted(out)


def get_favorite_presets() -> list[int]:
    """Return the list of hardware preset numbers marked as favorites."""
    if not _settings_cache:
        _load_settings()
    return _coerce_preset_list(_settings_cache.get("favorite_presets", []))


def get_dashboard_presets() -> list[int]:
    """Return the list of hardware preset numbers pinned to the dashboard."""
    if not _settings_cache:
        _load_settings()
    return _coerce_preset_list(_settings_cache.get("dashboard_presets", []))


def set_favorite_presets(presets: list[int]) -> bool:
    """Replace the full favorites list with the supplied preset numbers.

    Persists atomically — invalid or out-of-range entries are stripped.
    """
    global _settings_cache
    _settings_cache["favorite_presets"] = _coerce_preset_list(presets)
    return _save_settings()


def set_dashboard_presets(presets: list[int]) -> bool:
    """Replace the full dashboard-pinned list with the supplied preset numbers."""
    global _settings_cache
    _settings_cache["dashboard_presets"] = _coerce_preset_list(presets)
    return _save_settings()


def toggle_favorite_preset(preset_num: int) -> bool:
    """Add the preset number to favorites if absent, remove if present.

    Returns the new favorite state (``True`` if it's now a favorite).
    """
    global _settings_cache
    current = _coerce_preset_list(_settings_cache.get("favorite_presets", []))
    if preset_num in current:
        current.remove(preset_num)
        new_state = False
    else:
        if preset_num not in _VALID_PRESET_RANGE:
            return False
        current.append(preset_num)
        current.sort()
        new_state = True
    _settings_cache["favorite_presets"] = current
    if _save_settings():
        return new_state
    return False


def toggle_dashboard_preset(preset_num: int) -> bool:
    """Add the preset number to the dashboard if absent, remove if present."""
    global _settings_cache
    current = _coerce_preset_list(_settings_cache.get("dashboard_presets", []))
    if preset_num in current:
        current.remove(preset_num)
        new_state = False
    else:
        if preset_num not in _VALID_PRESET_RANGE:
            return False
        current.append(preset_num)
        current.sort()
        new_state = True
    _settings_cache["dashboard_presets"] = current
    if _save_settings():
        return new_state
    return False


# =============================================================================
# API Handlers
# =============================================================================


async def handle_get_device_settings(request: web.Request) -> web.Response:
    """GET /api/device-settings - Get all device settings."""
    try:
        settings = get_device_settings()
        return _json_response(True, settings)
    except Exception as e:
        _LOG.exception(f"Error getting device settings: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_get_input_settings(request: web.Request) -> web.Response:
    """GET /api/device-settings/input/{input} - Get settings for a specific input."""
    try:
        input_num = int(request.match_info["input"])
        if input_num < 1 or input_num > 8:
            return _json_response(False, error="Input must be 1-8", status=400)

        settings = get_input_setting(input_num)
        return _json_response(True, {"input": input_num, **settings})
    except ValueError:
        return _json_response(False, error="Invalid input number", status=400)
    except Exception as e:
        _LOG.exception(f"Error getting input settings: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_set_input_settings(request: web.Request) -> web.Response:
    """POST /api/device-settings/input/{input} - Update settings for a specific input."""
    try:
        input_num = int(request.match_info["input"])
        if input_num < 1 or input_num > 8:
            return _json_response(False, error="Input must be 1-8", status=400)

        data = await request.json()
        name = data.get("name")
        icon = data.get("icon")
        color = data.get("color")

        success = set_input_setting(input_num, name=name, icon=icon, color=color)

        if success:
            # Broadcast update to connected clients
            await broadcast_status_update(
                "device_settings", {"type": "input", "number": input_num, **get_input_setting(input_num)}
            )

            return _json_response(
                True,
                {"input": input_num, **get_input_setting(input_num), "message": f"Input {input_num} settings updated"},
            )
        else:
            return _json_response(False, error="Failed to save settings", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid input number", status=400)
    except Exception as e:
        _LOG.exception(f"Error setting input settings: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_get_output_settings(request: web.Request) -> web.Response:
    """GET /api/device-settings/output/{output} - Get settings for a specific output."""
    try:
        output_num = int(request.match_info["output"])
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)

        settings = get_output_setting(output_num)
        return _json_response(True, {"output": output_num, **settings})
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.exception(f"Error getting output settings: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_set_output_settings(request: web.Request) -> web.Response:
    """POST /api/device-settings/output/{output} - Update settings for a specific output."""
    try:
        output_num = int(request.match_info["output"])
        if output_num < 1 or output_num > 8:
            return _json_response(False, error="Output must be 1-8", status=400)

        data = await request.json()
        name = data.get("name")
        icon = data.get("icon")
        color = data.get("color")

        success = set_output_setting(output_num, name=name, icon=icon, color=color)

        if success:
            # Broadcast update to connected clients
            await broadcast_status_update(
                "device_settings", {"type": "output", "number": output_num, **get_output_setting(output_num)}
            )

            return _json_response(
                True,
                {
                    "output": output_num,
                    **get_output_setting(output_num),
                    "message": f"Output {output_num} settings updated",
                },
            )
        else:
            return _json_response(False, error="Failed to save settings", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.exception(f"Error setting output settings: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_bulk_update_settings(request: web.Request) -> web.Response:
    """POST /api/device-settings - Bulk update device settings.

    FIX (F12.7): collect per-entry errors instead of silently dropping
    invalid keys. Returns ``applied`` and ``errors`` arrays so the caller
    knows exactly which entries were updated and which were rejected.
    """
    try:
        data = await request.json()
        updated_inputs = []
        updated_outputs = []
        errors = []

        # Update inputs
        if "inputs" in data:
            for key, settings in data["inputs"].items():
                try:
                    input_num = int(key)
                except (ValueError, TypeError):
                    errors.append(f"inputs.{key}: not an integer")
                    continue
                if not (1 <= input_num <= 8):
                    errors.append(f"inputs.{key}: port must be 1-8")
                    continue
                if not isinstance(settings, dict):
                    errors.append(f"inputs.{input_num}: must be an object")
                    continue
                set_input_setting(
                    input_num,
                    name=settings.get("name"),
                    icon=settings.get("icon"),
                    color=settings.get("color"),
                )
                updated_inputs.append(input_num)

        # Update outputs
        if "outputs" in data:
            for key, settings in data["outputs"].items():
                try:
                    output_num = int(key)
                except (ValueError, TypeError):
                    errors.append(f"outputs.{key}: not an integer")
                    continue
                if not (1 <= output_num <= 8):
                    errors.append(f"outputs.{key}: port must be 1-8")
                    continue
                if not isinstance(settings, dict):
                    errors.append(f"outputs.{output_num}: must be an object")
                    continue
                set_output_setting(
                    output_num,
                    name=settings.get("name"),
                    icon=settings.get("icon"),
                    color=settings.get("color"),
                )
                updated_outputs.append(output_num)

        # Broadcast full settings update
        await broadcast_status_update("device_settings_full", get_device_settings())

        return _json_response(
            True,
            {
                "updated_inputs": updated_inputs,
                "updated_outputs": updated_outputs,
                "errors": errors if errors else None,
                "settings": get_device_settings(),
            },
        )
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.exception(f"Error bulk updating settings: {e}")
        return _json_response(False, error=str(e), status=500)


# =============================================================================
# Phase 7: Hardware-preset surface-visibility endpoints
# =============================================================================
#
# Hardware presets are fixed at 8 slots on the matrix itself, so they
# can't carry their own fields. These endpoints manage the
# ``favorite_presets`` and ``dashboard_presets`` lists in
# device_settings.json — the user-facing way to favorite or pin a
# hardware preset.


async def handle_get_favorite_presets(request: web.Request) -> web.Response:
    """GET /api/device-settings/favorite-presets — list favorite preset numbers."""
    try:
        return _json_response(True, {"favorite_presets": get_favorite_presets()})
    except Exception as e:
        _LOG.exception(f"Error getting favorite presets: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_get_dashboard_presets(request: web.Request) -> web.Response:
    """GET /api/device-settings/dashboard-presets — list dashboard-pinned preset numbers."""
    try:
        return _json_response(True, {"dashboard_presets": get_dashboard_presets()})
    except Exception as e:
        _LOG.exception(f"Error getting dashboard presets: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_set_favorite_presets(request: web.Request) -> web.Response:
    """PUT /api/device-settings/favorite-presets — replace the full favorites list.

    Body: ``{"favorite_presets": [1, 3, 5]}`` — only valid preset numbers (1-8)
    are kept; others are silently dropped.
    """
    try:
        body = await request.json()
        if "favorite_presets" not in body:
            return _json_response(False, error="Missing 'favorite_presets' field", status=400)
        if not isinstance(body["favorite_presets"], list):
            return _json_response(False, error="'favorite_presets' must be a list", status=400)
        if not set_favorite_presets(body["favorite_presets"]):
            return _json_response(False, error="Failed to save favorite presets", status=500)
        return _json_response(True, {"favorite_presets": get_favorite_presets()})
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.exception(f"Error setting favorite presets: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_set_dashboard_presets(request: web.Request) -> web.Response:
    """PUT /api/device-settings/dashboard-presets — replace the full dashboard list.

    Body: ``{"dashboard_presets": [2, 4]}``
    """
    try:
        body = await request.json()
        if "dashboard_presets" not in body:
            return _json_response(False, error="Missing 'dashboard_presets' field", status=400)
        if not isinstance(body["dashboard_presets"], list):
            return _json_response(False, error="'dashboard_presets' must be a list", status=400)
        if not set_dashboard_presets(body["dashboard_presets"]):
            return _json_response(False, error="Failed to save dashboard presets", status=500)
        return _json_response(True, {"dashboard_presets": get_dashboard_presets()})
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.exception(f"Error setting dashboard presets: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_toggle_favorite_preset(request: web.Request) -> web.Response:
    """POST /api/device-settings/favorite-presets/{preset}/toggle — toggle one preset."""
    try:
        try:
            preset_num = int(request.match_info["preset"])
        except (KeyError, TypeError, ValueError):
            return _json_response(False, error="Invalid preset number", status=400)
        if preset_num < 1 or preset_num > 8:
            return _json_response(False, error="Preset number must be 1-8", status=400)
        new_state = toggle_favorite_preset(preset_num)
        return _json_response(
            True,
            {
                "preset": preset_num,
                "favorite": new_state,
                "favorite_presets": get_favorite_presets(),
            },
        )
    except Exception as e:
        _LOG.exception(f"Error toggling favorite preset: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_toggle_dashboard_preset(request: web.Request) -> web.Response:
    """POST /api/device-settings/dashboard-presets/{preset}/toggle — toggle one preset."""
    try:
        try:
            preset_num = int(request.match_info["preset"])
        except (KeyError, TypeError, ValueError):
            return _json_response(False, error="Invalid preset number", status=400)
        if preset_num < 1 or preset_num > 8:
            return _json_response(False, error="Preset number must be 1-8", status=400)
        new_state = toggle_dashboard_preset(preset_num)
        return _json_response(
            True,
            {
                "preset": preset_num,
                "dashboard_visible": new_state,
                "dashboard_presets": get_dashboard_presets(),
            },
        )
    except Exception as e:
        _LOG.exception(f"Error toggling dashboard preset: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_set_preset_name(request: web.Request) -> web.Response:
    """POST /api/device-settings/preset/{preset}/name - Rename a preset."""
    try:
        preset_num = int(request.match_info["preset"])
        if not (1 <= preset_num <= 8):
            return _json_response(False, error="Preset must be 1-8", status=400)

        data = await request.json()
        name = data.get("name")
        if not name:
            return _json_response(False, error="'name' is required in body", status=400)

        success = set_preset_name(preset_num, name)
        if success:
            await broadcast_status_update("device_settings", {"type": "preset", "number": preset_num, "name": name})
            return _json_response(
                True, {"preset": preset_num, "name": name, "message": f"Preset {preset_num} renamed to {name}"}
            )
        else:
            return _json_response(False, error="Failed to save settings", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid preset number", status=400)
    except Exception as e:
        _LOG.exception(f"Error renaming preset {preset_num}: {e}")
        return _json_response(False, error=str(e), status=500)
