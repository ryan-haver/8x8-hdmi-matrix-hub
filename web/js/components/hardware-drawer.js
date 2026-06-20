/**
 * OREI Matrix Control - Hardware Settings Drawer
 *
 * Slide-out drawer containing Hardware settings:
 * - Display Settings (LCD timeout, system beep)
 * - External Audio (audio mode)
 * - Power Controls (power cycle, reboot)
 */

class HardwareDrawer {
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
        backdrop.id = "hardware-drawer-backdrop";
        backdrop.className = "settings-drawer-backdrop";
        backdrop.addEventListener("click", () => this.close());
        document.body.appendChild(backdrop);
        this.backdrop = backdrop;

        // Drawer container
        const drawer = document.createElement("aside");
        drawer.id = "hardware-drawer";
        drawer.className = "settings-drawer hardware-drawer";
        drawer.setAttribute("aria-hidden", "true");
        drawer.setAttribute("role", "dialog");
        drawer.setAttribute("aria-label", "Hardware Settings");
        drawer.innerHTML = `
            <div class="drawer-header">
                <h3>
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="4" y="4" width="16" height="16" rx="2"/>
                        <rect x="9" y="9" width="6" height="6"/>
                        <line x1="9" y1="1" x2="9" y2="4"/>
                        <line x1="15" y1="1" x2="15" y2="4"/>
                        <line x1="9" y1="20" x2="9" y2="23"/>
                        <line x1="15" y1="20" x2="15" y2="23"/>
                        <line x1="20" y1="9" x2="23" y2="9"/>
                        <line x1="20" y1="14" x2="23" y2="14"/>
                        <line x1="1" y1="9" x2="4" y2="9"/>
                        <line x1="1" y1="14" x2="4" y2="14"/>
                    </svg>
                    Hardware Settings
                </h3>
                <button class="btn-icon drawer-close" aria-label="Close drawer" title="Close">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>

            <div class="drawer-content">
                <!-- Display Settings -->
                <div class="settings-section">
                    <h4>Display Settings</h4>
                    <div class="form-row">
                        <label for="hardware-lcd-timeout">LCD Timeout</label>
                        <select id="hardware-lcd-timeout" class="select">
                            <option value="0">Off</option>
                            <option value="1">Always On</option>
                            <option value="2">15 seconds</option>
                            <option value="3">30 seconds</option>
                            <option value="4" selected>60 seconds</option>
                        </select>
                    </div>
                    <div class="form-row">
                        <label for="hardware-beep-enabled">System Beep</label>
                        <label class="toggle">
                            <input type="checkbox" id="hardware-beep-enabled" checked />
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                </div>

                <!-- External Audio -->
                <div class="settings-section">
                    <h4>External Audio</h4>
                    <div class="form-row">
                        <label for="hardware-ext-audio-mode">Audio Mode</label>
                        <select id="hardware-ext-audio-mode" class="select">
                            <option value="0">Follow Video</option>
                            <option value="1">Independent</option>
                            <option value="2">Mixer</option>
                        </select>
                    </div>
                </div>

                <!-- Power Controls -->
                <div class="settings-section">
                    <h4>Power Controls</h4>
                    <p class="settings-hint">System power cycles or hard reboots</p>
                    <div class="btn-row">
                        <button id="hardware-power-cycle-btn" class="btn btn-warning">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M23 4v6h-6M1 20v-6h6"/>
                                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                            </svg>
                            <span>Power Cycle</span>
                        </button>
                        <button id="hardware-reboot-btn" class="btn btn-danger">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18.36 6.64a9 9 0 1 1-12.73 0"/>
                                <line x1="12" y1="2" x2="12" y2="12"/>
                            </svg>
                            <span>Reboot</span>
                        </button>
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
        this.container.querySelector("#hardware-lcd-timeout")?.addEventListener("change", (e) => {
            const main = document.getElementById("lcd-timeout");
            if (main) {
                main.value = e.target.value;
                main.dispatchEvent(new Event("change"));
            }
        });

        this.container.querySelector("#hardware-beep-enabled")?.addEventListener("change", (e) => {
            const main = document.getElementById("beep-enabled");
            if (main) {
                main.checked = e.target.checked;
                main.dispatchEvent(new Event("change"));
            }
        });

        this.container.querySelector("#hardware-ext-audio-mode")?.addEventListener("change", (e) => {
            const main = document.getElementById("ext-audio-mode");
            if (main) {
                main.value = e.target.value;
                main.dispatchEvent(new Event("change"));
            }
        });

        this.container.querySelector("#hardware-power-cycle-btn")?.addEventListener("click", () => {
            const btn = document.getElementById("power-cycle-btn");
            if (btn) btn.click();
        });

        this.container.querySelector("#hardware-reboot-btn")?.addEventListener("click", () => {
            const btn = document.getElementById("reboot-btn");
            if (btn) btn.click();
        });
    }

    /**
     * Register with overlay manager
     */
    registerWithOverlayManager() {
        if (window.overlayManager) {
            window.overlayManager.register("hardware-drawer", {
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
            window.overlayManager.onOpen("hardware-drawer");
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
            window.overlayManager.onClose("hardware-drawer");
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

        syncValue("lcd-timeout", "hardware-lcd-timeout");
        syncChecked("beep-enabled", "hardware-beep-enabled");
        syncValue("ext-audio-mode", "hardware-ext-audio-mode");
    }
}

// Create global instance
window.hardwareDrawer = new HardwareDrawer();
