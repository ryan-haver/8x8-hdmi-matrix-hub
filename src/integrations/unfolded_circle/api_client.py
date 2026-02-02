"""
Matrix API Client for Unfolded Circle Integration.

This module provides a REST API client that allows the UC driver
to interact with the matrix through the API instead of directly
with the hardware. This enables modular deployment where the UC
driver can run separately from the core API.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Any, Callable, Optional

_LOG = logging.getLogger("uc.api_client")


class MatrixApiClient:
    """
    REST API client for UC driver to interact with the Matrix Hub API.
    
    This client wraps all matrix operations as HTTP calls to the REST API,
    allowing the UC driver to be decoupled from the core hardware library.
    """
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize the API client.
        
        :param base_url: Base URL of the Matrix Hub API (e.g., http://localhost:8080)
        """
        self.base_url = base_url.rstrip("/")
        self.ws_url = base_url.replace("http", "ws").rstrip("/") + "/ws"
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._ws_task: Optional[asyncio.Task] = None
        self._status_callbacks: list[Callable[[dict], Any]] = []
        self._connected = False
        
    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the API client and cleanup resources."""
        await self.disconnect_websocket()
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    # =========================================================================
    # Status & Health
    # =========================================================================
    
    async def get_health(self) -> dict:
        """Get API health status."""
        return await self._get("/api/health")
    
    async def get_status(self) -> dict:
        """Get current matrix status including routing."""
        return await self._get("/api/status")
    
    async def get_full_status(self) -> dict:
        """Get comprehensive matrix status."""
        return await self._get("/api/status/full")
    
    async def get_presets(self) -> dict:
        """Get all preset configurations."""
        return await self._get("/api/presets")
    
    async def get_inputs(self) -> dict:
        """Get all input information."""
        return await self._get("/api/inputs")
    
    async def get_outputs(self) -> dict:
        """Get all output information."""
        return await self._get("/api/outputs")
    
    async def get_cable_status(self) -> dict:
        """Get cable connection status for all ports."""
        return await self._get("/api/status/cables")
    
    async def get_cec_status(self) -> dict:
        """Get CEC status for all ports."""
        return await self._get("/api/status/cec")
    
    # =========================================================================
    # Control Commands
    # =========================================================================
    
    async def recall_preset(self, preset: int) -> bool:
        """
        Recall a matrix preset.
        
        :param preset: Preset number (1-8)
        :return: True if successful
        """
        result = await self._post(f"/api/preset/{preset}")
        return result.get("success", False) if result else False
    
    async def save_preset(self, preset: int) -> bool:
        """
        Save current routing to a preset.
        
        :param preset: Preset number (1-8)
        :return: True if successful
        """
        result = await self._post(f"/api/preset/{preset}/save")
        return result.get("success", False) if result else False
    
    async def switch_input(self, input_num: int, output_num: int) -> bool:
        """
        Route an input to an output.
        
        :param input_num: Input number (1-8)
        :param output_num: Output number (1-8)
        :return: True if successful
        """
        result = await self._post("/api/switch", json={
            "input": input_num,
            "output": output_num
        })
        return result.get("success", False) if result else False
    
    async def switch_all_outputs(self, input_num: int) -> bool:
        """
        Route an input to all outputs.
        
        :param input_num: Input number (1-8)
        :return: True if successful
        """
        result = await self._post("/api/switch", json={
            "input": input_num,
            "output": 0  # 0 = all outputs
        })
        return result.get("success", False) if result else False
    
    async def power_on(self) -> bool:
        """Power on the matrix."""
        result = await self._post("/api/power/on")
        return result.get("success", False) if result else False
    
    async def power_off(self) -> bool:
        """Power off the matrix."""
        result = await self._post("/api/power/off")
        return result.get("success", False) if result else False
    
    async def next_input(self, output: int = 1) -> bool:
        """
        Cycle to next input for an output.
        
        :param output: Output number (default: 1)
        :return: True if successful
        """
        result = await self._post("/api/input/next", json={"output": output})
        return result.get("success", False) if result else False
    
    async def previous_input(self, output: int = 1) -> bool:
        """
        Cycle to previous input for an output.
        
        :param output: Output number (default: 1)
        :return: True if successful
        """
        result = await self._post("/api/input/previous", json={"output": output})
        return result.get("success", False) if result else False
    
    # =========================================================================
    # CEC Commands
    # =========================================================================
    
    async def send_cec(self, target_type: str, port: int, command: str) -> bool:
        """
        Send a CEC command to an input or output device.
        
        :param target_type: "input" or "output"
        :param port: Port number (1-8)
        :param command: CEC command name (e.g., "POWER_ON", "PLAY", "MUTE")
        :return: True if successful
        """
        result = await self._post(f"/api/cec/{target_type}/{port}/{command}")
        return result.get("success", False) if result else False
    
    async def send_cec_input(self, input_num: int, command: str) -> bool:
        """Send CEC command to an input device."""
        return await self.send_cec("input", input_num, command)
    
    async def send_cec_output(self, output_num: int, command: str) -> bool:
        """Send CEC command to an output device."""
        return await self.send_cec("output", output_num, command)
    
    async def get_cec_commands(self) -> dict:
        """Get list of available CEC commands."""
        return await self._get("/api/cec/commands")
    
    # =========================================================================
    # Scenes & Profiles
    # =========================================================================
    
    async def get_scenes(self) -> list:
        """Get all scenes."""
        result = await self._get("/api/scenes")
        return result.get("scenes", []) if result else []
    
    async def recall_scene(self, scene_id: str) -> bool:
        """
        Recall a scene.
        
        :param scene_id: Scene identifier
        :return: True if successful
        """
        result = await self._post(f"/api/scene/{scene_id}/recall")
        return result.get("success", False) if result else False
    
    async def get_profiles(self) -> list:
        """Get all profiles."""
        result = await self._get("/api/profiles")
        return result.get("profiles", []) if result else []
    
    async def recall_profile(self, profile_id: str) -> bool:
        """
        Recall a profile.
        
        :param profile_id: Profile identifier
        :return: True if successful
        """
        result = await self._post(f"/api/profile/{profile_id}/recall")
        return result.get("success", False) if result else False
    
    # =========================================================================
    # Output Settings
    # =========================================================================
    
    async def set_output_hdcp(self, output: int, mode: str) -> bool:
        """Set HDCP mode for an output."""
        result = await self._post(f"/api/output/{output}/hdcp", json={"mode": mode})
        return result.get("success", False) if result else False
    
    async def set_output_hdr(self, output: int, mode: str) -> bool:
        """Set HDR mode for an output."""
        result = await self._post(f"/api/output/{output}/hdr", json={"mode": mode})
        return result.get("success", False) if result else False
    
    async def set_output_scaler(self, output: int, mode: str) -> bool:
        """Set scaler mode for an output."""
        result = await self._post(f"/api/output/{output}/scaler", json={"mode": mode})
        return result.get("success", False) if result else False
    
    async def set_output_arc(self, output: int, enabled: bool) -> bool:
        """Enable/disable ARC for an output."""
        result = await self._post(f"/api/output/{output}/arc", json={"enabled": enabled})
        return result.get("success", False) if result else False
    
    async def set_output_mute(self, output: int, muted: bool) -> bool:
        """Mute/unmute an output."""
        result = await self._post(f"/api/output/{output}/mute", json={"muted": muted})
        return result.get("success", False) if result else False
    
    # =========================================================================
    # Device Settings (Names, Icons)
    # =========================================================================
    
    async def get_device_settings(self) -> dict:
        """Get all device settings (names, icons, colors)."""
        return await self._get("/api/device-settings")
    
    async def set_input_name(self, input_num: int, name: str) -> bool:
        """Set custom name for an input."""
        result = await self._post(f"/api/input/{input_num}/name", json={"name": name})
        return result.get("success", False) if result else False
    
    async def set_output_name(self, output_num: int, name: str) -> bool:
        """Set custom name for an output."""
        result = await self._post(f"/api/output/{output_num}/name", json={"name": name})
        return result.get("success", False) if result else False
    
    # =========================================================================
    # WebSocket for Real-time Updates
    # =========================================================================
    
    async def connect_websocket(self) -> bool:
        """
        Connect to the API WebSocket for real-time updates.
        
        :return: True if connected successfully
        """
        try:
            await self._ensure_session()
            self._ws = await self._session.ws_connect(self.ws_url)
            self._connected = True
            self._ws_task = asyncio.create_task(self._ws_listen_loop())
            _LOG.info(f"WebSocket connected to {self.ws_url}")
            return True
        except Exception as e:
            _LOG.error(f"WebSocket connection failed: {e}")
            self._connected = False
            return False
    
    async def disconnect_websocket(self):
        """Disconnect from the WebSocket."""
        self._connected = False
        if self._ws_task:
            self._ws_task.cancel()
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass
            self._ws_task = None
        if self._ws and not self._ws.closed:
            await self._ws.close()
            self._ws = None
    
    async def _ws_listen_loop(self):
        """Background task to listen for WebSocket messages."""
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._dispatch_status_update(data)
                    except json.JSONDecodeError:
                        _LOG.warning(f"Invalid JSON from WebSocket: {msg.data[:100]}")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    _LOG.error(f"WebSocket error: {self._ws.exception()}")
                    break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    _LOG.info("WebSocket closed by server")
                    break
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _LOG.error(f"WebSocket listen error: {e}")
        finally:
            self._connected = False
    
    async def _dispatch_status_update(self, data: dict):
        """Dispatch status update to all registered callbacks."""
        for callback in self._status_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                _LOG.error(f"Callback error: {e}")
    
    def on_status_update(self, callback: Callable[[dict], Any]):
        """
        Register a callback for status updates from WebSocket.
        
        :param callback: Function to call with status update data
        """
        self._status_callbacks.append(callback)
    
    def remove_status_callback(self, callback: Callable[[dict], Any]):
        """Remove a previously registered callback."""
        if callback in self._status_callbacks:
            self._status_callbacks.remove(callback)
    
    @property
    def websocket_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._connected and self._ws is not None and not self._ws.closed
    
    # =========================================================================
    # HTTP Helpers
    # =========================================================================
    
    async def _get(self, path: str) -> Optional[dict]:
        """Make a GET request."""
        try:
            await self._ensure_session()
            async with self._session.get(f"{self.base_url}{path}") as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    _LOG.warning(f"GET {path} returned {resp.status}")
                    return None
        except Exception as e:
            _LOG.error(f"GET {path} failed: {e}")
            return None
    
    async def _post(self, path: str, json: dict = None) -> Optional[dict]:
        """Make a POST request."""
        try:
            await self._ensure_session()
            async with self._session.post(f"{self.base_url}{path}", json=json) as resp:
                if resp.status in (200, 201):
                    return await resp.json()
                else:
                    _LOG.warning(f"POST {path} returned {resp.status}")
                    try:
                        error = await resp.json()
                        return error
                    except:
                        return {"success": False, "error": f"HTTP {resp.status}"}
        except Exception as e:
            _LOG.error(f"POST {path} failed: {e}")
            return None
    
    async def _delete(self, path: str) -> Optional[dict]:
        """Make a DELETE request."""
        try:
            await self._ensure_session()
            async with self._session.delete(f"{self.base_url}{path}") as resp:
                if resp.status in (200, 204):
                    if resp.content_length and resp.content_length > 0:
                        return await resp.json()
                    return {"success": True}
                else:
                    _LOG.warning(f"DELETE {path} returned {resp.status}")
                    return None
        except Exception as e:
            _LOG.error(f"DELETE {path} failed: {e}")
            return None
