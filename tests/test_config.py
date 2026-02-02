"""
Unit tests for config.py module.

Tests all configuration classes:
- CecConfig
- SceneOutput
- Scene
- SceneManager
- Profile
- ProfileManager
- MatrixConfig
- Config
"""

import json
import os
import tempfile
import pytest

# Import config module
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import (
    CecConfig,
    SceneOutput,
    Scene,
    SceneManager,
    Profile,
    ProfileManager,
    MatrixConfig,
    Config,
)


# =============================================================================
# CecConfig Tests
# =============================================================================

class TestCecConfig:
    """Tests for CecConfig dataclass."""
    
    def test_create_default(self):
        """Test CecConfig.create_default() creates auto-resolved config."""
        config = CecConfig.create_default()
        
        assert config.auto_resolved is True
        assert config.nav_targets == []
        assert config.playback_targets == []
        assert config.volume_targets == []
        assert config.power_on_targets == []
        assert config.power_off_targets == []
    
    def test_to_dict(self):
        """Test CecConfig.to_dict() returns correct dictionary."""
        config = CecConfig(
            nav_targets=["input:1", "input:2"],
            playback_targets=["input:3"],
            volume_targets=["output:1"],
            power_on_targets=["input:1"],
            power_off_targets=["input:2"],
            auto_resolved=False,
        )
        
        result = config.to_dict()
        
        assert result["nav_targets"] == ["input:1", "input:2"]
        assert result["playback_targets"] == ["input:3"]
        assert result["volume_targets"] == ["output:1"]
        assert result["power_on_targets"] == ["input:1"]
        assert result["power_off_targets"] == ["input:2"]
        assert result["auto_resolved"] is False
    
    def test_from_dict(self):
        """Test CecConfig.from_dict() creates correct object."""
        data = {
            "nav_targets": ["input:1"],
            "playback_targets": ["input:2"],
            "volume_targets": ["output:1", "output:2"],
            "power_on_targets": [],
            "power_off_targets": ["all_inputs"],
            "auto_resolved": True,
        }
        
        config = CecConfig.from_dict(data)
        
        assert config.nav_targets == ["input:1"]
        assert config.playback_targets == ["input:2"]
        assert config.volume_targets == ["output:1", "output:2"]
        assert config.power_on_targets == []
        assert config.power_off_targets == ["all_inputs"]
        assert config.auto_resolved is True
    
    def test_from_dict_with_missing_fields(self):
        """Test CecConfig.from_dict() handles missing fields with defaults."""
        data = {"nav_targets": ["input:1"]}
        
        config = CecConfig.from_dict(data)
        
        assert config.nav_targets == ["input:1"]
        assert config.playback_targets == []
        assert config.volume_targets == []
        assert config.power_on_targets == []
        assert config.power_off_targets == []
        assert config.auto_resolved is True  # Default
    
    def test_roundtrip_serialization(self):
        """Test to_dict/from_dict roundtrip preserves data."""
        original = CecConfig(
            nav_targets=["input:1", "input:2"],
            playback_targets=["input:3"],
            volume_targets=["output:1"],
            power_on_targets=["input:4"],
            power_off_targets=["all_inputs"],
            auto_resolved=False,
        )
        
        result = CecConfig.from_dict(original.to_dict())
        
        assert result.nav_targets == original.nav_targets
        assert result.playback_targets == original.playback_targets
        assert result.volume_targets == original.volume_targets
        assert result.power_on_targets == original.power_on_targets
        assert result.power_off_targets == original.power_off_targets
        assert result.auto_resolved == original.auto_resolved
    
    def test_get_targets_for_category(self):
        """Test get_targets_for_category returns correct targets."""
        config = CecConfig(
            nav_targets=["input:1"],
            playback_targets=["input:2"],
            volume_targets=["output:1"],
            power_on_targets=["input:3"],
            power_off_targets=["input:4"],
        )
        
        assert config.get_targets_for_category("navigation") == ["input:1"]
        assert config.get_targets_for_category("playback") == ["input:2"]
        assert config.get_targets_for_category("volume") == ["output:1"]
        assert config.get_targets_for_category("power_on") == ["input:3"]
        assert config.get_targets_for_category("power_off") == ["input:4"]
        assert config.get_targets_for_category("unknown") == []
    
    def test_set_targets_for_category(self):
        """Test set_targets_for_category updates correct field."""
        config = CecConfig()
        
        config.set_targets_for_category("navigation", ["input:1"])
        config.set_targets_for_category("playback", ["input:2"])
        config.set_targets_for_category("volume", ["output:1"])
        config.set_targets_for_category("power_on", ["input:3"])
        config.set_targets_for_category("power_off", ["input:4"])
        
        assert config.nav_targets == ["input:1"]
        assert config.playback_targets == ["input:2"]
        assert config.volume_targets == ["output:1"]
        assert config.power_on_targets == ["input:3"]
        assert config.power_off_targets == ["input:4"]


# =============================================================================
# SceneOutput Tests
# =============================================================================

class TestSceneOutput:
    """Tests for SceneOutput dataclass."""
    
    def test_default_values(self):
        """Test SceneOutput default values."""
        output = SceneOutput(input=3)
        
        assert output.input == 3
        assert output.enabled is True
        assert output.audio_mute is False
        assert output.hdr_mode is None
        assert output.hdcp_mode is None
    
    def test_to_dict_minimal(self):
        """Test to_dict with minimal config."""
        output = SceneOutput(input=5)
        
        result = output.to_dict()
        
        assert result["input"] == 5
        assert result["enabled"] is True
        assert result["audio_mute"] is False
        assert "hdr_mode" not in result
        assert "hdcp_mode" not in result
    
    def test_to_dict_full(self):
        """Test to_dict with all fields."""
        output = SceneOutput(
            input=2,
            enabled=False,
            audio_mute=True,
            hdr_mode=3,
            hdcp_mode=2,
        )
        
        result = output.to_dict()
        
        assert result["input"] == 2
        assert result["enabled"] is False
        assert result["audio_mute"] is True
        assert result["hdr_mode"] == 3
        assert result["hdcp_mode"] == 2
    
    def test_from_dict(self):
        """Test from_dict creates correct object."""
        data = {
            "input": 4,
            "enabled": False,
            "audio_mute": True,
            "hdr_mode": 1,
            "hdcp_mode": 3,
        }
        
        output = SceneOutput.from_dict(data)
        
        assert output.input == 4
        assert output.enabled is False
        assert output.audio_mute is True
        assert output.hdr_mode == 1
        assert output.hdcp_mode == 3
    
    def test_from_dict_missing_fields(self):
        """Test from_dict handles missing fields."""
        data = {"input": 6}
        
        output = SceneOutput.from_dict(data)
        
        assert output.input == 6
        assert output.enabled is True  # Default
        assert output.audio_mute is False  # Default
        assert output.hdr_mode is None
        assert output.hdcp_mode is None
    
    def test_roundtrip_serialization(self):
        """Test to_dict/from_dict roundtrip."""
        original = SceneOutput(
            input=7,
            enabled=False,
            audio_mute=True,
            hdr_mode=2,
            hdcp_mode=1,
        )
        
        result = SceneOutput.from_dict(original.to_dict())
        
        assert result.input == original.input
        assert result.enabled == original.enabled
        assert result.audio_mute == original.audio_mute
        assert result.hdr_mode == original.hdr_mode
        assert result.hdcp_mode == original.hdcp_mode


# =============================================================================
# Scene Tests
# =============================================================================

class TestScene:
    """Tests for Scene dataclass."""
    
    def test_basic_creation(self):
        """Test basic Scene creation."""
        scene = Scene(id="test", name="Test Scene")
        
        assert scene.id == "test"
        assert scene.name == "Test Scene"
        assert scene.outputs == {}
        assert scene.cec_config is None
    
    def test_with_outputs(self):
        """Test Scene with outputs."""
        outputs = {
            1: SceneOutput(input=3),
            2: SceneOutput(input=5, audio_mute=True),
        }
        scene = Scene(id="multi", name="Multi Output", outputs=outputs)
        
        assert len(scene.outputs) == 2
        assert scene.outputs[1].input == 3
        assert scene.outputs[2].input == 5
        assert scene.outputs[2].audio_mute is True
    
    def test_to_dict(self):
        """Test Scene.to_dict() serialization."""
        scene = Scene(
            id="movie",
            name="Movie Night",
            outputs={
                1: SceneOutput(input=1),
                4: SceneOutput(input=2, audio_mute=True),
            },
            cec_config=CecConfig(nav_targets=["input:1"]),
        )
        
        result = scene.to_dict()
        
        assert result["id"] == "movie"
        assert result["name"] == "Movie Night"
        assert "1" in result["outputs"]
        assert "4" in result["outputs"]
        assert result["outputs"]["1"]["input"] == 1
        assert result["outputs"]["4"]["audio_mute"] is True
        assert result["cec_config"]["nav_targets"] == ["input:1"]
    
    def test_to_dict_without_cec(self):
        """Test to_dict without CEC config excludes field."""
        scene = Scene(id="simple", name="Simple")
        
        result = scene.to_dict()
        
        assert "cec_config" not in result
    
    def test_from_dict(self):
        """Test Scene.from_dict() deserialization."""
        data = {
            "id": "gaming",
            "name": "Gaming Mode",
            "outputs": {
                "1": {"input": 2},
                "3": {"input": 4, "enabled": False},
            },
            "cec_config": {
                "nav_targets": ["input:2"],
                "playback_targets": ["input:4"],
            },
        }
        
        scene = Scene.from_dict(data)
        
        assert scene.id == "gaming"
        assert scene.name == "Gaming Mode"
        assert scene.outputs[1].input == 2
        assert scene.outputs[3].input == 4
        assert scene.outputs[3].enabled is False
        assert scene.cec_config.nav_targets == ["input:2"]
        assert scene.cec_config.playback_targets == ["input:4"]
    
    def test_from_dict_missing_fields(self):
        """Test from_dict with minimal data."""
        data = {"id": "min", "name": "Minimal"}
        
        scene = Scene.from_dict(data)
        
        assert scene.id == "min"
        assert scene.name == "Minimal"
        assert scene.outputs == {}
        assert scene.cec_config is None
    
    def test_get_active_inputs(self):
        """Test get_active_inputs returns correct set."""
        scene = Scene(
            id="test",
            name="Test",
            outputs={
                1: SceneOutput(input=3, enabled=True),
                2: SceneOutput(input=5, enabled=True),
                3: SceneOutput(input=3, enabled=False),  # Disabled
                4: SceneOutput(input=7, enabled=True),
            },
        )
        
        active = scene.get_active_inputs()
        
        assert active == {3, 5, 7}  # Input 3 counted once, disabled output excluded
    
    def test_has_cec_config(self):
        """Test has_cec_config() method."""
        scene_without = Scene(id="no_cec", name="No CEC")
        scene_with = Scene(id="with_cec", name="With CEC", cec_config=CecConfig())
        
        assert scene_without.has_cec_config() is False
        assert scene_with.has_cec_config() is True
    
    def test_ensure_cec_config_creates(self):
        """Test ensure_cec_config creates config if missing."""
        scene = Scene(id="test", name="Test")
        assert scene.cec_config is None
        
        cec = scene.ensure_cec_config()
        
        assert cec is not None
        assert scene.cec_config is cec
        assert cec.auto_resolved is True
    
    def test_ensure_cec_config_returns_existing(self):
        """Test ensure_cec_config returns existing config."""
        existing = CecConfig(nav_targets=["input:1"])
        scene = Scene(id="test", name="Test", cec_config=existing)
        
        cec = scene.ensure_cec_config()
        
        assert cec is existing
        assert cec.nav_targets == ["input:1"]


# =============================================================================
# SceneManager Tests
# =============================================================================

class TestSceneManager:
    """Tests for SceneManager class."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_init_creates_empty_scenes(self, temp_config_dir):
        """Test SceneManager initializes with empty scenes."""
        manager = SceneManager(config_dir=temp_config_dir)
        
        assert manager.list_scenes() == []
    
    def test_create_scene(self, temp_config_dir):
        """Test creating a scene."""
        manager = SceneManager(config_dir=temp_config_dir)
        
        scene = manager.create_scene(
            scene_id="test_scene",
            name="Test Scene",
            outputs={1: {"input": 3}, 2: {"input": 5}},
        )
        
        assert scene.id == "test_scene"
        assert scene.name == "Test Scene"
        assert scene.outputs[1].input == 3
        assert scene.outputs[2].input == 5
    
    def test_create_scene_with_cec(self, temp_config_dir):
        """Test creating scene with CEC config."""
        manager = SceneManager(config_dir=temp_config_dir)
        
        scene = manager.create_scene(
            scene_id="cec_scene",
            name="CEC Scene",
            outputs={1: {"input": 1}},
            cec_config={"nav_targets": ["input:1"]},
        )
        
        assert scene.cec_config is not None
        assert scene.cec_config.nav_targets == ["input:1"]
    
    def test_get_scene(self, temp_config_dir):
        """Test getting a scene by ID."""
        manager = SceneManager(config_dir=temp_config_dir)
        manager.create_scene("scene1", "Scene 1", {1: {"input": 1}})
        
        scene = manager.get_scene("scene1")
        
        assert scene is not None
        assert scene.name == "Scene 1"
    
    def test_get_scene_not_found(self, temp_config_dir):
        """Test getting non-existent scene returns None."""
        manager = SceneManager(config_dir=temp_config_dir)
        
        scene = manager.get_scene("nonexistent")
        
        assert scene is None
    
    def test_list_scenes(self, temp_config_dir):
        """Test listing scenes."""
        manager = SceneManager(config_dir=temp_config_dir)
        manager.create_scene("s1", "Scene 1", {1: {"input": 1}})
        manager.create_scene("s2", "Scene 2", {1: {"input": 2}, 2: {"input": 3}})
        
        scenes = manager.list_scenes()
        
        assert len(scenes) == 2
        scene_ids = [s["id"] for s in scenes]
        assert "s1" in scene_ids
        assert "s2" in scene_ids
        
        s2 = next(s for s in scenes if s["id"] == "s2")
        assert s2["output_count"] == 2
    
    def test_delete_scene(self, temp_config_dir):
        """Test deleting a scene."""
        manager = SceneManager(config_dir=temp_config_dir)
        manager.create_scene("to_delete", "To Delete", {1: {"input": 1}})
        
        result = manager.delete_scene("to_delete")
        
        assert result is True
        assert manager.get_scene("to_delete") is None
    
    def test_delete_scene_not_found(self, temp_config_dir):
        """Test deleting non-existent scene returns False."""
        manager = SceneManager(config_dir=temp_config_dir)
        
        result = manager.delete_scene("nonexistent")
        
        assert result is False
    
    def test_update_scene_cec_config(self, temp_config_dir):
        """Test updating scene CEC config."""
        manager = SceneManager(config_dir=temp_config_dir)
        manager.create_scene("scene", "Scene", {1: {"input": 1}})
        
        updated = manager.update_scene_cec_config(
            "scene",
            {"nav_targets": ["input:1"], "volume_targets": ["output:1"]},
        )
        
        assert updated is not None
        assert updated.cec_config.nav_targets == ["input:1"]
        assert updated.cec_config.volume_targets == ["output:1"]
    
    def test_update_scene_cec_config_not_found(self, temp_config_dir):
        """Test updating CEC config for non-existent scene."""
        manager = SceneManager(config_dir=temp_config_dir)
        
        result = manager.update_scene_cec_config("nonexistent", {})
        
        assert result is None
    
    def test_persistence(self, temp_config_dir):
        """Test scenes persist across manager instances."""
        manager1 = SceneManager(config_dir=temp_config_dir)
        manager1.create_scene("persist", "Persistent", {1: {"input": 5}})
        
        # Create new manager instance
        manager2 = SceneManager(config_dir=temp_config_dir)
        
        scene = manager2.get_scene("persist")
        assert scene is not None
        assert scene.name == "Persistent"
        assert scene.outputs[1].input == 5


# =============================================================================
# Profile Tests
# =============================================================================

class TestProfile:
    """Tests for Profile dataclass."""
    
    def test_basic_creation(self):
        """Test basic Profile creation."""
        profile = Profile(id="test", name="Test Profile")
        
        assert profile.id == "test"
        assert profile.name == "Test Profile"
        assert profile.icon == "📺"
        assert profile.outputs == {}
        assert profile.cec_config is None
        assert profile.macros == []
        assert profile.power_on_macro is None
        assert profile.power_off_macro is None
    
    def test_full_creation(self):
        """Test Profile with all fields."""
        profile = Profile(
            id="full",
            name="Full Profile",
            icon="🎮",
            outputs={1: SceneOutput(input=3)},
            cec_config=CecConfig(nav_targets=["input:3"]),
            macros=["macro1", "macro2"],
            power_on_macro="startup",
            power_off_macro="shutdown",
        )
        
        assert profile.icon == "🎮"
        assert profile.macros == ["macro1", "macro2"]
        assert profile.power_on_macro == "startup"
        assert profile.power_off_macro == "shutdown"
    
    def test_to_dict(self):
        """Test Profile.to_dict() serialization."""
        profile = Profile(
            id="movie",
            name="Movie Night",
            icon="🎬",
            outputs={1: SceneOutput(input=1)},
            cec_config=CecConfig(volume_targets=["output:1"]),
            macros=["vol_up", "vol_down"],
            power_on_macro="tv_on",
            power_off_macro="tv_off",
        )
        
        result = profile.to_dict()
        
        assert result["id"] == "movie"
        assert result["name"] == "Movie Night"
        assert result["icon"] == "🎬"
        assert result["macros"] == ["vol_up", "vol_down"]
        assert result["power_on_macro"] == "tv_on"
        assert result["power_off_macro"] == "tv_off"
        assert "cec_config" in result
    
    def test_to_dict_without_optional_fields(self):
        """Test to_dict excludes empty optional fields."""
        profile = Profile(id="simple", name="Simple")
        
        result = profile.to_dict()
        
        assert "cec_config" not in result
        assert "power_on_macro" not in result
        assert "power_off_macro" not in result
        assert result["macros"] == []  # Always included
    
    def test_from_dict(self):
        """Test Profile.from_dict() deserialization."""
        data = {
            "id": "gaming",
            "name": "Gaming Mode",
            "icon": "🎮",
            "outputs": {"1": {"input": 2}},
            "cec_config": {"nav_targets": ["input:2"]},
            "macros": ["pause", "screenshot"],
            "power_on_macro": "game_mode_on",
            "power_off_macro": "game_mode_off",
        }
        
        profile = Profile.from_dict(data)
        
        assert profile.id == "gaming"
        assert profile.name == "Gaming Mode"
        assert profile.icon == "🎮"
        assert profile.outputs[1].input == 2
        assert profile.macros == ["pause", "screenshot"]
        assert profile.power_on_macro == "game_mode_on"
        assert profile.power_off_macro == "game_mode_off"
    
    def test_from_scene(self):
        """Test Profile.from_scene() conversion."""
        scene = Scene(
            id="scene1",
            name="Scene One",
            outputs={1: SceneOutput(input=3)},
            cec_config=CecConfig(nav_targets=["input:3"]),
        )
        
        profile = Profile.from_scene(scene)
        
        assert profile.id == "scene1"
        assert profile.name == "Scene One"
        assert profile.outputs[1].input == 3
        assert profile.cec_config.nav_targets == ["input:3"]
        assert profile.macros == []  # New field
        assert profile.power_on_macro is None
    
    def test_to_scene(self):
        """Test Profile.to_scene() conversion."""
        profile = Profile(
            id="profile1",
            name="Profile One",
            outputs={2: SceneOutput(input=5)},
            cec_config=CecConfig(volume_targets=["output:1"]),
            macros=["macro1"],  # Should be dropped
        )
        
        scene = profile.to_scene()
        
        assert scene.id == "profile1"
        assert scene.name == "Profile One"
        assert scene.outputs[2].input == 5
        assert scene.cec_config.volume_targets == ["output:1"]
    
    def test_get_active_inputs(self):
        """Test get_active_inputs returns correct set."""
        profile = Profile(
            id="test",
            name="Test",
            outputs={
                1: SceneOutput(input=2, enabled=True),
                2: SceneOutput(input=4, enabled=False),  # Disabled
                3: SceneOutput(input=2, enabled=True),   # Duplicate input
            },
        )
        
        active = profile.get_active_inputs()
        
        assert active == {2}
    
    def test_has_cec_config(self):
        """Test has_cec_config() method."""
        profile_without = Profile(id="no", name="No CEC")
        profile_with = Profile(id="yes", name="With CEC", cec_config=CecConfig())
        
        assert profile_without.has_cec_config() is False
        assert profile_with.has_cec_config() is True
    
    def test_ensure_cec_config(self):
        """Test ensure_cec_config creates or returns config."""
        profile = Profile(id="test", name="Test")
        assert profile.cec_config is None
        
        cec = profile.ensure_cec_config()
        
        assert cec is not None
        assert profile.cec_config is cec


# =============================================================================
# ProfileManager Tests
# =============================================================================

class TestProfileManager:
    """Tests for ProfileManager class."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_init_empty(self, temp_config_dir):
        """Test ProfileManager initializes with empty profiles."""
        manager = ProfileManager(config_dir=temp_config_dir)
        
        assert manager.list_profiles() == []
    
    def test_create_profile_minimal(self, temp_config_dir):
        """Test creating profile with minimal data."""
        manager = ProfileManager(config_dir=temp_config_dir)
        
        profile = manager.create_profile(
            profile_id="basic",
            name="Basic Profile",
            outputs={1: {"input": 1}},
        )
        
        assert profile.id == "basic"
        assert profile.name == "Basic Profile"
        assert profile.icon == "📺"  # Default
    
    def test_create_profile_full(self, temp_config_dir):
        """Test creating profile with all fields."""
        manager = ProfileManager(config_dir=temp_config_dir)
        
        profile = manager.create_profile(
            profile_id="full",
            name="Full Profile",
            outputs={1: {"input": 3}, 2: {"input": 5}},
            icon="🎬",
            cec_config={"nav_targets": ["input:3"]},
            macros=["m1", "m2"],
            power_on_macro="on_macro",
            power_off_macro="off_macro",
        )
        
        assert profile.id == "full"
        assert profile.icon == "🎬"
        assert profile.macros == ["m1", "m2"]
        assert profile.power_on_macro == "on_macro"
        assert profile.power_off_macro == "off_macro"
        assert profile.outputs[1].input == 3
        assert profile.cec_config.nav_targets == ["input:3"]
    
    def test_get_profile(self, temp_config_dir):
        """Test getting profile by ID."""
        manager = ProfileManager(config_dir=temp_config_dir)
        manager.create_profile("p1", "Profile 1", {1: {"input": 1}})
        
        profile = manager.get_profile("p1")
        
        assert profile is not None
        assert profile.name == "Profile 1"
    
    def test_get_profile_not_found(self, temp_config_dir):
        """Test getting non-existent profile returns None."""
        manager = ProfileManager(config_dir=temp_config_dir)
        
        profile = manager.get_profile("nonexistent")
        
        assert profile is None
    
    def test_list_profiles(self, temp_config_dir):
        """Test listing all profiles."""
        manager = ProfileManager(config_dir=temp_config_dir)
        manager.create_profile("p1", "Profile 1", {1: {"input": 1}}, macros=["m1"])
        manager.create_profile("p2", "Profile 2", {1: {"input": 2}}, icon="🎮")
        
        profiles = manager.list_profiles()
        
        assert len(profiles) == 2
        
        p1 = next(p for p in profiles if p["id"] == "p1")
        assert p1["name"] == "Profile 1"
        assert p1["macro_count"] == 1
        
        p2 = next(p for p in profiles if p["id"] == "p2")
        assert p2["icon"] == "🎮"
    
    def test_update_profile(self, temp_config_dir):
        """Test updating profile fields."""
        manager = ProfileManager(config_dir=temp_config_dir)
        manager.create_profile("update_test", "Original", {1: {"input": 1}})
        
        updated = manager.update_profile(
            "update_test",
            name="Updated Name",
            icon="🎵",
            macros=["new_macro"],
        )
        
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.icon == "🎵"
        assert updated.macros == ["new_macro"]
    
    def test_update_profile_partial(self, temp_config_dir):
        """Test partial update preserves unchanged fields."""
        manager = ProfileManager(config_dir=temp_config_dir)
        manager.create_profile(
            "partial",
            "Original",
            {1: {"input": 1}},
            icon="🎮",
            macros=["m1"],
        )
        
        updated = manager.update_profile("partial", name="New Name")
        
        assert updated.name == "New Name"
        assert updated.icon == "🎮"  # Preserved
        assert updated.macros == ["m1"]  # Preserved
    
    def test_update_profile_not_found(self, temp_config_dir):
        """Test updating non-existent profile returns None."""
        manager = ProfileManager(config_dir=temp_config_dir)
        
        result = manager.update_profile("nonexistent", name="New")
        
        assert result is None
    
    def test_delete_profile(self, temp_config_dir):
        """Test deleting a profile."""
        manager = ProfileManager(config_dir=temp_config_dir)
        manager.create_profile("to_delete", "Delete Me", {1: {"input": 1}})
        
        result = manager.delete_profile("to_delete")
        
        assert result is True
        assert manager.get_profile("to_delete") is None
    
    def test_delete_profile_not_found(self, temp_config_dir):
        """Test deleting non-existent profile returns False."""
        manager = ProfileManager(config_dir=temp_config_dir)
        
        result = manager.delete_profile("nonexistent")
        
        assert result is False
    
    def test_persistence(self, temp_config_dir):
        """Test profiles persist across manager instances."""
        manager1 = ProfileManager(config_dir=temp_config_dir)
        manager1.create_profile(
            "persist",
            "Persistent",
            {1: {"input": 7}},
            icon="💾",
            macros=["saved_macro"],
        )
        
        # Create new manager instance
        manager2 = ProfileManager(config_dir=temp_config_dir)
        
        profile = manager2.get_profile("persist")
        assert profile is not None
        assert profile.name == "Persistent"
        assert profile.icon == "💾"
        assert profile.macros == ["saved_macro"]
        assert profile.outputs[1].input == 7
    
    def test_migrate_from_scenes(self, temp_config_dir):
        """Test migration from scenes.json to profiles.json."""
        # Create a legacy scenes.json
        scenes_data = {
            "scenes": [
                {
                    "id": "legacy",
                    "name": "Legacy Scene",
                    "outputs": {"1": {"input": 4}},
                    "cec_config": {"nav_targets": ["input:4"]},
                }
            ]
        }
        scenes_file = os.path.join(temp_config_dir, "scenes.json")
        with open(scenes_file, "w") as f:
            json.dump(scenes_data, f)
        
        # Create ProfileManager - should migrate
        manager = ProfileManager(config_dir=temp_config_dir)
        
        # Verify migration
        profile = manager.get_profile("legacy")
        assert profile is not None
        assert profile.name == "Legacy Scene"
        assert profile.outputs[1].input == 4
        assert profile.cec_config.nav_targets == ["input:4"]
        
        # Verify profiles.json was created
        assert os.path.exists(os.path.join(temp_config_dir, "profiles.json"))
    
    def test_backward_compatibility_methods(self, temp_config_dir):
        """Test Scene-like backward compatibility methods."""
        manager = ProfileManager(config_dir=temp_config_dir)
        
        # create_scene
        manager.create_scene("compat", "Compat Scene", {1: {"input": 1}})
        
        # list_scenes
        scenes = manager.list_scenes()
        assert len(scenes) == 1
        assert scenes[0]["id"] == "compat"
        
        # get_scene
        scene = manager.get_scene("compat")
        assert scene is not None
        assert scene.name == "Compat Scene"
        
        # update_scene_cec_config
        updated = manager.update_scene_cec_config("compat", {"nav_targets": ["input:1"]})
        assert updated.cec_config.nav_targets == ["input:1"]
        
        # delete_scene
        result = manager.delete_scene("compat")
        assert result is True
        assert manager.get_scene("compat") is None


# =============================================================================
# MatrixConfig Tests
# =============================================================================

class TestMatrixConfig:
    """Tests for MatrixConfig dataclass."""
    
    def test_default_values(self):
        """Test MatrixConfig default values."""
        config = MatrixConfig(host="192.168.1.100")
        
        assert config.host == "192.168.1.100"
        assert config.port == 443
        assert config.name == "OREI Matrix"
    
    def test_custom_values(self):
        """Test MatrixConfig with custom values."""
        config = MatrixConfig(host="10.0.0.50", port=8080, name="Living Room Matrix")
        
        assert config.host == "10.0.0.50"
        assert config.port == 8080
        assert config.name == "Living Room Matrix"
    
    def test_to_dict(self):
        """Test MatrixConfig.to_dict() serialization."""
        config = MatrixConfig(host="192.168.1.200", port=23, name="Office Matrix")
        
        result = config.to_dict()
        
        assert result["host"] == "192.168.1.200"
        assert result["port"] == 23
        assert result["name"] == "Office Matrix"
    
    def test_from_dict(self):
        """Test MatrixConfig.from_dict() deserialization."""
        data = {"host": "192.168.2.100", "port": 443, "name": "Theater"}
        
        config = MatrixConfig.from_dict(data)
        
        assert config.host == "192.168.2.100"
        assert config.port == 443
        assert config.name == "Theater"
    
    def test_from_dict_missing_fields(self):
        """Test from_dict uses defaults for missing fields."""
        data = {}
        
        config = MatrixConfig.from_dict(data)
        
        assert config.host == "192.168.1.100"  # Default
        assert config.port == 23  # Default (note: different from dataclass default)
        assert config.name == "OREI Matrix"  # Default


# =============================================================================
# Config (Main Manager) Tests
# =============================================================================

class TestConfig:
    """Tests for Config class."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary config directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_init(self, temp_config_dir):
        """Test Config initialization."""
        config = Config(config_dir=temp_config_dir)
        
        assert config.config_dir == temp_config_dir
        assert config.matrix is None
    
    def test_set_matrix_config(self, temp_config_dir):
        """Test setting matrix configuration."""
        config = Config(config_dir=temp_config_dir)
        
        config.set_matrix_config("192.168.1.150", port=23, name="Test Matrix")
        
        assert config.matrix is not None
        assert config.matrix.host == "192.168.1.150"
        assert config.matrix.port == 23
        assert config.matrix.name == "Test Matrix"
    
    def test_save_and_load(self, temp_config_dir):
        """Test save and load configuration."""
        config1 = Config(config_dir=temp_config_dir)
        config1.set_matrix_config("10.0.0.100", port=8080, name="Saved Matrix")
        
        # Create new config instance and load
        config2 = Config(config_dir=temp_config_dir)
        result = config2.load()
        
        assert result is True
        assert config2.matrix is not None
        assert config2.matrix.host == "10.0.0.100"
        assert config2.matrix.port == 8080
        assert config2.matrix.name == "Saved Matrix"
    
    def test_load_nonexistent_file(self, temp_config_dir):
        """Test load returns False when file doesn't exist."""
        config = Config(config_dir=temp_config_dir)
        
        result = config.load()
        
        assert result is False
        assert config.matrix is None
    
    def test_save_without_config(self, temp_config_dir):
        """Test save returns False when no config set."""
        config = Config(config_dir=temp_config_dir)
        
        result = config.save()
        
        assert result is False
