"""
Unit tests for OREI Matrix control library.

Uses mocking to test without requiring actual hardware.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from orei_matrix import OreiMatrix, Events


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def matrix():
    """Create a fresh OreiMatrix instance for each test."""
    return OreiMatrix("192.168.1.100", port=443, use_https=True)


@pytest.fixture
def connected_matrix(matrix):
    """Create a matrix instance that appears connected."""
    matrix._connected = True
    matrix._session = MagicMock()
    return matrix


# =============================================================================
# Connection Tests
# =============================================================================


class TestConnection:
    """Tests for connection and authentication."""

    @pytest.mark.asyncio
    async def test_connect_success(self, matrix):
        """Test successful connection and authentication."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"comhead":"login","result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_response)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await matrix.connect()

        assert result is True
        assert matrix.connected is True

    @pytest.mark.asyncio
    async def test_connect_auth_failure(self, matrix):
        """Test connection with authentication failure."""
        # Matrix returns error response without 'login' comhead when auth fails
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"comhead":"error","result":0,"message":"invalid credentials"}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_response)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await matrix.connect()

        assert result is False
        assert matrix.connected is False

    @pytest.mark.asyncio
    async def test_connect_timeout(self, matrix):
        """Test connection timeout handling."""
        mock_session = MagicMock()
        mock_session.post = MagicMock(side_effect=asyncio.TimeoutError())

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await matrix.connect()

        assert result is False
        assert matrix.connected is False

    @pytest.mark.asyncio
    async def test_disconnect(self, connected_matrix):
        """Test disconnection."""
        connected_matrix._session.close = AsyncMock()

        await connected_matrix.disconnect()

        assert connected_matrix.connected is False
        assert connected_matrix._session is None


# =============================================================================
# Retry Logic Tests
# =============================================================================


class TestRetryLogic:
    """Tests for connection retry with exponential backoff."""

    def test_calculate_retry_delay_initial(self, matrix):
        """Test initial retry delay calculation."""
        delay = matrix._calculate_retry_delay(0)
        # Initial delay is 1.0 with ±10% jitter
        assert 0.9 <= delay <= 1.1

    def test_calculate_retry_delay_exponential(self, matrix):
        """Test exponential backoff increases delay."""
        delay_0 = matrix._calculate_retry_delay(0)
        delay_1 = matrix._calculate_retry_delay(1)
        delay_2 = matrix._calculate_retry_delay(2)

        # Each delay should roughly double (accounting for jitter)
        assert delay_1 > delay_0
        assert delay_2 > delay_1

    def test_calculate_retry_delay_max_cap(self, matrix):
        """Test delay is capped at MAX_RETRY_DELAY."""
        delay = matrix._calculate_retry_delay(100)  # Very high attempt
        # Should be capped at 60.0 with ±10% jitter
        assert delay <= 66.0  # 60 + 10%


# =============================================================================
# Preset Control Tests
# =============================================================================


class TestPresetControl:
    """Tests for preset recall and save."""

    @pytest.mark.asyncio
    async def test_recall_preset_success(self, connected_matrix):
        """Test successful preset recall."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"comhead":"preset set","result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        result = await connected_matrix.recall_preset(3)

        assert result is True
        assert connected_matrix.current_scene == 3

    @pytest.mark.asyncio
    async def test_recall_preset_invalid_number(self, connected_matrix):
        """Test preset recall with invalid preset number."""
        result_low = await connected_matrix.recall_preset(0)
        result_high = await connected_matrix.recall_preset(9)

        assert result_low is False
        assert result_high is False

    @pytest.mark.asyncio
    async def test_save_preset_success(self, connected_matrix):
        """Test successful preset save."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"comhead":"preset save","result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        result = await connected_matrix.save_preset(5)

        assert result is True

    @pytest.mark.asyncio
    async def test_save_preset_invalid_number(self, connected_matrix):
        """Test save preset with invalid preset number."""
        result = await connected_matrix.save_preset(10)
        assert result is False


# =============================================================================
# Input/Output Switching Tests
# =============================================================================


class TestSwitching:
    """Tests for input/output routing."""

    @pytest.mark.asyncio
    async def test_switch_input_success(self, connected_matrix):
        """Test successful input switching."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"comhead":"video switch","result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        result = await connected_matrix.switch_input(3, 1)

        assert result is True

    @pytest.mark.asyncio
    async def test_switch_input_invalid_input(self, connected_matrix):
        """Test switching with invalid input number."""
        result = await connected_matrix.switch_input(0, 1)
        assert result is False

        result = await connected_matrix.switch_input(9, 1)
        assert result is False

    @pytest.mark.asyncio
    async def test_switch_input_invalid_output(self, connected_matrix):
        """Test switching with invalid output number."""
        result = await connected_matrix.switch_input(1, 0)
        assert result is False

        result = await connected_matrix.switch_input(1, 9)
        assert result is False


# =============================================================================
# Advanced Output Control Tests (Sprint 2 Features)
# =============================================================================


class TestAdvancedOutputControl:
    """Tests for Sprint 2 advanced output control features."""

    @pytest.mark.asyncio
    async def test_set_output_hdcp_success(self, connected_matrix):
        """Test setting HDCP mode."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        result = await connected_matrix.set_output_hdcp(1, 2)

        assert result is True

    @pytest.mark.asyncio
    async def test_set_output_hdcp_invalid_output(self, connected_matrix):
        """Test HDCP with invalid output number."""
        result = await connected_matrix.set_output_hdcp(0, 2)
        assert result is False

    @pytest.mark.asyncio
    async def test_set_output_hdr_success(self, connected_matrix):
        """Test setting HDR mode."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        result = await connected_matrix.set_output_hdr(2, 1)

        assert result is True

    @pytest.mark.asyncio
    async def test_set_output_arc_success(self, connected_matrix):
        """Test enabling/disabling ARC."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        result = await connected_matrix.set_output_arc(1, True)
        assert result is True

        result = await connected_matrix.set_output_arc(1, False)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_output_audio_mute_success(self, connected_matrix):
        """Test muting/unmuting audio."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        result = await connected_matrix.set_output_audio_mute(3, True)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_cec_enable_success(self, connected_matrix):
        """Test enabling/disabling CEC per port."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        result = await connected_matrix.set_cec_enable("input", 2, True)
        assert result is True

        result = await connected_matrix.set_cec_enable("output", 1, False)
        assert result is True

    @pytest.mark.asyncio
    async def test_set_cec_enable_invalid_port_type(self, connected_matrix):
        """Test CEC enable with invalid port type."""
        result = await connected_matrix.set_cec_enable("invalid", 1, True)
        assert result is False

    @pytest.mark.asyncio
    async def test_system_reboot(self, connected_matrix):
        """Test system reboot command."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        result = await connected_matrix.system_reboot()

        assert result is True
        # After reboot, should be marked as disconnected
        assert connected_matrix.connected is False


# =============================================================================
# Power Control Tests
# =============================================================================


class TestPowerControl:
    """Tests for power on/off functionality."""

    @pytest.mark.asyncio
    async def test_power_on_success(self, connected_matrix):
        """Test powering on the matrix."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"comhead":"set standby","result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        result = await connected_matrix.power_on()

        assert result is True

    @pytest.mark.asyncio
    async def test_power_off_success(self, connected_matrix):
        """Test powering off the matrix."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"comhead":"set standby","result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        result = await connected_matrix.power_off()

        assert result is True


# =============================================================================
# Event Emission Tests
# =============================================================================


class TestEvents:
    """Tests for event emission."""

    @pytest.mark.asyncio
    async def test_connected_event_emitted(self, matrix):
        """Test CONNECTED event is emitted on successful connection."""
        events_received = []
        matrix.events.on(Events.CONNECTED, lambda: events_received.append("connected"))

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"comhead":"login","result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.post = MagicMock(return_value=mock_response)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            await matrix.connect()

        assert "connected" in events_received

    @pytest.mark.asyncio
    async def test_disconnected_event_emitted(self, connected_matrix):
        """Test DISCONNECTED event is emitted on disconnect."""
        events_received = []
        connected_matrix.events.on(Events.DISCONNECTED, lambda: events_received.append("disconnected"))

        connected_matrix._session.close = AsyncMock()
        await connected_matrix.disconnect()

        assert "disconnected" in events_received

    @pytest.mark.asyncio
    async def test_update_event_on_preset_recall(self, connected_matrix):
        """Test UPDATE event is emitted on preset recall."""
        events_received = []
        connected_matrix.events.on(Events.UPDATE, lambda data: events_received.append(data))

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value='{"comhead":"preset set","result":1}')
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)

        connected_matrix._session.post = MagicMock(return_value=mock_response)

        await connected_matrix.recall_preset(5)

        assert len(events_received) == 1
        assert events_received[0]["scene"] == 5
