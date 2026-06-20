/**
 * OREI Matrix Control - Quick Actions Drawer Component
 * Slide-out drawer with unified quick access to favorite profiles, presets,
 * system shortcuts, and macros. Data is now server-backed (Phase 7).
 */

class QuickActionsDrawer {
    constructor() {
        this.isOpen = false;
        this.container = null;
        this.backdrop = null;

        // Subscribe to unified favorites array from server (Phase 7)
        state.on('favorites', () => this.onStateChange());

        // Create drawer elements
        this.createDrawer();

        // Register as dashboard widget
        this.registerAsWidget();
    }

    /**
     * Handle state changes - update drawer and widget
     */
    onStateChange() {
        this.render();
        // Also refresh widget if pinned to dashboard
        if (window.dashboardManager && window.dashboardManager.isWidgetPinned('quick-actions')) {
            window.dashboardManager.refreshWidget('quick-actions');
        }
    }

    /**
     * Register as a dashboard widget
     */
    registerAsWidget() {
        if (typeof window.dashboardManager !== 'undefined') {
            window.dashboardManager.registerWidget({
                id: 'quick-actions',
                name: 'Quick Actions',
                icon: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>`,
                render: () => this.renderWidgetContent(),
                onMount: (el) => this.attachWidgetEventListeners(el),
                onUnmount: () => {},
                component: this
            });
        }
    }

    /**
     * Render content for the dashboard widget (compact version)
     */
    renderWidgetContent() {
        const allFavorites = state._collectAllFavorites();

        if (allFavorites.length === 0) {
            return `
                <div class="widget-empty">
                    <p>Star profiles, presets, or shortcuts to add them here.</p>
                    <button class="btn btn-secondary widget-empty-cta" data-action="open-drawer">
                        Open Quick Actions
                    </button>
                </div>
            `;
        }

        let html = '<div class="quick-actions-grid">';

        allFavorites.forEach(item => {
            html += this.renderFavoriteItem(item, true);
        });

        html += '</div>';
        return html;
    }

    /**
     * Render a single favorite item (for widget)
     */
    renderFavoriteItem(item, compact = false) {
        const icon = item.icon || '⚡';
        const name = Helpers.escapeHtml(item.name || item.id);
        const classes = compact ? 'quick-action-btn compact' : 'quick-action-btn';

        if (item.type === 'preset') {
            return `
                <button class="${classes} preset-btn" data-preset="${item.id}">
                    <span class="quick-action-icon">${icon}</span>
                    <span class="action-label">${name}</span>
                </button>
            `;
        } else if (item.type === 'profile') {
            return `
                <button class="${classes} profile-btn" data-profile="${item.id}">
                    <span class="quick-action-icon">${icon}</span>
                    <span class="action-label">${name}</span>
                </button>
            `;
        } else if (item.type === 'system_shortcut') {
            return `
                <button class="${classes} shortcut-btn" data-shortcut="${item.id}">
                    <span class="quick-action-icon">${icon}</span>
                    <span class="action-label">${name}</span>
                </button>
            `;
        } else if (item.type === 'macro') {
            return `
                <button class="${classes} macro-btn" data-macro="${item.id}">
                    <span class="quick-action-icon">${icon}</span>
                    <span class="action-label">${name}</span>
                </button>
            `;
        }
        return '';
    }

    /**
     * Attach event listeners to widget buttons
     */
    attachWidgetEventListeners(widgetEl) {
        if (!widgetEl) return;

        widgetEl.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const presetNum = parseInt(e.currentTarget.dataset.preset);
                await this.recallPreset(presetNum);
            });
        });

        widgetEl.querySelectorAll('.profile-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const profileId = e.currentTarget.dataset.profile;
                await this.recallProfile(profileId);
            });
        });

        widgetEl.querySelectorAll('.shortcut-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const shortcutId = e.currentTarget.dataset.shortcut;
                await this.executeShortcut(shortcutId);
            });
        });

        widgetEl.querySelectorAll('.macro-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const macroId = e.currentTarget.dataset.macro;
                await this.executeMacro(macroId);
            });
        });

        // Empty state CTA
        widgetEl.querySelectorAll('.widget-empty-cta').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                if (action === 'open-drawer') {
                    this.open();
                }
            });
        });
    }

    /**
     * Check if Quick Actions is pinned to dashboard (visible on mobile)
     */
    isPinnedToDashboard() {
        return window.dashboardManager && window.dashboardManager.isWidgetPinned('quick-actions');
    }

    /**
     * Toggle dashboard pin state (pin on desktop, hide on mobile)
     */
    toggleDashboardPin() {
        if (window.dashboardManager) {
            if (this.isPinnedToDashboard()) {
                window.dashboardManager.unpinWidget('quick-actions');
            } else {
                if (window.dashboardManager.pinWidget('quick-actions')) {
                    this.close();
                }
            }
        }
    }


    /**
     * Initialize the component
     */
    init() {
        this.render();
        if (window.overlayManager) {
            window.overlayManager.register('quick-actions-drawer', {
                close: () => this.close(),
                isOpen: () => this.isOpen
            });
        }
    }

    /**
     * Create the drawer DOM elements
     */
    createDrawer() {
        // Backdrop
        const backdrop = document.createElement('div');
        backdrop.id = 'quick-actions-backdrop';
        backdrop.className = 'quick-actions-backdrop';
        backdrop.addEventListener('click', () => {
            if (window.overlayManager) {
                window.overlayManager.closeAll();
            } else {
                this.close();
            }
        });
        document.body.appendChild(backdrop);

        // Drawer
        const drawer = document.createElement('aside');
        drawer.id = 'quick-actions-drawer';
        drawer.className = 'quick-actions-drawer';
        drawer.innerHTML = `
            <div class="drawer-header">
                <h3>
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                    </svg>
                    Quick Actions
                </h3>
                <div class="drawer-header-actions">
                    <button class="btn-icon drawer-pin-dashboard-btn" title="Pin to dashboard">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2"/>
                            <line x1="9" y1="3" x2="9" y2="21"/>
                            <line x1="15" y1="3" x2="15" y2="21"/>
                            <line x1="3" y1="9" x2="21" y2="9"/>
                            <line x1="3" y1="15" x2="21" y2="15"/>
                        </svg>
                    </button>
                    <button class="btn-icon drawer-close" aria-label="Close drawer">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="drawer-content" id="quick-actions-content">
                <!-- Content rendered dynamically -->
            </div>
            <div class="drawer-footer mobile-only">
                <button class="btn btn-primary btn-block back-to-deck-btn">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="19" y1="12" x2="5" y2="12"/>
                        <polyline points="12 19 5 12 12 5"/>
                    </svg>
                    Back to Control Deck
                </button>
            </div>
        `;
        document.body.appendChild(drawer);

        this.container = drawer;
        this.backdrop = backdrop;

        // Close button
        drawer.querySelector('.drawer-close').addEventListener('click', () => this.close());

        // Pin to dashboard button (toggles pin state)
        drawer.querySelector('.drawer-pin-dashboard-btn')?.addEventListener('click', () => this.toggleDashboardPin());

        // Back to Control Deck button
        drawer.querySelector('.back-to-deck-btn')?.addEventListener('click', () => {
            this.close();
            if (window.sideNavDrawer) {
                window.sideNavDrawer.open();
            }
        });

        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    /**
     * Update the dashboard pin button to show correct state
     */
    updateDashboardButton() {
        const btn = this.container?.querySelector('.drawer-pin-dashboard-btn');
        if (!btn) return;

        const isPinned = this.isPinnedToDashboard();
        if (isPinned) {
            btn.title = 'Hide from tabs';
            btn.innerHTML = `
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <line x1="5" y1="5" x2="19" y2="19"/>
                </svg>
            `;
        } else {
            btn.title = 'Pin to dashboard';
            btn.innerHTML = `
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <line x1="9" y1="3" x2="9" y2="21"/>
                    <line x1="15" y1="3" x2="15" y2="21"/>
                    <line x1="3" y1="9" x2="21" y2="9"/>
                    <line x1="3" y1="15" x2="21" y2="15"/>
                </svg>
            `;
        }
    }

    /**
     * Open the drawer
     */
    open() {
        if (window.overlayManager) {
            window.overlayManager.onOpen('quick-actions-drawer');
        }
        this.isOpen = true;
        this.container.classList.add('open');
        this.backdrop.classList.add('open');
        document.body.style.overflow = 'hidden';
        this.updateDashboardButton();
        this.render();
    }

    /**
     * Close the drawer
     */
    close() {
        if (window.overlayManager) {
            window.overlayManager.onClose('quick-actions-drawer');
        }
        this.isOpen = false;
        this.container.classList.remove('open');
        this.backdrop.classList.remove('open');
        document.body.style.overflow = '';
    }

    /**
     * Toggle drawer open/closed
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Render drawer content - unified favorites grid (Phase 7)
     */
    render() {
        const content = document.getElementById('quick-actions-content');
        if (!content) return;

        // Use the unified favorites array from state
        const favoriteProfiles = state.favoriteProfiles || [];
        const favoritePresets = state.favoritePresets || [];
        const favoriteSystemShortcuts = state.favoriteSystemShortcuts || [];
        const favoriteMacros = state.favoriteMacros || [];

        let html = '';

        // System Shortcuts Section (replaces legacy "All → Out 1" / "1:1 Mapping" buttons)
        if (favoriteSystemShortcuts.length > 0) {
            html += `
                <div class="drawer-section">
                    <h4 class="drawer-section-title">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                        </svg>
                        System Shortcuts
                    </h4>
                    <div class="drawer-actions">
                        ${this.renderFavoriteSystemShortcuts(favoriteSystemShortcuts)}
                    </div>
                </div>
            `;
        }

        // Favorite Profiles Section
        html += `
            <div class="drawer-section">
                <h4 class="drawer-section-title">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <polygon points="10 8 16 12 10 16 10 8"/>
                    </svg>
                    Favorite Profiles
                </h4>
                <div class="drawer-actions">
                    ${this.renderFavoriteProfiles(favoriteProfiles)}
                </div>
            </div>
        `;

        // Favorite Presets Section
        html += `
            <div class="drawer-section">
                <h4 class="drawer-section-title">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                    </svg>
                    Favorite Presets
                </h4>
                <div class="drawer-actions">
                    ${this.renderFavoritePresets(favoritePresets)}
                </div>
            </div>
        `;

        // Favorite Macros Section
        if (favoriteMacros.length > 0) {
            html += `
                <div class="drawer-section">
                    <h4 class="drawer-section-title">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/>
                        </svg>
                        Favorite Macros
                    </h4>
                    <div class="drawer-actions">
                        ${this.renderFavoriteMacros(favoriteMacros)}
                    </div>
                </div>
            `;
        }

        // All Presets Grid Section (with star toggle)
        html += `
            <div class="drawer-section">
                <h4 class="drawer-section-title">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
                        <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
                    </svg>
                    All Presets
                </h4>
                <div class="drawer-actions drawer-actions-grid">
                    ${this.renderAllPresets(favoritePresets)}
                </div>
            </div>
        `;

        content.innerHTML = html;
        this.attachEventListeners();
    }

    /**
     * Render favorite profiles
     */
    renderFavoriteProfiles(profiles) {
        if (profiles.length === 0) {
            return '<p class="drawer-empty">No favorite profiles. Star a profile to add it here.</p>';
        }

        return profiles.map(profile => `
            <button class="quick-action-btn profile-btn" data-profile="${profile.id}">
                <span class="quick-action-icon">${profile.icon || '🎬'}</span>
                <span class="quick-action-label">${Helpers.escapeHtml(profile.name)}</span>
                <button class="btn-icon star-btn starred" data-type="profile" data-id="${profile.id}" title="Remove from favorites">
                    <svg class="icon" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                    </svg>
                </button>
            </button>
        `).join('');
    }

    /**
     * Render favorite presets
     */
    renderFavoritePresets(presets) {
        if (presets.length === 0) {
            return '<p class="drawer-empty">No favorite presets. Star a preset below to add it here.</p>';
        }

        return presets.map(presetNum => {
            const preset = state.presets[presetNum] || { name: `Preset ${presetNum}` };
            return `
                <button class="quick-action-btn preset-btn" data-preset="${presetNum}">
                    <span class="quick-action-icon">⚡</span>
                    <span class="quick-action-label">${Helpers.escapeHtml(preset.name)}</span>
                    <button class="btn-icon star-btn starred" data-type="preset" data-id="${presetNum}" title="Remove from favorites">
                        <svg class="icon" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                        </svg>
                    </button>
                </button>
            `;
        }).join('');
    }

    /**
     * Render favorite system shortcuts
     */
    renderFavoriteSystemShortcuts(shortcuts) {
        return shortcuts.map(shortcut => `
            <button class="quick-action-btn shortcut-btn" data-shortcut="${shortcut.id}">
                <span class="quick-action-icon">${shortcut.icon || '⚡'}</span>
                <span class="quick-action-label">${Helpers.escapeHtml(shortcut.name)}</span>
                <button class="btn-icon star-btn starred" data-type="system_shortcut" data-id="${shortcut.id}" title="Remove from favorites">
                    <svg class="icon" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                    </svg>
                </button>
            </button>
        `).join('');
    }

    /**
     * Render favorite macros
     */
    renderFavoriteMacros(macros) {
        return macros.map(macro => `
            <button class="quick-action-btn macro-btn" data-macro="${macro.id}">
                <span class="quick-action-icon">${macro.icon || '⚡'}</span>
                <span class="quick-action-label">${Helpers.escapeHtml(macro.name)}</span>
                <button class="btn-icon star-btn starred" data-type="macro" data-id="${macro.id}" title="Remove from favorites">
                    <svg class="icon" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2">
                        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                    </svg>
                </button>
            </button>
        `).join('');
    }

    /**
     * Render all presets grid with star toggle (Phase 7 - uses state.favoritePresets)
     */
    renderAllPresets(favorites) {
        let html = '';

        for (let i = 1; i <= 8; i++) {
            const preset = state.presets[i] || { name: `Preset ${i}` };
            const isFavorite = favorites.includes(i);

            html += `
                <div class="preset-grid-item">
                    <button class="quick-action-btn preset-btn compact" data-preset="${i}">
                        <span class="quick-action-num">${i}</span>
                        <span class="quick-action-label">${Helpers.escapeHtml(preset.name)}</span>
                    </button>
                    <button class="btn-icon star-btn ${isFavorite ? 'starred' : ''}"
                            data-type="preset"
                            data-preset="${i}"
                            title="${isFavorite ? 'Remove from favorites' : 'Add to favorites'}">
                        <svg class="icon" viewBox="0 0 24 24" fill="${isFavorite ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                        </svg>
                    </button>
                </div>
            `;
        }
        return html;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const content = document.getElementById('quick-actions-content');
        if (!content) return;

        // Preset buttons
        content.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                // Ignore if clicking the star button inside
                if (e.target.closest('.star-btn')) return;
                const presetNum = parseInt(e.currentTarget.dataset.preset);
                await this.recallPreset(presetNum);
            });
        });

        // Profile buttons
        content.querySelectorAll('.profile-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                if (e.target.closest('.star-btn')) return;
                const profileId = e.currentTarget.dataset.profile;
                await this.recallProfile(profileId);
            });
        });

        // Shortcut buttons
        content.querySelectorAll('.shortcut-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                if (e.target.closest('.star-btn')) return;
                const shortcutId = e.currentTarget.dataset.shortcut;
                await this.executeShortcut(shortcutId);
            });
        });

        // Macro buttons
        content.querySelectorAll('.macro-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                if (e.target.closest('.star-btn')) return;
                const macroId = e.currentTarget.dataset.macro;
                await this.executeMacro(macroId);
            });
        });

        // Star buttons - toggle favorite via server (Phase 7)
        content.querySelectorAll('.star-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const type = e.currentTarget.dataset.type;
                const id = e.currentTarget.dataset.id || e.currentTarget.dataset.preset;
                await window.app.state.toggleFavorite(type, id);
            });
        });
    }

    /**
     * Recall a preset
     */
    async recallPreset(presetId) {
        try {
            const response = await api.recallPreset(presetId);
            if (response.success) {
                toast.show(`Preset ${presetId} recalled`, 'success');
                this.close();
            } else {
                toast.show(`Failed to recall preset: ${response.error}`, 'error');
            }
        } catch (error) {
            toast.show(`Error: ${error.message}`, 'error');
        }
    }

    /**
     * Recall a profile
     */
    async recallProfile(profileId) {
        try {
            const response = await api.recallProfile(profileId);
            if (response.success) {
                toast.show(`Profile recalled`, 'success');
                this.close();
            } else {
                toast.show(`Failed to recall profile: ${response.error}`, 'error');
            }
        } catch (error) {
            toast.show(`Error: ${error.message}`, 'error');
        }
    }

    /**
     * Execute a system shortcut
     */
    async executeShortcut(shortcutId) {
        try {
            const response = await api.executeSystemShortcut(shortcutId);
            if (response.success) {
                toast.show(`Shortcut executed`, 'success');
            } else {
                toast.show(`Failed to execute shortcut: ${response.error}`, 'error');
            }
        } catch (error) {
            toast.show(`Error: ${error.message}`, 'error');
        }
    }

    /**
     * Execute a CEC macro
     */
    async executeMacro(macroId) {
        try {
            const response = await api.executeMacro(macroId);
            if (response.success) {
                toast.show(`Macro executed`, 'success');
            } else {
                toast.show(`Failed to execute macro: ${response.error}`, 'error');
            }
        } catch (error) {
            toast.show(`Error: ${error.message}`, 'error');
        }
    }
}
