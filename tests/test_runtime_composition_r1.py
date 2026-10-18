"""R1 composition with a structural R2 barrier and transport doubles.

These tests do not claim migration or UC server acceptance before R2/R3 merge.
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import aiohttp
import pytest
from pyee.asyncio import AsyncIOEventEmitter

import run
from hub.runtime.composition import build_runtime
from hub.runtime.config import MatrixAddress, resolve_matrix_address


class MatrixDouble:
    def __init__(self, host, *, port=443, telnet_port=None, user=None, password=None):
        self.host, self.port, self.telnet_port = host, port, telnet_port or 23
        self.user, self.password = user, password
        self.connected = False
        self.telnet_connected = False
        self.events = AsyncIOEventEmitter()
        self.login_failure = None
        self.connect_gate = None
        self.read_gate = None
        self.connect_entered = asyncio.Event()
        self.read_entered = asyncio.Event()
        self.calls = []
        self.routes = [1] * 8
        self.on = True
        self.owner = None

    async def connect(self):
        self.calls.append("connect")
        self.connect_entered.set()
        if self.connect_gate:
            await self.connect_gate.wait()
        if self.host == "refused":
            self.login_failure = "auth"
            return False
        self.connected = True
        if self.owner:
            self.owner.maximum = max(self.owner.maximum, sum(m.connected for m in self.owner.instances))
        return True

    async def disconnect(self):
        self.calls.append("disconnect")
        self.connected = False

    async def get_video_status(self):
        self.calls.append("video")
        self.read_entered.set()
        if self.read_gate:
            await self.read_gate.wait()
        return {
            "allsource": list(self.routes),
            "power": int(self.on),
            "allinputname": [f"IN{i}-Source {i}" for i in range(1, 9)],
            "alloutputname": [f"Display {i}" for i in range(1, 9)],
            "allname": ["Movie"] * 8,
        }

    async def get_input_status(self, force_refresh=False):
        return {"inactive": [1, None, 0, 0, 0, 0, 0, 0], "edid": [1] * 8}

    async def get_output_status(self, force_refresh=False):
        return {
            "allconnect": [1] * 8,
            "allout": [1] * 8,
            "allaudiomute": [0] * 8,
            "allhdcp": [2] * 8,
            "allhdr": [0] * 8,
            "allscaler": [0] * 8,
            "allarc": [0] * 8,
        }

    async def get_all_cable_status(self, force_refresh=False):
        return {"inputs": {1: True, 2: None}, "outputs": {1: False}}

    async def switch_input(self, input_num, output_num):
        self.calls.append(("switch", input_num, output_num))
        self.routes[output_num - 1] = input_num
        return True

    async def switch_input_to_all(self, input_num):
        self.routes = [input_num] * 8
        return True

    async def power_on(self):
        self.on = True
        return True

    async def power_off(self):
        self.on = False
        return True

    async def send_cec(self, command, port, *, is_output=False):
        self.calls.append(("cec", command, port, is_output))
        return True

    async def get_cec_status(self):
        return {"inputindex": [1] * 8, "outputindex": [0] * 8}

    async def get_system_status(self):
        return {"beep": 1, "lock": 0, "mode": 2}

    async def get_device_info(self):
        return {"version": "test", "model": "simulator"}


class MatrixFactory:
    def __init__(self):
        self.instances = []
        self.maximum = 0

    def __call__(self, *args, **kwargs):
        matrix = MatrixDouble(*args, **kwargs)
        matrix.owner = self
        self.instances.append(matrix)
        return matrix


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
def runtime_builder(tmp_path, monkeypatch):
    """Only the frozen R2 storage barrier is substituted; managers and REST are real."""
    barrier = ModuleType("hub.persistence.startup")
    preparations = []

    def prepare_runtime_storage(*, config_dir, data_dir):
        config_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)
        preparations.append((config_dir, data_dir))
        return SimpleNamespace(paths=SimpleNamespace(config_dir=config_dir, data_dir=data_dir), results=())

    barrier.prepare_runtime_storage = prepare_runtime_storage
    monkeypatch.setitem(sys.modules, "hub.persistence.startup", barrier)
    # The shared fixture predates runtime binding; keep the new global isolated here.
    monkeypatch.setattr("rest_api.utils._runtime", None)

    def make(**overrides):
        environ = {
            "DATA_DIR": str(tmp_path / "data"),
            "UC_CONFIG_HOME": str(tmp_path / "config"),
            "API_PORT": str(free_port()),
            "MATRIX_HOST": "simulator",
            "FLIC_ENABLED": "false",
            "STATUS_POLL_INTERVAL": "60",
            **overrides,
        }
        factory = MatrixFactory()
        runtime = build_runtime(run.load_settings(environ), environ=environ, matrix_factory=factory)
        return runtime, factory

    make.preparations = preparations
    return make


@pytest.mark.parametrize("uc", [False, True])
def test_address_precedence_and_address_bound_credentials(tmp_path, uc):
    (tmp_path / "config_state.json").write_text(
        json.dumps({"host": "saved", "port": 8443, "telnet_port": 2323, "user": "saved-user", "password": "private"})
    )
    settings = run.load_settings({"UC_ENABLED": str(uc), "UC_CONFIG_HOME": str(tmp_path), "MATRIX_HOST": "env"})
    address = resolve_matrix_address(settings)
    assert address.host == ("saved" if uc else "env")
    assert address.password == ("private" if uc else None)
    assert "private" not in repr(address)


async def test_unconfigured_uc_creates_no_transport(runtime_builder):
    runtime, factory = runtime_builder(UC_ENABLED="true", MATRIX_HOST="")
    assert runtime.address is None
    assert factory.instances == []
    assert runtime_builder.preparations[0][0] != runtime_builder.preparations[0][1]
    await runtime.stop()


async def test_health_precedes_slow_connect_and_one_refresh_owner(runtime_builder):
    runtime, factory = runtime_builder()
    matrix = factory.instances[0]
    matrix.connect_gate = asyncio.Event()
    try:
        await runtime.start()
        await matrix.connect_entered.wait()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://127.0.0.1:{runtime.settings.api_port}/api/health") as response:
                body = await response.json()
                assert response.status == 200
                assert body["data"]["matrix"]["connected"] is False
                assert body["data"]["integrations"] == {}
            for path in ("/ui", "/kiosk"):
                async with session.get(f"http://127.0.0.1:{runtime.settings.api_port}{path}") as response:
                    assert response.status == 200
        assert len(factory.instances) == 1
        assert len([t for t in asyncio.all_tasks() if t.get_name() == "hub_runtime_refresh"]) == 1
        assert not [t for t in asyncio.all_tasks() if t.get_name() == "hub_status_poller"]
    finally:
        await runtime.stop()
    assert not matrix.connected


async def test_managers_injected_once_and_package_wrapper_preserves_paths(runtime_builder, monkeypatch):
    runtime, _ = runtime_builder()
    import os

    from rest_api import create_rest_app, utils

    before = dict(os.environ)
    app = create_rest_app(runtime=runtime, integration_routes=[])
    assert dict(os.environ) == before
    assert utils.get_profile_manager() is runtime.managers.profiles
    assert utils.get_macro_manager() is runtime.managers.macros
    assert utils.get_action_runner() is runtime.action_runner
    assert utils.get_hub_client() is runtime.local
    assert app["hub_runtime"] is runtime
    await runtime.stop()


async def test_reconfigure_rolls_back_refusal_and_preserves_saved_bytes(runtime_builder):
    runtime, factory = runtime_builder()
    await runtime.connect()
    saved = runtime.prepared.paths.config_dir / "config_state.json"
    saved.write_text('{"host":"simulator","extension":{"kept":true}}')
    before = saved.read_bytes()
    facade = runtime.matrix
    result = await runtime.reconfigure(MatrixAddress("refused", password="secret"), persist=True)
    assert not result.success and result.error_kind == "auth" and result.connected
    assert saved.read_bytes() == before
    assert runtime.matrix is facade
    assert runtime.address.host == "simulator"
    assert factory.maximum == 1
    assert factory.instances[1].connected is False
    assert await facade.switch_input(3, 1)
    assert factory.instances[0].routes[0] == 3
    await runtime.stop()


async def test_repeated_concurrent_reconfigure_has_one_transport_and_refresh_task(runtime_builder):
    runtime, factory = runtime_builder()
    await runtime.start()
    await runtime._connect_task
    results = await asyncio.gather(
        *(runtime.reconfigure(MatrixAddress(f"sim-{i}", password="new-secret")) for i in range(4))
    )
    assert all(result.success for result in results)
    assert factory.maximum == 1
    assert sum(matrix.connected for matrix in factory.instances) == 1
    assert len([t for t in asyncio.all_tasks() if t.get_name() == "hub_runtime_refresh"]) == 1
    await runtime.stop()
    assert not any(matrix.connected for matrix in factory.instances)


async def test_save_failure_rolls_back_and_new_address_does_not_receive_old_secret(runtime_builder, monkeypatch):
    runtime, factory = runtime_builder()
    runtime.address = MatrixAddress("simulator", password="old-secret")
    await runtime.connect()

    def fail(*_):
        raise OSError("write failed")

    monkeypatch.setattr("_file_io.atomic_write_json", fail)
    result = await runtime.reconfigure(MatrixAddress("new-simulator", password="new-secret"), persist=True)
    assert not result.success and result.error_kind == "other"
    assert factory.instances[-1].password == "new-secret"
    assert runtime.address.password == "old-secret"
    assert factory.maximum == 1
    await runtime.stop()


async def test_new_target_requires_own_credentials_and_same_target_preserves_them(runtime_builder):
    runtime, factory = runtime_builder()
    runtime.address = MatrixAddress("simulator", telnet_port=2323, user="saved-user", password="saved-secret")
    await runtime.connect()
    rejected = await runtime.reconfigure(MatrixAddress("new-target"))
    assert not rejected.success and rejected.error_kind == "auth"
    assert len(factory.instances) == 1 and factory.instances[0].connected
    accepted = await runtime.reconfigure(MatrixAddress("simulator"))
    assert accepted.success
    assert factory.instances[-1].password == "saved-secret"
    assert factory.instances[-1].user == "saved-user"
    assert factory.instances[-1].telnet_port == 2323
    await runtime.stop()


def test_storage_failure_preserves_bytes_and_prevents_reader_construction(runtime_builder, monkeypatch, tmp_path):
    import hub.runtime.composition as composition
    from _process_lock import ProcessLock

    sentinel = tmp_path / "data" / "profiles.json"
    sentinel.parent.mkdir()
    sentinel.write_bytes(b'{"future_schema":999}')

    def fail(**kwargs):
        raise RuntimeError("unsafe schema at profiles.json")

    def unexpected(*args):
        raise AssertionError("manager read occurred before storage preparation")

    monkeypatch.setattr(sys.modules["hub.persistence.startup"], "prepare_runtime_storage", fail)
    monkeypatch.setattr(composition, "create_managers", unexpected)
    with pytest.raises(RuntimeError, match="unsafe schema"):
        runtime_builder(UC_ENABLED="true")
    assert sentinel.read_bytes() == b'{"future_schema":999}'
    lock = ProcessLock(tmp_path / "config" / "driver.lock")
    lock.acquire()
    lock.release()


@pytest.mark.parametrize("uc", [False, True])
async def test_real_run_entry_with_simulator_and_explicit_parallel_seams(tmp_path, uc):
    """Actual run.py subprocess, real transport/simulator; R2/R3 are explicitly structural.

    Full startup acceptance must rerun without sitecustomize after peer integration.
    The UC seam deliberately opens no UC listener and proves no UC protocol behavior.
    """
    from tools.simulator import Simulator

    root = Path(__file__).resolve().parents[1]
    seam = tmp_path / "seam"
    seam.mkdir()
    stop = tmp_path / "stop"
    (seam / "sitecustomize.py").write_text(
        """
import os, signal, sys, threading, time, types
from pathlib import Path
from types import SimpleNamespace
barrier = types.ModuleType("hub.persistence.startup")
def prepare_runtime_storage(*, config_dir, data_dir):
    config_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    return SimpleNamespace(paths=SimpleNamespace(config_dir=config_dir, data_dir=data_dir), results=())
barrier.prepare_runtime_storage = prepare_runtime_storage
sys.modules["hub.persistence.startup"] = barrier
if os.environ["UC_ENABLED"] == "true":
    bridge = types.ModuleType("hub.integrations.unfolded_circle")
    class StructuralBridge:
        name, env_flag = "unfolded_circle", "UC_ENABLED"
        def __init__(self, config): pass
        @classmethod
        def config_from_env(cls, environ): return None
        def bind_runtime(self, **kwargs): self.hooks = kwargs
        async def start(self, hub):
            assert "reconfigure" in self.hooks
            self.hub = hub
        async def stop(self): pass
        def routes(self): return []
        def health(self): return {"structural_test_double": True}
    bridge.UnfoldedCircleIntegration = StructuralBridge
    sys.modules["hub.integrations.unfolded_circle"] = bridge
def watch():
    while not Path(os.environ["R1_TEST_STOP"]).exists(): time.sleep(.02)
    signal.raise_signal(signal.SIGTERM)
threading.Thread(target=watch, daemon=True).start()
""",
        encoding="utf-8",
    )
    sim = Simulator(host="127.0.0.1", https_port=0, telnet_port=0, control_port=0)
    await sim.start()
    api_port = free_port()
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("UC_", "OREI_", "MATRIX_", "DATA_DIR", "API_PORT", "REST_API_PORT"))
    }
    env.update(
        UC_ENABLED="true" if uc else "false",
        FLIC_ENABLED="false",
        HA_DISCOVERY_ENABLED="false",
        DATA_DIR=str(tmp_path / "data"),
        MATRIX_HOST="127.0.0.1",
        MATRIX_PORT=str(sim.https_port),
        OREI_TELNET_PORT=str(sim.telnet_port),
        OREI_AUTO_RECONNECT="false",
        API_PORT=str(api_port),
        STATUS_POLL_INTERVAL="0.2",
        PYTHONPATH=os.pathsep.join([str(seam), str(root / "src"), str(root)]),
        R1_TEST_STOP=str(stop),
        PYTHONUNBUFFERED="1",
    )
    log_path = tmp_path / "entry.log"
    process = None
    try:
        with log_path.open("wb") as output:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "run.py", cwd=root, env=env, stdout=output, stderr=output
            )
            async with aiohttp.ClientSession() as session:
                deadline = asyncio.get_running_loop().time() + 20
                while True:
                    assert process.returncode is None, log_path.read_text(errors="replace")
                    try:
                        async with session.get(f"http://127.0.0.1:{api_port}/api/status") as response:
                            body = await response.json()
                            if response.status == 200 and body["data"].get("routing"):
                                break
                    except aiohttp.ClientError:
                        pass
                    assert asyncio.get_running_loop().time() < deadline, log_path.read_text(errors="replace")
                    await asyncio.sleep(0.05)
                sim.state.outputs[0].source = 7
                while True:
                    async with session.get(f"http://127.0.0.1:{api_port}/api/status") as response:
                        body = await response.json()
                        if body.get("data", {}).get("routing", {}).get("1") == 7:
                            break
                    assert asyncio.get_running_loop().time() < deadline
                    await asyncio.sleep(0.05)
            stop.touch()
            assert await asyncio.wait_for(process.wait(), 12) == 0, log_path.read_text(errors="replace")
        assert "ucapi imported: False" in log_path.read_text(errors="replace")
        assert "driver.py" not in log_path.read_text(errors="replace")
    finally:
        if process is not None and process.returncode is None:
            process.kill()
            await process.wait()
        await sim.stop()
