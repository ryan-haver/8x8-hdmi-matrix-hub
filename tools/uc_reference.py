"""Fetch the pinned Unfolded Circle reference sources for local use.

Reads docs/vendor/unfoldedcircle-references.json and clones each source at
its pinned ref into reference/unfoldedcircle/<name>/ (git-ignored), so the
official spec, SDK and reference integrations are available offline while
working on the Remote integration. Nothing is redistributed with the repo.

    python tools/uc_reference.py            fetch or update to the pinned refs
    python tools/uc_reference.py --check    report sources that are missing or not at their pin
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "docs" / "vendor" / "unfoldedcircle-references.json"
DEST = ROOT / "reference" / "unfoldedcircle"


def _git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _pinned_sha(source: dict) -> str:
    return source.get("ref_sha") or source["ref"]


def _current_sha(path: Path) -> str | None:
    if not (path / ".git").exists():
        return None
    return _git("rev-parse", "HEAD", cwd=path)


def fetch(source: dict) -> None:
    path = DEST / source["name"]
    if not (path / ".git").exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        _git("clone", "--quiet", "--filter=blob:none", "--no-checkout", source["repo"], str(path))
    _git("fetch", "--quiet", "origin", source["ref"], cwd=path)
    _git("checkout", "--quiet", "--detach", "FETCH_HEAD", cwd=path)
    sha = _current_sha(path)
    expected = _pinned_sha(source)
    if expected and len(expected) == 40 and sha != expected:
        raise SystemExit(f"{source['name']}: checked out {sha}, expected pinned {expected}")
    print(f"{source['name']:<28} {source['ref'][:12]:<12} -> {path.relative_to(ROOT)}")


def check(sources: list[dict]) -> int:
    problems = 0
    for source in sources:
        path = DEST / source["name"]
        sha = _current_sha(path)
        expected = _pinned_sha(source)
        if sha is None:
            print(f"MISSING  {source['name']}")
            problems += 1
        elif len(expected) == 40 and sha != expected:
            print(f"DRIFT    {source['name']}: {sha[:12]} (pinned {expected[:12]})")
            problems += 1
        else:
            print(f"OK       {source['name']} @ {sha[:12]}")
    return 1 if problems else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="only report missing or drifted sources")
    args = parser.parse_args(argv)
    sources = json.loads(MANIFEST.read_text(encoding="utf-8"))["sources"]
    if args.check:
        return check(sources)
    for source in sources:
        fetch(source)
    return 0


if __name__ == "__main__":
    sys.exit(main())
