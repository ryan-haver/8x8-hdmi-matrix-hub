/**
 * KioskController
 *
 * Encapsulates the shared Kiosk logic for single-zone and all-zone switcher
 * modes, live WebSocket state handling, quick actions, and remembered-device
 * PIN unlocking (per UI-11 & Decision D7).
 */

class KioskController {
    /**
     * @param {Object} [options]
     * @param {string} [options.apiBase='/api'] - Base URL for REST API calls
     * @param {Object} [options.apiClient] - Optional ApiClient instance
     * @param {Object} [options.wsClient] - Optional MatrixWebSocket instance
     * @param {string} [options.url] - URL or query string to parse (defaults to window.location.href)
     * @param {Storage} [options.storage] - LocalStorage interface (defaults to window.localStorage)
     * @param {Function} [options.onRoutingChange] - Callback when routing changes: (routing) => {}
     * @param {Function} [options.onStateChange] - Callback when full state changes: (state) => {}
     * @param {Function} [options.onStatusChange] - Callback when connection status changes: (connected) => {}
     */
    constructor(options = {}) {
        this.apiBase = options.apiBase || '/api';
        this.apiClient = options.apiClient || (typeof window !== 'undefined' && window.apiClient ? window.apiClient : null);
        this.wsClient = options.wsClient || (typeof window !== 'undefined' && window.ws ? window.ws : null);
        this.storage = options.storage || (typeof window !== 'undefined' && window.localStorage ? window.localStorage : null);
        this.onRoutingChange = options.onRoutingChange || (() => {});
        this.onStateChange = options.onStateChange || (() => {});
        this.onStatusChange = options.onStatusChange || (() => {});

        // State
        this.lockedOutput = null; // null = all-zones mode, integer 1-8 = single-zone lock
        this.isSingleZoneMode = false;
        this.routing = {}; // map of output (1-8) -> input (1-8)
        this.inputs = {};
        this.outputs = {};
        this.connected = false;
        this._pinUnlocked = false;

        // Lifecycle event listener references
        this._visibilityHandler = null;
        this._onlineHandler = null;

        // Initialize state from URL and storage
        const initialUrl = options.url || (typeof window !== 'undefined' && window.location ? window.location.href : '');
        this.parseQueryParams(initialUrl);
        this._checkStoredPinSession();
        this.attachLifecycleListeners();
    }

    /**
     * Parse query parameters from URL or search string
     * Supports:
     *   ?output=1..8  -> locks to output zone 1..8
     *   ?zone=1..8    -> alternative alias for zone locking
     *   ?output=all   -> explicitly all-zones switcher mode
     *
     * @param {string} urlOrSearch - URL or search string
     * @returns {number|null} locked output or null
     */
    parseQueryParams(urlOrSearch = '') {
        try {
            let search = '';
            if (typeof urlOrSearch === 'string') {
                const qIdx = urlOrSearch.indexOf('?');
                search = qIdx !== -1 ? urlOrSearch.slice(qIdx) : (urlOrSearch.startsWith('?') ? urlOrSearch : '');
            } else if (typeof window !== 'undefined' && window.location) {
                search = window.location.search || '';
            }

            const params = new URLSearchParams(search);
            const outputVal = params.get('output') || params.get('zone');

            if (outputVal && outputVal.toLowerCase() !== 'all') {
                const parsed = parseInt(outputVal, 10);
                if (!isNaN(parsed) && parsed >= 1 && parsed <= 8) {
                    this.lockedOutput = parsed;
                    this.isSingleZoneMode = true;
                    return this.lockedOutput;
                }
            }

            this.lockedOutput = null;
            this.isSingleZoneMode = false;
            return null;
        } catch (e) {
            this.lockedOutput = null;
            this.isSingleZoneMode = false;
            return null;
        }
    }

    /**
     * Check if currently locked to a single output zone
     * @returns {boolean}
     */
    isSingleZone() {
        return this.isSingleZoneMode && this.lockedOutput !== null;
    }

    /**
     * Check if in all-zones switcher mode
     * @returns {boolean}
     */
    isAllZones() {
        return !this.isSingleZone();
    }

    /**
     * Return locked output zone number (1-8) or null if all-zones
     * @returns {number|null}
     */
    getLockedOutput() {
        return this.lockedOutput;
    }

    /**
     * Dynamically lock to a single zone or unlock to all-zones
     * @param {number|null} output - Output number 1-8, or null/'all' for all-zones
     */
    setLockedOutput(output) {
        if (output === null || output === undefined || output === 'all') {
            this.lockedOutput = null;
            this.isSingleZoneMode = false;
        } else {
            const parsed = parseInt(output, 10);
            if (!isNaN(parsed) && parsed >= 1 && parsed <= 8) {
                this.lockedOutput = parsed;
                this.isSingleZoneMode = true;
            } else {
                this.lockedOutput = null;
                this.isSingleZoneMode = false;
            }
        }
    }

    /**
     * Check persistent storage for remembered PIN unlock state
     * @private
     */
    _checkStoredPinSession() {
        if (this.storage) {
            try {
                const unlocked = this.storage.getItem('orei_kiosk_pin_unlocked');
                if (unlocked === 'true') {
                    this._pinUnlocked = true;
                }
            } catch (e) {
                // Ignore storage access error
            }
        }
    }

    /**
     * Attach visibilitychange and online lifecycle listeners for auto-resync
     */
    attachLifecycleListeners() {
        if (typeof document !== 'undefined' && document.addEventListener && !this._visibilityHandler) {
            this._visibilityHandler = () => {
                if (document.visibilityState === 'visible') {
                    this.loadState().catch(() => {});
                }
            };
            document.addEventListener('visibilitychange', this._visibilityHandler);
        }

        if (typeof window !== 'undefined' && window.addEventListener && !this._onlineHandler) {
            this._onlineHandler = () => {
                this.loadState().catch(() => {});
            };
            window.addEventListener('online', this._onlineHandler);
        }
    }

    /**
     * Detach lifecycle event listeners
     */
    detachLifecycleListeners() {
        if (typeof document !== 'undefined' && document.removeEventListener && this._visibilityHandler) {
            document.removeEventListener('visibilitychange', this._visibilityHandler);
            this._visibilityHandler = null;
        }

        if (typeof window !== 'undefined' && window.removeEventListener && this._onlineHandler) {
            window.removeEventListener('online', this._onlineHandler);
            this._onlineHandler = null;
        }
    }

    /**
     * Handle incoming WebSocket events from hub
     * Handles:
     *   - 'switch': single output routed { output, input }
     *   - 'switch_all': route_all event { input }
     *   - 'routing_change': standard hub event { output, input }
     *   - 'status': full snapshot { routing, inputs, outputs, ... }
     *   - 'switch_all_failed': triggers loadState() resync
     *
     * @param {Object} message - Raw message { type, data } or { event, data }
     */
    handleWebSocketMessage(message) {
        if (!message) return;
        const type = message.type || message.event;
        const data = message.data || {};

        switch (type) {
            case 'switch':
            case 'routing_change': {
                const out = parseInt(data.output, 10);
                const inp = parseInt(data.input, 10);
                if (!isNaN(out) && !isNaN(inp)) {
                    this.routing[out] = inp;
                    this.onRoutingChange({ ...this.routing });
                }
                break;
            }
            case 'switch_all': {
                const inp = parseInt(data.input, 10);
                if (!isNaN(inp)) {
                    for (let o = 1; o <= 8; o++) {
                        this.routing[o] = inp;
                    }
                    this.onRoutingChange({ ...this.routing });
                }
                break;
            }
            case 'status': {
                if (data.routing && typeof data.routing === 'object') {
                    for (let o = 1; o <= 8; o++) {
                        if (data.routing[o] !== undefined) {
                            this.routing[o] = parseInt(data.routing[o], 10);
                        }
                    }
                }
                if (data.inputs) this.inputs = data.inputs;
                if (data.outputs) this.outputs = data.outputs;
                this.connected = true;
                this.onRoutingChange({ ...this.routing });
                this.onStateChange(this.getState());
                this.onStatusChange(true);
                break;
            }
            case 'switch_all_failed': {
                this.loadState().catch(() => {});
                break;
            }
            default:
                break;
        }
    }

    /**
     * Fetch fresh state from the REST API to resync local cache
     * @returns {Promise<Object>} State object
     */
    async loadState() {
        try {
            let statusData = null;
            if (this.apiClient && typeof this.apiClient.getStatus === 'function') {
                const res = await this.apiClient.getStatus();
                statusData = res?.data || res;
            } else if (typeof fetch !== 'undefined') {
                const res = await fetch(`${this.apiBase}/status`);
                if (res.ok) {
                    const json = await res.json();
                    statusData = json.data || json;
                }
            }

            if (statusData) {
                if (statusData.routing) {
                    for (let o = 1; o <= 8; o++) {
                        if (statusData.routing[o] !== undefined) {
                            this.routing[o] = parseInt(statusData.routing[o], 10);
                        }
                    }
                }
                if (statusData.inputs) this.inputs = statusData.inputs;
                if (statusData.outputs) this.outputs = statusData.outputs;
                this.connected = true;

                this.onRoutingChange({ ...this.routing });
                this.onStateChange(this.getState());
                this.onStatusChange(true);
            }

            return this.getState();
        } catch (err) {
            return this.getState();
        }
    }

    /**
     * Return current snapshot of controller state
     * @returns {Object}
     */
    getState() {
        return {
            routing: { ...this.routing },
            inputs: this.inputs,
            outputs: this.outputs,
            lockedOutput: this.lockedOutput,
            isSingleZone: this.isSingleZone(),
            connected: this.connected,
            pinUnlocked: this.isPinUnlocked()
        };
    }

    // ===== Quick Actions Bar Support =====

    /**
     * Recall a preset (POST /api/preset/{presetNum})
     * @param {number|string} presetNum - Preset number 1-8
     * @returns {Promise<Object>} Response object
     */
    async recallPreset(presetNum) {
        const num = parseInt(presetNum, 10);
        if (isNaN(num) || num < 1 || num > 8) {
            throw new Error(`Invalid preset number: ${presetNum}`);
        }

        if (this.apiClient && typeof this.apiClient.recallPreset === 'function') {
            return this.apiClient.recallPreset(num);
        }

        const res = await fetch(`${this.apiBase}/preset/${num}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!res.ok) {
            throw new Error(`Failed to recall preset ${num}: HTTP ${res.status}`);
        }
        return res.json().catch(() => ({ success: true }));
    }

    /**
     * Recall a profile (POST /api/profile/{profileId}/recall)
     * @param {string} profileId - ID of profile to recall
     * @param {Object} [options]
     * @param {string} [options.passcode] - Optional passcode if profile is protected
     * @returns {Promise<Object>} Response object
     */
    async recallProfile(profileId, { passcode } = {}) {
        if (!profileId) {
            throw new Error('Profile ID is required');
        }

        if (this.apiClient && typeof this.apiClient.recallProfile === 'function') {
            return this.apiClient.recallProfile(profileId, { passcode });
        }

        const body = passcode ? JSON.stringify({ passcode }) : '{}';
        const res = await fetch(`${this.apiBase}/profile/${encodeURIComponent(profileId)}/recall`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body
        });

        if (!res.ok) {
            throw new Error(`Failed to recall profile ${profileId}: HTTP ${res.status}`);
        }
        return res.json().catch(() => ({ success: true }));
    }

    /**
     * Execute a shortcut (POST /api/shortcuts/{shortcutId}/execute or /api/system-shortcuts/{shortcutId}/execute)
     * @param {string} shortcutId - Shortcut key or ID
     * @param {Object} [options]
     * @param {boolean} [options.isSystem=false] - Whether this is a system shortcut
     * @returns {Promise<Object>} Response object
     */
    async executeShortcut(shortcutId, { isSystem = false } = {}) {
        if (!shortcutId) {
            throw new Error('Shortcut ID is required');
        }

        const prefix = isSystem ? '/system-shortcuts' : '/shortcuts';
        const res = await fetch(`${this.apiBase}${prefix}/${encodeURIComponent(shortcutId)}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!res.ok) {
            throw new Error(`Failed to execute shortcut ${shortcutId}: HTTP ${res.status}`);
        }
        return res.json().catch(() => ({ success: true }));
    }

    /**
     * Generic quick action executor
     * @param {Object} action - Action descriptor { type: 'preset'|'profile'|'shortcut', id: ... }
     * @returns {Promise<Object>}
     */
    async executeQuickAction(action) {
        if (!action || !action.type) {
            throw new Error('Action must specify a type');
        }
        switch (action.type) {
            case 'preset':
                return this.recallPreset(action.id);
            case 'profile':
            case 'scene':
                return this.recallProfile(action.id, { passcode: action.passcode });
            case 'shortcut':
                return this.executeShortcut(action.id, { isSystem: action.isSystem || false });
            case 'system_shortcut':
                return this.executeShortcut(action.id, { isSystem: true });
            default:
                throw new Error(`Unknown quick action type: ${action.type}`);
        }
    }

    // ===== Remembered-Device CONTROL_PIN Unlock Helper (Decision D7) =====

    /**
     * Check if control PIN is currently unlocked
     * @returns {boolean}
     */
    isPinUnlocked() {
        if (this._pinUnlocked) return true;
        if (this.storage) {
            try {
                return this.storage.getItem('orei_kiosk_pin_unlocked') === 'true';
            } catch (e) {
                return false;
            }
        }
        return false;
    }

    /**
     * Unlock kiosk with PIN (Decision D7).
     * Exchanges PIN for session via /api/auth/login or /api/auth/unlock,
     * remembering the device so tablet users are not prompted on every tap.
     *
     * @param {string} pin - Control PIN
     * @param {Object} [options]
     * @param {boolean} [options.rememberDevice=true] - Remember this device
     * @param {string} [options.deviceName='Kiosk'] - Device identifier
     * @returns {Promise<Object>}
     */
    async unlockWithPin(pin, options = {}) {
        if (!pin) {
            throw new Error('PIN is required');
        }

        const remember = options.rememberDevice !== false;
        const deviceName = options.deviceName || 'Kiosk';
        const payload = {
            pin: String(pin),
            level: 'control',
            remember_device: remember,
            device_name: deviceName
        };

        let response = null;
        let authErr = null;

        // Try /api/auth/login first, then /api/auth/unlock as fallback
        const endpoints = [`${this.apiBase}/auth/login`, `${this.apiBase}/auth/unlock`];
        for (const ep of endpoints) {
            try {
                const res = await fetch(ep, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (res.status === 404) {
                    continue; // try next endpoint
                }

                if (res.ok) {
                    response = await res.json().catch(() => ({ level: 'control' }));
                    break;
                } else {
                    const text = await res.text().catch(() => '');
                    authErr = new Error(text || `Auth failed: HTTP ${res.status}`);
                    authErr.status = res.status;
                    break; // Non-404 failure (e.g. 401 Incorrect PIN, 429 rate limit)
                }
            } catch (err) {
                authErr = err;
            }
        }

        if (response) {
            this._pinUnlocked = true;
            if (remember && this.storage) {
                try {
                    this.storage.setItem('orei_kiosk_pin_unlocked', 'true');
                } catch (e) {
                    // Ignore storage access error
                }
            }
            return { success: true, ...response };
        }

        throw authErr || new Error('Unlock request failed');
    }

    /**
     * Lock the PIN session and clear remembered device state
     * @returns {Promise<Object>}
     */
    async lockPin() {
        this._pinUnlocked = false;
        if (this.storage) {
            try {
                this.storage.removeItem('orei_kiosk_pin_unlocked');
            } catch (e) {
                // Ignore storage access error
            }
        }

        try {
            await fetch(`${this.apiBase}/auth/lock`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
        } catch (e) {
            // Ignore network error on lock
        }

        return { success: true, locked: true };
    }

    /**
     * Clean up all event listeners and timers
     */
    destroy() {
        this.detachLifecycleListeners();
    }
}

// Attach to window for browser classic scripts
if (typeof window !== 'undefined') {
    window.KioskController = KioskController;
}
