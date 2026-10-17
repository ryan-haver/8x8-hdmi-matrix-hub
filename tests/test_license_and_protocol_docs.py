"""Tests for Third-Party Notices, Asset/License Audit, Protocol Documentation, and Local Links.

Owned scope for WP-G1 (UI-22, DOC-11):
- THIRD_PARTY_NOTICES.md: Audit of bundled assets, icons, fonts, runtime dependencies (UI-22).
- docs/OREI_API_COMMANDS.md: HTTP and Telnet protocol specification based on shipped code
  and real-device captures, clearly separating verified wire protocol from unknown physical effects (DOC-11).
- Local link integrity across both documents.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
THIRD_PARTY_NOTICES_MD = REPO_ROOT / "THIRD_PARTY_NOTICES.md"
OREI_API_COMMANDS_MD = REPO_ROOT / "docs" / "OREI_API_COMMANDS.md"
PROVENANCE_MD = REPO_ROOT / "web" / "assets" / "icons" / "PROVENANCE.md"
LICENSE_FILE = REPO_ROOT / "LICENSE"
SRC_OREI_MATRIX = REPO_ROOT / "src" / "orei_matrix.py"
SRC_TELNET_CLIENT = REPO_ROOT / "src" / "telnet_client.py"


@pytest.fixture(scope="module")
def notices_text() -> str:
    """Read THIRD_PARTY_NOTICES.md."""
    assert THIRD_PARTY_NOTICES_MD.is_file(), "THIRD_PARTY_NOTICES.md is missing from repo root"
    text = THIRD_PARTY_NOTICES_MD.read_text(encoding="utf-8")
    assert text.strip(), "THIRD_PARTY_NOTICES.md is empty"
    return text


@pytest.fixture(scope="module")
def protocol_text() -> str:
    """Read docs/OREI_API_COMMANDS.md."""
    assert OREI_API_COMMANDS_MD.is_file(), "docs/OREI_API_COMMANDS.md is missing"
    text = OREI_API_COMMANDS_MD.read_text(encoding="utf-8")
    assert text.strip(), "docs/OREI_API_COMMANDS.md is empty"
    return text


def _slugify(heading: str) -> str:
    """Convert markdown heading to anchor slug."""
    text = heading.strip().lower()
    # Remove markdown link formatting e.g. [text](link) -> text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove characters that aren't alphanumeric, spaces, or hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    # Replace whitespace and repeated hyphens with a single hyphen
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text


def _extract_headings(markdown_text: str) -> set[str]:
    """Extract all markdown heading slugs from a document."""
    slugs = set()
    for line in markdown_text.splitlines():
        match = re.match(r"^#{1,6}\s+(.+)$", line.strip())
        if match:
            slugs.add(_slugify(match.group(1)))
    return slugs


def _extract_markdown_links(markdown_text: str) -> list[tuple[str, str]]:
    """Extract (link_text, link_target) from markdown text, ignoring external http/https."""
    # Matches [text](target) but avoids images ![alt](target)
    pattern = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")
    links = []
    for match in pattern.finditer(markdown_text):
        text = match.group(1).strip()
        target = match.group(2).strip()
        links.append((text, target))
    return links


# =============================================================================
# 1. THIRD_PARTY_NOTICES.md & UI-22 Asset Audit Tests
# =============================================================================


class TestThirdPartyNotices:
    """Validates the license audit, provenance reporting, and third-party notices."""

    def test_file_exists_and_formatted(self, notices_text: str) -> None:
        assert len(notices_text) > 1000, "THIRD_PARTY_NOTICES.md is too short; must be comprehensive"
        assert notices_text.lstrip().startswith("#"), "Document must start with markdown heading"

    def test_project_license_reference(self, notices_text: str) -> None:
        assert "Mozilla Public License Version 2.0" in notices_text or "MPL-2.0" in notices_text
        assert "LICENSE" in notices_text
        assert LICENSE_FILE.is_file(), "Root LICENSE file must exist"

    def test_device_icons_provenance_and_ui22_documented(self, notices_text: str) -> None:
        """UI-22: Provenance, origin risk, and release gate status must be honest and clear."""
        assert "web/assets/icons/svg/" in notices_text
        assert "PROVENANCE.md" in notices_text
        assert "UI-22" in notices_text
        assert "potrace" in notices_text
        assert "convert-icons-to-svg.js" in notices_text
        assert "generate_clean_device_icons.py" in notices_text or "optimize_device_icons.py" in notices_text

        lowered = notices_text.lower()
        # Must clearly record the provenance history (unresolved risk resolved via in-house artwork)
        assert any(
            phrase in lowered
            for phrase in [
                "unresolved",
                "open provenance risk",
                "unlicensed",
                "resolved",
                "in-house",
            ]
        ), "Must honestly record the device icon provenance and license resolution"

    def test_device_icons_runtime_usage_clarified(self, notices_text: str) -> None:
        """Document must clarify that running UI does not load external SVGs."""
        assert "IconLibrary.getIconHtml()" in notices_text or "inline" in notices_text
        assert "does not load" in notices_text or "disabled" in notices_text

    def test_device_icons_budget_documented(self, notices_text: str) -> None:
        """Size budget (< 5,120 bytes) must be documented."""
        assert "5,120" in notices_text or "5 KB" in notices_text

    def test_in_house_brand_assets_documented(self, notices_text: str) -> None:
        """In-house favicon and HA brand assets must be documented under MPL-2.0."""
        assert "web/assets/favicon.svg" in notices_text
        assert "custom_components/hdmi_matrix/brand/icon.png" in notices_text
        assert "custom_components/hdmi_matrix/brand/icon@2x.png" in notices_text
        assert "MPL-2.0" in notices_text

    def test_inline_icons_documented(self, notices_text: str) -> None:
        """Inline icons in icon-library.js must be documented."""
        assert "web/js/utils/icon-library.js" in notices_text

    def test_font_audit_documented(self, notices_text: str) -> None:
        """Audit must state zero bundled font files and system font stacks."""
        lowered = notices_text.lower()
        assert "font" in lowered
        assert "none" in lowered or "zero" in lowered
        assert "system" in lowered

    @pytest.mark.parametrize(
        ("package", "expected_license"),
        [
            ("ucapi", "MPL-2.0"),
            ("pyee", "MIT"),
            ("aiohttp", "Apache"),
            ("psutil", "BSD"),
        ],
    )
    def test_python_runtime_dependencies_documented(
        self, notices_text: str, package: str, expected_license: str
    ) -> None:
        """All runtime Python packages and their licenses must be documented."""
        assert package in notices_text
        assert expected_license in notices_text

    def test_vendor_proprietary_hygiene_documented(self, notices_text: str) -> None:
        """SEC-14: Confirmation that proprietary vendor binaries were purged."""
        assert "SEC-14" in notices_text
        assert "XP3.exe" in notices_text or "firmware" in notices_text


# =============================================================================
# 2. docs/OREI_API_COMMANDS.md & Protocol Documentation Tests (DOC-11)
# =============================================================================


class TestProtocolDocumentation:
    """Validates HTTP and Telnet command fidelity and protocol vs physical separation."""

    def test_file_exists_and_formatted(self, protocol_text: str) -> None:
        assert len(protocol_text) > 2000, "docs/OREI_API_COMMANDS.md is too short"
        assert protocol_text.lstrip().startswith("#"), "Document must start with markdown heading"

    def test_protocol_vs_physical_separation_section(self, protocol_text: str) -> None:
        """DOC-11: Protocol specification must clearly distinguish verified protocol from unknown physical effects."""
        assert "Protocol Verification vs. Physical Hardware Effects" in protocol_text
        lowered = protocol_text.lower()
        assert "physical" in lowered
        assert "wire" in lowered or "protocol" in lowered
        assert "cec" in lowered
        assert "edid" in lowered
        assert "reboot" in lowered

    @pytest.mark.parametrize(
        "read_cmd",
        [
            "login",
            "get system status",
            "get output status",
            "get input status",
            "get video status",
            "get cec status",
            "get ext-audio status",
            "get status",
            "get network",
        ],
    )
    def test_all_http_reads_documented(self, protocol_text: str, read_cmd: str) -> None:
        """Every HTTP read command sent by the hub must be documented."""
        assert read_cmd in protocol_text, f"HTTP read command '{read_cmd}' is missing from OREI_API_COMMANDS.md"

    @pytest.mark.parametrize(
        "write_cmd",
        [
            "video switch",
            "set poweronoff",
            "set input name",
            "set output name",
            "set beep",
            "set panel lock",
            "preset set",
            "preset save",
            "preset name",
            "tx stream",
            "tx hdcp",
            "set hdr conversion",
            "set video scaler",
            "set arc",
            "set output audio mute",
            "set edid",
            "set lcd on time",
            "reboot",
            "set cec index",
            "cec command",
            "set ext-audio mode",
            "set ext-audio out",
            "ext-audio switch",
            "set ext-audio index",
        ],
    )
    def test_all_http_writes_documented(self, protocol_text: str, write_cmd: str) -> None:
        """Every HTTP write command implemented in orei_matrix.py must be documented."""
        assert write_cmd in protocol_text, f"HTTP write command '{write_cmd}' is missing from OREI_API_COMMANDS.md"

    @pytest.mark.parametrize(
        "rejected_cmd",
        [
            "get routing status",
            "preset get",
            "copy edid",
            "set input edid",
        ],
    )
    def test_rejected_and_legacy_commands_documented(self, protocol_text: str, rejected_cmd: str) -> None:
        """Unimplemented / rejected commands must be explicitly documented."""
        assert rejected_cmd in protocol_text, f"Rejected command '{rejected_cmd}' must be documented"

    def test_all_codebase_comheads_covered(self, protocol_text: str) -> None:
        """Cross-check every comhead string literal found in src/orei_matrix.py."""
        matrix_source = SRC_OREI_MATRIX.read_text(encoding="utf-8")
        comheads = set(re.findall(r'["\']comhead["\']:\s*["\']([^"\']+)["\']', matrix_source))
        assert len(comheads) >= 15, "Expected to find comheads in orei_matrix.py"
        for comhead in comheads:
            assert comhead in protocol_text, f"Comhead '{comhead}' from src/orei_matrix.py is missing from doc"

    def test_telnet_protocol_spec(self, protocol_text: str) -> None:
        """Telnet protocol details must be documented."""
        assert "Port 23" in protocol_text or "port 23" in protocol_text
        assert r"!\r\n" in protocol_text
        assert "E00" in protocol_text
        assert "E01" in protocol_text
        assert "echo" in protocol_text.lower()

    @pytest.mark.parametrize(
        "telnet_cmd",
        [
            "status!",
            "r fw version!",
            "r type!",
            "r link in",
            "r link out",
            "r preset",
            "s output",
            "power 0!",
            "power 1!",
            "s beep",
            "s lock",
            "s save preset",
            "s recall preset",
            "s clear preset",
            "s cec in",
            "s cec hdmi out",
        ],
    )
    def test_all_telnet_commands_documented(self, protocol_text: str, telnet_cmd: str) -> None:
        """All Telnet commands implemented in TelnetClient must be documented."""
        assert telnet_cmd in protocol_text, f"Telnet command '{telnet_cmd}' is missing from OREI_API_COMMANDS.md"

    def test_ninth_entry_behavior_documented(self, protocol_text: str) -> None:
        """The 9th element behavior in per-output arrays (HIL-04) must be documented."""
        assert "Ninth Entry" in protocol_text or "ninth entry" in protocol_text.lower()
        assert "255" in protocol_text

    def test_real_device_capture_references(self, protocol_text: str) -> None:
        """Must reference real-device capture fixtures and firmware version."""
        assert "BK-808_V1.10.01_web-V2.00.03" in protocol_text
        assert "V1.10.01" in protocol_text
        assert "V2.00.03" in protocol_text


# =============================================================================
# 3. Local Link Integrity Tests
# =============================================================================


class TestLocalMarkdownLinks:
    """Verifies all local file and anchor links in THIRD_PARTY_NOTICES.md and OREI_API_COMMANDS.md."""

    def _verify_links(self, doc_path: Path, doc_text: str) -> None:
        doc_dir = doc_path.parent
        headings = _extract_headings(doc_text)
        links = _extract_markdown_links(doc_text)

        assert len(links) > 0, f"Expected links in {doc_path.name}"

        for link_text, target in links:
            # Skip external links
            if target.startswith(("http://", "https://", "mailto:")):
                continue

            # Case A: Same-file anchor link e.g. #output-settings
            if target.startswith("#"):
                anchor = target.lstrip("#")
                assert anchor in headings, (
                    f"Broken anchor link '{target}' (text: '{link_text}') in {doc_path.name}. "
                    f"Available headings: {sorted(headings)}"
                )
                continue

            # Case B: Local relative file path (optionally with #anchor)
            if "#" in target:
                file_part, anchor_part = target.split("#", 1)
            else:
                file_part, anchor_part = target, None

            # Resolve relative to the document's directory
            resolved_path = (doc_dir / file_part).resolve()

            assert resolved_path.exists(), (
                f"Broken file link '{target}' (text: '{link_text}') in {doc_path.name}. "
                f"Resolved path does not exist: {resolved_path}"
            )

            # If an anchor in the target file is specified, check it
            if anchor_part and resolved_path.is_file() and resolved_path.suffix.lower() == ".md":
                target_text = resolved_path.read_text(encoding="utf-8")
                target_headings = _extract_headings(target_text)
                assert anchor_part in target_headings, (
                    f"Broken cross-file anchor link '{target}' in {doc_path.name}. "
                    f"Anchor '#{anchor_part}' not found in {resolved_path.name}."
                )

    def test_third_party_notices_local_links(self, notices_text: str) -> None:
        """All local links in THIRD_PARTY_NOTICES.md must resolve to existing files or anchors."""
        self._verify_links(THIRD_PARTY_NOTICES_MD, notices_text)

    def test_orei_api_commands_local_links(self, protocol_text: str) -> None:
        """All local links in docs/OREI_API_COMMANDS.md must resolve to existing files or anchors."""
        self._verify_links(OREI_API_COMMANDS_MD, protocol_text)
