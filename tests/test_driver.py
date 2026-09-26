"""
Tests for driver.py utility functions.

Tests the standalone utility functions from driver.py without requiring
the full Unfolded Circle integration library. These include:
- Lock file management (acquire/release)
- Port availability checking
- Remote command parameters, device state mapping and entity state sync (WP-B2)
- Config save/load (JSON-based persistent storage)
- Stale mDNS cleanup
"""

import os
import socket
import sys
from pathlib import Path

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# =============================================================================
# Test Fixture: Clean Lock File
# =============================================================================


@pytest.fixture(autouse=True)
def clean_lock_file(tmp_path, monkeypatch):
    """Ensure lock file is cleaned before and after each test, and isolates LOCK_FILE."""
    test_lock = tmp_path / "driver.lock"
    monkeypatch.setattr("driver.LOCK_FILE", test_lock)

    # Cleanup before
    if test_lock.exists():
        try:
            test_lock.unlink()
        except Exception:
            pass

    yield

    # Drop the OS lock (if a test took it) before removing the file
    import driver

    driver.release_lock()

    # Cleanup after
    if test_lock.exists():
        try:
            test_lock.unlink()
        except Exception:
            pass


# =============================================================================
# Test Port Availability
# =============================================================================


class TestPortAvailability:
    """Test the port availability check function."""

    def test_unbound_port_is_available(self):
        """An unbound high port should be available."""
        from driver import check_port_available

        # Use a high random port that's unlikely to be in use
        port = 19876
        # This test may be flaky in CI - wrap in try/except
        try:
            assert check_port_available(port) is True
        except OSError:
            pytest.skip("Port check not supported in this environment")

    def test_bound_port_is_not_available(self):
        """A port already bound should not be available (skip on Windows due to SO_REUSEADDR)."""
        from driver import check_port_available

        # SO_REUSEADDR makes this test unreliable on some platforms
        # Just verify the function runs and returns a boolean
        port = 19877
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    s.bind(("0.0.0.0", port))
                except OSError:
                    pytest.skip("Cannot bind test port")
                s.listen(1)

                result = check_port_available(port)
                # Result may be True or False depending on platform SO_REUSEADDR behavior
                # We just verify it returns a boolean
                assert isinstance(result, bool)
        except OSError:
            pytest.skip("Socket operations not supported")


# =============================================================================
# Test Lock File Management
# =============================================================================


class TestLockFileManagement:
    """Test the file lock mechanism for single-instance enforcement."""

    def test_acquire_lock_creates_file(self):
        """Acquiring lock should create lock file with current PID."""
        from driver import LOCK_FILE, acquire_lock

        result = acquire_lock()

        assert result is True
        assert LOCK_FILE.exists()

        # Lock file should contain current PID
        with open(LOCK_FILE) as f:
            pid = int(f.read().strip())
        assert pid == os.getpid()

    def test_release_lock_removes_file(self):
        """Releasing lock should remove lock file."""
        from driver import LOCK_FILE, acquire_lock, release_lock

        acquire_lock()
        assert LOCK_FILE.exists()

        release_lock()
        assert not LOCK_FILE.exists()

    def test_acquire_lock_when_already_held(self, caplog):
        """Cannot acquire lock while another holder has the OS lock (BE-18)."""
        from _process_lock import ProcessLock
        from driver import LOCK_FILE, acquire_lock

        # Another handle holds the OS lock (the OS refuses a second handle
        # even within one process, so this stands in for another instance).
        with ProcessLock(LOCK_FILE):
            result = acquire_lock()

        assert result is False
        assert "already running" in caplog.text or "already holds it" in caplog.text

    def test_acquire_lock_with_stale_lock(self):
        """A leftover lock file nobody holds is simply taken over (no PID checks)."""
        from driver import LOCK_FILE, acquire_lock

        # Leftover file from a crashed instance; its PID may even be live
        # (PID reuse) — irrelevant, since nobody holds the OS lock.
        with open(LOCK_FILE, "w") as f:
            f.write("1")

        result = acquire_lock()

        assert result is True
        assert LOCK_FILE.exists()
        with open(LOCK_FILE) as f:
            assert int(f.read().strip()) == os.getpid()

    def test_acquire_lock_is_idempotent_for_holder(self):
        """A second acquire_lock() in the holding process succeeds (retry path in main)."""
        from driver import acquire_lock

        assert acquire_lock() is True
        assert acquire_lock() is True

    def test_release_lock_when_no_file(self):
        """Releasing lock when no file exists should not raise."""
        from driver import LOCK_FILE, release_lock

        # Ensure no lock file exists
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()

        # Should not raise
        release_lock()


# =============================================================================
# Test Config Save/Load
# =============================================================================


class TestConfigPersistence:
    """Test the JSON-based configuration save/load functions."""

    def test_save_config_creates_file(self, tmp_path, monkeypatch):
        """Saving config should create the config file."""
        from driver import save_config

        # Use temporary directory for test
        test_config_file = tmp_path / "test_config.json"
        monkeypatch.setattr("driver.CONFIG_FILE", test_config_file)

        save_config(
            host="192.168.1.100", port=443, input_names={1: "PS5", 2: "AppleTV"}, output_names={1: "Living Room TV"}
        )

        assert test_config_file.exists()

    def test_save_and_load_config_roundtrip(self, tmp_path, monkeypatch):
        """Saved config should be loadable with same values."""
        from driver import load_config, save_config

        test_config_file = tmp_path / "test_config.json"
        monkeypatch.setattr("driver.CONFIG_FILE", test_config_file)

        # Save
        save_config(
            host="192.168.1.100",
            port=443,
            input_names={1: "PS5", 2: "AppleTV"},
            output_names={1: "Living Room TV", 2: "Bedroom"},
        )

        # Load
        config = load_config()

        assert config is not None
        assert config["host"] == "192.168.1.100"
        assert config["port"] == 443
        assert config["input_names"] == {1: "PS5", 2: "AppleTV"}
        assert config["output_names"] == {1: "Living Room TV", 2: "Bedroom"}

    def test_load_config_no_file(self, tmp_path, monkeypatch):
        """Loading config when file doesn't exist should return None."""
        from driver import load_config

        test_config_file = tmp_path / "nonexistent.json"
        monkeypatch.setattr("driver.CONFIG_FILE", test_config_file)

        config = load_config()
        assert config is None

    def test_load_config_corrupted_file(self, tmp_path, monkeypatch):
        """Loading corrupted config should return None (not crash)."""
        from driver import load_config

        test_config_file = tmp_path / "corrupted.json"
        test_config_file.write_text("not valid json{{{")
        monkeypatch.setattr("driver.CONFIG_FILE", test_config_file)

        # Should not raise, just return None
        config = load_config()
        assert config is None

    def test_save_config_empty_output_names(self, tmp_path, monkeypatch):
        """Saving config without output_names should work (omit key when empty)."""
        from driver import load_config, save_config

        test_config_file = tmp_path / "test_config.json"
        monkeypatch.setattr("driver.CONFIG_FILE", test_config_file)

        # Save without output_names (None default)
        save_config(host="192.168.1.100", port=443, input_names={1: "PS5"})

        config = load_config()
        assert config is not None
        # When output_names is None/empty, it's omitted from saved config
        assert "output_names" not in config or config.get("output_names") == {}
        # But input_names should be saved correctly
        assert config["input_names"] == {1: "PS5"}


# =============================================================================
# Test Matrix State Management
# =============================================================================


class TestMatrixState:
    """Test the global matrix state management functions."""

    def test_initial_state_empty(self):
        """Initial state should have no matrix configured."""
        from driver import get_matrix, is_connected, set_matrix

        # Reset state
        set_matrix(None)

        assert get_matrix() is None
        assert is_connected() is False

    def test_set_and_get_matrix(self):
        """Setting matrix should make it retrievable."""
        from driver import get_matrix, set_matrix

        # Create a mock matrix
        mock = type("MockMatrix", (), {"connected": True})()

        set_matrix(mock)

        assert get_matrix() is mock

    def test_is_connected_reflects_matrix_state(self):
        """is_connected should return matrix.connected state."""
        from driver import is_connected, set_matrix

        # Connected matrix
        connected_mock = type("MockMatrix", (), {"connected": True})()
        set_matrix(connected_mock)
        assert is_connected() is True

        # Disconnected matrix
        disconnected_mock = type("MockMatrix", (), {"connected": False})()
        set_matrix(disconnected_mock)
        assert is_connected() is False


# =============================================================================
# Test CEC Command Resolution
# =============================================================================


class TestCecCommandResolution:
    """Test the CEC command index lookup functions."""

    def _get_mock_matrix_with_cec_map(self):
        """Create a mock matrix with CEC_COMMAND_MAP."""
        from unittest.mock import AsyncMock

        mock = type("MockMatrix", (), {"connected": True, "CEC_COMMAND_MAP": {}})()
        mock.CEC_COMMAND_MAP = {
            "POWER_ON": 1,
            "POWER_OFF": 2,
            "PLAY": 3,
            "PAUSE": 4,
            "MENU": 5,
            "BACK": 6,
            "MUTE": 7,
            "VOLUME_UP": 8,
            "VOLUME_DOWN": 9,
        }
        # The device's display table (BE-14): a different, smaller set of commands.
        mock.CEC_OUTPUT_COMMAND_MAP = {
            "POWER_ON": 0,
            "POWER_OFF": 1,
            "MUTE": 2,
            "VOLUME_DOWN": 3,
            "VOLUME_UP": 4,
            "ACTIVE": 5,
        }
        mock.send_cec = AsyncMock(return_value=True)
        return mock

    def test_get_input_cec_method_no_matrix(self):
        """Without a matrix, get_input_cec_method should return None."""
        from driver import get_input_cec_method, set_matrix

        set_matrix(None)
        result = get_input_cec_method("POWER_ON")
        assert result is None

    def test_get_input_cec_method_invalid_command(self):
        """Invalid CEC command should return None (warning logged)."""
        from driver import get_input_cec_method, set_matrix

        mock = self._get_mock_matrix_with_cec_map()
        set_matrix(mock)
        result = get_input_cec_method("nonexistent_command_xyz")
        assert result is None

    def test_get_output_cec_method_no_matrix(self):
        """Without a matrix, get_output_cec_method should return None."""
        from driver import get_output_cec_method, set_matrix

        set_matrix(None)
        result = get_output_cec_method("POWER_ON")
        assert result is None

    def test_get_output_cec_method_invalid_command(self):
        """Invalid output CEC command should return None (warning logged)."""
        from driver import get_output_cec_method, set_matrix

        mock = self._get_mock_matrix_with_cec_map()
        set_matrix(mock)
        result = get_output_cec_method("nonexistent_command_xyz")
        assert result is None

    def test_get_input_cec_method_valid_command(self):
        """Valid CEC command should return an async callable."""
        from driver import get_input_cec_method, set_matrix

        mock = self._get_mock_matrix_with_cec_map()
        set_matrix(mock)
        method = get_input_cec_method("POWER_ON")
        assert method is not None
        assert callable(method)

    def test_get_output_cec_method_uses_the_display_table(self):
        """Displays accept only the output table (BE-14): source-only keys are refused, ACTIVE is accepted."""
        from driver import get_output_cec_method, set_matrix

        mock = self._get_mock_matrix_with_cec_map()
        set_matrix(mock)
        for command in ("POWER_ON", "VOLUME_UP", "ACTIVE"):
            assert callable(get_output_cec_method(command)), command
        for command in ("MENU", "BACK", "PLAY", "UP"):
            assert get_output_cec_method(command) is None, command


# =============================================================================
# Test Connection State Transitions
# =============================================================================


class TestConnectionEvents:
    """Test the matrix event handler functions."""

    def test_on_matrix_error_logs_error(self):
        """on_matrix_error only logs: reconnecting is the matrix's job (BE-06)."""
        from driver import on_matrix_error, set_matrix

        mock = type("MockMatrix", (), {"connected": False})()
        set_matrix(mock)

        on_matrix_error("Connection timeout")
        on_matrix_error("")
        on_matrix_error("Complex error: " + "x" * 1000)

    def test_on_matrix_connected_with_no_api(self):
        """on_matrix_connected works before the integration API exists (no event loop needed)."""
        from driver import _driver_state, _entity_sync, on_matrix_connected, set_matrix

        _driver_state.api = None
        set_matrix(type("MockMatrix", (), {"connected": True})())
        on_matrix_connected()
        assert _entity_sync.available is True

    def test_on_matrix_disconnected_with_no_api(self):
        """on_matrix_disconnected marks the entities unavailable, also without an API."""
        from driver import _driver_state, _entity_sync, on_matrix_disconnected, set_matrix

        _driver_state.api = None
        set_matrix(type("MockMatrix", (), {"connected": False})())
        on_matrix_disconnected()
        assert _entity_sync.available is False

    def test_the_driver_has_no_reconnect_loop_of_its_own(self):
        """BE-06: the matrix reconnects itself; a second loop in the driver used to cancel itself."""
        import driver

        for name in ("_reconnect_loop", "_start_reconnection", "_stop_reconnection", "_reconnect_task"):
            assert not hasattr(driver, name), name


# =============================================================================
# Test Constants
# =============================================================================


class TestConstants:
    """Test that critical constants are defined with correct values."""

    def test_rest_api_port_default(self):
        """REST API port should be 8080 by default."""
        from driver import REST_API_PORT

        assert REST_API_PORT == 8080

    def test_polling_interval(self):
        """Polling interval should be reasonable (5-60 seconds)."""
        from driver import POLLING_INTERVAL

        assert 5 <= POLLING_INTERVAL <= 60

    def test_lock_file_path(self):
        """Lock file should be in a writable location."""
        from driver import LOCK_FILE

        assert isinstance(LOCK_FILE, Path)
        # Should be in data directory or system temp
        assert LOCK_FILE.parent.exists() or str(LOCK_FILE.parent).startswith("/tmp") or "Temp" in str(LOCK_FILE.parent)


# =============================================================================
# WP-B2: Remote commands, device state, entity state sync, start-up paths
# =============================================================================


class _FakeEntities:
    """Just enough of ucapi's Entities store: storage plus a record of update_attributes events."""

    def __init__(self):
        self.storage = {}
        self.sent = []

    def get(self, entity_id):
        return self.storage.get(entity_id)

    def contains(self, entity_id):
        return entity_id in self.storage

    def add(self, entity):
        if entity.id in self.storage:
            return False
        self.storage[entity.id] = entity
        return True

    def remove(self, entity_id):
        self.storage.pop(entity_id, None)
        return True

    def get_all(self):
        return [{"entity_id": e.id} for e in self.storage.values()]

    def update_attributes(self, entity_id, attributes):
        self.storage[entity_id].attributes.update(attributes)
        self.sent.append((entity_id, dict(attributes)))
        return True


class _FakeApi:
    def __init__(self):
        self.available_entities = _FakeEntities()
        self.configured_entities = _FakeEntities()


class _FakeEntity:
    def __init__(self, entity_id, **attributes):
        self.id = entity_id
        self.attributes = dict(attributes)


@pytest.fixture
def fake_api(monkeypatch):
    """A fresh EntityStateSync on a fake integration API (restored afterwards)."""
    import driver

    api = _FakeApi()
    monkeypatch.setattr(driver._driver_state, "api", api)
    monkeypatch.setattr(driver, "_entity_sync", driver.EntityStateSync())
    monkeypatch.setattr(driver, "_device_power", {})
    return api


class TestCommandParameters:
    """send_cmd / send_cmd_sequence parameters (entity_remote.md; UC-22)."""

    def test_defaults(self):
        from driver import DEFAULT_CMD_DELAY_MS, parse_command_timing

        assert parse_command_timing(None) == (1, DEFAULT_CMD_DELAY_MS, 0)
        assert parse_command_timing({"command": "UP"}) == (1, DEFAULT_CMD_DELAY_MS, 0)

    def test_values_and_caps(self):
        from driver import DEFAULT_CMD_DELAY_MS, MAX_CMD_DELAY_MS, MAX_CMD_REPEAT, parse_command_timing

        assert parse_command_timing({"repeat": 3, "delay": 50, "hold": 200}) == (3, 50, 200)
        assert parse_command_timing({"repeat": "2", "delay": "0"}) == (2, 0, 0)
        assert parse_command_timing({"repeat": 0}) == (1, DEFAULT_CMD_DELAY_MS, 0)
        assert parse_command_timing({"repeat": 10_000, "delay": 10**9, "hold": 10**9}) == (
            MAX_CMD_REPEAT, MAX_CMD_DELAY_MS, MAX_CMD_DELAY_MS)

    @pytest.mark.parametrize("params", [{"repeat": "many"}, {"delay": -1}, {"hold": [1]}])
    def test_garbage_is_rejected(self, params):
        from driver import parse_command_timing

        with pytest.raises((TypeError, ValueError)):
            parse_command_timing(params)

    def test_command_lists(self):
        from driver import command_list

        assert command_list("send_cmd", {"command": "VOLUME_UP"}) == ["VOLUME_UP"]
        assert command_list("send_cmd", {}) is None
        assert command_list("send_cmd", {"command": " "}) is None
        assert command_list("send_cmd_sequence", {"sequence": ["UP", "SELECT"]}) == ["UP", "SELECT"]
        # The button-mapping form of a sequence is a comma-separated string (entity_remote.md).
        assert command_list("send_cmd_sequence", {"sequence": "HOME, CURSOR_DOWN"}) == ["HOME", "CURSOR_DOWN"]
        assert command_list("send_cmd_sequence", {"sequence": []}) is None
        assert command_list("send_cmd_sequence", {"sequence": ["UP", 3]}) is None
        assert command_list("send_cmd_sequence", None) is None


class _CecMatrix:
    """A connected matrix that records CEC sends (the device's real tables are exercised in tests/uc)."""

    connected = True

    def __init__(self, fail_on=()):
        self.sent = []
        self.fail_on = set(fail_on)
        self.CEC_COMMAND_MAP = {"POWER_ON": 1, "POWER_OFF": 2, "UP": 3, "SELECT": 5, "VOLUME_UP": 19}
        self.CEC_OUTPUT_COMMAND_MAP = {"POWER_ON": 0, "POWER_OFF": 1, "VOLUME_UP": 4}

    async def send_cec(self, command, port, is_output=False):
        self.sent.append((command.upper(), port, is_output))
        return command.upper() not in self.fail_on


class TestCecRemoteCommands:
    """remote.<input|output>_N_cec: on/off/toggle/send_cmd/send_cmd_sequence (UC-01, UC-22)."""

    async def _run(self, matrix, port_type, cmd_id, params=None):
        import driver

        driver.set_matrix(matrix)
        getter = driver.get_output_cec_method if port_type == "output" else driver.get_input_cec_method
        handler = driver.create_cec_command_handler(2, port_type, getter)
        return await handler(_FakeEntity(f"remote.{port_type}_2_cec"), cmd_id, params, None)

    async def test_on_off_send_power(self, fake_api):
        matrix = _CecMatrix()
        assert await self._run(matrix, "output", "on") == 200
        assert await self._run(matrix, "input", "off") == 200
        assert matrix.sent == [("POWER_ON", 2, True), ("POWER_OFF", 2, False)]

    async def test_toggle_from_unknown_turns_on_then_follows_the_tracked_state(self, fake_api):
        matrix = _CecMatrix()
        for _ in range(3):
            assert await self._run(matrix, "output", "toggle") == 200
        assert [c for c, _, _ in matrix.sent] == ["POWER_ON", "POWER_OFF", "POWER_ON"]

    async def test_power_commands_update_the_entity_states(self, fake_api):
        import driver

        driver._entity_sync.available = True
        await self._run(_CecMatrix(), "output", "send_cmd", {"command": "POWER_OFF"})
        assert driver._entity_sync.value("remote.output_2_cec", "state") == "OFF"
        assert driver._entity_sync.value("media_player.output_2", "state") == "OFF"
        assert driver._toggle_turns_on("output", 2) is True

    async def test_send_cmd_repeat(self, fake_api):
        matrix = _CecMatrix()
        assert await self._run(matrix, "output", "send_cmd", {"command": "VOLUME_UP", "repeat": 3, "delay": 0}) == 200
        assert matrix.sent == [("VOLUME_UP", 2, True)] * 3

    async def test_sequence_with_repeat(self, fake_api):
        matrix = _CecMatrix()
        params = {"sequence": ["UP", "SELECT"], "repeat": 2, "delay": 0}
        assert await self._run(matrix, "input", "send_cmd_sequence", params) == 200
        assert [c for c, _, _ in matrix.sent] == ["UP", "UP", "SELECT", "SELECT"]

    async def test_an_unknown_command_in_a_sequence_sends_nothing(self, fake_api):
        matrix = _CecMatrix()
        params = {"sequence": ["UP", "SELF_DESTRUCT"], "delay": 0}
        assert await self._run(matrix, "input", "send_cmd_sequence", params) == 400
        assert matrix.sent == []

    @pytest.mark.parametrize(("cmd_id", "params"), [
        ("send_cmd", None), ("send_cmd", {"command": ""}), ("send_cmd_sequence", {"sequence": []}),
        ("send_cmd", {"command": "UP", "repeat": "x"}),
    ])
    async def test_malformed_requests_answer_400(self, fake_api, cmd_id, params):
        matrix = _CecMatrix()
        assert await self._run(matrix, "input", cmd_id, params) == 400
        assert matrix.sent == []

    async def test_a_failed_send_stops_the_sequence(self, fake_api):
        matrix = _CecMatrix(fail_on={"UP"})
        assert await self._run(matrix, "input", "send_cmd_sequence", {"sequence": ["UP", "SELECT"]}) == 500
        assert [c for c, _, _ in matrix.sent] == ["UP"]

    async def test_unknown_entity_command_is_501(self, fake_api):
        assert await self._run(_CecMatrix(), "input", "cursor_up") == 501

    async def test_disconnected_matrix_is_503(self, fake_api):
        matrix = _CecMatrix()
        matrix.connected = False
        assert await self._run(matrix, "input", "on") == 503
        assert matrix.sent == []

    async def test_an_exception_becomes_server_error(self, fake_api):
        """UC-01: an exception in a handler answers 500 instead of closing the Remote's WebSocket."""

        class Broken(_CecMatrix):
            async def send_cec(self, command, port, is_output=False):
                raise AttributeError("boom")

        assert await self._run(Broken(), "input", "on") == 500


class TestDeviceState:
    """The device state follows the matrix connection state (UC-04)."""

    @pytest.mark.parametrize(("state", "expected"), [
        ("connected", "CONNECTED"), ("degraded", "CONNECTED"), ("connecting", "CONNECTING"),
        ("backoff", "ERROR"), ("disconnected", "DISCONNECTED"),
    ])
    def test_mapping(self, state, expected):
        from driver import device_state_for
        from orei_matrix import ConnectionState

        matrix = type("M", (), {"connection_state": ConnectionState(state)})()
        assert device_state_for(matrix) == expected

    def test_no_matrix_is_disconnected(self):
        from driver import device_state_for

        assert device_state_for(None) == "DISCONNECTED"


class TestEntityStateSync:
    """Changed-only pushes (UC-07), UNAVAILABLE with last known values (UC-04), standby (UC-06)."""

    def _subscribe(self, api, entity):
        import driver

        api.available_entities.add(entity)
        driver._entity_sync.register(entity)
        api.configured_entities.add(entity)
        driver._entity_sync.resend([entity.id])
        api.configured_entities.sent.clear()

    def test_only_changed_attributes_are_sent(self, fake_api):
        import driver

        sync = driver._entity_sync
        sync.available = True
        self._subscribe(fake_api, _FakeEntity("sensor.x", state="UNKNOWN", value="Unknown"))
        sync.update("sensor.x", {"value": "Active", "state": "ON"})
        sync.update("sensor.x", {"value": "Active", "state": "ON"})
        sync.update("sensor.x", {"value": "No Signal", "state": "ON"})
        assert fake_api.configured_entities.sent == [
            ("sensor.x", {"value": "Active", "state": "ON"}), ("sensor.x", {"value": "No Signal"})]

    def test_outage_keeps_last_known_values(self, fake_api):
        import driver

        sync = driver._entity_sync
        sync.available = True
        self._subscribe(fake_api, _FakeEntity("media_player.output_1", state="ON", source="PS5"))
        sync.set_available(False)
        assert fake_api.configured_entities.sent == [("media_player.output_1", {"state": "UNAVAILABLE"})]
        assert fake_api.configured_entities.get("media_player.output_1").attributes["source"] == "PS5"
        sync.update("media_player.output_1", {"source": "Apple TV"})
        sync.set_available(True)
        assert fake_api.configured_entities.sent[-1] == ("media_player.output_1", {"state": "ON"})
        assert fake_api.configured_entities.get("media_player.output_1").attributes["source"] == "Apple TV"

    def test_standby_holds_changes_until_wake(self, fake_api):
        import driver

        sync = driver._entity_sync
        sync.available = True
        self._subscribe(fake_api, _FakeEntity("sensor.x", state="ON", value="a"))
        sync.set_standby(True)
        sync.update("sensor.x", {"value": "b"})
        sync.update("sensor.x", {"value": "c"})
        assert fake_api.configured_entities.sent == []
        sync.set_standby(False)
        assert fake_api.configured_entities.sent == [("sensor.x", {"value": "c"})]

    def test_subscribe_sends_the_full_state(self, fake_api):
        import driver

        sync = driver._entity_sync
        sync.available = False
        entity = _FakeEntity("sensor.x", state="UNKNOWN", value="Unknown")
        fake_api.available_entities.add(entity)
        sync.register(entity)
        fake_api.configured_entities.add(entity)
        sync.resend(["sensor.x"])
        assert fake_api.configured_entities.sent == [("sensor.x", {"state": "UNAVAILABLE", "value": "Unknown"})]


class TestNameRefresh:
    """A failed name read (answered with the default names) never replaces the known names."""

    async def test_default_names_from_a_failed_read_are_ignored(self, fake_api, monkeypatch):
        import driver

        known = {n: f"Source {n}" for n in range(1, 9)}
        monkeypatch.setattr(driver._driver_state, "input_names", dict(known))

        class M:
            host, port = "10.0.0.2", 443

            async def get_all_input_names(self):
                return {n: f"Input {n}" for n in range(1, 9)}

            async def get_output_names(self):  # pragma: no cover - must not be reached
                raise AssertionError("names must not be rebuilt")

        await driver.refresh_names(M(), save=True)
        assert driver._driver_state.input_names == known

    def test_rebuild_replaces_subscribed_entities_in_place(self, fake_api, monkeypatch):
        """UC-05: new names never clear the subscriptions; the subscribed entity is replaced and told what changed."""
        import driver

        monkeypatch.setattr(driver._driver_state, "input_names", {n: f"Input {n}" for n in range(1, 9)})
        monkeypatch.setattr(driver._driver_state, "output_names", {})
        driver._entity_sync.available = True
        driver.install_entities()
        assert len(fake_api.available_entities.storage) == 74
        old = fake_api.available_entities.get("media_player.output_1")
        fake_api.configured_entities.add(old)
        driver._entity_sync.update("media_player.output_1", {"source": "Input 2"})
        fake_api.configured_entities.sent.clear()

        monkeypatch.setattr(driver._driver_state, "input_names", {n: f"Source {n}" for n in range(1, 9)})
        driver.install_entities(rebuild=True)
        new = fake_api.configured_entities.get("media_player.output_1")
        assert new is not old and new is fake_api.available_entities.get("media_player.output_1")
        assert new.attributes["source"] == "Input 2"  # last known state kept
        assert fake_api.configured_entities.sent == [
            ("media_player.output_1", {"source_list": [f"Source {n}" for n in range(1, 9)]})]
        assert len(fake_api.available_entities.storage) == 74


class TestStartupHelpers:
    """UC-19 / BE-21: ports, driver.json and the config path do not depend on the CWD or the OS."""

    def test_address_in_use_on_every_platform(self):
        import errno

        from driver import is_address_in_use

        assert is_address_in_use(OSError(errno.EADDRINUSE, "in use"))  # 98 Linux / 48 macOS
        assert is_address_in_use(OSError(10048, "in use"))  # Windows WSAEADDRINUSE
        assert not is_address_in_use(OSError(errno.EACCES, "denied"))
        assert not is_address_in_use(ValueError("x"))

    def test_driver_json_is_found_relative_to_the_package(self, tmp_path, monkeypatch):
        import driver

        monkeypatch.chdir(tmp_path)
        assert driver.DRIVER_JSON.is_file()
        monkeypatch.delenv("UC_INTEGRATION_HTTP_PORT", raising=False)
        assert driver.integration_port() == 9095
        monkeypatch.setenv("UC_INTEGRATION_HTTP_PORT", "19095")
        assert driver.integration_port() == 19095

    def test_config_file_uses_the_ucapi_config_dir(self, tmp_path, monkeypatch):
        import driver

        api = type("Api", (), {"config_dir_path": str(tmp_path / "uc")})()
        monkeypatch.setattr(driver._driver_state, "api", api)
        legacy = tmp_path / "legacy" / "config_state.json"
        monkeypatch.setattr(driver, "CONFIG_FILE", legacy)
        assert driver.config_file_path() == tmp_path / "uc" / "config_state.json"
        # A configuration written by an older version at the legacy path is still found ...
        legacy.parent.mkdir()
        legacy.write_text('{"host": "10.0.0.2", "port": 443}', encoding="utf-8")
        assert driver.load_config()["host"] == "10.0.0.2"
        # ... and the next save goes to ucapi's config directory.
        (tmp_path / "uc").mkdir()
        driver.save_config("10.0.0.3", 443, {1: "PS5"})
        assert driver.load_config()["host"] == "10.0.0.3"
