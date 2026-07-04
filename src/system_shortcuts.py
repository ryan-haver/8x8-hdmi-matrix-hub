"""
System Shortcuts - Built-in quick routing and system actions that ship with the integration.

Unifies Phase 7 shortcuts and Phase 8 system actions.
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from persistence import ensure_data_dir, get_data_dir

_LOG = logging.getLogger("system_shortcuts")

_PREFS_FILE = "system_shortcuts.json"

# LCD timeout mode constants (from orei_matrix.py)
LCD_TIMEOUT_OFF = 0
LCD_TIMEOUT_10S = 1
LCD_TIMEOUT_30S = 2
LCD_TIMEOUT_60S = 3
LCD_TIMEOUT_ALWAYS_ON = 4

LCD_TIMEOUT_MODES = {
    "off": LCD_TIMEOUT_OFF,
    "10s": LCD_TIMEOUT_10S,
    "30s": LCD_TIMEOUT_30S,
    "60s": LCD_TIMEOUT_60S,
    "always_on": LCD_TIMEOUT_ALWAYS_ON,
}


@dataclass
class SystemShortcut:
    """
    A single executable matrix operation or shortcut.

    :param key: Stable identifier, e.g. ``"mute_all_audio"``
    :param label: User-facing display name (user-editable)
    :param icon: Emoji for display (user-editable)
    :param enabled: Whether the shortcut is active (user-editable)
    :param order: Sort order within lists (user-editable)
    :param builtin: True — Shortcuts are currently all built-in
    :param category: Grouping for display purposes ("routing", "presets", "system")
    :param favorite: True to show in Quick Actions favorite drawer
    :param dashboard_visible: True to render as card on Dashboard
    :param params: Optional parameters for execution
    :param type: Type of operation (defaults to key)
    """

    key: str
    label: str
    icon: str
    enabled: bool = True
    order: int = 0
    builtin: bool = True
    category: str = "routing"
    favorite: bool = False
    dashboard_visible: bool = False
    params: dict[str, Any] = field(default_factory=dict)
    type: str = ""

    def __post_init__(self):
        if not self.type:
            self.type = self.key

    def to_dict(self) -> dict[str, Any]:
        dct_id = self.key
        if self.builtin:
            legacy_key = self.key
            if legacy_key == "route_all_to_output":
                legacy_key = "all_to_out_1"
            elif legacy_key == "route_one_to_one":
                legacy_key = "one_to_one"
            dct_id = f"builtin.{legacy_key}"

        return {
            "key": self.key,
            "id": dct_id,  # Alias id to key with builtin. prefix for Phase 7 compatibility
            "name": self.label,  # Alias name to label for Phase 7 compatibility
            "label": self.label,
            "icon": self.icon,
            "enabled": self.enabled,
            "order": self.order,
            "category": self.category,
            "favorite": self.favorite,
            "dashboard_visible": self.dashboard_visible,
            "builtin": self.builtin,
            "params": self.params,
            "type": self.type,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SystemShortcut":
        # Handle backward compat fields from old system_shortcuts.json
        key = data.get("key") or data.get("id") or ""
        if key.startswith("builtin."):
            key = key.replace("builtin.", "")
        if key == "all_to_out_1":
            key = "route_all_to_output"
        elif key == "one_to_one":
            key = "route_one_to_one"
        label = data.get("label") or data.get("name") or key
        return SystemShortcut(
            key=key,
            label=label,
            icon=data.get("icon", "⚡"),
            enabled=bool(data.get("enabled", True)),
            order=int(data.get("order", 0)),
            category=data.get("category", "routing"),
            favorite=bool(data.get("favorite", False)),
            dashboard_visible=bool(data.get("dashboard_visible", False)),
            builtin=bool(data.get("builtin", True)),
            params=dict(data.get("params", {})),
            type=data.get("type", ""),
        )


def _default_shortcuts() -> list[SystemShortcut]:
    """Return the default set of built-in shortcuts."""
    return [
        # Routing templates
        SystemShortcut(
            key="route_all_to_output",
            label="All → Out 1",
            icon="🎯",
            category="routing",
            order=0,
            favorite=True,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="route_one_to_one",
            label="1:1 Mapping",
            icon="🔁",
            category="routing",
            order=1,
            favorite=True,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="power_off_all",
            label="Power Off All",
            icon="⏻",
            category="routing",
            order=2,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="mute_all_audio",
            label="Mute All Audio",
            icon="🔇",
            category="routing",
            order=3,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="unmute_all_audio",
            label="Unmute All Audio",
            icon="🔊",
            category="routing",
            order=4,
            favorite=False,
            dashboard_visible=False,
        ),
        # Hardware presets
        SystemShortcut(
            key="preset_recall_1",
            label="Preset 1",
            icon="1️⃣",
            category="presets",
            order=10,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="preset_recall_2",
            label="Preset 2",
            icon="2️⃣",
            category="presets",
            order=11,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="preset_recall_3",
            label="Preset 3",
            icon="3️⃣",
            category="presets",
            order=12,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="preset_recall_4",
            label="Preset 4",
            icon="4️⃣",
            category="presets",
            order=13,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="preset_recall_5",
            label="Preset 5",
            icon="5️⃣",
            category="presets",
            order=14,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="preset_recall_6",
            label="Preset 6",
            icon="6️⃣",
            category="presets",
            order=15,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="preset_recall_7",
            label="Preset 7",
            icon="7️⃣",
            category="presets",
            order=16,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="preset_recall_8",
            label="Preset 8",
            icon="8️⃣",
            category="presets",
            order=17,
            favorite=False,
            dashboard_visible=False,
        ),
        # System settings
        SystemShortcut(
            key="beep_on",
            label="Beep On",
            icon="🔔",
            category="system",
            order=20,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="beep_off",
            label="Beep Off",
            icon="🔕",
            category="system",
            order=21,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="panel_lock_on",
            label="Panel Lock On",
            icon="🔒",
            category="system",
            order=22,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="panel_lock_off",
            label="Panel Lock Off",
            icon="🔓",
            category="system",
            order=23,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="system_reboot",
            label="Reboot Matrix",
            icon="🔄",
            category="system",
            order=24,
            favorite=False,
            dashboard_visible=False,
        ),
        # LCD timeout sub-actions
        SystemShortcut(
            key="lcd_timeout_off",
            label="LCD: Off",
            icon="🖥️",
            category="system",
            order=25,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="lcd_timeout_10s",
            label="LCD: 10s",
            icon="🖥️",
            category="system",
            order=26,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="lcd_timeout_30s",
            label="LCD: 30s",
            icon="🖥️",
            category="system",
            order=27,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="lcd_timeout_60s",
            label="LCD: 60s",
            icon="🖥️",
            category="system",
            order=28,
            favorite=False,
            dashboard_visible=False,
        ),
        SystemShortcut(
            key="lcd_timeout_always_on",
            label="LCD: Always On",
            icon="🖥️",
            category="system",
            order=29,
            favorite=False,
            dashboard_visible=False,
        ),
    ]


@dataclass
class _ShortcutPrefs:
    """User-editable preferences for a single SystemShortcut."""

    label: str
    icon: str
    enabled: bool
    order: int
    favorite: bool = False
    dashboard_visible: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "icon": self.icon,
            "enabled": self.enabled,
            "order": self.order,
            "favorite": self.favorite,
            "dashboard_visible": self.dashboard_visible,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "_ShortcutPrefs":
        # Handle backward compatibility from old system_shortcuts.json
        label = data.get("label") or data.get("name") or ""
        return _ShortcutPrefs(
            label=label,
            icon=data.get("icon", "⚡"),
            enabled=bool(data.get("enabled", True)),
            order=int(data.get("order", 0)),
            favorite=bool(data.get("favorite", False)),
            dashboard_visible=bool(data.get("dashboard_visible", False)),
        )


def _normalize_key(key: str) -> str:
    if key.startswith("builtin."):
        key = key.replace("builtin.", "")
    if key == "all_to_out_1":
        return "route_all_to_output"
    if key == "one_to_one":
        return "route_one_to_one"
    return key


class SystemShortcutManager:
    """
    Manages SystemShortcut user preferences (label, icon, order, enabled, favorite, dashboard_visible).
    """

    def __init__(self, data_dir: Path | None = None):
        if data_dir is None:
            data_dir = get_data_dir()
        self.data_dir = Path(data_dir).resolve()
        self.prefs_path = self.data_dir / _PREFS_FILE
        self._prefs: dict[str, _ShortcutPrefs] = {}
        self._user_shortcuts: dict[str, SystemShortcut] = {}
        self._defaults: dict[str, SystemShortcut] = {s.key: s for s in _default_shortcuts()}
        self._ensure_loaded()

    def _ensure_loaded(self) -> None:
        if self.prefs_path.exists():
            try:
                with open(self.prefs_path, encoding="utf-8") as f:
                    raw: dict[str, Any] = json.load(f)

                # Handle old list-based system_shortcuts.json migration
                if isinstance(raw, list):
                    _LOG.info("Migrating legacy list-based system shortcuts file")
                    for item in raw:
                        key = item.get("id") or item.get("key")
                        if key:
                            # Map old shortcut types to new category/key if necessary
                            # but mostly we preserve what aligns
                            if key.startswith("builtin."):
                                key = key.replace("builtin.", "")
                            if key in self._defaults:
                                self._prefs[key] = _ShortcutPrefs.from_dict(item)
                            elif key.startswith("user."):
                                self._user_shortcuts[key] = SystemShortcut.from_dict(item)
                else:
                    for key, data in raw.items():
                        if key in self._defaults:
                            self._prefs[key] = _ShortcutPrefs.from_dict(data)
                        elif key.startswith("user."):
                            self._user_shortcuts[key] = SystemShortcut.from_dict(data)
                _LOG.debug("Loaded system shortcut prefs from %s", self.prefs_path)
            except Exception as e:
                _LOG.error("Error loading system shortcut prefs: %s", e)
        else:
            # Seed default preferences on first run
            for key, default in self._defaults.items():
                self._prefs[key] = _ShortcutPrefs(
                    label=default.label,
                    icon=default.icon,
                    enabled=default.enabled,
                    order=default.order,
                    favorite=default.favorite,
                    dashboard_visible=default.dashboard_visible,
                )
            self._save()

    def _save(self) -> bool:
        try:
            ensure_data_dir(self.data_dir)
            raw = {}
            for key, prefs in self._prefs.items():
                raw[key] = prefs.to_dict()
            for key, us in self._user_shortcuts.items():
                raw[key] = us.to_dict()
            from _file_io import atomic_write_json
            atomic_write_json(self.prefs_path, raw)
            return True
        except Exception as e:
            _LOG.error("Error saving system shortcut prefs: %s", e)
            return False

    def list_shortcuts(self, enabled_only: bool = False, include_builtin: bool = True) -> list[SystemShortcut]:
        """Return all shortcuts with user preferences applied."""
        result = []
        if include_builtin:
            for key, default in self._defaults.items():
                prefs = self._prefs.get(key)
                if prefs:
                    shortcut = SystemShortcut(
                        key=key,
                        label=prefs.label,
                        icon=prefs.icon,
                        enabled=prefs.enabled,
                        order=prefs.order,
                        category=default.category,
                        favorite=prefs.favorite,
                        dashboard_visible=prefs.dashboard_visible,
                        type=default.type,
                        params=default.params,
                    )
                else:
                    shortcut = default

                if enabled_only and not shortcut.enabled:
                    continue

                result.append(shortcut)

        for key, us in self._user_shortcuts.items():
            if enabled_only and not us.enabled:
                continue
            result.append(us)

        result.sort(key=lambda s: s.order)
        return result

    # Phase 8 system action compatibility
    def list_actions(self) -> list[SystemShortcut]:
        return self.list_shortcuts()

    def get_action(self, key: str) -> SystemShortcut | None:
        return self.get(key)

    def update_prefs(
        self,
        key: str,
        label: str | None = None,
        icon: str | None = None,
        enabled: bool | None = None,
        order: int | None = None,
        favorite: bool | None = None,
        dashboard_visible: bool | None = None,
    ) -> bool:
        key = _normalize_key(key)
        if key.startswith("user."):
            us = self._user_shortcuts.get(key)
            if not us:
                return False
            if label is not None:
                us.label = label
            if icon is not None:
                us.icon = icon
            if enabled is not None:
                us.enabled = enabled
            if order is not None:
                us.order = order
            if favorite is not None:
                us.favorite = favorite
            if dashboard_visible is not None:
                us.dashboard_visible = dashboard_visible
            return self._save()

        if key not in self._defaults:
            return False
        existing = self._prefs.get(key)
        if existing:
            if label is not None:
                existing.label = label
            if icon is not None:
                existing.icon = icon
            if enabled is not None:
                existing.enabled = enabled
            if order is not None:
                existing.order = order
            if favorite is not None:
                existing.favorite = favorite
            if dashboard_visible is not None:
                existing.dashboard_visible = dashboard_visible
        else:
            d = self._defaults[key]
            self._prefs[key] = _ShortcutPrefs(
                label=label if label is not None else d.label,
                icon=icon if icon is not None else d.icon,
                enabled=enabled if enabled is not None else d.enabled,
                order=order if order is not None else d.order,
                favorite=favorite if favorite is not None else d.favorite,
                dashboard_visible=dashboard_visible if dashboard_visible is not None else d.dashboard_visible,
            )
        return self._save()

    def get(self, key: str) -> SystemShortcut | None:
        """Return a single shortcut by key, or None."""
        key = _normalize_key(key)
        if key.startswith("user."):
            return self._user_shortcuts.get(key)
        default = self._defaults.get(key)
        if default is None:
            return None
        prefs = self._prefs.get(key)
        if prefs:
            return SystemShortcut(
                key=key,
                label=prefs.label,
                icon=prefs.icon,
                enabled=prefs.enabled,
                order=prefs.order,
                category=default.category,
                favorite=prefs.favorite,
                dashboard_visible=prefs.dashboard_visible,
                type=default.type,
                params=default.params,
            )
        return default

    def list_favorites(self) -> list[SystemShortcut]:
        return [s for s in self.list_shortcuts() if s.favorite and s.enabled]

    def list_dashboard(self) -> list[SystemShortcut]:
        return [s for s in self.list_shortcuts() if s.dashboard_visible and s.enabled]

    def toggle_favorite(self, key: str) -> bool:
        key = _normalize_key(key)
        if key.startswith("user."):
            us = self._user_shortcuts.get(key)
            if us:
                us.favorite = not us.favorite
                self._save()
                return us.favorite
            return False
        existing = self._prefs.get(key)
        if existing:
            existing.favorite = not existing.favorite
            self._save()
            return existing.favorite
        return False

    def toggle_dashboard_visible(self, key: str) -> bool:
        key = _normalize_key(key)
        if key.startswith("user."):
            us = self._user_shortcuts.get(key)
            if us:
                us.dashboard_visible = not us.dashboard_visible
                self._save()
                return us.dashboard_visible
            return False
        existing = self._prefs.get(key)
        if existing:
            existing.dashboard_visible = not existing.dashboard_visible
            self._save()
            return existing.dashboard_visible
        return False

    def add_user_shortcut(
        self,
        name: str,
        icon: str,
        type: str,
        params: dict[str, Any] | None = None,
    ) -> SystemShortcut | None:
        VALID_TYPES = {
            "route_all_to_output",
            "route_one_to_one",
            "power_off_all",
            "mute_all_audio",
            "unmute_all_audio",
        }
        if type not in VALID_TYPES:
            return None
        name = name.strip()
        if not name:
            return None
        key = f"user.{uuid.uuid4().hex[:12]}"
        us = SystemShortcut(
            key=key,
            label=name,
            icon=icon or "⚡",
            type=type,
            params=dict(params or {}),
            enabled=True,
            builtin=False,
            favorite=False,
            dashboard_visible=False,
            order=len(self._defaults) + len(self._user_shortcuts),
        )
        self._user_shortcuts[key] = us
        if self._save():
            return us
        return None

    def delete(self, key: str) -> bool:
        key = _normalize_key(key)
        if not key.startswith("user."):
            return False
        if key in self._user_shortcuts:
            del self._user_shortcuts[key]
            return self._save()
        return False

    def reorder(self, ordered_keys: list[str]) -> bool:
        for index, raw_key in enumerate(ordered_keys):
            key = _normalize_key(raw_key)
            if key.startswith("user."):
                if key in self._user_shortcuts:
                    self._user_shortcuts[key].order = index
            elif key in self._prefs:
                self._prefs[key].order = index
        return self._save()


# =============================================================================
# Executor
# =============================================================================


async def execute_shortcut(
    shortcut: SystemShortcut,
    matrix_device,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute a SystemShortcut against the matrix device.
    """
    merged_params = {**shortcut.params, **(params or {})}
    key = shortcut.key
    stype = shortcut.type

    try:
        # Routing templates
        if stype == "route_all_to_output":
            output = int(merged_params.get("output", 1))
            routing_input = int(merged_params.get("input", 1))
            await matrix_device.switch(routing_input, output)
            return {"success": True, "detail": f"Routed Input {routing_input} → Output {output}", "type": stype}

        if stype == "route_one_to_one":
            for n in range(1, 9):
                await matrix_device.switch(n, n)
            return {"success": True, "detail": "1:1 mapping applied", "type": stype}

        if stype == "power_off_all":
            for n in range(1, 9):
                await matrix_device.power_off()
            return {"success": True, "detail": "All outputs powered off", "type": stype}

        if stype == "mute_all_audio":
            for n in range(1, 9):
                await matrix_device.set_output_audio_mute(n, True)
            return {"success": True, "detail": "All audio muted", "type": stype}

        if stype == "unmute_all_audio":
            for n in range(1, 9):
                await matrix_device.set_output_audio_mute(n, False)
            return {"success": True, "detail": "All audio unmuted", "type": stype}

        # Hardware presets
        if stype.startswith("preset_recall_"):
            preset_num = int(stype.split("_")[-1])
            await matrix_device.recall_preset(preset_num)
            return {"success": True, "detail": f"Preset {preset_num} recalled", "type": stype}

        # System settings
        if stype == "beep_on":
            await matrix_device.set_beep(True)
            return {"success": True, "detail": "Beep enabled", "type": stype}

        if stype == "beep_off":
            await matrix_device.set_beep(False)
            return {"success": True, "detail": "Beep disabled", "type": stype}

        if stype == "panel_lock_on":
            await matrix_device.set_panel_lock(True)
            return {"success": True, "detail": "Panel locked", "type": stype}

        if stype == "panel_lock_off":
            await matrix_device.set_panel_lock(False)
            return {"success": True, "detail": "Panel unlocked", "type": stype}

        if stype == "system_reboot":
            await matrix_device.system_reboot()
            return {"success": True, "detail": "Matrix rebooting", "type": stype}

        # LCD timeout
        if stype.startswith("lcd_timeout_"):
            mode_name = stype.split("_", 2)[-1]  # e.g. "off", "10s"
            mode = LCD_TIMEOUT_MODES.get(mode_name)
            if mode is None:
                return {"success": False, "detail": f"Unknown LCD mode: {mode_name}", "type": stype}
            await matrix_device.set_lcd_timeout(mode)
            return {"success": True, "detail": f"LCD timeout set to {mode_name}", "type": stype}

        return {"success": False, "detail": f"Unknown shortcut key: {key}", "type": stype}

    except Exception as exc:
        _LOG.error("System shortcut %s failed: %s", key, exc)
        return {"success": False, "detail": str(exc), "type": stype}


# Phase 8 compatibility aliases
SystemAction = SystemShortcut
SystemActionManager = SystemShortcutManager
execute_action = execute_shortcut
