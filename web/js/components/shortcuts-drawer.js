/**
 * OREI Matrix Control - Shortcuts Drawer Component (Phase 8)
 * Slide-out drawer for system shortcuts — replaces the modal-based
 * SystemShortcutsPanel with a consistent drawer pattern matching
 * Route to All, Theme Style, and Settings drawers.
 *
 * Features:
 * - List all system shortcuts grouped by category
 * - One-click execute
 * - Toggle favorite (for Quick Actions / Dashboard)
 * - Rename inline
 * - Edit shortcut (params) inline
 * - Pin to dashboard
 */

class ShortcutsDrawer {
    constructor() {
        this.isOpen = false;
        this.container = null;
        this.backdrop = null;
        this.shortcuts = [];
        this.editingId = null;

        // Subscribe to state changes
        state.on('systemShortcuts', () => this.render());

        // Create drawer
        this.createDrawer();
    }

    createDrawer() {
        // Backdrop
        const backdrop = document.createElement('div');
        backdrop.id = 'shortcuts-backdrop';
        backdrop.className = 'routing-backdrop';
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
        drawer.id = 'shortcuts-drawer';
        drawer.className = 'routing-drawer';
        drawer.innerHTML = `
            <div class="drawer-header">
                <h3>
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                    </svg>
                    System Shortcuts
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
            <div class="drawer-content" id="shortcuts-content">
                <p class="loading-hint">Loading shortcuts...</p>
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

        // Pin to dashboard button
        drawer.querySelector('.drawer-pin-dashboard-btn')?.addEventListener('click', () => this.toggleDashboardPin());

        // Back to Control Deck button
        drawer.querySelector('.back-to-deck-btn')?.addEventListener('click', () => {
            this.close();
            if (window.sideNavDrawer) {
                window.sideNavDrawer.open();
            }
        });

        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    open() {
        if (window.overlayManager) {
            window.overlayManager.onOpen('shortcuts-drawer');
        }
        this.isOpen = true;
        this.container.classList.add('open');
        this.backdrop.classList.add('open');
        document.body.style.overflow = 'hidden';
        this.updateDashboardButton();
        this.loadShortcuts();
    }

    close() {
        if (window.overlayManager) {
            window.overlayManager.onClose('shortcuts-drawer');
        }
        this.isOpen = false;
        this.container.classList.remove('open');
        this.backdrop.classList.remove('open');
        document.body.style.overflow = '';
        this.editingId = null;
    }

    toggle() {
        if (this.isOpen) this.close();
        else this.open();
    }

    async loadShortcuts() {
        try {
            const result = await api.listSystemShortcuts();
            this.shortcuts = result.data?.shortcuts || result.shortcuts || [];
            this.render();
        } catch (err) {
            const content = document.getElementById('shortcuts-content');
            if (content) content.innerHTML = '<p class="error-hint">Failed to load shortcuts.</p>';
        }
    }

    render() {
        if (!this.isOpen) return;
        const content = document.getElementById('shortcuts-content');
        if (!content) return;

        if (this.shortcuts.length === 0) {
            content.innerHTML = '<p class="empty-hint">No system shortcuts configured.</p>';
            return;
        }

        // Group by category
        const groups = {};
        this.shortcuts.forEach(sc => {
            const cat = sc.category || 'other';
            if (!groups[cat]) groups[cat] = [];
            groups[cat].push(sc);
        });

        const categoryLabels = {
            routing: 'Routing',
            presets: 'Presets',
            system: 'System',
            other: 'Other',
        };

        let html = '';
        for (const [cat, items] of Object.entries(groups)) {
            html += `
                <div class="drawer-section">
                    <h4 class="drawer-section-title">${categoryLabels[cat] || cat}</h4>
                    <div class="shortcuts-list">
                        ${items.map(sc => this.renderShortcut(sc)).join('')}
                    </div>
                </div>
            `;
        }

        content.innerHTML = html;
        this.attachEventListeners(content);
    }

    renderShortcut(sc) {
        const isFavorite = sc.favorite === true;
        const isDashboard = sc.dashboard_visible === true;
        const isEditing = this.editingId === sc.id;

        return `
            <div class="shortcut-row" data-shortcut-id="${Helpers.escapeHtml(sc.id)}">
                <div class="shortcut-icon">${sc.icon || '⚡'}</div>
                <div class="shortcut-body">
                    ${isEditing ? `
                        <input type="text" class="shortcut-rename-input" value="${Helpers.escapeHtml(sc.label || sc.name || sc.id)}" maxlength="40">
                    ` : `
                        <div class="shortcut-name">${Helpers.escapeHtml(sc.label || sc.name || sc.id)}</div>
                        <div class="shortcut-type">${Helpers.escapeHtml(sc.type || '')}</div>
                    `}
                </div>
                <div class="shortcut-actions">
                    ${isEditing ? `
                        <button class="btn-icon shortcut-save-btn" data-id="${Helpers.escapeHtml(sc.id)}" title="Save">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="20 6 9 17 4 12"/>
                            </svg>
                        </button>
                        <button class="btn-icon shortcut-cancel-btn" title="Cancel">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                        </button>
                    ` : `
                        <button class="btn-icon shortcut-edit-btn" data-id="${Helpers.escapeHtml(sc.id)}" title="Rename">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                            </svg>
                        </button>
                        <button class="btn-icon shortcut-fav-btn ${isFavorite ? 'active' : ''}" data-id="${Helpers.escapeHtml(sc.id)}" title="${isFavorite ? 'Remove from favorites' : 'Add to favorites'}">
                            <svg class="icon" viewBox="0 0 24 24" fill="${isFavorite ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                            </svg>
                        </button>
                        <button class="btn-icon shortcut-dashboard-btn ${isDashboard ? 'active' : ''}" data-id="${Helpers.escapeHtml(sc.id)}" title="${isDashboard ? 'Remove from dashboard' : 'Pin to dashboard'}">
                            <svg class="icon" viewBox="0 0 24 24" fill="${isDashboard ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                                <rect x="3" y="3" width="18" height="18" rx="2"/>
                                <line x1="9" y1="3" x2="9" y2="21"/>
                                <line x1="15" y1="3" x2="15" y2="21"/>
                                <line x1="3" y1="9" x2="21" y2="9"/>
                                <line x1="3" y1="15" x2="21" y2="15"/>
                            </svg>
                        </button>
                        <button class="btn-icon shortcut-execute-btn" data-id="${Helpers.escapeHtml(sc.id)}" title="Execute">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="5 3 19 12 5 21 5 3"/>
                            </svg>
                        </button>
                    `}
                </div>
            </div>
        `;
    }

    attachEventListeners(content) {
        // Edit / rename
        content.querySelectorAll('.shortcut-edit-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.editingId = btn.dataset.id;
                this.render();
            });
        });

        // Cancel edit
        content.querySelectorAll('.shortcut-cancel-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.editingId = null;
                this.render();
            });
        });

        // Save rename
        content.querySelectorAll('.shortcut-save-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.dataset.id;
                const input = content.querySelector(`.shortcut-row[data-shortcut-id="${id}"] .shortcut-rename-input`);
                const newName = input ? input.value.trim() : '';
                if (!newName) return;
                try {
                    await api.updateSystemShortcut(id, { label: newName });
                    await this.loadShortcuts();
                    this.editingId = null;
                    toast.success('Shortcut renamed');
                } catch (err) {
                    toast.error('Failed to rename shortcut');
                }
            });
        });

        // Execute
        content.querySelectorAll('.shortcut-execute-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.dataset.id;
                try {
                    await api.executeSystemShortcut(id);
                    toast.success('Shortcut executed');
                } catch (err) {
                    toast.error('Failed to execute shortcut');
                }
            });
        });

        // Toggle favorite
        content.querySelectorAll('.shortcut-fav-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.dataset.id;
                try {
                    await api.toggleSystemShortcutFavorite(id);
                    await this.loadShortcuts();
                    if (state.loadAllFavorites) state.loadAllFavorites();
                } catch (err) {
                    toast.error('Failed to toggle favorite');
                }
            });
        });

        // Toggle dashboard
        content.querySelectorAll('.shortcut-dashboard-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.dataset.id;
                try {
                    await api.toggleSystemShortcutDashboard(id);
                    await this.loadShortcuts();
                } catch (err) {
                    toast.error('Failed to toggle dashboard pin');
                }
            });
        });

        // Pressing Enter in rename input saves
        content.querySelectorAll('.shortcut-rename-input').forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const row = input.closest('.shortcut-row');
                    const saveBtn = row?.querySelector('.shortcut-save-btn');
                    saveBtn?.click();
                } else if (e.key === 'Escape') {
                    e.preventDefault();
                    const row = input.closest('.shortcut-row');
                    const cancelBtn = row?.querySelector('.shortcut-cancel-btn');
                    cancelBtn?.click();
                }
            });
        });
    }

    isPinnedToDashboard() {
        return window.dashboardManager && window.dashboardManager.isWidgetPinned('shortcuts-drawer');
    }

    toggleDashboardPin() {
        if (window.dashboardManager) {
            const isPinned = this.isPinnedToDashboard();
            if (isPinned) {
                window.dashboardManager.removeWidget('shortcuts-drawer');
                toast.success('Removed from dashboard');
            } else {
                window.dashboardManager.addWidget({
                    id: 'shortcuts-drawer',
                    name: 'Shortcuts',
                    icon: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`,
                    render: () => this.renderWidgetContent(),
                    onMount: (el) => this.attachWidgetEventListeners(el),
                    onUnmount: () => {},
                    component: this,
                });
                toast.success('Pinned to dashboard');
            }
            this.updateDashboardButton();
        }
    }

    updateDashboardButton() {
        const btn = this.container?.querySelector('.drawer-pin-dashboard-btn');
        if (!btn) return;
        const isPinned = this.isPinnedToDashboard();
        btn.title = isPinned ? 'Hide from dashboard' : 'Pin to dashboard';
        if (isPinned) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    }

    renderWidgetContent() {
        // Compact view for dashboard widget
        const shortcuts = this.shortcuts;
        if (!shortcuts || shortcuts.length === 0) {
            return '<p class="widget-empty">No shortcuts configured.</p>';
        }
        let html = '<div class="shortcuts-widget-grid">';
        shortcuts.slice(0, 8).forEach(sc => {
            html += `
                <button class="shortcut-widget-btn" data-id="${Helpers.escapeHtml(sc.id)}" title="${Helpers.escapeHtml(sc.label || sc.name || sc.id)}">
                    <span class="shortcut-icon">${sc.icon || '⚡'}</span>
                    <span class="shortcut-label">${Helpers.escapeHtml(sc.label || sc.name || sc.id)}</span>
                </button>
            `;
        });
        html += '</div>';
        return html;
    }

    attachWidgetEventListeners(el) {
        if (!el) return;
        el.querySelectorAll('.shortcut-widget-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.dataset.id;
                try {
                    await api.executeSystemShortcut(id);
                } catch (err) {
                    toast.error('Failed to execute shortcut');
                }
            });
        });
    }
}

// Create global instance
window.shortcutsDrawer = new ShortcutsDrawer();