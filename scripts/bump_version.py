"""Synchronize release manifests with the canonical hub version.

Run ``python scripts/bump_version.py --check`` before a release, or pass an
explicit X.Y.Z version to update it. Packaging and the legacy ``version`` module
read hub.__version__ directly. All inputs are validated and replacements staged
before any file changes; an ordinary write failure rolls back completed writes.
This is not a multi-file transaction against process termination or power loss.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = Path("src/hub/__init__.py")
MANIFESTS = (Path("driver.json"), Path("custom_components/hdmi_matrix/manifest.json"))
RELEASE_VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\Z")


def canonical_version(root: Path) -> str:
    """Read the literal version without importing application dependencies."""
    tree = ast.parse((root / VERSION_FILE).read_bytes())
    assignments = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets)
    ]
    if len(assignments) != 1:
        raise ValueError("Expected exactly one canonical __version__ assignment")
    version = ast.literal_eval(assignments[0].value)
    if not isinstance(version, str) or not RELEASE_VERSION.fullmatch(version):
        raise ValueError("Canonical version must be an X.Y.Z release")
    return version


def version_plan(root: Path, version: str) -> dict[Path, bytes]:
    """Validate every input and return changed bytes, preserving file formatting."""
    if not RELEASE_VERSION.fullmatch(version):
        raise ValueError("Version must be X.Y.Z with no leading zeros")
    current = canonical_version(root)
    config = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    if "version" in config["project"] or config["tool"]["setuptools"]["dynamic"]["version"] != {
        "attr": "hub.__version__"
    }:
        raise ValueError("Packaging must read hub.__version__ dynamically")
    plan = {}
    source = (root / VERSION_FILE).read_bytes()
    updated, count = re.subn(
        rb'(?m)^__version__ = [\'"]' + re.escape(current.encode()) + rb'[\'"]\r?$',
        lambda match: match.group().replace(current.encode(), version.encode()),
        source,
    )
    if count != 1:
        raise ValueError("Expected a single literal __version__ line")
    plan[root / VERSION_FILE] = updated
    for relative in MANIFESTS:
        path = root / relative
        original = path.read_bytes()
        payload = json.loads(original)
        if not isinstance(payload.get("version"), str):
            raise ValueError(f"Missing string version in {relative}")
        updated, count = re.subn(
            rb'("version"\s*:\s*")[^"\r\n]*(")',
            lambda match: match[1] + version.encode() + match[2],
            original,
        )
        if count != 1:
            raise ValueError(f"Expected one version field in {relative}")
        plan[path] = updated
    return {path: content for path, content in plan.items() if path.read_bytes() != content}


def apply_plan(plan: dict[Path, bytes]) -> None:
    """Stage same-directory files, replacing atomically and rolling back on error."""
    originals = {path: path.read_bytes() for path in plan}
    staged: dict[Path, Path] = {}
    completed = []
    try:
        for path, content in plan.items():
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
                staged[path] = Path(stream.name)
                stream.write(content)
            staged[path].chmod(path.stat().st_mode)
        for path, temporary in staged.items():
            os.replace(temporary, path)
            completed.append(path)
    except OSError:
        for path in reversed(completed):
            path.write_bytes(originals[path])
        raise
    finally:
        for temporary in staged.values():
            temporary.unlink(missing_ok=True)


def main() -> int:
    """Check synchronization or set an explicit release version."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", nargs="?", help="Explicit release version (X.Y.Z)")
    parser.add_argument("--check", action="store_true", help="Check without changing files")
    args = parser.parse_args()
    if args.check and args.version:
        parser.error("--check cannot be combined with a version")
    if not args.check and args.version is None:
        parser.error("Pass a release version or --check")
    try:
        version = canonical_version(ROOT) if args.check else args.version
        plan = version_plan(ROOT, version)
        if args.check and plan:
            parser.exit(1, "Version drift: " + ", ".join(str(path.relative_to(ROOT)) for path in plan) + "\n")
        if not args.check:
            apply_plan(plan)
    except (OSError, ValueError, KeyError, SyntaxError) as error:
        parser.exit(1, f"Version update failed: {error}\n")
    print(f"Version {version}: synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
