"""
Unit tests for SystemShortcutManager and SystemShortcut dataclass (Phase 7).

Tests cover: round-trip serialization, validation, CRUD operations,
filtering, reordering, and execute_shortcut() against a mock matrix.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from system_shortcuts import (
    SystemShortcut,
    SystemShortcutManager,
    VALID_TYPES,
    TYPE_ROUTE_ALL_TO_OUTPUT,
    TYPE_ROUTE_ONE_TO_ONE,
    TYPE_POWER_OFF_ALL,
    TYPE_MUTE_ALL_AUDIO,
    TYPE_UNMUTE_ALL_AUDIO,
    execute_shortcut,
)


class TestSystemShortcutDataclass:
    """Tests for SystemShortcut.from_dict / to_dict round-trip and validation."""

    def test_roundtrip_valid(self):
        """A shortcut serializes and deserializes back to identical values."""
        original = SystemShortcut(
            id="test.id",
            name="Test Shortcut",
            icon="⚡",
            type=TYPE_ROUTE_ALL_TO_OUTPUT,
            params={"output": 2},
            enabled=True,
            builtin=False,
            favorite=True,
            dashboard_visible=False,
            order=5,
        )
        recovered = SystemShortcut.from_dict(original.to_dict())
        assert recovered.id == original.id
        assert recovered.name == original.name
        assert recovered.icon == original.icon
        assert recovered.type == original.type
        assert recovered.params == original.params
        assert recovered.enabled == original.enabled
        assert recovered.builtin == original.builtin
        assert recovered.favorite == original.favorite
        assert recovered.dashboard_visible == original.dashboard_visible
        assert recovered.order == original.order

    def test_from_dict_unknown_type_raises(self):
        """from_dict raises ValueError for an unknown shortcut type."""
        with pytest.raises(ValueError, match="Unknown shortcut type"):
            SystemShortcut.from_dict({
                "id": "bad",
                "name": "Bad",
                "type": "not_a_real_type",
            })

    def test_from_dict_missing_type_raises(self):
        """from_dict raises ValueError when type is absent."""
        with pytest.raises(ValueError, match="Unknown shortcut type"):
            SystemShortcut.from_dict({
                "id": "no_type",
                "name": "No Type",
            })

    def test_from_dict_missing_id_defaults_empty(self):
        """from_dict accepts a dict without id and fills in empty string."""
        sc = SystemShortcut.from_dict({
            "name": "No ID",
            "type": TYPE_POWER_OFF_ALL,
        })
        assert sc.id == ""

    def test_builtin_defaults_all_types_valid(self):
        """Every builtin type in VALID_TYPES is actually a valid type constant."""
        for t in VALID_TYPES:
            assert t in {
                TYPE_ROUTE_ALL_TO_OUTPUT,
                TYPE_ROUTE_ONE_TO_ONE,
                TYPE_POWER_OFF_ALL,
                TYPE_MUTE_ALL_AUDIO,
                TYPE_UNMUTE_ALL_AUDIO,
            }


class TestSystemShortcutManagerInit:
    """Tests for SystemShortcutManager initialization and seeding."""

    def test_seeds_five_defaults_on_first_load(self):
        """Manager seeds exactly the 5 built-in shortcuts when file is absent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            shortcuts = mgr.list_shortcuts()
            assert len(shortcuts) == 5

    def test_default_ids_are_builtin(self):
        """All 5 seeded shortcuts have builtin=True and IDs starting with 'builtin.'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            shortcuts = mgr.list_shortcuts()
            assert all(s.builtin for s in shortcuts)
            assert all(s.id.startswith("builtin.") for s in shortcuts)

    def test_default_shortcut_types_present(self):
        """The 5 default shortcuts cover all 5 VALID_TYPES."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            types = {s.type for s in mgr.list_shortcuts()}
            assert types == VALID_TYPES


class TestSystemShortcutManagerQueries:
    """Tests for list_shortcuts, list_favorites, list_dashboard, and get."""

    def test_list_shortcuts_returns_all_sorted_by_order(self):
        """list_shortcuts returns every shortcut, sorted by order then name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            shortcuts = mgr.list_shortcuts()
            assert len(shortcuts) == 5
            # Should be sorted by order (builtin defaults have orders 0-4)
            orders = [s.order for s in shortcuts]
            assert orders == sorted(orders)

    def test_list_shortcuts_enabled_only(self):
        """enabled_only=True filters out disabled shortcuts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            # Disable the first shortcut
            mgr.set_enabled("builtin.all_to_out_1", False)
            enabled = mgr.list_shortcuts(enabled_only=True)
            ids = [s.id for s in enabled]
            assert "builtin.all_to_out_1" not in ids
            assert len(enabled) == 4

    def test_list_shortcuts_include_builtin_false(self):
        """include_builtin=False excludes all built-in shortcuts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            user_only = mgr.list_shortcuts(include_builtin=False)
            assert all(not s.builtin for s in user_only)

    def test_list_favorites_returns_enabled_favorite_sorted(self):
        """list_favorites returns only enabled+favorite shortcuts, sorted by order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            favs = mgr.list_favorites()
            # builtin.all_to_out_1 and builtin.one_to_one are favorite=True by default
            assert len(favs) == 2
            assert all(s.favorite for s in favs)
            assert all(s.enabled for s in favs)

    def test_list_dashboard_returns_enabled_dashboard_visible_sorted(self):
        """list_dashboard returns only enabled+dashboard_visible shortcuts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            # None of the defaults have dashboard_visible=True
            dash = mgr.list_dashboard()
            assert len(dash) == 0

    def test_get_returns_shortcut(self):
        """get(id) returns the correct shortcut."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            sc = mgr.get("builtin.all_to_out_1")
            assert sc is not None
            assert sc.id == "builtin.all_to_out_1"
            assert sc.type == TYPE_ROUTE_ALL_TO_OUTPUT

    def test_get_returns_none_for_invalid_id(self):
        """get(invalid_id) returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            assert mgr.get("nonexistent.id") is None


class TestSystemShortcutManagerMutations:
    """Tests for rename, set_enabled, toggle_favorite, toggle_dashboard_visible."""

    def test_rename_updates_name_and_persists(self):
        """rename(id, name) updates the name and saves to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            result = mgr.rename("builtin.all_to_out_1", "New Name")
            assert result is True
            assert mgr.get("builtin.all_to_out_1").name == "New Name"
            # Verify persistence: create new manager and check
            mgr2 = SystemShortcutManager(Path(tmpdir))
            assert mgr2.get("builtin.all_to_out_1").name == "New Name"

    def test_rename_invalid_id_returns_false(self):
        """rename(invalid_id, name) returns False and does not persist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            result = mgr.rename("nonexistent", "Should Not Work")
            assert result is False
            # Confirm no change persisted
            mgr2 = SystemShortcutManager(Path(tmpdir))
            assert mgr2.get("builtin.all_to_out_1").name == "All → Out 1"

    def test_rename_empty_name_returns_false(self):
        """rename with blank name returns False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            assert mgr.rename("builtin.all_to_out_1", "   ") is False

    def test_set_enabled_false_disables_and_persists(self):
        """set_enabled(id, False) disables the shortcut and persists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            result = mgr.set_enabled("builtin.mute_all_audio", False)
            assert result is True
            assert mgr.get("builtin.mute_all_audio").enabled is False
            mgr2 = SystemShortcutManager(Path(tmpdir))
            assert mgr2.get("builtin.mute_all_audio").enabled is False

    def test_toggle_favorite_flips_and_returns_new_state(self):
        """toggle_favorite flips the flag, returns the new boolean state, persists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            # builtin.power_off_all is favorite=False by default
            new_state = mgr.toggle_favorite("builtin.power_off_all")
            assert new_state is True
            assert mgr.get("builtin.power_off_all").favorite is True
            # Toggle back
            new_state = mgr.toggle_favorite("builtin.power_off_all")
            assert new_state is False
            # Persists
            mgr2 = SystemShortcutManager(Path(tmpdir))
            assert mgr2.get("builtin.power_off_all").favorite is False

    def test_toggle_favorite_invalid_id_returns_false(self):
        """toggle_favorite with invalid id returns False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            assert mgr.toggle_favorite("bad.id") is False

    def test_toggle_dashboard_visible_flips_and_returns_new_state(self):
        """toggle_dashboard_visible flips the flag, returns new state, persists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            # builtin.all_to_out_1 has dashboard_visible=False by default
            new_state = mgr.toggle_dashboard_visible("builtin.all_to_out_1")
            assert new_state is True
            assert mgr.get("builtin.all_to_out_1").dashboard_visible is True
            # Persists
            mgr2 = SystemShortcutManager(Path(tmpdir))
            assert mgr2.get("builtin.all_to_out_1").dashboard_visible is True


class TestSystemShortcutManagerReorder:
    """Tests for reorder operation."""

    def test_reorder_updates_order_values(self):
        """reorder([id3, id1, id2]) assigns order 0,1,2 to those ids in that sequence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            shortcuts = mgr.list_shortcuts()
            ids = [s.id for s in shortcuts]  # default order
            # Reverse the list
            reversed_ids = list(reversed(ids))
            mgr.reorder(reversed_ids)
            # Verify new order
            reordered = mgr.list_shortcuts()
            assert [s.id for s in reordered] == reversed_ids

    def test_reorder_unknown_ids_appended_at_end(self):
        """reorder with unknown ids appends them at the end without error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            shortcuts = mgr.list_shortcuts()
            valid_ids = [s.id for s in shortcuts[:3]]
            # Add some invalid ids to the reorder list
            result = mgr.reorder(valid_ids + ["invalid1", "invalid2"])
            assert result is True


class TestSystemShortcutManagerUserShortcuts:
    """Tests for add_user_shortcut and delete."""

    def test_add_user_shortcut_creates_non_builtin_with_uuid_id(self):
        """add_user_shortcut creates a shortcut with builtin=False and id starting with 'user.'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            sc = mgr.add_user_shortcut(
                name="My Shortcut",
                icon="🎬",
                type=TYPE_ROUTE_ONE_TO_ONE,
            )
            assert sc is not None
            assert sc.builtin is False
            assert sc.id.startswith("user.")
            assert sc.name == "My Shortcut"

    def test_add_user_shortcut_invalid_type_returns_none(self):
        """add_user_shortcut with unknown type returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            sc = mgr.add_user_shortcut(
                name="Bad Type",
                icon="⚡",
                type="not_a_valid_type",
            )
            assert sc is None

    def test_add_user_shortcut_empty_name_returns_none(self):
        """add_user_shortcut with blank name returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            sc = mgr.add_user_shortcut(
                name="",
                icon="⚡",
                type=TYPE_MUTE_ALL_AUDIO,
            )
            assert sc is None

    def test_delete_builtin_returns_false(self):
        """delete(builtin_id) returns False — built-ins cannot be deleted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            result = mgr.delete("builtin.all_to_out_1")
            assert result is False
            # Verify still present
            assert mgr.get("builtin.all_to_out_1") is not None

    def test_delete_user_removes_and_returns_true(self):
        """delete(user_id) removes the shortcut and returns True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            sc = mgr.add_user_shortcut(
                name="To Delete",
                icon="⚡",
                type=TYPE_POWER_OFF_ALL,
            )
            assert sc is not None
            user_id = sc.id
            result = mgr.delete(user_id)
            assert result is True
            assert mgr.get(user_id) is None
            # Persists
            mgr2 = SystemShortcutManager(Path(tmpdir))
            assert mgr2.get(user_id) is None

    def test_delete_invalid_id_returns_false(self):
        """delete(nonexistent) returns False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = SystemShortcutManager(Path(tmpdir))
            assert mgr.delete("totally.fake.id") is False


class TestExecuteShortcut:
    """Tests for execute_shortcut() against a mock matrix device."""

    @pytest.fixture
    def mock_matrix(self):
        """Create a mock matrix with the methods execute_shortcut needs."""
        m = MagicMock()
        m.switch = AsyncMock(return_value=True)
        m.set_power = AsyncMock(return_value=True)
        m.set_audio_mute = AsyncMock(return_value=True)
        return m

    def test_execute_route_all_to_output_returns_success(self, mock_matrix):
        """route_all_to_output shortcut returns success without calling switch."""
        sc = SystemShortcut(
            id="test",
            name="Test",
            icon="⚡",
            type=TYPE_ROUTE_ALL_TO_OUTPUT,
            params={"output": 1},
        )
        result = execute_shortcut(sc, mock_matrix)
        assert result["success"] is True
        assert result["type"] == TYPE_ROUTE_ALL_TO_OUTPUT

    def test_execute_route_one_to_one_calls_switch_for_all_8(self, mock_matrix):
        """route_one_to_one calls matrix.switch(n, n) for all 8 outputs."""
        sc = SystemShortcut(
            id="test",
            name="Test",
            icon="🔁",
            type=TYPE_ROUTE_ONE_TO_ONE,
        )
        result = execute_shortcut(sc, mock_matrix)
        assert result["success"] is True
        assert mock_matrix.switch.call_count == 8
        for n in range(1, 9):
            mock_matrix.switch.assert_any_call(n, n)

    def test_execute_power_off_all_calls_set_power_false(self, mock_matrix):
        """power_off_all calls matrix.set_power(n, False) for all 8 outputs."""
        sc = SystemShortcut(
            id="test",
            name="Test",
            icon="⏻",
            type=TYPE_POWER_OFF_ALL,
        )
        result = execute_shortcut(sc, mock_matrix)
        assert result["success"] is True
        assert mock_matrix.set_power.call_count == 8
        for n in range(1, 9):
            mock_matrix.set_power.assert_any_call(n, False)

    def test_execute_mute_all_audio_calls_set_audio_mute_true(self, mock_matrix):
        """mute_all_audio calls matrix.set_audio_mute(n, True) for all 8 outputs."""
        sc = SystemShortcut(
            id="test",
            name="Test",
            icon="🔇",
            type=TYPE_MUTE_ALL_AUDIO,
        )
        result = execute_shortcut(sc, mock_matrix)
        assert result["success"] is True
        assert mock_matrix.set_audio_mute.call_count == 8
        for n in range(1, 9):
            mock_matrix.set_audio_mute.assert_any_call(n, True)

    def test_execute_unmute_all_audio_calls_set_audio_mute_false(self, mock_matrix):
        """unmute_all_audio calls matrix.set_audio_mute(n, False) for all 8 outputs."""
        sc = SystemShortcut(
            id="test",
            name="Test",
            icon="🔊",
            type=TYPE_UNMUTE_ALL_AUDIO,
        )
        result = execute_shortcut(sc, mock_matrix)
        assert result["success"] is True
        assert mock_matrix.set_audio_mute.call_count == 8
        for n in range(1, 9):
            mock_matrix.set_audio_mute.assert_any_call(n, False)

    def test_execute_unknown_type_returns_failure(self, mock_matrix):
        """A shortcut with an unrecognized type returns success=False."""
        sc = SystemShortcut(
            id="test",
            name="Test",
            icon="❓",
            type="not_a_real_type",
        )
        result = execute_shortcut(sc, mock_matrix)
        assert result["success"] is False
        assert "Unknown shortcut type" in result["detail"]
