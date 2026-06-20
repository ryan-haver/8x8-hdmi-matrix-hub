"""
Unfolded Circle Integration Module.

This module provides the UC Remote driver functionality by consuming
the REST API rather than directly communicating with the hardware.
"""

from .adapter import MatrixApiAdapter
from .api_client import MatrixApiClient
from .entities import (
    CEC_INPUT_COMMANDS,
    CEC_OUTPUT_COMMANDS,
    EntityContext,
    create_input_cec_remote_with_context,
    create_output_cec_remote_with_context,
    create_preset_button_with_context,
)

__all__ = [
    "MatrixApiClient",
    "MatrixApiAdapter",
    "EntityContext",
    "create_preset_button_with_context",
    "create_input_cec_remote_with_context",
    "create_output_cec_remote_with_context",
    "CEC_INPUT_COMMANDS",
    "CEC_OUTPUT_COMMANDS",
]
