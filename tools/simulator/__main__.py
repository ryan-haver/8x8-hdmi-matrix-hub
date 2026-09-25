"""CLI: ``python -m tools.simulator [options]``."""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import logging
import sys
from pathlib import Path

from . import protocol as proto
from .server import Simulator
from .state import DEFAULT_STATE_FILE, DeviceState, StateError, load_capture_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m tools.simulator", description="OREI BK-808 matrix simulator")
    parser.add_argument("--host", default="127.0.0.1", help="bind address (default 127.0.0.1)")
    parser.add_argument("--https-port", type=int, default=8443, help="device HTTPS port (default 8443; 0 = any)")
    parser.add_argument("--telnet-port", type=int, default=2323, help="device Telnet port (default 2323; 0 = any)")
    parser.add_argument("--control-port", type=int, default=8444, help="/_sim control API port (default 8444)")
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE_FILE, help="state JSON file to seed from")
    parser.add_argument("--captures", type=Path, help="directory of golden HTTP captures applied on top of --state")
    parser.add_argument("--golden", type=Path, metavar="DIR",
                        help="HIL-A capture folder (tests/fixtures/device/<fw>/): seed the state from it and "
                             "answer with the captured bytes (see tools/simulator/golden.py)")
    parser.add_argument("--report", action="store_true",
                        help="print which ASSUMPTION(HIL-A) guesses the --golden captures confirm, then exit")
    parser.add_argument("--user", help="override the login user from the state file")
    parser.add_argument("--password", help="override the login password from the state file")
    parser.add_argument("--no-tls", action="store_true", help="serve the device API over plain HTTP")
    parser.add_argument("--no-auth", action="store_true", help="accept commands without a prior login")
    parser.add_argument("--session-ttl", type=float, default=proto.DEFAULT_SESSION_TTL_S,
                        help="seconds before a login session expires (default: never)")
    parser.add_argument("--reboot-seconds", type=float, default=proto.DEFAULT_REBOOT_SECONDS,
                        help="how long a 'set reboot' keeps the device offline")
    parser.add_argument("--log-level", default="INFO", help="logging level (default INFO)")
    return parser


def load_golden(args: argparse.Namespace):  # -> GoldenSet | None
    if not args.golden:
        return None
    from .golden import GoldenSet

    return GoldenSet.load(args.golden)


def build_simulator(args: argparse.Namespace, golden=None) -> Simulator:
    state = DeviceState.load(args.state)
    if args.captures:
        state.apply_http_captures(load_capture_dir(args.captures))
    if golden is not None:
        golden.seed(state)
    if args.user is not None:
        state.auth["user"] = args.user
    if args.password is not None:
        state.auth["password"] = args.password
    return Simulator(
        state,
        host=args.host,
        https_port=args.https_port,
        telnet_port=args.telnet_port,
        control_port=args.control_port,
        tls=not args.no_tls,
        require_login=not args.no_auth,
        session_ttl_s=args.session_ttl,
        reboot_seconds=args.reboot_seconds,
        golden=golden,
    )


async def _run(sim: Simulator) -> None:
    await sim.start()
    print(
        f"BK-808 simulator ready: device={sim.device_url} telnet={sim.host}:{sim.telnet_port} "
        f"control={sim.control_url}/_sim/state",
        flush=True,
    )
    try:
        await asyncio.Event().wait()
    finally:
        await sim.stop()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    try:
        golden = load_golden(args)
        if args.report:
            from .golden import assumption_report, format_report

            print(format_report(assumption_report(golden, DeviceState.load(args.state)), golden))
            return 0
        sim = build_simulator(args, golden)
    except (OSError, StateError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if golden is not None:
        print(golden.describe(), flush=True)
        for warning in golden.warnings:
            print(f"warning: {warning}", flush=True)
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(_run(sim))
    return 0


if __name__ == "__main__":
    sys.exit(main())
