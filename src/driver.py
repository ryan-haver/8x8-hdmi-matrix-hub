#!/usr/bin/env python3
"""
OREI BK-808 HDMI Matrix integration driver for Unfolded Circle Remote Two/3.

:copyright: (c) 2026 by Custom Integration.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import atexit
import json
import logging
import os
import signal
import socket
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Coroutine

import ucapi
from orei_matrix import Events as MatrixEvents
from orei_matrix import OreiMatrix
from rest_api import RestApiServer, set_matrix_device, update_input_names, update_output_names, broadcast_status_update, set_macro_cec_sender
from ucapi import Button, StatusCodes, MediaPlayer, Switch, Sensor
from ucapi.remote import Attributes as RemoteAttr
from ucapi.remote import Commands as RemoteCommands
from ucapi.remote import Features as RemoteFeatures
from ucapi.remote import Remote
from ucapi.media_player import Attributes as MediaPlayerAttr
from ucapi.media_player import Commands as MediaPlayerCommands
from ucapi.media_player import Features as MediaPlayerFeatures
from ucapi.media_player import DeviceClasses as MediaPlayerDeviceClasses
from ucapi.media_player import States as MediaPlayerStates
from ucapi.switch import Attributes as SwitchAttr
from ucapi.switch import Commands as SwitchCommands
from ucapi.switch import Features as SwitchFeatures
from ucapi.switch import States as SwitchStates
from ucapi.sensor import Attributes as SensorAttr
from ucapi.sensor import DeviceClasses as SensorDeviceClasses
from ucapi.sensor import States as SensorStates

_LOG = logging.getLogger("driver")

# REST API configuration
REST_API_PORT = int(os.environ.get("REST_API_PORT", "8080"))
REST_API_ENABLED = os.environ.get("REST_API_ENABLED", "true").lower() == "true"

# Status polling configuration
POLLING_INTERVAL = int(os.environ.get("POLLING_INTERVAL", "30"))  # seconds
POLLING_ENABLED = os.environ.get("POLLING_ENABLED", "true").lower() == "true"

# Configuration file paths - use UC_CONFIG_HOME if set (for Docker), otherwise local directory
_CONFIG_HOME = Path(os.environ.get("UC_CONFIG_HOME", Path(__file__).parent))
CONFIG_FILE = _CONFIG_HOME / "config_state.json"
LOCK_FILE = _CONFIG_HOME / "driver.lock"


# =============================================================================
# Driver State Dataclass - Consolidates global state
# =============================================================================

@dataclass
class DriverState:
    """Centralized driver state management.
    
    This dataclass consolidates all driver state into a single object,
    making it easier to manage, test, and reason about state.
    
    Attributes:
        api: The Unfolded Circle integration API instance
        matrix_device: The OREI matrix device connection
        rest_api_server: The REST API server instance
        polling_task: Background task for status polling
        input_names: Mapping of input port numbers to names
        output_names: Mapping of output port numbers to names
        saved_config: Persisted configuration data
    """
    
    api: ucapi.IntegrationAPI | None = None
    matrix_device: OreiMatrix | None = None
    rest_api_server: "RestApiServer | None" = None
    polling_task: asyncio.Task | None = None
    input_names: dict[int, str] = field(default_factory=dict)
    output_names: dict[int, str] = field(default_factory=dict)
    saved_config: dict[str, Any] = field(default_factory=dict)
    
    @property
    def connected(self) -> bool:
        """Check if matrix is connected."""
        return self.matrix_device is not None and self.matrix_device.connected
    
    def get_input_name(self, port: int) -> str:
        """Get input name with fallback to default."""
        return self.input_names.get(port, f"Input {port}")
    
    def get_output_name(self, port: int) -> str:
        """Get output name with fallback to default."""
        return self.output_names.get(port, f"Output {port}")


# Global driver state instance - THE source of truth for all state
_driver_state = DriverState()

# Polling task reference for background status updates
_polling_task = None


# =============================================================================
# State Accessor Functions - Clean interface for accessing driver state
# =============================================================================

def get_state() -> DriverState:
    """Get the global driver state instance.
    
    Use this function instead of accessing _driver_state directly when possible.
    This provides a clean interface that can be easily mocked in tests.
    """
    return _driver_state


def get_matrix() -> OreiMatrix | None:
    """Get the matrix device instance."""
    return _driver_state.matrix_device


def is_connected() -> bool:
    """Check if the matrix device is connected."""
    return _driver_state.connected


def set_matrix(device: OreiMatrix | None) -> None:
    """Set the matrix device instance."""
    _driver_state.matrix_device = device


def set_input_names(names: dict[int, str]) -> None:
    """Update input names in driver state."""
    _driver_state.input_names = names.copy() if names else {}


def set_output_names(names: dict[int, str]) -> None:
    """Update output names in driver state."""
    _driver_state.output_names = names.copy() if names else {}


# NOTE: Legacy globals have been removed. Use accessor functions instead:
# - get_matrix() for matrix device
# - _driver_state.api for API instance
# - _driver_state.input_names for input names
# - _driver_state.output_names for output names


# =============================================================================
# CEC Command Handler Factory - Reduces duplication between input/output handlers
# =============================================================================

def create_cec_command_handler(
    port_num: int,
    port_type: str,  # "input" or "output"
    get_method: Callable[[str], Callable[[int], Coroutine[Any, Any, bool]]]
) -> Callable:
    """
    Factory function to create CEC command handlers for inputs or outputs.
    
    This eliminates ~200 lines of duplicate code between input and output CEC handlers.
    
    :param port_num: Input or output number (1-8)
    :param port_type: "input" or "output"
    :param get_method: Function that returns the appropriate CEC method for a command
    :return: Async command handler function
    """
    
    async def cec_cmd_handler(
        entity: Remote, cmd_id: str, params: dict[str, Any] | None, websocket: Any
    ) -> StatusCodes:
        """Handle CEC remote commands."""
        _LOG.info(f"{port_type.upper()} CEC: {entity.id} -> {cmd_id}")

        matrix = get_matrix()
        if matrix is None or not matrix.connected:
            _LOG.error("Matrix not connected")
            return StatusCodes.SERVICE_UNAVAILABLE

        # Handle SEND_CMD for simple commands
        if cmd_id == RemoteCommands.SEND_CMD:
            if params and "command" in params:
                command = params["command"]
                method = get_method(command)
                if method:
                    success = await method(port_num)
                    return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
                else:
                    _LOG.warning(f"Unknown CEC command: {command}")
                    return StatusCodes.BAD_REQUEST

        # Handle native remote commands (D-pad, playback buttons)
        native_cmd_map = {
            RemoteCommands.CURSOR_UP: "UP",
            RemoteCommands.CURSOR_DOWN: "DOWN",
            RemoteCommands.CURSOR_LEFT: "LEFT",
            RemoteCommands.CURSOR_RIGHT: "RIGHT",
            RemoteCommands.CURSOR_ENTER: "SELECT",
            RemoteCommands.MENU: "MENU",
            RemoteCommands.BACK: "BACK",
            RemoteCommands.PLAY_PAUSE: "PLAY",
            RemoteCommands.PREVIOUS: "PREVIOUS",
            RemoteCommands.NEXT: "NEXT",
            RemoteCommands.FAST_FORWARD: "FAST_FORWARD",
            RemoteCommands.REWIND: "REWIND",
            RemoteCommands.VOLUME_UP: "VOLUME_UP",
            RemoteCommands.VOLUME_DOWN: "VOLUME_DOWN",
            RemoteCommands.MUTE_TOGGLE: "MUTE",
            RemoteCommands.POWER_ON: "POWER_ON",
            RemoteCommands.POWER_OFF: "POWER_OFF",
            RemoteCommands.POWER_TOGGLE: "POWER_ON",
        }

        if cmd_id in native_cmd_map:
            method = get_method(native_cmd_map[cmd_id])
            if method:
                success = await method(port_num)
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
        
        _LOG.warning(f"Command not implemented: {cmd_id}")
        return StatusCodes.NOT_IMPLEMENTED
    
    return cec_cmd_handler


def get_input_cec_method(command: str) -> Callable[[int], Coroutine[Any, Any, bool]] | None:
    """
    Get a callable for executing a CEC command on an input device.
    
    Uses the unified send_cec method instead of individual method mappings.
    
    :param command: CEC command name (e.g., "POWER_ON", "PLAY", "MUTE")
    :return: Async callable that takes input_num and returns bool, or None if matrix unavailable
    """
    matrix = get_matrix()
    if matrix is None:
        return None
    
    # Validate command exists in the registry
    if command.upper() not in matrix.CEC_COMMAND_MAP:
        _LOG.warning(f"Unknown CEC command: {command}")
        return None
    
    # Return a closure that calls send_cec with is_output=False
    async def send_input_cec(input_num: int) -> bool:
        return await matrix.send_cec(command, input_num, is_output=False)
    
    return send_input_cec


def get_output_cec_method(command: str) -> Callable[[int], Coroutine[Any, Any, bool]] | None:
    """
    Get a callable for executing a CEC command on an output device.
    
    Uses the unified send_cec method instead of individual method mappings.
    
    :param command: CEC command name (e.g., "POWER_ON", "VOLUME_UP", "MUTE")
    :return: Async callable that takes output_num and returns bool, or None if matrix unavailable
    """
    matrix = get_matrix()
    if matrix is None:
        return None
    
    # Validate command exists in the registry
    if command.upper() not in matrix.CEC_COMMAND_MAP:
        _LOG.warning(f"Unknown CEC command: {command}")
        return None
    
    # Return a closure that calls send_cec with is_output=True
    async def send_output_cec(output_num: int) -> bool:
        return await matrix.send_cec(command, output_num, is_output=True)
    
    return send_output_cec


def acquire_lock() -> bool:
    """
    Acquire a file lock to ensure only one instance runs.
    This prevents mDNS conflicts from multiple instances.
    """
    try:
        # Check if lock file exists and if the process is still running
        if LOCK_FILE.exists():
            try:
                with open(LOCK_FILE, "r") as f:
                    old_pid = int(f.read().strip())
                # Check if process is still running (Windows-compatible)
                import psutil
                if psutil.pid_exists(old_pid):
                    _LOG.error(f"Another instance is already running (PID: {old_pid})")
                    return False
                else:
                    _LOG.info(f"Stale lock file found (PID {old_pid} not running), removing...")
                    LOCK_FILE.unlink()
            except (ValueError, ImportError):
                # If we can't check, just remove the stale lock
                _LOG.info("Removing potentially stale lock file...")
                LOCK_FILE.unlink()
        
        # Create lock file with our PID
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
        _LOG.info(f"Lock acquired (PID: {os.getpid()})")
        return True
    except Exception as e:
        _LOG.error(f"Failed to acquire lock: {e}")
        return False


def release_lock():
    """Release the file lock."""
    try:
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()
            _LOG.info("Lock released")
    except Exception as e:
        _LOG.warning(f"Failed to release lock: {e}")


def check_port_available(port: int) -> bool:
    """Check if the port is available before starting."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', port))
            return True
    except OSError as e:
        if e.errno == 10048:  # Windows: Address already in use
            return False
        raise


def wait_for_port(port: int, timeout: int = 10) -> bool:
    """Wait for a port to become available."""
    _LOG.info(f"Waiting for port {port} to become available...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_port_available(port):
            _LOG.info(f"Port {port} is now available")
            return True
        time.sleep(0.5)
    _LOG.error(f"Port {port} did not become available within {timeout} seconds")
    return False


def clear_stale_mdns(wait_time: int = 2):
    """
    Brief pause before mDNS registration to help avoid conflicts.
    
    Note: True mDNS cleanup is not possible for services we didn't register.
    In Docker/production, container restarts handle this cleanly.
    In development, rapid restarts may require waiting for mDNS TTL expiry.
    
    Args:
        wait_time: Seconds to wait (default 2)
    """
    _LOG.debug(f"Waiting {wait_time}s before mDNS registration...")
    time.sleep(wait_time)


def save_config(host: str, port: int, input_names: dict[int, str], output_names: dict[int, str] = None) -> None:
    """Save configuration to file for persistence across restarts."""
    config = {
        "host": host,
        "port": port,
        "input_names": {str(k): v for k, v in input_names.items()},  # JSON requires string keys
    }
    if output_names:
        config["output_names"] = {str(k): v for k, v in output_names.items()}
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        _LOG.info(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        _LOG.error(f"Failed to save configuration: {e}")


def load_config() -> dict[str, Any] | None:
    """Load configuration from file."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
            # Convert input_names keys back to integers
            if "input_names" in config:
                config["input_names"] = {int(k): v for k, v in config["input_names"].items()}
            # Legacy: migrate from old "preset_names" key
            if "preset_names" in config and "input_names" not in config:
                config["input_names"] = {int(k): v for k, v in config["preset_names"].items()}
                del config["preset_names"]
            if "output_names" in config:
                config["output_names"] = {int(k): v for k, v in config["output_names"].items()}
            _LOG.info(f"Configuration loaded from {CONFIG_FILE}")
            return config
    except Exception as e:
        _LOG.error(f"Failed to load configuration: {e}")
    return None


async def restore_from_config() -> bool:
    """
    Restore entities and matrix connection from saved configuration.
    Called at startup before Remote 3 connects.
    
    :return: True if successfully restored, False otherwise
    """
    
    config = load_config()
    if not config:
        _LOG.info("No saved configuration found - waiting for setup")
        return False
    
    host = config.get("host")
    port = config.get("port", 443)
    input_names = config.get("input_names", {})
    output_names = config.get("output_names", {})
    
    if not host:
        _LOG.warning("No host in saved configuration")
        return False
    
    _LOG.info(f"Restoring from saved config: host={host}, port={port}")
    
    # Create matrix device instance and update driver state
    matrix = OreiMatrix(host, port)
    set_matrix(matrix)
    
    # Register event handlers
    matrix.events.on(MatrixEvents.CONNECTED, on_matrix_connected)
    matrix.events.on(MatrixEvents.DISCONNECTED, on_matrix_disconnected)
    matrix.events.on(MatrixEvents.ERROR, on_matrix_error)
    matrix.events.on(MatrixEvents.UPDATE, on_matrix_update)
    
    # Try to connect and update names
    output_connections = [0] * 8
    input_inactive = []  # Inputs with no signal
    try:
        success = await matrix.connect()
        if success:
            _LOG.info("Connected to matrix, querying fresh status...")
            fresh_names = await matrix.get_all_input_names()
            if fresh_names:
                input_names = fresh_names
            
            fresh_output_names = await matrix.get_output_names()
            if fresh_output_names:
                output_names = fresh_output_names
            
            # Get output connection status
            output_status = await matrix.get_output_status()
            if output_status and "allconnect" in output_status:
                output_connections = output_status["allconnect"]
            
            # Get input status for signal detection
            input_status = await matrix.get_input_status()
            if input_status and "inactive" in input_status:
                input_inactive = input_status["inactive"]
            
            # Update saved config with fresh data
            save_config(host, port, input_names, output_names)
    except Exception as e:
        _LOG.warning(f"Could not connect to matrix on startup: {e}")
    
    # Store names using accessor functions
    set_input_names(input_names if input_names else {i: f"Input {i}" for i in range(1, 9)})
    set_output_names(output_names if output_names else {i: f"Output {i}" for i in range(1, 9)})
    
    # Create entities
    _LOG.info("Creating entities from saved configuration...")
    
    # Matrix remote with input names for source selection
    remote_entity = create_matrix_remote(_driver_state.input_names)
    _driver_state.api.available_entities.add(remote_entity)
    _LOG.info(f"Added remote entity: {remote_entity.id}")
    
    # Preset buttons (presets are saved configurations, not inputs)
    for preset_num in range(1, 9):
        button = create_preset_button(preset_num)  # Presets use generic names
        _driver_state.api.available_entities.add(button)
        _LOG.info(f"Added button entity: {button.id}")
    
    # CEC remote entities for each INPUT
    for input_num in range(1, 9):
        cec_remote = create_input_cec_remote(input_num, _driver_state.get_input_name(input_num))
        _driver_state.api.available_entities.add(cec_remote)
        _LOG.info(f"Added input CEC remote entity: {cec_remote.id}")
    
    # Input signal sensors
    for input_num in range(1, 9):
        input_name = _driver_state.get_input_name(input_num)
        signal_sensor = create_input_signal_sensor(input_num, input_name)
        # Update sensor with actual signal status
        # inactive array: 1 = signal present, 0 = no signal (at index input_num - 1)
        idx = input_num - 1
        has_signal = input_inactive[idx] == 1 if idx < len(input_inactive) else False
        signal_sensor.attributes[SensorAttr.VALUE] = "Active" if has_signal else "No Signal"
        _driver_state.api.available_entities.add(signal_sensor)
        _LOG.info(f"Added input signal sensor entity: {signal_sensor.id}")
    
    # Input cable connection sensors (Telnet-based)
    for input_num in range(1, 9):
        input_name = _driver_state.get_input_name(input_num)
        cable_sensor = create_input_cable_sensor(input_num, input_name)
        # Initial status will be updated by polling when Telnet connects
        _driver_state.api.available_entities.add(cable_sensor)
        _LOG.info(f"Added input cable sensor entity: {cable_sensor.id}")
    
    # === NEW ENHANCED ENTITIES ===
    
    # Matrix power switch
    power_switch = create_matrix_power_switch()
    _driver_state.api.available_entities.add(power_switch)
    _LOG.info(f"Added power switch entity: {power_switch.id}")
    
    # For each output: MediaPlayer, CEC Remote, and Sensors
    for output_num in range(1, 9):
        output_name = _driver_state.get_output_name(output_num)
        
        # MediaPlayer for source selection on this output
        media_player = create_output_media_player(output_num, output_name, _driver_state.input_names)
        _driver_state.api.available_entities.add(media_player)
        _LOG.info(f"Added media player entity: {media_player.id}")
        
        # CEC remote for controlling the TV/display on this output
        output_cec = create_output_cec_remote(output_num, output_name)
        _driver_state.api.available_entities.add(output_cec)
        _LOG.info(f"Added output CEC remote entity: {output_cec.id}")
        
        # Connection sensor for this output (HTTP-based)
        conn_sensor = create_connection_sensor(output_num, output_name)
        # Update sensor with actual connection status
        is_connected = output_connections[output_num - 1] == 1 if len(output_connections) >= output_num else False
        conn_sensor.attributes[SensorAttr.VALUE] = "Connected" if is_connected else "Disconnected"
        _driver_state.api.available_entities.add(conn_sensor)
        _LOG.info(f"Added connection sensor entity: {conn_sensor.id}")
        
        # Cable sensor for this output (Telnet-based)
        cable_sensor = create_output_cable_sensor(output_num, output_name)
        # Initial status will be updated by polling when Telnet connects
        _driver_state.api.available_entities.add(cable_sensor)
        _LOG.info(f"Added output cable sensor entity: {cable_sensor.id}")
        
        # Routing sensor for this output
        routing_sensor = create_routing_sensor(output_num, output_name)
        _driver_state.api.available_entities.add(routing_sensor)
        _LOG.info(f"Added routing sensor entity: {routing_sensor.id}")
    
    # Configure REST API with matrix device, names, and config file for persistence
    set_matrix_device(
        get_matrix(), 
        input_names=_driver_state.input_names,
        output_names=_driver_state.output_names,
        config_file=CONFIG_FILE
    )
    
    # Configure CEC sender for macros
    async def cec_sender(target_type: str, port: int, command: str) -> bool:
        """Send CEC command via matrix device."""
        matrix = get_matrix()
        if not matrix or not matrix.connected:
            return False
        # Normalize command to lowercase for method lookup
        command = command.lower()
        # Call the appropriate CEC method
        method_name = f"cec_{target_type}_{command}"
        method = getattr(matrix, method_name, None)
        if method:
            return await method(port)
        # Fallback to set_cec_enable for enable/disable
        if command in ("enable", "disable"):
            return await matrix.set_cec_enable(target_type, port, command == "enable")
        return False
    
    set_macro_cec_sender(cec_sender)
    
    # 1 remote + 8 buttons + 8 input CEC + 8 input signal + 8 input cable + 1 switch + 8*(MP+CEC+3 output sensors)
    entity_count = 1 + 8 + 8 + 8 + 8 + 1 + (8 * 5)
    _LOG.info(f"✓ Restored {entity_count} entities from saved configuration")
    _LOG.info("  - 1 matrix remote, 8 preset buttons, 8 input CEC remotes")
    _LOG.info("  - 8 input signal sensors, 8 input cable sensors")
    _LOG.info("  - 1 power switch")
    _LOG.info("  - 8 output media players, 8 output CEC remotes, 24 output sensors (conn+cable+routing)")
    return True


def create_preset_button(preset_num: int, preset_name: str = None) -> Button:
    """
    Create a button entity for a specific preset.


    :param preset_num: Preset number (1-8)
    :param preset_name: Custom name for the preset (optional)
    :return: Button entity
    """
    # Use custom name if provided, otherwise use generic name
    display_name = preset_name if preset_name else f"Preset {preset_num}"

    async def preset_cmd_handler(
        entity: Button, cmd_id: str, _params: dict[str, Any] | None, websocket: Any
    ) -> StatusCodes:
        """Handle preset button press."""
        _LOG.info("=" * 60)
        _LOG.info("BUTTON COMMAND HANDLER CALLED!")
        _LOG.info(f"Entity: {entity.id}, Command: {cmd_id}, Params: {_params}")
        _LOG.info(f"Preset %d (%s) button pressed", preset_num, display_name)
        _LOG.info("=" * 60)
        
        matrix = get_matrix()
        if matrix is None or not matrix.connected:
            _LOG.error("Matrix not connected")
            return StatusCodes.SERVICE_UNAVAILABLE

        _LOG.info(f"Calling matrix recall_preset({preset_num})...")
        success = await matrix.recall_preset(preset_num)
        _LOG.info(f"Preset recall result: {success}")
        return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

    button = Button(
        f"button.preset_{preset_num}",
        display_name,
        cmd_handler=preset_cmd_handler,
    )
    return button


def create_input_cec_remote(input_num: int, input_name: str = None) -> Remote:
    """
    Create a remote entity for CEC control of a specific input device.
    
    This allows controlling source devices (PS3, Apple TV, etc.) via CEC
    using the Remote 3's native D-pad, playback buttons, etc.

    :param input_num: Input number (1-8)
    :param input_name: Custom name for the input (optional)
    :return: Remote entity
    """
    display_name = input_name if input_name else f"Input {input_num}"
    entity_id = f"remote.input_{input_num}_cec"

    # CEC command mapping for simple_commands
    CEC_COMMANDS = [
        "POWER_ON", "POWER_OFF",
        "UP", "DOWN", "LEFT", "RIGHT", "SELECT",
        "MENU", "BACK",
        "PLAY", "PAUSE", "STOP",
        "PREVIOUS", "NEXT",
        "REWIND", "FAST_FORWARD",
        "VOLUME_UP", "VOLUME_DOWN", "MUTE"
    ]

    # Use factory pattern for command handler (reduces ~80 lines of duplicate code)
    cec_cmd_handler = create_cec_command_handler(input_num, "input", get_input_cec_method)

    # Create UI page with CEC controls laid out like a remote
    from ucapi.ui import Size, UiPage, create_ui_text, create_ui_icon

    # Main navigation page
    nav_page = UiPage(
        f"input_{input_num}_nav",
        "Navigation",
        grid=Size(4, 6),
        items=[
            # Power row
            create_ui_text("Power On", 0, 0, Size(2, 1), "POWER_ON"),
            create_ui_text("Power Off", 2, 0, Size(2, 1), "POWER_OFF"),
            # D-pad
            create_ui_text("▲", 1, 1, Size(2, 1), "UP"),
            create_ui_text("◀", 0, 2, Size(1, 1), "LEFT"),
            create_ui_text("OK", 1, 2, Size(2, 1), "SELECT"),
            create_ui_text("▶", 3, 2, Size(1, 1), "RIGHT"),
            create_ui_text("▼", 1, 3, Size(2, 1), "DOWN"),
            # Menu/Back row
            create_ui_text("Menu", 0, 4, Size(2, 1), "MENU"),
            create_ui_text("Back", 2, 4, Size(2, 1), "BACK"),
        ],
    )

    # Playback page
    playback_page = UiPage(
        f"input_{input_num}_playback",
        "Playback",
        grid=Size(4, 6),
        items=[
            # Transport controls
            create_ui_text("⏮", 0, 0, Size(1, 1), "PREVIOUS"),
            create_ui_text("⏪", 1, 0, Size(1, 1), "REWIND"),
            create_ui_text("⏩", 2, 0, Size(1, 1), "FAST_FORWARD"),
            create_ui_text("⏭", 3, 0, Size(1, 1), "NEXT"),
            # Play/Pause/Stop
            create_ui_text("▶ Play", 0, 1, Size(2, 1), "PLAY"),
            create_ui_text("⏸ Pause", 2, 1, Size(2, 1), "PAUSE"),
            create_ui_text("⏹ Stop", 1, 2, Size(2, 1), "STOP"),
            # Volume controls
            create_ui_text("🔉 Vol-", 0, 3, Size(1, 1), "VOLUME_DOWN"),
            create_ui_text("🔇 Mute", 1, 3, Size(2, 1), "MUTE"),
            create_ui_text("🔊 Vol+", 3, 3, Size(1, 1), "VOLUME_UP"),
        ],
    )

    # Create remote with all CEC features
    remote = Remote(
        entity_id,
        f"{display_name} CEC",
        [
            RemoteFeatures.SEND_CMD,
            RemoteFeatures.ON_OFF,
        ],
        attributes={RemoteAttr.STATE: ucapi.remote.States.ON},
        simple_commands=CEC_COMMANDS,
        ui_pages=[nav_page, playback_page],
        cmd_handler=cec_cmd_handler,
    )

    return remote


def create_output_cec_remote(output_num: int, output_name: str = None) -> Remote:
    """
    Create a remote entity for CEC control of a specific output device (TV/display).
    
    This allows controlling displays via CEC using the Remote 3's native controls.

    :param output_num: Output number (1-8)
    :param output_name: Custom name for the output (optional)
    :return: Remote entity
    """
    display_name = output_name if output_name else f"Output {output_num}"
    entity_id = f"remote.output_{output_num}_cec"

    # CEC command mapping for simple_commands (outputs typically use fewer commands)
    CEC_COMMANDS = [
        "POWER_ON", "POWER_OFF",
        "UP", "DOWN", "LEFT", "RIGHT", "SELECT",
        "MENU", "BACK",
        "VOLUME_UP", "VOLUME_DOWN", "MUTE"
    ]

    # Use factory pattern for command handler (reduces ~60 lines of duplicate code)
    cec_cmd_handler = create_cec_command_handler(output_num, "output", get_output_cec_method)

    # Create UI page with TV/display controls
    from ucapi.ui import Size, UiPage, create_ui_text

    control_page = UiPage(
        f"output_{output_num}_control",
        "TV Control",
        grid=Size(4, 6),
        items=[
            # Power row
            create_ui_text("📺 Power On", 0, 0, Size(2, 1), "POWER_ON"),
            create_ui_text("⏻ Power Off", 2, 0, Size(2, 1), "POWER_OFF"),
            # D-pad
            create_ui_text("▲", 1, 1, Size(2, 1), "UP"),
            create_ui_text("◀", 0, 2, Size(1, 1), "LEFT"),
            create_ui_text("OK", 1, 2, Size(2, 1), "SELECT"),
            create_ui_text("▶", 3, 2, Size(1, 1), "RIGHT"),
            create_ui_text("▼", 1, 3, Size(2, 1), "DOWN"),
            # Menu/Back/Volume row
            create_ui_text("Menu", 0, 4, Size(2, 1), "MENU"),
            create_ui_text("Back", 2, 4, Size(2, 1), "BACK"),
            # Volume
            create_ui_text("🔉", 0, 5, Size(1, 1), "VOLUME_DOWN"),
            create_ui_text("🔇 Mute", 1, 5, Size(2, 1), "MUTE"),
            create_ui_text("🔊", 3, 5, Size(1, 1), "VOLUME_UP"),
        ],
    )

    remote = Remote(
        entity_id,
        f"{display_name} TV",
        [
            RemoteFeatures.SEND_CMD,
            RemoteFeatures.ON_OFF,
        ],
        attributes={RemoteAttr.STATE: ucapi.remote.States.ON},
        simple_commands=CEC_COMMANDS,
        ui_pages=[control_page],
        cmd_handler=cec_cmd_handler,
    )

    return remote


def create_output_media_player(
    output_num: int, 
    output_name: str = None, 
    input_names: dict[int, str] = None
) -> MediaPlayer:
    """
    Create a MediaPlayer entity for a specific output with source selection.
    
    This provides the native UC source selector UI for switching inputs on an output.

    :param output_num: Output number (1-8)
    :param output_name: Custom name for the output (optional)
    :param input_names: Dictionary mapping input numbers to names
    :return: MediaPlayer entity
    """
    display_name = output_name if output_name else f"Output {output_num}"
    entity_id = f"media_player.output_{output_num}"
    
    # Build source list from input names
    if not input_names:
        input_names = {i: f"Input {i}" for i in range(1, 9)}
    
    source_list = [input_names.get(i, f"Input {i}") for i in range(1, 9)]

    async def media_player_cmd_handler(
        entity: MediaPlayer, cmd_id: str, params: dict[str, Any] | None, websocket: Any
    ) -> StatusCodes:
        """Handle MediaPlayer commands for output switching."""
        _LOG.info("=" * 60)
        _LOG.info("MEDIA PLAYER COMMAND HANDLER CALLED!")
        _LOG.info(f"Entity: {entity.id}, Command: {cmd_id}, Params: {params}")
        _LOG.info("=" * 60)

        matrix = get_matrix()
        if matrix is None or not matrix.connected:
            _LOG.error("Matrix not connected")
            return StatusCodes.SERVICE_UNAVAILABLE

        if cmd_id == MediaPlayerCommands.SELECT_SOURCE:
            if params and "source" in params:
                source_name = params["source"]
                _LOG.info(f"Selecting source '{source_name}' for output {output_num}")
                
                # Find input number from source name
                input_num = None
                for i in range(1, 9):
                    if input_names.get(i) == source_name:
                        input_num = i
                        break
                
                if input_num is None:
                    # Try parsing "Input X" format
                    try:
                        if source_name.startswith("Input "):
                            input_num = int(source_name.split(" ")[1])
                    except (ValueError, IndexError):
                        pass
                
                if input_num and 1 <= input_num <= 8:
                    success = await matrix.switch_input(input_num, output_num)
                    if success:
                        # Update entity attributes with new source
                        _driver_state.api.configured_entities.update_attributes(
                            entity.id,
                            {
                                MediaPlayerAttr.SOURCE: source_name,
                                MediaPlayerAttr.STATE: MediaPlayerStates.ON
                            }
                        )
                    return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
                else:
                    _LOG.error(f"Could not find input for source: {source_name}")
                    return StatusCodes.BAD_REQUEST
        
        elif cmd_id == MediaPlayerCommands.ON:
            # Turn on the display via CEC
            success = await matrix.cec_output_power_on(output_num)
            if success:
                _driver_state.api.configured_entities.update_attributes(
                    entity.id,
                    {MediaPlayerAttr.STATE: MediaPlayerStates.ON}
                )
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
        
        elif cmd_id == MediaPlayerCommands.OFF:
            # Turn off the display via CEC
            success = await matrix.cec_output_power_off(output_num)
            if success:
                _driver_state.api.configured_entities.update_attributes(
                    entity.id,
                    {MediaPlayerAttr.STATE: MediaPlayerStates.OFF}
                )
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
        
        elif cmd_id == MediaPlayerCommands.TOGGLE:
            # Toggle power - check current state
            current_state = entity.attributes.get(MediaPlayerAttr.STATE)
            if current_state == MediaPlayerStates.OFF:
                return await media_player_cmd_handler(entity, MediaPlayerCommands.ON, None, websocket)
            else:
                return await media_player_cmd_handler(entity, MediaPlayerCommands.OFF, None, websocket)
        
        elif cmd_id == MediaPlayerCommands.VOLUME_UP:
            success = await matrix.cec_output_volume_up(output_num)
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
        
        elif cmd_id == MediaPlayerCommands.VOLUME_DOWN:
            success = await matrix.cec_output_volume_down(output_num)
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
        
        elif cmd_id == MediaPlayerCommands.MUTE_TOGGLE:
            success = await matrix.cec_output_mute(output_num)
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
        
        _LOG.warning(f"Command not implemented: {cmd_id}")
        return StatusCodes.NOT_IMPLEMENTED

    # Determine initial state based on connection
    initial_state = MediaPlayerStates.UNKNOWN

    media_player = MediaPlayer(
        entity_id,
        display_name,
        [
            MediaPlayerFeatures.ON_OFF,
            MediaPlayerFeatures.TOGGLE,
            MediaPlayerFeatures.SELECT_SOURCE,
            MediaPlayerFeatures.VOLUME_UP_DOWN,
            MediaPlayerFeatures.MUTE_TOGGLE,
        ],
        attributes={
            MediaPlayerAttr.STATE: initial_state,
            MediaPlayerAttr.SOURCE_LIST: source_list,
            MediaPlayerAttr.SOURCE: source_list[0] if source_list else "",
        },
        device_class=MediaPlayerDeviceClasses.TV,
        cmd_handler=media_player_cmd_handler,
    )

    return media_player


def create_matrix_power_switch() -> Switch:
    """
    Create a Switch entity for matrix power control.

    :return: Switch entity
    """
    entity_id = "switch.matrix_power"

    async def switch_cmd_handler(
        entity: Switch, cmd_id: str, params: dict[str, Any] | None, websocket: Any
    ) -> StatusCodes:
        """Handle Switch commands for matrix power."""
        _LOG.info("=" * 60)
        _LOG.info("SWITCH COMMAND HANDLER CALLED!")
        _LOG.info(f"Entity: {entity.id}, Command: {cmd_id}, Params: {params}")
        _LOG.info("=" * 60)

        matrix = get_matrix()
        if matrix is None:
            _LOG.error("Matrix device not configured")
            return StatusCodes.SERVICE_UNAVAILABLE

        if cmd_id == SwitchCommands.ON:
            success = await matrix.power_on()
            if success:
                _driver_state.api.configured_entities.update_attributes(
                    entity.id,
                    {SwitchAttr.STATE: SwitchStates.ON}
                )
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
        
        elif cmd_id == SwitchCommands.OFF:
            success = await matrix.power_off()
            if success:
                _driver_state.api.configured_entities.update_attributes(
                    entity.id,
                    {SwitchAttr.STATE: SwitchStates.OFF}
                )
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
        
        elif cmd_id == SwitchCommands.TOGGLE:
            current_state = entity.attributes.get(SwitchAttr.STATE)
            if current_state == SwitchStates.ON:
                return await switch_cmd_handler(entity, SwitchCommands.OFF, None, websocket)
            else:
                return await switch_cmd_handler(entity, SwitchCommands.ON, None, websocket)
        
        return StatusCodes.NOT_IMPLEMENTED

    switch = Switch(
        entity_id,
        "Matrix Power",
        [
            SwitchFeatures.ON_OFF,
            SwitchFeatures.TOGGLE,
        ],
        attributes={SwitchAttr.STATE: SwitchStates.ON},
        cmd_handler=switch_cmd_handler,
    )

    return switch


def create_connection_sensor(output_num: int, output_name: str = None) -> Sensor:
    """
    Create a Sensor entity showing if an output has a display connected.

    :param output_num: Output number (1-8)
    :param output_name: Custom name for the output (optional)
    :return: Sensor entity
    """
    display_name = output_name if output_name else f"Output {output_num}"
    entity_id = f"sensor.output_{output_num}_connected"

    sensor = Sensor(
        entity_id,
        f"{display_name} Connected",
        [],  # No features needed for sensors
        attributes={
            SensorAttr.STATE: SensorStates.ON,
            SensorAttr.VALUE: "Unknown",
        },
        device_class=SensorDeviceClasses.CUSTOM,
        options={"custom_unit": ""},
    )

    return sensor


def create_routing_sensor(output_num: int, output_name: str = None) -> Sensor:
    """
    Create a Sensor entity showing the current input routed to an output.

    :param output_num: Output number (1-8)
    :param output_name: Custom name for the output (optional)
    :return: Sensor entity
    """
    display_name = output_name if output_name else f"Output {output_num}"
    entity_id = f"sensor.output_{output_num}_source"

    sensor = Sensor(
        entity_id,
        f"{display_name} Source",
        [],  # No features needed for sensors
        attributes={
            SensorAttr.STATE: SensorStates.ON,
            SensorAttr.VALUE: "Unknown",
        },
        device_class=SensorDeviceClasses.CUSTOM,
        options={"custom_unit": ""},
    )

    return sensor


def create_input_signal_sensor(input_num: int, input_name: str = None) -> Sensor:
    """
    Create a Sensor entity showing if an input has an active signal.

    :param input_num: Input number (1-8)
    :param input_name: Custom name for the input (optional)
    :return: Sensor entity
    """
    display_name = input_name if input_name else f"Input {input_num}"
    entity_id = f"sensor.input_{input_num}_signal"

    sensor = Sensor(
        entity_id,
        f"{display_name} Signal",
        [],  # No features needed for sensors
        attributes={
            SensorAttr.STATE: SensorStates.ON,
            SensorAttr.VALUE: "Unknown",
        },
        device_class=SensorDeviceClasses.CUSTOM,
        options={"custom_unit": ""},
    )

    return sensor


def create_input_cable_sensor(input_num: int, input_name: str = None) -> Sensor:
    """
    Create a Sensor entity showing if an input has a cable connected.
    
    This sensor uses Telnet-based cable detection which is more reliable
    than HTTP signal detection for detecting physical connections.

    :param input_num: Input number (1-8)
    :param input_name: Custom name for the input (optional)
    :return: Sensor entity
    """
    display_name = input_name if input_name else f"Input {input_num}"
    entity_id = f"sensor.input_{input_num}_cable"

    sensor = Sensor(
        entity_id,
        f"{display_name} Cable",
        [],  # No features needed for sensors
        attributes={
            SensorAttr.STATE: SensorStates.ON,
            SensorAttr.VALUE: "Unknown",
        },
        device_class=SensorDeviceClasses.CUSTOM,
        options={"custom_unit": ""},
    )

    return sensor


def create_output_cable_sensor(output_num: int, output_name: str = None) -> Sensor:
    """
    Create a Sensor entity showing if an output has a cable connected.
    
    This sensor uses Telnet-based cable detection which can detect
    physical HDMI cable connections to displays/TVs.

    :param output_num: Output number (1-8)
    :param output_name: Custom name for the output (optional)
    :return: Sensor entity
    """
    display_name = output_name if output_name else f"Output {output_num}"
    entity_id = f"sensor.output_{output_num}_cable"

    sensor = Sensor(
        entity_id,
        f"{display_name} Cable",
        [],  # No features needed for sensors
        attributes={
            SensorAttr.STATE: SensorStates.ON,
            SensorAttr.VALUE: "Unknown",
        },
        device_class=SensorDeviceClasses.CUSTOM,
        options={"custom_unit": ""},
    )

    return sensor


def create_matrix_remote(input_names: dict[int, str] = None) -> Remote:
    """
    Create a remote entity for the OREI Matrix with preset selection.

    :param input_names: Optional dictionary mapping input numbers to names (for future source selector use)
    :return: Remote entity
    """
    # Presets are saved routing configurations, use generic names
    # (The OREI matrix doesn't expose custom preset names via API)
    preset_labels = {i: f"Preset {i}" for i in range(1, 9)}

    async def remote_cmd_handler(
        entity: Remote, cmd_id: str, params: dict[str, Any] | None, websocket: Any
    ) -> StatusCodes:
        """Handle remote entity commands."""
        _LOG.info("=" * 60)
        _LOG.info("REMOTE COMMAND HANDLER CALLED!")
        _LOG.info(f"Entity: {entity.id}, Command: {cmd_id}, Params: {params}")
        _LOG.info("=" * 60)

        matrix = get_matrix()
        if matrix is None or not matrix.connected:
            _LOG.error("Matrix not connected")
            return StatusCodes.SERVICE_UNAVAILABLE

        # Handle scene recall via send_cmd
        if cmd_id == RemoteCommands.SEND_CMD:
            if params and "command" in params:
                command = params["command"]
                _LOG.info(f"Processing SEND_CMD with command: {command}")
                # Check if it's a preset command
                if command.startswith("PRESET_"):
                    try:
                        preset_num = int(command.split("_")[1])
                        _LOG.info(f"Calling matrix recall_preset({preset_num})...")
                        success = await matrix.recall_preset(preset_num)
                        _LOG.info(f"Preset recall result: {success}")
                        return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
                    except (ValueError, IndexError):
                        _LOG.error("Invalid scene command: %s", command)
                        return StatusCodes.BAD_REQUEST
        
        _LOG.warning(f"Command not implemented: {cmd_id}")
        return StatusCodes.NOT_IMPLEMENTED

    # Define simple commands for each preset
    simple_commands = [f"PRESET_{i}" for i in range(1, 9)]

    # Create UI pages for preset selection
    from ucapi.ui import Size, UiPage, create_ui_text

    main_page = UiPage(
        "orei_matrix_main",
        "Presets",
        grid=Size(4, 6),
        items=[
            create_ui_text(preset_labels[1], 0, 0, Size(2, 1), "PRESET_1"),
            create_ui_text(preset_labels[2], 2, 0, Size(2, 1), "PRESET_2"),
            create_ui_text(preset_labels[3], 0, 1, Size(2, 1), "PRESET_3"),
            create_ui_text(preset_labels[4], 2, 1, Size(2, 1), "PRESET_4"),
            create_ui_text(preset_labels[5], 0, 2, Size(2, 1), "PRESET_5"),
            create_ui_text(preset_labels[6], 2, 2, Size(2, 1), "PRESET_6"),
            create_ui_text(preset_labels[7], 0, 3, Size(2, 1), "PRESET_7"),
            create_ui_text(preset_labels[8], 2, 3, Size(2, 1), "PRESET_8"),
        ],
    )

    remote = Remote(
        "remote.orei_matrix",
        "OREI Matrix",
        [RemoteFeatures.SEND_CMD],
        attributes={RemoteAttr.STATE: ucapi.remote.States.ON},
        simple_commands=simple_commands,
        ui_pages=[main_page],
        cmd_handler=remote_cmd_handler,
    )

    return remote


# =============================================================================
# Status Polling - Periodic updates for sensors and entities
# =============================================================================

async def status_polling_loop():
    """
    Background task that periodically polls matrix status and updates entities.
    
    Updates connection sensors, routing sensors, and media player sources.
    Broadcasts changes to WebSocket clients.
    Runs every POLLING_INTERVAL seconds.
    """
    global _polling_task
    
    # Track previous state to detect changes for WebSocket broadcasts
    _prev_routing: list[int] = []
    _prev_connections: list[int] = []
    _prev_inactive_inputs: list[int] = []
    _prev_cable_status: dict[str, dict[int, bool]] = {"inputs": {}, "outputs": {}}
    
    _LOG.info(f"Status polling started (interval: {POLLING_INTERVAL}s)")
    
    while True:
        try:
            await asyncio.sleep(POLLING_INTERVAL)
            
            matrix = get_matrix()
            if matrix is None or not matrix.connected:
                _LOG.debug("Polling skipped - matrix not connected")
                continue
            
            if _driver_state.api is None:
                _LOG.debug("Polling skipped - API not initialized")
                continue
            
            _LOG.debug("Polling matrix status...")
            
            # Get video status for routing info
            video_status = await matrix.get_video_status()
            
            # Get output status for cable detection
            output_status = await matrix.get_output_status()
            
            # Combine data from both endpoints
            if video_status or output_status:
                # Extract routing info: which input is on each output (from video status)
                routing = video_status.get("allsource", []) if video_status else []
                # Extract connection status for each output (from output status)
                output_connections = output_status.get("allconnect", []) if output_status else []
                
                # Update each output's sensors
                for output_num in range(1, 9):
                    # Update connection sensor (matches sensor.output_{n}_connected entity ID)
                    conn_entity_id = f"sensor.output_{output_num}_connected"
                    is_connected = output_connections[output_num - 1] == 1 if len(output_connections) >= output_num else False
                    
                    if _driver_state.api.configured_entities.contains(conn_entity_id):
                        # Output status only provides cable detection, not signal detection
                        conn_state = "Connected" if is_connected else "Disconnected"
                        
                        _driver_state.api.configured_entities.update_attributes(
                            conn_entity_id,
                            {SensorAttr.VALUE: conn_state, SensorAttr.STATE: SensorStates.ON}
                        )
                    
                    # Broadcast connection change via WebSocket if changed
                    if len(_prev_connections) >= output_num:
                        prev_connected = _prev_connections[output_num - 1] == 1
                        if prev_connected != is_connected:
                            await broadcast_status_update("connection_change", {
                                "output": output_num,
                                "connected": is_connected,
                                "state": conn_state
                            })
                    
                    # Update routing sensor (matches sensor.output_{n}_source entity ID)
                    routing_entity_id = f"sensor.output_{output_num}_source"
                    current_input = routing[output_num - 1] if len(routing) >= output_num else 0
                    input_name = _driver_state.input_names.get(current_input, f"Input {current_input}")
                    
                    if _driver_state.api.configured_entities.contains(routing_entity_id):
                        _driver_state.api.configured_entities.update_attributes(
                            routing_entity_id,
                            {SensorAttr.VALUE: input_name, SensorAttr.STATE: SensorStates.ON}
                        )
                    
                    # Broadcast routing change via WebSocket if changed
                    if len(_prev_routing) >= output_num:
                        prev_input = _prev_routing[output_num - 1]
                        if prev_input != current_input:
                            await broadcast_status_update("routing_change", {
                                "output": output_num,
                                "input": current_input,
                                "input_name": input_name,
                                "previous_input": prev_input
                            })
                    
                    # Update media player source
                    mp_entity_id = f"orei_output_{output_num}"
                    if _driver_state.api.configured_entities.contains(mp_entity_id):
                        _driver_state.api.configured_entities.update_attributes(
                            mp_entity_id,
                            {MediaPlayerAttr.SOURCE: input_name}
                        )
                
                # Save current state for next comparison
                _prev_routing = routing.copy() if routing else []
                _prev_connections = output_connections.copy() if output_connections else []
                
                _LOG.debug(f"Polling complete - routing: {routing}, connections: {output_connections}")
            
            # Get input status for signal detection
            input_status = await matrix.get_input_status()
            
            if input_status:
                inactive_inputs = input_status.get("inactive", [])
                
                # Update each input's signal sensor
                for input_num in range(1, 9):
                    signal_entity_id = f"sensor.input_{input_num}_signal"
                    # inactive array from get_input_status: 1 = signal present, 0 = no signal
                    inp_idx = input_num - 1
                    has_signal = inactive_inputs[inp_idx] == 1 if inp_idx < len(inactive_inputs) else False
                    
                    if _driver_state.api.configured_entities.contains(signal_entity_id):
                        signal_state = "Active" if has_signal else "No Signal"
                        _driver_state.api.configured_entities.update_attributes(
                            signal_entity_id,
                            {SensorAttr.VALUE: signal_state, SensorAttr.STATE: SensorStates.ON}
                        )
                    
                    # Broadcast signal change via WebSocket if changed
                    # Check previous state using same index-based lookup (1=signal present)
                    prev_had_signal = _prev_inactive_inputs[inp_idx] == 1 if inp_idx < len(_prev_inactive_inputs) else False
                    if prev_had_signal != has_signal:
                        await broadcast_status_update("signal_change", {
                            "input": input_num,
                            "has_signal": has_signal,
                            "input_name": _driver_state.input_names.get(input_num, f"Input {input_num}")
                        })
                
                # Save current state for next comparison
                _prev_inactive_inputs = inactive_inputs.copy() if inactive_inputs else []
                
                _LOG.debug(f"Input signal polling complete - inactive: {inactive_inputs}")
            
            # Get cable status from Telnet if available
            if matrix.telnet_connected:
                cable_status = await matrix.get_all_cable_status()
                
                if cable_status:
                    input_cables = cable_status.get("inputs", {})
                    output_cables = cable_status.get("outputs", {})
                    
                    # Update input cable sensors
                    for input_num in range(1, 9):
                        cable_entity_id = f"sensor.input_{input_num}_cable"
                        is_connected = input_cables.get(input_num)
                        
                        if _driver_state.api.configured_entities.contains(cable_entity_id):
                            if is_connected is not None:
                                cable_state = "Connected" if is_connected else "Disconnected"
                            else:
                                cable_state = "Unknown"
                            _driver_state.api.configured_entities.update_attributes(
                                cable_entity_id,
                                {SensorAttr.VALUE: cable_state, SensorAttr.STATE: SensorStates.ON}
                            )
                        
                        # Broadcast cable change via WebSocket if changed
                        prev_connected = _prev_cable_status.get("inputs", {}).get(input_num)
                        if prev_connected != is_connected and is_connected is not None:
                            await broadcast_status_update("cable_change", {
                                "type": "input",
                                "port": input_num,
                                "connected": is_connected,
                                "name": _driver_state.input_names.get(input_num, f"Input {input_num}")
                            })
                    
                    # Update output cable sensors
                    for output_num in range(1, 9):
                        cable_entity_id = f"sensor.output_{output_num}_cable"
                        is_connected = output_cables.get(output_num)
                        
                        if _driver_state.api.configured_entities.contains(cable_entity_id):
                            if is_connected is not None:
                                cable_state = "Connected" if is_connected else "Disconnected"
                            else:
                                cable_state = "Unknown"
                            _driver_state.api.configured_entities.update_attributes(
                                cable_entity_id,
                                {SensorAttr.VALUE: cable_state, SensorAttr.STATE: SensorStates.ON}
                            )
                        
                        # Broadcast cable change via WebSocket if changed
                        prev_connected = _prev_cable_status.get("outputs", {}).get(output_num)
                        if prev_connected != is_connected and is_connected is not None:
                            await broadcast_status_update("cable_change", {
                                "type": "output",
                                "port": output_num,
                                "connected": is_connected,
                                "name": _driver_state.output_names.get(output_num, f"Output {output_num}")
                            })
                    
                    # Save current state for next comparison
                    _prev_cable_status = {
                        "inputs": input_cables.copy(),
                        "outputs": output_cables.copy()
                    }
                    
                    _LOG.debug(f"Cable status polling complete - inputs: {input_cables}, outputs: {output_cables}")
            
        except asyncio.CancelledError:
            _LOG.info("Status polling cancelled")
            break
        except Exception as e:
            _LOG.warning(f"Error during status polling: {e}")
            # Continue polling despite errors


def start_status_polling():
    """Start the background status polling task."""
    global _polling_task
    
    if not POLLING_ENABLED:
        _LOG.info("Status polling disabled (POLLING_ENABLED=false)")
        return
    
    if _polling_task is not None and not _polling_task.done():
        _LOG.warning("Status polling already running")
        return
    
    _polling_task = asyncio.create_task(status_polling_loop())
    _LOG.info("Status polling task started")


def stop_status_polling():
    """Stop the background status polling task."""
    global _polling_task
    
    if _polling_task is not None:
        _polling_task.cancel()
        _polling_task = None
        _LOG.info("Status polling task stopped")


async def on_connect() -> None:
    """Handle client connection."""
    _LOG.info("Client connected")
    
    # Connect to matrix if configured but not connected
    matrix = get_matrix()
    if matrix and not matrix.connected:
        _LOG.info("Connecting to matrix...")
        await matrix.connect()
    
    # Optionally refresh input names and update entities if changed
    if matrix and matrix.connected:
        try:
            _LOG.info("Querying input names on connect...")
            fresh_names = await matrix.get_all_input_names()
            
            # Check if names have changed
            if fresh_names != _driver_state.input_names:
                _LOG.info(f"Input names changed! Old: {_driver_state.input_names}, New: {fresh_names}")
                _LOG.info("Recreating entities with updated names...")
                
                # Store new names using accessor
                set_input_names(fresh_names)
                
                # Clear existing entities
                _driver_state.api.available_entities.clear()
                
                # Recreate remote entity with new names
                remote_entity = create_matrix_remote(_driver_state.input_names)
                _driver_state.api.available_entities.add(remote_entity)
                
                # Recreate button entities (presets use generic names)
                for preset_num in range(1, 9):
                    button = create_preset_button(preset_num)
                    _driver_state.api.available_entities.add(button)
                
                # Recreate CEC remote entities with new names
                for input_num in range(1, 9):
                    cec_remote = create_input_cec_remote(input_num, _driver_state.get_input_name(input_num))
                    _driver_state.api.available_entities.add(cec_remote)
                
                _LOG.info("✓ Entities updated with new input names")
            else:
                _LOG.debug("Input names unchanged")
                
        except Exception as ex:
            _LOG.warning(f"Failed to query input names on connect: {ex}")
    
    # Start status polling when client connects
    start_status_polling()
    
    await api.set_device_state(ucapi.DeviceStates.CONNECTED)


async def on_disconnect() -> None:
    """Handle client disconnection."""
    _LOG.info("Client disconnected")
    
    # Stop status polling when client disconnects
    stop_status_polling()


async def on_enter_standby() -> None:
    """Handle standby mode."""
    _LOG.info("Entering standby mode")
    
    # Stop polling in standby
    stop_status_polling()
    
    # Optionally disconnect from matrix to save resources
    matrix = get_matrix()
    if matrix and matrix.connected:
        await matrix.disconnect()


async def on_exit_standby() -> None:
    """Handle exit from standby mode."""
    _LOG.info("Exiting standby mode")
    # Reconnect to matrix
    matrix = get_matrix()
    if matrix and not matrix.connected:
        await matrix.connect()
    
    # Resume polling when exiting standby
    start_status_polling()


async def on_subscribe_entities(entity_ids: list[str]) -> None:
    """
    Subscribe to entities.

    :param entity_ids: entity identifiers.
    """
    _LOG.info("=" * 60)
    _LOG.info("SUBSCRIBE ENTITIES CALLED!")
    _LOG.info(f"Entity IDs to subscribe: {entity_ids}")
    _LOG.info("=" * 60)
    
    # Add each subscribed entity to configured_entities
    for entity_id in entity_ids:
        if _driver_state.api.available_entities.contains(entity_id):
            entity = _driver_state.api.available_entities.get(entity_id)
            _driver_state.api.configured_entities.add(entity)
            _LOG.info(f"Added entity to configured_entities: {entity_id}")
        else:
            _LOG.warning(f"Entity {entity_id} not found in available_entities")
    
    # Ensure matrix is connected
    matrix = get_matrix()
    if matrix and not matrix.connected:
        await matrix.connect()


async def on_unsubscribe_entities(entity_ids: list[str]) -> None:
    """
    Unsubscribe from entities.

    :param entity_ids: entity identifiers.
    """
    _LOG.info("=" * 60)
    _LOG.info("UNSUBSCRIBE ENTITIES CALLED!")
    _LOG.info(f"Entity IDs to unsubscribe: {entity_ids}")
    _LOG.info("=" * 60)
    
    # Remove each unsubscribed entity from configured_entities
    for entity_id in entity_ids:
        if _driver_state.api.configured_entities.contains(entity_id):
            _driver_state.api.configured_entities.remove(entity_id)
            _LOG.info(f"Removed entity from configured_entities: {entity_id}")
        else:
            _LOG.warning(f"Entity {entity_id} not found in configured_entities")


# =============================================================================
# Matrix Connection Event Handlers with Error Recovery
# =============================================================================

# Reconnection configuration
RECONNECT_DELAY_INITIAL = 5.0  # Initial delay before reconnection attempt (seconds)
RECONNECT_DELAY_MAX = 60.0  # Maximum delay between reconnection attempts
RECONNECT_BACKOFF_FACTOR = 2.0  # Exponential backoff multiplier

# Reconnection state tracking
_reconnect_task: asyncio.Task | None = None
_reconnect_attempt: int = 0


def _calculate_reconnect_delay() -> float:
    """Calculate delay for next reconnection attempt using exponential backoff."""
    global _reconnect_attempt
    delay = RECONNECT_DELAY_INITIAL * (RECONNECT_BACKOFF_FACTOR ** _reconnect_attempt)
    return min(delay, RECONNECT_DELAY_MAX)


async def _reconnect_loop() -> None:
    """Background task to handle automatic reconnection to the matrix."""
    global _reconnect_attempt
    
    while True:
        matrix = get_matrix()
        if matrix is None:
            _LOG.warning("No matrix device configured, stopping reconnection attempts")
            break
            
        if matrix.connected:
            _LOG.info("Matrix reconnected successfully, stopping reconnection loop")
            _reconnect_attempt = 0  # Reset counter on successful connection
            break
        
        delay = _calculate_reconnect_delay()
        _LOG.info(f"Reconnection attempt {_reconnect_attempt + 1} in {delay:.1f}s...")
        
        await asyncio.sleep(delay)
        
        try:
            success = await matrix.connect()
            if success:
                _LOG.info("✓ Matrix reconnected successfully!")
                _reconnect_attempt = 0
                
                # Notify UC that we're connected again
                await api.set_device_state(ucapi.DeviceStates.CONNECTED)
                
                # Restart status polling if it was running
                start_status_polling()
                break
            else:
                _reconnect_attempt += 1
                _LOG.warning(f"Reconnection attempt failed (attempt {_reconnect_attempt})")
        except Exception as e:
            _reconnect_attempt += 1
            _LOG.warning(f"Reconnection error: {e} (attempt {_reconnect_attempt})")
            
        # Cap the attempt counter to prevent overflow
        if _reconnect_attempt > 100:
            _reconnect_attempt = 10  # Reset to still use max delay


def _start_reconnection() -> None:
    """Start the reconnection background task if not already running."""
    global _reconnect_task
    
    if _reconnect_task is not None and not _reconnect_task.done():
        _LOG.debug("Reconnection task already running")
        return
    
    _LOG.info("Starting automatic reconnection...")
    _reconnect_task = asyncio.create_task(_reconnect_loop())


def _stop_reconnection() -> None:
    """Stop the reconnection background task."""
    global _reconnect_task, _reconnect_attempt
    
    if _reconnect_task is not None and not _reconnect_task.done():
        _reconnect_task.cancel()
        _LOG.info("Reconnection task cancelled")
    
    _reconnect_task = None
    _reconnect_attempt = 0


def on_matrix_connected():
    """Handle matrix connection event."""
    _LOG.info("Matrix connected successfully")
    
    # Stop any ongoing reconnection attempts
    _stop_reconnection()
    
    # Update entity states
    if _driver_state.api.configured_entities.contains("remote.orei_matrix"):
        _driver_state.api.configured_entities.update_attributes(
            "remote.orei_matrix",
            {RemoteAttr.STATE: ucapi.remote.States.ON}
        )
    
    # Update all connection sensors to show connected
    for output_num in range(1, 9):
        sensor_id = f"sensor.orei_output_{output_num}_connection"
        if _driver_state.api.configured_entities.contains(sensor_id):
            _LOG.debug(f"Updating connection sensor {sensor_id}")


def on_matrix_disconnected():
    """Handle matrix disconnection event."""
    _LOG.warning("Matrix disconnected - initiating automatic reconnection")
    
    # Update entity states
    if _driver_state.api.configured_entities.contains("remote.orei_matrix"):
        _driver_state.api.configured_entities.update_attributes(
            "remote.orei_matrix",
            {RemoteAttr.STATE: ucapi.remote.States.UNAVAILABLE}
        )
    
    # Stop polling while disconnected
    stop_status_polling()
    
    # Start automatic reconnection
    _start_reconnection()


def on_matrix_error(error: str):
    """Handle matrix error event."""
    _LOG.error("Matrix error: %s", error)
    
    # Check if we need to start reconnection
    matrix = get_matrix()
    if matrix and not matrix.connected:
        _start_reconnection()


def on_matrix_update(update: dict[str, Any]):
    """Handle matrix update event."""
    _LOG.debug("Matrix update: %s", update)


async def handle_driver_setup(msg: ucapi.DriverSetupRequest) -> ucapi.SetupAction:
    """
    Handle driver setup process.

    :param msg: Setup request data
    :return: Setup action
    """
    _LOG.info("Starting driver setup")
    _LOG.debug(f"Setup data: {msg.setup_data}")
    _LOG.debug(f"Reconfigure flag: {msg.reconfigure}")

    # Handle reconfiguration - this prevents "Data already exists" errors
    if msg.reconfigure:
        _LOG.info("Reconfiguring driver - clearing existing entities")
    else:
        _LOG.info("New driver setup - clearing entities")
    
    # Always clear entities to prevent duplicate registration issues
    # This is critical for proper setup flow
    _driver_state.api.available_entities.clear()
    _driver_state.api.configured_entities.clear()

    try:
        # Get configuration from setup data
        host = msg.setup_data.get("host", "192.168.0.100")
        port = int(msg.setup_data.get("port", 443))

        _LOG.info("Attempting to connect to matrix at %s:%d (HTTPS)", host, port)

        # Create matrix device instance and update driver state
        matrix = OreiMatrix(host, port)
        set_matrix(matrix)
        
        # Register event handlers
        matrix.events.on(MatrixEvents.CONNECTED, on_matrix_connected)
        matrix.events.on(MatrixEvents.DISCONNECTED, on_matrix_disconnected)
        matrix.events.on(MatrixEvents.ERROR, on_matrix_error)
        matrix.events.on(MatrixEvents.UPDATE, on_matrix_update)

        # Try to connect
        success = await matrix.connect()
        
        if not success:
            _LOG.error("Failed to connect to matrix")
            return ucapi.SetupError(error_type=ucapi.IntegrationSetupError.CONNECTION_REFUSED)

        # Query all status information from the matrix
        _LOG.info("Querying matrix status...")
        input_names = await matrix.get_all_input_names()
        output_names = await matrix.get_output_names()
        output_status = await matrix.get_output_status()
        input_status = await matrix.get_input_status()
        
        _LOG.info(f"Input names retrieved: {input_names}")
        _LOG.info(f"Output names retrieved: {output_names}")
        
        # Get output connections
        output_connections = output_status.get("allconnect", [0]*8) if output_status else [0]*8
        _LOG.info(f"Output connections: {output_connections}")
        
        # Get input signal status (inactive inputs = no signal)
        input_inactive = input_status.get("inactive", []) if input_status else []
        _LOG.info(f"Inactive inputs (no signal): {input_inactive}")

        # Store names in driver state using accessor functions
        set_input_names(input_names if input_names else {})
        set_output_names(output_names if output_names else {})

        # Create and register entities
        _LOG.info("Creating entities...")
        
        # === CORE ENTITIES ===
        
        # Create remote entity with input names for source selection
        remote_entity = create_matrix_remote(_driver_state.input_names)
        _LOG.info(f"Adding remote entity: {remote_entity.id}")
        _driver_state.api.available_entities.add(remote_entity)
        
        # Create individual preset buttons (presets use generic names)
        for preset_num in range(1, 9):
            button = create_preset_button(preset_num)
            _LOG.info(f"Adding button entity: {button.id}")
            _driver_state.api.available_entities.add(button)

        # Create CEC remote entities for each input device
        for input_num in range(1, 9):
            cec_remote = create_input_cec_remote(input_num, _driver_state.get_input_name(input_num))
            _LOG.info(f"Adding input CEC remote entity: {cec_remote.id}")
            _driver_state.api.available_entities.add(cec_remote)

        # Input signal sensors
        for input_num in range(1, 9):
            input_name = _driver_state.get_input_name(input_num)
            signal_sensor = create_input_signal_sensor(input_num, input_name)
            # Update sensor with actual signal status
            # inactive array: 0 = signal present, 1 = no signal (at index input_num - 1)
            idx = input_num - 1
            has_signal = input_inactive[idx] == 1 if idx < len(input_inactive) else False
            signal_sensor.attributes[SensorAttr.VALUE] = "Active" if has_signal else "No Signal"
            _LOG.info(f"Adding input signal sensor entity: {signal_sensor.id}")
            _driver_state.api.available_entities.add(signal_sensor)

        # Input cable connection sensors (Telnet-based)
        for input_num in range(1, 9):
            input_name = _driver_state.get_input_name(input_num)
            cable_sensor = create_input_cable_sensor(input_num, input_name)
            # Initial status will be updated by polling when Telnet connects
            _LOG.info(f"Adding input cable sensor entity: {cable_sensor.id}")
            _driver_state.api.available_entities.add(cable_sensor)

        # === ENHANCED ENTITIES ===
        
        # Matrix power switch
        power_switch = create_matrix_power_switch()
        _LOG.info(f"Adding power switch entity: {power_switch.id}")
        _driver_state.api.available_entities.add(power_switch)
        
        # For each output: MediaPlayer, CEC Remote, and Sensors
        for output_num in range(1, 9):
            output_name = _driver_state.get_output_name(output_num)
            
            # MediaPlayer for source selection on this output
            media_player = create_output_media_player(output_num, output_name, _driver_state.input_names)
            _LOG.info(f"Adding media player entity: {media_player.id}")
            _driver_state.api.available_entities.add(media_player)
            
            # CEC remote for controlling the TV/display on this output
            output_cec = create_output_cec_remote(output_num, output_name)
            _LOG.info(f"Adding output CEC remote entity: {output_cec.id}")
            _driver_state.api.available_entities.add(output_cec)
            
            # Connection sensor for this output (HTTP-based)
            conn_sensor = create_connection_sensor(output_num, output_name)
            is_connected = output_connections[output_num - 1] == 1 if len(output_connections) >= output_num else False
            conn_sensor.attributes[SensorAttr.VALUE] = "Connected" if is_connected else "Disconnected"
            _LOG.info(f"Adding connection sensor entity: {conn_sensor.id}")
            _driver_state.api.available_entities.add(conn_sensor)
            
            # Cable sensor for this output (Telnet-based)
            cable_sensor = create_output_cable_sensor(output_num, output_name)
            # Initial status will be updated by polling when Telnet connects
            _LOG.info(f"Adding output cable sensor entity: {cable_sensor.id}")
            _driver_state.api.available_entities.add(cable_sensor)
            
            # Routing sensor for this output
            routing_sensor = create_routing_sensor(output_num, output_name)
            _LOG.info(f"Adding routing sensor entity: {routing_sensor.id}")
            _driver_state.api.available_entities.add(routing_sensor)

        entity_count = len(_driver_state.api.available_entities._storage)
        _LOG.info(f"Setup complete - Total available entities: {entity_count}")
        
        # List all entities
        for entity_id in _driver_state.api.available_entities._storage.keys():
            _LOG.info(f"  - {entity_id}")
        
        # Save configuration for persistence across restarts
        save_config(host, port, _driver_state.input_names, _driver_state.output_names)
        
        # Update REST API with the new matrix device, names, and config file
        set_matrix_device(
            get_matrix(), 
            input_names=_driver_state.input_names,
            output_names=_driver_state.output_names,
            config_file=CONFIG_FILE
        )
        
        # Configure CEC sender for macros
        async def cec_sender(target_type: str, port: int, command: str) -> bool:
            """Send CEC command via matrix device."""
            matrix = get_matrix()
            if not matrix or not matrix.connected:
                return False
            # Normalize command to lowercase for method lookup
            command = command.lower()
            method_name = f"cec_{target_type}_{command}"
            method = getattr(matrix, method_name, None)
            if method:
                return await method(port)
            if command in ("enable", "disable"):
                return await matrix.set_cec_enable(target_type, port, command == "enable")
            return False
        
        set_macro_cec_sender(cec_sender)
        
        return ucapi.SetupComplete()
        
    except Exception as e:
        _LOG.error(f"Setup failed with exception: {e}", exc_info=True)
        return ucapi.SetupError(error_type=ucapi.IntegrationSetupError.OTHER)


async def setup_handler(msg: ucapi.SetupDriver) -> ucapi.SetupAction:
    """
    Dispatch driver setup requests.

    :param msg: Setup driver request
    :return: Setup action
    """
    _LOG.info(f"=== SETUP HANDLER CALLED ===")
    _LOG.info(f"Message type: {type(msg).__name__}")
    _LOG.info(f"Message content: {msg}")
    
    if isinstance(msg, ucapi.DriverSetupRequest):
        _LOG.info("Processing DriverSetupRequest")
        result = await handle_driver_setup(msg)
        _LOG.info(f"Setup handler returning: {type(result).__name__}")
        return result
    
    _LOG.error(f"Unsupported setup message type: {type(msg)}")
    return ucapi.SetupError()


async def shutdown(loop):
    """Cleanup tasks tied to the service's shutdown."""
    global _rest_api_server
    
    _LOG.info("Shutting down integration...")
    
    # Stop reconnection task
    _stop_reconnection()
    
    # Stop status polling
    stop_status_polling()
    
    # Stop REST API server
    if _rest_api_server and _rest_api_server.running:
        _LOG.info("Stopping REST API server...")
        try:
            await _rest_api_server.stop()
        except Exception as e:
            _LOG.warning(f"Error stopping REST API server: {e}")
    
    # Disconnect from matrix
    matrix = get_matrix()
    if matrix and matrix.connected:
        _LOG.info("Disconnecting from matrix...")
        try:
            await matrix.disconnect()
        except Exception as e:
            _LOG.warning(f"Error disconnecting from matrix: {e}")
    
    # Cancel all remaining tasks
    _LOG.info("Cancelling background tasks...")
    tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
    
    for task in tasks:
        if not task.done():
            task.cancel()
    
    # Wait for all tasks to complete cancellation, suppressing exceptions
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Log any non-cancellation errors
        for i, result in enumerate(results):
            if isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
                # Suppress the known OSError 10048 from ucapi's web socket server
                if not (isinstance(result, OSError) and result.errno == 10048):
                    _LOG.warning(f"Task {tasks[i].get_name()} raised: {result}")
    
    _LOG.info("Shutdown cleanup complete")


def handle_exit_signal(signame, loop):
    """Handle exit signals."""
    _LOG.info(f"Received {signame}, initiating shutdown...")
    asyncio.create_task(shutdown(loop))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    _LOG.info("Starting OREI HDMI Matrix integration driver")
    
    # Register cleanup on exit
    atexit.register(release_lock)
    
    # Acquire lock to prevent multiple instances
    if not acquire_lock():
        _LOG.error("Failed to acquire lock - another instance may be running")
        _LOG.info("Waiting 5 seconds for previous instance to release...")
        time.sleep(5)
        if not acquire_lock():
            _LOG.error("Still cannot acquire lock. Exiting.")
            sys.exit(1)
    
    # Check if port 9095 is available, wait if not
    if not check_port_available(9095):
        _LOG.warning("Port 9095 is in use, waiting for it to become available...")
        if not wait_for_port(9095, timeout=15):
            _LOG.error("Could not bind to port 9095. Exiting.")
            release_lock()
            sys.exit(1)
    
    # Clear any stale mDNS entries from previous crashed instances
    clear_stale_mdns()

    # Create event loop and API - set global api variable
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Set custom exception handler to suppress known ucapi errors
    def handle_exception(loop, context):
        exception = context.get("exception")
        # Suppress OSError 10048 from ucapi's web socket server
        if isinstance(exception, OSError) and exception.errno == 10048:
            return
        # Log other exceptions
        loop.default_exception_handler(context)
    
    loop.set_exception_handler(handle_exception)
    
    api = ucapi.IntegrationAPI(loop)
    _driver_state.api = api
    
    # Register event handlers after API is created
    api.add_listener(ucapi.Events.CONNECT, on_connect)
    api.add_listener(ucapi.Events.DISCONNECT, on_disconnect)
    api.add_listener(ucapi.Events.ENTER_STANDBY, on_enter_standby)
    api.add_listener(ucapi.Events.EXIT_STANDBY, on_exit_standby)
    api.add_listener(ucapi.Events.SUBSCRIBE_ENTITIES, on_subscribe_entities)
    api.add_listener(ucapi.Events.UNSUBSCRIBE_ENTITIES, on_unsubscribe_entities)

    # Restore entities from saved configuration BEFORE starting the API
    # This ensures entities exist when Remote 3 tries to subscribe to them
    _LOG.info("Attempting to restore from saved configuration...")
    loop.run_until_complete(restore_from_config())

    # Initialize API with retry logic for mDNS issues
    # mDNS records typically have TTL of 75-120 seconds, so we need to wait long enough
    max_retries = 6
    retry_delay = 5  # Start with 5 seconds
    
    for attempt in range(max_retries):
        try:
            _LOG.info(f"Initializing API (attempt {attempt + 1}/{max_retries})...")
            loop.run_until_complete(api.init("driver.json", setup_handler))
            _LOG.info("API initialized successfully")
            break
        except Exception as e:
            if "NonUniqueNameException" in str(type(e).__name__) or "NonUniqueNameException" in str(e):
                total_wait = retry_delay
                _LOG.warning(f"mDNS name conflict (attempt {attempt + 1}/{max_retries}), waiting {retry_delay}s before retry...")
                _LOG.info("This can happen if a previous instance didn't shut down cleanly.")
                _LOG.info("The mDNS cache will clear automatically - please wait...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay + 5, 30)  # Linear increase, max 30 seconds
                if attempt == max_retries - 1:
                    _LOG.error("Failed to initialize API after all retries. mDNS name still in use.")
                    _LOG.error("Try waiting 2 minutes and restarting, or reboot the computer.")
                    release_lock()
                    sys.exit(1)
            else:
                _LOG.error(f"Failed to initialize API: {e}", exc_info=True)
                release_lock()
                sys.exit(1)

    # Start REST API server for external integrations (Flic, Home Assistant, etc.)
    if REST_API_ENABLED:
        _LOG.info(f"Starting REST API server on port {REST_API_PORT}...")
        _rest_api_server = RestApiServer(port=REST_API_PORT)
        globals()['_rest_api_server'] = _rest_api_server
        try:
            loop.run_until_complete(_rest_api_server.start())
        except Exception as e:
            _LOG.error(f"Failed to start REST API server: {e}")
            _LOG.warning("Continuing without REST API - UC integration will still work")
    else:
        _LOG.info("REST API server disabled (REST_API_ENABLED=false)")

    # Handle graceful shutdown signals (important for Docker)
    def signal_handler(sig, frame):
        _LOG.info(f"Received signal {sig}, initiating shutdown...")
        loop.call_soon_threadsafe(loop.stop)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        _LOG.info("Driver running. Press Ctrl+C to stop.")
        loop.run_forever()
    except KeyboardInterrupt:
        _LOG.info("Keyboard interrupt received")
    except Exception as e:
        _LOG.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        _LOG.info("Cleaning up...")
        try:
            loop.run_until_complete(shutdown(loop))
        except Exception as e:
            _LOG.warning(f"Error during shutdown: {e}")
        loop.close()
        release_lock()
        _LOG.info("Shutdown complete")
