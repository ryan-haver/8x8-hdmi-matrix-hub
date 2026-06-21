"""
Tests for integrations/unfolded_circle/ folder.

Tests the UC integration layer:
- MatrixApiAdapter (OreiMatrix-compatible interface over REST API)
- MatrixApiClient (REST API client wrapper)
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# =============================================================================
# Test MatrixApiAdapter
# =============================================================================


class TestMatrixApiAdapter:
    """Test the API adapter that wraps MatrixApiClient."""

    def _get_mock_api_client(self):
        """Create a mock MatrixApiClient."""
        client = MagicMock()
        client.get_health = AsyncMock(return_value={"status": "ok"})
        client.get_inputs = AsyncMock(
            return_value={
                "inputs": [
                    {"port": 1, "name": "PS5"},
                    {"port": 2, "name": "AppleTV"},
                    {"port": 3, "name": "Switch"},
                ]
            }
        )
        client.get_outputs = AsyncMock(
            return_value={
                "outputs": [
                    {"port": 1, "name": "Living Room TV"},
                    {"port": 2, "name": "Bedroom TV"},
                ]
            }
        )
        client.close = AsyncMock()
        client.recall_preset = AsyncMock(return_value=True)
        client.save_preset = AsyncMock(return_value=True)
        client.switch_input = AsyncMock(return_value=True)
        client.switch_all_outputs = AsyncMock(return_value=True)
        client.power_on = AsyncMock(return_value=True)
        client.power_off = AsyncMock(return_value=True)
        client.send_cec_input = AsyncMock(return_value=True)
        client.send_cec_output = AsyncMock(return_value=True)
        return client

    def test_adapter_init_stores_client(self):
        """Adapter should store the API client reference."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        assert adapter._client is mock_client
        assert adapter.connected is False  # Not connected yet

    @pytest.mark.asyncio
    async def test_connect_success(self):
        """Connect should set connected state and refresh names."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        result = await adapter.connect()

        assert result is True
        assert adapter.connected is True
        mock_client.get_health.assert_called_once()
        mock_client.get_inputs.assert_called_once()
        mock_client.get_outputs.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure_health_check_fails(self):
        """Connect should fail if health check returns non-ok status."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        mock_client.get_health = AsyncMock(return_value={"status": "error"})

        adapter = MatrixApiAdapter(mock_client)
        result = await adapter.connect()

        assert result is False
        assert adapter.connected is False

    @pytest.mark.asyncio
    async def test_connect_handles_exception(self):
        """Connect should handle exceptions gracefully."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        mock_client.get_health = AsyncMock(side_effect=Exception("Network error"))

        adapter = MatrixApiAdapter(mock_client)
        result = await adapter.connect()

        assert result is False
        assert adapter.connected is False

    @pytest.mark.asyncio
    async def test_disconnect_closes_client(self):
        """Disconnect should close the API client and set disconnected state."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)
        await adapter.connect()
        await adapter.disconnect()

        assert adapter.connected is False
        mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_names_populates_dictionaries(self):
        """_refresh_names should populate input/output name dictionaries."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)
        await adapter._refresh_names()

        assert adapter.get_input_names() == {1: "PS5", 2: "AppleTV", 3: "Switch"}
        assert adapter.get_output_names() == {1: "Living Room TV", 2: "Bedroom TV"}

    @pytest.mark.asyncio
    async def test_refresh_names_handles_missing_keys(self):
        """_refresh_names should handle missing port/name keys gracefully."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        mock_client.get_inputs = AsyncMock(
            return_value={
                "inputs": [
                    {"port": 1, "name": "Valid"},
                    {"name": "Missing port"},  # No port
                    {"port": 3},  # No name
                ]
            }
        )

        adapter = MatrixApiAdapter(mock_client)
        await adapter._refresh_names()

        # Only valid entry should be added
        assert adapter.get_input_names() == {1: "Valid"}

    def test_get_input_names_returns_copy(self):
        """get_input_names should return a copy (not allow external mutation)."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        adapter = MatrixApiAdapter(self._get_mock_api_client())
        names = adapter.get_input_names()
        names[99] = "Modified"  # Modify the returned dict

        # Internal state should not be affected
        assert 99 not in adapter._input_names

    def test_get_output_names_returns_copy(self):
        """get_output_names should return a copy (not allow external mutation)."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        adapter = MatrixApiAdapter(self._get_mock_api_client())
        names = adapter.get_output_names()
        names[99] = "Modified"

        assert 99 not in adapter._output_names

    @pytest.mark.asyncio
    async def test_recall_preset_delegates_to_client(self):
        """recall_preset should delegate to API client."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        result = await adapter.recall_preset(3)
        assert result is True
        mock_client.recall_preset.assert_called_once_with(3)

    @pytest.mark.asyncio
    async def test_save_preset_delegates_to_client(self):
        """save_preset should delegate to API client."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        result = await adapter.save_preset(5)
        assert result is True
        mock_client.save_preset.assert_called_once_with(5)

    @pytest.mark.asyncio
    async def test_switch_input_delegates_to_client(self):
        """switch_input should delegate to API client."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        result = await adapter.switch_input(2, 5)  # input 2 to output 5
        assert result is True
        mock_client.switch_input.assert_called_once_with(2, 5)

    @pytest.mark.asyncio
    async def test_switch_all_delegates_to_client(self):
        """switch_all should delegate to API client."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        result = await adapter.switch_all(3)
        assert result is True
        mock_client.switch_all_outputs.assert_called_once_with(3)

    @pytest.mark.asyncio
    async def test_power_on_delegates_to_client(self):
        """power_on should delegate to API client."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        result = await adapter.power_on()
        assert result is True
        mock_client.power_on.assert_called_once()

    @pytest.mark.asyncio
    async def test_power_off_delegates_to_client(self):
        """power_off should delegate to API client."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        result = await adapter.power_off()
        assert result is True
        mock_client.power_off.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_cec_input_routes_to_input_client(self):
        """send_cec with is_output=False should use send_cec_input."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        result = await adapter.send_cec("POWER_ON", 2, is_output=False)
        assert result is True
        mock_client.send_cec_input.assert_called_once_with(2, "POWER_ON")
        mock_client.send_cec_output.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_cec_output_routes_to_output_client(self):
        """send_cec with is_output=True should use send_cec_output."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        result = await adapter.send_cec("MUTE", 1, is_output=True)
        assert result is True
        mock_client.send_cec_output.assert_called_once_with(1, "MUTE")
        mock_client.send_cec_input.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_cec_default_is_input(self):
        """send_cec default should be is_output=False (input)."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        await adapter.send_cec("PLAY", 3)  # No is_output specified
        mock_client.send_cec_input.assert_called_once_with(3, "PLAY")
        mock_client.send_cec_output.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_cec_input_method_directly(self):
        """send_cec_input should delegate to API client."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        result = await adapter.send_cec_input(2, "PAUSE")
        assert result is True
        mock_client.send_cec_input.assert_called_once_with(2, "PAUSE")

    @pytest.mark.asyncio
    async def test_send_cec_output_method_directly(self):
        """send_cec_output should delegate to API client."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        adapter = MatrixApiAdapter(mock_client)

        result = await adapter.send_cec_output(1, "VOLUME_UP")
        assert result is True
        mock_client.send_cec_output.assert_called_once_with(1, "VOLUME_UP")

    @pytest.mark.asyncio
    async def test_send_cec_returns_false_on_error(self):
        """send_cec should return False when client returns False."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        mock_client = self._get_mock_api_client()
        mock_client.send_cec_input = AsyncMock(return_value=False)

        adapter = MatrixApiAdapter(mock_client)
        result = await adapter.send_cec_input(1, "INVALID_CMD")

        assert result is False

    def test_cannot_connect_without_api_client(self):
        """Adapter should not be connected without explicit connect() call."""
        from integrations.unfolded_circle.adapter import MatrixApiAdapter

        adapter = MatrixApiAdapter(self._get_mock_api_client())
        assert adapter.connected is False
        # connected should be a property, not allow direct set
        with pytest.raises(AttributeError):
            adapter.connected = True
