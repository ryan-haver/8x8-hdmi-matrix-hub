"""
Structural tests for the project-root documentation the README, ARCHITECTURE,
INTEGRATIONS, ROADMAP, CHANGELOG and docs/README tasks own (DOC-02, DOC-10,
DOC-12). Each test asserts one thing the merged docs must keep doing, so a
later PR that loses the link to the modular runtime, drops a release version
from the changelog, or silently changes supported hardware breaks the build
instead of the user.

The tests read the docs as text and look for the strings the docs already
guarantee, so they stay meaningful when prose is rewritten as long as the
factual claims survive. They do not duplicate the existing
``tests/test_security_docs.py`` checks for SECURITY.md.

Conventions
-----------
- Every owned doc is a non-empty Markdown file at a stable path.
- Every section the doc claims to ship must appear as a heading.
- Every code path / route / env var the doc references must exist in the
  source tree the doc describes (``src/hub/...``, ``custom_components/...``,
  the ``hub/__init__.py`` ``__version__``).
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
    """The Python module paths the runtime actually ships (used by ARCHITECTURE)."""
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
    """The project root README must describe the actual modular runtime."""

    FILENAME = "README.md"

    @pytest.fixture(scope="class")
    def text(self) -> str:
        return _read(self.FILENAME)

    def test_mentions_actual_modular_runtime(self, text: str) -> None:
        """The README names the real hub package and the entry point."""
        assert "src/hub" in text, "README.md must describe the src/hub modular package"
        assert "run.py" in text, "README.md must describe run.py (the one entry point)"

    def test_mentions_core_services(self, text: str) -> None:
        """The README names each of the three layered owners by their public class."""
        for cls in ("MatrixService", "ActionRunner", "HubClient"):
            assert cls in text, f"README.md must mention {cls} (it is part of the modular runtime)"

    @pytest.mark.parametrize("integration", ["unfolded_circle", "flic", "homeassistant"])
    def test_mentions_each_integration(self, text: str, integration: str) -> None:
        """The README names each shipped integration module."""
        assert integration in text, f"README.md must mention the {integration} integration"

    def test_focused_ui_section_present(self, text: str) -> None:
        """The Focused UI / web UI section exists and is more than a stub."""
        assert _has_heading(text, "Focused UI", "Web UI"), (
            "README.md must have a Web UI / Focused UI section"
        )

    def test_does_not_claim_hardware_complete(self, text: str) -> None:
        """The README never claims hardware/soak validation is complete.

        The project has simulator scenarios (V2/V3) but no hardware-in-loop
        session yet for the v0.5.x line, so saying otherwise would be a lie.
        """
        lowered = text.lower()
        for forbidden in ("hardware validated", "hardware complete", "72h soak complete", "72h soak passed"):
            assert forbidden not in lowered, (
                f"README.md must not claim '{forbidden}' before HIL Session 2 finishes"
            )

    def test_links_to_validation_ledger(self, text: str) -> None:
        """The README links to the validation ledger so readers can verify claims."""
        assert "docs/validation/LEDGER.md" in text, (
            "README.md must link to docs/validation/LEDGER.md (the proof of function)"
        )

    def test_links_to_other_worker_deliverables(self, text: str) -> None:
        """The README links to CONFIGURATION.md and API_REFERENCE.md owned elsewhere.

        The wp-g2-openapi-swagger-config-docs worktree owns those files; the
        README must mention them so users find them even before they exist.
        """
        assert "docs/CONFIGURATION.md" in text, "README.md must link to docs/CONFIGURATION.md"
        assert "docs/API_REFERENCE.md" in text, "README.md must link to docs/API_REFERENCE.md"


# ---------------------------------------------------------------------------
# docs/ARCHITECTURE.md
# ---------------------------------------------------------------------------


class TestArchitecture:
    """docs/ARCHITECTURE.md must document the actual hub package layout."""

    FILENAME = "docs/ARCHITECTURE.md"

    @pytest.fixture(scope="class")
    def text(self) -> str:
        return _read(self.FILENAME)

    def test_describes_all_three_layers(self, text: str) -> None:
        """Each of core, domain, integrations has its own heading or section."""
        for layer in ("src/hub/core", "src/hub/domain", "src/hub/integrations"):
            assert layer in text, f"{self.FILENAME} must describe {layer}"

    def test_describes_persistence_layer(self, text: str) -> None:
        """Persistence migrations live in src/hub/persistence — document that."""
        assert "src/hub/persistence" in text, (
            f"{self.FILENAME} must describe src/hub/persistence (versioned migrations, PER-04)"
        )

    def test_names_every_published_module(
        self, text: str, hub_modules: dict[str, list[str]]
    ) -> None:
        """Every Python module the hub ships appears in the docs.

        This is the layer of the docs the user looks at when wiring a new
        client against the hub. A missing module is an onboarding hazard.
        """
        all_modules = [module for modules in hub_modules.values() for module in modules]
        for module in all_modules:
            assert module in text, f"{self.FILENAME} must reference {module}"

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
                f"{self.FILENAME} must document the '{topic}' event topic (it is part of HubEvent.topic)"
            )

    def test_documents_action_runner_kinds(self, text: str) -> None:
        """Each ActionRunner kind is part of the public contract for the executor."""
        for kind in ("profile", "scene", "macro", "shortcut", "preset"):
            assert kind in text, f"{self.FILENAME} must document the '{kind}' ActionRunner kind"

    def test_documents_openapi_generation(self, text: str) -> None:
        """OpenAPI/Swagger is a Phase 4 deliverable; the architecture must mention it."""
        assert "OpenAPI" in text, f"{self.FILENAME} must describe OpenAPI generation"
        assert "/api/docs" in text, f"{self.FILENAME} must mention the /api/docs Swagger UI route"

    def test_honest_about_simulator_vs_hardware(self, text: str) -> None:
        """ARCHITECTURE distinguishes simulator proof from hardware proof."""
        assert "simulator" in text.lower(), (
            f"{self.FILENAME} must discuss what the simulator does and does not prove"
        )
        assert "hardware" in text.lower(), (
            f"{self.FILENAME} must state that real-device validation is pending"
        )


# ---------------------------------------------------------------------------
# docs/INTEGRATIONS.md
# ---------------------------------------------------------------------------


class TestIntegrations:
    """docs/INTEGRATIONS.md must enumerate every shipped integration module."""

    FILENAME = "docs/INTEGRATIONS.md"

    @pytest.fixture(scope="class")
    def text(self) -> str:
        return _read(self.FILENAME)

    def test_describes_integration_framework(self, text: str) -> None:
        """The opt-in integration framework is the foundation; it must be documented."""
        for symbol in ("IntegrationRegistry", "IntegrationLoader"):
            assert symbol in text, f"{self.FILENAME} must describe the '{symbol}' registry/loader"

    def test_lists_every_shipped_integration(self, text: str, integration_packages: set[str]) -> None:
        """Every integration package under src/hub/integrations/ has a section."""
        for integration in integration_packages:
            assert integration in text, (
                f"{self.FILENAME} must have a section for the '{integration}' integration"
            )

    def test_documents_hub_client_transports(self, text: str) -> None:
        """The two HubClient transports are public — both must be described."""
        for transport in ("HubClientLocal", "HubClientHttp"):
            assert transport in text, f"{self.FILENAME} must describe {transport}"

    def test_documents_hacs_component(self, text: str) -> None:
        """Home Assistant ships as a HACS component and a built-in integration."""
        assert "custom_components/hdmi_matrix" in text, (
            f"{self.FILENAME} must point at the HACS component at custom_components/hdmi_matrix"
        )


# ---------------------------------------------------------------------------
# docs/README.md (DOC-10 unified index)
# ---------------------------------------------------------------------------


class TestDocsReadme:
    """docs/README.md is the unified documentation index (DOC-10)."""

    FILENAME = "docs/README.md"

    @pytest.fixture(scope="class")
    def text(self) -> str:
        return _read(self.FILENAME)

    def test_has_unified_index_heading(self, text: str) -> None:
        """The index must announce itself and link the canonical docs."""
        assert _has_heading(text, "Documentation Index", "Documentation index"), (
            f"{self.FILENAME} must lead with a 'Documentation Index' heading"
        )

    def test_links_validation_ledger(self, text: str) -> None:
        """The validation ledger is the proof of function (DOC-10 evidence links)."""
        assert "docs/validation/LEDGER.md" in text, (
            f"{self.FILENAME} must link docs/validation/LEDGER.md (the feature ledger)"
        )
        assert "docs/validation/VALIDATION_PLAN.md" in text, (
            f"{self.FILENAME} must link docs/validation/VALIDATION_PLAN.md"
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


# ---------------------------------------------------------------------------
# CHANGELOG.md
# ---------------------------------------------------------------------------


class TestChangelog:
    """CHANGELOG.md must record the merged phases accurately (DOC-12)."""

    FILENAME = "CHANGELOG.md"

    @pytest.fixture(scope="class")
    def text(self) -> str:
        return _read(self.FILENAME)

    @pytest.mark.parametrize("version", ["0.3.0", "0.4.0", "0.5.0"])
    def test_records_each_merged_phase(self, text: str, version: str) -> None:
        """Each merged phase has a section in the changelog."""
        assert re.search(rf"^##\s+\[{re.escape(version)}\]", text, re.MULTILINE), (
            f"{self.FILENAME} must have a '## [{version}] -' section"
        )

    def test_v030_records_security_phase(self, text: str) -> None:
        """v0.3.0 'Secure' is the result of Phase 3."""
        section = self._section(text, "0.3.0")
        assert re.search(r"security", section, re.IGNORECASE), (
            "CHANGELOG.md v0.3.0 section must mention security (Phase 3 is 'WP-F1 Secure')"
        )

    def test_v040_records_backend_consolidation(self, text: str) -> None:
        """v0.4.0 'Consolidate' is the result of Phase 4 (WP-C3 backend consolidation)."""
        section = self._section(text, "0.4.0")
        for needle in ("MatrixService", "ActionRunner", "HubClient"):
            assert needle in section, (
                f"CHANGELOG.md v0.4.0 section must mention the new {needle} class"
            )

    def test_v050_records_focused_ui(self, text: str) -> None:
        """v0.5.0 'Focused UI' is the result of Phase 5 (WP-E2 UI simplification)."""
        section = self._section(text, "0.5.0")
        for needle in ("UnifiedSettingsController", "OverlayManager", "EditorShell", "KioskController"):
            assert needle in section, (
                f"CHANGELOG.md v0.5.0 section must mention the new {needle}"
            )

    def test_honest_about_unreleased(self, text: str) -> None:
        """The changelog must not call unreleased work released."""
        assert "Unreleased" not in text, (
            "CHANGELOG.md must not have an unreleased section once v0.5.0 has shipped"
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
    """ROADMAP.md (DOC-01) must describe what is shipped, what is next, and what is pending."""

    FILENAME = "ROADMAP.md"

    @pytest.fixture(scope="class")
    def text(self) -> str:
        return _read(self.FILENAME)

    def test_records_each_phased_release(self, text: str) -> None:
        """v0.3.0, v0.4.0, v0.5.0 and v1.0.0 all appear as planned / shipped phases."""
        for version in ("v0.3.0", "v0.4.0", "v0.5.0", "v1.0.0"):
            assert version in text, f"{self.FILENAME} must mention the {version} phase"

    def test_documents_v100_gate_is_hardware(self, text: str) -> None:
        """v1.0.0 depends on hardware-in-loop evidence (Phase 8, WP-V3)."""
        lowered = text.lower()
        assert "hardware" in lowered, f"{self.FILENAME} must say v1.0.0 needs hardware evidence"
        assert "72" in text or "soak" in lowered, (
            f"{self.FILENAME} must reference the 72h soak / V5 reliability target"
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


def test_version_consistency(hub_version: str) -> None:
    """The repo's runtime version is the same as the changelog's current one.

    ``src/hub/__init__.__version__`` is the source of truth (DEP-06).
    The CHANGELOG.md entry that records the current release must agree, so
    a stale release note fails the test instead of shipping.
    """
    changelog = _read("CHANGELOG.md")
    assert f"[{hub_version}]" in changelog, (
        f"CHANGELOG.md is missing a '[{hub_version}] -' entry; the changelog must record the current version"
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
        "docs/ARCHITECTURE.md must describe hub.persistence (versioned migrations, PER-04)"
    )
