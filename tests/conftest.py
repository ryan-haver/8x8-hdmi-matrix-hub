"""
Shared pytest configuration.

Matrix connection settings
    The suite runs **offline against mocks by default** (TST-05). No test talks
    to a real matrix unless it is marked ``@pytest.mark.hardware`` and pytest is
    run with ``-m hardware``. ``pyproject.toml`` sets ``addopts = "-m 'not hardware'"``,
    so hardware tests are deselected by default. Hardware tests get the target from:

        MATRIX_HOST - IP address of the matrix (required; there is no default)
        MATRIX_PORT - port number (default 443)

    Example::

        MATRIX_HOST=192.168.1.50 pytest -m hardware

    Interactive hardware scripts live in ``tools/hil/`` and are not collected.

Test isolation (TST-06)
    ``_isolate_global_state`` (autouse) points ``MATRIX_DATA_DIR`` at a fresh
    temporary directory for every test and resets all REST API module globals
    (matrix device, name caches, managers, rate limiter, WebSocket clients,
    persistence caches) before and after each test, so state cannot leak
    between tests or into the developer's ``data/`` directory.

Home Assistant tests
    ``tests/ha/`` needs ``homeassistant`` (Python 3.13+, see
    ``requirements-test-ha.txt``) and is ignored when it is not installed.

Route inventory
    ``tests/route_inventory.py`` records which REST routes the suite exercises
    and writes ``route-coverage.json`` (see that module for details).
"""

import asyncio
import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

pytest_plugins = ("pytest_asyncio", "tests.route_inventory")

# Home Assistant tests need the real `homeassistant` package (Python 3.13+).
# Skip collecting them entirely when it is not available so the normal suite
# (Python 3.12 venv) is unaffected.
collect_ignore_glob = [] if importlib.util.find_spec("homeassistant") else ["ha/*"]


# =============================================================================
# Matrix Connection Configuration
# =============================================================================

# Real hardware is opt-in: MATRIX_HOST has no default (TST-05).
MATRIX_HOST = os.environ.get("MATRIX_HOST") or None
MATRIX_PORT = int(os.environ.get("MATRIX_PORT", "443"))

# Address used by the mock matrix (RFC 5737 TEST-NET-1, never routable).
MOCK_MATRIX_HOST = "192.0.2.100"


def get_matrix_config() -> dict:
    """Get current matrix configuration."""
    return {
        "host": MATRIX_HOST,
        "port": MATRIX_PORT,
        "use_mock": MATRIX_HOST is None,
    }


# =============================================================================
# Global state isolation (TST-06)
# =============================================================================


def _reset_rest_api_globals() -> None:
    """Reset module-level state of the REST API package and persistence layer.

    Only touches modules that are already imported, so this costs nothing for
    tests that never import the REST API (and works in the HA test environment,
    where ``src/`` dependencies are not installed).
    """
    persistence = sys.modules.get("persistence")
    if persistence is not None:
        persistence.reset_data_dir_cache()

    utils = sys.modules.get("rest_api.utils")
    if utils is not None:
        utils._matrix_device = None
        utils._input_names = {}
        utils._output_names = {}
        utils._config_file = None
        utils._scene_manager = None
        utils._profile_manager = None
        utils._macro_manager = None
        utils._system_shortcut_manager = None
        utils._dashboard_layout_manager = None
        utils._ws_clients.clear()
        utils.reset_rate_limiter()
        utils._rate_limit_last_cleanup = 0.0
        # asyncio locks bind to the first event loop that contends on them;
        # each test gets a new loop, so hand out fresh locks.
        utils._state_lock = asyncio.Lock()
        utils._ws_clients_lock = asyncio.Lock()
        utils._rate_limit_lock = asyncio.Lock()

    control = sys.modules.get("rest_api.control")
    if control is not None:
        control._cycle_locks = {i: asyncio.Lock() for i in control._cycle_locks}

    device_settings = sys.modules.get("rest_api.device_settings")
    if device_settings is not None:
        device_settings._settings_path = None
        device_settings._settings_cache = {}

    themes = sys.modules.get("rest_api.themes")
    if themes is not None:
        themes._theme_path = None

    ui = sys.modules.get("rest_api.ui")
    if ui is not None:
        ui._ui_prefs_path = None

    integrations = sys.modules.get("rest_api.integrations")
    if integrations is not None:
        integrations._registered_buttons = {}
        integrations._loaded = False

    scenes_v2 = sys.modules.get("rest_api.scenes_v2")
    if scenes_v2 is not None:
        scenes_v2._phase8_scene_manager = None


@pytest.fixture(autouse=True)
def _isolate_global_state(tmp_path_factory, monkeypatch):
    """Give every test a private data dir and pristine REST module globals."""
    data_dir = tmp_path_factory.mktemp("matrix-data")
    # monkeypatch restores the original values afterwards, even if a test (or
    # rest_api.create_rest_app(data_dir=...)) overwrote os.environ directly.
    monkeypatch.setenv("MATRIX_DATA_DIR", str(data_dir))
    monkeypatch.delenv("UC_CONFIG_HOME", raising=False)
    _reset_rest_api_globals()
    yield
    _reset_rest_api_globals()


# =============================================================================
# Real Matrix Fixture (hardware tests only)
# =============================================================================


@pytest.fixture
def matrix_config():
    """Provide matrix connection configuration."""
    return get_matrix_config()


@pytest.fixture
async def real_matrix():
    """
    Create a real matrix connection for hardware tests.

    Use only from tests marked ``@pytest.mark.hardware``. Skips unless
    ``MATRIX_HOST`` is set.
    """
    if MATRIX_HOST is None:
        pytest.skip("Hardware test - set MATRIX_HOST (and run with -m hardware)")

    from orei_matrix import OreiMatrix

    matrix = OreiMatrix(MATRIX_HOST, MATRIX_PORT)
    connected = await matrix.connect()

    if not connected:
        pytest.skip(f"Cannot connect to matrix at {MATRIX_HOST}:{MATRIX_PORT}")

    yield matrix

    await matrix.disconnect()


# =============================================================================
# Mock Matrix Fixture (default for unit tests / CI)
# =============================================================================


@pytest.fixture
def mock_matrix():
    """
    Create a mock matrix device for unit tests.

    This is the default for the whole suite; no test needs real hardware
    unless it is marked ``hardware``.
    """
    matrix = MagicMock()
    matrix.connected = True
    matrix.current_scene = 1
    matrix.host = MOCK_MATRIX_HOST
    matrix.port = 443

    # CEC Command registry for mock
    matrix.CEC_COMMAND_MAP = {
        "POWER_ON": 1,
        "POWER_OFF": 2,
        "UP": 3,
        "LEFT": 4,
        "SELECT": 5,
        "RIGHT": 6,
        "MENU": 7,
        "DOWN": 8,
        "BACK": 9,
        "PREVIOUS": 10,
        "PLAY": 11,
        "NEXT": 12,
        "REWIND": 13,
        "PAUSE": 14,
        "FAST_FORWARD": 15,
        "STOP": 16,
        "MUTE": 17,
        "VOLUME_DOWN": 18,
        "VOLUME_UP": 19,
    }

    # Mock async methods
    matrix.connect = AsyncMock(return_value=True)
    matrix.send_cec = AsyncMock(return_value=True)
    matrix.recall_preset = AsyncMock(return_value=True)
    matrix.save_preset = AsyncMock(return_value=True)
    matrix.switch_input = AsyncMock(return_value=True)
    matrix.power_on = AsyncMock(return_value=True)
    matrix.power_off = AsyncMock(return_value=True)
    matrix.get_status = AsyncMock(
        return_value={
            "power": "on",
            "routing": [1, 2, 3, 4, 5, 6, 7, 8],
            "input_names": ["Input 1", "Input 2", "Input 3", "Input 4", "Input 5", "Input 6", "Input 7", "Input 8"],
        }
    )
    matrix.get_video_status = AsyncMock(
        return_value={
            "alloutputname": ["TV 1", "TV 2", "TV 3", "TV 4", "TV 5", "TV 6", "TV 7", "TV 8"],
        }
    )
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
    matrix.get_edid_status = AsyncMock(return_value={"edid": [36, 36, 36, 36, 36, 36, 36, 36]})
    matrix.set_input_edid = AsyncMock(return_value=True)
    matrix.copy_edid_from_output = AsyncMock(return_value=True)

    # Sprint 4 LCD timeout methods
    matrix.set_lcd_timeout = AsyncMock(return_value=True)

    # Sprint 4 ext-audio methods
    matrix.get_ext_audio_status = AsyncMock(
        return_value={
            "mode": 0,
            "allsource": [1, 2, 3, 4, 5, 6, 7, 8],
            "allout": [1, 0, 0, 0, 0, 0, 0, 0],
        }
    )
    matrix.set_ext_audio_mode = AsyncMock(return_value=True)
    matrix.set_ext_audio_enable = AsyncMock(return_value=True)
    matrix.set_ext_audio_source = AsyncMock(return_value=True)

    # Status endpoint methods
    matrix.get_full_status = AsyncMock(
        return_value={
            "power": 1,
            "routing": [1, 2, 3, 4, 5, 6, 7, 8],
        }
    )
    matrix.get_output_status = AsyncMock(
        return_value={
            "allsource": [1, 2, 3, 4, 5, 6, 7, 8],
            "allout": [1, 1, 1, 1, 1, 1, 1, 1],
            "allconnect": [1, 1, 1, 1, 0, 0, 0, 0],
            "allaudiomute": [0, 0, 0, 0, 0, 0, 0, 0],
            "allhdcp": [3, 3, 3, 3, 3, 3, 3, 3],
            "allhdr": [3, 3, 3, 3, 3, 3, 3, 3],
            "allscaler": [0, 0, 0, 0, 0, 0, 0, 0],
            "allarc": [0, 0, 0, 0, 0, 0, 0, 0],
        }
    )
    matrix.get_input_status = AsyncMock(
        return_value={
            "inactive": [1, 1, 1, 1, 0, 0, 0, 0],
            "edid": [36, 36, 36, 36, 36, 36, 36, 36],
        }
    )
    matrix.get_all_cable_status = AsyncMock(
        return_value={
            "inputs": {1: True, 2: True, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False},
            "outputs": {1: True, 2: True, 3: True, 4: True, 5: False, 6: False, 7: False, 8: False},
        }
    )
    matrix.get_system_status = AsyncMock(
        return_value={
            "power": 1,
            "beep": 1,
            "lock": 0,
            "mode": 0,
            "baudrate": 115200,
        }
    )
    matrix.get_device_info = AsyncMock(
        return_value={
            "model": "BK-808",
            "version": "1.0.0",
            "webversion": "1.0.0",
            "hostname": "matrix",
            "macaddress": "00:11:22:33:44:55",
        }
    )
    matrix.get_network_info = AsyncMock(
        return_value={
            "ipaddress": MOCK_MATRIX_HOST,
            "subnet": "255.255.255.0",
            "gateway": "192.168.0.1",
            "dhcp": 0,
            "telnetport": 23,
            "tcpport": 8000,
        }
    )
    matrix.get_output_names = AsyncMock(
        return_value={
            1: "TV 1",
            2: "TV 2",
            3: "TV 3",
            4: "TV 4",
            5: "TV 5",
            6: "TV 6",
            7: "TV 7",
            8: "TV 8",
        }
    )
    matrix.get_input_names = AsyncMock(
        return_value={
            1: "Input 1",
            2: "Input 2",
            3: "Input 3",
            4: "Input 4",
            5: "Input 5",
            6: "Input 6",
            7: "Input 7",
            8: "Input 8",
        }
    )
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
    matrix.get_cec_enabled = AsyncMock(
        return_value={
            "inputs": {1: True, 2: True, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False},
            "outputs": {1: True, 2: True, 3: True, 4: True, 5: False, 6: False, 7: False, 8: False},
        }
    )
    matrix.get_all_capabilities = AsyncMock(
        return_value={
            "inputs": [{"input_num": i, "signal_detected": i <= 4, "cec_enabled": i <= 2} for i in range(1, 9)],
            "outputs": [
                {"output_num": i, "connected": i <= 4, "arc_enabled": i == 1, "is_audio_only": False}
                for i in range(1, 9)
            ],
        }
    )
    matrix.get_input_capabilities = AsyncMock(
        return_value={
            "input_num": 1,
            "signal_detected": True,
            "cec_enabled": True,
            "commands": ["power_on", "power_off", "up", "down", "left", "right", "select"],
        }
    )
    matrix.get_output_capabilities = AsyncMock(
        return_value={
            "output_num": 1,
            "connected": True,
            "arc_enabled": True,
            "is_audio_only": False,
            "commands": ["power_on", "power_off", "volume_up", "volume_down", "mute"],
        }
    )

    return matrix


# Markers (`hardware`, `mock`) are registered in pyproject.toml [tool.pytest.ini_options].
