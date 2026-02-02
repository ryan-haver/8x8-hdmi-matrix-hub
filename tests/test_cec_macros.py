#!/usr/bin/env python3
"""
Unit tests for CEC Macros module.

Tests cover:
- MacroStep and CecMacro dataclasses
- MacroManager CRUD operations
- Macro execution and validation
- Target parsing
- File persistence

Run with: pytest tests/test_cec_macros.py -v
"""
import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cec_macros import MacroStep, CecMacro, MacroManager


# =============================================================================
# MacroStep Tests
# =============================================================================

class TestMacroStep:
    """Tests for MacroStep dataclass."""

    def test_create_basic_step(self):
        """Test creating a basic macro step."""
        step = MacroStep(
            command="POWER_ON",
            targets=["input_1", "output_2"],
            delay_ms=500
        )
        assert step.command == "POWER_ON"
        assert step.targets == ["input_1", "output_2"]
        assert step.delay_ms == 500

    def test_default_values(self):
        """Test default values for optional fields."""
        step = MacroStep(command="PLAY")
        assert step.targets == []
        assert step.delay_ms == 0

    def test_to_dict(self):
        """Test serialization to dictionary."""
        step = MacroStep(
            command="VOLUME_UP",
            targets=["output_1"],
            delay_ms=100
        )
        data = step.to_dict()
        assert data == {
            "command": "VOLUME_UP",
            "targets": ["output_1"],
            "delay_ms": 100
        }

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "command": "MUTE",
            "targets": ["output_1", "output_2"],
            "delay_ms": 200
        }
        step = MacroStep.from_dict(data)
        assert step.command == "MUTE"
        assert step.targets == ["output_1", "output_2"]
        assert step.delay_ms == 200

    def test_from_dict_missing_fields(self):
        """Test deserialization handles missing optional fields."""
        data = {"command": "STOP"}
        step = MacroStep.from_dict(data)
        assert step.command == "STOP"
        assert step.targets == []
        assert step.delay_ms == 0


# =============================================================================
# CecMacro Tests
# =============================================================================

class TestCecMacro:
    """Tests for CecMacro dataclass."""

    def test_create_macro(self):
        """Test creating a CEC macro."""
        steps = [
            MacroStep(command="POWER_ON", targets=["input_1"]),
            MacroStep(command="POWER_ON", targets=["output_1"], delay_ms=1000),
        ]
        macro = CecMacro(
            id="test_macro",
            name="Test Macro",
            icon="🎬",
            description="A test macro",
            steps=steps
        )
        assert macro.id == "test_macro"
        assert macro.name == "Test Macro"
        assert macro.icon == "🎬"
        assert len(macro.steps) == 2
        assert macro.created_at  # Should be auto-set
        assert macro.updated_at  # Should be auto-set

    def test_default_icon(self):
        """Test default icon is set."""
        macro = CecMacro(id="m1", name="Macro 1")
        assert macro.icon == "⚡"

    def test_to_dict(self):
        """Test serialization to dictionary."""
        steps = [MacroStep(command="PLAY", targets=["input_1"])]
        macro = CecMacro(
            id="m1",
            name="Movie Mode",
            steps=steps,
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-01T00:00:00Z"
        )
        data = macro.to_dict()
        assert data["id"] == "m1"
        assert data["name"] == "Movie Mode"
        assert len(data["steps"]) == 1
        assert data["steps"][0]["command"] == "PLAY"

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "id": "m2",
            "name": "Night Mode",
            "icon": "🌙",
            "description": "For nighttime viewing",
            "steps": [
                {"command": "POWER_OFF", "targets": ["output_1"], "delay_ms": 0}
            ],
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T12:00:00Z"
        }
        macro = CecMacro.from_dict(data)
        assert macro.id == "m2"
        assert macro.name == "Night Mode"
        assert macro.icon == "🌙"
        assert len(macro.steps) == 1
        assert macro.steps[0].command == "POWER_OFF"

    def test_update_timestamp(self):
        """Test updating the timestamp."""
        macro = CecMacro(
            id="m1",
            name="Test",
            updated_at="2026-01-01T00:00:00Z"
        )
        old_updated = macro.updated_at
        macro.update_timestamp()
        assert macro.updated_at != old_updated


# =============================================================================
# MacroManager Tests
# =============================================================================

class TestMacroManager:
    """Tests for MacroManager class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def manager(self, temp_dir):
        """Create a MacroManager with a temp directory."""
        return MacroManager(config_dir=temp_dir)

    def test_init_creates_empty_macros(self, manager):
        """Test initialization with no existing file."""
        assert manager.list_macros() == []

    def test_create_macro(self, manager):
        """Test creating a new macro."""
        macro = manager.create_macro(
            name="Power On All",
            steps=[
                {"command": "POWER_ON", "targets": ["input_1", "output_1"]}
            ],
            icon="⚡",
            description="Powers on all devices"
        )
        assert macro.id.startswith("macro_")
        assert macro.name == "Power On All"
        assert len(macro.steps) == 1

    def test_create_macro_with_custom_id(self, manager):
        """Test creating a macro with a custom ID."""
        macro = manager.create_macro(
            name="Custom ID Macro",
            steps=[{"command": "PLAY", "targets": ["input_1"]}],
            macro_id="my_custom_macro"
        )
        assert macro.id == "my_custom_macro"

    def test_list_macros(self, manager):
        """Test listing macros returns summaries."""
        manager.create_macro(
            name="Macro A",
            steps=[{"command": "POWER_ON", "targets": ["input_1"]}]
        )
        manager.create_macro(
            name="Macro B",
            steps=[
                {"command": "POWER_ON", "targets": ["input_1"]},
                {"command": "POWER_ON", "targets": ["output_1"]}
            ]
        )
        
        macros = manager.list_macros()
        assert len(macros) == 2
        
        # Check summary fields
        names = [m["name"] for m in macros]
        assert "Macro A" in names
        assert "Macro B" in names
        
        # Check step counts
        macro_b = next(m for m in macros if m["name"] == "Macro B")
        assert macro_b["step_count"] == 2

    def test_get_macro(self, manager):
        """Test getting a macro by ID."""
        created = manager.create_macro(
            name="Get Test",
            steps=[{"command": "STOP", "targets": ["input_2"]}]
        )
        
        macro = manager.get_macro(created.id)
        assert macro is not None
        assert macro.name == "Get Test"
        assert macro.steps[0].command == "STOP"

    def test_get_macro_not_found(self, manager):
        """Test getting a non-existent macro returns None."""
        macro = manager.get_macro("nonexistent_id")
        assert macro is None

    def test_update_macro(self, manager):
        """Test updating a macro."""
        created = manager.create_macro(
            name="Original Name",
            steps=[{"command": "PLAY", "targets": ["input_1"]}],
            icon="⚡"
        )
        
        updated = manager.update_macro(
            macro_id=created.id,
            name="Updated Name",
            icon="🎬"
        )
        
        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.icon == "🎬"
        # Steps should remain unchanged
        assert len(updated.steps) == 1
        assert updated.steps[0].command == "PLAY"

    def test_update_macro_steps(self, manager):
        """Test updating macro steps."""
        created = manager.create_macro(
            name="Steps Test",
            steps=[{"command": "PLAY", "targets": ["input_1"]}]
        )
        
        new_steps = [
            {"command": "POWER_ON", "targets": ["input_1"]},
            {"command": "POWER_ON", "targets": ["output_1"], "delay_ms": 1000}
        ]
        
        updated = manager.update_macro(
            macro_id=created.id,
            steps=new_steps
        )
        
        assert len(updated.steps) == 2
        assert updated.steps[0].command == "POWER_ON"
        assert updated.steps[1].delay_ms == 1000

    def test_update_macro_not_found(self, manager):
        """Test updating a non-existent macro returns None."""
        result = manager.update_macro(
            macro_id="nonexistent",
            name="New Name"
        )
        assert result is None

    def test_delete_macro(self, manager):
        """Test deleting a macro."""
        created = manager.create_macro(
            name="To Delete",
            steps=[{"command": "STOP", "targets": ["input_1"]}]
        )
        
        assert manager.delete_macro(created.id) is True
        assert manager.get_macro(created.id) is None

    def test_delete_macro_not_found(self, manager):
        """Test deleting a non-existent macro returns False."""
        result = manager.delete_macro("nonexistent_id")
        assert result is False

    def test_persistence(self, temp_dir):
        """Test that macros persist across manager instances."""
        # Create manager and add macro
        manager1 = MacroManager(config_dir=temp_dir)
        manager1.create_macro(
            name="Persistent Macro",
            steps=[{"command": "MUTE", "targets": ["output_1"]}],
            macro_id="persistent_test"
        )
        
        # Create new manager instance (simulates restart)
        manager2 = MacroManager(config_dir=temp_dir)
        
        # Macro should still exist
        macro = manager2.get_macro("persistent_test")
        assert macro is not None
        assert macro.name == "Persistent Macro"

    def test_file_format(self, temp_dir):
        """Test the saved file format."""
        manager = MacroManager(config_dir=temp_dir)
        manager.create_macro(
            name="Format Test",
            steps=[{"command": "PLAY", "targets": ["input_1"]}],
            macro_id="format_test"
        )
        
        # Read the file directly
        file_path = os.path.join(temp_dir, "cec_macros.json")
        with open(file_path, "r") as f:
            data = json.load(f)
        
        assert "version" in data
        assert data["version"] == 1
        assert "macros" in data
        assert len(data["macros"]) == 1
        assert data["macros"][0]["id"] == "format_test"


# =============================================================================
# Target Parsing Tests
# =============================================================================

class TestTargetParsing:
    """Tests for target string parsing."""

    @pytest.fixture
    def manager(self):
        """Create a MacroManager for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield MacroManager(config_dir=tmpdir)

    def test_parse_input_target(self, manager):
        """Test parsing input targets."""
        target_type, port = manager._parse_target("input_1")
        assert target_type == "input"
        assert port == 1

    def test_parse_output_target(self, manager):
        """Test parsing output targets."""
        target_type, port = manager._parse_target("output_8")
        assert target_type == "output"
        assert port == 8

    def test_parse_invalid_format(self, manager):
        """Test parsing invalid target format."""
        with pytest.raises(ValueError, match="Invalid target format"):
            manager._parse_target("invalid")

    def test_parse_invalid_type(self, manager):
        """Test parsing invalid target type."""
        with pytest.raises(ValueError, match="Invalid target type"):
            manager._parse_target("display_1")

    def test_parse_invalid_port_number(self, manager):
        """Test parsing invalid port number."""
        with pytest.raises(ValueError, match="Invalid port number"):
            manager._parse_target("input_abc")

    def test_parse_port_out_of_range(self, manager):
        """Test parsing port number out of range."""
        with pytest.raises(ValueError, match="Invalid port number|Port out of range"):
            manager._parse_target("input_9")
        with pytest.raises(ValueError, match="Invalid port number|Port out of range"):
            manager._parse_target("output_0")


# =============================================================================
# Macro Execution Tests
# =============================================================================

class TestMacroExecution:
    """Tests for macro execution."""

    @pytest.fixture
    def manager(self):
        """Create a MacroManager for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield MacroManager(config_dir=tmpdir)

    @pytest.mark.asyncio
    async def test_execute_macro_not_found(self, manager):
        """Test executing a non-existent macro."""
        result = await manager.execute_macro("nonexistent")
        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_macro_no_sender(self, manager):
        """Test executing without CEC sender configured."""
        manager.create_macro(
            name="Test",
            steps=[{"command": "POWER_ON", "targets": ["input_1"]}],
            macro_id="test_macro"
        )
        
        result = await manager.execute_macro("test_macro")
        assert result["success"] is False
        assert "sender not configured" in result["error"]

    @pytest.mark.asyncio
    async def test_execute_macro_success(self, manager):
        """Test successful macro execution."""
        # Create mock CEC sender
        mock_sender = AsyncMock(return_value=True)
        manager.set_cec_sender(mock_sender)
        
        manager.create_macro(
            name="Power On Sequence",
            steps=[
                {"command": "POWER_ON", "targets": ["input_1"]},
                {"command": "POWER_ON", "targets": ["output_1"], "delay_ms": 100}
            ],
            macro_id="power_on_seq"
        )
        
        result = await manager.execute_macro("power_on_seq")
        
        assert result["success"] is True
        assert result["macro_id"] == "power_on_seq"
        assert result["steps_executed"] == 2
        assert len(result["results"]) == 2
        
        # Verify sender was called correctly
        assert mock_sender.call_count == 2
        mock_sender.assert_any_call("input", 1, "POWER_ON")
        mock_sender.assert_any_call("output", 1, "POWER_ON")

    @pytest.mark.asyncio
    async def test_execute_macro_multiple_targets(self, manager):
        """Test macro execution with multiple targets per step."""
        mock_sender = AsyncMock(return_value=True)
        manager.set_cec_sender(mock_sender)
        
        manager.create_macro(
            name="All Power Off",
            steps=[
                {"command": "POWER_OFF", "targets": ["output_1", "output_2", "output_3"]}
            ],
            macro_id="all_power_off"
        )
        
        result = await manager.execute_macro("all_power_off")
        
        assert result["success"] is True
        assert mock_sender.call_count == 3

    @pytest.mark.asyncio
    async def test_execute_macro_partial_failure(self, manager):
        """Test macro execution with partial failures."""
        # Mock sender that fails on output_2
        async def selective_sender(target_type, port, command):
            if target_type == "output" and port == 2:
                return False
            return True
        
        manager.set_cec_sender(selective_sender)
        
        manager.create_macro(
            name="Mixed Results",
            steps=[
                {"command": "POWER_ON", "targets": ["output_1", "output_2", "output_3"]}
            ],
            macro_id="mixed_macro"
        )
        
        result = await manager.execute_macro("mixed_macro")
        
        # Overall should report partial failure
        assert result["success"] is False
        assert result["steps_executed"] == 1
        
        # Step should have errors
        step_result = result["results"][0]
        assert step_result["success"] is False
        assert len(step_result["errors"]) == 1


# =============================================================================
# Macro Validation (Test/Dry Run) Tests
# =============================================================================

class TestMacroValidation:
    """Tests for macro validation (dry run)."""

    @pytest.fixture
    def manager(self):
        """Create a MacroManager for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield MacroManager(config_dir=tmpdir)

    @pytest.mark.asyncio
    async def test_test_macro_not_found(self, manager):
        """Test validating a non-existent macro."""
        result = await manager.test_macro("nonexistent")
        assert result["success"] is False
        assert "not found" in result["error"]

    @pytest.mark.asyncio
    async def test_test_macro_valid(self, manager):
        """Test validating a valid macro."""
        manager.create_macro(
            name="Valid Macro",
            steps=[
                {"command": "POWER_ON", "targets": ["input_1"], "delay_ms": 500},
                {"command": "POWER_ON", "targets": ["output_1"], "delay_ms": 1000}
            ],
            macro_id="valid_macro"
        )
        
        result = await manager.test_macro("valid_macro")
        
        assert result["success"] is True
        assert result["step_count"] == 2
        assert result["estimated_duration_ms"] == 1500
        assert len(result["issues"]) == 0

    @pytest.mark.asyncio
    async def test_test_macro_missing_command(self, manager):
        """Test validating macro with missing command."""
        manager.create_macro(
            name="Bad Macro",
            steps=[
                {"command": "", "targets": ["input_1"]}
            ],
            macro_id="bad_macro"
        )
        
        result = await manager.test_macro("bad_macro")
        
        assert result["success"] is False
        assert any("Missing command" in issue for issue in result["issues"])

    @pytest.mark.asyncio
    async def test_test_macro_no_targets(self, manager):
        """Test validating macro with no targets."""
        manager.create_macro(
            name="No Targets",
            steps=[
                {"command": "POWER_ON", "targets": []}
            ],
            macro_id="no_targets"
        )
        
        result = await manager.test_macro("no_targets")
        
        assert result["success"] is False
        assert any("No targets" in issue for issue in result["issues"])

    @pytest.mark.asyncio
    async def test_test_macro_invalid_target(self, manager):
        """Test validating macro with invalid target."""
        manager.create_macro(
            name="Invalid Target",
            steps=[
                {"command": "POWER_ON", "targets": ["invalid_target"]}
            ],
            macro_id="invalid_target"
        )
        
        result = await manager.test_macro("invalid_target")
        
        assert result["success"] is False
        assert len(result["issues"]) > 0


# =============================================================================
# Run tests if executed directly
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
