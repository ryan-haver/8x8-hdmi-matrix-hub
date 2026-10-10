"""
Unit tests for DashboardLayoutManager, DashboardLayout, and DashboardCard (Phase 7).

Tests cover: round-trip serialization, validation, card CRUD,
deduplication, and order compaction.
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dashboard_layout import (
    CARD_AGGREGATE_WIDGET,
    CARD_PRESET,
    CARD_PROFILE,
    DashboardCard,
    DashboardLayout,
    DashboardLayoutManager,
)


class TestDashboardCardDataclass:
    """Tests for DashboardCard.from_dict / to_dict round-trip and validation."""

    def test_roundtrip_valid(self):
        """A card serializes and deserializes back to identical values."""
        original = DashboardCard(type=CARD_PROFILE, id="my_profile", order=3)
        recovered = DashboardCard.from_dict(original.to_dict())
        assert recovered.type == original.type
        assert recovered.id == original.id
        assert recovered.order == original.order

    def test_from_dict_unknown_type_raises(self):
        """from_dict raises ValueError for an unknown card type."""
        with pytest.raises(ValueError, match="Unknown card type"):
            DashboardCard.from_dict({"type": "not_a_card", "id": "x"})

    def test_from_dict_empty_id_raises(self):
        """from_dict raises ValueError for empty or missing id."""
        with pytest.raises(ValueError, match="non-empty string"):
            DashboardCard.from_dict({"type": CARD_PROFILE, "id": ""})

    def test_from_dict_missing_id_raises(self):
        """from_dict raises ValueError when id is absent."""
        with pytest.raises(ValueError, match="non-empty string"):
            DashboardCard.from_dict({"type": CARD_PROFILE})

    def test_key_returns_type_id_tuple(self):
        """key() returns a stable (type, id) tuple for dedup/lookup."""
        card = DashboardCard(type=CARD_PROFILE, id="my_profile")
        assert card.key() == (CARD_PROFILE, "my_profile")


class TestDashboardLayoutDataclass:
    """Tests for DashboardLayout.from_dict / to_dict round-trip."""

    def test_roundtrip_valid(self):
        """A layout serializes and deserializes back to identical values."""
        original = DashboardLayout(
            cards=[
                DashboardCard(type=CARD_PROFILE, id="p1", order=0),
                DashboardCard(type=CARD_PRESET, id="2", order=1),
            ],
            version=1,
        )
        recovered = DashboardLayout.from_dict(original.to_dict())
        assert len(recovered.cards) == 2
        assert recovered.version == 1
        assert recovered.cards[0].type == CARD_PROFILE
        assert recovered.cards[0].id == "p1"
        assert recovered.cards[1].type == CARD_PRESET
        assert recovered.cards[1].id == "2"

    def test_from_dict_skips_invalid_cards_with_warning(self):
        """from_dict silently skips card entries that fail validation."""
        raw = {
            "version": 1,
            "cards": [
                {"type": CARD_PROFILE, "id": "valid", "order": 0},
                {"type": "bad_type", "id": "invalid", "order": 1},
                {"type": CARD_PRESET, "id": "1", "order": 2},
            ],
        }
        layout = DashboardLayout.from_dict(raw)
        assert len(layout.cards) == 2
        assert layout.cards[0].id == "valid"
        assert layout.cards[1].id == "1"

    def test_from_dict_sorts_by_order(self):
        """from_dict sorts cards by order field after loading."""
        raw = {
            "version": 1,
            "cards": [
                {"type": CARD_PROFILE, "id": "third", "order": 2},
                {"type": CARD_PROFILE, "id": "first", "order": 0},
                {"type": CARD_PROFILE, "id": "second", "order": 1},
            ],
        }
        layout = DashboardLayout.from_dict(raw)
        ids = [c.id for c in layout.cards]
        assert ids == ["first", "second", "third"]


class TestDashboardLayoutManagerInit:
    """Tests for DashboardLayoutManager initialization and seeding."""

    def test_first_load_seeds_an_empty_layout(self):
        """UI-55/UI-57: a new install starts with no cards (no widget cards)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = DashboardLayoutManager(Path(tmpdir))
            assert mgr.list_cards() == []
            assert json.loads((Path(tmpdir) / "dashboard_layout.json").read_text(encoding="utf-8")) == {
                "version": 1,
                "cards": [],
            }


def _write_layout(data_dir: Path, cards: list[dict]) -> Path:
    path = data_dir / "dashboard_layout.json"
    path.write_text(json.dumps({"version": 1, "cards": cards}), encoding="utf-8")
    return path


# The layout every install seeded before UI-55/UI-57, with a user's profile card after it
_LEGACY_SEEDED = [
    {"type": "aggregate_widget", "id": "cec-tray", "order": 0},
    {"type": "aggregate_widget", "id": "routing-dashboard", "order": 1},
    {"type": "aggregate_widget", "id": "quick-actions", "order": 2},
    {"type": "profile", "id": "movie_night", "order": 3},
]


class TestRetiredWidgetCards:
    """UI-55/UI-57 (owner decision 2026-10-09): widgets live only as pinned widgets.

    The dashboard layout holds items only. Stored widget cards (the retired
    ``aggregate_widget`` type) are dropped once on load, and new ones are refused.
    """

    def test_stored_widget_cards_are_dropped_on_load(self):
        """The three seeded widget cards go; the user's cards stay, in order, renumbered."""
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_layout(Path(tmpdir), _LEGACY_SEEDED)
            mgr = DashboardLayoutManager(Path(tmpdir))
            assert [(c.type, c.id, c.order) for c in mgr.list_cards()] == [(CARD_PROFILE, "movie_night", 0)]

    def test_the_migration_is_saved(self):
        """The cleaned layout is written back, so the next load (and other readers) see it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = _write_layout(Path(tmpdir), _LEGACY_SEEDED)
            DashboardLayoutManager(Path(tmpdir))
            assert json.loads(path.read_text(encoding="utf-8"))["cards"] == [
                {"type": "profile", "id": "movie_night", "order": 0}
            ]

    def test_a_layout_without_widget_cards_is_not_rewritten(self):
        """Loading a layout that needs no migration leaves the file untouched."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original = json.dumps({"version": 1, "cards": [{"type": "preset", "id": "2", "order": 5}]})
            path = Path(tmpdir) / "dashboard_layout.json"
            path.write_text(original, encoding="utf-8")
            DashboardLayoutManager(Path(tmpdir))
            assert path.read_text(encoding="utf-8") == original

    def test_widget_card_type_is_refused(self):
        """add_card and from_dict reject the retired widget card type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = DashboardLayoutManager(Path(tmpdir))
            assert mgr.add_card(CARD_AGGREGATE_WIDGET, "routing-dashboard") is False
            assert mgr.list_cards() == []
        with pytest.raises(ValueError, match="Unknown card type"):
            DashboardCard.from_dict({"type": CARD_AGGREGATE_WIDGET, "id": "cec-tray"})

    def test_replace_layout_drops_widget_cards(self):
        """A bulk replace containing a widget card keeps only the item cards."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = DashboardLayoutManager(Path(tmpdir))
            mgr.replace_layout(
                DashboardLayout(
                    cards=[
                        DashboardCard(type=CARD_AGGREGATE_WIDGET, id="routing-dashboard", order=0),
                        DashboardCard(type=CARD_PRESET, id="1", order=1),
                    ]
                )
            )
            assert [(c.type, c.id) for c in mgr.list_cards()] == [(CARD_PRESET, "1")]


def _manager_with_cards(tmpdir: str, *cards: tuple[str, str]) -> DashboardLayoutManager:
    _write_layout(
        Path(tmpdir), [{"type": card_type, "id": card_id, "order": i} for i, (card_type, card_id) in enumerate(cards)]
    )
    return DashboardLayoutManager(Path(tmpdir))


class TestDashboardLayoutManagerQueries:
    """Tests for get_layout, list_cards, has_card."""

    def test_get_layout_returns_full_layout(self):
        """get_layout() returns the complete DashboardLayout object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = _manager_with_cards(tmpdir, (CARD_PROFILE, "a"), (CARD_PRESET, "1"), (CARD_PROFILE, "b"))
            layout = mgr.get_layout()
            assert isinstance(layout, DashboardLayout)
            assert len(layout.cards) == 3

    def test_list_cards_returns_cards_sorted_by_order(self):
        """list_cards() returns all cards sorted by order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = _manager_with_cards(tmpdir, (CARD_PROFILE, "a"), (CARD_PRESET, "1"), (CARD_PROFILE, "b"))
            cards = mgr.list_cards()
            assert len(cards) == 3
            orders = [c.order for c in cards]
            assert orders == sorted(orders)

    def test_has_card_returns_true_for_existing(self):
        """has_card(type, id) returns True for a card that is present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = _manager_with_cards(tmpdir, (CARD_PROFILE, "a"), (CARD_PRESET, "1"))
            assert mgr.has_card(CARD_PROFILE, "a") is True
            assert mgr.has_card(CARD_PRESET, "1") is True

    def test_has_card_returns_false_for_missing(self):
        """has_card(type, id) returns False for a card that is not present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = DashboardLayoutManager(Path(tmpdir))
            assert mgr.has_card(CARD_PROFILE, "nonexistent") is False
            assert mgr.has_card(CARD_PRESET, "99") is False


class TestDashboardLayoutManagerMutations:
    """Tests for add_card, remove_card, replace_layout."""

    def test_add_card_appends_to_end(self):
        """add_card(type, id) adds a new card with the next order value."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = _manager_with_cards(tmpdir, (CARD_PROFILE, "a"), (CARD_PRESET, "1"), (CARD_PROFILE, "b"))
            result = mgr.add_card(CARD_PROFILE, "my_profile")
            assert result is True
            assert mgr.has_card(CARD_PROFILE, "my_profile") is True
            # Should be at the end (order = 3, after the three stored cards)
            cards = mgr.list_cards()
            new_card = next(c for c in cards if c.id == "my_profile")
            assert new_card.order == 3

    def test_add_card_noop_if_duplicate(self):
        """add_card(type, id) returns False if the card is already present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = DashboardLayoutManager(Path(tmpdir))
            result1 = mgr.add_card(CARD_PROFILE, "my_profile")
            assert result1 is True
            result2 = mgr.add_card(CARD_PROFILE, "my_profile")
            assert result2 is False

    def test_add_card_invalid_type_returns_false(self):
        """add_card(invalid_type, id) returns False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = DashboardLayoutManager(Path(tmpdir))
            result = mgr.add_card("not_a_card_type", "some_id")
            assert result is False

    def test_remove_card_deletes_and_compacts_order(self):
        """remove_card(type, id) removes the card and recompacts remaining order values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = _manager_with_cards(tmpdir, (CARD_PROFILE, "a"), (CARD_PRESET, "1"), (CARD_PROFILE, "b"))
            # Remove the middle card (preset 1, order=1)
            result = mgr.remove_card(CARD_PRESET, "1")
            assert result is True
            assert mgr.has_card(CARD_PRESET, "1") is False
            # Remaining cards should have compacted orders 0 and 1
            cards = mgr.list_cards()
            orders = [c.order for c in cards]
            assert orders == [0, 1]

    def test_remove_card_returns_false_if_not_present(self):
        """remove_card(type, id) returns False if the card was not present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = DashboardLayoutManager(Path(tmpdir))
            result = mgr.remove_card(CARD_PROFILE, "nonexistent")
            assert result is False

    def test_replace_layout_atomically_replaces(self):
        """replace_layout(new_layout) atomically replaces the entire layout."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = DashboardLayoutManager(Path(tmpdir))
            new_layout = DashboardLayout(
                cards=[
                    DashboardCard(type=CARD_PRESET, id="1", order=0),
                    DashboardCard(type=CARD_PRESET, id="2", order=1),
                ]
            )
            result = mgr.replace_layout(new_layout)
            assert result is True
            cards = mgr.list_cards()
            assert len(cards) == 2
            ids = {c.id for c in cards}
            assert ids == {"1", "2"}

    def test_replace_layout_deduplicates_by_type_id(self):
        """replace_layout deduplicates cards with the same (type, id), keeping first."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = DashboardLayoutManager(Path(tmpdir))
            new_layout = DashboardLayout(
                cards=[
                    DashboardCard(type=CARD_PRESET, id="1", order=0),
                    DashboardCard(type=CARD_PRESET, id="1", order=1),  # duplicate
                    DashboardCard(type=CARD_PRESET, id="2", order=2),
                ]
            )
            mgr.replace_layout(new_layout)
            # Should only have one "preset:1" card
            preset1_count = sum(1 for c in mgr.list_cards() if c.type == CARD_PRESET and c.id == "1")
            assert preset1_count == 1

    def test_replace_layout_recompacts_order(self):
        """replace_layout recompacts order values to 0..N-1 after dedup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = DashboardLayoutManager(Path(tmpdir))
            new_layout = DashboardLayout(
                cards=[
                    DashboardCard(type=CARD_PROFILE, id="a", order=99),
                    DashboardCard(type=CARD_PROFILE, id="b", order=100),
                ]
            )
            mgr.replace_layout(new_layout)
            orders = [c.order for c in mgr.list_cards()]
            assert orders == [0, 1]

    def test_replace_layout_skips_invalid_card_types(self):
        """replace_layout silently skips cards with invalid types (logs warning)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = DashboardLayoutManager(Path(tmpdir))
            new_layout = DashboardLayout(
                cards=[
                    DashboardCard(type=CARD_PROFILE, id="valid", order=0),
                    DashboardCard(type="bad_type", id="invalid", order=1),
                ]
            )
            mgr.replace_layout(new_layout)
            assert mgr.has_card(CARD_PROFILE, "valid") is True
            assert mgr.has_card("bad_type", "invalid") is False
