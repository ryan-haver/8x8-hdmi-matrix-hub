/**
 * OREI Matrix Control - Quick Actions Drawer Component
 * Slide-out drawer with quick access to favorite presets and scenes
 * Also supports dashboard widget mode for pinned inline display
 */

class QuickActionsDrawer {
    constructor() {
        this.isOpen = false;
        this.container = null;
        this.backdrop = null;
        
        // Subscribe to state changes
        state.on('presets', () => this.onStateChange());
        state.on('scenes', () => this.onStateChange());
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
        const favoritePresets = state.favorites?.presets || [];
        const favoriteScenes = state.favorites?.scenes || [];
        
        let html = '<div class="quick-actions-grid">';
        
        // Show favorite presets
        favoritePresets.forEach(presetId => {
            const preset = state.presets[presetId];
            if (preset) {
                html += `
                    <button class="quick-action-btn preset-btn" data-preset="${presetId}">
                        <span class="quick-action-icon">📋</span>
                        <span class="action-label">${Helpers.escapeHtml(preset.name)}</span>
                    </button>
                `;
            }
        });
        
        // Show favorite scenes
        favoriteScenes.forEach(sceneId => {
            const scene = state.scenes.find(s => s.id === sceneId);
            if (scene) {
                html += `
                    <button class="quick-action-btn scene-btn" data-scene="${sceneId}">
                        <span class="quick-action-icon">🎬</span>
                        <span class="action-label">${Helpers.escapeHtml(scene.name)}</span>
                    </button>
                `;
            }
        });
        
        // Quick routing shortcuts
        html += `
            <button class="quick-action-btn routing-btn" data-action="1-to-1">
                <span class="quick-action-icon">🔄</span>
                <span class="action-label">1:1 Mapping</span>
            </button>
        `;
        
        if (favoritePresets.length === 0 && favoriteScenes.length === 0) {
            html = `
                <div class="widget-empty">
                    <p>Star presets or scenes to add them here.</p>
                    <button class="btn btn-secondary widget-empty-cta" data-action="go-profiles">
                        Browse Profiles
                    </button>
                </div>
            `;
        } else {
            html += '</div>';
        }
        
        return html;
    }

    /**
     * Attach event listeners to widget buttons
     */
    attachWidgetEventListeners(widgetEl) {
        if (!widgetEl) return;
        
        widgetEl.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const presetId = parseInt(e.currentTarget.dataset.preset);
                await this.recallPreset(presetId);
            });
        });
        
        widgetEl.querySelectorAll('.scene-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const sceneId = e.currentTarget.dataset.scene;
                await this.recallScene(sceneId);
            });
        });
        
        widgetEl.querySelectorAll('.routing-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const action = e.currentTarget.dataset.action;
                await this.executeQuickRouting(action);
            });
        });
        
        // Empty state CTA - navigate to profiles
        widgetEl.querySelectorAll('.widget-empty-cta').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                if (action === 'go-profiles') {
                    // Switch to profiles tab
                    state.setActiveTab('profiles');
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
                // Already pinned/visible - unpin/hide it
                window.dashboardManager.unpinWidget('quick-actions');
            } else {
                // Not pinned/visible - pin/show it
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
        // Load favorites from localStorage
        state.loadFavorites();
        this.render();
    }

    /**
     * Create the drawer DOM elements
     */
    createDrawer() {
        // Backdrop
        const backdrop = document.createElement('div');
        backdrop.id = 'quick-actions-backdrop';
        backdrop.className = 'quick-actions-backdrop';
        backdrop.addEventListener('click', () => this.close());
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
        `;
        document.body.appendChild(drawer);
        
        this.container = drawer;
        this.backdrop = backdrop;
        
        // Close button
        drawer.querySelector('.drawer-close').addEventListener('click', () => this.close());
        
        // Pin to dashboard button (toggles pin state)
        drawer.querySelector('.drawer-pin-dashboard-btn')?.addEventListener('click', () => this.toggleDashboardPin());
        
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
     * Render drawer content
     */
    render() {
        const content = document.getElementById('quick-actions-content');
        if (!content) return;
        
        const favoritePresets = state.favorites?.presets || [];
        const favoriteScenes = state.favorites?.scenes || [];
        
        let html = '';
        
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
        
        // Favorite Scenes Section
        html += `
            <div class="drawer-section">
                <h4 class="drawer-section-title">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <polygon points="10 8 16 12 10 16 10 8"/>
                    </svg>
                    Favorite Scenes
                </h4>
                <div class="drawer-actions">
                    ${this.renderFavoriteScenes(favoriteScenes)}
                </div>
            </div>
        `;
        
        // All Presets Section
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
        
        // Quick Routing Section
        html += `
            <div class="drawer-section">
                <h4 class="drawer-section-title">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                        <polyline points="15 3 21 3 21 9"/>
                        <line x1="10" y1="14" x2="21" y2="3"/>
                    </svg>
                    Quick Routing
                </h4>
                <div class="drawer-actions">
                    ${this.renderQuickRouting()}
                </div>
            </div>
        `;
        
        content.innerHTML = html;
        this.attachEventListeners();
    }

    /**
     * Render favorite presets buttons
     */
    renderFavoritePresets(favorites) {
        if (favorites.length === 0) {
            return '<p class="drawer-empty">No favorite presets. Star a preset to add it here.</p>';
        }
        
        let html = '';
        favorites.forEach(presetId => {
            const preset = state.presets[presetId];
            if (preset) {
                html += `
                    <button class="quick-action-btn preset-btn" data-preset="${presetId}">
                        <span class="quick-action-icon">📋</span>
                        <span class="quick-action-label">${Helpers.escapeHtml(preset.name)}</span>
                    </button>
                `;
            }
        });
        return html;
    }

    /**
     * Render favorite scenes buttons
     */
    renderFavoriteScenes(favorites) {
        if (favorites.length === 0) {
            return '<p class="drawer-empty">No favorite scenes. Star a scene to add it here.</p>';
        }
        
        let html = '';
        favorites.forEach(sceneId => {
            const scene = state.scenes.find(s => s.id === sceneId);
            if (scene) {
                html += `
                    <button class="quick-action-btn scene-btn" data-scene="${sceneId}">
                        <span class="quick-action-icon">🎬</span>
                        <span class="quick-action-label">${Helpers.escapeHtml(scene.name)}</span>
                    </button>
                `;
            }
        });
        return html;
    }

    /**
     * Render all presets grid with star toggle
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
     * Render quick routing buttons
     */
    renderQuickRouting() {
        return `
            <button class="quick-action-btn routing-btn" data-action="all-to-1">
                <span class="quick-action-icon">📺</span>
                <span class="quick-action-label">All → Output 1</span>
            </button>
            <button class="quick-action-btn routing-btn" data-action="1-to-1">
                <span class="quick-action-icon">🔄</span>
                <span class="quick-action-label">1:1 Mapping</span>
            </button>
        `;
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
                const presetId = parseInt(e.currentTarget.dataset.preset);
                await this.recallPreset(presetId);
            });
        });
        
        // Scene buttons
        content.querySelectorAll('.scene-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const sceneId = e.currentTarget.dataset.scene;
                await this.recallScene(sceneId);
            });
        });
        
        // Star buttons
        content.querySelectorAll('.star-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const presetId = parseInt(e.currentTarget.dataset.preset);
                state.toggleFavoritePreset(presetId);
            });
        });
        
        // Quick routing buttons
        content.querySelectorAll('.routing-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const action = e.currentTarget.dataset.action;
                await this.executeQuickRouting(action);
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
     * Recall a scene
     */
    async recallScene(sceneId) {
        const scene = state.scenes.find(s => s.id === sceneId);
        if (!scene) return;
        
        try {
            // Apply all routes in the scene
            for (const [output, input] of Object.entries(scene.routing)) {
                await api.switchInput(parseInt(output), input);
            }
            toast.show(`Scene "${scene.name}" applied`, 'success');
            this.close();
        } catch (error) {
            toast.show(`Error: ${error.message}`, 'error');
        }
    }

    /**
     * Execute quick routing action
     */
    async executeQuickRouting(action) {
        try {
            if (action === 'all-to-1') {
                // Route all outputs to input 1
                for (let o = 1; o <= 8; o++) {
                    await api.switchInput(o, 1);
                }
                toast.show('All outputs routed to Input 1', 'success');
            } else if (action === '1-to-1') {
                // 1:1 mapping
                for (let i = 1; i <= 8; i++) {
                    await api.switchInput(i, i);
                }
                toast.show('1:1 mapping applied', 'success');
            }
            this.close();
        } catch (error) {
            toast.show(`Error: ${error.message}`, 'error');
        }
    }

}
