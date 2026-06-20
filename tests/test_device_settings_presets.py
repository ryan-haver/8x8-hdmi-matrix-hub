"""
Tests for device settings preset favorite/dashboard endpoints (Phase 7).

Tests the REST API endpoints for hardware-preset surface-visibility
(favorite_presets and dashboard_presets lists).
"""

from pathlib import Path
import tempfile

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rest_api import create_rest_app, reset_rate_limiter, set_matrix_device
from rest_api.device_settings import (
    init_device_settings,
    get_favorite_presets,
    get_dashboard_presets,
    toggle_favorite_preset,
    toggle_dashboard_preset,
    set_favorite_presets,
    set_dashboard_presets,
    _coerce_preset_list,
)
from persistence import reset_data_dir_cache


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_data_dir():
    """Provide a temporary directory for device settings storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def app_with_device_settings(extended_mock_matrix, temp_data_dir):
    """Create REST app with mock matrix and initialized device settings."""
    reset_rate_limiter()
    # CRITICAL: reset_data_dir_cache() clears the process-level cache so
    # get_data_dir() re-resolves from the env var instead of returning a
    # stale cached path from a previous test.
    reset_data_dir_cache()
    # Set the env var so get_data_dir() resolves to our temp dir
    import os
    os.environ["MATRIX_DATA_DIR"] = str(temp_data_dir)
    # Reset the device settings module state and load from the fresh temp dir
    init_device_settings(temp_data_dir)
    set_matrix_device(extended_mock_matrix, {
        1: "Apple TV",
        2: "PS5",
        3: "Nintendo Switch",
        4: "PC",
        5: "Shield",
        6: "Cable Box",
        7: "Blu-ray",
        8: "Chromecast",
    }, data_dir=temp_data_dir)
    return create_rest_app(temp_data_dir)


@pytest.fixture
async def client_with_device_settings(aiohttp_client, app_with_device_settings):
    """Create test client for app with device settings initialized."""
    return await aiohttp_client(app_with_device_settings)


# Inherit the extended mock matrix fixture from test_rest_api.py
@pytest.fixture
def extended_mock_matrix(mock_matrix):
    """Add methods needed for Phase 7 REST API tests."""
    from unittest.mock import AsyncMock
    mock_matrix.switch = AsyncMock(return_value=True)
    mock_matrix.get_output_status = AsyncMock(return_value={
        "allsource": [1, 2, 3, 4, 5, 6, 7, 8],
        "allout": [1, 1, 1, 1, 1, 1, 1, 1],
        "allaudiomute": [0, 0, 0, 0, 0, 0, 0, 0],
        "allhdr": [3, 3, 3, 3, 3, 3, 3, 3],
        "allhdcp": [3, 3, 3, 3, 3, 3, 3, 3],
    })
    mock_matrix.set_audio_mute = AsyncMock(return_value=True)
    mock_matrix.set_hdr_mode = AsyncMock(return_value=True)
    mock_matrix.set_hdcp_mode = AsyncMock(return_value=True)
    return mock_matrix


# =============================================================================
# Unit tests for coerce / toggle helpers
# =============================================================================

class TestCoercePresetList:
    """Unit tests for _coerce_preset_list()."""

    def test_coerce_preset_list_valid(self):
        """Valid preset numbers 1-8 are kept."""
        assert _coerce_preset_list([1, 3, 5, 8]) == [1, 3, 5, 8]

    def test_coerce_preset_list_deduplicates(self):
        """Duplicates are removed."""
        assert _coerce_preset_list([1, 1, 2, 2, 3]) == [1, 2, 3]

    def test_coerce_preset_list_sorts(self):
        """Output is sorted."""
        assert _coerce_preset_list([5, 2, 8, 1]) == [1, 2, 5, 8]

    def test_coerce_preset_list_ignores_out_of_range(self):
        """Numbers outside 1-8 are dropped."""
        assert _coerce_preset_list([0, 1, 9, 8]) == [1, 8]
        assert _coerce_preset_list([-1, 10]) == []

    def test_coerce_preset_list_ignores_non_ints(self):
        """Non-integer values are skipped."""
        assert _coerce_preset_list([1, "two", None, 3]) == [1, 3]
        assert _coerce_preset_list(["a", "b"]) == []

    def test_coerce_preset_list_empty_input(self):
        """Empty list returns empty list."""
        assert _coerce_preset_list([]) == []
        assert _coerce_preset_list(None) == []
        assert _coerce_preset_list("not a list") == []


class TestToggleFavoritePreset:
    """Unit tests for toggle_favorite_preset()."""

    def test_toggle_adds_preset_when_not_favorite(self, temp_data_dir):
        """toggle_favorite_preset adds preset to favorites when not present."""
        init_device_settings(temp_data_dir)
        # Start with empty favorites
        set_favorite_presets([])
        result = toggle_favorite_preset(3)
        assert result is True
        assert get_favorite_presets() == [3]

    def test_toggle_removes_preset_when_already_favorite(self, temp_data_dir):
        """toggle_favorite_preset removes preset from favorites when already present."""
        init_device_settings(temp_data_dir)
        set_favorite_presets([3])
        result = toggle_favorite_preset(3)
        assert result is False
        assert get_favorite_presets() == []

    def test_toggle_invalid_preset_returns_false(self, temp_data_dir):
        """toggle_favorite_preset with out-of-range preset returns False."""
        init_device_settings(temp_data_dir)
        assert toggle_favorite_preset(0) is False
        assert toggle_favorite_preset(9) is False


class TestToggleDashboardPreset:
    """Unit tests for toggle_dashboard_preset()."""

    def test_toggle_adds_preset_when_not_on_dashboard(self, temp_data_dir):
        """toggle_dashboard_preset adds preset to dashboard when not present."""
        init_device_settings(temp_data_dir)
        set_dashboard_presets([])
        result = toggle_dashboard_preset(5)
        assert result is True
        assert get_dashboard_presets() == [5]

    def test_toggle_removes_preset_when_already_on_dashboard(self, temp_data_dir):
        """toggle_dashboard_preset removes preset from dashboard when already present."""
        init_device_settings(temp_data_dir)
        set_dashboard_presets([5])
        result = toggle_dashboard_preset(5)
        assert result is False
        assert get_dashboard_presets() == []


# =============================================================================
# REST API tests for preset favorites/dashboard
# =============================================================================

class TestFavoritePresetsAPI:
    """Tests for GET /api/device-settings/favorite-presets."""

    @pytest.mark.asyncio
    async def test_get_favorite_presets_empty(self, client_with_device_settings):
        """GET /api/device-settings/favorite-presets returns empty list initially."""
        resp = await client_with_device_settings.get("/api/device-settings/favorite-presets")
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["favorite_presets"] == []

    @pytest.mark.asyncio
    async def test_get_favorite_presets_after_toggle(self, client_with_device_settings):
        """After toggling preset 1 on, GET returns [1]."""
        # Toggle preset 1 on
        await client_with_device_settings.post("/api/device-settings/favorite-presets/1/toggle")
        resp = await client_with_device_settings.get("/api/device-settings/favorite-presets")
        data = await resp.json()
        assert data["data"]["favorite_presets"] == [1]


class TestDashboardPresetsAPI:
    """Tests for GET /api/device-settings/dashboard-presets."""

    @pytest.mark.asyncio
    async def test_get_dashboard_presets_empty(self, client_with_device_settings):
        """GET /api/device-settings/dashboard-presets returns empty list initially."""
        resp = await client_with_device_settings.get("/api/device-settings/dashboard-presets")
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["dashboard_presets"] == []


class TestToggleFavoritePresetAPI:
    """Tests for POST /api/device-settings/favorite-presets/{n}/toggle."""

    @pytest.mark.asyncio
    async def test_toggle_favorite_preset_adds(self, client_with_device_settings):
        """POST toggle adds preset to favorites."""
        resp = await client_with_device_settings.post(
            "/api/device-settings/favorite-presets/4/toggle"
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["preset"] == 4
        assert data["data"]["favorite"] is True
        assert 4 in data["data"]["favorite_presets"]

    @pytest.mark.asyncio
    async def test_toggle_favorite_preset_removes(self, client_with_device_settings):
        """POST toggle removes preset from favorites when already present."""
        # Add first
        await client_with_device_settings.post(
            "/api/device-settings/favorite-presets/4/toggle"
        )
        # Toggle again to remove
        resp = await client_with_device_settings.post(
            "/api/device-settings/favorite-presets/4/toggle"
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["data"]["favorite"] is False
        assert 4 not in data["data"]["favorite_presets"]

    @pytest.mark.asyncio
    async def test_toggle_favorite_preset_invalid_preset_0(self, client_with_device_settings):
        """POST with preset=0 returns 400."""
        resp = await client_with_device_settings.post(
            "/api/device-settings/favorite-presets/0/toggle"
        )
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_toggle_favorite_preset_invalid_preset_9(self, client_with_device_settings):
        """POST with preset=9 returns 400."""
        resp = await client_with_device_settings.post(
            "/api/device-settings/favorite-presets/9/toggle"
        )
        assert resp.status == 400

    @pytest.mark.asyncio
    async def test_toggle_favorite_twice_returns_to_original(self, client_with_device_settings):
        """Toggle twice returns to original state (empty)."""
        await client_with_device_settings.post(
            "/api/device-settings/favorite-presets/7/toggle"
        )
        await client_with_device_settings.post(
            "/api/device-settings/favorite-presets/7/toggle"
        )
        resp = await client_with_device_settings.get("/api/device-settings/favorite-presets")
        data = await resp.json()
        assert data["data"]["favorite_presets"] == []


class TestToggleDashboardPresetAPI:
    """Tests for POST /api/device-settings/dashboard-presets/{n}/toggle."""

    @pytest.mark.asyncio
    async def test_toggle_dashboard_preset_adds(self, client_with_device_settings):
        """POST toggle adds preset to dashboard."""
        resp = await client_with_device_settings.post(
            "/api/device-settings/dashboard-presets/2/toggle"
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["data"]["preset"] == 2
        assert data["data"]["dashboard_visible"] is True
        assert 2 in data["data"]["dashboard_presets"]

    @pytest.mark.asyncio
    async def test_toggle_dashboard_preset_removes(self, client_with_device_settings):
        """POST toggle removes preset from dashboard when already present."""
        await client_with_device_settings.post(
            "/api/device-settings/dashboard-presets/2/toggle"
        )
        resp = await client_with_device_settings.post(
            "/api/device-settings/dashboard-presets/2/toggle"
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["data"]["dashboard_visible"] is False

    @pytest.mark.asyncio
    async def test_toggle_dashboard_preset_invalid(self, client_with_device_settings):
        """POST with invalid preset returns 400."""
        resp = await client_with_device_settings.post(
            "/api/device-settings/dashboard-presets/0/toggle"
        )
        assert resp.status == 400
        resp = await client_with_device_settings.post(
            "/api/device-settings/dashboard-presets/9/toggle"
        )
        assert resp.status == 400


class TestSetFavoritePresetsAPI:
    """Tests for PUT /api/device-settings/favorite-presets."""

    @pytest.mark.asyncio
    async def test_put_favorite_presets_replaces_list(self, client_with_device_settings):
        """PUT replaces the favorites list with the provided preset numbers."""
        resp = await client_with_device_settings.put(
            "/api/device-settings/favorite-presets",
            json={"favorite_presets": [1, 3, 5]}
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["favorite_presets"] == [1, 3, 5]

    @pytest.mark.asyncio
    async def test_put_favorite_presets_invalid_presets_stripped(self, client_with_device_settings):
        """PUT with out-of-range presets silently drops them."""
        resp = await client_with_device_settings.put(
            "/api/device-settings/favorite-presets",
            json={"favorite_presets": [1, 9, 3, 0, 8]}
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["data"]["favorite_presets"] == [1, 3, 8]

    @pytest.mark.asyncio
    async def test_put_favorite_presets_deduplicates(self, client_with_device_settings):
        """PUT deduplicates preset numbers."""
        resp = await client_with_device_settings.put(
            "/api/device-settings/favorite-presets",
            json={"favorite_presets": [1, 1, 2, 2, 3]}
        )
        data = await resp.json()
        assert data["data"]["favorite_presets"] == [1, 2, 3]


class TestSetDashboardPresetsAPI:
    """Tests for PUT /api/device-settings/dashboard-presets."""

    @pytest.mark.asyncio
    async def test_put_dashboard_presets_replaces_list(self, client_with_device_settings):
        """PUT replaces the dashboard presets list."""
        resp = await client_with_device_settings.put(
            "/api/device-settings/dashboard-presets",
            json={"dashboard_presets": [2, 4]}
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert data["data"]["dashboard_presets"] == [2, 4]

    @pytest.mark.asyncio
    async def test_put_dashboard_presets_invalid_presets_stripped(self, client_with_device_settings):
        """PUT with out-of-range presets silently drops them."""
        resp = await client_with_device_settings.put(
            "/api/device-settings/dashboard-presets",
            json={"dashboard_presets": [2, 99, 4, 0]}
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["data"]["dashboard_presets"] == [2, 4]
