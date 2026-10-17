"""
WP-E2 Track 5: the design token sheet (``web/css/tokens.css``) and the Tron
background's frame budget (``web/js/tron-background.js``).

Two deliverables, two kinds of check:

* **Tokens.** The rest of Phase 5 (and the kiosk) is supposed to be built on
  ``web/css/tokens.css``, so this module pins the contract that sheet has to
  keep: the surface and accent tokens, the four Tron presets, semantic status
  colours that stay distinct whichever accent is active, the spacing / radius /
  z-index scales, the 44px touch target (UI-15), the focus ring and the
  reduced-motion override. A token renamed or dropped breaks the UI silently -
  it falls back to no value at all - so the checks fail instead.
* **Animation budget.** ``web/js/tron-background.js`` used to redraw every
  ~16ms frame with heavy canvas shadow blur and never looked at the OS motion
  setting (UI-16). The class is loaded into a stubbed DOM in Node and driven
  frame by frame, so the 30 fps cap, the reduced-motion pause and the low-power
  shadow-blur cap are verified as *behaviour*, not by grepping the source.

The Node and npm gates skip when the toolchain is absent (the pytest CI job has
no Node), so the static token checks still run everywhere.
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TOKENS_CSS = REPO_ROOT / "web" / "css" / "tokens.css"
TRON_JS = REPO_ROOT / "web" / "js" / "tron-background.js"
INDEX_HTML = REPO_ROOT / "web" / "index.html"

#: The four Tron presets of the token sheet (docs/ui/LOOK_AND_FEEL.md 2.2).
THEMES = ("ares", "legacy", "cluu", "athena")

#: Accent channels a preset is allowed to move; anything else stays shared.
ACCENT_CHANNELS = ("--accent-h", "--accent-s", "--accent-l", "--secondary-h")

#: Semantic status colours (UI-20).
STATUS_TOKENS = ("--color-success", "--color-warning", "--color-error", "--color-info")


# =============================================================================
# Token sheet: helpers
# =============================================================================


@pytest.fixture(scope="module")
def tokens_css() -> str:
    """The text of web/css/tokens.css, read once for the whole module."""
    assert TOKENS_CSS.is_file(), "web/css/tokens.css is missing (WP-E2 Track 5 deliverable)"
    text = TOKENS_CSS.read_text(encoding="utf-8")
    assert text.strip(), "web/css/tokens.css is empty"
    return text


def _block(text: str, open_brace: int) -> str:
    """Return the body of the brace block that starts at *open_brace* (nesting aware)."""
    depth = 1
    index = open_brace + 1
    while index < len(text) and depth:
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
        index += 1
    return text[open_brace + 1 : index - 1]


def _rule_body(text: str, selector: str) -> str:
    """Return the declarations block for the first rule with *selector*."""
    match = re.search(rf"(?m)^\s*{re.escape(selector)}\s*\{{", text)
    assert match, f"tokens.css has no `{selector}` rule"
    return _block(text, match.end() - 1)


def _declarations(body: str) -> dict[str, str]:
    """Parse `--name: value;` custom properties out of a declarations block."""
    found = {}
    for name, value in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", body):
        found[name] = " ".join(value.split())
    return found


def _properties(body: str) -> dict[str, str]:
    """Parse `prop: value;` declarations of any property out of a block."""
    found = {}
    for name, value in re.findall(r"([-*\w]+)\s*:\s*([^;{}]+);", body):
        found[name] = " ".join(value.split())
    return found


def _root(text: str) -> dict[str, str]:
    """The custom properties declared on :root."""
    return _declarations(_rule_body(text, ":root"))


def _pixels(value: str) -> float:
    """The numeric part of a `12px`-style value."""
    match = re.match(r"-?[\d.]+", value)
    assert match, f"{value!r} is not a length"
    return float(match.group())


def _hue(value: str) -> float:
    """The hue channel of an `hsl(210 80% 50%)`-style value."""
    match = re.search(r"hsl\(\s*([\d.]+)", value)
    assert match, f"{value!r} is not an hsl() colour"
    return float(match.group(1))


# =============================================================================
# Token sheet: surfaces, accent system and presets
# =============================================================================


def test_tokens_css_exists(tokens_css: str) -> None:
    """The consolidated sheet exists and is the single source for both UIs."""
    assert ":root" in tokens_css, "tokens.css must define the tokens on :root"
    assert "docs/ui/LOOK_AND_FEEL.md" in tokens_css, "tokens.css must point at the look-and-feel spec"


@pytest.mark.parametrize(
    "token",
    [
        "--bg-primary",
        "--bg-secondary",
        "--bg-tertiary",
        "--bg-elevated",
        "--bg-glass",
        "--bg-glass-heavy",
    ],
)
def test_surface_tokens(tokens_css: str, token: str) -> None:
    """Every background/surface layer of LOOK_AND_FEEL.md 3 is a token."""
    value = _root(tokens_css).get(token)
    assert value, f"tokens.css does not define the surface token {token}"
    assert re.search(r"(#[0-9a-f]{3,8}|rgba?\(|hsla?\()", value, re.I), f"{token} must be a colour, got {value!r}"


@pytest.mark.parametrize(
    "token",
    [
        "--accent-h",
        "--accent-s",
        "--accent-l",
        "--secondary-h",
        "--accent-primary",
        "--accent-secondary",
        "--accent-glow",
    ],
)
def test_accent_system_tokens(tokens_css: str, token: str) -> None:
    """The dynamic HSL accent system is present on :root."""
    assert token in _root(tokens_css), f"tokens.css does not define the accent token {token}"


def test_accent_colours_are_derived_from_the_channels(tokens_css: str) -> None:
    """Accent colours are computed from --accent-h/-s/-l, never a literal hue.

    That is what makes a preset a two-line change instead of a search-and-replace
    across every stylesheet.
    """
    root = _root(tokens_css)
    assert root["--accent-primary"].startswith("hsl(var(--accent-h)"), root["--accent-primary"]
    assert "var(--accent-h)" in root["--accent-glow"], root["--accent-glow"]
    assert "var(--secondary-h)" in root["--accent-secondary"], root["--accent-secondary"]


@pytest.mark.parametrize("theme", THEMES)
def test_tron_presets_define_the_accent_channels(tokens_css: str, theme: str) -> None:
    """Each of the four presets is a `[data-tron-theme]` rule over the channels."""
    body = _rule_body(tokens_css, f"[data-tron-theme='{theme}']")
    declared = _declarations(body)
    for channel in ACCENT_CHANNELS:
        assert channel in declared, f"preset '{theme}' does not set {channel}"
    for hue_channel in ("--accent-h", "--secondary-h"):
        hue = _pixels(declared[hue_channel])
        assert 0 <= hue <= 360, f"preset '{theme}': {hue_channel}={hue} is not a hue"
    for percent_channel in ("--accent-s", "--accent-l"):
        assert declared[percent_channel].endswith("%"), f"preset '{theme}': {percent_channel} needs a percentage"


def test_presets_only_move_the_accent_channels(tokens_css: str) -> None:
    """A preset may not touch surfaces, spacing, layers or motion.

    Keeping the blast radius at four hue channels is what makes "error stays red
    in every preset" and "spacing never shifts with a theme" true by construction.
    """
    for theme in THEMES:
        declared = _declarations(_rule_body(tokens_css, f"[data-tron-theme='{theme}']"))
        unexpected = set(declared) - set(ACCENT_CHANNELS)
        assert not unexpected, f"preset '{theme}' overrides non-accent tokens: {sorted(unexpected)}"


def test_the_four_presets_use_four_distinct_accent_hues(tokens_css: str) -> None:
    """Two presets sharing a primary hue would make one of them unreachable."""
    hues = {}
    for theme in THEMES:
        body = _declarations(_rule_body(tokens_css, f"[data-tron-theme='{theme}']"))
        hues[theme] = (float(body["--accent-h"]), float(body["--secondary-h"]))
    assert len(set(hues.values())) == len(THEMES), f"presets share a hue pairing: {hues}"


# =============================================================================
# Token sheet: status colours (UI-20)
# =============================================================================


def test_status_colors_are_defined(tokens_css: str) -> None:
    """The four semantic status colours exist as tokens."""
    root = _root(tokens_css)
    for token in STATUS_TOKENS:
        assert token in root, f"tokens.css does not define the status token {token}"
        assert root[token].startswith("hsl("), f"{token} must be an hsl() colour, got {root[token]}"


def test_status_colors_are_not_derived_from_the_accent(tokens_css: str) -> None:
    """Status colours are fixed hues, so they survive an accent swap.

    The old tokens derived error from `accent hue + 120`, which turned it blue
    under a cyan theme and green under an orange one.
    """
    for token in STATUS_TOKENS:
        value = _root(tokens_css)[token]
        assert "var(--accent-h)" not in value, f"{token} follows the accent hue: {value}"
        assert "var(--secondary-h)" not in value, f"{token} follows the secondary hue: {value}"


def test_status_colors_are_pairwise_distinct_in_every_theme(tokens_css: str) -> None:
    """Success, warning, error and info never collide, in any of the four presets."""
    root = _root(tokens_css)
    for theme in THEMES:
        block = _declarations(_rule_body(tokens_css, f"[data-tron-theme='{theme}']"))
        resolved = {token: block.get(token, root[token]) for token in STATUS_TOKENS}
        assert len(set(resolved.values())) == len(STATUS_TOKENS), f"theme '{theme}': {resolved}"


@pytest.mark.parametrize("first,second", [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
def test_status_hues_are_widely_separated(tokens_css: str, first: int, second: int) -> None:
    """Two status colours need a real hue gap, not a different shade of one hue.

    Below ~30 degrees apart they read as the same colour on a small status pill,
    which is exactly the confusion UI-20 is about.
    """
    root = _root(tokens_css)
    a = _hue(root[STATUS_TOKENS[first]])
    b = _hue(root[STATUS_TOKENS[second]])
    gap = abs(a - b) % 360
    gap = min(gap, 360 - gap)
    assert gap >= 30, (
        f"{STATUS_TOKENS[first]} ({a}deg) and {STATUS_TOKENS[second]} ({b}deg) are only {gap:.0f}deg apart"
    )


# =============================================================================
# Token sheet: scales, layering and touch target
# =============================================================================


def test_spacing_scale(tokens_css: str) -> None:
    """--space-1..--space-12 is a 4px-base ascending scale (LOOK_AND_FEEL.md 5)."""
    root = _root(tokens_css)
    spaces = {}
    for step in range(1, 13):
        token = f"--space-{step}"
        assert token in root, f"tokens.css does not define the spacing token {token}"
        spaces[step] = _pixels(root[token])
    values = [spaces[step] for step in range(1, 13)]
    assert values == sorted(values), f"the spacing scale is not monotonic: {values}"
    assert values[0] == 4, f"the scale must start at the 4px base, got {values[0]}"
    for step, value in spaces.items():
        assert value % 4 == 0, f"--space-{step} ({value}px) is not on the 4px grid"


def test_radius_scale(tokens_css: str) -> None:
    """Radii run from small chips to fully round pills (LOOK_AND_FEEL.md 5)."""
    root = _root(tokens_css)
    for token in ("--radius-sm", "--radius-md", "--radius-lg", "--radius-xl", "--radius-full"):
        assert token in root, f"tokens.css does not define the radius token {token}"
    ordered = ["--radius-sm", "--radius-md", "--radius-lg", "--radius-xl"]
    values = [_pixels(root[token]) for token in ordered]
    assert values == sorted(values), f"the radius scale is not monotonic: {values}"
    assert _pixels(root["--radius-full"]) >= 999, "--radius-full must round a pill/circle off"


def test_z_index_scale(tokens_css: str) -> None:
    """The layer tokens keep the order LOOK_AND_FEEL.md 5 documents.

    Drawers under modals under toasts is what UI-32/UI-59 verified; the numbers
    here must not drift apart from the ones already in use.
    """
    root = _root(tokens_css)
    expected = {
        "--z-base": 0,
        "--z-popover": 100,
        "--z-sticky": 200,
        "--z-drawer": 450,
        "--z-modal": 500,
        "--z-toast": 600,
    }
    actual = {}
    for token, value in expected.items():
        assert token in root, f"tokens.css does not define the layer token {token}"
        actual[token] = int(_pixels(root[token]))
    assert actual == expected, f"the layer scale drifted from the documented one: {actual}"
    assert actual["--z-drawer"] < actual["--z-modal"] < actual["--z-toast"], "a drawer hides under a modal or a toast"


def test_minimum_touch_target(tokens_css: str) -> None:
    """UI-15: no pointer target smaller than 44x44 CSS px."""
    root = _root(tokens_css)
    assert "--touch-target-min" in root, "tokens.css does not define --touch-target-min"
    value = root["--touch-target-min"]
    assert value == "44px", f"--touch-target-min must be 44px (WCAG 2.5.5), got {value}"


# =============================================================================
# Token sheet: accessibility rules
# =============================================================================


def test_focus_ring_uses_the_accent(tokens_css: str) -> None:
    """Keyboard focus is visible on every surface, drawn with the accent colour."""
    root = _root(tokens_css)
    body = _rule_body(tokens_css, ":focus-visible")
    declarations = _properties(body)
    outline = declarations.get("outline", "")
    assert "var(--accent-primary)" in outline, f"the focus ring must use --accent-primary, got {outline!r}"
    assert _pixels(root["--focus-ring-width"]) >= 2, "the focus ring must be at least 2px wide"
    offset = declarations.get("outline-offset", "")
    assert "var(--focus-ring-offset)" in offset, f"the focus ring needs an offset token, got {offset!r}"


def test_reduced_motion_collapses_durations(tokens_css: str) -> None:
    """`prefers-reduced-motion: reduce` makes transitions and animations instant.

    0.01ms, not 0s: a zero duration suppresses the transitionend/animationend
    events some components wait on.
    """
    match = re.search(r"@media\s*\(\s*prefers-reduced-motion\s*:\s*reduce\s*\)\s*\{", tokens_css)
    assert match, "tokens.css has no prefers-reduced-motion block (LOOK_AND_FEEL.md 6)"
    body = _block(tokens_css, match.end() - 1)
    assert "0.01ms" in body, "the reduced-motion block must collapse durations to 0.01ms"
    for declaration in ("transition-duration", "animation-duration"):
        assert declaration in body, f"the reduced-motion block must set {declaration}"
        rule = re.search(rf"{declaration}\s*:\s*([^;]+);", body)
        assert rule and "0.01ms" in rule.group(1), f"{declaration} must be 0.01ms under reduced motion"
    nested = re.search(r":root\s*\{", body)
    assert nested, "the reduced-motion block must collapse the duration tokens too"
    duration_tokens = _declarations(_block(body, nested.end() - 1))
    for token in ("--duration-fast", "--duration-normal", "--duration-slow"):
        assert duration_tokens.get(token) == "0.01ms", f"{token} must be 0.01ms under reduced motion"


def test_tokens_are_loaded_before_the_legacy_sheets() -> None:
    """tokens.css may never be linked after the sheets it consolidates.

    theme.css and style.css still hold the legacy declarations; if tokens.css
    came later in the cascade it would silently repaint every screen, and its
    global `:focus-visible` / reduced-motion rules would do the same. The sheet
    is not linked at all today (see its header), so this only bites when the
    switch is flipped - which is exactly when it should be checked.
    """
    html = INDEX_HTML.read_text(encoding="utf-8")
    tokens_at = html.find("/css/tokens.css")
    if tokens_at == -1:
        return
    for legacy in ("/css/theme.css", "/css/style.css"):
        assert tokens_at < html.find(legacy), f"tokens.css must be linked before {legacy}"


# =============================================================================
# Lint gates
# =============================================================================


def _npm(*args: str) -> "subprocess.CompletedProcess[str]":
    """Run an npm script from the repository root, skipping when Node is absent."""
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if npm is None:
        pytest.skip("npm is not installed; skipping the UI lint gate")
    if not (REPO_ROOT / "node_modules").is_dir():
        pytest.skip("node_modules is missing; run `npm ci` first")
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [npm, *args],
        capture_output=True,
        text=True,
        timeout=900,
        cwd=REPO_ROOT,
        check=False,
    )


def test_tokens_css_lints_clean() -> None:
    """The token sheet is stylelint-clean on its own, zero findings.

    It is the one file allowed to hold literal colours, so anything else in it
    (a stray shorthand, a deprecated keyword, a descending specificity) has
    nowhere to hide.
    """
    proc = _npm("exec", "--no-install", "--", "stylelint", "web/css/tokens.css")
    assert proc.returncode == 0, f"stylelint findings in web/css/tokens.css:\n{proc.stdout}{proc.stderr}"
    assert proc.stdout.strip() == "", f"stylelint reported findings in web/css/tokens.css:\n{proc.stdout}"


def test_css_lint_gate() -> None:
    """`npm run lint:css` - no new stylelint findings anywhere in web/css/."""
    proc = _npm("run", "lint:css")
    assert proc.returncode == 0, f"npm run lint:css failed:\n{proc.stdout}{proc.stderr}"


def test_js_lint_gate() -> None:
    """`npm run lint:js` - the Tron background changes stay within the baseline."""
    proc = _npm("run", "lint:js")
    assert proc.returncode == 0, f"npm run lint:js failed:\n{proc.stdout}{proc.stderr}"


# =============================================================================
# Tron background: frame budget, motion preference and low power (UI-16)
# =============================================================================

# A headless DOM: enough for TronBackground.init()/render(), and a requestAnimationFrame
# we can step by hand. Scenarios are printed as JSON so the assertions below read
# like the behaviour they check, not like the implementation.
TRON_HARNESS_JS = r"""
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(process.argv[2], 'utf8');
const scenario = process.argv[3];

function buildWorld({ reducedMotion = false, cores = 8, memory = 8 } = {}) {
    const calls = { renders: 0, frames: 0, scheduled: 0, shadowBlurs: [] };
    let rafCallback = null;
    let clock = 0;

    const gradient = { addColorStop() {} };
    const ctx2d = new Proxy(
        {},
        {
            get(target, prop) {
                if (prop in target) return target[prop];
                if (prop === 'createRadialGradient' || prop === 'createLinearGradient') return () => gradient;
                return () => undefined;
            },
            set(target, prop, value) {
                target[prop] = value;
                if (prop === 'shadowBlur') calls.shadowBlurs.push(value);
                return true;
            },
        },
    );

    const canvas = { id: 'tron-background', width: 1280, height: 720, style: {}, getContext: () => ctx2d };
    const documentStub = {
        documentElement: {},
        body: { firstChild: null, insertBefore() {}, appendChild() {} },
        getElementById: (id) => (id === 'tron-background' ? canvas : null),
        createElement: () => ({ style: {}, setAttribute() {}, appendChild() {} }),
        addEventListener() {},
        removeEventListener() {},
    };
    const localStorageStub = { getItem: () => 'true', setItem() {} };
    const sandbox = {
        console,
        localStorage: localStorageStub,
        document: documentStub,
        performance: { now: () => clock },
        getComputedStyle: () => ({ getPropertyValue: () => '' }),
        cancelAnimationFrame: () => {},
        requestAnimationFrame: (cb) => {
            calls.scheduled++;
            rafCallback = cb;
            return calls.scheduled;
        },
    };
    sandbox.window = {
        innerWidth: 1280,
        innerHeight: 720,
        navigator: { hardwareConcurrency: cores, deviceMemory: memory },
        // Only the reduce query reports a preference, exactly like the browser:
        // asking for anything else always comes back false.
        matchMedia: (query) => ({ matches: reducedMotion && /prefers-reduced-motion:\s*reduce/.test(query), media: query }),
        localStorage: localStorageStub,
        addEventListener() {},
        removeEventListener() {},
        requestAnimationFrame: sandbox.requestAnimationFrame,
        cancelAnimationFrame: sandbox.cancelAnimationFrame,
        performance: sandbox.performance,
    };
    sandbox.globalThis = sandbox;

    vm.createContext(sandbox);
    vm.runInContext(source + '\n;globalThis.TronBackgroundClass = TronBackground;', sandbox);
    const Klass = sandbox.TronBackgroundClass;
    const bg = new Klass();
    const realRender = bg.render.bind(bg);
    bg.render = () => {
        calls.renders++;
        realRender();
    };

    return {
        calls,
        bg,
        Klass,
        frame(t) {
            clock = t;
            calls.frames++;
            const cb = rafCallback;
            rafCallback = null;
            if (cb) cb(t);
            return Boolean(rafCallback);
        },
    };
}

function drive(world, seconds, stepMs = 16.7) {
    const frames = Math.round((seconds * 1000) / stepMs);
    for (let i = 1; i <= frames; i++) world.frame(i * stepMs);
    return frames;
}

function detectedLowPower(cores, memory) {
    return new (buildWorld({ cores, memory }).Klass)().isLowPowerMode;
}

const scenarios = {
    // 60 Hz input, at most 30 draws a second. The step is a realistic rAF delta
    // (16.7ms), not the exact 1000/60 float, which would sit on a rounding
    // knife-edge instead of on real compositor timestamps.
    frame() {
        const world = buildWorld();
        world.bg.start();
        const firstFrameRenders = world.calls.renders;
        const frames = drive(world, 1);
        return {
            maxFps: world.bg.maxFps,
            frameInterval: world.bg.frameInterval,
            frames,
            renders: world.calls.renders,
            scheduled: world.calls.scheduled,
            firstFrameRenders,
            lastRenderTime: world.bg.lastRenderTime,
            lastTime: world.bg.lastTime,
            trailPoints: world.bg.trails.reduce((sum, trail) => sum + trail.length, 0),
        };
    },

    // prefers-reduced-motion: reduce -> one static frame, no loop.
    reducedMotion() {
        const world = buildWorld({ reducedMotion: true });
        world.bg.start();
        // Even if something keeps calling the loop, it must stay paused.
        world.bg.animate(1000);
        world.bg.animate(2000);
        return {
            renders: world.calls.renders,
            scheduled: world.calls.scheduled,
            paused: world.bg.isPausedForReducedMotion,
        };
    },

    // Motion allowed: the loop must run.
    motionAllowed() {
        const world = buildWorld({ reducedMotion: false });
        world.bg.start();
        drive(world, 0.5);
        return {
            paused: world.bg.isPausedForReducedMotion,
            renders: world.calls.renders,
            scheduled: world.calls.scheduled,
            maxFps: world.bg.maxFps,
        };
    },

    // Shadow blur: untouched by default, capped on low power.
    shadow(cores, memory) {
        const result = {};
        for (const lowPower of [false, true]) {
            const world = buildWorld({ cores, memory });
            world.bg.setLowPowerMode(lowPower);
            world.bg.start();
            drive(world, 0.5);
            world.bg.lastWinner = 'cyan';
            world.bg.showingWinner = true;
            world.bg.target = { x: 3, y: 3 };
            world.bg.particles.push({ x: 10, y: 10, size: 4, life: 0.5, color: world.bg.colors.cyan });
            world.bg.render();
            result[lowPower ? 'lowPower' : 'default'] = {
                isLowPowerMode: world.bg.isLowPowerMode,
                cap: world.bg.lowPowerMaxShadowBlur,
                values: [...new Set(world.calls.shadowBlurs)].sort((a, b) => a - b),
                max: Math.max(...world.calls.shadowBlurs),
            };
        }
        return result;
    },

    // What a fresh instance infers from the navigator hints.
    detect(cores, memory) {
        return detectedLowPower(cores, memory);
    },
};

const [first, second] = [process.argv[4], process.argv[5]];
const outcome = scenarios[scenario](
    first === undefined ? undefined : Number(first),
    second === undefined ? undefined : Number(second),
);
process.stdout.write(JSON.stringify(outcome));
"""


@pytest.fixture(scope="module")
def tron_harness(tmp_path_factory: pytest.TempPathFactory):
    """A Node runner for the stubbed-DOM harness, or a skip when Node is absent."""
    node = shutil.which("node") or shutil.which("node.exe")
    if node is None:
        pytest.skip("node is not installed; cannot drive web/js/tron-background.js")
    assert TRON_JS.is_file(), "web/js/tron-background.js is missing"
    script = tmp_path_factory.mktemp("tron") / "tron_harness.mjs"
    script.write_text(TRON_HARNESS_JS, encoding="utf-8")
    return node, script


def _run(tron_harness, scenario: str, *args: int) -> dict[str, object]:
    """Run one harness scenario and return its JSON report."""
    node, script = tron_harness
    proc = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [node, str(script), str(TRON_JS), scenario, *[str(arg) for arg in args]],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_ROOT,
        check=False,
    )
    assert proc.returncode == 0, f"harness scenario '{scenario}' failed:\n{proc.stdout}\n{proc.stderr}"
    return json.loads(proc.stdout)


def test_frame_cap_is_thirty_fps(tron_harness) -> None:
    """60 Hz input draws about 30 times a second, not 60 (UI-16).

    The count is the immediate first frame plus the paced ones, so a second of
    60 Hz frames yields 31 draws instead of 60.
    """
    report = _run(tron_harness, "frame")
    assert report["maxFps"] == 30, f"maxFps must be 30, got {report['maxFps']}"
    assert report["frameInterval"] == pytest.approx(1000 / 30, abs=1e-6)
    assert report["frames"] == 60, "the harness must feed 60 frames to be meaningful"
    assert 29 <= report["renders"] <= 31, f"expected ~30 draws in 1s, got {report['renders']}"


def test_the_first_frame_renders_immediately(tron_harness) -> None:
    """The first draw is not deferred by the frame interval.

    A background that appears a third of a second after the page does is what
    makes the visual baselines flaky, so `start()` paints at once.
    """
    report = _run(tron_harness, "frame")
    assert report["firstFrameRenders"] == 1, "start() must render one frame before the loop starts"


def test_skipped_frames_still_keep_the_loop_alive(tron_harness) -> None:
    """Every frame schedules the next one, even the ones that skip the draw.

    Stopping the loop on a skipped frame would freeze the animation until the
    next start(); the simulation itself also has to keep advancing.
    """
    report = _run(tron_harness, "frame")
    assert report["scheduled"] >= report["frames"], "the animation loop stopped scheduling frames"
    assert report["lastTime"] > 0, "frames were skipped without advancing the simulation"
    assert report["trailPoints"] > 2, "the light cycles never moved"


def test_reduced_motion_paints_one_static_frame_and_stops(tron_harness) -> None:
    """`prefers-reduced-motion: reduce` renders once and never starts the loop."""
    report = _run(tron_harness, "reducedMotion")
    assert report["paused"] is True, "the animation must record that it paused for reduced motion"
    assert report["renders"] == 1, f"reduced motion must paint exactly one frame, got {report['renders']}"
    assert report["scheduled"] == 0, "reduced motion must not schedule animation frames"


def test_motion_allowed_runs_the_loop(tron_harness) -> None:
    """Without the motion preference the animation still runs and stays capped."""
    report = _run(tron_harness, "motionAllowed")
    assert report["paused"] is False, "the animation paused although motion was allowed"
    assert report["maxFps"] == 30
    assert report["renders"] > 5, "the animation loop is not rendering"
    assert report["renders"] <= 16, f"0.5s at {report['maxFps']} fps is ~15 draws, got {report['renders']}"


def test_shadow_blur_is_unchanged_by_default(tron_harness) -> None:
    """A capable device keeps the exact glows the approved baselines were shot with."""
    report = _run(tron_harness, "shadow", 16, 16)
    default = report["default"]
    assert default["isLowPowerMode"] is False
    assert default["cap"] == 4, "the low-power cap must be 4px"
    assert default["max"] == 20, f"the winner glow must stay 20px, got {default['values']}"
    for blur in (20, 15, 10, 8):
        assert blur in default["values"], f"the {blur}px glow disappeared: {default['values']}"


def test_low_power_mode_caps_shadow_blur(tron_harness) -> None:
    """On a low-power device no glow exceeds the 4px budget."""
    report = _run(tron_harness, "shadow", 2, 2)
    low_power = report["lowPower"]
    assert low_power["isLowPowerMode"] is True
    assert low_power["max"] <= 4, f"shadow blur is not capped: {low_power['values']}"
    assert max(low_power["values"]) == 4, f"the capped draws should still glow a little: {low_power['values']}"


@pytest.mark.parametrize(
    "cores,memory,expected",
    [
        (2, 8, True),  # a small ARM TV box
        (16, 8, False),  # a desktop
        (8, 2, True),  # a cheap tablet with little RAM
        (8, 8, False),
    ],
)
def test_low_power_detection(tron_harness, cores: int, memory: int, expected: bool) -> None:
    """Detection reads the CPU/memory hints; unknown hardware is treated as capable."""
    assert _run(tron_harness, "detect", cores, memory) is expected


def test_source_documents_the_frame_cap_and_the_motion_check() -> None:
    """The source names the constants the UI-16 fix is specified in.

    Cheap guard against a rewrite that keeps the behaviour but drops the
    documented knobs a kiosk or a settings toggle needs to reach for.
    """
    source = TRON_JS.read_text(encoding="utf-8")
    assert re.search(r"this\.maxFps\s*=\s*30", source), "maxFps = 30 is gone"
    assert re.search(r"this\.frameInterval\s*=\s*1000\s*/\s*(this\.maxFps|30)", source)
    assert re.search(r"this\.lastRenderTime\s*===\s*0\s*\|\|", source), "the first frame must bypass the cap"
    assert "prefers-reduced-motion: reduce" in source, "the OS motion preference is no longer read"
    assert "isPausedForReducedMotion" in source
    assert re.search(r"this\.lowPowerMaxShadowBlur\s*=\s*4", source), "the 4px low-power blur budget is gone"
    assert "setLowPowerMode" in source, "there must be a way to force the low-power budget on"
    raw_writes = re.findall(r"(?<!this\.)ctx\.shadowBlur\s*=", source)
    assert not raw_writes, "every shadow blur must go through setShadowBlur(), which applies the low-power cap"
    assert len(re.findall(r"this\.ctx\.shadowBlur\s*=", source)) == 1, "the cap must live in one place: setShadowBlur()"
