"""
Unit tests for system_shortcuts.py (unified SystemShortcuts).

Tests cover: SystemShortcut dataclass round-trip, SystemShortcutManager
CRUD/persistence, and the async execute_shortcut() function.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from system_shortcuts import SystemShortcut, SystemShortcutManager, execute_shortcut


class TestSystemShortcutDataclass:
    """Tests for SystemShortcut dataclass."""

    def test_roundtrip(self):
        """SystemShortcut round-trips through to_dict/from_dict."""
        original = SystemShortcut(
            key="test.shortcut",
            label="Test Shortcut",
            icon="⚡",
            enabled=True,
            order=5,
            category="routing",
        )
        recovered = SystemShortcut.from_dict(original.to_dict())
        assert recovered.key == original.key
        assert recovered.label == original.label
        assert recovered.icon == original.icon
        assert recovered.enabled == original.enabled
        assert recovered.order == original.order

    def test_from_dict_minimal(self):
        """from_dict with minimal fields uses defaults."""
        a = SystemShortcut.from_dict({"key": "k", "label": "K"})
        assert a.key == "k"
        assert a.icon == "⚡"  # default
        assert a.enabled is True  # default
        assert a.category == "routing"  # default


class TestSystemShortcutManager:
    """Tests for SystemShortcutManager."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def mgr(self, temp_dir):
        return SystemShortcutManager(data_dir=temp_dir)

    def test_list_shortcuts_returns_builtins(self, mgr):
        """list_shortcuts returns the built-in shortcut set."""
        shortcuts = mgr.list_shortcuts()
        assert len(shortcuts) > 0
        assert all(isinstance(a, SystemShortcut) for a in shortcuts)

    def test_list_shortcuts_sorted_by_order(self, mgr):
        """list_shortcuts returns shortcuts sorted by order."""
        shortcuts = mgr.list_shortcuts()
        orders = [a.order for a in shortcuts]
        assert orders == sorted(orders)

    def test_list_shortcuts_keys_unique(self, mgr):
        """Each shortcut key appears exactly once."""
        keys = [a.key for a in mgr.list_shortcuts()]
        assert len(keys) == len(set(keys))

    def test_get_shortcut_existing(self, mgr):
        """get returns the shortcut for known key."""
        shortcut = mgr.get("mute_all_audio")
        assert shortcut is not None
        assert shortcut.key == "mute_all_audio"

    def test_get_shortcut_unknown(self, mgr):
        """get returns None for unknown key."""
        assert mgr.get("nonexistent.key") is None

    def test_update_prefs(self, mgr):
        """update_prefs modifies label and persists."""
        ok = mgr.update_prefs("mute_all_audio", label="Custom Mute")
        assert ok is True
        shortcut = mgr.get("mute_all_audio")
        assert shortcut.label == "Custom Mute"

    def test_update_prefs_invalid_key(self, mgr):
        """update_prefs returns False for unknown key."""
        ok = mgr.update_prefs("invalid.key", label="Bad")
        assert ok is False

    def test_persistence(self, mgr, temp_dir):
        """Prefs persist across manager instantiation."""
        mgr.update_prefs("mute_all_audio", label="Persistent")
        mgr2 = SystemShortcutManager(data_dir=temp_dir)
        shortcut = mgr2.get("mute_all_audio")
        assert shortcut.label == "Persistent"


class TestExecuteShortcut:
    """Tests for the async execute_shortcut() function."""

    @pytest.fixture
    def mock_matrix(self):
        matrix = MagicMock()
        matrix.switch = AsyncMock(return_value=None)
        matrix.set_output_audio_mute = AsyncMock(return_value=None)
        matrix.recall_preset = AsyncMock(return_value=None)
        matrix.set_beep = AsyncMock(return_value=None)
        matrix.system_reboot = AsyncMock(return_value=None)
        matrix.power_off = AsyncMock(return_value=None)
        return matrix

    @pytest.mark.asyncio
    async def test_mute_all_audio(self, mock_matrix):
        """mute_all_audio calls set_output_audio_mute for all 8 outputs."""
        shortcut = SystemShortcut(key="mute_all_audio", label="Mute All", icon="🔇")
        result = await execute_shortcut(shortcut, mock_matrix)
        assert result["success"] is True
        assert mock_matrix.set_output_audio_mute.call_count == 8

    @pytest.mark.asyncio
    async def test_unmute_all_audio(self, mock_matrix):
        """unmute_all_audio calls set_output_audio_mute with False for all outputs."""
        shortcut = SystemShortcut(key="unmute_all_audio", label="Unmute All", icon="🔊")
        result = await execute_shortcut(shortcut, mock_matrix)
        assert result["success"] is True
        assert mock_matrix.set_output_audio_mute.call_count == 8

    @pytest.mark.asyncio
    async def test_route_one_to_one(self, mock_matrix):
        """route_one_to_one calls switch for all 8 outputs."""
        shortcut = SystemShortcut(key="route_one_to_one", label="1:1", icon="🔁")
        result = await execute_shortcut(shortcut, mock_matrix)
        assert result["success"] is True
        assert mock_matrix.switch.call_count == 8

    @pytest.mark.asyncio
    async def test_route_all_to_output(self, mock_matrix):
        """route_all_to_output routes input 1 to specified output."""
        shortcut = SystemShortcut(key="route_all_to_output", label="All → Out", icon="🎯")
        result = await execute_shortcut(shortcut, mock_matrix, {"output": 3})
        assert result["success"] is True
        mock_matrix.switch.assert_called_with(1, 3)

    @pytest.mark.asyncio
    async def test_preset_recall(self, mock_matrix):
        """preset_recall_N calls recall_preset with N."""
        shortcut = SystemShortcut(key="preset_recall_5", label="Preset 5", icon="5️⃣")
        result = await execute_shortcut(shortcut, mock_matrix)
        assert result["success"] is True
        mock_matrix.recall_preset.assert_called_with(5)

    @pytest.mark.asyncio
    async def test_unknown_shortcut_returns_failure(self, mock_matrix):
        """Unknown shortcut key returns failure."""
        shortcut = SystemShortcut(key="unknown.key", label="Unknown", icon="❓")
        result = await execute_shortcut(shortcut, mock_matrix)
        assert result["success"] is False
        assert "Unknown" in result["detail"]
