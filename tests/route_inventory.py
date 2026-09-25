"""Route inventory: which REST routes does the test suite actually exercise?

Validation strategy L3 (docs/REMEDIATION_PLAN.md §5): every route registered
by ``rest_api.app.create_rest_app`` should be hit by at least one test.

How it works
    * During the session, every request that an aiohttp app resolves to a
      registered route (via ``UrlDispatcher.resolve``) is recorded as
      ``(METHOD, canonical path)``, e.g. ``("POST", "/api/output/{output}/source")``.
      This covers every test client, however the app was built.
    * At session end, the full inventory is built from a throwaway
      ``create_rest_app()`` (auto-generated ``HEAD`` routes are ignored), the
      two sets are compared, ``route-coverage.json`` is written to the rootdir
      and a ``Route coverage: X/Y`` summary with the uncovered routes is printed.

Report-only for now. Set ``ROUTE_COVERAGE_STRICT=1`` to make the session fail
when any route is uncovered (planned to become the default at the Phase 2 exit).
Only use strict mode for full-suite runs; a partial run naturally covers fewer
routes.

Nothing is reported when the session never imported ``rest_api`` (for example
when running only ``tests/ha``).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

REPORT_FILE = "route-coverage.json"
STRICT_ENV = "ROUTE_COVERAGE_STRICT"

_hits: set[tuple[str, str]] = set()
_result: dict | None = None
_original_resolve = None


def _install_recorder() -> None:
    global _original_resolve
    from aiohttp.web_urldispatcher import UrlDispatcher

    if _original_resolve is not None:
        return
    _original_resolve = UrlDispatcher.resolve

    async def _recording_resolve(self, request):
        match_info = await _original_resolve(self, request)
        if match_info.http_exception is None:
            route = match_info.route
            resource = route.resource
            if resource is not None:
                _hits.add((route.method.upper(), resource.canonical))
        return match_info

    UrlDispatcher.resolve = _recording_resolve


def _uninstall_recorder() -> None:
    global _original_resolve
    if _original_resolve is None:
        return
    from aiohttp.web_urldispatcher import UrlDispatcher

    UrlDispatcher.resolve = _original_resolve
    _original_resolve = None


def registered_routes() -> set[tuple[str, str]]:
    """Return ``{(METHOD, canonical path)}`` for every route of the REST app."""
    from rest_api.app import create_rest_app

    with tempfile.TemporaryDirectory(prefix="route-inventory-") as tmp:
        app = create_rest_app(Path(tmp))
        routes = set()
        for route in app.router.routes():
            if route.method.upper() == "HEAD":  # added implicitly by add_get()
                continue
            resource = route.resource
            if resource is None:
                continue
            routes.add((route.method.upper(), resource.canonical))
    return routes


def _fmt(route: tuple[str, str]) -> str:
    return f"{route[0]} {route[1]}"


def pytest_configure(config: pytest.Config) -> None:
    _hits.clear()
    try:
        _install_recorder()
    except ImportError:  # pragma: no cover - aiohttp is always installed
        pass


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    global _result
    _result = None
    if "rest_api" not in sys.modules or not _hits:
        return

    inventory = registered_routes()
    covered = sorted(inventory & _hits)
    uncovered = sorted(inventory - _hits)
    total = len(inventory)
    _result = {
        "covered": len(covered),
        "total": total,
        "percent": round(100.0 * len(covered) / total, 1) if total else 100.0,
        "strict": os.environ.get(STRICT_ENV) == "1",
        "uncovered": [_fmt(r) for r in uncovered],
        "covered_routes": [_fmt(r) for r in covered],
    }
    report_path = Path(session.config.rootpath) / REPORT_FILE
    report_path.write_text(json.dumps(_result, indent=2) + "\n", encoding="utf-8")
    _result["report_path"] = str(report_path)

    if _result["strict"] and uncovered and session.exitstatus == pytest.ExitCode.OK:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(terminalreporter, exitstatus: int, config: pytest.Config) -> None:
    if _result is None:
        return
    tr = terminalreporter
    tr.section("route inventory")
    tr.write_line(
        f"Route coverage: {_result['covered']}/{_result['total']} ({_result['percent']}%) "
        f"-> {_result['report_path']}"
    )
    if _result["uncovered"]:
        mode = "FAILING (ROUTE_COVERAGE_STRICT=1)" if _result["strict"] else "report-only"
        tr.write_line(f"Uncovered routes ({len(_result['uncovered'])}, {mode}):")
        for line in _result["uncovered"]:
            tr.write_line(f"  {line}")


def pytest_unconfigure(config: pytest.Config) -> None:
    _uninstall_recorder()
