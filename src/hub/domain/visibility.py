"""One view of the surface-visibility flags of everything the hub owns (DI-5, API-20).

Five kinds of item decide where they show up, and each kept its own flags:
profiles, scenes, macros and shortcuts carry ``favorite`` and
``dashboard_visible`` on the item itself, while the eight hardware preset slots
keep two lists in ``device_settings.json`` because they cannot carry fields.
The dashboard layout, the Quick Actions drawer and the Remote integration each
reconciled those five sources themselves, which is how a deleted item kept a
card alive.

:class:`VisibilityStore` reads and writes all five through one interface and
writes both flags of an item in a single manager call, so a surface can ask
"what is visible?" and change it without knowing where it is stored.
"""

from __future__ import annotations

import logging
from typing import Any

_LOG = logging.getLogger(__name__)

#: The kinds of item the store knows about.
VISIBILITY_KINDS: tuple[str, ...] = ("presets", "profiles", "scenes", "macros", "shortcuts")

#: What an item the store does not know reads as.
DEFAULT_FLAGS: dict[str, bool] = {"favorite": False, "show_on_dashboard": False}

#: The hardware preset slots the matrix offers.
PRESET_SLOTS = range(1, 9)

Flags = dict[str, bool]


def _flags(favorite: Any, show_on_dashboard: Any) -> Flags:
    """The two flags of one item, always both present."""
    return {"favorite": bool(favorite), "show_on_dashboard": bool(show_on_dashboard)}


class VisibilityStore:
    """
    The favorite / dashboard flags of every kind of item, in one place.

    Every manager is optional: a kind without its source reads as empty (and
    writes as "no such item"), so a caller never has to know which parts of the
    hub are running. ``from_runtime()`` builds one from the running hub's
    managers.
    """

    def __init__(
        self,
        *,
        profiles: Any = None,
        scenes: Any = None,
        macros: Any = None,
        shortcuts: Any = None,
        presets: Any = None,
    ) -> None:
        """
        :param profiles: ``ProfileManager`` (``favorite`` / ``dashboard_visible``)
        :param scenes: ``SceneManager`` (``favorite`` / ``dashboard_visible``)
        :param macros: ``MacroManager`` (``favorite`` / ``dashboard_visible``)
        :param shortcuts: ``SystemShortcutManager`` (``favorite`` / ``dashboard_visible``)
        :param presets: the device-settings store, which keeps the two preset
                        lists (``get_favorite_presets`` / ``set_favorite_presets``
                        and their ``dashboard`` counterparts)
        """
        self._adapters: dict[str, _VisibilityAdapter] = {
            "presets": _PresetVisibility(presets),
            "profiles": _ProfileVisibility(profiles),
            "scenes": _SceneVisibility(scenes),
            "macros": _MacroVisibility(macros),
            "shortcuts": _ShortcutVisibility(shortcuts),
        }

    @classmethod
    def from_runtime(cls) -> VisibilityStore:
        """A store bound to the managers the running hub already holds."""
        from rest_api import device_settings
        from rest_api.utils import (
            get_macro_manager,
            get_profile_manager,
            get_scene_manager,
            get_system_shortcut_manager,
        )

        return cls(
            profiles=get_profile_manager(),
            scenes=get_scene_manager(),
            macros=get_macro_manager(),
            shortcuts=get_system_shortcut_manager(),
            presets=device_settings,
        )

    @property
    def kinds(self) -> tuple[str, ...]:
        """The kinds of item this store knows about."""
        return VISIBILITY_KINDS

    def get_visibility(self, kind: str, item_id: str | int) -> Flags:
        """
        The flags of one item.

        An item the store does not know reads as both False, so a surface can
        ask about anything without checking first.
        """
        flags = self._adapter(kind).read(str(item_id))
        return dict(flags) if flags is not None else dict(DEFAULT_FLAGS)

    def set_favorite(self, kind: str, item_id: str | int, favorite: bool) -> Flags | None:
        """Set the favorite flag (Quick Actions drawer); None if there is no such item."""
        return self.apply(kind, item_id, favorite=bool(favorite))

    def set_dashboard(self, kind: str, item_id: str | int, show_on_dashboard: bool) -> Flags | None:
        """Set the dashboard flag; None if there is no such item."""
        return self.apply(kind, item_id, show_on_dashboard=bool(show_on_dashboard))

    def apply(
        self,
        kind: str,
        item_id: str | int,
        *,
        favorite: bool | None = None,
        show_on_dashboard: bool | None = None,
    ) -> Flags | None:
        """
        Set one or both flags of one item in a single write.

        Only the flags given are changed. A manager that keeps both flags on one
        item is written once (one save, no window where the two disagree); the
        preset slots keep them in two lists of one settings file, which their
        store writes in turn.
        """
        adapter = self._adapter(kind)
        if favorite is None and show_on_dashboard is None:
            return self.get_visibility(kind, item_id)

        flags = adapter.write(str(item_id), favorite=favorite, show_on_dashboard=show_on_dashboard)
        if flags is None:
            _LOG.warning("Cannot change the visibility of %s '%s': no such item", kind, item_id)
        return flags

    def snapshot(self) -> dict[str, dict[str, Flags]]:
        """
        Every flag of every item: ``{kind: {item_id: {"favorite", "show_on_dashboard"}}}``.

        All kinds are present even when they have no items, so a caller can tell
        "nothing is favourited" from "favourites are not loaded".
        """
        return {kind: self._adapters[kind].items() for kind in VISIBILITY_KINDS}

    def _adapter(self, kind: str) -> _VisibilityAdapter:
        """The adapter of one kind; ValueError for a kind this store does not have."""
        try:
            return self._adapters[kind]
        except KeyError:
            raise ValueError(
                f"Unknown visibility kind: {kind!r}; expected one of {', '.join(VISIBILITY_KINDS)}"
            ) from None


# =============================================================================
# Adapters: one per kind, each knowing where that kind keeps its flags
# =============================================================================


class _VisibilityAdapter:
    """Reads and writes the two flags of one kind of item."""

    def __init__(self, source: Any = None) -> None:
        self.source = source

    def read(self, item_id: str) -> Flags | None:
        """The flags of one item, or None if it does not exist."""
        raise NotImplementedError

    def write(self, item_id: str, *, favorite: bool | None, show_on_dashboard: bool | None) -> Flags | None:
        """Change the flags given and return the item's new flags, or None if unknown."""
        raise NotImplementedError

    def items(self) -> dict[str, Flags]:
        """The flags of every item of this kind."""
        return {}


class _ProfileVisibility(_VisibilityAdapter):
    """Profiles keep both flags on the profile (``Profile.favorite``)."""

    def read(self, item_id: str) -> Flags | None:
        if self.source is None:
            return None
        profile = self.source.get_profile(item_id)
        return None if profile is None else _flags(profile.favorite, profile.dashboard_visible)

    def write(self, item_id: str, *, favorite: bool | None, show_on_dashboard: bool | None) -> Flags | None:
        if self.source is None:
            return None
        updated = self.source.update_profile(item_id, favorite=favorite, dashboard_visible=show_on_dashboard)
        return None if updated is None else self.read(item_id)

    def items(self) -> dict[str, Flags]:
        if self.source is None:
            return {}
        return {
            profile_id: _flags(profile.favorite, profile.dashboard_visible)
            for profile_id, profile in self.source.get_profiles_map().items()
        }


class _SceneVisibility(_VisibilityAdapter):
    """Scenes keep both flags on the scene (``Scene.favorite``)."""

    def read(self, item_id: str) -> Flags | None:
        if self.source is None:
            return None
        scene = self.source.get_scene(item_id)
        return None if scene is None else _flags(scene.favorite, scene.dashboard_visible)

    def write(self, item_id: str, *, favorite: bool | None, show_on_dashboard: bool | None) -> Flags | None:
        if self.source is None:
            return None
        scene, error = self.source.update_scene(
            item_id, favorite=favorite, dashboard_visible=show_on_dashboard
        )
        if scene is None or error:
            _LOG.warning("Scene '%s' rejected a visibility change: %s", item_id, error or "not found")
            return None
        return self.read(item_id)

    def items(self) -> dict[str, Flags]:
        if self.source is None:
            return {}
        return {scene.id: _flags(scene.favorite, scene.dashboard_visible) for scene in self.source.list_scenes()}


class _MacroVisibility(_VisibilityAdapter):
    """CEC macros keep both flags on the macro (``CecMacro.favorite``)."""

    def read(self, item_id: str) -> Flags | None:
        if self.source is None:
            return None
        macro = self.source.get_macro(item_id)
        return None if macro is None else _flags(macro.favorite, macro.dashboard_visible)

    def write(self, item_id: str, *, favorite: bool | None, show_on_dashboard: bool | None) -> Flags | None:
        if self.source is None:
            return None
        updated = self.source.update_macro(item_id, favorite=favorite, dashboard_visible=show_on_dashboard)
        return None if updated is None else self.read(item_id)

    def items(self) -> dict[str, Flags]:
        if self.source is None:
            return {}
        flags: dict[str, Flags] = {}
        for summary in self.source.list_macros():
            item_flags = self.read(str(summary.get("id", "")))
            if item_flags is not None:
                flags[str(summary["id"])] = item_flags
        return flags


class _ShortcutVisibility(_VisibilityAdapter):
    """Shortcuts keep both flags in the manager's preferences (built-in or user)."""

    def read(self, item_id: str) -> Flags | None:
        if self.source is None:
            return None
        shortcut = self.source.get(item_id)
        return None if shortcut is None else _flags(shortcut.favorite, shortcut.dashboard_visible)

    def write(self, item_id: str, *, favorite: bool | None, show_on_dashboard: bool | None) -> Flags | None:
        if self.source is None:
            return None
        saved = self.source.update_prefs(item_id, favorite=favorite, dashboard_visible=show_on_dashboard)
        return self.read(item_id) if saved else None

    def items(self) -> dict[str, Flags]:
        if self.source is None:
            return {}
        return {shortcut.key: _flags(shortcut.favorite, shortcut.dashboard_visible)
                for shortcut in self.source.list_shortcuts()}


class _PresetVisibility(_VisibilityAdapter):
    """
    The eight hardware preset slots, whose flags are two lists in the device
    settings: they are matrix slots, not items the hub can add fields to.
    """

    @staticmethod
    def _number(item_id: str) -> int | None:
        try:
            number = int(str(item_id).strip())
        except (TypeError, ValueError):
            return None
        return number if number in PRESET_SLOTS else None

    def _lists(self) -> tuple[set[int], set[int]]:
        return set(self.source.get_favorite_presets()), set(self.source.get_dashboard_presets())

    def read(self, item_id: str) -> Flags | None:
        number = self._number(item_id)
        if number is None or self.source is None:
            return None
        favorites, dashboard = self._lists()
        return _flags(number in favorites, number in dashboard)

    def write(self, item_id: str, *, favorite: bool | None, show_on_dashboard: bool | None) -> Flags | None:
        number = self._number(item_id)
        if number is None or self.source is None:
            return None
        favorites, dashboard = self._lists()
        if favorite is not None:
            favorites.add(number) if favorite else favorites.discard(number)
            self.source.set_favorite_presets(sorted(favorites))
        if show_on_dashboard is not None:
            dashboard.add(number) if show_on_dashboard else dashboard.discard(number)
            self.source.set_dashboard_presets(sorted(dashboard))
        return self.read(item_id)

    def items(self) -> dict[str, Flags]:
        if self.source is None:
            return {}
        favorites, dashboard = self._lists()
        return {str(number): _flags(number in favorites, number in dashboard) for number in PRESET_SLOTS}
