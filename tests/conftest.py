"""
Test configuration for pytest.

Matrix Connection Settings:
    Default: Uses real matrix at 192.168.0.100:443
    Override via environment variables:
        MATRIX_HOST - IP address of the matrix
        MATRIX_PORT - Port number (default 443)
        USE_MOCK_MATRIX - Set to "1" to use mock instead of real device

Examples:
    # Use real device (default)
    pytest tests/

    # Use different matrix IP
    MATRIX_HOST=192.168.1.50 pytest tests/

    # Use mock for CI/offline testing
    USE_MOCK_MATRIX=1 pytest tests/
"""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Configure pytest-asyncio to use auto mode
pytest_plugins = ('pytest_asyncio',)


# =============================================================================
# Matrix Connection Configuration
# =============================================================================

# Default to real device - configure once, use everywhere
MATRIX_HOST = os.environ.get("MATRIX_HOST", "192.168.0.100")
MATRIX_PORT = int(os.environ.get("MATRIX_PORT", "443"))
USE_MOCK = os.environ.get("USE_MOCK_MATRIX", "0") == "1"


def get_matrix_config() -> dict:
    """Get current matrix configuration."""
    return {
        "host": MATRIX_HOST,
        "port": MATRIX_PORT,
        "use_mock": USE_MOCK,
    }


# =============================================================================
# Real Matrix Fixture
# =============================================================================

@pytest.fixture
def matrix_config():
    """Provide matrix connection configuration."""
    return get_matrix_config()


@pytest.fixture
async def real_matrix():
    """
    Create a real matrix connection for integration tests.
    
    Skips if USE_MOCK_MATRIX=1 is set.
    """
    if USE_MOCK:
        pytest.skip("USE_MOCK_MATRIX=1 - skipping real device test")
    
    from orei_matrix import OreiMatrix
    
    matrix = OreiMatrix(MATRIX_HOST, MATRIX_PORT)
    connected = await matrix.connect()
    
    if not connected:
        pytest.skip(f"Cannot connect to matrix at {MATRIX_HOST}:{MATRIX_PORT}")
    
    yield matrix
    
    # Cleanup - close connection if needed
    if hasattr(matrix, 'close'):
        await matrix.close()


# =============================================================================
# Mock Matrix Fixture (opt-in for unit tests / CI)
# =============================================================================

@pytest.fixture
def mock_matrix():
    """
    Create a mock matrix device for unit tests.
    
    Use this when you need to test without real hardware, 
    or to test error conditions that are hard to trigger on real device.
    """
    matrix = MagicMock()
    matrix.connected = True
    matrix.current_scene = 1
    matrix.host = MATRIX_HOST  # Use configured host for consistency
    matrix.port = MATRIX_PORT
    
    # Mock async methods
    matrix.connect = AsyncMock(return_value=True)
    matrix.recall_preset = AsyncMock(return_value=True)
    matrix.save_preset = AsyncMock(return_value=True)
    matrix.switch_input = AsyncMock(return_value=True)
    matrix.power_on = AsyncMock(return_value=True)
    matrix.power_off = AsyncMock(return_value=True)
    matrix.get_status = AsyncMock(return_value={
        "power": "on",
        "routing": [1, 2, 3, 4, 5, 6, 7, 8],
        "input_names": ["Input 1", "Input 2", "Input 3", "Input 4", 
                       "Input 5", "Input 6", "Input 7", "Input 8"],
    })
    matrix.get_video_status = AsyncMock(return_value={
        "alloutputname": ["TV 1", "TV 2", "TV 3", "TV 4", 
                         "TV 5", "TV 6", "TV 7", "TV 8"],
    })
    matrix.get_current_input_for_output = AsyncMock(return_value=1)
    
    # Sprint 2 methods
    matrix.set_output_enable = AsyncMock(return_value=True)
    matrix.set_output_hdcp = AsyncMock(return_value=True)
    matrix.set_output_hdr = AsyncMock(return_value=True)
    matrix.set_output_scaler = AsyncMock(return_value=True)
    matrix.set_output_arc = AsyncMock(return_value=True)
    matrix.set_output_audio_mute = AsyncMock(return_value=True)
    matrix.set_cec_enable = AsyncMock(return_value=True)
    matrix.system_reboot = AsyncMock(return_value=True)
    
    # Sprint 4 EDID methods
    matrix.get_edid_status = AsyncMock(return_value={
        "edid": [36, 36, 36, 36, 36, 36, 36, 36]
    })
    matrix.set_input_edid = AsyncMock(return_value=True)
    matrix.copy_edid_from_output = AsyncMock(return_value=True)
    
    # Sprint 4 LCD timeout methods
    matrix.set_lcd_timeout = AsyncMock(return_value=True)
    
    # Sprint 4 ext-audio methods
    matrix.get_ext_audio_status = AsyncMock(return_value={
        "mode": 0,
        "allsource": [1, 2, 3, 4, 5, 6, 7, 8],
        "allout": [1, 0, 0, 0, 0, 0, 0, 0],
    })
    matrix.set_ext_audio_mode = AsyncMock(return_value=True)
    matrix.set_ext_audio_enable = AsyncMock(return_value=True)
    matrix.set_ext_audio_source = AsyncMock(return_value=True)
    
    # Status endpoint methods
    matrix.get_full_status = AsyncMock(return_value={
        "power": 1,
        "routing": [1, 2, 3, 4, 5, 6, 7, 8],
    })
    matrix.get_output_status = AsyncMock(return_value={
        "allsource": [1, 2, 3, 4, 5, 6, 7, 8],
        "allout": [1, 1, 1, 1, 1, 1, 1, 1],
        "allconnect": [1, 1, 1, 1, 0, 0, 0, 0],
        "allaudiomute": [0, 0, 0, 0, 0, 0, 0, 0],
        "allhdcp": [3, 3, 3, 3, 3, 3, 3, 3],
        "allhdr": [3, 3, 3, 3, 3, 3, 3, 3],
        "allscaler": [0, 0, 0, 0, 0, 0, 0, 0],
        "allarc": [0, 0, 0, 0, 0, 0, 0, 0],
    })
    matrix.get_input_status = AsyncMock(return_value={
        "inactive": [1, 1, 1, 1, 0, 0, 0, 0],
        "edid": [36, 36, 36, 36, 36, 36, 36, 36],
    })
    matrix.get_all_cable_status = AsyncMock(return_value={
        "inputs": {1: True, 2: True, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False},
        "outputs": {1: True, 2: True, 3: True, 4: True, 5: False, 6: False, 7: False, 8: False},
    })
    matrix.get_system_status = AsyncMock(return_value={
        "power": 1,
        "beep": 1,
        "lock": 0,
        "mode": 0,
        "baudrate": 115200,
    })
    matrix.get_device_info = AsyncMock(return_value={
        "model": "BK-808",
        "version": "1.0.0",
        "webversion": "1.0.0",
        "hostname": "matrix",
        "macaddress": "00:11:22:33:44:55",
    })
    matrix.get_network_info = AsyncMock(return_value={
        "ipaddress": MATRIX_HOST,
        "subnet": "255.255.255.0",
        "gateway": "192.168.0.1",
        "dhcp": 0,
        "telnetport": 23,
        "tcpport": 8000,
    })
    matrix.get_output_names = AsyncMock(return_value={
        1: "TV 1", 2: "TV 2", 3: "TV 3", 4: "TV 4",
        5: "TV 5", 6: "TV 6", 7: "TV 7", 8: "TV 8",
    })
    matrix.get_input_names = AsyncMock(return_value={
        1: "Input 1", 2: "Input 2", 3: "Input 3", 4: "Input 4",
        5: "Input 5", 6: "Input 6", 7: "Input 7", 8: "Input 8",
    })
    matrix.telnet_connected = True
    
    # System settings methods
    matrix.set_beep = AsyncMock(return_value=True)
    matrix.set_panel_lock = AsyncMock(return_value=True)
    
    # CEC command methods (for REST API CEC_INPUT_COMMANDS and CEC_OUTPUT_COMMANDS)
    # Input CEC commands
    matrix.cec_input_power_on = AsyncMock(return_value=True)
    matrix.cec_input_power_off = AsyncMock(return_value=True)
    matrix.cec_input_up = AsyncMock(return_value=True)
    matrix.cec_input_down = AsyncMock(return_value=True)
    matrix.cec_input_left = AsyncMock(return_value=True)
    matrix.cec_input_right = AsyncMock(return_value=True)
    matrix.cec_input_select = AsyncMock(return_value=True)
    matrix.cec_input_menu = AsyncMock(return_value=True)
    matrix.cec_input_back = AsyncMock(return_value=True)
    matrix.cec_input_play = AsyncMock(return_value=True)
    matrix.cec_input_pause = AsyncMock(return_value=True)
    matrix.cec_input_stop = AsyncMock(return_value=True)
    matrix.cec_input_previous = AsyncMock(return_value=True)
    matrix.cec_input_next = AsyncMock(return_value=True)
    matrix.cec_input_rewind = AsyncMock(return_value=True)
    matrix.cec_input_fast_forward = AsyncMock(return_value=True)
    matrix.cec_input_volume_up = AsyncMock(return_value=True)
    matrix.cec_input_volume_down = AsyncMock(return_value=True)
    matrix.cec_input_mute = AsyncMock(return_value=True)
    
    # Output CEC commands
    matrix.cec_output_power_on = AsyncMock(return_value=True)
    matrix.cec_output_power_off = AsyncMock(return_value=True)
    matrix.cec_output_up = AsyncMock(return_value=True)
    matrix.cec_output_down = AsyncMock(return_value=True)
    matrix.cec_output_left = AsyncMock(return_value=True)
    matrix.cec_output_right = AsyncMock(return_value=True)
    matrix.cec_output_select = AsyncMock(return_value=True)
    matrix.cec_output_menu = AsyncMock(return_value=True)
    matrix.cec_output_back = AsyncMock(return_value=True)
    matrix.cec_output_volume_up = AsyncMock(return_value=True)
    matrix.cec_output_volume_down = AsyncMock(return_value=True)
    matrix.cec_output_mute = AsyncMock(return_value=True)
    
    # CEC capabilities methods
    matrix.get_cec_enabled = AsyncMock(return_value={
        "inputs": {1: True, 2: True, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False},
        "outputs": {1: True, 2: True, 3: True, 4: True, 5: False, 6: False, 7: False, 8: False},
    })
    matrix.get_all_capabilities = AsyncMock(return_value={
        "inputs": [
            {"input_num": i, "signal_detected": i <= 4, "cec_enabled": i <= 2}
            for i in range(1, 9)
        ],
        "outputs": [
            {"output_num": i, "connected": i <= 4, "arc_enabled": i == 1, "is_audio_only": False}
            for i in range(1, 9)
        ],
    })
    matrix.get_input_capabilities = AsyncMock(return_value={
        "input_num": 1,
        "signal_detected": True,
        "cec_enabled": True,
        "commands": ["power_on", "power_off", "up", "down", "left", "right", "select"],
    })
    matrix.get_output_capabilities = AsyncMock(return_value={
        "output_num": 1,
        "connected": True,
        "arc_enabled": True,
        "is_audio_only": False,
        "commands": ["power_on", "power_off", "volume_up", "volume_down", "mute"],
    })
    
    return matrix


# =============================================================================
# Pytest Markers
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "mock: mark test as using mock matrix (can run offline)"
    )
    config.addinivalue_line(
        "markers", "hardware: mark test as requiring real hardware"
    )
