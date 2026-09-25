"""Ledger levels, staleness and the CI gate, on a throw-away git repository."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tools.validate import gitinfo
from tools.validate.evidence import LoadedRecord, write_record
from tools.validate.ledger import compute, freshness, gate, render
from tools.validate.model import Level
from tools.validate.registry import Finding

from .helpers import make_record

#: Identity for the throw-away repository, passed through the environment so
#: the tests never write git config anywhere (a leaked GIT_DIR once made
#: `git config` in this fixture rewrite the real repository's config).
_TEST_IDENTITY = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.invalid",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.invalid",
}


def _git(repo: Path, *args: str) -> str:
    env = {**gitinfo.clean_git_env(), **_TEST_IDENTITY}
    # Signing is disabled only inside this throw-away repository.
    return subprocess.run(["git", "-c", "commit.gpgsign=false", *args], cwd=repo, check=True,
                          capture_output=True, text=True, env=env).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    (r / "src").mkdir(parents=True)
    _git(r, "init", "-q")
    # Refuse to continue unless git really created a repository in tmp_path.
    git_dir = Path(_git(r, "rev-parse", "--absolute-git-dir")).resolve()
    assert git_dir == (r / ".git").resolve(), f"git init did not create {r / '.git'} (got {git_dir})"
    (r / "src" / "a.py").write_text("a = 1\n")
    (r / "src" / "b.py").write_text("b = 1\n")
    _git(r, "add", ".")
    _git(r, "commit", "-q", "-m", "one")
    gitinfo.changed_since.cache_clear()
    return r


def _commit(repo: Path, path: str, text: str) -> str:
    (repo / path).write_text(text)
    _git(repo, "commit", "-q", "-am", f"touch {path}")
    gitinfo.changed_since.cache_clear()
    return _git(repo, "rev-parse", "HEAD")


def _rec(sha: str, covers: list[str], **over) -> LoadedRecord:
    data = make_record(commit={"sha": sha, "short": sha[:8], "dirty": False, "dirty_files": []}, covers=covers, **over)
    return LoadedRecord(Path("x.json"), data)


# ------------------------------------------------------------------ staleness


def test_freshness_follows_covered_paths(repo):
    sha1 = _git(repo, "rev-parse", "HEAD")
    rec = _rec(sha1, ["src/a.py"])
    assert freshness(rec, sha1, repo) == "fresh"
    head = _commit(repo, "src/b.py", "b = 2\n")  # unrelated change
    assert freshness(rec, head, repo) == "fresh"
    head = _commit(repo, "src/a.py", "a = 2\n")  # covered change
    assert freshness(rec, head, repo) == "stale"
    # a directory entry covers everything below it; globs work too
    assert freshness(_rec(sha1, ["src"]), head, repo) == "stale"
    assert freshness(_rec(sha1, ["src/*.py"]), head, repo) == "stale"
    assert freshness(_rec(sha1, ["web"]), head, repo) == "fresh"


def test_unknown_commit_and_dirty_files(repo):
    head = _git(repo, "rev-parse", "HEAD")
    assert freshness(_rec("f" * 40, ["src/a.py"]), head, repo) == "unknown"
    dirty = _rec(head, ["src/a.py"])
    dirty.data["commit"]["dirty_files"] = ["src/a.py"]
    assert freshness(dirty, head, repo) == "stale"
    other = _rec(head, ["src/a.py"])
    other.data["commit"]["dirty_files"] = ["docs/x.md"]
    assert freshness(other, head, repo) == "fresh"


# ------------------------------------------------------------------ levels and gate

FINDINGS = {
    "BE-01": Finding("BE-01", "C", "critical", True, "t"),
    "BE-12": Finding("BE-12", "M", "medium", True, "t"),
    "BE-99": Finding("BE-99", "H", "closed high", False, "t"),
}


def _feature(fid: str, current: str = "V1", findings=()):
    return {"id": fid, "area": "matrix", "title": fid, "claim": "c", "interfaces": {"rest": ["GET /x"]}, "target": "V4",
            "current": current, "basis": "tests/x.py", "evidence": [], "findings": list(findings), "scenarios": []}


def _write(root: Path, sha: str, fid: str, level: str, result: str, scenario: str = "routing.switch_one", **over):
    rec = make_record(features=[fid], level=level, result=result, scenario=scenario,
                      client="browser" if level == "V3" else "api",
                      gate="ok" if result == "pass" else "known-failure",
                      commit={"sha": sha, "short": sha[:8], "dirty": False, "dirty_files": []},
                      covers=["src/a.py"], **over)
    return write_record(root, rec)


def test_levels_from_evidence(repo, tmp_path):
    sha = _git(repo, "rev-parse", "HEAD")
    ev = tmp_path / "ev"
    _write(ev, sha, "F-MTX-001", "V2", "pass")
    _write(ev, sha, "F-MTX-001", "V3", "pass", scenario="routing.route_all")
    _write(ev, sha, "F-MTX-002", "V2", "pass")
    _write(ev, sha, "F-MTX-003", "V2", "fail")
    _write(ev, sha, "F-MTX-004", "V2", "pass")
    features = [_feature("F-MTX-001"), _feature("F-MTX-002", findings=["BE-01"]), _feature("F-MTX-003", "V2"),
                _feature("F-MTX-004", findings=["BE-12", "BE-99"]), _feature("F-MTX-005", "V1")]
    rows = {r.id: r for r in compute(features, FINDINGS, [ev], repo)}
    assert rows["F-MTX-001"].level is Level.V3 and rows["F-MTX-001"].proven is Level.V3
    assert rows["F-MTX-002"].level is Level.V1 and rows["F-MTX-002"].capped_by == ["BE-01"]  # open critical caps
    assert rows["F-MTX-004"].level is Level.V2  # medium and closed-high findings do not cap
    assert rows["F-MTX-004"].open_findings == ["BE-12"]
    assert rows["F-MTX-005"].level is Level.V1 and rows["F-MTX-005"].freshness == "—"  # no evidence: recorded level
    # F-MTX-003 is recorded V2 but its V2 scenario failed: that is a drop below the recorded level
    assert rows["F-MTX-003"].dropped
    errors = gate(list(rows.values()), None)
    assert any("F-MTX-003" in e and "(b)" in e for e in errors)
    assert not any("F-MTX-001" in e for e in errors)


def test_stale_evidence_falls_back_to_recorded(repo, tmp_path):
    sha = _git(repo, "rev-parse", "HEAD")
    ev = tmp_path / "ev"
    _write(ev, sha, "F-MTX-001", "V3", "pass")
    _commit(repo, "src/a.py", "a = 3\n")
    rows = compute([_feature("F-MTX-001", "V1")], FINDINGS, [ev], repo)
    assert rows[0].level is Level.V1 and rows[0].freshness == "stale" and rows[0].proven is None


def test_lower_fresh_evidence_is_a_drop(repo, tmp_path):
    sha = _git(repo, "rev-parse", "HEAD")
    ev = tmp_path / "ev"
    _write(ev, sha, "F-MTX-001", "V2", "pass")  # only V2 proven now ...
    rows = compute([_feature("F-MTX-001", "V3")], FINDINGS, [ev], repo)  # ... but V3 was recorded
    assert rows[0].dropped == ["level V2 < recorded V3"]


def test_gate_scenario_failures():
    summary = {"outcomes": [
        {"scenario": "a.b", "client": "api", "status": "fail", "gate": "known-failure",
         "failed_checks": [{"description": "x", "finding": "BE-12"}]},
        {"scenario": "c.d", "client": "api", "status": "fail", "gate": "regression",
         "failed_checks": [{"description": "device outputs[0].source == 6", "finding": None}], "reason": ""},
        {"scenario": "e.f", "client": "api", "status": "pass", "gate": "ok", "failed_checks": []},
    ]}
    errors = gate([], summary)
    assert len(errors) == 1 and "c.d" in errors[0] and "outputs[0].source" in errors[0]
    assert gate([], {"outcomes": [], "aborted": "restore failed"}) == ["run aborted: restore failed"]


def test_render(repo, tmp_path):
    sha = _git(repo, "rev-parse", "HEAD")
    ev = tmp_path / "ev"
    _write(ev, sha, "F-MTX-001", "V2", "pass")
    features = [_feature("F-MTX-001"), _feature("F-MTX-002", findings=["BE-01"])]
    rows = compute(features, FINDINGS, [ev], repo)
    text = render(rows, FINDINGS, out_path=tmp_path / "LEDGER.md", run_summary={"target": "sim", "clients": ["api"],
                  "commit": {"short": "abc"}, "outcomes": [{"status": "pass"}]})
    assert "## Summary" in text and "## Matrix control (F-MTX)" in text
    assert "| Matrix control | 2 | 0 | 1 | 1 | 0 | 0 | 0 | 2 | 0 |" in text
    assert "(capped)" in text and "BE-01(C)" in text
    assert "[routing.switch_one·api·pass](ev/F-MTX-001/" in text
