#!/usr/bin/env python3
"""
OREI BK-808 HDMI Matrix integration driver for Unfolded Circle Remote Two/3.

Lifecycle (WP-B2, docs/audits/UC_INTEGRATION_AUDIT.md):

* The hub owns the matrix connection and the status poller. Both start with
  the hub (``restore_from_config`` or a completed setup), independent of any
  Remote: the poller also feeds the web app and Home Assistant (``/ws``). A
  Remote's ``connect``/``disconnect``/standby never connects, disconnects or
  stops anything (UC-17, UC-06). The matrix reconnects itself after a lost
  link (``OreiMatrix`` BE-04); the driver only follows its events (BE-06).
* What the Remote is told goes through :class:`EntityStateSync`: the last
  known attributes of every entity, projected to UNAVAILABLE while the matrix
  link is down (never made-up values), pushed only when they change (UC-07),
  and held back while the Remote is in standby (UC-06).
* The device state follows the matrix connection state (UC-04):
  CONNECTED/DEGRADED -> CONNECTED, CONNECTING -> CONNECTING, BACKOFF (link
  lost, reconnecting) -> ERROR, DISCONNECTED -> DISCONNECTED.

:copyright: (c) 2026 by Custom Integration.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import atexit
import contextlib
import errno
import functools
import json
import logging
import os
import re
import signal
import socket
import sys
import threading
import time
from collections.abc import Awaitable, Callable, Coroutine
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import ucapi
from ucapi import Button, MediaPlayer, Sensor, StatusCodes, Switch
from ucapi.media_player import Attributes as MediaPlayerAttr
from ucapi.media_player import Commands as MediaPlayerCommands
from ucapi.media_player import DeviceClasses as MediaPlayerDeviceClasses
from ucapi.media_player import Features as MediaPlayerFeatures
from ucapi.media_player import States as MediaPlayerStates
from ucapi.remote import Attributes as RemoteAttr
from ucapi.remote import Commands as RemoteCommands
from ucapi.remote import Features as RemoteFeatures
from ucapi.remote import Remote
from ucapi.remote import States as RemoteStates
from ucapi.sensor import Attributes as SensorAttr
from ucapi.sensor import DeviceClasses as SensorDeviceClasses
from ucapi.sensor import States as SensorStates
from ucapi.switch import Attributes as SwitchAttr
from ucapi.switch import Commands as SwitchCommands
from ucapi.switch import Features as SwitchFeatures
from ucapi.switch import States as SwitchStates

from _process_lock import ProcessLock, ProcessLockError
from orei_matrix import ConnectionState, OreiMatrix, per_output
from orei_matrix import Events as MatrixEvents

try:
    from _task_supervisor import cancel_and_wait, create_supervised_task
except ImportError:
    from ._task_supervisor import (  # type: ignore[no-redef]  # package-relative fallback
        cancel_and_wait,
        create_supervised_task,
    )
from rest_api import (
    RestApiServer,
    set_macro_cec_sender,
    set_matrix_device,
    update_input_names,
    update_output_names,
)
from rest_api.device_settings import add_change_listener, get_favorite_presets, preset_display_name

_LOG = logging.getLogger("driver")

# REST API configuration
def rest_api_port() -> int:
    """The hub's REST port: API_PORT (as everywhere in the hub), else the older REST_API_PORT, else 8080."""
    return int(os.environ.get("API_PORT") or os.environ.get("REST_API_PORT") or "8080")


REST_API_PORT = rest_api_port()
REST_API_ENABLED = os.environ.get("REST_API_ENABLED", "true").lower() == "true"

# Status polling configuration
POLLING_INTERVAL = int(os.environ.get("POLLING_INTERVAL", "30"))  # seconds
POLLING_ENABLED = os.environ.get("POLLING_ENABLED", "true").lower() == "true"

#: driver.json ships next to the package (repository root / image /app), not in the CWD (UC-19).
DRIVER_JSON = Path(__file__).resolve().parent.parent / "driver.json"

# Configuration file paths - use UC_CONFIG_HOME if set (for Docker), otherwise local data directory.
# CONFIG_FILE is the location before the integration API exists (and the legacy location): once it
# does, the configuration lives in ucapi's config directory (config_file_path(), UC-19).
_CONFIG_HOME = Path(os.environ.get("UC_CONFIG_HOME", Path(__file__).parent.parent / "data"))
CONFIG_FILE = _CONFIG_HOME / "config_state.json"
LOCK_FILE = _CONFIG_HOME / "driver.lock"
CONFIG_FILE_NAME = "config_state.json"

#: How long a Remote's `connect` waits for the start-up connection attempt before it gets the device state.
STARTUP_CONNECT_WAIT = 10.0

#: Remote entity `send_cmd` / `send_cmd_sequence` timing (entity_remote.md). The Remote processes one
#: message per connection at a time, so repeat/delay/hold are bounded to keep the connection responsive.
MAX_CMD_REPEAT = 20
MAX_CMD_DELAY_MS = 5000
#: Delay between repeated commands / sequence steps when the Remote sends none ("the integration driver
#: has to choose an appropriate delay"): a CEC key press needs a moment on the bus before the next one.
DEFAULT_CMD_DELAY_MS = 100


# =============================================================================
# Driver State Dataclass - Consolidates global state
# =============================================================================


@dataclass
class DriverState:
    """Centralized driver state management.

    This dataclass consolidates all driver state into a single object,
    making it easier to manage, test, and reason about state.

    Attributes:
        api: The Unfolded Circle integration API instance
        matrix_device: The OREI matrix device connection
        rest_api_server: The REST API server instance
        polling_task: Background task for status polling
        startup_task: The start-up connection attempt (restore, UC-19)
        input_names: Mapping of input port numbers to names
        output_names: Mapping of output port numbers to names
        saved_config: Persisted configuration data
    """

    api: ucapi.IntegrationAPI | None = None
    matrix_device: OreiMatrix | None = None
    rest_api_server: "RestApiServer | None" = None
    polling_task: asyncio.Task | None = None
    startup_task: asyncio.Task | None = None
    input_names: dict[int, str] = field(default_factory=dict)
    output_names: dict[int, str] = field(default_factory=dict)
    saved_config: dict[str, Any] = field(default_factory=dict)
    #: The matrix's own preset names (``get video status`` ``allname``), the web app's fallback (UC-14).
    preset_matrix_names: list[str] = field(default_factory=list)
    #: What the preset entities were built with: (names 1-8, favourites), see :func:`preset_view`.
    preset_view: "PresetView | None" = None
    # threading.Lock (not asyncio.Lock) because input_names/output_names are
    # read by the polling task and written from REST handlers / setup flows
    # which may run in either sync or async contexts. threading.Lock works
    # in both and the critical sections are tiny (dict assignment).
    _names_lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    @property
    def connected(self) -> bool:
        """Check if matrix is connected."""
        return self.matrix_device is not None and self.matrix_device.connected

    def get_input_name(self, port: int) -> str:
        """Get input name with fallback to default."""
        return self.input_names.get(port, f"Input {port}")

    def get_output_name(self, port: int) -> str:
        """Get output name with fallback to default."""
        return self.output_names.get(port, f"Output {port}")


@dataclass(frozen=True)
class PresetView:
    """The hardware presets as the web app shows them (UC-14): names 1-8 and the favourites, in order."""

    names: tuple[str, ...]
    favourites: tuple[int, ...]

    def name(self, preset: int) -> str:
        return self.names[preset - 1]


# Global driver state instance - THE source of truth for all state
_driver_state = DriverState()

# Polling task reference for background status updates
_polling_task: asyncio.Task | None = None
# Serializes start/stop of the polling task, so there is only ever one poller.
_polling_task_lock = asyncio.Lock()
# Set to run the next poll now instead of after POLLING_INTERVAL (link up, Remote wake).
_poll_wakeup = asyncio.Event()

# Background tasks started from sync event handlers (strong references until done).
_background_tasks: set[asyncio.Task] = set()


# =============================================================================
# State Accessor Functions - Clean interface for accessing driver state
# =============================================================================


def get_state() -> DriverState:
    """Get the global driver state instance.

    Use this function instead of accessing _driver_state directly when possible.
    This provides a clean interface that can be easily mocked in tests.
    """
    return _driver_state


def get_matrix() -> OreiMatrix | None:
    """Get the matrix device instance."""
    return _driver_state.matrix_device


def is_connected() -> bool:
    """Check if the matrix device is connected."""
    return _driver_state.connected


def set_matrix(device: OreiMatrix | None) -> None:
    """Set the matrix device instance."""
    _driver_state.matrix_device = device


def set_input_names(names: dict[int, str]) -> None:
    """Update input names in driver state (thread-safe)."""
    with _driver_state._names_lock:
        _driver_state.input_names = names.copy() if names else {}


def set_output_names(names: dict[int, str]) -> None:
    """Update output names in driver state (thread-safe)."""
    with _driver_state._names_lock:
        _driver_state.output_names = names.copy() if names else {}


def _spawn(coro: Coroutine[Any, Any, Any], name: str) -> asyncio.Task | None:
    """Run ``coro`` in the background from sync code (keeps a reference; no-op without a running loop)."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        coro.close()
        return None
    task = loop.create_task(coro, name=name)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


# =============================================================================
# Entity state sync - what the Remote is told (UC-04, UC-06, UC-07)
# =============================================================================


class EntityStateSync:
    """Last known entity attributes, and what the Remote has been sent.

    * ``update()`` records the truth (the device's last known values) and
      pushes the attributes that changed to the subscribed entity. Unchanged
      attributes are never re-sent (UC-07).
    * While the matrix link is down every entity's ``state`` is UNAVAILABLE;
      all other attributes keep their last known value (no placeholders,
      UC-04). When the link comes back the last known state is restored.
    * While the Remote is in standby nothing is sent; the changes are kept
      and sent when it wakes (UC-06).
    """

    def __init__(self) -> None:
        self.truth: dict[str, dict[str, Any]] = {}
        self.available = False
        self.standby = False
        self.pending: dict[str, set[str]] = {}

    @staticmethod
    def _api() -> ucapi.IntegrationAPI | None:
        return _driver_state.api

    def projected(self, entity_id: str) -> dict[str, Any]:
        """The attributes the Remote should see for ``entity_id`` now."""
        attrs = dict(self.truth.get(entity_id, {}))
        if not self.available:
            attrs["state"] = "UNAVAILABLE"
        return attrs

    #: Attributes that come from how the entity is built (port names), not from the device's state.
    BUILT_ATTRIBUTES = frozenset({"source_list"})

    def register(self, entity: Any) -> None:
        """Adopt a newly built entity: seed its truth once (built attributes always), show the projection."""
        if entity.id not in self.truth:
            self.truth[entity.id] = dict(entity.attributes)
        for key in self.BUILT_ATTRIBUTES & set(entity.attributes):
            self.truth[entity.id][key] = entity.attributes[key]
        entity.attributes.update(self.projected(entity.id))

    def replaced(self, entity_id: str, old_attributes: dict[str, Any]) -> None:
        """A subscribed entity was rebuilt (new names): send the Remote what differs from what it had."""
        api = self._api()
        entity = api.configured_entities.get(entity_id) if api is not None else None
        if entity is None:
            return
        changed = {k: v for k, v in entity.attributes.items() if old_attributes.get(k) != v}
        if not changed:
            return
        if self.standby:
            self.pending.setdefault(entity_id, set()).update(changed)
            return
        api.configured_entities.update_attributes(entity_id, changed)

    def update(self, entity_id: str, attributes: dict[str, Any]) -> None:
        """Record new last-known attributes for ``entity_id`` and publish what changed."""
        self.truth.setdefault(entity_id, {}).update(attributes)
        self.publish(entity_id)

    def value(self, entity_id: str, key: str) -> Any:
        return self.truth.get(entity_id, {}).get(key)

    def set_available(self, available: bool) -> None:
        """The matrix link went up or down: republish every entity's state."""
        if available == self.available:
            return
        self.available = available
        _LOG.info("Entities are now %s", "available" if available else "UNAVAILABLE (matrix unreachable)")
        for entity_id in self._all_ids():
            self.publish(entity_id)

    def _all_ids(self) -> list[str]:
        ids = set(self.truth)
        api = self._api()
        if api is not None:
            ids.update(e["entity_id"] for e in api.available_entities.get_all())
        return sorted(ids)

    def publish(self, entity_id: str) -> None:
        """Bring the entity objects in line with the projection; send the changes to the Remote."""
        api = self._api()
        if api is None:
            return
        proj = self.projected(entity_id)
        configured = api.configured_entities.get(entity_id)
        available = api.available_entities.get(entity_id)
        if available is not None and available is not configured:
            available.attributes.update(proj)
        if configured is None:
            return
        changed = {k: v for k, v in proj.items() if configured.attributes.get(k) != v}
        if not changed:
            return
        if self.standby:
            configured.attributes.update(changed)
            self.pending.setdefault(entity_id, set()).update(changed)
            return
        api.configured_entities.update_attributes(entity_id, changed)

    def resend(self, entity_ids: list[str]) -> None:
        """Send the full current state of newly subscribed entities (the Remote's view starts in sync)."""
        api = self._api()
        if api is None:
            return
        for entity_id in entity_ids:
            configured = api.configured_entities.get(entity_id)
            if configured is None:
                continue
            if entity_id not in self.truth:
                self.truth[entity_id] = dict(configured.attributes)
            proj = self.projected(entity_id)
            if self.standby:
                configured.attributes.update(proj)
                self.pending.setdefault(entity_id, set()).update(proj)
            else:
                api.configured_entities.update_attributes(entity_id, proj)

    def set_standby(self, standby: bool) -> None:
        """Remote standby pauses pushes; waking sends what changed meanwhile."""
        self.standby = standby
        if standby:
            _LOG.info("Remote in standby: pausing entity updates")
            return
        pending, self.pending = self.pending, {}
        api = self._api()
        if api is None or not pending:
            return
        _LOG.info("Remote awake: sending %d entities that changed during standby", len(pending))
        for entity_id, keys in pending.items():
            configured = api.configured_entities.get(entity_id)
            if configured is not None:
                api.configured_entities.update_attributes(
                    entity_id, {k: configured.attributes[k] for k in keys if k in configured.attributes}
                )


_entity_sync = EntityStateSync()

#: Tracked power state of the device behind a CEC port (("input"|"output", port) -> on?). The matrix
#: cannot read a TV's or source's power state; this is the last power command the hub sent.
_device_power: dict[tuple[str, int], bool] = {}


def _power_entities(port_type: str, port: int) -> list[str]:
    ids = [f"remote.{port_type}_{port}_cec"]
    if port_type == "output":
        ids.append(f"media_player.output_{port}")
    return ids


def _set_device_power(port_type: str, port: int, on: bool) -> None:
    """A power command reached the device: the remote (and the display's media player) show it."""
    _device_power[(port_type, port)] = on
    for entity_id in _power_entities(port_type, port):
        _entity_sync.update(entity_id, {"state": "ON" if on else "OFF"})


def _toggle_turns_on(port_type: str, port: int) -> bool:
    """Toggle rule (UC-10): off -> on, on -> off, and UNKNOWN -> on.

    The hub cannot read a display's or source's power state. When it does not
    know it, toggle powers the device on: turning on a device that is already
    on is harmless, turning off one the user wanted to use is not.
    """
    return _device_power.get((port_type, port)) is not True


# =============================================================================
# Command handlers
# =============================================================================


CommandHandler = Callable[[Any, str, dict[str, Any] | None, Any], Awaitable[StatusCodes]]


def guarded_handler(handler: CommandHandler) -> Callable[..., Awaitable[StatusCodes]]:
    """Every entity command answers: an exception becomes SERVER_ERROR (UC-01).

    ucapi does not catch exceptions from command handlers; one used to close
    the Remote's WebSocket (1011) and take every entity offline.
    """

    @functools.wraps(handler)
    async def wrapper(entity: Any, cmd_id: str, params: dict[str, Any] | None = None,
                      websocket: Any = None) -> StatusCodes:
        try:
            return await handler(entity, cmd_id, params, websocket)
        except asyncio.CancelledError:
            raise
        except Exception:
            _LOG.exception("Command '%s' on %s failed", cmd_id, getattr(entity, "id", "?"))
            return StatusCodes.SERVER_ERROR

    return wrapper


def _int_param(params: dict[str, Any], key: str, default: int, maximum: int) -> int:
    """A non-negative integer parameter, bounded (raises ValueError on garbage)."""
    value = params.get(key)
    if value is None:
        return default
    number = int(value)
    if number < 0:
        raise ValueError(f"{key} must not be negative")
    return min(number, maximum)


def parse_command_timing(params: dict[str, Any] | None) -> tuple[int, int, int]:
    """``(repeat, delay_ms, hold_ms)`` from send_cmd / send_cmd_sequence parameters (entity_remote.md).

    ``repeat`` defaults to 1 (0 counts as 1), ``delay`` to :data:`DEFAULT_CMD_DELAY_MS`, ``hold`` to 0.
    Values are capped (:data:`MAX_CMD_REPEAT`, :data:`MAX_CMD_DELAY_MS`). Raises ValueError on bad input.
    """
    params = params or {}
    repeat = max(1, _int_param(params, "repeat", 1, MAX_CMD_REPEAT))
    delay = _int_param(params, "delay", DEFAULT_CMD_DELAY_MS, MAX_CMD_DELAY_MS)
    hold = _int_param(params, "hold", 0, MAX_CMD_DELAY_MS)
    return repeat, delay, hold


def command_list(cmd_id: str, params: dict[str, Any] | None) -> list[str] | None:
    """The simple commands a send_cmd / send_cmd_sequence asks for (None = malformed request).

    A sequence may be a list or a comma-separated string (the button-mapping form in entity_remote.md).
    """
    params = params or {}
    if cmd_id == RemoteCommands.SEND_CMD:
        command = params.get("command")
        return [command.strip()] if isinstance(command, str) and command.strip() else None
    sequence = params.get("sequence")
    if isinstance(sequence, str):
        sequence = sequence.split(",")
    if not isinstance(sequence, list):
        return None
    commands = [c.strip() for c in sequence if isinstance(c, str) and c.strip()]
    return commands if commands and len(commands) == len(sequence) else None


def create_cec_command_handler(
    port_num: int,
    port_type: str,  # "input" or "output"
    get_method: Callable[[str], Callable[[int], Coroutine[Any, Any, bool]] | None],
) -> Callable[..., Awaitable[StatusCodes]]:
    """
    Create the command handler of a CEC remote entity (``remote.<port_type>_<n>_cec``).

    Remote entity commands (entity_remote.md; UC-01, UC-22):

    * ``on`` / ``off``: CEC power on / off (the source table for inputs, the
      display table for outputs);
    * ``toggle``: from the tracked power state (see :func:`_toggle_turns_on`);
    * ``send_cmd``: one simple command, with ``repeat``, ``delay`` and ``hold``;
    * ``send_cmd_sequence``: several simple commands, each with the same
      ``repeat``/``hold``, ``delay`` between all of them.

    Every command in a request is validated before anything is sent; an
    unknown one answers 400 with no CEC frame. ``hold``: the BK-808 sends a
    CEC key as one press and release, so a hold is honoured as the time the
    key occupies before the next one is sent.

    :param port_num: Input or output number (1-8)
    :param port_type: "input" or "output"
    :param get_method: Function that returns the appropriate CEC method for a command
    :return: Async command handler function
    """

    async def cec_cmd_handler(
        entity: Remote, cmd_id: str, params: dict[str, Any] | None, websocket: Any = None
    ) -> StatusCodes:
        """Handle CEC remote commands."""
        _LOG.info("%s CEC: %s -> %s %s", port_type.upper(), entity.id, cmd_id, params or "")

        matrix = get_matrix()
        if matrix is None or not matrix.connected:
            _LOG.error("Matrix not connected")
            return StatusCodes.SERVICE_UNAVAILABLE

        if cmd_id in (RemoteCommands.ON, RemoteCommands.OFF, RemoteCommands.TOGGLE):
            if cmd_id == RemoteCommands.TOGGLE:
                turn_on = _toggle_turns_on(port_type, port_num)
            else:
                turn_on = cmd_id == RemoteCommands.ON
            commands = ["POWER_ON" if turn_on else "POWER_OFF"]
            repeat, delay, hold = 1, 0, 0
        elif cmd_id in (RemoteCommands.SEND_CMD, RemoteCommands.SEND_CMD_SEQUENCE):
            maybe_commands = command_list(cmd_id, params)
            if maybe_commands is None:
                _LOG.warning("%s on %s without a valid command: %s", cmd_id, entity.id, params)
                return StatusCodes.BAD_REQUEST
            commands = maybe_commands
            try:
                repeat, delay, hold = parse_command_timing(params)
            except (TypeError, ValueError) as ex:
                _LOG.warning("Bad repeat/delay/hold for %s on %s: %s", cmd_id, entity.id, ex)
                return StatusCodes.BAD_REQUEST
        else:
            _LOG.warning("Command not implemented: %s", cmd_id)
            return StatusCodes.NOT_IMPLEMENTED

        methods = []
        for command in commands:
            method = get_method(command)
            if method is None:
                _LOG.warning("Unknown CEC command for %s: %s", entity.id, command)
                return StatusCodes.BAD_REQUEST
            methods.append((command.upper(), method))

        first = True
        for command, method in methods:
            for _ in range(repeat):
                if not first and delay:
                    await asyncio.sleep(delay / 1000)
                first = False
                if not await method(port_num):
                    return StatusCodes.SERVER_ERROR
                if command in ("POWER_ON", "POWER_OFF"):
                    _set_device_power(port_type, port_num, command == "POWER_ON")
                if hold:
                    await asyncio.sleep(hold / 1000)
        return StatusCodes.OK

    return guarded_handler(cec_cmd_handler)


def get_input_cec_method(command: str) -> Callable[[int], Coroutine[Any, Any, bool]] | None:
    """
    Get a callable for executing a CEC command on an input device.

    Uses the unified send_cec method instead of individual method mappings.

    :param command: CEC command name (e.g., "POWER_ON", "PLAY", "MUTE")
    :return: Async callable that takes input_num and returns bool, or None if matrix unavailable
    """
    matrix = get_matrix()
    if matrix is None:
        return None

    # Validate command exists in the registry
    if command.upper() not in matrix.CEC_COMMAND_MAP:
        _LOG.warning(f"Unknown CEC command: {command}")
        return None

    # Return a closure that calls send_cec with is_output=False
    async def send_input_cec(input_num: int) -> bool:
        return await matrix.send_cec(command, input_num, is_output=False)

    return send_input_cec


def get_output_cec_method(command: str) -> Callable[[int], Coroutine[Any, Any, bool]] | None:
    """
    Get a callable for executing a CEC command on an output device.

    Uses the unified send_cec method instead of individual method mappings.
    Displays only have the six commands of the device's output table
    (``OreiMatrix.CEC_OUTPUT_COMMAND_MAP``, BE-14); anything else is refused
    here, so the Remote gets 400 (like the REST API) instead of a failed send.

    :param command: CEC command name (e.g., "POWER_ON", "VOLUME_UP", "MUTE")
    :return: Async callable that takes output_num and returns bool, or None if
        the matrix is unavailable or the display table has no such command
    """
    matrix = get_matrix()
    if matrix is None:
        return None

    # Validate command exists in the display (output) table
    if command.upper() not in matrix.CEC_OUTPUT_COMMAND_MAP:
        _LOG.warning(f"CEC command not available for displays: {command}")
        return None

    # Return a closure that calls send_cec with is_output=True
    async def send_output_cec(output_num: int) -> bool:
        return await matrix.send_cec(command, output_num, is_output=True)

    return send_output_cec


async def macro_cec_sender(target_type: str, port: int, command: str) -> bool:
    """CEC sender for the hub's CEC macros (``set_macro_cec_sender``)."""
    matrix = get_matrix()
    if not matrix or not matrix.connected:
        return False
    # Normalize command to lowercase for method lookup
    command = command.lower()
    method = getattr(matrix, f"cec_{target_type}_{command}", None)
    if method:
        return await method(port)
    # Fallback to set_cec_enable for enable/disable
    if command in ("enable", "disable"):
        return await matrix.set_cec_enable(target_type, port, command == "enable")
    return False


_instance_lock: ProcessLock | None = None  # held for the process lifetime


def acquire_lock() -> bool:
    """
    Acquire the single-instance lock to ensure only one instance runs.
    This prevents mDNS conflicts from multiple instances.

    Backed by an OS advisory lock (BE-18) that the OS drops when the process
    exits, however it exits — so there are no stale locks and no PID checks.
    """
    global _instance_lock
    if _instance_lock is not None and _instance_lock.held and _instance_lock.path == LOCK_FILE:
        return True
    lock = ProcessLock(LOCK_FILE)
    try:
        lock.acquire()
    except ProcessLockError as e:
        _LOG.error(str(e))
        return False
    except Exception as e:
        _LOG.error(f"Failed to acquire lock: {e}")
        return False
    _instance_lock = lock
    _LOG.info(f"Lock acquired (PID: {os.getpid()})")
    return True


def release_lock():
    """Release the single-instance lock (idempotent)."""
    global _instance_lock
    lock, _instance_lock = _instance_lock, None
    if lock is None:
        return
    try:
        lock.release()
        _LOG.info("Lock released")
    except Exception as e:
        _LOG.warning(f"Failed to release lock: {e}")


#: "Address already in use" on Linux/macOS (EADDRINUSE: 98 / 48) and Windows (WSAEADDRINUSE 10048).
_ADDR_IN_USE = frozenset({errno.EADDRINUSE, getattr(errno, "WSAEADDRINUSE", 10048), 10048})


def is_address_in_use(exc: BaseException | None) -> bool:
    """Whether ``exc`` is the OS error for a port that is already bound (BE-21)."""
    return isinstance(exc, OSError) and exc.errno in _ADDR_IN_USE


def check_port_available(port: int) -> bool:
    """Check if the port is available before starting."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", port))
            return True
    except OSError as e:
        if is_address_in_use(e):
            return False
        raise


def integration_port(driver_json: Path | None = None) -> int:
    """The integration WebSocket port ucapi will listen on (UC_INTEGRATION_HTTP_PORT, else driver.json)."""
    env = os.environ.get("UC_INTEGRATION_HTTP_PORT")
    if env:
        return int(env)
    try:
        return int(json.loads((driver_json or DRIVER_JSON).read_text(encoding="utf-8")).get("port", 9090))
    except (OSError, ValueError):
        return 9090


def wait_for_port(port: int, timeout: int = 10) -> bool:
    """Wait for a port to become available."""
    _LOG.info(f"Waiting for port {port} to become available...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_port_available(port):
            _LOG.info(f"Port {port} is now available")
            return True
        time.sleep(0.5)
    _LOG.error(f"Port {port} did not become available within {timeout} seconds")
    return False


def clear_stale_mdns(wait_time: int = 2):
    """
    Brief pause before mDNS registration to help avoid conflicts.

    Note: True mDNS cleanup is not possible for services we didn't register.
    In Docker/production, container restarts handle this cleanly.
    In development, rapid restarts may require waiting for mDNS TTL expiry.

    Args:
        wait_time: Seconds to wait (default 2)
    """
    _LOG.debug(f"Waiting {wait_time}s before mDNS registration...")
    time.sleep(wait_time)


def config_file_path() -> Path:
    """Where the configuration is saved: ucapi's config directory once the API exists (UC-19)."""
    api = _driver_state.api
    if api is not None:
        return Path(api.config_dir_path) / CONFIG_FILE_NAME
    return CONFIG_FILE


def save_config(host: str, port: int, input_names: dict[int, str], output_names: dict[int, str] | None = None,
                credentials: tuple[str, str] | None = None) -> None:
    """Save configuration to file for persistence across restarts.

    ``credentials``: the matrix login entered in the Remote's setup for this
    host (UC-02, UC-05); without them the matrix uses ``OREI_USER`` /
    ``OREI_PASSWORD``. The file is written with owner-only permissions
    (``atomic_write_json`` creates it with mode 0600 on POSIX).
    """
    config: dict[str, Any] = {
        "host": host,
        "port": port,
        "input_names": {str(k): v for k, v in input_names.items()},  # JSON requires string keys
    }
    if output_names:
        config["output_names"] = {str(k): v for k, v in output_names.items()}
    if credentials is not None:
        config["user"], config["password"] = credentials
    path = config_file_path()
    try:
        from _file_io import atomic_write_json
        atomic_write_json(path, config)
        _LOG.info(f"Configuration saved to {path}")
    except Exception as e:
        _LOG.error(f"Failed to save configuration: {e}")


def own_credentials(matrix: OreiMatrix) -> tuple[str, str] | None:
    """The login a Remote setup entered for this matrix, to save with it (None: the environment's)."""
    return matrix.credentials() if matrix.has_own_credentials else None


def load_config() -> dict[str, Any] | None:
    """Load configuration from file (ucapi's config directory, else the legacy location)."""
    path = config_file_path()
    if not path.exists() and CONFIG_FILE.exists():
        path = CONFIG_FILE  # written by an older version; the next save moves it
    try:
        if path.exists():
            with open(path) as f:
                config = json.load(f)
            # Convert input_names keys back to integers
            if "input_names" in config:
                config["input_names"] = {int(k): v for k, v in config["input_names"].items()}
            # Legacy: migrate from old "preset_names" key
            if "preset_names" in config and "input_names" not in config:
                config["input_names"] = {int(k): v for k, v in config["preset_names"].items()}
                del config["preset_names"]
            if "output_names" in config:
                config["output_names"] = {int(k): v for k, v in config["output_names"].items()}
            _LOG.info(f"Configuration loaded from {path}")
            return config
    except Exception as e:
        _LOG.error(f"Failed to load configuration: {e}")
    return None


# =============================================================================
# Entities
# =============================================================================


def preset_view() -> PresetView:
    """The hardware presets as the web app shows them right now (UC-14).

    Names follow ``GET /api/presets`` (:func:`rest_api.device_settings.preset_display_name`:
    the web app's name, else the matrix's own preset name, else "Preset N");
    the favourites are the web app's favourite presets.
    """
    names = tuple(preset_display_name(n, _driver_state.preset_matrix_names) for n in range(1, 9))
    return PresetView(names=names, favourites=tuple(get_favorite_presets()))


#: The entities that show preset names or favourites.
PRESET_ENTITY_IDS = frozenset({"remote.orei_matrix", *(f"button.preset_{n}" for n in range(1, 9))})
MATRIX_POWER_SWITCH = "switch.matrix_power"


def sync_matrix_power(power: Any) -> None:
    """The matrix reported its power (``get video status`` ``power``: 1 on, 0 standby) or the hub changed it."""
    if isinstance(power, str):
        power = {"on": 1, "off": 0}.get(power.strip().lower(), power)
    if power not in (0, 1) or isinstance(power, bool):
        return  # not a value the device sends: keep the last known state
    _entity_sync.update(MATRIX_POWER_SWITCH, {SwitchAttr.STATE: SwitchStates.ON if power else SwitchStates.OFF})


def refresh_presets(matrix_names: list[Any] | None = None) -> bool:
    """Rebuild the preset entities when the web app's preset names or favourites changed (UC-14).

    ``matrix_names``: the matrix's own preset names when a status read just
    returned them. Returns True when the entities were rebuilt.
    """
    if matrix_names is not None:
        _driver_state.preset_matrix_names = [str(n) for n in matrix_names[:8]]
    view = preset_view()
    if view == _driver_state.preset_view:
        return False
    previous, _driver_state.preset_view = _driver_state.preset_view, view
    if previous is not None:
        _LOG.info("Preset names/favourites changed in the web app: %s, favourites %s",
                  list(view.names), list(view.favourites))
        install_entities(rebuild=True, only=PRESET_ENTITY_IDS)
    return True


def on_web_app_settings_changed() -> None:
    """The web app saved its device settings (a preset renamed, a favourite toggled, ...)."""
    refresh_presets()


def build_entities() -> list[Any]:
    """All 74 entities, named from the current port names (one factory for restore, setup and renames)."""
    view = _driver_state.preset_view or preset_view()
    _driver_state.preset_view = view
    entities: list[Any] = [create_matrix_remote(view)]
    entities += [create_preset_button(n, view.name(n)) for n in range(1, 9)]
    for n in range(1, 9):
        entities.append(create_input_cec_remote(n, _driver_state.get_input_name(n)))
    for n in range(1, 9):
        entities.append(create_input_signal_sensor(n, _driver_state.get_input_name(n)))
    for n in range(1, 9):
        entities.append(create_input_cable_sensor(n, _driver_state.get_input_name(n)))
    entities.append(create_matrix_power_switch())
    for n in range(1, 9):
        name = _driver_state.get_output_name(n)
        entities.append(create_output_media_player(n, name, _driver_state.input_names))
        entities.append(create_output_cec_remote(n, name))
        entities.append(create_connection_sensor(n, name))
        entities.append(create_output_cable_sensor(n, name))
        entities.append(create_routing_sensor(n, name))
    return entities


def install_entities(*, rebuild: bool = False, only: frozenset[str] | None = None) -> None:
    """Offer the entities to the Remote (``available_entities``).

    ``rebuild`` (new port or preset names) replaces every entity object (or
    those in ``only``) in place, in both stores: the Remote's subscriptions
    (by entity id) stay, and it is sent what changed (e.g. the source list).
    Subscribed entities are never cleared (UC-05). Every entity keeps showing
    the last known state.
    """
    api = _driver_state.api
    if api is None:
        return
    for entity in build_entities():
        if only is not None and entity.id not in only:
            continue
        if api.available_entities.contains(entity.id):
            if not rebuild:
                continue
            api.available_entities.remove(entity.id)
        api.available_entities.add(entity)
        _entity_sync.register(entity)
        old = api.configured_entities.get(entity.id)
        if rebuild and old is not None:
            api.configured_entities.remove(entity.id)
            api.configured_entities.add(entity)
            _entity_sync.replaced(entity.id, dict(old.attributes))
    _LOG.info("%d entities available", len(api.available_entities.get_all()))


def create_preset_button(preset_num: int, preset_name: str | None = None) -> Button:
    """
    Create a button entity for a specific preset.

    :param preset_num: Preset number (1-8)
    :param preset_name: The preset's name as the web app shows it (UC-14); "Preset N" if not given
    :return: Button entity
    """
    display_name = preset_name if preset_name else f"Preset {preset_num}"

    async def preset_cmd_handler(
        entity: Button, cmd_id: str, _params: dict[str, Any] | None, websocket: Any = None
    ) -> StatusCodes:
        """Handle preset button press."""
        _LOG.info("Preset %d (%s) button pressed (%s)", preset_num, display_name, cmd_id)

        matrix = get_matrix()
        if matrix is None or not matrix.connected:
            _LOG.error("Matrix not connected")
            return StatusCodes.SERVICE_UNAVAILABLE

        success = await matrix.recall_preset(preset_num)
        _LOG.info(f"Preset recall result: {success}")
        return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

    button = Button(
        f"button.preset_{preset_num}",
        display_name,
        cmd_handler=guarded_handler(preset_cmd_handler),
    )
    return button


def create_input_cec_remote(input_num: int, input_name: str = None) -> Remote:
    """
    Create a remote entity for CEC control of a specific input device.

    This allows controlling source devices (PS3, Apple TV, etc.) via CEC
    using the Remote 3's native D-pad, playback buttons, etc.

    :param input_num: Input number (1-8)
    :param input_name: Custom name for the input (optional)
    :return: Remote entity
    """
    display_name = input_name if input_name else f"Input {input_num}"
    entity_id = f"remote.input_{input_num}_cec"

    # CEC command mapping for simple_commands
    CEC_COMMANDS = [
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
    ]

    # Use factory pattern for command handler (reduces ~80 lines of duplicate code)
    cec_cmd_handler = create_cec_command_handler(input_num, "input", get_input_cec_method)

    # Create UI page with CEC controls laid out like a remote
    from ucapi.ui import Size, UiPage, create_ui_text

    # Main navigation page
    nav_page = UiPage(
        f"input_{input_num}_nav",
        "Navigation",
        grid=Size(4, 6),
        items=[
            # Power row
            create_ui_text("Power On", 0, 0, Size(2, 1), "POWER_ON"),
            create_ui_text("Power Off", 2, 0, Size(2, 1), "POWER_OFF"),
            # D-pad
            create_ui_text("▲", 1, 1, Size(2, 1), "UP"),
            create_ui_text("◀", 0, 2, Size(1, 1), "LEFT"),
            create_ui_text("OK", 1, 2, Size(2, 1), "SELECT"),
            create_ui_text("▶", 3, 2, Size(1, 1), "RIGHT"),
            create_ui_text("▼", 1, 3, Size(2, 1), "DOWN"),
            # Menu/Back row
            create_ui_text("Menu", 0, 4, Size(2, 1), "MENU"),
            create_ui_text("Back", 2, 4, Size(2, 1), "BACK"),
        ],
    )

    # Playback page
    playback_page = UiPage(
        f"input_{input_num}_playback",
        "Playback",
        grid=Size(4, 6),
        items=[
            # Transport controls
            create_ui_text("⏮", 0, 0, Size(1, 1), "PREVIOUS"),
            create_ui_text("⏪", 1, 0, Size(1, 1), "REWIND"),
            create_ui_text("⏩", 2, 0, Size(1, 1), "FAST_FORWARD"),
            create_ui_text("⏭", 3, 0, Size(1, 1), "NEXT"),
            # Play/Pause/Stop
            create_ui_text("▶ Play", 0, 1, Size(2, 1), "PLAY"),
            create_ui_text("⏸ Pause", 2, 1, Size(2, 1), "PAUSE"),
            create_ui_text("⏹ Stop", 1, 2, Size(2, 1), "STOP"),
            # Volume controls
            create_ui_text("🔉 Vol-", 0, 3, Size(1, 1), "VOLUME_DOWN"),
            create_ui_text("🔇 Mute", 1, 3, Size(2, 1), "MUTE"),
            create_ui_text("🔊 Vol+", 3, 3, Size(1, 1), "VOLUME_UP"),
        ],
    )

    # Create remote with all CEC features. The state is the source's power as far as the hub knows:
    # UNKNOWN until the hub sent a power command (it cannot read a source's power state).
    remote = Remote(
        entity_id,
        f"{display_name} CEC",
        [
            RemoteFeatures.SEND_CMD,
            RemoteFeatures.ON_OFF,
            # Power toggle (UC-24, DI-13): from the tracked power state, unknown -> on (_toggle_turns_on).
            RemoteFeatures.TOGGLE,
        ],
        attributes={RemoteAttr.STATE: RemoteStates.UNKNOWN},
        simple_commands=CEC_COMMANDS,
        ui_pages=[nav_page, playback_page],
        cmd_handler=cec_cmd_handler,
    )

    return remote


def create_output_cec_remote(output_num: int, output_name: str = None) -> Remote:
    """
    Create a remote entity for CEC control of a specific output device (TV/display).

    This allows controlling displays via CEC using the Remote 3's native controls.

    :param output_num: Output number (1-8)
    :param output_name: Custom name for the output (optional)
    :return: Remote entity
    """
    display_name = output_name if output_name else f"Output {output_num}"
    entity_id = f"remote.output_{output_num}_cec"

    # Simple commands = the device's display (output) CEC table, and nothing
    # else (BE-14): POWER_ON, POWER_OFF, MUTE, VOLUME_DOWN, VOLUME_UP, ACTIVE.
    # A display has no navigation or playback keys on the BK-808 (the device
    # web interface's output pad has only these six), so the D-pad, OK, Menu
    # and Back the remote used to offer are gone: the hub refuses them.
    CEC_COMMANDS = list(OreiMatrix.CEC_OUTPUT_COMMAND_MAP)

    # Use factory pattern for command handler (reduces ~60 lines of duplicate code)
    cec_cmd_handler = create_cec_command_handler(output_num, "output", get_output_cec_method)

    # Create UI page with TV/display controls
    from ucapi.ui import Size, UiPage, create_ui_text

    control_page = UiPage(
        f"output_{output_num}_control",
        "TV Control",
        grid=Size(4, 3),
        items=[
            # Power row
            create_ui_text("📺 Power On", 0, 0, Size(2, 1), "POWER_ON"),
            create_ui_text("⏻ Power Off", 2, 0, Size(2, 1), "POWER_OFF"),
            # The output pad's "active/input" key: make the display select the matrix
            create_ui_text("Input", 1, 1, Size(2, 1), "ACTIVE"),
            # Volume
            create_ui_text("🔉", 0, 2, Size(1, 1), "VOLUME_DOWN"),
            create_ui_text("🔇 Mute", 1, 2, Size(2, 1), "MUTE"),
            create_ui_text("🔊", 3, 2, Size(1, 1), "VOLUME_UP"),
        ],
    )

    # The state is the display's power as far as the hub knows (UNKNOWN until it sent a power command).
    remote = Remote(
        entity_id,
        f"{display_name} TV",
        [
            RemoteFeatures.SEND_CMD,
            RemoteFeatures.ON_OFF,
            # Power toggle (UC-24, DI-13): from the tracked power state, unknown -> on (_toggle_turns_on).
            RemoteFeatures.TOGGLE,
        ],
        attributes={RemoteAttr.STATE: RemoteStates.UNKNOWN},
        simple_commands=CEC_COMMANDS,
        ui_pages=[control_page],
        cmd_handler=cec_cmd_handler,
    )

    return remote


def create_output_media_player(
    output_num: int, output_name: str = None, input_names: dict[int, str] = None
) -> MediaPlayer:
    """
    Create a MediaPlayer entity for a specific output with source selection.

    This provides the native UC source selector UI for switching inputs on an output.
    ``source`` is the input routed to the output (from the poller; empty until
    known). ``state`` is the display's power as far as the hub knows: UNKNOWN
    until it sent a power command (routing a source does not switch a TV on).

    :param output_num: Output number (1-8)
    :param output_name: Custom name for the output (optional)
    :param input_names: Dictionary mapping input numbers to names
    :return: MediaPlayer entity
    """
    display_name = output_name if output_name else f"Output {output_num}"
    entity_id = f"media_player.output_{output_num}"

    # Build source list from input names
    if not input_names:
        input_names = {i: f"Input {i}" for i in range(1, 9)}

    source_list = [input_names.get(i, f"Input {i}") for i in range(1, 9)]

    async def display_power(matrix: OreiMatrix, turn_on: bool) -> StatusCodes:
        if turn_on:
            success = await matrix.cec_output_power_on(output_num)
        else:
            success = await matrix.cec_output_power_off(output_num)
        if success:
            _set_device_power("output", output_num, turn_on)
        return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

    async def media_player_cmd_handler(
        entity: MediaPlayer, cmd_id: str, params: dict[str, Any] | None, websocket: Any = None
    ) -> StatusCodes:
        """Handle MediaPlayer commands for output switching."""
        _LOG.info("Media player %s: %s %s", entity.id, cmd_id, params or "")

        matrix = get_matrix()
        if matrix is None or not matrix.connected:
            _LOG.error("Matrix not connected")
            return StatusCodes.SERVICE_UNAVAILABLE

        if cmd_id == MediaPlayerCommands.SELECT_SOURCE:
            if params and "source" in params:
                source_name = params["source"]
                _LOG.info(f"Selecting source '{source_name}' for output {output_num}")

                # Find input number from source name
                input_num = None
                for i in range(1, 9):
                    if input_names.get(i) == source_name:
                        input_num = i
                        break

                if input_num is None:
                    # Try parsing "Input X" format
                    try:
                        if source_name.startswith("Input "):
                            input_num = int(source_name.split(" ")[1])
                    except (ValueError, IndexError):
                        pass

                if input_num and 1 <= input_num <= 8:
                    success = await matrix.switch_input(input_num, output_num)
                    if success:
                        _entity_sync.update(entity.id, {MediaPlayerAttr.SOURCE: source_name})
                    return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
                else:
                    _LOG.error(f"Could not find input for source: {source_name}")
                    return StatusCodes.BAD_REQUEST
            return StatusCodes.BAD_REQUEST

        elif cmd_id == MediaPlayerCommands.ON:
            return await display_power(matrix, True)

        elif cmd_id == MediaPlayerCommands.OFF:
            return await display_power(matrix, False)

        elif cmd_id == MediaPlayerCommands.TOGGLE:
            # UC-10: from UNKNOWN (and OFF) a toggle powers the display on, see _toggle_turns_on.
            return await display_power(matrix, _toggle_turns_on("output", output_num))

        elif cmd_id == MediaPlayerCommands.VOLUME_UP:
            success = await matrix.cec_output_volume_up(output_num)
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

        elif cmd_id == MediaPlayerCommands.VOLUME_DOWN:
            success = await matrix.cec_output_volume_down(output_num)
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

        elif cmd_id == MediaPlayerCommands.MUTE_TOGGLE:
            success = await matrix.cec_output_mute(output_num)
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

        _LOG.warning(f"Command not implemented: {cmd_id}")
        return StatusCodes.NOT_IMPLEMENTED

    media_player = MediaPlayer(
        entity_id,
        display_name,
        [
            MediaPlayerFeatures.ON_OFF,
            MediaPlayerFeatures.TOGGLE,
            MediaPlayerFeatures.SELECT_SOURCE,
            MediaPlayerFeatures.VOLUME_UP_DOWN,
            MediaPlayerFeatures.MUTE_TOGGLE,
        ],
        attributes={
            MediaPlayerAttr.STATE: MediaPlayerStates.UNKNOWN,
            MediaPlayerAttr.SOURCE_LIST: source_list,
            MediaPlayerAttr.SOURCE: "",
        },
        device_class=MediaPlayerDeviceClasses.TV,
        cmd_handler=guarded_handler(media_player_cmd_handler),
    )

    return media_player


def create_matrix_power_switch() -> Switch:
    """
    Create a Switch entity for matrix power control.

    Its state is the matrix's power as the device reports it (UC-09): UNKNOWN
    until the first status read, then synced from every poll (a front-panel or
    web-app power change shows within one cycle) and from the hub's own power
    commands at once.

    :return: Switch entity
    """
    entity_id = MATRIX_POWER_SWITCH

    async def switch_cmd_handler(
        entity: Switch, cmd_id: str, params: dict[str, Any] | None, websocket: Any = None
    ) -> StatusCodes:
        """Handle Switch commands for matrix power."""
        _LOG.info("Switch %s: %s", entity.id, cmd_id)

        matrix = get_matrix()
        if matrix is None or not matrix.connected:
            _LOG.error("Matrix not connected")
            return StatusCodes.SERVICE_UNAVAILABLE

        if cmd_id == SwitchCommands.TOGGLE:
            # The last known state (the entity itself shows UNAVAILABLE while the matrix is unreachable);
            # unknown -> on, like every toggle of this integration.
            current = _entity_sync.value(entity.id, SwitchAttr.STATE)
            cmd_id = SwitchCommands.OFF if current == SwitchStates.ON else SwitchCommands.ON

        if cmd_id == SwitchCommands.ON:
            success = await matrix.power_on()
            if success:
                _entity_sync.update(entity.id, {SwitchAttr.STATE: SwitchStates.ON})
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

        elif cmd_id == SwitchCommands.OFF:
            success = await matrix.power_off()
            if success:
                _entity_sync.update(entity.id, {SwitchAttr.STATE: SwitchStates.OFF})
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

        return StatusCodes.NOT_IMPLEMENTED

    switch = Switch(
        entity_id,
        "Matrix Power",
        [
            SwitchFeatures.ON_OFF,
            SwitchFeatures.TOGGLE,
        ],
        attributes={SwitchAttr.STATE: SwitchStates.UNKNOWN},
        cmd_handler=guarded_handler(switch_cmd_handler),
    )

    return switch


def _status_sensor(entity_id: str, name: str) -> Sensor:
    """A text status sensor. Its value is unknown until the matrix reported it (UC-04: never made up)."""
    return Sensor(
        entity_id,
        name,
        [],  # No features needed for sensors
        attributes={
            SensorAttr.STATE: SensorStates.UNKNOWN,
            SensorAttr.VALUE: "Unknown",
        },
        device_class=SensorDeviceClasses.CUSTOM,
        options={"custom_unit": ""},
    )


def create_connection_sensor(output_num: int, output_name: str = None) -> Sensor:
    """
    Create a Sensor entity showing if an output has a display connected.

    :param output_num: Output number (1-8)
    :param output_name: Custom name for the output (optional)
    :return: Sensor entity
    """
    display_name = output_name if output_name else f"Output {output_num}"
    return _status_sensor(f"sensor.output_{output_num}_connected", f"{display_name} Connected")


def create_routing_sensor(output_num: int, output_name: str = None) -> Sensor:
    """
    Create a Sensor entity showing the current input routed to an output.

    :param output_num: Output number (1-8)
    :param output_name: Custom name for the output (optional)
    :return: Sensor entity
    """
    display_name = output_name if output_name else f"Output {output_num}"
    return _status_sensor(f"sensor.output_{output_num}_source", f"{display_name} Source")


def create_input_signal_sensor(input_num: int, input_name: str = None) -> Sensor:
    """
    Create a Sensor entity showing if an input has an active signal.

    :param input_num: Input number (1-8)
    :param input_name: Custom name for the input (optional)
    :return: Sensor entity
    """
    display_name = input_name if input_name else f"Input {input_num}"
    return _status_sensor(f"sensor.input_{input_num}_signal", f"{display_name} Signal")


def create_input_cable_sensor(input_num: int, input_name: str = None) -> Sensor:
    """
    Create a Sensor entity showing if an input has a cable connected.

    This sensor uses Telnet-based cable detection which is more reliable
    than HTTP signal detection for detecting physical connections.

    :param input_num: Input number (1-8)
    :param input_name: Custom name for the input (optional)
    :return: Sensor entity
    """
    display_name = input_name if input_name else f"Input {input_num}"
    return _status_sensor(f"sensor.input_{input_num}_cable", f"{display_name} Cable")


def create_output_cable_sensor(output_num: int, output_name: str = None) -> Sensor:
    """
    Create a Sensor entity showing if an output has a cable connected.

    This sensor uses Telnet-based cable detection which can detect
    physical HDMI cable connections to displays/TVs.

    :param output_num: Output number (1-8)
    :param output_name: Custom name for the output (optional)
    :return: Sensor entity
    """
    display_name = output_name if output_name else f"Output {output_num}"
    return _status_sensor(f"sensor.output_{output_num}_cable", f"{display_name} Cable")


def _preset_page(page_id: str, title: str, presets: list[int], view: PresetView) -> Any:
    """A 4x6 page of preset buttons, two per row, labelled with the web app's preset names."""
    from ucapi.ui import Size, UiPage, create_ui_text

    items = [
        create_ui_text(view.name(n), (i % 2) * 2, i // 2, Size(2, 1), f"PRESET_{n}")
        for i, n in enumerate(presets)
    ]
    return UiPage(page_id, title, grid=Size(4, 6), items=items)


def create_matrix_remote(view: PresetView | None = None) -> Remote:
    """
    Create a remote entity for the OREI Matrix with preset selection.

    Its pages mirror the web app's presets (UC-14): a "Favourites" page with
    the web app's favourite presets (only when there are any; the web app's
    quick actions list them first too), then the "Presets" page with all
    eight, labelled with the names the web app shows. The simple commands stay
    ``PRESET_1`` ... ``PRESET_8`` whatever the names are, so activities and
    macros keep working after a rename.

    :param view: preset names and favourites (default: "Preset N", no favourites)
    :return: Remote entity
    """
    view = view or PresetView(names=tuple(f"Preset {n}" for n in range(1, 9)), favourites=())

    async def remote_cmd_handler(
        entity: Remote, cmd_id: str, params: dict[str, Any] | None, websocket: Any = None
    ) -> StatusCodes:
        """Handle remote entity commands."""
        _LOG.info("Matrix remote %s: %s %s", entity.id, cmd_id, params or "")

        matrix = get_matrix()
        if matrix is None or not matrix.connected:
            _LOG.error("Matrix not connected")
            return StatusCodes.SERVICE_UNAVAILABLE

        # Handle scene recall via send_cmd
        if cmd_id == RemoteCommands.SEND_CMD:
            if params and "command" in params:
                command = params["command"]
                # Check if it's a preset command
                if isinstance(command, str) and command.startswith("PRESET_"):
                    try:
                        preset_num = int(command.split("_")[1])
                    except (ValueError, IndexError):
                        _LOG.error("Invalid scene command: %s", command)
                        return StatusCodes.BAD_REQUEST
                    _LOG.info(f"Calling matrix recall_preset({preset_num})...")
                    success = await matrix.recall_preset(preset_num)
                    _LOG.info(f"Preset recall result: {success}")
                    return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

        _LOG.warning(f"Command not implemented: {cmd_id}")
        return StatusCodes.NOT_IMPLEMENTED

    # Define simple commands for each preset
    simple_commands = [f"PRESET_{i}" for i in range(1, 9)]

    pages = []
    if view.favourites:
        pages.append(_preset_page("orei_matrix_favourites", "Favourites", list(view.favourites), view))
    pages.append(_preset_page("orei_matrix_main", "Presets", list(range(1, 9)), view))

    remote = Remote(
        "remote.orei_matrix",
        "OREI Matrix",
        [RemoteFeatures.SEND_CMD],
        attributes={RemoteAttr.STATE: RemoteStates.ON},
        simple_commands=simple_commands,
        ui_pages=pages,
        cmd_handler=guarded_handler(remote_cmd_handler),
    )

    return remote


# =============================================================================
# Status Polling - hub-owned, independent of any Remote (UC-17)
# =============================================================================


def _valid_input(value: Any) -> bool:
    """Input numbers are 1-8; 0 or anything else in the routing array means "unknown" (UC-04)."""
    return isinstance(value, int) and not isinstance(value, bool) and 1 <= value <= 8


async def poll_matrix_status() -> None:
    """One status poll: update the Remote's entities (last known values only).

    Nothing is updated from a read that failed, and a poll stops as soon as
    the matrix link is lost, so the Remote never sees placeholders ("Input 0",
    "Disconnected") for values the hub does not know (UC-04, BE-08).

    The /ws events for web clients are not sent from here: the hub's own
    event stream (rest_api/events.py) announces every change once, with or
    without a Remote (UC-17, docs/api/WEBSOCKET.md).
    """
    matrix = get_matrix()
    await publish_device_state()
    if matrix is None or _driver_state.api is None:
        return
    _entity_sync.set_available(matrix.connected)
    if not matrix.connected:
        _LOG.debug("Polling skipped - matrix not connected")
        return

    _LOG.debug("Polling matrix status...")
    video_status = await matrix.get_video_status()
    output_status = await matrix.get_output_status()
    if not matrix.connected:
        _LOG.debug("Matrix link lost during the poll - keeping the last known values")
        return

    if video_status:
        sync_matrix_power(video_status.get("power"))  # UC-09
        if isinstance(video_status.get("allname"), list):
            refresh_presets(video_status["allname"])  # the matrix's own preset names (UC-14)
    routing = per_output(video_status.get("allsource")) if video_status else []
    connections = per_output(output_status.get("allconnect")) if output_status else []

    for output_num in range(1, 9):
        idx = output_num - 1
        if idx < len(connections):
            is_connected = connections[idx] == 1
            conn_state = "Connected" if is_connected else "Disconnected"
            _entity_sync.update(
                f"sensor.output_{output_num}_connected",
                {SensorAttr.VALUE: conn_state, SensorAttr.STATE: SensorStates.ON},
            )

        current_input = routing[idx] if idx < len(routing) else None
        if not _valid_input(current_input):
            continue  # unknown: keep the last known source
        input_name = _driver_state.input_names.get(current_input, f"Input {current_input}")
        _entity_sync.update(
            f"sensor.output_{output_num}_source", {SensorAttr.VALUE: input_name, SensorAttr.STATE: SensorStates.ON}
        )
        _entity_sync.update(f"media_player.output_{output_num}", {MediaPlayerAttr.SOURCE: input_name})

    _LOG.debug(f"Polling complete - routing: {routing}, connections: {connections}")

    # Get input status for signal detection
    input_status = await matrix.get_input_status()
    if not matrix.connected:
        return
    if input_status:
        inactive_inputs = input_status.get("inactive", []) or []
        for input_num in range(1, 9):
            # inactive array from get_input_status: 1 = signal present, 0 = no signal
            inp_idx = input_num - 1
            if inp_idx < len(inactive_inputs):
                has_signal = inactive_inputs[inp_idx] == 1
                _entity_sync.update(
                    f"sensor.input_{input_num}_signal",
                    {SensorAttr.VALUE: "Active" if has_signal else "No Signal", SensorAttr.STATE: SensorStates.ON},
                )
        _LOG.debug(f"Input signal polling complete - inactive: {inactive_inputs}")

    # Get cable status from Telnet if available
    if matrix.telnet_connected:
        cable_status = await matrix.get_all_cable_status()
        if not matrix.connected:
            return
        if cable_status:
            for side in ("inputs", "outputs"):
                port_kind = side[:-1]  # "input" / "output"
                cables = cable_status.get(side, {})
                for port in range(1, 9):
                    is_connected = cables.get(port)
                    if is_connected is None:
                        attrs = {SensorAttr.VALUE: "Unknown", SensorAttr.STATE: SensorStates.UNKNOWN}
                    else:
                        attrs = {
                            SensorAttr.VALUE: "Connected" if is_connected else "Disconnected",
                            SensorAttr.STATE: SensorStates.ON,
                        }
                    _entity_sync.update(f"sensor.{port_kind}_{port}_cable", attrs)


def request_poll() -> None:
    """Run the next poll now (link came up, Remote woke up) instead of after POLLING_INTERVAL."""
    _poll_wakeup.set()


async def status_polling_loop() -> None:
    """
    Background task that polls the matrix status and updates entities.

    Started with the hub, not with a Remote (UC-17); there is exactly one
    (start_status_polling). Runs every POLLING_INTERVAL seconds, or sooner
    after request_poll(). A failed poll is logged and the next one runs;
    cancellation stops it (CancelledError is re-raised).
    """
    _LOG.info(f"Status polling started (interval: {POLLING_INTERVAL}s)")

    while True:
        try:
            try:
                await asyncio.wait_for(_poll_wakeup.wait(), POLLING_INTERVAL)
            except TimeoutError:
                pass
            _poll_wakeup.clear()
            await poll_matrix_status()
        except asyncio.CancelledError:
            _LOG.info("Status polling cancelled")
            raise
        except Exception as e:
            _LOG.warning(f"Error during status polling: {e}", exc_info=True)
            # Continue polling despite errors


async def start_status_polling():
    """Start the background status polling task (idempotent: one poller)."""
    global _polling_task

    if not POLLING_ENABLED:
        _LOG.info("Status polling disabled (POLLING_ENABLED=false)")
        return

    async with _polling_task_lock:
        if _polling_task is not None and not _polling_task.done():
            _LOG.debug("Status polling already running")
            return
        _polling_task = create_supervised_task(status_polling_loop, "status_polling")
        _driver_state.polling_task = _polling_task
        _LOG.info("Status polling task started")


async def stop_status_polling():
    """Stop the background status polling task and wait until it has stopped."""
    global _polling_task

    async with _polling_task_lock:
        task, _polling_task = _polling_task, None
        _driver_state.polling_task = None
        if task is not None:
            await cancel_and_wait(task, "status_polling")
            _LOG.info("Status polling task stopped")


# =============================================================================
# Device state (UC-04)
# =============================================================================


def device_state_for(matrix: Any) -> ucapi.DeviceStates:
    """The integration's device state for the matrix connection state."""
    if matrix is None:
        return ucapi.DeviceStates.DISCONNECTED
    state = getattr(matrix, "connection_state", None)
    if state in (ConnectionState.CONNECTED, ConnectionState.DEGRADED):
        return ucapi.DeviceStates.CONNECTED
    if state == ConnectionState.CONNECTING:
        return ucapi.DeviceStates.CONNECTING
    if state == ConnectionState.BACKOFF:
        return ucapi.DeviceStates.ERROR
    if state is None:
        return ucapi.DeviceStates.CONNECTED if getattr(matrix, "connected", False) else ucapi.DeviceStates.ERROR
    return ucapi.DeviceStates.DISCONNECTED


async def publish_device_state(force: bool = False) -> None:
    """Tell the Remote the device state when it changed (``force``: always, e.g. answering `connect`).

    Held back while the Remote is in standby (sent on wake).
    """
    api = _driver_state.api
    if api is None:
        return
    state = device_state_for(get_matrix())
    if _entity_sync.standby and not force:
        return
    if force or state != api.device_state:
        _LOG.info("Device state: %s", state.value if hasattr(state, "value") else state)
        await api.set_device_state(state)


# =============================================================================
# Remote lifecycle events (the Remote never connects/disconnects the matrix: UC-17)
# =============================================================================


async def _await_startup_connect() -> None:
    """Let a Remote that connects during start-up get the real state, not an in-between one."""
    task = _driver_state.startup_task
    if task is not None and not task.done():
        await asyncio.wait({task}, timeout=STARTUP_CONNECT_WAIT)
    matrix = get_matrix()
    if matrix is not None and matrix.connection_state == ConnectionState.CONNECTING:
        with_timeout = asyncio.wait_for(asyncio.shield(matrix.connect()), STARTUP_CONNECT_WAIT)
        try:
            await with_timeout
        except TimeoutError:
            pass


async def refresh_matrix_preset_names(matrix: OreiMatrix) -> None:
    """Read the matrix's own preset names (``allname``) and power, and apply them (UC-14, UC-09)."""
    try:
        video = await matrix.get_video_status()
    except Exception as ex:
        _LOG.debug("Could not read the matrix's preset names: %s", ex)
        return
    if not video:
        return
    sync_matrix_power(video.get("power"))
    if isinstance(video.get("allname"), list):
        refresh_presets(video["allname"])


async def refresh_names(matrix: OreiMatrix, *, save: bool = False) -> None:
    """Re-read the port names; when they changed, rebuild the offered entities with them.

    The entities are replaced in place (subscriptions stay). The matrix's own
    preset names are read too (the web app's fallback names, UC-14).
    """
    await refresh_matrix_preset_names(matrix)
    fresh_names = await matrix.get_all_input_names()
    if not fresh_names or fresh_names == _driver_state.input_names:
        _LOG.debug("Input names unchanged")
        return
    generic = {n: f"Input {n}" for n in range(1, 9)}
    if fresh_names == generic and any(_driver_state.input_names.get(n) != name for n, name in generic.items()):
        # get_all_input_names() answers the generic names when the read fails (BE-16); never replace real
        # names with them (they would also be saved and handed to the web app).
        _LOG.warning("Input name read returned only default names; keeping the known names")
        return
    _LOG.info(f"Input names changed! Old: {_driver_state.input_names}, New: {fresh_names}")
    set_input_names(fresh_names)
    fresh_output_names = await matrix.get_output_names()
    if fresh_output_names:
        set_output_names(fresh_output_names)
    install_entities(rebuild=True)
    await update_input_names(_driver_state.input_names)
    await update_output_names(_driver_state.output_names)
    if save:
        save_config(matrix.host, matrix.port, _driver_state.input_names, _driver_state.output_names,
                    credentials=own_credentials(matrix))


async def on_connect() -> None:
    """The Remote (re)connected (`connect`): answer with the device state; the matrix is hub-owned."""
    _LOG.info("Remote connect")
    _entity_sync.set_standby(False)

    await _await_startup_connect()
    matrix = get_matrix()
    if matrix is not None and matrix.connected:
        try:
            await refresh_names(matrix)
        except Exception as ex:
            _LOG.warning(f"Failed to query input names on connect: {ex}")

    await publish_device_state(force=True)
    request_poll()


async def on_disconnect() -> None:
    """The Remote sent `disconnect`. The matrix and the poller serve the whole hub, so they keep running."""
    _LOG.info("Remote disconnect: the matrix connection and status polling stay up (hub-owned)")


async def on_client_connected() -> None:
    """A WebSocket client (a Remote) connected (ucapi >= 0.4 `CLIENT_CONNECTED`)."""
    api = _driver_state.api
    _LOG.info("Integration client connected (%d connected)", api.client_count if api else 0)


async def on_client_disconnected() -> None:
    """A WebSocket client went away (ucapi >= 0.4 `CLIENT_DISCONNECTED`; no longer reported as `disconnect`).

    Nothing to stop: polling and the matrix are hub-owned. When the last
    client is gone the standby flag is cleared, so a Remote that reconnects
    after sleeping starts with a full resync.
    """
    api = _driver_state.api
    remaining = api.client_count if api else 0
    _LOG.info("Integration client disconnected (%d still connected)", remaining)
    if remaining == 0 and _entity_sync.standby:
        _entity_sync.set_standby(False)


async def on_enter_standby() -> None:
    """Remote standby: only pause the pushes to the Remote (never disconnect the matrix, UC-17/UC-06)."""
    _LOG.info("Remote entering standby")
    _entity_sync.set_standby(True)


async def on_exit_standby() -> None:
    """Remote awake: send what changed meanwhile and poll now."""
    _LOG.info("Remote exiting standby")
    _entity_sync.set_standby(False)
    await publish_device_state()
    request_poll()


async def on_subscribe_entities(entity_ids: list[str]) -> None:
    """
    Subscribe to entities: they start with their full current state.

    :param entity_ids: entity identifiers.
    """
    _LOG.info(f"Subscribe entities: {entity_ids}")
    api = _driver_state.api
    if api is None:
        return

    # ucapi already added the available entities to configured_entities; unknown ids are logged.
    for entity_id in entity_ids:
        if api.available_entities.contains(entity_id):
            entity = api.available_entities.get(entity_id)
            api.configured_entities.add(entity)
        else:
            _LOG.warning(f"Entity {entity_id} not found in available_entities")

    _entity_sync.resend([e for e in entity_ids if api.configured_entities.contains(e)])


async def on_unsubscribe_entities(entity_ids: list[str]) -> None:
    """
    Unsubscribe from entities.

    :param entity_ids: entity identifiers.
    """
    _LOG.info(f"Unsubscribe entities: {entity_ids}")
    api = _driver_state.api
    if api is None:
        return

    # Remove each unsubscribed entity from configured_entities
    for entity_id in entity_ids:
        if api.configured_entities.contains(entity_id):
            api.configured_entities.remove(entity_id)


# =============================================================================
# Matrix connection events. The matrix reconnects itself (OreiMatrix, BE-04);
# the driver only reflects its state (BE-06: no reconnect loop of its own).
# =============================================================================


def on_matrix_connected():
    """The matrix link is up (first connect or a reconnect): entities available, resync now."""
    _LOG.info("Matrix connected")
    _entity_sync.set_available(True)
    startup = _driver_state.startup_task
    if startup is None or startup.done():
        # During start-up, startup_connect() reports CONNECTED once the names are refreshed too.
        _spawn(publish_device_state(), "uc_device_state")
    request_poll()


def on_matrix_disconnected():
    """The matrix link is down (lost: the matrix is reconnecting; or an intentional disconnect)."""
    matrix = get_matrix()
    reconnecting = matrix is not None and getattr(matrix, "connection_state", None) == ConnectionState.BACKOFF
    _LOG.warning("Matrix disconnected%s", " - the matrix is reconnecting" if reconnecting else "")
    _entity_sync.set_available(False)
    _spawn(publish_device_state(), "uc_device_state")


def on_matrix_error(error: str):
    """Handle matrix error event (reconnecting is the matrix's job)."""
    _LOG.error("Matrix error: %s", error)


def on_matrix_update(update: dict[str, Any]):
    """A change the hub made on the matrix (from the web app, Home Assistant, a scene, the Remote).

    Shown on the Remote at once, not at the next poll or reconnect:

    * ``power``: the matrix power switch (UC-09);
    * ``input_name`` / ``output_name``: a port rename; the entities are
      replaced in place and the subscribed media players get the new source
      list, so a source can be chosen by its new name right away (UC-08);
    * ``preset_name``: the matrix's own preset name (UC-14).
    """
    _LOG.debug("Matrix update: %s", update)
    if not isinstance(update, dict):
        return
    if "power" in update:
        sync_matrix_power(update["power"])
    renames = {key: update[key] for key in ("input_name", "output_name") if isinstance(update.get(key), dict)}
    if renames:
        apply_port_renames(renames.get("input_name", {}), renames.get("output_name", {}))
    if isinstance(update.get("preset_name"), dict):
        names = list(_driver_state.preset_matrix_names) or [f"Preset {n}" for n in range(1, 9)]
        names += [f"Preset {n}" for n in range(len(names) + 1, 9)]
        for preset, name in update["preset_name"].items():
            if isinstance(preset, int) and 1 <= preset <= 8:
                names[preset - 1] = str(name)
        refresh_presets(names)


def apply_port_renames(inputs: dict[int, str], outputs: dict[int, str]) -> None:
    """Port names changed on the matrix through the hub: rebuild the entities with them (UC-08).

    The REST API already updated and saved its own names; this brings the
    Remote's entities in line (names, source lists, source selection).
    """
    new_inputs = {**_driver_state.input_names, **{int(k): str(v) for k, v in inputs.items()}}
    new_outputs = {**_driver_state.output_names, **{int(k): str(v) for k, v in outputs.items()}}
    if new_inputs == _driver_state.input_names and new_outputs == _driver_state.output_names:
        return
    _LOG.info("Port renamed through the hub: inputs %s, outputs %s", inputs, outputs)
    set_input_names(new_inputs)
    set_output_names(new_outputs)
    install_entities(rebuild=True)


def attach_matrix(matrix: OreiMatrix) -> None:
    """Follow the matrix's connection events."""
    matrix.events.on(MatrixEvents.CONNECTED, on_matrix_connected)
    matrix.events.on(MatrixEvents.DISCONNECTED, on_matrix_disconnected)
    matrix.events.on(MatrixEvents.ERROR, on_matrix_error)
    matrix.events.on(MatrixEvents.UPDATE, on_matrix_update)


async def dispose_matrix(matrix: OreiMatrix | None) -> None:
    """Stop listening to a matrix and close its session, Telnet and reconnect task (BE-10)."""
    if matrix is None:
        return
    try:
        matrix.events.remove_all_listeners()
    except Exception as e:
        _LOG.debug(f"Removing matrix listeners failed: {e}")
    try:
        await asyncio.wait_for(matrix.disconnect(), 10)
    except Exception as e:
        _LOG.warning(f"Error disconnecting old matrix {matrix.host}: {e}")


def _wire_rest_api() -> None:
    """Hand the matrix, names and config file to the REST API, and the CEC sender to the macros."""
    set_matrix_device(
        get_matrix(),
        input_names=_driver_state.input_names,
        output_names=_driver_state.output_names,
        config_file=config_file_path(),
    )
    set_macro_cec_sender(macro_cec_sender)


# =============================================================================
# Start-up restore (UC-19) and setup (UC-05, BE-02, BE-10)
# =============================================================================


async def restore_from_config() -> bool:
    """
    Restore entities and the matrix from the saved configuration, without waiting for the matrix.

    Everything here is local (config file, entities, REST wiring, poller): the
    entities exist before the Remote can ask for them, and an unreachable or
    hanging matrix never delays start-up. The connection is made in the
    background (:func:`startup_connect`); until it is up, entities are
    UNAVAILABLE with unknown values.

    Without a saved setup, ``MATRIX_HOST`` (and ``MATRIX_PORT``/``OREI_PORT``)
    is used, so the web app has the matrix before a Remote is set up. It is
    never saved: a saved setup (the Remote's) always wins over the variable.

    :return: True if a configuration was restored, False otherwise
    """
    config: dict[str, Any] | None = load_config()
    from_env = False
    if not config:
        env_host = os.environ.get("MATRIX_HOST", "").strip()
        if not env_host:
            _LOG.info("No saved configuration found - waiting for setup")
            return False
        env_port = int(os.environ.get("MATRIX_PORT") or os.environ.get("OREI_PORT") or "443")
        config = {"host": env_host, "port": env_port}
        from_env = True
        _LOG.info("No saved setup: using MATRIX_HOST %s:%d until the Remote's setup saves one", env_host, env_port)

    host = config.get("host")
    port = config.get("port", 443)
    if not host:
        _LOG.warning("No host in saved configuration")
        return False

    _LOG.info(f"Restoring: host={host}, port={port}")
    input_names = config.get("input_names", {})
    output_names = config.get("output_names", {})
    set_input_names(input_names if input_names else {i: f"Input {i}" for i in range(1, 9)})
    set_output_names(output_names if output_names else {i: f"Output {i}" for i in range(1, 9)})

    # The login entered in the Remote's setup for this matrix, else OREI_USER / OREI_PASSWORD (UC-02).
    matrix = OreiMatrix(host, port, user=config.get("user"), password=config.get("password"))
    attach_matrix(matrix)
    set_matrix(matrix)
    install_entities()
    _wire_rest_api()
    await start_status_polling()
    _driver_state.startup_task = _spawn(startup_connect(matrix, save=not from_env), "matrix_startup_connect")
    return True


async def startup_connect(matrix: OreiMatrix, *, save: bool = True) -> None:
    """Connect the restored matrix; if it is unreachable, let it keep trying on its own.

    ``save``: store refreshed names in the saved setup (not for a MATRIX_HOST-only start).
    """
    try:
        ok = await matrix.connect()
    except Exception as e:
        _LOG.warning(f"Could not connect to matrix on startup: {e}")
        ok = False
    if get_matrix() is not matrix:
        return  # replaced by a setup in the meantime
    if not ok:
        _LOG.warning("Matrix not reachable at start-up; reconnecting in the background")
        matrix.start_auto_reconnect()
        await publish_device_state()
        return
    try:
        await refresh_names(matrix, save=save)
    except Exception as e:
        _LOG.warning(f"Could not refresh names at start-up: {e}")
    await publish_device_state()


#: The matrix address on the setup's first page: an IPv4 address or a host name (driver.json uses the same
#: pattern to validate the field). No scheme, path or port.
HOST_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$")
#: How long the setup waits for the new address to accept a connection.
SETUP_PROBE_TIMEOUT = 5.0

_SETUP_ERRORS = {
    "auth": ucapi.IntegrationSetupError.AUTHORIZATION_ERROR,
    "timeout": ucapi.IntegrationSetupError.TIMEOUT,
    "not_found": ucapi.IntegrationSetupError.NOT_FOUND,
    "refused": ucapi.IntegrationSetupError.CONNECTION_REFUSED,
}


@dataclass
class PendingSetup:
    """A setup waiting on its login page (UC-05): the address from the first page."""

    host: str
    port: int


_pending_setup: PendingSetup | None = None


def parse_setup_address(setup_data: dict[str, Any]) -> tuple[str, int] | None:
    """``(host, port)`` from the first setup page, or None when they are not a usable address."""
    host = str(setup_data.get("host") or "").strip()
    if not HOST_PATTERN.fullmatch(host):
        return None
    try:
        port = int(setup_data.get("port") or 443)
    except (TypeError, ValueError):
        return None
    return (host, port) if 1 <= port <= 65535 else None


async def probe_address(host: str, port: int, timeout: float = SETUP_PROBE_TIMEOUT
                        ) -> ucapi.IntegrationSetupError | None:
    """Whether the hub can open a connection to ``host:port``; nothing is sent (no credentials, UC-02).

    :return: None if it can, else the setup error that says why not.
    """
    try:
        _reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
    except TimeoutError:
        return ucapi.IntegrationSetupError.TIMEOUT
    except socket.gaierror:
        return ucapi.IntegrationSetupError.NOT_FOUND
    except OSError:
        return ucapi.IntegrationSetupError.CONNECTION_REFUSED
    writer.close()
    with contextlib.suppress(Exception):
        await writer.wait_closed()
    return None


def login_page(host: str, port: int) -> ucapi.RequestUserInput:
    """The setup's credential step (UC-05): the matrix login for a new address, never pre-filled."""
    return ucapi.RequestUserInput(
        {"en": "Matrix login"},
        [
            {
                "id": "info",
                "label": {"en": "Matrix login"},
                "field": {"label": {"value": {"en": (
                    f"Enter the login of the matrix at {host}:{port}, the one its own web interface uses "
                    "(factory default: Admin / admin). It is sent only to this address."
                )}}},
            },
            {"id": "user", "label": {"en": "User"}, "field": {"text": {"value": "Admin"}}},
            {"id": "password", "label": {"en": "Password"}, "field": {"password": {}}},
        ],
    )


async def connect_for_setup(host: str, port: int, *, user: str | None = None, password: str | None = None
                            ) -> tuple[OreiMatrix | None, ucapi.IntegrationSetupError | None]:
    """Log in to ``host:port`` with a temporary client; on failure it is disposed and the reason returned."""
    probe = OreiMatrix(host, port, user=user, password=password)
    try:
        if await probe.connect():
            return probe, None
        failure = probe.login_failure
    except Exception as ex:
        _LOG.error("Setup: connecting to %s:%d failed: %s", host, port, ex)
        failure = "other"
    await dispose_matrix(probe)
    return None, _SETUP_ERRORS.get(failure or "", ucapi.IntegrationSetupError.OTHER)


async def adopt_setup_matrix(matrix: OreiMatrix) -> ucapi.SetupAction:
    """Make the matrix the setup connected to the hub's matrix: names, entities, saved setup, poller.

    The previous matrix (if another one) is disposed (BE-10). Entities are
    updated in place: the subscribed ones are never cleared (UC-05).
    """
    current = get_matrix()
    try:
        input_names = await matrix.get_all_input_names()
        output_names = await matrix.get_output_names()
        _LOG.info(f"Input names retrieved: {input_names}")
        _LOG.info(f"Output names retrieved: {output_names}")

        if matrix is not current:
            attach_matrix(matrix)
            set_matrix(matrix)
            await dispose_matrix(current)
            _entity_sync.set_available(matrix.connected)
    except Exception as e:
        _LOG.error(f"Setup failed with exception: {e}", exc_info=True)
        if matrix is not current and get_matrix() is not matrix:
            await dispose_matrix(matrix)
        return ucapi.SetupError(error_type=ucapi.IntegrationSetupError.OTHER)

    names_changed = (input_names or {}) != _driver_state.input_names or (
        output_names or {}
    ) != _driver_state.output_names
    set_input_names(input_names if input_names else {})
    set_output_names(output_names if output_names else {})
    await refresh_matrix_preset_names(matrix)
    api = _driver_state.api
    if api is not None and api.available_entities.get_all() and names_changed:
        install_entities(rebuild=True)
    else:
        install_entities()

    save_config(matrix.host, matrix.port, _driver_state.input_names, _driver_state.output_names,
                credentials=own_credentials(matrix))
    _wire_rest_api()  # sync (BE-02: it used to be awaited, which failed every setup)
    await start_status_polling()
    await publish_device_state()
    request_poll()
    _LOG.info("Setup complete (%s:%d)", matrix.host, matrix.port)
    return ucapi.SetupComplete()


async def handle_driver_setup(msg: ucapi.DriverSetupRequest) -> ucapi.SetupAction:
    """
    First setup page (address), for a new setup and a reconfigure (UC-05, UC-02 short term).

    * The same address as the hub's matrix: its login already goes there, so
      the setup completes without asking (a reconfigure that only confirms).
      If that login is now rejected, the login page is shown.
    * A new address: the hub first checks that it accepts a connection
      (nothing is sent; unreachable -> CONNECTION_REFUSED / NOT_FOUND /
      TIMEOUT), then asks for that matrix's login. The configured login is
      never sent to a new address.

    Nothing changes until a login succeeds: a typo leaves a working
    installation untouched. The setup data is never logged (the password
    field is also redacted by ucapi's message log).
    """
    global _pending_setup
    _pending_setup = None
    _LOG.info("Starting driver setup (reconfigure: %s)", msg.reconfigure)
    address = parse_setup_address(msg.setup_data or {})
    if address is None:
        _LOG.error("Setup: the matrix address is not a host name or IP address with a port 1-65535")
        return ucapi.SetupError(error_type=ucapi.IntegrationSetupError.NOT_FOUND)
    host, port = address

    current = get_matrix()
    if current is not None and (current.host, current.port) == (host, port):
        if current.connected:
            _LOG.info("Setup: keeping the working connection to %s:%d", host, port)
            return await adopt_setup_matrix(current)
        _LOG.info("Setup: reconnecting to %s:%d with its saved login", host, port)
        own = own_credentials(current)
        matrix, error = await connect_for_setup(host, port, user=own[0] if own else None,
                                                password=own[1] if own else None)
        if matrix is not None:
            return await adopt_setup_matrix(matrix)
        if error != ucapi.IntegrationSetupError.AUTHORIZATION_ERROR:
            _LOG.error("Setup: the matrix at %s:%d did not answer (%s); nothing changed", host, port, error)
            return ucapi.SetupError(error_type=error or ucapi.IntegrationSetupError.OTHER)
        _LOG.info("Setup: the saved login for %s:%d was rejected; asking for it", host, port)
    else:
        error = await probe_address(host, port)
        if error is not None:
            _LOG.error("Setup: no connection to %s:%d (%s); nothing changed", host, port, error)
            return ucapi.SetupError(error_type=error)
        _LOG.info("Setup: %s:%d is a new matrix address; asking for its login", host, port)
    _pending_setup = PendingSetup(host, port)
    return login_page(host, port)


async def handle_setup_login(msg: ucapi.UserDataResponse) -> ucapi.SetupAction:
    """The login page's answer: log in to the new address with exactly this login (UC-05)."""
    global _pending_setup
    pending, _pending_setup = _pending_setup, None
    if pending is None:
        _LOG.error("Setup: login received without a setup in progress")
        return ucapi.SetupError(error_type=ucapi.IntegrationSetupError.OTHER)
    values = msg.input_values or {}
    user = str(values.get("user") or "").strip() or "Admin"
    password = str(values.get("password") or "")
    matrix, error = await connect_for_setup(pending.host, pending.port, user=user, password=password)
    if matrix is None:
        _LOG.error("Setup: login to %s:%d failed (%s); nothing changed", pending.host, pending.port, error)
        return ucapi.SetupError(error_type=error or ucapi.IntegrationSetupError.OTHER)
    return await adopt_setup_matrix(matrix)


async def setup_handler(msg: ucapi.SetupDriver) -> ucapi.SetupAction:
    """
    Dispatch driver setup messages (driver-setup.md): the first page, the login page, abort.

    :param msg: Setup driver request
    :return: Setup action
    """
    global _pending_setup
    if isinstance(msg, ucapi.DriverSetupRequest):
        result = await handle_driver_setup(msg)
    elif isinstance(msg, ucapi.UserDataResponse):
        result = await handle_setup_login(msg)
    elif isinstance(msg, ucapi.AbortDriverSetup):
        pending, _pending_setup = _pending_setup, None
        _LOG.info("Setup aborted by the Remote (%s)%s; the current configuration is unchanged", msg.error,
                  f", discarding the pending setup for {pending.host}:{pending.port}" if pending else "")
        return ucapi.SetupError()
    else:
        _LOG.error(f"Unsupported setup message type: {type(msg).__name__}")
        _pending_setup = None
        return ucapi.SetupError(error_type=ucapi.IntegrationSetupError.OTHER)
    _LOG.info(f"Setup handler returning: {type(result).__name__}")
    return result


async def shutdown(loop):
    """Cleanup tasks tied to the service's shutdown."""
    _LOG.info("Shutting down integration...")

    # Stop status polling
    await stop_status_polling()

    # Stop REST API server
    rest_api_server = _driver_state.rest_api_server
    if rest_api_server and rest_api_server.running:
        _LOG.info("Stopping REST API server...")
        try:
            await rest_api_server.stop()
        except Exception as e:
            _LOG.warning(f"Error stopping REST API server: {e}")

    # Disconnect from matrix
    matrix = get_matrix()
    if matrix:
        _LOG.info("Disconnecting from matrix...")
        try:
            await matrix.disconnect()
        except Exception as e:
            _LOG.warning(f"Error disconnecting from matrix: {e}")

    # Cancel all remaining tasks
    _LOG.info("Cancelling background tasks...")
    tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]

    for task in tasks:
        if not task.done():
            task.cancel()

    # Wait for all tasks to complete cancellation, suppressing exceptions
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Log any non-cancellation errors
        for i, result in enumerate(results):
            if isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
                # Suppress "address in use" from ucapi's web socket server (BE-21)
                if not is_address_in_use(result):
                    _LOG.warning(f"Task {tasks[i].get_name()} raised: {result}")

    _LOG.info("Shutdown cleanup complete")


def handle_exit_signal(signame, loop):
    """Handle exit signals."""
    _LOG.info(f"Received {signame}, initiating shutdown...")
    asyncio.create_task(shutdown(loop))


def main(driver_json: str | Path | None = None) -> None:
    """Run the driver: integration WebSocket, then restore, then the REST API (UC-19).

    :param driver_json: the driver metadata file to publish (default: ``driver.json`` next to the
        package). A caller that adjusts the metadata (e.g. a driver URL) passes its own copy.
    """
    metadata = Path(driver_json) if driver_json else DRIVER_JSON
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    _LOG.info("Starting OREI HDMI Matrix integration driver")

    # Register cleanup on exit
    atexit.register(release_lock)

    # Acquire lock to prevent multiple instances
    if not acquire_lock():
        _LOG.error("Failed to acquire lock - another instance may be running")
        _LOG.info("Waiting 5 seconds for previous instance to release...")
        time.sleep(5)
        if not acquire_lock():
            _LOG.error("Still cannot acquire lock. Exiting.")
            sys.exit(1)

    # Check that the integration port is available, wait if not (BE-21: the configured port, any OS)
    uc_port = integration_port(metadata)
    if not check_port_available(uc_port):
        _LOG.warning(f"Port {uc_port} is in use, waiting for it to become available...")
        if not wait_for_port(uc_port, timeout=15):
            _LOG.error(f"Could not bind to port {uc_port}. Exiting.")
            release_lock()
            sys.exit(1)

    # Clear any stale mDNS entries from previous crashed instances
    clear_stale_mdns()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Custom exception handler: suppress the known "address in use" error of ucapi's server task
    def handle_exception(loop, context):
        if is_address_in_use(context.get("exception")):
            return
        loop.default_exception_handler(context)

    loop.set_exception_handler(handle_exception)

    api = ucapi.IntegrationAPI(loop)
    _driver_state.api = api

    # Register event handlers after API is created
    api.add_listener(ucapi.Events.CONNECT, on_connect)
    api.add_listener(ucapi.Events.DISCONNECT, on_disconnect)
    api.add_listener(ucapi.Events.CLIENT_CONNECTED, on_client_connected)
    api.add_listener(ucapi.Events.CLIENT_DISCONNECTED, on_client_disconnected)
    api.add_listener(ucapi.Events.ENTER_STANDBY, on_enter_standby)
    api.add_listener(ucapi.Events.EXIT_STANDBY, on_exit_standby)
    api.add_listener(ucapi.Events.SUBSCRIBE_ENTITIES, on_subscribe_entities)
    api.add_listener(ucapi.Events.UNSUBSCRIBE_ENTITIES, on_unsubscribe_entities)

    # Initialize API with retry logic for mDNS issues
    # mDNS records typically have TTL of 75-120 seconds, so we need to wait long enough
    max_retries = 6
    retry_delay = 5  # Start with 5 seconds

    for attempt in range(max_retries):
        try:
            _LOG.info(f"Initializing API (attempt {attempt + 1}/{max_retries})...")
            loop.run_until_complete(api.init(str(metadata), setup_handler))
            _LOG.info("API initialized successfully")
            break
        except Exception as e:
            if "NonUniqueNameException" in str(type(e).__name__) or "NonUniqueNameException" in str(e):
                _LOG.warning(
                    f"mDNS name conflict (attempt {attempt + 1}/{max_retries}), waiting {retry_delay}s before retry..."
                )
                _LOG.info("This can happen if a previous instance didn't shut down cleanly.")
                _LOG.info("The mDNS cache will clear automatically - please wait...")
                time.sleep(retry_delay)
                retry_delay = min(retry_delay + 5, 30)  # Linear increase, max 30 seconds
                if attempt == max_retries - 1:
                    _LOG.error("Failed to initialize API after all retries. mDNS name still in use.")
                    _LOG.error("Try waiting 2 minutes and restarting, or reboot the computer.")
                    release_lock()
                    sys.exit(1)
            else:
                _LOG.error(f"Failed to initialize API: {e}", exc_info=True)
                release_lock()
                sys.exit(1)

    # Restore entities from the saved configuration. It runs before the WebSocket server task has
    # bound its port (no network I/O happens in it), so the entities exist before a Remote can ask;
    # the matrix is connected in the background and never delays start-up (UC-19).
    _LOG.info("Attempting to restore from saved configuration...")
    loop.run_until_complete(restore_from_config())

    # Start REST API server for external integrations (Flic, Home Assistant, etc.)
    if REST_API_ENABLED:
        _LOG.info(f"Starting REST API server on port {REST_API_PORT}...")
        rest_api_server = RestApiServer(port=REST_API_PORT)
        _driver_state.rest_api_server = rest_api_server
        try:
            loop.run_until_complete(rest_api_server.start())
        except Exception as e:
            _LOG.error(f"Failed to start REST API server: {e}")
            _LOG.warning("Continuing without REST API - UC integration will still work")
    else:
        _LOG.info("REST API server disabled (REST_API_ENABLED=false)")

    # The Remote shows the web app's preset names and favourites (UC-14): now that the REST API has
    # loaded the device settings, and after every change the web app saves.
    add_change_listener(on_web_app_settings_changed)
    refresh_presets()

    # Handle graceful shutdown signals (important for Docker)
    def signal_handler(sig, frame):
        _LOG.info(f"Received signal {sig}, initiating shutdown...")
        loop.call_soon_threadsafe(loop.stop)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        _LOG.info("Driver running. Press Ctrl+C to stop.")
        loop.run_forever()
    except KeyboardInterrupt:
        _LOG.info("Keyboard interrupt received")
    except Exception as e:
        _LOG.error(f"Unexpected error: {e}", exc_info=True)
    finally:
        _LOG.info("Cleaning up...")
        try:
            loop.run_until_complete(shutdown(loop))
        except Exception as e:
            _LOG.warning(f"Error during shutdown: {e}")
        loop.close()
        release_lock()
        _LOG.info("Shutdown complete")


if __name__ == "__main__":
    main()
