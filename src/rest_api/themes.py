"""
Theme endpoints for UI theme management.
Stores user theme preferences persistently on the backend.
"""

import json
import logging
import os
from pathlib import Path
from aiohttp import web

from .utils import _json_response

_LOG = logging.getLogger("rest_api.themes")

# Theme storage file location
THEME_STORAGE_FILE = Path(__file__).parent.parent.parent / "data" / "themes.json"

# Default theme presets
DEFAULT_THEMES = {
    "presets": [
        {"id": "preset-1", "name": "Tron Classic", "primaryH": 187, "secondaryH": 25},
        {"id": "preset-2", "name": "Neon", "primaryH": 300, "secondaryH": 80},
        {"id": "preset-3", "name": "Royal", "primaryH": 280, "secondaryH": 45},
        {"id": "preset-4", "name": "Vaporwave", "primaryH": 170, "secondaryH": 330}
    ],
    "activePresetIndex": 0,
    "cardOpacity": 0.8,
    "hoverPreference": "primary"
}


def _ensure_data_dir():
    """Ensure the data directory exists."""
    THEME_STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load_themes() -> dict:
    """Load theme settings from file, or return defaults."""
    try:
        if THEME_STORAGE_FILE.exists():
            with open(THEME_STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        _LOG.warning(f"Failed to load themes: {e}")
    
    return DEFAULT_THEMES.copy()


def _save_themes(data: dict) -> bool:
    """Save theme settings to file."""
    try:
        _ensure_data_dir()
        with open(THEME_STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        _LOG.error(f"Failed to save themes: {e}")
        return False


async def handle_get_themes(request: web.Request) -> web.Response:
    """Get current theme settings."""
    themes = _load_themes()
    return _json_response(True, themes)


async def handle_put_themes(request: web.Request) -> web.Response:
    """Update theme settings."""
    try:
        body = await request.json()
        
        # Validate required fields
        if "presets" not in body:
            return _json_response(False, error="Missing 'presets' field", status=400)
        
        # Validate presets array
        presets = body.get("presets", [])
        if not isinstance(presets, list) or len(presets) != 4:
            return _json_response(False, error="Presets must be an array of 4 items", status=400)
        
        # Validate each preset
        for i, preset in enumerate(presets):
            if not isinstance(preset.get("primaryH"), (int, float)):
                return _json_response(False, error=f"Preset {i} missing valid primaryH", status=400)
            if not isinstance(preset.get("secondaryH"), (int, float)):
                return _json_response(False, error=f"Preset {i} missing valid secondaryH", status=400)
            if not preset.get("name"):
                preset["name"] = f"Preset {i + 1}"
            if not preset.get("id"):
                preset["id"] = f"preset-{i + 1}"
        
        # Build clean data object
        theme_data = {
            "presets": presets,
            "activePresetIndex": int(body.get("activePresetIndex", 0)) % 4,
            "cardOpacity": max(0, min(1, float(body.get("cardOpacity", 0.8)))),
            "hoverPreference": body.get("hoverPreference", "primary") if body.get("hoverPreference") in ["primary", "secondary"] else "primary"
        }
        
        if _save_themes(theme_data):
            _LOG.info("Theme settings saved successfully")
            return _json_response(True, theme_data)
        else:
            return _json_response(False, error="Failed to save theme settings", status=500)
            
    except json.JSONDecodeError:
        return _json_response(False, error="Invalid JSON body", status=400)
    except Exception as e:
        _LOG.error(f"Error updating themes: {e}")
        return _json_response(False, error=str(e), status=500)


async def handle_reset_themes(request: web.Request) -> web.Response:
    """Reset theme settings to defaults."""
    if _save_themes(DEFAULT_THEMES.copy()):
        _LOG.info("Theme settings reset to defaults")
        return _json_response(True, DEFAULT_THEMES)
    else:
        return _json_response(False, error="Failed to reset theme settings", status=500)
