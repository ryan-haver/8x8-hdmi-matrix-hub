"""WP-E2 Track 6: PWA manifest, icon provenance/size budget, API copy base URL, shortcuts input guard.

Covers the four UI issues closed in this track:

* **UI-21** - the plan claimed a PWA manifest, but ``web/manifest.json`` did not
  exist. It has to be a valid manifest *and* actually served: the app only routed
  ``/css``, ``/js`` and ``/assets``, so ``/manifest.json`` used to 404.
* **UI-22** - the device icons were potrace traces of a PNG sprite set of
  unknown licence, up to 376 KB each, and ``_icon-paths.json`` was 2.9 MB. Every
  SVG must now be under the 5 KB-per-icon budget documented in
  ``web/assets/icons/PROVENANCE.md``, and the provenance record must exist.
* **UI-18** - ``api-copy.js`` hard-coded ``http://<hostname>:8080``, so the
  copy-paste curl commands were wrong behind HTTPS, a reverse proxy or any port
  other than 8080. It must derive the base URL from ``window.location``.
* **UI-06** - ``handleKeydown`` only checked ``INPUT``/``TEXTAREA``/
  ``isContentEditable`` on the event target itself, so shortcuts fired while
  typing in a ``SELECT`` or inside a ``[contenteditable="true"]`` subtree, and
  Escape closed neither the top overlay nor the open input.

The JavaScript checks are source-level: the web UI is a set of classic
``<script>`` files with no test runner, so the invariants are asserted against
the shipped source. ``npm run lint:js`` is run when node_modules is present.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = REPO_ROOT / "web"
MANIFEST = WEB_DIR / "manifest.json"
ICONS_DIR = WEB_DIR / "assets" / "icons" / "svg"
PROVENANCE = WEB_DIR / "assets" / "icons" / "PROVENANCE.md"
FAVICON = WEB_DIR / "assets" / "favicon.svg"
API_COPY = WEB_DIR / "js" / "utils" / "api-copy.js"
KEYBOARD_SHORTCUTS = WEB_DIR / "js" / "components" / "keyboard-shortcuts.js"

# docs/REMEDIATION_PLAN.md: "Target < 5 KB per icon".
ICON_BUDGET_BYTES = 5120


# String literals are matched first so a "//" inside a URL or a template
# string is never mistaken for a comment.
JS_TOKEN_RE = re.compile(
    r"'(?:\\.|[^'\\])*'"
    r'|"(?:\\.|[^"\\])*"'
    r"|`(?:\\.|[^`\\])*`"
    r"|//[^\n]*"
    r"|/\*.*?\*/",
    re.DOTALL,
)


def strip_js_comments(source: str) -> str:
    """Drop ``//`` and ``/* */`` comments so checks see code, not prose.

    String literals survive untouched, and whitespace is collapsed so an
    expression wrapped over several lines still matches a single-line pattern.
    """
    without_comments = JS_TOKEN_RE.sub(
        lambda match: " " if match.group(0).startswith(("//", "/*")) else match.group(0),
        source,
    )
    return re.sub(r"\s+", " ", without_comments)


# =============================================================================
# UI-21: Web App Manifest
# =============================================================================


@pytest.fixture(scope="module")
def manifest() -> dict:
    """The parsed web app manifest."""
    assert MANIFEST.is_file(), "web/manifest.json is missing (UI-21)"
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:  # pragma: no cover - failure path
        pytest.fail(f"web/manifest.json is not valid JSON: {error}")


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("name", "OREI 8x8 HDMI Matrix Control"),
        ("short_name", "OREI Matrix"),
        ("start_url", "/"),
        ("display", "standalone"),
        ("background_color", "#09090d"),
        ("theme_color", "#00d4ff"),
    ],
)
def test_manifest_fields(manifest: dict, field: str, expected: str) -> None:
    """The identity, launch and colour fields the hub promised are present."""
    assert manifest.get(field) == expected, f"manifest {field!r} is {manifest.get(field)!r}, expected {expected!r}"


def test_manifest_colors_are_css_hex(manifest: dict) -> None:
    """background_color/theme_color must be #rrggbb, not a CSS keyword."""
    for field in ("background_color", "theme_color"):
        value = manifest[field]
        assert re.fullmatch(r"#[0-9a-fA-F]{6}", value), f"{field} is not a #rrggbb colour: {value!r}"


def test_manifest_icon_is_the_favicon(manifest: dict) -> None:
    """The single icon is the SVG favicon, declared maskable and scalable."""
    icons = manifest.get("icons")
    assert isinstance(icons, list) and icons, "manifest has no icons"
    favicon = next((icon for icon in icons if icon.get("src") == "/assets/favicon.svg"), None)
    assert favicon is not None, "manifest does not reference /assets/favicon.svg"
    assert favicon["type"] == "image/svg+xml"
    assert favicon["sizes"] == "any"
    assert favicon["purpose"] == "any maskable"
    assert FAVICON.is_file(), "the manifest icon /assets/favicon.svg does not exist"


def test_manifest_has_no_unknown_keys(manifest: dict) -> None:
    """Only keys the Web App Manifest spec defines, so no typo is shipped."""
    allowed = {
        "name", "short_name", "description", "start_url", "scope", "id", "display",
        "display_override", "orientation", "background_color", "theme_color",
        "categories", "icons", "screenshots", "shortcuts", "prefer_related_applications",
        "related_applications", "lang", "dir", "description",
    }
    unknown = set(manifest) - allowed
    assert not unknown, f"unknown manifest keys: {sorted(unknown)}"


def test_index_html_links_the_manifest() -> None:
    """A manifest nothing links to is not installed by any browser."""
    index = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    assert re.search(r'<link[^>]+rel="manifest"[^>]+href="/manifest\.json"', index), (
        "index.html does not link rel=\"manifest\" href=\"/manifest.json\""
    )


@pytest.mark.asyncio
async def test_manifest_is_served_at_the_origin_root(aiohttp_client) -> None:
    """GET /manifest.json returns the manifest: the spec fixes it at the root."""
    from rest_api import create_rest_app

    client = await aiohttp_client(create_rest_app())
    response = await client.get("/manifest.json")
    assert response.status == 200, f"/manifest.json returned {response.status}"
    assert response.content_type == "application/json"
    body = await response.json()
    assert body["short_name"] == "OREI Matrix"
    assert body["start_url"] == "/"


# =============================================================================
# UI-22: icon provenance and the 5 KB per-icon budget
# =============================================================================


def test_provenance_record_exists() -> None:
    """web/assets/icons/PROVENANCE.md documents where the icons came from."""
    assert PROVENANCE.is_file(), "web/assets/icons/PROVENANCE.md is missing (UI-22)"
    text = PROVENANCE.read_text(encoding="utf-8")
    assert len(text.strip()) > 500, "PROVENANCE.md is a stub"
    assert text.lstrip().startswith("#"), "PROVENANCE.md must start with a Markdown heading"


@pytest.mark.parametrize(
    "detail",
    [
        "convert-icons-to-svg.js",   # how the set was produced
        "potrace",                   # the tracer that inflated the files
        "_icon-paths.json",          # the 2.9 MB build artefact
        "5,120",                     # the budget the table is measured against
    ],
)
def test_provenance_covers_the_open_questions(provenance: str, detail: str) -> None:
    """The record names the origin, the tracer, the stale artefact and the budget."""
    assert detail in provenance, f"PROVENANCE.md does not mention {detail}"


def test_provenance_states_the_licence_status(provenance: str) -> None:
    """The licence is still unresolved, and the document must say so."""
    lowered = provenance.lower()
    assert "licence" in lowered
    assert "undetermined" in lowered or "unresolved" in lowered or "still open" in lowered, (
        "PROVENANCE.md must state that the icon licence is still unresolved"
    )


@pytest.fixture(scope="module")
def provenance() -> str:
    """The provenance document, read once for the whole module."""
    assert PROVENANCE.is_file(), "web/assets/icons/PROVENANCE.md is missing (UI-22)"
    return PROVENANCE.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def icons() -> list[Path]:
    """Every bundled device icon."""
    found = sorted(ICONS_DIR.glob("*.svg"))
    assert found, f"no SVG icons found in {ICONS_DIR}"
    return found


def test_icon_set_is_not_empty(icons: list[Path]) -> None:
    """A passing budget check over zero files would prove nothing."""
    assert len(icons) >= 40, f"expected the full icon set, found {len(icons)} files"


def test_unused_sprite_sheet_svg_is_not_in_icon_picker() -> None:
    """The raw sprite-sheet trace is not exposed as a selectable device icon."""
    picker_js = (WEB_DIR / "js" / "components" / "icon-picker.js").read_text(encoding="utf-8")
    assert "device_icons_set" not in picker_js


@pytest.mark.parametrize("icon", sorted(ICONS_DIR.glob("*.svg")), ids=lambda p: p.name)
def test_every_icon_is_valid_svg(icon: Path) -> None:
    """Each icon parses as XML, keeps its viewBox and inherits the text colour."""
    from xml.etree import ElementTree

    text = icon.read_text(encoding="utf-8")
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as error:
        pytest.fail(f"{icon.name} is not well-formed XML: {error}")

    assert root.tag == "{http://www.w3.org/2000/svg}svg", f"{icon.name} is not an <svg> element"
    view_box = root.get("viewBox")
    assert view_box, f"{icon.name} has no viewBox"
    assert re.fullmatch(r"-?\d+(\.\d+)? -?\d+(\.\d+)? \d+(\.\d+)? \d+(\.\d+)?", view_box), (
        f"{icon.name} has a malformed viewBox: {view_box!r}"
    )
    assert ("currentColor" in text or 'fill="' in text), f"{icon.name} does not specify a fill"


def test_provenance_lists_every_icon(provenance: str, icons: list[Path]) -> None:
    """The size table names each icon, so a new file cannot escape the record."""
    missing = [icon.name for icon in icons if f"`{icon.name}`" not in provenance]
    assert not missing, f"PROVENANCE.md does not list: {missing}"


# =============================================================================
# UI-18: api-copy base URL follows the page
# =============================================================================


@pytest.fixture(scope="module")
def api_copy() -> str:
    """The API copy utility source, comments stripped.

    Comments are removed because this module's own fix notes the old hard-coded
    URL; only executable code is interesting here.
    """
    return strip_js_comments(API_COPY.read_text(encoding="utf-8"))


def test_api_copy_uses_the_page_origin(api_copy: str) -> None:
    """The base URL comes from window.location, not from a hard-coded host."""
    assert "window.location.origin" in api_copy, (
        "api-copy.js must build its base URL from window.location.origin (UI-18)"
    )
    assert "${window.location.protocol}//${window.location.host}" in api_copy, (
        "api-copy.js must fall back to protocol//host when window.location.origin is missing"
    )


@pytest.mark.parametrize("hardcoded", [":8080", "location.hostname", "http://"])
def test_api_copy_has_no_hardcoded_host(api_copy: str, hardcoded: str) -> None:
    """No assumption about scheme or port survives in the copy utility."""
    assert hardcoded not in api_copy, (
        f"api-copy.js still hard-codes {hardcoded!r}; copy-paste commands break behind a proxy (UI-18)"
    )


# =============================================================================
# UI-06: keyboard shortcuts must not steal keys from text entry
# =============================================================================


@pytest.fixture(scope="module")
def shortcuts() -> str:
    """The keyboard shortcuts component source."""
    return KEYBOARD_SHORTCUTS.read_text(encoding="utf-8")


@pytest.mark.parametrize("guard", ["INPUT", "TEXTAREA", "SELECT", "isContentEditable", "contenteditable"])
def test_handle_keydown_guards_text_entry(shortcuts: str, guard: str) -> None:
    """Key handling ignores keys typed into fields and editable regions."""
    assert guard in shortcuts, f"keyboard-shortcuts.js does not guard against {guard} (UI-06)"


def test_input_guard_runs_before_the_shortcut_lookup(shortcuts: str) -> None:
    """The guard sits in the keydown path, not in an unused helper."""
    handler = shortcuts[shortcuts.index("static handleKeydown") :]
    assert "isTypingTarget" in handler, "handleKeydown does not consult the text-entry guard"
    assert handler.index("isTypingTarget") < handler.index("shortcuts.get(id)"), (
        "the guard has to run before a shortcut is dispatched (UI-06)"
    )


def test_escape_still_works_while_typing(shortcuts: str) -> None:
    """Escape is the exception: it blurs the field and closes the overlay."""
    body = shortcuts[shortcuts.index("static handleKeydown") :]
    assert "Escape" in body, "handleKeydown must let Escape through from a text field"
    assert ".blur()" in body, "Escape in a text field should blur it (UI-06)"


@pytest.mark.parametrize("closer", ["overlayStack?.closeTop()", "overlayManager?.closeActive()", "ContextMenu?.closeAll()"])
def test_escape_closes_the_top_overlay(shortcuts: str, closer: str) -> None:
    """One Escape closes the top overlay, the context menu or the help sheet."""
    assert closer in shortcuts, f"the Escape shortcut does not call {closer} (UI-06)"


# =============================================================================
# JavaScript lint baseline
# =============================================================================


@pytest.mark.skipif(shutil.which("npm") is None, reason="npm is not installed")
@pytest.mark.skipif(not (REPO_ROOT / "node_modules").is_dir(), reason="node_modules is not installed")
def test_javascript_lint_has_no_errors() -> None:
    """``npm run lint:js`` fails only on new violations; it must stay clean."""
    environment = dict(os.environ, npm_config_yes="true")
    result = subprocess.run(
        [shutil.which("npm"), "run", "--silent", "lint:js"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=600,
        env=environment,
    )
    assert result.returncode == 0, f"npm run lint:js reported problems:\n{result.stdout}\n{result.stderr}"
