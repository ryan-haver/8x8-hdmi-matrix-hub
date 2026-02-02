"""
Tests for CEC resolver functionality.

Tests the CEC auto-resolution logic for scenes:
- Volume target resolution (audio-only > ARC-enabled > first output)
- Navigation/playback target resolution
- Power target resolution
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports (conftest.py also does this)
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from cec_resolver import (
    resolve_volume_targets,
    resolve_power_targets,
    resolve_scene_cec_config,
    create_empty_cec_config,
)


class TestVolumeTargetResolution:
    """Test volume target resolution priority."""
    
    def test_audio_only_output_preferred(self):
        """Audio-only outputs (scaler=4) should be preferred."""
        active_outputs = {1, 2, 3}
        status = {
            "allscaler": [0, 4, 0],  # Output 2 is audio-only (0-indexed: 4 = audio only)
            "allarc": [1, 1, 1],
            "allconnect": [1, 1, 1],  # All connected (integers)
        }
        
        targets = resolve_volume_targets(active_outputs, status)
        
        assert len(targets) == 1
        assert targets[0] == "output_2"
    
    def test_arc_enabled_preferred_when_no_audio_only(self):
        """ARC-enabled outputs should be preferred when no audio-only."""
        active_outputs = {1, 2, 3}
        status = {
            "allscaler": [0, 1, 0],  # No audio-only
            "allarc": [0, 1, 0],     # Output 2 has ARC (integer 1)
            "allconnect": [1, 1, 1],
        }
        
        targets = resolve_volume_targets(active_outputs, status)
        
        assert len(targets) == 1
        assert targets[0] == "output_2"
    
    def test_first_output_fallback(self):
        """Falls back to first output when no audio-only or ARC."""
        active_outputs = {2, 3, 4}
        status = {
            "allscaler": [0, 0, 0, 0],
            "allarc": [0, 0, 0, 0],
            "allconnect": [1, 1, 1, 1],
        }
        
        targets = resolve_volume_targets(active_outputs, status)
        
        assert len(targets) == 1
        assert targets[0] == "output_2"  # First in sorted order
    
    def test_empty_outputs(self):
        """Returns empty list when no outputs specified."""
        targets = resolve_volume_targets(set(), {})
        assert targets == []


class TestPowerTargetResolution:
    """Test power target resolution."""
    
    def test_power_targets_include_inputs_and_outputs(self):
        """Power on includes inputs+outputs, power off includes only outputs."""
        active_inputs = {1, 3}
        active_outputs = {1, 2}
        
        power_on, power_off = resolve_power_targets(active_inputs, active_outputs)
        
        # Power on includes all inputs and outputs
        assert "input_1" in power_on
        assert "input_3" in power_on
        assert "output_1" in power_on
        assert "output_2" in power_on
        
        # Power off only includes outputs (users want sources to stay on)
        assert "input_1" not in power_off
        assert "input_3" not in power_off
        assert "output_1" in power_off
        assert "output_2" in power_off
    
    def test_empty_inputs_outputs(self):
        """Returns empty lists when no inputs/outputs."""
        power_on, power_off = resolve_power_targets(set(), set())
        assert power_on == []
        assert power_off == []


class TestSceneCecConfigResolution:
    """Test complete scene CEC config resolution."""
    
    def test_complete_resolution(self):
        """Test complete CEC config resolution for a scene."""
        config = resolve_scene_cec_config(
            active_inputs=[1, 3],
            active_outputs=[1, 2],
            status={
                "allscaler": [0, 4],  # Output 2 is audio-only (0-indexed)
                "allarc": [0, 0],
                "allconnect": [1, 1],  # Both connected (integers)
            }
        )
        
        assert config["auto_resolved"] is True
        assert config["nav_targets"] == ["input_1"]  # Primary input
        assert config["playback_targets"] == ["input_1"]
        assert config["volume_targets"] == ["output_2"]  # Audio-only output
        assert "input_1" in config["power_on_targets"]
        assert "input_3" in config["power_on_targets"]
    
    def test_empty_scene(self):
        """Empty scene returns empty config."""
        config = resolve_scene_cec_config(
            active_inputs=[],
            active_outputs=[],
            status={}
        )
        
        expected = create_empty_cec_config()
        assert config == expected


class TestEmptyCecConfig:
    """Test empty CEC config creation."""
    
    def test_empty_config_structure(self):
        """Empty config has all required fields."""
        config = create_empty_cec_config()
        
        assert "auto_resolved" in config
        assert "nav_targets" in config
        assert "playback_targets" in config
        assert "volume_targets" in config
        assert "power_on_targets" in config
        assert "power_off_targets" in config
        
        # Default empty config has auto_resolved=True as a baseline
        assert config["auto_resolved"] is True
        assert config["nav_targets"] == []
        assert config["playback_targets"] == []
        assert config["volume_targets"] == []
        assert config["power_on_targets"] == []
        assert config["power_off_targets"] == []
