"""
Tests for Phase 5 (WP-E2) Track 2:
Unified Settings Controller & Stack-Aware Overlay Manager.

Covers:
- OverlayManager stack management (onOpen, onClose, closeTop, Escape handling,
  desktop side-nav coexistence, right-side drawer mutual exclusion, mobile mutual
  exclusion, modal stacking above drawers per UI-07, DOM ordering in register(),
  and focus restoration via triggerElements).
- UnifiedSettingsController 9-section routing (general, hardware, interface,
  theme, integrations, shortcuts, profiles, scenes, system) and #settings/<section>
  hash synchronization per DI-7, UI-05, UI-14.
- SettingsDrawer initHashRouting() delegation for the 6 non-settings-drawer
  sections while keeping DOM structure 100% intact for visual regression baselines.
- JavaScript linting via `npm run lint:js`.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
OVERLAY_MANAGER_JS = REPO_ROOT / "web" / "js" / "utils" / "overlay-manager.js"
UNIFIED_SETTINGS_JS = REPO_ROOT / "web" / "js" / "components" / "unified-settings-drawer.js"
SETTINGS_DRAWER_JS = REPO_ROOT / "web" / "js" / "components" / "settings-drawer.js"

ALL_NINE_SECTIONS = [
    "general",
    "hardware",
    "interface",
    "theme",
    "integrations",
    "shortcuts",
    "profiles",
    "scenes",
    "system",
]

INDIVIDUAL_DRAWER_SECTIONS = [
    "general",
    "hardware",
    "interface",
    "theme",
    "integrations",
    "shortcuts",
]

SETTINGS_DRAWER_SECTIONS = [
    "profiles",
    "scenes",
    "system",
]


def _run_node_script(script: str) -> dict[str, Any]:
    """Execute a JavaScript snippet in Node.js and parse its JSON stdout."""
    node_bin = shutil.which("node") or "node"
    proc = subprocess.run(
        [node_bin, "-e", script],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, (
        f"Node script failed (exit {proc.returncode}):\n"
        f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
    )
    return json.loads(proc.stdout.strip())


class TestStaticStructureAndVisualBaselineInvariants:
    """Verify file existence and DOM preservation in settings-drawer.js."""

    def test_required_files_exist(self) -> None:
        assert OVERLAY_MANAGER_JS.is_file(), "overlay-manager.js must exist"
        assert UNIFIED_SETTINGS_JS.is_file(), "unified-settings-drawer.js must exist"
        assert SETTINGS_DRAWER_JS.is_file(), "settings-drawer.js must exist"

    def test_settings_drawer_preserves_dom_structure_and_classes(self) -> None:
        content = SETTINGS_DRAWER_JS.read_text(encoding="utf-8")
        assert "this.backdrop.className = 'drawer-backdrop';" in content
        assert "this.container.className = 'settings-drawer';" in content
        assert "this.container.id = 'settings-drawer';" in content
        assert 'class="drawer-tab-btn active" data-tab="profiles"' in content
        assert 'class="drawer-tab-btn" data-tab="scenes"' in content
        assert 'class="drawer-tab-btn" data-tab="system"' in content
        assert 'class="drawer-content" id="settings-drawer-content"' in content


class TestOverlayManagerStackAndFocus:
    """Verify OverlayManager stack behavior, coexistence, modal stacking, and focus restoration."""

    def test_overlay_manager_stack_and_modal_layering(self) -> None:
        script = f"""
const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync({json.dumps(str(OVERLAY_MANAGER_JS))}, 'utf8');

const keydownListeners = [];
const sandbox = {{
    window: {{ innerWidth: 1280 }},
    document: {{
        activeElement: null,
        body: {{
            querySelector: () => null,
            querySelectorAll: () => [],
            insertBefore: () => {{}},
            contains: (el) => Boolean(el && el.isConnected !== false),
        }},
        contains: (el) => Boolean(el && el.isConnected !== false),
        addEventListener: (type, fn) => {{
            if (type === 'keydown') keydownListeners.push(fn);
        }},
    }},
    Node: {{ DOCUMENT_POSITION_FOLLOWING: 4 }},
}};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

const om = sandbox.window.overlayManager;
const state = {{}};
const closedCalls = [];

function registerMock(name, extra = {{}}) {{
    state[name] = false;
    om.register(name, {{
        open: () => {{
            state[name] = true;
            om.onOpen(name);
        }},
        close: () => {{
            state[name] = false;
            closedCalls.push(name);
        }},
        isOpen: () => Boolean(state[name]),
        ...extra,
    }});
}}

[
    'side-nav-drawer',
    'general-drawer',
    'hardware-drawer',
    'settings-drawer',
    'icon-picker',
    'confirm-dialog',
    'scene-editor',
    'profile-editor',
    'cec-macro-editor',
].forEach((n) => registerMock(n));

// 1. Desktop side-nav-drawer coexistence with right-side drawer
om.overlays.get('side-nav-drawer').open();
om.overlays.get('general-drawer').open();
const afterSideAndGeneral = {{
    stack: om.getStack(),
    sideOpen: state['side-nav-drawer'],
    generalOpen: state['general-drawer'],
    top: om.getTopOverlay(),
}};

// 2. Right-side drawer mutual exclusion on desktop (general-drawer closes when hardware-drawer opens, side-nav stays open)
om.overlays.get('hardware-drawer').open();
const afterHardwareOpen = {{
    stack: om.getStack(),
    sideOpen: state['side-nav-drawer'],
    generalOpen: state['general-drawer'],
    hardwareOpen: state['hardware-drawer'],
    top: om.getTopOverlay(),
}};

// 3. Modal stacking above drawer (scene-editor -> icon-picker -> confirm-dialog)
om.overlays.get('scene-editor').open();
om.overlays.get('icon-picker').open();
om.overlays.get('confirm-dialog').open();
const afterModalsStacked = {{
    stack: om.getStack(),
    hardwareOpen: state['hardware-drawer'],
    sceneEditorOpen: state['scene-editor'],
    iconPickerOpen: state['icon-picker'],
    confirmDialogOpen: state['confirm-dialog'],
    top: om.getTopOverlay(),
}};

// 4. closeTop() closes ONLY confirm-dialog
const closedFirst = om.closeTop();
const afterCloseTop1 = {{
    closedFirst,
    stack: om.getStack(),
    confirmDialogOpen: state['confirm-dialog'],
    iconPickerOpen: state['icon-picker'],
    hardwareOpen: state['hardware-drawer'],
    top: om.getTopOverlay(),
}};

// 5. Escape keydown closes ONLY icon-picker (now top of stack)
let prevented = false;
keydownListeners[0]({{
    key: 'Escape',
    defaultPrevented: false,
    preventDefault: () => {{ prevented = true; }},
    stopImmediatePropagation: () => {{}},
}});
const afterEscape = {{
    prevented,
    stack: om.getStack(),
    iconPickerOpen: state['icon-picker'],
    sceneEditorOpen: state['scene-editor'],
    hardwareOpen: state['hardware-drawer'],
    top: om.getTopOverlay(),
}};

// 6. Close remaining modal via closeActive(), leaving hardware-drawer as top
om.closeActive();
const afterCloseSceneEditor = {{
    stack: om.getStack(),
    sceneEditorOpen: state['scene-editor'],
    hardwareOpen: state['hardware-drawer'],
    top: om.getTopOverlay(),
}};

// 7. Mobile viewport mutual exclusion (innerWidth < 768 closes side-nav-drawer when settings-drawer opens)
sandbox.window.innerWidth = 480;
om.overlays.get('settings-drawer').open();
const afterMobileOpen = {{
    stack: om.getStack(),
    sideOpen: state['side-nav-drawer'],
    hardwareOpen: state['hardware-drawer'],
    settingsOpen: state['settings-drawer'],
    hasActive: om.hasActiveOverlay(),
}};

// 8. closeAll() closes everything and empties stack
om.closeAll();
const afterCloseAll = {{
    stack: om.getStack(),
    settingsOpen: state['settings-drawer'],
    hasActive: om.hasActiveOverlay(),
    activeOverlay: om.activeOverlay,
}};

process.stdout.write(JSON.stringify({{
    afterSideAndGeneral,
    afterHardwareOpen,
    afterModalsStacked,
    afterCloseTop1,
    afterEscape,
    afterCloseSceneEditor,
    afterMobileOpen,
    afterCloseAll,
}}));
"""
        result = _run_node_script(script)

        assert result["afterSideAndGeneral"] == {
            "stack": ["side-nav-drawer", "general-drawer"],
            "sideOpen": True,
            "generalOpen": True,
            "top": "general-drawer",
        }
        assert result["afterHardwareOpen"] == {
            "stack": ["side-nav-drawer", "hardware-drawer"],
            "sideOpen": True,
            "generalOpen": False,
            "hardwareOpen": True,
            "top": "hardware-drawer",
        }
        assert result["afterModalsStacked"] == {
            "stack": [
                "side-nav-drawer",
                "hardware-drawer",
                "scene-editor",
                "icon-picker",
                "confirm-dialog",
            ],
            "hardwareOpen": True,
            "sceneEditorOpen": True,
            "iconPickerOpen": True,
            "confirmDialogOpen": True,
            "top": "confirm-dialog",
        }
        assert result["afterCloseTop1"] == {
            "closedFirst": "confirm-dialog",
            "stack": [
                "side-nav-drawer",
                "hardware-drawer",
                "scene-editor",
                "icon-picker",
            ],
            "confirmDialogOpen": False,
            "iconPickerOpen": True,
            "hardwareOpen": True,
            "top": "icon-picker",
        }
        assert result["afterEscape"] == {
            "prevented": True,
            "stack": ["side-nav-drawer", "hardware-drawer", "scene-editor"],
            "iconPickerOpen": False,
            "sceneEditorOpen": True,
            "hardwareOpen": True,
            "top": "scene-editor",
        }
        assert result["afterCloseSceneEditor"] == {
            "stack": ["side-nav-drawer", "hardware-drawer"],
            "sceneEditorOpen": False,
            "hardwareOpen": True,
            "top": "hardware-drawer",
        }
        assert result["afterMobileOpen"] == {
            "stack": ["settings-drawer"],
            "sideOpen": False,
            "hardwareOpen": False,
            "settingsOpen": True,
            "hasActive": True,
        }
        assert result["afterCloseAll"] == {
            "stack": [],
            "settingsOpen": False,
            "hasActive": False,
            "activeOverlay": None,
        }

    def test_overlay_manager_focus_restoration_and_dom_ordering(self) -> None:
        script = f"""
const fs = require('fs');
const vm = require('vm');

const code = fs.readFileSync({json.dumps(str(OVERLAY_MANAGER_JS))}, 'utf8');

const insertedBeforeCalls = [];
const firstSettingsEl = {{
    id: 'settings-drawer',
    compareDocumentPosition: () => 4,
}};
const routingEl = {{ id: 'routing-drawer' }};

const sandbox = {{
    window: {{ innerWidth: 1280 }},
    document: {{
        activeElement: null,
        body: {{
            querySelector: (sel) => sel.includes('settings-drawer') ? firstSettingsEl : null,
            querySelectorAll: (sel) => sel.includes('routing-drawer') ? [routingEl] : [],
            insertBefore: (el, ref) => insertedBeforeCalls.push([el.id, ref.id]),
            contains: (el) => Boolean(el && el.isConnected !== false),
        }},
        contains: (el) => Boolean(el && el.isConnected !== false),
        addEventListener: () => {{}},
    }},
    Node: {{ DOCUMENT_POSITION_FOLLOWING: 4 }},
}};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.createContext(sandbox);
vm.runInContext(code, sandbox);

const om = sandbox.window.overlayManager;

// Verify DOM ordering in register('routing-drawer')
om.register('routing-drawer', {{ close: () => {{}}, isOpen: () => false }});

// Verify focus restoration across stacked drawer + modal, and detached element guard
const focusLog = [];
const gearBtn = {{
    id: 'gear-btn',
    isConnected: true,
    focus: () => focusLog.push('gear-btn'),
}};
const pickIconBtn = {{
    id: 'pick-icon-btn',
    isConnected: true,
    focus: () => focusLog.push('pick-icon-btn'),
}};
const detachedBtn = {{
    id: 'detached-btn',
    isConnected: false,
    focus: () => focusLog.push('detached-btn'),
}};

sandbox.document.activeElement = gearBtn;
om.onOpen('general-drawer');

sandbox.document.activeElement = pickIconBtn;
om.onOpen('icon-picker');

// Close icon-picker -> should focus pick-icon-btn
om.onClose('icon-picker');

// Close general-drawer -> should focus gear-btn
om.onClose('general-drawer');

// Open profile-editor from detachedBtn -> close should NOT focus detachedBtn
sandbox.document.activeElement = detachedBtn;
om.onOpen('profile-editor');
om.onClose('profile-editor');

process.stdout.write(JSON.stringify({{
    insertedBeforeCalls,
    focusLog,
}}));
"""
        result = _run_node_script(script)
        assert result["insertedBeforeCalls"] == [["routing-drawer", "settings-drawer"]]
        assert result["focusLog"] == ["pick-icon-btn", "gear-btn"]


class TestUnifiedSettingsControllerAndHashRouting:
    """Verify 9-section routing, hash synchronization, and SettingsDrawer delegation."""

    def test_unified_settings_9_sections_routing_and_hash_sync(self) -> None:
        script = f"""
const fs = require('fs');
const vm = require('vm');

const overlayCode = fs.readFileSync({json.dumps(str(OVERLAY_MANAGER_JS))}, 'utf8');
const unifiedCode = fs.readFileSync({json.dumps(str(UNIFIED_SETTINGS_JS))}, 'utf8');

const hashListeners = [];
const locationObj = {{
    hash: '',
    pathname: '/',
    search: '',
}};
const historyObj = {{
    replaceState: (_state, _title, url) => {{
        if (typeof url === 'string' && url.startsWith('#')) {{
            locationObj.hash = url;
        }} else {{
            locationObj.hash = '';
        }}
    }},
}};

const domElements = {{}};
function makeEl(id) {{
    const classes = new Set();
    const attrs = {{}};
    return {{
        id,
        classList: {{
            add: (c) => classes.add(c),
            remove: (c) => classes.delete(c),
            contains: (c) => classes.has(c),
        }},
        setAttribute: (k, v) => {{ attrs[k] = v; }},
        getAttribute: (k) => attrs[k],
    }};
}}

[
    'general-drawer',
    'hardware-drawer',
    'interface-drawer',
    'theme-drawer',
    'integrations-drawer',
    'shortcuts-drawer',
    'settings-drawer',
].forEach((id) => {{ domElements[id] = makeEl(id); }});

const sandbox = {{
    window: {{
        innerWidth: 1280,
        location: locationObj,
        history: historyObj,
        addEventListener: (type, fn) => {{
            if (type === 'hashchange') hashListeners.push(fn);
        }},
    }},
    document: {{
        activeElement: null,
        getElementById: (id) => domElements[id] || null,
        querySelector: () => null,
        body: {{
            querySelector: () => null,
            querySelectorAll: () => [],
            insertBefore: () => {{}},
            contains: () => true,
        }},
        contains: () => true,
        addEventListener: () => {{}},
    }},
    Node: {{ DOCUMENT_POSITION_FOLLOWING: 4 }},
}};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(overlayCode, sandbox);

const om = sandbox.window.overlayManager;
const openedLog = [];
const drawerStates = {{}};

// Register individual drawers
['general', 'hardware', 'interface', 'theme', 'integrations', 'shortcuts'].forEach((sec) => {{
    const overlayName = `${{sec}}-drawer`;
    drawerStates[overlayName] = false;
    om.register(overlayName, {{
        open: () => {{
            drawerStates[overlayName] = true;
            openedLog.push({{ type: 'individual', section: sec, overlayName }});
            om.onOpen(overlayName);
        }},
        close: () => {{
            drawerStates[overlayName] = false;
            om.onClose(overlayName);
        }},
        isOpen: () => drawerStates[overlayName],
    }});
}});

// Mock window.settingsDrawer for profiles, scenes, system
sandbox.window.settingsDrawer = {{
    isOpen: false,
    activeTab: 'profiles',
    open: function(tab) {{
        this.isOpen = true;
        if (tab) this.activeTab = tab;
        openedLog.push({{ type: 'settingsDrawer', section: this.activeTab }});
        om.onOpen('settings-drawer');
        historyObj.replaceState(null, '', `#settings/${{this.activeTab}}`);
    }},
    close: function() {{
        this.isOpen = false;
        om.onClose('settings-drawer');
    }},
}};
om.register('settings-drawer', {{
    open: (tab) => sandbox.window.settingsDrawer.open(tab),
    close: () => sandbox.window.settingsDrawer.close(),
    isOpen: () => sandbox.window.settingsDrawer.isOpen,
}});

vm.runInContext(unifiedCode, sandbox);
const us = sandbox.window.unifiedSettings;

const sections = us.getSections();
const sectionResults = [];

for (const sec of sections) {{
    us.open(sec);
    sectionResults.push({{
        section: sec,
        hash: locationObj.hash,
        activeSection: us.getActiveSection(),
        topOverlay: om.getTopOverlay(),
    }});
}}

// Test close() clears hash and resets active section
us.close();
const afterClose = {{
    hash: locationObj.hash,
    activeSection: us.getActiveSection(),
    isOpen: us.isOpen,
}};

// Test hashchange listener for #settings/integrations and #settings/scenes
locationObj.hash = '#settings/integrations';
hashListeners.forEach((fn) => fn());
const afterHashIntegrations = {{
    hash: locationObj.hash,
    activeSection: us.getActiveSection(),
    topOverlay: om.getTopOverlay(),
}};

locationObj.hash = '#settings/scenes';
hashListeners.forEach((fn) => fn());
const afterHashScenes = {{
    hash: locationObj.hash,
    activeSection: us.getActiveSection(),
    topOverlay: om.getTopOverlay(),
    settingsDrawerTab: sandbox.window.settingsDrawer.activeTab,
}};

const navHtml = us.renderSectionNav('theme');

process.stdout.write(JSON.stringify({{
    sections,
    sectionResults,
    openedLog,
    afterClose,
    afterHashIntegrations,
    afterHashScenes,
    navHtml,
}}));
"""
        result = _run_node_script(script)

        assert result["sections"] == ALL_NINE_SECTIONS

        for item in result["sectionResults"]:
            sec = item["section"]
            assert item["hash"] == f"#settings/{sec}"
            assert item["activeSection"] == sec
            if sec in SETTINGS_DRAWER_SECTIONS:
                assert item["topOverlay"] == "settings-drawer"
            else:
                assert item["topOverlay"] == f"{sec}-drawer"

        assert result["afterClose"] == {
            "hash": "",
            "activeSection": None,
            "isOpen": False,
        }
        assert result["afterHashIntegrations"] == {
            "hash": "#settings/integrations",
            "activeSection": "integrations",
            "topOverlay": "integrations-drawer",
        }
        assert result["afterHashScenes"] == {
            "hash": "#settings/scenes",
            "activeSection": "scenes",
            "topOverlay": "settings-drawer",
            "settingsDrawerTab": "scenes",
        }
        for sec in ALL_NINE_SECTIONS:
            assert f'data-section="{sec}"' in result["navHtml"]
        assert 'data-section="theme" data-drawer="theme-drawer" role="tab" aria-selected="true"' in result["navHtml"]

    def test_settings_drawer_init_hash_routing_delegates_all_sections(self) -> None:
        script = f"""
const fs = require('fs');
const vm = require('vm');

const overlayCode = fs.readFileSync({json.dumps(str(OVERLAY_MANAGER_JS))}, 'utf8');
const unifiedCode = fs.readFileSync({json.dumps(str(UNIFIED_SETTINGS_JS))}, 'utf8');
const settingsDrawerCode = fs.readFileSync({json.dumps(str(SETTINGS_DRAWER_JS))}, 'utf8');

const hashListeners = [];
const locationObj = {{ hash: '#settings/scenes', pathname: '/', search: '' }};
const historyObj = {{
    replaceState: (_s, _t, url) => {{
        locationObj.hash = (typeof url === 'string' && url.startsWith('#')) ? url : '';
    }},
}};

function makeMockElement() {{
    return {{
        className: '',
        id: '',
        innerHTML: '',
        style: {{}},
        dataset: {{}},
        classList: {{ add: () => {{}}, remove: () => {{}}, toggle: () => {{}} }},
        addEventListener: () => {{}},
        appendChild: () => {{}},
        querySelector: () => makeMockElement(),
        querySelectorAll: () => [],
    }};
}}

const sandbox = {{
    window: {{
        innerWidth: 1280,
        location: locationObj,
        history: historyObj,
        addEventListener: (type, fn) => {{
            if (type === 'hashchange') hashListeners.push(fn);
        }},
    }},
    document: {{
        activeElement: null,
        createElement: () => makeMockElement(),
        getElementById: () => makeMockElement(),
        querySelector: () => makeMockElement(),
        body: {{
            style: {{}},
            appendChild: () => {{}},
            querySelector: () => null,
            querySelectorAll: () => [],
            insertBefore: () => {{}},
            contains: () => true,
        }},
        contains: () => true,
        addEventListener: () => {{}},
    }},
    state: {{
        on: () => {{}},
        profiles: [],
        phase8Scenes: [],
        systemActions: [],
        favorites: [],
    }},
    Helpers: {{ escapeHtml: (s) => String(s) }},
    Node: {{ DOCUMENT_POSITION_FOLLOWING: 4 }},
}};
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(overlayCode, sandbox);
vm.runInContext(settingsDrawerCode, sandbox);
vm.runInContext(unifiedCode, sandbox);

// Initialize SettingsDrawer hash routing as app.js does
sandbox.window.settingsDrawer.initHashRouting();

const initialActiveTab = sandbox.window.settingsDrawer.activeTab;
const delegatedCalls = [];
const origOpen = sandbox.window.unifiedSettings.open.bind(sandbox.window.unifiedSettings);
sandbox.window.unifiedSettings.open = (sec) => {{
    delegatedCalls.push(sec);
    return origOpen(sec);
}};

// Trigger hashchange for a delegated section (#settings/hardware)
locationObj.hash = '#settings/hardware';
hashListeners[0]();
const afterHardwareHash = {{
    hash: locationObj.hash,
    activeSection: sandbox.window.unifiedSettings.getActiveSection(),
}};

// Trigger hashchange for a settings-drawer tab (#settings/system)
locationObj.hash = '#settings/system';
hashListeners[0]();
const afterSystemHash = {{
    hash: locationObj.hash,
    settingsDrawerOpen: sandbox.window.settingsDrawer.isOpen,
    settingsDrawerTab: sandbox.window.settingsDrawer.activeTab,
}};

process.stdout.write(JSON.stringify({{
    initialActiveTab,
    delegatedCalls,
    afterHardwareHash,
    afterSystemHash,
}}));
"""
        result = _run_node_script(script)
        assert result["initialActiveTab"] == "scenes"
        assert "hardware" in result["delegatedCalls"]
        assert result["afterHardwareHash"] == {
            "hash": "#settings/hardware",
            "activeSection": "hardware",
        }
        assert result["afterSystemHash"] == {
            "hash": "#settings/system",
            "settingsDrawerOpen": True,
            "settingsDrawerTab": "system",
        }


class TestJavaScriptLinting:
    """Verify `npm run lint:js` passes with zero errors."""

    def test_npm_run_lint_js_passes(self) -> None:
        import os

        npm_bin = shutil.which("npm") or "npm"
        env = os.environ.copy()
        local_nm = REPO_ROOT / "node_modules"
        shared_nm = Path("C:/scripts/unfoldedcircle-orei-hdmi-matrix-integration/node_modules")
        if not local_nm.exists() and shared_nm.exists():
            bin_dir = str(shared_nm / ".bin")
            env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
            env["NODE_PATH"] = str(shared_nm)

        proc = subprocess.run(
            [npm_bin, "run", "lint:js"],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, (
            f"npm run lint:js failed (exit {proc.returncode}):\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
