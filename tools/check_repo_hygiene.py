"""Repository hygiene guard (BE-27, docs/REMEDIATION_PLAN.md Phase 6).

Fails when a change commits files that do not belong in the repository:

* binaries and traffic captures: ``*.bin``, ``*.exe``, ``*.c4z``, ``*.har`` (any case)
* runtime leftovers: ``__pycache__/``, ``*.pyc``/``*.pyo``, ``*.egg-info/`` anywhere,
  and ``*.lock`` / ``config_state.json`` under ``src/``
* files over 2 MB stored in Git itself instead of as a Git LFS pointer

Only the change is checked: files added between the merge base of BASE and HEAD,
and files whose size grows past the limit there. Files already in the base are
not re-litigated; an existing file that was already over the limit only warns
when it is modified. Sizes are read from the committed Git objects, so a file
committed through Git LFS is measured as its small pointer, and a file that
.gitattributes routes to LFS but was committed without LFS installed is caught.

    python -m tools.check_repo_hygiene --base origin/main   check the change since the merge base
    python -m tools.check_repo_hygiene --all                check every file in HEAD

When BASE is empty, all zeros (a new branch or tag push) or not in the clone
(a force push), every file in HEAD is checked instead; there is no allow-list,
so any oversized or blocked file then fails. Paths are read with
``-z``, so spaces, newlines, quotes and non-ASCII names are handled as-is.
Exit status: 0 clean, 1 problems found, 2 Git error.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from tools.validate.gitinfo import clean_git_env

MAX_BYTES = 2 * 1024 * 1024
BLOCKED_SUFFIXES = (".bin", ".exe", ".c4z", ".har")
BYTECODE_SUFFIXES = (".pyc", ".pyo")
SRC_LEFTOVER_NAMES = ("config_state.json",)
SRC_LEFTOVER_SUFFIXES = (".lock",)
# A 40-hex all-zero SHA is what GitHub sends as `before` for a new branch or tag.
NULL_SHA = "0" * 40


class GitError(RuntimeError):
    pass


@dataclass(frozen=True)
class Problem:
    path: str
    message: str
    level: str = "error"


def _git(repo: Path, *args: str) -> bytes:
    # clean_git_env: under a Git hook (pre-commit runs the tests) GIT_DIR, GIT_INDEX_FILE
    # etc. point at the repository being committed to and would override `-C repo`.
    result = subprocess.run(  # noqa: S603 - fixed git argv
        ["git", "-C", str(repo), "-c", "core.quotePath=false", *args],  # noqa: S607
        capture_output=True,
        check=False,
        env=clean_git_env(),
    )
    if result.returncode != 0:
        raise GitError(f"git {' '.join(args)}: {result.stderr.decode('utf-8', 'replace').strip()}")
    return result.stdout


def _decode(raw: bytes) -> str:
    # surrogateescape keeps non-UTF-8 names distinct and round-trippable.
    return raw.decode("utf-8", "surrogateescape")


def _commit_exists(repo: Path, ref: str) -> bool:
    try:
        _git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
    except GitError:
        return False
    return True


def blob_sizes(repo: Path, commit: str) -> dict[str, int]:
    """Path -> size in bytes of every blob in `commit` (submodules are skipped)."""
    sizes: dict[str, int] = {}
    for entry in _git(repo, "ls-tree", "-r", "-z", "-l", "--full-tree", commit).split(b"\0"):
        if not entry:
            continue
        meta, _, path = entry.partition(b"\t")
        _mode, kind, _sha, size = meta.split(maxsplit=3)
        if kind == b"blob":
            sizes[_decode(path)] = int(size)
    return sizes


def changed_paths(repo: Path, base: str, head: str) -> dict[str, str]:
    """Path -> status letter (A, M, T, D) between `base` and `head`, renames split into D + A."""
    out = _git(repo, "diff", "--no-renames", "--no-ext-diff", "--name-status", "-z", base, head)
    tokens = out.split(b"\0")
    changes: dict[str, str] = {}
    for status, path in zip(tokens[0::2], tokens[1::2], strict=False):
        if status:
            changes[_decode(path)] = _decode(status)[:1]
    return changes


def name_problem(path: str) -> str | None:
    """Why a newly added path is not allowed, or None."""
    pure = PurePosixPath(path)
    suffix = pure.suffix.lower()
    parts = pure.parts
    if suffix in BLOCKED_SUFFIXES:
        return f"{suffix} files are not committed (binaries, firmware, driver packages and HAR captures stay out of Git)"
    if "__pycache__" in parts[:-1] or suffix in BYTECODE_SUFFIXES:
        return "Python bytecode is a build artefact"
    if any(part.lower().endswith(".egg-info") for part in parts[:-1]):
        return "*.egg-info is packaging output"
    if parts and parts[0] == "src":
        if pure.name.lower() in SRC_LEFTOVER_NAMES or suffix in SRC_LEFTOVER_SUFFIXES:
            return "runtime state under src/ (the hub writes it to DATA_DIR)"
    return None


def _size_text(size: int) -> str:
    return f"{size / (1024 * 1024):.1f} MB"


def check(repo: Path, base: str | None, head: str = "HEAD", max_bytes: int = MAX_BYTES) -> tuple[list[Problem], str]:
    """Problems in the change from merge-base(base, head) to head; the second value describes the scope."""
    if not _commit_exists(repo, head):
        raise GitError(f"{head} is not a commit")
    head_sizes = blob_sizes(repo, head)
    base_sizes: dict[str, int] = {}
    if base and base != NULL_SHA and _commit_exists(repo, base):
        merge_base = _decode(_git(repo, "merge-base", base, head)).strip()
        changes = changed_paths(repo, merge_base, head)
        base_sizes = blob_sizes(repo, merge_base)
        scope = f"changes since {merge_base[:12]}"
    else:
        changes = {path: "A" for path in head_sizes}
        scope = "every file in HEAD" if not base or base == NULL_SHA else f"every file in HEAD ({base} is not in this clone)"

    problems: list[Problem] = []
    for path, status in sorted(changes.items()):
        if status == "D" or path not in head_sizes:
            continue
        if status == "A":
            reason = name_problem(path)
            if reason:
                problems.append(Problem(path, reason))
        size = head_sizes[path]
        if size <= max_bytes:
            continue
        message = (
            f"is {_size_text(size)} in Git (limit {_size_text(max_bytes)}); "
            "store it with Git LFS (.gitattributes) or keep it out of the repository"
        )
        if base_sizes.get(path, 0) > max_bytes:
            problems.append(Problem(path, f"{message} (already over the limit before this change)", "warning"))
        else:
            problems.append(Problem(path, message))
    return problems, scope


def _escape_data(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _escape_property(value: str) -> str:
    return _escape_data(value).replace(":", "%3A").replace(",", "%2C")


def format_problem(problem: Problem, github: bool) -> str:
    if github:
        return (
            f"::{problem.level} file={_escape_property(problem.path)},title=Repository hygiene::"
            f"{_escape_data(problem.path)} {_escape_data(problem.message)}"
        )
    return f"{problem.level}: {problem.path!r} {problem.message}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--base", help="base commit or ref; the change since its merge base with HEAD is checked")
    scope.add_argument("--all", action="store_true", help="check every file in HEAD")
    parser.add_argument("--head", default="HEAD", help="commit to check (default HEAD)")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="repository (default: current directory)")
    args = parser.parse_args(argv)

    github = os.environ.get("GITHUB_ACTIONS") == "true"
    try:
        problems, described = check(args.repo, None if args.all else args.base, args.head)
    except GitError as exc:
        print(f"check_repo_hygiene: {exc}", file=sys.stderr)
        return 2

    out = sys.stdout
    for problem in problems:
        line = format_problem(problem, github)
        out.write(line.encode(out.encoding or "utf-8", "backslashreplace").decode(out.encoding or "utf-8") + "\n")
    errors = sum(1 for p in problems if p.level == "error")
    print(f"Repository hygiene: {errors} error(s), {len(problems) - errors} warning(s) in {described}.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
