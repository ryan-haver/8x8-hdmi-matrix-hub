"""Release version, failure rollback and built-distribution regression gates."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tomllib
import zipfile
from email.parser import BytesParser
from pathlib import Path

import pytest

from hub import __version__
from hub.integrations.homeassistant import HomeAssistantDiscoveryIntegration
from hub.integrations.unfolded_circle.mdns import UCMdnsPublisher
from version import __version__ as legacy_version

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bump_version", ROOT / "scripts/bump_version.py")
assert spec is not None and spec.loader is not None
bump_version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bump_version)


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = {key: value for key, value in os.environ.items() if key.upper() != "PYTHONPATH"}
    result = subprocess.run([sys.executable, *args], cwd=cwd, env=env, capture_output=True, text=True, timeout=180)
    assert result.returncode == 0, result.stdout + result.stderr
    return result


@pytest.fixture
def release_copy(tmp_path: Path) -> Path:
    for relative in (*bump_version.MANIFESTS, bump_version.VERSION_FILE, Path("pyproject.toml")):
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    (tmp_path / "scripts").mkdir()
    shutil.copyfile(ROOT / "scripts/bump_version.py", tmp_path / "scripts/bump_version.py")
    return tmp_path


def snapshot(root: Path) -> dict[Path, bytes]:
    return {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def test_versions_and_discovery_match_canonical() -> None:
    assert legacy_version == __version__ == bump_version.canonical_version(ROOT)
    assert not bump_version.version_plan(ROOT, __version__)
    assert HomeAssistantDiscoveryIntegration().build_zeroconf_properties()["version"] == __version__
    assert UCMdnsPublisher(disable_mdns=True).txt_properties()["ver"] == __version__
    assert not (ROOT / "setup.py").exists()
    run("scripts/bump_version.py", "--check", cwd=ROOT)


@pytest.mark.parametrize("target_version", ["9.8.7", "1.0.0rc1"])
def test_bump_roundtrip_preserves_every_byte(release_copy: Path, target_version: str) -> None:
    original = snapshot(release_copy)
    run("scripts/bump_version.py", target_version, cwd=release_copy)
    run("scripts/bump_version.py", "--check", cwd=release_copy)
    assert bump_version.canonical_version(release_copy) == target_version
    for manifest in bump_version.MANIFESTS:
        assert json.loads((release_copy / manifest).read_bytes())["version"] == target_version
    run("scripts/bump_version.py", __version__, cwd=release_copy)
    assert snapshot(release_copy) == original


@pytest.mark.parametrize("version, tag", [("1.0.0rc1", "v1.0.0-rc1"), ("1.0.0", "v1.0.0")])
def test_release_tag_matches_canonical_version(release_copy: Path, version: str, tag: str) -> None:
    run("scripts/bump_version.py", version, cwd=release_copy)
    original = snapshot(release_copy)
    assert run("scripts/bump_version.py", "--tag", cwd=release_copy).stdout.strip() == tag
    assert snapshot(release_copy) == original


@pytest.mark.parametrize("version", ["v1.2.3", "1.2", "01.2.3", "1.2.3-rc1", "1.2.3rc01", "1.2.3\n", "1.2.3;echo bad"])
def test_invalid_version_does_not_write(release_copy: Path, version: str) -> None:
    original = snapshot(release_copy)
    with pytest.raises(ValueError, match="Version must"):
        bump_version.version_plan(release_copy, version)
    assert snapshot(release_copy) == original


def test_invalid_manifest_does_not_write(release_copy: Path) -> None:
    (release_copy / bump_version.MANIFESTS[-1]).write_text("{broken", encoding="utf-8")
    original = snapshot(release_copy)
    with pytest.raises(ValueError):
        bump_version.version_plan(release_copy, "9.8.7")
    assert snapshot(release_copy) == original


def test_replace_failure_rolls_back(release_copy: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = snapshot(release_copy)
    replace = bump_version.os.replace
    calls = 0

    def fail_second(source: Path, target: Path) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected replacement failure")
        replace(source, target)

    monkeypatch.setattr(bump_version.os, "replace", fail_second)
    with pytest.raises(OSError, match="injected"):
        bump_version.apply_plan(bump_version.version_plan(release_copy, "9.8.7"))
    assert calls == 2
    assert snapshot(release_copy) == original


def test_staging_failure_does_not_write(release_copy: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = snapshot(release_copy)
    create = bump_version.tempfile.NamedTemporaryFile
    calls = 0

    def fail_second(**kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("injected staging failure")
        return create(**kwargs)

    monkeypatch.setattr(bump_version.tempfile, "NamedTemporaryFile", fail_second)
    with pytest.raises(OSError, match="injected"):
        bump_version.apply_plan(bump_version.version_plan(release_copy, "9.8.7"))
    assert snapshot(release_copy) == original


def test_check_reports_drift_without_write(release_copy: Path) -> None:
    path = release_copy / bump_version.MANIFESTS[0]
    path.write_bytes(path.read_bytes().replace(__version__.encode(), b"9.8.7"))
    original = snapshot(release_copy)
    result = subprocess.run(
        [sys.executable, "scripts/bump_version.py", "--check"],
        cwd=release_copy, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 1
    assert "Version drift: driver.json" in result.stderr
    assert snapshot(release_copy) == original


@pytest.mark.parametrize("filename", ["requirements.txt", "requirements-dev.txt"])
def test_locks_are_fully_pinned_and_hashed(filename: str) -> None:
    text = (ROOT / filename).read_text(encoding="utf-8")
    requirements = [
        line.strip() for line in text.replace("\\\n", " ").splitlines()
        if line.strip() and not line.lstrip().startswith(("#", "--"))
    ]
    assert requirements
    for line in requirements:
        assert re.match(r"^[a-zA-Z0-9_.-]+==[^\s]+", line), line
        assert re.search(r"--hash=sha256:[a-f0-9]{64}(?:\s|$)", line), line


@pytest.fixture(scope="module", params=[None, "1.0.0rc1"])
def distributions(tmp_path_factory: pytest.TempPathFactory, request: pytest.FixtureRequest) -> tuple[Path, Path, str]:
    project = tmp_path_factory.mktemp("packaging")
    for name in ("pyproject.toml", "LICENSE", "THIRD_PARTY_NOTICES.md", "README.md", "driver.json"):
        shutil.copyfile(ROOT / name, project / name)
    shutil.copytree(ROOT / "LICENSES", project / "LICENSES")
    shutil.copytree(ROOT / "src", project / "src", ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    shutil.copytree(ROOT / "web", project / "web")
    for manifest in bump_version.MANIFESTS:
        target = project / manifest
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / manifest, target)
    expected_version = request.param or __version__
    if request.param:
        bump_version.apply_plan(bump_version.version_plan(project, expected_version))
    # Default build creates an sdist and then builds the wheel from that sdist.
    run("-m", "build", "--no-isolation", cwd=project)
    return next((project / "dist").glob("*.whl")), next((project / "dist").glob("*.tar.gz")), expected_version


def test_built_metadata_modules_and_assets(distributions: tuple[Path, Path, str]) -> None:
    wheel, sdist, expected_version = distributions
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    modules = {f"{name}.py" for name in config["tool"]["setuptools"]["py-modules"]}
    # Check every top-level source module, including private runtime helpers.
    assert modules == {path.name for path in (ROOT / "src").glob("*.py") if path.name != "__init__.py"}
    assets = {
        path.relative_to(ROOT).as_posix() for path in (ROOT / "web").rglob("*")
        if path.suffix in {".html", ".json", ".js", ".css", ".svg"}
    }
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        assert modules | assets | {"hub/core/matrix_service.py", "rest_api/app.py"} <= names
        metadata = BytesParser().parsebytes(archive.read(next(name for name in names if name.endswith("/METADATA"))))
        assert metadata["Name"] == config["project"]["name"]
        assert metadata["Version"] == expected_version
        assert metadata["Requires-Python"] == ">=3.11"
        assert metadata["License-Expression"] == "MPL-2.0"
        requirements = metadata.get_all("Requires-Dist", [])
        for dependency in config["project"]["dependencies"]:
            assert dependency in requirements
        entrypoints = archive.read(next(name for name in names if name.endswith("/entry_points.txt"))).decode()
        assert "orei-matrix-driver = driver:main" in entrypoints
        driver_manifest = next(name for name in names if name.endswith(".data/data/driver.json"))
        assert json.loads(archive.read(driver_manifest))["version"] == expected_version
        license_files = {"LICENSE", "THIRD_PARTY_NOTICES.md"} | {
            path.relative_to(ROOT).as_posix() for path in (ROOT / "LICENSES").rglob("*") if path.is_file()
        }
        assert all(any(name.endswith("/licenses/" + license_file) for name in names) for license_file in license_files)
    with tarfile.open(sdist) as archive:
        names = {name.partition("/")[2] for name in archive.getnames()}
        assert {f"src/{module}" for module in modules} | assets | license_files | {"driver.json", "pyproject.toml"} <= names
        assert "setup.py" not in names


def test_installed_wheel_imports_outside_checkout(distributions: tuple[Path, Path, str], tmp_path: Path) -> None:
    wheel, _, _ = distributions
    target = tmp_path / "installed"
    run("-m", "pip", "install", "--no-deps", "--target", str(target), str(wheel), cwd=tmp_path)
    code = (
        "import sys; from pathlib import Path; "
        "sys.path.insert(0, sys.argv[1]); "
        "import _file_io, _process_lock, _task_supervisor, _telnet_proto, device_codes; "
        "import hub, version, rest_api, profile_execution; "
        "from importlib.metadata import version as metadata_version; "
        "from importlib.resources import files; "
        "assert hub.__version__ == version.__version__ == metadata_version('ucapi-orei-hdmi-matrix'); "
        "assert Path(hub.__file__).is_relative_to(Path(sys.argv[1])); "
        "assert files('web').joinpath('index.html').is_file(); "
        "assert files('web').joinpath('js/app.js').is_file(); "
        "assert Path(sys.argv[1], 'driver.json').is_file()"
    )
    # -P removes cwd; run() also clears PYTHONPATH. Installed third-party
    # dependencies remain available even when pytest runs in a user installation.
    run("-P", "-c", code, str(target), cwd=tmp_path)
