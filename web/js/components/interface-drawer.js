/**
 * OREI Matrix Control - Interface Settings Drawer
 *
 * Slide-out drawer containing Interface settings:
 * - CEC Remote Tray position
 * - Visual Effects (Tron animation, glow reduction)
 * - Developer Tools (debug panel)
 * - Kiosk Mode link
 */

class InterfaceDrawer {
    constructor() {
        this.isOpen = false;
        this.container = null;
        this.backdrop = null;

        this.createDrawer();
        this.registerWithOverlayManager();
    }

    /**
     * Create drawer and backdrop in DOM
     */
    createDrawer() {
        // Backdrop overlay
        const backdrop = document.createElement("div");
        backdrop.id = "interface-drawer-backdrop";
        backdrop.className = "settings-drawer-backdrop";
        backdrop.addEventListener("click", () => this.close());
        document.body.appendChild(backdrop);
        this.backdrop = backdrop;

        // Drawer container
        const drawer = document.createElement("aside");
        drawer.id = "interface-drawer";
        drawer.className = "settings-drawer interface-drawer";
        drawer.setAttribute("aria-hidden", "true");
        drawer.setAttribute("role", "dialog");
        drawer.setAttribute("aria-label", "Interface Settings");
        drawer.innerHTML = `
            <div class="drawer-header">
                <h3>
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                        <line x1="8" y1="21" x2="16" y2="21"/>
                        <line x1="12" y1="17" x2="12" y2="21"/>
                    </svg>
                    Interface Settings
                </h3>
                <button class="btn-icon drawer-close" aria-label="Close drawer" title="Close">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>

            <div class="drawer-content">
                <!-- CEC Remote Tray -->
                <div class="settings-section">
                    <h4>CEC Remote Tray</h4>
                    <div class="form-row">
                        <label for="interface-cec-tray-position">Tray Position</label>
                        <select id="interface-cec-tray-position" class="select">
                            <option value="bottom-right">Bottom Right</option>
                            <option value="bottom-left">Bottom Left</option>
                            <option value="top-right">Top Right</option>
                        </select>
                    </div>
                </div>

                <!-- Visual Effects -->
                <div class="settings-section">
                    <h4>Visual Effects</h4>
                    <p class="settings-hint">
                        TRON-inspired light cycle animation in the background
                    </p>
                    <div class="form-row">
                        <label for="interface-tron-animation-toggle">Light Cycle Animation</label>
                        <label class="toggle">
                            <input type="checkbox" id="interface-tron-animation-toggle" checked />
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    <div class="form-row">
                        <label for="interface-reduce-glow-toggle">Reduce UI Glow</label>
                        <label class="toggle">
                            <input type="checkbox" id="interface-reduce-glow-toggle" />
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>

                <!-- Developer Tools -->
                <div class="settings-section">
                    <h4>Developer Tools</h4>
                    <p class="settings-hint">
                        Debug panel: single 3-finger tap on mobile
                    </p>
                    <div class="form-row">
                        <label for="interface-debug-fab-toggle">Show Debug Panel</label>
                        <label class="toggle">
                            <input type="checkbox" id="interface-debug-fab-toggle" />
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>

                <!-- Kiosk Mode -->
                <div class="settings-section">
                    <h4>Kiosk Mode</h4>
                    <p class="settings-hint">
                        Simplified tablet UI for quick input switching. Double 2-finger
                        tap to enter/exit.
                    </p>
                    <div class="form-row">
                        <label>Open Kiosk Interface</label>
                        <a href="/kiosk" class="btn btn-secondary btn-sm">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                                <line x1="8" y1="21" x2="16" y2="21"/>
                                <line x1="12" y1="17" x2="12" y2="21"/>
                            </svg>
                            <span>Open</span>
                        </a>
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
     * Set up event listeners
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
        this.container.querySelector("#interface-cec-tray-position")?.addEventListener("change", (e) => {
            const main = document.getElementById("cec-tray-position");
            if (main) {
                main.value = e.target.value;
                main.dispatchEvent(new Event("change"));
            }
        });

        this.container.querySelector("#interface-tron-animation-toggle")?.addEventListener("change", (e) => {
            const main = document.getElementById("tron-animation-toggle");
            if (main) {
                main.checked = e.target.checked;
                main.dispatchEvent(new Event("change"));
            }
        });

        this.container.querySelector("#interface-reduce-glow-toggle")?.addEventListener("change", (e) => {
            const main = document.getElementById("reduce-glow-toggle");
            if (main) {
                main.checked = e.target.checked;
                main.dispatchEvent(new Event("change"));
            }
        });

        this.container.querySelector("#interface-debug-fab-toggle")?.addEventListener("change", (e) => {
            const main = document.getElementById("debug-fab-toggle");
            if (main) {
                main.checked = e.target.checked;
                main.dispatchEvent(new Event("change"));
            }
        });
    }

    /**
     * Register with overlay manager
     */
    registerWithOverlayManager() {
        if (window.overlayManager) {
            window.overlayManager.register("interface-drawer", {
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
            window.overlayManager.onOpen("interface-drawer");
        }
        this.isOpen = true;
        this.container.classList.add("open");
        this.container.setAttribute("aria-hidden", "false");
        this.backdrop.classList.add("open");
        document.body.style.overflow = "hidden";

        this.refreshContent();

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
            window.overlayManager.onClose("interface-drawer");
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
        const syncValue = (sourceId, targetId) => {
            const source = document.getElementById(sourceId);
            const target = document.getElementById(targetId);
            if (source && target) {
                target.value = source.value;
            }
        };

        const syncChecked = (sourceId, targetId) => {
            const source = document.getElementById(sourceId);
            const target = document.getElementById(targetId);
            if (source && target) {
                target.checked = source.checked;
            }
        };

        syncValue("cec-tray-position", "interface-cec-tray-position");
        syncChecked("tron-animation-toggle", "interface-tron-animation-toggle");
        syncChecked("reduce-glow-toggle", "interface-reduce-glow-toggle");
        syncChecked("debug-fab-toggle", "interface-debug-fab-toggle");
    }
}

// Create global instance
window.interfaceDrawer = new InterfaceDrawer();
