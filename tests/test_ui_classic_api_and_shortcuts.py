"""Classic web UI scripts, run for real in Node: the API client, keyboard shortcuts, Power Cycle.

Each test loads the shipped files (``web/js/api.js``,
``web/js/components/keyboard-shortcuts.js``, ``web/js/components/settings-panel.js``)
into a ``vm`` context with small stand-ins for the browser globals they use,
then drives them and prints what they did as JSON.

- ``MatrixAPI.clearOverride`` passed its payload where ``delete()`` reads
  options, so the request had no body and the hub answered 400.
- ``renamePreset`` was defined twice.
- ``?`` (Shift+/) never opened the help, ``s`` called an object that does not
  exist, and ``4`` clicked a tab name the page does not have.
- Power Cycle showed "Power cycling matrix..." although nothing was sent.

This shows what the scripts do with these inputs, not how a browser renders
them. Needs Node on PATH (skipped otherwise).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
NODE = shutil.which("node")

pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js is not installed")

HARNESS = r"""
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const root = process.argv[2];
const out = (value) => console.log(JSON.stringify(value));
const quiet = { error() {}, warn() {}, info() {}, log() {} };

function load(context, rel) {
    vm.runInContext(fs.readFileSync(path.join(root, rel), 'utf8'), context, { filename: rel });
}

/** A context with the API client loaded; every fetch is recorded and answered 200. */
function apiContext(extra = {}) {
    const requests = [];
    const context = vm.createContext({
        console: quiet,
        window: { location: { origin: 'http://hub.test' } },
        localStorage: { getItem() { return null; }, setItem() {}, removeItem() {} },
        Logger: { api() {}, apiResponse() {} },
        Constants: {},
        AbortController, setTimeout, clearTimeout,
        fetch: async (url, init) => {
            requests.push({
                method: init.method,
                url,
                contentType: init.headers ? init.headers['Content-Type'] : null,
                body: init.body === undefined ? null : JSON.parse(init.body),
            });
            return { ok: true, status: 200, json: async () => ({ success: true }) };
        },
        ...extra,
    });
    load(context, 'web/js/api.js');
    context.api = context.window.api;
    return { context, requests };
}
"""


def run_node(tmp_path: Path, body: str) -> dict:
    script = tmp_path / "check.cjs"
    script.write_text(HARNESS + body, encoding="utf-8")
    proc = subprocess.run(
        [NODE, str(script), str(ROOT)], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=60
    )
    assert proc.returncode == 0, f"node failed:\n{proc.stdout}\n{proc.stderr}"
    return json.loads(proc.stdout.strip().splitlines()[-1])


# ----------------------------------------------------------------------------- API client


def test_clear_override_sends_the_override_in_the_delete_body(tmp_path):
    result = run_node(
        tmp_path,
        """
        (async () => {
            const { context, requests } = apiContext();
            await context.api.clearOverride('scene_1', { profile_id: 'game_day', output_num: 3, setting_key: 'audio_mute' });
            await context.api.deleteProfile('game_day');
            out(requests);
        })();
        """,
    )

    assert result[0] == {
        "method": "DELETE",
        "url": "http://hub.test/api/v2/scenes/scene_1/override",
        "contentType": "application/json",
        "body": {"profile_id": "game_day", "output_num": 3, "setting_key": "audio_mute"},
    }
    # Negative control: a DELETE without a payload still has no body and no content type.
    assert result[1] == {
        "method": "DELETE",
        "url": "http://hub.test/api/profile/game_day",
        "contentType": None,
        "body": None,
    }


def test_rename_preset_is_defined_once_and_posts_the_name(tmp_path):
    source = (ROOT / "web" / "js" / "api.js").read_text(encoding="utf-8")
    assert len(re.findall(r"^\s*async renamePreset\(", source, flags=re.MULTILINE)) == 1

    result = run_node(
        tmp_path,
        """
        (async () => {
            const { context, requests } = apiContext();
            await context.api.renamePreset(3, 'Movie');
            out(requests);
        })();
        """,
    )

    assert result == [{
        "method": "POST",
        "url": "http://hub.test/api/device-settings/preset/3/name",
        "contentType": "application/json",
        "body": {"name": "Movie"},
    }]


def test_the_lint_baseline_no_longer_excuses_a_duplicate_member_in_the_api_client():
    suppressions = json.loads((ROOT / "eslint-suppressions.json").read_text(encoding="utf-8"))

    assert "web/js/api.js" not in suppressions


# ----------------------------------------------------------------------------- keyboard shortcuts


def page_tabs() -> list[str]:
    """The view tabs the main page really has (``<button class="tab-btn" data-tab="...">``)."""
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    return re.findall(r'class="tab-btn[^"]*"\s+data-tab="([^"]+)"', html)


SHORTCUTS = """
(async () => {
    const tabs = __TABS__;
    const done = { clicks: [], missing: [], help: 0, settings: 0, prevented: 0 };
    let keydown = null;
    class Element {}
    const context = vm.createContext({
        console: quiet,
        Element,
        window: { generalDrawer: { toggle() { done.settings += 1; } } },
        document: {
            readyState: 'complete',
            activeElement: null,
            addEventListener(type, fn) { if (type === 'keydown') keydown = fn; },
            querySelector(selector) {
                const tab = /^\\[data-tab="([^"]+)"\\]$/.exec(selector);
                if (!tab || !tabs.includes(tab[1])) { done.missing.push(selector); return null; }
                return { click() { done.clicks.push(tab[1]); } };
            },
        },
    });
    load(context, 'web/js/components/keyboard-shortcuts.js');
    context.window.KeyboardShortcuts.toggleHelp = () => { done.help += 1; };
    const press = (key, extra = {}) => keydown({
        key, shiftKey: false, ctrlKey: false, altKey: false, metaKey: false, target: null,
        preventDefault() { done.prevented += 1; }, ...extra,
    });
    const input = Object.assign(new Element(), { tagName: 'INPUT', getAttribute: () => 'text', blur() {} });
    __KEYS__
    out(done);
})();
"""


def press_keys(tmp_path: Path, keys: str) -> dict:
    return run_node(tmp_path, SHORTCUTS.replace("__TABS__", json.dumps(page_tabs())).replace("__KEYS__", keys))


def test_question_mark_opens_the_help_with_and_without_shift(tmp_path):
    # Shift+/ on most layouts, and a layout that types "?" without Shift
    done = press_keys(tmp_path, "press('?', { shiftKey: true }); press('?');")

    assert (done["help"], done["prevented"]) == (2, 2)


def test_s_opens_the_settings_drawer(tmp_path):
    done = press_keys(tmp_path, "press('s');")

    assert (done["settings"], done["prevented"]) == (1, 1)


def test_digits_switch_to_tabs_the_page_has(tmp_path):
    done = press_keys(tmp_path, "press('1'); press('2'); press('3'); press('4');")

    assert done["clicks"] == ["matrix", "inputs", "outputs", "profiles"]
    assert done["missing"] == []
    assert set(done["clicks"]) <= set(page_tabs())


def test_shift_does_not_turn_other_keys_into_shortcuts(tmp_path):
    """Negative controls: Shift+letter, Shift+digit, Ctrl+?, and keys typed into a field do nothing."""
    done = press_keys(
        tmp_path,
        """
        press('S', { shiftKey: true });
        press('4', { shiftKey: true });
        press('?', { shiftKey: true, ctrlKey: true });
        press('?', { shiftKey: true, target: input });
        press('s', { target: input });
        """,
    )

    assert done == {"clicks": [], "missing": [], "help": 0, "settings": 0, "prevented": 0}


# ----------------------------------------------------------------------------- Power Cycle


def test_power_cycle_reports_that_nothing_was_sent(tmp_path):
    result = run_node(
        tmp_path,
        """
        (async () => {
            const toasts = [];
            const { context, requests } = apiContext({
                ConfirmDialog: { confirm: async () => true },
                toast: Object.fromEntries(['info', 'success', 'warning', 'error'].map(
                    (kind) => [kind, (text) => toasts.push([kind, text])])),
            });
            load(context, 'web/js/components/settings-panel.js');
            // The method alone: the constructor wires the settings modal, which is not under test.
            await vm.runInContext('SettingsPanel.prototype.powerCycle.call({})', context);
            out({ toasts, requests });
        })();
        """,
    )

    assert result["requests"] == []
    assert [kind for kind, _ in result["toasts"]] == ["error"]
    assert "not available" in result["toasts"][0][1]
