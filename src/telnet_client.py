"""
OREI BK-808 Telnet Client.

Provides persistent Telnet connection for:
- CEC control commands (faster than HTTP)
- Input cable detection (not available via HTTP)
- Bulk status queries (single command returns all state)
- Real-time push notifications (cable connect/disconnect events)

Command format: command!\r\n
Response: one or more text lines. Set commands are acknowledged with a line
(e.g. "cec in 1 on"); E00 (unknown command) and E01 (bad parameter) are
failures. See ``_telnet_proto`` for the completion rules (BE-07, HIL-A).

:copyright: (c) 2026 by Custom Integration.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import logging
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum

try:
    from _task_supervisor import cancel_and_wait, create_supervised_task
except ImportError:
    from ._task_supervisor import cancel_and_wait, create_supervised_task  # type: ignore[no-redef]

try:
    from _telnet_proto import TelnetIACFilter, is_acknowledged, is_response_complete, response_error
except ImportError:
    from ._telnet_proto import (  # type: ignore[no-redef]
        TelnetIACFilter,
        is_acknowledged,
        is_response_complete,
        response_error,
    )

_LOG = logging.getLogger(__name__)

# Telnet configuration
TELNET_PORT = 23
COMMAND_TIMEOUT = 5.0  # seconds to wait for response
RECONNECT_DELAY = 5.0  # seconds between reconnect attempts
MAX_RECONNECT_ATTEMPTS = 10
COMMAND_TERMINATOR = b"!\r\n"


class TelnetError(Exception):
    """Base exception for Telnet errors."""

    pass


class ConnectionError(TelnetError):
    """Connection-related errors."""

    pass


class ConnectionLostError(ConnectionError):
    """The matrix closed the connection (EOF) or the socket failed (BE-28/29)."""

    pass


class CommandError(TelnetError):
    """Command execution errors."""

    pass


class TelnetState(Enum):
    """Telnet connection state."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"


@dataclass
class InputStatus:
    """Status of an HDMI input port."""

    port: int
    connected: bool  # Cable connected (from Telnet)
    name: str = ""
    edid: str = ""


@dataclass
class OutputStatus:
    """Status of an HDMI output port."""

    port: int
    connected: bool  # Cable connected
    source: int = 0  # Currently routed input (1-8)
    hdcp: str = ""
    stream_enabled: bool = True
    video_mode: str = "pass-through"
    hdr_mode: str = "pass-through"
    arc: bool = False
    audio_mute: bool = False


@dataclass
class MatrixStatus:
    """Full matrix status from Telnet 'status!' command."""

    power: bool = True
    beep: bool = True
    panel_lock: bool = False
    lcd_timeout: int = 30
    inputs: dict[int, InputStatus] = field(default_factory=dict)
    outputs: dict[int, OutputStatus] = field(default_factory=dict)
    routing: dict[int, int] = field(default_factory=dict)  # output -> input mapping


class TelnetClient:
    """
    Async Telnet client for OREI BK-808 matrix.

    Provides persistent connection with auto-reconnect,
    command queuing, and response parsing.
    """

    def __init__(
        self,
        host: str,
        port: int = TELNET_PORT,
        on_status_update: Callable[[MatrixStatus], None] | None = None,
        on_connection_change: Callable[[TelnetState], None] | None = None,
    ):
        """
        Initialize Telnet client.

        :param host: Matrix IP address
        :param port: Telnet port (default 23)
        :param on_status_update: Callback for push status updates
        :param on_connection_change: Callback for connection state changes
        """
        self.host = host
        self.port = port
        self._on_status_update = on_status_update
        self._on_connection_change = on_connection_change

        # Connection state
        self._state = TelnetState.DISCONNECTED
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._reconnect_task: asyncio.Task | None = None
        self._listener_task: asyncio.Task | None = None

        # Single-flight connect() (BE-11): concurrent callers (the reconnect
        # loop, the matrix, REST handlers) must not open two sockets.
        self._connect_lock = asyncio.Lock()
        # Set by disconnect(): a connection loss after an intentional close
        # must not schedule a reconnect.
        self._closing = False

        # Command queue for serialization
        self._command_lock = asyncio.Lock()
        self._command_pending = False
        self._push_reading = False

        # IAC protocol filter (Item 1.1)
        self._filter = TelnetIACFilter()

        # Push notification buffer — stores stray bytes received during _send_raw
        # that should be processed by _listen_for_push after command completes (Item 1.3)
        self._push_buffer: list[str] = []

        # Firmware version (from banner)
        self.firmware_version: str = ""

    @property
    def connected(self) -> bool:
        """Check if connected."""
        return self._state == TelnetState.CONNECTED

    @property
    def state(self) -> TelnetState:
        """Get current connection state."""
        return self._state

    def _set_state(self, new_state: TelnetState) -> None:
        """Update state and notify callback."""
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            _LOG.info(f"Telnet state: {old_state.value} -> {new_state.value}")
            if self._on_connection_change:
                try:
                    self._on_connection_change(new_state)
                except Exception as e:
                    _LOG.error(f"Error in connection change callback: {e}")

    async def connect(self) -> bool:
        """
        Connect to the matrix Telnet interface.

        Single-flight (BE-11): concurrent callers wait for the attempt in
        progress instead of opening a second socket. The writer is closed on
        every failure path.

        :return: True if connection successful
        """
        async with self._connect_lock:
            if self._state == TelnetState.CONNECTED:
                return True

            self._closing = False
            self._set_state(TelnetState.CONNECTING)

            try:
                _LOG.info(f"Connecting to Telnet at {self.host}:{self.port}")

                self._reader, self._writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port), timeout=COMMAND_TIMEOUT
                )
                # Fresh IAC parser state for a fresh connection.
                self._filter = TelnetIACFilter()

                # Read welcome banner. EOF here (the device accepted the socket
                # and closed it) raises ConnectionLostError, so connect fails.
                await asyncio.sleep(0.5)
                banner = await self._read_available()
                if banner:
                    _LOG.debug(f"Telnet banner: {banner}")
                    # Extract firmware version from banner
                    match = re.search(r"fw version\s*:\s*v?([\d.]+)", banner, re.IGNORECASE)
                    if match:
                        self.firmware_version = match.group(1)
                        _LOG.info(f"Matrix firmware version: {self.firmware_version}")

                self._set_state(TelnetState.CONNECTED)

                # Start background listener for push notifications
                self._listener_task = create_supervised_task(self._listen_for_push, "telnet_push_listener")

                _LOG.info("Telnet connection established")
                return True

            except TimeoutError:
                _LOG.error(f"Telnet connection timeout to {self.host}:{self.port}")
                await self._close_transport()
                self._set_state(TelnetState.DISCONNECTED)
                return False
            except Exception as e:
                _LOG.error(f"Telnet connection failed: {e}")
                await self._close_transport()
                self._set_state(TelnetState.DISCONNECTED)
                return False
            except BaseException:
                # Cancelled mid-connect: do not leak the socket.
                self._abort_transport()
                self._set_state(TelnetState.DISCONNECTED)
                raise

    async def disconnect(self) -> None:
        """Disconnect from the matrix (intentional: no reconnect afterwards)."""
        _LOG.info("Disconnecting Telnet")
        self._closing = True

        # Stop the reconnect loop first so it cannot reopen the socket.
        await cancel_and_wait(self._reconnect_task, "telnet_reconnect")
        self._reconnect_task = None
        await cancel_and_wait(self._listener_task, "telnet_push_listener")
        self._listener_task = None

        await self._close_transport()
        self._set_state(TelnetState.DISCONNECTED)

    def _abort_transport(self) -> None:
        """Close the socket without waiting (safe from sync code)."""
        writer = self._writer
        self._reader = None
        self._writer = None
        if writer is not None:
            try:
                writer.close()
            except Exception as e:
                _LOG.debug(f"Error closing Telnet writer: {e}")

    async def _close_transport(self) -> None:
        """Close the socket and wait (briefly) until it is closed."""
        writer = self._writer
        self._abort_transport()
        if writer is not None:
            try:
                await asyncio.wait_for(writer.wait_closed(), timeout=1.0)
            except Exception as e:
                _LOG.debug(f"Error waiting for Telnet close: {e}")

    def _connection_lost(self, reason: str) -> None:
        """Handle an unexpected EOF or socket error (BE-28, BE-29).

        Closes the socket, moves to DISCONNECTED (so ``connected`` and the
        matrix's ``telnet_connected`` turn false), stops the push listener
        and schedules a reconnect unless ``disconnect()`` is in progress.
        Only the first report of a loss acts; later ones just make sure the
        socket is closed.
        """
        if self._state != TelnetState.CONNECTED:
            self._abort_transport()
            return
        _LOG.warning(f"Telnet connection lost: {reason}")
        self._abort_transport()
        self._set_state(TelnetState.DISCONNECTED)

        listener = self._listener_task
        if listener is not None and not listener.done() and listener is not asyncio.current_task():
            listener.cancel()

        if not self._closing:
            self._schedule_reconnect()

    async def _read_available(self, timeout: float = 0.5) -> str:
        """Read all available data from the connection.

        FIX (F4.3): Pass raw bytes through TelnetIACFilter to strip IAC
        negotiation sequences and handle auto-replies before decoding.

        FIX (F4.5): Detect binary data (non-printable bytes) and return
        empty string to avoid corrupting command response parsing.

        BE-28/BE-29: ``b""`` from ``read()`` is EOF (the matrix closed the
        connection) and a socket error means the same; both raise
        :class:`ConnectionLostError` instead of returning ``""``, which made
        callers loop until their timeout. A timeout with no data returns ``""``.
        """
        if not self._reader:
            raise ConnectionLostError("Not connected")

        try:
            data = await asyncio.wait_for(self._reader.read(8192), timeout=timeout)
        except TimeoutError:
            return ""
        except OSError as e:
            raise ConnectionLostError(f"read failed: {e}") from e
        if not data:
            raise ConnectionLostError("connection closed by the matrix (EOF)")

        try:
            # FIX (F4.3): Filter IAC negotiation bytes
            user_data, response_bytes = self._filter.feed(data)

            # Send any IAC auto-reply bytes back to the server
            if response_bytes and self._writer:
                self._writer.write(response_bytes)
                await self._writer.drain()

            # FIX (F4.5): Binary data detection
            if user_data:
                binary_count = sum(
                    1 for b in user_data
                    if b > 127 or (b < 32 and b not in (9, 10, 13))
                )
                non_printable_ratio = binary_count / len(user_data) if user_data else 0
                if non_printable_ratio > 0.1:
                    _LOG.warning(
                        f"Binary data detected in Telnet read: "
                        f"{binary_count}/{len(user_data)} non-printable bytes "
                        f"({non_printable_ratio:.0%}), returning empty string"
                    )
                    return ""

            return user_data.decode("utf-8", errors="replace")
        except OSError as e:
            raise ConnectionLostError(f"write failed: {e}") from e

    async def _send_raw(self, command: str) -> str:
        """
        Send a raw command and wait for response.

        :param command: Command without terminator
        :return: Response text
        :raises CommandError: If command fails
        """
        if not self.connected or not self._writer:
            raise ConnectionError("Not connected")

        self._command_pending = True
        try:
            async with self._command_lock:
                # Wait for push listener to exit its read block
                while self._push_reading:
                    await asyncio.sleep(0.02)

                # The connection may have been lost while we waited.
                writer = self._writer
                if not self.connected or writer is None:
                    raise ConnectionLostError("Not connected")

                # FIX (F4.2): Removed pre-clear read here.
                # Bytes that arrive during _send_raw are stored in _push_buffer
                # by _listen_for_push and drained after the lock is released.

                # Send command with terminator
                full_cmd = command + "!\r\n"
                _LOG.debug(f"Telnet TX: {repr(full_cmd)}")
                # FIX (F4.3): Escape any 0xFF bytes per RFC 854 §3
                encoded_cmd = self._filter.escape_ff(full_cmd.encode())
                writer.write(encoded_cmd)
                await writer.drain()

                # Read response until complete or COMMAND_TIMEOUT. EOF raises
                # ConnectionLostError (BE-29) instead of spinning to the timeout.
                response = ""
                loop = asyncio.get_running_loop()
                deadline = loop.time() + COMMAND_TIMEOUT

                while True:
                    remaining = deadline - loop.time()
                    if remaining <= 0:
                        _LOG.warning(f"Command timeout: {command}")
                        break
                    chunk = await self._read_available(timeout=min(0.5, remaining))
                    if chunk:
                        response += chunk
                        # Check for command completion
                        if self._is_response_complete(response, command):
                            break

                _LOG.debug(f"Telnet RX: {repr(response[:200])}...")
                return response

        except Exception as e:
            _LOG.error(f"Telnet command error ({command}): {e}")
            # Close the socket (BE-11), mark disconnected and trigger reconnect
            self._connection_lost(str(e))
            raise CommandError(f"Command failed: {e}") from e
        finally:
            self._command_pending = False

    def _is_response_complete(self, response: str, command: str = "") -> bool:
        """Check if we've received a complete response (BE-07).

        See :func:`_telnet_proto.is_response_complete`. Error codes complete
        (and fail) any command; ``status`` completes on its ``mac address``
        line; ``r link`` on its connect/disconnect line; every other command,
        including set commands, completes on its first answer line, so a
        successful set command no longer waits the whole ``COMMAND_TIMEOUT``.
        """
        return is_response_complete(response, command)

    def _command_ok(self, response: str, command: str) -> bool:
        """Log and report whether a set command succeeded (BE-07).

        ``E00`` (unknown command) and ``E01`` (bad parameter) are failures,
        never completion markers of a success; so is no answer at all (the
        command timed out).
        """
        error = response_error(response)
        if error is not None:
            _LOG.warning(f"Telnet command '{command}' rejected by the matrix: {error}")
            return False
        if not is_acknowledged(response, command):
            _LOG.warning(f"Telnet command '{command}' was not acknowledged (response: {response!r})")
            return False
        return True

    async def _listen_for_push(self) -> None:
        """Background task to listen for push notifications from the matrix.

        FIX (F2.3): previously this loop only slept without reading — push
        notifications from the matrix (cable connect/disconnect events)
        were never received. Now it reads from ``self._reader`` and parses
        cable-change events, dispatching them to ``on_status_update``.

        Note: this task runs concurrently with ``_send_raw`` which holds
        ``self._command_lock``. Bytes that arrive between commands are
        read here; bytes that arrive during a command response are read
        by ``_send_raw`` (which holds the lock). The two readers cooperate
        via the command lock — push data that arrives mid-command is
        stored in ``self._push_buffer`` and drained here after the lock
        is released (Item 1.3).
        """
        import re

        _LOG.debug("Starting Telnet push listener")

        # Cable connect/disconnect events look like:
        #   "hdmi input 3: connect"
        #   "hdmi output 5: disconnect"
        _push_event_re = re.compile(
            r"hdmi\s+(input|output)\s+(\d+)\s*:\s*(connect|disconnect)", re.IGNORECASE
        )
        # Buffer partial lines that may arrive split across reads
        line_buffer = ""

        while self.connected and self._reader:
            if self._command_pending:
                await asyncio.sleep(0.05)
                continue

            # FIX (F4.2): Drain any bytes stored during _send_raw
            while self._push_buffer:
                buffered = self._push_buffer.pop(0)
                line_buffer += buffered
                # Process complete lines from buffered data
                while "\n" in line_buffer:
                    raw_line, line_buffer = line_buffer.split("\n", 1)
                    line = raw_line.rstrip("\r").strip()
                    if line:
                        await self._dispatch_push_line(line, _push_event_re)

            self._push_reading = True
            try:
                data = await asyncio.wait_for(
                    self._reader.read(4096),
                    timeout=0.1,  # Short timeout to release quickly for commands
                )
            except TimeoutError:
                # No data within timeout — normal idle, loop and recheck state
                continue
            except Exception as e:
                # A failed socket read never recovers: treat it as a drop.
                self._connection_lost(f"push listener read error: {e}")
                return
            finally:
                self._push_reading = False

            if not data:
                # BE-28: b"" is EOF (matrix rebooted / network dropped). The old
                # code `continue`d here and read b"" again without ever
                # yielding, freezing the event loop at 100% CPU.
                self._connection_lost("connection closed by the matrix (EOF)")
                return

            # FIX (F4.3): Filter IAC negotiation bytes
            user_data, response_bytes = self._filter.feed(data)

            # Send any IAC auto-reply bytes back to the server
            if response_bytes and self._writer:
                try:
                    self._writer.write(response_bytes)
                    await self._writer.drain()
                except OSError as e:
                    self._connection_lost(f"push listener write error: {e}")
                    return

            # FIX (F4.5): Binary data detection
            if user_data:
                binary_count = sum(
                    1 for b in user_data
                    if b > 127 or (b < 32 and b not in (9, 10, 13))
                )
                non_printable_ratio = binary_count / len(user_data) if user_data else 0
                if non_printable_ratio > 0.1:
                    _LOG.warning(
                        f"Binary data detected in push listener: "
                        f"{binary_count}/{len(user_data)} non-printable bytes "
                        f"({non_printable_ratio:.0%}), skipping"
                    )
                    continue

            text = user_data.decode("utf-8", errors="replace")
            line_buffer += text

            # Process complete lines (delimited by \r\n or \n)
            while "\n" in line_buffer:
                raw_line, line_buffer = line_buffer.split("\n", 1)
                line = raw_line.rstrip("\r").strip()
                if not line:
                    continue
                await self._dispatch_push_line(line, _push_event_re)

        _LOG.debug("Telnet push listener stopped")

    async def _dispatch_push_line(self, line: str, event_re) -> None:
        """Parse a single push notification line and fire the callback.

        Parses cable connect/disconnect events and builds a partial
        MatrixStatus containing only the changed ports. This is sufficient
        for the on_status_update callback which typically just broadcasts
        a WebSocket notification.
        """
        m = event_re.search(line)
        if not m:
            return
        port_type, port_str, state = m.group(1).lower(), int(m.group(2)), m.group(3).lower()
        connected = state == "connect"
        _LOG.info(f"Telnet push event: {port_type} {port_str} {state}")

        if self._on_status_update is None:
            return

        # Build a minimal MatrixStatus with only the changed port.
        # Callers that want full state should re-poll.
        try:
            status = MatrixStatus()
            if port_type == "input":
                status.inputs[port_str] = InputStatus(
                    port=port_str, connected=connected
                )
            else:
                status.outputs[port_str] = OutputStatus(
                    port=port_str, connected=connected
                )
            self._on_status_update(status)
        except Exception as e:
            _LOG.warning(f"Failed to dispatch push event: {e}")

    def _schedule_reconnect(self) -> None:
        """Schedule a reconnection attempt."""
        if self._reconnect_task and not self._reconnect_task.done():
            return  # Already scheduled

        self._reconnect_task = create_supervised_task(self._reconnect_loop, "telnet_reconnect")

    # Maximum reconnect delay (5 minutes) — caps exponential growth so
    # the loop doesn't eventually wait hours between attempts.
    _MAX_RECONNECT_DELAY = 300.0

    async def _reconnect_loop(self) -> None:
        """Attempt to reconnect indefinitely with exponential backoff + jitter.

        FIX (F2.4): previously this loop ran at most ``MAX_RECONNECT_ATTEMPTS``
        (10) times then gave up permanently, leaving Telnet/CEC/cable-detection
        features dead until the entire driver process restarted. Now the loop
        runs forever with exponential backoff capped at 5 minutes — CEC and
        cable detection self-recover when the matrix comes back online.
        """
        import random

        attempt = 0
        while not self._closing:
            self._set_state(TelnetState.RECONNECTING)
            attempt += 1
            # Exponential backoff: 5, 10, 20, 40, 80, 160, 300 (capped)
            delay = min(RECONNECT_DELAY * (2 ** (attempt - 1)), self._MAX_RECONNECT_DELAY)
            # ±10% jitter to avoid thundering herd if many clients reconnect
            delay *= 0.9 + 0.2 * random.random()

            _LOG.info(
                f"Telnet reconnect attempt {attempt} in {delay:.1f}s"
            )
            await asyncio.sleep(delay)

            if await self.connect():
                _LOG.info(
                    f"Telnet reconnected after {attempt} attempts"
                )
                self._reconnect_task = None
                return
            # Otherwise loop again with backoff

    # =========================================================================
    # Status Commands
    # =========================================================================

    async def get_full_status(self) -> MatrixStatus:
        """
        Get full matrix status using 'status!' command.

        Returns parsed MatrixStatus with all input/output states.
        """
        response = await self._send_raw("status")
        _LOG.debug(f"Full status response:\n{response}")
        result = self._parse_status_response(response)
        _LOG.debug(f"Parsed inputs: {result.inputs}")
        _LOG.debug(f"Parsed outputs: {result.outputs}")
        return result

    @staticmethod
    def _parse_link_response(response: str, port_type: str, port: int) -> bool | None:
        """Parse ``hdmi input|output N: connect|disconnect``; None if absent."""
        match = re.search(
            rf"hdmi\s+{port_type}\s+{port}\s*:\s*(connect|disconnect)\b", response, re.IGNORECASE
        )
        if match is None:
            return None
        return match.group(1).lower() == "connect"

    async def get_input_connection(self, input_num: int) -> bool | None:
        """
        Check if an input port has a cable connected.

        :param input_num: Input port (1-8)
        :return: True/False, or None if the response did not say (BE-29)
        """
        if input_num < 1 or input_num > 8:
            raise ValueError(f"Invalid input number: {input_num}")

        response = await self._send_raw(f"r link in {input_num}")
        # Response: "hdmi input X: connect" or "hdmi input X: disconnect"
        return self._parse_link_response(response, "input", input_num)

    async def get_output_connection(self, output_num: int) -> bool | None:
        """
        Check if an output port has a cable connected.

        :param output_num: Output port (1-8)
        :return: True/False, or None if the response did not say (BE-29)
        """
        if output_num < 1 or output_num > 8:
            raise ValueError(f"Invalid output number: {output_num}")

        response = await self._send_raw(f"r link out {output_num}")
        return self._parse_link_response(response, "output", output_num)

    @staticmethod
    def connections_from_status(status: MatrixStatus) -> dict[str, dict[int, bool | None]]:
        """Cable state per port from one parsed ``status`` dump.

        BE-29: a port missing from the dump (truncated or garbled response)
        is ``None`` (unknown), not ``False`` (disconnected).
        """
        return {
            "inputs": {i: status.inputs[i].connected if i in status.inputs else None for i in range(1, 9)},
            "outputs": {i: status.outputs[i].connected if i in status.outputs else None for i in range(1, 9)},
        }

    async def get_all_connections(self) -> dict[str, dict[int, bool | None]]:
        """Cable state of every input and output from a single ``status!`` (BE-30).

        :return: ``{"inputs": {1..8: bool|None}, "outputs": {1..8: bool|None}}``
        """
        return self.connections_from_status(await self.get_full_status())

    async def get_all_input_connections(self) -> dict[int, bool | None]:
        """
        Get cable connection status for all inputs using bulk status command.

        Prefer :meth:`get_all_connections` when outputs are needed too (one
        ``status!`` instead of two).

        :return: Dict mapping input number to connection status (None = unknown)
        """
        return (await self.get_all_connections())["inputs"]

    async def get_all_output_connections(self) -> dict[int, bool | None]:
        """
        Get cable connection status for all outputs using bulk status command.

        Prefer :meth:`get_all_connections` when inputs are needed too.

        :return: Dict mapping output number to connection status (None = unknown)
        """
        return (await self.get_all_connections())["outputs"]

    def _parse_status_response(self, response: str) -> MatrixStatus:
        """Parse the response from 'status!' command."""
        status = MatrixStatus()

        # Parse power state
        if "power on" in response.lower():
            status.power = True
        elif "power off" in response.lower():
            status.power = False

        # Parse beep state
        if "beep on" in response.lower():
            status.beep = True
        elif "beep off" in response.lower():
            status.beep = False

        # Parse panel lock
        if "panel button lock on" in response.lower():
            status.panel_lock = True
        elif "panel button lock off" in response.lower():
            status.panel_lock = False

        # Parse LCD timeout
        lcd_match = re.search(r"lcd on (\d+) seconds", response.lower())
        if lcd_match:
            status.lcd_timeout = int(lcd_match.group(1))

        # Parse input connections
        for match in re.finditer(r"hdmi input (\d+):\s*(connect|disconnect)", response.lower()):
            port = int(match.group(1))
            connected = match.group(2) == "connect"
            status.inputs[port] = InputStatus(port=port, connected=connected)

        # Parse output connections
        for match in re.finditer(r"hdmi output (\d+):\s*(connect|disconnect)", response.lower()):
            port = int(match.group(1))
            connected = match.group(2) == "connect"
            status.outputs[port] = OutputStatus(port=port, connected=connected)

        # Parse routing: output1->input1
        for match in re.finditer(r"output(\d+)->input(\d+)", response.lower()):
            output = int(match.group(1))
            input_src = int(match.group(2))
            status.routing[output] = input_src
            if output in status.outputs:
                status.outputs[output].source = input_src

        # Parse HDCP settings
        for match in re.finditer(r"output (\d+) hdcp:\s*(.+)", response.lower()):
            port = int(match.group(1))
            hdcp = match.group(2).strip()
            if port in status.outputs:
                status.outputs[port].hdcp = hdcp

        # Parse stream enable/disable
        for match in re.finditer(r"output (\d+) stream:\s*(enable|disable)", response.lower()):
            port = int(match.group(1))
            enabled = match.group(2) == "enable"
            if port in status.outputs:
                status.outputs[port].stream_enabled = enabled

        # Parse video mode
        for match in re.finditer(r"output (\d+) video mode:\s*(.+)", response.lower()):
            port = int(match.group(1))
            mode = match.group(2).strip()
            if port in status.outputs:
                status.outputs[port].video_mode = mode

        # Parse HDR mode
        for match in re.finditer(r"output (\d+) hdr mode:\s*(.+)", response.lower()):
            port = int(match.group(1))
            mode = match.group(2).strip()
            if port in status.outputs:
                status.outputs[port].hdr_mode = mode

        # Parse ARC
        for match in re.finditer(r"output (\d+) arc:\s*(on|off)", response.lower()):
            port = int(match.group(1))
            enabled = match.group(2) == "on"
            if port in status.outputs:
                status.outputs[port].arc = enabled

        # Parse audio mute
        for match in re.finditer(r"output (\d+) audio mute:\s*(on|off)", response.lower()):
            port = int(match.group(1))
            muted = match.group(2) == "on"
            if port in status.outputs:
                status.outputs[port].audio_mute = muted

        # Parse EDID for inputs
        for match in re.finditer(r"input (\d+) edid:\s*(.+)", response.lower()):
            port = int(match.group(1))
            edid = match.group(2).strip()
            if port in status.inputs:
                status.inputs[port].edid = edid

        return status

    # =========================================================================
    # CEC Commands
    # =========================================================================

    async def cec_input_power_on(self, input_num: int) -> bool:
        """Send Power On CEC command to input device."""
        return await self._send_cec_input(input_num, "on")

    async def cec_input_power_off(self, input_num: int) -> bool:
        """Send Power Off CEC command to input device."""
        return await self._send_cec_input(input_num, "off")

    async def cec_input_menu(self, input_num: int) -> bool:
        """Send Menu CEC command to input device."""
        return await self._send_cec_input(input_num, "menu")

    async def cec_input_back(self, input_num: int) -> bool:
        """Send Back CEC command to input device."""
        return await self._send_cec_input(input_num, "back")

    async def cec_input_up(self, input_num: int) -> bool:
        """Send Up navigation CEC command to input device."""
        return await self._send_cec_input(input_num, "up")

    async def cec_input_down(self, input_num: int) -> bool:
        """Send Down navigation CEC command to input device."""
        return await self._send_cec_input(input_num, "down")

    async def cec_input_left(self, input_num: int) -> bool:
        """Send Left navigation CEC command to input device."""
        return await self._send_cec_input(input_num, "left")

    async def cec_input_right(self, input_num: int) -> bool:
        """Send Right navigation CEC command to input device."""
        return await self._send_cec_input(input_num, "right")

    async def cec_input_enter(self, input_num: int) -> bool:
        """Send Enter/Select CEC command to input device."""
        return await self._send_cec_input(input_num, "enter")

    async def cec_input_play(self, input_num: int) -> bool:
        """Send Play CEC command to input device."""
        return await self._send_cec_input(input_num, "play")

    async def cec_input_pause(self, input_num: int) -> bool:
        """Send Pause CEC command to input device."""
        return await self._send_cec_input(input_num, "pause")

    async def cec_input_stop(self, input_num: int) -> bool:
        """Send Stop CEC command to input device."""
        return await self._send_cec_input(input_num, "stop")

    async def cec_input_previous(self, input_num: int) -> bool:
        """Send Previous CEC command to input device."""
        return await self._send_cec_input(input_num, "previous")

    async def cec_input_next(self, input_num: int) -> bool:
        """Send Next CEC command to input device."""
        return await self._send_cec_input(input_num, "next")

    async def cec_input_rewind(self, input_num: int) -> bool:
        """Send Rewind CEC command to input device."""
        return await self._send_cec_input(input_num, "rew")

    async def cec_input_fast_forward(self, input_num: int) -> bool:
        """Send Fast Forward CEC command to input device."""
        return await self._send_cec_input(input_num, "ff")

    async def cec_input_volume_up(self, input_num: int) -> bool:
        """Send Volume Up CEC command to input device."""
        return await self._send_cec_input(input_num, "vol+")

    async def cec_input_volume_down(self, input_num: int) -> bool:
        """Send Volume Down CEC command to input device."""
        return await self._send_cec_input(input_num, "vol-")

    async def cec_input_mute(self, input_num: int) -> bool:
        """Send Mute CEC command to input device."""
        return await self._send_cec_input(input_num, "mute")

    async def _send_cec_input(self, input_num: int, command: str) -> bool:
        """
        Send a CEC command to an input device.

        Command format: s cec in {input} {command}!
        Example: s cec in 1 on!
        """
        if input_num < 1 or input_num > 8:
            _LOG.error(f"Invalid input number: {input_num}")
            return False

        try:
            telnet_cmd = f"s cec in {input_num} {command}"
            response = await self._send_raw(telnet_cmd)
            if not self._command_ok(response, telnet_cmd):
                _LOG.warning(f"CEC input command failed: {command} on input {input_num}")
                return False
            _LOG.info(f"CEC input {input_num}: {command} sent successfully")
            return True
        except Exception as e:
            _LOG.error(f"CEC input command error: {e}")
            return False

    # Output CEC Commands

    async def cec_output_power_on(self, output_num: int) -> bool:
        """Send Power On CEC command to output device (TV)."""
        return await self._send_cec_output(output_num, "on")

    async def cec_output_power_off(self, output_num: int) -> bool:
        """Send Power Off CEC command to output device (TV)."""
        return await self._send_cec_output(output_num, "off")

    async def cec_output_volume_up(self, output_num: int) -> bool:
        """Send Volume Up CEC command to output device."""
        return await self._send_cec_output(output_num, "vol+")

    async def cec_output_volume_down(self, output_num: int) -> bool:
        """Send Volume Down CEC command to output device."""
        return await self._send_cec_output(output_num, "vol-")

    async def cec_output_mute(self, output_num: int) -> bool:
        """Send Mute CEC command to output device."""
        return await self._send_cec_output(output_num, "mute")

    async def cec_output_active_source(self, output_num: int) -> bool:
        """Set output as active source via CEC."""
        return await self._send_cec_output(output_num, "active")

    async def _send_cec_output(self, output_num: int, command: str) -> bool:
        """
        Send a CEC command to an output device (TV).

        Command format: s cec hdmi out {output} {command}!
        Example: s cec hdmi out 1 on!
        """
        if output_num < 1 or output_num > 8:
            _LOG.error(f"Invalid output number: {output_num}")
            return False

        try:
            telnet_cmd = f"s cec hdmi out {output_num} {command}"
            response = await self._send_raw(telnet_cmd)
            if not self._command_ok(response, telnet_cmd):
                _LOG.warning(f"CEC output command failed: {command} on output {output_num}")
                return False
            _LOG.info(f"CEC output {output_num}: {command} sent successfully")
            return True
        except Exception as e:
            _LOG.error(f"CEC output command error: {e}")
            return False

    # =========================================================================
    # Preset Commands (via Telnet)
    # =========================================================================

    async def save_preset(self, preset_num: int) -> bool:
        """Save current routing to a preset."""
        if preset_num < 1 or preset_num > 8:
            _LOG.error(f"Invalid preset number: {preset_num}")
            return False

        try:
            telnet_cmd = f"s save preset {preset_num}"
            return self._command_ok(await self._send_raw(telnet_cmd), telnet_cmd)
        except Exception as e:
            _LOG.error(f"Save preset error: {e}")
            return False

    async def recall_preset(self, preset_num: int) -> bool:
        """Recall a saved preset."""
        if preset_num < 1 or preset_num > 8:
            _LOG.error(f"Invalid preset number: {preset_num}")
            return False

        try:
            telnet_cmd = f"s recall preset {preset_num}"
            return self._command_ok(await self._send_raw(telnet_cmd), telnet_cmd)
        except Exception as e:
            _LOG.error(f"Recall preset error: {e}")
            return False

    async def clear_preset(self, preset_num: int) -> bool:
        """Clear a saved preset."""
        if preset_num < 1 or preset_num > 8:
            _LOG.error(f"Invalid preset number: {preset_num}")
            return False

        try:
            telnet_cmd = f"s clear preset {preset_num}"
            return self._command_ok(await self._send_raw(telnet_cmd), telnet_cmd)
        except Exception as e:
            _LOG.error(f"Clear preset error: {e}")
            return False

    async def get_preset_info(self, preset_num: int) -> dict | None:
        """Get information about a preset."""
        if preset_num < 1 or preset_num > 8:
            _LOG.error(f"Invalid preset number: {preset_num}")
            return None

        try:
            response = await self._send_raw(f"r preset {preset_num}")
            # Parse preset info from response
            # Format: preset X: output1->inputY, output2->inputZ, ...
            info: dict = {"preset": preset_num, "routing": {}}
            for match in re.finditer(r"output(\d+)->input(\d+)", response.lower()):
                output = int(match.group(1))
                input_src = int(match.group(2))
                info["routing"][output] = input_src
            return info
        except Exception as e:
            _LOG.error(f"Get preset info error: {e}")
            return None

    # =========================================================================
    # Routing Commands (via Telnet)
    # =========================================================================

    async def switch_input(self, input_num: int, output_num: int) -> bool:
        """
        Route an input to an output.

        Command: s output Y in source X!
        """
        if input_num < 1 or input_num > 8:
            _LOG.error(f"Invalid input number: {input_num}")
            return False
        if output_num < 1 or output_num > 8:
            _LOG.error(f"Invalid output number: {output_num}")
            return False

        try:
            telnet_cmd = f"s output {output_num} in source {input_num}"
            success = self._command_ok(await self._send_raw(telnet_cmd), telnet_cmd)
            if success:
                _LOG.info(f"Routed input {input_num} to output {output_num}")
            return success
        except Exception as e:
            _LOG.error(f"Switch input error: {e}")
            return False

    async def switch_input_to_all(self, input_num: int) -> bool:
        """Route an input to all outputs."""
        if input_num < 1 or input_num > 8:
            _LOG.error(f"Invalid input number: {input_num}")
            return False

        try:
            # Use output 0 to target all outputs
            telnet_cmd = f"s output 0 in source {input_num}"
            success = self._command_ok(await self._send_raw(telnet_cmd), telnet_cmd)
            if success:
                _LOG.info(f"Routed input {input_num} to all outputs")
            return success
        except Exception as e:
            _LOG.error(f"Switch input to all error: {e}")
            return False

    # =========================================================================
    # Power/System Commands
    # =========================================================================

    async def power_on(self) -> bool:
        """Power on the matrix."""
        try:
            return self._command_ok(await self._send_raw("power 1"), "power 1")
        except Exception as e:
            _LOG.error(f"Power on error: {e}")
            return False

    async def power_off(self) -> bool:
        """Power off the matrix (standby)."""
        try:
            return self._command_ok(await self._send_raw("power 0"), "power 0")
        except Exception as e:
            _LOG.error(f"Power off error: {e}")
            return False

    async def reboot(self) -> bool:
        """Reboot the matrix."""
        try:
            await self._send_raw("reboot")
            return True  # Connection will drop after reboot
        except Exception as e:
            _LOG.error(f"Reboot error: {e}")
            return False

    async def get_firmware_version(self) -> str:
        """Get firmware version."""
        try:
            response = await self._send_raw("r fw version")
            match = re.search(r"v?([\d.]+)", response)
            if match:
                return match.group(1)
            return self.firmware_version
        except Exception as e:
            _LOG.error(f"Get firmware version error: {e}")
            return self.firmware_version

    async def get_device_type(self) -> str:
        """Get device model/type."""
        try:
            response = await self._send_raw("r type")
            # Parse model from response
            return response.strip()
        except Exception as e:
            _LOG.error(f"Get device type error: {e}")
            return ""
