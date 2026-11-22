"""Construct exactly one manager bundle after the persistence barrier."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cec_macros import MacroManager
    from config import ProfileManager
    from dashboard_layout import DashboardLayoutManager
    from hub.persistence.startup import PreparedPersistence
    from scene_manager import SceneManager
    from system_shortcuts import SystemShortcutManager


@dataclass
class RuntimeManagers:
    profiles: ProfileManager
    scenes: SceneManager
    macros: MacroManager
    shortcuts: SystemShortcutManager
    dashboard: DashboardLayoutManager


def create_managers(prepared: PreparedPersistence) -> RuntimeManagers:
    from cec_macros import MacroManager
    from config import ProfileManager
    from dashboard_layout import DashboardLayoutManager
    from scene_manager import SceneManager
    from system_shortcuts import SystemShortcutManager

    return RuntimeManagers(
        ProfileManager(str(prepared.paths.config_dir)),
        SceneManager(prepared.paths.data_dir),
        MacroManager(str(prepared.paths.config_dir)),
        SystemShortcutManager(prepared.paths.data_dir),
        DashboardLayoutManager(prepared.paths.data_dir),
    )
