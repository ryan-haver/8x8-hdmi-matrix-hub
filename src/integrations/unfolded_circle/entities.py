"""
Entity Factory Functions for Unfolded Circle Integration.

This module provides factory functions for creating UC entities that can
work with either direct matrix communication or via the REST API client.

The approach supports a gradual migration:
1. Direct mode (current): Uses OreiMatrix directly with get_matrix()
2. API mode (new): Uses MatrixApiClient for all operations

This allows the UC driver to be run either co-located with the API
or as a separate process consuming the API.
"""

import asyncio
import logging
from typing import Any, Callable, Optional, Protocol

import ucapi
from ucapi import Button, StatusCodes
from ucapi.remote import Remote
from ucapi.remote import Attributes as RemoteAttr
from ucapi.remote import Features as RemoteFeatures
from ucapi.remote import Commands as RemoteCommands

_LOG = logging.getLogger("uc.entities")


class MatrixBackend(Protocol):
    """Protocol defining the interface for matrix operations.
    
    This protocol allows entity factory functions to work with either:
    - OreiMatrix (direct hardware access)
    - MatrixApiClient (REST API access)
    """
    
    async def recall_preset(self, preset: int) -> bool:
        """Recall a preset configuration."""
        ...
    
    async def switch_input(self, input_num: int, output_num: int) -> bool:
        """Route an input to an output."""
        ...
    
    # CEC methods follow the API client interface
    async def send_cec_input(self, input_num: int, command: str) -> bool:
        """Send CEC command to an input device."""
        ...
    
    async def send_cec_output(self, output_num: int, command: str) -> bool:
        """Send CEC command to an output device."""
        ...


class EntityContext:
    """
    Context object that holds references to shared state for entities.
    
    This decouples entities from global state, making them testable
    and allowing different backends to be injected.
    """
    
    def __init__(
        self,
        get_backend: Callable[[], Optional[MatrixBackend]],
        get_input_names: Callable[[], dict[int, str]],
        get_output_names: Callable[[], dict[int, str]],
    ):
        self.get_backend = get_backend
        self.get_input_names = get_input_names
        self.get_output_names = get_output_names
    
    def get_input_name(self, port: int) -> str:
        """Get input name with fallback."""
        names = self.get_input_names()
        return names.get(port, f"Input {port}")
    
    def get_output_name(self, port: int) -> str:
        """Get output name with fallback."""
        names = self.get_output_names()
        return names.get(port, f"Output {port}")


def create_preset_button_with_context(
    preset_num: int,
    ctx: EntityContext,
    preset_name: str = None
) -> Button:
    """
    Create a button entity for a specific preset using injected context.
    
    :param preset_num: Preset number (1-8)
    :param ctx: Entity context with backend access
    :param preset_name: Custom name for the preset (optional)
    :return: Button entity
    """
    display_name = preset_name if preset_name else f"Preset {preset_num}"

    async def preset_cmd_handler(
        entity: Button, cmd_id: str, _params: dict[str, Any] | None, websocket: Any
    ) -> StatusCodes:
        """Handle preset button press."""
        _LOG.info(f"Preset {preset_num} ({display_name}) button pressed")
        
        backend = ctx.get_backend()
        if backend is None:
            _LOG.error("Backend not available")
            return StatusCodes.SERVICE_UNAVAILABLE

        try:
            success = await backend.recall_preset(preset_num)
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
        except Exception as e:
            _LOG.error(f"Preset recall failed: {e}")
            return StatusCodes.SERVER_ERROR

    button = Button(
        f"button.preset_{preset_num}",
        display_name,
        cmd_handler=preset_cmd_handler,
    )
    return button


# CEC command list shared by remotes
CEC_INPUT_COMMANDS = [
    "POWER_ON", "POWER_OFF",
    "UP", "DOWN", "LEFT", "RIGHT", "SELECT",
    "MENU", "BACK",
    "PLAY", "PAUSE", "STOP",
    "PREVIOUS", "NEXT",
    "REWIND", "FAST_FORWARD",
    "VOLUME_UP", "VOLUME_DOWN", "MUTE"
]

CEC_OUTPUT_COMMANDS = [
    "POWER_ON", "POWER_OFF",
    "UP", "DOWN", "LEFT", "RIGHT", "SELECT",
    "MENU", "BACK",
    "VOLUME_UP", "VOLUME_DOWN", "MUTE"
]

# Remote command to CEC command mapping
# These are string constants that match what UC Remote sends
NATIVE_CMD_MAP = {
    "cursor_up": "UP",
    "cursor_down": "DOWN",
    "cursor_left": "LEFT",
    "cursor_right": "RIGHT",
    "cursor_enter": "SELECT",
    "menu": "MENU",
    "back": "BACK",
    "play_pause": "PLAY",
    "previous": "PREVIOUS",
    "next": "NEXT",
    "fast_forward": "FAST_FORWARD",
    "rewind": "REWIND",
    "volume_up": "VOLUME_UP",
    "volume_down": "VOLUME_DOWN",
    "mute_toggle": "MUTE",
    "power_on": "POWER_ON",
    "power_off": "POWER_OFF",
    "power_toggle": "POWER_ON",
}


def create_cec_command_handler_with_context(
    port_num: int,
    port_type: str,  # "input" or "output"
    ctx: EntityContext,
) -> Callable:
    """
    Factory function to create CEC command handlers using injected context.
    
    :param port_num: Input or output number (1-8)
    :param port_type: "input" or "output"
    :param ctx: Entity context with backend access
    :return: Async command handler function
    """
    
    async def cec_cmd_handler(
        entity: Remote, cmd_id: str, params: dict[str, Any] | None, websocket: Any
    ) -> StatusCodes:
        """Handle CEC remote commands."""
        _LOG.info(f"{port_type.upper()} CEC: {entity.id} -> {cmd_id}")

        backend = ctx.get_backend()
        if backend is None:
            _LOG.error("Backend not available")
            return StatusCodes.SERVICE_UNAVAILABLE

        # Determine which CEC command to send
        cec_command = None
        
        # Handle SEND_CMD for simple commands
        if cmd_id == ucapi.remote.Commands.SEND_CMD:
            if params and "command" in params:
                cec_command = params["command"]
        # Handle native remote commands (D-pad, playback buttons)
        elif cmd_id in NATIVE_CMD_MAP:
            cec_command = NATIVE_CMD_MAP[cmd_id]
        
        if not cec_command:
            _LOG.warning(f"Command not implemented: {cmd_id}")
            return StatusCodes.NOT_IMPLEMENTED

        try:
            if port_type == "input":
                success = await backend.send_cec_input(port_num, cec_command)
            else:
                success = await backend.send_cec_output(port_num, cec_command)
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
        except Exception as e:
            _LOG.error(f"CEC command failed: {e}")
            return StatusCodes.SERVER_ERROR
    
    return cec_cmd_handler


def create_input_cec_remote_with_context(
    input_num: int,
    ctx: EntityContext,
    input_name: str = None
) -> Remote:
    """
    Create a remote entity for CEC control of a specific input device.
    
    :param input_num: Input number (1-8)
    :param ctx: Entity context with backend access
    :param input_name: Custom name for the input (optional)
    :return: Remote entity
    """
    display_name = input_name if input_name else ctx.get_input_name(input_num)
    entity_id = f"remote.input_{input_num}_cec"

    cec_cmd_handler = create_cec_command_handler_with_context(
        input_num, "input", ctx
    )

    # Create UI pages for the remote
    from ucapi.ui import Size, UiPage, create_ui_text

    nav_page = UiPage(
        f"input_{input_num}_nav",
        "Navigation",
        grid=Size(4, 6),
        items=[
            create_ui_text("Power On", 0, 0, Size(2, 1), "POWER_ON"),
            create_ui_text("Power Off", 2, 0, Size(2, 1), "POWER_OFF"),
            create_ui_text("▲", 1, 1, Size(2, 1), "UP"),
            create_ui_text("◀", 0, 2, Size(1, 1), "LEFT"),
            create_ui_text("OK", 1, 2, Size(2, 1), "SELECT"),
            create_ui_text("▶", 3, 2, Size(1, 1), "RIGHT"),
            create_ui_text("▼", 1, 3, Size(2, 1), "DOWN"),
            create_ui_text("Menu", 0, 4, Size(2, 1), "MENU"),
            create_ui_text("Back", 2, 4, Size(2, 1), "BACK"),
        ],
    )

    playback_page = UiPage(
        f"input_{input_num}_playback",
        "Playback",
        grid=Size(4, 6),
        items=[
            create_ui_text("⏮", 0, 0, Size(1, 1), "PREVIOUS"),
            create_ui_text("⏪", 1, 0, Size(1, 1), "REWIND"),
            create_ui_text("⏩", 2, 0, Size(1, 1), "FAST_FORWARD"),
            create_ui_text("⏭", 3, 0, Size(1, 1), "NEXT"),
            create_ui_text("▶ Play", 0, 1, Size(2, 1), "PLAY"),
            create_ui_text("⏸ Pause", 2, 1, Size(2, 1), "PAUSE"),
            create_ui_text("⏹ Stop", 1, 2, Size(2, 1), "STOP"),
            create_ui_text("🔉 Vol-", 0, 3, Size(1, 1), "VOLUME_DOWN"),
            create_ui_text("🔇 Mute", 1, 3, Size(2, 1), "MUTE"),
            create_ui_text("🔊 Vol+", 3, 3, Size(1, 1), "VOLUME_UP"),
        ],
    )

    remote = Remote(
        entity_id,
        f"{display_name} CEC",
        [
            RemoteFeatures.SEND_CMD,
            RemoteFeatures.ON_OFF,
        ],
        attributes={RemoteAttr.STATE: ucapi.remote.States.ON},
        simple_commands=CEC_INPUT_COMMANDS,
        ui_pages=[nav_page, playback_page],
        cmd_handler=cec_cmd_handler,
    )

    return remote


def create_output_cec_remote_with_context(
    output_num: int,
    ctx: EntityContext,
    output_name: str = None
) -> Remote:
    """
    Create a remote entity for CEC control of an output device (TV/display).
    
    :param output_num: Output number (1-8)
    :param ctx: Entity context with backend access
    :param output_name: Custom name for the output (optional)
    :return: Remote entity
    """
    display_name = output_name if output_name else ctx.get_output_name(output_num)
    entity_id = f"remote.output_{output_num}_cec"

    cec_cmd_handler = create_cec_command_handler_with_context(
        output_num, "output", ctx
    )

    from ucapi.ui import Size, UiPage, create_ui_text

    control_page = UiPage(
        f"output_{output_num}_control",
        "TV Control",
        grid=Size(4, 6),
        items=[
            create_ui_text("📺 Power On", 0, 0, Size(2, 1), "POWER_ON"),
            create_ui_text("⏻ Power Off", 2, 0, Size(2, 1), "POWER_OFF"),
            create_ui_text("▲", 1, 1, Size(2, 1), "UP"),
            create_ui_text("◀", 0, 2, Size(1, 1), "LEFT"),
            create_ui_text("OK", 1, 2, Size(2, 1), "SELECT"),
            create_ui_text("▶", 3, 2, Size(1, 1), "RIGHT"),
            create_ui_text("▼", 1, 3, Size(2, 1), "DOWN"),
            create_ui_text("Menu", 0, 4, Size(2, 1), "MENU"),
            create_ui_text("Back", 2, 4, Size(2, 1), "BACK"),
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
        simple_commands=CEC_OUTPUT_COMMANDS,
        ui_pages=[control_page],
        cmd_handler=cec_cmd_handler,
    )

    return remote
