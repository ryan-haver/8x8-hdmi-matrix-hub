"""R5B safety regressions using real imports, R2 stores and owned resources."""

from __future__ import annotations

import asyncio
import itertools
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
from aiohttp import web

from hub.integrations.base import IntegrationLoader, IntegrationRegistry
from hub.integrations.flic import FlicButtonRegistry
from hub.integrations.homeassistant import HomeAssistantDiscoveryConfig, HomeAssistantDiscoveryIntegration
from hub.persistence import CURRENT_SCHEMA_VERSION, flat_map_records, reset_preparation
from hub.runtime.integrations import bind_integrations, build_integration_loader
from rest_api.app import create_rest_app

ADDRESS = "aa:bb:cc:dd:ee:01"
OTHER = "aa:bb:cc:dd:ee:02"
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def reset_r2_blocks():
    yield
    reset_preparation()


def run_fresh(tmp_path, flags):
    """No sys.modules replacement: execute the real production import graph."""
    environ = {k: v for k, v in os.environ.items() if k not in {
        "UC_ENABLED", "FLIC_ENABLED", "HA_DISCOVERY_ENABLED", "UC_CONFIG_HOME", "DATA_DIR",
    }}
    environ.update(flags)
    environ["MATRIX_DATA_DIR"] = str(tmp_path)
    environ["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT)))
    script = '''
import asyncio, json, os, sys
from pathlib import Path
from hub.cli import load_settings
from hub.runtime.adapters import NullMatrix
from hub.runtime.composition import build_runtime
from hub.runtime.integrations import bind_integrations
from rest_api.app import create_rest_app
names = {"unfolded_circle": "hub.integrations.unfolded_circle", "flic": "hub.integrations.flic", "homeassistant": "hub.integrations.homeassistant"}
before = {k: v in sys.modules for k,v in names.items()}
async def main():
    # Only the transport is inert. R2 preparation, managers, runtime, binder,
    # loader and both app factories are the actual production implementation.
    runtime = build_runtime(load_settings(os.environ), environ=os.environ, matrix_factory=lambda *a, **kw: NullMatrix())
    try:
        loader = runtime.loader
        loader.load()
        bind_integrations(loader, runtime)
        uc = loader.integrations.get("unfolded_circle")
        if uc is not None:
            assert uc.bridge._reconfigure_hook.__self__ is runtime
            assert uc.bridge._persistence_runtime() is runtime
        app = create_rest_app(runtime=runtime)
        direct = create_rest_app(Path(os.environ["MATRIX_DATA_DIR"]) / "direct")
        print(json.dumps({"before": before, "loaded": sorted(loader.integrations), "imports": {k: v in sys.modules for k,v in names.items()}, "paths": sorted({r.resource.canonical for r in app.router.routes()}), "direct": sorted({r.resource.canonical for r in direct.router.routes()}), "origins": {"hub": sys.modules["hub"].__file__, "rest": sys.modules["rest_api.app"].__file__}, "optional": {k: k in sys.modules for k in ("ucapi", "zeroconf")}}))
    finally:
        await runtime.stop()
asyncio.run(main())
'''
    result = subprocess.run([sys.executable, "-c", script], cwd=tmp_path, env=environ,
                            capture_output=True, text=True, timeout=30, check=True)
    return json.loads(result.stdout.strip().splitlines()[-1])


@pytest.mark.parametrize("uc,flic,ha", list(itertools.product((False, True), repeat=3)))
def test_actual_fresh_imports_all_flags(tmp_path, uc, flic, ha):
    flags = {"UC_ENABLED": str(uc), "FLIC_ENABLED": str(flic), "HA_DISCOVERY_ENABLED": str(ha)}
    result = run_fresh(tmp_path, flags)
    expected = {k for k, v in zip(("unfolded_circle", "flic", "homeassistant"), (uc, flic, ha), strict=True) if v}
    assert not any(result["before"].values())
    assert set(result["loaded"]) == expected
    assert {k for k, v in result["imports"].items() if v} == expected
    assert ("/api/integrations/flic/buttons" in result["paths"]) is flic
    assert ("/api/integrations/flic/buttons" in result["direct"]) is flic
    assert "/api/switch" in result["paths"]
    assert Path(result["origins"]["hub"]).is_relative_to(ROOT)
    assert Path(result["origins"]["rest"]).is_relative_to(ROOT)
    if not uc:
        assert not result["optional"]["ucapi"]
        assert not result["optional"]["zeroconf"]  # HA imports the dependency only on start.


@pytest.mark.parametrize("value,enabled", [(None, True), ("", True), ("  ", True), ("0", False),
    ("false", False), (" FALSE ", False), ("no", False), (" off ", False), ("maybe", True)])
def test_fresh_default_and_false_spellings(tmp_path, value, enabled):
    flags = {} if value is None else dict.fromkeys(("UC_ENABLED", "FLIC_ENABLED", "HA_DISCOVERY_ENABLED"), value)
    result = run_fresh(tmp_path, flags)
    assert result["loaded"] == (["flic"] if enabled else [])
    assert result["imports"]["flic"] is enabled
    assert ("/api/integrations/flic/register" in result["direct"]) is enabled


def test_metadata_only_is_not_a_button_and_real_r2_roundtrip(tmp_path):
    path = tmp_path / "flic_buttons.json"
    extension = {"bdaddr": "metadata-only", "password": "synthetic-private"}
    payload = {"schema_version": CURRENT_SCHEMA_VERSION, "extension_object": extension}
    path.write_text(json.dumps(payload))
    assert flat_map_records(path.name, payload) == {}
    registry = FlicButtonRegistry(file_path=path)
    assert len(registry) == 0
    assert registry.list_buttons() == []
    registry.register_buttons([{"bdaddr": ADDRESS, "name": "Den"}])
    raw = json.loads(path.read_text())
    raw[ADDRESS]["opaque"] = {"password": "synthetic-record-private"}
    raw["late_metadata"] = {"serial": "private-metadata"}
    path.write_text(json.dumps(raw))
    registry.register_buttons([{"bdaddr": ADDRESS, "name": "Updated"}])
    reloaded = FlicButtonRegistry(file_path=path)
    assert reloaded.list_buttons() == [{"bdaddr": ADDRESS, "name": "Updated", "serial": ""}]
    raw = json.loads(path.read_text())
    assert raw["extension_object"] == extension
    assert raw["late_metadata"] == {"serial": "private-metadata"}
    assert raw[ADDRESS]["opaque"]["password"] == "synthetic-record-private"
    assert "private" not in json.dumps(reloaded.list_buttons())


@pytest.mark.parametrize("bad", [None, {}, [], 1, "metadata-only", "aa:bb", "aa:bb:cc:dd:ee:gg"])
def test_invalid_registration_does_not_create_records(tmp_path, bad):
    registry = FlicButtonRegistry(data_dir=tmp_path)
    assert registry.register_buttons([{"bdaddr": bad, "password": "synthetic-private"}]) == 0
    assert not registry.file_path.exists()
    assert registry.list_buttons() == []


def test_public_fields_cannot_project_objects(tmp_path):
    path = tmp_path / "flic_buttons.json"
    path.write_text(json.dumps({"schema_version": CURRENT_SCHEMA_VERSION,
                               ADDRESS: {"name": {"password": "private"}, "serial": {"token": "private"}}}))
    assert FlicButtonRegistry(file_path=path).list_buttons() == [{"bdaddr": ADDRESS, "name": ADDRESS, "serial": ""}]


@pytest.mark.parametrize("writer", ["register", "save", "raw_keyword", "compatibility"])
@pytest.mark.parametrize("late", [b'{"schema_version":999,"private":"future"}', b'{bad',
    ('{"schema_version":2,"' + ADDRESS + '":42}').encode()])
def test_every_writer_refuses_late_bad_files_original_bytes(tmp_path, monkeypatch, writer, late):
    from rest_api import integrations

    registry = FlicButtonRegistry(data_dir=tmp_path)
    registry.register_buttons([{"bdaddr": ADDRESS, "name": "Original"}])
    registry.file_path.write_bytes(late)
    if writer == "register":
        with pytest.raises(RuntimeError, match="Failed to save"):
            registry.register_buttons([{"bdaddr": OTHER, "name": "Rejected"}])
        assert registry.list_buttons() == [{"bdaddr": ADDRESS, "name": "Original", "serial": ""}]
    elif writer == "compatibility":
        monkeypatch.setattr(integrations, "_default_registry", registry)
        monkeypatch.setattr(integrations, "_registered_buttons", registry._buttons)
        assert not integrations._save_buttons()
    else:
        assert not registry.save(versioned=writer != "raw_keyword")
    assert registry.file_path.read_bytes() == late


@pytest.mark.parametrize("writer", ["save", "raw_keyword", "compatibility"])
def test_every_writer_preserves_r2_extensions(tmp_path, monkeypatch, writer):
    from rest_api import integrations

    path = tmp_path / "flic_buttons.json"
    path.write_text(json.dumps({"schema_version": CURRENT_SCHEMA_VERSION, "private": {"password": "secret"},
        ADDRESS: {"bdaddr": ADDRESS, "name": "Old", "opaque": {"token": "secret"}}}))
    registry = FlicButtonRegistry(file_path=path)
    registry._buttons = {ADDRESS: {"bdaddr": ADDRESS, "name": "New"}}
    if writer == "compatibility":
        monkeypatch.setattr(integrations, "_default_registry", registry)
        monkeypatch.setattr(integrations, "_registered_buttons", registry._buttons)
        assert integrations._save_buttons()
    else:
        assert registry.save(versioned=writer != "raw_keyword")
    raw = json.loads(path.read_text())
    assert raw["schema_version"] == CURRENT_SCHEMA_VERSION
    assert raw["private"] == {"password": "secret"}
    assert raw[ADDRESS]["opaque"] == {"token": "secret"}
    assert FlicButtonRegistry(file_path=path).list_buttons()[0]["name"] == "New"


def test_real_r2_atomic_write_failure_rolls_back_registration(tmp_path, monkeypatch):
    registry = FlicButtonRegistry(data_dir=tmp_path)
    registry.register_buttons([{"bdaddr": ADDRESS, "name": "Original"}])
    before = registry.file_path.read_bytes()
    writes = []

    def refuse(path, payload, **kwargs):
        writes.append(path)
        raise OSError("synthetic replacement failure")

    monkeypatch.setattr("hub.persistence.migrations.atomic_write_json", refuse)
    with pytest.raises(RuntimeError, match="Failed to save"):
        registry.register_buttons([{"bdaddr": ADDRESS, "name": "Rejected"}, {"bdaddr": OTHER}])
    assert writes == [registry.file_path]
    assert registry.file_path.read_bytes() == before
    assert registry.list_buttons() == [{"bdaddr": ADDRESS, "name": "Original", "serial": ""}]


async def test_apps_and_compatibility_routes_do_not_share_stale_registry(tmp_path, aiohttp_client):
    from rest_api import integrations

    first = create_rest_app(tmp_path / "first")
    second = create_rest_app(tmp_path / "second")
    assert first["flic_integration"].registry is not second["flic_integration"].registry
    # Explicit app context also applies to the old module handler names.
    first.router.add_get("/compat", integrations.handle_get_flic_buttons)
    first_client = await aiohttp_client(first)
    second_client = await aiohttp_client(second)
    response = await first_client.post("/api/integrations/flic/register", json={"buttons": [{"bdaddr": ADDRESS}]})
    assert (await response.json())["data"]["count"] == 1
    assert (await (await first_client.get("/compat")).json())["data"]["buttons"][0]["bdaddr"] == ADDRESS
    assert (await (await second_client.get("/api/integrations/flic/buttons")).json())["data"]["buttons"] == []


async def test_runtime_compatibility_handler_uses_active_registry(tmp_path, aiohttp_client, monkeypatch):
    from rest_api import integrations

    loader = build_integration_loader({"FLIC_ENABLED": "true", "MATRIX_DATA_DIR": str(tmp_path)})
    loader.load()
    runtime = SimpleNamespace(loader=loader)
    bind_integrations(loader, runtime)
    integration = loader.integrations["flic"]
    app = web.Application()
    app["hub_runtime"] = runtime
    for method, path, handler in integration.routes():
        app.router.add_route(method, path, handler)
    app.router.add_get("/compat", integrations.handle_get_flic_buttons)
    monkeypatch.setattr(integrations, "_registered_buttons", {})
    monkeypatch.setattr(integrations, "_loaded", False)
    integration.registry.register_buttons([{"bdaddr": ADDRESS}])
    client = await aiohttp_client(app)
    assert (await (await client.get("/compat")).json())["data"]["buttons"][0]["bdaddr"] == ADDRESS
    assert integrations._default_registry is integration.registry


async def test_factory_flic_security_and_status_contract(tmp_path, aiohttp_client, monkeypatch):
    monkeypatch.setenv("ADMIN_PIN", "8642")
    monkeypatch.setenv("CONTROL_API_KEY", "synthetic-control-key")
    app = create_rest_app(tmp_path)
    client = await aiohttp_client(app)
    endpoint = "/api/integrations/flic/register"
    body = {"buttons": [{"bdaddr": ADDRESS, "name": "Den", "serial": "S1"}]}
    assert (await client.post(endpoint, json=body)).status == 401
    assert (await client.post(endpoint, json=body, headers={"X-API-Key": "synthetic-control-key"})).status == 401
    assert (await client.post(endpoint, json=body, headers={"X-Admin-PIN": "0000"})).status == 401
    admin = {"X-Admin-PIN": "8642"}
    assert (await client.post(endpoint, json=body, headers={**admin, "Origin": "https://example.invalid"})).status == 403
    assert (await client.post(endpoint, data='{}', headers=admin)).status == 415
    response = await client.post(endpoint, data='{"buttons":', headers={**admin, "Content-Type": "application/json"})
    assert response.status == 400
    assert (await response.json())["success"] is False
    assert (await client.post(endpoint, json={"buttons": {}}, headers=admin)).status == 400
    response = await client.post(endpoint, json=body, headers=admin)
    result = await response.json()
    assert response.status == 200
    assert result["success"] is True
    assert result["data"] == {"count": 1}
    response = await client.get("/api/integrations/flic/buttons")
    assert response.status == 200
    assert (await response.json())["data"] == {"buttons": body["buttons"]}
    assert (await client.head("/api/integrations/flic/buttons")).status == 200


def test_binder_does_not_hide_import_failure(tmp_path, monkeypatch):
    import builtins

    loader = build_integration_loader({"FLIC_ENABLED": "true", "MATRIX_DATA_DIR": str(tmp_path)})
    loader.load()
    real_import = builtins.__import__

    def blocked_import(name, *args, **kwargs):
        if name == "rest_api.integrations":
            raise ImportError("synthetic binding failure")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", blocked_import)
    with pytest.raises(ImportError, match="synthetic binding failure"):
        bind_integrations(loader, SimpleNamespace(loader=loader))


class ResourceIntegration:
    """An actual owned background task and loopback TCP listener."""

    def __init__(self, name, order):
        self.name = name
        self.order = order
        self.entered = asyncio.Event()
        self.release = asyncio.Event()
        self.server = None
        self.task = None
        self.closed = False
        self.fail_start = False
        self.fail_stop = False
        self.wait_start = False
        self.wait_stop = False

    async def start(self, hub):
        self.server = await asyncio.start_server(lambda r, w: w.close(), "127.0.0.1", 0)
        self.task = asyncio.create_task(asyncio.Event().wait(), name=f"resource:{self.name}")
        self.entered.set()
        if self.fail_start:
            raise ValueError("original start failure")
        if self.wait_start:
            await self.release.wait()

    async def stop(self):
        self.order.append(self.name)
        self.entered.set()
        try:
            if self.wait_stop:
                await self.release.wait()
        finally:
            self.server.close()
            await self.server.wait_closed()
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
            self.closed = True
        if self.fail_stop:
            raise RuntimeError("stop failure")

    def health(self):
        return {"status": "ok"}


def resource_loader(*resources):
    loader = IntegrationLoader(IntegrationRegistry(), {}, cleanup_timeout=0.15, cleanup_cancel_timeout=0.15)
    loader.integrations = {item.name: item for item in resources}
    return loader


def assert_closed(*resources):
    for item in resources:
        assert item.closed
        assert item.task.done()
        assert not item.server.is_serving()
        assert item.server.sockets == ()


async def test_stop_repeated_cancellation_joins_actual_cleanup():
    order = []
    first, second = (ResourceIntegration(name, order) for name in ("first", "second"))
    loader = resource_loader(first, second)
    await loader.start(None)
    second.entered.clear()
    second.wait_stop = True
    stop = asyncio.create_task(loader.stop())
    await second.entered.wait()
    stop.cancel("first cancellation")
    await asyncio.sleep(0)
    stop.cancel("repeated cancellation")
    await asyncio.sleep(0)
    assert not stop.done()
    second.release.set()
    with pytest.raises(asyncio.CancelledError):
        await stop
    assert_closed(first, second)
    assert order == ["second", "first"]
    assert loader._pending_cleanup == {}
    assert loader._cleanup_task.done()
    assert loader.integrations == {}


async def test_cancel_during_start_side_effects_and_repeated_rollback_cancel():
    order = []
    first, second = (ResourceIntegration(name, order) for name in ("first", "second"))
    second.wait_start = True
    first.wait_stop = True
    loader = resource_loader(first, second)
    start = asyncio.create_task(loader.start(None))
    await second.entered.wait()
    first.entered.clear()
    start.cancel("startup cancellation")
    await first.entered.wait()
    start.cancel("rollback cancellation one")
    await asyncio.sleep(0)
    start.cancel("rollback cancellation two")
    first.release.set()
    with pytest.raises(asyncio.CancelledError, match="startup cancellation"):
        await start
    assert_closed(first, second)
    assert order == ["second", "first"]
    assert loader._pending_cleanup == {}


async def test_original_start_failure_survives_cleanup_failure():
    order = []
    first, second = (ResourceIntegration(name, order) for name in ("first", "second"))
    first.fail_stop = True
    second.fail_start = True
    loader = resource_loader(first, second)
    with pytest.raises(ValueError, match="original start failure"):
        await loader.start(None)
    assert_closed(first, second)
    assert order == ["second", "first"]
    assert loader._cleanup_errors["first"]["status"] == "error"
    assert loader.health_summary()["first"]["status"] == "error"


async def test_startup_rollback_deadline_closes_resources_and_keeps_original_error():
    order = []
    first, second = (ResourceIntegration(name, order) for name in ("first", "second"))
    first.wait_stop = True
    second.fail_start = True
    loader = resource_loader(first, second)
    async with asyncio.timeout(1):
        with pytest.raises(ValueError, match="original start failure"):
            await loader.start(None)
    assert_closed(first, second)
    assert order == ["second", "first"]
    assert loader._pending_cleanup == {}


async def test_hanging_stop_deadline_failure_and_remaining_lifo_resources():
    order = []
    resources = [ResourceIntegration(name, order) for name in ("first", "failure", "hang")]
    resources[1].fail_stop = True
    resources[2].wait_stop = True
    loader = resource_loader(*resources)
    await loader.start(None)
    async with asyncio.timeout(1):
        with pytest.raises(ExceptionGroup) as caught:
            await loader.stop()
    assert {type(e) for e in caught.value.exceptions} == {TimeoutError, RuntimeError}
    assert_closed(*resources)
    assert order == ["hang", "failure", "first"]
    assert loader._pending_cleanup == {}
    assert loader._cleanup_errors["hang"]["status"] == "error"
    assert loader.health_summary()["hang"]["status"] == "error"


async def test_failed_cleanup_retains_owner_until_retry_then_allows_restart():
    class RefuseClose(ResourceIntegration):
        async def stop(self):
            if self.fail_stop:
                raise RuntimeError("resource still open")
            await super().stop()

    resource = RefuseClose("owner", [])
    resource.fail_stop = True
    loader = resource_loader(resource)
    await loader.start(None)
    with pytest.raises(ExceptionGroup):
        await loader.stop()
    assert not resource.closed
    assert resource.server.is_serving()
    assert resource in loader._failed_cleanup
    assert loader.health_summary()["owner"]["status"] == "error"
    with pytest.raises(RuntimeError, match="retry stop"):
        await loader.start(None)
    with pytest.raises(RuntimeError, match="retry stop"):
        loader.load()
    resource.fail_stop = False
    await loader.stop()
    assert_closed(resource)
    assert loader._failed_cleanup == {}
    assert loader.health_summary() == {}
    await loader.start(None)
    await loader.stop()


async def test_cancellation_resistant_cleanup_stays_owned_and_blocks_restart():
    order = []

    class Delayed(ResourceIntegration):
        async def stop(self):
            try:
                await self.release.wait()
            except asyncio.CancelledError:
                await self.release.wait()
            await super().stop()

    first, delayed = ResourceIntegration("first", order), Delayed("delayed", order)
    loader = resource_loader(first, delayed)
    await loader.start(None)
    with pytest.raises(ExceptionGroup):
        await loader.stop()
    assert_closed(first)
    assert not delayed.closed
    assert len(loader._pending_cleanup) == 1
    assert loader.health_summary()["delayed"]["status"] == "error"
    with pytest.raises(RuntimeError, match="cleanup is still pending"):
        await loader.start(None)
    delayed.release.set()
    await asyncio.gather(*loader._pending_cleanup.values())
    await asyncio.sleep(0)
    assert_closed(delayed)
    assert loader._pending_cleanup == {}


async def test_concurrent_stop_retries_join_the_same_retained_resource():
    class RetryOwner(ResourceIntegration):
        calls = 0

        async def stop(self):
            self.calls += 1
            if self.fail_stop:
                raise RuntimeError("resource still open")
            await super().stop()

    resource = RetryOwner("retry-owner", [])
    resource.fail_stop = True
    loader = resource_loader(resource)
    await loader.start(None)
    with pytest.raises(ExceptionGroup):
        await loader.stop()
    resource.fail_stop = False
    resource.wait_stop = True
    resource.entered.clear()
    first = asyncio.create_task(loader.stop())
    await resource.entered.wait()
    second = asyncio.create_task(loader.stop())
    await asyncio.sleep(0)
    first.cancel()
    await asyncio.sleep(0)
    first.cancel()
    assert resource.calls == 2  # Initial failure plus exactly one shared retry.
    resource.release.set()
    with pytest.raises(asyncio.CancelledError):
        await first
    await second
    assert_closed(resource)
    assert loader._failed_cleanup == {}
    assert loader.health_summary() == {}


async def test_stop_failure_and_external_cancellation_both_propagate():
    resource = ResourceIntegration("failing", [])
    resource.fail_stop = True
    resource.wait_stop = True
    loader = resource_loader(resource)
    await loader.start(None)
    resource.entered.clear()
    stop = asyncio.create_task(loader.stop())
    await resource.entered.wait()
    stop.cancel()
    resource.release.set()
    with pytest.raises(BaseExceptionGroup) as caught:
        await stop

    def leaves(error):
        if isinstance(error, BaseExceptionGroup):
            return [leaf for child in error.exceptions for leaf in leaves(child)]
        return [error]

    assert {type(exc) for exc in leaves(caught.value)} == {RuntimeError, asyncio.CancelledError}
    assert_closed(resource)


async def test_loader_restart_recreates_and_closes_resources(monkeypatch):
    order = []

    class Restartable(ResourceIntegration):
        name = "restartable"
        env_flag = "RESTARTABLE"

        @classmethod
        def config_from_env(cls, env):
            return None

        def __init__(self, config):
            super().__init__(self.name, order)

    monkeypatch.setattr(sys.modules[__name__], "Restartable", Restartable, raising=False)
    registry = IntegrationRegistry()
    registry.register("restartable", "RESTARTABLE", f"{__name__}:Restartable")
    loader = IntegrationLoader(registry, {"RESTARTABLE": "true"})
    old = None
    for _ in range(2):
        await loader.start(None)
        current = loader.integrations["restartable"]
        assert current is not old
        assert loader.health_summary() == {"restartable": {"status": "ok"}}
        await loader.stop()
        assert_closed(current)
        old = current


class ZeroconfResource:
    """Match real AsyncZeroconf's nested announcement/goodbye awaitables."""

    def __init__(self, *, fail=False, block=False):
        self.entered = asyncio.Event()
        self.release = asyncio.Event()
        self.advertised = False
        self.closed = False
        self.fail = fail
        self.block = block
        self.goodbye_finished = False

    async def async_register_service(self, info, *, strict):
        assert strict is False
        self.advertised = True
        self.entered.set()
        if self.block:
            await self.release.wait()
        if self.fail:
            raise RuntimeError("synthetic-private")

        async def finish_announcement():
            await asyncio.sleep(0)
        return finish_announcement()

    async def async_unregister_service(self, info):
        async def finish_goodbye():
            await asyncio.sleep(0)
            self.advertised = False
            self.goodbye_finished = True
        return finish_goodbye()

    async def async_close(self):
        self.closed = True


@pytest.mark.parametrize("mode", ["normal", "failure", "cancel"])
async def test_owned_ha_closes_and_withdraws_partial_registration(monkeypatch, mode):
    zc = ZeroconfResource(fail=mode == "failure", block=mode == "cancel")
    monkeypatch.setattr("zeroconf.asyncio.AsyncZeroconf", lambda: zc)
    ha = HomeAssistantDiscoveryIntegration(HomeAssistantDiscoveryConfig(enabled=True, host_ip="127.0.0.1"))
    start = asyncio.create_task(ha.start(None))
    await zc.entered.wait()
    if mode == "cancel":
        start.cancel()
        with pytest.raises(asyncio.CancelledError):
            await start
    else:
        await start
        if mode == "normal":
            assert ha.health()["registered"]
            await ha.stop()
        else:
            assert ha.health()["status"] == "error"
            assert "synthetic-private" not in json.dumps(ha.health())
    assert zc.goodbye_finished
    assert not zc.advertised
    assert zc.closed
    assert ha._zeroconf is None


async def test_ha_close_failure_keeps_resource_owned_and_discovery_degraded(monkeypatch):
    class CloseFailure(ZeroconfResource):
        async def async_close(self):
            if self.fail:
                raise RuntimeError("synthetic close failure")
            await super().async_close()

    zc = CloseFailure(fail=True)
    monkeypatch.setattr("zeroconf.asyncio.AsyncZeroconf", lambda: zc)
    ha = HomeAssistantDiscoveryIntegration(HomeAssistantDiscoveryConfig(enabled=True, host_ip="127.0.0.1"))
    await ha.start(None)
    assert ha.health()["status"] == "error"
    assert ha._zeroconf is zc
    assert ha._owns_zeroconf
    assert not zc.closed
    zc.fail = False
    await ha.stop()
    assert zc.closed
    assert ha._zeroconf is None


async def test_real_loopback_ha_discovery_api_and_goodbye(monkeypatch, tmp_path, aiohttp_client):
    """Actual multicast and REST on loopback; no HA installation/image claim."""
    from zeroconf import ServiceStateChange
    from zeroconf.asyncio import AsyncServiceBrowser, AsyncServiceInfo, AsyncZeroconf

    from hub.integrations.homeassistant import SERVICE_TYPE

    client = await aiohttp_client(create_rest_app(tmp_path, integration_routes=[]))
    service_name = "R5B-loopback-" + uuid.uuid4().hex[:8]
    full_name = service_name + "." + SERVICE_TYPE
    added, removed = asyncio.Event(), asyncio.Event()
    observer = AsyncZeroconf(interfaces=["127.0.0.1"])

    def changed(zeroconf, service_type, name, state_change):
        if name == full_name:
            if state_change is ServiceStateChange.Added:
                added.set()
            elif state_change is ServiceStateChange.Removed:
                removed.set()

    browser = AsyncServiceBrowser(observer.zeroconf, SERVICE_TYPE, handlers=[changed])
    owned = []

    def factory():
        # Only constrain interfaces; this is the real installed implementation.
        zc = AsyncZeroconf(interfaces=["127.0.0.1"])
        owned.append(zc)
        return zc

    monkeypatch.setattr("zeroconf.asyncio.AsyncZeroconf", factory)
    ha = HomeAssistantDiscoveryIntegration(HomeAssistantDiscoveryConfig(
        enabled=True, host_ip="127.0.0.1", api_port=client.server.port, service_name=service_name))
    loader = IntegrationLoader(IntegrationRegistry(), {})
    loader.integrations = {ha.name: ha}
    try:
        await loader.start(None)
        assert loader.health_summary()[ha.name]["status"] == "ok"
        await asyncio.wait_for(added.wait(), 5)
        info = AsyncServiceInfo(SERVICE_TYPE, full_name)
        assert await info.async_request(observer.zeroconf, 2000)
        assert info.parsed_addresses() == ["127.0.0.1"]
        assert info.port == client.server.port
        assert info.properties[b"path"] == b"/api"
        response = await client.get("/api/health")
        assert response.status == 200
        assert (await response.json())["data"]["status"] == "healthy"
        await loader.stop()
        await asyncio.wait_for(removed.wait(), 5)
        assert owned[0].zeroconf.done
        assert ha._zeroconf is None
        assert loader._pending_cleanup == {}
    finally:
        await loader.stop()
        await browser.async_cancel()
        await observer.async_close()
        for zc in owned:
            await zc.async_close()


async def test_real_zeroconf_registration_cancel_closes_owned_instance(monkeypatch):
    from zeroconf.asyncio import AsyncZeroconf

    created = asyncio.Event()
    owned = []

    def factory():
        zc = AsyncZeroconf(interfaces=["127.0.0.1"])
        owned.append(zc)
        created.set()
        return zc

    monkeypatch.setattr("zeroconf.asyncio.AsyncZeroconf", factory)
    ha = HomeAssistantDiscoveryIntegration(HomeAssistantDiscoveryConfig(
        enabled=True, host_ip="127.0.0.1", service_name="R5B-cancel-" + uuid.uuid4().hex[:8]))
    start = asyncio.create_task(ha.start(None))
    try:
        await created.wait()
        start.cancel("original registration cancellation")
        await asyncio.sleep(0)
        start.cancel("repeated registration cancellation")
        with pytest.raises(asyncio.CancelledError, match="original registration cancellation"):
            await start
        assert owned[0].zeroconf.done
        assert ha._zeroconf is None
        assert not ha._registered
        assert ha._cleanup_task.done()
    finally:
        await ha.stop()
        await asyncio.gather(start, return_exceptions=True)
        for zc in owned:
            await zc.async_close()
