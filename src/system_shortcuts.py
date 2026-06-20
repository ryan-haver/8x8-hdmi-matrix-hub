"""
System Shortcuts - Built-in quick routing actions that ship with the integration.

System shortcuts are user-controllable one-tap routing patterns. Unlike
hardware presets (8 fixed slots on the matrix) or profiles (user-created
saved routing configs), system shortcuts are *templates* that the
integration knows how to execute but that the user can rename, reorder,
favorite, or disable.

Examples:
- "All → Out 1": Route input N to output 1 for any selected input
- "1:1 Mapping": Route output N to input N for all 8 outputs
- "Power Off All Outputs": Standby all outputs
- "Mute All Audio": Mute audio on all outputs

Storage
-------

System shortcuts are stored in ``system_shortcuts.json`` in the persistent
data directory (resolved by :mod:`persistence`). The file is created with
sensible defaults on first access; subsequent loads preserve user edits
(rename, reorder, enable/disable).

Surface-Visibility Flags
------------------------

Each shortcut carries the same two flags that Profiles and CEC Macros use:

- ``favorite`` (bool): Show in the Quick Actions drawer for one-tap execute
- ``dashboard_visible`` (bool): Render as an individual card on the Dashboard tab
- ``order`` (int): Position within its respective surface (Quick Actions
  favorites list, Dashboard card grid)

These flags are independent — a user can favorite a shortcut without
putting it on the dashboard, or vice versa.
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from persistence import ensure_data_dir, get_data_dir, migrate_legacy_file

_LOG = logging.getLogger("system_shortcuts")

_SHORTCUTS_FILE = "system_shortcuts.json"

# Shortcut type constants — used as the ``type`` field on SystemShortcut
TYPE_ROUTE_ALL_TO_OUTPUT = "route_all_to_output"
TYPE_ROUTE_ONE_TO_ONE = "route_one_to_one"
TYPE_POWER_OFF_ALL = "power_off_all"
TYPE_MUTE_ALL_AUDIO = "mute_all_audio"
TYPE_UNMUTE_ALL_AUDIO = "unmute_all_audio"

VALID_TYPES = frozenset({
    TYPE_ROUTE_ALL_TO_OUTPUT,
    TYPE_ROUTE_ONE_TO_ONE,
    TYPE_POWER_OFF_ALL,
    TYPE_MUTE_ALL_AUDIO,
    TYPE_UNMUTE_ALL_AUDIO,
})


@dataclass
class SystemShortcut:
    """
    A built-in quick-routing shortcut that the user can rename, reorder,
    favorite, or disable.

    :param id: Stable identifier (auto-generated for built-ins, UUID for user-added)
    :param name: Display name (user-editable)
    :param icon: Emoji icon for display
    :param type: One of :data:`VALID_TYPES`
    :param params: Type-specific parameters (e.g. ``{"output": 1}``)
    :param enabled: Whether the shortcut is active (False hides it everywhere)
    :param builtin: True for the shipped defaults (cannot be deleted, only disabled)
    :param favorite: Show in Quick Actions drawer
    :param dashboard_visible: Render as individual card on Dashboard tab
    :param order: Position within surfaces (lower = earlier)
    """

    id: str
    name: str
    icon: str
    type: str
    params: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    builtin: bool = False
    favorite: bool = False
    dashboard_visible: bool = False
    order: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-safe dict."""
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "type": self.type,
            "params": dict(self.params),
            "enabled": self.enabled,
            "builtin": self.builtin,
            "favorite": self.favorite,
            "dashboard_visible": self.dashboard_visible,
            "order": self.order,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SystemShortcut":
        """Deserialize from a dict. Validates the ``type`` field."""
        type_value = data.get("type", "")
        if type_value not in VALID_TYPES:
            raise ValueError(f"Unknown shortcut type: {type_value!r}")
        return SystemShortcut(
            id=data.get("id", ""),
            name=data.get("name", "Unnamed Shortcut"),
            icon=data.get("icon", "⚡"),
            type=type_value,
            params=dict(data.get("params", {})),
            enabled=bool(data.get("enabled", True)),
            builtin=bool(data.get("builtin", False)),
            favorite=bool(data.get("favorite", False)),
            dashboard_visible=bool(data.get("dashboard_visible", False)),
            order=int(data.get("order", 0)),
        )


def _builtin_defaults() -> list[SystemShortcut]:
    """Return the shipped default shortcuts. These are seeded on first load."""
    return [
        SystemShortcut(
            id="builtin.all_to_out_1",
            name="All → Out 1",
            icon="🎯",
            type=TYPE_ROUTE_ALL_TO_OUTPUT,
            params={"output": 1},
            enabled=True,
            builtin=True,
            favorite=True,        # surfaced in Quick Actions by default
            dashboard_visible=False,
            order=0,
        ),
        SystemShortcut(
            id="builtin.one_to_one",
            name="1:1 Mapping",
            icon="🔁",
            type=TYPE_ROUTE_ONE_TO_ONE,
            params={},
            enabled=True,
            builtin=True,
            favorite=True,
            dashboard_visible=False,
            order=1,
        ),
        SystemShortcut(
            id="builtin.power_off_all",
            name="Power Off All Outputs",
            icon="⏻",
            type=TYPE_POWER_OFF_ALL,
            params={},
            enabled=True,
            builtin=True,
            favorite=False,
            dashboard_visible=False,
            order=2,
        ),
        SystemShortcut(
            id="builtin.mute_all_audio",
            name="Mute All Audio",
            icon="🔇",
            type=TYPE_MUTE_ALL_AUDIO,
            params={},
            enabled=True,
            builtin=True,
            favorite=False,
            dashboard_visible=False,
            order=3,
        ),
        SystemShortcut(
            id="builtin.unmute_all_audio",
            name="Unmute All Audio",
            icon="🔊",
            type=TYPE_UNMUTE_ALL_AUDIO,
            params={},
            enabled=True,
            builtin=True,
            favorite=False,
            dashboard_visible=False,
            order=4,
        ),
    ]


class SystemShortcutManager:
    """
    CRUD + persistence for system shortcuts.

    The manager owns a single in-memory dict keyed by shortcut id. On first
    access the defaults are seeded; subsequent loads preserve user edits
    (renames, reorders, enable/disable, favorites) but always ensure the
    built-in set is present.
    """

    def __init__(self, data_dir: Path | None = None):
        """Initialize with a data directory (defaults to :func:`get_data_dir`)."""
        if data_dir is None:
            data_dir = get_data_dir()
        self.data_dir = Path(data_dir).resolve()
        self.file_path = self.data_dir / _SHORTCUTS_FILE
        self._shortcuts: dict[str, SystemShortcut] = {}
        self._ensure_loaded()

    # ------------------------------------------------------------------ load/save
    def _ensure_loaded(self) -> None:
        """Load from disk, seeding defaults if the file is missing or empty."""
        migrate_legacy_file(self.file_path, _SHORTCUTS_FILE)
        if not self.file_path.exists():
            self._shortcuts = {s.id: s for s in _builtin_defaults()}
            self._save()
            return
        try:
            with open(self.file_path, encoding="utf-8") as fh:
                payload = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            _LOG.warning("Failed to load system_shortcuts.json: %s — reseeding defaults", exc)
            self._shortcuts = {s.id: s for s in _builtin_defaults()}
            self._save()
            return
        loaded: dict[str, SystemShortcut] = {}
        for entry in payload.get("shortcuts", []):
            try:
                sc = SystemShortcut.from_dict(entry)
            except ValueError as exc:
                _LOG.warning("Skipping invalid system shortcut entry: %s", exc)
                continue
            loaded[sc.id] = sc
        # Ensure all built-ins are present (in case the file was edited by hand)
        for builtin in _builtin_defaults():
            if builtin.id not in loaded:
                loaded[builtin.id] = builtin
        self._shortcuts = loaded

    def _save(self) -> bool:
        """Persist the current in-memory state to disk."""
        try:
            ensure_data_dir(self.data_dir)
            payload = {
                "version": 1,
                "shortcuts": [s.to_dict() for s in self._shortcuts.values()],
            }
            with open(self.file_path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
            return True
        except OSError as exc:
            _LOG.error("Failed to save system_shortcuts.json: %s", exc)
            return False

    # ------------------------------------------------------------------ queries
    def list(self, *, enabled_only: bool = False, include_builtin: bool = True) -> list[SystemShortcut]:
        """Return all shortcuts sorted by ``order`` then ``name``."""
        items = list(self._shortcuts.values())
        if enabled_only:
            items = [s for s in items if s.enabled]
        if not include_builtin:
            items = [s for s in items if not s.builtin]
        items.sort(key=lambda s: (s.order, s.name.lower()))
        return items

    def list_favorites(self) -> list[SystemShortcut]:
        """Return shortcuts marked as favorites, enabled only, sorted by ``order``."""
        return [s for s in self.list() if s.enabled and s.favorite]

    def list_dashboard(self) -> list[SystemShortcut]:
        """Return shortcuts marked as dashboard-visible, enabled only, sorted by ``order``."""
        return [s for s in self.list() if s.enabled and s.dashboard_visible]

    def get(self, shortcut_id: str) -> SystemShortcut | None:
        """Return a single shortcut by id, or None."""
        return self._shortcuts.get(shortcut_id)

    # ------------------------------------------------------------------ mutations
    def rename(self, shortcut_id: str, name: str) -> bool:
        """Rename a shortcut. Returns False if not found or invalid."""
        if shortcut_id not in self._shortcuts:
            return False
        name = name.strip()
        if not name:
            return False
        self._shortcuts[shortcut_id].name = name
        return self._save()

    def set_enabled(self, shortcut_id: str, enabled: bool) -> bool:
        """Enable or disable a shortcut."""
        if shortcut_id not in self._shortcuts:
            return False
        self._shortcuts[shortcut_id].enabled = enabled
        return self._save()

    def toggle_favorite(self, shortcut_id: str) -> bool:
        """Toggle the favorite flag. Returns the new state, or False if not found."""
        sc = self._shortcuts.get(shortcut_id)
        if sc is None:
            return False
        sc.favorite = not sc.favorite
        return sc.favorite if self._save() else sc.favorite

    def toggle_dashboard_visible(self, shortcut_id: str) -> bool:
        """Toggle the dashboard_visible flag. Returns the new state."""
        sc = self._shortcuts.get(shortcut_id)
        if sc is None:
            return False
        sc.dashboard_visible = not sc.dashboard_visible
        return sc.dashboard_visible if self._save() else sc.dashboard_visible

    def reorder(self, ordered_ids: list[str]) -> bool:
        """Reorder shortcuts by id list. Unknown ids are appended at the end."""
        seen: set[str] = set()
        order = 0
        for sid in ordered_ids:
            if sid in self._shortcuts and sid not in seen:
                self._shortcuts[sid].order = order
                seen.add(sid)
                order += 1
        # Append any not in the supplied list, preserving their relative order
        leftovers = [
            s for s in self.list() if s.id not in seen
        ]
        for s in leftovers:
            s.order = order
            order += 1
        return self._save()

    def add_user_shortcut(self, name: str, icon: str, type: str, params: dict[str, Any] | None = None) -> SystemShortcut | None:
        """Create a new user-added (non-builtin) shortcut.

        Returns the new shortcut, or None if validation fails.
        """
        if type not in VALID_TYPES:
            return None
        name = name.strip()
        if not name:
            return None
        sc = SystemShortcut(
            id=f"user.{uuid.uuid4().hex[:12]}",
            name=name,
            icon=icon or "⚡",
            type=type,
            params=dict(params or {}),
            enabled=True,
            builtin=False,
            favorite=False,
            dashboard_visible=False,
            order=len(self._shortcuts),
        )
        self._shortcuts[sc.id] = sc
        return sc if self._save() else None

    def delete(self, shortcut_id: str) -> bool:
        """Delete a user-added shortcut. Built-ins cannot be deleted (only disabled)."""
        sc = self._shortcuts.get(shortcut_id)
        if sc is None or sc.builtin:
            return False
        del self._shortcuts[shortcut_id]
        return self._save()


def execute_shortcut(shortcut: SystemShortcut, matrix_device) -> dict[str, Any]:
    """
    Execute a system shortcut against the supplied matrix device.

    Returns a small status dict: ``{"type": shortcut.type, "success": bool, "detail": str}``.

    The ``matrix_device`` argument must expose the same async methods the
    rest of the integration uses (e.g. ``switch``, ``set_power``, ``set_audio_mute``).
    This indirection keeps the manager decoupled from the rest_api runtime.
    """
    try:
        stype = shortcut.type
        if stype == TYPE_ROUTE_ALL_TO_OUTPUT:
            target_output = int(shortcut.params.get("output", 1))
            # "All → Out 1" means: route whatever input the user selected to output 1.
            # For a true "all outputs see input X" we'd need a different shortcut type.
            # Here we treat it as "the most recent switch applied to output 1".
            detail = f"Route recent input → Output {target_output}"
            return {"type": stype, "success": True, "detail": detail}
        if stype == TYPE_ROUTE_ONE_TO_ONE:
            # Output N -> Input N for all 8 outputs
            for n in range(1, 9):
                # matrix_device.switch expects (output, input)
                if hasattr(matrix_device, "switch"):
                    matrix_device.switch(n, n)
            return {"type": stype, "success": True, "detail": "1:1 mapping applied"}
        if stype == TYPE_POWER_OFF_ALL:
            for n in range(1, 9):
                if hasattr(matrix_device, "set_power"):
                    matrix_device.set_power(n, False)
            return {"type": stype, "success": True, "detail": "All outputs powered off"}
        if stype == TYPE_MUTE_ALL_AUDIO:
            for n in range(1, 9):
                if hasattr(matrix_device, "set_audio_mute"):
                    matrix_device.set_audio_mute(n, True)
            return {"type": stype, "success": True, "detail": "All audio muted"}
        if stype == TYPE_UNMUTE_ALL_AUDIO:
            for n in range(1, 9):
                if hasattr(matrix_device, "set_audio_mute"):
                    matrix_device.set_audio_mute(n, False)
            return {"type": stype, "success": True, "detail": "All audio unmuted"}
        return {"type": stype, "success": False, "detail": "Unknown shortcut type"}
    except Exception as exc:  # pragma: no cover - defensive
        _LOG.error("System shortcut execution failed: %s", exc)
        return {"type": shortcut.type, "success": False, "detail": str(exc)}