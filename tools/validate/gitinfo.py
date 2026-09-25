"""Git facts for evidence records and staleness."""

from __future__ import annotations

import fnmatch
import os
import subprocess
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


#: Variables git sets for hooks (pre-commit runs the test suite). Inherited, they
#: would point every git call - including ones for other repositories - at the
#: repository being committed to, and at its in-progress index.
_GIT_LOCATION_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_COMMON_DIR",
                      "GIT_PREFIX", "GIT_ALTERNATE_OBJECT_DIRECTORIES")


def clean_git_env() -> dict[str, str]:
    """``os.environ`` without git's repository-location variables."""
    return {k: v for k, v in os.environ.items() if k not in _GIT_LOCATION_VARS}


def _git(*args: str, cwd: Path = ROOT) -> str:
    out = subprocess.run(  # noqa: S603 - fixed git argv
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True, env=clean_git_env()
    )
    return out.stdout.strip()


def head_sha(cwd: Path = ROOT) -> str:
    try:
        return _git("rev-parse", "HEAD", cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def branch(cwd: Path = ROOT) -> str:
    try:
        return _git("rev-parse", "--abbrev-ref", "HEAD", cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def dirty_files(cwd: Path = ROOT) -> list[str]:
    """Tracked files with uncommitted changes (staged or not)."""
    try:
        out = _git("status", "--porcelain", "--untracked-files=no", cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    files = []
    for line in out.splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        files.append(path.strip().strip('"'))
    return sorted(files)


@lru_cache(maxsize=256)
def changed_since(sha: str, cwd: Path = ROOT) -> tuple[str, ...] | None:
    """Files changed by commits after ``sha`` up to HEAD; ``None`` if ``sha`` is unknown here."""
    if not sha or sha == "unknown":
        return None
    try:
        _git("cat-file", "-e", f"{sha}^{{commit}}", cwd=cwd)
        # Only meaningful if sha is an ancestor of HEAD (evidence from this history).
        subprocess.run(  # noqa: S603
            ["git", "merge-base", "--is-ancestor", sha, "HEAD"], cwd=cwd, check=True, capture_output=True,
            env=clean_git_env(),
        )
        out = _git("diff", "--name-only", f"{sha}..HEAD", cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return tuple(sorted(p for p in out.splitlines() if p))


def matches(path: str, patterns: list[str] | tuple[str, ...]) -> bool:
    """``covers`` entries are paths or globs; a directory entry covers everything below it."""
    for pat in patterns:
        pat = pat.rstrip("/")
        if path == pat or path.startswith(pat + "/") or fnmatch.fnmatch(path, pat):
            return True
    return False
