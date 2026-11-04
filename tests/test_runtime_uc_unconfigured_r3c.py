"""R3C tests for unconfigured UC startup/event guards and coordinated R4 `cycle_input` dispatcher delegation."""

from __future__ import annotations

import asyncio
import json
import socket
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest
from pyee.asyncio import AsyncIOEventEmitter

import _file_io
import hub.integrations.unfolded_circle.bridge as uc_bridge_mod
import hub.integrations.unfolded_circle.handlers as uc_handlers_mod
import hub.persistence.startup as persistence_startup_mod
import hub.runtime.composition as runtime_composition_mod
import run
from hub.integrations.hub_client import HubEvent, HubSnapshot
from hub.integrations.unfolded_circle import (
    APPROVED_GOLDEN_ENTITY_IDS,
    EntityStateProjector,
    UCCommandDispatcher,
    UnfoldedCircleIntegration,
)
from hub.runtime.composition import HubRuntime, build_runtime
from tools.uc_remote_sim import UcRemoteSim
from tools.validate.device import SimDevice
from tools.validate.stack import HubProcess, SimulatorProcess


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class _MatrixClientDouble:
    """In-process matrix transport double for `build_runtime` tests."""

    def __init__(
        self,
        host: str,
        *,
        port: int = 443,
        telnet_port: int | None = None,
        user: str | None = None,
        password: str | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.telnet_port = telnet_port or 23
        self.user = user or "Admin"
        self.password = password
        self.connected = False
        self.telnet_connected = False
        self.events = AsyncIOEventEmitter()
        self.login_failure: str | None = None
        self.power_state = 1
        self.routes = [1, 2, 3, 4, 5, 6, 7, 8]
        self.input_names = {i: f"Matrix In {i}" for i in range(1, 9)}
        self.output_names = {i: f"Matrix Out {i}" for i in range(1, 9)}
        self.preset_names = {i: f"Matrix Preset {i}" for i in range(1, 9)}
        self.calls: list[tuple[Any, ...]] = []

    async def connect(self) -> bool:
        if self.host.startswith("auth-fail"):
            self.login_failure = "auth"
            self.connected = False
            return False
        if self.host.startswith("offline"):
            self.login_failure = "unreachable"
            self.connected = False
            return False
        self.connected = True
        self.telnet_connected = True
        return True

    async def disconnect(self) -> None:
        self.connected = False
        self.telnet_connected = False

    async def get_status(self) -> dict[str, Any]:
        return {
            "connected": self.connected,
            "power": self.power_state,
            "allsource": list(self.routes),
            "allinputname": [self.input_names[i] for i in range(1, 9)],
            "alloutputname": [self.output_names[i] for i in range(1, 9)],
            "allname": [self.preset_names[i] for i in range(1, 9)],
        }

    async def get_output_status(self, force_refresh: bool = False) -> dict[str, Any]:
        return {
            "allsource": list(self.routes),
            "allconnect": [1, 1, 1, 0, 0, 1, 0, 0],
            "allout": [1] * 8,
            "allaudiomute": [0] * 8,
            "allarc": [0] * 8,
            "allhdr": [3] * 8,
            "allhdcp": [2] * 8,
            "allscaler": [0] * 8,
            "allname": [self.output_names[i] for i in range(1, 9)],
        }

    async def get_input_status(self, force_refresh: bool = False) -> dict[str, Any]:
        return {
            "inactive": [1, 1, 0, 0, 1, 1, 0, 0],
            "edid": [1] * 8,
            "inname": [self.input_names[i] for i in range(1, 9)],
        }

    async def get_all_cable_status(self, force_refresh: bool = False) -> dict[str, Any]:
        return {
            "inputs": {i: (i in (1, 2, 5, 6)) for i in range(1, 9)},
            "outputs": {i: (i in (1, 2, 3, 6)) for i in range(1, 9)},
        }

    async def get_video_status(self) -> dict[str, Any]:
        return {
            "allsource": list(self.routes),
            "power": self.power_state,
            "allinputname": [self.input_names[i] for i in range(1, 9)],
            "alloutputname": [self.output_names[i] for i in range(1, 9)],
            "allname": [self.preset_names[i] for i in range(1, 9)],
        }

    async def get_cec_status(self) -> dict[str, Any]:
        return {"inputindex": [1] * 8, "outputindex": [1] * 8}

    async def get_system_status(self) -> dict[str, Any]:
        return {"power": self.power_state, "beep": 0, "lock": 0, "mode": 1}

    async def get_device_info(self) -> dict[str, Any]:
        return {
            "model": "BK-808",
            "version": "v1.0",
            "webversion": "v1.0",
            "hostname": self.host,
            "ipaddress": self.host,
            "macaddress": "00:11:22:33:44:55",
        }

    async def switch_input(self, input_num: int, output_num: int) -> bool:
        self.calls.append(("switch_input", input_num, output_num))
        self.routes[output_num - 1] = input_num
        return True

    async def switch_input_to_all(self, input_num: int) -> bool:
        self.calls.append(("switch_input_to_all", input_num))
        self.routes = [input_num] * 8
        return True

    async def recall_preset(self, preset: int) -> bool:
        self.calls.append(("recall_preset", preset))
        return True

    async def save_preset(self, preset: int) -> bool:
        self.calls.append(("save_preset", preset))
        return True

    async def power_on(self) -> bool:
        self.calls.append(("power_on",))
        self.power_state = 1
        return True

    async def power_off(self) -> bool:
        self.calls.append(("power_off",))
        self.power_state = 0
        return True

    async def send_cec(self, command: str, port: int, *, is_output: bool = False) -> bool:
        self.calls.append(("send_cec", command, port, is_output))
        return True

    async def set_input_name(self, port: int, name: str) -> bool:
        self.calls.append(("set_input_name", port, name))
        self.input_names[port] = name
        return True

    async def set_output_name(self, port: int, name: str) -> bool:
        self.calls.append(("set_output_name", port, name))
        self.output_names[port] = name
        return True


def _build_real_uc_runtime(
    tmp_path: Path,
    *,
    matrix_host: str = "",
) -> tuple[HubRuntime, UnfoldedCircleIntegration, list[_MatrixClientDouble], int]:
    api_port = _free_port()
    uc_port = _free_port()
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    env = {
        "DATA_DIR": str(data_dir),
        "UC_CONFIG_HOME": str(data_dir),
        "MATRIX_DATA_DIR": str(data_dir / "data"),
        "UC_ENABLED": "true",
        "MATRIX_HOST": matrix_host,
        "API_HOST": "127.0.0.1",
        "API_PORT": str(api_port),
        "UC_INTEGRATION_INTERFACE": "127.0.0.1",
        "UC_INTEGRATION_HTTP_PORT": str(uc_port),
        "UC_DISABLE_MDNS_PUBLISH": "true",
        "FLIC_ENABLED": "false",
        "HA_DISCOVERY_ENABLED": "false",
        "STATUS_POLL_INTERVAL": "60",
    }
    instances: list[_MatrixClientDouble] = []

    def _factory(*args: Any, **kwargs: Any) -> _MatrixClientDouble:
        client = _MatrixClientDouble(*args, **kwargs)
        instances.append(client)
        return client

    runtime = build_runtime(run.load_settings(env), environ=env, matrix_factory=_factory)
    runtime.loader.load()
    uc_integration = runtime.loader.integrations["unfolded_circle"]
    assert isinstance(uc_integration, UnfoldedCircleIntegration)
    uc_integration.bridge._probe_fn = AsyncMock(return_value=None)
    return runtime, uc_integration, instances, uc_port


async def _drain_runtime(runtime: HubRuntime, uc_integration: UnfoldedCircleIntegration) -> None:
    await runtime.bus.drain(timeout=1.0)
    while runtime.local._tasks or uc_integration.bridge._background_tasks:
        tasks = set(runtime.local._tasks) | set(uc_integration.bridge._background_tasks)
        await asyncio.wait_for(asyncio.gather(*tasks), 2.0)
        await asyncio.sleep(0)


def test_module_origins_resolve_to_this_worktree() -> None:
    root = Path(__file__).resolve().parents[1] / "src"
    origins = {
        "bridge": Path(uc_bridge_mod.__file__).resolve(),
        "handlers": Path(uc_handlers_mod.__file__).resolve(),
        "composition": Path(runtime_composition_mod.__file__).resolve(),
        "persistence_startup": Path(persistence_startup_mod.__file__).resolve(),
    }
    for name, mod_path in origins.items():
        print(f"MODULE_ORIGIN[{name}]={mod_path}")
        assert mod_path.is_relative_to(root), f"{name} loaded from outside worktree: {mod_path}"


async def test_unconfigured_runtime_event_order_attach_standby_and_setup_to_restart(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Real R2 + R1 + R3 composition proof: initial HubClientLocal snapshot events, catalog/refresh
    notifications, Remote connect/attach/standby/subscribe, and failed/rolled-back setup never expose
    entities before authorized setup completes; post-setup and restart expose all 74 golden entities."""
    runtime, uc_integration, instances, uc_port = _build_real_uc_runtime(tmp_path)
    config_file = tmp_path / "data" / "config_state.json"

    await runtime.start()
    try:
        await _drain_runtime(runtime, uc_integration)

        assert runtime.address is None
        assert instances == []
        assert uc_integration.entities == []
        assert uc_integration.projector.available_entities == {}
        assert uc_integration.projector.configured_entities == {}
        assert uc_integration.health()["entity_count"] == 0
        assert uc_integration.health()["configured_entity_count"] == 0
        assert uc_integration.health()["device_state"] == "DISCONNECTED"
        assert list(uc_integration.pushed_updates) == []
        assert not config_file.exists()

        async with UcRemoteSim(f"ws://127.0.0.1:{uc_port}") as remote:
            assert await remote.get_available_entities() == []
            assert await remote.get_entity_states() == []
            assert (await remote.get_device_state())["msg_data"]["state"] == "DISCONNECTED"

            # Remote attach/connect/subscribe while unconfigured must receive DISCONNECTED and 0 entities.
            attached = await remote.attach(["media_player.output_1", "switch.matrix_power"])
            assert attached == []
            assert remote.device_states()[-1] == "DISCONNECTED"
            assert await remote.get_available_entities() == []
            assert await remote.get_entity_states() == []

            # Bus events, catalog notifications, refresh, and standby wake while unconfigured stay empty.
            runtime.notify_catalog_changed()
            await runtime.refresh()
            runtime.bus.publish("names", {"inputs": {1: "Leak In"}, "outputs": {1: "Leak Out"}})
            runtime.bus.publish("presets", {"names": {1: "Leak Preset"}, "favorites": [1]})
            runtime.bus.publish("routing", {"output": 1, "input": 4})
            await _drain_runtime(runtime, uc_integration)

            await remote.enter_standby()
            await remote.exit_standby()
            await remote.send_connect()
            await asyncio.sleep(0.05)

            assert await remote.get_available_entities() == []
            assert await remote.get_entity_states() == []
            assert (await remote.get_device_state())["msg_data"]["state"] == "DISCONNECTED"
            assert list(uc_integration.pushed_updates) == []
            assert not config_file.exists()

            # Failed setup (auth error) keeps bridge unconfigured with 0 entities.
            step1_fail = await remote.setup_driver({"host": "auth-fail.local", "port": 443})
            assert step1_fail.state == "WAIT_USER_ACTION"
            step2_fail = await remote.set_driver_user_data(
                input_values={"user": "Admin", "password": "wrong-password"}
            )
            assert step2_fail.final == {"event_type": "STOP", "state": "ERROR", "error": "AUTHORIZATION_ERROR"}
            assert await remote.get_available_entities() == []
            assert await remote.get_entity_states() == []
            assert not config_file.exists()

            # Candidate connect that fails during config_state save rolls back and never leaks entities.
            real_atomic_write = _file_io.atomic_write_json

            def _boom_write(path: Path, payload: Any, **kwargs: Any) -> None:
                if Path(path).name == "config_state.json":
                    raise OSError("simulated disk full during setup save")
                real_atomic_write(path, payload, **kwargs)

            monkeypatch.setattr(_file_io, "atomic_write_json", _boom_write)
            step1_save_err = await remote.setup_driver({"host": "10.20.30.40", "port": 443})
            assert step1_save_err.state == "WAIT_USER_ACTION"
            step2_save_err = await remote.set_driver_user_data(
                input_values={"user": "Admin", "password": "candidate-secret"}
            )
            assert step2_save_err.state == "ERROR"
            await _drain_runtime(runtime, uc_integration)
            assert runtime.address is None
            assert await remote.get_available_entities() == []
            assert await remote.get_entity_states() == []
            assert (await remote.get_device_state())["msg_data"]["state"] == "DISCONNECTED"
            assert not config_file.exists()
            monkeypatch.setattr(_file_io, "atomic_write_json", real_atomic_write)

            # Now perform authorized setup and verify all 74 golden entities appear immediately.
            step1_ok = await remote.setup_driver({"host": "10.20.30.50", "port": 443})
            assert step1_ok.state == "WAIT_USER_ACTION"
            step2_ok = await remote.set_driver_user_data(
                input_values={"user": "Admin", "password": "matrix-password-123"}
            )
            assert step2_ok.final == {"event_type": "STOP", "state": "OK"}

            available = await remote.get_available_entities()
            assert len(available) == 74
            assert {e["entity_id"] for e in available} == APPROVED_GOLDEN_ENTITY_IDS
            assert (await remote.get_device_state())["msg_data"]["state"] == "CONNECTED"
            assert config_file.exists()
            saved = json.loads(config_file.read_text(encoding="utf-8"))
            assert saved["host"] == "10.20.30.50"
            assert saved["password"] == "matrix-password-123"
            assert saved["input_names"]["1"] == "Matrix In 1"

            # Subscribe and verify live state readback, command routing, and post-setup dynamic rename.
            await remote.subscribe_events(["media_player.output_1", "switch.matrix_power"])
            states = {s["entity_id"]: s["attributes"] for s in await remote.get_entity_states()}
            assert states["media_player.output_1"]["source"] == "Matrix In 1"
            assert states["switch.matrix_power"]["state"] == "ON"

            since = remote.mark()
            resp = await remote.select_source("media_player.output_1", "Matrix In 6")
            assert resp["code"] == 200
            assert instances[-1].routes[0] == 6
            await remote.wait_event(
                "entity_change",
                lambda d: d["entity_id"] == "media_player.output_1"
                and d["attributes"].get("source") == "Matrix In 6",
                since=since,
                timeout=3.0,
            )

            # Post-setup port rename updates entities and persists through runtime authority.
            since_rename = remote.mark()
            assert await runtime.matrix.set_input_name(6, "Gaming Rig")
            await _drain_runtime(runtime, uc_integration)
            await remote.wait_event(
                "entity_change",
                lambda d: d["entity_id"] == "media_player.output_1"
                and "Gaming Rig" in d["attributes"].get("source_list", []),
                since=since_rename,
                timeout=3.0,
            )
            saved_after_rename = json.loads(config_file.read_text(encoding="utf-8"))
            assert saved_after_rename["input_names"]["6"] == "Gaming Rig"
    finally:
        await runtime.stop()

    # Restart against the same DATA_DIR and verify immediate 74-entity restore without setup.
    runtime2, uc_integration2, instances2, uc_port2 = _build_real_uc_runtime(tmp_path)
    await runtime2.start()
    try:
        if runtime2._connect_task is not None:
            await runtime2._connect_task
        await _drain_runtime(runtime2, uc_integration2)

        assert runtime2.address is not None
        assert runtime2.address.host == "10.20.30.50"
        assert len(uc_integration2.entities) == 74
        async with UcRemoteSim(f"ws://127.0.0.1:{uc_port2}") as remote2:
            avail2 = await remote2.get_available_entities()
            assert len(avail2) == 74
            by_id2 = {e["entity_id"]: e for e in avail2}
            assert by_id2["remote.input_6_cec"]["name"] == {"en": "Gaming Rig CEC"}
            await remote2.subscribe_events(["media_player.output_1"])
            assert (await remote2.select_source("media_player.output_1", "Matrix In 3"))["code"] == 200
            assert instances2[-1].routes[0] == 3
    finally:
        await runtime2.stop()


async def test_configured_offline_startup_retains_74_unavailable_entities(tmp_path: Path) -> None:
    """Legitimate configured-offline startup (saved config_state.json with unreachable matrix)
    still publishes the 74-entity catalog with UNAVAILABLE state and rejects commands with 503."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "config_state.json").write_text(
        json.dumps(
            {
                "host": "offline.matrix.local",
                "port": 443,
                "telnet_port": 23,
                "input_names": {"1": "Saved Apple TV"},
                "output_names": {"1": "Saved Living Room"},
            }
        ),
        encoding="utf-8",
    )

    runtime, uc_integration, _instances, uc_port = _build_real_uc_runtime(tmp_path)
    await runtime.start()
    try:
        if runtime._connect_task is not None:
            await runtime._connect_task
        await _drain_runtime(runtime, uc_integration)

        assert len(uc_integration.entities) == 74
        async with UcRemoteSim(f"ws://127.0.0.1:{uc_port}") as remote:
            available = await remote.get_available_entities()
            assert len(available) == 74
            by_id = {e["entity_id"]: e for e in available}
            assert by_id["remote.input_1_cec"]["name"] == {"en": "Saved Apple TV CEC"}
            assert by_id["media_player.output_1"]["name"] == {"en": "Saved Living Room"}

            await remote.subscribe_events(["media_player.output_1", "switch.matrix_power"])
            states = {s["entity_id"]: s["attributes"] for s in await remote.get_entity_states()}
            assert states["media_player.output_1"]["state"] == "UNAVAILABLE"
            assert states["switch.matrix_power"]["state"] == "UNAVAILABLE"
            assert (await remote.select_source("media_player.output_1", "Saved Apple TV"))["code"] == 503
    finally:
        await runtime.stop()


async def test_real_hub_process_unconfigured_uc_bootstrap_setup_and_restart(tmp_path: Path) -> None:
    """Subprocess `HubProcess(mode='uc', uc_restore=False)` + `SimulatorProcess` + `UcRemoteSim`
    proof matching the installed/subprocess unconfigured startup -> setup -> control -> restart flow."""
    sim_proc = SimulatorProcess(log_dir=tmp_path / "sim")
    sim_proc.start()
    hub_proc = HubProcess(
        matrix_host=sim_proc.host,
        matrix_port=sim_proc.https_port,
        telnet_port=sim_proc.telnet_port,
        log_dir=tmp_path / "hub",
        mode="uc",
        uc_restore=False,
        polling_interval=1,
        stop_timeout=3,
        keep_data_on_restart=True,
        extra_env={"MATRIX_HOST": ""},
    )
    try:
        hub_proc.start()
        async with SimDevice(sim_proc.control_url) as sim:
            await sim.reset()
            async with UcRemoteSim(hub_proc.uc_url) as remote:
                assert await remote.attach() == []
                assert remote.device_states()[-1] == "DISCONNECTED"
                assert await remote.get_available_entities() == []
                assert await remote.get_entity_states() == []

                step1 = await remote.setup_driver(
                    {"host": sim_proc.host, "port": sim_proc.https_port}
                )
                assert step1.state == "WAIT_USER_ACTION"
                step2 = await remote.set_driver_user_data(
                    input_values={"user": "Admin", "password": "admin"}
                )
                assert step2.final == {"event_type": "STOP", "state": "OK"}

                available = await remote.get_available_entities()
                assert len(available) == 74
                assert {e["entity_id"] for e in available} == APPROVED_GOLDEN_ENTITY_IDS

                await remote.attach()
                resp = await remote.select_source("media_player.output_1", "PS5")
                assert resp["code"] == 200
                assert (await sim.state())["outputs"][0]["source"] == 6

            assert hub_proc.data_dir is not None
            saved_bytes = (hub_proc.data_dir / "config_state.json").read_bytes()
            saved_cfg = json.loads(saved_bytes)
            assert (saved_cfg["host"], saved_cfg["port"]) == (sim_proc.host, sim_proc.https_port)
            assert (saved_cfg["user"], saved_cfg["password"]) == ("Admin", "admin")

            await asyncio.to_thread(hub_proc.restart)
            async with UcRemoteSim(hub_proc.uc_url) as remote_after:
                avail_after = await remote_after.get_available_entities()
                assert len(avail_after) == 74
                await remote_after.attach(["media_player.output_1"])
                assert (await remote_after.get_device_state())["msg_data"]["state"] == "CONNECTED"
                resp2 = await remote_after.select_source("media_player.output_1", "Switch")
                assert resp2.get("code") == 200
                assert (await sim.state())["outputs"][0]["source"] == 4
            assert (hub_proc.data_dir / "config_state.json").read_bytes() == saved_bytes
    finally:
        hub_proc.stop()
        sim_proc.stop()


# =============================================================================
# Coordinated R4 seam tests for UCCommandDispatcher select_next / select_previous
# =============================================================================


class _R4CycleSeamHubDouble:
    """Explicit R4 seam double implementing `async cycle_input(direction, output_num=1, *, cycle=True) -> bool`
    and emitting authoritative `HubEvent('routing', ...)` updates without exposing a fallback switch path."""

    def __init__(
        self,
        *,
        initial_routing: dict[int, int] | None = None,
        clamp_refuses_at_boundary: bool = False,
    ) -> None:
        self.connected = True
        self.routing: dict[int, int] = dict(initial_routing or {i: i for i in range(1, 9)})
        self.clamp_refuses_at_boundary = clamp_refuses_at_boundary
        self.cycle_calls: list[tuple[str, int, bool]] = []
        self.switch = AsyncMock(return_value=True)
        self.next_result_override: Any = None
        self._subscribers: list[Any] = []

    def subscribe(self, callback: Any) -> Any:
        self._subscribers.append(callback)
        return lambda: self._subscribers.remove(callback) if callback in self._subscribers else None

    async def snapshot(self) -> HubSnapshot:
        return HubSnapshot(
            connected=self.connected,
            power=True,
            routing=dict(self.routing),
            input_names={i: f"Input {i}" for i in range(1, 9)},
            output_names={i: f"Output {i}" for i in range(1, 9)},
        )

    async def cycle_input(self, direction: str, output_num: int = 1, *, cycle: bool = True) -> Any:
        self.cycle_calls.append((direction, output_num, cycle))
        if self.next_result_override is not None:
            override, self.next_result_override = self.next_result_override, None
            if isinstance(override, Exception):
                raise override
            return override
        if not self.connected or output_num not in self.routing:
            return False
        current = self.routing[output_num]
        step = 1 if direction == "next" else -1
        nxt = current + step
        if cycle:
            target = ((nxt - 1) % 8) + 1
        else:
            if not (1 <= nxt <= 8) and self.clamp_refuses_at_boundary:
                return False
            target = max(1, min(8, nxt))
        self.routing[output_num] = target
        event = HubEvent("routing", {"routing": dict(self.routing)})
        for cb in list(self._subscribers):
            cb(event)
        return True


async def test_dispatcher_select_next_previous_delegates_to_r4_cycle_input_seam_wrap_and_clamp() -> None:
    """Explicit R4 seam test: `select_next` and `select_previous` delegate to
    `hub_client.cycle_input(direction, output_num, cycle=bool(params.get('cycle', True)))`,
    never call `switch`, and project from authoritative hub events rather than stale projector state."""
    hub = _R4CycleSeamHubDouble(initial_routing={1: 5, 2: 8, 3: 1})
    proj = EntityStateProjector()
    # Seed projector with intentionally stale route on output 1 (projector thinks 1, hub is at 5).
    proj.project_snapshot(
        {
            "connected": True,
            "power": 1,
            "routing": [1, 8, 1, 4, 5, 6, 7, 8],
            "input_names": {i: f"Input {i}" for i in range(1, 9)},
            "output_names": {i: f"Output {i}" for i in range(1, 9)},
        },
        force=True,
    )
    proj.subscribe_entities(["select.output_1_source", "select.output_2_source", "select.output_3_source"])

    emitted_diffs: list[dict[str, dict[str, Any]]] = []
    hub.subscribe(lambda ev: emitted_diffs.append(proj.apply_event(ev)))
    disp = UCCommandDispatcher(hub, proj, on_state_diff=emitted_diffs.append)

    # 1. Default wrap (params omitted -> cycle=True) uses authoritative hub route (5 -> 6, not stale 1 -> 2).
    code = await disp.dispatch("select.output_1_source", "select_next")
    assert code == 200
    assert hub.cycle_calls[-1] == ("next", 1, True)
    hub.switch.assert_not_awaited()
    assert proj.routed_inputs[1] == 6
    assert proj.projected_attributes("select.output_1_source")["current_option"] == "Input 6"
    # Exactly one diff emitted from authoritative hub event, no duplicate optimistic publish from dispatcher.
    non_empty = [d for d in emitted_diffs if d]
    assert len(non_empty) == 1
    assert non_empty[0]["select.output_1_source"] == {"current_option": "Input 6"}

    # 2. Wrap at upper boundary (8 -> 1) with explicit cycle=True.
    emitted_diffs.clear()
    assert await disp.dispatch("select.output_2_source", "select_next", {"cycle": True}) == 200
    assert hub.cycle_calls[-1] == ("next", 2, True)
    assert proj.routed_inputs[2] == 1
    assert [d for d in emitted_diffs if d] == [
        {
            "media_player.output_2": {"source": "Input 1"},
            "select.output_2_source": {"current_option": "Input 1"},
        }
    ]

    # 3. Wrap at lower boundary (1 -> 8) with default cycle=True.
    emitted_diffs.clear()
    assert await disp.dispatch("select.output_3_source", "select_previous") == 200
    assert hub.cycle_calls[-1] == ("previous", 3, True)
    assert proj.routed_inputs[3] == 8

    # 4. Clamp with cycle=False at boundaries (output 3 is at 8; select_next clamps at 8; output 2 is at 1; select_previous clamps at 1).
    emitted_diffs.clear()
    assert await disp.dispatch("select.output_3_source", "select_next", {"cycle": False}) == 200
    assert hub.cycle_calls[-1] == ("next", 3, False)
    assert proj.routed_inputs[3] == 8
    assert [d for d in emitted_diffs if d] == []

    assert await disp.dispatch("select.output_2_source", "select_previous", {"cycle": False}) == 200
    assert hub.cycle_calls[-1] == ("previous", 2, False)
    assert proj.routed_inputs[2] == 1
    assert [d for d in emitted_diffs if d] == []
    hub.switch.assert_not_awaited()


async def test_dispatcher_select_next_previous_refusal_and_status_codes() -> None:
    """Focused refusal and status-code coverage for `select_next` and `select_previous`."""
    hub = _R4CycleSeamHubDouble(
        initial_routing={1: 1, 8: 8},
        clamp_refuses_at_boundary=True,
    )
    proj = EntityStateProjector()
    proj.project_snapshot({"connected": True, "power": 1, "routing": [1, 2, 3, 4, 5, 6, 7, 8]}, force=True)
    disp = UCCommandDispatcher(hub, proj)

    # Boundary refusal when provider returns False -> 500
    assert await disp.dispatch("select.output_8_source", "select_next", {"cycle": False}) == 500
    assert hub.cycle_calls[-1] == ("next", 8, False)
    assert await disp.dispatch("select.output_1_source", "select_previous", {"cycle": False}) == 500
    assert hub.cycle_calls[-1] == ("previous", 1, False)

    # Structured error status mapping (400 / 503 / 500)
    hub.next_result_override = {"success": False, "status": 400, "error": "invalid cycle"}
    assert await disp.dispatch("select.output_1_source", "select_next", {"cycle": False}) == 400

    hub.next_result_override = {"success": False, "status": 503, "error": "matrix offline"}
    assert await disp.dispatch("select.output_1_source", "select_next") == 503

    hub.next_result_override = RuntimeError("transport failure")
    assert await disp.dispatch("select.output_1_source", "select_previous") == 500

    # Invalid output numbers rejected with 400 before calling cycle_input
    call_count_before = len(hub.cycle_calls)
    assert await disp.dispatch("select.output_0_source", "select_next") == 400
    assert await disp.dispatch("select.output_9_source", "select_previous") == 400
    assert await disp.dispatch("select.output_bad_source", "select_next") == 400
    assert len(hub.cycle_calls) == call_count_before

    # Disconnected state returns 503 without calling cycle_input
    proj.connected = False
    assert await disp.dispatch("select.output_1_source", "select_next") == 503
    assert len(hub.cycle_calls) == call_count_before
