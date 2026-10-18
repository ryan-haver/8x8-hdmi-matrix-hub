"""Unfolded Circle `ucapi` WebSocket server, entity store, subscription, and state bridge (R3)."""

from __future__ import annotations

import asyncio
import copy
import inspect
import json
import logging
import os
from collections import deque
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import ucapi
import websockets

from .config import UCIntegrationConfig
from .entities import (
    normalize_snapshot,
    to_ucapi_entity,
)
from .handlers import UCCommandDispatcher
from .mdns import UCMdnsPublisher
from .migration import load_config_state, migrate_legacy_config_state, save_config_state
from .setup import UCSetupHandler
from .state import EntityStateProjector

_LOG = logging.getLogger("uc.bridge")

DEFAULT_DRIVER_JSON_PATH = Path(__file__).resolve().parents[4] / "driver.json"
MAX_DIAGNOSTIC_UPDATES = 100


def _ensure_sensitive_keys() -> None:
    """Register auth token and password keys with ``ucapi`` log sanitizer (`UC-02`, `UC-05`)."""
    try:
        import ucapi.api as _ucapi_api

        sensitive = getattr(_ucapi_api, "_SENSITIVE_KEYS", None)
        if isinstance(sensitive, set):
            sensitive.update({"auth_token", "pin", "current_password", "password"})
    except Exception:
        pass


def _to_ucapi_device_state(state_str: str) -> ucapi.DeviceStates:
    upper = (state_str or "DISCONNECTED").strip().upper()
    if upper == "CONNECTED":
        return ucapi.DeviceStates.CONNECTED
    if upper == "CONNECTING":
        return ucapi.DeviceStates.CONNECTING
    if upper == "ERROR":
        return ucapi.DeviceStates.ERROR
    return ucapi.DeviceStates.DISCONNECTED


class UCBridge:
    """Bridges ``HubClientLocal`` snapshots/events/commands with a live ``ucapi.IntegrationAPI`` server."""

    def __init__(
        self,
        config: UCIntegrationConfig,
        projector: EntityStateProjector,
        mdns: UCMdnsPublisher,
        *,
        api_factory: Callable[[asyncio.AbstractEventLoop], Any] | None = None,
        driver_metadata: str | Path | dict[str, Any] | None = None,
        probe_fn: Callable[[str, int], Any] | None = None,
    ) -> None:
        self.config = config
        self.projector = projector
        self.mdns = mdns
        self._api_factory = api_factory
        self._driver_metadata = driver_metadata
        self._probe_fn = probe_fn

        self.hub_client: Any = None
        self.api: Any = None
        self.dispatcher: UCCommandDispatcher | None = None
        self.setup_handler: UCSetupHandler | None = None
        self.entities: list[dict[str, Any]] = []
        self.migrated_config: dict[str, Any] | None = None
        self.pushed_updates: deque[dict[str, dict[str, Any]]] = deque(maxlen=MAX_DIAGNOSTIC_UPDATES)

        self._reconfigure_hook: Callable[..., Any] | None = None
        self._current_address_hook: Callable[[], Any] | None = None
        self._unsubscribe: Callable[[], Any] | None = None
        self._running: bool = False
        self._last_published_device_state: ucapi.DeviceStates | None = None

        self._ws_server: Any = None
        self._ws_ready_event: asyncio.Event | None = None
        self._ws_stop_event: asyncio.Event | None = None
        self._temp_driver_file: Path | None = None
        self._background_tasks: set[asyncio.Task[Any]] = set()

    @property
    def running(self) -> bool:
        return self._running

    def bind_runtime(
        self,
        *,
        reconfigure: Callable[..., Any] | None = None,
        current_address: Callable[[], Any] | None = None,
        driver_metadata: str | Path | dict[str, Any] | None = None,
    ) -> None:
        """Bind runtime hooks for matrix address inspection and live reconfiguration."""
        if reconfigure is not None:
            self._reconfigure_hook = reconfigure
        if current_address is not None:
            self._current_address_hook = current_address
        if driver_metadata is not None:
            self._driver_metadata = driver_metadata

    def _schedule_task(self, coro: Any) -> asyncio.Task[Any] | None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return None
        task = loop.create_task(coro)
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        return task

    def _effective_auth_token(self) -> str | None:
        if self.config.auth_token:
            return self.config.auth_token
        env_tok = os.environ.get("UC_AUTH_TOKEN", "").strip() or os.environ.get("ADMIN_PIN", "").strip()
        return env_tok or None

    def _effective_driver_url(self) -> str | None:
        if self.config.driver_url:
            return self.config.driver_url
        env_url = os.environ.get("UC_DRIVER_URL", "").strip()
        return env_url or None

    def _is_configured_at_start(self) -> bool:
        if self.migrated_config and str(self.migrated_config.get("host") or "").strip():
            return True
        if self._current_address_hook is not None:
            addr = self._current_address_hook()
            if addr is not None:
                if isinstance(addr, Mapping):
                    host = str(addr.get("host") or "").strip()
                    explicit_cfg = addr.get("configured")
                    return bool(host) if explicit_cfg is None else (bool(explicit_cfg) and bool(host))
                host = str(getattr(addr, "host", "") or "").strip()
                explicit_cfg = getattr(addr, "configured", None)
                return bool(host) if explicit_cfg is None else (bool(explicit_cfg) and bool(host))
            return False
        if os.environ.get("MATRIX_HOST", "").strip():
            return True
        if self.hub_client is not None and hasattr(self.hub_client, "configured"):
            return bool(self.hub_client.configured)
        return self.hub_client is not None

    def _prepare_driver_metadata_path(self) -> str:
        if isinstance(self._driver_metadata, dict):
            self.config.config_home.mkdir(parents=True, exist_ok=True)
            tmp_path = self.config.config_home / ".uc_driver_metadata.json"
            tmp_path.write_text(json.dumps(self._driver_metadata, indent=2), encoding="utf-8")
            self._temp_driver_file = tmp_path
            return str(tmp_path)
        if isinstance(self._driver_metadata, (str, Path)):
            return str(Path(self._driver_metadata).resolve())
        return str(DEFAULT_DRIVER_JSON_PATH)

    def _adjust_driver_metadata(self, driver_info: dict[str, Any] | None) -> None:
        if not isinstance(driver_info, dict):
            return
        driver_url = self._effective_driver_url()
        if driver_url:
            driver_info["driver_url"] = driver_url
        else:
            driver_info.pop("driver_url", None)

        schema = driver_info.get("setup_data_schema")
        settings = schema.get("settings") if isinstance(schema, dict) else None
        token = self._effective_auth_token()

        if token:
            driver_info["pwd"] = True
            if isinstance(settings, list):
                settings[:] = [s for s in settings if isinstance(s, dict) and s.get("id") != "current_password"]
                if not any(isinstance(s, dict) and s.get("id") == "auth_token" for s in settings):
                    settings.append(
                        {
                            "id": "auth_token",
                            "label": {"en": "Setup Token / PIN"},
                            "field": {"password": {}},
                        }
                    )
        else:
            driver_info.pop("pwd", None)
            if isinstance(settings, list):
                settings[:] = [s for s in settings if isinstance(s, dict) and s.get("id") != "auth_token"]

    def _install_controlled_ws_server(self, api: ucapi.IntegrationAPI) -> None:
        ready_event = asyncio.Event()
        stop_event = asyncio.Event()
        self._ws_ready_event = ready_event
        self._ws_stop_event = stop_event
        bind_host = self.config.interface if self.config.interface else "0.0.0.0"
        bind_port = self.config.port

        async def _controlled_start_ws_server(
            host: str,
            port: int,
            ssl_context: Any = None,
        ) -> None:
            effective_host = bind_host or host or "0.0.0.0"
            effective_port = bind_port or port
            _LOG.info("Starting UC WebSocket server on %s:%d", effective_host, effective_port)
            async with websockets.serve(
                api._handle_ws,
                effective_host,
                effective_port,
                ssl=ssl_context,
                reuse_address=True,
            ) as ws_server:
                self._ws_server = ws_server
                ready_event.set()
                await stop_event.wait()

        api._start_web_socket_server = _controlled_start_ws_server  # type: ignore[method-assign]

    def _register_api_listeners(self, api: Any) -> None:
        if not hasattr(api, "add_listener"):
            return
        api.add_listener(ucapi.Events.CONNECT, self._on_connect)
        api.add_listener(ucapi.Events.DISCONNECT, self._on_disconnect)
        api.add_listener(ucapi.Events.CLIENT_CONNECTED, self._on_client_connected)
        api.add_listener(ucapi.Events.CLIENT_DISCONNECTED, self._on_client_disconnected)
        api.add_listener(ucapi.Events.ENTER_STANDBY, self.on_enter_standby)
        api.add_listener(ucapi.Events.EXIT_STANDBY, self.on_exit_standby)
        api.add_listener(ucapi.Events.SUBSCRIBE_ENTITIES, self._on_subscribe_entities)
        api.add_listener(ucapi.Events.UNSUBSCRIBE_ENTITIES, self._on_unsubscribe_entities)

    async def _init_api(self, api: Any, driver_path: str) -> None:
        is_real_ucapi = isinstance(api, ucapi.IntegrationAPI)
        if is_real_ucapi:
            self._install_controlled_ws_server(api)

        prev_disable = os.environ.get("UC_DISABLE_MDNS_PUBLISH")
        prev_port = os.environ.get("UC_INTEGRATION_HTTP_PORT")
        prev_iface = os.environ.get("UC_INTEGRATION_INTERFACE")
        try:
            os.environ["UC_DISABLE_MDNS_PUBLISH"] = "true"
            os.environ["UC_INTEGRATION_HTTP_PORT"] = str(self.config.port)
            if self.config.interface:
                os.environ["UC_INTEGRATION_INTERFACE"] = self.config.interface
            res = api.init(driver_path, self.setup_handler)
            if inspect.isawaitable(res):
                await res
        finally:
            if prev_disable is None:
                os.environ.pop("UC_DISABLE_MDNS_PUBLISH", None)
            else:
                os.environ["UC_DISABLE_MDNS_PUBLISH"] = prev_disable
            if prev_port is None:
                os.environ.pop("UC_INTEGRATION_HTTP_PORT", None)
            else:
                os.environ["UC_INTEGRATION_HTTP_PORT"] = prev_port
            if prev_iface is None:
                os.environ.pop("UC_INTEGRATION_INTERFACE", None)
            else:
                os.environ["UC_INTEGRATION_INTERFACE"] = prev_iface

        driver_info = getattr(api, "_driver_info", None)
        if isinstance(driver_info, dict):
            # Work on a fresh copy so nothing shares mutable nested lists unexpectedly
            api._driver_info = copy.deepcopy(driver_info)
            self._adjust_driver_metadata(api._driver_info)

        if is_real_ucapi and self._ws_ready_event is not None:
            server_task = getattr(api, "_server_task", None)
            ready_waiter = asyncio.create_task(self._ws_ready_event.wait())
            try:
                wait_set = {ready_waiter}
                if isinstance(server_task, asyncio.Task):
                    wait_set.add(server_task)
                done, _ = await asyncio.wait(wait_set, timeout=10.0, return_when=asyncio.FIRST_COMPLETED)
                if not done:
                    raise TimeoutError(f"Timed out waiting for UC WebSocket server on port {self.config.port}")
                if isinstance(server_task, asyncio.Task) and server_task in done:
                    exc = server_task.exception()
                    if exc is not None:
                        raise exc
                await self._ws_ready_event.wait()
            finally:
                if not ready_waiter.done():
                    ready_waiter.cancel()

    def _sync_entities_from_projector(self, snapshot: Mapping[str, Any] | None = None) -> None:
        """Install or refresh entities in ``api.available_entities`` and replace subscribed entities in place."""
        descriptors = self.projector._build_descriptor_list(snapshot)
        self.entities = descriptors

        for desc in descriptors:
            eid = desc["entity_id"]
            self.projector.entity_names[eid] = dict(desc["name"])
            if eid not in self.projector.truth:
                self.projector.truth[eid] = dict(desc["attributes"])
            proj_attrs = self.projector.projected_attributes(eid)
            avail_copy = dict(desc)
            avail_copy["attributes"] = dict(proj_attrs)
            self.projector.available_entities[eid] = avail_copy
            if eid in self.projector.configured_entities:
                cfg_copy = dict(desc)
                cfg_copy["attributes"] = dict(proj_attrs)
                self.projector.configured_entities[eid] = cfg_copy

        if self.api is None:
            return

        avail_store = getattr(self.api, "available_entities", None)
        cfg_store = getattr(self.api, "configured_entities", None)
        cmd_handler = self.dispatcher.as_ucapi_handler() if self.dispatcher is not None else None

        subscribed_ids: set[str] = set(self.projector.configured_entities.keys())
        if cfg_store is not None:
            for desc in descriptors:
                eid = desc["entity_id"]
                if hasattr(cfg_store, "contains") and cfg_store.contains(eid):
                    subscribed_ids.add(eid)
                elif hasattr(cfg_store, "get") and cfg_store.get(eid) is not None:
                    subscribed_ids.add(eid)

        if avail_store is not None and hasattr(avail_store, "clear"):
            avail_store.clear()

        for desc in descriptors:
            eid = desc["entity_id"]
            desc_with_proj = dict(desc)
            desc_with_proj["attributes"] = self.projector.projected_attributes(eid)
            uc_ent = to_ucapi_entity(desc_with_proj, cmd_handler=cmd_handler)

            if avail_store is not None and hasattr(avail_store, "add"):
                avail_store.add(uc_ent)

            if eid in subscribed_ids and cfg_store is not None:
                # Replace in place without clearing configured_entities or dropping subscriptions
                uc_cfg_ent = to_ucapi_entity(desc_with_proj, cmd_handler=cmd_handler)
                if hasattr(cfg_store, "remove"):
                    cfg_store.remove(eid)
                if hasattr(cfg_store, "add"):
                    cfg_store.add(uc_cfg_ent)

    def _deliver_diff(self, diff: dict[str, dict[str, Any]]) -> None:
        if not diff:
            return
        self.pushed_updates.append(diff)
        if self.projector.standby or self.api is None:
            return

        avail_store = getattr(self.api, "available_entities", None)
        cfg_store = getattr(self.api, "configured_entities", None)

        for eid, attrs in diff.items():
            if avail_store is not None and hasattr(avail_store, "get"):
                avail_ent = avail_store.get(eid)
                if avail_ent is not None and hasattr(avail_ent, "attributes"):
                    avail_ent.attributes.update(attrs)

            if cfg_store is not None:
                has_ent = (
                    cfg_store.contains(eid)
                    if hasattr(cfg_store, "contains")
                    else (cfg_store.get(eid) is not None if hasattr(cfg_store, "get") else False)
                )
                if has_ent and hasattr(cfg_store, "update_attributes"):
                    cfg_store.update_attributes(eid, dict(attrs))

    async def _publish_device_state(self, *, force: bool = False) -> None:
        if self.api is None or not hasattr(self.api, "set_device_state"):
            return
        if self.projector.standby and not force:
            return
        target = _to_ucapi_device_state(self.projector.device_state)
        if not force and self._last_published_device_state == target:
            return
        self._last_published_device_state = target
        res = self.api.set_device_state(target)
        if inspect.isawaitable(res):
            await res

    async def _fetch_snapshot(self) -> dict[str, Any]:
        if self.hub_client is None or not hasattr(self.hub_client, "snapshot"):
            return {}
        res = self.hub_client.snapshot()
        raw = await res if inspect.isawaitable(res) else res
        snap = normalize_snapshot(raw)
        if self.migrated_config:
            if not snap.get("input_names") and self.migrated_config.get("input_names"):
                snap["input_names"] = dict(self.migrated_config["input_names"])
            if not snap.get("output_names") and self.migrated_config.get("output_names"):
                snap["output_names"] = dict(self.migrated_config["output_names"])
        return snap

    async def start(self, hub_client: Any) -> None:
        """Start the UC integration server, project initial state if configured, subscribe, and publish mDNS."""
        _ensure_sensitive_keys()
        self.migrated_config = migrate_legacy_config_state(self.config.config_home)
        self.hub_client = hub_client
        self.dispatcher = UCCommandDispatcher(
            hub_client,
            self.projector,
            on_state_diff=self._deliver_diff,
        )
        self.setup_handler = UCSetupHandler(
            self.config,
            hub_getter=lambda: self.hub_client,
            reconfigure_getter=lambda: self._reconfigure_hook,
            current_address_getter=lambda: self._current_address_hook,
            saved_config_getter=lambda: self.migrated_config or load_config_state(self.config.config_home),
            on_setup_complete=self._on_setup_complete,
            probe_fn=self._probe_fn,
        )

        loop = asyncio.get_running_loop()
        self.api = self._api_factory(loop) if self._api_factory is not None else ucapi.IntegrationAPI(loop)
        self._register_api_listeners(self.api)

        try:
            configured = self._is_configured_at_start()
            if configured:
                snapshot = await self._fetch_snapshot()
                self.dispatcher.update_pin_blocks(snapshot)
                initial_diff = self.projector.project_snapshot(snapshot, force=True)
                self._sync_entities_from_projector(snapshot)
                if initial_diff:
                    self.pushed_updates.append(initial_diff)
            else:
                self.entities = []
                self.projector.available_entities.clear()
                self.projector.configured_entities.clear()

            driver_path = self._prepare_driver_metadata_path()
            await self._init_api(self.api, driver_path)

            if hasattr(hub_client, "subscribe"):
                sub_res = hub_client.subscribe(self._on_hub_event)
                if inspect.isawaitable(sub_res):
                    sub_res = await sub_res
                if callable(sub_res):
                    self._unsubscribe = sub_res

            if configured:
                await self._publish_device_state(force=True)

            await self.mdns.start()
            self._running = True
            _LOG.info("UCBridge started on port %d (%d available entities)", self.config.port, len(self.entities))
        except Exception:
            await self._rollback_start()
            raise

    async def _rollback_start(self) -> None:
        self._running = False
        await self.stop()

    async def stop(self) -> None:
        """Stop the UC integration server, unsubscribe from hub events, and unregister mDNS (`UC-11`)."""
        unsub, self._unsubscribe = self._unsubscribe, None
        if unsub is not None:
            try:
                res = unsub()
                if inspect.isawaitable(res):
                    await res
            except Exception:
                _LOG.debug("Error unsubscribing from hub events", exc_info=True)

        await self.mdns.stop()

        for task in list(self._background_tasks):
            task.cancel()
        if self._background_tasks:
            await asyncio.gather(*self._background_tasks, return_exceptions=True)
        self._background_tasks.clear()

        if self._ws_stop_event is not None:
            self._ws_stop_event.set()

        if self._ws_server is not None:
            try:
                self._ws_server.close()
                await asyncio.wait_for(self._ws_server.wait_closed(), timeout=3.0)
            except Exception:
                _LOG.debug("Error closing UC WebSocket server", exc_info=True)
            finally:
                self._ws_server = None

        if self.api is not None:
            server_task = getattr(self.api, "_server_task", None)
            if isinstance(server_task, asyncio.Task) and not server_task.done():
                server_task.cancel()
                try:
                    await asyncio.wait_for(server_task, timeout=2.0)
                except (asyncio.CancelledError, Exception):
                    pass

        if self._temp_driver_file is not None:
            try:
                self._temp_driver_file.unlink(missing_ok=True)
            except OSError:
                pass
            self._temp_driver_file = None

        self._ws_ready_event = None
        self._ws_stop_event = None
        self._last_published_device_state = None
        self._running = False
        _LOG.info("UCBridge stopped")

    async def _on_setup_complete(self, address: Any, save_credentials: bool) -> None:
        snapshot = await self._fetch_snapshot()
        if self.dispatcher is not None:
            self.dispatcher.update_pin_blocks(snapshot)

        # Force connected if reconfigure just succeeded
        if "connected" not in snapshot:
            snapshot["connected"] = True
        diff = self.projector.project_snapshot(snapshot, force=True)
        self._sync_entities_from_projector(snapshot)
        self._deliver_diff(diff)

        host = str(getattr(address, "host", "") or "")
        port = int(getattr(address, "port", 443))
        telnet_port = getattr(address, "telnet_port", None)
        user = getattr(address, "user", None)
        password = getattr(address, "password", None)
        creds = (str(user), str(password)) if (save_credentials and user and password) else None
        save_config_state(
            self.config.config_home,
            host=host,
            port=port,
            telnet_port=int(telnet_port) if telnet_port is not None else None,
            input_names=dict(self.projector.input_names),
            output_names=dict(self.projector.output_names),
            credentials=creds,
        )
        self.migrated_config = load_config_state(self.config.config_home)
        await self._publish_device_state(force=True)

    async def _on_connect(self, *_: Any, **__: Any) -> None:
        if self.projector.standby:
            await self.on_exit_standby()
        elif self.hub_client is not None and self._is_configured_at_start():
            snapshot = await self._fetch_snapshot()
            if snapshot:
                if self.dispatcher is not None:
                    self.dispatcher.update_pin_blocks(snapshot)
                diff = self.projector.project_snapshot(snapshot)
                self._sync_entities_from_projector(snapshot)
                if diff:
                    self._deliver_diff(diff)
            resynced = self.projector.resync(list(self.projector.configured_entities.keys()))
            if resynced:
                self._deliver_diff(resynced)
        await self._publish_device_state(force=True)

    async def _on_disconnect(self, *_: Any, **__: Any) -> None:
        """Handle Remote `disconnect` event without stopping the hub's matrix connection (`UC-17`)."""
        _LOG.info("Remote sent disconnect event; keeping hub matrix connection active")

    async def _on_client_connected(self, *_: Any, **__: Any) -> None:
        _LOG.debug("Remote WebSocket client connected")

    async def _on_client_disconnected(self, *_: Any, **__: Any) -> None:
        """Handle Remote WebSocket disconnect without stopping the hub's matrix connection (`UC-17`)."""
        _LOG.debug("Remote WebSocket client disconnected")

    async def on_enter_standby(self, *_: Any, **__: Any) -> None:
        """Pause entity/device pushes while the Remote sleeps without disconnecting the matrix (`UC-06`, `UC-17`)."""
        self.projector.enter_standby()

    async def on_exit_standby(self, *_: Any, **__: Any) -> dict[str, dict[str, Any]]:
        """Resume pushes on wake and resync state from the hub (`UC-06`, `UC-17`)."""
        flushed = self.projector.exit_standby()
        if self.hub_client is not None and self._is_configured_at_start():
            snapshot = await self._fetch_snapshot()
            if snapshot:
                if self.dispatcher is not None:
                    self.dispatcher.update_pin_blocks(snapshot)
                extra = self.projector.project_snapshot(snapshot)
                self._sync_entities_from_projector(snapshot)
                for eid, attrs in extra.items():
                    flushed.setdefault(eid, {}).update(attrs)
        if flushed:
            self._deliver_diff(flushed)
        await self._publish_device_state()
        return flushed

    async def _on_subscribe_entities(self, entity_ids: list[str] | None = None, *_: Any, **__: Any) -> None:
        ids = [str(eid) for eid in (entity_ids or []) if eid]
        if not ids:
            return
        if self.api is not None:
            avail_store = getattr(self.api, "available_entities", None)
            cfg_store = getattr(self.api, "configured_entities", None)
            if avail_store is not None and cfg_store is not None:
                for eid in ids:
                    ent = avail_store.get(eid) if hasattr(avail_store, "get") else None
                    if ent is not None and hasattr(cfg_store, "add"):
                        has_ent = (
                            cfg_store.contains(eid)
                            if hasattr(cfg_store, "contains")
                            else (cfg_store.get(eid) is not None if hasattr(cfg_store, "get") else False)
                        )
                        if not has_ent:
                            cfg_store.add(ent)

        resynced = self.projector.subscribe_entities(ids)
        if resynced and not self.projector.standby:
            self._deliver_diff(resynced)

    async def _on_unsubscribe_entities(self, entity_ids: list[str] | None = None, *_: Any, **__: Any) -> None:
        ids = [str(eid) for eid in (entity_ids or []) if eid]
        if not ids:
            return
        self.projector.unsubscribe_entities(ids)
        if self.api is not None:
            cfg_store = getattr(self.api, "configured_entities", None)
            if cfg_store is not None and hasattr(cfg_store, "remove"):
                for eid in ids:
                    cfg_store.remove(eid)

    async def _refresh_after_reconnect(self) -> None:
        snapshot = await self._fetch_snapshot()
        if snapshot:
            if self.dispatcher is not None:
                self.dispatcher.update_pin_blocks(snapshot)
            diff = self.projector.project_snapshot(snapshot)
            self._sync_entities_from_projector(snapshot)
            if diff:
                self._deliver_diff(diff)
        await self._publish_device_state()

    def _persist_renamed_ports(self) -> None:
        saved = self.migrated_config or load_config_state(self.config.config_home)
        if not saved or not saved.get("host"):
            return
        creds: tuple[str, str] | None = None
        if saved.get("user") and saved.get("password"):
            creds = (str(saved["user"]), str(saved["password"]))
        self.migrated_config = save_config_state(
            self.config.config_home,
            host=str(saved["host"]),
            port=int(saved.get("port", 443)),
            telnet_port=saved.get("telnet_port"),
            input_names=dict(self.projector.input_names),
            output_names=dict(self.projector.output_names),
            credentials=creds,
        )

    def _on_hub_event(
        self,
        event: Any,
        data: dict[str, Any] | None = None,
    ) -> dict[str, dict[str, Any]]:
        if isinstance(event, str):
            kind = event.strip().lower()
            payload = data if isinstance(data, Mapping) else {}
        elif isinstance(event, Mapping):
            kind = str(event.get("kind") or event.get("event") or event.get("type") or "").strip().lower()
            raw_data = event.get("data")
            payload = raw_data if isinstance(raw_data, Mapping) else event
        else:
            kind = str(getattr(event, "kind", "") or getattr(event, "event", "") or "").strip().lower()
            raw_data = getattr(event, "data", None)
            payload = raw_data if isinstance(raw_data, Mapping) else {}

        was_connected = self.projector.connected
        prev_device_state = self.projector.device_state

        if kind in ("catalog", "profiles", "scenes") and self.dispatcher is not None:
            self.dispatcher.update_pin_blocks({kind: payload.get(kind, payload)} if kind != "catalog" else payload)

        diff = self.projector.apply_event(event, data)

        if kind in (
            "names",
            "presets",
            "favorite_presets",
            "favourites",
            "catalog",
            "profiles",
            "scenes",
            "shortcuts",
            "macros",
        ):
            self._sync_entities_from_projector()
            if kind == "names":
                self._persist_renamed_ports()

        if diff:
            self._deliver_diff(diff)

        if self.projector.device_state != prev_device_state or self.projector.connected != was_connected:
            self._schedule_task(self._publish_device_state())
            if not was_connected and self.projector.connected:
                self._schedule_task(self._refresh_after_reconnect())

        return diff
