/**
 * OREI Matrix Control - Side Navigation Drawer Component
 * Handles the slide-out hamburger menu drawer, collapsed utility buttons,
 * and interface customization settings (tab pinning and re-ordering) with backend persistence.
 */

class SideNavDrawer {
    constructor() {
        this.isOpen = false;
        this.container = null;
        this.backdrop = null;
        
        // Default UI preference fallback
        this.preferences = {
            pinnedTabs: ["matrix", "dashboard", "inputs", "outputs", "profiles"],
            tabOrder: ["matrix", "dashboard", "inputs", "outputs", "profiles"]
        };

        // Create DOM nodes immediately
        this.createDrawer();
    }

    /**
     * Initialize the component by fetching preferences from the backend
     */
    async init() {
        try {
            const response = await api.getUiPreferences();
            if (response && response.success && response.data) {
                this.preferences = response.data;
            }
        } catch (e) {
            console.warn("Failed to load persistent UI preferences from server, using default.", e);
        }

        this.setupEventListeners();
        this.render();
    }

    /**
     * Get list of all available tab specifications
     */
    getTabSpecs() {
        return [
            { id: "dashboard", name: "Dashboard", icon: `<rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>` },
            { id: "matrix", name: "Matrix Routing", icon: `<rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="3" y1="15" x2="21" y2="15"/><circle cx="9" cy="9" r="1.5" fill="currentColor"/><circle cx="15" cy="15" r="1.5" fill="currentColor"/><circle cx="15" cy="9" r="1.5" fill="currentColor"/>` },
            { id: "inputs", name: "Inputs status", icon: `<rect x="2" y="5" width="20" height="14" rx="2"/><polygon points="10 9 15 12 10 15" fill="currentColor"/>` },
            { id: "outputs", name: "Outputs status", icon: `<rect x="2" y="3" width="20" height="13" rx="2"/><path d="M9 20h6M12 16v4"/>` },
            { id: "profiles", name: "Profiles settings", icon: `<line x1="4" y1="21" x2="4" y2="14" stroke-linecap="round" stroke-linejoin="round"/><line x1="4" y1="10" x2="4" y2="3" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="21" x2="12" y2="12" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="8" x2="12" y2="3" stroke-linecap="round" stroke-linejoin="round"/><line x1="20" y1="21" x2="20" y2="16" stroke-linecap="round" stroke-linejoin="round"/><line x1="20" y1="12" x2="20" y2="3" stroke-linecap="round" stroke-linejoin="round"/><line x1="1" y1="14" x2="7" y2="14" stroke-linecap="round" stroke-linejoin="round"/><line x1="9" y1="8" x2="15" y2="8" stroke-linecap="round" stroke-linejoin="round"/><line x1="17" y1="16" x2="23" y2="16" stroke-linecap="round" stroke-linejoin="round"/>` }
        ];
    }

    /**
     * Create side drawer and backdrop in DOM
     */
    createDrawer() {
        // Backdrop overlay
        const backdrop = document.createElement("div");
        backdrop.id = "side-nav-backdrop";
        backdrop.className = "side-nav-backdrop";
        backdrop.addEventListener("click", () => {
            if (window.overlayManager) {
                window.overlayManager.closeAll();
            } else {
                this.close();
            }
        });
        document.body.appendChild(backdrop);
        
        // Sidebar Aside
        const drawer = document.createElement("aside");
        drawer.id = "side-nav-drawer";
        drawer.className = "side-nav-drawer";
        drawer.innerHTML = `
            <div class="drawer-header">
                <h3>
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 12h18M3 6h18M3 18h18"/>
                    </svg>
                    Control Deck
                </h3>
                <button class="btn-icon drawer-close" aria-label="Close drawer" title="Close menu">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
            
            <div class="drawer-content">
                <!-- Collapsed utility buttons section -->
                <div class="drawer-section">
                    <h4 class="drawer-section-title">Quick Utilities</h4>
                    <div class="drawer-utilities-grid">
                        <button id="drawer-routing-btn" class="utility-btn" title="Route to All">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M3 8h15M3 16h15M8 3v18M16 3v18"/><circle cx="8" cy="8" r="2" fill="currentColor"/><circle cx="16" cy="16" r="2" fill="currentColor"/><path d="M18 10l3 3-3 3"/>
                            </svg>
                            <span>Route to All</span>
                        </button>
                        
                        <button id="drawer-theme-btn" class="utility-btn" title="Theme Settings">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="13.5" cy="6.5" r="0.5" fill="currentColor"/>
                                <circle cx="17.5" cy="10.5" r="0.5" fill="currentColor"/>
                                <circle cx="8.5" cy="7.5" r="0.5" fill="currentColor"/>
                                <circle cx="6.5" cy="12.5" r="0.5" fill="currentColor"/>
                                <path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.555C21.965 6.012 17.461 2 12 2z"/>
                            </svg>
                            <span>Theme Style</span>
                        </button>
                        
                        <button id="drawer-refresh-btn" class="utility-btn" title="Refresh Status">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M23 4v6h-6M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
                            </svg>
                            <span>Refresh Status</span>
                        </button>
                    </div>
                </div>

                <!-- Settings sections (split into 3 drawers) -->
                <div class="drawer-section">
                    <h4 class="drawer-section-title">Settings</h4>
                    <div class="drawer-utilities-grid">
                        <button id="drawer-general-btn" class="utility-btn" title="General Settings">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="3"/>
                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                            </svg>
                            <span>General</span>
                        </button>

                        <button id="drawer-hardware-btn" class="utility-btn" title="Hardware Settings">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="4" y="4" width="16" height="16" rx="2"/>
                                <rect x="9" y="9" width="6" height="6"/>
                                <line x1="9" y1="1" x2="9" y2="4"/>
                                <line x1="15" y1="1" x2="15" y2="4"/>
                                <line x1="9" y1="20" x2="9" y2="23"/>
                                <line x1="15" y1="20" x2="15" y2="23"/>
                            </svg>
                            <span>Hardware</span>
                        </button>

                        <button id="drawer-interface-btn" class="utility-btn" title="Interface Settings">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                                <line x1="8" y1="21" x2="16" y2="21"/>
                                <line x1="12" y1="17" x2="12" y2="21"/>
                            </svg>
                            <span>Interface</span>
                        </button>

                        <button id="drawer-shortcuts-btn" class="utility-btn" title="System Shortcuts">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                            </svg>
                            <span>Shortcuts</span>
                        </button>
                    </div>
                </div>
                
                <!-- Interface configuration section (pinning, re-ordering) -->
                <div class="drawer-section">
                    <h4 class="drawer-section-title">Personalize Tabs</h4>
                    <ul id="drawer-tab-settings-list" class="drawer-settings-list">
                        <!-- Custom settings rows rendered dynamically -->
                    </ul>
                </div>
            </div>
        `;
        document.body.appendChild(drawer);
        
        this.container = drawer;
        this.backdrop = backdrop;
    }

    /**
     * Attach interaction handlers
     */
    setupEventListeners() {
        const toggleBtn = document.getElementById("menu-toggle");
        if (toggleBtn) {
            toggleBtn.addEventListener("click", () => this.toggle());
        }

        // Close drawer handlers
        this.container.querySelector(".drawer-close").addEventListener("click", () => this.close());
        
        // Escape key close
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && this.isOpen) {
                this.close();
            }
        });

        // Utility actions - keep Control Deck open on desktop/tablet
        document.getElementById("drawer-routing-btn").addEventListener("click", () => {
            if (window.innerWidth < 768) {
                this.close();
            }
            window.app.components.routeAllDrawer.toggle();
        });

        document.getElementById("drawer-theme-btn").addEventListener("click", () => {
            if (window.innerWidth < 768) {
                this.close();
            }
            window.themeDrawer.toggle();
        });

        document.getElementById("drawer-refresh-btn").addEventListener("click", () => {
            if (window.innerWidth < 768) {
                this.close();
            }
            window.app.refresh();
        });

        // Settings drawers (split into 3 sections)
        document.getElementById("drawer-general-btn")?.addEventListener("click", () => {
            if (window.innerWidth < 768) {
                this.close();
            }
            if (window.generalDrawer) {
                window.generalDrawer.toggle();
            }
        });

        document.getElementById("drawer-hardware-btn")?.addEventListener("click", () => {
            if (window.innerWidth < 768) {
                this.close();
            }
            if (window.hardwareDrawer) {
                window.hardwareDrawer.toggle();
            }
        });

        document.getElementById("drawer-interface-btn")?.addEventListener("click", () => {
            if (window.innerWidth < 768) {
                this.close();
            }
            if (window.interfaceDrawer) {
                window.interfaceDrawer.toggle();
            }
        });

        document.getElementById("drawer-shortcuts-btn")?.addEventListener("click", () => {
            if (window.innerWidth < 768) {
                this.close();
            }
            if (window.systemShortcutsPanel) {
                window.systemShortcutsPanel.open();
            }
        });
    }

    /**
     * Render the personalization tab settings rows dynamically
     */
    render() {
        const listEl = document.getElementById("drawer-tab-settings-list");
        if (!listEl) return;

        const specs = this.getTabSpecs();
        const tabOrder = this.preferences.tabOrder || [];
        const pinnedTabs = this.preferences.pinnedTabs || [];

        // Sort tab specs based on active preferences order
        const sortedSpecs = [...specs].sort((a, b) => {
            let indexA = tabOrder.indexOf(a.id);
            let indexB = tabOrder.indexOf(b.id);
            if (indexA === -1) indexA = 99;
            if (indexB === -1) indexB = 99;
            return indexA - indexB;
        });

        let html = "";
        sortedSpecs.forEach((tab, index) => {
            const isPinned = pinnedTabs.includes(tab.id);
            const isFirst = index === 0;
            const isLast = index === sortedSpecs.length - 1;

            html += `
                <li class="tab-settings-item" data-id="${tab.id}">
                    <div class="tab-settings-info">
                        <svg class="icon tab-settings-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            ${tab.icon}
                        </svg>
                        <span class="tab-settings-label">${tab.name}</span>
                    </div>
                    
                    <div class="tab-settings-actions">
                        <label class="toggle-switch settings-pin-toggle" title="${isPinned ? 'Unpin Tab' : 'Pin Tab'}">
                            <input type="checkbox" class="pin-checkbox" ${isPinned ? 'checked' : ''} data-id="${tab.id}">
                            <span class="slider"></span>
                        </label>
                        
                        <button class="btn-icon move-up-btn" data-id="${tab.id}" ${isFirst ? 'disabled' : ''} title="Move Up">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="18 15 12 9 6 15"/>
                            </svg>
                        </button>
                        
                        <button class="btn-icon move-down-btn" data-id="${tab.id}" ${isLast ? 'disabled' : ''} title="Move Down">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="6 9 12 15 18 9"/>
                            </svg>
                        </button>
                    </div>
                </li>
            `;
        });

        listEl.innerHTML = html;

        // Attach events for pin/unpin toggles
        listEl.querySelectorAll(".pin-checkbox").forEach(chk => {
            chk.addEventListener("change", (e) => {
                const id = e.target.dataset.id;
                const checked = e.target.checked;
                this.toggleTabPinned(id, checked);
            });
        });

        // Attach events for up/down arrow buttons
        listEl.querySelectorAll(".move-up-btn").forEach(btn => {
            if (!btn.disabled) {
                btn.addEventListener("click", () => this.moveTabOrder(btn.dataset.id, -1));
            }
        });

        listEl.querySelectorAll(".move-down-btn").forEach(btn => {
            if (!btn.disabled) {
                btn.addEventListener("click", () => this.moveTabOrder(btn.dataset.id, 1));
            }
        });
    }

    /**
     * Pin or unpin a tab from navigation
     */
    async toggleTabPinned(tabId, isPinned) {
        let pinned = [...(this.preferences.pinnedTabs || [])];
        if (isPinned) {
            if (!pinned.includes(tabId)) {
                pinned.push(tabId);
            }
        } else {
            pinned = pinned.filter(id => id !== tabId);
        }

        // Must keep at least one tab pinned to prevent empty state crashes
        if (pinned.length === 0) {
            toast.warning("At least one tab must remain pinned");
            this.render(); // Redraw to reset checkbox state
            return;
        }

        this.preferences.pinnedTabs = pinned;
        await this.savePreferences();
    }

    /**
     * Shift a tab up or down in the sorting order
     */
    async moveTabOrder(tabId, direction) {
        const order = [...(this.preferences.tabOrder || [])];
        const index = order.indexOf(tabId);
        if (index === -1) return;

        const targetIndex = index + direction;
        if (targetIndex < 0 || targetIndex >= order.length) return;

        // Swap items
        const temp = order[index];
        order[index] = order[targetIndex];
        order[targetIndex] = temp;

        this.preferences.tabOrder = order;
        await this.savePreferences();
    }

    /**
     * Send updated preferences to server and trigger dynamic tab layout reload
     */
    async savePreferences() {
        try {
            const result = await api.updateUiPreferences(this.preferences);
            if (result && result.success) {
                toast.success("Preferences updated", 1500);
                this.render();
                
                // Fire window custom event to inform matrixApp to reload UI
                const event = new CustomEvent("uiPreferencesChanged", { detail: this.preferences });
                window.dispatchEvent(event);
            } else {
                toast.error("Failed to save preferences: " + (result?.error || "Unknown"));
            }
        } catch (error) {
            console.error("Preferences save error:", error);
            toast.error("Network error saving preferences");
        }
    }

    /**
     * Open Drawer
     */
    open() {
        if (window.overlayManager) {
            window.overlayManager.onOpen("side-nav-drawer");
        }
        this.isOpen = true;
        this.container.classList.add("open");
        this.backdrop.classList.add("open");
        document.body.style.overflow = "hidden";
        
        // Hide Settings drawer and others to avoid overlaps on mobile only
        if (window.innerWidth < 768) {
            if (window.app?.components?.settingsDrawer?.isOpen) {
                window.app.components.settingsDrawer.close();
            }
            if (window.app?.components?.routeAllDrawer?.isOpen) {
                window.app.components.routeAllDrawer.close();
            }
            if (window.themeDrawer?.isOpen) {
                window.themeDrawer.close();
            }
        }
    }

    /**
     * Close Drawer
     */
    close() {
        if (window.overlayManager) {
            window.overlayManager.onClose("side-nav-drawer");
        }
        this.isOpen = false;
        this.container.classList.remove("open");
        this.backdrop.classList.remove("open");
        document.body.style.overflow = "";
    }

    /**
     * Toggle Drawer
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
}

// Instantiate side navigation drawer on DOM load
document.addEventListener("DOMContentLoaded", () => {
    window.sideNavDrawer = new SideNavDrawer();
    
    // Register with overlay manager if it exists
    if (window.overlayManager) {
        window.overlayManager.register("side-nav-drawer", {
            close: () => window.sideNavDrawer.close(),
            isOpen: () => window.sideNavDrawer.isOpen
        });
    }
});
