"""
Unit tests for system_actions.py (Phase 8).

Tests cover: SystemAction dataclass round-trip, SystemActionManager
CRUD/persistence, and the async execute_action() function.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from system_actions import SystemAction, SystemActionManager, execute_action


class TestSystemActionDataclass:
    """Tests for SystemAction dataclass."""

    def test_roundtrip(self):
        """SystemAction round-trips through to_dict/from_dict."""
        original = SystemAction(
            key="test.action",
            label="Test Action",
            icon="⚡",
            enabled=True,
            order=5,
            category="routing",
        )
        recovered = SystemAction.from_dict(original.to_dict())
        assert recovered.key == original.key
        assert recovered.label == original.label
        assert recovered.icon == original.icon
        assert recovered.enabled == original.enabled
        assert recovered.order == original.order

    def test_from_dict_minimal(self):
        """from_dict with minimal fields uses defaults."""
        a = SystemAction.from_dict({"key": "k", "label": "K"})
        assert a.key == "k"
        assert a.icon == "⚡"  # default
        assert a.enabled is True  # default
        assert a.category == "routing"  # default


class TestSystemActionManager:
    """Tests for SystemActionManager."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as d:
            yield Path(d)

    @pytest.fixture
    def mgr(self, temp_dir):
        return SystemActionManager(data_dir=temp_dir)

    def test_list_actions_returns_builtins(self, mgr):
        """list_actions returns the built-in action set."""
        actions = mgr.list_actions()
        assert len(actions) > 0
        assert all(isinstance(a, SystemAction) for a in actions)

    def test_list_actions_sorted_by_order(self, mgr):
        """list_actions returns actions sorted by order."""
        actions = mgr.list_actions()
        orders = [a.order for a in actions]
        assert orders == sorted(orders)

    def test_list_actions_keys_unique(self, mgr):
        """Each action key appears exactly once."""
        keys = [a.key for a in mgr.list_actions()]
        assert len(keys) == len(set(keys))

    def test_get_action_existing(self, mgr):
        """get_action returns the action for known key."""
        action = mgr.get_action("mute_all_audio")
        assert action is not None
        assert action.key == "mute_all_audio"

    def test_get_action_unknown(self, mgr):
        """get_action returns None for unknown key."""
        assert mgr.get_action("nonexistent.key") is None

    def test_update_prefs(self, mgr):
        """update_prefs modifies label and persists."""
        ok = mgr.update_prefs("mute_all_audio", label="Custom Mute")
        assert ok is True
        action = mgr.get_action("mute_all_audio")
        assert action.label == "Custom Mute"

    def test_update_prefs_invalid_key(self, mgr):
        """update_prefs returns False for unknown key."""
        ok = mgr.update_prefs("invalid.key", label="Bad")
        assert ok is False

    def test_persistence(self, mgr, temp_dir):
        """Prefs persist across manager instantiation."""
        mgr.update_prefs("mute_all_audio", label="Persistent")
        mgr2 = SystemActionManager(data_dir=temp_dir)
        action = mgr2.get_action("mute_all_audio")
        assert action.label == "Persistent"


class TestExecuteAction:
    """Tests for the async execute_action() function."""

    @pytest.fixture
    def mock_matrix(self):
        matrix = MagicMock()
        matrix.switch = AsyncMock(returnValue=None)
        matrix.set_output_audio_mute = AsyncMock(returnValue=None)
        matrix.recall_preset = AsyncMock(returnValue=None)
        matrix.set_beep = AsyncMock(returnValue=None)
        matrix.system_reboot = AsyncMock(returnValue=None)
        matrix.power_off = AsyncMock(returnValue=None)
        return matrix

    @pytest.mark.asyncio
    async def test_mute_all_audio(self, mock_matrix):
        """mute_all_audio calls set_output_audio_mute for all 8 outputs."""
        action = SystemAction(key="mute_all_audio", label="Mute All", icon="🔇")
        result = await execute_action(action, mock_matrix)
        assert result["success"] is True
        assert mock_matrix.set_output_audio_mute.call_count == 8

    @pytest.mark.asyncio
    async def test_unmute_all_audio(self, mock_matrix):
        """unmute_all_audio calls set_output_audio_mute with False for all outputs."""
        action = SystemAction(key="unmute_all_audio", label="Unmute All", icon="🔊")
        result = await execute_action(action, mock_matrix)
        assert result["success"] is True
        assert mock_matrix.set_output_audio_mute.call_count == 8

    @pytest.mark.asyncio
    async def test_route_one_to_one(self, mock_matrix):
        """route_one_to_one calls switch for all 8 outputs."""
        action = SystemAction(key="route_one_to_one", label="1:1", icon="🔁")
        result = await execute_action(action, mock_matrix)
        assert result["success"] is True
        assert mock_matrix.switch.call_count == 8

    @pytest.mark.asyncio
    async def test_route_all_to_output(self, mock_matrix):
        """route_all_to_output routes input 1 to specified output."""
        action = SystemAction(key="route_all_to_output", label="All → Out", icon="🎯")
        result = await execute_action(action, mock_matrix, {"output": 3})
        assert result["success"] is True
        mock_matrix.switch.assert_called_with(1, 3)

    @pytest.mark.asyncio
    async def test_preset_recall(self, mock_matrix):
        """preset_recall_N calls recall_preset with N."""
        action = SystemAction(key="preset_recall_5", label="Preset 5", icon="5️⃣")
        result = await execute_action(action, mock_matrix)
        assert result["success"] is True
        mock_matrix.recall_preset.assert_called_with(5)

    @pytest.mark.asyncio
    async def test_unknown_action_returns_failure(self, mock_matrix):
        """Unknown action key returns failure."""
        action = SystemAction(key="unknown.key", label="Unknown", icon="❓")
        result = await execute_action(action, mock_matrix)
        assert result["success"] is False
        assert "Unknown" in result["detail"]