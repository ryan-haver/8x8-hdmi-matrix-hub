"""Run scenarios against the simulator or a real matrix and write evidence records.

One run = one target (``sim`` | ``hardware``) x one or more clients. For every
scenario the runner prepares the device, performs the action through the
client, observes everything that happened (HTTP exchange, device state before
and after, simulator command log, WebSocket events, screenshots, operator
answers) and evaluates the scenario's expectations. Nothing is inferred from a
2xx: effects are read back from the device.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import json
import platform
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import aiohttp

from . import gitinfo
from .clients import CLIENTS, ActionResult, ApiClient, Client, HubInfo, NotSupportedError, make_client
from .device import RESTORABLE_DOMAINS, HardwareDevice, SimDevice
from .evidence import SCHEMA_VERSION, record_stem, redact, write_record
from .model import (
    RUNNER_INTENTS,
    Action,
    ClientState,
    CommandGap,
    CommandSent,
    Device,
    DeviceUnchanged,
    Expectation,
    Hub,
    NoCommand,
    NoProtocolWarnings,
    NoWsEvent,
    PresetCatalog,
    PresetRouting,
    Response,
    Scenario,
    WsEvent,
    diff_states,
    level_for,
    path_matches,
    resolve,
)
from .registry import Finding
from .stack import HubProcess, SimStack

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "build" / "validation"
#: The /ws message contract every recorded WebSocket message is checked against (WP-C2).
WS_SCHEMA = ROOT / "docs" / "api" / "websocket.schema.json"


def ws_contract_check(events: list[dict[str, Any]]) -> dict[str, Any]:
    """One check: every message the /ws observer received follows docs/api/websocket.schema.json."""
    description = "every WebSocket message follows docs/api/websocket.schema.json"
    try:
        import jsonschema
    except ImportError:
        return {"description": description, "result": "n/a", "detail": "jsonschema is not installed",
                "finding": None, "linked_finding": None, "note": None}
    validator = jsonschema.Draft202012Validator(json.loads(WS_SCHEMA.read_text(encoding="utf-8")))
    bad = []
    for e in events:
        message = {"event": e.get("event"), "data": e.get("data")}
        errors = sorted(validator.iter_errors(message), key=str)
        if errors:
            bad.append(f"{e.get('event')}: {errors[0].message[:200]}")
    return {"description": description, "result": "fail" if bad else "pass",
            "detail": "; ".join(bad[:5]) if bad else f"{len(events)} message(s) checked",
            "finding": None, "linked_finding": None, "note": None}

#: Device paths that change on their own on real hardware (signal, hot-plug).
VOLATILE_PATHS = ("inputs[*].signal", "inputs[*].cable", "outputs[*].connected")


def _now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def compare_preset_catalog(hub_presets: list[dict[str, Any]],
                           device_slots: dict[int, list[int] | None]) -> list[dict[str, Any]]:
    """Slots where ``GET /api/presets`` disagrees with the device's own slot (``PresetCatalog``)."""
    by_number = {p.get("number"): p for p in hub_presets if isinstance(p, dict)}
    problems: list[dict[str, Any]] = []
    for n in range(1, 9):
        entry = by_number.get(n)
        if entry is None:
            problems.append({"slot": n, "problem": "missing from the hub's catalog"})
            continue
        stored = device_slots.get(n)
        expected = {} if stored is None else {str(o): i for o, i in enumerate(stored, start=1)}
        reported = {str(k): v for k, v in (entry.get("routing") or {}).items()}
        if entry.get("routing_source") != "matrix" or reported != expected:
            problems.append({"slot": n, "routing_source": entry.get("routing_source"),
                             "hub": reported, "device": expected})
    return problems


def preset_routing_verdict(before: list[Any] | None, after: list[Any] | None,
                           slot: list[int] | None) -> tuple[str, str]:
    """``PresetRouting``: the routing after a recall against the slot the device stores."""
    if slot is None:
        return "fail", "the slot is empty on the device"
    if before == slot:
        return "fail", ("inconclusive: the live routing already equalled the slot before the recall; "
                        "route something else first")
    if after == slot:
        return "pass", f"routing = the slot's stored routing {slot}"
    return "fail", f"routing = {after}, the slot stores {slot}"


def _subset(expected: Any, actual: Any) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(k in actual and _subset(v, actual[k]) for k, v in expected.items())
    return bool(expected == actual)


def _is_read(entry: dict[str, Any]) -> bool:
    cmd = str(entry.get("command", ""))
    return cmd.startswith(("get ", "preset get", "r ")) or cmd == "status"


def compact_log(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Command log excerpt for the record: every write/CEC command in full; plain reads
    (which a page load issues by the dozen) without their payload and response, unless
    they carried a fault or warning."""
    out = []
    for e in entries:
        if _is_read(e) and not e.get("fault") and not e.get("warnings"):
            out.append({k: e[k] for k in ("t", "channel", "command", "recognised") if k in e})
        else:
            out.append(e)
    return out


def simulator_fingerprint() -> dict[str, Any]:
    """Identify the simulator build: hash of its source and seed state (it has no version number)."""
    h = hashlib.sha256()
    sim_dir = ROOT / "tools" / "simulator"
    for p in sorted(sim_dir.rglob("*")):
        if p.is_file() and p.suffix in (".py", ".json"):
            h.update(p.relative_to(sim_dir).as_posix().encode())
            h.update(p.read_bytes())
    return {"source_sha256": h.hexdigest()[:16], "seed_state": "tools/simulator/states/default.json"}


# --------------------------------------------------------------------------- options / results


@dataclass
class RunOptions:
    target: str = "sim"
    clients: tuple[str, ...] = ("api",)
    out_dir: Path = DEFAULT_OUT
    #: where evidence records go (default ``<out_dir>/evidence``; ``--record``
    #: writes straight into ``docs/validation/evidence`` for a milestone commit)
    evidence_dir: Path | None = None
    operator: str = "automation"
    # hardware
    matrix_host: str | None = None
    matrix_port: int = 443
    matrix_https: bool = True
    matrix_user: str = "Admin"
    matrix_password: str = "admin"
    telnet_port: int = 23
    hub_url: str | None = None
    #: Existing disposable simulator + shipped hub image (V3); never a hardware URL.
    sim_control_url: str | None = None
    hub_image_digest: str | None = None
    allow_writes: bool = False
    allow_unrestorable: bool = False
    answers: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    interactive: bool = False
    findings: dict[str, Finding] = field(default_factory=dict)


@dataclass
class Outcome:
    scenario: str
    client: str
    status: str  # pass | fail | blocked | skipped
    level: str | None = None
    features: list[str] = field(default_factory=list)
    failed_checks: list[dict[str, Any]] = field(default_factory=list)
    gate: str = "ok"  # ok | known-failure | regression | skipped
    reason: str = ""
    record: str | None = None


# --------------------------------------------------------------------------- WebSocket observer


class WsObserver:
    """A plain WebSocket client on the hub's /ws that records every event.

    Event times (``e["t"]``) come from :meth:`now`, a high-resolution monotonic clock: the wall clock
    ticks only every ~15.6 ms on Windows, so an event received just before a mark could carry the same
    time and count as after it (TST-15). Take marks with ``ws.now()``.
    """

    @staticmethod
    def now() -> float:
        return time.perf_counter()

    def __init__(self, url: str, forwarded_for: str) -> None:
        self.url = url
        self.forwarded_for = forwarded_for
        self.events: list[dict[str, Any]] = []
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._task: asyncio.Task[None] | None = None
        self._session: aiohttp.ClientSession | None = None
        self.error: str | None = None

    async def start(self) -> None:
        self._session = aiohttp.ClientSession(headers={"X-Forwarded-For": self.forwarded_for})
        connected = asyncio.get_running_loop().create_future()

        async def pump() -> None:
            assert self._session is not None
            try:
                async with self._session.ws_connect(self.url, heartbeat=None) as ws:
                    self._ws = ws
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                data = json.loads(msg.data)
                            except ValueError:
                                continue
                            self.events.append({"t": self.now(), "event": data.get("event"), "data": data.get("data")})
                            if not connected.done():
                                connected.set_result(True)
            except (aiohttp.ClientError, OSError) as exc:
                self.error = f"{type(exc).__name__}: {exc}"
            finally:
                if not connected.done():
                    connected.set_result(False)

        self._task = asyncio.create_task(pump())
        try:
            await asyncio.wait_for(connected, 5)
        except TimeoutError:
            self.error = "no welcome message within 5 s"

    async def sync(self, timeout: float = 15.0) -> bool:
        """Ask the hub for a fresh read (``get_status``) and wait for its answer.

        The runner resets the simulator behind the hub's back before each scenario. Until the hub has read
        the matrix again, the changes the reset made would be announced during the scenario (docs/api/
        WEBSOCKET.md: the hub announces what it notices). After this, they have been announced before it.
        """
        if self._ws is None or self._ws.closed:
            return False
        # The snapshot sent after `connected` must not be taken for the answer: let it arrive first.
        settle = time.monotonic() + 3
        while not any(e["event"] == "status" for e in self.events) and time.monotonic() < settle:
            await asyncio.sleep(0.05)
        # Only events received after the request count: ordered by position in the list, not by time.
        mark = len(self.events)
        await self._ws.send_json({"command": "get_status"})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            answers = [e["event"] for e in self.events[mark:] if e["event"] in ("status", "error")]
            if answers:
                return answers[0] == "status"
            await asyncio.sleep(0.05)
        return False

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001 - shutting down
                pass
        if self._session:
            await self._session.close()

    def since(self, t0: float) -> list[dict[str, Any]]:
        if t0 > 1e8:  # a wall-clock time (time.time()) would silently match nothing
            raise ValueError("WsObserver.since() takes a mark from WsObserver.now(), not time.time()")
        return [e for e in self.events if e["t"] >= t0]


# --------------------------------------------------------------------------- the runner


class Runner:
    def __init__(self, options: RunOptions) -> None:
        self.o = options
        self.commit: dict[str, Any] = {
            "sha": gitinfo.head_sha(),
            "branch": gitinfo.branch(),
            "dirty_files": gitinfo.dirty_files(),
        }
        self.commit["short"] = self.commit["sha"][:8]
        self.commit["dirty"] = bool(self.commit["dirty_files"])
        self.outcomes: list[Outcome] = []
        self.stack: SimStack | None = None
        self.hub: HubProcess | None = None
        self.device: SimDevice | HardwareDevice | None = None
        self.hub_health: dict[str, Any] = {}
        self.device_info: dict[str, Any] = {}
        self._xff_counter = 0
        self.aborted: str | None = None

    # ------------------------------------------------------------ lifecycle

    @property
    def evidence_dir(self) -> Path:
        return self.o.evidence_dir or self.o.out_dir / "evidence"

    @property
    def base_url(self) -> str:
        if self.stack and self.stack.hub:
            return self.stack.hub.base_url
        assert self.hub is not None
        return self.hub.base_url

    def _xff(self) -> str:
        self._xff_counter += 1
        n = self._xff_counter
        return f"10.77.{(n // 250) % 250}.{n % 250 + 1}"

    def _start_system(self) -> None:
        logs = self.o.out_dir / "logs"
        # Start the hub in the mode the first client needs (the uc client needs the UC integration).
        first = CLIENTS.get(self.o.clients[0]) if self.o.clients else None
        mode = first.hub_mode if first else "api"
        if self.o.sim_control_url:
            if self.o.target != "sim" or not self.o.hub_url:
                raise ValueError("sim_control_url requires target sim and an existing hub_url")
            self.hub = self._hardware_hub("api")
            self.hub_health = self.hub.start()
        elif self.o.target == "sim":
            self.stack = SimStack(logs)
            self.stack.start(mode)
            self.hub_health = self.stack.health
        else:
            if not self.o.matrix_host:
                raise SystemExit("--target hardware needs --matrix-host")
            self.hub = self._hardware_hub(mode if not self.o.hub_url else "api")
            self.hub_health = self.hub.start()

    def _hardware_hub(self, mode: str) -> HubProcess:
        return HubProcess(
            matrix_host=self.o.matrix_host or "",
            matrix_port=self.o.matrix_port,
            telnet_port=self.o.telnet_port,
            log_dir=self.o.out_dir / "logs",
            matrix_user=self.o.matrix_user,
            matrix_password=self.o.matrix_password,
            external_url=self.o.hub_url,
            mode=mode,
            polling_interval=2 if mode == "uc" else 30,
        )

    def _hub_process(self) -> HubProcess | None:
        if self.stack and self.stack.hub:
            return self.stack.hub
        return self.hub

    def _use_hub_mode(self, mode: str) -> None:
        """Run the hub in the mode the next client needs (restarting it in the other mode if needed)."""
        hub = self._hub_process()
        if hub is not None and hub.mode == mode:
            return
        if self.stack:
            self.stack.use_hub_mode(mode)
            self.hub_health = self.stack.health
            return
        if self.hub is not None and self.hub.external_url:
            raise RuntimeError(f"an already running hub (--hub-url) cannot be restarted in '{mode}' mode")
        if self.hub is not None:
            self.hub.stop()
        self.hub = self._hardware_hub(mode)
        self.hub_health = self.hub.start()

    def _stop_system(self) -> None:
        if self.stack:
            self.stack.stop()
        if self.hub:
            self.hub.stop()

    def _restart_hub(self) -> None:
        if self.stack:
            self.stack.restart_hub()
            self.hub_health = self.stack.health
        elif self.hub and not self.hub.external_url:
            self.hub_health = self.hub.restart()

    def _environment(self, client: Client) -> dict[str, Any]:
        env: dict[str, Any] = {
            "target": self.o.target,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "hub": {
                "entry": self._hub_process().entry if self._hub_process() else self.o.hub_url,
                "version": self.hub_health.get("version"),
                "api_version": self.hub_health.get("api_version"),
                "image_digest": self.o.hub_image_digest,
                "env": (self.stack.hub.recorded_env() if self.stack and self.stack.hub
                        else self.hub.recorded_env() if self.hub and not self.hub.external_url else {}),
            },
            "client": client.environment(),
        }
        if self.o.target == "sim":
            env["simulator"] = {**simulator_fingerprint(), **self.device_info}
        else:
            env["matrix"] = self.device_info
        return env

    # ------------------------------------------------------------ public

    @staticmethod
    def _scenario_environment(sc: Scenario) -> dict[str, str]:
        # Faults must reach a fresh device read. Happy paths retain the hub's
        # normal cache behavior, including preset read-count assertions.
        return {"OREI_USE_TELNET_CEC": "false", "OREI_STATUS_CACHE_TTL": "0" if sc.faults else "3", **sc.hub_env}

    def _scenario_environment_changes(self, sc: Scenario) -> bool:
        if self.stack is None or self.stack.hub is None:
            return False  # External hubs and real hardware keep the operator's settings.
        desired = self._scenario_environment(sc)
        return self.stack.hub.extra_env != desired

    def _use_scenario_environment(self, sc: Scenario) -> None:
        if not self._scenario_environment_changes(sc):
            return
        assert self.stack is not None and self.stack.hub is not None
        self.stack.hub.extra_env = self._scenario_environment(sc)
        self._restart_hub()

    def _client_hub_info(self) -> HubInfo:
        hub = self._hub_process()
        return HubInfo(self.base_url, forwarded_for=self._xff(), artifacts_dir=self.o.out_dir / "artifacts",
                       uc_url=hub.uc_url if hub is not None and hub.mode == "uc" else None)

    def _runner_started_hub(self) -> bool:
        """The hub is ours: the simulator stack's, or one started for a matrix (not --hub-url)."""
        return self.stack is not None or (self.hub is not None and not self.o.hub_url)

    async def _wait_hub_telnet(self, helper: ApiClient) -> None:
        """Wait for the hub's Telnet link to the matrix (simulator or hardware) before a scenario.

        Preset slot reads (BE-36), cable status and Telnet CEC need it; a hub the runner just
        started connects Telnet a moment after HTTP is up. An operator's own hub is not waited for.
        """
        if not self._runner_started_hub():
            return
        deadline = time.perf_counter() + 10
        while time.perf_counter() < deadline:
            status, _, _ = await helper.request("GET", "/api/status/cables")
            if status == 200:
                return
            await asyncio.sleep(0.05)
        raise RuntimeError("the hub's Telnet link to the matrix did not become ready before the scenario")

    async def run(self, scenarios: list[Scenario]) -> list[Outcome]:
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(self._start_system)
        try:
            if self.o.target == "sim":
                sim_url = self.o.sim_control_url or (self.stack.sim.control_url if self.stack else None)
                assert sim_url is not None
                dev: SimDevice | HardwareDevice = SimDevice(sim_url)
            else:
                dev = HardwareDevice(self.o.matrix_host or "", self.o.matrix_port, https=self.o.matrix_https,
                                     user=self.o.matrix_user, password=self.o.matrix_password,
                                     telnet_port=self.o.telnet_port)
            async with dev:
                self.device = dev
                self.device_info = await dev.info()
                for client_name in self.o.clients:
                    await self._run_client(client_name, scenarios)
                    if self.aborted:
                        break
        finally:
            await asyncio.to_thread(self._stop_system)
        self._write_summary()
        return self.outcomes

    async def _run_client(self, client_name: str, scenarios: list[Scenario]) -> None:
        client = make_client(client_name)
        # (per-record artifact dirs are passed in client.context before each action)
        try:
            if any(client_name in sc.clients for sc in scenarios):
                await asyncio.to_thread(self._use_hub_mode, client.hub_mode)
                first = next(sc for sc in scenarios if client_name in sc.clients)
                await asyncio.to_thread(self._use_scenario_environment, first)
            await client.start(self._client_hub_info())
        except (NotImplementedError, RuntimeError) as exc:
            for sc in scenarios:
                if client_name in sc.clients:
                    self.outcomes.append(Outcome(sc.id, client_name, "skipped", gate="skipped", reason=str(exc)))
            if not any(client_name in sc.clients for sc in scenarios):
                self.outcomes.append(Outcome("-", client_name, "skipped", gate="skipped", reason=str(exc)))
            print(f"[validate] client '{client_name}' unavailable: {exc}", flush=True)
            return
        try:
            for sc in scenarios:
                if self.aborted:
                    break
                if client_name not in sc.clients:
                    continue  # not a flow this client has
                reason = self._refusal(sc, client)
                if reason:
                    self.outcomes.append(Outcome(sc.id, client_name, "skipped", gate="skipped", reason=reason))
                    print(f"[validate] skip    {sc.id} [{client_name}]: {reason}", flush=True)
                    continue
                if self._scenario_environment_changes(sc):
                    await client.stop()
                    await asyncio.to_thread(self._use_scenario_environment, sc)
                    await client.start(self._client_hub_info())
                outcome = await self._run_one(sc, client)
                self.outcomes.append(outcome)
                mark = {"pass": "PASS", "fail": "FAIL", "blocked": "BLOCKED"}.get(outcome.status, outcome.status)
                extra = f" ({outcome.gate}: {', '.join(c['finding'] or '-' for c in outcome.failed_checks)})" \
                    if outcome.status == "fail" else ""
                print(f"[validate] {mark:7} {sc.id} [{client_name}] {outcome.level or ''}{extra}", flush=True)
        finally:
            await client.stop()

    def _refusal(self, sc: Scenario, client: Client) -> str | None:
        if client.name not in sc.clients:
            return f"scenario is not defined for client '{client.name}'"
        if sc.action.intent in RUNNER_INTENTS:
            if not client.observes:
                return f"client '{client.name}' cannot observe a '{sc.action.intent}'"
        elif not client.supports(sc.action):
            return f"client '{client.name}' cannot perform '{sc.action.intent}'"
        if self.o.target not in sc.targets:
            return f"scenario does not run on target '{self.o.target}'"
        if self.o.target == "hardware":
            if sc.writes and not self.o.allow_writes:
                return f"writes {list(sc.writes)} to the real matrix; pass --allow-writes to run it"
            unrestorable = set(sc.writes) - RESTORABLE_DOMAINS
            if unrestorable and not self.o.allow_unrestorable:
                return f"changes {sorted(unrestorable)}, which cannot be restored; pass --allow-unrestorable"
        return None

    # ------------------------------------------------------------ one scenario

    async def _run_one(self, sc: Scenario, client: Client) -> Outcome:
        assert self.device is not None
        dev = self.device
        level = level_for(self.o.target, client.name)
        started = _now()
        procedure: list[str] = []
        notes: list[str] = []
        xff = self._xff()
        helper = ApiClient()
        await helper.start(HubInfo(self.base_url, forwarded_for=xff))
        ws = WsObserver(self.base_url.replace("http", "ws", 1) + "/ws", xff)
        snapshot: dict[str, Any] | None = None
        restore_report: dict[str, Any] | None = None
        result = ActionResult(intent=sc.action.intent, ok=False)
        checks: list[dict[str, Any]] = []
        state_before: dict[str, Any] = {}
        state_after: dict[str, Any] = {}
        log_excerpt: list[dict[str, Any]] = []
        operator: list[dict[str, Any]] = []
        hub_reads: list[dict[str, Any]] = []
        t_action = WsObserver.now()
        blocked: str | None = None
        try:
            # ---- prepare the device
            if isinstance(dev, SimDevice):
                await dev.reset(sc.sim_state)
                procedure.append("reset the simulator to the seed state" + (f" + {sc.sim_state}" if sc.sim_state else ""))
                await self._wait_hub_telnet(helper)
                if self.stack is not None:
                    procedure.append("wait for the simulator Telnet link before setup and fault injection")
            else:
                await self._wait_hub_telnet(helper)
                if self._runner_started_hub():
                    procedure.append("wait for the hub's Telnet link to the matrix")
                snapshot = await dev.state()
                procedure.append("snapshot the matrix state (readback)")
            await ws.start()
            if ws.error:
                notes.append(f"WebSocket observer: {ws.error}")
            elif await ws.sync():
                procedure.append("let the hub read the matrix (/ws get_status), so it is in sync before the action")
            else:
                notes.append("the hub did not answer get_status on /ws")
            for step in sc.setup:
                r = await helper.perform(step)
                procedure.append(f"setup (api): {step.describe()} -> HTTP {r.status}")
                if not r.ok:
                    blocked = f"setup step {step.describe()} failed: HTTP {r.status} {r.error or ''}".strip()
                    break
            if blocked is None:
                if sc.faults and isinstance(dev, SimDevice):
                    await dev.set_faults(sc.faults)
                    procedure.append(f"inject simulator fault {sc.faults}")
                state_before = await dev.state()
                # Preconditions on what the client shows (ClientState.before): wait for them, so a
                # passing check afterwards proves a change the client saw.
                for exp in sc.expect:
                    if (isinstance(exp, ClientState) and exp.before is not None and client.observes
                            and (exp.clients is None or client.name in exp.clients)):
                        pre = await self._client_state(client, exp.key, exp.before, exp.timeout)
                        procedure.append(f"client showed {exp.key} = {pre['value']!r} before the action"
                                         + ("" if pre["ok"] else f" (expected {exp.before!r})"))
                        if not pre["ok"]:
                            checks.append({"description": f"client shows {exp.key} == {exp.before!r} before the action",
                                           "result": "fail", "detail": f"{exp.key} = {pre['value']!r}",
                                           "finding": exp.finding, "linked_finding": exp.finding,
                                           "note": exp.note or None})
                log_cursor = len(await dev.log()) if isinstance(dev, SimDevice) else 0
                # ---- the action
                stem = record_stem(started[:10], str(level), self.commit["short"], sc.id, client.name)
                artifacts_dir = self.evidence_dir / sc.features_for(client.name)[0] / stem
                client.context = {"label": sc.id, "forwarded_for": xff, "artifacts_dir": str(artifacts_dir)}
                t_action = WsObserver.now()
                procedure.append(f"action ({client.name}): {sc.action.describe()}")
                try:
                    if sc.action.intent in RUNNER_INTENTS:
                        result = await self._device_change(dev, sc.action)
                    else:
                        result = await client.perform(sc.action)
                except NotSupportedError:
                    return Outcome(sc.id, client.name, "skipped", gate="skipped",
                                   reason=f"client cannot perform {sc.action.intent}")
                procedure.extend(f"  {s}" for s in result.steps)
                if result.error:
                    notes.append(f"client error: {result.error}")
                # ---- expectations
                for exp in sc.expect:
                    checks.append(await self._check(exp, sc, client, result, state_before, t_action, ws, helper,
                                                    log_cursor, hub_reads))
                if ws.events:
                    checks.append(ws_contract_check(ws.events))
                state_after = await dev.state()
                if isinstance(dev, SimDevice):
                    log_excerpt = (await dev.log())[log_cursor:]
                # ---- operator observations (hardware)
                if self.o.target == "hardware" and sc.observe:
                    operator = self._observe(sc)
        except Exception as exc:  # noqa: BLE001 - record infrastructure failures as blocked evidence
            blocked = f"{type(exc).__name__}: {exc}"
        finally:
            await ws.stop()
            if isinstance(dev, SimDevice):
                try:
                    await dev.clear_faults()
                except Exception as exc:  # noqa: BLE001
                    notes.append(f"could not clear faults: {exc}")
            for step in sc.cleanup:
                try:
                    r = await helper.perform(step)
                    procedure.append(f"cleanup (api): {step.describe()} -> HTTP {r.status}")
                except Exception as exc:  # noqa: BLE001
                    notes.append(f"cleanup {step.describe()} failed: {exc}")
            await helper.stop()
            if isinstance(dev, HardwareDevice) and snapshot is not None and sc.writes:
                report = await dev.restore(snapshot, set(sc.writes))
                restore_report = report
                procedure.append(f"restore the matrix from the snapshot (verified: {report['verified']})")
                if not report["verified"]:
                    self.aborted = (f"restore after {sc.id} did not verify; stopping the session. Remaining: "
                                    f"{report['remaining_differences']}")
                    print(f"[validate] !!! {self.aborted}", flush=True)
            if sc.restart_after or sc.faults:
                await asyncio.to_thread(self._restart_hub)
                procedure.append("restart the hub (scenario may leave it in a bad state)")

        # ---- verdict
        failed = [c for c in checks if c["result"] == "fail"]
        unanswered = [o for o in operator if o["answer"] is None]
        negative = [o for o in operator if o["answer"] is not None and not o["confirmed"]]
        if blocked or unanswered:
            status = "blocked"
            if unanswered:
                blocked = blocked or "operator observation(s) not answered"
        elif failed or negative:
            status = "fail"
        else:
            status = "pass"
        for o in negative:
            failed.append({"description": f"operator: {o['question']}", "result": "fail",
                           "detail": f"answer: {o['answer']}", "finding": None})
        open_ids = {fid for fid, f in self.o.findings.items() if f.open}
        scenario_known = set(sc.findings) & open_ids
        gate = "ok"
        if status == "fail":
            unexplained = [c for c in failed if not ((c.get("finding") in open_ids) or scenario_known)]
            gate = "regression" if unexplained else "known-failure"
        elif status == "blocked":
            gate = "regression" if self.o.target == "sim" else "ok"
        findings = sorted({c["finding"] for c in failed if c.get("finding")} | (scenario_known if failed else set()))
        record = {
            "schema_version": SCHEMA_VERSION,
            "features": list(sc.features_for(client.name)),
            "level": str(level),
            "scenario": sc.id,
            "scenario_title": sc.title,
            "scenario_kind": sc.kind,
            "target": self.o.target,
            "client": client.name,
            "result": status,
            "gate": gate,
            "blocked_reason": blocked,
            "commit": self.commit,
            "timestamp": {"started": started, "finished": _now()},
            "operator": self.o.operator,
            "environment": self._environment(client),
            "procedure": procedure,
            "observations": {
                "requests": redact(result.requests),
                "response_status": result.status,
                "hub_reads": redact(hub_reads),
                "state_before": state_before,
                "state_after": state_after,
                "state_diff": diff_states(state_before, state_after) if state_before and state_after else [],
                "device_log": redact(compact_log(log_excerpt)),
                "ws_events": [
                    {"t_ms": round((e["t"] - t_action) * 1000), "event": e["event"], "data": e["data"]}
                    for e in ws.events
                ],
                # relative to the record file: <feature>/<record stem>/<name>.png
                "screenshots": [self._rel_to(p, self.evidence_dir / sc.features_for(client.name)[0])
                                for p in result.screenshots],
                "client_diagnostics": result.body if client.name != "api" else None,
                "operator": operator,
                "restore": restore_report,
                "notes": notes,
            },
            "checks": checks,
            "findings": findings,
            "covers": list(sc.covers),
        }
        path = write_record(self.evidence_dir, record)
        return Outcome(sc.id, client.name, status, str(level), list(sc.features_for(client.name)),
                       [{"description": c["description"], "finding": c.get("finding")} for c in failed],
                       gate, blocked or "", self._rel(path))

    @staticmethod
    def _rel_to(p: str | Path, base: Path) -> str:
        try:
            return Path(p).resolve().relative_to(base.resolve()).as_posix()
        except ValueError:
            return Path(p).as_posix()

    def _rel(self, p: str | Path) -> str:
        p = Path(p)
        try:
            return p.resolve().relative_to(self.o.out_dir.resolve()).as_posix()
        except ValueError:
            return p.as_posix()

    # ------------------------------------------------------------ runner-performed actions

    async def _device_change(self, dev: SimDevice | HardwareDevice, action: Action) -> ActionResult:
        """The device changes behind the hub's back (``device_change``): simulator event or state patch."""
        if not isinstance(dev, SimDevice):
            raise RuntimeError("device_change needs the simulator")
        result = ActionResult(intent=action.intent, ok=False)
        t0 = time.perf_counter()
        if "event" in action.params:
            await dev.event(action.params["event"])
            result.steps.append(f"simulator event {action.params['event']}")
        elif "reboot" in action.params:
            await dev.reboot(float(action.params["reboot"]))
            result.steps.append(f"simulator reboot: the device is offline for {action.params['reboot']} s")
        else:
            await dev.patch_state(action.params["patch"])
            result.steps.append(f"simulator state patch {action.params['patch']}")
        result.ok = True
        result.elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)
        return result

    @staticmethod
    async def _client_state(client: Client, key: str, expected: Any, timeout: float) -> dict[str, Any]:
        """Poll ``client.observe(key)`` until it equals ``expected`` or ``timeout`` passes."""
        deadline = time.monotonic() + timeout
        while True:
            value = await client.observe(key)
            ok = value == expected
            if ok or time.monotonic() >= deadline:
                return {"ok": ok, "value": value}
            await asyncio.sleep(0.5)

    # ------------------------------------------------------------ checks

    async def _check(self, exp: Expectation, sc: Scenario, client: Client, result: ActionResult,
                     before: dict[str, Any], t_action: float, ws: WsObserver, helper: ApiClient,
                     log_cursor: int, hub_reads: list[dict[str, Any]]) -> dict[str, Any]:
        assert self.device is not None
        dev = self.device
        verdict, detail = "pass", ""
        if exp.clients is not None and client.name not in exp.clients:
            return {"description": exp.describe(), "result": "n/a", "detail": f"not checked for client '{client.name}'",
                    "finding": None, "linked_finding": exp.finding, "note": exp.note or None}
        try:
            if isinstance(exp, Device):
                deadline = time.monotonic() + exp.timeout
                while True:
                    value = resolve(await dev.state(), exp.path)
                    ok = value != exp.not_equals if exp.not_equals is not None else value == exp.equals
                    if ok or time.monotonic() >= deadline:
                        break
                    await asyncio.sleep(0.25)
                verdict = "pass" if ok else "fail"
                detail = f"{exp.path} = {value!r}"
            elif isinstance(exp, DeviceUnchanged):
                after = await dev.state()
                ignore = VOLATILE_PATHS if self.o.target == "hardware" else ()
                changed = [
                    d for d in diff_states(before, after)
                    if not any(path_matches(d["path"], a) for a in (*exp.allow, *ignore))
                ]
                verdict = "fail" if changed else "pass"
                detail = f"unexpected changes: {changed[:10]}" if changed else "no other changes"
            elif isinstance(exp, CommandSent | CommandGap | NoCommand | NoProtocolWarnings):
                if not isinstance(dev, SimDevice):
                    return {"description": exp.describe(), "result": "n/a",
                            "detail": "no command log on hardware; proven by readback/observation", "finding": None}
                entries = (await dev.log())[log_cursor:]
                if isinstance(exp, CommandSent):
                    hits = [e for e in entries if e.get("channel") == exp.channel and e.get("command") == exp.command
                            and (exp.payload is None or _subset(exp.payload, e.get("payload")))]
                    ok = len(hits) == exp.count if exp.count is not None else bool(hits)
                    verdict = "pass" if ok else "fail"
                    seen = [(e.get("command"), e.get("payload")) for e in entries if e.get("channel") == exp.channel]
                    detail = f"{len(hits)} matching; {exp.channel} commands seen: {seen[:12]}"
                elif isinstance(exp, CommandGap):
                    first = next((e for e in entries if e.get("command") == exp.before), None)
                    last = next((e for e in entries if e.get("command") == exp.after), None)
                    gap = last["t"] - first["t"] if first and last else None
                    verdict = "pass" if gap is not None and gap >= exp.seconds else "fail"
                    detail = f"device command gap = {gap!r}s"
                elif isinstance(exp, NoCommand):
                    hits = [e for e in entries if e.get("channel") in ("http", "telnet")
                            and (e.get("mutated") if exp.command == "*" else e.get("command") == exp.command)]
                    verdict = "fail" if hits else "pass"
                    detail = f"write commands seen: {[(e.get('command'), e.get('payload')) for e in hits][:8]}"
                else:
                    warned = [(e.get("command"), e.get("warnings")) for e in entries if e.get("warnings")]
                    verdict = "fail" if warned else "pass"
                    detail = f"warnings: {warned}" if warned else "none"
            elif isinstance(exp, Response):
                status = result.status
                ok = status is not None
                if exp.status is not None:
                    allowed = exp.status if isinstance(exp.status, tuple) else (exp.status,)
                    ok = ok and status in allowed
                if exp.min_status is not None:
                    ok = ok and status is not None and status >= exp.min_status
                if exp.json and client.name == "api":
                    ok = ok and _subset(exp.json, result.body)
                verdict = "pass" if ok else "fail"
                body = json.dumps(result.body, default=str)[:300] if client.name == "api" else f"({client.name})"
                detail = f"HTTP {status}; body {body}" + (f"; error {result.error}" if result.error else "")
            elif isinstance(exp, Hub):
                deadline = time.monotonic() + 4.0
                while True:
                    status, body, exchange = await helper.request("GET", exp.path)
                    got: Any = None
                    try:
                        got = resolve(body, exp.field_path) if exp.field_path else body
                        found = True
                    except KeyError:
                        found = False
                    if exp.absent_or_false:
                        ok = not (found and got is True)
                    elif exp.not_equals is not None:
                        ok = found and got != exp.not_equals
                    else:
                        ok = (not exp.field_path or (found and got == exp.equals))
                    ok = ok and (exp.status is None or status == exp.status)
                    if ok or time.monotonic() >= deadline:
                        hub_reads.append(exchange)
                        break
                    await asyncio.sleep(0.5)
                verdict = "pass" if ok else "fail"
                shown = got if found else "<absent>"
                detail = f"HTTP {status}; {exp.field_path or 'body'} = {json.dumps(shown, default=str)[:200]}"
            elif isinstance(exp, PresetRouting):
                stored = (await dev.preset_slots()).get(exp.slot)
                deadline = time.monotonic() + exp.timeout
                while True:
                    after = (await dev.state()).get("routing")
                    verdict, detail = preset_routing_verdict(before.get("routing"), after, stored)
                    if verdict == "pass" or stored is None or time.monotonic() >= deadline:
                        break
                    await asyncio.sleep(0.25)
            elif isinstance(exp, PresetCatalog):
                status, body, exchange = await helper.request("GET", "/api/presets")
                hub_reads.append(exchange)
                slots = await dev.preset_slots()
                problems = compare_preset_catalog(resolve(body, "data.presets"), slots)
                verdict = "pass" if status == 200 and not problems else "fail"
                detail = (f"HTTP {status}; 8 slots agree ({sum(v is not None for v in slots.values())} stored, "
                          f"{sum(v is None for v in slots.values())} empty)") if verdict == "pass" else                     f"HTTP {status}; disagreements: {json.dumps(problems)[:600]}"
            elif isinstance(exp, ClientState):
                if not client.observes:
                    return {"description": exp.describe(), "result": "n/a",
                            "detail": f"client '{client.name}' has no view of {exp.key}", "finding": None,
                            "linked_finding": exp.finding, "note": exp.note or None}
                t0 = time.monotonic()
                seen = await self._client_state(client, exp.key, exp.equals, exp.timeout)
                verdict = "pass" if seen["ok"] else "fail"
                detail = f"{exp.key} = {seen['value']!r} after {time.monotonic() - t0:.1f} s"
            elif isinstance(exp, WsEvent):
                deadline = time.monotonic() + exp.timeout
                while True:
                    hits = [e for e in ws.since(t_action) if e["event"] == exp.event
                            and (exp.data is None or _subset(exp.data, e["data"]))]
                    if hits or time.monotonic() >= deadline:
                        break
                    await asyncio.sleep(0.1)
                verdict = "pass" if hits else "fail"
                detail = f"events after the action: {[e['event'] for e in ws.since(t_action)][:12]}"
            elif isinstance(exp, NoWsEvent):
                await asyncio.sleep(exp.timeout)
                hits = [e for e in ws.since(t_action) if e["event"] == exp.event]
                verdict = "fail" if hits else "pass"
                detail = f"events after the action: {[e['event'] for e in ws.since(t_action)][:12]}"
            else:  # pragma: no cover - new expectation type without a checker
                verdict, detail = "fail", f"no checker for {type(exp).__name__}"
        except Exception as exc:  # noqa: BLE001 - a check that crashes is a failed check
            verdict, detail = "fail", f"check raised {type(exc).__name__}: {exc}"
        return {
            "description": exp.describe(),
            "result": verdict,
            "detail": detail,
            "finding": exp.finding if verdict == "fail" else None,
            "linked_finding": exp.finding,
            "note": exp.note or None,
        }

    # ------------------------------------------------------------ operator

    def _observe(self, sc: Scenario) -> list[dict[str, Any]]:
        """Ask the operator about physical effects; answers from ``--answers`` or the terminal."""
        scripted = list(self.o.answers.get(sc.id, []))
        out = []
        for q in sc.observe:
            entry: dict[str, Any] = {"question": q, "answer": None, "media": [], "at": _now(), "confirmed": False}
            if scripted:
                a = scripted.pop(0)
                entry["answer"] = str(a.get("answer"))
                entry["media"] = list(a.get("media", []))
                entry["source"] = "answers file"
            elif self.o.interactive:
                ans = input(f"\n[observe] {sc.id}: {q} [y/n] ").strip()
                media = input("  optional photo/video path(s), comma-separated: ").strip()
                entry["answer"] = ans
                entry["media"] = [m.strip() for m in media.split(",") if m.strip()]
                entry["source"] = "terminal"
            entry["confirmed"] = str(entry["answer"]).lower() in ("y", "yes", "true", "1")
            out.append(entry)
        return out

    # ------------------------------------------------------------ summary

    def _write_summary(self) -> None:
        summary = {
            "commit": self.commit,
            "target": self.o.target,
            "clients": list(self.o.clients),
            "operator": self.o.operator,
            "finished": _now(),
            "aborted": self.aborted,
            "outcomes": [o.__dict__ for o in self.outcomes],
        }
        self.o.out_dir.mkdir(parents=True, exist_ok=True)
        (self.o.out_dir / "run-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
