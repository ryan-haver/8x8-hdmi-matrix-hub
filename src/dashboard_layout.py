"""
Dashboard Layout - Server-backed card ordering for the Dashboard tab.

The Dashboard tab renders a grid of cards. Each card is one of:

- **profile**: A saved routing profile (one-tap recall)
- **preset**: A hardware preset 1-8 (one-tap recall)
- **system_shortcut**: A built-in quick-routing shortcut like "All → Out 1"
- **macro**: A CEC macro (one-tap execute)
- **scene**: A scene (one-tap execute)

Widgets (Routing, CEC Remote) are not cards: the web UI pins them per
browser. The former ``aggregate_widget`` card type is retired (UI-55/UI-57).

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

A new install starts with an empty layout. Earlier versions seeded three
``aggregate_widget`` cards (cec-tray, routing-dashboard, quick-actions);
they showed the pinned Routing and CEC Remote widgets a second time and the
retired Quick Actions widget as an empty card. Loading a stored layout drops
them once and saves the result (UI-55/UI-57, owner decision 2026-10-09).
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
CARD_SCENE = "scene"
CARD_AGGREGATE_WIDGET = "aggregate_widget"

VALID_CARD_TYPES = frozenset(
    {
        CARD_PROFILE,
        CARD_PRESET,
        CARD_SYSTEM_SHORTCUT,
        CARD_MACRO,
        CARD_SCENE,
    }
)

# Card types older versions stored; a stored layout drops them on load (UI-55/UI-57).
RETIRED_CARD_TYPES = frozenset({CARD_AGGREGATE_WIDGET})


@dataclass
class DashboardCard:
    """
    A single card on the dashboard grid.

    :param type: One of :data:`VALID_CARD_TYPES`
    :param id: Identifier — profile id, preset number (1-8), shortcut id,
                macro id, or scene id
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
    """The first-run layout: no cards."""
    return DashboardLayout(cards=[], version=1)


def _drop_retired_cards(payload: dict[str, Any]) -> bool:
    """Remove cards of a retired type from a stored layout payload, in place.

    :return: True if any card was removed
    """
    cards = payload.get("cards")
    if not isinstance(cards, list):
        return False
    kept = [c for c in cards if not (isinstance(c, dict) and c.get("type") in RETIRED_CARD_TYPES)]
    if len(kept) == len(cards):
        return False
    _LOG.info("Removing %d retired widget card(s) from the dashboard layout", len(cards) - len(kept))
    payload["cards"] = kept
    return True


class DashboardLayoutManager:
    """
    CRUD + persistence for the dashboard layout.

    The manager owns a single ``DashboardLayout`` value. On first access
    an empty layout is seeded; subsequent loads preserve user edits.
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
        migrated = isinstance(payload, dict) and _drop_retired_cards(payload)
        self._layout = DashboardLayout.from_dict(payload)
        if migrated:
            for i, c in enumerate(self._layout.cards):
                c.order = i
            self._save()

    def _save(self) -> bool:
        """Persist the current layout to disk atomically."""
        try:
            ensure_data_dir(self.data_dir)
            from _file_io import atomic_write_json
            atomic_write_json(self.file_path, self._layout.to_dict())
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
        self._layout.cards.append(DashboardCard(type=card_type, id=card_id, order=next_order))
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
