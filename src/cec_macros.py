"""
CEC Macros module for OREI HDMI Matrix integration.

CEC Macros are saved sequences of CEC commands that can be executed with a single tap.
They're the building blocks for automation, enabling power-on/power-off sequences
across multiple devices.

:copyright: (c) 2026 by Custom Integration.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

_LOG = logging.getLogger(__name__)


# =============================================================================
# Macro Data Structures
# =============================================================================

@dataclass
class MacroStep:
    """
    A single step in a CEC macro.
    
    Each step specifies a CEC command to send to one or more targets,
    with an optional delay after the command executes.
    """
    
    command: str  # CEC command name (e.g., "POWER_ON", "POWER_OFF")
    targets: list[str] = field(default_factory=list)  # Target strings: "input_1", "output_2", etc.
    delay_ms: int = 0  # Delay AFTER this step executes (milliseconds)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "command": self.command,
            "targets": self.targets,
            "delay_ms": self.delay_ms,
        }
    
    @staticmethod
    def from_dict(data: dict[str, Any]) -> "MacroStep":
        """Create from dictionary."""
        return MacroStep(
            command=data.get("command", ""),
            targets=data.get("targets", []),
            delay_ms=data.get("delay_ms", 0),
        )


@dataclass
class CecMacro:
    """
    A CEC Macro - a named sequence of CEC commands.
    
    Macros can be executed standalone, assigned to profiles for quick access,
    or triggered via the REST API.
    """
    
    id: str  # Unique identifier
    name: str  # Display name (e.g., "Movie Night Power On")
    icon: str = "⚡"  # Optional emoji/icon for display
    description: str = ""  # Optional description
    steps: list[MacroStep] = field(default_factory=list)  # Ordered list of steps
    created_at: str = ""  # ISO timestamp
    updated_at: str = ""  # ISO timestamp
    
    def __post_init__(self):
        """Set timestamps if not provided."""
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @staticmethod
    def from_dict(data: dict[str, Any]) -> "CecMacro":
        """Create from dictionary."""
        steps = [MacroStep.from_dict(s) for s in data.get("steps", [])]
        return CecMacro(
            id=data.get("id", ""),
            name=data.get("name", "Unnamed Macro"),
            icon=data.get("icon", "⚡"),
            description=data.get("description", ""),
            steps=steps,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# =============================================================================
# Macro Manager
# =============================================================================

class MacroManager:
    """
    Manages CEC macros - CRUD operations and execution.
    
    Macros are stored in cec_macros.json in the config directory.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize macro manager.
        
        :param config_dir: Configuration directory path
        """
        if config_dir is None:
            config_dir = os.getenv("UC_CONFIG_HOME") or os.getenv("HOME") or "./"
        
        self.config_dir = config_dir
        self.macros_file = os.path.join(config_dir, "cec_macros.json")
        self._macros: dict[str, CecMacro] = {}
        self._cec_sender = None  # Set by set_cec_sender()
        self.load()
    
    def set_cec_sender(self, sender):
        """
        Set the CEC sender function.
        
        :param sender: Async function(target_type, port, command) -> bool
                       target_type: 'input' or 'output'
                       port: 1-8
                       command: CEC command string
        """
        self._cec_sender = sender
    
    def load(self) -> bool:
        """Load macros from file."""
        if not os.path.exists(self.macros_file):
            _LOG.info("Macros file not found: %s", self.macros_file)
            return False
        
        try:
            with open(self.macros_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._macros = {}
                for macro_data in data.get("macros", []):
                    macro = CecMacro.from_dict(macro_data)
                    self._macros[macro.id] = macro
                _LOG.info("Loaded %d macros", len(self._macros))
                return True
        except Exception as ex:
            _LOG.error("Failed to load macros: %s", ex)
            return False
    
    def save(self) -> bool:
        """Save macros to file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            data = {
                "version": 1,
                "macros": [m.to_dict() for m in self._macros.values()]
            }
            with open(self.macros_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            _LOG.info("Saved %d macros", len(self._macros))
            return True
        except Exception as ex:
            _LOG.error("Failed to save macros: %s", ex)
            return False
    
    # -------------------------------------------------------------------------
    # CRUD Operations
    # -------------------------------------------------------------------------
    
    def list_macros(self) -> list[dict[str, Any]]:
        """
        List all macros (summary info).
        
        :return: List of macro summaries
        """
        return [
            {
                "id": m.id,
                "name": m.name,
                "icon": m.icon,
                "description": m.description,
                "step_count": len(m.steps),
                "created_at": m.created_at,
                "updated_at": m.updated_at,
            }
            for m in self._macros.values()
        ]
    
    def get_macro(self, macro_id: str) -> Optional[CecMacro]:
        """
        Get a macro by ID.
        
        :param macro_id: Macro identifier
        :return: CecMacro or None if not found
        """
        return self._macros.get(macro_id)
    
    def create_macro(
        self,
        name: str,
        steps: list[dict[str, Any]],
        icon: str = "⚡",
        description: str = "",
        macro_id: Optional[str] = None,
    ) -> CecMacro:
        """
        Create a new macro.
        
        :param name: Macro display name
        :param steps: List of step dictionaries
        :param icon: Optional emoji/icon
        :param description: Optional description
        :param macro_id: Optional ID (generated if not provided)
        :return: Created macro
        """
        if macro_id is None:
            macro_id = f"macro_{uuid.uuid4().hex[:8]}"
        
        parsed_steps = [MacroStep.from_dict(s) for s in steps]
        macro = CecMacro(
            id=macro_id,
            name=name,
            icon=icon,
            description=description,
            steps=parsed_steps,
        )
        
        self._macros[macro_id] = macro
        self.save()
        _LOG.info("Created macro: %s (%s)", name, macro_id)
        return macro
    
    def update_macro(
        self,
        macro_id: str,
        name: Optional[str] = None,
        steps: Optional[list[dict[str, Any]]] = None,
        icon: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[CecMacro]:
        """
        Update an existing macro.
        
        :param macro_id: Macro identifier
        :param name: New name (optional)
        :param steps: New steps (optional)
        :param icon: New icon (optional)
        :param description: New description (optional)
        :return: Updated macro or None if not found
        """
        macro = self._macros.get(macro_id)
        if macro is None:
            return None
        
        if name is not None:
            macro.name = name
        if icon is not None:
            macro.icon = icon
        if description is not None:
            macro.description = description
        if steps is not None:
            macro.steps = [MacroStep.from_dict(s) for s in steps]
        
        macro.update_timestamp()
        self.save()
        _LOG.info("Updated macro: %s", macro_id)
        return macro
    
    def delete_macro(self, macro_id: str) -> bool:
        """
        Delete a macro.
        
        :param macro_id: Macro identifier
        :return: True if deleted, False if not found
        """
        if macro_id in self._macros:
            del self._macros[macro_id]
            self.save()
            _LOG.info("Deleted macro: %s", macro_id)
            return True
        return False
    
    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------
    
    def _parse_target(self, target: str) -> tuple[str, int]:
        """
        Parse a target string into type and port.
        
        :param target: Target string like "input_1" or "output_2"
        :return: Tuple of (type, port) e.g., ("input", 1)
        """
        parts = target.split("_")
        if len(parts) != 2:
            raise ValueError(f"Invalid target format: {target}")
        
        target_type = parts[0]
        if target_type not in ("input", "output"):
            raise ValueError(f"Invalid target type: {target_type}")
        
        try:
            port = int(parts[1])
            if port < 1 or port > 8:
                raise ValueError(f"Port out of range: {port}")
        except ValueError:
            raise ValueError(f"Invalid port number: {parts[1]}")
        
        return target_type, port
    
    async def execute_macro(self, macro_id: str) -> dict[str, Any]:
        """
        Execute a macro.
        
        :param macro_id: Macro identifier
        :return: Execution result with success status and details
        """
        macro = self._macros.get(macro_id)
        if macro is None:
            return {
                "success": False,
                "error": f"Macro not found: {macro_id}",
            }
        
        if self._cec_sender is None:
            return {
                "success": False,
                "error": "CEC sender not configured",
            }
        
        _LOG.info("Executing macro: %s (%s)", macro.name, macro_id)
        
        results = []
        total_steps = len(macro.steps)
        
        for i, step in enumerate(macro.steps):
            step_result = {
                "step": i + 1,
                "command": step.command,
                "targets": step.targets,
                "success": True,
                "errors": [],
            }
            
            # Send command to each target
            for target in step.targets:
                try:
                    target_type, port = self._parse_target(target)
                    success = await self._cec_sender(target_type, port, step.command)
                    if not success:
                        step_result["success"] = False
                        step_result["errors"].append(f"Failed to send {step.command} to {target}")
                except Exception as ex:
                    step_result["success"] = False
                    step_result["errors"].append(f"Error sending to {target}: {str(ex)}")
            
            results.append(step_result)
            
            # Apply delay if specified and not the last step
            if step.delay_ms > 0 and i < total_steps - 1:
                await asyncio.sleep(step.delay_ms / 1000.0)
        
        # Determine overall success
        all_success = all(r["success"] for r in results)
        
        _LOG.info("Macro %s completed: %s", macro_id, "success" if all_success else "partial failure")
        
        return {
            "success": all_success,
            "macro_id": macro_id,
            "macro_name": macro.name,
            "steps_executed": len(results),
            "results": results,
        }
    
    async def test_macro(self, macro_id: str) -> dict[str, Any]:
        """
        Test a macro (dry run - doesn't actually send commands).
        
        :param macro_id: Macro identifier
        :return: Test result with validation info
        """
        macro = self._macros.get(macro_id)
        if macro is None:
            return {
                "success": False,
                "error": f"Macro not found: {macro_id}",
            }
        
        issues = []
        
        for i, step in enumerate(macro.steps):
            # Validate command
            if not step.command:
                issues.append(f"Step {i+1}: Missing command")
            
            # Validate targets
            if not step.targets:
                issues.append(f"Step {i+1}: No targets specified")
            
            for target in step.targets:
                try:
                    self._parse_target(target)
                except ValueError as ex:
                    issues.append(f"Step {i+1}: {str(ex)}")
        
        return {
            "success": len(issues) == 0,
            "macro_id": macro_id,
            "macro_name": macro.name,
            "step_count": len(macro.steps),
            "issues": issues,
            "estimated_duration_ms": sum(s.delay_ms for s in macro.steps),
        }
