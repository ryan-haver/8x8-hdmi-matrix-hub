"""
API Client Adapter for OreiMatrix compatibility.

This adapter wraps the MatrixApiClient to provide an interface compatible
with OreiMatrix, allowing seamless switching between direct hardware
communication and REST API-based communication.
"""

import logging
from typing import Optional

from .api_client import MatrixApiClient

_LOG = logging.getLogger("uc.adapter")


class MatrixApiAdapter:
    """
    Adapter that makes MatrixApiClient compatible with OreiMatrix interface.
    
    This allows the UC driver to use either:
    - Direct mode: OreiMatrix instance
    - API mode: MatrixApiClient via this adapter
    
    Both provide the same interface for entity command handlers.
    """
    
    def __init__(self, api_client: MatrixApiClient):
        """
        Initialize the adapter.
        
        :param api_client: MatrixApiClient instance to wrap
        """
        self._client = api_client
        self._connected = False
        self._input_names: dict[int, str] = {}
        self._output_names: dict[int, str] = {}
    
    @property
    def connected(self) -> bool:
        """Check if connected to the API."""
        return self._connected
    
    async def connect(self) -> bool:
        """
        Connect to the API and verify it's responsive.
        
        :return: True if connection successful
        """
        try:
            health = await self._client.get_health()
            if health and health.get("status") == "ok":
                self._connected = True
                await self._refresh_names()
                _LOG.info("Connected to Matrix Hub API")
                return True
            return False
        except Exception as e:
            _LOG.error(f"Failed to connect to API: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from the API."""
        await self._client.close()
        self._connected = False
    
    async def _refresh_names(self):
        """Refresh input/output names from API."""
        try:
            inputs = await self._client.get_inputs()
            if inputs and "inputs" in inputs:
                for inp in inputs["inputs"]:
                    port = inp.get("port", inp.get("input"))
                    name = inp.get("name")
                    if port and name:
                        self._input_names[int(port)] = name
            
            outputs = await self._client.get_outputs()
            if outputs and "outputs" in outputs:
                for out in outputs["outputs"]:
                    port = out.get("port", out.get("output"))
                    name = out.get("name")
                    if port and name:
                        self._output_names[int(port)] = name
        except Exception as e:
            _LOG.warning(f"Failed to refresh names: {e}")
    
    def get_input_names(self) -> dict[int, str]:
        """Get input names dictionary."""
        return self._input_names.copy()
    
    def get_output_names(self) -> dict[int, str]:
        """Get output names dictionary."""
        return self._output_names.copy()
    
    # =========================================================================
    # Matrix Control Commands (OreiMatrix-compatible interface)
    # =========================================================================
    
    async def recall_preset(self, preset: int) -> bool:
        """Recall a preset configuration."""
        return await self._client.recall_preset(preset)
    
    async def save_preset(self, preset: int) -> bool:
        """Save current routing to a preset."""
        return await self._client.save_preset(preset)
    
    async def switch_input(self, input_num: int, output_num: int) -> bool:
        """Route an input to an output."""
        return await self._client.switch_input(input_num, output_num)
    
    async def switch_all(self, input_num: int) -> bool:
        """Route an input to all outputs."""
        return await self._client.switch_all_outputs(input_num)
    
    async def power_on(self) -> bool:
        """Power on the matrix."""
        return await self._client.power_on()
    
    async def power_off(self) -> bool:
        """Power off the matrix."""
        return await self._client.power_off()
    
    # =========================================================================
    # CEC Commands (OreiMatrix-compatible interface)
    # =========================================================================
    
    async def send_cec(
        self, command: str, port: int, is_output: bool = False
    ) -> bool:
        """
        Send a CEC command to a port.
        
        :param command: CEC command name
        :param port: Port number (1-8)
        :param is_output: True for output, False for input
        :return: True if successful
        """
        if is_output:
            return await self._client.send_cec_output(port, command)
        return await self._client.send_cec_input(port, command)
    
    async def send_cec_input(self, input_num: int, command: str) -> bool:
        """Send CEC command to an input device."""
        return await self._client.send_cec_input(input_num, command)
    
    async def send_cec_output(self, output_num: int, command: str) -> bool:
        """Send CEC command to an output device."""
        return await self._client.send_cec_output(output_num, command)
    
    # =========================================================================
    # Status Queries
    # =========================================================================
    
    async def get_status(self) -> dict:
        """Get current matrix status."""
        return await self._client.get_status()
    
    async def get_all_input_names(self) -> dict[int, str]:
        """Get input names from API."""
        await self._refresh_names()
        return self._input_names.copy()
    
    async def get_output_names(self) -> dict[int, str]:
        """Get output names from API."""
        await self._refresh_names()
        return self._output_names.copy()
    
    async def get_output_status(self) -> Optional[dict]:
        """Get output status including routing."""
        result = await self._client.get_outputs()
        if result and "outputs" in result:
            # Convert to OreiMatrix format
            connections = []
            for out in result["outputs"]:
                current_input = out.get("current_input", 0)
                connections.append(current_input)
            return {"allconnect": connections}
        return None
    
    async def get_input_status(self) -> Optional[dict]:
        """Get input status including signal presence."""
        result = await self._client.get_inputs()
        if result and "inputs" in result:
            # Convert to OreiMatrix format
            inactive = []
            for inp in result["inputs"]:
                has_signal = inp.get("signal", False)
                inactive.append(1 if has_signal else 0)
            return {"inactive": inactive}
        return None
    
    # =========================================================================
    # WebSocket for Real-time Updates
    # =========================================================================
    
    async def connect_websocket(self) -> bool:
        """Connect to WebSocket for real-time updates."""
        return await self._client.connect_websocket()
    
    def on_status_update(self, callback):
        """Register callback for status updates."""
        self._client.on_status_update(callback)
    
    @property
    def websocket_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._client.websocket_connected
