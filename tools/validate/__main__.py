"""Validation CLI (docs/validation/README.md).

    python -m tools.validate list
    python -m tools.validate run [--target sim|hardware] [--client api|browser ...] [--feature F-...] [--scenario ID]
    python -m tools.validate ledger [--evidence DIR ...] [--run-summary FILE] [--out FILE]
    python -m tools.validate check  [--evidence DIR ...] [--run-summary FILE] [--expect-clients api,browser]

Exit codes: ``run`` 0 unless the stack could not start; ``check`` 1 when the
gate fails; ``ledger`` 0.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import os
import sys
from pathlib import Path

from . import ledger as ledger_mod
from .evidence import COMMITTED_EVIDENCE
from .registry import load_features, load_findings, validate_features
from .runner import DEFAULT_OUT, Runner, RunOptions
from .scenarios import discover, select


def _cmd_list(args: argparse.Namespace) -> int:
    for sc in discover().values():
        print(f"{sc.id:32} {sc.kind:7} clients={','.join(sc.clients):12} targets={','.join(sc.targets):13} "
              f"features={','.join(sc.features)}  {sc.title}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    scenarios = select(discover(), args.scenario, args.feature)
    if not scenarios:
        print("no scenarios selected", file=sys.stderr)
        return 2
    answers = {}
    if args.answers:
        answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
    if args.target == "hardware":
        if args.operator in (None, "automation"):
            print("--target hardware needs --operator <your name> (V4 evidence is attested by a person)",
                  file=sys.stderr)
            return 2
        if not args.matrix_host:
            print("--target hardware needs --matrix-host", file=sys.stderr)
            return 2
    opts = RunOptions(
        target=args.target,
        clients=tuple(args.client or ["api"]),
        out_dir=Path(args.out).resolve(),
        evidence_dir=COMMITTED_EVIDENCE if args.record else None,
        operator=args.operator or "automation",
        matrix_host=args.matrix_host,
        matrix_port=args.matrix_port,
        matrix_https=not args.no_tls,
        matrix_user=args.matrix_user,
        matrix_password=args.matrix_password or os.environ.get("MATRIX_PASSWORD", "admin"),
        telnet_port=args.telnet_port,
        hub_url=args.hub_url,
        allow_writes=args.allow_writes,
        allow_unrestorable=args.allow_unrestorable,
        answers=answers,
        interactive=args.target == "hardware" and not args.answers and sys.stdin.isatty(),
        findings=load_findings(),
    )
    runner = Runner(opts)
    outcomes = asyncio.run(runner.run(scenarios))
    counts: dict[str, int] = {}
    for o in outcomes:
        counts[o.status] = counts.get(o.status, 0) + 1
    print(f"[validate] done: {counts}; evidence in {opts.out_dir / 'evidence'}; summary {opts.out_dir / 'run-summary.json'}")
    if runner.aborted:
        print(f"[validate] ABORTED: {runner.aborted}", file=sys.stderr)
        return 3
    return 0


def _rows(args: argparse.Namespace) -> tuple[list[ledger_mod.FeatureRow], dict, dict | None]:
    features = load_features()
    findings = load_findings()
    problems = validate_features(features, findings, set(discover()))
    if problems:
        print("registry problems:\n  " + "\n  ".join(problems), file=sys.stderr)
        raise SystemExit(1)
    roots = ledger_mod.default_roots([Path(p) for p in args.evidence or []])
    summary = ledger_mod.load_run_summary(Path(args.run_summary) if args.run_summary else None)
    return ledger_mod.compute(features, findings, roots), findings, summary


def _cmd_ledger(args: argparse.Namespace) -> int:
    rows, findings, summary = _rows(args)
    out = Path(args.out).resolve()
    stamp = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC") if args.timestamp else ""
    text = ledger_mod.render(rows, findings, out_path=out, run_summary=summary, generated_at=stamp)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"[validate] ledger written to {out}")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    rows, _findings, summary = _rows(args)
    errors = ledger_mod.gate(rows, summary)
    if args.expect_clients:
        outcomes = (summary or {}).get("outcomes", [])
        for c in args.expect_clients.split(","):
            ran = [o for o in outcomes if o["client"] == c and o["status"] in ("pass", "fail")]
            if not ran:
                reasons = {o.get("reason") for o in outcomes if o["client"] == c}
                errors.append(f"client '{c}' ran no scenario ({'; '.join(r for r in reasons if r) or 'not in run'})")
    if errors:
        print("validation gate FAILED:\n  " + "\n  ".join(errors), file=sys.stderr)
        return 1
    known = [o for o in (summary or {}).get("outcomes", []) if o.get("gate") == "known-failure"]
    print(f"[validate] gate OK ({len(known)} known failure(s) linked to open findings)")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m tools.validate", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list scenarios")

    r = sub.add_parser("run", help="run scenarios and write evidence records")
    r.add_argument("--target", choices=("sim", "hardware"), default="sim")
    r.add_argument("--client", action="append", choices=("api", "browser", "ha", "uc", "flic"),
                   help="repeatable; default api")
    r.add_argument("--feature", action="append", help="only scenarios proving this feature (repeatable)")
    r.add_argument("--scenario", action="append", help="only this scenario id (repeatable)")
    r.add_argument("--out", default=str(DEFAULT_OUT), help="output dir (evidence/, artifacts/, logs/, run-summary.json)")
    r.add_argument("--operator", help="who ran it ('automation' for CI; a person's name for hardware)")
    r.add_argument("--record", action="store_true",
                   help="write evidence into docs/validation/evidence (milestone/hardware records to commit)")
    hw = r.add_argument_group("hardware target (never used by CI)")
    hw.add_argument("--matrix-host")
    hw.add_argument("--matrix-port", type=int, default=443)
    hw.add_argument("--no-tls", action="store_true", help="device API over plain HTTP")
    hw.add_argument("--matrix-user", default="Admin")
    hw.add_argument("--matrix-password", help="default: $MATRIX_PASSWORD or 'admin'")
    hw.add_argument("--telnet-port", type=int, default=23)
    hw.add_argument("--hub-url", help="use an already running hub instead of starting run.py")
    hw.add_argument("--allow-writes", action="store_true", help="run scenarios that change the matrix (restored after)")
    hw.add_argument("--allow-unrestorable", action="store_true", help="also run scenarios whose changes cannot be restored")
    hw.add_argument("--answers", help="JSON {scenario id: [{answer, media}]} for observe steps (else prompted)")

    for name in ("ledger", "check"):
        s = sub.add_parser(name, help="generate LEDGER.md" if name == "ledger" else "CI gate")
        s.add_argument("--evidence", action="append", help="extra evidence dir (e.g. build/validation/evidence)")
        s.add_argument("--run-summary", help="run-summary.json of the run to gate/show")
        if name == "ledger":
            s.add_argument("--out", default=str(ledger_mod.LEDGER_FILE))
            s.add_argument("--timestamp", action="store_true", help="stamp the generation time (CI artifacts)")
        else:
            s.add_argument("--expect-clients", help="comma-separated clients that must have run scenarios")

    args = p.parse_args(argv)
    handler = {"list": _cmd_list, "run": _cmd_run, "ledger": _cmd_ledger, "check": _cmd_check}[args.cmd]
    return handler(args)


if __name__ == "__main__":
    sys.exit(main())
