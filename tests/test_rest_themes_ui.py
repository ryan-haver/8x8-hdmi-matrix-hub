"""
Tests for themes.py and ui.py REST modules.

Tests the theme preferences and UI preferences handlers.
These are NOT covered by test_rest_api.py, so they get focused tests here.
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# =============================================================================
# Test themes.py handlers
# =============================================================================


class TestThemesHandlers:
    """Test theme preferences handlers."""

    @pytest.mark.asyncio
    async def test_get_themes_returns_valid_structure(self):
        """handle_get_themes should return theme preferences with valid structure."""
        from rest_api.themes import handle_get_themes

        request = MagicMock()
        response = await handle_get_themes(request)
        body = json.loads(response.body)

        assert body["success"] is True
        # The data has: presets (array of 4), activePresetIndex, cardOpacity, hoverPreference
        assert "presets" in body["data"]
        assert len(body["data"]["presets"]) == 4
        assert "activePresetIndex" in body["data"]
        assert "cardOpacity" in body["data"]
        assert "hoverPreference" in body["data"]

    @pytest.mark.asyncio
    async def test_get_themes_default_presets_have_valid_structure(self):
        """Default presets should have id, name, primaryH, secondaryH fields."""
        from rest_api.themes import handle_get_themes

        request = MagicMock()
        response = await handle_get_themes(request)
        body = json.loads(response.body)

        for preset in body["data"]["presets"]:
            assert "id" in preset
            assert "name" in preset
            assert "primaryH" in preset
            assert "secondaryH" in preset
            # Hue should be 0-360
            assert 0 <= preset["primaryH"] <= 360
            assert 0 <= preset["secondaryH"] <= 360

    @pytest.mark.asyncio
    async def test_put_themes_accepts_valid_data(self):
        """handle_put_themes should accept valid 4-preset array."""
        from rest_api.themes import handle_put_themes

        new_theme = {
            "presets": [
                {"id": "preset-1", "name": "Custom 1", "primaryH": 187, "secondaryH": 25},
                {"id": "preset-2", "name": "Custom 2", "primaryH": 300, "secondaryH": 80},
                {"id": "preset-3", "name": "Custom 3", "primaryH": 280, "secondaryH": 45},
                {"id": "preset-4", "name": "Custom 4", "primaryH": 170, "secondaryH": 330},
            ],
            "activePresetIndex": 1,
            "cardOpacity": 0.9,
            "hoverPreference": "secondary",
        }
        request = MagicMock()
        request.json = AsyncMock(return_value=new_theme)

        response = await handle_put_themes(request)
        body = json.loads(response.body)

        assert body["success"] is True
        assert body["data"]["activePresetIndex"] == 1
        assert body["data"]["hoverPreference"] == "secondary"

    @pytest.mark.asyncio
    async def test_put_themes_rejects_wrong_preset_count(self):
        """handle_put_themes should reject presets array of wrong length."""
        from rest_api.themes import handle_put_themes

        bad_theme = {
            "presets": [{"id": "p1", "name": "Only", "primaryH": 0, "secondaryH": 0}],  # Only 1
        }
        request = MagicMock()
        request.json = AsyncMock(return_value=bad_theme)

        response = await handle_put_themes(request)
        body = json.loads(response.body)

        assert body["success"] is False
        assert response.status == 400

    @pytest.mark.asyncio
    async def test_reset_themes_returns_defaults(self):
        """handle_reset_themes should return to default theme settings."""
        from rest_api.themes import handle_reset_themes

        request = MagicMock()
        response = await handle_reset_themes(request)
        body = json.loads(response.body)

        assert body["success"] is True
        assert len(body["data"]["presets"]) == 4


# =============================================================================
# Test ui.py handlers
# =============================================================================


class TestUiPreferencesHandlers:
    """Test UI preferences handlers."""

    @pytest.mark.asyncio
    async def test_get_ui_preferences_returns_defaults(self):
        """handle_get_ui_preferences should return tab preferences."""
        from rest_api.ui import handle_get_ui_preferences

        request = MagicMock()
        response = await handle_get_ui_preferences(request)
        body = json.loads(response.body)

        assert body["success"] is True
        assert "pinnedTabs" in body["data"]
        assert "tabOrder" in body["data"]
        # tabOrder should always include all available tabs
        assert len(body["data"]["tabOrder"]) >= 1
        # Each pinned tab should also be in tabOrder
        for tab in body["data"]["pinnedTabs"]:
            assert tab in body["data"]["tabOrder"]

    @pytest.mark.asyncio
    async def test_ui_preferences_includes_matrix_tab(self):
        """UI preferences should always include the 'matrix' tab (core feature)."""
        from rest_api.ui import handle_get_ui_preferences

        request = MagicMock()
        response = await handle_get_ui_preferences(request)
        body = json.loads(response.body)

        # The matrix tab is the primary feature, should always be present
        assert "matrix" in body["data"]["pinnedTabs"]
        assert "matrix" in body["data"]["tabOrder"]

    @pytest.mark.asyncio
    async def test_set_ui_preferences_updates_tabs(self):
        """handle_set_ui_preferences should update and return new preferences."""
        from rest_api.ui import handle_set_ui_preferences

        new_prefs = {
            "pinnedTabs": ["matrix", "dashboard", "outputs"],
            "tabOrder": ["matrix", "outputs", "dashboard", "inputs", "profiles"],
        }
        request = MagicMock()
        request.json = AsyncMock(return_value=new_prefs)

        response = await handle_set_ui_preferences(request)
        body = json.loads(response.body)

        assert body["success"] is True
        assert body["data"]["pinnedTabs"] == new_prefs["pinnedTabs"]
        assert body["data"]["tabOrder"] == new_prefs["tabOrder"]
