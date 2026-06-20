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

        this.createDrawer();
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

                <div class="drawer-spacer"></div>
            </div>
        `;
        document.body.appendChild(drawer);
        this.container = drawer;

        this.setupEventListeners();
        this.registerWithOverlayManager();
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
