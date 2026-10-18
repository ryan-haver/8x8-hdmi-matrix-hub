"""WP-E2 Track 3: exercise the classic browser components using the pinned npm Playwright.

No server or matrix is needed. Install the UI dev dependencies with ``npm ci``
and the matching Chromium with ``npx playwright install chromium``.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "web" / "js" / "components"


def require_ui_dependencies() -> None:
    """The Python-only CI job omits npm tooling; the UI job runs these checks."""
    if not shutil.which("node") or not (ROOT / "node_modules" / "@playwright" / "test").is_dir():
        pytest.skip("UI checks need npm ci; they run in the UI CI job")


def browser_check(body: str, *, scripts: tuple[str, ...] = ("editor-shell.js", "cec-remote.js")) -> None:
    """Run real DOM, focus, keyboard and pointer assertions; surface JS failures in pytest."""
    require_ui_dependencies()
    paths = [str(COMPONENTS / name) for name in scripts]
    source = """
        import { chromium, expect } from '@playwright/test';
        const browser = await chromium.launch();
        const page = await browser.newPage();
        page.setDefaultTimeout(5000);
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        try {
            await page.setContent('<button id="launcher">Launch</button><div id="mount"></div>');
            // Match the app's authored display rule, which overrides the UA hidden rule.
            await page.addStyleTag({ content: '.btn { display: inline-flex; }' });
            await page.evaluate(() => {
                window.prompt = () => { throw new Error('Native prompt must never be used'); };
                window.calls = [];
                window.api = { sendCecCommand: async (...args) => {
                    calls.push(args); return { success: true };
                } };
            });
    """
    source += f"for (const path of {json.dumps(paths)}) await page.addScriptTag({{ path }});\n"
    source += body
    source += "\nexpect(errors).toEqual([]);\n} finally { await browser.close(); }\n"
    result = subprocess.run(
        [shutil.which("node") or "node", "--input-type=module"],
        input=source,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_shell_validation_actions_and_nested_focus() -> None:
    browser_check("""
        await page.locator('#launcher').focus();
        await page.evaluate(() => {
            window.shell = new EditorShell({ title: 'Profile', icon: '★', drawer: true,
                onSave: () => { calls.push('save'); shell.showValidationErrors(['Name required']); return false; },
                onDelete: () => { calls.push('delete'); }
            }).open();
            shell.showValidationErrors(['<img src=x onerror=alert(1)>', { message: 'Choose a target' }]);
        });
        await expect(page.getByRole('dialog')).toHaveAccessibleName('Profile');
        await expect(page.getByRole('alert')).toContainText('<img src=x onerror=alert(1)>');
        expect(await page.locator('.editor-shell-validation img').count()).toBe(0);
        await expect(page.getByRole('alert').locator('li')).toHaveCount(2);
        expect(await page.locator('.editor-shell-body').evaluate(el => getComputedStyle(el).overflow)).toBe('auto');
        expect(await page.locator('.editor-shell-footer').evaluate(el => getComputedStyle(el).position)).toBe('sticky');
        await page.evaluate(() => shell.clearValidationErrors());
        await expect(page.getByRole('alert')).toBeHidden();
        await page.getByRole('button', { name: 'Save', exact: true }).click();
        await expect(page.getByRole('alert')).toHaveText('Name required');
        await expect(page.getByRole('dialog')).toBeVisible();
        await page.evaluate(() => EditorShell.openPicker({ items: ['Play'] }));
        await page.keyboard.press('Escape');
        await expect(page.getByRole('dialog')).toHaveCount(1);
        expect(await page.evaluate(() => document.body.style.overflow)).toBe('hidden');
        await page.getByRole('button', { name: 'Delete', exact: true }).click();
        await expect(page.getByRole('dialog')).toHaveCount(0);
        await expect(page.locator('#launcher')).toBeFocused();
        expect(await page.evaluate(() => document.body.style.overflow)).toBe('');
        expect(await page.evaluate(() => calls)).toEqual(['save', 'delete']);
        await page.evaluate(() => new EditorShell({ onCancel: () => calls.push('cancel') }).open());
        await page.getByRole('button', { name: 'Cancel', exact: true }).click();
        expect(await page.evaluate(() => calls.at(-1))).toBe('cancel');
    """)


def test_searchable_picker_keyboard_filter_empty_and_click() -> None:
    browser_check("""
        await page.evaluate(() => {
            window.items = [{ id: 'play', name: 'Play', keywords: 'media' },
                { id: 'pause', label: 'Pause', description: 'media' }, { id: 'up', name: 'Up' }];
            EditorShell.openPicker({ title: 'Step', items, placeholder: 'Find command',
                onSelect: item => calls.push({ id: item.id, same: item === items[1] }) });
        });
        const search = page.getByRole('combobox');
        await expect(search).toBeFocused();
        await search.fill('MEDIA');
        await expect(page.getByRole('option')).toHaveCount(2);
        await search.press('ArrowUp');
        await expect(page.getByRole('option', { name: 'Pause' })).toHaveAttribute('aria-selected', 'true');
        await search.press('ArrowDown');
        await expect(page.getByRole('option', { name: 'Play', exact: true })).toHaveAttribute('aria-selected', 'true');
        await search.press('ArrowDown');
        await search.press('Enter');
        expect(await page.evaluate(() => calls)).toEqual([{ id: 'pause', same: true }]);
        await expect(page.getByRole('dialog')).toHaveCount(0);
        await page.evaluate(() => EditorShell.openPicker({ items: ['Play', '<svg onload=alert(1)>'], onSelect: item => calls.push(item) }));
        await search.fill('missing');
        await expect(page.getByText('No matches')).toBeVisible();
        await search.press('ArrowDown');
        await search.press('Enter');
        expect(await page.evaluate(() => calls.length)).toBe(1);
        await search.fill('svg');
        expect(await page.locator('.editor-picker-list svg').count()).toBe(0);
        await page.getByRole('option').click();
        expect(await page.evaluate(() => calls.at(-1))).toBe('<svg onload=alert(1)>');
        await page.evaluate(() => EditorShell.openPicker({ items: [] }));
        await page.keyboard.press('Escape');
        await expect(page.getByRole('dialog')).toHaveCount(0);
    """)


def test_scene_step_bridge_replaces_all_prompt_paths_without_changing_markup() -> None:
    browser_check("""
        await page.evaluate(() => {
            window.state = { profiles: [{ id: 'movie', name: 'Movie Night' }],
                systemActions: [{ key: 'wake', name: 'Wake up' }], cecMacros: [{ id: 'tv', name: 'TV On' }] };
            window.Helpers = { escapeHtml: value => String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;') };
        });
        await page.addScriptTag({ path: 'web/js/components/scene-editor.js' });
        const before = await page.locator('#scene-editor-modal').innerHTML();
        await page.evaluate(() => {
            EditorShell.installSceneEditor(sceneEditor, state);
            sceneEditor.validateScene = () => calls.push('validate');
        });
        expect(await page.locator('#scene-editor-modal').innerHTML()).toBe(before);
        await page.evaluate(() => sceneEditor.open());
        await page.locator('#scene-editor-name').fill('Unsaved scene');
        await page.locator('#scene-desc').fill('Keep my description');
        for (const [type, label] of [['profile', 'Movie Night'], ['system_action', 'Wake up'], ['macro', 'TV On']]) {
            await page.evaluate(type => sceneEditor.addStep(type), type);
            await page.getByRole('combobox').fill(label);
            await page.getByRole('combobox').press('Enter');
        }
        await page.evaluate(() => sceneEditor.addStep('wait'));
        await page.getByLabel('Wait duration in seconds').fill('31');
        await page.locator('.editor-shell').getByRole('button', { name: 'Save', exact: true }).click();
        await expect(page.getByRole('alert')).toContainText('0.5 and 30');
        await page.getByLabel('Wait duration in seconds').fill('0.75');
        await page.locator('.editor-shell').getByRole('button', { name: 'Save', exact: true }).click();
        await expect(page.locator('.editor-shell')).toHaveCount(0);
        expect(await page.evaluate(() => sceneEditor.sceneData.steps)).toEqual([
            { type: 'profile', id: 'movie' }, { type: 'system_action', id: 'wake' },
            { type: 'macro', id: 'tv' }, { type: 'wait', id: '', params: { seconds: 0.75 } }
        ]);
        await expect(page.locator('#scene-editor-name')).toHaveValue('Unsaved scene');
        await expect(page.locator('#scene-desc')).toHaveValue('Keep my description');
        expect(await page.evaluate(() => calls)).toEqual(['validate']);
        await page.evaluate(() => sceneEditor.addStep('macro'));
        await page.keyboard.press('Escape');
        expect(await page.evaluate(() => sceneEditor.sceneData.steps.length)).toBe(4);
    """)


def test_standalone_macro_editor_validation_picker_create_update_and_delete() -> None:
    browser_check("""
        await page.evaluate(() => {
            window.saved = null;
            api.createMacro = async macro => { saved = structuredClone(macro); calls.push('create'); return { success: true }; };
            api.getMacro = async id => { calls.push(['get', id]); return { success: true, data: saved }; };
            api.updateMacro = async (id, macro) => { calls.push(['update', id, macro.name]); return { success: true }; };
            api.deleteMacro = async id => { calls.push(['delete', id]); return { success: true }; };
            cecMacroEditor.open();
        });
        await expect(page.getByRole('dialog')).toHaveAccessibleName('New CEC Macro');
        await page.getByRole('button', { name: 'Save', exact: true }).click();
        await expect(page.getByRole('alert')).toContainText('macro name');
        await expect(page.getByRole('alert')).toContainText('at least one step');
        await page.getByLabel('Name', { exact: true }).fill('Movie');
        await page.getByRole('button', { name: 'Add Step', exact: true }).click();
        await page.getByRole('combobox').fill('POWER_ON');
        await page.getByRole('combobox').press('Enter');
        await page.getByRole('button', { name: 'Save', exact: true }).click();
        await expect(page.getByRole('alert')).toContainText('select at least one target');
        await page.getByLabel('Step 1 targets').selectOption(['input_2', 'output_1']);
        await page.getByLabel('Step 1 delay in milliseconds').fill('750');
        await page.getByRole('button', { name: 'Save', exact: true }).click();
        await expect(page.getByRole('dialog')).toHaveCount(0);
        expect(await page.evaluate(() => saved.steps)).toEqual([{ command: 'POWER_ON', targets: ['input_2', 'output_1'], delay_ms: 750 }]);
        await page.evaluate(() => cecMacroEditor.open('movie'));
        await expect(page.getByLabel('Name', { exact: true })).toHaveValue('Movie');
        await page.getByLabel('Name', { exact: true }).fill('Movie Updated');
        await page.getByRole('button', { name: 'Save', exact: true }).click();
        await expect(page.getByRole('dialog')).toHaveCount(0);
        await page.evaluate(() => cecMacroEditor.open('movie'));
        await page.getByRole('button', { name: 'Delete', exact: true }).click();
        await expect(page.getByRole('dialog')).toHaveCount(0);
        expect(await page.evaluate(() => calls)).toEqual(['create', ['get', 'movie'], ['update', 'movie', 'Movie Updated'], ['get', 'movie'], ['delete', 'movie']]);
    """)


def test_macro_bridge_settings_legacy_and_load_failure() -> None:
    browser_check("""
        await page.evaluate(async () => {
            window.cecSettings = { showMacroModal: id => calls.push(['settings', id]) };
            await cecMacroEditor.open('existing');
            delete window.cecSettings;
            const bridge = new window.CecMacroEditor({ legacy: { open: id => calls.push(['legacy', id]) } });
            await bridge.open('old');
            api.getMacro = async () => { throw new Error('Macro unavailable'); };
            await cecMacroEditor.open('missing');
        });
        expect(await page.evaluate(() => calls)).toEqual([['settings', 'existing'], ['legacy', 'old']]);
        await expect(page.getByRole('alert')).toHaveText('Macro unavailable');
        await expect(page.getByRole('button', { name: 'Save', exact: true })).toBeDisabled();
        await page.keyboard.press('Escape');
        await expect(page.getByRole('dialog')).toHaveCount(0);
    """)


def test_legacy_macro_global_and_direct_edit_preserve_existing_shell() -> None:
    browser_check("""
        await page.evaluate(() => {
            window.Helpers = { escapeHtml: value => String(value ?? '') };
            window.toast = { error: message => { throw new Error(message); } };
            window.state = {};
            api.getMacros = async () => ({ success: true, data: { macros: [] } });
            api.getMacro = async () => ({ success: true, data: { name: 'Existing', id: 'one', steps: [] } });
        });
        await page.addScriptTag({ path: 'web/js/components/cec-macro-editor.js' });
        const original = await page.locator('#cec-macro-modal').innerHTML();
        await page.addScriptTag({ path: 'web/js/components/editor-shell.js' });
        expect(await page.locator('#cec-macro-modal').innerHTML()).toBe(original);
        await page.evaluate(() => window.cecMacroEditor.open('one'));
        await expect(page.locator('#macro-name')).toHaveValue('Existing');
        await expect(page.locator('#cec-macro-modal')).toHaveClass(/visible/);
        expect(await page.locator('.editor-shell').count()).toBe(0);
        await page.evaluate(() => window.cecMacroEditor.close());
        await page.evaluate(() => cecMacroEditor.open());
        await expect(page.locator('.macro-list-view')).toBeVisible();
    """, scripts=())


def test_remote_buttons_targets_capabilities_rebind_and_api_errors() -> None:
    browser_check("""
        await page.evaluate(() => {
            window.remote = CecRemote.render(document.getElementById('mount'), {
                target: { type: 'input', port: 2 },
                quickTargets: [{ type: 'input', port: 3, name: '<img src=x>' }, { type: 'output', port: 8, name: 'TV' }]
            });
        });
        expect(await page.locator('.cec-quick-targets img').count()).toBe(0);
        for (const cmd of ['up', 'select', 'play', 'volume_up', 'power_on']) {
            await page.locator(`[data-cmd="${cmd}"]`).click();
        }
        expect(await page.evaluate(() => calls)).toEqual(['up', 'select', 'play', 'volume_up', 'power_on'].map(cmd => ['input', 2, cmd]));
        await page.getByRole('button', { name: '<img src=x>', exact: true }).click();
        await page.locator('[data-cmd="down"]').click();
        expect(await page.evaluate(() => calls.at(-1))).toEqual(['input', 3, 'down']);
        await page.getByLabel('CEC target').selectOption('output:8');
        await expect(page.locator('[data-cmd="up"]')).toBeHidden();
        await expect(page.locator('[data-cmd="play"]')).toBeHidden();
        await page.locator('[data-cmd="mute"]').click();
        expect(await page.evaluate(() => calls.at(-1))).toEqual(['output', 8, 'mute']);
        await page.evaluate(() => remote.dispatch('up'));
        await expect(page.getByRole('status')).toContainText('not supported');
        expect(await page.evaluate(() => calls.length)).toBe(7);
        await page.evaluate(() => { api.sendCecCommand = async () => { throw new Error('Network unavailable'); }; });
        await page.locator('[data-cmd="volume_down"]').click();
        await expect(page.getByRole('status')).toHaveText('Network unavailable');
        await page.evaluate(() => {
            const root = document.querySelector('.cec-remote');
            const options = { onCommand: (cmd, action) => calls.push([cmd, action]) };
            CecRemote.attachEvents(root, options);
            window.remote = CecRemote.attachEvents(root, options);
        });
        await page.locator('[data-cmd="power_off"]').click();
        expect(await page.evaluate(() => calls.at(-1))).toEqual(['power_off', 'power']);
        expect(await page.evaluate(() => calls.length)).toBe(8);
        await page.evaluate(() => remote.destroy());
        await page.locator('[data-cmd="power_off"]').click();
        expect(await page.evaluate(() => calls.length)).toBe(8);
    """)


@pytest.mark.parametrize("pointer_type", ["mouse", "touch", "pen"])
def test_remote_trackpad_thresholds_feedback_cancel_and_modes(pointer_type: str) -> None:
    browser_check("""
        await page.evaluate(() => { window.remote = CecRemote.render(document.getElementById('mount')); });
        await page.getByRole('button', { name: 'Trackpad', exact: true }).click();
        await expect(page.locator('.trackpad-surface')).toBeVisible();
        await expect(page.locator('[data-cec-buttons]')).toBeHidden();
        await page.evaluate(pointerType => {
            const surface = document.querySelector('.trackpad-surface');
            surface.setPointerCapture = () => {};
            window.gesture = (dx, dy, cancel = false) => {
                const data = { pointerId: 1, pointerType, isPrimary: true, button: 0, bubbles: true };
                surface.dispatchEvent(new PointerEvent('pointerdown', { ...data, clientX: 100, clientY: 100 }));
                surface.dispatchEvent(new PointerEvent(cancel ? 'pointercancel' : 'pointerup', { ...data, clientX: 100 + dx, clientY: 100 + dy }));
            };
        }, """ + json.dumps(pointer_type) + """);
        for (const [dx, dy, command] of [[0, 0, 'select'], [30, 0, 'right'], [-31, 0, 'left'], [0, -30, 'up'], [0, 40, 'down'], [23, 23, 'down']]) {
            await page.evaluate(([dx, dy]) => gesture(dx, dy), [dx, dy]);
            await expect.poll(() => page.evaluate(() => calls.at(-1))).toEqual(['input', 1, command]);
            await expect(page.locator('.trackpad-feedback')).toHaveClass(new RegExp(`active ${command === 'select' ? 'tap' : command}`));
        }
        await page.evaluate(() => { gesture(29, 0); gesture(0, 40, true); });
        expect(await page.evaluate(() => calls.length)).toBe(6);
        await expect(page.locator('.trackpad-surface')).not.toHaveClass(/touching/);
        await page.locator('.trackpad-surface').focus();
        await page.keyboard.press('ArrowLeft');
        await expect.poll(() => page.evaluate(() => calls.at(-1))).toEqual(['input', 1, 'left']);
        await page.getByRole('button', { name: 'output 1', exact: true }).click();
        await expect(page.locator('.trackpad-surface')).toBeHidden();
        await expect(page.locator('[data-cmd="power_on"]')).toBeVisible();
        await page.getByRole('button', { name: 'input 1', exact: true }).click();
        await page.getByRole('button', { name: 'Buttons', exact: true }).click();
        await expect(page.locator('[data-cmd="up"]')).toBeVisible();
        await expect(page.locator('.trackpad-surface')).toBeHidden();
    """)


def test_new_components_never_call_native_prompt_and_consumers_load_them() -> None:
    for name in ("editor-shell.js", "cec-remote.js"):
        assert "prompt(" not in (COMPONENTS / name).read_text(encoding="utf-8")
    assert "EditorShell.installSceneEditor" in (ROOT / "web/js/app.js").read_text(encoding="utf-8")
    assert "CecRemote.attachEvents" in (COMPONENTS / "cec-tray.js").read_text(encoding="utf-8")
    assert "CecRemote.attachEvents" in (ROOT / "web/kiosk.html").read_text(encoding="utf-8")


def test_javascript_lint() -> None:
    require_ui_dependencies()
    npm = shutil.which("npm")
    assert npm, "npm is required; install UI dependencies with npm ci"
    result = subprocess.run(
        [npm, "run", "lint:js"], cwd=ROOT, capture_output=True, text=True, timeout=120, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
