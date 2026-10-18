"""Repository hygiene guard, Docker build context and CI supply-chain contracts
(docs/REMEDIATION_PLAN.md Phase 6: BE-27, DEP-09, DEP-12, SEC-15).

* tools/check_repo_hygiene.py runs against throw-away Git repositories built in
  tmp_path, with the user's global and system Git config switched off so local
  hooks, LFS filters or autocrlf cannot change what gets committed. Paths are
  written straight into the index, so names Windows cannot create on disk
  (newlines, quotes, colons) are covered on every platform.
* The Dockerfile, .dockerignore, workflows and Dependabot config are read as
  files: digest-pinned base images, SHA-pinned actions, the hygiene job wired
  into CI and in front of `publish`, amd64 + arm64 publishing.
* Tests marked ``docker`` (deselected by default; CI runs them in the
  docker-build job) export the real build context through BuildKit and check
  what .dockerignore lets through.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
import yaml

from tests.deploy._docker import docker, docker_available
from tools import check_repo_hygiene as hygiene
from tools.validate.gitinfo import clean_git_env

ROOT = Path(__file__).resolve().parent.parent
DOCKERFILE = ROOT / "Dockerfile"
DOCKERIGNORE = ROOT / ".dockerignore"
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
CI = ROOT / ".github" / "workflows" / "ci.yml"
DEPENDABOT = ROOT / ".github" / "dependabot.yml"

SHA_PIN = re.compile(r"^[\w.-]+/[\w.-]+(/[\w./-]+)?@[0-9a-f]{40}$")
DIGEST_PIN = re.compile(r"^[\w./:-]+:[\w.-]+@sha256:[0-9a-f]{64}$")
#: What Git exports to hooks (pre-commit runs this module): inherited, they would point
#: `git -C <tmp repo>` at the checkout being committed to.
GIT_LOCATION_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY", "GIT_COMMON_DIR",
                     "GIT_PREFIX", "GIT_ALTERNATE_OBJECT_DIRECTORIES")
#: Blobs over the limit that predate the guard, by exact content; only the
#: repository self-test tolerates them (the guard itself has no allow-list).
#: Remove an entry once the file is shrunk or moved to LFS.
PRE_GUARD_OVERSIZED = {
    "web/assets/icons/svg/_icon-paths.json": "a861e8e812674b56ca878e30909de49b565514d2",
}
LFS_POINTER = (
    b"version https://git-lfs.github.com/spec/v1\n"
    b"oid sha256:" + b"a" * 64 + b"\n"
    b"size 3145728\n"
)


# ---------------------------------------------------------------------------
# Throw-away Git repositories
# ---------------------------------------------------------------------------


class Repo:
    def __init__(self, path: Path) -> None:
        self.path = path

    def git(self, *args: str, stdin: bytes | None = None) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.path), *args], input=stdin, capture_output=True, check=True, env=clean_git_env(),
        )
        return result.stdout.decode("utf-8", "replace").strip()

    def add(self, path: str, data: bytes = b"x\n") -> None:
        """Stage `data` at `path` without touching the file system (any byte-legal name works)."""
        blob = self.git("hash-object", "-w", "--stdin", stdin=data)
        self.git("update-index", "-z", "--index-info", stdin=f"100644 {blob}\t{path}\0".encode())
        assert path in self.git("ls-files", "-z", "--cached").split("\0"), f"{path!r} was not staged"

    def remove(self, path: str) -> None:
        self.git("update-index", "-z", "--force-remove", "--stdin", stdin=f"{path}\0".encode())

    def commit(self, message: str = "change") -> str:
        self.git("commit", "--quiet", "--allow-empty", "--no-verify", "-m", message)
        return self.git("rev-parse", "HEAD")

    def check(self, base: str | None) -> tuple[list[hygiene.Problem], str]:
        return hygiene.check(self.path, base)


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Repo]:
    for var in GIT_LOCATION_VARS:
        monkeypatch.delenv(var, raising=False)
    empty = tmp_path / "gitconfig"
    empty.write_text("", encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    path = tmp_path / "repo"
    path.mkdir()
    r = Repo(path)
    r.git("init", "--quiet", "--initial-branch=main")
    r.git("config", "user.name", "Hygiene Test")
    r.git("config", "user.email", "hygiene@example.invalid")
    # Git for Windows silently drops index paths NTFS cannot store (":", '"', newlines);
    # nothing here is checked out, so allow every name Git itself allows.
    r.git("config", "core.protectNTFS", "false")
    r.add("README.md", b"# test\n")
    r.commit("base")
    yield r


def errors(problems: list[hygiene.Problem]) -> dict[str, str]:
    return {p.path: p.message for p in problems if p.level == "error"}


def warnings(problems: list[hygiene.Problem]) -> dict[str, str]:
    return {p.path: p.message for p in problems if p.level == "warning"}


# ---------------------------------------------------------------------------
# Blocked file types
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    ["firmware/update.bin", "tools/Setup.EXE", "dist/orei-matrix.c4z", "captures/session one.har", "a.BiN"],
)
def test_new_blocked_file_types_are_rejected(repo: Repo, path: str) -> None:
    base = repo.git("rev-parse", "HEAD")
    repo.add(path)
    repo.add("docs/ok.md")
    repo.commit()
    problems, scope = repo.check(base)
    assert set(errors(problems)) == {path}
    assert "not committed" in errors(problems)[path]
    assert scope.startswith("changes since ")


@pytest.mark.parametrize(
    "path",
    [
        "captures/line\nbreak.har",
        'dir with "quotes"/x.bin',
        "-leading-dash.exe",
        "colon:comma,percent%.c4z",
        "unicodé/żółw.bin",
        "tab\there.har",
    ],
)
def test_awkward_file_names_are_read_exactly(repo: Repo, path: str) -> None:
    base = repo.git("rev-parse", "HEAD")
    repo.add(path)
    repo.commit()
    problems, _ = repo.check(base)
    assert list(errors(problems)) == [path]


def test_rename_to_a_blocked_name_is_rejected(repo: Repo) -> None:
    repo.add("capture.txt", b"GET / HTTP/1.1\n" * 50)
    base = repo.commit()
    repo.remove("capture.txt")
    repo.add("capture.har", b"GET / HTTP/1.1\n" * 50)
    repo.commit("rename")
    assert repo.git("diff", "--name-status", "-M", base, "HEAD").startswith("R")
    problems, _ = repo.check(base)
    assert set(errors(problems)) == {"capture.har"}


def test_existing_and_deleted_blocked_files_pass(repo: Repo) -> None:
    repo.add("legacy/old.bin")
    repo.add("legacy/gone.exe")
    base = repo.commit("legacy binaries")
    repo.add("legacy/old.bin", b"changed\n")
    repo.remove("legacy/gone.exe")
    repo.add("src/new.py", b"print('ok')\n")
    repo.commit()
    assert repo.check(base)[0] == []


def test_only_changes_since_the_merge_base_are_checked(repo: Repo) -> None:
    main = repo.git("rev-parse", "HEAD")
    repo.git("checkout", "--quiet", "-b", "feature")
    repo.add("feature.txt")
    repo.commit("feature")
    repo.git("checkout", "--quiet", "main")
    repo.add("landed-on-main.bin")
    main_tip = repo.commit("main moved on")
    repo.git("checkout", "--quiet", "feature")
    # main gained a blocked file after the branch point: not this branch's change.
    problems, scope = repo.check(main_tip)
    assert problems == []
    assert main[:12] in scope


# ---------------------------------------------------------------------------
# Runtime leftovers (BE-27)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "src/driver.lock",
        "src/config_state.json",
        "src/ucapi_orei_hdmi_matrix.egg-info/PKG-INFO",
        "tools/__pycache__/x.cpython-312.pyc",
        "src/hub/stale.pyc",
    ],
)
def test_runtime_leftovers_are_rejected(repo: Repo, path: str) -> None:
    base = repo.git("rev-parse", "HEAD")
    repo.add(path)
    repo.commit()
    assert set(errors(repo.check(base)[0])) == {path}


@pytest.mark.parametrize(
    "path", ["package-lock.json", "tests/fixtures/config_state.json", "docs/lockfiles.md", "src/_process_lock.py"],
)
def test_similar_legitimate_names_pass(repo: Repo, path: str) -> None:
    base = repo.git("rev-parse", "HEAD")
    repo.add(path)
    repo.commit()
    assert repo.check(base)[0] == []


# ---------------------------------------------------------------------------
# Size limit (2 MB outside Git LFS)
# ---------------------------------------------------------------------------


def test_files_over_the_limit_are_rejected_and_at_the_limit_pass(repo: Repo) -> None:
    base = repo.git("rev-parse", "HEAD")
    repo.add("assets/at-limit.json", b"a" * hygiene.MAX_BYTES)
    repo.add("assets/over.json", b"a" * (hygiene.MAX_BYTES + 1))
    repo.commit()
    problems = errors(repo.check(base)[0])
    assert set(problems) == {"assets/over.json"}
    assert "Git LFS" in problems["assets/over.json"]


def test_lfs_pointer_passes_but_lfs_file_committed_raw_is_rejected(repo: Repo) -> None:
    repo.add(".gitattributes", b"*.psd filter=lfs diff=lfs merge=lfs -text\n")
    base = repo.commit("lfs attributes")
    repo.add("art/pointer.psd", LFS_POINTER)
    repo.add("art/raw.psd", b"\x00" * (3 * 1024 * 1024))
    repo.commit()
    assert set(errors(repo.check(base)[0])) == {"art/raw.psd"}


def test_file_growing_past_the_limit_is_rejected(repo: Repo) -> None:
    repo.add("data/table.json", b"{}")
    base = repo.commit("small table")
    repo.add("data/table.json", b"a" * (hygiene.MAX_BYTES + 10))
    repo.commit("big table")
    assert set(errors(repo.check(base)[0])) == {"data/table.json"}


def test_already_oversized_file_only_warns_when_modified(repo: Repo) -> None:
    repo.add("data/big.json", b"a" * (hygiene.MAX_BYTES + 10))
    base = repo.commit("pre-existing big file")
    repo.add("data/big.json", b"b" * (hygiene.MAX_BYTES + 20))
    repo.commit()
    problems = repo.check(base)[0]
    assert errors(problems) == {}
    assert "already over the limit" in warnings(problems)["data/big.json"]


@pytest.mark.parametrize("path", sorted(PRE_GUARD_OVERSIZED))
def test_no_path_is_exempt_from_the_size_limit(repo: Repo, path: str) -> None:
    repo.add(path, b"[]")
    base = repo.commit("small")
    repo.add(path, b"a" * (hygiene.MAX_BYTES + 1))
    repo.commit("grown past the limit")
    assert set(errors(repo.check(base)[0])) == {path}
    problems, scope = repo.check(None)
    assert set(errors(problems)) == {path}
    assert scope == "every file in HEAD"


# ---------------------------------------------------------------------------
# Base selection (CI push events)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("base", ["", hygiene.NULL_SHA, "1234567890abcdef1234567890abcdef12345678"])
def test_missing_base_falls_back_to_every_file(repo: Repo, base: str) -> None:
    repo.add("old/blob.bin")
    repo.commit()
    problems, scope = repo.check(base)
    assert set(errors(problems)) == {"old/blob.bin"}
    assert scope.startswith("every file in HEAD")


def test_bad_head_is_a_git_error(repo: Repo) -> None:
    with pytest.raises(hygiene.GitError):
        hygiene.check(repo.path, None, head="no-such-ref")
    assert hygiene.main(["--all", "--head", "no-such-ref", "--repo", str(repo.path)]) == 2


# ---------------------------------------------------------------------------
# Output and command line
# ---------------------------------------------------------------------------


def test_github_annotations_escape_paths() -> None:
    problem = hygiene.Problem("a,b:c%\nd.bin", "msg 100%")
    line = hygiene.format_problem(problem, github=True)
    assert line.startswith("::error file=a%2Cb%3Ac%25%0Ad.bin,title=Repository hygiene::")
    assert line.endswith("a,b:c%25%0Ad.bin msg 100%25")
    assert "\n" not in line


def test_main_exit_codes_and_plain_output(
    repo: Repo, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    base = repo.git("rev-parse", "HEAD")
    assert hygiene.main(["--base", base, "--repo", str(repo.path)]) == 0
    repo.add("blob.exe")
    repo.commit()
    assert hygiene.main(["--base", base, "--repo", str(repo.path)]) == 1
    out = capsys.readouterr().out
    assert "error: 'blob.exe'" in out
    assert "1 error(s), 0 warning(s)" in out


def test_module_entry_point_emits_github_annotations(repo: Repo) -> None:
    base = repo.git("rev-parse", "HEAD")
    repo.add("payload.c4z")
    repo.commit()
    result = subprocess.run(
        [sys.executable, "-m", "tools.check_repo_hygiene", "--base", base, "--repo", str(repo.path)],
        cwd=ROOT, capture_output=True, text=True, env={**_clean_env(), "GITHUB_ACTIONS": "true"},
    )
    assert result.returncode == 1, result.stderr
    assert "::error file=payload.c4z,title=Repository hygiene::" in result.stdout


def _clean_env() -> dict[str, str]:
    return {k: v for k, v in os.environ.items() if k != "GITHUB_ACTIONS"}


def test_this_repository_passes_a_full_tree_check() -> None:
    if not (ROOT / ".git").exists():
        pytest.skip("not a Git checkout")
    problems, _ = hygiene.check(ROOT, None)
    tolerated = {
        path for path, sha in PRE_GUARD_OVERSIZED.items()
        if _blob_sha(ROOT, path) == sha and "Git LFS" in errors(problems).get(path, "")
    }
    assert set(errors(problems)) - tolerated == set()


def _blob_sha(repo: Path, path: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", f"HEAD:{path}"], capture_output=True, text=True, env=clean_git_env(),
    )
    return result.stdout.strip() if result.returncode == 0 else None


def test_hook_environment_cannot_redirect_the_guard(repo: Repo, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Under a Git hook GIT_DIR & co. point at the checkout being committed; the guard must ignore them."""
    parent = Repo(tmp_path / "parent")
    parent.path.mkdir()
    parent.git("init", "--quiet", "--initial-branch=main")
    parent.git("config", "user.name", "Parent")
    parent.git("config", "user.email", "parent@example.invalid")
    (parent.path / "tracked.txt").write_text("parent\n", encoding="utf-8")
    parent.git("add", "tracked.txt")
    parent_head = parent.commit("parent")
    (parent.path / "staged.txt").write_text("in progress\n", encoding="utf-8")
    parent.git("add", "staged.txt")
    index = parent.path / ".git" / "index"
    before = (parent.git("ls-files", "--stage", "-z"), parent.git("status", "--porcelain=v1", "-z"))

    base = repo.git("rev-parse", "HEAD")
    repo.add("payload.bin")
    repo.commit()

    git_dir = parent.path / ".git"
    poison = {"GIT_DIR": git_dir, "GIT_WORK_TREE": parent.path, "GIT_INDEX_FILE": index,
              "GIT_OBJECT_DIRECTORY": git_dir / "objects", "GIT_COMMON_DIR": git_dir, "GIT_PREFIX": ""}
    for var, value in poison.items():
        monkeypatch.setenv(var, str(value))

    problems, _ = hygiene.check(repo.path, base)
    assert set(errors(problems)) == {"payload.bin"}
    result = subprocess.run(
        [sys.executable, "-m", "tools.check_repo_hygiene", "--base", base, "--repo", str(repo.path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "payload.bin" in result.stdout

    for var in poison:
        monkeypatch.delenv(var)
    assert parent.git("rev-parse", "HEAD") == parent_head
    assert (parent.git("ls-files", "--stage", "-z"), parent.git("status", "--porcelain=v1", "-z")) == before
    assert "payload.bin" not in parent.git("log", "--all", "--name-only", "--format=")


# ---------------------------------------------------------------------------
# Dockerfile and .dockerignore (DEP-09, SEC-15)
# ---------------------------------------------------------------------------


def _dockerfile_instructions() -> list[tuple[str, str]]:
    text = DOCKERFILE.read_text(encoding="utf-8").replace("\\\n", " ")
    out = []
    for line in text.splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            keyword, _, rest = line.partition(" ")
            out.append((keyword.upper(), rest.strip()))
    return out


def _copy_sources() -> set[str]:
    sources: set[str] = set()
    for keyword, rest in _dockerfile_instructions():
        if keyword in ("COPY", "ADD"):
            args = [a for a in rest.split() if not a.startswith("--")]
            assert not any(a.startswith("--from") for a in rest.split()), "multi-stage COPY: update this test"
            sources.update(args[:-1])
    return sources


def _dockerignore_rules() -> list[str]:
    lines = DOCKERIGNORE.read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def test_every_external_base_image_is_digest_pinned() -> None:
    stages: set[str] = set()
    external = []
    for keyword, rest in _dockerfile_instructions():
        if keyword != "FROM":
            continue
        parts = rest.split()
        image = parts[0]
        if image.lower() not in stages:
            external.append(image)
        if len(parts) == 3 and parts[1].upper() == "AS":
            stages.add(parts[2].lower())
    assert external, "no FROM image found"
    for image in external:
        assert DIGEST_PIN.match(image), f"{image} is not pinned as name:tag@sha256:<digest>"


def test_dockerignore_is_an_allow_list_matching_the_copy_sources() -> None:
    rules = _dockerignore_rules()
    assert rules[0] == "*", "the context must start from deny-all"
    allowed = {r[1:].rstrip("/") for r in rules if r.startswith("!")}
    sources = {s.rstrip("/") for s in _copy_sources()}
    assert sources == allowed, f"COPY sources {sorted(sources)} != .dockerignore allow-list {sorted(allowed)}"


@pytest.mark.parametrize(
    "rule",
    [
        "**/__pycache__/", "**/*.egg-info/", "**/*.lock", "**/config_state.json", "**/node_modules/",
        "**/.env", "**/*.pem", "**/*.key", "**/*.bin", "**/*.exe", "**/*.c4z", "**/*.har",
    ],
)
def test_dockerignore_excludes_leftovers_secrets_and_binaries_inside_allowed_folders(rule: str) -> None:
    rules = _dockerignore_rules()
    assert rule in rules
    # Exclusions only work if no later `!` rule re-includes them.
    assert all(not r.startswith("!") for r in rules[rules.index(rule):])


# ---------------------------------------------------------------------------
# Workflows and Dependabot (SEC-15, DEP-12)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ci() -> dict:
    return yaml.safe_load(CI.read_text(encoding="utf-8"))


def _steps(workflow: dict) -> Iterator[tuple[str, dict]]:
    for job_id, job in workflow["jobs"].items():
        for step in job.get("steps", []):
            yield job_id, step


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda p: p.name)
def test_every_action_is_sha_pinned_with_a_version_comment(workflow: Path) -> None:
    text = workflow.read_text(encoding="utf-8")
    uses_lines = re.findall(r"^\s*-?\s*uses:\s*(\S+)(.*)$", text, flags=re.M)
    assert uses_lines
    for ref, rest in uses_lines:
        if ref.startswith("./"):
            continue
        assert SHA_PIN.match(ref), f"{workflow.name}: {ref} is not pinned to a full commit SHA"
        assert re.match(r"\s+#\s*\S+", rest), f"{workflow.name}: {ref} has no `# version` comment"


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda p: p.name)
def test_job_containers_are_digest_pinned(workflow: Path) -> None:
    data = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    for job_id, job in data["jobs"].items():
        container = job.get("container")
        if container:
            image = container if isinstance(container, str) else container["image"]
            assert DIGEST_PIN.match(image), f"{job_id}: container {image} is not digest-pinned"


@pytest.mark.parametrize("workflow", WORKFLOWS, ids=lambda p: p.name)
def test_event_data_is_never_interpolated_into_scripts(workflow: Path) -> None:
    data = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    for job_id, step in _steps(data):
        script = step.get("run", "")
        assert "github.event." not in script and "github.head_ref" not in script, (
            f"{job_id}/{step.get('name')}: pass event data through env, not ${{{{ }}}} in run"
        )


def test_hygiene_job_runs_the_guard_on_the_change(ci: dict) -> None:
    job = ci["jobs"]["hygiene"]
    assert job["permissions"] == {"contents": "read"}
    checkout = next(s for s in job["steps"] if s.get("uses", "").startswith("actions/checkout@"))
    assert checkout["with"]["fetch-depth"] == 0, "the merge base needs full history"
    run = next(s for s in job["steps"] if "tools.check_repo_hygiene" in s.get("run", ""))
    assert '--base "${BASE_SHA}"' in run["run"]
    assert "pull_request.base.sha" in run["env"]["BASE_SHA"]
    assert "github.event.before" in run["env"]["BASE_SHA"]


def test_publish_needs_every_gate_and_never_runs_for_pull_requests(ci: dict) -> None:
    publish = ci["jobs"]["publish"]
    # Every other job gates the image, except the PR-only review comment (skipped on main/tags).
    assert set(publish["needs"]) == set(ci["jobs"]) - {"publish", "ui-comment"}
    assert "pull_request" in ci["jobs"]["ui-comment"]["if"]
    assert "github.event_name != 'pull_request'" in publish["if"]
    assert publish["permissions"] == {"contents": "read", "packages": "write"}


def _version_steps(ci: dict) -> dict[str, dict]:
    return {
        job_id: next(s for s in ci["jobs"][job_id]["steps"] if s.get("id") == "version")
        for job_id in ("docker-build", "publish")
    }


def test_ci_reads_the_canonical_version_without_importing(ci: dict) -> None:
    expected = subprocess.run(
        [sys.executable, "-c", "import sys; sys.path.insert(0, 'src'); import hub; print(hub.__version__)"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.strip()
    for job_id, step in _version_steps(ci).items():
        match = re.search(r"python3 -c '([^']+)'", step["run"])
        assert match, f"{job_id}: no version one-liner"
        got = subprocess.run([sys.executable, "-c", match.group(1)], cwd=ROOT, capture_output=True, text=True)
        assert got.returncode == 0, got.stderr
        assert got.stdout.strip() == expected, job_id
        # A release tag must name the same version.
        assert '"$GITHUB_REF_NAME" != "v$version"' in step["run"], job_id


def test_images_are_labelled_with_the_canonical_version(ci: dict) -> None:
    instructions = _dockerfile_instructions()
    assert ("ARG", "VERSION=unknown") in instructions
    assert ("LABEL", 'org.opencontainers.image.version="${VERSION}"') in instructions
    # Declared after the last RUN, so a version bump keeps the dependency layers cached.
    last_run = max(i for i, (k, _) in enumerate(instructions) if k == "RUN")
    assert instructions.index(("ARG", "VERSION=unknown")) > last_run
    arg = "VERSION=${{ steps.version.outputs.version }}"
    for job_id in ("docker-build", "publish"):
        builds = [s for s in ci["jobs"][job_id]["steps"] if s.get("uses", "").startswith("docker/build-push-action@")]
        assert builds and all(b["with"].get("build-args") == arg for b in builds), job_id
    meta = next(s for s in ci["jobs"]["publish"]["steps"] if s.get("id") == "meta")
    assert "org.opencontainers.image.version=${{ steps.version.outputs.version }}" in meta["with"]["labels"]
    check = next(s for s in ci["jobs"]["docker-build"]["steps"] if s.get("name") == "Check the image version label")
    assert "docker image inspect hdmi-matrix-hub:ci" in check["run"]


def test_publish_pushes_and_verifies_amd64_and_arm64(ci: dict) -> None:
    steps = ci["jobs"]["publish"]["steps"]
    uses = [s.get("uses", "").split("@")[0] for s in steps]
    assert "docker/setup-qemu-action" in uses and "docker/setup-buildx-action" in uses
    build = next(s for s in steps if s.get("uses", "").startswith("docker/build-push-action@"))
    assert build["id"] == "build"
    assert set(build["with"]["platforms"].split(",")) == {"linux/amd64", "linux/arm64"}
    assert build["with"]["push"] is True
    verify = next(s for s in steps if "imagetools inspect" in s.get("run", ""))
    assert verify["env"]["DIGEST"] == "${{ steps.build.outputs.digest }}"
    assert "linux/amd64 linux/arm64" in verify["run"]
    assert "org.opencontainers.image.version" in verify["run"]


def test_pull_requests_build_arm64_and_run_docker_tests(ci: dict) -> None:
    steps = ci["jobs"]["docker-build"]["steps"]
    builds = [s for s in steps if s.get("uses", "").startswith("docker/build-push-action@")]
    assert any(b["with"].get("platforms") == "linux/arm64" and b["with"]["push"] is False for b in builds)
    assert any(s.get("uses", "").startswith("docker/setup-qemu-action@") for s in steps)
    tests = next(s for s in steps if "pytest" in s.get("run", "") and "-m docker" in s["run"])
    assert "tests/test_repo_hygiene_and_docker.py" in tests["run"]


def test_dependabot_tracks_actions_docker_and_pip() -> None:
    config = yaml.safe_load(DEPENDABOT.read_text(encoding="utf-8"))
    assert config["version"] == 2
    updates = {u["package-ecosystem"]: u for u in config["updates"]}
    assert {"github-actions", "docker", "pip"} <= set(updates)
    for ecosystem, update in updates.items():
        assert update["directory"] == "/", ecosystem
        assert update["schedule"]["interval"] in ("daily", "weekly", "monthly"), ecosystem


# ---------------------------------------------------------------------------
# Real build context through BuildKit (marker: docker)
# ---------------------------------------------------------------------------


def _export_context(context: Path, tmp_path: Path) -> set[str]:
    """Every file BuildKit sends from `context` (after .dockerignore), as POSIX paths."""
    dockerfile = tmp_path / "export.Dockerfile"
    dockerfile.write_text("FROM scratch\nCOPY . /\n", encoding="utf-8")
    out = tmp_path / "exported"
    docker("build", "--quiet", "-f", str(dockerfile), "--output", f"type=local,dest={out}", str(context),
           env={"DOCKER_BUILDKIT": "1"}, timeout=300)
    return {p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()}


@pytest.fixture
def needs_docker() -> None:
    if not docker_available():
        pytest.skip("Docker is not available")


@pytest.mark.docker
def test_dockerignore_drops_leftovers_inside_allowed_folders(tmp_path: Path, needs_docker: None) -> None:
    ctx = tmp_path / "ctx"
    keep = ["src/driver.py", "src/hub/core/x.py", "web/index.html", "web/js/app.js", "run.py", "run_server.py",
            "driver.json", "requirements.txt", "requirements-uc.txt"]
    drop = ["docs/README.md", "tests/test_x.py", "tools/x.py", "full_codebase_audit_prompt.md", ".env",
            "src/__pycache__/driver.cpython-312.pyc", "src/hub/old.pyc", "src/driver.lock", "src/config_state.json",
            "src/ucapi_orei_hdmi_matrix.egg-info/PKG-INFO", "src/.mypy_cache/x.json", "web/node_modules/a/index.js",
            "web/.env.local", "src/certs/hub.pem", "src/certs/hub.key", "src/hub/debug.log", "web/capture.har",
            "src/firmware.bin", "web/setup.exe", "src/driver.c4z"]
    for rel in keep + drop:
        (ctx / rel).parent.mkdir(parents=True, exist_ok=True)
        (ctx / rel).write_text("x", encoding="utf-8")
    (ctx / ".dockerignore").write_bytes(DOCKERIGNORE.read_bytes())
    assert _export_context(ctx, tmp_path) == set(keep)


@pytest.mark.docker
def test_real_build_context_only_contains_the_allow_list(tmp_path: Path, needs_docker: None) -> None:
    files = _export_context(ROOT, tmp_path)
    allowed = {s.rstrip("/") for s in _copy_sources()}
    assert files
    assert {f.split("/")[0] for f in files} <= allowed
    leaked = [f for f in files if hygiene.name_problem(f) or "__pycache__" in f or f.endswith(".egg-info")]
    assert leaked == []
