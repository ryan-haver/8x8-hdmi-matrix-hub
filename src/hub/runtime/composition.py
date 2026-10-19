"""One asynchronous owner for REST, integrations, matrix state and shutdown."""

from __future__ import annotations

import asyncio
import contextlib
import inspect
import json
import logging
import math
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path

from hub.core.event_bus import EventBus
from hub.core.matrix_service import MatrixService
from hub.integrations.hub_client import HubEvent, HubSnapshot
from hub.integrations.hub_client_local import HubClientLocal
from hub.runtime_paths import default_config_dir, driver_metadata_path
from orei_matrix import OreiMatrix

from .actions import run_action_envelope
from .adapters import CommandProvider, MatrixFacade, NullMatrix, TransactionLock
from .config import MatrixAddress, ReconfigureResult, resolve_matrix_address
from .integrations import bind_integrations, build_integration_loader
from .managers import create_managers

_LOG = logging.getLogger(__name__)
CLEANUP_TIMEOUT = 5.0


def _redact(value):
    if isinstance(value, dict):
        return {
            key: _redact(item)
            for key, item in value.items()
            if key.lower() not in {"password", "passcode", "passcode_hash", "password_hash", "pin", "pin_hash"}
        }
    if isinstance(value, (tuple, list)):
        return [_redact(item) for item in value]
    return deepcopy(value)


class HubRuntime:
    def __init__(self, settings, *, environ, prepared, managers, address, matrix_factory):
        self.settings, self.environ = settings, dict(environ)
        self.prepared, self.managers = prepared, managers
        self.address, self.matrix_factory = address, matrix_factory
        self.bus = EventBus()
        self.service = MatrixService(self._make_client(address), bus=self.bus)
        self._restore_names()
        self.transaction = TransactionLock()
        self._reconfigure_lock = asyncio.Lock()
        self.commands = CommandProvider(self)
        self.matrix = MatrixFacade(self)
        from hub.domain.action_runner import ActionRunner

        self.action_runner = ActionRunner(
            self.matrix,
            profile_manager=managers.profiles,
            scene_manager=managers.scenes,
            macro_manager=managers.macros,
            shortcut_manager=managers.shortcuts,
            preset_executor=self.service,
        )
        self.local = HubClientLocal(
            self.commands,
            snapshot_provider=self.snapshot,
            action_runner=lambda *a, **kw: run_action_envelope(self, *a, **kw),
            event_subscribe=self.subscribe,
        )
        managers.macros.set_cec_sender(self.commands.send_cec)
        self.loader = build_integration_loader(self.environ)
        self.server = None
        self.driver_metadata = driver_metadata_path()
        self._temporary_metadata = None
        self._process_lock = None
        self._wake = asyncio.Event()
        self._refresh_task = None
        self._connect_task = None
        self._start_task = None
        self._stop_task = None
        self._operations = set()
        self._raw_unlisten = []
        self._settings_unlisten = None
        self._stopping = False
        self._started = False
        raw_interval = self.environ.get("STATUS_POLL_INTERVAL", "").strip()
        if not raw_interval and settings.uc_enabled:
            raw_interval = self.environ.get("POLLING_INTERVAL", "")
        try:
            interval = float(raw_interval or 5)
            self.poll_interval = max(0.2, interval) if math.isfinite(interval) else 5.0
        except ValueError:
            self.poll_interval = 5.0

    def _make_client(self, address):
        if address is None:
            return NullMatrix()
        return self.matrix_factory(
            address.host,
            port=address.port,
            telnet_port=address.telnet_port,
            user=address.user,
            password=address.password,
        )

    def _restore_names(self):
        primary = self.prepared.paths.config_dir / "config_state.json"
        source = primary if primary.exists() else primary.with_suffix(".json.migrated")
        try:
            saved = json.loads(source.read_text(encoding="utf-8"))
            if (
                not self.address
                or saved.get("host") != self.address.host
                or int(saved.get("port") or 443) != self.address.port
            ):
                return
            for kind in ("input", "output"):
                for port, name in saved.get(f"{kind}_names", {}).items():
                    if str(port).isdigit() and 1 <= int(port) <= 8 and isinstance(name, str):
                        getattr(self.service.names, f"set_{kind}_name")(int(port), name)
        except (OSError, ValueError, TypeError, AttributeError):
            pass

    def snapshot(self) -> HubSnapshot:
        state = self.service.snapshot()

        def known(values):
            return {port: value for port, value in values.items() if value is not None}

        def rows(items):
            return [_redact(item.to_dict() if hasattr(item, "to_dict") else item) for item in items]

        from rest_api.device_settings import get_favorite_presets, preset_display_name

        return HubSnapshot(
            connected=state["connected"],
            power=state["power"] is True,
            routing=known(state["routing"]),
            input_names=state["inputs"],
            output_names=state["outputs"],
            preset_names={p: preset_display_name(p, list(state["presets"].values())) for p in state["presets"]},
            input_signals=known(state["signal"]),
            input_cables=known(state["cables"]["inputs"]),
            output_displays=known({p: fields["connected"] for p, fields in state["display"].items()}),
            favorite_presets=get_favorite_presets(),
            profiles=rows(self.managers.profiles.list_profiles()),
            scenes=rows(self.managers.scenes.list_scenes()),
            macros=rows(self.managers.macros.list_macros()),
            shortcuts=rows(self.managers.shortcuts.list_shortcuts()),
        )

    def subscribe(self, callback):
        def changed(event):
            state = self.snapshot()
            fields = {
                "hub_connection": {"connected": state.connected},
                "power": {"on": state.power},
                "routing": {"routing": state.routing},
                "signal": {"input_signals": state.input_signals},
                "cable": {"input_cables": state.input_cables},
                "display": {"output_displays": state.output_displays},
                "names": {
                    "input_names": state.input_names,
                    "output_names": state.output_names,
                    "preset_names": state.preset_names,
                },
                "presets": {"preset_names": state.preset_names, "favorite_presets": state.favorite_presets},
            }
            deliveries = [callback(HubEvent(event.topic, deepcopy(fields.get(event.topic, event.data))))]
            if event.topic == "cable":
                for port, connected in event.data.get("changed", {}).get("outputs", {}).items():
                    if isinstance(connected, bool):
                        deliveries.append(
                            callback(HubEvent("cable", {"type": "output", "port": port, "connected": connected}))
                        )
            pending = [delivery for delivery in deliveries if inspect.isawaitable(delivery)]
            if pending:
                return asyncio.gather(*pending)
            return None

        return self.bus.subscribe(changed)

    def notify_catalog_changed(self):
        if self._stopping:
            return
        state = self.snapshot()
        self.bus.publish("catalog", {key: getattr(state, key) for key in ("profiles", "scenes", "macros", "shortcuts")})
        self.bus.publish("names", {})
        self.bus.publish("presets", {})

    def request_refresh(self):
        if not self._stopping:
            self._wake.set()

    def _listen(self):
        self._unlisten()
        from orei_matrix import Events

        events = getattr(self.service.client, "events", None)
        if events is None:
            return

        def changed(*_):
            self.request_refresh()

        for event in (Events.CONNECTED, Events.DISCONNECTED, Events.STATE_CHANGED):
            events.on(event, changed)
            self._raw_unlisten.append(lambda event=event: events.remove_listener(event, changed))

    def _unlisten(self):
        for remove in self._raw_unlisten:
            try:
                remove()
            except Exception:
                _LOG.warning("Removing matrix listener failed", exc_info=True)
        self._raw_unlisten.clear()

    @contextlib.asynccontextmanager
    async def operation(self):
        task = asyncio.current_task()
        nested = task in self._operations
        if self._stopping and not nested:
            raise RuntimeError("Hub runtime is stopping")
        self._operations.add(task)
        try:
            async with self.transaction:
                if self._stopping and not nested:
                    raise RuntimeError("Hub runtime is stopping")
                yield
        finally:
            if not nested:
                self._operations.discard(task)

    async def command(self, method, *args, **kwargs):
        async with self.operation():
            result = await method(*args, **kwargs)
            self.request_refresh()
            return result

    async def protocol(self, name, *args, **kwargs):
        async with self.operation():
            result = await getattr(self.service.client, name)(*args, **kwargs)
            if not name.startswith(("get_", "is_")):
                self.request_refresh()
            return result

    async def connect(self):
        async with self.operation():
            if not self.address:
                return False
            if self.service.connected:
                return True
            return await self.service.connect()

    async def refresh(self, *, force_refresh=False):
        async with self.operation():
            self.service._sync_connection()
            if force_refresh:
                self.service.invalidate_preset_cache()
                self.service.invalidate_cec_cache()
            if self.service.connected:
                await self.service.refresh_snapshot()

    async def _refresh_loop(self):
        while True:
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(self._wake.wait(), self.poll_interval)
            self._wake.clear()
            try:
                await self.refresh()
            except asyncio.CancelledError:
                raise
            except Exception:
                _LOG.exception("Runtime refresh failed")

    async def run_action(self, kind, action_id, *, passcode=None, params=None):
        async with self.operation():
            return await self.action_runner.run(kind, action_id, passcode=passcode, params=params)

    async def start(self):
        if self._started:
            return
        if self._stopping:
            raise RuntimeError("Hub runtime is stopping")
        self._start_task = asyncio.current_task()
        try:
            if self.settings.uc_enabled and self._process_lock is None:
                from _process_lock import ProcessLock

                self._process_lock = ProcessLock(self.prepared.paths.config_dir / "driver.lock")
                self._process_lock.acquire()
            if self.settings.uc_driver_url:
                import tempfile

                from _file_io import atomic_write_json

                with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as target:
                    self._temporary_metadata = Path(target.name)
                metadata = json.loads(self.driver_metadata.read_text(encoding="utf-8"))
                metadata["driver_url"] = self.settings.uc_driver_url
                atomic_write_json(self._temporary_metadata, metadata)
                self.driver_metadata = self._temporary_metadata
            self._listen()
            self.loader.load()
            bind_integrations(self.loader, self)
            from rest_api import RestApiServer
            from rest_api.device_settings import add_change_listener, remove_change_listener

            add_change_listener(self.notify_catalog_changed)
            self._settings_unlisten = lambda: remove_change_listener(self.notify_catalog_changed)
            self.server = RestApiServer(
                data_dir=self.prepared.paths.data_dir,
                runtime=self,
                port=self.settings.api_port,
                integration_routes=self.loader.routes(),
            )
            await self.server.start()
            await self.loader.start(self.local)
            self._connect_task = asyncio.create_task(self._initial_connect(), name="hub_initial_connect")
            self._refresh_task = asyncio.create_task(self._refresh_loop(), name="hub_runtime_refresh")
            self._started = True
        except BaseException:
            self._start_task = None
            if not self._stopping:
                await self.stop()
            raise
        finally:
            self._start_task = None

    async def _initial_connect(self):
        try:
            connected = await self.connect()
            if not connected and self.address and not self._stopping:
                reconnect = getattr(self.service.client, "start_auto_reconnect", None)
                if reconnect:
                    reconnect()
        except asyncio.CancelledError:
            raise
        except Exception:
            _LOG.warning("Matrix unavailable at startup; REST remains available")

    async def _cancel(self, tasks):
        tasks = {task for task in tasks if task and task is not asyncio.current_task() and not task.done()}
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.wait(tasks, timeout=CLEANUP_TIMEOUT)

    async def _cleanup(self, function):
        try:
            await asyncio.wait_for(function(), CLEANUP_TIMEOUT)
        except (Exception, asyncio.CancelledError):
            _LOG.warning("Runtime cleanup phase failed", exc_info=True)

    async def stop(self):
        if self._stop_task is None:
            self._stopping = True
            self._stop_task = asyncio.create_task(self._stop(), name="hub_runtime_stop")
        await asyncio.shield(self._stop_task)

    async def _stop(self):
        self._unlisten()
        if self._settings_unlisten:
            try:
                self._settings_unlisten()
            except Exception:
                _LOG.warning("Removing settings listener failed", exc_info=True)
            self._settings_unlisten = None
        try:
            await self._cleanup(self.loader.stop)
            await self._cancel(self._operations | {self._start_task, self._connect_task, self._refresh_task})
            if self.server:
                await self._cleanup(self.server.stop)
            await self._cleanup(self.local.close)
            await self._cleanup(self.service.disconnect)
            await self.bus.drain(timeout=CLEANUP_TIMEOUT)
        finally:
            try:
                if self._temporary_metadata:
                    self._temporary_metadata.unlink(missing_ok=True)
            finally:
                if self._process_lock:
                    self._process_lock.release()
                self._started = False

    # UC uses this explicit capability rather than guessing from the result type.
    reconfigure_persists_config_state = True

    @property
    def reconfiguring(self):
        return self._reconfigure_lock.locked()

    def persist_uc_names(self):
        """Persist live names only for the already authorized, saved address.

        Synchronous by design: no transition can interleave between the guard
        and the atomic write. Candidate/rollback notifications may arrive late.
        """
        if self.reconfiguring or self._stopping or self.address is None:
            return
        path = self.prepared.paths.config_dir / "config_state.json"
        if not path.exists():
            return  # An environment bootstrap has not been adopted by setup.
        previous = json.loads(path.read_text(encoding="utf-8"))
        if (previous.get("host"), int(previous.get("port") or 443)) != (self.address.host, self.address.port):
            return  # Transient REST reconfiguration must not become permanent.
        names = self.service.names.snapshot()
        updated = dict(previous)
        updated.update(
            input_names={str(k): v for k, v in names["inputs"].items()},
            output_names={str(k): v for k, v in names["outputs"].items()},
        )
        if updated != previous:
            from _file_io import atomic_write_json

            atomic_write_json(path, updated)

    async def reconfigure(self, address: MatrixAddress, *, persist=False) -> ReconfigureResult:
        async with self._reconfigure_lock:
            if self._stopping:
                raise RuntimeError("Hub runtime is stopping")
            same_address = self.address and (address.host, address.port) == (self.address.host, self.address.port)
            if not same_address:
                # A new target must never inherit bootstrap environment credentials.
                if address.password is None:
                    return ReconfigureResult(False, "auth", self.service.connected)
                address = MatrixAddress(
                    address.host,
                    address.port,
                    address.telnet_port,
                    address.user if address.user is not None else "Admin",
                    address.password,
                )
            return await self._reconfigure(address, persist=persist)

    async def _reconfigure(self, address: MatrixAddress, *, persist=False) -> ReconfigureResult:
        # Cancel only runtime-owned connect/refresh work before waiting for commands.
        await self._cancel({self._connect_task, self._refresh_task})
        try:
            async with self.operation():
                old_address, old_client, old_names = self.address, self.service.client, self.service.names
                if old_address and (address.host, address.port) == (old_address.host, old_address.port):
                    address = MatrixAddress(
                        address.host,
                        address.port,
                        address.telnet_port if address.telnet_port is not None else old_address.telnet_port,
                        address.user or old_address.user,
                        address.password or old_address.password,
                    )
                candidate = None
                try:
                    await asyncio.wait_for(self.service.disconnect(), CLEANUP_TIMEOUT)
                    if getattr(old_client, "connected", False):
                        raise _ReconfigureError("other")
                    self._unlisten()
                    candidate = self._make_client(address)
                    self.address = address
                    same_address = old_address and (address.host, address.port) == (old_address.host, old_address.port)
                    self.service.replace_client(candidate, names=old_names if same_address else None)
                    self._listen()
                    connected = await asyncio.wait_for(self.service.connect(), 30)
                    if not connected:
                        error = getattr(candidate, "login_failure", None)
                        raise _ReconfigureError(
                            error if error in {"auth", "timeout", "not_found", "refused"} else "other"
                        )
                    self._rebind_rest()
                    if persist:
                        from _file_io import atomic_write_json

                        path = self.prepared.paths.config_dir / "config_state.json"
                        previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
                        previous.update(
                            host=address.host,
                            port=address.port,
                            telnet_port=address.telnet_port,
                            input_names={str(k): v for k, v in self.service.names.snapshot()["inputs"].items()},
                            output_names={str(k): v for k, v in self.service.names.snapshot()["outputs"].items()},
                        )
                        # Bootstrap credentials live in the client's environment, not
                        # MatrixAddress. Only explicitly address-bound logins belong on disk.
                        previous.pop("user", None)
                        previous.pop("password", None)
                        if address.user is not None and address.password is not None:
                            previous.update(user=address.user, password=address.password)
                        # Last fallible step: no await or rebinding after the commit.
                        atomic_write_json(path, previous)
                    return ReconfigureResult(True, connected=True)
                except BaseException as exc:

                    async def rollback():
                        if candidate:
                            await candidate.disconnect()
                        self._unlisten()
                        self.address = old_address
                        self.service.replace_client(old_client, names=old_names)
                        self._listen()
                        if old_address and not self._stopping:
                            await self.service.connect()
                        self._rebind_rest()

                    await self._cleanup(rollback)
                    if isinstance(exc, asyncio.CancelledError):
                        raise
                    return ReconfigureResult(
                        False,
                        getattr(exc, "kind", "timeout" if isinstance(exc, TimeoutError) else "other"),
                        self.service.connected,
                    )
        finally:
            if self._started and not self._stopping:
                self._refresh_task = asyncio.create_task(self._refresh_loop(), name="hub_runtime_refresh")

    def _rebind_rest(self):
        from rest_api.utils import bind_runtime, get_runtime

        if get_runtime() is self:
            bind_runtime(self)


class _ReconfigureError(Exception):
    def __init__(self, kind):
        self.kind = kind


def build_runtime(settings, *, environ: Mapping[str, str], matrix_factory=OreiMatrix) -> HubRuntime:
    # No fallback: R2 must be integrated before a production runtime can construct readers.
    from hub.persistence.startup import prepare_runtime_storage
    from persistence import get_data_dir

    config_dir = (settings.uc_config_home or default_config_dir(data_dir=settings.data_dir)).resolve()
    data_dir = (settings.data_dir or get_data_dir()).resolve()
    process_lock = None
    if settings.uc_enabled:
        from _process_lock import ProcessLock

        process_lock = ProcessLock(config_dir / "driver.lock")
        process_lock.acquire()
    effective = dict(environ)
    effective["MATRIX_DATA_DIR"] = str(data_dir)
    effective["UC_CONFIG_HOME"] = str(config_dir)
    effective["API_PORT"] = str(settings.api_port)
    effective["UC_ENABLED"] = "true" if settings.uc_enabled else "false"
    try:
        address = resolve_matrix_address(settings)
        prepared = prepare_runtime_storage(config_dir=config_dir, data_dir=data_dir)
        managers = create_managers(prepared)
        runtime = HubRuntime(
            settings,
            environ=effective,
            prepared=prepared,
            managers=managers,
            address=address,
            matrix_factory=matrix_factory,
        )
        runtime._process_lock = process_lock
        return runtime
    except BaseException:
        if process_lock:
            process_lock.release()
        raise
