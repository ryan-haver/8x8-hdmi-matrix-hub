"""
CEC Command Registry for OREI HDMI Matrix.

Centralized definitions for all CEC commands supported by input and
output devices.

.. warning::
    The ``index`` fields historically defined in this module were
    derived from a Control4 driver analysis and **do not match** the
    HAR-captured indices in :class:`orei_matrix.OreiMatrix.CEC_COMMAND_MAP`.

    Using these indices with the HTTP path would send the wrong commands
    (e.g. "Volume Down" instead of "Down"). They have been removed.

    The authoritative source of CEC indices is
    ``orei_matrix.OreiMatrix.CEC_COMMAND_MAP`` (HAR-verified). The
    authoritative source of Telnet command strings is the ``telnet``
    field in this module (used by :mod:`telnet_client`).

Input devices (sources): 19 commands supported
Output devices (displays): 6 commands supported
"""


# =============================================================================
# Input CEC Commands (Source devices: PS5, Apple TV, Roku, etc.)
# =============================================================================

INPUT_CEC_COMMANDS: dict[str, dict] = {
    # Power commands
    "POWER_ON": {
        "telnet": "on",
        "category": "power",
        "description": "Power on the device",
    },
    "POWER_OFF": {
        "telnet": "off",
        "category": "power",
        "description": "Power off / standby",
    },
    # Navigation commands
    "UP": {
        "telnet": "up",
        "category": "navigation",
        "description": "D-pad up",
    },
    "LEFT": {
        "telnet": "left",
        "category": "navigation",
        "description": "D-pad left",
    },
    "SELECT": {
        "telnet": "enter",
        "category": "navigation",
        "description": "Select / OK / Enter",
    },
    "RIGHT": {
        "telnet": "right",
        "category": "navigation",
        "description": "D-pad right",
    },
    "DOWN": {
        "telnet": "down",
        "category": "navigation",
        "description": "D-pad down",
    },
    # Playback commands
    "PLAY": {
        "telnet": "play",
        "category": "playback",
        "description": "Play",
    },
    "PAUSE": {
        "telnet": "pause",
        "category": "playback",
        "description": "Pause",
    },
    "STOP": {
        "telnet": "stop",
        "category": "playback",
        "description": "Stop",
    },
    "REWIND": {
        "telnet": "rew",
        "category": "playback",
        "description": "Rewind",
    },
    "FAST_FORWARD": {
        "telnet": "ff",
        "category": "playback",
        "description": "Fast forward",
    },
    "PREVIOUS": {
        "telnet": "previous",
        "category": "playback",
        "description": "Previous track/chapter",
    },
    "NEXT": {
        "telnet": "next",
        "category": "playback",
        "description": "Next track/chapter",
    },
    # Volume commands
    "VOLUME_UP": {
        "telnet": "vol+",
        "category": "volume",
        "description": "Volume up",
    },
    "VOLUME_DOWN": {
        "telnet": "vol-",
        "category": "volume",
        "description": "Volume down",
    },
    "MUTE": {
        "telnet": "mute",
        "category": "volume",
        "description": "Mute toggle",
    },
    # Menu commands
    "MENU": {
        "telnet": "menu",
        "category": "navigation",
        "description": "Menu / Home",
    },
    "BACK": {
        "telnet": "back",
        "category": "navigation",
        "description": "Back / Return",
    },
}

# =============================================================================
# Output CEC Commands (Display devices: TVs, Projectors, Soundbars)
# =============================================================================

OUTPUT_CEC_COMMANDS: dict[str, dict] = {
    # Power commands
    "POWER_ON": {
        "telnet": "on",
        "category": "power",
        "description": "Power on the display",
    },
    "POWER_OFF": {
        "telnet": "off",
        "category": "power",
        "description": "Power off the display",
    },
    # Volume commands (primary use case for outputs)
    "MUTE": {
        "telnet": "mute",
        "category": "volume",
        "description": "Mute toggle",
    },
    "VOLUME_UP": {
        "telnet": "vol+",
        "category": "volume",
        "description": "Volume up",
    },
    "VOLUME_DOWN": {
        "telnet": "vol-",
        "category": "volume",
        "description": "Volume down",
    },
    # Special commands
    "ACTIVE": {
        "telnet": "active",
        "category": "source",
        "description": "Set as active source (make TV switch to this input)",
    },
}

# =============================================================================
# Command Categories
# =============================================================================

CEC_CATEGORIES: dict[str, list[str]] = {
    "power": ["POWER_ON", "POWER_OFF"],
    "navigation": ["UP", "DOWN", "LEFT", "RIGHT", "SELECT", "MENU", "BACK"],
    "playback": ["PLAY", "PAUSE", "STOP", "REWIND", "FAST_FORWARD", "PREVIOUS", "NEXT"],
    "volume": ["VOLUME_UP", "VOLUME_DOWN", "MUTE"],
    "source": ["ACTIVE"],
}

# =============================================================================
# Helper Functions
# =============================================================================


def get_command_info(category: str) -> list[dict]:
    """
    Get all commands in a given category.

    :param category: Category name (power, navigation, playback, volume, source)
    :return: List of command info dicts (without the 'index' field — see
        module docstring for why index was removed)
    """
    commands = CEC_CATEGORIES.get(category, [])
    result = []
    for cmd_name in commands:
        if cmd_name in INPUT_CEC_COMMANDS:
            result.append({"name": cmd_name, **INPUT_CEC_COMMANDS[cmd_name]})
        elif cmd_name in OUTPUT_CEC_COMMANDS:
            result.append({"name": cmd_name, **OUTPUT_CEC_COMMANDS[cmd_name]})
    return result


def get_telnet_command(command_name: str, is_output: bool = False) -> str | None:
    """
    Get the Telnet command string for a CEC command.

    :param command_name: CEC command name (e.g. "POWER_ON")
    :param is_output: True for output commands, False for input
    :return: Telnet command string (e.g. "on") or None if unknown
    """
    table = OUTPUT_CEC_COMMANDS if is_output else INPUT_CEC_COMMANDS
    info = table.get(command_name)
    if info is None:
        return None
    return info.get("telnet")


def get_available_commands(is_output: bool = False) -> list[str]:
    """
    Get list of available CEC command names for input or output devices.

    :param is_output: True for output commands, False for input
    :return: Sorted list of command names
    """
    table = OUTPUT_CEC_COMMANDS if is_output else INPUT_CEC_COMMANDS
    return sorted(table.keys())


# Convenience wrappers used by cec_resolver
def get_input_commands() -> list[str]:
    """Get sorted list of input CEC command names."""
    return get_available_commands(is_output=False)


def get_output_commands() -> list[str]:
    """Get sorted list of output CEC command names."""
    return get_available_commands(is_output=True)


def get_commands_by_category(category: str) -> list[str]:
    """Get command names in a given category."""
    return CEC_CATEGORIES.get(category, [])


def is_audio_only_output(scaler_value: int) -> bool:
    """Return True if the scaler value indicates an Audio Only output (value 4)."""
    return scaler_value == 4
