#!/usr/bin/env python3
"""Run the BK-808 simulator and the hub (REST API + web UI) together.

For local UI development and Playwright capture, no hardware needed::

    python tools/dev_stack.py                 # UI at http://127.0.0.1:8080/ui
    python tools/dev_stack.py --api-port 8090 --data-dir .dev-data

The hub is started through its real entry point (``run.py`` in modular,
API-only mode) with environment variables pointing it at the simulator:
``MATRIX_HOST``/``MATRIX_PORT`` (HTTPS) and ``OREI_TELNET_PORT`` (Telnet).
Hub data (profiles, scenes, settings) goes to a throw-away temp directory
unless ``--data-dir`` is given. Ctrl+C stops both processes.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _wait_for(url: str, proc: subprocess.Popen, timeout: float, what: str) -> dict:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError(f"{what} exited early with code {proc.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:  # noqa: S310 - local dev URL
                return json.loads(resp.read().decode())
        except (urllib.error.URLError, OSError, ValueError) as exc:
            last_error = exc
            time.sleep(0.25)
    raise RuntimeError(f"{what} not ready at {url} after {timeout:.0f}s: {last_error}")


def _stop(proc: subprocess.Popen | None, name: str, timeout: float = 8) -> None:
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"[dev-stack] killing {name}", flush=True)
        proc.kill()
        proc.wait()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1", help="address for all listeners (default 127.0.0.1)")
    parser.add_argument("--api-port", type=int, default=8080, help="hub REST/web UI port (default 8080)")
    parser.add_argument("--https-port", type=int, default=8443, help="simulator HTTPS port (default 8443)")
    parser.add_argument("--telnet-port", type=int, default=2323, help="simulator Telnet port (default 2323)")
    parser.add_argument("--control-port", type=int, default=8444, help="simulator /_sim control port (default 8444)")
    parser.add_argument("--state", type=Path, default=ROOT / "tools" / "simulator" / "states" / "default.json")
    parser.add_argument("--data-dir", type=Path, help="persistent hub data dir (default: temp dir, deleted on exit)")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)

    temp_dir = None
    data_dir = args.data_dir
    if data_dir is None:
        temp_dir = tempfile.mkdtemp(prefix="hub-dev-data-")
        data_dir = Path(temp_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    sim_cmd = [
        sys.executable, "-m", "tools.simulator",
        "--host", args.host,
        "--https-port", str(args.https_port),
        "--telnet-port", str(args.telnet_port),
        "--control-port", str(args.control_port),
        "--state", str(args.state),
        "--log-level", args.log_level,
    ]
    hub_env = {
        **os.environ,
        "USE_MODULAR": "true",
        "UC_ENABLED": "false",
        "MATRIX_HOST": args.host,
        "MATRIX_PORT": str(args.https_port),
        "OREI_TELNET_PORT": str(args.telnet_port),
        "API_PORT": str(args.api_port),
        "MATRIX_DATA_DIR": str(data_dir.resolve()),
        "UC_CONFIG_HOME": str(data_dir.resolve()),
        "LOG_LEVEL": args.log_level,
        "PYTHONUNBUFFERED": "1",
    }
    for key in ("OREI_USER", "OREI_PASSWORD", "OREI_PORT"):
        hub_env.pop(key, None)

    sim = hub = None
    try:
        print(f"[dev-stack] starting simulator: {' '.join(sim_cmd[1:])}", flush=True)
        sim = subprocess.Popen(sim_cmd, cwd=ROOT)
        _wait_for(f"http://{args.host}:{args.control_port}/_sim/health", sim, 20, "simulator")

        print(f"[dev-stack] starting hub (run.py, modular API-only) with data in {data_dir}", flush=True)
        hub = subprocess.Popen([sys.executable, "run.py"], cwd=ROOT, env=hub_env)
        health = _wait_for(f"http://{args.host}:{args.api_port}/api/health", hub, 30, "hub")
        connected = health.get("data", {}).get("matrix", {}).get("connected")

        base = f"http://{args.host}:{args.api_port}"
        print(
            "\n[dev-stack] ready\n"
            f"  Web UI:      {base}/ui\n"
            f"  Kiosk:       {base}/kiosk\n"
            f"  Hub API:     {base}/api/status   (matrix connected: {connected})\n"
            f"  Simulator:   https://{args.host}:{args.https_port}/cgi-bin/instr, telnet {args.host}:{args.telnet_port}\n"
            f"  Sim control: http://{args.host}:{args.control_port}/_sim/state  (faults: /_sim/faults)\n"
            "  Ctrl+C to stop.\n",
            flush=True,
        )
        while True:
            for proc, name in ((sim, "simulator"), (hub, "hub")):
                if proc.poll() is not None:
                    print(f"[dev-stack] {name} exited with code {proc.returncode}", flush=True)
                    return 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[dev-stack] stopping...", flush=True)
        return 0
    except RuntimeError as exc:
        print(f"[dev-stack] {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        _stop(hub, "hub")
        _stop(sim, "simulator")
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
