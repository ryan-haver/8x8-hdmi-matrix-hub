"""
Dashboard Layout - Server-backed card ordering for the Dashboard tab.

The Dashboard tab renders a grid of cards. Each card is one of:

- **profile**: A saved routing profile (one-tap recall)
- **preset**: A hardware preset 1-8 (one-tap recall)
- **system_shortcut**: A built-in quick-routing shortcut like "All → Out 1"
- **macro**: A CEC macro (one-tap execute)
- **aggregate_widget**: A built-in multi-item widget (CEC Tray, Routing, etc.)

Storage
-------

A single ``dashboard_layout.json`` file in the persistent data directory
holds the canonical ordered list of cards. Per-item ``favorite`` and
``dashboard_visible`` flags (on Profile / SystemShortcut / CecMacro) and
the ``favorite_presets`` / ``dashboard_presets`` lists in device_settings
provide redundant access for sorting and queries, but the layout file is
the single source of truth for *what is on the dashboard and in what
order*.

Backwards Compatibility
-----------------------

On first load, the layout is seeded with the three legacy aggregate
widgets (cec-tray, routing-dashboard, quick-actions) so existing users
see the same dashboard as before. Adding/removing/reordering individual
cards is then purely additive — the legacy widgets stay until the user
removes them.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from persistence import ensure_data_dir, get_data_dir, migrate_legacy_file

_LOG = logging.getLogger("dashboard_layout")

_LAYOUT_FILE = "dashboard_layout.json"

# Card type constants
CARD_PROFILE = "profile"
CARD_PRESET = "preset"
CARD_SYSTEM_SHORTCUT = "system_shortcut"
CARD_MACRO = "macro"
CARD_AGGREGATE_WIDGET = "aggregate_widget"

VALID_CARD_TYPES = frozenset({
    CARD_PROFILE,
    CARD_PRESET,
    CARD_SYSTEM_SHORTCUT,
    CARD_MACRO,
    CARD_AGGREGATE_WIDGET,
})

# The three legacy aggregate widgets that shipped pre-Phase 7.
# They remain in the default layout for backwards compatibility.
LEGACY_AGGREGATE_WIDGETS = ("cec-tray", "routing-dashboard", "quick-actions")


@dataclass
class DashboardCard:
    """
    A single card on the dashboard grid.

    :param type: One of :data:`VALID_CARD_TYPES`
    :param id: Identifier — profile id, preset number (1-8), shortcut id,
                macro id, or aggregate-widget id (e.g. ``cec-tray``)
    :param order: Position in the grid (lower = earlier; ties broken by id)
    """

    type: str
    id: str
    order: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dict."""
        return {
            "type": self.type,
            "id": self.id,
            "order": self.order,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "DashboardCard":
        """Deserialize from a dict. Validates the ``type`` field."""
        type_value = data.get("type", "")
        if type_value not in VALID_CARD_TYPES:
            raise ValueError(f"Unknown card type: {type_value!r}")
        id_value = data.get("id", "")
        if not isinstance(id_value, str) or not id_value:
            raise ValueError("Card id must be a non-empty string")
        return DashboardCard(
            type=type_value,
            id=id_value,
            order=int(data.get("order", 0)),
        )

    def key(self) -> tuple[str, str]:
        """Return a stable (type, id) tuple for dedup / lookup."""
        return (self.type, self.id)


@dataclass
class DashboardLayout:
    """
    The full dashboard layout — an ordered list of cards plus a schema
    version (for future migrations).
    """

    cards: list[DashboardCard] = field(default_factory=list)
    version: int = 1

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dict."""
        return {
            "version": self.version,
            "cards": [c.to_dict() for c in self.cards],
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "DashboardLayout":
        """Deserialize from a dict. Unknown card types are skipped."""
        cards: list[DashboardCard] = []
        for entry in data.get("cards", []):
            try:
                cards.append(DashboardCard.from_dict(entry))
            except ValueError as exc:
                _LOG.warning("Skipping invalid dashboard card: %s", exc)
        # Sort by order (stable on ties)
        cards.sort(key=lambda c: c.order)
        return DashboardLayout(
            cards=cards,
            version=int(data.get("version", 1)),
        )


def _default_layout() -> DashboardLayout:
    """The first-run layout: the three legacy aggregate widgets only."""
    cards = [
        DashboardCard(type=CARD_AGGREGATE_WIDGET, id=widget_id, order=i)
        for i, widget_id in enumerate(LEGACY_AGGREGATE_WIDGETS)
    ]
    return DashboardLayout(cards=cards, version=1)


class DashboardLayoutManager:
    """
    CRUD + persistence for the dashboard layout.

    The manager owns a single ``DashboardLayout`` value. On first access
    the default (legacy aggregate widgets) is seeded; subsequent loads
    preserve user edits.
    """

    def __init__(self, data_dir: Path | None = None):
        """Initialize with a data directory (defaults to :func:`get_data_dir`)."""
        if data_dir is None:
            data_dir = get_data_dir()
        self.data_dir = Path(data_dir).resolve()
        self.file_path = self.data_dir / _LAYOUT_FILE
        self._layout: DashboardLayout = DashboardLayout()
        self._ensure_loaded()

    # ------------------------------------------------------------------ load/save
    def _ensure_loaded(self) -> None:
        """Load from disk, seeding defaults if the file is missing or invalid."""
        migrate_legacy_file(self.file_path, _LAYOUT_FILE)
        if not self.file_path.exists():
            self._layout = _default_layout()
            self._save()
            return
        try:
            with open(self.file_path, encoding="utf-8") as fh:
                payload = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            _LOG.warning("Failed to load dashboard_layout.json: %s — reseeding defaults", exc)
            self._layout = _default_layout()
            self._save()
            return
        self._layout = DashboardLayout.from_dict(payload)

    def _save(self) -> bool:
        """Persist the current layout to disk."""
        try:
            ensure_data_dir(self.data_dir)
            with open(self.file_path, "w", encoding="utf-8") as fh:
                json.dump(self._layout.to_dict(), fh, indent=2)
            return True
        except OSError as exc:
            _LOG.error("Failed to save dashboard_layout.json: %s", exc)
            return False

    # ------------------------------------------------------------------ queries
    def get_layout(self) -> DashboardLayout:
        """Return the current full layout."""
        return self._layout

    def list_cards(self) -> list[DashboardCard]:
        """Return the cards in display order."""
        return list(self._layout.cards)

    def has_card(self, card_type: str, card_id: str) -> bool:
        """Return True if the specified card is currently on the dashboard."""
        target = (card_type, card_id)
        return any(c.key() == target for c in self._layout.cards)

    # ------------------------------------------------------------------ mutations
    def add_card(self, card_type: str, card_id: str) -> bool:
        """Add a card to the end of the layout. No-op if already present."""
        if card_type not in VALID_CARD_TYPES:
            return False
        if not card_id:
            return False
        if self.has_card(card_type, card_id):
            return False
        next_order = (max((c.order for c in self._layout.cards), default=-1)) + 1
        self._layout.cards.append(
            DashboardCard(type=card_type, id=card_id, order=next_order)
        )
        return self._save()

    def remove_card(self, card_type: str, card_id: str) -> bool:
        """Remove a card from the layout. No-op if not present."""
        target = (card_type, card_id)
        before = len(self._layout.cards)
        self._layout.cards = [c for c in self._layout.cards if c.key() != target]
        if len(self._layout.cards) == before:
            return False
        # Compact order values so we don't leave gaps
        self._layout.cards.sort(key=lambda c: c.order)
        for i, c in enumerate(self._layout.cards):
            c.order = i
        return self._save()

    def replace_layout(self, layout: DashboardLayout) -> bool:
        """Replace the full layout atomically. Used by the bulk PUT endpoint."""
        if not isinstance(layout, DashboardLayout):
            return False
        # Deduplicate by (type, id) preserving first occurrence
        seen: set[tuple[str, str]] = set()
        deduped: list[DashboardCard] = []
        for c in sorted(layout.cards, key=lambda x: x.order):
            if c.type not in VALID_CARD_TYPES or not c.id:
                continue
            key = c.key()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(c)
        # Recompact order
        for i, c in enumerate(deduped):
            c.order = i
        self._layout = DashboardLayout(cards=deduped, version=layout.version or 1)
        return self._save()