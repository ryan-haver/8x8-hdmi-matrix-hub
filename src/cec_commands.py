"""
CEC Command Registry for OREI HDMI Matrix.

Centralized definitions for all CEC commands supported by input and output devices.
Based on Control4 driver analysis and OREI API documentation.

Input devices (sources): 19 commands supported
Output devices (displays): 6 commands supported
"""

from typing import Dict, List, Set

# =============================================================================
# Input CEC Commands (Source devices: PS5, Apple TV, Roku, etc.)
# =============================================================================

INPUT_CEC_COMMANDS: Dict[str, Dict] = {
    # Power commands
    "POWER_ON": {
        "index": 1,
        "telnet": "on",
        "category": "power",
        "description": "Power on the device",
    },
    "POWER_OFF": {
        "index": 2,
        "telnet": "off",
        "category": "power",
        "description": "Power off / standby",
    },
    # Navigation commands
    "UP": {
        "index": 3,
        "telnet": "up",
        "category": "navigation",
        "description": "D-pad up",
    },
    "LEFT": {
        "index": 4,
        "telnet": "left",
        "category": "navigation",
        "description": "D-pad left",
    },
    "SELECT": {
        "index": 5,
        "telnet": "enter",
        "category": "navigation",
        "description": "Select / OK / Enter",
    },
    "RIGHT": {
        "index": 6,
        "telnet": "right",
        "category": "navigation",
        "description": "D-pad right",
    },
    "DOWN": {
        "index": 7,
        "telnet": "down",
        "category": "navigation",
        "description": "D-pad down",
    },
    # Playback commands
    "PLAY": {
        "index": 8,
        "telnet": "play",
        "category": "playback",
        "description": "Play",
    },
    "PAUSE": {
        "index": 9,
        "telnet": "pause",
        "category": "playback",
        "description": "Pause",
    },
    "STOP": {
        "index": 10,
        "telnet": "stop",
        "category": "playback",
        "description": "Stop",
    },
    "REWIND": {
        "index": 11,
        "telnet": "rew",
        "category": "playback",
        "description": "Rewind",
    },
    "FAST_FORWARD": {
        "index": 12,
        "telnet": "ff",
        "category": "playback",
        "description": "Fast forward",
    },
    "PREVIOUS": {
        "index": 13,
        "telnet": "previous",
        "category": "playback",
        "description": "Previous track/chapter",
    },
    "NEXT": {
        "index": 14,
        "telnet": "next",
        "category": "playback",
        "description": "Next track/chapter",
    },
    # Volume commands
    "VOLUME_UP": {
        "index": 15,
        "telnet": "vol+",
        "category": "volume",
        "description": "Volume up",
    },
    "VOLUME_DOWN": {
        "index": 16,
        "telnet": "vol-",
        "category": "volume",
        "description": "Volume down",
    },
    "MUTE": {
        "index": 17,
        "telnet": "mute",
        "category": "volume",
        "description": "Mute toggle",
    },
    # Menu commands
    "MENU": {
        "index": 18,
        "telnet": "menu",
        "category": "navigation",
        "description": "Menu / Home",
    },
    "BACK": {
        "index": 19,
        "telnet": "back",
        "category": "navigation",
        "description": "Back / Return",
    },
}

# =============================================================================
# Output CEC Commands (Display devices: TVs, Projectors, Soundbars)
# =============================================================================

OUTPUT_CEC_COMMANDS: Dict[str, Dict] = {
    # Power commands
    "POWER_ON": {
        "index": 1,
        "telnet": "on",
        "category": "power",
        "description": "Power on the display",
    },
    "POWER_OFF": {
        "index": 2,
        "telnet": "off",
        "category": "power",
        "description": "Power off / standby",
    },
    # Volume commands (primary use case for outputs)
    "MUTE": {
        "index": 3,
        "telnet": "mute",
        "category": "volume",
        "description": "Mute toggle",
    },
    "VOLUME_UP": {
        "index": 4,
        "telnet": "vol+",
        "category": "volume",
        "description": "Volume up",
    },
    "VOLUME_DOWN": {
        "index": 5,
        "telnet": "vol-",
        "category": "volume",
        "description": "Volume down",
    },
    # Special commands
    "ACTIVE": {
        "index": 6,
        "telnet": "active",
        "category": "source",
        "description": "Set as active source (make TV switch to this input)",
    },
}

# =============================================================================
# Command Categories
# =============================================================================

CEC_CATEGORIES: Dict[str, List[str]] = {
    "power": ["POWER_ON", "POWER_OFF"],
    "navigation": ["UP", "DOWN", "LEFT", "RIGHT", "SELECT", "MENU", "BACK"],
    "playback": ["PLAY", "PAUSE", "STOP", "REWIND", "FAST_FORWARD", "PREVIOUS", "NEXT"],
    "volume": ["VOLUME_UP", "VOLUME_DOWN", "MUTE"],
    "source": ["ACTIVE"],
}

# =============================================================================
# Helper Functions
# =============================================================================

def get_input_commands() -> List[str]:
    """Get list of all input CEC command names."""
    return list(INPUT_CEC_COMMANDS.keys())


def get_output_commands() -> List[str]:
    """Get list of all output CEC command names."""
    return list(OUTPUT_CEC_COMMANDS.keys())


def get_commands_by_category(category: str, device_type: str = "input") -> List[str]:
    """
    Get commands for a specific category filtered by device type.
    
    :param category: Command category (power, navigation, playback, volume, source)
    :param device_type: "input" or "output"
    :return: List of command names available for that device type and category
    """
    commands = CEC_CATEGORIES.get(category, [])
    cmd_registry = INPUT_CEC_COMMANDS if device_type == "input" else OUTPUT_CEC_COMMANDS
    return [cmd for cmd in commands if cmd in cmd_registry]


def get_command_info(command: str, device_type: str = "input") -> Dict | None:
    """
    Get full command info for a specific command.
    
    :param command: Command name (e.g., "POWER_ON")
    :param device_type: "input" or "output"
    :return: Command info dict or None if not found
    """
    cmd_registry = INPUT_CEC_COMMANDS if device_type == "input" else OUTPUT_CEC_COMMANDS
    return cmd_registry.get(command)


def get_command_index(command: str, device_type: str = "input") -> int | None:
    """
    Get the HTTP API command index for a command.
    
    :param command: Command name (e.g., "POWER_ON")
    :param device_type: "input" or "output"
    :return: Command index or None if not found
    """
    info = get_command_info(command, device_type)
    return info.get("index") if info else None


def get_telnet_command(command: str, device_type: str = "input") -> str | None:
    """
    Get the Telnet command string for a command.
    
    :param command: Command name (e.g., "POWER_ON")
    :param device_type: "input" or "output"
    :return: Telnet command string or None if not found
    """
    info = get_command_info(command, device_type)
    return info.get("telnet") if info else None


def get_supported_categories(device_type: str = "input") -> List[str]:
    """
    Get list of CEC categories supported by a device type.
    
    :param device_type: "input" or "output"
    :return: List of category names
    """
    cmd_registry = INPUT_CEC_COMMANDS if device_type == "input" else OUTPUT_CEC_COMMANDS
    categories = set()
    for cmd_info in cmd_registry.values():
        categories.add(cmd_info["category"])
    return list(categories)


def get_all_commands_detailed(device_type: str = "input") -> Dict[str, Dict]:
    """
    Get all commands with full details for a device type.
    
    :param device_type: "input" or "output"
    :return: Dict of command name -> command info
    """
    return INPUT_CEC_COMMANDS.copy() if device_type == "input" else OUTPUT_CEC_COMMANDS.copy()


# =============================================================================
# Scaler Mode Constants (for audio_only detection)
# =============================================================================

class ScalerMode:
    """Scaler mode constants (0-indexed as returned by matrix)."""
    BYPASS = 0          # Passthrough
    DOWNSCALE_8K_4K = 1  # 8K → 4K
    DOWNSCALE_1080P = 2  # 8K/4K → 1080p
    AUTO = 3            # Auto
    AUDIO_ONLY = 4      # Audio Only (key for CEC routing!)


# API uses 1-indexed values
class ScalerModeAPI:
    """Scaler mode constants (1-indexed for our REST API)."""
    PASSTHROUGH = 1
    DOWNSCALE_8K_4K = 2
    DOWNSCALE_1080P = 3
    AUTO = 4
    AUDIO_ONLY = 5


def is_audio_only_output(scaler_value: int, api_indexed: bool = False) -> bool:
    """
    Check if an output is configured as audio-only based on scaler mode.
    
    :param scaler_value: Scaler mode value
    :param api_indexed: True if value is 1-indexed (from our API), False if 0-indexed (from matrix)
    :return: True if audio-only mode
    """
    if api_indexed:
        return scaler_value == ScalerModeAPI.AUDIO_ONLY
    return scaler_value == ScalerMode.AUDIO_ONLY
