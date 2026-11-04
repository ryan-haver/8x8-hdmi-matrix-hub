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

import copy
import dataclasses
import logging
import math
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from _file_io import atomic_read_json
from password import (
    PasswordError,
    ensure_hashed_passcode,
    hash_passcode,
    needs_passcode,
    verify_passcode,
    verify_passcode_async,
)
from persistence import ensure_data_dir, get_data_dir


def _write_blocked(path) -> bool:
    from hub.persistence.startup import is_write_blocked

    return is_write_blocked(path)


def _block_reason(path) -> str | None:
    from hub.persistence.startup import block_reason

    return block_reason(path)


_LOG = logging.getLogger("scene_manager")

# R2 contract §4: scene_manager.SceneManager targets ``scenes_v2.json``; the legacy
# ``scenes.json`` (used by config.SceneManager and pre-Phase-8 releases) is imported
# non-destructively by ``hub.persistence.startup.prepare_runtime_storage``.
_SCENES_FILE = "scenes_v2.json"
SCENES_LEGACY_FILE = "scenes.json"

#: 7-day execution history retention
_HISTORY_RETENTION = timedelta(days=7)

#: Valid step types
STEP_TYPE_PROFILE = "profile"
STEP_TYPE_SYSTEM_ACTION = "system_action"
STEP_TYPE_MACRO = "macro"
STEP_TYPE_WAIT = "wait"
VALID_STEP_TYPES = frozenset({STEP_TYPE_PROFILE, STEP_TYPE_SYSTEM_ACTION, STEP_TYPE_MACRO, STEP_TYPE_WAIT})

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


def validate_overrides(overrides: Any) -> str | None:
    """Check a ``{profile_id: {output_num: {setting_key: bool}}}`` overrides map.

    Returns an error string, or None if it is valid. Output numbers are 1-8
    and setting keys are the :data:`OVERRIDABLE_SETTINGS`.
    """
    if not isinstance(overrides, dict):
        return "overrides must be an object"
    for profile_id, outputs in overrides.items():
        if not isinstance(profile_id, str) or not profile_id:
            return "override profile id must be a non-empty string"
        if not isinstance(outputs, dict):
            return f"overrides for {profile_id!r} must be an object"
        for output_num, settings in outputs.items():
            if isinstance(output_num, bool) or not isinstance(output_num, int) or not 1 <= output_num <= 8:
                return f"override output {output_num!r} must be 1-8"
            if not isinstance(settings, dict):
                return f"overrides for {profile_id!r} output {output_num} must be an object"
            for key, disabled in settings.items():
                if key not in OVERRIDABLE_SETTINGS:
                    return f"unknown override setting {key!r} (one of {sorted(OVERRIDABLE_SETTINGS)})"
                if not isinstance(disabled, bool):
                    return f"override {key!r} must be true or false"
    return None


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
                 - ``"wait"`` — pause for ``params.seconds`` (0.5–30 seconds)
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
        if self.type == STEP_TYPE_WAIT:
            seconds = self.params.get("seconds")
            if (
                isinstance(seconds, bool)
                or not isinstance(seconds, (int, float))
                or not 0.5 <= seconds <= 30
                or not math.isfinite(seconds)
            ):
                return "Wait seconds must be a finite number from 0.5 to 30"
            return None
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
    # R2 contract §4: unknown record-level scalar metadata passes through
    # load/edit/save on disk; public serializers exclude these private fields.
    _unknown_fields: dict[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def is_password_protected(self) -> bool:
        """True if the scene has its own passcode (the flag or a stored hash; fails closed)."""
        return self.password_protected or needs_passcode(self.passcode_hash)

    def to_dict(self, include_hash: bool = False) -> dict[str, Any]:
        """
        Convert to dictionary.

        :param include_hash: include ``passcode_hash``; only for persistence,
                             never for clients (SEC-04 / F-SEC-005)

        Unknown extension fields are excluded from this public projection;
        the private storage writer preserves them separately.
        """
        result: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "steps": [s.to_dict() for s in self.steps],
            "overrides": {
                pid: {
                    str(out_num): {key: value for key, value in settings.items() if key in OVERRIDABLE_SETTINGS}
                    for out_num, settings in out_map.items()
                }
                for pid, out_map in self.overrides.items()
            },
            "favorite": self.favorite,
            "dashboard_visible": self.dashboard_visible,
            "dashboard_order": self.dashboard_order,
            "password_protected": self.is_password_protected(),
            "last_executed": self.last_executed,
            "execution_history": [e.to_dict() for e in self.execution_history],
        }
        if include_hash:
            result["passcode_hash"] = self.passcode_hash
        return result

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Scene":
        steps = [SceneStep.from_dict(s) for s in data.get("steps", [])]
        overrides_raw: dict[str, dict[str, dict[str, bool]]] = data.get("overrides", {})
        overrides: dict[str, dict[int, dict[str, bool]]] = {}
        for pid, outers in overrides_raw.items():
            out_map: dict[int, dict[str, bool]] = {}
            for out_str, settings in outers.items():
                known = {key: value for key, value in settings.items() if key in OVERRIDABLE_SETTINGS}
                if known:
                    out_map[int(out_str)] = known
            if out_map:
                overrides[pid] = out_map

        history = [ExecutionHistoryEntry.from_dict(h) for h in data.get("execution_history", [])]

        declared_keys = {
            "id",
            "name",
            "icon",
            "steps",
            "overrides",
            "favorite",
            "dashboard_visible",
            "dashboard_order",
            "password_protected",
            "passcode_hash",
            "last_executed",
            "execution_history",
        }
        unknown = {k: v for k, v in data.items() if k not in declared_keys}

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
            # A raw PIN found on load is hashed (F-SEC-004)
            passcode_hash=ensure_hashed_passcode(data.get("passcode_hash")) or "",
            last_executed=data.get("last_executed"),
            execution_history=history,
            _unknown_fields=unknown,
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

    A conflict exists when profiles write different values to the same setting.
    Defaults are writes too; absent optional settings and overridden writes
    cannot conflict. Disabled outputs still receive their profile state.
    """
    # Per-output, per-profile settings collected from profile steps
    output_profile_settings: dict[int, dict[str, list[tuple[str, str, Any]]]] = {}

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

            # Check each setting
            for setting_key, value in _output_settings_iter(output_cfg):
                # Skip disabled settings
                if disabled_settings.get(setting_key):
                    continue
                if value is None:
                    continue

                entries = output_profile_settings.setdefault(output_num, {}).setdefault(setting_key, [])
                entries.append((step.id, profile.name, value))

    # Build conflict entries from duplicates
    conflicts: list[ConflictEntry] = []
    for output_num, settings_map in sorted(output_profile_settings.items()):
        for setting_key, entries_list in settings_map.items():
            if any(entry[2] != entries_list[0][2] for entry in entries_list[1:]):
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
        ("arc", getattr(output_cfg, "arc", None)),
        ("audio_mute", getattr(output_cfg, "audio_mute", False)),
    ]


def _profile_is_protected(profile: Any) -> bool:
    """True if a Profile (or Profile-like object) needs a passcode."""
    check = getattr(profile, "is_password_protected", None)
    if callable(check):
        return bool(check())
    return bool(getattr(profile, "password_protected", False)) or needs_passcode(getattr(profile, "passcode_hash", ""))


def _protected_profiles(steps: list[SceneStep], profile_map: dict[str, Any] | None) -> list[Any]:
    """The distinct protected Profiles that profile steps reference (none without a map)."""
    if not profile_map:
        return []
    found: dict[str, Any] = {}
    for step in steps:
        if step.type != STEP_TYPE_PROFILE or step.id in found:
            continue
        profile = profile_map.get(step.id)
        if profile is not None and _profile_is_protected(profile):
            found[step.id] = profile
    return list(found.values())


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
        # Unknown top-level keys captured at load time; re-emitted on save so
        # operator data and forward-compatible fields survive every edit.
        self._unknown_top_keys: dict[str, Any] = {}
        self._ensure_loaded()

    def _ensure_loaded(self) -> None:
        from hub.persistence.migrations import load_versioned_json
        from hub.persistence.startup import prepare_scene_files
        from persistence import migrate_legacy_file

        migrate_legacy_file(self.scenes_file, "scenes_v2.json")
        migrate_legacy_file(self.data_dir / SCENES_LEGACY_FILE, SCENES_LEGACY_FILE)
        prepare_scene_files(self.data_dir)
        data = load_versioned_json(self.scenes_file, default=None)
        if data is None:
            legacy = self.data_dir / SCENES_LEGACY_FILE
            if legacy.exists():
                from hub.persistence.startup import scene_shape

                if scene_shape(atomic_read_json(legacy)) == "legacy":
                    return
            if not self._save_initial_empty():
                from hub.persistence import MigrationError

                raise MigrationError(f"{self.scenes_file}: defaults could not be saved")
            return
        self._unknown_top_keys = {k: v for k, v in data.items() if k != "scenes"}
        rehashed = False
        for raw in data["scenes"]:
            scene = Scene.from_dict(raw)
            self._scenes[scene.id] = scene
            rehashed |= scene.passcode_hash != (raw.get("passcode_hash") or "")
        if rehashed and not self._save():
            from hub.persistence import MigrationError

            raise MigrationError(f"{self.scenes_file}: PIN rehash could not be saved")

    def _save(self) -> bool:
        if _write_blocked(self.scenes_file):
            _LOG.error(
                "Refusing to save scenes: %s",
                _block_reason(self.scenes_file),
            )
            return False
        try:
            ensure_data_dir(self.data_dir)
            data: dict[str, Any] = {}
            data["scenes"] = [s.to_dict(include_hash=True) for s in self._scenes.values()]
            from hub.persistence.migrations import save_versioned_json

            save_versioned_json(self.scenes_file, data)
            return True
        except Exception as e:
            _LOG.error("Failed to save scenes: %s", e)
            return False

    def _save_initial_empty(self) -> bool:
        """Materialise ``scenes_v2.json`` with an empty scenes list (first run / no legacy)."""
        try:
            ensure_data_dir(self.data_dir)
            from hub.persistence.migrations import save_versioned_json as atomic_write_json

            atomic_write_json(self.scenes_file, {"scenes": []})
            return True
        except Exception as e:
            _LOG.error("Failed to seed scenes_v2.json: %s", e)
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

        return bool(_protected_profiles(steps, profile_map))

    # ---- Passcodes (SEC-04, SEC-05, SEC-06) ----

    def is_scene_password_protected(self, scene_id: str, profiles_map: dict[str, Any] | None = None) -> bool:
        """
        True if running the scene needs a passcode: its own, or one inherited
        from a protected Profile among its steps (``profiles_map`` is
        ``{profile_id: Profile}``; without it only the scene's own PIN counts).
        """
        scene = self._scenes.get(scene_id)
        if scene is None:
            return False
        return scene.is_password_protected() or bool(_protected_profiles(scene.steps, profiles_map))

    def is_passcode_inherited(self, scene_id: str, profiles_map: dict[str, Any] | None = None) -> bool:
        """True if the scene has no PIN of its own but runs a protected Profile."""
        scene = self._scenes.get(scene_id)
        if scene is None or scene.is_password_protected():
            return False
        return bool(_protected_profiles(scene.steps, profiles_map))

    def _passcode_hashes(self, scene: Scene, profiles_map: dict[str, Any] | None) -> list[str]:
        """
        The hashes a passcode must match to run ``scene``: the scene's own, or
        else those of every protected Profile it runs. A protected item with no
        hash contributes ``""``, which never verifies (fails closed).
        """
        if scene.is_password_protected():
            return [scene.passcode_hash]
        return [getattr(p, "passcode_hash", "") or "" for p in _protected_profiles(scene.steps, profiles_map)]

    def verify_scene_passcode(
        self, scene_id: str, passcode: str | None, profiles_map: dict[str, Any] | None = None
    ) -> bool:
        """
        Verify ``passcode`` for running the scene (synchronous; the REST layer
        uses :meth:`verify_scene_passcode_async`).

        Unknown scenes fail; unprotected scenes pass.
        """
        scene = self._scenes.get(scene_id)
        if scene is None:
            return False
        hashes = self._passcode_hashes(scene, profiles_map)
        if not hashes:
            return True
        try:
            return all(needs_passcode(h) and verify_passcode(passcode, h) for h in hashes)
        except PasswordError:
            return False

    async def verify_scene_passcode_async(
        self, scene_id: str, passcode: str | None, profiles_map: dict[str, Any] | None = None
    ) -> bool:
        """:meth:`verify_scene_passcode` with PBKDF2 in the thread executor (SEC-06)."""
        scene = self._scenes.get(scene_id)
        if scene is None:
            return False
        hashes = self._passcode_hashes(scene, profiles_map)
        if not hashes:
            return True
        try:
            for stored in hashes:
                if not needs_passcode(stored) or not await verify_passcode_async(passcode, stored):
                    return False
        except PasswordError:
            return False
        return True

    # ---- Create ----

    def create_scene(
        self,
        name: str,
        icon: str = "🎬",
        steps: list[SceneStep] | None = None,
        password_protected: bool = False,
        passcode: str | None = None,
        passcode_hash: str | None = None,
        profiles_map: dict[str, Any] | None = None,
    ) -> tuple[Scene | None, str | None]:
        """
        Create a new scene.

        :param name: Display name
        :param icon: Emoji icon
        :param steps: Initial steps list
        :param password_protected: Whether this scene requires a passcode
        :param passcode: Plaintext passcode (required if password_protected is True)
        :param passcode_hash: Already-hashed passcode, used instead of ``passcode``
                              (the REST layer hashes in a thread, SEC-06)
        :param profiles_map: ``{profile_id: Profile}`` for the inheritance check
        :returns: (created_scene, error_string) — scene is None if error
        """
        scene_id = f"scene_{uuid.uuid4().hex[:12]}"
        step_list = steps or []

        # Password inheritance: scene containing a protected profile must itself be protected
        if not password_protected and self.steps_reference_protected_profile(step_list, profiles_map):
            return None, ("Scene contains a password-protected Profile; the Scene must also be password-protected")

        if not password_protected:
            passcode_hash = ""
        elif not passcode_hash:
            if not passcode:
                return None, "passcode required when password_protected is True"
            try:
                passcode_hash = hash_passcode(passcode)
            except PasswordError as e:
                return None, str(e)

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
        passcode_hash: str | None = None,
        profiles_map: dict[str, Any] | None = None,
    ) -> tuple[Scene | None, str | None]:
        """
        Update an existing scene.

        The changes are applied to a copy, which is validated and saved before
        it replaces the stored scene: a rejected update leaves the scene as it
        was, in memory and on disk (API-13).

        ``password_protected=False`` removes the scene's PIN. Callers check the
        current PIN first (SEC-05); the REST layer does.

        :param passcode_hash: Already-hashed new passcode, used instead of ``passcode``
        :param profiles_map: ``{profile_id: Profile}`` for the inheritance check
        :returns: (updated_scene, error_string)
        """
        scene = self._scenes.get(scene_id)
        if scene is None:
            return None, "Scene not found"

        if overrides is not None:
            err = validate_overrides(overrides)
            if err:
                return None, err

        candidate = copy.deepcopy(scene)
        if name is not None:
            candidate.name = name
        if icon is not None:
            candidate.icon = icon
        if steps is not None:
            candidate.steps = list(steps)
        if overrides is not None:
            candidate.overrides = overrides
        if favorite is not None:
            candidate.favorite = favorite
        if dashboard_visible is not None:
            candidate.dashboard_visible = dashboard_visible
        if dashboard_order is not None:
            candidate.dashboard_order = dashboard_order
        if password_protected is not None:
            candidate.password_protected = password_protected
            if not password_protected:
                candidate.passcode_hash = ""
            elif passcode_hash:
                candidate.passcode_hash = passcode_hash
            elif passcode:
                try:
                    candidate.passcode_hash = hash_passcode(passcode)
                except PasswordError as e:
                    return None, str(e)
            elif not candidate.passcode_hash:
                return None, "passcode required when enabling password protection"

        # Password inheritance: scene containing a protected profile must itself be protected
        if not candidate.password_protected and self.steps_reference_protected_profile(candidate.steps, profiles_map):
            return None, ("Scene contains a password-protected Profile; the Scene must also be password-protected")

        valid, errors = candidate.is_valid()
        if not valid:
            return None, "; ".join(errors)

        self._scenes[scene_id] = candidate
        if not self._save():
            self._scenes[scene_id] = scene
            return None, "Failed to save"
        return candidate, None

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

        # Validate the scene as it would be before changing it (API-13)
        valid, errors = dataclasses.replace(scene, steps=prospective).is_valid()
        if not valid:
            return None, "; ".join(errors)

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
        err = validate_overrides({profile_id: {output_num: {setting_key: disabled}}})
        if err:
            return None, err
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
        """Verify a passcode against a scene's own stored hash (see :meth:`verify_scene_passcode`)."""
        return self.verify_scene_passcode(scene_id, passcode)

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
