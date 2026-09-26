"""
OREI BK-808 HDMI Matrix control library.

Hybrid HTTP/Telnet control architecture:
- HTTP: Authentication, routing changes, naming, EDID/video settings, presets
- Telnet: CEC commands (faster), input cable detection, bulk status queries

HTTP API: POST to /cgi-bin/instr with JSON payload
Telnet: Port 23, commands end with !\\r\\n

Connection state (BE-04): ``OreiMatrix.connection_state`` is one of
:class:`ConnectionState`. ``connected`` is true while the HTTP session works
(CONNECTED, or DEGRADED when only Telnet is down). A transport error
(connection refused or reset, DNS, TLS) moves the matrix to BACKOFF, emits
``Events.DISCONNECTED`` and starts the matrix-owned reconnect supervisor;
``disconnect()`` is intentional and never triggers a reconnect.

HIL-12: the BK-808 never answers a command it does not implement (captured on
V1.10.01), so a command that times out, gets an HTTP error status or an
unparseable body is a *failed command*, not a lost link: the hub logs
"device did not answer <comhead>", returns failure, and checks the link with a
status read. Only when that health read fails too is the link marked lost.
"""

import asyncio
import datetime
import json
import logging
import os
import random
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Any, TypeVar

import aiohttp
from pyee.asyncio import AsyncIOEventEmitter

# Import Telnet client for CEC and cable detection
try:
    from ._task_supervisor import cancel_and_wait, create_supervised_task
    from .device_codes import (
        CEC_INPUT_COMMANDS,
        CEC_OUTPUT_COMMANDS,
        HDCP_MODES,
        HDR_MODES,
        SCALER_AUDIO_ONLY,
        SCALER_MODES,
        edid_copy_from_output,
        hdr_from_device,
        hdr_to_device,
        scaler_from_device,
        scaler_to_device,
    )
    from .device_codes import (
        EDID_MODES as DEVICE_EDID_MODES,
    )
    from .device_codes import (
        EXT_AUDIO_MODES as DEVICE_EXT_AUDIO_MODES,
    )
    from .device_codes import (
        LCD_TIMEOUT_MODES as DEVICE_LCD_MODES,
    )
    from .telnet_client import MatrixStatus, TelnetClient, TelnetState
except ImportError:
    from _task_supervisor import cancel_and_wait, create_supervised_task  # type: ignore[no-redef]
    from device_codes import (  # type: ignore[no-redef]
        CEC_INPUT_COMMANDS,
        CEC_OUTPUT_COMMANDS,
        HDCP_MODES,
        HDR_MODES,
        SCALER_AUDIO_ONLY,
        SCALER_MODES,
        edid_copy_from_output,
        hdr_from_device,
        hdr_to_device,
        scaler_from_device,
        scaler_to_device,
    )
    from device_codes import (
        EDID_MODES as DEVICE_EDID_MODES,
    )
    from device_codes import (
        EXT_AUDIO_MODES as DEVICE_EXT_AUDIO_MODES,
    )
    from device_codes import (
        LCD_TIMEOUT_MODES as DEVICE_LCD_MODES,
    )
    from telnet_client import MatrixStatus, TelnetClient, TelnetState

_LOG = logging.getLogger(__name__)

# Connection retry configuration
MAX_RETRIES = int(os.environ.get("OREI_MAX_RETRIES", "5"))
INITIAL_RETRY_DELAY = float(os.environ.get("OREI_RETRY_DELAY", "1.0"))
MAX_RETRY_DELAY = float(os.environ.get("OREI_MAX_RETRY_DELAY", "60.0"))
RETRY_JITTER = 0.1  # 10% jitter to prevent thundering herd

#: HTTP request timeout (seconds) for every command, login included.
HTTP_TIMEOUT = 5.0

#: Read used to tell "the device ignored one command" from "the device is
#: gone" (HIL-12), and how often it is tried: right after an unanswered
#: command the device's web server can stall for one more request (captured).
HEALTH_CHECK_COMMAND = {"comhead": "get system status", "language": 0}
HEALTH_CHECK_ATTEMPTS = 2

_T = TypeVar("_T")


class Events(IntEnum):
    """Internal OREI Matrix events."""

    CONNECTED = 0
    DISCONNECTED = 1
    ERROR = 2
    UPDATE = 3
    RECONNECTING = 4  # New event for reconnection attempts
    CONFIG_CHANGED = 5


class ConnectionState(StrEnum):
    """Link state of the matrix (BE-04).

    - ``DISCONNECTED``: not connected and no reconnect scheduled (initial
      state, after ``disconnect()``, or after a failed first connect).
    - ``CONNECTING``: login in progress.
    - ``CONNECTED``: HTTP session and Telnet both up.
    - ``DEGRADED``: HTTP session up, Telnet down (CEC and cable detection use
      the HTTP fallbacks).
    - ``BACKOFF``: the link was lost; the reconnect supervisor is waiting
      before its next attempt.
    """

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DEGRADED = "degraded"
    BACKOFF = "backoff"


#: States in which HTTP commands can be sent (``OreiMatrix.connected``).
_LINK_UP = frozenset({ConnectionState.CONNECTED, ConnectionState.DEGRADED})

# `result` of a successful login: 1 on MCU V1.10.01 (captured,
# tests/fixtures/device/BK-808_V1.10.01_web-V2.00.03/http/login.json). The API
# doc lists "success"; it is kept for other firmware.
LOGIN_SUCCESS_RESULTS: tuple[int | str, ...] = (1, "success")
# `result` of an accepted write: 1 on V1.10.01 (captured for video switch,
# names, beep, panel lock, set cec index and set poweronoff, write/*.json).
# "success" is kept for other firmware.
WRITE_SUCCESS_RESULTS: tuple[int | str, ...] = (1, "success")
# `result` values that mean failure. V1.10.01 answers a rejected write and a
# wrong-password login with 0 (captured, write/*.json and
# probe/login_wrong_password.json); the strings are kept for other firmware.
# The answer to a command sent without a session is still uncaptured (HIL-14).
FAILURE_RESULTS: tuple[int | str, ...] = (0, "fail", "failed", "failure", "error")


def _normalise_result(value: Any) -> Any:
    """``"1"``/``" Success "`` -> ``1``/``"success"``; other values unchanged."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, str):
        text = value.strip().lower()
        return int(text) if text.isdigit() else text
    return value


def is_login_success(response: Any) -> bool:
    """Whether a ``login`` response reports success (BE-05).

    The matrix echoes ``comhead: "login"`` even for a wrong password
    (captured on V1.10.01: ``{"comhead":"login","result":0}``), so the echo
    proves nothing: only an explicit success ``result`` counts. A failure
    ``result`` (0, "fail", ...), a missing ``result`` or anything unexpected
    is a failed login.
    """
    if not isinstance(response, dict):
        return False
    return _normalise_result(response.get("result")) in LOGIN_SUCCESS_RESULTS


def is_write_success(response: Any) -> bool:
    """Whether a write command's response reports success (BE-12)."""
    if not isinstance(response, dict):
        return False
    return _normalise_result(response.get("result")) in WRITE_SUCCESS_RESULTS


def _copy_cables(cables: dict[str, Any]) -> dict[str, Any]:
    """Copy a cable-status dict including its per-side port dicts."""
    return {side: dict(ports) if isinstance(ports, dict) else ports for side, ports in cables.items()}


#: Physical outputs. Per-output arrays of V1.10.01 have one more entry
#: (``allsource``, ``allscaler``, ``allhdr``, ``allhdcp``, ``allarc``, ``allout``,
#: ``allaudiomute``: 9 values). The device's own web interface shows the ninth
#: entry as its "All Output" row and writes it with port 0 (HIL-04).
OUTPUT_COUNT = 8


def per_output(values: Any) -> list[Any]:
    """The first ``OUTPUT_COUNT`` entries of a per-output array (drops the ninth, HIL-04)."""
    return list(values[:OUTPUT_COUNT]) if isinstance(values, list) else []


def api_output_settings(status: dict[str, Any] | None) -> dict[str, list[Any]]:
    """Per-output HDR/scaler/HDCP from ``get output status``, as API values.

    HDR and scaler are 1-based in the hub's API and 0-based on the device
    (:mod:`device_codes`); a code the device table does not know reads as None.
    """
    status = status or {}
    return {
        "hdr": [hdr_from_device(v) for v in per_output(status.get("allhdr"))],
        "scaler": [scaler_from_device(v) for v in per_output(status.get("allscaler"))],
        "hdcp": per_output(status.get("allhdcp")),
    }


def _is_read_command(comhead: str) -> bool:
    return comhead.startswith("get") or comhead.endswith("get") or "get" in comhead


# Commands whose effect is not idempotent: sending one twice changes the
# result (a CEC volume step, a power toggle). They are never resent after an
# ambiguous failure answer, because the first send may already have acted.
NON_IDEMPOTENT_COMMANDS = frozenset({"cec command"})


def _looks_like_login_page(text: str) -> bool:
    # HIL-A: confirm -- some firmwares may answer an expired session with the
    # HTML login page instead of JSON.
    lowered = text.lstrip().lower()
    return lowered.startswith("<") and ("<html" in lowered or "login" in lowered)


@dataclass
class _HttpResult:
    """Outcome of one POST to /cgi-bin/instr.

    ``kind`` is ``ok``, ``auth`` (the session is not valid, or a failure
    ``result`` that may mean that), ``transport`` (the connection failed:
    refused, reset, DNS, TLS), ``no_answer`` (the request was sent but timed
    out, HIL-12), ``http_error`` (an HTTP error status) or ``bad_response``
    (not a JSON object).
    """

    kind: str
    data: dict[str, Any] | None = None
    error: str | None = None
    timeout: bool = False


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
        self._session: aiohttp.ClientSession | None = None
        self._state = ConnectionState.DISCONNECTED
        # Typed as Any: pyee annotates event names as `str`, but this codebase
        # keys events by the `Events` IntEnum (any hashable works at runtime).
        self.events: Any = AsyncIOEventEmitter()

        # Device state
        self._current_scene: int | None = None
        self._last_error: str | None = None

        # Retry / reconnect state. The reconnect supervisor is owned by this
        # object and only runs after the link was lost (not after disconnect()).
        self.auto_reconnect = os.environ.get("OREI_AUTO_RECONNECT", "true").lower() != "false"
        self._retry_count = 0
        self._reconnect_task: asyncio.Task | None = None
        self._intentional_disconnect = False
        # Single-flight connect / re-login (BE-11): concurrent callers await
        # the attempt already in progress.
        self._connect_task: asyncio.Future[bool] | None = None
        self._relogin_task: asyncio.Future[bool] | None = None

        # Telnet client for CEC commands and cable detection
        self._telnet: TelnetClient | None = None
        self._telnet_port = int(os.environ.get("OREI_TELNET_PORT", "23"))
        self._use_telnet_cec = os.environ.get("OREI_USE_TELNET_CEC", "false").lower() == "true"

        # CEC enabled status cache
        # inputindex/outputindex: 1 = CEC enabled, 0 = disabled
        self._cec_enabled_cache: dict[str, Any] = {
            "inputs": [False] * 8,
            "outputs": [False] * 8,
            "last_updated": None,  # datetime when last fetched
        }
        self._cec_cache_ttl = int(os.environ.get("OREI_CEC_CACHE_TTL", "300"))  # 5 minutes cache TTL

        # Serializes HTTP requests so concurrent REST/HA/UC callers cannot
        # interleave JSON POSTs against the same matrix aiohttp session. It is
        # held for one request only -- never across a reconnect or a backoff
        # sleep (BE-17).
        self._command_lock = asyncio.Lock()

        # Protects _cec_enabled_cache reads/writes from concurrent coroutines.
        self._cec_cache_lock = asyncio.Lock()

        # Status caches to speed up UI loads (BE-03). Every cache below expires
        # after OREI_STATUS_CACHE_TTL seconds; writes invalidate all of them.
        # Concurrent refreshes of one cache share a single request
        # (_single_flight); _cache_generation increases on every invalidation
        # so a refresh started before a write is never cached or joined after it.
        self._status_cache: dict[str, Any] | None = None
        self._status_cache_time: float = 0.0
        self._status_cache_ttl = float(os.environ.get("OREI_STATUS_CACHE_TTL", "3.0"))
        self._cache_generation = 0
        self._inflight: dict[str, tuple[int, asyncio.Future[Any]]] = {}

        self._output_status_cache: dict[str, Any] | None = None
        self._output_status_cache_time: float = 0.0

        self._input_status_cache: dict[str, Any] | None = None
        self._input_status_cache_time: float = 0.0

        self._cable_status_cache: dict[str, Any] | None = None
        self._cable_status_cache_time: float = 0.0

        # UTC time of the last successful status read (for /api/health)
        self._last_successful_poll: datetime.datetime | None = None

    # =========================================================================
    # Connection state
    # =========================================================================

    @property
    def connection_state(self) -> ConnectionState:
        """Current link state (see :class:`ConnectionState`)."""
        return self._state

    @property
    def connected(self) -> bool:
        """True while HTTP commands can be sent (CONNECTED or DEGRADED)."""
        return self._state in _LINK_UP

    @property
    def _connected(self) -> bool:
        """Backward-compatible alias of :attr:`connected` (tests set it)."""
        return self.connected

    @_connected.setter
    def _connected(self, value: bool) -> None:
        self._set_state(self._link_up_state() if value else ConnectionState.DISCONNECTED)

    def _set_state(self, new_state: ConnectionState) -> None:
        if new_state is not self._state:
            _LOG.info("Matrix connection state: %s -> %s", self._state.value, new_state.value)
            self._state = new_state

    def _link_up_state(self) -> ConnectionState:
        return ConnectionState.CONNECTED if self.telnet_connected else ConnectionState.DEGRADED

    def _link_lost(self, reason: str | None) -> None:
        """The HTTP link failed: leave CONNECTED/DEGRADED and schedule a reconnect.

        Emits ``Events.DISCONNECTED`` when the link was up, so existing
        listeners (driver.py) keep working. Never called for an intentional
        ``disconnect()``.
        """
        was_up = self.connected
        if self._intentional_disconnect or not self.auto_reconnect:
            self._set_state(ConnectionState.DISCONNECTED)
        else:
            self._set_state(ConnectionState.BACKOFF)
            self._start_reconnect()
        if was_up:
            _LOG.warning("Lost connection to OREI Matrix: %s", reason)
            self.events.emit(Events.DISCONNECTED)

    def start_auto_reconnect(self) -> None:
        """Keep trying to connect in the background until it works.

        For entry points whose first ``connect()`` failed (matrix offline at
        startup). No-op when connected or already reconnecting.
        """
        if self.connected:
            return
        self._intentional_disconnect = False
        self._set_state(ConnectionState.BACKOFF)
        self._start_reconnect()

    def _start_reconnect(self) -> None:
        if not self.auto_reconnect or self._intentional_disconnect:
            return
        task = self._reconnect_task
        if task is not None and not task.done():
            return
        self._reconnect_task = create_supervised_task(self._reconnect_loop, "matrix_reconnect")

    async def _reconnect_loop(self) -> None:
        """Reconnect with exponential backoff until connected (or disconnect())."""
        attempt = 0
        while not self._intentional_disconnect and not self.connected:
            delay = self._calculate_retry_delay(attempt)
            if self._state is not ConnectionState.CONNECTING:
                self._set_state(ConnectionState.BACKOFF)
            _LOG.info("Matrix reconnect attempt %d in %.1fs", attempt + 1, delay)
            await asyncio.sleep(delay)
            if self._intentional_disconnect or self.connected:
                break
            if await self.connect():
                _LOG.info("Reconnected to OREI Matrix after %d attempt(s)", attempt + 1)
                break
            attempt += 1

    @property
    def last_successful_poll(self) -> datetime.datetime | None:
        """UTC time the matrix last answered a status read, or None."""
        return self._last_successful_poll

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

        # BE-11: dispose of the previous client (its socket, push listener and
        # reconnect loop) before replacing it, or it keeps running and
        # reconnecting in the background.
        await self._dispose_telnet()

        client: TelnetClient | None = None
        try:
            _LOG.info(f"Connecting Telnet to {self.host}:{self._telnet_port}")
            client = TelnetClient(
                host=self.host, port=self._telnet_port, on_connection_change=self._on_telnet_state_change
            )
            self._telnet = client

            if await client.connect():
                _LOG.info(f"Telnet connected (firmware: {client.firmware_version})")
                return True
            else:
                _LOG.warning("Telnet connection failed - CEC and cable detection will use HTTP fallback")
                await self._dispose_telnet()
                return False

        except Exception as e:
            _LOG.warning(f"Telnet connection error: {e} - falling back to HTTP-only mode")
            await self._dispose_telnet()
            return False

    async def _dispose_telnet(self) -> None:
        """Disconnect and drop the current Telnet client, if any."""
        telnet, self._telnet = self._telnet, None
        if telnet is not None:
            try:
                await telnet.disconnect()
            except Exception as e:
                _LOG.warning(f"Error disposing Telnet client: {e}")
        if self.connected:
            self._set_state(self._link_up_state())

    def _on_telnet_state_change(self, state: TelnetState) -> None:
        """Track Telnet up/down as CONNECTED/DEGRADED while HTTP is up."""
        _LOG.info(f"Telnet state changed to: {state.value}")
        if self.connected:
            self._set_state(self._link_up_state())

    def _calculate_retry_delay(self, attempt: int) -> float:
        """
        Calculate retry delay with exponential backoff and jitter.

        :param attempt: Current retry attempt (0-indexed)
        :return: Delay in seconds
        """
        # Exponential backoff: delay = initial * 2^attempt
        delay = INITIAL_RETRY_DELAY * (2 ** min(attempt, 32))
        # Cap at maximum delay
        delay = min(delay, MAX_RETRY_DELAY)
        # Add jitter (±10%) to prevent thundering herd
        jitter = delay * RETRY_JITTER * (2 * random.random() - 1)
        return delay + jitter

    async def connect_with_retry(self, max_retries: int | None = None) -> bool:
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
            _LOG.warning(
                f"Connection failed, retrying in {delay:.1f}s (attempt {self._retry_count + 1}/{max_retries + 1})"
            )
            self.events.emit(Events.RECONNECTING, self._retry_count + 1, max_retries + 1)

            await asyncio.sleep(delay)
            self._retry_count += 1

        return False

    async def connect(self) -> bool:
        """
        Connect to the OREI Matrix via HTTPS/HTTP and authenticate.

        Single-flight (BE-11): a call made while another connect is in
        progress waits for that attempt's result instead of logging in again.

        :return: True if connection successful
        """
        task = self._connect_task
        if task is None or task.done():
            task = asyncio.ensure_future(self._connect_once())
            self._connect_task = task
        return await self._await_shared(task)

    @staticmethod
    async def _await_shared(task: "asyncio.Future[bool]") -> bool:
        """Await a shared attempt; its cancellation reads as failure, ours propagates."""
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            current = asyncio.current_task()
            if current is not None and current.cancelling():
                raise
            return False

    def _url(self) -> str:
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.host}:{self.port}/cgi-bin/instr"

    async def _connect_once(self) -> bool:
        """One login attempt, then Telnet. Used through :meth:`connect`."""
        self._intentional_disconnect = False
        reconnecting = self._reconnect_task is not None and not self._reconnect_task.done()
        self._set_state(ConnectionState.CONNECTING)
        try:
            protocol = "https" if self.use_https else "http"
            _LOG.info("Connecting to OREI Matrix at %s://%s:%d", protocol, self.host, self.port)

            # SSL verification is disabled by default. Set OREI_VERIFY_SSL=true
            # to enable strict verification if a CA-signed certificate is installed.
            if not self._session:
                if self.use_https:
                    ssl_enabled = os.environ.get("OREI_VERIFY_SSL", "false").lower() == "true"
                    connector = aiohttp.TCPConnector(ssl=ssl_enabled)
                    if not ssl_enabled:
                        _LOG.warning("SSL verification disabled for matrix connection")
                else:
                    connector = None
                self._session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(), connector=connector)

            _LOG.debug("Authenticating with matrix...")
            logged_in = await self._login()
        except Exception as ex:
            _LOG.error("Failed to connect to OREI Matrix: %s", ex)
            self._last_error = str(ex)
            self.events.emit(Events.ERROR, str(ex))
            logged_in = False

        if not logged_in:
            self._set_state(ConnectionState.BACKOFF if reconnecting else ConnectionState.DISCONNECTED)
            return False

        # HTTP works: usable now (DEGRADED until Telnet is up).
        self._set_state(ConnectionState.DEGRADED)
        self._last_error = None
        self.events.emit(Events.CONNECTED)
        _LOG.info("Successfully authenticated to OREI Matrix via HTTP")

        # Also connect Telnet for CEC and cable detection
        await self._connect_telnet()
        if self.connected:
            self._set_state(self._link_up_state())
        return True

    async def _login(self) -> bool:
        """POST the login command; True only on an explicit success result."""
        # Credentials can be overridden via environment variables
        login_cmd = {
            "comhead": "login",
            "user": os.environ.get("OREI_USER", "Admin"),
            "password": os.environ.get("OREI_PASSWORD", "admin"),
        }
        result = await self._post(login_cmd)
        if result.kind != "ok":
            if result.timeout:
                _LOG.error("Connection timeout to OREI Matrix at %s:%d", self.host, self.port)
                self._last_error = "Connection timeout"
            else:
                _LOG.error("Login request failed: %s", result.error)
                self._last_error = result.error or "Login failed"
            self.events.emit(Events.ERROR, self._last_error)
            return False
        if not is_login_success(result.data):
            _LOG.error("Login failed: %s", result.data)
            self._last_error = "Authentication failed"
            return False
        return True

    async def _relogin(self) -> bool:
        """Re-authenticate once (single-flight) after the session was lost."""
        task = self._relogin_task
        if task is None or task.done():
            task = asyncio.ensure_future(self._login())
            self._relogin_task = task
        ok = await self._await_shared(task)
        if ok:
            _LOG.info("Re-authenticated to OREI Matrix")
        else:
            self._link_lost(f"re-authentication failed: {self._last_error}")
        return ok

    async def _post(self, payload: dict[str, Any]) -> _HttpResult:
        """Send one JSON command and classify the answer.

        ``_command_lock`` is held for this single request only (BE-17).
        """
        session = self._session
        if session is None:
            return _HttpResult("transport", error="No HTTP session")
        _LOG.debug("Sending POST to %s: %s", self._url(), payload if payload.get("comhead") != "login" else "login")
        async with self._command_lock:
            try:
                async with session.post(
                    self._url(), json=payload, timeout=aiohttp.ClientTimeout(total=HTTP_TIMEOUT)
                ) as response:
                    status = response.status
                    # Matrix returns text/plain, so read as text then parse JSON
                    text = await response.text() if status == 200 else ""
            except TimeoutError:
                return _HttpResult("no_answer", error="Command timeout", timeout=True)
            except Exception as ex:  # aiohttp.ClientError, OSError, ...
                return _HttpResult("transport", error=str(ex) or type(ex).__name__)
        return self._classify_response(payload, status, text)

    @staticmethod
    def _classify_response(payload: dict[str, Any], status: int, text: str) -> _HttpResult:
        if status in (401, 403):
            return _HttpResult("auth", error=f"HTTP {status}")
        if status != 200:
            return _HttpResult("http_error", error=f"HTTP {status}")
        _LOG.debug("Command response (raw): %s", text)
        try:
            data = json.loads(text)
        except ValueError as ex:
            if _looks_like_login_page(text):
                return _HttpResult("auth", error="Session expired (login page)")
            _LOG.warning("Could not parse JSON response: %s (raw: %.200s)", ex, text)
            return _HttpResult("bad_response", error=f"Unparseable matrix response: {ex}")
        if not isinstance(data, dict):
            return _HttpResult("bad_response", error="Unparseable matrix response: not a JSON object")
        comhead = payload.get("comhead", "")
        # How the device answers a command sent without a valid session is
        # not captured yet (HIL-14). Reads never carry `result` on success, so
        # a failure result on a read is taken as "not logged in". On a write
        # it is usually a plain rejection (V1.10.01 answers bad parameters with
        # result 0); the caller re-logs in once and retries, and a second
        # failure is reported as a rejected write.
        if comhead != "login" and "result" in data and _normalise_result(data["result"]) in FAILURE_RESULTS:
            return _HttpResult("auth", data=data, error="Matrix returned a failure result (session may have expired)")
        return _HttpResult("ok", data=data)

    async def disconnect(self):
        """Disconnect from the OREI Matrix (both HTTP and Telnet).

        Intentional: no reconnect is scheduled afterwards.
        """
        self._intentional_disconnect = True
        await cancel_and_wait(self._reconnect_task, "matrix_reconnect")
        self._reconnect_task = None
        for attr in ("_connect_task", "_relogin_task"):
            pending = getattr(self, attr)
            if isinstance(pending, asyncio.Task):
                await cancel_and_wait(pending, attr)
            setattr(self, attr, None)

        # Disconnect Telnet first
        await self._dispose_telnet()

        # Clear caches on disconnect to prevent stale data
        self.clear_cec_cache()
        self._invalidate_status_caches()

        if self._session:
            try:
                await self._session.close()
            except Exception as ex:
                _LOG.warning("Error closing session: %s", ex)
        self._session = None
        self._set_state(ConnectionState.DISCONNECTED)
        self.events.emit(Events.DISCONNECTED)
        _LOG.info("Disconnected from OREI Matrix")

    def _check_write(self, success: bool, response: dict | None, command: dict[str, Any]) -> bool:
        """Report whether a write was accepted (BE-12), logging why not.

        A write succeeds only if the matrix answered with a success ``result``
        (see :func:`is_write_success`); HTTP 200 alone proves nothing.
        """
        comhead = command.get("comhead", "?")
        if not success:
            _LOG.error("Write '%s' failed: no valid answer from the matrix (%s)", comhead, self._last_error)
            return False
        if is_write_success(response):
            return True
        result = response.get("result") if isinstance(response, dict) else None
        args = {k: v for k, v in command.items() if k not in ("comhead", "language")}
        _LOG.error("Matrix rejected '%s' %s (result=%r)", comhead, args, result)
        self._last_error = f"Matrix rejected '{comhead}' (result={result!r})"
        return False

    def _invalidate_status_caches(self) -> None:
        self._cache_generation += 1
        self._status_cache = None
        self._output_status_cache = None
        self._input_status_cache = None
        self._cable_status_cache = None

    async def _send_command(self, command: dict, retry_on_failure: bool = True) -> tuple[bool, dict | None]:
        """
        Send a JSON command to the matrix via HTTP POST.

        - Not connected: one single-flight connect attempt first (no backoff
          sleep, no lock held -- BE-17).
        - Session lost (HTTP 401/403, login page, failure ``result``): one
          re-login and one retry when ``retry_on_failure`` (BE-04).
        - No answer (timeout), HTTP error status or unparseable answer
          (HIL-12): the command fails ("device did not answer"); a health
          read decides whether the link is still up. Only if that read fails
          too is the link marked lost.
        - Transport error (refused, reset, DNS, TLS): the link is marked
          lost (BACKOFF + ``Events.DISCONNECTED``) and the command fails.
        - A write the matrix answered with a failure ``result`` returns
          ``(True, response)`` so the caller reports the rejection (BE-12).

        :param command: Command dictionary to send as JSON
        :param retry_on_failure: Whether to re-login and retry once on a session failure
        :return: Tuple of (success, response_dict)
        """
        if not self._session or not self.connected:
            _LOG.warning("No session or not connected, attempting to connect...")
            if not await self.connect():
                return False, None

        comhead = command.get("comhead", "")
        is_read = _is_read_command(comhead)

        result = await self._post(command)
        if result.kind == "auth" and retry_on_failure:
            _LOG.warning("Matrix answered '%s' with '%s'; re-authenticating once", comhead, result.error)
            relogged = await self._relogin()
            # A JSON failure result on a write is ambiguous (expired session or
            # plain rejection); resending a non-idempotent command could run it
            # twice, so only unambiguous session loss (no JSON body) is resent.
            ambiguous = result.data is not None and not is_read
            if relogged and not (ambiguous and comhead in NON_IDEMPOTENT_COMMANDS):
                result = await self._post(command)

        if result.kind == "ok" or (result.kind == "auth" and result.data is not None and not is_read):
            if not is_read:
                # Invalidate status caches on state-changing/write commands
                _LOG.debug("Invalidating all status caches due to write command: %s", comhead)
                self._invalidate_status_caches()
            return True, result.data

        self._last_error = result.error
        if result.kind == "auth":
            _LOG.error("Command '%s' failed: %s", comhead, result.error)
            return False, None

        if result.kind in ("no_answer", "http_error", "bad_response"):
            # HIL-12: the device ignores commands it does not implement. One
            # unanswered command is a failed command; the link is only lost
            # if a health read fails as well.
            if result.kind == "no_answer":
                _LOG.error("Matrix: device did not answer '%s' within %.1fs", comhead, HTTP_TIMEOUT)
                self._last_error = f"device did not answer '{comhead}'"
            else:
                _LOG.error("Matrix: bad answer to '%s': %s", comhead, result.error)
            if await self._link_healthy():
                return False, None
            self._link_lost(f"no answer to '{comhead}' and to the health read")
            return False, None

        # Transport error: the connection itself failed.
        _LOG.error("Failed to send command '%s': %s", comhead, result.error)
        self.events.emit(Events.ERROR, result.error)
        self._link_lost(result.error)
        return False, None

    async def _link_healthy(self) -> bool:
        """Health read after a failed command (HIL-12): does the matrix still answer?

        Any answer counts (even "not logged in": the device is reachable).
        A transport error means the link is gone; a timeout is retried once,
        because the device's web server can stall for one request right after
        a command it ignored (captured on V1.10.01).
        """
        for attempt in range(1, HEALTH_CHECK_ATTEMPTS + 1):
            result = await self._post(dict(HEALTH_CHECK_COMMAND))
            if result.kind in ("ok", "auth"):
                _LOG.info("Matrix health read answered; the connection is still up")
                return True
            _LOG.warning("Matrix health read %d/%d failed: %s", attempt, HEALTH_CHECK_ATTEMPTS, result.error)
            if result.kind == "transport":
                return False
        return False

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
        command = {"comhead": "preset set", "language": 0, "index": scene}

        success, response = await self._send_command(command)

        if self._check_write(success, response, command):
            _LOG.info("✓ Preset %d recalled successfully (confirmed by matrix)", scene)
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

    async def get_preset_info(self, preset: int) -> dict | None:
        """
        Get information about a specific preset.

        :param preset: Preset number (1-8)
        :return: Dictionary with preset info, or None if failed
        """
        if preset < 1 or preset > 8:
            _LOG.error("Invalid preset number: %d. Must be 1-8", preset)
            return None

        # Telnet `r preset N` is the only preset read this firmware answers.
        # HIL-01: MCU V1.10.01 never answers the HTTP `preset get` or
        # `get routing status` (the capture timed out on both), so there is no
        # HTTP fallback: it would only block for the whole HTTP timeout.
        if self._telnet and self._telnet.connected:
            try:
                return await self._telnet.get_preset_info(preset)
            except Exception as e:
                _LOG.warning(f"Failed to get preset info from Telnet client: {e}")
                return None

        _LOG.warning(
            "Cannot read preset %d: Telnet is not connected, and the matrix firmware does not implement "
            "an HTTP preset read ('preset get' / 'get routing status' go unanswered, HIL-01)",
            preset,
        )
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

                # MCU V1.10.01 sends plain names ("NES", "SNES", ...: capture
                # http/get_video_status). Only strip an "IN01-" style prefix if
                # one is there; splitting on any "-" cut names like "Sega-CD".
                # Only process up to 8 inputs (matrix is 8x8); ignore any terminator entries
                for idx, name in enumerate(raw_input_names[:8]):
                    input_num = idx + 1  # Convert 0-based index to 1-based input number

                    prefixed = re.match(r"^IN\d+-(.*)$", name, re.IGNORECASE) if isinstance(name, str) else None
                    if prefixed:
                        device_name = prefixed.group(1).strip()
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
        command = {"comhead": "video switch", "language": 0, "source": [output_num, input_num]}

        success, response = await self._send_command(command)

        if self._check_write(success, response, command):
            _LOG.info("✓ Input %d switched to output %d (confirmed)", input_num, output_num)
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
        command = {"comhead": "video switch", "language": 0, "source": [0, input_num]}

        success, response = await self._send_command(command)

        # BE-12: this used to report success even when the matrix rejected it.
        if self._check_write(success, response, command):
            _LOG.info("✓ Input %d switched to all outputs (confirmed)", input_num)
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
        command = {"comhead": "set poweronoff", "language": 0, "power": 1}

        success, response = await self._send_command(command)

        if self._check_write(success, response, command):
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
        command = {"comhead": "set poweronoff", "language": 0, "power": 0}

        success, response = await self._send_command(command)

        if self._check_write(success, response, command):
            _LOG.info("✓ Matrix powered OFF (confirmed)")
            self.events.emit(Events.UPDATE, {"power": "off"})
            return True

        _LOG.error("Failed to power off matrix")
        return False

    async def get_video_status(self) -> dict[str, Any] | None:
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
        command = {"comhead": "get video status", "language": 0}

        success, response = await self._send_command(command)

        if success and response:
            _LOG.debug("Video status: %s", response)
            self._last_successful_poll = datetime.datetime.now(datetime.UTC)
            return response

        _LOG.error("Failed to get video status")
        return None

    async def get_status(self, force_refresh: bool = False) -> dict[str, Any]:
        """
        Get the current status of the matrix.

        Served from a cache younger than ``OREI_STATUS_CACHE_TTL`` (default
        3 s) unless ``force_refresh``; concurrent refreshes share one request.

        :param force_refresh: Force update from physical switcher even if cache is fresh.
        :return: Dictionary with status information
        """
        if not force_refresh and self._status_cache is not None and self._cache_fresh(self._status_cache_time):
            _LOG.debug("Returning cached status (cache age: %.2fs)", time.time() - self._status_cache_time)
            return self._status_cache.copy()
        return (await self._single_flight("status", self._fetch_status)).copy()

    async def _fetch_status(self) -> dict[str, Any]:
        generation = self._cache_generation
        # Get detailed video status from matrix
        video_status = await self.get_video_status()

        status = {
            "connected": self.connected,
            "host": self.host,
            "port": self.port,
            "current_scene": self._current_scene,
            "last_error": self._last_error,
        }

        if video_status:
            status.update(
                {
                    "power": "on" if video_status.get("power") == 1 else "off",
                    "routing": per_output(video_status.get("allsource")),
                    "input_names": video_status.get("allinputname", []),
                    "output_names": video_status.get("alloutputname", []),
                    "preset_names": video_status.get("allname", []),
                }
            )
            if generation == self._cache_generation:  # no write landed meanwhile
                self._status_cache = status.copy()
                self._status_cache_time = time.time()
        return status

    # =========================================================================
    # Status snapshot helpers (BE-03)
    # =========================================================================

    def _cache_fresh(self, cache_time: float) -> bool:
        """Whether a cache written at ``cache_time`` is younger than the TTL."""
        return time.time() - cache_time < self._status_cache_ttl

    async def _single_flight(self, key: str, fetch: Callable[[], Awaitable[_T]]) -> _T:
        """Run ``fetch`` once for all concurrent callers of the same ``key``.

        A caller that arrives after a write invalidated the caches (new cache
        generation) starts its own fetch instead of joining one that may have
        read the old state.
        """
        generation = self._cache_generation
        entry = self._inflight.get(key)
        if entry is not None and entry[0] == generation and not entry[1].done():
            task = entry[1]
        else:
            task = asyncio.ensure_future(fetch())
            self._inflight[key] = (generation, task)

            def _forget(done: asyncio.Future, key: str = key) -> None:
                current = self._inflight.get(key)
                if current is not None and current[1] is done:
                    del self._inflight[key]

            task.add_done_callback(_forget)
        return await asyncio.shield(task)

    # =========================================================================
    # CEC Control Methods
    # =========================================================================

    # CEC command indices for the HTTP ``cec command`` (object 0 = source
    # device). Kept as class constants for existing callers; the tables live
    # in device_codes (VAL-03, BE-14).
    CEC_POWER_ON = CEC_INPUT_COMMANDS["POWER_ON"]
    CEC_POWER_OFF = CEC_INPUT_COMMANDS["POWER_OFF"]
    CEC_UP = CEC_INPUT_COMMANDS["UP"]
    CEC_LEFT = CEC_INPUT_COMMANDS["LEFT"]
    CEC_SELECT = CEC_INPUT_COMMANDS["SELECT"]
    CEC_RIGHT = CEC_INPUT_COMMANDS["RIGHT"]
    CEC_MENU = CEC_INPUT_COMMANDS["MENU"]
    CEC_DOWN = CEC_INPUT_COMMANDS["DOWN"]
    CEC_BACK = CEC_INPUT_COMMANDS["BACK"]
    CEC_PREVIOUS = CEC_INPUT_COMMANDS["PREVIOUS"]
    CEC_PLAY = CEC_INPUT_COMMANDS["PLAY"]
    CEC_NEXT = CEC_INPUT_COMMANDS["NEXT"]
    CEC_REWIND = CEC_INPUT_COMMANDS["REWIND"]
    CEC_PAUSE = CEC_INPUT_COMMANDS["PAUSE"]
    CEC_FAST_FORWARD = CEC_INPUT_COMMANDS["FAST_FORWARD"]
    CEC_STOP = CEC_INPUT_COMMANDS["STOP"]
    CEC_MUTE = CEC_INPUT_COMMANDS["MUTE"]
    CEC_VOLUME_DOWN = CEC_INPUT_COMMANDS["VOLUME_DOWN"]
    CEC_VOLUME_UP = CEC_INPUT_COMMANDS["VOLUME_UP"]

    #: Every CEC command name the hub knows, with its source-device (input)
    #: index. Displays (outputs) use :attr:`CEC_OUTPUT_COMMAND_MAP`, a different
    #: 0-based table of six commands (BE-14).
    CEC_COMMAND_MAP: dict[str, int] = dict(CEC_INPUT_COMMANDS)
    #: CEC commands a display (output) accepts, with the device's output index.
    CEC_OUTPUT_COMMAND_MAP: dict[str, int] = dict(CEC_OUTPUT_COMMANDS)

    # CEC command name -> Telnet word (``s cec in N <word>`` / ``s cec hdmi out N <word>``)
    _CEC_NAME_TO_TELNET = {
        "POWER_ON": "on",
        "POWER_OFF": "off",
        "UP": "up",
        "LEFT": "left",
        "SELECT": "enter",
        "RIGHT": "right",
        "MENU": "menu",
        "DOWN": "down",
        "BACK": "back",
        "PREVIOUS": "previous",
        "PLAY": "play",
        "NEXT": "next",
        "REWIND": "rew",
        "PAUSE": "pause",
        "FAST_FORWARD": "ff",
        "STOP": "stop",
        "MUTE": "mute",
        "VOLUME_DOWN": "vol-",
        "VOLUME_UP": "vol+",
        "ACTIVE": "active",
    }
    # Input index -> Telnet word (kept for callers of the old name).
    _CEC_INDEX_TO_TELNET = {CEC_INPUT_COMMANDS[name]: word for name, word in _CEC_NAME_TO_TELNET.items()
                            if name in CEC_INPUT_COMMANDS}

    async def send_cec(self, command: str, port: int, is_output: bool = False) -> bool:
        """
        Send a CEC command by name to an input or output device.

        Sources (inputs) accept every name in :attr:`CEC_COMMAND_MAP`;
        displays (outputs) only the six in :attr:`CEC_OUTPUT_COMMAND_MAP`
        (power on/off, mute, volume up/down, active). Each side has its own
        index table on the device (BE-14).

        :param command: Command name (e.g., "POWER_ON", "VOLUME_UP", "PLAY")
        :param port: Port number (1-8)
        :param is_output: True for output device (TV), False for input device (source)
        :return: True if command sent successfully

        Example:
            await matrix.send_cec("POWER_ON", 1, is_output=True)  # Turn on TV 1
            await matrix.send_cec("PLAY", 3, is_output=False)    # Play on source 3
        """
        name = command.upper()
        table = self.CEC_OUTPUT_COMMAND_MAP if is_output else self.CEC_COMMAND_MAP
        command_index = table.get(name)
        if command_index is None:
            _LOG.error(
                "CEC command %s is not available for %s devices. Valid commands: %s",
                command,
                "output" if is_output else "input",
                list(table.keys()),
            )
            return False

        return await self._send_cec_command(port, command_index, is_output, name=name)

    async def _send_cec_command(
        self, port_num: int, command_index: int, is_output: bool = False, *, name: str | None = None
    ) -> bool:
        """
        Send a CEC command to an input or output device.

        Uses Telnet when enabled (``OREI_USE_TELNET_CEC``), otherwise HTTP.
        Automatically ensures CEC is enabled on the target port before sending.

        :param port_num: Port number (1-8)
        :param command_index: CEC command index from the input (1-19) or output (0-5) table
        :param is_output: True for output device (TV), False for input device (source)
        :return: True if command sent successfully
        """
        if port_num < 1 or port_num > 8:
            _LOG.error("Invalid port number: %d. Must be 1-8", port_num)
            return False

        table = self.CEC_OUTPUT_COMMAND_MAP if is_output else self.CEC_COMMAND_MAP
        by_index = {index: cmd_name for cmd_name, index in table.items()}
        if command_index not in by_index:
            _LOG.error(
                "Invalid %s CEC command index: %d. Must be one of %s",
                "output" if is_output else "input",
                command_index,
                sorted(by_index),
            )
            return False
        name = name or by_index[command_index]

        # Ensure CEC is enabled on the target port (auto-enables if needed)
        cec_enabled = await self.ensure_cec_enabled(port_num, is_output)
        if not cec_enabled:
            _LOG.warning(
                "Could not ensure CEC enabled on %s %d, attempting command anyway",
                "output" if is_output else "input",
                port_num,
            )

        # Telnet (opt-in, faster persistent connection)
        if self._use_telnet_cec and self._telnet and self._telnet.connected:
            telnet_cmd = self._CEC_NAME_TO_TELNET.get(name)
            if telnet_cmd:
                try:
                    if is_output:
                        success = await self._telnet._send_cec_output(port_num, telnet_cmd)
                    else:
                        success = await self._telnet._send_cec_input(port_num, telnet_cmd)

                    if success:
                        _LOG.debug(
                            "CEC via Telnet: %s %d -> %s", "output" if is_output else "input", port_num, telnet_cmd
                        )
                        return True
                except Exception as e:
                    _LOG.warning(f"Telnet CEC failed, falling back to HTTP: {e}")

        # Fall back to HTTP
        _LOG.debug("CEC via HTTP: %s %d -> index %d", "output" if is_output else "input", port_num, command_index)

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
            "index": command_index,
        }

        _LOG.debug("Sending CEC command: %s", command)
        success, response = await self._send_command(command)

        if self._check_write(success, response, command):
            _LOG.info("✓ CEC %s sent to %s %d", name, "output" if is_output else "input", port_num)
            return True

        _LOG.error("Failed to send CEC %s to %s %d", name, "output" if is_output else "input", port_num)
        return False

    # Input CEC Control Methods (for source devices like PS3, Apple TV, etc.)

    async def cec_input_power_on(self, input_num: int) -> bool:
        """Send Power On CEC command to an input device."""
        return await self.send_cec("POWER_ON", input_num, is_output=False)

    async def cec_input_power_off(self, input_num: int) -> bool:
        """Send Power Off CEC command to an input device."""
        return await self.send_cec("POWER_OFF", input_num, is_output=False)

    async def cec_input_up(self, input_num: int) -> bool:
        """Send Up navigation CEC command to an input device."""
        return await self.send_cec("UP", input_num, is_output=False)

    async def cec_input_down(self, input_num: int) -> bool:
        """Send Down navigation CEC command to an input device."""
        return await self.send_cec("DOWN", input_num, is_output=False)

    async def cec_input_left(self, input_num: int) -> bool:
        """Send Left navigation CEC command to an input device."""
        return await self.send_cec("LEFT", input_num, is_output=False)

    async def cec_input_right(self, input_num: int) -> bool:
        """Send Right navigation CEC command to an input device."""
        return await self.send_cec("RIGHT", input_num, is_output=False)

    async def cec_input_select(self, input_num: int) -> bool:
        """Send Select/Enter CEC command to an input device."""
        return await self.send_cec("SELECT", input_num, is_output=False)

    async def cec_input_menu(self, input_num: int) -> bool:
        """Send Menu CEC command to an input device."""
        return await self.send_cec("MENU", input_num, is_output=False)

    async def cec_input_back(self, input_num: int) -> bool:
        """Send Back/Return CEC command to an input device."""
        return await self.send_cec("BACK", input_num, is_output=False)

    async def cec_input_play(self, input_num: int) -> bool:
        """Send Play CEC command to an input device."""
        return await self.send_cec("PLAY", input_num, is_output=False)

    async def cec_input_pause(self, input_num: int) -> bool:
        """Send Pause CEC command to an input device."""
        return await self.send_cec("PAUSE", input_num, is_output=False)

    async def cec_input_stop(self, input_num: int) -> bool:
        """Send Stop CEC command to an input device."""
        return await self.send_cec("STOP", input_num, is_output=False)

    async def cec_input_previous(self, input_num: int) -> bool:
        """Send Previous CEC command to an input device."""
        return await self.send_cec("PREVIOUS", input_num, is_output=False)

    async def cec_input_next(self, input_num: int) -> bool:
        """Send Next CEC command to an input device."""
        return await self.send_cec("NEXT", input_num, is_output=False)

    async def cec_input_rewind(self, input_num: int) -> bool:
        """Send Rewind CEC command to an input device."""
        return await self.send_cec("REWIND", input_num, is_output=False)

    async def cec_input_fast_forward(self, input_num: int) -> bool:
        """Send Fast Forward CEC command to an input device."""
        return await self.send_cec("FAST_FORWARD", input_num, is_output=False)

    async def cec_input_volume_up(self, input_num: int) -> bool:
        """Send Volume Up CEC command to an input device."""
        return await self.send_cec("VOLUME_UP", input_num, is_output=False)

    async def cec_input_volume_down(self, input_num: int) -> bool:
        """Send Volume Down CEC command to an input device."""
        return await self.send_cec("VOLUME_DOWN", input_num, is_output=False)

    async def cec_input_mute(self, input_num: int) -> bool:
        """Send Mute CEC command to an input device."""
        return await self.send_cec("MUTE", input_num, is_output=False)

    # Output CEC Control Methods (for displays). A display only has the six
    # commands of CEC_OUTPUT_COMMAND_MAP; the navigation helpers below are
    # kept for callers and fail (return False) because the device has no
    # output index for them (BE-14).

    async def cec_output_power_on(self, output_num: int) -> bool:
        """Send Power On CEC command to an output device."""
        return await self.send_cec("POWER_ON", output_num, is_output=True)

    async def cec_output_power_off(self, output_num: int) -> bool:
        """Send Power Off CEC command to an output device."""
        return await self.send_cec("POWER_OFF", output_num, is_output=True)

    async def cec_output_up(self, output_num: int) -> bool:
        """Not supported by the device's output CEC table (returns False)."""
        return await self.send_cec("UP", output_num, is_output=True)

    async def cec_output_down(self, output_num: int) -> bool:
        """Not supported by the device's output CEC table (returns False)."""
        return await self.send_cec("DOWN", output_num, is_output=True)

    async def cec_output_left(self, output_num: int) -> bool:
        """Not supported by the device's output CEC table (returns False)."""
        return await self.send_cec("LEFT", output_num, is_output=True)

    async def cec_output_right(self, output_num: int) -> bool:
        """Not supported by the device's output CEC table (returns False)."""
        return await self.send_cec("RIGHT", output_num, is_output=True)

    async def cec_output_select(self, output_num: int) -> bool:
        """Not supported by the device's output CEC table (returns False)."""
        return await self.send_cec("SELECT", output_num, is_output=True)

    async def cec_output_menu(self, output_num: int) -> bool:
        """Not supported by the device's output CEC table (returns False)."""
        return await self.send_cec("MENU", output_num, is_output=True)

    async def cec_output_back(self, output_num: int) -> bool:
        """Not supported by the device's output CEC table (returns False)."""
        return await self.send_cec("BACK", output_num, is_output=True)

    async def cec_output_volume_up(self, output_num: int) -> bool:
        """Send Volume Up CEC command to an output device."""
        return await self.send_cec("VOLUME_UP", output_num, is_output=True)

    async def cec_output_volume_down(self, output_num: int) -> bool:
        """Send Volume Down CEC command to an output device."""
        return await self.send_cec("VOLUME_DOWN", output_num, is_output=True)

    async def cec_output_mute(self, output_num: int) -> bool:
        """Send Mute CEC command to an output device."""
        return await self.send_cec("MUTE", output_num, is_output=True)

    async def cec_output_active(self, output_num: int) -> bool:
        """Send the output pad's "active/input" CEC command to a display."""
        return await self.send_cec("ACTIVE", output_num, is_output=True)

    # =========================================================================
    # Extended Status Methods (discovered from HAR capture)
    # =========================================================================

    async def get_output_status(self, force_refresh: bool = False) -> dict[str, Any] | None:
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

        Cached for ``OREI_STATUS_CACHE_TTL`` seconds (BE-03: the cache used to
        never expire); concurrent refreshes share one request.
        """
        if (
            not force_refresh
            and self._output_status_cache is not None
            and self._cache_fresh(self._output_status_cache_time)
        ):
            return self._output_status_cache.copy()
        response = await self._single_flight("output_status", self._fetch_output_status)
        return response.copy() if response is not None else None

    async def _fetch_output_status(self) -> dict[str, Any] | None:
        generation = self._cache_generation
        _LOG.debug("Getting output status")

        command = {"comhead": "get output status", "language": 0}
        success, response = await self._send_command(command)

        if success and response:
            _LOG.debug("Output status: %s", response)
            if generation == self._cache_generation:
                self._output_status_cache = response.copy()
                self._output_status_cache_time = time.time()
            return response

        _LOG.error("Failed to get output status")
        return None

    async def get_input_status(self, force_refresh: bool = False) -> dict[str, Any] | None:
        """
        Get detailed input status including signal detection.

        :return: Dictionary with input status or None if failed
        Returns:
            - power: 1 (on) or 0 (off)
            - edid: EDID mode per input
            - inactive: array showing inactive inputs (signal detection)
            - inname: array of input names

        Cached for ``OREI_STATUS_CACHE_TTL`` seconds (BE-03); concurrent
        refreshes share one request.
        """
        if (
            not force_refresh
            and self._input_status_cache is not None
            and self._cache_fresh(self._input_status_cache_time)
        ):
            return self._input_status_cache.copy()
        response = await self._single_flight("input_status", self._fetch_input_status)
        return response.copy() if response is not None else None

    async def _fetch_input_status(self) -> dict[str, Any] | None:
        generation = self._cache_generation
        _LOG.debug("Getting input status")

        command = {"comhead": "get input status", "language": 0}
        success, response = await self._send_command(command)

        if success and response:
            _LOG.debug("Input status: %s", response)
            if generation == self._cache_generation:
                self._input_status_cache = response.copy()
                self._input_status_cache_time = time.time()
            return response

        _LOG.error("Failed to get input status")
        return None

    # =========================================================================
    # Cable Detection Methods (via Telnet)
    # =========================================================================

    async def get_input_cable_status(self, input_num: int) -> bool | None:
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

    async def get_output_cable_status(self, output_num: int) -> bool | None:
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
                telnet_result = await self._telnet.get_output_connection(output_num)
                if telnet_result is not None:
                    return telnet_result
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

    async def get_all_cable_status(self, force_refresh: bool = False) -> dict[str, dict[int, bool | None]]:
        """
        Get cable connection status for all inputs and outputs.

        Queries each port individually via Telnet for accurate detection,
        falling back to HTTP for outputs if Telnet unavailable.

        :return: Dict with 'inputs' and 'outputs' sub-dicts mapping port -> connected
            (None = unknown)

        Cached for ``OREI_STATUS_CACHE_TTL`` seconds (BE-03); concurrent
        refreshes share one ``status!``.
        """
        if (
            not force_refresh
            and self._cable_status_cache is not None
            and self._cache_fresh(self._cable_status_cache_time)
        ):
            return _copy_cables(self._cable_status_cache)
        result = await self._single_flight("cable_status", lambda: self._fetch_cable_status(force_refresh))
        return _copy_cables(result)

    async def _fetch_cable_status(self, force_refresh: bool) -> dict[str, dict[int, bool | None]]:
        generation = self._cache_generation
        result: dict[str, dict[int, bool | None]] = {
            "inputs": dict.fromkeys(range(1, 9)),
            "outputs": dict.fromkeys(range(1, 9)),
        }

        # One Telnet `status!` gives every input and output (BE-30: this used
        # to send it twice). Ports missing from the dump stay None (BE-29).
        if self._telnet and self._telnet.connected:
            try:
                result = await self._telnet.get_all_connections()
            except Exception as e:
                _LOG.warning(f"Failed to get cable status via Telnet: {e}")

        # Outputs Telnet did not report: fall back to HTTP 'allconnect'
        # (inputs are not available via HTTP and stay None = unknown).
        if any(v is None for v in result["outputs"].values()):
            output_status = await self.get_output_status(force_refresh=force_refresh)
            allconnect = output_status.get("allconnect") if output_status else None
            if isinstance(allconnect, list):
                for i, connected in enumerate(allconnect[:8]):
                    if result["outputs"].get(i + 1) is None:
                        result["outputs"][i + 1] = connected == 1

        if generation == self._cache_generation:
            self._cable_status_cache = _copy_cables(result)
            self._cable_status_cache_time = time.time()
        return result

    async def get_telnet_full_status(self) -> MatrixStatus | None:
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

    async def get_cec_status(self) -> dict[str, Any] | None:
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
            await self._update_cec_cache(response)
            return response

        _LOG.error("Failed to get CEC status")
        return None

    async def _update_cec_cache(self, cec_status: dict) -> None:
        """
        Update the CEC enabled cache from a get cec status response.

        Thread-safe under ``_cec_cache_lock`` so concurrent CEC commands
        cannot observe a torn cache state during refresh.

        :param cec_status: Response from get cec status command
        """
        import datetime

        async with self._cec_cache_lock:
            if "inputindex" in cec_status:
                for i, val in enumerate(cec_status["inputindex"][:8]):
                    self._cec_enabled_cache["inputs"][i] = val == 1

            if "outputindex" in cec_status:
                for i, val in enumerate(cec_status["outputindex"][:8]):
                    self._cec_enabled_cache["outputs"][i] = val == 1

            self._cec_enabled_cache["last_updated"] = datetime.datetime.now()
            _LOG.debug(
                "CEC cache updated: inputs=%s, outputs=%s",
                self._cec_enabled_cache["inputs"],
                self._cec_enabled_cache["outputs"],
            )

    async def _is_cec_cache_valid(self) -> bool:
        """
        Check if the CEC cache is still valid (not expired).

        Thread-safe under ``_cec_cache_lock`` so the validity check and
        subsequent cache read see a consistent ``last_updated`` timestamp.

        :return: True if cache is valid and fresh
        """
        import datetime

        async with self._cec_cache_lock:
            if self._cec_enabled_cache["last_updated"] is None:
                return False
            age = (
                datetime.datetime.now() - self._cec_enabled_cache["last_updated"]
            ).total_seconds()
            return age < self._cec_cache_ttl

    def clear_cec_cache(self):
        """
        Clear the CEC enabled cache.

        Called on disconnect to prevent stale data when reconnecting.
        """
        self._cec_enabled_cache = {
            "inputs": [False] * 8,
            "outputs": [False] * 8,
            "last_updated": None,
        }

    async def is_cec_enabled(self, port_num: int, is_output: bool = False) -> bool | None:
        """
        Check if CEC is enabled on a specific port from cache.

        Thread-safe under ``_cec_cache_lock`` — the validity check and the
        cache read are performed atomically so callers see a consistent
        snapshot of CEC enablement state.

        :param port_num: Port number (1-8)
        :param is_output: True for output, False for input
        :return: True/False from cache, or None if cache is stale
        """
        if not await self._is_cec_cache_valid():
            return None

        if port_num < 1 or port_num > 8:
            return None

        async with self._cec_cache_lock:
            cache_key = "outputs" if is_output else "inputs"
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
        is_enabled = await self.is_cec_enabled(port_num, is_output)
        if is_enabled is None:
            _LOG.debug("CEC cache stale, refreshing...")
            if not await self.refresh_cec_status():
                _LOG.warning("Failed to refresh CEC status, proceeding anyway")
                # Proceed without knowing - let the command try
                return True
            is_enabled = await self.is_cec_enabled(port_num, is_output)

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
        if not await self._is_cec_cache_valid():
            await self.refresh_cec_status()

        # Build the new arrays preserving existing state
        async with self._cec_cache_lock:
            input_array = [1 if self._cec_enabled_cache["inputs"][i] else 0 for i in range(8)]
            output_array = [1 if self._cec_enabled_cache["outputs"][i] else 0 for i in range(8)]

        # Update the target port
        if is_output:
            output_array[port_num - 1] = 1 if enabled else 0
        else:
            input_array[port_num - 1] = 1 if enabled else 0

        # Send the command
        command = {"comhead": "set cec index", "language": 0, "inputindex": input_array, "outputindex": output_array}

        _LOG.debug("Setting CEC index: %s", command)
        success, response = await self._send_command(command)

        if self._check_write(success, response, command):
            # Update cache immediately
            if is_output:
                self._cec_enabled_cache["outputs"][port_num - 1] = enabled
            else:
                self._cec_enabled_cache["inputs"][port_num - 1] = enabled

            _LOG.info(
                "✓ CEC %s on %s %d", "enabled" if enabled else "disabled", "output" if is_output else "input", port_num
            )
            return True

        _LOG.error("Failed to set CEC enabled on %s %d", "output" if is_output else "input", port_num)
        return False

    # NOTE: get_ext_audio_status() is defined once, in the ext-audio section
    # below. An earlier duplicate definition here was always shadowed by it
    # (ruff F811) and has been removed without changing runtime behaviour.

    async def get_system_status(self) -> dict[str, Any] | None:
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

    async def get_network_info(self) -> dict[str, Any] | None:
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

    async def get_device_info(self) -> dict[str, Any] | None:
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

        command = {"comhead": "set panel lock", "language": 0, "lock": 1 if locked else 0}

        success, response = await self._send_command(command)

        if self._check_write(success, response, command):
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

        command = {"comhead": "set beep", "language": 0, "beep": 1 if enabled else 0}

        success, response = await self._send_command(command)

        if self._check_write(success, response, command):
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
            "outputindex": [1 if p else 0 for p in output_ports],
        }

        success, response = await self._send_command(command)

        if self._check_write(success, response, command):
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
            status["routing"] = per_output(video_status.get("allsource"))
            status["input_names"] = video_status.get("allinputname", [])
            status["output_names"] = video_status.get("alloutputname", [])
            status["preset_names"] = video_status.get("allname", [])

        if output_status:
            status["outputs_connected"] = output_status.get("allconnect", [])
            # HDR/scaler as API values (1-based, like the setters), HIL-02
            settings = api_output_settings(output_status)
            status["output_scaler"] = settings["scaler"]
            status["output_hdr"] = settings["hdr"]
            status["output_hdcp"] = settings["hdcp"]
            status["output_arc"] = per_output(output_status.get("allarc"))
            status["output_enabled"] = per_output(output_status.get("allout"))
            status["output_muted"] = per_output(output_status.get("allaudiomute"))

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
                # Only process up to 8 outputs (matrix is 8x8); ignore any terminator entries
                for idx, name in enumerate(names[:8]):
                    output_names[idx + 1] = name if name else f"Output {idx + 1}"
            else:
                for i in range(1, 9):
                    output_names[i] = f"Output {i}"
        except Exception as e:
            _LOG.error(f"Error getting output names: {e}")
            for i in range(1, 9):
                output_names[i] = f"Output {i}"

        return output_names

    async def is_output_connected(self, output_num: int) -> bool | None:
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

    async def get_current_input_for_output(self, output_num: int) -> int | None:
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

        command = {"comhead": "set input name", "language": 0, "name": name, "index": input_num}

        success, response = await self._send_command(command)

        if self._check_write(success, response, command):
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

        command = {"comhead": "set output name", "language": 0, "name": name, "index": output_num}

        success, response = await self._send_command(command)

        if self._check_write(success, response, command):
            _LOG.info("✓ Output %d renamed to: %s", output_num, name)
            self.events.emit(Events.UPDATE, {"output_name": {output_num: name}})
            return True

        _LOG.error("Failed to set output %d name", output_num)
        return False

    # =========================================================================
    # OUTPUT SETTINGS (HIL-09)
    #
    # MCU V1.10.01 never answers the commands the hub used to send here
    # (``set output stream|hdcp|hdr|scaler|arc|mute``: captured, HIL-09). The
    # commands and payload shapes below are the ones the device's own web
    # interface sends: ``{"comhead": ..., "language": 0, <key>: [port, value]}``,
    # port 0 = all outputs. Value codes and the API -> device mapping live in
    # ``device_codes``. Status per command: docs/OREI_API_COMMANDS.md.
    # =========================================================================

    async def _write(self, command: dict[str, Any], what: str) -> bool:
        """Send one write, log the outcome, return whether the matrix accepted it."""
        _LOG.info("Setting %s", what)
        success, response = await self._send_command(command)
        if self._check_write(success, response, command):
            return True
        _LOG.error("Failed to set %s", what)
        return False

    @staticmethod
    def _valid_output(output_num: int) -> bool:
        if 1 <= output_num <= OUTPUT_COUNT:
            return True
        _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
        return False

    async def set_output_enable(self, output_num: int, enable: bool) -> bool:
        """
        Enable or disable the video stream of an output (``tx stream``).

        :param output_num: Output number (1-8)
        :param enable: True to enable output, False to disable (blank)
        :return: True if the matrix accepted the command
        """
        if not self._valid_output(output_num):
            return False
        command = {"comhead": "tx stream", "language": 0, "out": [output_num, 1 if enable else 0]}
        return await self._write(command, f"output {output_num} stream {'on' if enable else 'off'}")

    async def set_output_hdcp(self, output_num: int, mode: int) -> bool:
        """
        Set the HDCP mode of an output (``tx hdcp``).

        :param output_num: Output number (1-8)
        :param mode: HDCP mode (1=HDCP 1.4, 2=HDCP 2.2, 3=Follow Sink, 4=Follow Source, 5=User Mode)
        :return: True if the matrix accepted the command
        """
        if not self._valid_output(output_num):
            return False
        if mode not in HDCP_MODES:
            _LOG.error("Invalid HDCP mode: %d. Must be 1-5", mode)
            return False
        command = {"comhead": "tx hdcp", "language": 0, "hdcp": [output_num, mode]}
        return await self._write(command, f"output {output_num} HDCP to {mode} ({HDCP_MODES[mode]})")

    async def set_output_hdr(self, output_num: int, mode: int) -> bool:
        """
        Set the HDR conversion of an output (``set hdr conversion``).

        :param output_num: Output number (1-8)
        :param mode: HDR mode, API value (1=Passthrough, 2=HDR to SDR, 3=Auto/follow sink EDID).
            The device code is ``mode - 1`` (HIL-02: the device reports 0 for pass-through).
        :return: True if the matrix accepted the command
        """
        if not self._valid_output(output_num):
            return False
        if mode not in HDR_MODES:
            _LOG.error("Invalid HDR mode: %d. Must be 1-3", mode)
            return False
        command = {"comhead": "set hdr conversion", "language": 0, "hdr": [output_num, hdr_to_device(mode)]}
        return await self._write(command, f"output {output_num} HDR to {mode} ({HDR_MODES[mode]})")

    async def set_output_scaler(self, output_num: int, mode: int) -> bool:
        """
        Set the video mode (scaler) of an output (``set video scaler``).

        :param output_num: Output number (1-8)
        :param mode: Scaler mode, API value (1=Passthrough, 2=8K→4K, 3=8K/4K→1080p, 4=Auto, 5=Audio Only).
            The device code is ``mode - 1`` (BE-15: audio only is 4 on the device, in reads and writes).
        :return: True if the matrix accepted the command
        """
        if not self._valid_output(output_num):
            return False
        if mode not in SCALER_MODES:
            _LOG.error("Invalid scaler mode: %d. Must be 1-5", mode)
            return False
        command = {
            "comhead": "set video scaler",
            "language": 0,
            "scaler": [output_num, scaler_to_device(mode)],
        }
        return await self._write(command, f"output {output_num} scaler to {mode} ({SCALER_MODES[mode]})")

    async def set_output_arc(self, output_num: int, enable: bool) -> bool:
        """
        Enable or disable ARC (Audio Return Channel) of an output (``set arc``).

        :param output_num: Output number (1-8)
        :param enable: True to enable ARC, False to disable
        :return: True if the matrix accepted the command
        """
        if not self._valid_output(output_num):
            return False
        command = {"comhead": "set arc", "language": 0, "arc": [output_num, 1 if enable else 0]}
        return await self._write(command, f"output {output_num} ARC {'on' if enable else 'off'}")

    async def set_output_audio_mute(self, output_num: int, mute: bool) -> bool:
        """
        Mute or unmute the audio of an output (``set output audio mute``).

        :param output_num: Output number (1-8)
        :param mute: True to mute, False to unmute
        :return: True if the matrix accepted the command
        """
        if not self._valid_output(output_num):
            return False
        command = {"comhead": "set output audio mute", "language": 0, "mute": [output_num, 1 if mute else 0]}
        return await self._write(command, f"output {output_num} audio {'muted' if mute else 'unmuted'}")

    async def set_cec_enable(self, port_type: str, port_num: int, enable: bool) -> bool:
        """
        Enable or disable CEC for a specific input or output.

        HIL-10 / BE-13: the device rejects the single-port ``set cec index``
        payload (``result: 0``, captured); only the documented form with both
        8-element arrays works. This method therefore reads the current
        arrays and sends both (:meth:`set_cec_enabled`).

        :param port_type: "input" or "output"
        :param port_num: Port number (1-8)
        :param enable: True to enable CEC, False to disable
        :return: True if the matrix accepted the command
        """
        if port_type not in ("input", "output"):
            _LOG.error("Invalid port type: %s. Must be 'input' or 'output'", port_type)
            return False
        return await self.set_cec_enabled(port_num, enable, is_output=port_type == "output")

    # =========================================================================
    # Presets
    # =========================================================================

    async def save_preset(self, preset_num: int) -> bool:
        """
        Save the current routing configuration to a preset (``preset save``).

        :param preset_num: Preset number (1-8)
        :return: True if the matrix accepted the command
        """
        if preset_num < 1 or preset_num > 8:
            _LOG.error("Invalid preset number: %d. Must be 1-8", preset_num)
            return False
        command = {"comhead": "preset save", "language": 0, "index": preset_num}
        return await self._write(command, f"preset {preset_num} to the current routing")

    async def set_preset_name(self, preset_num: int, name: str) -> bool:
        """
        Rename a preset on the matrix (``preset name``).

        The device reports preset names in ``get video status.allname``.

        :param preset_num: Preset number (1-8)
        :param name: New name (the device web interface allows 32 characters)
        :return: True if the matrix accepted the command
        """
        if preset_num < 1 or preset_num > 8:
            _LOG.error("Invalid preset number: %d. Must be 1-8", preset_num)
            return False
        name = name[:32]
        command = {"comhead": "preset name", "language": 0, "index": preset_num, "name": name}
        if await self._write(command, f"preset {preset_num} name to {name!r}"):
            self.events.emit(Events.UPDATE, {"preset_name": {preset_num: name}})
            return True
        return False

    # =========================================================================
    # System
    # =========================================================================

    async def system_reboot(self) -> bool:
        """
        Reboot the OREI Matrix.

        :return: True if command sent (connection will be lost after reboot)
        """
        _LOG.warning("Initiating system reboot...")

        # Try Telnet reboot first if connected, as it is much more reliable and standard
        if self._telnet and self._telnet.connected:
            _LOG.info("Sending reboot command via Telnet...")
            success = await self._telnet.reboot()
            if success:
                # Not an intentional disconnect: reconnect once it is back.
                self._link_lost("matrix reboot requested")
                return True

        # HTTP: the device web interface's reboot command (HIL-09: ``set reboot``
        # was never captured; ``reboot`` with ``reboot: 1`` is web-UI-derived).
        _LOG.info("Sending reboot command via HTTP...")
        command = {"comhead": "reboot", "language": 0, "reboot": 1}
        sent, response = await self._send_command(command, retry_on_failure=False)
        success = self._check_write(sent, response, command)

        if success:
            self._link_lost("matrix reboot requested")

        return success

    # LCD timeout mode values (device code == API value; read back as
    # ``get system status.mode``)
    LCD_TIMEOUT_MODES = dict(DEVICE_LCD_MODES)

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
        Set how long the front-panel LCD stays on (``set lcd on time``).

        HIL-09: the old ``{"time": N}`` payload is rejected for every code
        (captured); the value goes in a key named ``"lcd on time"``.

        :param mode: 0=Off, 1=Always on, 2=15 s, 3=30 s, 4=60 s
        :return: True if the matrix accepted the command
        """
        if mode not in DEVICE_LCD_MODES:
            _LOG.error("Invalid LCD timeout mode: %d. Must be 0-4", mode)
            return False
        command = {"comhead": "set lcd on time", "language": 0, "lcd on time": mode}
        return await self._write(command, f"LCD on time to {mode} ({self.get_lcd_timeout_name(mode)})")

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

    #: EDID ids the device offers (device id == API value), see device_codes.
    #: 40-47 copy the EDID of output 1-8 (BE-25: there is no ``copy edid``).
    EDID_MODES = dict(DEVICE_EDID_MODES)

    @classmethod
    def get_edid_mode_name(cls, mode_value: int) -> str:
        """Get human-readable name for an EDID mode value."""
        return cls.EDID_MODES.get(mode_value, f"Unknown ({mode_value})")

    @classmethod
    def get_edid_modes(cls) -> dict[int, str]:
        """Get all available EDID modes."""
        return cls.EDID_MODES.copy()

    async def get_edid_status(self) -> dict[str, Any] | None:
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
                    "mode_name": edid_names[i] if i < len(edid_names) else "Unknown",
                }
                for i in range(8)
            },
        }

    async def set_input_edid(self, input_num: int, mode: int) -> bool:
        """
        Set the EDID of an input (``set edid``).

        :param input_num: Input number (1-8)
        :param mode: EDID id 1-47 (see :attr:`EDID_MODES`): 1-36 built-in
            resolution/audio sets, 37-39 user EDIDs, 40-47 copy from output 1-8
        :return: True if the matrix accepted the command
        """
        if input_num < 1 or input_num > 8:
            _LOG.error("Invalid input number: %d. Must be 1-8", input_num)
            return False
        if mode not in DEVICE_EDID_MODES:
            _LOG.error("Invalid EDID mode: %d. Must be %d-%d", mode, min(DEVICE_EDID_MODES), max(DEVICE_EDID_MODES))
            return False
        command = {"comhead": "set edid", "language": 0, "edid": [input_num, mode]}
        return await self._write(command, f"input {input_num} EDID to {mode} ({self.get_edid_mode_name(mode)})")

    async def copy_edid_from_output(self, input_num: int, output_num: int) -> bool:
        """
        Copy the EDID of a connected display (output) to an input.

        BE-25: the device has no ``copy edid`` command (captured: no answer);
        copying is EDID id 39 + output (40 = output 1 ... 47 = output 8).

        :param input_num: Input number (1-8) to receive the EDID
        :param output_num: Output number (1-8) to copy EDID from
        :return: True if the matrix accepted the command
        """
        if not 1 <= output_num <= 8:
            _LOG.error("Invalid output number: %d. Must be 1-8", output_num)
            return False
        return await self.set_input_edid(input_num, edid_copy_from_output(output_num))

    # =========================================================================
    # External Audio (Ext-Audio) Matrix Control
    # =========================================================================

    # Ext-audio mode values (device code == API value)
    EXT_AUDIO_MODES = dict(DEVICE_EXT_AUDIO_MODES)

    @classmethod
    def get_ext_audio_mode_name(cls, mode: int) -> str:
        """Get human-readable name for an ext-audio mode value."""
        return cls.EXT_AUDIO_MODES.get(mode, f"Unknown ({mode})")

    @classmethod
    def get_ext_audio_modes(cls) -> dict:
        """Get all available ext-audio modes."""
        return cls.EXT_AUDIO_MODES.copy()

    async def get_ext_audio_status(self) -> dict | None:
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
        Set the external audio routing mode (``set ext-audio mode``).

        :param mode: 0 = bind to input, 1 = bind to output, 2 = matrix mode
        :return: True if the matrix accepted the command
        """
        if mode not in DEVICE_EXT_AUDIO_MODES:
            _LOG.error("Invalid ext-audio mode: %d. Must be 0-2", mode)
            return False
        command = {"comhead": "set ext-audio mode", "language": 0, "mode": mode}
        return await self._write(command, f"ext-audio mode to {mode} ({self.get_ext_audio_mode_name(mode)})")

    async def set_ext_audio_enable(self, output_num: int, enabled: bool) -> bool:
        """
        Enable or disable an external audio output (``set ext-audio out``).

        :param output_num: Ext-audio output number (1-8)
        :param enabled: True to enable, False to disable
        :return: True if the matrix accepted the command
        """
        if not self._valid_output(output_num):
            return False
        command = {"comhead": "set ext-audio out", "language": 0, "out": [output_num, 1 if enabled else 0]}
        return await self._write(command, f"ext-audio output {output_num} {'enabled' if enabled else 'disabled'}")

    async def set_ext_audio_source(self, output_num: int, input_num: int) -> bool:
        """
        Route an input to an external audio output (``ext-audio switch``).

        The device applies this in matrix mode (2); its web interface only
        offers it there.

        :param output_num: Ext-audio output number (1-8)
        :param input_num: Input source number (1-8)
        :return: True if the matrix accepted the command
        """
        if not self._valid_output(output_num):
            return False
        if input_num < 1 or input_num > 8:
            _LOG.error("Invalid input number: %d. Must be 1-8", input_num)
            return False
        command = {"comhead": "ext-audio switch", "language": 0, "source": [output_num, input_num]}
        return await self._write(command, f"ext-audio output {output_num} source to input {input_num}")

    async def set_ext_audio_index(self, output_num: int) -> bool:
        """
        Select the "current" ext-audio output (``set ext-audio index``; read
        back as ``get ext-audio status.index``).

        The device's own web page sends it in matrix mode when an audio output
        is clicked, before routing a source to it; no other effect is known.

        :param output_num: Ext-audio output number (1-8)
        :return: True if the matrix accepted the command
        """
        if not self._valid_output(output_num):
            return False
        command = {"comhead": "set ext-audio index", "language": 0, "index": output_num}
        return await self._write(command, f"ext-audio selected output to {output_num}")

    # =========================================================================
    # Device Capability Detection (for CEC routing)
    # =========================================================================

    async def get_output_capabilities(self, output_num: int) -> dict[str, Any] | None:
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
        # get output status returns 'name' field (not 'alloutputname')
        alloutputname = output_status.get("name") or output_status.get("alloutputname", [])

        cec_outputindex = cec_status.get("outputindex", [])

        scaler_value = allscaler[idx] if idx < len(allscaler) else 0

        # Audio only is device scaler code 4 (BE-15)
        is_audio_only = scaler_value == SCALER_AUDIO_ONLY

        return {
            "output_num": output_num,
            "name": alloutputname[idx] if idx < len(alloutputname) else f"Output {output_num}",
            "connected": allconnect[idx] == 1 if idx < len(allconnect) else False,
            "stream_enabled": allout[idx] == 1 if idx < len(allout) else True,
            "is_audio_only": is_audio_only,
            "arc_enabled": allarc[idx] == 1 if idx < len(allarc) else False,
            "cec_enabled": cec_outputindex[idx] == 1 if idx < len(cec_outputindex) else False,
            "scaler_mode": scaler_value,
            "supported_cec_commands": list(self.CEC_OUTPUT_COMMAND_MAP),
        }

    async def get_input_capabilities(self, input_num: int) -> dict[str, Any] | None:
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
                "POWER_ON",
                "POWER_OFF",
                "UP",
                "DOWN",
                "LEFT",
                "RIGHT",
                "SELECT",
                "MENU",
                "BACK",
                "PLAY",
                "PAUSE",
                "STOP",
                "PREVIOUS",
                "NEXT",
                "REWIND",
                "FAST_FORWARD",
                "VOLUME_UP",
                "VOLUME_DOWN",
                "MUTE",
            ],
        }

    async def get_all_capabilities(self) -> dict[str, Any] | None:
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

            inputs.append(
                {
                    "input_num": i,
                    "name": inname[idx] if idx < len(inname) else f"Input {i}",
                    "signal_detected": inactive[idx] == 1 if idx < len(inactive) else False,
                    "cec_enabled": cec_inputindex[idx] == 1 if idx < len(cec_inputindex) else False,
                    "supported_cec_commands": [
                        "POWER_ON",
                        "POWER_OFF",
                        "UP",
                        "DOWN",
                        "LEFT",
                        "RIGHT",
                        "SELECT",
                        "MENU",
                        "BACK",
                        "PLAY",
                        "PAUSE",
                        "STOP",
                        "PREVIOUS",
                        "NEXT",
                        "REWIND",
                        "FAST_FORWARD",
                        "VOLUME_UP",
                        "VOLUME_DOWN",
                        "MUTE",
                    ],
                }
            )

            # Output capabilities
            allscaler = output_status.get("allscaler", [])
            allarc = output_status.get("allarc", [])
            allconnect = output_status.get("allconnect", [])
            allout = output_status.get("allout", [])
            # get output status returns 'name' field (not 'alloutputname')
            alloutputname = output_status.get("name") or output_status.get("alloutputname", [])
            cec_outputindex = cec_status.get("outputindex", [])

            scaler_value = allscaler[idx] if idx < len(allscaler) else 0
            is_audio_only = scaler_value == SCALER_AUDIO_ONLY

            outputs.append(
                {
                    "output_num": i,
                    "name": alloutputname[idx] if idx < len(alloutputname) else f"Output {i}",
                    "connected": allconnect[idx] == 1 if idx < len(allconnect) else False,
                    "stream_enabled": allout[idx] == 1 if idx < len(allout) else True,
                    "is_audio_only": is_audio_only,
                    "arc_enabled": allarc[idx] == 1 if idx < len(allarc) else False,
                    "cec_enabled": cec_outputindex[idx] == 1 if idx < len(cec_outputindex) else False,
                    "scaler_mode": scaler_value,
                    "supported_cec_commands": list(self.CEC_OUTPUT_COMMAND_MAP),
                }
            )

        return {
            "inputs": inputs,
            "outputs": outputs,
        }
