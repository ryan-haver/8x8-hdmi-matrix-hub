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
from typing import Any, Optional

from aiohttp import web

from .utils import _json_response
from .websocket import broadcast_status_update

_LOG = logging.getLogger("rest_api.device_settings")

# Storage file location (relative to data/ directory)
_SETTINGS_FILE = "device_settings.json"
_settings_path: Optional[Path] = None
_settings_cache: dict = {}


# =============================================================================
# Settings Storage
# =============================================================================

def init_device_settings(data_dir: Optional[Path] = None):
    """Initialize device settings with the data directory path."""
    global _settings_path, _settings_cache
    
    if data_dir is None:
        # Default to data/ in project root
        data_dir = Path(__file__).parent.parent.parent / "data"
    
    _settings_path = data_dir / _SETTINGS_FILE
    _load_settings()
    _LOG.info(f"Device settings initialized from {_settings_path}")


def _load_settings():
    """Load settings from disk into memory cache."""
    global _settings_cache
    
    if _settings_path is None or not _settings_path.exists():
        _settings_cache = _get_default_settings()
        return
    
    try:
        with open(_settings_path, "r", encoding="utf-8") as f:
            _settings_cache = json.load(f)
        _LOG.debug(f"Loaded device settings from {_settings_path}")
    except Exception as e:
        _LOG.error(f"Error loading device settings: {e}")
        _settings_cache = _get_default_settings()


def _save_settings():
    """Save settings cache to disk."""
    if _settings_path is None:
        _LOG.warning("Cannot save settings: path not initialized")
        return False
    
    try:
        # Ensure directory exists
        _settings_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(_settings_path, "w", encoding="utf-8") as f:
            json.dump(_settings_cache, f, indent=2)
        
        _LOG.debug(f"Saved device settings to {_settings_path}")
        return True
    except Exception as e:
        _LOG.error(f"Error saving device settings: {e}")
        return False


def _get_default_settings() -> dict:
    """Return default settings structure."""
    return {
        "version": 1,
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
    return settings.get("inputs", {}).get(str(input_num), {
        "name": f"Input {input_num}",
        "icon": None,
        "color": None,
    })


def get_output_setting(output_num: int) -> dict:
    """Get settings for a specific output."""
    settings = get_device_settings()
    return settings.get("outputs", {}).get(str(output_num), {
        "name": f"Output {output_num}",
        "icon": None,
        "color": None,
    })


def set_input_setting(input_num: int, name: Optional[str] = None, icon: Optional[str] = None, color: Optional[str] = None) -> bool:
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


def set_output_setting(output_num: int, name: Optional[str] = None, icon: Optional[str] = None, color: Optional[str] = None) -> bool:
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


# =============================================================================
# API Handlers
# =============================================================================

async def handle_get_device_settings(request: web.Request) -> web.Response:
    """GET /api/device-settings - Get all device settings."""
    try:
        settings = get_device_settings()
        return _json_response(True, settings)
    except Exception as e:
        _LOG.error(f"Error getting device settings: {e}")
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
        _LOG.error(f"Error getting input settings: {e}")
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
            await broadcast_status_update("device_settings", {
                "type": "input",
                "number": input_num,
                **get_input_setting(input_num)
            })
            
            return _json_response(True, {
                "input": input_num,
                **get_input_setting(input_num),
                "message": f"Input {input_num} settings updated"
            })
        else:
            return _json_response(False, error="Failed to save settings", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid input number", status=400)
    except Exception as e:
        _LOG.error(f"Error setting input settings: {e}")
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
        _LOG.error(f"Error getting output settings: {e}")
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
            await broadcast_status_update("device_settings", {
                "type": "output",
                "number": output_num,
                **get_output_setting(output_num)
            })
            
            return _json_response(True, {
                "output": output_num,
                **get_output_setting(output_num),
                "message": f"Output {output_num} settings updated"
            })
        else:
            return _json_response(False, error="Failed to save settings", status=500)
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except ValueError:
        return _json_response(False, error="Invalid output number", status=400)
    except Exception as e:
        _LOG.error(f"Error setting output settings: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_bulk_update_settings(request: web.Request) -> web.Response:
    """POST /api/device-settings - Bulk update device settings."""
    try:
        data = await request.json()
        updated_inputs = []
        updated_outputs = []
        
        # Update inputs
        if "inputs" in data:
            for key, settings in data["inputs"].items():
                input_num = int(key)
                if 1 <= input_num <= 8:
                    set_input_setting(
                        input_num,
                        name=settings.get("name"),
                        icon=settings.get("icon"),
                        color=settings.get("color")
                    )
                    updated_inputs.append(input_num)
        
        # Update outputs
        if "outputs" in data:
            for key, settings in data["outputs"].items():
                output_num = int(key)
                if 1 <= output_num <= 8:
                    set_output_setting(
                        output_num,
                        name=settings.get("name"),
                        icon=settings.get("icon"),
                        color=settings.get("color")
                    )
                    updated_outputs.append(output_num)
        
        # Broadcast full settings update
        await broadcast_status_update("device_settings_full", get_device_settings())
        
        return _json_response(True, {
            "updated_inputs": updated_inputs,
            "updated_outputs": updated_outputs,
            "settings": get_device_settings()
        })
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.error(f"Error bulk updating settings: {e}")
        return _json_response(False, error=str(e), status=500)
