"""
Phase 8 Scene Manager — ordered grouping of Profiles and System Actions.

A Scene is a named automation that executes a sequence of Profiles and
System Actions in order. Scenes can be pinned to the dashboard as cards.

Data model:
  - scenes.json  — list of Scene objects
  - profiles.json — Profile objects (unchanged, from config.py)

Unlike the old Phase 7 SceneManager (config.SceneManager), this module
defines the NEW unified Scene concept for Phase 8.
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from password import PasswordError, hash_passcode, needs_passcode, verify_passcode
from persistence import ensure_data_dir, get_data_dir

_LOG = logging.getLogger("scene_manager")

_SCENES_FILE = "scenes.json"

#: 7-day execution history retention
_HISTORY_RETENTION = timedelta(days=7)

#: Valid step types
STEP_TYPE_PROFILE = "profile"
STEP_TYPE_SYSTEM_ACTION = "system_action"
STEP_TYPE_MACRO = "macro"
VALID_STEP_TYPES = frozenset({STEP_TYPE_PROFILE, STEP_TYPE_SYSTEM_ACTION, STEP_TYPE_MACRO})

#: Settings keys that can be overridden per-scene
OVERRIDABLE_SETTINGS = frozenset(
    {
        "input",
        "enabled",
        "hdcp",
        "hdr",
        "scaler",
        "arc",
        "audio_mute",
    }
)


# =============================================================================
# Data classes
# =============================================================================


@dataclass
class SceneStep:
    """
    A single step within a Scene execution plan.

    :param type: One of:
                 - ``"profile"`` — execute a Profile
                 - ``"system_action"`` — execute a SystemAction by key
                 - ``"macro"`` — execute a saved CEC Macro by ID
    :param id: For ``profile`` steps: the Profile ID.
               For ``system_action`` steps: the SystemAction key.
               For ``macro`` steps: the CEC Macro ID.
    :param params: For ``system_action`` steps: runtime params
                   (e.g. ``{"output": 1}`` for route_all_to_output).
    """

    type: str
    id: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"type": self.type, "id": self.id}
        if self.params:
            result["params"] = self.params
        return result

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SceneStep":
        return SceneStep(
            type=data.get("type", STEP_TYPE_PROFILE),
            id=data.get("id", ""),
            params=dict(data.get("params", {})),
        )

    def validate(self) -> str | None:
        """Return None if valid, or an error string if invalid."""
        if self.type not in VALID_STEP_TYPES:
            return f"Invalid step type: {self.type!r}"
        if not self.id:
            return "Step id cannot be empty"
        return None


@dataclass
class ExecutionHistoryEntry:
    """A single execution record in a Scene's or Profile's history."""

    timestamp: str  # ISO 8601
    status: str  # "success" | "error"
    steps_completed: int
    total_steps: int
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "status": self.status,
            "steps_completed": self.steps_completed,
            "total_steps": self.total_steps,
            "error": self.error,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ExecutionHistoryEntry":
        return ExecutionHistoryEntry(
            timestamp=data.get("timestamp", ""),
            status=data.get("status", "error"),
            steps_completed=int(data.get("steps_completed", 0)),
            total_steps=int(data.get("total_steps", 0)),
            error=data.get("error"),
        )


@dataclass
class Scene:
    """
    A named grouping of Profiles and System Actions, executed in order.

    :param id: Stable identifier
    :param name: Display name
    :param icon: Emoji icon
    :param steps: Ordered list of SceneSteps to execute
    :param overrides: Per-profile output setting overrides for this scene
    :param favorite: Show in favorites list
    :param dashboard_visible: Render as card on dashboard
    :param dashboard_order: Position in dashboard grid
    :param password_protected: True if passcode required to execute
    :param passcode_hash: Hashed passcode (empty if not protected)
    :param last_executed: ISO timestamp of last execution
    :param execution_history: List of recent execution records (max 7 days)
    """

    id: str
    name: str
    icon: str = "🎬"
    steps: list[SceneStep] = field(default_factory=list)
    overrides: dict[str, dict[int, dict[str, bool]]] = field(default_factory=dict)
    favorite: bool = False
    dashboard_visible: bool = False
    dashboard_order: int = 0
    password_protected: bool = False
    passcode_hash: str = ""
    last_executed: str | None = None
    execution_history: list[ExecutionHistoryEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "steps": [s.to_dict() for s in self.steps],
            "overrides": {
                pid: {str(out_num): settings for out_num, settings in out_map.items()}
                for pid, out_map in self.overrides.items()
            },
            "favorite": self.favorite,
            "dashboard_visible": self.dashboard_visible,
            "dashboard_order": self.dashboard_order,
            "password_protected": self.password_protected,
            "passcode_hash": self.passcode_hash,
            "last_executed": self.last_executed,
            "execution_history": [e.to_dict() for e in self.execution_history],
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Scene":
        steps = [SceneStep.from_dict(s) for s in data.get("steps", [])]
        overrides_raw: dict[str, dict[str, dict[str, bool]]] = data.get("overrides", {})
        overrides: dict[str, dict[int, dict[str, bool]]] = {}
        for pid, outers in overrides_raw.items():
            out_map: dict[int, dict[str, bool]] = {}
            for out_str, settings in outers.items():
                out_map[int(out_str)] = settings
            overrides[pid] = out_map

        history = [ExecutionHistoryEntry.from_dict(h) for h in data.get("execution_history", [])]

        return Scene(
            id=data.get("id", ""),
            name=data.get("name", "Unnamed Scene"),
            icon=data.get("icon", "🎬"),
            steps=steps,
            overrides=overrides,
            favorite=bool(data.get("favorite", False)),
            dashboard_visible=bool(data.get("dashboard_visible", False)),
            dashboard_order=int(data.get("dashboard_order", 0)),
            password_protected=bool(data.get("password_protected", False)),
            passcode_hash=data.get("passcode_hash", ""),
            last_executed=data.get("last_executed"),
            execution_history=history,
        )

    def add_profile_step(self, profile_id: str) -> None:
        """Append a profile step."""
        self.steps.append(SceneStep(type=STEP_TYPE_PROFILE, id=profile_id))

    def add_system_action_step(self, action_key: str, params: dict[str, Any] | None = None) -> None:
        """Append a system action step."""
        self.steps.append(
            SceneStep(
                type=STEP_TYPE_SYSTEM_ACTION,
                id=action_key,
                params=params or {},
            )
        )

    def add_macro_step(self, macro_id: str, params: dict[str, Any] | None = None) -> None:
        """Append a CEC macro step."""
        self.steps.append(
            SceneStep(
                type=STEP_TYPE_MACRO,
                id=macro_id,
                params=params or {},
            )
        )

    def remove_step(self, index: int) -> bool:
        """Remove step at index. Returns True if removed."""
        if 0 <= index < len(self.steps):
            self.steps.pop(index)
            return True
        return False

    def reorder_steps(self, from_index: int, to_index: int) -> bool:
        """Move step from from_index to to_index."""
        if not (0 <= from_index < len(self.steps) and 0 <= to_index < len(self.steps)):
            return False
        step = self.steps.pop(from_index)
        self.steps.insert(to_index, step)
        return True

    def set_override(self, profile_id: str, output_num: int, setting_key: str, disabled: bool = True) -> None:
        """Set an override for a specific profile's output setting in this scene."""
        if profile_id not in self.overrides:
            self.overrides[profile_id] = {}
        if output_num not in self.overrides[profile_id]:
            self.overrides[profile_id][output_num] = {}
        self.overrides[profile_id][output_num][setting_key] = disabled

    def clear_override(self, profile_id: str, output_num: int, setting_key: str) -> None:
        """Remove a specific override."""
        if (
            profile_id in self.overrides
            and output_num in self.overrides[profile_id]
            and setting_key in self.overrides[profile_id][output_num]
        ):
            del self.overrides[profile_id][output_num][setting_key]
            if not self.overrides[profile_id][output_num]:
                del self.overrides[profile_id][output_num]
            if not self.overrides[profile_id]:
                del self.overrides[profile_id]

    def get_overrides_for_profile(self, profile_id: str) -> dict[int, dict[str, bool]]:
        """Return the overrides dict for a profile, or empty."""
        return self.overrides.get(profile_id, {})

    def record_execution(self, status: str, steps_completed: int, error: str | None = None) -> None:
        """Append to execution history, pruning entries older than 7 days."""
        now = datetime.now(UTC).isoformat()
        self.last_executed = now
        entry = ExecutionHistoryEntry(
            timestamp=now,
            status=status,
            steps_completed=steps_completed,
            total_steps=len(self.steps),
            error=error,
        )
        self.execution_history.append(entry)
        self._prune_history()

    def _prune_history(self) -> None:
        """Remove entries older than 7 days."""
        cutoff = datetime.now(UTC) - _HISTORY_RETENTION
        cutoff_str = cutoff.isoformat()
        self.execution_history = [e for e in self.execution_history if e.timestamp >= cutoff_str]

    def is_valid(self) -> tuple[bool, list[str]]:
        """
        Validate the scene.

        Returns (is_valid, list_of_errors).
        """
        errors: list[str] = []
        if not self.id:
            errors.append("Scene id cannot be empty")
        if not self.name:
            errors.append("Scene name cannot be empty")
        if self.password_protected and not needs_passcode(self.passcode_hash):
            errors.append("password_protected is True but no passcode is set")
        seen_profile_ids = set()
        for i, step in enumerate(self.steps):
            err = step.validate()
            if err:
                errors.append(f"Step {i}: {err}")
            if step.type == STEP_TYPE_PROFILE:
                if step.id in seen_profile_ids:
                    errors.append(f"Step {i}: duplicate profile id {step.id!r}")
                seen_profile_ids.add(step.id)
        return (len(errors) == 0, errors)


# =============================================================================
# Conflict detection
# =============================================================================


@dataclass
class ConflictEntry:
    """Describes a single conflicting setting across profiles in a scene."""

    output_num: int
    setting_key: str
    profile_ids: list[tuple[str, str, Any]]  # (profile_id, profile_name, value)

    def to_dict(self) -> dict[str, Any]:
        return {
            "output": self.output_num,
            "setting": self.setting_key,
            "profiles": [{"id": pid, "name": pname, "value": val} for pid, pname, val in self.profile_ids],
        }


def detect_conflicts(
    scene: Scene,
    profile_map: dict[str, Any],  # profile_id -> Profile object
) -> list[ConflictEntry]:
    """
    Detect conflicting output settings across all Profile steps in a Scene.

    A conflict exists when two profiles set different non-default values for
    the same output's same setting.

    Default values (no conflict):
      enabled=True, input=1, hdcp=3, hdr=3, scaler=0, arc=False, audio_mute=False
    """
    # Per-output, per-profile settings collected from profile steps
    output_profile_settings: dict[int, dict[str, tuple[str, str, Any]]] = {}

    for step in scene.steps:
        if step.type != STEP_TYPE_PROFILE:
            continue
        profile = profile_map.get(step.id)
        if profile is None:
            continue
        overrides_for_profile = scene.get_overrides_for_profile(step.id)

        for output_num, output_cfg in profile.outputs.items():
            # Skip outputs that are disabled in the scene (via override)
            disabled_settings = overrides_for_profile.get(output_num, {})
            if not output_cfg.enabled:
                continue  # disabled outputs don't conflict

            # Check each setting
            for setting_key, value in _output_settings_iter(output_cfg):
                # Skip disabled settings
                if disabled_settings.get(setting_key):
                    continue
                # Skip default values
                if _is_default(setting_key, value):
                    continue

                if output_num not in output_profile_settings:
                    output_profile_settings[output_num] = {}
                if setting_key in output_profile_settings[output_num]:
                    existing_pid, existing_pname, existing_val = output_profile_settings[output_num][setting_key]
                    if existing_val != value:
                        # Conflict!
                        pass
                else:
                    output_profile_settings[output_num][setting_key] = (step.id, profile.name, value)

    # Build conflict entries from duplicates
    conflicts: list[ConflictEntry] = []
    for output_num, settings_map in output_profile_settings.items():
        for setting_key, entries_list in _group_by_setting(settings_map).items():
            if len(entries_list) > 1:
                # Multiple different values = conflict
                conflicts.append(
                    ConflictEntry(
                        output_num=output_num,
                        setting_key=setting_key,
                        profile_ids=entries_list,
                    )
                )

    return conflicts


def _output_settings_iter(output_cfg) -> list[tuple[str, Any]]:
    """Yield (setting_key, value) pairs for an output config."""
    return [
        ("input", output_cfg.input),
        ("enabled", output_cfg.enabled),
        ("hdcp", getattr(output_cfg, "hdcp_mode", None)),
        ("hdr", getattr(output_cfg, "hdr_mode", None)),
        ("scaler", getattr(output_cfg, "scaler_mode", None)),
        ("arc", getattr(output_cfg, "arc", False)),
        ("audio_mute", getattr(output_cfg, "audio_mute", False)),
    ]


def _is_default(setting_key: str, value: Any) -> bool:
    defaults = {
        "enabled": True,
        "input": 1,
        "hdcp": 3,
        "hdr": 3,
        "scaler": 0,
        "arc": False,
        "audio_mute": False,
    }
    return defaults.get(setting_key) == value


def _group_by_setting(settings_map: dict[str, tuple[str, str, Any]]) -> dict[str, list[tuple[str, str, Any]]]:
    """Group by setting_key, returning {setting_key: [(pid, pname, value), ...]}."""
    groups: dict[str, list[tuple[str, str, Any]]] = {}
    for setting_key, entry in settings_map.items():
        if setting_key not in groups:
            groups[setting_key] = []
        groups[setting_key].append(entry)
    return groups


# =============================================================================
# Scene Manager
# =============================================================================


class SceneManager:
    """
    CRUD + persistence for Phase 8 Scenes.

    Lives in the same data directory as profiles.json.
    """

    def __init__(self, data_dir: Path | None = None):
        if data_dir is None:
            data_dir = get_data_dir()
        self.data_dir = Path(data_dir).resolve()
        self.scenes_file = self.data_dir / _SCENES_FILE
        self._scenes: dict[str, Scene] = {}
        self._ensure_loaded()

    def _ensure_loaded(self) -> None:
        if not self.scenes_file.exists():
            _LOG.info("Scenes file not found (first run): %s", self.scenes_file)
            return
        try:
            with open(self.scenes_file, encoding="utf-8") as f:
                data = json.load(f)
            for scene_data in data.get("scenes", []):
                scene = Scene.from_dict(scene_data)
                self._scenes[scene.id] = scene
            _LOG.info("Loaded %d scenes", len(self._scenes))
        except Exception as e:
            _LOG.error("Failed to load scenes: %s", e)

    def _save(self) -> bool:
        try:
            ensure_data_dir(self.data_dir)
            data = {"scenes": [s.to_dict() for s in self._scenes.values()]}
            with open(self.scenes_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            _LOG.error("Failed to save scenes: %s", e)
            return False

    # ---- Read ----

    def list_scenes(self) -> list[Scene]:
        """Return all scenes sorted by dashboard_order."""
        return sorted(self._scenes.values(), key=lambda s: s.dashboard_order)

    def get_scene(self, scene_id: str) -> Scene | None:
        """Return a scene by ID."""
        return self._scenes.get(scene_id)

    def steps_reference_protected_profile(
        self,
        steps: list[SceneStep],
        profile_map: dict[str, Any] | None = None,
    ) -> bool:
        """
        Return True if any step in the list references a password-protected Profile.

        :param steps: List of SceneSteps to inspect
        :param profile_map: Optional dict of profile_id -> Profile. If None,
                           returns False (no way to determine without profiles).
        """
        if profile_map is None:
            # Without a profile map we can't determine protection status.
            # Callers in the REST API path supply the map explicitly.
            return False

        for step in steps:
            if step.type != STEP_TYPE_PROFILE:
                continue
            profile = profile_map.get(step.id)
            if profile is not None and getattr(profile, "password_protected", False):
                return True
        return False

    # ---- Create ----

    def create_scene(
        self,
        name: str,
        icon: str = "🎬",
        steps: list[SceneStep] | None = None,
        password_protected: bool = False,
        passcode: str | None = None,
    ) -> tuple[Scene | None, str | None]:
        """
        Create a new scene.

        :param name: Display name
        :param icon: Emoji icon
        :param steps: Initial steps list
        :param password_protected: Whether this scene requires a passcode
        :param passcode: Plaintext passcode (required if password_protected is True)
        :returns: (created_scene, error_string) — scene is None if error
        """
        scene_id = f"scene_{uuid.uuid4().hex[:12]}"
        passcode_hash = ""
        step_list = steps or []

        # Password inheritance: scene containing a protected profile must itself be protected
        if not password_protected and self.steps_reference_protected_profile(step_list):
            return None, ("Scene contains a password-protected Profile; the Scene must also be password-protected")

        if password_protected:
            if not passcode:
                return None, "passcode required when password_protected is True"
            passcode_hash = hash_passcode(passcode)

        scene = Scene(
            id=scene_id,
            name=name,
            icon=icon,
            steps=step_list,
            password_protected=password_protected,
            passcode_hash=passcode_hash,
        )
        valid, errors = scene.is_valid()
        if not valid:
            return None, "; ".join(errors)

        self._scenes[scene_id] = scene
        if not self._save():
            del self._scenes[scene_id]
            return None, "Failed to save"
        return scene, None

    # ---- Update ----

    def update_scene(
        self,
        scene_id: str,
        name: str | None = None,
        icon: str | None = None,
        steps: list[SceneStep] | None = None,
        overrides: dict[str, dict[int, dict[str, bool]]] | None = None,
        favorite: bool | None = None,
        dashboard_visible: bool | None = None,
        dashboard_order: int | None = None,
        password_protected: bool | None = None,
        passcode: str | None = None,
    ) -> tuple[Scene | None, str | None]:
        """
        Update an existing scene.

        :returns: (updated_scene, error_string)
        """
        scene = self._scenes.get(scene_id)
        if scene is None:
            return None, "Scene not found"

        if name is not None:
            scene.name = name
        if icon is not None:
            scene.icon = icon
        if steps is not None:
            scene.steps = steps
        if overrides is not None:
            scene.overrides = overrides
        if favorite is not None:
            scene.favorite = favorite
        if dashboard_visible is not None:
            scene.dashboard_visible = dashboard_visible
        if dashboard_order is not None:
            scene.dashboard_order = dashboard_order
        if password_protected is not None:
            scene.password_protected = password_protected
            if password_protected and passcode:
                scene.passcode_hash = hash_passcode(passcode)
            elif password_protected and not scene.passcode_hash:
                return None, "passcode required when enabling password protection"

        # Password inheritance: scene containing a protected profile must itself be protected
        if not scene.password_protected and self.steps_reference_protected_profile(scene.steps):
            return None, ("Scene contains a password-protected Profile; the Scene must also be password-protected")

        valid, errors = scene.is_valid()
        if not valid:
            return None, "; ".join(errors)

        if not self._save():
            return None, "Failed to save"
        return scene, None

    def add_step(
        self,
        scene_id: str,
        step: SceneStep,
    ) -> tuple[Scene | None, str | None]:
        """Append a step to a scene."""
        scene = self._scenes.get(scene_id)
        if scene is None:
            return None, "Scene not found"

        # Password inheritance check
        prospective = list(scene.steps) + [step]
        if not scene.password_protected and self.steps_reference_protected_profile(prospective):
            return None, ("Cannot add a step referencing a password-protected Profile to an unprotected Scene")

        scene.steps.append(step)
        if not self._save():
            scene.steps.pop()
            return None, "Failed to save"
        return scene, None

    def remove_step(self, scene_id: str, index: int) -> tuple[Scene | None, str | None]:
        """Remove step at index from a scene."""
        scene = self._scenes.get(scene_id)
        if scene is None:
            return None, "Scene not found"
        if not (0 <= index < len(scene.steps)):
            return None, f"Invalid step index: {index}"
        step = scene.steps[index]
        scene.remove_step(index)
        if not self._save():
            scene.steps.insert(index, step)
            return None, "Failed to save"
        return scene, None

    def set_override(
        self,
        scene_id: str,
        profile_id: str,
        output_num: int,
        setting_key: str,
        disabled: bool = True,
    ) -> tuple[Scene | None, str | None]:
        """Set an override for a profile's output setting within a scene."""
        scene = self._scenes.get(scene_id)
        if scene is None:
            return None, "Scene not found"
        scene.set_override(profile_id, output_num, setting_key, disabled)
        if not self._save():
            scene.clear_override(profile_id, output_num, setting_key)
            return None, "Failed to save"
        return scene, None

    def clear_override(
        self,
        scene_id: str,
        profile_id: str,
        output_num: int,
        setting_key: str,
    ) -> tuple[Scene | None, str | None]:
        """Remove an override."""
        scene = self._scenes.get(scene_id)
        if scene is None:
            return None, "Scene not found"
        scene.clear_override(profile_id, output_num, setting_key)
        if not self._save():
            return None, "Failed to save"
        return scene, None

    def verify_passcode(self, scene_id: str, passcode: str) -> bool:
        """Verify a passcode against a scene's stored hash."""
        scene = self._scenes.get(scene_id)
        if scene is None:
            return False
        if not scene.password_protected:
            return True
        if not needs_passcode(scene.passcode_hash):
            return True
        try:
            return verify_passcode(passcode, scene.passcode_hash)
        except PasswordError:
            return False

    # ---- Delete ----

    def delete_scene(self, scene_id: str) -> bool:
        """Delete a scene by ID."""
        if scene_id in self._scenes:
            del self._scenes[scene_id]
            return self._save()
        return False

    # ---- Display helpers ----

    def list_dashboard_scenes(self) -> list[Scene]:
        """Return scenes with dashboard_visible=True, sorted by dashboard_order."""
        return sorted(
            (s for s in self._scenes.values() if s.dashboard_visible),
            key=lambda s: s.dashboard_order,
        )

    def list_favorite_scenes(self) -> list[Scene]:
        """Return scenes with favorite=True."""
        return sorted(
            (s for s in self._scenes.values() if s.favorite),
            key=lambda s: s.dashboard_order,
        )
