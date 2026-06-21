"""
System Actions — built-in matrix operations exposed as scene steps.

SystemActions are NOT stored as entities. Their definitions are here;
user preferences (label, icon, order, enabled) are stored in
``system_actions.json`` in the data directory.

Action Keys
===========

Routing templates:
  route_all_to_output    — requires param: output (1-8)
  route_one_to_one       — no params
  power_off_all          — no params
  mute_all_audio         — no params
  unmute_all_audio       — no params

System settings:
  beep_on / beep_off
  panel_lock_on / panel_lock_off
  lcd_timeout_<mode>    — mode: off, 10s, 30s, 60s, always_on
  system_reboot

Hardware presets:
  preset_recall_<n>     — n: 1-8
"""

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from persistence import ensure_data_dir, get_data_dir

_LOG = logging.getLogger("system_actions")

_PREFS_FILE = "system_actions.json"


# =============================================================================
# Default definitions
# =============================================================================

#: LCD timeout mode constants (from orei_matrix.py)
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
class SystemAction:
    """
    A single executable matrix operation.

    :param key: Stable identifier, e.g. ``"mute_all_audio"``
    :param label: User-facing display name (user-editable)
    :param icon: Emoji for display (user-editable)
    :param enabled: Whether the action is active (user-editable)
    :param order: Sort order within the action list (user-editable)
    :param builtin: True — SystemActions are never user-created
    :param category: Grouping for display purposes
    """
    key: str
    label: str
    icon: str
    enabled: bool = True
    order: int = 0
    builtin: bool = True
    category: str = "routing"

    # Tunable params for actions that need them (e.g. route_all_to_output needs `output`)
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "icon": self.icon,
            "enabled": self.enabled,
            "order": self.order,
            "category": self.category,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SystemAction":
        return SystemAction(
            key=data["key"],
            label=data.get("label", data["key"]),
            icon=data.get("icon", "⚡"),
            enabled=bool(data.get("enabled", True)),
            order=int(data.get("order", 0)),
            category=data.get("category", "routing"),
        )


def _default_actions() -> list[SystemAction]:
    """Return the full set of built-in SystemActions."""
    return [
        # Routing templates
        SystemAction(key="route_all_to_output", label="All → Out 1", icon="🎯",
                     category="routing", order=0),
        SystemAction(key="route_one_to_one", label="1:1 Mapping", icon="🔁",
                     category="routing", order=1),
        SystemAction(key="power_off_all", label="Power Off All", icon="⏻",
                     category="routing", order=2),
        SystemAction(key="mute_all_audio", label="Mute All Audio", icon="🔇",
                     category="routing", order=3),
        SystemAction(key="unmute_all_audio", label="Unmute All Audio", icon="🔊",
                     category="routing", order=4),
        # Hardware presets
        SystemAction(key="preset_recall_1", label="Preset 1", icon="1️⃣",
                     category="presets", order=10),
        SystemAction(key="preset_recall_2", label="Preset 2", icon="2️⃣",
                     category="presets", order=11),
        SystemAction(key="preset_recall_3", label="Preset 3", icon="3️⃣",
                     category="presets", order=12),
        SystemAction(key="preset_recall_4", label="Preset 4", icon="4️⃣",
                     category="presets", order=13),
        SystemAction(key="preset_recall_5", label="Preset 5", icon="5️⃣",
                     category="presets", order=14),
        SystemAction(key="preset_recall_6", label="Preset 6", icon="6️⃣",
                     category="presets", order=15),
        SystemAction(key="preset_recall_7", label="Preset 7", icon="7️⃣",
                     category="presets", order=16),
        SystemAction(key="preset_recall_8", label="Preset 8", icon="8️⃣",
                     category="presets", order=17),
        # System settings
        SystemAction(key="beep_on", label="Beep On", icon="🔔",
                     category="system", order=20),
        SystemAction(key="beep_off", label="Beep Off", icon="🔕",
                     category="system", order=21),
        SystemAction(key="panel_lock_on", label="Panel Lock On", icon="🔒",
                     category="system", order=22),
        SystemAction(key="panel_lock_off", label="Panel Lock Off", icon="🔓",
                     category="system", order=23),
        SystemAction(key="system_reboot", label="Reboot Matrix", icon="🔄",
                     category="system", order=24),
        # LCD timeout sub-actions (each mode as its own action for clarity)
        SystemAction(key="lcd_timeout_off", label="LCD: Off", icon="🖥️",
                     category="system", order=25),
        SystemAction(key="lcd_timeout_10s", label="LCD: 10s", icon="🖥️",
                     category="system", order=26),
        SystemAction(key="lcd_timeout_30s", label="LCD: 30s", icon="🖥️",
                     category="system", order=27),
        SystemAction(key="lcd_timeout_60s", label="LCD: 60s", icon="🖥️",
                     category="system", order=28),
        SystemAction(key="lcd_timeout_always_on", label="LCD: Always On", icon="🖥️",
                     category="system", order=29),
    ]


# =============================================================================
# Preferences manager
# =============================================================================

@dataclass
class _ActionPrefs:
    """User-editable preferences for a single SystemAction."""
    label: str
    icon: str
    enabled: bool
    order: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "icon": self.icon,
            "enabled": self.enabled,
            "order": self.order,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "_ActionPrefs":
        return _ActionPrefs(
            label=data.get("label", ""),
            icon=data.get("icon", "⚡"),
            enabled=bool(data.get("enabled", True)),
            order=int(data.get("order", 0)),
        )


class SystemActionManager:
    """
    Manages SystemAction user preferences (label, icon, order, enabled).

    The action definitions themselves are hardcoded; only the preferences
    are persisted to ``system_actions.json``.
    """

    def __init__(self, data_dir: Path | None = None):
        if data_dir is None:
            data_dir = get_data_dir()
        self.data_dir = Path(data_dir).resolve()
        self.prefs_path = self.data_dir / _PREFS_FILE
        self._prefs: dict[str, _ActionPrefs] = {}
        self._defaults: dict[str, SystemAction] = {a.key: a for a in _default_actions()}
        self._ensure_loaded()

    def _ensure_loaded(self) -> None:
        if self.prefs_path.exists():
            try:
                with open(self.prefs_path, encoding="utf-8") as f:
                    raw: dict[str, Any] = json.load(f)
                for key, data in raw.items():
                    if key in self._defaults:
                        self._prefs[key] = _ActionPrefs.from_dict(data)
                _LOG.debug("Loaded system action prefs from %s", self.prefs_path)
            except Exception as e:
                _LOG.error("Error loading system action prefs: %s", e)
        else:
            # First run — seed with defaults and save
            self._save()

    def _save(self) -> bool:
        try:
            ensure_data_dir(self.data_dir)
            raw = {key: prefs.to_dict() for key, prefs in self._prefs.items()}
            with open(self.prefs_path, "w", encoding="utf-8") as f:
                json.dump(raw, f, indent=2)
            return True
        except Exception as e:
            _LOG.error("Error saving system action prefs: %s", e)
            return False

    def list_actions(self) -> list[SystemAction]:
        """Return all actions with user preferences applied."""
        result = []
        for key, default in self._defaults.items():
            prefs = self._prefs.get(key)
            if prefs:
                action = SystemAction(
                    key=key,
                    label=prefs.label,
                    icon=prefs.icon,
                    enabled=prefs.enabled,
                    order=prefs.order,
                    category=default.category,
                )
            else:
                action = default
            result.append(action)
        result.sort(key=lambda a: a.order)
        return result

    def get_action(self, key: str) -> SystemAction | None:
        """Return a single action by key, or None."""
        default = self._defaults.get(key)
        if default is None:
            return None
        prefs = self._prefs.get(key)
        if prefs:
            return SystemAction(
                key=key,
                label=prefs.label,
                icon=prefs.icon,
                enabled=prefs.enabled,
                order=prefs.order,
                category=default.category,
            )
        return default

    def update_prefs(
        self,
        key: str,
        label: str | None = None,
        icon: str | None = None,
        enabled: bool | None = None,
        order: int | None = None,
    ) -> bool:
        """
        Update editable preferences for an action.

        Returns True on success, False if the key is not a valid action.
        """
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
        else:
            d = self._defaults[key]
            self._prefs[key] = _ActionPrefs(
                label=label if label is not None else d.label,
                icon=icon if icon is not None else d.icon,
                enabled=enabled if enabled is not None else d.enabled,
                order=order if order is not None else d.order,
            )
        return self._save()


# =============================================================================
# Executor
# =============================================================================

async def execute_action(
    action: SystemAction,
    matrix_device,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Execute a SystemAction against the matrix device.

    :param action: The SystemAction to execute
    :param matrix_device: OreiMatrix instance
    :param params: Runtime params (e.g. ``{"output": 1}`` for ``route_all_to_output``)
    :returns: Result dict ``{"success": bool, "detail": str}``
    """
    merged_params = {**action.params, **(params or {})}
    key = action.key

    try:
        # Routing templates
        if key == "route_all_to_output":
            output = int(merged_params.get("output", 1))
            # Route input 1 to the specified output (the "selected input" concept
            # from the old shortcut — we use input 1 as the default)
            routing_input = int(merged_params.get("input", 1))
            await matrix_device.switch(routing_input, output)
            return {"success": True, "detail": f"Routed Input {routing_input} → Output {output}"}

        if key == "route_one_to_one":
            for n in range(1, 9):
                await matrix_device.switch(n, n)
            return {"success": True, "detail": "1:1 mapping applied"}

        if key == "power_off_all":
            for n in range(1, 9):
                await matrix_device.power_off()
            return {"success": True, "detail": "All outputs powered off"}

        if key == "mute_all_audio":
            for n in range(1, 9):
                await matrix_device.set_output_audio_mute(n, True)
            return {"success": True, "detail": "All audio muted"}

        if key == "unmute_all_audio":
            for n in range(1, 9):
                await matrix_device.set_output_audio_mute(n, False)
            return {"success": True, "detail": "All audio unmuted"}

        # Hardware presets
        if key.startswith("preset_recall_"):
            preset_num = int(key.split("_")[-1])
            await matrix_device.recall_preset(preset_num)
            return {"success": True, "detail": f"Preset {preset_num} recalled"}

        # System settings
        if key == "beep_on":
            await matrix_device.set_beep(True)
            return {"success": True, "detail": "Beep enabled"}

        if key == "beep_off":
            await matrix_device.set_beep(False)
            return {"success": True, "detail": "Beep disabled"}

        if key == "panel_lock_on":
            await matrix_device.set_panel_lock(True)
            return {"success": True, "detail": "Panel locked"}

        if key == "panel_lock_off":
            await matrix_device.set_panel_lock(False)
            return {"success": True, "detail": "Panel unlocked"}

        if key == "system_reboot":
            await matrix_device.system_reboot()
            return {"success": True, "detail": "Matrix rebooting"}

        # LCD timeout
        if key.startswith("lcd_timeout_"):
            mode_name = key.split("_", 2)[-1]  # e.g. "off", "10s", "always_on"
            mode = LCD_TIMEOUT_MODES.get(mode_name)
            if mode is None:
                return {"success": False, "detail": f"Unknown LCD mode: {mode_name}"}
            await matrix_device.set_lcd_timeout(mode)
            return {"success": True, "detail": f" LCD timeout set to {mode_name}"}

        return {"success": False, "detail": f"Unknown action key: {key}"}

    except Exception as exc:
        _LOG.error("System action %s failed: %s", key, exc)
        return {"success": False, "detail": str(exc)}
