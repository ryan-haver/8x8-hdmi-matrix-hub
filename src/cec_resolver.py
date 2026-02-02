"""
CEC Configuration Resolver for Profile-based CEC Control.

This module handles auto-resolution of CEC command routing based on:
- Profile routing configuration (which inputs → which outputs)
- Output device capabilities (audio_only, arc_enabled)
- Smart defaults with manual override support
"""

import logging
from typing import Dict, List, Set, Optional, Any

# Support both package and direct imports
try:
    from .cec_commands import (
        get_input_commands,
        get_output_commands,
        get_commands_by_category,
        is_audio_only_output,
        ScalerMode,
    )
except ImportError:
    from cec_commands import (
        get_input_commands,
        get_output_commands,
        get_commands_by_category,
        is_audio_only_output,
        ScalerMode,
    )

_LOG = logging.getLogger(__name__)

# =============================================================================
# CEC Config Schema
# =============================================================================

DEFAULT_CEC_CONFIG = {
    "auto_resolved": True,
    "nav_targets": [],          # D-pad, menu, back → input devices
    "playback_targets": [],     # Play, pause, stop → input devices
    "volume_targets": [],       # Volume, mute → output devices (audio)
    "power_on_targets": [],     # Power on → inputs + outputs
    "power_off_targets": [],    # Power off → usually just outputs
    "device_overrides": {},     # Per-device overrides
}


def create_empty_cec_config() -> Dict:
    """Create an empty CEC config with default structure."""
    return DEFAULT_CEC_CONFIG.copy()


# =============================================================================
# Auto-Resolution Logic
# =============================================================================

async def resolve_profile_cec_config(
    profile: Dict,
    output_status: Dict,
    cec_status: Dict,
    input_status: Optional[Dict] = None,
) -> Dict:
    """
    Auto-generate CEC config for a profile based on device capabilities.
    
    :param profile: Profile dict with routing configuration
    :param output_status: Matrix output status (from get_output_status)
    :param cec_status: Matrix CEC status (from get_cec_status)
    :param input_status: Optional input status for signal detection
    :return: Resolved CEC config dict
    """
    routing = profile.get("routing", {})
    
    if not routing:
        _LOG.debug("Profile has no routing, returning empty CEC config")
        return create_empty_cec_config()
    
    # Extract devices in this profile
    inputs_in_profile = set()
    outputs_in_profile = set()
    
    for input_num, outputs in routing.items():
        # Handle both string and int keys
        input_num = int(input_num) if isinstance(input_num, str) else input_num
        inputs_in_profile.add(input_num)
        
        if isinstance(outputs, list):
            outputs_in_profile.update(outputs)
        else:
            outputs_in_profile.add(outputs)
    
    _LOG.debug(f"Profile devices - Inputs: {inputs_in_profile}, Outputs: {outputs_in_profile}")
    
    # Resolve primary input for navigation/playback
    primary_input = min(inputs_in_profile) if inputs_in_profile else None
    
    # Resolve volume targets
    volume_targets = resolve_volume_targets(outputs_in_profile, output_status)
    
    # Resolve power targets
    power_on_targets, power_off_targets = resolve_power_targets(
        inputs_in_profile, outputs_in_profile
    )
    
    config = {
        "auto_resolved": True,
        "nav_targets": [f"input_{primary_input}"] if primary_input else [],
        "playback_targets": [f"input_{primary_input}"] if primary_input else [],
        "volume_targets": volume_targets,
        "power_on_targets": power_on_targets,
        "power_off_targets": power_off_targets,
        "device_overrides": {},
    }
    
    _LOG.info(f"Resolved CEC config: nav→{config['nav_targets']}, "
              f"vol→{config['volume_targets']}")
    
    return config


def resolve_volume_targets(
    outputs: Set[int],
    output_status: Dict,
) -> List[str]:
    """
    Resolve which outputs should receive volume CEC commands.
    
    Priority:
    1. Outputs with scaler = Audio Only (mode 4)
    2. Outputs with ARC enabled
    3. First output in the set
    
    :param outputs: Set of output numbers in the profile
    :param output_status: Matrix output status dict
    :return: List of target strings (e.g., ["output_2"])
    """
    if not outputs:
        return []
    
    allscaler = output_status.get("allscaler", [])
    allarc = output_status.get("allarc", [])
    allconnect = output_status.get("allconnect", [])
    
    # Only consider connected outputs
    connected_outputs = [
        o for o in outputs 
        if o <= len(allconnect) and allconnect[o - 1] == 1
    ]
    
    if not connected_outputs:
        # Fall back to all outputs if none connected (might be detection issue)
        connected_outputs = list(outputs)
    
    # Priority 1: Audio Only outputs
    audio_only_outputs = [
        o for o in connected_outputs
        if o <= len(allscaler) and is_audio_only_output(allscaler[o - 1])
    ]
    if audio_only_outputs:
        _LOG.debug(f"Volume targets: Audio Only outputs {audio_only_outputs}")
        return [f"output_{o}" for o in sorted(audio_only_outputs)]
    
    # Priority 2: ARC-enabled outputs
    arc_outputs = [
        o for o in connected_outputs
        if o <= len(allarc) and allarc[o - 1] == 1
    ]
    if arc_outputs:
        _LOG.debug(f"Volume targets: ARC outputs {arc_outputs}")
        return [f"output_{o}" for o in sorted(arc_outputs)]
    
    # Priority 3: First connected output
    first_output = min(connected_outputs)
    _LOG.debug(f"Volume targets: Default to first output {first_output}")
    return [f"output_{first_output}"]


def resolve_power_targets(
    inputs: Set[int],
    outputs: Set[int],
) -> tuple[List[str], List[str]]:
    """
    Resolve which devices should receive power on/off commands.
    
    Power On: All inputs and outputs in profile
    Power Off: Usually just outputs (users often want sources to stay on)
    
    :param inputs: Set of input numbers
    :param outputs: Set of output numbers
    :return: Tuple of (power_on_targets, power_off_targets)
    """
    power_on = []
    power_off = []
    
    # Add all inputs to power on
    for i in sorted(inputs):
        power_on.append(f"input_{i}")
    
    # Add all outputs to both power on and off
    for o in sorted(outputs):
        power_on.append(f"output_{o}")
        power_off.append(f"output_{o}")
    
    return power_on, power_off


# =============================================================================
# CEC Config Utilities
# =============================================================================

def get_targets_for_category(cec_config: Dict, category: str) -> List[str]:
    """
    Get target devices for a CEC command category.
    
    :param cec_config: Profile CEC config
    :param category: Command category (navigation, playback, volume, power)
    :return: List of target device strings
    """
    category_map = {
        "navigation": "nav_targets",
        "playback": "playback_targets",
        "volume": "volume_targets",
        "power": "power_on_targets",  # Default to power_on
        "power_on": "power_on_targets",
        "power_off": "power_off_targets",
    }
    
    key = category_map.get(category, "nav_targets")
    return cec_config.get(key, [])


def parse_target(target: str) -> tuple[str, int]:
    """
    Parse a target string into device type and number.
    
    :param target: Target string (e.g., "input_5" or "output_2")
    :return: Tuple of (device_type, device_number)
    """
    parts = target.split("_")
    if len(parts) == 2:
        device_type = parts[0]  # "input" or "output"
        device_num = int(parts[1])
        return device_type, device_num
    raise ValueError(f"Invalid target format: {target}")


def is_command_supported(command: str, target: str) -> bool:
    """
    Check if a command is supported by the target device type.
    
    :param command: Command name (e.g., "UP", "VOLUME_UP")
    :param target: Target device string (e.g., "input_5", "output_2")
    :return: True if command is supported
    """
    device_type, _ = parse_target(target)
    
    if device_type == "input":
        return command in get_input_commands()
    elif device_type == "output":
        return command in get_output_commands()
    
    return False


def get_supported_commands_for_target(target: str) -> List[str]:
    """
    Get list of supported commands for a target device.
    
    :param target: Target device string (e.g., "input_5", "output_2")
    :return: List of supported command names
    """
    device_type, _ = parse_target(target)
    
    if device_type == "input":
        return get_input_commands()
    elif device_type == "output":
        return get_output_commands()
    
    return []


# =============================================================================
# Capability Detection
# =============================================================================

def get_output_capabilities(
    output_num: int,
    output_status: Dict,
    cec_status: Dict,
) -> Dict:
    """
    Get capabilities for a specific output device.
    
    :param output_num: Output number (1-8)
    :param output_status: Matrix output status dict
    :param cec_status: Matrix CEC status dict
    :return: Capabilities dict
    """
    idx = output_num - 1  # Convert to 0-indexed
    
    allscaler = output_status.get("allscaler", [])
    allarc = output_status.get("allarc", [])
    allconnect = output_status.get("allconnect", [])
    allout = output_status.get("allout", [])
    alloutputname = output_status.get("alloutputname", [])
    
    cec_outputindex = cec_status.get("outputindex", [])
    
    scaler_value = allscaler[idx] if idx < len(allscaler) else 0
    
    return {
        "output_num": output_num,
        "name": alloutputname[idx] if idx < len(alloutputname) else f"Output {output_num}",
        "connected": allconnect[idx] == 1 if idx < len(allconnect) else False,
        "stream_enabled": allout[idx] == 1 if idx < len(allout) else True,
        "is_audio_only": is_audio_only_output(scaler_value),
        "arc_enabled": allarc[idx] == 1 if idx < len(allarc) else False,
        "cec_enabled": cec_outputindex[idx] == 1 if idx < len(cec_outputindex) else False,
        "scaler_mode": scaler_value,
        "supported_cec_commands": get_output_commands(),
    }


def get_input_capabilities(
    input_num: int,
    input_status: Dict,
    cec_status: Dict,
) -> Dict:
    """
    Get capabilities for a specific input device.
    
    :param input_num: Input number (1-8)
    :param input_status: Matrix input status dict
    :param cec_status: Matrix CEC status dict
    :return: Capabilities dict
    """
    idx = input_num - 1  # Convert to 0-indexed
    
    inname = input_status.get("inname", [])
    inactive = input_status.get("inactive", [])
    
    cec_inputindex = cec_status.get("inputindex", [])
    
    return {
        "input_num": input_num,
        "name": inname[idx] if idx < len(inname) else f"Input {input_num}",
        "signal_detected": inactive[idx] == 1 if idx < len(inactive) else False,
        "cec_enabled": cec_inputindex[idx] == 1 if idx < len(cec_inputindex) else False,
        "supported_cec_commands": get_input_commands(),
    }


def get_all_capabilities(
    input_status: Dict,
    output_status: Dict,
    cec_status: Dict,
) -> Dict:
    """
    Get capabilities for all input and output devices.
    
    :return: Dict with 'inputs' and 'outputs' lists
    """
    inputs = []
    outputs = []
    
    for i in range(1, 9):
        inputs.append(get_input_capabilities(i, input_status, cec_status))
        outputs.append(get_output_capabilities(i, output_status, cec_status))
    
    return {
        "inputs": inputs,
        "outputs": outputs,
    }


def resolve_scene_cec_config(
    active_inputs: List[int],
    active_outputs: List[int],
    status: Dict,
) -> Dict:
    """
    Synchronous CEC config resolver for scene-based profiles.
    
    This is a simpler version for use with scenes that doesn't require
    async status fetching.
    
    :param active_inputs: List of input numbers used in the scene
    :param active_outputs: List of output numbers used in the scene
    :param status: Matrix status dict with allscaler, allarc, allconnect arrays
    :return: CEC config dict
    """
    if not active_inputs and not active_outputs:
        return create_empty_cec_config()
    
    # Resolve primary input for navigation/playback (first active input)
    primary_input = min(active_inputs) if active_inputs else None
    
    # Build volume targets from outputs
    volume_targets = resolve_volume_targets(set(active_outputs), status)
    
    # Build nav/playback targets from primary input
    nav_targets = [f"input_{primary_input}"] if primary_input else []
    playback_targets = [f"input_{primary_input}"] if primary_input else []
    
    # Build power targets
    power_on_targets, power_off_targets = resolve_power_targets(
        set(active_inputs), set(active_outputs)
    )
    
    config = {
        "auto_resolved": True,
        "nav_targets": nav_targets,
        "playback_targets": playback_targets,
        "volume_targets": volume_targets,
        "power_on_targets": power_on_targets,
        "power_off_targets": power_off_targets,
    }
    
    _LOG.info(f"Resolved scene CEC config: nav→{nav_targets}, vol→{volume_targets}")
    return config


# Alias for backward compatibility with REST API
resolve_profile_cec_config_sync = resolve_scene_cec_config
