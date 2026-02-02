"""
OREI BK-808 HDMI Matrix control library.

Hybrid HTTP/Telnet control architecture:
- HTTP: Authentication, routing changes, naming, EDID/video settings, presets
- Telnet: CEC commands (faster), input cable detection, bulk status queries

HTTP API: POST to /cgi-bin/instr with JSON payload
Telnet: Port 23, commands end with !\\r\\n
"""

import asyncio
import json
import logging
import os
import random
from enum import IntEnum
from typing import Any, Optional

import aiohttp
from pyee.asyncio import AsyncIOEventEmitter

# Import Telnet client for CEC and cable detection
try:
    from .telnet_client import TelnetClient, TelnetState, MatrixStatus
except ImportError:
    from telnet_client import TelnetClient, TelnetState, MatrixStatus

_LOG = logging.getLogger(__name__)

# Connection retry configuration
MAX_RETRIES = int(os.environ.get("OREI_MAX_RETRIES", "5"))
INITIAL_RETRY_DELAY = float(os.environ.get("OREI_RETRY_DELAY", "1.0"))
MAX_RETRY_DELAY = float(os.environ.get("OREI_MAX_RETRY_DELAY", "60.0"))
RETRY_JITTER = 0.1  # 10% jitter to prevent thundering herd


class Events(IntEnum):
    """Internal OREI Matrix events."""

    CONNECTED = 0
    DISCONNECTED = 1
    ERROR = 2
    UPDATE = 3
    RECONNECTING = 4  # New event for reconnection attempts


class OreiMatrix:
    """Representing an OREI BK-808 HDMI Matrix device."""

    def __init__(self, host: str, port: int = 443, use_https: bool = True):
        """
        Initialize the OREI Matrix device.

        :param host: IP address of the matrix
        :param port: Port (default 443 for HTTPS)
        :param use_https: Use HTTPS instead of HTTP (default True)
        """
        self.host = host
        self.port = port
        self.use_https = use_https
        self._session: Optional[aiohttp.ClientSession] = None
        self._connected = False
        self.events = AsyncIOEventEmitter()

        # Device state
        self._current_scene: int | None = None
        self._last_error: str | None = None
        
        # Retry state
        self._retry_count = 0
        self._reconnect_task: Optional[asyncio.Task] = None
        
        # Telnet client for CEC commands and cable detection
        self._telnet: Optional[TelnetClient] = None
        self._telnet_port = int(os.environ.get("OREI_TELNET_PORT", "23"))
        self._use_telnet_cec = os.environ.get("OREI_USE_TELNET_CEC", "false").lower() == "true"
        
        # CEC enabled status cache
        # inputindex/outputindex: 1 = CEC enabled, 0 = disabled
        self._cec_enabled_cache: dict[str, Any] = {
            'inputs': [False] * 8,
            'outputs': [False] * 8,
            'last_updated': None  # datetime when last fetched
        }
        self._cec_cache_ttl = 300  # 5 minutes cache TTL

    @property
    def connected(self) -> bool:
        """Return connection status."""
        return self._connected

    @property
    def telnet_connected(self) -> bool:
        """Return Telnet connection status."""
        return self._telnet is not None and self._telnet.connected

    @property
    def current_scene(self) -> int | None:
        """Return the currently active scene (1-8)."""
        return self._current_scene

    async def _connect_telnet(self) -> bool:
        """
        Connect to the matrix Telnet interface for CEC and cable detection.
        
        This is called automatically after HTTP authentication succeeds.
        Telnet failure is non-fatal - HTTP-only operation is supported.
        """
        if self._telnet and self._telnet.connected:
            return True
        
        try:
            _LOG.info(f"Connecting Telnet to {self.host}:{self._telnet_port}")
            self._telnet = TelnetClient(
                host=self.host,
                port=self._telnet_port,
                on_connection_change=self._on_telnet_state_change
            )
            
            if await self._telnet.connect():
                _LOG.info(f"Telnet connected (firmware: {self._telnet.firmware_version})")
                return True
            else:
                _LOG.warning("Telnet connection failed - CEC and cable detection will use HTTP fallback")
                self._telnet = None
                return False
                
        except Exception as e:
            _LOG.warning(f"Telnet connection error: {e} - falling back to HTTP-only mode")
            self._telnet = None
            return False

    def _on_telnet_state_change(self, state: TelnetState) -> None:
        """Handle Telnet connection state changes."""
        _LOG.info(f"Telnet state changed to: {state.value}")
        if state == TelnetState.DISCONNECTED:
            # Could trigger reconnect here if needed
            pass

    def _calculate_retry_delay(self, attempt: int) -> float:
        """
        Calculate retry delay with exponential backoff and jitter.
        
        :param attempt: Current retry attempt (0-indexed)
        :return: Delay in seconds
        """
        # Exponential backoff: delay = initial * 2^attempt
        delay = INITIAL_RETRY_DELAY * (2 ** attempt)
        # Cap at maximum delay
        delay = min(delay, MAX_RETRY_DELAY)
        # Add jitter (±10%) to prevent thundering herd
        jitter = delay * RETRY_JITTER * (2 * random.random() - 1)
        return delay + jitter

    async def connect_with_retry(self, max_retries: int = None) -> bool:
        """
        Connect to the OREI Matrix with exponential backoff retry.
        
        :param max_retries: Maximum retry attempts (None = use default)
        :return: True if connection successful
        """
        if max_retries is None:
            max_retries = MAX_RETRIES
            
        self._retry_count = 0
        
        while self._retry_count <= max_retries:
            if await self.connect():
                self._retry_count = 0
                return True
            
            if self._retry_count >= max_retries:
                _LOG.error(f"Failed to connect after {max_retries + 1} attempts")
                return False
            
            delay = self._calculate_retry_delay(self._retry_count)
            _LOG.warning(f"Connection failed, retrying in {delay:.1f}s (attempt {self._retry_count + 1}/{max_retries + 1})")
            self.events.emit(Events.RECONNECTING, self._retry_count + 1, max_retries + 1)
            
            await asyncio.sleep(delay)
            self._retry_count += 1
        
        return False

    async def connect(self) -> bool:
        """
        Connect to the OREI Matrix via HTTPS/HTTP and authenticate.

        :return: True if connection successful
        """
        try:
            protocol = "https" if self.use_https else "http"
            _LOG.info("Connecting to OREI Matrix at %s://%s:%d", protocol, self.host, self.port)
            
            # Create aiohttp session with cookie jar for session management
            # Disable SSL verification for self-signed certificates
            if not self._session:
                connector = aiohttp.TCPConnector(ssl=False) if self.use_https else None
                self._session = aiohttp.ClientSession(
                    cookie_jar=aiohttp.CookieJar(),
                    connector=connector
                )
            
            # Authenticate with login command
            # Credentials can be overridden via environment variables
            url = f"{protocol}://{self.host}:{self.port}/cgi-bin/instr"
            login_cmd = {
                "comhead": "login",
                "user": os.environ.get("OREI_USER", "Admin"),
                "password": os.environ.get("OREI_PASSWORD", "admin")
            }
            
            _LOG.debug("Authenticating with matrix...")
            async with self._session.post(
                url,
                json=login_cmd,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    try:
                        # Matrix returns text/plain, so read as text then parse JSON
                        text = await response.text()
                        _LOG.debug("Login response (raw): %s", text)
                        result = json.loads(text)
                        _LOG.debug("Login response (parsed): %s", result)
                        # Check if login was successful
                        if result.get("result") == 1 or result.get("comhead") == "login":
                            self._connected = True
                            self.events.emit(Events.CONNECTED)
                            _LOG.info("Successfully authenticated to OREI Matrix via HTTP")
                            
                            # Also connect Telnet for CEC and cable detection
                            await self._connect_telnet()
                            
                            return True
                        else:
                            _LOG.error("Login failed: %s", result)
                            self._last_error = "Authentication failed"
                            return False
                    except Exception as ex:
                        _LOG.error("Failed to parse login response: %s", ex)
                        return False
                else:
                    _LOG.warning("Login request returned status %d", response.status)
                    return False
                    
        except asyncio.TimeoutError:
            _LOG.error("Connection timeout to OREI Matrix at %s:%d", self.host, self.port)
            self._last_error = "Connection timeout"
            self.events.emit(Events.ERROR, "Connection timeout")
            return False
        except Exception as ex:
            _LOG.error("Failed to connect to OREI Matrix: %s", ex)
            self._last_error = str(ex)
            self.events.emit(Events.ERROR, str(ex))
            return False

    async def disconnect(self):
        """Disconnect from the OREI Matrix (both HTTP and Telnet)."""
        # Cancel any pending reconnect task
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass
            self._reconnect_task = None
        
        # Disconnect Telnet first
        if self._telnet:
            await self._telnet.disconnect()
            self._telnet = None
            
        if self._session:
            try:
                await self._session.close()
            except Exception as ex:
                _LOG.warning("Error closing session: %s", ex)
        self._connected = False
        self._session = None
        self.events.emit(Events.DISCONNECTED)
        _LOG.info("Disconnected from OREI Matrix")

    async def _send_command(self, command: dict, retry_on_failure: bool = True) -> tuple[bool, Optional[dict]]:
        """
        Send a JSON command to the matrix via HTTP POST.

        :param command: Command dictionary to send as JSON
        :param retry_on_failure: Whether to attempt reconnection on failure
        :return: Tuple of (success, response_dict)
        """
        if not self._session or not self._connected:
            _LOG.warning("No session or not connected, attempting to connect...")
            if retry_on_failure:
                if not await self.connect_with_retry(max_retries=2):
                    return False, None
            else:
                if not await self.connect():
                    return False, None

        try:
            protocol = "https" if self.use_https else "http"
            url = f"{protocol}://{self.host}:{self.port}/cgi-bin/instr"
            _LOG.debug("Sending %s POST to %s: %s", protocol.upper(), url, command)
            
            async with self._session.post(
                url,
                json=command,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    try:
                        # Matrix returns text/plain, so read as text then parse JSON
                        text = await response.text()
                        _LOG.debug("Command response (raw): %s", text)
                        response_data = json.loads(text)
                        _LOG.debug("Command response (parsed): %s", response_data)
                        return True, response_data
                    except Exception as ex:
                        _LOG.debug("Could not parse JSON response: %s", ex)
                        # Command sent successfully even if response parsing failed
                        return True, None
                else:
                    _LOG.warning("HTTP request failed with status %d", response.status)
                    # Mark as disconnected on HTTP error
                    self._connected = False
                    return False, None
                    
        except asyncio.TimeoutError:
            _LOG.error("Command timeout")
            self._last_error = "Command timeout"
            return False, None
        except Exception as ex:
            _LOG.error("Failed to send command '%s': %s", command, ex)
            self._last_error = str(ex)
            self.events.emit(Events.ERROR, str(ex))
            return False, None

    async def recall_scene(self, scene: int) -> bool:
        """
        Recall a preset using JSON protocol.

        :param scene: Preset number (1-8)
        :return: True if command sent successfully and confirmed
        """
        if scene < 1 or scene > 8:
            _LOG.error("Invalid preset number: %d. Must be 1-8", scene)
            return False

        _LOG.info("Recalling preset %d", scene)
        
        # OREI BK-808 uses JSON protocol
        # Command: {"comhead":"preset set","language":0,"index":<preset_num>}
        # Response: {"comhead":"preset set","result":1}
        command = {
            "comhead": "preset set",
            "language": 0,
            "index": scene
        }
        
        success, response = await self._send_command(command)
        
        if success:
            # Check if we got a valid response
            if response and response.get("result") == 1:
                _LOG.info("✓ Preset %d recalled successfully (confirmed by matrix)", scene)
                self._current_scene = scene
                self.events.emit(Events.UPDATE, {"scene": scene})
                return True
            elif response:
                _LOG.warning("Preset %d command sent but matrix returned result: %s", 
                           scene, response.get("result"))
                return False
            else:
                # No response but command sent - assume success
                _LOG.info("✓ Preset %d command sent (no response from matrix)", scene)
                self._current_scene = scene
                self.events.emit(Events.UPDATE, {"scene": scene})
                return True
        
        _LOG.error("Failed to recall preset %d", scene)
        return False

    async def recall_preset(self, preset: int) -> bool:
        """
        Recall a preset (alias for recall_scene).

        :param preset: Preset number (1-8)
        :return: True if command sent successfully
        """
        return await self.recall_scene(preset)

    async def get_preset_info(self, preset: int) -> Optional[dict]:
        """
        Get information about a specific preset.

        :param preset: Preset number (1-8)
        :return: Dictionary with preset info, or None if failed
        """
        if preset < 1 or preset > 8:
            _LOG.error("Invalid preset number: %d. Must be 1-8", preset)
            return None

        _LOG.debug("Getting info for preset %d", preset)
        
        # Command: {"comhead":"preset get","index":<preset_num>}
        command = {
            "comhead": "preset get",
            "index": preset
        }
        
        success, response = await self._send_command(command)
        
        if success and response:
            _LOG.debug("Preset %d info: %s", preset, response)
            return response
        
        _LOG.warning("Failed to get info for preset %d", preset)
        return None

    async def get_all_input_names(self) -> dict[int, str]:
        """
        Get names for all physical HDMI inputs (1-8).

        :return: Dictionary mapping input number to name
        """
        input_names = {}
        
        try:
            # Query all input names at once using "get video status"
            data = {"comhead": "get video status", "language": 0}
            success, response = await self._send_command(data)
            
            _LOG.debug(f"get_all_input_names success: {success}, response: {response}")
            
            if success and response and "allinputname" in response:
                raw_input_names = response["allinputname"]
                _LOG.info(f"Found {len(raw_input_names)} input names")
                
                # Parse each input name (format: "IN01-DeviceName")
                for idx, name in enumerate(raw_input_names):
                    input_num = idx + 1  # Convert 0-based index to 1-based input number
                    
                    if name and "-" in name:
                        # Extract device name after the dash
                        device_name = name.split("-", 1)[1].strip()
                        input_names[input_num] = device_name if device_name else f"Input {input_num}"
                    elif name:
                        # Use the name as-is if no dash
                        input_names[input_num] = name
                    else:
                        # Fallback for empty names
                        input_names[input_num] = f"Input {input_num}"
                
                _LOG.info(f"Parsed input names: {input_names}")
            else:
                # Fallback if command fails
                _LOG.warning(f"Failed to get video status (response={response}), using generic input names")
                for input_num in range(1, 9):
                    input_names[input_num] = f"Input {input_num}"
                    
        except Exception as e:
            _LOG.error(f"Error getting input names: {e}")
            # Fallback to generic names on error
            for input_num in range(1, 9):
                input_names[input_num] = f"Input {input_num}"
        
        return input_names

    async def save_scene(self, scene: int) -> bool:
        """
        Save current routing as a preset.
        
        DEPRECATED: Use save_preset() instead. This method is kept for
        backwards compatibility but now delegates to save_preset().

        :param scene: Preset number (1-8)
        :return: True if command sent successfully
        """
        _LOG.debug("save_scene() called - delegating to save_preset()")
        return await self.save_preset(scene)

    async def switch_input(self, input_num: int, output_num: int) -> bool:
        """
        Switch a specific input to a specific output.

        :param input_num: Input number (1-8)
        :param output_num: Output number (1-8)
        :return: True if command sent successfully
        """
        if input_num < 1 or input_num > 8:
            _LOG.error("Invalid input number: %d. Must be 1-8", input_num)
            return False
        
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False

        _LOG.info("Switching input %d to output %d", input_num, output_num)
        
        # OREI BK-808 uses JSON protocol for video switching
        # Command: {"comhead":"video switch","language":0,"source":[output, input]}
        # Response: {"comhead":"video switch","result":1}
        command = {
            "comhead": "video switch",
            "language": 0,
            "source": [output_num, input_num]
        }
        
        success, response = await self._send_command(command)
        
        if success:
            if response and response.get("result") == 1:
                _LOG.info("✓ Input %d switched to output %d (confirmed)", input_num, output_num)
                self.events.emit(Events.UPDATE, {"input": input_num, "output": output_num})
                return True
            else:
                _LOG.info("✓ Switch command sent (no confirmation)")
                self.events.emit(Events.UPDATE, {"input": input_num, "output": output_num})
                return True
        
        _LOG.error("Failed to switch input %d to output %d", input_num, output_num)
        return False

    async def switch_input_to_all(self, input_num: int) -> bool:
        """
        Switch a specific input to ALL outputs.

        :param input_num: Input number (1-8)
        :return: True if command sent successfully
        """
        if input_num < 1 or input_num > 8:
            _LOG.error("Invalid input number: %d. Must be 1-8", input_num)
            return False

        _LOG.info("Switching input %d to ALL outputs", input_num)
        
        # OREI BK-808 uses "video switch" command with source=[0, input] for routing to all outputs
        # The first element 0 means "all outputs", second element is the input number
        command = {
            "comhead": "video switch",
            "language": 0,
            "source": [0, input_num]
        }
        
        success, response = await self._send_command(command)
        
        if success:
            if response and response.get("result") == 1:
                _LOG.info("✓ Input %d switched to all outputs (confirmed)", input_num)
                self.events.emit(Events.UPDATE, {"input": input_num, "all_outputs": True})
                return True
            else:
                _LOG.info("✓ Switch all command sent (no confirmation)")
                self.events.emit(Events.UPDATE, {"input": input_num, "all_outputs": True})
                return True
        
        _LOG.error("Failed to switch input %d to all outputs", input_num)
        return False

    async def power_on(self) -> bool:
        """
        Turn the matrix power on.

        :return: True if command sent successfully
        """
        _LOG.info("Turning matrix power ON")
        
        # Command: {"comhead":"set poweronoff","language":0,"power":1}
        # Response: {"comhead":"set poweronoff","result":1}
        command = {
            "comhead": "set poweronoff",
            "language": 0,
            "power": 1
        }
        
        success, response = await self._send_command(command)
        
        if success and response and response.get("result") == 1:
            _LOG.info("✓ Matrix powered ON (confirmed)")
            self.events.emit(Events.UPDATE, {"power": "on"})
            return True
        
        _LOG.error("Failed to power on matrix")
        return False

    async def power_off(self) -> bool:
        """
        Turn the matrix power off (standby).

        :return: True if command sent successfully
        """
        _LOG.info("Turning matrix power OFF (standby)")
        
        # Command: {"comhead":"set poweronoff","language":0,"power":0}
        # Response: {"comhead":"set poweronoff","result":1}
        command = {
            "comhead": "set poweronoff",
            "language": 0,
            "power": 0
        }
        
        success, response = await self._send_command(command)
        
        if success and response and response.get("result") == 1:
            _LOG.info("✓ Matrix powered OFF (confirmed)")
            self.events.emit(Events.UPDATE, {"power": "off"})
            return True
        
        _LOG.error("Failed to power off matrix")
        return False

    async def get_video_status(self) -> Optional[dict[str, Any]]:
        """
        Get the current video status including power state, routing, and names.

        :return: Dictionary with video status or None if failed
        Returns:
            - power: 1 (on) or 0 (off)
            - allsource: array of input numbers routed to each output [out1_input, out2_input, ...]
            - allinputname: array of input names
            - alloutputname: array of output names
            - allname: array of preset names
        """
        _LOG.debug("Getting video status")
        
        # Command: {"comhead":"get video status","language":0}
        command = {
            "comhead": "get video status",
            "language": 0
        }
        
        success, response = await self._send_command(command)
        
        if success and response:
            _LOG.debug("Video status: %s", response)
            return response
        
        _LOG.error("Failed to get video status")
        return None

    async def get_status(self) -> dict[str, Any]:
        """
        Get the current status of the matrix.

        :return: Dictionary with status information
        """
        # Get detailed video status from matrix
        video_status = await self.get_video_status()
        
        status = {
            "connected": self._connected,
            "host": self.host,
            "port": self.port,
            "current_scene": self._current_scene,
            "last_error": self._last_error,
        }
        
        if video_status:
            status.update({
                "power": "on" if video_status.get("power") == 1 else "off",
                "routing": video_status.get("allsource", []),
                "input_names": video_status.get("allinputname", []),
                "output_names": video_status.get("alloutputname", []),
                "preset_names": video_status.get("allname", []),
            })
        
        return status

    # =========================================================================
    # CEC Control Methods
    # =========================================================================
    
    # CEC Command Index Mapping for HTTP API (verified from HAR capture)
    CEC_POWER_ON = 1
    CEC_POWER_OFF = 2
    CEC_UP = 3
    CEC_LEFT = 4
    CEC_SELECT = 5
    CEC_RIGHT = 6
    CEC_MENU = 7
    CEC_DOWN = 8
    CEC_BACK = 9
    CEC_PREVIOUS = 10
    CEC_PLAY = 11
    CEC_NEXT = 12
    CEC_REWIND = 13
    CEC_PAUSE = 14
    CEC_FAST_FORWARD = 15
    CEC_STOP = 16
    CEC_MUTE = 17
    CEC_VOLUME_DOWN = 18
    CEC_VOLUME_UP = 19
    
    # Unified CEC command registry: command name -> (index, description)
    # This eliminates the need for separate input/output method mappings
    CEC_COMMAND_MAP: dict[str, int] = {
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
    
    # CEC Command mapping: HTTP index -> Telnet command string
    _CEC_INDEX_TO_TELNET = {
        1: "on",        # POWER_ON
        2: "off",       # POWER_OFF
        3: "up",        # UP
        4: "left",      # LEFT
        5: "enter",     # SELECT
        6: "right",     # RIGHT
        7: "menu",      # MENU
        8: "down",      # DOWN
        9: "back",      # BACK
        10: "previous", # PREVIOUS
        11: "play",     # PLAY
        12: "next",     # NEXT
        13: "rew",      # REWIND
        14: "pause",    # PAUSE
        15: "ff",       # FAST_FORWARD
        16: "stop",     # STOP
        17: "mute",     # MUTE
        18: "vol-",     # VOLUME_DOWN
        19: "vol+",     # VOLUME_UP
    }

    async def send_cec(self, command: str, port: int, is_output: bool = False) -> bool:
        """
        Send a CEC command by name to an input or output device.
        
        This is the unified CEC interface that accepts command names from the
        CEC_COMMAND_MAP. Use this instead of the individual cec_input_* and
        cec_output_* methods.
        
        :param command: Command name (e.g., "POWER_ON", "VOLUME_UP", "PLAY")
        :param port: Port number (1-8)
        :param is_output: True for output device (TV), False for input device (source)
        :return: True if command sent successfully
        
        Example:
            await matrix.send_cec("POWER_ON", 1, is_output=True)  # Turn on TV 1
            await matrix.send_cec("PLAY", 3, is_output=False)    # Play on source 3
        """
        command_index = self.CEC_COMMAND_MAP.get(command.upper())
        if command_index is None:
            _LOG.error("Unknown CEC command: %s. Valid commands: %s", 
                      command, list(self.CEC_COMMAND_MAP.keys()))
            return False
        
        return await self._send_cec_command(port, command_index, is_output)

    async def _send_cec_command(self, port_num: int, command_index: int, is_output: bool = False) -> bool:
        """
        Send a CEC command to an input or output device.
        
        Uses Telnet when available (faster), falls back to HTTP.
        Automatically ensures CEC is enabled on the target port before sending.

        :param port_num: Port number (1-8)
        :param command_index: CEC command index (1-19)
        :param is_output: True for output device (TV), False for input device (source)
        :return: True if command sent successfully
        """
        if port_num < 1 or port_num > 8:
            _LOG.error("Invalid port number: %d. Must be 1-8", port_num)
            return False
        
        if command_index < 1 or command_index > 19:
            _LOG.error("Invalid CEC command index: %d. Must be 1-19", command_index)
            return False
        
        # Ensure CEC is enabled on the target port (auto-enables if needed)
        cec_enabled = await self.ensure_cec_enabled(port_num, is_output)
        if not cec_enabled:
            _LOG.warning("Could not ensure CEC enabled on %s %d, attempting command anyway",
                        "output" if is_output else "input", port_num)
        
        # Try Telnet first (faster, persistent connection)
        if self._use_telnet_cec and self._telnet and self._telnet.connected:
            telnet_cmd = self._CEC_INDEX_TO_TELNET.get(command_index)
            if telnet_cmd:
                try:
                    if is_output:
                        success = await self._telnet._send_cec_output(port_num, telnet_cmd)
                    else:
                        success = await self._telnet._send_cec_input(port_num, telnet_cmd)
                    
                    if success:
                        _LOG.debug("CEC via Telnet: %s %d -> %s", 
                                   "output" if is_output else "input", port_num, telnet_cmd)
                        return True
                except Exception as e:
                    _LOG.warning(f"Telnet CEC failed, falling back to HTTP: {e}")
        
        # Fall back to HTTP
        _LOG.debug("CEC via HTTP: %s %d -> index %d", 
                   "output" if is_output else "input", port_num, command_index)

        # Build port array - all zeros except the target port
        port_array = [0] * 8
        port_array[port_num - 1] = 1  # Set the target port to 1

        # object: 0 = input device, 1 = output device
        object_type = 1 if is_output else 0

        command = {
            "comhead": "cec command",
            "language": 0,
            "object": object_type,
            "port": port_array,
            "index": command_index
        }

        _LOG.debug("Sending CEC command: %s", command)
        success, response = await self._send_command(command)
        
        if success:
            _LOG.info("✓ CEC command %d sent to %s %d", 
                     command_index, "output" if is_output else "input", port_num)
            return True
        
        _LOG.error("Failed to send CEC command %d to %s %d", 
                  command_index, "output" if is_output else "input", port_num)
        return False

    # Input CEC Control Methods (for source devices like PS3, Apple TV, etc.)
    
    async def cec_input_power_on(self, input_num: int) -> bool:
        """Send Power On CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_POWER_ON, is_output=False)

    async def cec_input_power_off(self, input_num: int) -> bool:
        """Send Power Off CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_POWER_OFF, is_output=False)

    async def cec_input_up(self, input_num: int) -> bool:
        """Send Up navigation CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_UP, is_output=False)

    async def cec_input_down(self, input_num: int) -> bool:
        """Send Down navigation CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_DOWN, is_output=False)

    async def cec_input_left(self, input_num: int) -> bool:
        """Send Left navigation CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_LEFT, is_output=False)

    async def cec_input_right(self, input_num: int) -> bool:
        """Send Right navigation CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_RIGHT, is_output=False)

    async def cec_input_select(self, input_num: int) -> bool:
        """Send Select/Enter CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_SELECT, is_output=False)

    async def cec_input_menu(self, input_num: int) -> bool:
        """Send Menu CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_MENU, is_output=False)

    async def cec_input_back(self, input_num: int) -> bool:
        """Send Back/Return CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_BACK, is_output=False)

    async def cec_input_play(self, input_num: int) -> bool:
        """Send Play CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_PLAY, is_output=False)

    async def cec_input_pause(self, input_num: int) -> bool:
        """Send Pause CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_PAUSE, is_output=False)

    async def cec_input_stop(self, input_num: int) -> bool:
        """Send Stop CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_STOP, is_output=False)

    async def cec_input_previous(self, input_num: int) -> bool:
        """Send Previous CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_PREVIOUS, is_output=False)

    async def cec_input_next(self, input_num: int) -> bool:
        """Send Next CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_NEXT, is_output=False)

    async def cec_input_rewind(self, input_num: int) -> bool:
        """Send Rewind CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_REWIND, is_output=False)

    async def cec_input_fast_forward(self, input_num: int) -> bool:
        """Send Fast Forward CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_FAST_FORWARD, is_output=False)

    async def cec_input_volume_up(self, input_num: int) -> bool:
        """Send Volume Up CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_VOLUME_UP, is_output=False)

    async def cec_input_volume_down(self, input_num: int) -> bool:
        """Send Volume Down CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_VOLUME_DOWN, is_output=False)

    async def cec_input_mute(self, input_num: int) -> bool:
        """Send Mute CEC command to an input device."""
        return await self._send_cec_command(input_num, self.CEC_MUTE, is_output=False)

    # Output CEC Control Methods (for TVs/displays)
    
    async def cec_output_power_on(self, output_num: int) -> bool:
        """Send Power On CEC command to an output device (TV)."""
        return await self._send_cec_command(output_num, self.CEC_POWER_ON, is_output=True)

    async def cec_output_power_off(self, output_num: int) -> bool:
        """Send Power Off CEC command to an output device (TV)."""
        return await self._send_cec_command(output_num, self.CEC_POWER_OFF, is_output=True)

    async def cec_output_up(self, output_num: int) -> bool:
        """Send Up navigation CEC command to an output device."""
        return await self._send_cec_command(output_num, self.CEC_UP, is_output=True)

    async def cec_output_down(self, output_num: int) -> bool:
        """Send Down navigation CEC command to an output device."""
        return await self._send_cec_command(output_num, self.CEC_DOWN, is_output=True)

    async def cec_output_left(self, output_num: int) -> bool:
        """Send Left navigation CEC command to an output device."""
        return await self._send_cec_command(output_num, self.CEC_LEFT, is_output=True)

    async def cec_output_right(self, output_num: int) -> bool:
        """Send Right navigation CEC command to an output device."""
        return await self._send_cec_command(output_num, self.CEC_RIGHT, is_output=True)

    async def cec_output_select(self, output_num: int) -> bool:
        """Send Select/Enter CEC command to an output device."""
        return await self._send_cec_command(output_num, self.CEC_SELECT, is_output=True)

    async def cec_output_menu(self, output_num: int) -> bool:
        """Send Menu CEC command to an output device."""
        return await self._send_cec_command(output_num, self.CEC_MENU, is_output=True)

    async def cec_output_back(self, output_num: int) -> bool:
        """Send Back/Return CEC command to an output device."""
        return await self._send_cec_command(output_num, self.CEC_BACK, is_output=True)

    async def cec_output_volume_up(self, output_num: int) -> bool:
        """Send Volume Up CEC command to an output device."""
        return await self._send_cec_command(output_num, self.CEC_VOLUME_UP, is_output=True)

    async def cec_output_volume_down(self, output_num: int) -> bool:
        """Send Volume Down CEC command to an output device."""
        return await self._send_cec_command(output_num, self.CEC_VOLUME_DOWN, is_output=True)

    async def cec_output_mute(self, output_num: int) -> bool:
        """Send Mute CEC command to an output device."""
        return await self._send_cec_command(output_num, self.CEC_MUTE, is_output=True)

    # =========================================================================
    # Extended Status Methods (discovered from HAR capture)
    # =========================================================================

    async def get_output_status(self) -> Optional[dict[str, Any]]:
        """
        Get detailed output/display status including connection detection.

        :return: Dictionary with output status or None if failed
        Returns:
            - power: 1 (on) or 0 (off)
            - allconnect: array showing which outputs have displays connected [1,1,0,0,0,0,0,0]
            - name: array of output names
            - allscaler: scaler settings per output
            - allhdr: HDR settings per output
            - allhdcp: HDCP version per output (3 = auto)
            - allarc: ARC enabled per output
            - allout: output enabled per output
            - allaudiomute: audio mute per output
        """
        _LOG.debug("Getting output status")
        
        command = {"comhead": "get output status", "language": 0}
        success, response = await self._send_command(command)
        
        if success and response:
            _LOG.debug("Output status: %s", response)
            return response
        
        _LOG.error("Failed to get output status")
        return None

    async def get_input_status(self) -> Optional[dict[str, Any]]:
        """
        Get detailed input status including signal detection.

        :return: Dictionary with input status or None if failed
        Returns:
            - power: 1 (on) or 0 (off)
            - edid: EDID mode per input
            - inactive: array showing inactive inputs (signal detection)
            - inname: array of input names
        """
        _LOG.debug("Getting input status")
        
        command = {"comhead": "get input status", "language": 0}
        success, response = await self._send_command(command)
        
        if success and response:
            _LOG.debug("Input status: %s", response)
            return response
        
        _LOG.error("Failed to get input status")
        return None

    # =========================================================================
    # Cable Detection Methods (via Telnet)
    # =========================================================================

    async def get_input_cable_status(self, input_num: int) -> Optional[bool]:
        """
        Check if a cable is connected to an input port.
        
        This uses Telnet 'r link in x!' command which can detect cable presence
        even without an active signal.
        
        :param input_num: Input port number (1-8)
        :return: True if cable connected, False if not, None if unable to determine
        """
        if input_num < 1 or input_num > 8:
            _LOG.error("Invalid input number: %d. Must be 1-8", input_num)
            return None
        
        if self._telnet and self._telnet.connected:
            try:
                return await self._telnet.get_input_connection(input_num)
            except Exception as e:
                _LOG.warning(f"Failed to get input cable status via Telnet: {e}")
        
        # No Telnet - cannot determine cable status (only signal via HTTP)
        _LOG.debug("Telnet not available for input cable detection")
        return None

    async def get_output_cable_status(self, output_num: int) -> Optional[bool]:
        """
        Check if a cable is connected to an output port.
        
        Uses Telnet when available, falls back to HTTP 'allconnect' array.
        
        :param output_num: Output port number (1-8)
        :return: True if cable connected, False if not, None if unable to determine
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return None
        
        # Try Telnet first
        if self._telnet and self._telnet.connected:
            try:
                return await self._telnet.get_output_connection(output_num)
            except Exception as e:
                _LOG.warning(f"Failed to get output cable status via Telnet: {e}")
        
        # Fall back to HTTP
        status = await self.get_output_status()
        if status and "allconnect" in status:
            try:
                return status["allconnect"][output_num - 1] == 1
            except (IndexError, TypeError):
                pass
        
        return None

    async def get_all_cable_status(self) -> dict[str, dict[int, bool]]:
        """
        Get cable connection status for all inputs and outputs.
        
        Queries each port individually via Telnet for accurate detection,
        falling back to HTTP for outputs if Telnet unavailable.
        
        :return: Dict with 'inputs' and 'outputs' sub-dicts mapping port -> connected
        """
        result = {
            "inputs": {},
            "outputs": {}
        }
        
        # Try Telnet individual queries for accuracy
        if self._telnet and self._telnet.connected:
            try:
                # Query each input individually
                result["inputs"] = await self._telnet.get_all_input_connections()
                # Query each output individually  
                result["outputs"] = await self._telnet.get_all_output_connections()
                return result
            except Exception as e:
                _LOG.warning(f"Failed to get cable status via Telnet: {e}")
        
        # Fall back to HTTP for outputs only (inputs not available via HTTP)
        output_status = await self.get_output_status()
        if output_status and "allconnect" in output_status:
            for i, connected in enumerate(output_status["allconnect"]):
                result["outputs"][i + 1] = (connected == 1)
        
        # Inputs: cannot determine via HTTP
        for i in range(1, 9):
            result["inputs"][i] = None
        
        return result

    async def get_telnet_full_status(self) -> Optional[MatrixStatus]:
        """
        Get comprehensive status via Telnet 'status!' command.
        
        Returns all device state in a single query including:
        - Power, beep, panel lock, LCD timeout
        - Input cable connections
        - Output cable connections
        - Routing (output -> input mapping)
        - HDCP, stream, video mode, HDR mode per output
        - ARC and audio mute per output
        - EDID per input
        
        :return: MatrixStatus dataclass or None if Telnet unavailable
        """
        if not self._telnet or not self._telnet.connected:
            _LOG.debug("Telnet not available for full status query")
            return None
        
        try:
            return await self._telnet.get_full_status()
        except Exception as e:
            _LOG.warning(f"Failed to get Telnet full status: {e}")
            return None

    async def get_cec_status(self) -> Optional[dict[str, Any]]:
        """
        Get CEC configuration status showing which ports have CEC enabled.

        :return: Dictionary with CEC status or None if failed
        Returns:
            - power: 1 (on) or 0 (off)
            - allinputname: array of input names
            - alloutputname: array of output names
            - inputindex: array showing CEC enabled per input [0,1,0,0,0,0,0,0]
            - outputindex: array showing CEC enabled per output [1,0,0,0,0,0,0,0]
        """
        _LOG.debug("Getting CEC status")
        
        command = {"comhead": "get cec status", "language": 0}
        success, response = await self._send_command(command)
        
        if success and response:
            _LOG.debug("CEC status: %s", response)
            # Update cache from response
            self._update_cec_cache(response)
            return response
        
        _LOG.error("Failed to get CEC status")
        return None
    
    def _update_cec_cache(self, cec_status: dict) -> None:
        """
        Update the CEC enabled cache from a get cec status response.
        
        :param cec_status: Response from get cec status command
        """
        import datetime
        
        if 'inputindex' in cec_status:
            for i, val in enumerate(cec_status['inputindex'][:8]):
                self._cec_enabled_cache['inputs'][i] = val == 1
        
        if 'outputindex' in cec_status:
            for i, val in enumerate(cec_status['outputindex'][:8]):
                self._cec_enabled_cache['outputs'][i] = val == 1
        
        self._cec_enabled_cache['last_updated'] = datetime.datetime.now()
        _LOG.debug("CEC cache updated: inputs=%s, outputs=%s", 
                   self._cec_enabled_cache['inputs'], 
                   self._cec_enabled_cache['outputs'])
    
    def _is_cec_cache_valid(self) -> bool:
        """
        Check if the CEC cache is still valid (not expired).
        
        :return: True if cache is valid and fresh
        """
        import datetime
        
        if self._cec_enabled_cache['last_updated'] is None:
            return False
        
        age = (datetime.datetime.now() - self._cec_enabled_cache['last_updated']).total_seconds()
        return age < self._cec_cache_ttl
    
    def is_cec_enabled(self, port_num: int, is_output: bool = False) -> Optional[bool]:
        """
        Check if CEC is enabled on a specific port from cache.
        
        :param port_num: Port number (1-8)
        :param is_output: True for output, False for input
        :return: True/False from cache, or None if cache is stale
        """
        if not self._is_cec_cache_valid():
            return None
        
        if port_num < 1 or port_num > 8:
            return None
        
        cache_key = 'outputs' if is_output else 'inputs'
        return self._cec_enabled_cache[cache_key][port_num - 1]
    
    async def refresh_cec_status(self) -> bool:
        """
        Refresh the CEC enabled status cache from the device.
        
        :return: True if refresh succeeded
        """
        result = await self.get_cec_status()
        return result is not None
    
    async def ensure_cec_enabled(self, port_num: int, is_output: bool = False) -> bool:
        """
        Ensure CEC is enabled on a specific port, enabling it if necessary.
        
        This method checks the cache first, refreshes if stale, and only
        enables CEC on the port if it's currently disabled.
        
        :param port_num: Port number (1-8)
        :param is_output: True for output, False for input
        :return: True if CEC is now enabled (or was already enabled)
        """
        if port_num < 1 or port_num > 8:
            _LOG.error("Invalid port number: %d", port_num)
            return False
        
        # Check cache, refresh if stale
        is_enabled = self.is_cec_enabled(port_num, is_output)
        if is_enabled is None:
            _LOG.debug("CEC cache stale, refreshing...")
            if not await self.refresh_cec_status():
                _LOG.warning("Failed to refresh CEC status, proceeding anyway")
                # Proceed without knowing - let the command try
                return True
            is_enabled = self.is_cec_enabled(port_num, is_output)
        
        if is_enabled:
            _LOG.debug("CEC already enabled on %s %d", "output" if is_output else "input", port_num)
            return True
        
        # CEC not enabled - enable it
        _LOG.info("Auto-enabling CEC on %s %d", "output" if is_output else "input", port_num)
        return await self.set_cec_enabled(port_num, True, is_output)
    
    async def set_cec_enabled(self, port_num: int, enabled: bool, is_output: bool = False) -> bool:
        """
        Enable or disable CEC on a specific port.
        
        This sends the 'set cec index' command which updates CEC enable state
        for all ports at once. We preserve other ports' states.
        
        :param port_num: Port number (1-8)
        :param enabled: True to enable, False to disable
        :param is_output: True for output, False for input
        :return: True if successful
        """
        if port_num < 1 or port_num > 8:
            _LOG.error("Invalid port number: %d", port_num)
            return False
        
        # Ensure we have current state
        if not self._is_cec_cache_valid():
            await self.refresh_cec_status()
        
        # Build the new arrays preserving existing state
        input_array = [1 if self._cec_enabled_cache['inputs'][i] else 0 for i in range(8)]
        output_array = [1 if self._cec_enabled_cache['outputs'][i] else 0 for i in range(8)]
        
        # Update the target port
        if is_output:
            output_array[port_num - 1] = 1 if enabled else 0
        else:
            input_array[port_num - 1] = 1 if enabled else 0
        
        # Send the command
        command = {
            "comhead": "set cec index",
            "language": 0,
            "inputindex": input_array,
            "outputindex": output_array
        }
        
        _LOG.debug("Setting CEC index: %s", command)
        success, response = await self._send_command(command)
        
        if success:
            # Update cache immediately
            if is_output:
                self._cec_enabled_cache['outputs'][port_num - 1] = enabled
            else:
                self._cec_enabled_cache['inputs'][port_num - 1] = enabled
            
            _LOG.info("✓ CEC %s on %s %d", 
                      "enabled" if enabled else "disabled",
                      "output" if is_output else "input", 
                      port_num)
            return True
        
        _LOG.error("Failed to set CEC enabled on %s %d", 
                   "output" if is_output else "input", port_num)
        return False

    async def get_ext_audio_status(self) -> Optional[dict[str, Any]]:
        """
        Get external audio routing status.

        :return: Dictionary with audio status or None if failed
        Returns:
            - power: 1 (on) or 0 (off)
            - mode: audio mode (0 = follow video, etc.)
            - allsource: audio source per output
            - allout: audio output enabled per output
            - allinputname: array of input names
            - alloutputname: array of output names
            - index: current audio index
        """
        _LOG.debug("Getting ext-audio status")
        
        command = {"comhead": "get ext-audio status", "language": 0}
        success, response = await self._send_command(command)
        
        if success and response:
            _LOG.debug("Ext-audio status: %s", response)
            return response
        
        _LOG.error("Failed to get ext-audio status")
        return None

    async def get_system_status(self) -> Optional[dict[str, Any]]:
        """
        Get system settings status.

        :return: Dictionary with system status or None if failed
        Returns:
            - power: 1 (on) or 0 (off)
            - baudrate: serial baud rate setting
            - beep: beep enabled (0/1)
            - lock: panel lock enabled (0/1)
            - mode: system mode
        """
        _LOG.debug("Getting system status")
        
        command = {"comhead": "get system status", "language": 0}
        success, response = await self._send_command(command)
        
        if success and response:
            _LOG.debug("System status: %s", response)
            return response
        
        _LOG.error("Failed to get system status")
        return None

    async def get_network_info(self) -> Optional[dict[str, Any]]:
        """
        Get network configuration.

        :return: Dictionary with network info or None if failed
        Returns:
            - power: 1 (on) or 0 (off)
            - dhcp: DHCP enabled (0/1)
            - ipaddress: current IP address
            - subnet: subnet mask
            - gateway: gateway address
            - telnetport: telnet port
            - tcpport: TCP port
            - macaddress: MAC address
            - hostname: device hostname
            - username: username setting
            - model: device model (e.g., "BK-808")
        """
        _LOG.debug("Getting network info")
        
        command = {"comhead": "get network", "language": 0}
        success, response = await self._send_command(command)
        
        if success and response:
            _LOG.debug("Network info: %s", response)
            return response
        
        _LOG.error("Failed to get network info")
        return None

    async def get_device_info(self) -> Optional[dict[str, Any]]:
        """
        Get device/firmware information.

        :return: Dictionary with device info or None if failed
        Returns:
            - power: 1 (on) or 0 (off)
            - version: firmware version (e.g., "V1.10.01")
            - hostname: device hostname
            - ipaddress: IP address
            - subnet: subnet mask
            - gateway: gateway address
            - macaddress: MAC address
            - model: device model (e.g., "BK-808")
            - webversion: web interface version (e.g., "V2.00.03")
        """
        _LOG.debug("Getting device info")
        
        command = {"comhead": "get status", "language": 0}
        success, response = await self._send_command(command)
        
        if success and response:
            _LOG.debug("Device info: %s", response)
            return response
        
        _LOG.error("Failed to get device info")
        return None

    # =========================================================================
    # System Control Methods
    # =========================================================================

    async def set_panel_lock(self, locked: bool) -> bool:
        """
        Lock or unlock the front panel controls.

        :param locked: True to lock, False to unlock
        :return: True if command succeeded
        """
        _LOG.info("Setting panel lock to: %s", "LOCKED" if locked else "UNLOCKED")
        
        command = {
            "comhead": "set panel lock",
            "language": 0,
            "lock": 1 if locked else 0
        }
        
        success, response = await self._send_command(command)
        
        if success and response and response.get("result") == 1:
            _LOG.info("✓ Panel lock set to: %s", "LOCKED" if locked else "UNLOCKED")
            self.events.emit(Events.UPDATE, {"panel_lock": locked})
            return True
        
        _LOG.error("Failed to set panel lock")
        return False

    async def set_beep(self, enabled: bool) -> bool:
        """
        Enable or disable the system beep sound.

        :param enabled: True to enable beep, False to disable
        :return: True if command succeeded
        """
        _LOG.info("Setting beep to: %s", "ON" if enabled else "OFF")
        
        command = {
            "comhead": "set beep",
            "language": 0,
            "beep": 1 if enabled else 0
        }
        
        success, response = await self._send_command(command)
        
        if success and response and response.get("result") == 1:
            _LOG.info("✓ Beep set to: %s", "ON" if enabled else "OFF")
            self.events.emit(Events.UPDATE, {"beep": enabled})
            return True
        
        _LOG.error("Failed to set beep")
        return False

    async def set_cec_enabled_bulk(self, input_ports: list[bool], output_ports: list[bool]) -> bool:
        """
        Configure which ports have CEC enabled (bulk update all ports at once).

        :param input_ports: List of 8 booleans for input CEC enable states
        :param output_ports: List of 8 booleans for output CEC enable states
        :return: True if command succeeded
        """
        if len(input_ports) != 8 or len(output_ports) != 8:
            _LOG.error("Must provide exactly 8 input and 8 output port states")
            return False
        
        _LOG.info("Setting CEC enabled - Inputs: %s, Outputs: %s", input_ports, output_ports)
        
        command = {
            "comhead": "set cec index",
            "language": 0,
            "inputindex": [1 if p else 0 for p in input_ports],
            "outputindex": [1 if p else 0 for p in output_ports]
        }
        
        success, response = await self._send_command(command)
        
        if success and response and response.get("result") == 1:
            _LOG.info("✓ CEC configuration updated")
            self.events.emit(Events.UPDATE, {"cec_config": {"inputs": input_ports, "outputs": output_ports}})
            return True
        
        _LOG.error("Failed to set CEC configuration")
        return False

    # =========================================================================
    # Comprehensive Status Method
    # =========================================================================

    async def get_full_status(self) -> dict[str, Any]:
        """
        Get comprehensive status from all status endpoints.
        
        :return: Dictionary with all status information combined
        """
        status = {
            "connected": self._connected,
            "host": self.host,
            "port": self.port,
        }
        
        # Get all status data in parallel
        video_status = await self.get_video_status()
        output_status = await self.get_output_status()
        input_status = await self.get_input_status()
        cec_status = await self.get_cec_status()
        system_status = await self.get_system_status()
        device_info = await self.get_device_info()
        
        if video_status:
            status["power"] = "on" if video_status.get("power") == 1 else "off"
            status["routing"] = video_status.get("allsource", [])
            status["input_names"] = video_status.get("allinputname", [])
            status["output_names"] = video_status.get("alloutputname", [])
            status["preset_names"] = video_status.get("allname", [])
        
        if output_status:
            status["outputs_connected"] = output_status.get("allconnect", [])
            status["output_scaler"] = output_status.get("allscaler", [])
            status["output_hdr"] = output_status.get("allhdr", [])
            status["output_hdcp"] = output_status.get("allhdcp", [])
            status["output_arc"] = output_status.get("allarc", [])
            status["output_enabled"] = output_status.get("allout", [])
            status["output_muted"] = output_status.get("allaudiomute", [])
        
        if input_status:
            status["input_edid"] = input_status.get("edid", [])
            status["inputs_inactive"] = input_status.get("inactive", [])
        
        if cec_status:
            status["cec_inputs_enabled"] = cec_status.get("inputindex", [])
            status["cec_outputs_enabled"] = cec_status.get("outputindex", [])
        
        if system_status:
            status["beep_enabled"] = system_status.get("beep") == 1
            status["panel_locked"] = system_status.get("lock") == 1
            status["system_mode"] = system_status.get("mode")
        
        if device_info:
            status["firmware_version"] = device_info.get("version")
            status["web_version"] = device_info.get("webversion")
            status["model"] = device_info.get("model")
            status["mac_address"] = device_info.get("macaddress")
        
        return status

    async def get_output_names(self) -> dict[int, str]:
        """
        Get names for all outputs (1-8).

        :return: Dictionary mapping output number to name
        """
        output_names = {}
        
        try:
            status = await self.get_video_status()
            
            if status and "alloutputname" in status:
                names = status["alloutputname"]
                for idx, name in enumerate(names):
                    output_names[idx + 1] = name if name else f"Output {idx + 1}"
            else:
                for i in range(1, 9):
                    output_names[i] = f"Output {i}"
        except Exception as e:
            _LOG.error(f"Error getting output names: {e}")
            for i in range(1, 9):
                output_names[i] = f"Output {i}"
        
        return output_names

    async def is_output_connected(self, output_num: int) -> Optional[bool]:
        """
        Check if an output has a display connected.

        :param output_num: Output number (1-8)
        :return: True if connected, False if not, None if unknown
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return None
        
        status = await self.get_output_status()
        
        if status and "allconnect" in status:
            connections = status["allconnect"]
            if len(connections) >= output_num:
                return connections[output_num - 1] == 1
        
        return None

    async def get_current_input_for_output(self, output_num: int) -> Optional[int]:
        """
        Get the currently selected input for a specific output.

        :param output_num: Output number (1-8)
        :return: Input number (1-8) or None if unknown
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return None
        
        status = await self.get_video_status()
        
        if status and "allsource" in status:
            routing = status["allsource"]
            if len(routing) >= output_num:
                return routing[output_num - 1]
        
        return None

    # =========================================================================
    # Port Name Methods
    # =========================================================================

    async def set_input_name(self, input_num: int, name: str) -> bool:
        """
        Set the name of an HDMI input port.
        
        :param input_num: Input number (1-8)
        :param name: New name for the input (max 32 chars)
        :return: True if command succeeded
        """
        if not 1 <= input_num <= 8:
            _LOG.error("Invalid input number: %d. Must be 1-8", input_num)
            return False
        
        if len(name) > 32:
            name = name[:32]
        
        _LOG.info("Setting input %d name to: %s", input_num, name)
        
        command = {
            "comhead": "set input name",
            "language": 0,
            "name": name,
            "index": input_num
        }
        
        success, response = await self._send_command(command)
        
        if success and response and response.get("result") == 1:
            _LOG.info("✓ Input %d renamed to: %s", input_num, name)
            self.events.emit(Events.UPDATE, {"input_name": {input_num: name}})
            return True
        
        _LOG.error("Failed to set input %d name", input_num)
        return False

    async def set_output_name(self, output_num: int, name: str) -> bool:
        """
        Set the name of an HDMI output port.
        
        :param output_num: Output number (1-8)
        :param name: New name for the output (max 32 chars)
        :return: True if command succeeded
        """
        if not 1 <= output_num <= 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False
        
        if len(name) > 32:
            name = name[:32]
        
        _LOG.info("Setting output %d name to: %s", output_num, name)
        
        command = {
            "comhead": "set output name",
            "language": 0,
            "name": name,
            "index": output_num
        }
        
        success, response = await self._send_command(command)
        
        if success and response and response.get("result") == 1:
            _LOG.info("✓ Output %d renamed to: %s", output_num, name)
            self.events.emit(Events.UPDATE, {"output_name": {output_num: name}})
            return True
        
        _LOG.error("Failed to set output %d name", output_num)
        return False

    # =========================================================================
    # ADVANCED OUTPUT CONTROL (from Control4/RTI drivers)
    # =========================================================================

    async def set_output_enable(self, output_num: int, enable: bool) -> bool:
        """
        Enable or disable video output stream for a specific output.
        
        :param output_num: Output number (1-8)
        :param enable: True to enable output, False to disable (blank)
        :return: True if command sent successfully
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False
        
        command = {
            "comhead": "set output stream",
            "output": output_num,
            "enable": 1 if enable else 0
        }
        
        action = "enable" if enable else "disable"
        _LOG.info(f"Setting output {output_num} stream to {action}")
        success, _ = await self._send_command(command)
        return success

    async def set_output_hdcp(self, output_num: int, mode: int) -> bool:
        """
        Set HDCP mode for a specific output.
        
        :param output_num: Output number (1-8)
        :param mode: HDCP mode (1=HDCP 1.4, 2=HDCP 2.2, 3=Follow Sink, 4=Follow Source, 5=User Mode)
        :return: True if command sent successfully
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False
        
        if mode < 1 or mode > 5:
            _LOG.error("Invalid HDCP mode: %d. Must be 1-5", mode)
            return False
        
        command = {
            "comhead": "set output hdcp",
            "output": output_num,
            "hdcp": mode
        }
        
        _LOG.info(f"Setting output {output_num} HDCP mode to {mode}")
        success, _ = await self._send_command(command)
        return success

    async def set_output_hdr(self, output_num: int, mode: int) -> bool:
        """
        Set HDR mode for a specific output.
        
        :param output_num: Output number (1-8)
        :param mode: HDR mode (1=Passthrough, 2=HDR to SDR, 3=Auto/follow sink EDID)
        :return: True if command sent successfully
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False
        
        if mode < 1 or mode > 3:
            _LOG.error("Invalid HDR mode: %d. Must be 1-3", mode)
            return False
        
        command = {
            "comhead": "set output hdr",
            "output": output_num,
            "hdr": mode
        }
        
        _LOG.info(f"Setting output {output_num} HDR mode to {mode}")
        success, _ = await self._send_command(command)
        return success

    async def set_output_scaler(self, output_num: int, mode: int) -> bool:
        """
        Set scaler/video mode for a specific output.
        
        :param output_num: Output number (1-8)
        :param mode: Scaler mode (1=Passthrough, 2=8K→4K, 3=8K/4K→1080p, 4=Auto, 5=Audio Only)
        :return: True if command sent successfully
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False
        
        if mode < 1 or mode > 5:
            _LOG.error("Invalid scaler mode: %d. Must be 1-5", mode)
            return False
        
        command = {
            "comhead": "set output scaler",
            "output": output_num,
            "scaler": mode
        }
        
        _LOG.info(f"Setting output {output_num} scaler mode to {mode}")
        success, _ = await self._send_command(command)
        return success

    async def set_output_arc(self, output_num: int, enable: bool) -> bool:
        """
        Enable or disable ARC (Audio Return Channel) for a specific output.
        
        :param output_num: Output number (1-8)
        :param enable: True to enable ARC, False to disable
        :return: True if command sent successfully
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False
        
        command = {
            "comhead": "set output arc",
            "output": output_num,
            "arc": 1 if enable else 0
        }
        
        action = "enable" if enable else "disable"
        _LOG.info(f"Setting output {output_num} ARC to {action}")
        success, _ = await self._send_command(command)
        return success

    async def set_output_audio_mute(self, output_num: int, mute: bool) -> bool:
        """
        Mute or unmute audio for a specific output.
        
        :param output_num: Output number (1-8)
        :param mute: True to mute, False to unmute
        :return: True if command sent successfully
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False
        
        command = {
            "comhead": "set output mute",
            "output": output_num,
            "mute": 1 if mute else 0
        }
        
        action = "mute" if mute else "unmute"
        _LOG.info(f"Setting output {output_num} audio to {action}")
        success, _ = await self._send_command(command)
        return success

    async def set_cec_enable(self, port_type: str, port_num: int, enable: bool) -> bool:
        """
        Enable or disable CEC for a specific input or output.
        
        :param port_type: "input" or "output"
        :param port_num: Port number (1-8)
        :param enable: True to enable CEC, False to disable
        :return: True if command sent successfully
        """
        if port_type not in ("input", "output"):
            _LOG.error("Invalid port type: %s. Must be 'input' or 'output'", port_type)
            return False
        
        if port_num < 1 or port_num > 8:
            _LOG.error("Invalid port number: %d. Must be 1-8", port_num)
            return False
        
        command = {
            "comhead": "set cec index",
            "port": port_type,
            "index": port_num,
            "enable": 1 if enable else 0
        }
        
        action = "enable" if enable else "disable"
        _LOG.info(f"Setting CEC on {port_type} {port_num} to {action}")
        success, _ = await self._send_command(command)
        return success

    async def save_preset(self, preset_num: int) -> bool:
        """
        Save the current routing configuration to a preset.
        
        :param preset_num: Preset number (1-8)
        :return: True if command sent successfully
        """
        if preset_num < 1 or preset_num > 8:
            _LOG.error("Invalid preset number: %d. Must be 1-8", preset_num)
            return False
        
        command = {
            "comhead": "preset save",
            "language": 0,
            "index": preset_num
        }
        
        _LOG.info(f"Saving current routing to preset {preset_num}")
        success, _ = await self._send_command(command)
        return success

    async def system_reboot(self) -> bool:
        """
        Reboot the OREI Matrix.
        
        :return: True if command sent (connection will be lost after reboot)
        """
        command = {"comhead": "set reboot"}
        
        _LOG.warning("Initiating system reboot...")
        success, _ = await self._send_command(command, retry_on_failure=False)
        
        if success:
            self._connected = False
            self.events.emit(Events.DISCONNECTED)
        
        return success

    # =========================================================================
    # LCD Display Settings
    # =========================================================================
    
    # LCD timeout mode values
    LCD_TIMEOUT_MODES = {
        0: "Off",
        1: "Always On",
        2: "15 seconds",
        3: "30 seconds",
        4: "60 seconds",
    }
    
    @classmethod
    def get_lcd_timeout_name(cls, mode: int) -> str:
        """Get human-readable name for an LCD timeout mode value."""
        return cls.LCD_TIMEOUT_MODES.get(mode, f"Unknown ({mode})")
    
    @classmethod
    def get_lcd_timeout_modes(cls) -> dict:
        """Get all available LCD timeout modes."""
        return cls.LCD_TIMEOUT_MODES.copy()
    
    async def set_lcd_timeout(self, mode: int) -> bool:
        """
        Set the LCD display timeout on the front panel.
        
        :param mode: Timeout mode:
            - 0: Off (LCD disabled)
            - 1: Always on
            - 2: 15 seconds
            - 3: 30 seconds
            - 4: 60 seconds
        :return: True if command sent successfully
        """
        if mode < 0 or mode > 4:
            _LOG.error("Invalid LCD timeout mode: %d. Must be 0-4", mode)
            return False
        
        # Command format from Control4 driver: "s lcd on time N"
        # JSON equivalent follows standard pattern
        command = {
            "comhead": "set lcd on time",
            "time": mode
        }
        
        mode_name = self.get_lcd_timeout_name(mode)
        _LOG.info(f"Setting LCD timeout to {mode} ({mode_name})")
        success, _ = await self._send_command(command)
        return success

    async def route_input_to_all_outputs(self, input_num: int) -> bool:
        """
        Route a single input to all outputs at once.
        
        :param input_num: Input number (1-8)
        :return: True if command sent successfully
        """
        if input_num < 1 or input_num > 8:
            _LOG.error("Invalid input number: %d. Must be 1-8", input_num)
            return False
        
        # Route to each output
        success = True
        for output in range(1, 9):
            if not await self.switch_input(input_num, output):
                success = False
        
        return success
    # =========================================================================
    # EDID Management
    # =========================================================================
    
    # EDID mode constants - maps human-readable names to API values
    # Values based on typical HDMI matrix EDID presets
    EDID_MODES = {
        1: "1080p 2CH",           # 1080p stereo audio
        2: "1080p 5.1CH",         # 1080p 5.1 surround
        3: "1080p 7.1CH",         # 1080p 7.1 surround
        4: "1080i",               # 1080i
        5: "3D",                  # 3D mode
        6: "4K30 2CH",            # 4K 30Hz stereo
        7: "4K30 5.1CH",          # 4K 30Hz 5.1 surround
        8: "4K30 7.1CH",          # 4K 30Hz 7.1 surround
        9: "4K60 2CH",            # 4K 60Hz stereo
        10: "4K60 5.1CH",         # 4K 60Hz 5.1 surround
        11: "4K60 7.1CH",         # 4K 60Hz 7.1 surround
        12: "4K60 4:4:4 2CH",     # 4K 60Hz 4:4:4 stereo
        13: "4K60 4:4:4 5.1CH",   # 4K 60Hz 4:4:4 5.1
        14: "4K60 4:4:4 7.1CH",   # 4K 60Hz 4:4:4 7.1
        15: "Copy Output 1",      # Copy EDID from output 1
        16: "Copy Output 2",      # Copy EDID from output 2
        17: "Copy Output 3",      # Copy EDID from output 3
        18: "Copy Output 4",      # Copy EDID from output 4
        19: "Copy Output 5",      # Copy EDID from output 5
        20: "Copy Output 6",      # Copy EDID from output 6
        21: "Copy Output 7",      # Copy EDID from output 7
        22: "Copy Output 8",      # Copy EDID from output 8
        # Additional HDR/Dolby modes typically at higher values
        33: "4K60 HDR 2CH",       # 4K 60Hz HDR stereo
        34: "4K60 HDR 5.1CH",     # 4K 60Hz HDR 5.1
        35: "4K60 HDR 7.1CH",     # 4K 60Hz HDR 7.1
        36: "4K60 HDR Atmos",     # 4K 60Hz HDR with Dolby Atmos (observed in HAR)
        37: "8K30",               # 8K 30Hz
        38: "8K60",               # 8K 60Hz
    }
    
    @classmethod
    def get_edid_mode_name(cls, mode_value: int) -> str:
        """Get human-readable name for an EDID mode value."""
        return cls.EDID_MODES.get(mode_value, f"Unknown ({mode_value})")
    
    @classmethod
    def get_edid_modes(cls) -> dict[int, str]:
        """Get all available EDID modes."""
        return cls.EDID_MODES.copy()
    
    async def get_edid_status(self) -> Optional[dict[str, Any]]:
        """
        Get current EDID settings for all inputs.
        
        :return: Dictionary with EDID status or None if failed
        Returns:
            - edid: array of EDID mode values per input (1-indexed)
            - edid_names: array of human-readable EDID mode names
        """
        input_status = await self.get_input_status()
        if not input_status:
            return None
        
        edid_values = input_status.get("edid", [])
        edid_names = [self.get_edid_mode_name(v) for v in edid_values]
        
        return {
            "edid": edid_values,
            "edid_names": edid_names,
            "inputs": {
                i + 1: {
                    "mode": edid_values[i] if i < len(edid_values) else None,
                    "mode_name": edid_names[i] if i < len(edid_names) else "Unknown"
                }
                for i in range(8)
            }
        }
    
    async def set_input_edid(self, input_num: int, mode: int) -> bool:
        """
        Set EDID mode for a specific input.
        
        :param input_num: Input number (1-8)
        :param mode: EDID mode value (see EDID_MODES for available values)
        :return: True if command sent successfully
        
        Common modes:
        - 1-14: Resolution/audio presets (1080p to 4K60 4:4:4)
        - 15-22: Copy from output 1-8
        - 33-36: HDR modes
        - 37-38: 8K modes
        """
        if input_num < 1 or input_num > 8:
            _LOG.error("Invalid input number: %d. Must be 1-8", input_num)
            return False
        
        if mode < 1:
            _LOG.error("Invalid EDID mode: %d. Must be >= 1", mode)
            return False
        
        # Command format follows the pattern of other settings
        command = {
            "comhead": "set input edid",
            "input": input_num,
            "edid": mode
        }
        
        mode_name = self.get_edid_mode_name(mode)
        _LOG.info(f"Setting input {input_num} EDID to {mode} ({mode_name})")
        success, _ = await self._send_command(command)
        return success
    
    async def copy_edid_from_output(self, input_num: int, output_num: int) -> bool:
        """
        Copy EDID from a connected display (output) to an input.
        
        This is useful when you want an input device to see the exact
        capabilities of a specific display.
        
        :param input_num: Input number (1-8) to receive the EDID
        :param output_num: Output number (1-8) to copy EDID from
        :return: True if command sent successfully
        """
        if input_num < 1 or input_num > 8:
            _LOG.error("Invalid input number: %d. Must be 1-8", input_num)
            return False
        
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False
        
        # Copy from output X uses mode values 15-22 (15 = output 1, etc.)
        mode = 14 + output_num
        return await self.set_input_edid(input_num, mode)

    # =========================================================================
    # External Audio (Ext-Audio) Matrix Control
    # =========================================================================
    
    # Ext-audio mode values
    EXT_AUDIO_MODES = {
        0: "Bind to Input",    # Audio follows video source (default)
        1: "Bind to Output",   # Audio follows output routing
        2: "Matrix Mode",      # Independent audio routing
    }
    
    @classmethod
    def get_ext_audio_mode_name(cls, mode: int) -> str:
        """Get human-readable name for an ext-audio mode value."""
        return cls.EXT_AUDIO_MODES.get(mode, f"Unknown ({mode})")
    
    @classmethod
    def get_ext_audio_modes(cls) -> dict:
        """Get all available ext-audio modes."""
        return cls.EXT_AUDIO_MODES.copy()
    
    async def get_ext_audio_status(self) -> Optional[dict]:
        """
        Get external audio matrix status.
        
        :return: Dict with ext-audio status including mode, sources, and enabled states
        """
        command = {"comhead": "get ext-audio status", "language": 0}
        success, response = await self._send_command(command)
        
        if success and response:
            return response
        return None
    
    async def set_ext_audio_mode(self, mode: int) -> bool:
        """
        Set the external audio routing mode.
        
        :param mode: Mode value:
            - 0: Bind to input (audio follows video source)
            - 1: Bind to output (audio follows output routing)
            - 2: Matrix mode (independent audio routing)
        :return: True if command sent successfully
        """
        if mode < 0 or mode > 2:
            _LOG.error("Invalid ext-audio mode: %d. Must be 0-2", mode)
            return False
        
        command = {
            "comhead": "set output exa mode",
            "mode": mode
        }
        
        mode_name = self.get_ext_audio_mode_name(mode)
        _LOG.info(f"Setting ext-audio mode to {mode} ({mode_name})")
        success, _ = await self._send_command(command)
        return success
    
    async def set_ext_audio_enable(self, output_num: int, enabled: bool) -> bool:
        """
        Enable or disable external audio output on a specific port.
        
        :param output_num: Output number (1-8)
        :param enabled: True to enable, False to disable
        :return: True if command sent successfully
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False
        
        # From Control4 driver: exa 1 = enable, exa 2 = disable
        command = {
            "comhead": "set output exa",
            "output": output_num,
            "exa": 1 if enabled else 2
        }
        
        state = "enabled" if enabled else "disabled"
        _LOG.info(f"Setting ext-audio output {output_num} to {state}")
        success, _ = await self._send_command(command)
        return success
    
    async def set_ext_audio_source(self, output_num: int, input_num: int) -> bool:
        """
        Route an input source to an external audio output.
        
        This only works when ext-audio mode is set to Matrix Mode (2).
        
        :param output_num: Ext-audio output number (1-8)
        :param input_num: Input source number (1-8)
        :return: True if command sent successfully
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False
        
        if input_num < 1 or input_num > 8:
            _LOG.error("Invalid input number: %d. Must be 1-8", input_num)
            return False
        
        command = {
            "comhead": "set output exa in source",
            "output": output_num,
            "input": input_num
        }
        
        _LOG.info(f"Setting ext-audio output {output_num} source to input {input_num}")
        success, _ = await self._send_command(command)
        return success

    # =========================================================================
    # Device Capability Detection (for CEC routing)
    # =========================================================================

    async def get_output_capabilities(self, output_num: int) -> Optional[dict[str, Any]]:
        """
        Get capabilities for a specific output device.
        
        Used for CEC routing decisions (audio_only, arc, cec_enabled).
        
        :param output_num: Output number (1-8)
        :return: Capabilities dict or None if failed
        """
        if output_num < 1 or output_num > 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return None
        
        # Fetch required status data
        output_status = await self.get_output_status()
        cec_status = await self.get_cec_status()
        
        if not output_status or not cec_status:
            _LOG.error("Failed to get status for capability detection")
            return None
        
        idx = output_num - 1  # Convert to 0-indexed
        
        allscaler = output_status.get("allscaler", [])
        allarc = output_status.get("allarc", [])
        allconnect = output_status.get("allconnect", [])
        allout = output_status.get("allout", [])
        alloutputname = output_status.get("alloutputname", [])
        
        cec_outputindex = cec_status.get("outputindex", [])
        
        scaler_value = allscaler[idx] if idx < len(allscaler) else 0
        
        # Scaler value 4 = Audio Only (0-indexed from matrix)
        is_audio_only = scaler_value == 4
        
        return {
            "output_num": output_num,
            "name": alloutputname[idx] if idx < len(alloutputname) else f"Output {output_num}",
            "connected": allconnect[idx] == 1 if idx < len(allconnect) else False,
            "stream_enabled": allout[idx] == 1 if idx < len(allout) else True,
            "is_audio_only": is_audio_only,
            "arc_enabled": allarc[idx] == 1 if idx < len(allarc) else False,
            "cec_enabled": cec_outputindex[idx] == 1 if idx < len(cec_outputindex) else False,
            "scaler_mode": scaler_value,
            "supported_cec_commands": [
                "POWER_ON", "POWER_OFF", "MUTE", 
                "VOLUME_UP", "VOLUME_DOWN", "ACTIVE"
            ],
        }

    async def get_input_capabilities(self, input_num: int) -> Optional[dict[str, Any]]:
        """
        Get capabilities for a specific input device.
        
        Used for CEC routing decisions.
        
        :param input_num: Input number (1-8)
        :return: Capabilities dict or None if failed
        """
        if input_num < 1 or input_num > 8:
            _LOG.error("Invalid input number: %d. Must be 1-8", input_num)
            return None
        
        # Fetch required status data
        input_status = await self.get_input_status()
        cec_status = await self.get_cec_status()
        
        if not input_status or not cec_status:
            _LOG.error("Failed to get status for capability detection")
            return None
        
        idx = input_num - 1  # Convert to 0-indexed
        
        inname = input_status.get("inname", [])
        inactive = input_status.get("inactive", [])
        
        cec_inputindex = cec_status.get("inputindex", [])
        
        return {
            "input_num": input_num,
            "name": inname[idx] if idx < len(inname) else f"Input {input_num}",
            "signal_detected": inactive[idx] == 1 if idx < len(inactive) else False,
            "cec_enabled": cec_inputindex[idx] == 1 if idx < len(cec_inputindex) else False,
            "supported_cec_commands": [
                "POWER_ON", "POWER_OFF", "UP", "DOWN", "LEFT", "RIGHT",
                "SELECT", "MENU", "BACK", "PLAY", "PAUSE", "STOP",
                "PREVIOUS", "NEXT", "REWIND", "FAST_FORWARD",
                "VOLUME_UP", "VOLUME_DOWN", "MUTE"
            ],
        }

    async def get_all_capabilities(self) -> Optional[dict[str, Any]]:
        """
        Get capabilities for all input and output devices.
        
        Efficient single-call method that fetches all status once.
        
        :return: Dict with 'inputs' and 'outputs' lists, or None if failed
        """
        # Fetch all status data in parallel
        output_status = await self.get_output_status()
        input_status = await self.get_input_status()
        cec_status = await self.get_cec_status()
        
        if not output_status or not input_status or not cec_status:
            _LOG.error("Failed to get status for capability detection")
            return None
        
        inputs = []
        outputs = []
        
        for i in range(1, 9):
            idx = i - 1
            
            # Input capabilities
            inname = input_status.get("inname", [])
            inactive = input_status.get("inactive", [])
            cec_inputindex = cec_status.get("inputindex", [])
            
            inputs.append({
                "input_num": i,
                "name": inname[idx] if idx < len(inname) else f"Input {i}",
                "signal_detected": inactive[idx] == 1 if idx < len(inactive) else False,
                "cec_enabled": cec_inputindex[idx] == 1 if idx < len(cec_inputindex) else False,
                "supported_cec_commands": [
                    "POWER_ON", "POWER_OFF", "UP", "DOWN", "LEFT", "RIGHT",
                    "SELECT", "MENU", "BACK", "PLAY", "PAUSE", "STOP",
                    "PREVIOUS", "NEXT", "REWIND", "FAST_FORWARD",
                    "VOLUME_UP", "VOLUME_DOWN", "MUTE"
                ],
            })
            
            # Output capabilities
            allscaler = output_status.get("allscaler", [])
            allarc = output_status.get("allarc", [])
            allconnect = output_status.get("allconnect", [])
            allout = output_status.get("allout", [])
            alloutputname = output_status.get("alloutputname", [])
            cec_outputindex = cec_status.get("outputindex", [])
            
            scaler_value = allscaler[idx] if idx < len(allscaler) else 0
            is_audio_only = scaler_value == 4
            
            outputs.append({
                "output_num": i,
                "name": alloutputname[idx] if idx < len(alloutputname) else f"Output {i}",
                "connected": allconnect[idx] == 1 if idx < len(allconnect) else False,
                "stream_enabled": allout[idx] == 1 if idx < len(allout) else True,
                "is_audio_only": is_audio_only,
                "arc_enabled": allarc[idx] == 1 if idx < len(allarc) else False,
                "cec_enabled": cec_outputindex[idx] == 1 if idx < len(cec_outputindex) else False,
                "scaler_mode": scaler_value,
                "supported_cec_commands": [
                    "POWER_ON", "POWER_OFF", "MUTE", 
                    "VOLUME_UP", "VOLUME_DOWN", "ACTIVE"
                ],
            })
        
        return {
            "inputs": inputs,
            "outputs": outputs,
        }