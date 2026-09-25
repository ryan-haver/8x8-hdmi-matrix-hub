"""``python -m tools.hil.capture``: capture golden responses from a real BK-808.

See ``tools/hil/README.md`` for the HIL Session 1 runbook.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import os
import signal
import sys
from typing import Any

from .context import DEFAULT_OUT, Capture, CaptureError, Console, Options, RestoreError
from .probe_mode import probe_before_login, run_probe
from .read_mode import run_read
from .write_mode import GROUPS, OPT_IN_GROUPS, run_write

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2
EXIT_NOT_RESTORED = 3
EXIT_SECRET_LEAK = 4
EXIT_INTERRUPTED = 130

DANGER_FLAG = "--i-understand-this-changes-the-matrix"


def _csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def _floats(value: str) -> list[float]:
    try:
        return [float(v) for v in _csv(value)]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected comma-separated seconds, got {value!r}") from exc


def _port_num(value: str) -> int:
    n = int(value)
    if not 1 <= n <= 8:
        raise argparse.ArgumentTypeError("must be 1-8")
    return n


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m tools.hil.capture",
        description="Record raw BK-808 responses as golden fixtures (HIL-A, docs/REMEDIATION_PLAN.md §5.2).",
        epilog="Modes: read (default, safe), probe (login/session/Telnet semantics; mostly read-only), "
               f"write (DANGEROUS: changes routing/settings, needs {DANGER_FLAG}).",
    )
    p.add_argument("--host", required=True, help="matrix IP address or hostname (no default)")
    p.add_argument("--port", type=int, default=443, help="HTTP(S) port (default 443)")
    p.add_argument("--telnet-port", type=int, default=23, help="Telnet port (default 23)")
    p.add_argument("--no-tls", action="store_true", help="plain HTTP instead of HTTPS")
    p.add_argument("--no-telnet", action="store_true", help="skip everything that needs Telnet")
    p.add_argument("--user", default=os.environ.get("OREI_USER", "Admin"), help="login user (default Admin)")
    p.add_argument("--password", help="login password (default: $OREI_PASSWORD, else prompt). Never stored.")
    p.add_argument("--out", default=DEFAULT_OUT,
                   help="output folder; {firmware} is replaced by the name derived from the device versions "
                        f"(default {DEFAULT_OUT})")
    p.add_argument("--firmware", help="override the derived firmware folder name")
    p.add_argument("--mode", choices=("read", "write", "probe"), default="read", help="what to capture")
    p.add_argument("--redact", action="append", default=[], metavar="TEXT",
                   help="extra text to scrub from every stored file (repeatable)")
    p.add_argument("--yes", action="store_true", help="skip interactive confirmations and operator prompts")
    timing = p.add_argument_group("timing")
    timing.add_argument("--http-timeout", type=float, default=5.0, help="seconds per HTTP request (default 5)")
    timing.add_argument("--telnet-idle", type=float, default=1.0,
                        help="a Telnet response is complete after this many silent seconds (default 1.0)")
    timing.add_argument("--telnet-timeout", type=float, default=5.0, help="max seconds per Telnet response")
    timing.add_argument("--banner-idle", type=float, default=1.5, help="silence that ends the Telnet banner")
    w = p.add_argument_group("write mode (DANGEROUS)")
    w.add_argument(DANGER_FLAG, dest="i_understand", action="store_true",
                   help="required for --mode write")
    w.add_argument("--only", type=_csv, default=[], help=f"only these groups/tests (groups: {', '.join(GROUPS)})")
    w.add_argument("--skip", type=_csv, default=[], help="skip these groups/tests")
    w.add_argument("--include", type=_csv, default=[],
                   help=f"opt-in groups to add: {', '.join(OPT_IN_GROUPS)}")
    w.add_argument("--test-output", type=_port_num, default=8, help="output used for per-output tests (default 8)")
    w.add_argument("--test-input", type=_port_num, default=8, help="input used for per-input tests (default 8)")
    w.add_argument("--test-preset", type=_port_num, default=8, help="preset slot used for preset tests (default 8)")
    w.add_argument("--cec-output", type=_port_num, default=1, help="display output for --include cec-live")
    w.add_argument("--push-grace", type=float, default=0.3, help="seconds to wait for Telnet pushes after a write")
    w.add_argument("--reboot-wait", type=float, default=180.0, help="max seconds to wait for a reboot")
    pr = p.add_argument_group("probe mode")
    pr.add_argument("--idle-waits", type=_floats, default=[], metavar="S[,S...]",
                    help="idle periods (seconds) for the session-expiry probe, e.g. 60,300,900 (default: skip)")
    pr.add_argument("--push-seconds", type=float, default=30.0,
                    help="length of the front-panel push-notification window (0 = skip; default 30)")
    return p


def options_from_args(args: argparse.Namespace, *, password: str) -> Options:
    return Options(
        host=args.host, port=args.port, telnet_port=args.telnet_port, tls=not args.no_tls,
        user=args.user, password=password, out=args.out, firmware=args.firmware, mode=args.mode,
        telnet=not args.no_telnet, http_timeout=args.http_timeout, telnet_idle=args.telnet_idle,
        telnet_timeout=args.telnet_timeout, banner_idle=args.banner_idle, redact=list(args.redact),
        yes=args.yes, i_understand=args.i_understand, only=args.only, skip=args.skip, include=args.include,
        test_output=args.test_output, test_input=args.test_input, test_preset=args.test_preset,
        cec_output=args.cec_output, push_grace=args.push_grace, reboot_wait=args.reboot_wait,
        idle_waits=args.idle_waits, push_seconds=args.push_seconds,
    )


async def run_capture(opts: Options, console: Console | None = None, *,
                      after_step: Any = None) -> tuple[int, Capture]:
    """Run one capture. Returns ``(exit code, capture)``; never raises for device problems."""
    console = console or Console(interactive=None if not opts.yes else False)
    cap = Capture(opts, console)
    cap.after_step = after_step
    code = EXIT_OK
    extra: dict[str, Any] = {}
    if opts.mode == "write" and not opts.i_understand:
        console.print(f"write mode changes the live matrix; re-run with {DANGER_FLAG}")
        return EXIT_USAGE, cap
    console.print(f"Capture mode={opts.mode} target={cap.http.base_url} telnet={opts.host}:{opts.telnet_port}"
                  + ("" if opts.telnet else " (disabled)"))
    try:
        if opts.mode == "probe":
            console.print("HTTP probes (before login):")
            await probe_before_login(cap)
        login_ex = await cap.identify()
        console.print(f"Device: {cap.device}")
        console.print(f"Output: {cap.writer.root if cap.writer else '?'}")
        if opts.mode == "read":
            await run_read(cap, login_ex)
        elif opts.mode == "probe":
            await run_probe(cap)
        else:
            extra["write_outcome"] = await run_write(cap)
    except RestoreError as exc:
        cap.errors.append(str(exc))
        console.print(f"error: {exc}")
        code = EXIT_NOT_RESTORED
    except CaptureError as exc:
        cap.errors.append(str(exc))
        console.print(f"error: {exc}")
        code = EXIT_FAILED
    except asyncio.CancelledError:
        cap.errors.append("interrupted")
        code = EXIT_INTERRUPTED
    finally:
        await cap.close()
        if cap.writer is not None:
            info = cap.run_info(extra)
            if code == EXIT_INTERRUPTED:
                info["interrupted"] = True
            cap.writer.update_manifest(cap.device, info)
            leaks = cap.writer.verify_no_secrets()
            if leaks:
                console.print("SECRET FOUND IN OUTPUT - do not commit these files:")
                for leak in leaks:
                    console.print(f"  {leak}")
                code = EXIT_SECRET_LEAK
    if write_outcome := extra.get("write_outcome"):
        if write_outcome.get("restored") is False and code == EXIT_OK:
            code = EXIT_NOT_RESTORED
    if cap.errors and code == EXIT_OK:
        code = EXIT_FAILED
    if cap.writer is not None:
        console.print(f"\nWrote {len(cap.writer.written)} record(s) to {cap.writer.root}")
        for line in cap.summary_lines():
            console.print(line)
    for w in cap.warnings:
        console.print(f"warning: {w}")
    for e in cap.errors:
        console.print(f"error: {e}")
    return code, cap


def _install_interrupt_handler(console: Console) -> Any:
    """First Ctrl+C cancels the capture (which restores in ``finally``); later ones are ignored.

    Four presses force-quit (the restore log shows what was already undone).
    """
    loop = asyncio.get_running_loop()
    task = asyncio.current_task()
    presses = 0

    def handler(signum: int, frame: Any) -> None:
        nonlocal presses
        presses += 1
        if presses == 1:
            console.print("\nInterrupted - stopping and restoring the matrix. Please wait...")
            if task is not None:
                loop.call_soon_threadsafe(task.cancel)
        elif presses < 4:
            console.print(f"Restore in progress, please wait ({4 - presses} more Ctrl+C to force quit).")
        else:
            raise KeyboardInterrupt

    previous = {}
    for name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        sig = getattr(signal, name, None)
        if sig is not None:
            try:
                previous[sig] = signal.signal(sig, handler)
            except (ValueError, OSError):
                pass
    return previous


async def _main_async(opts: Options, console: Console) -> int:
    previous = _install_interrupt_handler(console)
    try:
        code, _ = await run_capture(opts, console)
        return code
    finally:
        for sig, old in previous.items():
            try:
                signal.signal(sig, old)
            except (ValueError, OSError):
                pass


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.mode == "write" and not args.i_understand:
        print(f"error: --mode write changes the live matrix; add {DANGER_FLAG} to confirm you mean it",
              file=sys.stderr)
        return EXIT_USAGE
    password = args.password if args.password is not None else os.environ.get("OREI_PASSWORD")
    if password is None:
        if sys.stdin.isatty():
            password = getpass.getpass(f"Password for {args.user}@{args.host}: ")
        else:
            print("error: no password (use --password, $OREI_PASSWORD, or run interactively)", file=sys.stderr)
            return EXIT_USAGE
    opts = options_from_args(args, password=password)
    console = Console(interactive=sys.stdin.isatty() and not args.yes)
    try:
        return asyncio.run(_main_async(opts, console))
    except KeyboardInterrupt:
        print("force-quit: check write/restore-log.jsonl and the initial snapshot", file=sys.stderr)
        return EXIT_INTERRUPTED
