"""R3E regression: WebSocket routing updates during initial UI load are not overwritten by stale REST status."""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import socket
import subprocess
from pathlib import Path

import aiohttp
import pytest

import hub.core.matrix_service as service_module
import hub.runtime.adapters as adapters
import hub.runtime.composition as composition
import orei_matrix
import rest_api.events as events_module
from hub.cli import export_env, load_settings
from tools.simulator import DeviceState, Simulator

CHECKOUT_ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def test_r3e_module_origins_are_from_child_checkout() -> None:
    for module in (composition, adapters, service_module, events_module, orei_matrix):
        origin = Path(module.__file__).resolve()
        assert origin.is_relative_to(CHECKOUT_ROOT), f"{module.__name__} loaded from {origin}, expected {CHECKOUT_ROOT}"
    for rel in ("web/js/state.js", "web/js/app.js", "tests/e2e/smoke.spec.ts"):
        path = (CHECKOUT_ROOT / rel).resolve()
        assert path.is_file() and path.is_relative_to(CHECKOUT_ROOT)


@pytest.mark.asyncio
@pytest.mark.skipif(not shutil.which("node"), reason="Actual frontend routing regression requires Node.js")
async def test_startup_ws_routing_change_not_overwritten_by_stale_initial_rest_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reproduce a deterministic feasible Test 3 -> sim.reset() -> Test 4 startup ordering using real runtime/simulator payloads and actual web/js/state.js + web/js/app.js (distinct from claiming exact event-timestamp attribution of the uninstrumented pinned CI run)."""
    import persistence
    import rest_api.utils as api_utils

    monkeypatch.setattr(api_utils, "_runtime", None)
    monkeypatch.setattr(persistence, "get_legacy_data_paths", lambda: [])

    seed_path = CHECKOUT_ROOT / "tools" / "simulator" / "states" / "default.json"
    seed = DeviceState.from_dict(json.loads(seed_path.read_text(encoding="utf-8")))
    sim = Simulator(seed, host="127.0.0.1", https_port=0, telnet_port=0, control_port=0)
    await sim.start()

    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(CHECKOUT_ROOT / "tests" / "e2e" / "fixtures" / "data", data_dir, dirs_exist_ok=True)

    api_port = _free_port()
    environ = {
        "DATA_DIR": str(data_dir),
        "MATRIX_DATA_DIR": str(data_dir),
        "UC_CONFIG_HOME": str(data_dir),
        "API_PORT": str(api_port),
        "MATRIX_HOST": "127.0.0.1",
        "MATRIX_PORT": str(sim.https_port),
        "OREI_TELNET_PORT": str(sim.telnet_port),
        "OREI_STATUS_CACHE_TTL": "0",
        "UC_ENABLED": "false",
        "FLIC_ENABLED": "false",
        "HA_DISCOVERY_ENABLED": "false",
    }
    for key, value in environ.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("OREI_USER", raising=False)
    monkeypatch.delenv("OREI_PASSWORD", raising=False)

    settings = load_settings(environ)
    export_env(settings, os.environ)
    runtime = composition.build_runtime(settings, environ=environ)
    base_url = f"http://127.0.0.1:{api_port}"

    try:
        await runtime.start()
        assert runtime._connect_task is not None
        await asyncio.wait_for(asyncio.shield(runtime._connect_task), timeout=15.0)

        async with aiohttp.ClientSession() as session:
            # 1. Prior smoke test routes output 1 -> input 3 via REST.
            async with session.post(f"{base_url}/api/output/1/source", json={"input": 3}) as resp:
                assert resp.status == 200
            assert sim.state.outputs[0].source == 3
            await runtime.refresh()
            assert runtime.snapshot().routing[1] == 3

            # 2. Hold runtime.transaction to deterministically capture the pre-refresh window after sim.reset()
            #    (matching the window in Test 4 where GET /api/info holds runtime.transaction while /api/status
            #    and initial /ws connect read the pre-refresh snapshot).
            async with runtime.transaction:
                async with session.put(f"{sim.control_url}/_sim/state", json=seed.to_dict()) as resp:
                    assert resp.status == 200
                async with session.delete(f"{sim.control_url}/_sim/faults") as resp:
                    assert resp.status == 200

                assert sim.state.outputs[0].source == 2
                assert runtime.snapshot().routing[1] == 3

                async with session.ws_connect(f"{base_url}/ws") as ws:
                    welcome = await ws.receive_json(timeout=2.0)
                    initial_ws = await ws.receive_json(timeout=2.0)
                    assert welcome["event"] == "connected"
                    assert initial_ws["event"] == "status"
                    assert initial_ws["data"]["routing"]["1"] == 3

                    async with session.get(f"{base_url}/api/status") as resp:
                        assert resp.status == 200
                        initial_rest = await resp.json()
                        assert initial_rest["data"]["routing"]["1"] == 3

                    async with session.get(f"{base_url}/api/status/inputs") as resp:
                        assert resp.status == 200
                        initial_inputs = await resp.json()

                    async with session.get(f"{base_url}/api/status/outputs") as resp:
                        assert resp.status == 200
                        initial_outputs = await resp.json()

                    # Warm-cache input/output status reads scheduled a background runtime refresh.
                    assert runtime._wake.is_set()

                    await runtime.refresh()
                    routing_change = None
                    while True:
                        frame = await ws.receive_json(timeout=3.0)
                        if frame.get("event") == "routing_change" and frame.get("data", {}).get("output") == 1:
                            routing_change = frame
                            break

                    assert routing_change is not None
                    assert routing_change["data"]["input"] == 2
                    assert routing_change["data"]["previous_input"] == 3
                    fresh_ws_snapshot = json.loads(json.dumps(runtime.server.app["event_stream"].status_snapshot()))
                    assert fresh_ws_snapshot is not None
                    assert fresh_ws_snapshot["routing"]["1"] == 2

                    # Subsequent unchanged poll emits no further routing_change.
                    observed_topics: list[str] = []
                    unsubscribe = runtime.bus.subscribe(lambda ev: observed_topics.append(ev.topic))
                    try:
                        await runtime.refresh()
                    finally:
                        unsubscribe()
                    assert "routing" not in observed_topics

                    # Simulate offline front-panel patch to input 7 and reconnect snapshot resync.
                    async with session.patch(
                        f"{sim.control_url}/_sim/state", json={"outputs": {"0": {"source": 7}}}
                    ) as resp:
                        assert resp.status == 200
                    await runtime.refresh()
                    reconnect_snapshot = json.loads(json.dumps(runtime.server.app["event_stream"].status_snapshot()))
                    assert reconnect_snapshot is not None
                    assert reconnect_snapshot["routing"]["1"] == 7
    finally:
        await runtime.stop()
        await sim.stop()

    captures = {
        "initial_ws": initial_ws,
        "initial_rest": initial_rest,
        "initial_inputs": initial_inputs,
        "initial_outputs": initial_outputs,
        "routing_change": routing_change,
        "fresh_ws_snapshot": fresh_ws_snapshot,
        "reconnect_snapshot": reconnect_snapshot,
    }
    captures_file = tmp_path / "captures.json"
    captures_file.write_text(json.dumps(captures), encoding="utf-8")

    node_script = """
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert/strict');

const root = process.argv[1];
const captures = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

function createHarness() {
  const context = vm.createContext({
    console,
    window: {},
    document: { addEventListener() {}, getElementById() { return null; } },
    localStorage: { getItem() { return null; }, setItem() {}, removeItem() {} },
    Logger: { state() {}, info() {}, api() {}, apiResponse() {}, log() {} },
    Constants: {},
    toast: { info() {}, success() {}, error() {} },
    setTimeout,
    clearTimeout,
  });
  for (const rel of ['web/js/state.js', 'web/js/app.js']) {
    const full = path.join(root, rel);
    vm.runInContext(fs.readFileSync(full, 'utf8'), context, { filename: rel });
  }
  context.state = context.window.state;
  context.captures = JSON.parse(JSON.stringify(captures));
  return context;
}

async function runScenario(mode) {
  const context = createHarness();
  context.mode = mode;
  return vm.runInContext(`(async () => {
    for (const name of [
      'loadProfiles', 'loadDeviceSettings', 'loadSystemShortcuts',
      'loadCecMacros', 'loadAllFavorites', 'loadDashboardLayout', 'loadDashboardPresets',
      'loadPhase8Scenes', 'loadSystemActions'
    ]) {
      state[name] = async () => [];
    }
    let releaseSlowRequest;
    let slowRequestStarted;
    const reachedSlowRequest = new Promise((resolve) => { slowRequestStarted = resolve; });
    const slowRequestGate = new Promise((resolve) => { releaseSlowRequest = resolve; });

    globalThis.api = {
      ensureAwake: async () => true,
      getInfo: () => { slowRequestStarted(); return slowRequestGate; },
      getStatus: async () => (
        mode === 'ws_retained_when_rest_unavailable' || mode === 'both_unavailable'
          ? null
          : captures.initial_rest
      ),
      getInputStatus: async () => captures.initial_inputs,
      getOutputStatus: async () => captures.initial_outputs,
    };

    const app = new MatrixApp();
    if (mode === 'ws_routing_change_during_load') {
      app.handleWebSocketMessage({ type: 'status', data: captures.initial_ws.data });
      const loading = app.loadInitialData();
      await reachedSlowRequest;
      app.handleWebSocketMessage({ type: 'routing_change', data: captures.routing_change.data });
      const afterWs = state.routing[1];
      releaseSlowRequest({ data: { model: 'BK-808', connected: true } });
      await loading;
      const afterRest = state.routing[1];
      const otherRoutePreserved = state.routing[5];
      const inputNamePreserved = state.inputs[2].name;
      app.handleWebSocketMessage({ type: 'status', data: captures.reconnect_snapshot });
      const afterReconnect = state.routing[1];
      return { afterWs, afterRest, otherRoutePreserved, inputNamePreserved, afterReconnect, dataLoaded: state.ui.dataLoaded };
    }

    if (mode === 'ws_status_during_load') {
      const loading = app.loadInitialData();
      await reachedSlowRequest;
      app.handleWebSocketMessage({ type: 'status', data: captures.fresh_ws_snapshot });
      const afterWs = state.routing[1];
      releaseSlowRequest({ data: { model: 'BK-808', connected: true } });
      await loading;
      const afterRest = state.routing[1];
      app.handleWebSocketMessage({ type: 'status', data: captures.reconnect_snapshot });
      const afterReconnect = state.routing[1];
      return { afterWs, afterRest, afterReconnect, dataLoaded: state.ui.dataLoaded };
    }

    if (mode === 'ws_outputs_alias_only') {
      const loading = app.loadInitialData();
      await reachedSlowRequest;
      app.handleWebSocketMessage({ type: 'status', data: { outputs: [2, 2, 1, 1, 5, 6, 1, 1] } });
      const afterWs = state.routing[1];
      releaseSlowRequest(null);
      await loading;
      const afterRest = state.routing[1];
      return { afterWs, afterRest, dataLoaded: state.ui.dataLoaded };
    }

    if (mode === 'rest_only_fallback') {
      const loading = app.loadInitialData();
      await reachedSlowRequest;
      releaseSlowRequest({ data: { model: 'BK-808', connected: true } });
      await loading;
      return {
        afterRest: state.routing[1],
        otherRoute: state.routing[5],
        model: state.info.model,
        statusLoaded: state.ui.statusLoaded,
        statusError: state.ui.statusError,
        dataLoaded: state.ui.dataLoaded,
      };
    }

    if (mode === 'ws_retained_when_rest_unavailable') {
      const loading = app.loadInitialData();
      await reachedSlowRequest;
      app.handleWebSocketMessage({ type: 'status', data: captures.fresh_ws_snapshot });
      releaseSlowRequest(null);
      await loading;
      return {
        afterRest: state.routing[1],
        statusLoaded: state.ui.statusLoaded,
        statusError: state.ui.statusError,
        dataLoaded: state.ui.dataLoaded,
      };
    }

    if (mode === 'both_unavailable') {
      const loading = app.loadInitialData();
      await reachedSlowRequest;
      releaseSlowRequest(null);
      await loading;
      return {
        statusLoaded: state.ui.statusLoaded,
        statusError: state.ui.statusError,
        dataLoaded: state.ui.dataLoaded,
      };
    }

    if (mode === 'manual_refresh_ws_during_load') {
      let releaseProfiles;
      let announceProfiles;
      const reachedProfiles = new Promise((resolve) => { announceProfiles = resolve; });
      const profilesGate = new Promise((resolve) => { releaseProfiles = resolve; });
      state.loadProfiles = () => { announceProfiles(); return profilesGate; };

      app.handleWebSocketMessage({ type: 'status', data: captures.initial_ws.data });
      const pendingRefresh = app.refresh();
      await reachedProfiles;
      app.handleWebSocketMessage({ type: 'routing_change', data: captures.routing_change.data });
      const afterWs = state.routing[1];
      releaseProfiles([]);
      await pendingRefresh;
      const afterRefresh = state.routing[1];
      const otherRoutePreserved = state.routing[5];
      return { afterWs, afterRefresh, otherRoutePreserved };
    }

    if (mode === 'overlapping_initial_and_keyboard_refresh') {
      const infoGates = [];
      let statusCallCount = 0;
      globalThis.api.getInfo = () => new Promise((resolve) => { infoGates.push(resolve); });
      globalThis.api.getStatus = async () => {
        statusCallCount += 1;
        if (statusCallCount === 6) {
          return { data: captures.reconnect_snapshot };
        }
        return captures.initial_rest;
      };

      app.handleWebSocketMessage({ type: 'status', data: captures.initial_ws.data });
      const load1 = app.loadInitialData();
      const load2 = app.loadInitialData();
      while (infoGates.length < 2) {
        await new Promise((resolve) => setTimeout(resolve, 0));
      }

      // First overlapping load completes while second (e.g. keyboard shortcut refresh) is still pending.
      infoGates[0]({ data: { model: 'BK-808', connected: true } });
      await load1;

      // WS routing_change arrives while second load is still in flight.
      app.handleWebSocketMessage({ type: 'routing_change', data: captures.routing_change.data });
      const afterWsDuringSecond = state.routing[1];

      infoGates[1]({ data: { model: 'BK-808', connected: true } });
      await load2;
      const afterSecondLoad = state.routing[1];

      // Reverse completion order when both overlapping loads started before the WS update:
      // load4 finishes first, then load3 finishes second; neither overwrites WS route 2.
      const load3 = app.loadInitialData();
      const load4 = app.loadInitialData();
      while (infoGates.length < 4) {
        await new Promise((resolve) => setTimeout(resolve, 0));
      }
      app.handleWebSocketMessage({ type: 'routing_change', data: captures.routing_change.data });
      infoGates[3]({ data: { model: 'BK-808', connected: true } });
      await load4;
      infoGates[2]({ data: { model: 'BK-808', connected: true } });
      await load3;
      const afterOutOfOrderLoads = state.routing[1];

      // Late REST fallback after a pre-existing WS update in an overlapping load + reverse completion:
      // load5 starts (stale REST 3), WS route 2 arrives (then WS is offline), load6 starts AFTER that WS
      // update and reads fresh REST 7 (statusCallCount === 6), load6 finishes first (-> 7), and load5
      // finishes later without overwriting 7.
      const load5 = app.loadInitialData();
      while (infoGates.length < 5) {
        await new Promise((resolve) => setTimeout(resolve, 0));
      }
      app.handleWebSocketMessage({ type: 'routing_change', data: captures.routing_change.data });
      const load6 = app.loadInitialData();
      while (infoGates.length < 6) {
        await new Promise((resolve) => setTimeout(resolve, 0));
      }
      infoGates[5]({ data: { model: 'BK-808', connected: true } });
      await load6;
      const afterLateRestFallback = state.routing[1];
      infoGates[4]({ data: { model: 'BK-808', connected: true } });
      await load5;
      const afterOlderLoadCompletes = state.routing[1];

      // Subsequent intentional refresh after all in-flight loads have settled applies fresh REST status.
      await app.refresh();
      const afterSubsequentRefresh = state.routing[1];

      return {
        afterWsDuringSecond,
        afterSecondLoad,
        afterOutOfOrderLoads,
        afterLateRestFallback,
        afterOlderLoadCompletes,
        afterSubsequentRefresh,
      };
    }

    if (mode === 'ws_during_ensure_awake_then_later_rest') {
      let releaseAwake;
      let awakeStarted;
      const reachedAwake = new Promise((resolve) => { awakeStarted = resolve; });
      const awakeGate = new Promise((resolve) => { releaseAwake = resolve; });

      globalThis.api.ensureAwake = () => { awakeStarted(); return awakeGate; };
      globalThis.api.getInfo = async () => ({ data: { model: 'BK-808', connected: true } });
      globalThis.api.getStatus = async () => ({ data: captures.reconnect_snapshot });

      app.handleWebSocketMessage({ type: 'status', data: captures.initial_ws.data });
      const loading = app.loadInitialData();
      await reachedAwake;

      // WS routing_change (to 2) arrives during ensureAwake, BEFORE api.getStatus() is issued.
      app.handleWebSocketMessage({ type: 'routing_change', data: captures.routing_change.data });
      const afterWsDuringAwake = state.routing[1];

      // Release ensureAwake; api.getStatus() now starts and returns genuinely later REST route 7.
      releaseAwake(true);
      await loading;
      const afterLaterRest = state.routing[1];
      return { afterWsDuringAwake, afterLaterRest };
    }
  })()`, context);
}

(async () => {
  const changeResult = await runScenario('ws_routing_change_during_load');
  const snapshotResult = await runScenario('ws_status_during_load');
  const aliasResult = await runScenario('ws_outputs_alias_only');
  const fallbackResult = await runScenario('rest_only_fallback');
  const unavailableResult = await runScenario('ws_retained_when_rest_unavailable');
  const bothUnavailableResult = await runScenario('both_unavailable');
  const manualRefreshResult = await runScenario('manual_refresh_ws_during_load');
  const overlappingResult = await runScenario('overlapping_initial_and_keyboard_refresh');
  const awakeBoundaryResult = await runScenario('ws_during_ensure_awake_then_later_rest');

  console.log(JSON.stringify({
    changeResult,
    snapshotResult,
    aliasResult,
    fallbackResult,
    unavailableResult,
    bothUnavailableResult,
    manualRefreshResult,
    overlappingResult,
    awakeBoundaryResult,
  }));

  assert.equal(changeResult.afterWs, 2);
  assert.equal(changeResult.afterRest, 2, 'stale initial REST status must not overwrite newer WS routing_change');
  assert.equal(changeResult.otherRoutePreserved, 5);
  assert.equal(changeResult.inputNamePreserved, 'AppleTV');
  assert.equal(changeResult.afterReconnect, 7);
  assert.equal(changeResult.dataLoaded, true);

  assert.equal(snapshotResult.afterWs, 2);
  assert.equal(snapshotResult.afterRest, 2, 'stale initial REST status must not overwrite newer WS status snapshot');
  assert.equal(snapshotResult.afterReconnect, 7);
  assert.equal(snapshotResult.dataLoaded, true);

  assert.equal(aliasResult.afterWs, 2);
  assert.equal(aliasResult.afterRest, 2, 'outputs array alias from WS status must not be overwritten by stale REST status');

  assert.equal(fallbackResult.afterRest, 3);
  assert.equal(fallbackResult.otherRoute, 5);
  assert.equal(fallbackResult.model, 'BK-808');
  assert.equal(fallbackResult.statusLoaded, true);
  assert.equal(fallbackResult.statusError, null);
  assert.equal(fallbackResult.dataLoaded, true);

  assert.equal(unavailableResult.afterRest, 2);
  assert.equal(unavailableResult.statusLoaded, true);
  assert.equal(unavailableResult.statusError, null);
  assert.equal(unavailableResult.dataLoaded, true);

  assert.equal(Boolean(bothUnavailableResult.statusLoaded), false);
  assert.equal(bothUnavailableResult.statusError, 'Matrix not reachable');
  assert.equal(bothUnavailableResult.dataLoaded, true);

  assert.equal(manualRefreshResult.afterWs, 2);
  assert.equal(manualRefreshResult.afterRefresh, 2, 'stale manual refresh REST status must not overwrite WS routing_change');
  assert.equal(manualRefreshResult.otherRoutePreserved, 5);

  assert.equal(overlappingResult.afterWsDuringSecond, 2);
  assert.equal(overlappingResult.afterSecondLoad, 2, 'overlapping loadInitialData calls must not clear active WS guard');
  assert.equal(overlappingResult.afterOutOfOrderLoads, 2, 'older overlapping loadInitialData must not overwrite newer WS route');
  assert.equal(overlappingResult.afterLateRestFallback, 7, 'load started after WS update must apply its later REST fallback');
  assert.equal(overlappingResult.afterOlderLoadCompletes, 7, 'older load completing after newer load must not overwrite newer REST status');
  assert.equal(overlappingResult.afterSubsequentRefresh, 3, 'subsequent intentional refresh after completion applies REST status');

  assert.equal(awakeBoundaryResult.afterWsDuringAwake, 2);
  assert.equal(awakeBoundaryResult.afterLaterRest, 7, 'WS update during ensureAwake must not override a getStatus request started after ensureAwake');
})().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
"""
    proc = subprocess.run(
        ["node", "-e", node_script, str(CHECKOUT_ROOT), str(captures_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
