"""Scenario discovery: every ``Scenario`` defined in ``tests/validation/scenarios/*.py``."""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from .model import Scenario

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_PACKAGE = "tests.validation.scenarios"


def discover() -> dict[str, Scenario]:
    """``{scenario id: Scenario}`` from every module's ``SCENARIOS`` list."""
    pkg = importlib.import_module(SCENARIO_PACKAGE)
    found: dict[str, Scenario] = {}
    for mod in sorted(pkgutil.iter_modules(pkg.__path__), key=lambda m: m.name):
        if mod.name.startswith("_"):
            continue
        module = importlib.import_module(f"{SCENARIO_PACKAGE}.{mod.name}")
        for sc in getattr(module, "SCENARIOS", []):
            if not isinstance(sc, Scenario):
                raise TypeError(f"{module.__name__}.SCENARIOS contains {sc!r}")
            if sc.id in found:
                raise ValueError(f"duplicate scenario id {sc.id} ({module.__name__})")
            found[sc.id] = sc
    return found


def select(scenarios: dict[str, Scenario], ids: list[str] | None = None,
           features: list[str] | None = None) -> list[Scenario]:
    chosen = list(scenarios.values())
    if ids:
        unknown = [i for i in ids if i not in scenarios]
        if unknown:
            raise SystemExit(f"unknown scenario(s): {', '.join(unknown)}")
        chosen = [s for s in chosen if s.id in ids]
    if features:
        chosen = [s for s in chosen if s.all_features & set(features)]
    return chosen
