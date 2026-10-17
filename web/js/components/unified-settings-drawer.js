/**
 * OREI Matrix Control - Unified Settings Controller (Phase 5 / WP-E2)
 *
 * Unifies hash routing (#settings/<section>) and programmatic navigation across all 9
 * settings sections (general, hardware, interface, theme, integrations, shortcuts,
 * profiles, scenes, system) per DI-7, UI-05, UI-14 while keeping existing drawer DOM
 * structures pixel-identical.
 */

class UnifiedSettingsController {
    constructor() {
        this.sections = [
            'general',
            'hardware',
            'interface',
            'theme',
            'integrations',
            'shortcuts',
            'profiles',
            'scenes',
            'system',
        ];

        this.sectionConfig = {
            general: {
                id: 'general',
                label: 'General',
                drawerId: 'general-drawer',
                overlayName: 'general-drawer',
                globalKey: 'generalDrawer',
                delegatedToSettingsDrawer: false,
            },
            hardware: {
                id: 'hardware',
                label: 'Hardware',
                drawerId: 'hardware-drawer',
                overlayName: 'hardware-drawer',
                globalKey: 'hardwareDrawer',
                delegatedToSettingsDrawer: false,
            },
            interface: {
                id: 'interface',
                label: 'Interface',
                drawerId: 'interface-drawer',
                overlayName: 'interface-drawer',
                globalKey: 'interfaceDrawer',
                delegatedToSettingsDrawer: false,
            },
            theme: {
                id: 'theme',
                label: 'Theme',
                drawerId: 'theme-drawer',
                overlayName: 'theme-drawer',
                globalKey: 'themeDrawer',
                delegatedToSettingsDrawer: false,
            },
            integrations: {
                id: 'integrations',
                label: 'Integrations',
                drawerId: 'integrations-drawer',
                overlayName: 'integrations-drawer',
                globalKey: 'integrationsDrawer',
                delegatedToSettingsDrawer: false,
            },
            shortcuts: {
                id: 'shortcuts',
                label: 'Shortcuts',
                drawerId: 'shortcuts-drawer',
                overlayName: 'shortcuts-drawer',
                globalKey: 'shortcutsDrawer',
                delegatedToSettingsDrawer: false,
            },
            profiles: {
                id: 'profiles',
                label: 'Profiles',
                drawerId: 'settings-drawer',
                overlayName: 'settings-drawer',
                globalKey: 'settingsDrawer',
                delegatedToSettingsDrawer: true,
            },
            scenes: {
                id: 'scenes',
                label: 'Scenes',
                drawerId: 'settings-drawer',
                overlayName: 'settings-drawer',
                globalKey: 'settingsDrawer',
                delegatedToSettingsDrawer: true,
            },
            system: {
                id: 'system',
                label: 'System',
                drawerId: 'settings-drawer',
                overlayName: 'settings-drawer',
                globalKey: 'settingsDrawer',
                delegatedToSettingsDrawer: true,
            },
        };

        this.activeSection = null;
        this.isOpen = false;
        this._suppressHashChange = false;
        this._hashRoutingInitialized = false;

        this.initHashRouting();
    }

    /**
     * Return all 9 supported settings section identifiers
     * @returns {string[]}
     */
    getSections() {
        return [...this.sections];
    }

    /**
     * Return the currently active settings section or null when closed
     * @returns {string|null}
     */
    getActiveSection() {
        if (typeof window !== 'undefined' && window.overlayManager) {
            const top = typeof window.overlayManager.getTopOverlay === 'function'
                ? window.overlayManager.getTopOverlay()
                : window.overlayManager.activeOverlay;

            if (top === 'settings-drawer') {
                if (window.settingsDrawer?.activeTab && ['profiles', 'scenes', 'system'].includes(window.settingsDrawer.activeTab)) {
                    return window.settingsDrawer.activeTab;
                }
                if (this.activeSection && ['profiles', 'scenes', 'system'].includes(this.activeSection)) {
                    return this.activeSection;
                }
                return 'profiles';
            }

            for (const [sec, cfg] of Object.entries(this.sectionConfig)) {
                if (!cfg.delegatedToSettingsDrawer && top === cfg.overlayName) {
                    return sec;
                }
            }
        }

        return this.isOpen ? this.activeSection : null;
    }

    /**
     * Locate a drawer DOM element if present in document
     * @param {Object} config
     * @returns {Element|null}
     */
    _getDrawerElement(config) {
        if (typeof document === 'undefined' || !config) return null;
        if (typeof document.getElementById === 'function') {
            const byId = document.getElementById(config.drawerId);
            if (byId) return byId;
        }
        if (typeof document.querySelector === 'function') {
            return document.querySelector(`#${config.drawerId}, .${config.drawerId}`);
        }
        return null;
    }

    /**
     * Synchronize the browser URL hash to targetHash without re-triggering hash routing
     * @param {string} targetHash
     */
    _syncHash(targetHash) {
        if (typeof window === 'undefined' || !window.location) return;
        if (window.location.hash !== targetHash) {
            this._suppressHashChange = true;
            try {
                if (window.history && typeof window.history.replaceState === 'function') {
                    window.history.replaceState(null, '', targetHash);
                }
                if (window.location.hash !== targetHash) {
                    window.location.hash = targetHash;
                }
            } catch {
                // Ignore read-only location errors in restricted test environments
            } finally {
                this._suppressHashChange = false;
            }
        }
    }

    /**
     * Open a specific settings section and synchronize #settings/<section>
     * @param {string} section - One of the 9 settings sections (defaults to 'general')
     * @returns {string} The opened section identifier
     */
    open(section = 'general') {
        const normalized = typeof section === 'string' && section.trim()
            ? section.trim().toLowerCase().replace(/^#?settings\//, '')
            : 'general';
        const targetSection = this.sections.includes(normalized) ? normalized : 'general';
        const config = this.sectionConfig[targetSection];

        this.activeSection = targetSection;
        this.isOpen = true;

        if (config.delegatedToSettingsDrawer) {
            if (typeof window !== 'undefined' && window.settingsDrawer && typeof window.settingsDrawer.open === 'function') {
                window.settingsDrawer.open(targetSection);
            } else if (typeof window !== 'undefined' && window.overlayManager) {
                const reg = window.overlayManager.overlays?.get('settings-drawer');
                if (reg && typeof reg.open === 'function') {
                    reg.open(targetSection);
                }
                if (window.overlayManager.activeOverlay !== 'settings-drawer') {
                    window.overlayManager.onOpen('settings-drawer');
                }
            }
            const domEl = this._getDrawerElement(config);
            if (domEl) {
                domEl.classList?.add('open');
                domEl.setAttribute?.('aria-hidden', 'false');
            }
        } else {
            const reg = typeof window !== 'undefined' ? window.overlayManager?.overlays?.get(config.overlayName) : null;
            const globalDrawer = typeof window !== 'undefined' ? window[config.globalKey] : null;

            if (reg && typeof reg.open === 'function') {
                reg.open();
            } else if (globalDrawer && typeof globalDrawer.open === 'function') {
                globalDrawer.open();
            }

            if (typeof window !== 'undefined' && window.overlayManager && window.overlayManager.activeOverlay !== config.overlayName) {
                window.overlayManager.onOpen(config.overlayName);
            }

            const domEl = this._getDrawerElement(config);
            if (domEl) {
                domEl.classList?.add('open');
                domEl.setAttribute?.('aria-hidden', 'false');
            }
        }

        this._syncHash(`#settings/${targetSection}`);
        return targetSection;
    }

    /**
     * Close the active settings drawer and clear any #settings/* hash
     */
    close() {
        const current = this.getActiveSection() || this.activeSection;
        if (current && this.sectionConfig[current]) {
            const config = this.sectionConfig[current];
            const reg = typeof window !== 'undefined' ? window.overlayManager?.overlays?.get(config.overlayName) : null;
            const globalDrawer = typeof window !== 'undefined' ? window[config.globalKey] : null;

            if (reg && typeof reg.close === 'function') {
                reg.close();
            } else if (globalDrawer && typeof globalDrawer.close === 'function') {
                globalDrawer.close();
            }

            if (typeof window !== 'undefined' && window.overlayManager && window.overlayManager.activeOverlay === config.overlayName) {
                window.overlayManager.onClose(config.overlayName);
            }

            const domEl = this._getDrawerElement(config);
            if (domEl) {
                domEl.classList?.remove('open');
                domEl.setAttribute?.('aria-hidden', 'true');
            }
        }

        this.isOpen = false;
        this.activeSection = null;

        if (typeof window !== 'undefined' && window.location && String(window.location.hash || '').startsWith('#settings/')) {
            const cleanUrl = (window.location.pathname || '/') + (window.location.search || '');
            this._suppressHashChange = true;
            try {
                if (window.history && typeof window.history.replaceState === 'function') {
                    window.history.replaceState(null, '', cleanUrl);
                }
                if (window.location.hash !== '') {
                    window.location.hash = '';
                }
            } catch {
                // Ignore read-only location errors
            } finally {
                this._suppressHashChange = false;
            }
        }
    }

    /**
     * Toggle a settings section drawer
     * @param {string} section
     */
    toggle(section = 'general') {
        if (this.isOpen && this.getActiveSection() === section) {
            this.close();
        } else {
            this.open(section);
        }
    }

    /**
     * Render navigation markup for all 9 settings sections
     * @param {string|null} activeSection
     * @returns {string}
     */
    renderSectionNav(activeSection = null) {
        const current = activeSection || this.getActiveSection() || 'general';
        const buttons = this.sections
            .map((sec) => {
                const cfg = this.sectionConfig[sec];
                const isActive = sec === current;
                return `<button type="button" class="drawer-tab-btn unified-settings-tab-btn${isActive ? ' active' : ''}" data-section="${cfg.id}" data-drawer="${cfg.drawerId}" role="tab" aria-selected="${isActive ? 'true' : 'false'}">${cfg.label}</button>`;
            })
            .join('');
        return `<div class="drawer-tabs unified-settings-nav" role="tablist" aria-label="Settings Sections">${buttons}</div>`;
    }

    /**
     * Handle URL hash changes for #settings/<section>
     */
    handleHashChange() {
        if (this._suppressHashChange || typeof window === 'undefined' || !window.location) {
            return;
        }
        const hash = String(window.location.hash || '');
        if (hash.startsWith('#settings/')) {
            const section = hash.replace('#settings/', '').trim().toLowerCase();
            if (this.sections.includes(section)) {
                this.open(section);
            }
        } else if (this.isOpen) {
            this.close();
        }
    }

    /**
     * Initialize #settings/<section> hash routing listener
     */
    initHashRouting() {
        if (this._hashRoutingInitialized || typeof window === 'undefined') {
            return;
        }
        this._hashRoutingInitialized = true;

        if (typeof window.addEventListener === 'function') {
            window.addEventListener('hashchange', () => this.handleHashChange());
        }

        const hash = String(window.location?.hash || '');
        if (hash.startsWith('#settings/')) {
            const section = hash.replace('#settings/', '').trim().toLowerCase();
            if (this.sections.includes(section)) {
                this.activeSection = section;
            }
        }
    }
}

// Create global instance
window.UnifiedSettingsController = UnifiedSettingsController;
window.unifiedSettings = new UnifiedSettingsController();
