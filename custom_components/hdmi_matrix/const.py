"""Constants for the HDMI Matrix integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "hdmi_matrix"
DEFAULT_NAME = "HDMI Matrix"
MANUFACTURER = "OREI"
DEFAULT_MODEL = "BK-808"
DEFAULT_PORT = 8080

CONF_IP_ADDRESS = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = 15  # seconds
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 300

#: Every hub request gives up after this many seconds, so the event loop is never
#: held up by an unreachable hub.
REQUEST_TIMEOUT = 10

LOGGER = logging.getLogger(__package__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.BUTTON, Platform.SELECT, Platform.SWITCH]

#: The BK-808 has 8 inputs, 8 outputs and 8 preset slots.
PORT_COUNT = 8
PRESET_COUNT = 8

# CEC commands the hub accepts (``POST /api/cec/{input|output}/{n}/{command}``).
# Mirrors the hub's tables in src/device_codes.py (the component ships on its
# own through HACS, so it cannot import them; tests/ha/test_services.py checks
# the two stay equal). Sources use the 19-command input table; displays use the
# device's smaller output table (BE-14).
CEC_INPUT_COMMANDS: tuple[str, ...] = (
    "power_on",
    "power_off",
    "up",
    "left",
    "select",
    "right",
    "menu",
    "down",
    "back",
    "previous",
    "play",
    "next",
    "rewind",
    "pause",
    "fast_forward",
    "stop",
    "mute",
    "volume_down",
    "volume_up",
)
CEC_OUTPUT_COMMANDS: tuple[str, ...] = ("power_on", "power_off", "mute", "volume_down", "volume_up", "active")
CEC_COMMANDS: tuple[str, ...] = (*CEC_INPUT_COMMANDS, *(c for c in CEC_OUTPUT_COMMANDS if c not in CEC_INPUT_COMMANDS))

SERVICE_RECALL_PRESET = "recall_preset"
SERVICE_SWITCH_INPUT = "switch_input"
SERVICE_SEND_CEC_COMMAND = "send_cec_command"

ATTR_CONFIG_ENTRY_ID = "config_entry_id"
ATTR_DEVICE_ID = "device_id"
ATTR_PRESET = "preset"
ATTR_OUTPUT = "output"
ATTR_INPUT = "input"
ATTR_PORT_TYPE = "port_type"
ATTR_PORT_NUM = "port_num"
ATTR_COMMAND = "command"


def scan_interval(seconds: int | None) -> timedelta:
    """Polling interval from the options (default 15 s)."""
    return timedelta(seconds=seconds or DEFAULT_SCAN_INTERVAL)
