"""Shared HubClient contract exercised in-process and over real aiohttp sockets."""

import asyncio
import importlib
import sys
from collections.abc import Callable
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

import hub

# This scoped worktree contributes a hub namespace subpackage. A shared editable
# venv may already contain the hub root from the parallel core worktree. Always
# exercise this worktree's integration code, without changing that installation.
_hub_path = str(Path(__file__).resolve().parents[1] / "src" / "hub")
hub.__path__ = [_hub_path, *[path for path in hub.__path__ if path != _hub_path]]

from hub.integrations import (
    HubClient,
    HubClientHttp,
    HubClientLocal,
    HubEvent,
    HubSnapshot,
    Integration,
    IntegrationConfig,
    IntegrationLoader,
    IntegrationRegistry,
)
from hub.integrations.hub_client_http import HubClientError
from rest_api import control, core, outputs
from rest_api.utils import set_matrix_device, update_input_names


class MemoryMatrix:
    """Stateful matrix/state provider; no network or mocked methods."""

    host = "127.0.0.1"
    port = 443
    telnet_connected = True

    def __init__(self):
        self.state = HubSnapshot(
            connected=True,
            power=True,
            routing={i: i for i in range(1, 9)},
            input_names={i: f"Source {i}" for i in range(1, 9)},
            output_names={i: f"TV {i}" for i in range(1, 9)},
            preset_names={i: f"Slot {i}" for i in range(1, 9)},
            input_signals={i: i % 2 == 0 for i in range(1, 9)},
            input_cables={i: i != 3 for i in range(1, 9)},
            output_displays={i: i != 4 for i in range(1, 9)},
            favorite_presets=[2, 4],
            profiles=[{"id": "movie", "name": "Movie"}],
            scenes=[{"id": "evening", "name": "Evening"}],
            shortcuts=[{"id": "mute", "name": "Mute"}],
            macros=[{"id": "wake", "name": "Wake"}],
        )
        self.callbacks: list[Callable] = []
        self.saved = {}
        self.cec = []

    @property
    def connected(self):
        return self.state.connected

    async def snapshot(self):
        return deepcopy(self.state)

    def subscribe(self, callback):
        self.callbacks.append(callback)
        return lambda: self.callbacks.remove(callback)

    def changed(self):
        for callback in list(self.callbacks):
            callback(HubEvent("status", asdict(self.state)))

    async def get_status(self):
        return {
            "connected": self.connected,
            "power": "on" if self.state.power else "off",
            "routing": list(self.state.routing.values()),
            "input_names": list(self.state.input_names.values()),
            "output_names": list(self.state.output_names.values()),
            "preset_names": list(self.state.preset_names.values()),
        }

    async def get_full_status(self):
        return {
            **await self.get_status(),
            "inputs_inactive": list(self.state.input_signals.values()),
            "outputs_connected": list(self.state.output_displays.values()),
        }

    async def get_preset_slots(self):
        return {number: {"routing": routing} for number, routing in self.saved.items()}

    async def get_all_input_names(self):
        return dict(self.state.input_names)

    async def get_output_names(self):
        return dict(self.state.output_names)

    async def get_all_cable_status(self):
        return {"inputs": self.state.input_cables, "outputs": {i: True for i in range(1, 9)}}

    async def switch_input(self, input_num, output_num):
        if not 1 <= input_num <= 8 or not 1 <= output_num <= 8:
            return False
        self.state.routing[output_num] = input_num
        self.changed()
        return True

    async def switch_input_to_all(self, input_num):
        for output_num in range(1, 9):
            await self.switch_input(input_num, output_num)
        return True

    async def switch(self, input_num, output_num=None):
        if output_num is None:
            return await self.switch_input_to_all(input_num)
        return await self.switch_input(input_num, output_num)

    async def get_current_input_for_output(self, output_num):
        return self.state.routing[output_num]

    async def recall_preset(self, preset):
        self.state.routing = dict(self.saved.get(preset, dict.fromkeys(range(1, 9), preset)))
        self.changed()
        return True

    async def save_preset(self, preset):
        self.saved[preset] = dict(self.state.routing)
        return True

    async def power(self, on):
        self.state.power = on
        self.changed()
        return True

    async def power_on(self):
        return await self.power(True)

    async def power_off(self):
        return await self.power(False)

    async def send_cec(self, target_kind, port, command):
        self.cec.append((target_kind, port, command))
        return True

    async def run_action(self, kind, action_id, *, passcode=None):
        if action_id == "locked" and passcode != "1234":
            return {"success": False, "data": {"error": "passcode_required"}, "error": None}
        return {"success": True, "data": {"kind": kind, "id": action_id}, "error": None}


class ContractServer:
    """Real production status/control handlers plus deterministic catalog/WS peers."""

    def __init__(self, matrix, api_key=None):
        self.matrix = matrix
        self.api_key = api_key
        self.websockets = set()
        self.requests = []
        self.ws_connections = 0
        self.status_override = None
        self.fail_path = None

    async def start(self):
        set_matrix_device(self.matrix, self.matrix.state.input_names, self.matrix.state.output_names)

        @web.middleware
        async def authentication(request, handler):
            self.requests.append((request.method, request.path_qs, request.headers.get("X-API-Key")))
            if self.api_key and request.headers.get("X-API-Key") != self.api_key:
                return web.json_response({"success": False, "data": None, "error": "API key required"}, status=401)
            if request.path == self.fail_path:
                return web.json_response({"success": False, "data": None, "error": "Unavailable"}, status=503)
            return await handler(request)

        app = web.Application(middlewares=[authentication])
        app.router.add_get("/api/health", core.handle_health)
        app.router.add_get("/api/status", self.status)
        app.router.add_get("/api/status/full", outputs.handle_full_status)
        app.router.add_get("/api/inputs", core.handle_inputs)
        app.router.add_get("/api/outputs", core.handle_outputs)
        app.router.add_get("/api/presets", core.handle_presets)
        app.router.add_get("/api/status/cables", outputs.handle_cable_status)
        for path in ("profiles", "scenes", "shortcuts", "cec/macros", "device-settings/favorite-presets"):
            app.router.add_get("/api/" + path, self.catalog)
        app.router.add_post("/api/switch", control.handle_switch)
        app.router.add_post("/api/input/next", control.handle_input_next)
        app.router.add_post("/api/input/previous", control.handle_input_previous)
        app.router.add_post("/api/preset/{preset}", control.handle_preset)
        app.router.add_post("/api/preset/{preset}/save", control.handle_preset_save)
        app.router.add_post("/api/power/on", control.handle_power_on)
        app.router.add_post("/api/power/off", control.handle_power_off)
        app.router.add_post("/api/cec/{kind}/{port}/{command}", self.cec)
        app.router.add_post("/api/profile/{id}/recall", self.action)
        app.router.add_post("/api/scene/{id}/recall", self.action)
        app.router.add_post("/api/v2/scenes/{id}/execute", self.action)
        app.router.add_post("/api/shortcuts/{id}/execute", self.action)
        app.router.add_post("/api/cec/macro/{id}/execute", self.action)
        app.router.add_get("/ws", self.websocket)
        self.server = TestServer(app)
        await self.server.start_server()
        self.url = str(self.server.make_url("/")).rstrip("/")
        return self

    async def close(self):
        for ws in list(self.websockets):
            await ws.close()
        await self.server.close()

    async def status(self, request):
        if self.status_override is not None:
            return web.json_response({"success": True, "data": self.status_override, "error": None})
        return await core.handle_status(request)

    async def catalog(self, request):
        key = request.path.rsplit("/", 1)[-1].replace("-", "_")
        return web.json_response({"success": True, "data": {key: getattr(self.matrix.state, key)}, "error": None})

    async def cec(self, request):
        p = request.match_info
        await self.matrix.send_cec(p["kind"], int(p["port"]), p["command"])
        return web.json_response({"success": True, "data": {}, "error": None})

    async def action(self, request):
        if request.path.startswith("/api/v2/scenes/"):
            kind = "scene"
        else:
            kind = "macro" if "/cec/" in request.path else request.path.split("/")[2].rstrip("s")
        body = await request.json() if request.can_read_body else {}
        result = await self.matrix.run_action(kind, request.match_info["id"], passcode=body.get("passcode"))
        return web.json_response(result, status=200 if result["success"] else 403)

    async def websocket(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websockets.add(ws)
        self.ws_connections += 1
        try:
            async for _ in ws:
                pass
        finally:
            self.websockets.discard(ws)
        return ws

    async def emit(self, event, data):
        for ws in list(self.websockets):
            await ws.send_json({"event": event, "data": data})


@pytest.fixture
async def contract_server():
    peer = await ContractServer(MemoryMatrix(), api_key="control-secret").start()
    try:
        yield peer
    finally:
        await peer.close()


@pytest.fixture(params=["local", "http"])
async def contract_client(request, contract_server):
    matrix = contract_server.matrix
    if request.param == "local":
        client = HubClientLocal(matrix)
    else:
        client = HubClientHttp(contract_server.url, api_key=contract_server.api_key, reconnect_delay=0.01)
    try:
        yield client, contract_server
    finally:
        await client.close()


async def eventually(predicate):
    async with asyncio.timeout(3):
        while not predicate():
            await asyncio.sleep(0.005)


async def test_shared_snapshot_contract(contract_client):
    client, peer = contract_client
    assert isinstance(client, HubClient)
    assert await client.snapshot() == peer.matrix.state
    state = await client.snapshot()
    state.routing[1] = 99
    state.profiles[0]["name"] = "Changed"
    assert (await client.snapshot()).routing[1] == 1
    assert (await client.snapshot()).profiles[0]["name"] == "Movie"


async def test_shared_command_contract(contract_client):
    client, peer = contract_client
    assert await client.switch(7, 2)
    assert (await client.snapshot()).routing[2] == 7
    assert await client.switch(8)
    assert (await client.snapshot()).routing == dict.fromkeys(range(1, 9), 8)
    assert await client.cycle_input("next", 5)
    assert (await client.snapshot()).routing[5] == 1
    assert (await client.snapshot()).routing[1] == 8
    assert await client.cycle_input("previous", 5)
    assert (await client.snapshot()).routing[5] == 8
    assert await client.save_preset(3)
    assert await client.switch(2)
    assert await client.recall_preset(3)
    assert (await client.snapshot()).routing == dict.fromkeys(range(1, 9), 8)
    assert await client.power(False)
    assert not (await client.snapshot()).power
    assert await client.power(True)
    assert await client.send_cec("output", 4, "power_on")
    assert peer.matrix.cec[-1] == ("output", 4, "power_on")
    assert not await client.switch(3, 0)
    with pytest.raises(ValueError):
        await client.cycle_input("sideways")
    with pytest.raises(ValueError):
        await client.send_cec("other", 1, "power_on")


@pytest.mark.parametrize("kind", ["profile", "scene", "shortcut", "macro"])
async def test_shared_actions_and_passcodes(contract_client, kind):
    client, _ = contract_client
    assert await client.run_action(kind, "movie") == {
        "success": True,
        "data": {"kind": kind, "id": "movie"},
        "error": None,
    }
    result = await client.run_action(kind, "locked")
    assert result["success"] is False
    assert result["data"]["error"] == "passcode_required"
    assert (await client.run_action(kind, "locked", passcode="1234"))["success"] is True
    with pytest.raises(ValueError):
        await client.run_action("other", "id")


async def test_shared_subscribe_projection_and_changes(contract_client):
    client, peer = contract_client
    events = []
    unsubscribe = client.subscribe(events.append)
    await eventually(
        lambda: (
            {e.kind for e in events}
            >= {"routing", "signal", "cable", "display", "power", "names", "presets", "hub_connection"}
        )
    )
    if isinstance(client, HubClientHttp):
        await eventually(lambda: client.websocket_connected)
    events.clear()
    state = peer.matrix.state
    state.routing[2] = 6
    state.input_signals[1] = True
    state.input_cables[3] = True
    state.output_displays[4] = True
    state.power = False
    state.input_names[1] = "Console"
    await update_input_names(state.input_names)
    state.preset_names[1] = "Gaming"
    state.favorite_presets = [1]
    state.connected = False
    peer.matrix.changed()
    # Send each event through the real WebSocket transport.
    for event, data in [
        ("routing_change", {"input": 6, "output": 2}),
        ("signal_change", {"input": 1, "has_signal": True}),
        ("cable_change", {"type": "input", "port": 3, "connected": True}),
        ("connection_change", {"output": 4, "connected": True}),
        ("power_change", {"power": "off"}),
        ("names_change", {"input_names": state.input_names}),
        ("presets_change", {"preset_names": state.preset_names}),
        ("matrix_connection", {"connected": False}),
    ]:
        await peer.emit(event, data)
    await eventually(
        lambda: (
            {e.kind for e in events}
            >= {"routing", "signal", "cable", "display", "power", "names", "presets", "hub_connection"}
        )
    )
    assert next(e for e in reversed(events) if e.kind == "routing").data["routing"][2] == 6
    unsubscribe()
    unsubscribe()
    count = len(events)
    peer.matrix.changed()
    await peer.emit("routing_change", {"input": 2, "output": 2})
    await asyncio.sleep(0.03)
    assert len(events) == count


async def test_shared_close_is_idempotent_and_does_not_close_provider(contract_client):
    client, peer = contract_client
    unsubscribe = client.subscribe(lambda event: None)
    await asyncio.sleep(0.02)
    unsubscribe()
    await client.close()
    await client.close()
    assert peer.matrix.connected
    assert not peer.matrix.callbacks
    with pytest.raises(RuntimeError):
        await client.snapshot()
    with pytest.raises(RuntimeError):
        client.subscribe(lambda event: None)


async def test_http_authentication_failure_is_actionable(contract_server):
    client = HubClientHttp(contract_server.url)
    try:
        with pytest.raises(HubClientError, match="HUB_API_KEY / CONTROL_PIN"):
            await client.snapshot()
        assert not await client.switch(3)
    finally:
        await client.close()


@pytest.mark.parametrize("routing", [{"routing": {"1": 7}}, {"outputs": [7]}, {"allconnect": [7]}])
async def test_http_routing_sources(contract_server, routing):
    contract_server.status_override = routing
    client = HubClientHttp(contract_server.url, api_key=contract_server.api_key)
    try:
        assert (await client.snapshot()).routing == {1: 7}
    finally:
        await client.close()


async def test_http_reconnect_full_catalog_resync(contract_server):
    peer = contract_server
    client = HubClientHttp(peer.url, api_key=peer.api_key, reconnect_delay=0.01)
    events = []
    unsubscribe = client.subscribe(events.append)
    try:
        await eventually(lambda: peer.ws_connections == 1 and bool(events))
        # Changes made while the socket is down must arrive without any delta event.
        peer.matrix.state.routing[8] = 2
        peer.matrix.state.input_names[2] = "New source"
        await update_input_names(peer.matrix.state.input_names)
        peer.matrix.state.scenes = [{"id": "new-scene"}]
        for ws in list(peer.websockets):
            await ws.close()
        await eventually(lambda: peer.ws_connections >= 2 and client._snapshot.scenes == [{"id": "new-scene"}])
        assert client._snapshot.routing[8] == 2
        assert client._snapshot.input_names[2] == "New source"
        assert any(e.kind == "hub_connection" and not e.data["connected"] for e in events)
        assert all(key == peer.api_key for _, _, key in peer.requests)
        for path in (
            "/api/health",
            "/api/status",
            "/api/status/full",
            "/api/profiles",
            "/api/scenes",
            "/api/shortcuts",
            "/api/cec/macros",
        ):
            assert sum(p == path for _, p, _ in peer.requests) >= 2
    finally:
        unsubscribe()
        await client.close()
    assert not client._tasks
    assert client._ws_task is None
    assert client._session is None


@pytest.mark.parametrize("event", ["status", "status_update"])
async def test_http_current_and_legacy_snapshot_events(contract_server, event):
    client = HubClientHttp(contract_server.url, api_key=contract_server.api_key)
    try:
        await client.connect_websocket()
        await contract_server.emit(
            event,
            {
                "routing": {"3": 7},
                "power": "off",
                "connected": True,
                "inputs": [{"number": 2, "signalActive": False}],
                "outputs_detail": [{"number": 5, "connected": False}],
            },
        )
        await eventually(lambda: client._snapshot.routing.get(3) == 7)
        assert client._snapshot.power is False
        assert client._snapshot.input_signals[2] is False
        assert client._snapshot.output_displays[5] is False
    finally:
        await client.close()


async def test_http_recovers_after_initial_ws_failure(contract_server):
    peer = contract_server
    peer.fail_path = "/ws"
    client = HubClientHttp(peer.url, api_key=peer.api_key, reconnect_delay=0.01)
    try:
        assert not await client.connect_websocket()
        peer.fail_path = None
        await eventually(lambda: peer.ws_connections == 1 and client.websocket_connected)
        assert client._snapshot.routing == peer.matrix.state.routing
    finally:
        await client.close()


class DemoIntegration(Integration):
    name = "demo"
    env_flag = "DEMO_ENABLED"
    calls: list[str] = []
    fail_start = False
    fail_stop = False

    def __init__(self, config):
        assert isinstance(config, IntegrationConfig)
        self.config = config

    async def start(self, hub):
        self.calls.append("start:" + self.name)
        if self.fail_start:
            raise RuntimeError("start failed")

    async def stop(self):
        self.calls.append("stop:" + self.name)
        if self.fail_stop:
            raise RuntimeError("stop failed")

    def health(self):
        return {"status": "healthy"}

    def routes(self):
        return [web.get("/demo", lambda request: web.Response())]


def register_demo(registry):
    registry.register("demo", "DEMO_ENABLED", __name__ + ":DemoIntegration")


@pytest.mark.parametrize("flag", [None, "", "false", "0", "no", "off"])
def test_disabled_integrations_never_import_or_register_routes(tmp_path, monkeypatch, flag):
    (tmp_path / "disabled_plugin.py").write_text("raise AssertionError('disabled integration imported')\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    registry = IntegrationRegistry()
    registry.register("disabled", "DISABLED_ENABLED", "disabled_plugin:Plugin")
    loader = IntegrationLoader(registry, {} if flag is None else {"DISABLED_ENABLED": flag})
    assert loader.load() == {}
    assert loader.routes() == []
    assert loader.health_summary() == {}
    assert "disabled_plugin" not in sys.modules


@pytest.mark.parametrize("flag", ["1", "TRUE", "yes", " on "])
async def test_loader_lifecycle_routes_health(flag):
    DemoIntegration.calls = []
    registry = IntegrationRegistry()
    register_demo(registry)
    loader = IntegrationLoader(registry, {"DEMO_ENABLED": flag})
    assert loader.load()["demo"].config.enabled
    assert len(loader.routes()) == 1
    await loader.start(HubClientLocal(MemoryMatrix()))
    await loader.start(HubClientLocal(MemoryMatrix()))
    assert loader.health_summary() == {"demo": {"status": "healthy"}}
    await loader.stop()
    await loader.stop()
    assert DemoIntegration.calls == ["start:demo", "stop:demo"]
    assert loader.routes() == []
    assert loader.health_summary() == {}


async def test_loader_cleans_up_partial_start_and_attempts_all_stops(monkeypatch):
    class BrokenIntegration(DemoIntegration):
        name = "broken"
        env_flag = "BROKEN_ENABLED"
        fail_start = True
        fail_stop = True

    module = importlib.import_module(__name__)
    monkeypatch.setattr(module, "BrokenIntegration", BrokenIntegration, raising=False)
    DemoIntegration.calls = []
    registry = IntegrationRegistry()
    register_demo(registry)
    registry.register("broken", "BROKEN_ENABLED", __name__ + ":BrokenIntegration")
    loader = IntegrationLoader(registry, {"DEMO_ENABLED": "true", "BROKEN_ENABLED": "true"})
    with pytest.raises(RuntimeError, match="start failed"):
        await loader.start(HubClientLocal(MemoryMatrix()))
    assert DemoIntegration.calls == ["start:demo", "start:broken", "stop:broken", "stop:demo"]
    assert loader.health_summary() == {"broken": {"status": "error", "error": "shutdown failed"}}


def test_registry_duplicate_and_registration_validation():
    registry = IntegrationRegistry()
    register_demo(registry)
    with pytest.raises(ValueError, match="already registered"):
        register_demo(registry)
    with pytest.raises(ValueError, match="module:Class"):
        registry.register("bad", "BAD_ENABLED", "not-an-import-path")


async def test_local_orei_matrix_and_callbacks_path():
    matrix = MemoryMatrix()

    class MatrixOnly:
        @property
        def connected(self):
            return matrix.connected

        get_status = matrix.get_status
        get_full_status = matrix.get_full_status
        get_all_cable_status = matrix.get_all_cable_status
        switch_input = matrix.switch_input
        switch_input_to_all = matrix.switch_input_to_all
        recall_preset = matrix.recall_preset
        save_preset = matrix.save_preset
        power_on = matrix.power_on
        power_off = matrix.power_off

        async def send_cec(self, command, port, is_output=False):
            return await matrix.send_cec("output" if is_output else "input", port, command)

    client = HubClientLocal(MatrixOnly(), action_runner=matrix.run_action, event_subscribe=matrix.subscribe)
    try:
        state = await client.snapshot()
        assert state.routing == matrix.state.routing
        assert state.input_signals == matrix.state.input_signals
        assert state.input_cables == matrix.state.input_cables
        assert state.output_displays == matrix.state.output_displays
        events = []
        client.subscribe(events.append)
        await eventually(lambda: len(events) >= 8)
        assert await client.switch(8)
        assert await client.cycle_input("next", 4)
        assert (await client.snapshot()).routing[4] == 1
        assert await client.cycle_input("previous", 4)
        assert await client.power(False)
        assert await client.send_cec("output", 2, "power_on")
        assert matrix.cec[-1] == ("output", 2, "power_on")
        assert (await client.run_action("scene", "locked", passcode="1234"))["success"]
        matrix.state.input_names[1] = "Front-panel name"
        matrix.changed()
        await eventually(
            lambda: any(e.kind == "names" and e.data["input_names"][1] == "Front-panel name" for e in events)
        )
    finally:
        await client.close()
    assert not matrix.callbacks
    assert matrix.connected


async def test_shared_async_callbacks_are_isolated(contract_client):
    client, peer = contract_client
    received = []

    def broken(event):
        raise RuntimeError("Subscriber failed")

    async def changed(event):
        await asyncio.sleep(0)
        received.append(event)
        if event.kind == "routing":
            event.data["routing"][1] = 99

    client.subscribe(broken)
    unsubscribe = client.subscribe(changed)
    await eventually(lambda: len(received) >= 8)
    assert (await client.snapshot()).routing[1] == 1
    unsubscribe()


async def test_shared_output_cable_event(contract_client):
    client, peer = contract_client
    events = []
    client.subscribe(events.append)
    await eventually(lambda: len(events) >= 8)
    if isinstance(client, HubClientHttp):
        await eventually(lambda: client.websocket_connected)
    data = {"type": "output", "port": 3, "connected": False}
    for callback in peer.matrix.callbacks:
        callback(HubEvent("cable", data))
    await peer.emit("cable_change", data)
    await eventually(lambda: any(e.kind == "cable" and e.data == data for e in events))


async def test_http_malformed_ws_message_does_not_kill_updates(contract_server):
    client = HubClientHttp(contract_server.url, api_key=contract_server.api_key)
    try:
        assert await client.connect_websocket()
        for ws in contract_server.websockets:
            await ws.send_str("{not-json}")
            await ws.send_json([])
        await contract_server.emit("routing_change", {"output": "not-a-port"})
        await contract_server.emit("routing_change", {"output": 1, "input": 8})
        await eventually(lambda: client._snapshot.routing[1] == 8)
        assert client.websocket_connected
    finally:
        await client.close()


async def test_loader_stop_failure_and_health_failure(monkeypatch):
    DemoIntegration.calls = []
    monkeypatch.setattr(DemoIntegration, "fail_stop", True)
    registry = IntegrationRegistry()
    register_demo(registry)
    loader = IntegrationLoader(registry, {"DEMO_ENABLED": "1"})
    await loader.start(HubClientLocal(MemoryMatrix()))

    def health(self):
        raise RuntimeError("Health failed")

    monkeypatch.setattr(DemoIntegration, "health", health)
    assert loader.health_summary() == {"demo": {"status": "error"}}
    with pytest.raises(ExceptionGroup, match="shutdown failed"):
        await loader.stop()
    assert loader.health_summary() == {"demo": {"status": "error", "error": "shutdown failed"}}
    owner, = loader._failed_cleanup
    owner.fail_stop = False
    await loader.stop()
    assert loader.health_summary() == {}
    assert DemoIntegration.calls == ["start:demo", "stop:demo", "stop:demo"]
    assert loader.routes() == []


async def test_real_security_middleware_control_pin_and_api_key(tmp_path, monkeypatch):
    from rest_api.security import SecurityManager, security_middleware

    monkeypatch.setenv("CONTROL_PIN", "5678")
    monkeypatch.setenv("CONTROL_API_KEY", "real-control-key")
    monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
    matrix = MemoryMatrix()
    set_matrix_device(matrix, matrix.state.input_names, matrix.state.output_names)
    app = web.Application(middlewares=[security_middleware])
    app["security_manager"] = SecurityManager(tmp_path)
    app.router.add_post("/api/switch", control.handle_switch)
    server = TestServer(app)
    await server.start_server()
    url = str(server.make_url("/")).rstrip("/")
    anonymous = HubClientHttp(url)
    authorized = HubClientHttp(url, api_key="real-control-key")
    try:
        assert not await anonymous.switch(7, 2)
        with pytest.raises(HubClientError, match="HUB_API_KEY / CONTROL_PIN"):
            await anonymous._request("POST", "/api/switch", {"input": 7, "output": 2})
        assert await authorized.switch(7, 2)
        assert matrix.state.routing[2] == 7
    finally:
        await anonymous.close()
        await authorized.close()
        await server.close()


async def test_http_hub_names_take_precedence_over_matrix_cable_names(contract_server):
    names = dict(contract_server.matrix.state.input_names)
    names[1] = "Custom hub label"
    await update_input_names(names)
    client = HubClientHttp(contract_server.url, api_key=contract_server.api_key)
    try:
        state = await client.snapshot()
        assert state.input_names[1] == "Custom hub label"
        assert state.input_cables[1] is True
    finally:
        await client.close()


async def test_http_reconnects_if_health_resync_initially_unavailable(contract_server):
    peer = contract_server
    peer.fail_path = "/api/health"
    client = HubClientHttp(peer.url, api_key=peer.api_key, reconnect_delay=0.01)
    try:
        assert not await client.connect_websocket()
        peer.fail_path = None
        await eventually(lambda: client.websocket_connected)
        assert client._snapshot.routing == peer.matrix.state.routing
    finally:
        await client.close()


async def test_http_presets_event_applies_explicit_favorites(contract_server):
    client = HubClientHttp(contract_server.url, api_key=contract_server.api_key)
    try:
        assert await client.connect_websocket()
        await contract_server.emit("presets_change", {"preset_names": {"1": "Gaming"}, "favorite_presets": [1]})
        await eventually(lambda: client._snapshot.favorite_presets == [1])
        assert client._snapshot.preset_names == {1: "Gaming"}
    finally:
        await client.close()
