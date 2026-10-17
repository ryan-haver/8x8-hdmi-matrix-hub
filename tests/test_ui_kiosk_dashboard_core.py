"""Tests for Phase 5 (WP-E2) Track 4: Shared Kiosk Controller & Server-Backed Dashboard Store.

Tests KioskController (switch + switch_all live updates, single-zone vs all-zone mode,
remembered-device PIN unlock) and DashboardStore (one-time localStorage migration,
no resurrection of deleted widgets, server persistence), and verifies npm run lint:js passes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from rest_api import set_matrix_device
from rest_api.app import create_rest_app

ROOT_DIR = Path(__file__).resolve().parent.parent


def _run_node_script(script_body: str) -> dict:
    """Execute a Node script with mocked browser environment and return parsed JSON result."""
    harness = f"""
    const assert = require('assert');
    const fs = require('fs');
    const path = require('path');

    class MemoryStorage {{
        constructor() {{
            this.store = {{}};
        }}
        getItem(key) {{
            return Object.prototype.hasOwnProperty.call(this.store, key) ? this.store[key] : null;
        }}
        setItem(key, value) {{
            this.store[key] = String(value);
        }}
        removeItem(key) {{
            delete this.store[key];
        }}
        clear() {{
            this.store = {{}};
        }}
    }}

    const localStorage = new MemoryStorage();
    const documentListeners = {{}};
    const windowListeners = {{}};

    global.window = global;
    global.localStorage = localStorage;
    global.document = {{
        visibilityState: 'visible',
        addEventListener(event, fn) {{
            documentListeners[event] = documentListeners[event] || [];
            documentListeners[event].push(fn);
        }},
        removeEventListener(event, fn) {{
            if (documentListeners[event]) {{
                documentListeners[event] = documentListeners[event].filter(f => f !== fn);
            }}
        }}
    }};
    global.window.addEventListener = (event, fn) => {{
        windowListeners[event] = windowListeners[event] || [];
        windowListeners[event].push(fn);
    }};
    global.window.removeEventListener = (event, fn) => {{
        if (windowListeners[event]) {{
            windowListeners[event] = windowListeners[event].filter(f => f !== fn);
        }}
    }};

    // Load implementations
    const kioskCode = fs.readFileSync(path.join('{ROOT_DIR.as_posix()}', 'web/js/utils/kiosk-controller.js'), 'utf8');
    const dashCode = fs.readFileSync(path.join('{ROOT_DIR.as_posix()}', 'web/js/utils/dashboard-store.js'), 'utf8');

    eval(kioskCode);
    eval(dashCode);

    (async () => {{
        {script_body}
    }})().then(() => {{
        console.log(JSON.stringify({{ success: true }}));
    }}).catch((err) => {{
        console.error(err);
        console.log(JSON.stringify({{ success: false, error: err.message, stack: err.stack }}));
        process.exit(1);
    }});
    """

    res = subprocess.run(
        ["node", "-e", harness],
        capture_output=True,
        text=True,
        cwd=str(ROOT_DIR),
        check=False,
    )
    if res.returncode != 0:
        raise AssertionError(f"Node script failed (exit code {res.returncode}):\n{res.stderr}\n{res.stdout}")

    for line in reversed(res.stdout.splitlines()):
        try:
            return json.loads(line)
        except Exception:
            continue
    raise AssertionError(f"No JSON output from Node script:\n{res.stdout}\n{res.stderr}")


# =============================================================================
# 1. KioskController Tests (Browser Logic via Node)
# =============================================================================


class TestKioskController:
    """Test suite for KioskController (UI-11 & Decision D7)."""

    def test_single_zone_and_all_zones_query_param_parsing(self):
        """KioskController correctly parses ?output=1 lock vs all-zones switcher mode."""
        script = """
        // 1. Single zone mode with ?output=1
        const ctrl1 = new KioskController({ url: 'http://localhost/kiosk.html?output=1' });
        assert.strictEqual(ctrl1.isSingleZone(), true);
        assert.strictEqual(ctrl1.isAllZones(), false);
        assert.strictEqual(ctrl1.getLockedOutput(), 1);

        // 2. Single zone mode with ?output=4
        const ctrl2 = new KioskController({ url: 'http://localhost/kiosk.html?output=4' });
        assert.strictEqual(ctrl2.isSingleZone(), true);
        assert.strictEqual(ctrl2.getLockedOutput(), 4);

        // 3. Single zone mode with ?zone=3 alias
        const ctrl3 = new KioskController({ url: 'http://localhost/kiosk.html?zone=3' });
        assert.strictEqual(ctrl3.isSingleZone(), true);
        assert.strictEqual(ctrl3.getLockedOutput(), 3);

        // 4. All-zones switcher mode with ?output=all
        const ctrlAll = new KioskController({ url: 'http://localhost/kiosk.html?output=all' });
        assert.strictEqual(ctrlAll.isSingleZone(), false);
        assert.strictEqual(ctrlAll.isAllZones(), true);
        assert.strictEqual(ctrlAll.getLockedOutput(), null);

        // 5. Default with no query param
        const ctrlDefault = new KioskController({ url: 'http://localhost/kiosk.html' });
        assert.strictEqual(ctrlDefault.isSingleZone(), false);
        assert.strictEqual(ctrlDefault.isAllZones(), true);
        assert.strictEqual(ctrlDefault.getLockedOutput(), null);

        // 6. Out of range / invalid param
        const ctrlInvalid = new KioskController({ url: 'http://localhost/kiosk.html?output=99' });
        assert.strictEqual(ctrlInvalid.isSingleZone(), false);
        assert.strictEqual(ctrlInvalid.getLockedOutput(), null);

        // 7. Dynamic lock / unlock
        ctrlDefault.setLockedOutput(6);
        assert.strictEqual(ctrlDefault.isSingleZone(), true);
        assert.strictEqual(ctrlDefault.getLockedOutput(), 6);
        ctrlDefault.setLockedOutput(null);
        assert.strictEqual(ctrlDefault.isSingleZone(), false);
        assert.strictEqual(ctrlDefault.getLockedOutput(), null);
        """
        result = _run_node_script(script)
        assert result.get("success") is True

    def test_live_websocket_switch_and_switch_all_events(self):
        """KioskController handles BOTH single switch and switch_all events live."""
        script = """
        let routingChanges = [];
        const ctrl = new KioskController({
            onRoutingChange: (r) => routingChanges.push({ ...r })
        });

        // 1. Initial snapshot status
        ctrl.handleWebSocketMessage({
            type: 'status',
            data: {
                routing: { 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8 }
            }
        });
        assert.strictEqual(ctrl.routing[1], 1);
        assert.strictEqual(ctrl.routing[8], 8);

        // 2. Single output switch event ({ output, input })
        ctrl.handleWebSocketMessage({
            type: 'switch',
            data: { output: 2, input: 5 }
        });
        assert.strictEqual(ctrl.routing[2], 5);
        assert.strictEqual(ctrl.routing[1], 1); // unchanged
        assert.strictEqual(routingChanges[routingChanges.length - 1][2], 5);

        // 3. routing_change standard event alias
        ctrl.handleWebSocketMessage({
            type: 'routing_change',
            data: { output: 3, input: 7 }
        });
        assert.strictEqual(ctrl.routing[3], 7);

        // 4. switch_all event (route_all all outputs to input 4)
        ctrl.handleWebSocketMessage({
            type: 'switch_all',
            data: { input: 4 }
        });
        for (let o = 1; o <= 8; o++) {
            assert.strictEqual(ctrl.routing[o], 4, `Output ${o} should be routed to input 4`);
        }
        assert.strictEqual(routingChanges[routingChanges.length - 1][1], 4);
        assert.strictEqual(routingChanges[routingChanges.length - 1][8], 4);
        """
        result = _run_node_script(script)
        assert result.get("success") is True

    def test_visibilitychange_and_online_state_resync(self):
        """KioskController resyncs state via loadState on visibilitychange and online."""
        script = """
        let loadStateCalls = 0;
        const ctrl = new KioskController();
        ctrl.loadState = async () => {
            loadStateCalls++;
            return { routing: { 1: 2 } };
        };

        // Trigger visibilitychange to visible
        document.visibilityState = 'visible';
        assert.ok(documentListeners['visibilitychange'].length > 0);
        documentListeners['visibilitychange'].forEach(fn => fn());
        assert.strictEqual(loadStateCalls, 1);

        // Trigger hidden does not resync
        document.visibilityState = 'hidden';
        documentListeners['visibilitychange'].forEach(fn => fn());
        assert.strictEqual(loadStateCalls, 1);

        // Trigger online
        assert.ok(windowListeners['online'].length > 0);
        windowListeners['online'].forEach(fn => fn());
        assert.strictEqual(loadStateCalls, 2);

        // Clean up
        ctrl.destroy();
        assert.strictEqual(documentListeners['visibilitychange'].length, 0);
        assert.strictEqual(windowListeners['online'].length, 0);
        """
        result = _run_node_script(script)
        assert result.get("success") is True

    def test_quick_actions_bar_support(self):
        """KioskController supports Presets, Shortcuts, and Profiles recall."""
        script = """
        const requests = [];
        global.fetch = async (url, options = {}) => {
            requests.push({ url, method: options.method || 'GET', body: options.body ? JSON.parse(options.body) : null });
            return {
                ok: true,
                status: 200,
                json: async () => ({ success: true })
            };
        };

        const ctrl = new KioskController();

        // 1. Recall Preset
        await ctrl.recallPreset(3);
        assert.strictEqual(requests[0].url, '/api/preset/3');
        assert.strictEqual(requests[0].method, 'POST');

        // 2. Recall Profile
        await ctrl.recallProfile('movie_night', { passcode: '1234' });
        assert.strictEqual(requests[1].url, '/api/profile/movie_night/recall');
        assert.strictEqual(requests[1].method, 'POST');
        assert.deepStrictEqual(requests[1].body, { passcode: '1234' });

        // 3. Execute Shortcut
        await ctrl.executeShortcut('power_all', { isSystem: true });
        assert.strictEqual(requests[2].url, '/api/system-shortcuts/power_all/execute');
        assert.strictEqual(requests[2].method, 'POST');

        // 4. Generic quick action runner
        await ctrl.executeQuickAction({ type: 'preset', id: 5 });
        assert.strictEqual(requests[3].url, '/api/preset/5');
        """
        result = _run_node_script(script)
        assert result.get("success") is True

    def test_remembered_device_control_pin_unlock(self):
        """KioskController remembered-device CONTROL_PIN unlock helper (Decision D7)."""
        script = """
        const requests = [];
        global.fetch = async (url, options = {}) => {
            const body = options.body ? JSON.parse(options.body) : {};
            requests.push({ url, method: options.method, body });

            if (url.endsWith('/auth/login') || url.endsWith('/auth/unlock')) {
                if (body.pin === '5678') {
                    return {
                        ok: true,
                        status: 200,
                        json: async () => ({ success: true, level: 'control' })
                    };
                } else {
                    return {
                        ok: false,
                        status: 401,
                        text: async () => 'Incorrect PIN'
                    };
                }
            } else if (url.endsWith('/auth/lock')) {
                return {
                    ok: true,
                    status: 200,
                    json: async () => ({ locked: true })
                };
            }
            return { ok: false, status: 404 };
        };

        const memStorage = new MemoryStorage();
        const ctrl = new KioskController({ storage: memStorage });

        // 1. Initially locked
        assert.strictEqual(ctrl.isPinUnlocked(), false);

        // 2. Failed unlock
        let failed = false;
        try {
            await ctrl.unlockWithPin('wrong');
        } catch (e) {
            failed = true;
        }
        assert.strictEqual(failed, true);
        assert.strictEqual(ctrl.isPinUnlocked(), false);
        assert.strictEqual(memStorage.getItem('orei_kiosk_pin_unlocked'), null);

        // 3. Successful unlock with rememberDevice=true
        const res = await ctrl.unlockWithPin('5678', { rememberDevice: true, deviceName: 'Tablet Wall' });
        assert.strictEqual(res.success, true);
        assert.strictEqual(ctrl.isPinUnlocked(), true);
        assert.strictEqual(memStorage.getItem('orei_kiosk_pin_unlocked'), 'true');
        assert.strictEqual(requests[requests.length - 1].body.remember_device, true);
        assert.strictEqual(requests[requests.length - 1].body.device_name, 'Tablet Wall');

        // 4. Tablet users are not prompted on reload / new instance (Decision D7)
        const ctrl2 = new KioskController({ storage: memStorage });
        assert.strictEqual(ctrl2.isPinUnlocked(), true, 'New instance reads remembered pin unlock from storage');

        // 5. Lock Pin clears persistent state
        await ctrl.lockPin();
        assert.strictEqual(ctrl.isPinUnlocked(), false);
        assert.strictEqual(memStorage.getItem('orei_kiosk_pin_unlocked'), null);
        """
        result = _run_node_script(script)
        assert result.get("success") is True


# =============================================================================
# 2. DashboardStore Tests (Browser Logic via Node)
# =============================================================================


class TestDashboardStore:
    """Test suite for DashboardStore (DI-5 & UI-08)."""

    def test_one_time_legacy_migration_and_no_resurrection(self):
        """DashboardStore performs one-time migration and prevents resurrection of deleted defaults (UI-08)."""
        script = """
        let savedLayout = null;
        global.fetch = async (url, options = {}) => {
            if (url.endsWith('/dashboard/layout')) {
                if (options.method === 'POST' || options.method === 'PUT') {
                    savedLayout = JSON.parse(options.body);
                    return {
                        ok: true,
                        status: 200,
                        json: async () => ({ success: true, data: savedLayout })
                    };
                } else if (!options.method || options.method === 'GET') {
                    return {
                        ok: true,
                        status: 200,
                        json: async () => ({ success: true, data: savedLayout || { version: 1, cards: [] } })
                    };
                }
            }
            return { ok: false, status: 404 };
        };

        const memStorage = new MemoryStorage();

        // Populate legacy localStorage keys
        memStorage.setItem('orei_dashboard_widgets', JSON.stringify([
            { id: '1', type: 'preset' },
            { id: '2', type: 'preset' }
        ]));
        memStorage.setItem('orei_pinned_scenes', JSON.stringify(['movie_night', 'gaming']));
        memStorage.setItem('matrix_dashboard_layout', JSON.stringify({
            cards: [{ id: 'pwr_off', type: 'system_shortcut' }]
        }));

        assert.strictEqual(memStorage.getItem('orei_dashboard_migrated_v1'), null);

        // Initialize store
        const store = new DashboardStore({ storage: memStorage });
        assert.strictEqual(store.isMigrated(), false);

        // Perform one-time migration
        const migrationResult = await store.migrateLegacyStorage();
        assert.strictEqual(migrationResult.migrated, true);
        assert.strictEqual(migrationResult.count >= 5, true);

        // Verification 1: Layout sent to server
        assert.ok(savedLayout !== null);
        assert.ok(savedLayout.cards.length >= 5);
        const cardIds = savedLayout.cards.map(c => c.id);
        assert.ok(cardIds.includes('1'));
        assert.ok(cardIds.includes('movie_night'));
        assert.ok(cardIds.includes('pwr_off'));

        // Verification 2: Migration flag set
        assert.strictEqual(memStorage.getItem('orei_dashboard_migrated_v1'), 'true');

        // Verification 3: Legacy keys cleared
        assert.strictEqual(memStorage.getItem('orei_dashboard_widgets'), null);
        assert.strictEqual(memStorage.getItem('orei_pinned_scenes'), null);
        assert.strictEqual(memStorage.getItem('matrix_dashboard_layout'), null);

        // Verification 4: Idempotent - second call does not re-migrate
        const secondMigration = await store.migrateLegacyStorage();
        assert.strictEqual(secondMigration.migrated, false);
        assert.strictEqual(secondMigration.alreadyMigrated, true);

        // Verification 5 (UI-08): No resurrection of deleted widgets
        await store.loadLayout();
        // Remove preset 1
        const removed = store.removeWidget('1');
        assert.strictEqual(removed, true);
        await store.flush();

        // Reload layout
        await store.loadLayout();
        const reloadedIds = store.getWidgets().map(w => w.id);
        assert.strictEqual(reloadedIds.includes('1'), false, 'Deleted widget must NEVER resurrect from legacy storage');
        """
        result = _run_node_script(script)
        assert result.get("success") is True

    def test_widget_add_remove_reorder_resize_and_debounced_persistence(self):
        """DashboardStore supports add, remove, reorder, and resize with debounced persistence."""
        script = """
        let saveCount = 0;
        let lastPayload = null;

        global.fetch = async (url, options = {}) => {
            if (url.endsWith('/dashboard/layout')) {
                if (options.method === 'POST' || options.method === 'PUT') {
                    saveCount++;
                    lastPayload = JSON.parse(options.body);
                    return {
                        ok: true,
                        status: 200,
                        json: async () => ({ success: true, data: lastPayload })
                    };
                }
            }
            return { ok: false, status: 404 };
        };

        const store = new DashboardStore({ debounceMs: 50 });

        // 1. Add widgets
        store.addWidget({ id: '1', type: 'preset' });
        store.addWidget({ id: '2', type: 'preset' });
        store.addWidget({ id: 'scene_a', type: 'profile' });

        assert.strictEqual(store.getWidgets().length, 3);
        assert.strictEqual(saveCount, 0, 'Saves should be debounced, not immediate');

        // 2. Resize widget
        store.resizeWidget('1', { width: 2, height: 2, size: 'large' });
        const w1 = store.getWidgets().find(w => w.id === '1');
        assert.strictEqual(w1.width, 2);
        assert.strictEqual(w1.size, 'large');

        // 3. Reorder widgets
        store.reorderWidgets(['scene_a', '2', '1']);
        assert.deepStrictEqual(store.getWidgets().map(w => w.id), ['scene_a', '2', '1']);

        // 4. Remove widget
        store.removeWidget('2');
        assert.deepStrictEqual(store.getWidgets().map(w => w.id), ['scene_a', '1']);

        // 5. Flush persistence immediately
        await store.flush();
        assert.strictEqual(saveCount, 1, 'Debounced calls should coalesce into exactly 1 save');
        assert.ok(lastPayload !== null);
        assert.strictEqual(lastPayload.cards.length, 2);
        assert.strictEqual(lastPayload.cards[0].id, 'scene_a');
        assert.strictEqual(lastPayload.cards[1].id, '1');
        assert.strictEqual(lastPayload.cards[1].width, 2);
        """
        result = _run_node_script(script)
        assert result.get("success") is True


# =============================================================================
# 3. REST API Backend Integration Tests (Python aiohttp)
# =============================================================================


class TestBackendEndpoints:
    """Verify backend routes for /api/auth/login and POST /api/dashboard/layout."""

    @pytest.fixture
    def app_with_data_dir(self, tmp_path, mock_matrix, monkeypatch):
        monkeypatch.setenv("MATRIX_PASSWORD_ITERATIONS", "1000")
        from persistence import reset_data_dir_cache
        reset_data_dir_cache()
        set_matrix_device(mock_matrix, {i: f"In {i}" for i in range(1, 9)}, data_dir=str(tmp_path))
        return create_rest_app(tmp_path)

    @pytest.fixture
    async def client(self, aiohttp_client, app_with_data_dir):
        return await aiohttp_client(app_with_data_dir)

    @pytest.mark.asyncio
    async def test_auth_login_sets_cookie_and_remembers_device(self, client):
        """POST /api/auth/login behaves as auth_unlock with cookie and device remembering."""
        # Set control PIN
        await client.post("/api/auth/pin", json={"level": "control", "pin": "7788"})

        # Unauthorized before unlock
        resp = await client.post("/api/power/on")
        assert resp.status == 401

        # Unlock via /api/auth/login
        login_resp = await client.post(
            "/api/auth/login",
            json={
                "level": "control",
                "pin": "7788",
                "remember_device": True,
                "device_name": "Kiosk Tablet",
            },
        )
        assert login_resp.status == 200
        data = await login_resp.json()
        assert data.get("level") == "control"
        assert any("orei_device_token=" in val for val in login_resp.headers.getall("Set-Cookie"))

        # Subsequent control requests succeed
        assert (await client.post("/api/power/on")).status != 401

    @pytest.mark.asyncio
    async def test_post_dashboard_layout_replaces_atomically(self, client):
        """POST /api/dashboard/layout replaces the layout atomically just like PUT."""
        resp = await client.post(
            "/api/dashboard/layout",
            json={
                "version": 1,
                "cards": [
                    {"type": "preset", "id": "1", "order": 0},
                    {"type": "preset", "id": "2", "order": 1},
                ],
            },
        )
        assert resp.status == 200
        data = await resp.json()
        assert data["success"] is True
        assert len(data["data"]["cards"]) == 2

        # Verify via GET
        get_resp = await client.get("/api/dashboard/layout")
        assert get_resp.status == 200
        get_data = await get_resp.json()
        assert len(get_data["data"]["cards"]) == 2
        assert get_data["data"]["cards"][0]["id"] == "1"


# =============================================================================
# 4. ESLint Verification
# =============================================================================


def test_npm_run_lint_js_passes():
    """Verify that npm run lint:js runs cleanly with zero ESLint errors."""
    proc = subprocess.run(
        ["npm", "run", "lint:js"],
        cwd=str(ROOT_DIR),
        capture_output=True,
        text=True,
        shell=sys.platform == "win32",
    )
    assert proc.returncode == 0, f"ESLint failed:\n{proc.stderr}\n{proc.stdout}"
