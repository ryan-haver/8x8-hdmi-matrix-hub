"""
Unit tests for system_shortcuts.py (unified SystemShortcuts).

Tests cover: SystemShortcut dataclass round-trip, SystemShortcutManager
CRUD/persistence, and the async execute_shortcut() function.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, create_autospec

import pytest

from orei_matrix import OreiMatrix
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




class TestLcdLabel:
    """API-07 (owner-approved rename): ``lcd_timeout_10s`` sets 15 s and is labelled so; the key stays."""

    @pytest.fixture
    def temp_dir(self, tmp_path):
        return tmp_path

    @pytest.fixture
    def mgr(self, temp_dir):
        return SystemShortcutManager(data_dir=temp_dir)

    def test_default_label(self, mgr):
        assert mgr.get("lcd_timeout_10s").label == "LCD: 15s"

    def test_stored_old_default_label_is_migrated(self, temp_dir):
        (temp_dir / "system_shortcuts.json").write_text(
            json.dumps({"lcd_timeout_10s": {"label": "LCD: 10s", "icon": "🖥️", "enabled": True, "order": 26}}),
            encoding="utf-8",
        )
        mgr = SystemShortcutManager(data_dir=temp_dir)
        assert mgr.get("lcd_timeout_10s").label == "LCD: 15s"
        saved = json.loads((temp_dir / "system_shortcuts.json").read_text(encoding="utf-8"))
        assert saved["lcd_timeout_10s"]["label"] == "LCD: 15s"

    def test_a_label_the_user_chose_is_kept(self, temp_dir):
        (temp_dir / "system_shortcuts.json").write_text(
            json.dumps({"lcd_timeout_10s": {"label": "Panel quick", "icon": "🖥️", "enabled": True, "order": 26}}),
            encoding="utf-8",
        )
        assert SystemShortcutManager(data_dir=temp_dir).get("lcd_timeout_10s").label == "Panel quick"

    def test_legacy_builtin_id_still_resolves(self, mgr):
        assert mgr.get("builtin.lcd_timeout_10s").key == "lcd_timeout_10s"


def make_matrix(result: bool = True):
    """An OreiMatrix double: only real methods exist (the old double had ``switch``, which OreiMatrix lacks)."""
    matrix = create_autospec(OreiMatrix, instance=True)
    for name in dir(OreiMatrix):
        attr = getattr(matrix, name, None)
        if isinstance(attr, AsyncMock):
            attr.return_value = result
    return matrix


def shortcut(key: str) -> SystemShortcut:
    return SystemShortcut(key=key, label=key, icon="⚡")


class TestExecuteShortcut:
    """Tests for the async execute_shortcut() function."""

    @pytest.fixture
    def mock_matrix(self):
        return make_matrix()

    async def test_mute_all_audio(self, mock_matrix):
        result = await execute_shortcut(shortcut("mute_all_audio"), mock_matrix)
        assert result["success"] is True
        assert [c.args for c in mock_matrix.set_output_audio_mute.await_args_list] == [(n, True) for n in range(1, 9)]

    async def test_unmute_all_audio(self, mock_matrix):
        result = await execute_shortcut(shortcut("unmute_all_audio"), mock_matrix)
        assert result["success"] is True
        assert [c.args for c in mock_matrix.set_output_audio_mute.await_args_list] == [(n, False) for n in range(1, 9)]

    async def test_route_one_to_one(self, mock_matrix):
        """API-01: switch_input, not the non-existent switch()."""
        result = await execute_shortcut(shortcut("route_one_to_one"), mock_matrix)
        assert result["success"] is True
        assert [c.args for c in mock_matrix.switch_input.await_args_list] == [(n, n) for n in range(1, 9)]

    async def test_route_all_to_output(self, mock_matrix):
        """route_all_to_output routes input (default 1) to the output."""
        result = await execute_shortcut(shortcut("route_all_to_output"), mock_matrix, {"output": 3})
        assert result["success"] is True
        mock_matrix.switch_input.assert_awaited_once_with(1, 3)

    async def test_power_off_all_powers_off_once(self, mock_matrix):
        """API-06: the matrix power-off used to be sent eight times."""
        result = await execute_shortcut(shortcut("power_off_all"), mock_matrix)
        assert result["success"] is True
        mock_matrix.power_off.assert_awaited_once_with()

    async def test_preset_recall(self, mock_matrix):
        result = await execute_shortcut(shortcut("preset_recall_5"), mock_matrix)
        assert result["success"] is True
        mock_matrix.recall_preset.assert_awaited_once_with(5)

    @pytest.mark.parametrize(
        ("key", "mode"),
        [("lcd_timeout_off", 0), ("lcd_timeout_always_on", 1), ("lcd_timeout_10s", 2), ("lcd_timeout_15s", 2),
         ("lcd_timeout_30s", 3), ("lcd_timeout_60s", 4)],
    )
    async def test_lcd_timeout_device_codes(self, mock_matrix, key, mode):
        """API-07: device codes 0 off, 1 always on, 2/3/4 = 15/30/60 s."""
        result = await execute_shortcut(shortcut(key), mock_matrix)
        assert result["success"] is True
        mock_matrix.set_lcd_timeout.assert_awaited_once_with(mode)

    async def test_lcd_10s_result_names_15s(self, mock_matrix):
        result = await execute_shortcut(shortcut("lcd_timeout_10s"), mock_matrix)
        assert "15s" in result["detail"]

    @pytest.mark.parametrize(
        "key",
        ["route_all_to_output", "route_one_to_one", "power_off_all", "mute_all_audio", "unmute_all_audio",
         "preset_recall_1", "beep_on", "beep_off", "panel_lock_on", "panel_lock_off", "system_reboot",
         "lcd_timeout_30s"],
    )
    async def test_a_refused_command_is_a_failure(self, key):
        """API-08: the matrix's False answers were ignored and every shortcut reported success."""
        result = await execute_shortcut(shortcut(key), make_matrix(result=False))
        assert result["success"] is False
        assert result["detail"].startswith("Failed")

    async def test_partly_refused_mute_names_the_outputs(self):
        matrix = make_matrix()
        matrix.set_output_audio_mute.side_effect = lambda n, m: n not in (3, 7)
        result = await execute_shortcut(shortcut("mute_all_audio"), matrix)
        assert result["success"] is False
        assert result["failed_outputs"] == [3, 7]
        assert matrix.set_output_audio_mute.await_count == 8

    async def test_an_exception_is_a_failure(self):
        matrix = make_matrix()
        matrix.recall_preset.side_effect = ConnectionError("gone")
        result = await execute_shortcut(shortcut("preset_recall_2"), matrix)
        assert result["success"] is False
        assert "gone" in result["detail"]

    async def test_unknown_shortcut_returns_failure(self, mock_matrix):
        result = await execute_shortcut(shortcut("unknown.key"), mock_matrix)
        assert result["success"] is False
        assert "Unknown" in result["detail"]
