/**
 * OREI Matrix Control - General Settings Drawer
 *
 * Slide-out drawer containing General settings:
 * - System Info (model, firmware, API version, server IP)
 * - Connection Settings (matrix IP, test/save/reset)
 */

class GeneralDrawer {
    constructor() {
        this.isOpen = false;
        this.container = null;
        this.backdrop = null;
        this.authStatus = null;
        this.authDevices = [];
        this.apiKeys = [];
        this.lastCreatedApiKey = null;
        this.accessExpanded = false;

        this.createDrawer();
        this.registerWithOverlayManager();
    }

    /**
     * Create drawer and backdrop in DOM
     */
    createDrawer() {
        // Backdrop overlay
        const backdrop = document.createElement("div");
        backdrop.id = "general-drawer-backdrop";
        backdrop.className = "settings-drawer-backdrop";
        backdrop.addEventListener("click", () => this.close());
        document.body.appendChild(backdrop);
        this.backdrop = backdrop;

        // Drawer container
        const drawer = document.createElement("aside");
        drawer.id = "general-drawer";
        drawer.className = "settings-drawer general-drawer";
        drawer.setAttribute("aria-hidden", "true");
        drawer.setAttribute("role", "dialog");
        drawer.setAttribute("aria-label", "General Settings");
        drawer.innerHTML = `
            <style>
                #general-access-section .auth-subblock {
                    margin-top: var(--space-3);
                    padding-top: var(--space-2);
                    border-top: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
                }
                #general-access-section .auth-list {
                    display: flex;
                    flex-direction: column;
                    gap: var(--space-1);
                    margin-top: var(--space-2);
                }
                #general-access-section .auth-list-item {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: var(--space-2);
                    padding: var(--space-1) var(--space-2);
                    background: var(--surface-secondary, rgba(255, 255, 255, 0.04));
                    border-radius: var(--radius-sm, 6px);
                    font-size: var(--font-size-xs, 0.75rem);
                }
                #general-access-section .auth-key-banner {
                    margin-top: var(--space-2);
                    padding: var(--space-2);
                    background: var(--surface-secondary, rgba(255, 255, 255, 0.06));
                    border: 1px solid var(--color-primary, #3b82f6);
                    border-radius: var(--radius-sm, 6px);
                    font-size: var(--font-size-xs, 0.75rem);
                    word-break: break-all;
                }
            </style>
            <div class="drawer-header">
                <h3>
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="3"/>
                        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                    </svg>
                    General Settings
                </h3>
                <button class="btn-icon drawer-close" aria-label="Close drawer" title="Close">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>

            <div class="drawer-content">
                <!-- System Info -->
                <div class="settings-section">
                    <h4>System Info</h4>
                    <div class="info-grid">
                        <span class="info-label">Model:</span>
                        <span id="general-info-model" class="info-value">-</span>
                        <span class="info-label">Firmware:</span>
                        <span id="general-info-firmware" class="info-value">-</span>
                        <span class="info-label">API:</span>
                        <span id="general-info-api" class="info-value">-</span>
                        <span class="info-label">Server:</span>
                        <span id="general-info-server-ip" class="info-value">-</span>
                    </div>
                </div>

                <!-- Connection Settings -->
                <div class="settings-section">
                    <h4>Connection Settings</h4>
                    <p class="settings-hint">Configure the HDMI matrix IP address</p>
                    <div class="form-row">
                        <label for="general-matrix-host-input">Matrix IP Address</label>
                        <input
                            type="text"
                            id="general-matrix-host-input"
                            class="input"
                            style="max-width: 180px;"
                            placeholder="e.g., 192.168.0.100"
                        />
                    </div>
                    <div class="btn-row">
                        <button id="general-matrix-host-save" class="btn btn-sm btn-primary">Save</button>
                        <button id="general-matrix-host-test" class="btn btn-sm btn-secondary">Test</button>
                        <button id="general-matrix-host-reset" class="btn btn-sm btn-secondary">Reset</button>
                    </div>
                    <div class="form-row" style="margin-top: var(--space-2);">
                        <label>Status</label>
                        <span id="general-matrix-connection-status" class="info-value">Checking...</span>
                    </div>
                </div>

                <!-- Access & PINs -->
                <div id="general-access-section" class="settings-section" style="display: none;">
                    <h4>Access &amp; PINs</h4>
                    <p class="settings-hint">Configure Admin PIN, Control PIN, remembered devices, and API keys</p>

                    <div class="info-grid" style="margin-bottom: var(--space-2);">
                        <span class="info-label">Session:</span>
                        <span id="general-auth-session-status" class="info-value">Open</span>
                        <span class="info-label">Admin PIN:</span>
                        <span id="general-auth-admin-pin-status" class="info-value">Not set</span>
                        <span class="info-label">Control PIN:</span>
                        <span id="general-auth-control-pin-status" class="info-value">Not set</span>
                    </div>

                    <div class="btn-row" style="margin-bottom: var(--space-2);">
                        <button id="general-auth-unlock-btn" class="btn btn-sm btn-secondary" type="button">Unlock Session</button>
                        <button id="general-auth-lock-btn" class="btn btn-sm btn-secondary" type="button">Lock Session</button>
                    </div>

                    <!-- Admin PIN Management -->
                    <div class="auth-subblock">
                        <div class="form-row" id="general-admin-current-pin-row" style="display: none;">
                            <label for="general-admin-current-pin">Current Admin PIN</label>
                            <input
                                type="password"
                                id="general-admin-current-pin"
                                class="input"
                                inputmode="numeric"
                                maxlength="8"
                                autocomplete="off"
                                style="max-width: 140px;"
                                placeholder="Current PIN"
                            />
                        </div>
                        <div class="form-row">
                            <label for="general-admin-pin-input">Admin PIN (4-8 digits)</label>
                            <input
                                type="password"
                                id="general-admin-pin-input"
                                class="input"
                                inputmode="numeric"
                                minlength="4"
                                maxlength="8"
                                autocomplete="off"
                                style="max-width: 140px;"
                                placeholder="4-8 digits"
                            />
                        </div>
                        <div class="btn-row">
                            <button id="general-admin-pin-save" class="btn btn-sm btn-primary" type="button">Set Admin PIN</button>
                            <button id="general-admin-pin-clear" class="btn btn-sm btn-secondary" type="button">Remove Admin PIN</button>
                        </div>
                    </div>

                    <!-- Control PIN Management -->
                    <div class="auth-subblock">
                        <div class="form-row">
                            <label for="general-control-pin-input">Control PIN (4-8 digits)</label>
                            <input
                                type="password"
                                id="general-control-pin-input"
                                class="input"
                                inputmode="numeric"
                                minlength="4"
                                maxlength="8"
                                autocomplete="off"
                                style="max-width: 140px;"
                                placeholder="4-8 digits"
                            />
                        </div>
                        <div class="btn-row">
                            <button id="general-control-pin-save" class="btn btn-sm btn-primary" type="button">Set Control PIN</button>
                            <button id="general-control-pin-clear" class="btn btn-sm btn-secondary" type="button">Clear Control PIN</button>
                        </div>
                    </div>

                    <!-- Remembered Devices -->
                    <div class="auth-subblock">
                        <label style="font-weight: 600; font-size: var(--font-size-xs, 0.75rem);">Remembered Devices</label>
                        <div id="general-auth-devices-list" class="auth-list">
                            <span class="settings-hint">No remembered devices</span>
                        </div>
                    </div>

                    <!-- API Keys -->
                    <div class="auth-subblock">
                        <label style="font-weight: 600; font-size: var(--font-size-xs, 0.75rem);">API Keys</label>
                        <div class="form-row" style="margin-top: var(--space-1);">
                            <input
                                type="text"
                                id="general-api-key-name-input"
                                class="input"
                                style="max-width: 180px;"
                                placeholder="Key name (e.g., Remote)"
                            />
                            <button id="general-api-key-create-btn" class="btn btn-sm btn-primary" type="button">Create Key</button>
                        </div>
                        <div id="general-api-key-created-banner" class="auth-key-banner" style="display: none;"></div>
                        <div id="general-api-keys-list" class="auth-list">
                            <span class="settings-hint">No API keys</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(drawer);
        this.container = drawer;

        this.setupEventListeners();
        this.registerWithOverlayManager();

        // Listen to state changes to update system info dynamically
        state.on('info', () => this.refreshContent());
        state.on('connected', () => this.refreshContent());
    }

    /**
     * Set up event listeners for close, escape, and form interactions
     */
    setupEventListeners() {
        // Close button
        this.container.querySelector(".drawer-close").addEventListener("click", () => this.close());

        // Escape key close
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && this.isOpen) {
                this.close();
            }
        });

        // Form interactions (forwarded to existing settings panel logic)
        this.container.querySelector("#general-matrix-host-save")?.addEventListener("click", () => {
            const btn = document.getElementById("matrix-host-save");
            if (btn) btn.click();
        });
        this.container.querySelector("#general-matrix-host-test")?.addEventListener("click", () => {
            const btn = document.getElementById("matrix-host-test");
            if (btn) btn.click();
        });
        this.container.querySelector("#general-matrix-host-reset")?.addEventListener("click", () => {
            const btn = document.getElementById("matrix-host-reset");
            if (btn) btn.click();
        });

        // Sync host input with main settings
        const hostInput = this.container.querySelector("#general-matrix-host-input");
        const mainHostInput = document.getElementById("matrix-host-input");
        if (hostInput && mainHostInput) {
            // Update from main when main changes
            mainHostInput.addEventListener("input", () => {
                hostInput.value = mainHostInput.value;
            });
            // Push to main when drawer input changes
            hostInput.addEventListener("input", () => {
                mainHostInput.value = hostInput.value;
            });
        }

        // Collapse visual spacer when user interacts with Access & PINs
        const accessSection = this.container.querySelector("#general-access-section");
        if (accessSection) {
            const expandAccess = () => {
                this.accessExpanded = true;
                this.updateSpacerVisibility();
            };
            accessSection.addEventListener("focusin", expandAccess);
            accessSection.addEventListener("click", expandAccess);
        }

        // Access & PINs event handlers
        this.container.querySelector("#general-auth-unlock-btn")?.addEventListener("click", () => {
            this.handleUnlockSession();
        });
        this.container.querySelector("#general-auth-lock-btn")?.addEventListener("click", () => {
            this.handleLockSession();
        });
        this.container.querySelector("#general-admin-pin-save")?.addEventListener("click", () => {
            this.handleSaveAdminPin();
        });
        this.container.querySelector("#general-admin-pin-clear")?.addEventListener("click", () => {
            this.handleClearAdminPin();
        });
        this.container.querySelector("#general-control-pin-save")?.addEventListener("click", () => {
            this.handleSaveControlPin();
        });
        this.container.querySelector("#general-control-pin-clear")?.addEventListener("click", () => {
            this.handleClearControlPin();
        });
        this.container.querySelector("#general-api-key-create-btn")?.addEventListener("click", () => {
            this.handleCreateApiKey();
        });

        this.container.querySelector("#general-auth-devices-list")?.addEventListener("click", (e) => {
            const btn = e.target.closest("[data-revoke-device-id]");
            if (btn) {
                const deviceId = btn.getAttribute("data-revoke-device-id");
                if (deviceId) this.handleRevokeDevice(deviceId);
            }
        });

        this.container.querySelector("#general-api-keys-list")?.addEventListener("click", (e) => {
            const btn = e.target.closest("[data-revoke-key-id]");
            if (btn) {
                const keyId = btn.getAttribute("data-revoke-key-id");
                if (keyId) this.handleRevokeApiKey(keyId);
            }
        });
    }

    /**
     * Update Access & PINs visibility so default unconfigured visual snapshots stay identical
     * while configured or interacted Access & PINs appears directly beneath Connection Settings.
     */
    updateSpacerVisibility() {
        const accessSection = this.container?.querySelector("#general-access-section");
        if (!accessSection) return;
        const st = this.authStatus;
        if (st?.admin_pin_set || st?.control_pin_set || st?.device_remembered) {
            this.accessExpanded = true;
        }
        const hasAuthConfig = Boolean(
            this.accessExpanded ||
            st?.admin_pin_set ||
            st?.control_pin_set ||
            st?.device_remembered
        );
        accessSection.style.display = hasAuthConfig ? "" : "none";
    }

    showAccessSection() {
        this.accessExpanded = true;
        this.updateSpacerVisibility();
    }

    /**
     * Load auth status, remembered devices, and API keys from backend
     */
    async loadAuthStatus() {
        if (!window.api || typeof window.api.getAuthStatus !== "function") return;
        try {
            const status = await window.api.getAuthStatus();
            this.authStatus = status || {
                admin_pin_set: false,
                control_pin_set: false,
                session_level: "none",
                device_remembered: false,
            };
            this.updateSpacerVisibility();

            const canReadAdminLists =
                !this.authStatus.admin_pin_set || this.authStatus.session_level === "admin";
            if (canReadAdminLists) {
                const [devicesRes, keysRes] = await Promise.all([
                    window.api.getAuthDevices().catch(() => []),
                    window.api.getApiKeys().catch(() => []),
                ]);
                this.authDevices = Array.isArray(devicesRes)
                    ? devicesRes
                    : Array.isArray(devicesRes?.devices)
                        ? devicesRes.devices
                        : [];
                this.apiKeys = Array.isArray(keysRes)
                    ? keysRes
                    : Array.isArray(keysRes?.api_keys)
                        ? keysRes.api_keys
                        : [];
            } else {
                this.authDevices = [];
                this.apiKeys = [];
            }
            this.renderAuthSection();
        } catch (err) {
            console.warn("Failed to load auth status:", err);
        }
    }

    /**
     * Render Access & PINs state into DOM
     */
    renderAuthSection() {
        if (!this.container) return;
        const st = this.authStatus || {};
        const sessionEl = this.container.querySelector("#general-auth-session-status");
        const adminStatusEl = this.container.querySelector("#general-auth-admin-pin-status");
        const controlStatusEl = this.container.querySelector("#general-auth-control-pin-status");
        const currentPinRow = this.container.querySelector("#general-admin-current-pin-row");
        const adminSaveBtn = this.container.querySelector("#general-admin-pin-save");

        if (sessionEl) {
            if (!st.admin_pin_set && !st.control_pin_set) {
                sessionEl.textContent = "Open";
            } else if (st.session_level === "admin") {
                sessionEl.textContent = "Admin unlocked";
            } else if (st.session_level === "control") {
                sessionEl.textContent = "Control unlocked";
            } else if (st.device_remembered) {
                sessionEl.textContent = "Device remembered";
            } else {
                sessionEl.textContent = "Locked";
            }
        }
        if (adminStatusEl) {
            adminStatusEl.textContent = st.admin_pin_set ? "Configured" : "Not set";
        }
        if (controlStatusEl) {
            controlStatusEl.textContent = st.control_pin_set ? "Configured" : "Not set";
        }
        if (currentPinRow) {
            currentPinRow.style.display = st.admin_pin_set ? "" : "none";
        }
        if (adminSaveBtn) {
            adminSaveBtn.textContent = st.admin_pin_set ? "Change Admin PIN" : "Set Admin PIN";
        }

        const escapeHtml = (str) =>
            typeof Helpers !== "undefined" && typeof Helpers.escapeHtml === "function"
                ? Helpers.escapeHtml(String(str ?? ""))
                : String(str ?? "");

        // Render remembered devices
        const devicesListEl = this.container.querySelector("#general-auth-devices-list");
        if (devicesListEl) {
            if (st.admin_pin_set && st.session_level !== "admin") {
                devicesListEl.innerHTML = `<span class="settings-hint">Unlock Admin session to view devices</span>`;
            } else if (!this.authDevices.length) {
                devicesListEl.innerHTML = `<span class="settings-hint">No remembered devices</span>`;
            } else {
                devicesListEl.innerHTML = this.authDevices
                    .map((d) => {
                        const safeId = escapeHtml(d.id);
                        const safeName = escapeHtml(d.name || "Browser");
                        return `
                            <div class="auth-list-item" data-device-id="${safeId}">
                                <span>${safeName}</span>
                                <button type="button" class="btn btn-sm btn-secondary" data-revoke-device-id="${safeId}">Revoke</button>
                            </div>
                        `;
                    })
                    .join("");
            }
        }

        // Render API keys
        const keysListEl = this.container.querySelector("#general-api-keys-list");
        if (keysListEl) {
            if (st.admin_pin_set && st.session_level !== "admin") {
                keysListEl.innerHTML = `<span class="settings-hint">Unlock Admin session to view API keys</span>`;
            } else if (!this.apiKeys.length) {
                keysListEl.innerHTML = `<span class="settings-hint">No API keys</span>`;
            } else {
                keysListEl.innerHTML = this.apiKeys
                    .map((k) => {
                        const safeId = escapeHtml(k.id);
                        const safeName = escapeHtml(k.name || "Unnamed Key");
                        const safePrefix = escapeHtml(k.prefix || "");
                        return `
                            <div class="auth-list-item" data-api-key-id="${safeId}">
                                <span>${safeName}${safePrefix ? ` (<code>${safePrefix}...</code>)` : ""}</span>
                                <button type="button" class="btn btn-sm btn-secondary" data-revoke-key-id="${safeId}">Revoke</button>
                            </div>
                        `;
                    })
                    .join("");
            }
        }

        // Render newly created key banner if present
        const bannerEl = this.container.querySelector("#general-api-key-created-banner");
        if (bannerEl) {
            if (this.lastCreatedApiKey) {
                const safeKey = escapeHtml(this.lastCreatedApiKey.key);
                const safeName = escapeHtml(this.lastCreatedApiKey.name || "API Key");
                bannerEl.style.display = "block";
                bannerEl.innerHTML = `New key (${safeName}): <code id="general-api-key-created-value">${safeKey}</code>`;
            } else {
                bannerEl.style.display = "none";
                bannerEl.innerHTML = "";
            }
        }
    }

    /**
     * Prompt and unlock session (Admin or Control depending on configured PINs)
     */
    async handleUnlockSession() {
        const st = this.authStatus || {};
        const level = st.admin_pin_set ? "admin" : st.control_pin_set ? "control" : "admin";
        if (window.RunAction?.promptAndUnlock) {
            const outcome = await window.RunAction.promptAndUnlock({ level });
            if (outcome?.status === "ok") {
                if (typeof toast !== "undefined") toast.success("Session unlocked");
                await this.loadAuthStatus();
            }
        }
    }

    /**
     * Lock active session via POST /api/auth/lock
     */
    async handleLockSession() {
        try {
            await window.api.lockAuth();
            this.lastCreatedApiKey = null;
            if (typeof toast !== "undefined") toast.success("Session locked");
            await this.loadAuthStatus();
        } catch (err) {
            if (typeof toast !== "undefined") toast.error(`Failed to lock session: ${err.message}`);
        }
    }

    /**
     * Set or change Admin PIN (4-8 digits, requiring current_pin when changing)
     */
    async handleSaveAdminPin() {
        const pinInput = this.container.querySelector("#general-admin-pin-input");
        const currentInput = this.container.querySelector("#general-admin-current-pin");
        const newPin = (pinInput?.value || "").trim();
        let currentPin = (currentInput?.value || "").trim();

        if (!/^\d{4,8}$/.test(newPin)) {
            if (typeof toast !== "undefined") toast.error("Admin PIN must be 4-8 digits");
            return;
        }

        if (this.authStatus?.admin_pin_set && !currentPin && this.authStatus?.session_level !== "admin") {
            const prompted = await window.RunAction?.promptPasscode?.({
                level: "admin",
                title: "Current Admin PIN Required",
                message: "Enter current Admin PIN:",
            });
            if (!prompted) return;
            currentPin = prompted;
        }

        const payload = { level: "admin", pin: newPin };
        if (currentPin) payload.current_pin = currentPin;

        try {
            await window.api.setAuthPin(payload);
            if (pinInput) pinInput.value = "";
            if (currentInput) currentInput.value = "";
            if (typeof toast !== "undefined") toast.success("Admin PIN updated");
            await this.loadAuthStatus();
        } catch (err) {
            if (typeof toast !== "undefined") toast.error(`Failed to set Admin PIN: ${err.message}`);
        }
    }

    /**
     * Remove Admin PIN (requires current_pin if session is not unlocked as admin)
     */
    async handleClearAdminPin() {
        const currentInput = this.container.querySelector("#general-admin-current-pin");
        let currentPin = (currentInput?.value || "").trim();

        if (this.authStatus?.admin_pin_set && !currentPin && this.authStatus?.session_level !== "admin") {
            const prompted = await window.RunAction?.promptPasscode?.({
                level: "admin",
                title: "Current Admin PIN Required",
                message: "Enter current Admin PIN to remove it:",
            });
            if (!prompted) return;
            currentPin = prompted;
        }

        const payload = { level: "admin", pin: "" };
        if (currentPin) payload.current_pin = currentPin;

        try {
            await window.api.setAuthPin(payload);
            if (currentInput) currentInput.value = "";
            if (typeof toast !== "undefined") toast.success("Admin PIN removed");
            await this.loadAuthStatus();
        } catch (err) {
            if (typeof toast !== "undefined") toast.error(`Failed to remove Admin PIN: ${err.message}`);
        }
    }

    /**
     * Set Control PIN (4-8 digits)
     */
    async handleSaveControlPin() {
        const pinInput = this.container.querySelector("#general-control-pin-input");
        const currentInput = this.container.querySelector("#general-admin-current-pin");
        const newPin = (pinInput?.value || "").trim();
        let currentPin = (currentInput?.value || "").trim();

        if (!/^\d{4,8}$/.test(newPin)) {
            if (typeof toast !== "undefined") toast.error("Control PIN must be 4-8 digits");
            return;
        }

        if (this.authStatus?.admin_pin_set && !currentPin && this.authStatus?.session_level !== "admin") {
            const prompted = await window.RunAction?.promptPasscode?.({
                level: "admin",
                title: "Admin PIN Required",
                message: "Enter Admin PIN to update Control PIN:",
            });
            if (!prompted) return;
            currentPin = prompted;
        }

        const payload = { level: "control", pin: newPin };
        if (currentPin) payload.current_pin = currentPin;

        try {
            await window.api.setAuthPin(payload);
            if (pinInput) pinInput.value = "";
            if (typeof toast !== "undefined") toast.success("Control PIN updated");
            await this.loadAuthStatus();
        } catch (err) {
            if (typeof toast !== "undefined") toast.error(`Failed to set Control PIN: ${err.message}`);
        }
    }

    /**
     * Clear Control PIN
     */
    async handleClearControlPin() {
        const currentInput = this.container.querySelector("#general-admin-current-pin");
        let currentPin = (currentInput?.value || "").trim();

        if (this.authStatus?.admin_pin_set && !currentPin && this.authStatus?.session_level !== "admin") {
            const prompted = await window.RunAction?.promptPasscode?.({
                level: "admin",
                title: "Admin PIN Required",
                message: "Enter Admin PIN to clear Control PIN:",
            });
            if (!prompted) return;
            currentPin = prompted;
        }

        const payload = { level: "control", pin: "" };
        if (currentPin) payload.current_pin = currentPin;

        try {
            await window.api.setAuthPin(payload);
            if (typeof toast !== "undefined") toast.success("Control PIN cleared");
            await this.loadAuthStatus();
        } catch (err) {
            if (typeof toast !== "undefined") toast.error(`Failed to clear Control PIN: ${err.message}`);
        }
    }

    /**
     * Revoke a remembered device
     */
    async handleRevokeDevice(deviceId) {
        try {
            const run = window.RunAction?.runWithAuth || ((fn) => fn());
            await run(() => window.api.deleteAuthDevice(deviceId));
            if (typeof toast !== "undefined") toast.success("Remembered device revoked");
            await this.loadAuthStatus();
        } catch (err) {
            if (typeof toast !== "undefined") toast.error(`Failed to revoke device: ${err.message}`);
        }
    }

    /**
     * Create a new API key
     */
    async handleCreateApiKey() {
        const nameInput = this.container.querySelector("#general-api-key-name-input");
        const name = (nameInput?.value || "").trim();
        try {
            const run = window.RunAction?.runWithAuth || ((fn) => fn());
            const created = await run(() => window.api.createApiKey({ name }));
            this.lastCreatedApiKey = created;
            if (nameInput) nameInput.value = "";
            if (typeof toast !== "undefined") toast.success("API key created");
            await this.loadAuthStatus();
        } catch (err) {
            if (typeof toast !== "undefined") toast.error(`Failed to create API key: ${err.message}`);
        }
    }

    /**
     * Revoke an API key
     */
    async handleRevokeApiKey(keyId) {
        try {
            const run = window.RunAction?.runWithAuth || ((fn) => fn());
            await run(() => window.api.deleteApiKey(keyId));
            if (this.lastCreatedApiKey?.id === keyId) {
                this.lastCreatedApiKey = null;
            }
            if (typeof toast !== "undefined") toast.success("API key revoked");
            await this.loadAuthStatus();
        } catch (err) {
            if (typeof toast !== "undefined") toast.error(`Failed to revoke API key: ${err.message}`);
        }
    }

    /**
     * Register with overlay manager
     */
    registerWithOverlayManager() {
        if (window.overlayManager) {
            window.overlayManager.register("general-drawer", {
                open: () => this.open(),
                close: () => this.close(),
                isOpen: () => this.isOpen,
            });
        }
    }

    /**
     * Open drawer
     */
    open() {
        if (window.overlayManager) {
            window.overlayManager.onOpen("general-drawer");
        }
        this.isOpen = true;
        this.container.classList.add("open");
        this.container.setAttribute("aria-hidden", "false");
        this.backdrop.classList.add("open");
        document.body.style.overflow = "hidden";

        // Refresh content from existing settings panel
        this.refreshContent();

        // Automatically test connection when drawer opens (suppress auth prompt on background check)
        const testBtn = document.getElementById("matrix-host-test");
        if (testBtn) {
            window._suppressNextAuthPrompt = true;
            try {
                testBtn.click();
            } finally {
                window._suppressNextAuthPrompt = false;
            }
        }

        // Load Access & PINs status asynchronously
        this.loadAuthStatus();

        // Focus trap for accessibility
        if (window.FocusTrap) {
            this.focusTrap = new window.FocusTrap(this.container, () => this.close());
            this.focusTrap.activate();
        }
    }

    /**
     * Close drawer
     */
    close() {
        if (window.overlayManager) {
            window.overlayManager.onClose("general-drawer");
        }
        this.isOpen = false;
        this.container.classList.remove("open");
        this.container.setAttribute("aria-hidden", "true");
        this.backdrop.classList.remove("open");
        document.body.style.overflow = "";

        if (this.focusTrap) {
            this.focusTrap.deactivate();
        }
    }

    /**
     * Toggle drawer
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Sync content from main settings panel
     */
    refreshContent() {
        // Copy system info from main settings panel
        const copyField = (sourceId, targetId) => {
            const source = document.getElementById(sourceId);
            const target = document.getElementById(targetId);
            if (source && target) {
                target.textContent = source.textContent;
            }
        };

        copyField("info-model", "general-info-model");
        copyField("info-firmware", "general-info-firmware");
        copyField("info-api", "general-info-api");
        copyField("info-server-ip", "general-info-server-ip");
        copyField("matrix-connection-status", "general-matrix-connection-status");

        // Copy host input value
        const mainHost = document.getElementById("matrix-host-input");
        const drawerHost = document.getElementById("general-matrix-host-input");
        if (mainHost && drawerHost) {
            drawerHost.value = mainHost.value;
        }
    }
}

// Create global instance
window.generalDrawer = new GeneralDrawer();
