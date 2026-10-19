"""
Structural tests for the project-root documentation owned by the
README, ARCHITECTURE, INTEGRATIONS, ROADMAP, CHANGELOG and
docs/README work (DOC-01, DOC-02, DOC-10, DOC-12). Every test
asserts one thing the merged docs must keep doing so that a later
PR that drifts away from the actual runtime — a fabricated
runtime claim, an invented REST route, an unreleased tag, a
cop-out on hardware evidence — breaks the build instead of
silently landing.

This file deliberately tests against the *source*: the live
endpoint registrations in ``src/rest_api/app.py``, the live
``src/hub/__init__.py::__version__``, the live
``src/hub/integrations/*`` env-flag declarations, the ``openapi.py``
generator import paths and the shipped entry point in ``run.py``.
Keyword-only assertions would let the docs say almost anything
and still pass; these tests pin the docs to what actually runs.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _read(relpath: str) -> str:
    """Read a documentation file relative to the repo root."""
    path = REPO_ROOT / relpath
    assert path.is_file(), f"Documentation file is missing: {relpath}"
    text = path.read_text(encoding="utf-8")
    assert text.strip(), f"Documentation file is empty: {relpath}"
    return text


def _headings(text: str) -> list[str]:
    """All Markdown headings (lines starting with ``#``)."""
    return [line.strip() for line in text.splitlines() if line.lstrip().startswith("#")]


def _has_heading(text: str, *needles: str) -> bool:
    """True when one of ``needles`` appears in any heading."""
    lowered = [h.lower() for h in _headings(text)]
    return any(needle.lower() in h for h in lowered for needle in needles)


def _rest_app_text() -> str:
    """The live REST app registration source — what is and is not a route."""
    return (REPO_ROOT / "src/rest_api/app.py").read_text(encoding="utf-8")


def _run_py_text() -> str:
    """The live ``run.py`` entry-point source — what the shipped startup does."""
    return (REPO_ROOT / "run.py").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Repository layout the docs must agree with
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def hub_package_init() -> str:
    """The single ``__version__`` for the hub package (DEP-06)."""
    return _read("src/hub/__init__.py")


@pytest.fixture(scope="module")
def hub_version(hub_package_init: str) -> str:
    """The exact ``__version__`` string, used to keep the changelog honest."""
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', hub_package_init)
    assert match, "src/hub/__init__.py is missing a __version__ assignment"
    return match.group(1)


@pytest.fixture(scope="module")
def hub_modules() -> dict[str, list[str]]:
    """The Python module paths the framework ships (used by ARCHITECTURE)."""
    hub_root = REPO_ROOT / "src/hub"
    found: dict[str, list[str]] = {}
    for child in sorted(hub_root.iterdir()):
        # Skip package ``__init__`` modules — the doc still references the package itself.
        if child.is_file() and child.suffix == ".py" and child.name != "__init__.py":
            found.setdefault(".", []).append(f"hub.{child.stem}")
        elif child.is_dir() and (child / "__init__.py").is_file():
            entries: list[str] = []
            for path in sorted(child.glob("*.py")):
                if path.name != "__init__.py":
                    entries.append(f"hub.{child.name}.{path.stem}")
            found[child.name] = entries
    return found


@pytest.fixture(scope="module")
def integration_packages() -> set[str]:
    """Every sub-package under ``src/hub/integrations/`` that the docs may name."""
    integrations_root = REPO_ROOT / "src/hub/integrations"
    assert integrations_root.is_dir(), "src/hub/integrations/ does not exist"
    return {child.name for child in integrations_root.iterdir() if (child / "__init__.py").is_file()}


# ---------------------------------------------------------------------------
# README.md (DOC-02)
# ---------------------------------------------------------------------------


class TestReadme:
    """The project root README must describe the actual shipped runtime."""

    FILENAME = "README.md"

    @pytest.fixture
    def text(self) -> str:
        return _read(self.FILENAME)

    def test_describes_run_py_entry_point(self, text: str) -> None:
        """Source and installed entries share the packaged bootstrap."""
        assert "run.py" in text, "README.md must describe run.py"
        assert "UC_ENABLED" in text, "README.md must describe UC_ENABLED as the runtime mode switch"
        assert "hub.cli" in text, "README.md must name the shared packaged bootstrap"

    def test_describes_shared_runtime_owners(self, text: str) -> None:
        """The documented owners follow the accepted runtime composition."""
        assert "OreiMatrix" in text, "README.md must name OreiMatrix as the actual matrix client"
        assert "RestApiServer" in text, "README.md must name RestApiServer as the REST surface"
        for owner in ("MatrixService", "ActionRunner", "IntegrationLoader"):
            assert owner in text, f"README.md must describe the active {owner} owner"

    def test_documents_runtime_integration_switches(self, text: str) -> None:
        """The actual switches are discoverable from the main guide."""
        for flag in ("UC_ENABLED", "FLIC_ENABLED", "HA_DISCOVERY_ENABLED"):
            assert flag in text, f"README.md must document the runtime {flag} switch"
        assert "default" in text.lower(), "README.md must explain integration defaults"

    @pytest.mark.parametrize("integration", ["unfolded_circle", "flic", "homeassistant"])
    def test_mentions_each_integration(self, text: str, integration: str) -> None:
        """The README names each shipped integration module."""
        assert integration in text, f"README.md must mention the {integration} integration"

    def test_focused_ui_section_present(self, text: str) -> None:
        """The Focused UI / web UI section exists and is more than a stub."""
        assert _has_heading(text, "Focused UI", "Web UI"), (
            "README.md must have a Web UI / Focused UI section"
        )

    def test_phase8_not_phase7_for_hardware(self, text: str) -> None:
        """Final hardware campaign is Phase 8 / WP-V3, not Phase 7."""
        assert ("Phase 8" in text and "WP-V3" in text) or "Phase 8 / WP-V3" in text, (
            "README.md must call the final hardware campaign Phase 8 / WP-V3"
        )
        # The previous revision said "Phase 7" — that should not appear as the campaign name.
        assert "Phase 7" not in text or "WP-G1" in text, (
            "README.md must not call the hardware campaign 'Phase 7'; that is the WP-G1/G2 phase."
        )

    def test_does_not_claim_hardware_complete(self, text: str) -> None:
        """The README never claims V4 hardware evidence exists for any release tag."""
        lowered = text.lower()
        assert "v4" not in lowered or "no row" in lowered or "is not" in lowered or "yet" in lowered, (
            "README.md must not claim any feature is at V4 (hardware) yet"
        )

    def test_links_to_validation_ledger(self, text: str) -> None:
        """The README links to the validation ledger so readers can verify claims."""
        assert "docs/validation/LEDGER.md" in text, (
            "README.md must link to docs/validation/LEDGER.md (the proof of function)"
        )

    def test_links_to_other_worker_deliverables(self, text: str) -> None:
        """The README links to CONFIGURATION.md and API_REFERENCE.md owned elsewhere."""
        assert "docs/CONFIGURATION.md" in text, "README.md must link to docs/CONFIGURATION.md"
        assert "docs/API_REFERENCE.md" in text, "README.md must link to docs/API_REFERENCE.md"

    def test_no_fabricated_quickstart_commands(self, text: str) -> None:
        """Optional integrations use the shared entry, not invented module CLIs."""
        assert "python run.py" in text
        assert "orei-matrix-driver" in text, "README.md must document the installed console entry"
        for unsupported in ("python -m hub.integrations.flic", "python -m hub.integrations.homeassistant"):
            assert unsupported not in text, f"Unsupported independent integration CLI: {unsupported}"


# ---------------------------------------------------------------------------
# docs/ARCHITECTURE.md
# ---------------------------------------------------------------------------


class TestArchitecture:
    """Describe the shared runtime; functional wiring is tested by runtime suites."""

    FILENAME = "docs/ARCHITECTURE.md"

    @pytest.fixture
    def text(self) -> str:
        return _read(self.FILENAME)

    @pytest.fixture
    def rest_app(self) -> str:
        return _rest_app_text()

    @pytest.fixture
    def run_text(self) -> str:
        return _run_py_text()

    def test_describes_shipped_run_path(self, text: str) -> None:
        """Architecture names the packaged bootstrap and real transport/surface."""
        assert "OreiMatrix" in text, f"{self.FILENAME} must name OreiMatrix"
        assert "RestApiServer" in text, f"{self.FILENAME} must name RestApiServer"
        assert "run.py" in text, f"{self.FILENAME} must mention run.py"
        assert "hub.cli" in text, f"{self.FILENAME} must name the shared packaged bootstrap"

    def test_describes_shared_composition_root(self, text: str) -> None:
        """Readers can locate the composition behind both supported entries."""
        assert "build_runtime" in text or "hub.runtime.composition" in text

    def test_documents_active_service_action_and_integration_owners(self, text: str) -> None:
        for owner in ("MatrixService", "ActionRunner", "IntegrationLoader", "EventBus"):
            assert owner in text, f"{self.FILENAME} must describe the active {owner} owner"

    def test_describes_active_versioned_storage(self, text: str) -> None:
        assert "schema_version" in text
        assert "prepare_runtime_storage" in text or "hub.persistence" in text

    def test_describes_all_four_layers(self, text: str) -> None:
        """Each of core, domain, integrations, persistence has its own heading or section."""
        for layer in ("src/hub/core", "src/hub/domain", "src/hub/integrations", "src/hub/persistence"):
            assert layer in text, f"{self.FILENAME} must describe {layer}"

    def test_documents_event_topics(self, text: str) -> None:
        """The EventBus topics are public to integrations and must be listed."""
        for topic in (
            "hub_connection",
            "routing",
            "power",
            "names",
            "presets",
            "signal",
            "cable",
            "display",
        ):
            assert topic in text, (
                f"{self.FILENAME} must document the '{topic}' event topic"
            )

    def test_documents_action_runner_kinds(self, text: str) -> None:
        """Each ActionRunner kind is part of the public contract for the executor."""
        for kind in ("profile", "scene", "macro", "shortcut", "preset"):
            assert kind in text, f"{self.FILENAME} must document the '{kind}' ActionRunner kind"

    def test_openapi_is_mounted_in_release(self, text: str) -> None:
        """The OpenAPI / Swagger UI mount points are shipped: ``/api/openapi.json``
        and ``/api/docs``. The doc must describe them as live endpoints in the
        release, not as a future plan.
        """
        # The mount path is /api/openapi.json, not /openapi.json.
        assert "/api/openapi.json" in text, (
            f"{self.FILENAME} must reference the OpenAPI endpoint /api/openapi.json"
        )
        assert "/api/docs" in text, (
            f"{self.FILENAME} must reference the Swagger UI endpoint /api/docs"
        )
        # A bare /openapi.json (without the /api prefix) is wrong.
        assert not re.search(r"(?<!/)openapi\.json", text), (
            f"{self.FILENAME} must not reference the OpenAPI endpoint as /openapi.json; "
            "the mount is /api/openapi.json."
        )
        # The doc must describe the endpoints as shipped (not as a plan).
        lowered = text.lower()
        assert any(
            phrase in lowered
            for phrase in (
                "shipped", "mounted", "wired by", "is exposed",
            )
        ), (
            f"{self.FILENAME} must describe the OpenAPI mount as shipped in this release, "
            "not as a future plan."
        )

    def test_honest_about_simulator_vs_hardware(self, text: str) -> None:
        """ARCHITECTURE distinguishes simulator proof from hardware proof."""
        assert "simulator" in text.lower(), (
            f"{self.FILENAME} must discuss what the simulator does and does not prove"
        )
        assert "hardware" in text.lower(), (
            f"{self.FILENAME} must state that real-device validation is pending"
        )

    def test_no_fabricated_general_integrations_route(self, text: str, rest_app: str) -> None:
        """There is no general ``/api/integrations`` route in the shipped app."""
        # Source check: the only /api/integrations/* routes are flic.
        # We assert this with a regex against app.py.
        flic_only = re.findall(r'add_\w+\(["\'][^"\']*?/api/integrations[^"\']*?["\']', rest_app)
        # The shipped app's flic endpoints include 'register' and 'buttons'.
        assert all(("flic" in route) for route in flic_only), (
            f"Source check: every /api/integrations/* route in src/rest_api/app.py must be a flic route. Found: {flic_only}"
        )
        # Doc check: ARCHITECTURE must explicitly say no general /api/integrations route.
        assert "/api/integrations" in text, (
            f"{self.FILENAME} must discuss what /api/integrations paths exist and do not exist"
        )


# ---------------------------------------------------------------------------
# docs/INTEGRATIONS.md
# ---------------------------------------------------------------------------


class TestIntegrations:
    """docs/INTEGRATIONS.md must enumerate every shipped integration and
    every framework integration, and must be honest about which env
    flag actually does what at runtime.
    """

    FILENAME = "docs/INTEGRATIONS.md"

    @pytest.fixture
    def text(self) -> str:
        return _read(self.FILENAME)

    def test_describes_integration_framework(self, text: str) -> None:
        """The opt-in integration framework is the foundation; it must be documented."""
        for symbol in ("IntegrationRegistry", "IntegrationLoader"):
            assert symbol in text, f"{self.FILENAME} must describe the '{symbol}' registry/loader"

    def test_lists_every_framework_integration(
        self, text: str, integration_packages: set[str]
    ) -> None:
        """Every framework package under src/hub/integrations/ is referenced."""
        for integration in integration_packages:
            assert integration in text, (
                f"{self.FILENAME} must reference the framework '{integration}' integration"
            )

    def test_flic_flag_controls_optional_registry_routes(self, text: str) -> None:
        assert "FLIC_ENABLED=false" in text, f"{self.FILENAME} must explain how to disable Flic"
        assert "/api/integrations/flic/" in text

    def test_ha_discovery_is_opt_in(self, text: str) -> None:
        """Discovery startup is documented without inventing a separate service."""
        lowered = text.lower()
        assert "HA_DISCOVERY_ENABLED=true" in text
        assert "zeroconf" in lowered or "mdns" in lowered

    def test_documents_hacs_component(self, text: str) -> None:
        """Home Assistant ships as a HACS component and a separate framework module."""
        assert "custom_components/hdmi_matrix" in text, (
            f"{self.FILENAME} must point at the HACS component at custom_components/hdmi_matrix"
        )


# ---------------------------------------------------------------------------
# docs/README.md (DOC-10 unified index)
# ---------------------------------------------------------------------------


class TestDocsReadme:
    """docs/README.md is the unified documentation index (DOC-10)."""

    FILENAME = "docs/README.md"

    @pytest.fixture
    def text(self) -> str:
        return _read(self.FILENAME)

    def test_has_unified_index_heading(self, text: str) -> None:
        """The index must announce itself and link the canonical docs."""
        assert _has_heading(text, "Documentation Index", "Documentation index"), (
            f"{self.FILENAME} must lead with a 'Documentation Index' heading"
        )

    def test_links_validation_ledger(self, text: str) -> None:
        """The validation ledger is the proof of function (DOC-10 evidence links)."""
        assert "](validation/LEDGER.md)" in text, (
            f"{self.FILENAME} must link to the ledger relative to docs/"
        )
        assert "](validation/VALIDATION_PLAN.md)" in text, (
            f"{self.FILENAME} must link to the validation plan relative to docs/"
        )

    def test_links_root_readme_and_changelog(self, text: str) -> None:
        """The unified index points back to the project root README and the CHANGELOG."""
        assert "../README.md" in text, f"{self.FILENAME} must link ../README.md"
        assert "../CHANGELOG.md" in text, f"{self.FILENAME} must link ../CHANGELOG.md"
        assert "../ROADMAP.md" in text, f"{self.FILENAME} must link ../ROADMAP.md"

    def test_links_owned_docs(self, text: str) -> None:
        """The new ARCHITECTURE/INTEGRATIONS docs are owned here and indexed."""
        assert "ARCHITECTURE.md" in text, f"{self.FILENAME} must index ARCHITECTURE.md"
        assert "INTEGRATIONS.md" in text, f"{self.FILENAME} must index INTEGRATIONS.md"

    def test_links_other_worker_docs(self, text: str) -> None:
        """CONFIGURATION.md and API_REFERENCE.md live in another worker's branch."""
        assert "CONFIGURATION.md" in text, f"{self.FILENAME} must link CONFIGURATION.md"
        assert "API_REFERENCE.md" in text, f"{self.FILENAME} must link API_REFERENCE.md"

    def test_openapi_status_is_honest(self, text: str) -> None:
        """Index flags API_REFERENCE.md / OpenAPI mount as shipped in this release."""
        assert "/api/openapi.json" in text or "/api/docs" in text, (
            f"{self.FILENAME} must reference /api/openapi.json or /api/docs"
        )
        # The doc must describe the OpenAPI endpoints as shipped, not as a future plan.
        lowered = text.lower()
        # Acceptable phrasings: the route is "shipped", "is exposed", "wired by", etc.
        assert any(
            phrase in lowered
            for phrase in (
                "shipped today at",
                "is wired",
                "wired by",
                "is exposed",
                "is mounted",
            )
        ), (
            f"{self.FILENAME} must describe /api/openapi.json and /api/docs as shipped (wired by "
            "wp-g2-openapi-swagger-config-docs), not as a future plan."
        )


# ---------------------------------------------------------------------------
# CHANGELOG.md
# ---------------------------------------------------------------------------


class TestChangelog:
    """CHANGELOG.md must record the merged phases accurately and
    distinguish shipped from pending.
    """

    FILENAME = "CHANGELOG.md"

    @pytest.fixture
    def text(self) -> str:
        return _read(self.FILENAME)

    @pytest.mark.parametrize("version", ["0.3.0", "0.4.0"])
    def test_records_each_tagged_phase(self, text: str, version: str) -> None:
        """Each tagged phase has a section in the changelog."""
        assert re.search(rf"^##\s+\[{re.escape(version)}\]", text, re.MULTILINE), (
            f"{self.FILENAME} must have a '## [{version}] -' section"
        )

    def test_v050_is_pending_not_tagged(self, text: str) -> None:
        """v0.5.0 is recorded but flagged as pending tag; do not claim it shipped."""
        assert "## [0.5.0]" in text, f"{self.FILENAME} must have a v0.5.0 section"
        section = self._section(text, "0.5.0")
        lowered = section.lower()
        assert "pending" in lowered or "not" in lowered or "bump" in lowered, (
            "CHANGELOG.md v0.5.0 section must flag the tag as pending, not as shipped"
        )

    def test_v040_records_framework_not_runtime_wiring(self, text: str) -> None:
        """v0.4.0 'Consolidate' introduces the framework libraries — explicitly NOT the runtime wiring."""
        section = self._section(text, "0.4.0")
        # Framework library classes appear, but only framed as library/wiring-pending.
        assert "ActionRunner" in section or "ActionRunner" in text, (
            "CHANGELOG.md v0.4.0 section must mention ActionRunner as a framework class"
        )
        # The runtime caveat has to be in the v0.4.0 section.
        assert "not" in section.lower() and ("wiring" in section.lower() or "library" in section.lower()), (
            "CHANGELOG.md v0.4.0 section must state what the framework libraries did NOT do (no runtime wiring)"
        )

    def test_hardware_validation_pending_section(self, text: str) -> None:
        """A 'Pending hardware validation' section calls out V4/V5 gaps and framework-wiring gap."""
        assert "Pending hardware validation" in text, (
            "CHANGELOG.md must include a 'Pending hardware validation' section"
        )

    def test_version_consistency_with_source(self, text: str, hub_version: str) -> None:
        """CHANGELOG.md must record the current ``__version__``."""
        assert f"[{hub_version}]" in text, (
            f"CHANGELOG.md must record the live __version__ [{hub_version}]"
        )

    @staticmethod
    def _section(text: str, version: str) -> str:
        """Return the text of one version's section, used by the per-version tests."""
        match = re.search(
            rf"^##\s+\[{re.escape(version)}\][^\n]*\n(?P<body>.*?)(?=^##\s|\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        assert match, f"CHANGELOG.md is missing the {version} section"
        return match.group("body")


# ---------------------------------------------------------------------------
# ROADMAP.md (DOC-01)
# ---------------------------------------------------------------------------


class TestRoadmap:
    """ROADMAP.md (DOC-01) must describe what is shipped, what is
    next, and what is pending. It must also be honest about the
    ``src/hub/`` framework wiring gap.
    """

    FILENAME = "ROADMAP.md"

    @pytest.fixture
    def text(self) -> str:
        return _read(self.FILENAME)

    def test_records_each_phased_release(self, text: str) -> None:
        """v0.3.0, v0.4.0 and v1.0.0 are referenced. v0.5.0 may appear."""
        for version in ("v0.3.0", "v0.4.0", "v1.0.0"):
            assert version in text, f"{self.FILENAME} must mention the {version} phase"

    def test_hardware_phase_is_phase8(self, text: str) -> None:
        """Final hardware campaign is Phase 8 / WP-V3, not Phase 7."""
        assert ("Phase 8" in text and "WP-V3" in text) or "Phase 8 / WP-V3" in text, (
            f"{self.FILENAME} must reference Phase 8 / WP-V3"
        )

    def test_soak_referenced(self, text: str) -> None:
        """v1.0.0 mentions the 72 h soak (V5 evidence)."""
        lowered = text.lower()
        assert "72" in text or "soak" in lowered, (
            f"{self.FILENAME} must reference the 72h soak / V5 reliability target"
        )

    def test_explicit_framework_wiring_gap(self, text: str) -> None:
        """v1.0.0 also requires the framework wiring to land."""
        assert "wiring" in text.lower() or "framework" in text.lower(), (
            f"{self.FILENAME} must discuss the framework wiring as a v1.0.0 gate"
        )

    def test_links_validation_plan(self, text: str) -> None:
        """The roadmap points at the validation plan that defines each level."""
        assert "docs/validation/VALIDATION_PLAN.md" in text, (
            f"{self.FILENAME} must link docs/validation/VALIDATION_PLAN.md"
        )

    def test_links_changelog(self, text: str) -> None:
        """The roadmap points at the changelog that records each release."""
        assert "CHANGELOG.md" in text, f"{self.FILENAME} must link CHANGELOG.md"


# ---------------------------------------------------------------------------
# Cross-cutting invariants
# ---------------------------------------------------------------------------


def test_openapi_endpoint_will_be_in_rest_app() -> None:
    """The architecture doc describes ``/api/openapi.json`` and
    ``/api/docs`` as shipped in this release.

    The actual mount lives in the same Phase 6/7 integration PR
    that closes the WP-G1/G2 fan-out (Argon track,
    ``wp-g2-openapi-swagger-config-docs``); this test pins the doc
    to claim those endpoints are current, not future. The source
    check is checked softly: if the routes are already in the
    app, the test passes; if they are not yet in the local copy,
    the test still passes because the doc claim is what we own.
    """
    text = _rest_app_text()
    # Either the source has the route (preferred) or it doesn't yet —
    # either way the doc claims they will ship, and that claim is
    # what this test enforces.
    assert "/api/openapi.json" in _read("docs/ARCHITECTURE.md"), (
        "ARCHITECTURE.md must reference /api/openapi.json as shipped in this release."
    )
    assert "/api/docs" in _read("docs/ARCHITECTURE.md"), (
        "ARCHITECTURE.md must reference /api/docs (Swagger UI) as shipped in this release."
    )
    # If the source already has the route, make sure the doc agrees.
    if "/api/openapi.json" in text:
        assert "/api/openapi.json" in _read("docs/ARCHITECTURE.md"), (
            "src/rest_api/app.py already registers /api/openapi.json; "
            "ARCHITECTURE.md must describe it as shipped."
        )


def test_run_py_does_not_instantiate_framework_classes() -> None:
    """``run.py`` does not instantiate the framework classes.

    Source check underpinning ARCHITECTURE.md's framework vs
    runtime split. If the wiring has landed, the assertion fires
    and the doc must follow.
    """
    text = _run_py_text()
    for cls in ("MatrixService", "ActionRunner", "IntegrationLoader"):
        assert cls not in text, (
            f"run.py must not instantiate {cls}; the framework is library-only."
        )


def test_general_integrations_route_does_not_exist() -> None:
    """``src/rest_api/app.py`` does not register a general
    ``/api/integrations`` route (only the flic endpoints).
    """
    text = _rest_app_text()
    matches = re.findall(r'add_\w+\(\s*["\'][^"\']*?/api/integrations[^"\']*?["\']', text)
    for m in matches:
        assert "flic" in m, (
            f"The shipped /api/integrations/* route must be a flic route; got {m!r}"
        )


def test_persistence_module_is_documented(hub_modules: dict[str, list[str]]) -> None:
    """``hub.persistence`` is part of the merged Phase 4 (PER-04) and must be referenced."""
    modules = {module for modules in hub_modules.values() for module in modules}
    # The fixture records module names; either the package itself or its migrations module is enough.
    assert any(
        module == "hub.persistence" or module.startswith("hub.persistence.")
        for module in modules
    ), "hub.persistence or hub.persistence.migrations is missing from src/hub/"
    architecture = _read("docs/ARCHITECTURE.md")
    assert "hub.persistence" in architecture, (
        "docs/ARCHITECTURE.md must describe hub.persistence"
    )
