"""UC dispatcher and registered REST share atomic cycles with real simulator I/O.

The installed SDK 0.7 catalog has no select entity. UC calls here reach the
actual dispatcher directly; this is not Remote WebSocket select support proof.
"""

from __future__ import annotations

import asyncio
import socket

import aiohttp
import pytest

import run
from hub.runtime.composition import build_runtime
from tools.simulator import DeviceState, Simulator


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture
async def shared_runtime(tmp_path):
    async with Simulator(DeviceState.default(), host="127.0.0.1", https_port=0,
                         telnet_port=0, control_port=0, tls=True) as sim:
        env = {
            "DATA_DIR": str(tmp_path), "UC_CONFIG_HOME": str(tmp_path),
            "API_PORT": str(free_port()), "MATRIX_HOST": "127.0.0.1",
            "MATRIX_PORT": str(sim.https_port), "OREI_TELNET_PORT": str(sim.telnet_port),
            "UC_ENABLED": "true", "FLIC_ENABLED": "false", "HA_DISCOVERY_ENABLED": "false",
            "UC_INTEGRATION_HTTP_PORT": str(free_port()),
            "UC_INTEGRATION_INTERFACE": "127.0.0.1", "UC_DISABLE_MDNS_PUBLISH": "true",
        }
        runtime = build_runtime(run.load_settings(env), environ=env)
        try:
            await runtime.start()
            await runtime._connect_task
            assert runtime.service.connected
            async with aiohttp.ClientSession(base_url=f"http://127.0.0.1:{env['API_PORT']}") as session:
                yield runtime, session, sim
        finally:
            await runtime.stop()


@pytest.mark.parametrize(
    "direction,boundary,cycle,targets",
    [
        ("next", 8, True, [1, 2]),
        ("previous", 1, True, [8, 7]),
        ("next", 8, False, [8, 8]),
        ("previous", 1, False, [1, 1]),
    ],
)
async def test_concurrent_dispatcher_rest_cycles_read_back_both_operations(
    shared_runtime, direction, boundary, cycle, targets,
):
    runtime, hub_api, sim = shared_runtime
    dispatcher = runtime.loader.integrations["unfolded_circle"].bridge.dispatcher
    response = await hub_api.post("/api/switch", json={"input": boundary, "output": 1})
    assert response.status == 200, await response.text()
    before = [output.source for output in sim.state.outputs]
    sim.log.clear()

    async def rest_cycle():
        response = await hub_api.post(
            f"/api/input/{direction}?output=1&cycle={str(cycle).lower()}"
        )
        assert response.status == 200, await response.text()
        return (await response.json())["data"]

    remote_result, rest_result = await asyncio.gather(
        dispatcher.dispatch("select.output_1_source", f"select_{direction}", {"cycle": cycle}),
        rest_cycle(),
    )
    assert remote_result == 200
    pairs = list(zip([boundary, *targets[:-1]], targets, strict=True))
    assert (rest_result["previous_input"], rest_result["current_input"]) in pairs
    assert rest_result["output"] == 1
    assert sim.state.outputs[0].source == targets[-1]
    assert [output.source for output in sim.state.outputs][1:] == before[1:]
    operations = [entry["payload"] for entry in sim.log if entry["command"] == "video switch"]
    assert [operation["source"] for operation in operations] == [[1, target] for target in targets]
    status = await hub_api.get("/api/status")
    assert status.status == 200
    assert (await status.json())["data"]["routing"]["1"] == targets[-1]
