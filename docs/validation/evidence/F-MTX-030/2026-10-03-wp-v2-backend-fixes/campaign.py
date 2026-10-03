"""Record validation evidence against the packaged hub image and the containerised simulator.

Run from the repository root with a clean tracked tree:

    python campaign.py --image hdmi-matrix-hub:TAG --sim-image hdmi-matrix-hub-sim:TAG \
        --client api --select <prefix|id>[,...] [--exclude <prefix>,...] [--env K=V ...] --out build/x [--record]

One disposable stack per invocation: a network, a data volume seeded with
tests/e2e/fixtures/data, the simulator container and the hub container (UC off).
The hub reconnects by itself after fault scenarios; the runner waits for both
matrix transports before each next scenario. The record's hub env is the
container's actual environment (docker inspect), not the runner's process env.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import socket
import subprocess
import sys
import time
import urllib.request
import uuid
from pathlib import Path

sys.path.insert(0, ".")

# Windows + Python 3.12: time.time() ticks every ~15.6 ms, so WsObserver.sync() (which keeps
# events with t >= t0) can take the welcome snapshot received in the same tick for the answer
# to its get_status, skip the hub's fresh read, and run the scenario on stale caches.
# A high-resolution wall clock (perf_counter anchored to time.time) removes that tie.
_WALL0, _PERF0 = time.time(), time.perf_counter()
time.time = lambda: _WALL0 + (time.perf_counter() - _PERF0)  # type: ignore[assignment]
from tools.validate.evidence import COMMITTED_EVIDENCE  # noqa: E402
from tools.validate.registry import load_findings  # noqa: E402
from tools.validate.runner import Runner, RunOptions  # noqa: E402
from tools.validate.scenarios import discover  # noqa: E402
from tools.validate.stack import RECORDED_ENV  # noqa: E402

ROOT = Path.cwd()


def docker(*args: str, check: bool = True) -> str:
    p = subprocess.run(["docker", *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"docker {' '.join(args[:3])}: {p.stderr.strip()}")
    return p.stdout.strip()


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=2) as r:
        return json.load(r)


def wait(fn, seconds: float, what: str) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            if fn():
                return
        except Exception:
            pass
        time.sleep(0.2)
    raise RuntimeError(f"timed out waiting for {what}")


class Stack:
    def __init__(self, image: str, sim_image: str, env: dict[str, str], publish_all: bool) -> None:
        self.image, self.sim_image, self.env = image, sim_image, env
        sfx = uuid.uuid4().hex[:10]
        self.net, self.vol = f"wpv2-net-{sfx}", f"wpv2-data-{sfx}"
        self.sim, self.hub = f"wpv2-sim-{sfx}", f"wpv2-hub-{sfx}"
        self.bind = "0.0.0.0" if publish_all else "127.0.0.1"

    def __enter__(self) -> Stack:
        self.control, self.api = free_port(), free_port()
        docker("network", "create", self.net)
        docker("volume", "create", self.vol)
        fixtures = (ROOT / "tests/e2e/fixtures/data").as_posix()
        docker("run", "--rm", "--user", "root", "-v", f"{self.vol}:/data", "-v", f"{fixtures}:/fixtures:ro",
               "--entrypoint", "sh", self.image, "-c", "cp /fixtures/*.json /data/; chown -R appuser:app /data")
        docker("run", "-d", "--name", self.sim, "--network", self.net, "--network-alias", "domain-matrix",
               "-p", f"127.0.0.1:{self.control}:8444", "--no-healthcheck", self.sim_image,
               "python", "-m", "tools.simulator", "--host", "0.0.0.0", "--https-port", "8443",
               "--telnet-port", "2323", "--control-port", "8444", "--reboot-seconds", "3")
        wait(lambda: get_json(f"{self.control_url}/_sim/health") is not None, 90, "simulator")
        env = {"MATRIX_HOST": "domain-matrix", "MATRIX_PORT": "8443", "OREI_TELNET_PORT": "2323",
               "UC_ENABLED": "false", "TRUST_PROXY_HEADERS": "true",
               "TRUSTED_PROXY_IPS": "127.0.0.1,172.16.0.0/12,192.168.0.0/16", **self.env}
        args = ["run", "-d", "--name", self.hub, "--network", self.net, "-p", f"{self.bind}:{self.api}:8080",
                "-v", f"{self.vol}:/data"]
        for k, v in env.items():
            args += ["-e", f"{k}={v}"]
        docker(*args, self.image)
        self.ready(120)
        self.digest = docker("image", "inspect", "-f", "{{.Id}}", self.image)
        lines = docker("inspect", "-f", "{{range .Config.Env}}{{println .}}{{end}}", self.hub).splitlines()
        actual = dict(line.split("=", 1) for line in lines if "=" in line)
        for k, v in self.env.items():
            assert actual.get(k) == v, f"hub env {k}={actual.get(k)!r}, expected {v!r}"
        self.recorded_env = {k: actual[k] for k in RECORDED_ENV if k in actual}
        return self

    @property
    def control_url(self) -> str:
        return f"http://127.0.0.1:{self.control}"

    @property
    def hub_url(self) -> str:
        return f"http://127.0.0.1:{self.api}"

    def ready(self, seconds: float = 40) -> None:
        def ok() -> bool:
            m = get_json(f"{self.hub_url}/api/health")["data"]["matrix"]
            return bool(m["connected"] and m["telnet_connected"])
        wait(ok, seconds, "hub HTTP and Telnet links to the simulator")

    def __exit__(self, *exc: object) -> None:
        for name in (self.hub, self.sim):
            docker("rm", "-f", name, check=False)
        docker("volume", "rm", self.vol, check=False)
        docker("network", "rm", self.net, check=False)


class ReadyRunner(Runner):
    dstack: Stack

    async def _run_one(self, sc, client):  # type: ignore[no-untyped-def]
        # The api client sends every action with one X-Forwarded-For for the whole run, so the
        # hub's per-IP limit (60 requests / 10 s) would answer 429 to fast scenarios: pace them.
        await asyncio.sleep(0.3)
        return await super()._run_one(sc, client)

    def _start_system(self) -> None:
        super()._start_system()
        self.dstack.ready()

    def _restart_hub(self) -> None:
        # the packaged hub is not restarted: it reconnects; wait for both transports
        super()._restart_hub()
        self.dstack.ready()

    def _environment(self, client):  # type: ignore[no-untyped-def]
        environment = super()._environment(client)
        environment["hub"]["env"] = dict(self.dstack.recorded_env)
        return environment


def pick(all_ids: list[str], select: list[str], exclude: list[str]) -> list[str]:
    def hit(sid: str, pats: list[str]) -> bool:
        return any(p == "*" or sid == p or (p.endswith(".") and sid.startswith(p)) for p in pats)
    return [s for s in all_ids if hit(s, select) and not hit(s, exclude)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--sim-image", required=True)
    ap.add_argument("--client", default="api")
    ap.add_argument("--select", required=True, help="comma list: exact ids or prefixes ending in '.'")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--env", action="append", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--publish-all", action="store_true", help="publish the hub on 0.0.0.0 (HA container)")
    a = ap.parse_args()
    if a.record and subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                                   capture_output=True, text=True).stdout.strip():
        raise SystemExit("tracked files are dirty: commit first")
    scenarios = discover()
    ids = pick([sid for sid, sc in scenarios.items() if a.client in sc.clients],
               [s for s in a.select.split(",") if s], [s for s in a.exclude.split(",") if s])
    selected = sorted((scenarios[s] for s in ids), key=lambda s: (bool(s.faults), s.id))
    if not selected:
        raise SystemExit("nothing selected")
    env = dict(e.split("=", 1) for e in a.env)
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "selection.json").write_text(json.dumps([s.id for s in selected], indent=1), encoding="utf-8")
    print(f"[campaign] {len(selected)} scenarios, client {a.client}, env {env}", flush=True)
    # One fresh stack (simulator, hub, fixture data) per scenario module, as earlier batches did:
    # a long-lived hub carries state (name caches, saved data) from one module into the next.
    groups: dict[str, list] = {}
    for sc in selected:
        groups.setdefault(sc.id.split(".")[0], []).append(sc)
    outcomes = []
    summaries = []
    for module, group in groups.items():
        gout = out / module
        print(f"[campaign] module {module}: {len(group)} scenarios", flush=True)
        with Stack(a.image, a.sim_image, env, a.publish_all) as stack:
            opts = RunOptions(target="sim", clients=(a.client,), out_dir=gout,
                              evidence_dir=COMMITTED_EVIDENCE if a.record else None, findings=load_findings(),
                              hub_url=stack.hub_url, sim_control_url=stack.control_url,
                              hub_image_digest=stack.digest)
            runner = ReadyRunner(opts)
            runner.dstack = stack
            outcomes += asyncio.run(runner.run(group))
            summaries.append({"module": module, "image": a.image, "digest": stack.digest,
                              "sim_image": a.sim_image, "env": stack.recorded_env, "client": a.client})
    (out / "stacks.json").write_text(json.dumps(summaries, indent=1), encoding="utf-8")
    counts: dict[str, int] = {}
    for o in outcomes:
        counts[o.status] = counts.get(o.status, 0) + 1
    print(f"[campaign] done {counts}", flush=True)
    for o in outcomes:
        if o.status != "pass":
            print(f"[campaign] {o.status} {o.scenario} [{o.client}] {o.gate} {o.reason} "
                  f"{[c.get('description') for c in o.failed_checks]}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
