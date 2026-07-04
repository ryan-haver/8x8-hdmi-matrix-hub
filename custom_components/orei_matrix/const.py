"""Constants for the OREI HDMI Matrix integration."""
import logging

DOMAIN = "orei_matrix"
DEFAULT_NAME = "OREI HDMI Matrix"
DEFAULT_PORT = 8080

CONF_IP_ADDRESS = "host"
CONF_PORT = "port"

LOGGER = logging.getLogger(__package__)

PLATFORMS = ["select", "switch", "button", "binary_sensor"]
