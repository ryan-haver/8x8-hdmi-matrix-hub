"""
Contract tests for the client-facing documentation track
(``wp-g2-client-guides-doc-archive``, DOC-04/05/13/UC-20).

These five documents are owned by this track and act as the user-facing
contract for the hub:

* ``docs/HOME_ASSISTANT.md`` — Home Assistant integration (REST + HACS)
* ``docs/DOCKER.md`` — Docker / Docker Compose deployment
* ``docs/FLIC_SETUP.md`` — Flic button + Flic Hub SDK setup
* ``docs/UNFOLDED_CIRCLE.md`` — Unfolded Circle Remote 3 integration
* ``CONTRIBUTING.md`` — developer guide

The docs are only useful if they keep naming the env vars, routes and
mechanisms that actually exist in the source. The tests below verify that
every required variable, port, endpoint and section is present, and that
cross-doc links between the five files (and the vendor reference) are
intact. Renaming a variable, removing a section or breaking an anchor
fails the build instead of silently leaving the user guide out of date.

Source-of-truth files referenced by these tests:

* ``src/hub/env.py`` — canonical env-var table
* ``src/rest_api/app.py`` — every registered REST route
* ``src/rest_api/security.py`` — access model
* ``src/hub/integrations/flic/__init__.py`` — Flic routes / persistence
* ``src/hub/integrations/unfolded_circle/config.py`` — UC env-var names
* ``run.py`` — env-var resolution + retired-name handling
* ``docker-compose.yml`` + ``docker-compose.uc-host.yml`` +
  ``docker-compose.uc-bridge.yml`` — compose-only variables
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

import pytest

from rest_api import create_rest_app

REPO_ROOT = Path(__file__).resolve().parent.parent

DOCS_DIR = REPO_ROOT / "docs"
HOME_ASSISTANT_MD = DOCS_DIR / "HOME_ASSISTANT.md"
DOCKER_MD = DOCS_DIR / "DOCKER.md"
FLIC_SETUP_MD = DOCS_DIR / "FLIC_SETUP.md"
UNFOLDED_CIRCLE_MD = DOCS_DIR / "UNFOLDED_CIRCLE.md"
CONTRIBUTING_MD = REPO_ROOT / "CONTRIBUTING.md"

# Cross-doc references the docs must keep linking to.
VENDOR_UC_MD = DOCS_DIR / "vendor" / "UNFOLDED_CIRCLE.md"
INTEGRATION_TEMPLATE_MD = DOCS_DIR / "INTEGRATION_TEMPLATE.md"
UC_INTEGRATION_GUIDE_MD = DOCS_DIR / "UNFOLDED_CIRCLE_INTEGRATION_GUIDE.md"
REMEDIATION_PLAN_MD = DOCS_DIR / "REMEDIATION_PLAN.md"
SECURITY_MD = REPO_ROOT / "SECURITY.md"


@pytest.mark.parametrize("guide", [HOME_ASSISTANT_MD, FLIC_SETUP_MD])
def test_documented_endpoint_table_matches_registered_routes(guide: Path, tmp_path: Path) -> None:
    """Reject invented legacy endpoints or unsupported methods in client guides."""
    app = create_rest_app(data_dir=tmp_path)

    def normalized(path: str) -> str:
        return re.sub(r"\{[^}]+\}", "{}", path.split("?", 1)[0])

    actual = {
        (route.method, normalized(route.resource.canonical))
        for route in app.router.routes()
    }
    rows = re.findall(
        r"^\| `(/api/[^`]+)` \| ((?:GET|POST|PUT|DELETE)(?: / (?:GET|POST|PUT|DELETE))*) \|",
        guide.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    assert rows, f"No endpoint table found in {guide.name}"
    missing = [
        f"{method} {path}"
        for path, methods in rows
        for method in methods.split(" / ")
        if (method, normalized(path)) not in actual
    ]
    assert not missing, f"{guide.name} documents unregistered routes: {missing}"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def home_assistant() -> str:
    assert HOME_ASSISTANT_MD.is_file(), f"{HOME_ASSISTANT_MD.name} is missing from the repository"
    text = HOME_ASSISTANT_MD.read_text(encoding="utf-8")
    assert text.strip(), f"{HOME_ASSISTANT_MD.name} is empty"
    return text


@pytest.fixture(scope="module")
def docker_md() -> str:
    assert DOCKER_MD.is_file(), f"{DOCKER_MD.name} is missing from the repository"
    text = DOCKER_MD.read_text(encoding="utf-8")
    assert text.strip(), f"{DOCKER_MD.name} is empty"
    return text


@pytest.fixture(scope="module")
def flic_setup() -> str:
    assert FLIC_SETUP_MD.is_file(), f"{FLIC_SETUP_MD.name} is missing from the repository"
    text = FLIC_SETUP_MD.read_text(encoding="utf-8")
    assert text.strip(), f"{FLIC_SETUP_MD.name} is empty"
    return text


@pytest.fixture(scope="module")
def unfolded_circle() -> str:
    assert UNFOLDED_CIRCLE_MD.is_file(), f"{UNFOLDED_CIRCLE_MD.name} is missing from the repository"
    text = UNFOLDED_CIRCLE_MD.read_text(encoding="utf-8")
    assert text.strip(), f"{UNFOLDED_CIRCLE_MD.name} is empty"
    return text


@pytest.fixture(scope="module")
def contributing() -> str:
    assert CONTRIBUTING_MD.is_file(), f"{CONTRIBUTING_MD.name} is missing from the repository"
    text = CONTRIBUTING_MD.read_text(encoding="utf-8")
    assert text.strip(), f"{CONTRIBUTING_MD.name} is empty"
    return text


# =============================================================================
# Helpers
# =============================================================================


_MD_LINK_RE = re.compile(r"\[[^\]]+\]\((?P<target>[^)]+)\)")


def _resolve_doc_link(link: str, source: Path) -> Path | None:
    """Resolve a Markdown relative link to a file path; ``None`` for external links."""
    target = link.split("#", 1)[0].strip()
    if not target or target.startswith(("http://", "https://", "mailto:", "tel:")):
        return None
    return (source.parent / target).resolve()


def _assert_link_targets_exist(
    doc_text: str,
    doc_path: Path,
    *,
    predicate: Callable[[Path], bool] | None = None,
) -> list[str]:
    """Return the list of unresolved (or predicate-rejected) local Markdown links in ``doc_text``."""
    missing: list[str] = []
    for match in _MD_LINK_RE.finditer(doc_text):
        target = _resolve_doc_link(match.group("target"), doc_path)
        if target is None:
            continue
        if not target.exists() or (predicate is not None and not predicate(target)):
            missing.append(match.group("target"))
    return missing


# =============================================================================
# 1. File presence and minimum content
# =============================================================================


@pytest.mark.parametrize(
    "path",
    [HOME_ASSISTANT_MD, DOCKER_MD, FLIC_SETUP_MD, UNFOLDED_CIRCLE_MD, CONTRIBUTING_MD],
)
def test_doc_exists_and_is_substantial(path: Path) -> None:
    """Every owned doc exists and is more than a stub."""
    assert path.is_file(), f"{path.relative_to(REPO_ROOT)} is missing"
    text = path.read_text(encoding="utf-8")
    assert len(text.strip()) > 2000, f"{path.name} is a stub ({len(text.strip())} chars)"
    assert text.lstrip().startswith("#"), f"{path.name} must start with a Markdown heading"


# =============================================================================
# 2. HOME_ASSISTANT.md — REST endpoints, two-level access, the control PIN
# =============================================================================


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/status",
        "/api/info",
        "/api/health",
        "/api/inputs",
        "/api/outputs",
        "/api/presets",
        "/api/input/next",
        "/api/input/previous",
        "/api/output/{n}/source",
        "/api/output/{n}/enable",
        "/api/output/{n}/mute",
        "/api/preset/{n}",
        "/api/power/on",
        "/api/power/off",
        "/api/auth/status",
        "/api/auth/unlock",
        "/api/auth/api-keys",
        "/api/auth/devices",
        "/api/settings/matrix-host",
        "/api/system/beep",
        "/api/system/reboot",
        "/api/profile/{id}/recall",
        "/api/scene/{id}/recall",
        "/api/cec/macro/{id}/execute",
        "/api/cec/input/{n}/{command}",
        "/api/cec/output/{n}/{command}",
        "/api/integrations/flic/register",
        "/api/integrations/flic/buttons",
        # HACS Option B service
        "hdmi_matrix.recall_preset",
        "hdmi_matrix.switch_input",
        "hdmi_matrix.send_cec_command",
    ],
)
def test_home_assistant_documents_endpoint(home_assistant: str, endpoint: str) -> None:
    """Every required REST endpoint and HACS service name is documented."""
    # Substitute placeholder tokens that match the documented paths.
    # The docs use ``{n}`` / ``{id}`` instead of real numbers to express a route.
    candidates = [endpoint]
    candidates.append(endpoint.replace("{n}", "1"))
    candidates.append(endpoint.replace("{n}", "2"))
    candidates.append(endpoint.replace("{id}", "movie-night"))
    if "{n}/{command}" in endpoint:
        candidates.append(endpoint.replace("{n}/{command}", "1/play"))
        candidates.append(endpoint.replace("{n}/{command}", "1/volume_up"))
    if "cec/" in endpoint and endpoint.endswith("{command}"):
        candidates.append(endpoint.replace("{command}", "play"))
        candidates.append(endpoint.replace("{command}", "volume_up"))
    assert any(c in home_assistant for c in candidates), f"HOME_ASSISTANT.md does not mention endpoint {endpoint}"


@pytest.mark.parametrize(
    "term",
    [
        "X-API-Key",
        "CONTROL_PIN",
        "ADMIN_PIN",
        "control_pin_set",
        "admin_pin_set",
        "session_level",
        "remembered",
        "Content-Type: application/json",
        "config_flow",
        "HACS",
        "api_key",
        "polling",
        "rest_command",
        "service",
    ],
)
def test_home_assistant_documents_auth_mechanism(home_assistant: str, term: str) -> None:
    """The two-level access model and the HACS flow are described in plain terms."""
    assert term in home_assistant, f"HOME_ASSISTANT.md does not mention {term}"


@pytest.mark.parametrize(
    "section",
    [
        "Option A: REST Commands",
        "Option B: HACS Custom Component",
        "API key",
        "Alexa Integration",
        "Entities",
        "Services",
        "Troubleshooting",
    ],
)
def test_home_assistant_required_sections(home_assistant: str, section: str) -> None:
    """Every required section of the guide is present as a heading."""
    headings = [line for line in home_assistant.splitlines() if line.startswith("#")]
    assert any(section in heading for heading in headings), f"HOME_ASSISTANT.md has no '{section}' section"


def test_home_assistant_no_placeholder_endpoint(home_assistant: str) -> None:
    """Guards against the legacy DOC-04 finding: no "planned" component text."""
    lowered = home_assistant.lower()
    assert "planned" not in lowered or "as planned" in lowered, (
        "HOME_ASSISTANT.md still describes the component as 'planned'"
    )


def test_home_assistant_local_links_resolve(home_assistant: str) -> None:
    """Every Markdown link inside HOME_ASSISTANT.md points at a real file."""
    missing = _assert_link_targets_exist(home_assistant, HOME_ASSISTANT_MD)
    assert not missing, f"HOME_ASSISTANT.md has broken local links: {missing}"


# =============================================================================
# 3. DOCKER.md — env vars, compose files, persistence, retired variables
# =============================================================================


@pytest.mark.parametrize(
    "variable",
    [
        # Core env vars (src/hub/env.py)
        "MATRIX_HOST",
        "MATRIX_PORT",
        "API_PORT",
        "DATA_DIR",
        "LOG_LEVEL",
        "ADMIN_PIN",
        "CONTROL_PIN",
        "ALLOWED_HOSTS",
        "CORS_ALLOWED_ORIGINS",
        # UC integration env vars
        "UC_ENABLED",
        "UC_INTEGRATION_HTTP_PORT",
        "UC_INTEGRATION_INTERFACE",
        "UC_DISABLE_MDNS_PUBLISH",
        "UC_DRIVER_URL",
        "UC_CONFIG_HOME",
        "UC_AUTH_TOKEN",
        # Optional integrations
        "FLIC_ENABLED",
        "HA_DISCOVERY_ENABLED",
        # Polling
        "STATUS_POLL_INTERVAL",
        "POLLING_INTERVAL",
        "POLLING_ENABLED",
        # Deprecated aliases still accepted
        "OREI_HOST",
        "OREI_PORT",
        "REST_API_PORT",
        "MATRIX_DATA_DIR",
        "UC_PORT",
        "UC_DISABLE_MDNS",
        # Retired (logged and ignored)
        "USE_MODULAR",
        "WEBUI_ENABLED",
        "REST_API_ENABLED",
    ],
)
def test_docker_documents_env_var(docker_md: str, variable: str) -> None:
    """Every environment variable the hub reads is documented in DOCKER.md."""
    assert variable in docker_md, f"DOCKER.md does not document env var {variable}"


@pytest.mark.parametrize(
    "alias",
    [
        ("MATRIX_HOST", "OREI_HOST"),
        ("MATRIX_PORT", "OREI_PORT"),
        ("API_PORT", "REST_API_PORT"),
        ("DATA_DIR", "MATRIX_DATA_DIR"),
        ("UC_INTEGRATION_HTTP_PORT", "UC_PORT"),
        ("UC_DISABLE_MDNS_PUBLISH", "UC_DISABLE_MDNS"),
    ],
)
def test_docker_documents_deprecated_alias(docker_md: str, alias: tuple[str, str]) -> None:
    """The deprecated alias table lists both names together so users can grep."""
    canonical, deprecated = alias
    assert canonical in docker_md, f"DOCKER.md missing canonical {canonical}"
    assert deprecated in docker_md, f"DOCKER.md missing deprecated alias {deprecated}"


@pytest.mark.parametrize("port", ["8080", "9095"])
def test_docker_documents_listening_port(docker_md: str, port: str) -> None:
    """Both listening ports (REST + UC) are named explicitly."""
    assert port in docker_md, f"DOCKER.md does not mention port {port}"


@pytest.mark.parametrize(
    "compose_file",
    [
        "docker-compose.yml",
        "docker-compose.uc-host.yml",
        "docker-compose.uc-bridge.yml",
        "HUB_HOST_IP",
        "HUB_PORT",
        "MATRIX_DATA_DIR",
        "UC_HOST_PORT",
        "HUB_CONTAINER_NAME",
    ],
)
def test_docker_documents_compose_variable(docker_md: str, compose_file: str) -> None:
    """Every compose-only variable / file is named in DOCKER.md."""
    assert compose_file in docker_md, f"DOCKER.md does not mention {compose_file}"


@pytest.mark.parametrize(
    "data_file",
    [
        "device_settings.json",
        "themes.json",
        "ui_preferences.json",
        "system_shortcuts.json",
        "dashboard_layout.json",
        "profiles.json",
        "cec_macros.json",
        "scenes.json",
        "config_state.json",
        "driver.lock",
        "security.json",
        "flic_buttons.json",
    ],
)
def test_docker_documents_persistent_file(docker_md: str, data_file: str) -> None:
    """DOCKER.md names every persistent file under ``/data`` (or with the new name)."""
    assert data_file in docker_md, f"DOCKER.md does not mention persistent file {data_file}"


@pytest.mark.parametrize(
    "section",
    [
        "Quick start",
        "Compose files",
        "Remote 3 integration and networking",
        "Environment variables",
        "Persistent storage",
        "Upgrading from the earlier image",
        "Troubleshooting",
        "Deployment tests",
    ],
)
def test_docker_required_sections(docker_md: str, section: str) -> None:
    """Every required section of the guide is present as a heading."""
    headings = [line for line in docker_md.splitlines() if line.startswith("#")]
    assert any(section in heading for heading in headings), f"DOCKER.md has no '{section}' section"


def test_docker_no_legacy_multi_compose_reference(docker_md: str) -> None:
    """Guards against the legacy DOC-05 finding: ``docker-compose.multi.yml`` is gone."""
    assert "docker-compose.multi.yml" not in docker_md, (
        "DOCKER.md still references the removed docker-compose.multi.yml"
    )


def test_docker_local_links_resolve(docker_md: str) -> None:
    """Every Markdown link inside DOCKER.md points at a real file."""
    missing = _assert_link_targets_exist(docker_md, DOCKER_MD)
    assert not missing, f"DOCKER.md has broken local links: {missing}"


# =============================================================================
# 4. FLIC_SETUP.md — auth model, routes, Flic Hub SDK examples
# =============================================================================


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/status",
        "/api/auth/status",
        "/api/input/next",
        "/api/input/previous",
        "/api/output/{n}/source",
        "/api/output/{n}/enable",
        "/api/output/{n}/mute",
        "/api/preset/{n}",
        "/api/power/on",
        "/api/power/off",
        "/api/system/beep",
        "/api/profile/{id}/recall",
        "/api/scene/{id}/recall",
        "/api/cec/macro/{id}/execute",
        "/api/cec/macro/{id}/test",
        "/api/cec/input/{n}/{command}",
        "/api/cec/output/{n}/{command}",
        "/api/integrations/flic/register",
        "/api/integrations/flic/buttons",
        "/api/auth/api-keys",
        "/api/auth/unlock",
    ],
)
def test_flic_setup_documents_endpoint(flic_setup: str, endpoint: str) -> None:
    """Every Flic-relevant REST endpoint is documented."""
    candidates = [endpoint]
    if "{n}" in endpoint:
        candidates.append(endpoint.replace("{n}", "1"))
        candidates.append(endpoint.replace("{n}", "2"))
    if "{id}" in endpoint:
        candidates.append(endpoint.replace("{id}", "movie-night"))
        candidates.append(endpoint.replace("{id}", "theater-on"))
    if "{n}/{command}" in endpoint:
        candidates.append(endpoint.replace("{n}/{command}", "1/play"))
        candidates.append(endpoint.replace("{n}/{command}", "1/volume_up"))
    if endpoint.endswith("/{command}"):
        candidates.append(endpoint.replace("{command}", "play"))
        candidates.append(endpoint.replace("{command}", "volume_up"))
    assert any(c in flic_setup for c in candidates), f"FLIC_SETUP.md does not mention endpoint {endpoint}"


@pytest.mark.parametrize(
    "term",
    [
        "X-API-Key",
        "?key=",
        "CONTROL_PIN",
        "CONTROL_API_KEY",
        "API_KEY",
        "api_keys",
        "control_pin_set",
        "remembered",
        "admin_pin_set",
        "session_level",
        "Content-Type: application/json",
        "Content-Type",
        "415",
        "401",
        "Authorization",
        "flic_buttons.json",
        "FLIC_ENABLED",
        "Flic Hub SDK",
        "Flic Twist",
        "Flic Duo",
        "Flic Original",
    ],
)
def test_flic_setup_documents_term(flic_setup: str, term: str) -> None:
    """The auth model, Flic SDK and integration terms are all present."""
    assert term in flic_setup, f"FLIC_SETUP.md does not mention {term}"


@pytest.mark.parametrize(
    "section",
    [
        "Prerequisites",
        "Quick Start",
        "Supported Button Types",
        "Available API Endpoints",
        "Authentication",
        "Configuration Steps",
        "Profiles Integration",
        "CEC Macros Integration",
        "Zone-Based Configurations",
        "Flic Hub SDK Integration",
        "Troubleshooting",
    ],
)
def test_flic_setup_required_sections(flic_setup: str, section: str) -> None:
    """Every required section of the Flic guide is present as a heading."""
    headings = [line for line in flic_setup.splitlines() if line.startswith("#")]
    assert any(section in heading for heading in headings), f"FLIC_SETUP.md has no '{section}' section"


def test_flic_setup_local_links_resolve(flic_setup: str) -> None:
    """Every Markdown link inside FLIC_SETUP.md points at a real file."""
    missing = _assert_link_targets_exist(flic_setup, FLIC_SETUP_MD)
    assert not missing, f"FLIC_SETUP.md has broken local links: {missing}"


# =============================================================================
# 5. UNFOLDED_CIRCLE.md — modular UC setup (UC-20)
# =============================================================================


@pytest.mark.parametrize(
    "variable",
    [
        "UC_ENABLED",
        "UC_INTEGRATION_HTTP_PORT",
        "UC_INTEGRATION_INTERFACE",
        "UC_DISABLE_MDNS_PUBLISH",
        "UC_DRIVER_URL",
        "UC_CONFIG_HOME",
        "UC_AUTH_TOKEN",
        "ADMIN_PIN",
        "MATRIX_HOST",
        "API_PORT",
        "DATA_DIR",
        "STATUS_POLL_INTERVAL",
        "FLIC_ENABLED",
        "HA_DISCOVERY_ENABLED",
    ],
)
def test_unfolded_circle_documents_env_var(unfolded_circle: str, variable: str) -> None:
    """Every UC-related env var is named in UNFOLDED_CIRCLE.md."""
    assert variable in unfolded_circle, f"UNFOLDED_CIRCLE.md does not document env var {variable}"


@pytest.mark.parametrize(
    "alias",
    [
        ("UC_INTEGRATION_HTTP_PORT", "UC_PORT"),
        ("UC_DISABLE_MDNS_PUBLISH", "UC_DISABLE_MDNS"),
    ],
)
def test_unfolded_circle_documents_alias(unfolded_circle: str, alias: tuple[str, str]) -> None:
    """The two accepted aliases for UC_* variables are named together."""
    canonical, deprecated = alias
    assert canonical in unfolded_circle, f"UNFOLDED_CIRCLE.md missing canonical {canonical}"
    assert deprecated in unfolded_circle, f"UNFOLDED_CIRCLE.md missing deprecated alias {deprecated}"


@pytest.mark.parametrize(
    "term",
    [
        # Networking modes
        "network_mode: host",
        "docker-compose.uc-host.yml",
        "docker-compose.uc-bridge.yml",
        "HUB_HOST_IP",
        "UC_HOST_PORT",
        "_uc-integration._tcp",
        "mDNS",
        "ws://",
        # Setup token behaviour
        "pwd: true",
        "Hub setup token",
        "auth_token",
        "AUTHORIZATION_ERROR",
        "hmac.compare_digest",
        # Setup flow
        "DriverSetupRequest",
        "Reconfigure",
        "config_state.json",
        "driver.lock",
        # Source-of-truth files
        "src/driver.py",
        "src/hub/integrations/unfolded_circle",
        "run.py",
        "src/hub/env.py",
        "driver.json",
        # Compose override behaviour
        "docker compose -f docker-compose.yml -f docker-compose.uc-host.yml",
        # Firewall guidance
        "TCP 9095",
        "UDP 5353",
    ],
)
def test_unfolded_circle_documents_term(unfolded_circle: str, term: str) -> None:
    """The UC integration's networking, setup token and matrix-address lifecycle are all covered."""
    assert term in unfolded_circle, f"UNFOLDED_CIRCLE.md does not mention {term}"


@pytest.mark.parametrize(
    "section",
    [
        "Modular setup",
        "Remote's setup flow",
        "Networking",
        "matrix address",
        "Firewall and exposure",
        "Reset and recovery",
        "Troubleshooting",
        "References",
    ],
)
def test_unfolded_circle_required_sections(unfolded_circle: str, section: str) -> None:
    """Every required section of the UC guide is present as a heading."""
    headings = [line for line in unfolded_circle.splitlines() if line.startswith("#")]
    assert any(section in heading for heading in headings), f"UNFOLDED_CIRCLE.md has no '{section}' section"


def test_unfolded_circle_no_setup_data_token_logging(unfolded_circle: str) -> None:
    """The guide explicitly says the token / password is never logged."""
    lowered = unfolded_circle.lower()
    assert "never logged" in lowered or "redacted" in lowered or "is never logged" in lowered, (
        "UNFOLDED_CIRCLE.md must state the setup token / password is never logged"
    )


def test_unfolded_circle_no_setup_data_in_clear(unfolded_circle: str) -> None:
    """Sanity: the guide does not leak a sample real token (it may use <key>)."""
    # Make sure no real-looking token (long base64 / urlsafe) is accidentally
    # embedded. The guide uses ``<key>`` placeholders only. The threshold
    # (40 chars, urlsafe alphabet, no dashes — dashes are typical of
    # Markdown slugs and curl headers, not API keys) matches what
    # `secrets.token_urlsafe(32)` produces.
    suspect = re.search(r"\b[A-Za-z0-9_]{40,}\b", unfolded_circle)
    assert suspect is None, (
        f"UNFOLDED_CIRCLE.md appears to contain a real-looking token ({suspect.group(0)!r}); redact it"
    )


def test_unfolded_circle_local_links_resolve(unfolded_circle: str) -> None:
    """Every local Markdown link inside UNFOLDED_CIRCLE.md points at a real file."""
    missing = _assert_link_targets_exist(unfolded_circle, UNFOLDED_CIRCLE_MD)
    assert not missing, f"UNFOLDED_CIRCLE.md has broken local links: {missing}"


# =============================================================================
# 6. CONTRIBUTING.md — current project layout, tooling, tests (DOC-13)
# =============================================================================


@pytest.mark.parametrize(
    "path",
    [
        "run.py",
        "pyproject.toml",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.uc-host.yml",
        "docker-compose.uc-bridge.yml",
        "src/hub/env.py",
        "src/hub/openapi.py",
        "src/hub/integrations/",
        "src/rest_api/app.py",
        "src/rest_api/security.py",
        "src/driver.py",
        "src/orei_matrix.py",
        "driver.json",
        "custom_components/hdmi_matrix/",
        "docs/DOCKER.md",
        "docs/HOME_ASSISTANT.md",
        "docs/FLIC_SETUP.md",
        "docs/UNFOLDED_CIRCLE.md",
        "docs/INTEGRATION_TEMPLATE.md",
        "docs/SECURITY.md",
        "docs/REMEDIATION_PLAN.md",
        "docs/vendor/UNFOLDED_CIRCLE.md",
        "docs/api/WEBSOCKET.md",
        "tests/conftest.py",
        "tests/uc/",
        "tests/sim/",
        "tests/deploy/",
        "tests/validation/",
        ".githooks",
    ],
)
def test_contributing_documents_path(contributing: str, path: str) -> None:
    """The developer guide names every current directory / file in the layout."""
    assert path in contributing, f"CONTRIBUTING.md does not mention {path}"


@pytest.mark.parametrize(
    "term",
    [
        "Ruff",
        "Mypy",
        "pytest",
        "pytest-asyncio",
        "pyproject.toml",
        "Python 3.11",
        "Python 3.12",
        "Docker Compose",
        "Conventional Commits",
        "run.py",
        "UC_ENABLED",
        "FLIC_ENABLED",
        "HA_DISCOVERY_ENABLED",
        "HACS",
        "DOC-04",
        "DOC-05",
        "DOC-13",
        "UC-20",
    ],
)
def test_contributing_documents_term(contributing: str, term: str) -> None:
    """The guide names every tool, marker and finding register relevant to this track."""
    assert term in contributing, f"CONTRIBUTING.md does not mention {term}"


@pytest.mark.parametrize(
    "marker",
    [
        "hardware",
        "docker",
        "mock",
        "pytest -m hardware",
        "pytest -m docker",
    ],
)
def test_contributing_documents_marker(contributing: str, marker: str) -> None:
    """The guide explains the pytest markers that gate hardware / docker tests."""
    assert marker in contributing, f"CONTRIBUTING.md does not mention the {marker!r} marker"


@pytest.mark.parametrize(
    "section",
    [
        "Development Setup",
        "Project Structure",
        "Code Style",
        "Making Changes",
        "Testing with Docker",
        "Documentation",
        "Commit Messages",
        "Questions?",
    ],
)
def test_contributing_required_sections(contributing: str, section: str) -> None:
    """Every required section of the developer guide is present as a heading."""
    headings = [line for line in contributing.splitlines() if line.startswith("#")]
    assert any(section in heading for heading in headings), f"CONTRIBUTING.md has no '{section}' section"


def test_contributing_no_setup_py_install_command(contributing: str) -> None:
    """Guards against the legacy DOC-13 finding: ``setup.py`` is gone (DEP-04)."""
    # ``setup.py`` may still be mentioned in "no longer needed" context; the install
    # command itself must not use it.
    install_lines = [
        line for line in contributing.splitlines()
        if re.match(r"(?:python -m )?pip install\b", line.strip())
    ]
    assert install_lines, "CONTRIBUTING.md has no install command"
    for line in install_lines:
        assert "setup.py" not in line, f"CONTRIBUTING.md install command still references setup.py: {line.strip()}"


def test_contributing_local_links_resolve(contributing: str) -> None:
    """Every Markdown link inside CONTRIBUTING.md points at a real file."""
    missing = _assert_link_targets_exist(contributing, CONTRIBUTING_MD)
    assert not missing, f"CONTRIBUTING.md has broken local links: {missing}"


# =============================================================================
# 7. Cross-doc integration — the five documents point at each other correctly
# =============================================================================


def _doc_names(text: str) -> list[str]:
    """The list of Markdown links in ``text``, with the file basenames."""
    out: list[str] = []
    for match in _MD_LINK_RE.finditer(text):
        target = match.group("target").split("#", 1)[0].strip()
        if target.startswith(("http://", "https://", "mailto:", "tel:")):
            continue
        out.append(target)
    return out


@pytest.mark.parametrize(
    "doc_path",
    [
        HOME_ASSISTANT_MD,
        DOCKER_MD,
        FLIC_SETUP_MD,
        UNFOLDED_CIRCLE_MD,
        CONTRIBUTING_MD,
    ],
)
def test_cross_doc_references_resolve(doc_path: Path) -> None:
    """Every local link in this track's documents points to a real file in the repo."""
    text = doc_path.read_text(encoding="utf-8")
    missing = _assert_link_targets_exist(text, doc_path)
    assert not missing, f"{doc_path.name} has broken local links: {missing}"


def test_unfolded_circle_links_to_known_companions() -> None:
    """UNFOLDED_CIRCLE.md links to the vendor reference and the integration cookbook."""
    text = UNFOLDED_CIRCLE_MD.read_text(encoding="utf-8")
    for sibling in (VENDOR_UC_MD, UC_INTEGRATION_GUIDE_MD, REMEDIATION_PLAN_MD, SECURITY_MD):
        # The doc references its companion by *relative* path; SECURITY.md
        # is at the repo root so the link is "../SECURITY.md".
        try:
            rel = sibling.relative_to(UNFOLDED_CIRCLE_MD.parent).as_posix()
        except ValueError:
            rel = "../" + sibling.name
        assert rel in text or rel.replace("../", "") in text, (
            f"UNFOLDED_CIRCLE.md does not link to its companion {sibling.name} (expected {rel!r})"
        )


def test_home_assistant_links_to_flic_setup() -> None:
    """HOME_ASSISTANT.md cross-references FLIC_SETUP.md for the API-key creation flow."""
    text = HOME_ASSISTANT_MD.read_text(encoding="utf-8")
    assert "FLIC_SETUP.md" in text, "HOME_ASSISTANT.md does not link to FLIC_SETUP.md"


def test_flic_setup_links_to_home_assistant() -> None:
    """FLIC_SETUP.md cross-references HOME_ASSISTANT.md for the API-key context."""
    text = FLIC_SETUP_MD.read_text(encoding="utf-8")
    assert "HOME_ASSISTANT.md" in text, "FLIC_SETUP.md does not link to HOME_ASSISTANT.md"


def test_docker_links_to_unfolded_circle() -> None:
    """DOCKER.md cross-references UNFOLDED_CIRCLE.md for the Remote-3 details."""
    text = DOCKER_MD.read_text(encoding="utf-8")
    assert "UNFOLDED_CIRCLE.md" in text, "DOCKER.md does not link to UNFOLDED_CIRCLE.md"


def test_unfolded_circle_links_to_docker() -> None:
    """UNFOLDED_CIRCLE.md cross-references DOCKER.md for the compose files."""
    text = UNFOLDED_CIRCLE_MD.read_text(encoding="utf-8")
    assert "DOCKER.md" in text, "UNFOLDED_CIRCLE.md does not link to DOCKER.md"


def test_contributing_links_to_owned_docs() -> None:
    """CONTRIBUTING.md references all four owned docs."""
    text = CONTRIBUTING_MD.read_text(encoding="utf-8")
    for sibling in ("HOME_ASSISTANT.md", "DOCKER.md", "FLIC_SETUP.md", "UNFOLDED_CIRCLE.md"):
        assert sibling in text, f"CONTRIBUTING.md does not link to {sibling}"


def test_vendor_uc_md_exists() -> None:
    """UNFOLDED_CIRCLE.md links to docs/vendor/UNFOLDED_CIRCLE.md — make sure it exists."""
    assert VENDOR_UC_MD.is_file(), "docs/vendor/UNFOLDED_CIRCLE.md is missing"
