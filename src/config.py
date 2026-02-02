"""
Configuration module for OREI HDMI Matrix integration.

:copyright: (c) 2026 by Custom Integration.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

_LOG = logging.getLogger(__name__)


# =============================================================================
# CEC Configuration for Scenes
# =============================================================================

@dataclass
class CecConfig:
    """
    CEC command routing configuration for a scene.
    
    Each target is a string like "input:3", "output:1", or "all_inputs".
    When a scene is recalled, CEC commands from these categories are routed
    to the specified targets.
    
    Volume commands are special - they auto-resolve to:
    1. Audio-only outputs (scaler=4) first
    2. ARC-enabled outputs if no audio-only
    3. First output as fallback
    
    When auto_resolved is True, the targets are regenerated on each scene load
    based on the current matrix state.
    """
    
    # Navigation commands (UP, DOWN, LEFT, RIGHT, SELECT, BACK, HOME, MENU)
    nav_targets: list[str] = field(default_factory=list)
    
    # Playback commands (PLAY, PAUSE, STOP, REWIND, FAST_FORWARD, RECORD, PREVIOUS, NEXT, EJECT)
    playback_targets: list[str] = field(default_factory=list)
    
    # Volume commands (VOLUME_UP, VOLUME_DOWN, MUTE)
    # Auto-resolved to audio_only/ARC outputs if empty
    volume_targets: list[str] = field(default_factory=list)
    
    # Power ON commands - sent to inputs when activating scene
    power_on_targets: list[str] = field(default_factory=list)
    
    # Power OFF commands - sent to inputs when deactivating/switching away
    power_off_targets: list[str] = field(default_factory=list)
    
    # If True, volume_targets is auto-resolved from current matrix state
    auto_resolved: bool = True
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "nav_targets": self.nav_targets,
            "playback_targets": self.playback_targets,
            "volume_targets": self.volume_targets,
            "power_on_targets": self.power_on_targets,
            "power_off_targets": self.power_off_targets,
            "auto_resolved": self.auto_resolved,
        }
    
    @staticmethod
    def from_dict(data: dict[str, Any]) -> "CecConfig":
        """Create from dictionary."""
        return CecConfig(
            nav_targets=data.get("nav_targets", []),
            playback_targets=data.get("playback_targets", []),
            volume_targets=data.get("volume_targets", []),
            power_on_targets=data.get("power_on_targets", []),
            power_off_targets=data.get("power_off_targets", []),
            auto_resolved=data.get("auto_resolved", True),
        )
    
    @staticmethod
    def create_default() -> "CecConfig":
        """Create a default CEC config with auto-resolution enabled."""
        return CecConfig(auto_resolved=True)
    
    def get_targets_for_category(self, category: str) -> list[str]:
        """
        Get targets for a CEC command category.
        
        :param category: One of 'navigation', 'playback', 'volume', 'power_on', 'power_off'
        :return: List of target strings
        """
        mapping = {
            "navigation": self.nav_targets,
            "playback": self.playback_targets,
            "volume": self.volume_targets,
            "power_on": self.power_on_targets,
            "power_off": self.power_off_targets,
        }
        return mapping.get(category, [])
    
    def set_targets_for_category(self, category: str, targets: list[str]) -> None:
        """
        Set targets for a CEC command category.
        
        :param category: One of 'navigation', 'playback', 'volume', 'power_on', 'power_off'
        :param targets: List of target strings
        """
        if category == "navigation":
            self.nav_targets = targets
        elif category == "playback":
            self.playback_targets = targets
        elif category == "volume":
            self.volume_targets = targets
        elif category == "power_on":
            self.power_on_targets = targets
        elif category == "power_off":
            self.power_off_targets = targets


@dataclass
class SceneOutput:
    """Configuration for a single output in a scene."""
    
    input: int  # 1-8, which input to route to this output
    enabled: bool = True  # Whether the output is enabled
    audio_mute: bool = False  # Whether audio is muted
    hdr_mode: int | None = None  # HDR mode (1=passthrough, 2=HDR→SDR, 3=auto)
    hdcp_mode: int | None = None  # HDCP mode (1=1.4, 2=2.2, 3=follow sink, etc.)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {"input": self.input, "enabled": self.enabled, "audio_mute": self.audio_mute}
        if self.hdr_mode is not None:
            result["hdr_mode"] = self.hdr_mode
        if self.hdcp_mode is not None:
            result["hdcp_mode"] = self.hdcp_mode
        return result
    
    @staticmethod
    def from_dict(data: dict[str, Any]) -> "SceneOutput":
        """Create from dictionary."""
        return SceneOutput(
            input=data.get("input", 1),
            enabled=data.get("enabled", True),
            audio_mute=data.get("audio_mute", False),
            hdr_mode=data.get("hdr_mode"),
            hdcp_mode=data.get("hdcp_mode"),
        )


@dataclass
class Scene:
    """A named routing configuration (scene) with optional CEC control."""
    
    id: str  # Unique identifier
    name: str  # Human-readable name
    outputs: dict[int, SceneOutput] = field(default_factory=dict)  # Output number -> config
    cec_config: CecConfig | None = None  # Optional CEC command routing config
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "id": self.id,
            "name": self.name,
            "outputs": {str(k): v.to_dict() for k, v in self.outputs.items()},
        }
        if self.cec_config is not None:
            result["cec_config"] = self.cec_config.to_dict()
        return result
    
    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Scene":
        """Create from dictionary."""
        outputs = {}
        for k, v in data.get("outputs", {}).items():
            outputs[int(k)] = SceneOutput.from_dict(v)
        
        # Parse CEC config if present
        cec_config = None
        if "cec_config" in data:
            cec_config = CecConfig.from_dict(data["cec_config"])
        
        return Scene(
            id=data.get("id", ""),
            name=data.get("name", "Unnamed"),
            outputs=outputs,
            cec_config=cec_config,
        )
    
    def get_active_inputs(self) -> set[int]:
        """Get the set of input numbers used by enabled outputs in this scene."""
        return {output.input for output in self.outputs.values() if output.enabled}
    
    def has_cec_config(self) -> bool:
        """Check if this scene has CEC configuration."""
        return self.cec_config is not None
    
    def ensure_cec_config(self) -> CecConfig:
        """Get or create CEC config for this scene."""
        if self.cec_config is None:
            self.cec_config = CecConfig.create_default()
        return self.cec_config


class SceneManager:
    """Manages named scenes (routing configurations)."""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize scene manager.
        
        :param config_dir: Configuration directory path
        """
        if config_dir is None:
            config_dir = os.getenv("UC_CONFIG_HOME") or os.getenv("HOME") or "./"
        
        self.config_dir = config_dir
        self.scenes_file = os.path.join(config_dir, "scenes.json")
        self._scenes: dict[str, Scene] = {}
        self.load()
    
    def load(self) -> bool:
        """Load scenes from file."""
        if not os.path.exists(self.scenes_file):
            _LOG.info("Scenes file not found: %s", self.scenes_file)
            return False
        
        try:
            with open(self.scenes_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._scenes = {}
                for scene_data in data.get("scenes", []):
                    scene = Scene.from_dict(scene_data)
                    self._scenes[scene.id] = scene
                _LOG.info("Loaded %d scenes", len(self._scenes))
                return True
        except Exception as ex:
            _LOG.error("Failed to load scenes: %s", ex)
            return False
    
    def save(self) -> bool:
        """Save scenes to file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            data = {"scenes": [s.to_dict() for s in self._scenes.values()]}
            with open(self.scenes_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            _LOG.info("Saved %d scenes", len(self._scenes))
            return True
        except Exception as ex:
            _LOG.error("Failed to save scenes: %s", ex)
            return False
    
    def list_scenes(self) -> list[dict[str, Any]]:
        """List all scenes with CEC config info."""
        return [
            {
                "id": s.id,
                "name": s.name,
                "output_count": len(s.outputs),
                "has_cec_config": s.has_cec_config(),
            }
            for s in self._scenes.values()
        ]
    
    def get_scene(self, scene_id: str) -> Scene | None:
        """Get a scene by ID."""
        return self._scenes.get(scene_id)
    
    def create_scene(
        self,
        scene_id: str,
        name: str,
        outputs: dict[int, dict],
        cec_config: dict[str, Any] | None = None
    ) -> Scene:
        """
        Create or update a scene.
        
        :param scene_id: Unique identifier
        :param name: Human-readable name
        :param outputs: Dict of output number -> output config
        :param cec_config: Optional CEC configuration dict
        :return: Created/updated scene
        """
        scene_outputs = {}
        for output_num, config in outputs.items():
            scene_outputs[int(output_num)] = SceneOutput.from_dict(config)
        
        # Parse CEC config if provided
        cec = None
        if cec_config is not None:
            cec = CecConfig.from_dict(cec_config)
        
        scene = Scene(id=scene_id, name=name, outputs=scene_outputs, cec_config=cec)
        self._scenes[scene_id] = scene
        self.save()
        return scene
    
    def update_scene_cec_config(
        self,
        scene_id: str,
        cec_config: dict[str, Any]
    ) -> Scene | None:
        """
        Update only the CEC config for an existing scene.
        
        :param scene_id: Scene identifier
        :param cec_config: CEC configuration dict
        :return: Updated scene or None if not found
        """
        scene = self._scenes.get(scene_id)
        if scene is None:
            return None
        
        scene.cec_config = CecConfig.from_dict(cec_config)
        self.save()
        return scene
    
    def delete_scene(self, scene_id: str) -> bool:
        """Delete a scene by ID."""
        if scene_id in self._scenes:
            del self._scenes[scene_id]
            self.save()
            return True
        return False


# =============================================================================
# Profile (Enhanced Scene with Macros) - Terminology Aliases
# =============================================================================

# Profile is the new terminology for Scene
# These aliases provide a migration path while maintaining backward compatibility

# Alias: ProfileOutput = SceneOutput
ProfileOutput = SceneOutput


@dataclass
class Profile:
    """
    A named routing configuration (profile) with CEC control and macro assignments.
    
    Profile is the enhanced terminology for Scene, adding:
    - Macro assignments for quick-access buttons
    - Power-on/power-off macro triggers
    
    This class extends Scene functionality while maintaining backward compatibility.
    """
    
    id: str  # Unique identifier
    name: str  # Human-readable name
    outputs: dict[int, SceneOutput] = field(default_factory=dict)  # Output number -> config
    cec_config: CecConfig | None = None  # CEC command routing config
    icon: str = "📺"  # Display icon
    # Macro assignments
    macros: list[str] = field(default_factory=list)  # List of macro IDs for quick access
    power_on_macro: str | None = None  # Macro to run when profile activates
    power_off_macro: str | None = None  # Macro to run when profile deactivates
    # Pin/visibility settings
    pinned: bool = True  # Whether this profile appears in the main UI
    pin_order: int = 0  # Order in pinned list (0-7)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "outputs": {str(k): v.to_dict() for k, v in self.outputs.items()},
            "macros": self.macros,
            "pinned": self.pinned,
            "pin_order": self.pin_order,
        }
        if self.cec_config is not None:
            result["cec_config"] = self.cec_config.to_dict()
        if self.power_on_macro:
            result["power_on_macro"] = self.power_on_macro
        if self.power_off_macro:
            result["power_off_macro"] = self.power_off_macro
        return result
    
    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Profile":
        """Create from dictionary."""
        outputs = {}
        for k, v in data.get("outputs", {}).items():
            outputs[int(k)] = SceneOutput.from_dict(v)
        
        cec_config = None
        if "cec_config" in data:
            cec_config = CecConfig.from_dict(data["cec_config"])
        
        return Profile(
            id=data.get("id", ""),
            name=data.get("name", "Unnamed"),
            icon=data.get("icon", "📺"),
            outputs=outputs,
            cec_config=cec_config,
            macros=data.get("macros", []),
            power_on_macro=data.get("power_on_macro"),
            power_off_macro=data.get("power_off_macro"),
            pinned=data.get("pinned", True),
            pin_order=data.get("pin_order", 0),
        )
    
    @staticmethod
    def from_scene(scene: Scene) -> "Profile":
        """Create a Profile from a legacy Scene."""
        return Profile(
            id=scene.id,
            name=scene.name,
            outputs=scene.outputs,
            cec_config=scene.cec_config,
        )
    
    def to_scene(self) -> Scene:
        """Convert to legacy Scene format."""
        return Scene(
            id=self.id,
            name=self.name,
            outputs=self.outputs,
            cec_config=self.cec_config,
        )
    
    def get_active_inputs(self) -> set[int]:
        """Get the set of input numbers used by enabled outputs."""
        return {output.input for output in self.outputs.values() if output.enabled}
    
    def has_cec_config(self) -> bool:
        """Check if this profile has CEC configuration."""
        return self.cec_config is not None
    
    def ensure_cec_config(self) -> CecConfig:
        """Get or create CEC config for this profile."""
        if self.cec_config is None:
            self.cec_config = CecConfig.create_default()
        return self.cec_config


class ProfileManager:
    """
    Manages profiles (enhanced scenes with macro support).
    
    Provides backward compatibility by:
    - Auto-migrating scenes.json to profiles.json on first load
    - Supporting both Scene and Profile data formats
    """
    
    def __init__(self, config_dir: str = None):
        """
        Initialize profile manager.
        
        :param config_dir: Configuration directory path
        """
        if config_dir is None:
            config_dir = os.getenv("UC_CONFIG_HOME") or os.getenv("HOME") or "./"
        
        self.config_dir = config_dir
        self.profiles_file = os.path.join(config_dir, "profiles.json")
        self.legacy_scenes_file = os.path.join(config_dir, "scenes.json")
        self._profiles: dict[str, Profile] = {}
        self.load()
    
    def load(self) -> bool:
        """Load profiles from file, migrating from scenes.json if needed."""
        # Try loading profiles.json first
        if os.path.exists(self.profiles_file):
            return self._load_profiles()
        
        # Fall back to migrating from scenes.json
        if os.path.exists(self.legacy_scenes_file):
            _LOG.info("Migrating scenes.json to profiles.json...")
            return self._migrate_from_scenes()
        
        _LOG.info("No profiles or scenes file found")
        return False
    
    def _load_profiles(self) -> bool:
        """Load profiles from profiles.json."""
        try:
            with open(self.profiles_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._profiles = {}
                for profile_data in data.get("profiles", []):
                    profile = Profile.from_dict(profile_data)
                    self._profiles[profile.id] = profile
                _LOG.info("Loaded %d profiles", len(self._profiles))
                return True
        except Exception as ex:
            _LOG.error("Failed to load profiles: %s", ex)
            return False
    
    def _migrate_from_scenes(self) -> bool:
        """Migrate data from scenes.json to profiles.json."""
        try:
            with open(self.legacy_scenes_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._profiles = {}
                for scene_data in data.get("scenes", []):
                    scene = Scene.from_dict(scene_data)
                    profile = Profile.from_scene(scene)
                    self._profiles[profile.id] = profile
                
                # Save as profiles.json
                self.save()
                _LOG.info("Migrated %d scenes to profiles", len(self._profiles))
                return True
        except Exception as ex:
            _LOG.error("Failed to migrate scenes: %s", ex)
            return False
    
    def save(self) -> bool:
        """Save profiles to file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            data = {
                "version": 2,
                "profiles": [p.to_dict() for p in self._profiles.values()]
            }
            with open(self.profiles_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            _LOG.info("Saved %d profiles", len(self._profiles))
            return True
        except Exception as ex:
            _LOG.error("Failed to save profiles: %s", ex)
            return False
    
    def list_profiles(self) -> list[dict[str, Any]]:
        """List all profiles with summary info."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "icon": p.icon,
                "output_count": len(p.outputs),
                "has_cec_config": p.has_cec_config(),
                "macro_count": len(p.macros),
                "pinned": p.pinned,
                "pin_order": p.pin_order,
            }
            for p in self._profiles.values()
        ]
    
    def get_profile(self, profile_id: str) -> Profile | None:
        """Get a profile by ID."""
        return self._profiles.get(profile_id)
    
    def create_profile(
        self,
        profile_id: str,
        name: str,
        outputs: dict[int, dict],
        icon: str = "📺",
        cec_config: dict[str, Any] | None = None,
        macros: list[str] | None = None,
        power_on_macro: str | None = None,
        power_off_macro: str | None = None,
        pinned: bool | None = None,
        pin_order: int | None = None,
    ) -> Profile:
        """Create or update a profile."""
        profile_outputs = {}
        for output_num, config in outputs.items():
            profile_outputs[int(output_num)] = SceneOutput.from_dict(config)
        
        cec = None
        if cec_config is not None:
            cec = CecConfig.from_dict(cec_config)
        
        # Auto-pin logic: pin if < 8 pinned profiles exist
        if pinned is None:
            pinned_count = sum(1 for p in self._profiles.values() if p.pinned)
            pinned = pinned_count < 8
        
        # Auto-assign pin_order if pinned and not specified
        if pin_order is None and pinned:
            used_orders = {p.pin_order for p in self._profiles.values() if p.pinned}
            for i in range(8):
                if i not in used_orders:
                    pin_order = i
                    break
            if pin_order is None:
                pin_order = 0  # Fallback
        elif pin_order is None:
            pin_order = 0
        
        profile = Profile(
            id=profile_id,
            name=name,
            icon=icon,
            outputs=profile_outputs,
            cec_config=cec,
            macros=macros or [],
            power_on_macro=power_on_macro,
            power_off_macro=power_off_macro,
            pinned=pinned,
            pin_order=pin_order,
        )
        self._profiles[profile_id] = profile
        self.save()
        return profile
    
    def update_profile(
        self,
        profile_id: str,
        name: str | None = None,
        icon: str | None = None,
        outputs: dict[int, dict] | None = None,
        cec_config: dict[str, Any] | None = None,
        macros: list[str] | None = None,
        power_on_macro: str | None = None,
        power_off_macro: str | None = None,
        pinned: bool | None = None,
        pin_order: int | None = None,
    ) -> Profile | None:
        """Update an existing profile."""
        profile = self._profiles.get(profile_id)
        if profile is None:
            return None
        
        if name is not None:
            profile.name = name
        if icon is not None:
            profile.icon = icon
        if outputs is not None:
            profile.outputs = {int(k): SceneOutput.from_dict(v) for k, v in outputs.items()}
        if cec_config is not None:
            profile.cec_config = CecConfig.from_dict(cec_config)
        if macros is not None:
            profile.macros = macros
        if power_on_macro is not None:
            profile.power_on_macro = power_on_macro if power_on_macro else None
        if power_off_macro is not None:
            profile.power_off_macro = power_off_macro if power_off_macro else None
        if pinned is not None:
            profile.pinned = pinned
        if pin_order is not None:
            profile.pin_order = pin_order
        
        self.save()
        return profile
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile by ID."""
        if profile_id in self._profiles:
            del self._profiles[profile_id]
            self.save()
            return True
        return False
    
    # Backward compatibility: Scene-like methods
    def list_scenes(self) -> list[dict[str, Any]]:
        """Alias for list_profiles() - backward compatibility."""
        return self.list_profiles()
    
    def get_scene(self, scene_id: str) -> Profile | None:
        """Alias for get_profile() - backward compatibility."""
        return self.get_profile(scene_id)
    
    def create_scene(self, scene_id: str, name: str, outputs: dict[int, dict], 
                     cec_config: dict[str, Any] | None = None) -> Profile:
        """Alias for create_profile() - backward compatibility."""
        return self.create_profile(scene_id, name, outputs, cec_config=cec_config)
    
    def delete_scene(self, scene_id: str) -> bool:
        """Alias for delete_profile() - backward compatibility."""
        return self.delete_profile(scene_id)
    
    def update_scene_cec_config(self, scene_id: str, cec_config: dict[str, Any]) -> Profile | None:
        """Update CEC config - backward compatibility."""
        return self.update_profile(scene_id, cec_config=cec_config)
    
    def update_profile_cec_config(self, profile_id: str, cec_config: dict[str, Any]) -> Profile | None:
        """Update only the CEC config for a profile."""
        return self.update_profile(profile_id, cec_config=cec_config)


@dataclass
class MatrixConfig:
    """Configuration for OREI Matrix device."""

    host: str
    port: int = 443
    name: str = "OREI Matrix"

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "name": self.name,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "MatrixConfig":
        """Create configuration from dictionary."""
        return MatrixConfig(
            host=data.get("host", "192.168.1.100"),
            port=data.get("port", 23),
            name=data.get("name", "OREI Matrix"),
        )


class Config:
    """Integration configuration manager."""

    def __init__(self, config_dir: str = None):
        """
        Initialize configuration manager.

        :param config_dir: Configuration directory path
        """
        if config_dir is None:
            config_dir = os.getenv("UC_CONFIG_HOME") or os.getenv("HOME") or "./"
        
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "orei_matrix_config.json")
        self._matrix_config: MatrixConfig | None = None

    def load(self) -> bool:
        """
        Load configuration from file.

        :return: True if configuration loaded successfully
        """
        if not os.path.exists(self.config_file):
            _LOG.info("Configuration file not found: %s", self.config_file)
            return False

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._matrix_config = MatrixConfig.from_dict(data)
                _LOG.info("Configuration loaded successfully")
                return True
        except Exception as ex:
            _LOG.error("Failed to load configuration: %s", ex)
            return False

    def save(self) -> bool:
        """
        Save configuration to file.

        :return: True if configuration saved successfully
        """
        if self._matrix_config is None:
            _LOG.warning("No configuration to save")
            return False

        try:
            os.makedirs(self.config_dir, exist_ok=True)
            
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._matrix_config.to_dict(), f, indent=2)
                _LOG.info("Configuration saved successfully")
                return True
        except Exception as ex:
            _LOG.error("Failed to save configuration: %s", ex)
            return False

    @property
    def matrix(self) -> MatrixConfig | None:
        """Get matrix configuration."""
        return self._matrix_config

    def set_matrix_config(self, host: str, port: int = 23, name: str = "OREI Matrix"):
        """
        Set matrix configuration.

        :param host: Matrix IP address
        :param port: Matrix TCP port
        :param name: Device name
        """
        self._matrix_config = MatrixConfig(host=host, port=port, name=name)
        self.save()
