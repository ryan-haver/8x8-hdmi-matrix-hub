"""Real runtime capture and subprocess listener readiness regressions (R1D).

Only disposable storage and simulator sockets are used. Capture uses the real
composition, transport, managers and REST listener; barriers wrap real reads to
prove transaction/cancellation behavior without sleeps or substitute clients.
"""

from __future__ import annotations

import asyncio
import json
import socket
from contextlib import contextmanager
from pathlib import Path

import aiohttp
import pytest

from hub.cli import load_settings
from hub.runtime.composition import build_runtime
from hub.runtime.config import MatrixAddress
from rest_api.scenes import _capture_current_outputs
from tools.validate.device import SimDevice
from tools.validate.stack import HubProcess, SimulatorProcess, free_port, port_open


@contextmanager
def _exclusive_listener():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        listener.bind(("0.0.0.0", 0))
        listener.listen()
        yield listener.getsockname()[1]


@pytest.mark.parametrize("conflict", ["api", "uc"])
def test_explicit_occupied_listener_fails_without_moving_other_auto_port(tmp_path, conflict):
    with _exclusive_listener() as occupied:
        hub = HubProcess(
            matrix_host="127.0.0.1", matrix_port=free_port(), telnet_port=free_port(),
            log_dir=tmp_path, mode="uc", uc_restore=False,
            api_port=occupied if conflict == "api" else 0,
            uc_port=occupied if conflict == "uc" else 0,
            matrix_password="r1d-bind-secret", extra_env={"MATRIX_HOST": ""},
        )
        try:
            hub.launch()
            with pytest.raises(RuntimeError) as failure:
                hub.wait_ready(timeout=10)
            assert hub._proc.wait(timeout=10) != 0
            assert hub.starts == 1
            assert (hub.api_port if conflict == "api" else hub.uc_port) == occupied
            assert "r1d-bind-secret" not in str(failure.value)
            assert "UCBridge started" not in hub.log_tail(200)
            if conflict == "uc":
                # Startup rollback closes HTTP even though it was healthy first.
                assert not port_open(hub.host, hub.api_port)
                assert "REST API server started" in hub.log_tail(200)
            assert port_open("127.0.0.1", occupied)  # the other owner remains alive
        finally:
            hub.stop()


def test_uc_readiness_requires_this_childs_completed_bind(tmp_path):
    """Another accepting socket cannot satisfy either readiness path."""
    with _exclusive_listener() as occupied:
        hub = HubProcess(
            matrix_host="127.0.0.1", matrix_port=free_port(), telnet_port=free_port(),
            log_dir=tmp_path, mode="uc", uc_restore=False, uc_port=occupied,
            extra_env={"MATRIX_HOST": ""},
        )
        try:
            hub.launch()
            # Wait only for HTTP, deliberately at the dangerous startup boundary.
            from tools.dev_stack import _wait_for

            try:
                _wait_for(f"{hub.base_url}/api/health", hub._proc, 10, "hub")
            except RuntimeError:
                pass  # Fast rollback may close HTTP before the first observation.
            try:
                assert hub.ready() is False
            except RuntimeError:
                assert hub.returncode is not None
            with pytest.raises(RuntimeError):
                hub.wait_ready(timeout=10)
            assert hub.starts == 1
        finally:
            hub.stop()


@pytest.fixture(scope="module")
def capture_simulator(tmp_path_factory):
    simulator = SimulatorProcess(log_dir=tmp_path_factory.mktemp("r1d-capture-sim"))
    simulator.start()
    try:
        yield simulator
    finally:
        simulator.stop()


@pytest.fixture
async def capture_runtime(capture_simulator, tmp_path, monkeypatch):
    sim = capture_simulator
    environ = {
        "DATA_DIR": str(tmp_path / "data"), "UC_CONFIG_HOME": str(tmp_path / "config"),
        "API_PORT": str(free_port()), "MATRIX_HOST": "127.0.0.1", "MATRIX_PORT": str(sim.https_port),
        "OREI_TELNET_PORT": str(sim.telnet_port), "OREI_VERIFY_SSL": "false",
        "OREI_STATUS_CACHE_TTL": "3600", "STATUS_POLL_INTERVAL": "3600",
        "UC_ENABLED": "false", "FLIC_ENABLED": "false", "HA_DISCOVERY_ENABLED": "false",
    }
    for key, value in environ.items():
        monkeypatch.setenv(key, value)
    runtime = build_runtime(load_settings(environ), environ=environ)
    async with SimDevice(sim.control_url) as dev:
        await dev.reset()
        try:
            await runtime.start()
            await asyncio.wait_for(asyncio.shield(runtime._connect_task), 15)
            # Settle startup event-triggered refreshes, then keep the sole worker
            # gated until the test explicitly exercises it.
            await runtime.refresh()
            assert runtime.service.connected
            assert runtime.service.raw_snapshot()["outputs"]
            yield runtime, dev
        finally:
            await dev.clear_faults()
            await runtime.stop()


async def _capture(runtime, profile_id="r1d_capture"):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://127.0.0.1:{runtime.settings.api_port}/api/scene/save-current", json={"id": profile_id}
        ) as response:
            return response.status, await response.json()


async def test_capture_observes_out_of_band_changes_inside_nonzero_cache_ttl(capture_runtime):
    runtime, dev = capture_runtime
    cached_output = await runtime.matrix.get_output_status()
    assert runtime.service.client._status_cache_ttl == 3600
    routes = [8, 7, 6, 5, 4, 3, 2, 1]
    await dev.patch_state({"outputs": {
        str(index): {"source": source, "stream": index % 2, "audio_mute": 1, "hdr": 2, "hdcp": 2}
        for index, source in enumerate(routes)
    }})
    before = await dev.state()
    await dev.clear_log()
    status, result = await _capture(runtime)
    assert status == 200, result
    outputs = result["data"]["outputs"]
    assert [outputs[str(port)]["input"] for port in range(1, 9)] == routes
    assert [outputs[str(port)]["enabled"] for port in range(1, 9)] == [bool(i % 2) for i in range(8)]
    assert all(value["audio_mute"] and value["hdr_mode"] == 3 and value["hdcp_mode"] == 2
               for value in outputs.values())
    # The capture read doesn't replace ordinary cached facade semantics.
    assert await runtime.matrix.get_output_status() == cached_output
    commands = [entry["command"] for entry in await dev.log() if entry["channel"] == "http"]
    assert commands == ["get output status", "get video status"]
    assert await dev.state() == before
    saved = json.loads((runtime.prepared.paths.config_dir / "profiles.json").read_text(encoding="utf-8"))
    assert next(row for row in saved["profiles"] if row["id"] == "r1d_capture")["outputs"] == outputs


@pytest.mark.parametrize("comhead", ["get output status", "get video status"])
async def test_capture_failure_never_uses_last_good_snapshot(capture_runtime, comhead):
    runtime, dev = capture_runtime
    before = await dev.state()
    path = runtime.prepared.paths.config_dir / "profiles.json"
    saved_before = path.read_bytes() if path.exists() else None
    await dev.set_faults({"http_status": 500, "comheads": [comhead]})
    await dev.clear_log()
    status, result = await _capture(runtime)
    assert status == 502, result
    assert result["success"] is False
    assert "profile not saved" in result["error"]
    assert runtime.managers.profiles.get_profile("r1d_capture") is None
    assert (path.read_bytes() if path.exists() else None) == saved_before
    assert any(entry["command"] == comhead and entry.get("fault") for entry in await dev.log())
    assert await dev.state() == before


@pytest.mark.parametrize("fault", [False, True])
async def test_standalone_real_transport_capture_bypasses_nonzero_output_ttl(capture_runtime, fault):
    runtime, dev = capture_runtime
    transport = runtime.service.client
    old_outputs = await transport.get_output_status()
    await dev.patch_state({"outputs": {"0": {"source": 8, "stream": 0, "audio_mute": 1}}})
    assert await transport.get_output_status() == old_outputs  # a live cache
    if fault:
        await dev.set_faults({"http_status": 500, "comheads": ["get output status"]})
    await dev.clear_log()
    outputs, error = await _capture_current_outputs(transport)
    if fault:
        assert outputs is None
        assert error == "the output status read failed"
    else:
        assert error is None
        assert outputs[1]["input"] == 8
        assert outputs[1]["enabled"] is False
        assert outputs[1]["audio_mute"] is True
    assert any(entry["command"] == "get output status" for entry in await dev.log())


@pytest.mark.parametrize("change", ["write", "reconfigure"])
async def test_capture_pair_serializes_changes_and_uses_one_transport(capture_runtime, monkeypatch, change):
    runtime, dev = capture_runtime
    client = runtime.service.client
    original = client.get_output_status
    entered, release, mutation_entered = asyncio.Event(), asyncio.Event(), asyncio.Event()

    async def held_read(*args, **kwargs):
        value = await original(*args, **kwargs)
        entered.set()
        await release.wait()
        return value

    monkeypatch.setattr(client, "get_output_status", held_read)
    capture = asyncio.create_task(runtime.matrix.capture_current_status())
    await asyncio.wait_for(entered.wait(), 5)

    async def mutate():
        mutation_entered.set()
        if change == "write":
            return await runtime.matrix.switch_input(8, 1)
        return await runtime.reconfigure(MatrixAddress(client.host, client.port, client.telnet_port))

    mutation = asyncio.create_task(mutate())
    try:
        await asyncio.wait_for(mutation_entered.wait(), 5)
        assert not mutation.done()
        assert runtime.service.client is client
        old_source = (await dev.state())["outputs"][0]["source"]
        release.set()
        _, video = await asyncio.wait_for(capture, 5)
        assert video["allsource"][0] == old_source
        changed = await asyncio.wait_for(mutation, 10)
        if change == "write":
            assert changed is True
            assert (await dev.state())["outputs"][0]["source"] == 8
            assert runtime.service.client is client
        else:
            assert changed.success is True
            assert runtime.service.client is not client
            assert not client.connected
    finally:
        release.set()
        await asyncio.gather(capture, mutation, return_exceptions=True)


async def test_cancelled_capture_propagates_and_releases_transaction(capture_runtime, monkeypatch):
    runtime, _ = capture_runtime
    client = runtime.service.client
    original = client.get_output_status
    entered = asyncio.Event()

    async def held_read(*args, **kwargs):
        await original(*args, **kwargs)
        entered.set()
        await asyncio.Event().wait()

    monkeypatch.setattr(client, "get_output_status", held_read)
    capture = asyncio.create_task(runtime.matrix.capture_current_status())
    try:
        await asyncio.wait_for(entered.wait(), 5)
        capture.cancel()
        with pytest.raises(asyncio.CancelledError):
            await capture
        assert runtime.managers.profiles.get_profile("r1d_capture") is None
        monkeypatch.setattr(client, "get_output_status", original)
        outputs, video = await asyncio.wait_for(runtime.matrix.capture_current_status(), 5)
        assert outputs["allout"] and video["allsource"]
    finally:
        capture.cancel()
        await asyncio.gather(capture, return_exceptions=True)


async def test_matrix_readiness_wait_uses_health_without_protocol_reads(capture_runtime, tmp_path):
    runtime, dev = capture_runtime
    hub = HubProcess(
        matrix_host="127.0.0.1", matrix_port=runtime.address.port, telnet_port=runtime.address.telnet_port,
        log_dir=tmp_path, external_url=f"http://127.0.0.1:{runtime.settings.api_port}",
    )
    before = await dev.log()
    health = await asyncio.to_thread(hub.wait_matrix_ready, 5)
    assert health["matrix"]["connected"] is True
    assert health["matrix"]["telnet_connected"] is True
    assert health["matrix"]["last_successful_poll"]
    assert await dev.log() == before
    assert hub.starts == 0


@pytest.mark.parametrize("mode", ["api", "uc"])
def test_real_source_process_sigterm_cleans_listeners_and_records_origins(capture_simulator, tmp_path, mode):
    """The test hook triggers SIGTERM; composition/transport/SDK are unmodified."""
    sim = capture_simulator
    hook = Path(__file__).resolve().parents[1] / "fixtures/runtime_installed_r1p/shutdown_control.py"
    (tmp_path / "sitecustomize.py").write_bytes(hook.read_bytes())
    stop, result = tmp_path / "stop", tmp_path / "origins.json"
    hub = HubProcess(
        matrix_host=sim.host, matrix_port=sim.https_port, telnet_port=sim.telnet_port,
        log_dir=tmp_path / "hub", mode=mode,
        extra_env={
            "R1P_STOP": str(stop), "R1P_RESULT": str(result),
            # Only inject the shutdown hook. The normal source entry must
            # locate its own modules without any inherited PYTHONPATH.
            "PYTHONPATH": str(tmp_path),
        },
    )
    try:
        hub.start()
        hub.wait_matrix_ready()
        stop.touch()
        assert hub._proc.wait(timeout=15) == 0, hub.log_tail(100)
        assert not port_open(hub.host, hub.api_port)
        if mode == "uc":
            assert not port_open(hub.host, hub.uc_port)
        origins = json.loads(result.read_text(encoding="utf-8"))
        source = Path(__file__).resolve().parents[2] / "src"
        assert Path(origins["hub.cli"]).is_relative_to(source)
        assert Path(origins["hub.runtime.composition"]).is_relative_to(source)
        assert "driver" not in origins
        assert ("hub.integrations.unfolded_circle.bridge" in origins) == (mode == "uc")
        log = hub.log_tail(200)
        assert "Unclosed client session" not in log
        assert "Task was destroyed" not in log
        assert "never retrieved" not in log
    finally:
        hub.stop()
