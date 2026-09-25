#!/usr/bin/env python3
"""Generate REST API contract fixtures (TST-02).

Clients of the hub (the Home Assistant component, the web UI, and future
tests) must be tested against the JSON the hub *really* returns, not against
shapes someone typed by hand. This script builds those responses by running
the real code path:

    raw device responses (below)
      -> real ``OreiMatrix`` status parsing (only ``_send_command`` is faked)
      -> real ``rest_api`` app built by ``create_rest_app``
      -> real HTTP request through aiohttp's test server

and writes each response body to ``tests/fixtures/api/<name>.json``.

``tests/test_contract_fixtures.py`` regenerates the fixtures in memory and
fails when they differ from the committed files. If you change an endpoint's
response on purpose, regenerate and commit the fixtures:

    python tools/gen_contract_fixtures.py          # rewrite fixtures
    python tools/gen_contract_fixtures.py --check  # exit 1 on drift

The raw device state is a deterministic, realistic 8x8 setup: named inputs,
two named outputs (TV, Soundbar), mixed routing, some signals and displays
present. The raw shapes follow docs/OREI_API_COMMANDS.md.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "api"

if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

# -----------------------------------------------------------------------------
# Deterministic raw device state
# -----------------------------------------------------------------------------

MATRIX_HOST = "192.0.2.10"  # RFC 5737 TEST-NET-1: never a real device
MATRIX_PORT = 443

INPUT_NAMES = ["PS3", "AppleTV", "Computer", "Switch", "Shield", "PS5", "Analogue", "Input 8"]
OUTPUT_NAMES = ["TV", "Soundbar", "Output 3", "Output 4", "Output 5", "Output 6", "Output 7", "Output 8"]
PRESET_NAMES = ["Movie Night", "Gaming", "Preset 3", "Preset 4", "Preset 5", "Preset 6", "Preset 7", "Preset 8"]

# allsource[i] = input routed to output i+1.
# TV and Soundbar both watch AppleTV; the idle outputs show other sources.
ROUTING = [2, 2, 6, 4, 1, 3, 5, 7]

# Raw JSON the matrix returns per `comhead` (see docs/OREI_API_COMMANDS.md).
RAW_DEVICE_RESPONSES: dict[str, dict[str, Any]] = {
    "get video status": {
        "comhead": "get video status",
        "power": 1,
        "allsource": ROUTING,
        "allinputname": INPUT_NAMES,
        "alloutputname": OUTPUT_NAMES,
        "allname": PRESET_NAMES,
    },
    "get output status": {
        "comhead": "get output status",
        "power": 1,
        "allconnect": [1, 1, 0, 0, 0, 0, 0, 0],  # TV + Soundbar plugged in
        "allscaler": [1, 1, 1, 1, 1, 1, 1, 1],
        "allhdr": [3, 3, 3, 3, 3, 3, 3, 3],
        "allhdcp": [3, 3, 3, 3, 3, 3, 3, 3],
        "allarc": [1, 0, 0, 0, 0, 0, 0, 0],  # ARC from the TV
        "allout": [1, 1, 1, 1, 1, 1, 1, 0],  # output 8 stream disabled
        "allaudiomute": [0, 1, 0, 0, 0, 0, 0, 0],  # Soundbar audio muted
        "allsource": ROUTING,
        "allinputname": INPUT_NAMES,
        "alloutputname": OUTPUT_NAMES,
    },
    "get input status": {
        "comhead": "get input status",
        "power": 1,
        "edid": [3, 3, 3, 3, 3, 3, 3, 3],
        "inactive": [0, 1, 0, 1, 0, 1, 0, 0],  # 1 = signal present (AppleTV, Switch, PS5)
        "inname": INPUT_NAMES,
    },
}

# fixture file name -> hub route
FIXTURES: dict[str, str] = {
    "health.json": "/api/health",
    "status.json": "/api/status",
    "status_outputs.json": "/api/status/outputs",
    "status_inputs.json": "/api/status/inputs",
    "presets.json": "/api/presets",
    "inputs.json": "/api/inputs",
    "outputs.json": "/api/outputs",
}


def make_matrix_device():
    """Build a real ``OreiMatrix`` whose transport returns the raw state above."""
    from orei_matrix import OreiMatrix

    device = OreiMatrix(MATRIX_HOST, MATRIX_PORT)
    device._connected = True
    # A zero TTL keeps /api/status from spawning a background refresh task.
    device._status_cache_ttl = 0.0

    async def fake_send_command(command: dict, retry_on_failure: bool = True):
        response = RAW_DEVICE_RESPONSES.get(command.get("comhead", ""))
        if response is None:
            return False, None
        return True, copy.deepcopy(response)

    device._send_command = fake_send_command  # type: ignore[method-assign]
    return device


async def _fetch(route: str, data_dir: Path) -> dict[str, Any]:
    from aiohttp.test_utils import TestClient, TestServer

    from rest_api.app import create_rest_app
    from rest_api.utils import reset_rate_limiter, set_matrix_device

    reset_rate_limiter()
    set_matrix_device(
        make_matrix_device(),
        input_names={i + 1: name for i, name in enumerate(INPUT_NAMES)},
        output_names={i + 1: name for i, name in enumerate(OUTPUT_NAMES)},
        config_dir=str(data_dir),
        data_dir=str(data_dir),
    )
    app = create_rest_app(data_dir)
    async with TestClient(TestServer(app)) as client:
        resp = await client.get(route)
        body = await resp.json()
        if resp.status != 200:
            raise RuntimeError(f"{route} returned HTTP {resp.status}: {body}")
        return body


async def generate() -> dict[str, dict[str, Any]]:
    """Return ``{fixture file name: response body}`` for every fixture.

    Each route is fetched from a fresh app, device and data directory, so
    the output does not depend on request order or on local state.
    """
    from persistence import reset_data_dir_cache

    results: dict[str, dict[str, Any]] = {}
    saved_env = os.environ.get("MATRIX_DATA_DIR")
    try:
        for name, route in FIXTURES.items():
            with tempfile.TemporaryDirectory(prefix="contract-fixtures-") as tmp:
                os.environ["MATRIX_DATA_DIR"] = tmp
                reset_data_dir_cache()
                results[name] = await _fetch(route, Path(tmp))
    finally:
        if saved_env is None:
            os.environ.pop("MATRIX_DATA_DIR", None)
        else:
            os.environ["MATRIX_DATA_DIR"] = saved_env
        reset_data_dir_cache()
    return results


def render(payload: dict[str, Any]) -> str:
    """Serialize a fixture exactly as it is committed."""
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="do not write; exit 1 if committed fixtures differ")
    args = parser.parse_args(argv)

    import logging

    logging.basicConfig(level=logging.WARNING)
    generated = asyncio.run(generate())

    drift = []
    for name, payload in generated.items():
        path = FIXTURE_DIR / name
        text = render(payload)
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current != text:
            drift.append(name)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")

    if args.check:
        if drift:
            print(f"Contract fixtures out of date: {', '.join(drift)}")
            print("Run: python tools/gen_contract_fixtures.py")
            return 1
        print(f"Contract fixtures up to date ({len(generated)} files).")
        return 0

    print(f"Wrote {len(drift)} of {len(generated)} fixture(s) to {FIXTURE_DIR.relative_to(REPO_ROOT)}")
    for name in drift:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
