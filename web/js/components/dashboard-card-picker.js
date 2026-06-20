/**
 * OREI Matrix Control - Dashboard Card Picker
 * Modal for adding cards to the dashboard (Phase 7)
 */

class DashboardCardPicker {
    constructor() {
        this.modal = null;
    }

    /**
     * Create the modal DOM
     */
    createModal() {
        this.modal = document.createElement('div');
        this.modal.id = 'dashboard-card-picker';
        this.modal.className = 'settings-modal-overlay';
        this.modal.setAttribute('aria-hidden', 'true');

        this.modal.innerHTML = `
            <div class="settings-modal dashboard-card-picker-modal">
                <div class="settings-modal-header">
                    <h3>
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="7" height="9" rx="1"/>
                            <rect x="14" y="3" width="7" height="5" rx="1"/>
                            <rect x="14" y="12" width="7" height="9" rx="1"/>
                            <rect x="3" y="16" width="7" height="5" rx="1"/>
                        </svg>
                        Add Card to Dashboard
                    </h3>
                    <button class="modal-close-btn" title="Close">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="settings-modal-body">
                    <p class="section-help">Select an item to add to your dashboard.</p>
                    <div class="picker-tabs">
                        <button class="picker-tab-btn active" data-tab="profiles">Profiles</button>
                        <button class="picker-tab-btn" data-tab="presets">Presets</button>
                        <button class="picker-tab-btn" data-tab="shortcuts">Shortcuts</button>
                        <button class="picker-tab-btn" data-tab="macros">Macros</button>
                    </div>
                    <div class="picker-content" id="picker-content">
                        <!-- Content rendered dynamically -->
                    </div>
                </div>
                <div class="settings-modal-footer">
                    <button class="btn btn-secondary" id="close-picker-btn">Cancel</button>
                </div>
            </div>
        `;

        document.body.appendChild(this.modal);
        this.attachEventListeners();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        this.modal.querySelector('.modal-close-btn').addEventListener('click', () => this.close());
        this.modal.querySelector('#close-picker-btn').addEventListener('click', () => this.close());

        // Click outside to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });

        // Tab switching
        this.modal.querySelectorAll('.picker-tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.modal.querySelectorAll('.picker-tab-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.renderTab(e.target.dataset.tab);
            });
        });

        // Escape to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.getAttribute('aria-hidden') === 'false') {
                this.close();
            }
        });
    }

    /**
     * Open the picker modal
     */
    open() {
        if (!this.modal) {
            this.createModal();
        }

        this.modal.setAttribute('aria-hidden', 'false');
        this.modal.classList.add('visible');
        document.body.style.overflow = 'hidden';

        // Default to profiles tab
        this.renderTab('profiles');
    }

    /**
     * Close the picker modal
     */
    close() {
        this.modal.setAttribute('aria-hidden', 'true');
        this.modal.classList.remove('visible');
        document.body.style.overflow = '';
    }

    /**
     * Get set of card keys already on dashboard
     */
    getCurrentCardKeys() {
        const keys = new Set();
        const cards = window.state.dashboardCards || [];
        cards.forEach(card => {
            if (card.type === 'aggregate_widget') {
                keys.add(`${card.type}:${card.widget_id}`);
            } else {
                keys.add(`${card.type}:${card.id}`);
            }
        });
        return keys;
    }

    /**
     * Render a specific tab
     */
    renderTab(tab) {
        const container = this.modal.querySelector('#picker-content');
        const currentKeys = this.getCurrentCardKeys();

        if (tab === 'profiles') {
            this.renderProfiles(container, currentKeys);
        } else if (tab === 'presets') {
            this.renderPresets(container, currentKeys);
        } else if (tab === 'shortcuts') {
            this.renderShortcuts(container, currentKeys);
        } else if (tab === 'macros') {
            this.renderMacros(container, currentKeys);
        }
    }

    /**
     * Render profiles tab
     */
    renderProfiles(container, currentKeys) {
        const profiles = window.state.profiles || [];

        if (profiles.length === 0) {
            container.innerHTML = '<p class="empty-message">No profiles available.</p>';
            return;
        }

        const html = profiles.map(profile => {
            const key = `profile:${profile.id}`;
            const isAdded = currentKeys.has(key);

            return `
                <div class="picker-item ${isAdded ? 'added' : ''}" data-type="profile" data-id="${profile.id}">
                    <span class="picker-item-icon">${profile.icon || '🎬'}</span>
                    <span class="picker-item-name">${Helpers.escapeHtml(profile.name)}</span>
                    ${isAdded
                        ? '<span class="picker-item-badge">Added</span>'
                        : `<button class="btn btn-sm btn-primary picker-add-btn" data-type="profile" data-id="${profile.id}">Add</button>`
                    }
                </div>
            `;
        }).join('');

        container.innerHTML = html;
        this.attachPickerListeners(container);
    }

    /**
     * Render presets tab
     */
    renderPresets(container, currentKeys) {
        let html = '';

        for (let i = 1; i <= 8; i++) {
            const preset = window.state.presets[i] || { name: `Preset ${i}` };
            const key = `preset:${i}`;
            const isAdded = currentKeys.has(key);

            html += `
                <div class="picker-item ${isAdded ? 'added' : ''}" data-type="preset" data-id="${i}">
                    <span class="picker-item-icon">⚡</span>
                    <span class="picker-item-name">${Helpers.escapeHtml(preset.name)}</span>
                    ${isAdded
                        ? '<span class="picker-item-badge">Added</span>'
                        : `<button class="btn btn-sm btn-primary picker-add-btn" data-type="preset" data-id="${i}">Add</button>`
                    }
                </div>
            `;
        }

        container.innerHTML = html;
        this.attachPickerListeners(container);
    }

    /**
     * Render shortcuts tab
     */
    renderShortcuts(container, currentKeys) {
        const shortcuts = window.state.systemShortcuts || [];

        if (shortcuts.length === 0) {
            container.innerHTML = '<p class="empty-message">No shortcuts available.</p>';
            return;
        }

        const html = shortcuts
            .filter(s => s.enabled !== false) // Only show enabled shortcuts
            .map(shortcut => {
                const key = `system_shortcut:${shortcut.id}`;
                const isAdded = currentKeys.has(key);

                return `
                    <div class="picker-item ${isAdded ? 'added' : ''}" data-type="system_shortcut" data-id="${shortcut.id}">
                        <span class="picker-item-icon">${shortcut.icon || '⚡'}</span>
                        <span class="picker-item-name">${Helpers.escapeHtml(shortcut.name)}</span>
                        ${isAdded
                            ? '<span class="picker-item-badge">Added</span>'
                            : `<button class="btn btn-sm btn-primary picker-add-btn" data-type="system_shortcut" data-id="${shortcut.id}">Add</button>`
                        }
                    </div>
                `;
            }).join('');

        container.innerHTML = html;
        this.attachPickerListeners(container);
    }

    /**
     * Render macros tab
     */
    renderMacros(container, currentKeys) {
        const macros = window.state.cecMacros || [];

        if (macros.length === 0) {
            container.innerHTML = '<p class="empty-message">No macros available.</p>';
            return;
        }

        const html = macros.map(macro => {
            const key = `macro:${macro.id}`;
            const isAdded = currentKeys.has(key);

            return `
                <div class="picker-item ${isAdded ? 'added' : ''}" data-type="macro" data-id="${macro.id}">
                    <span class="picker-item-icon">${macro.icon || '⚡'}</span>
                    <span class="picker-item-name">${Helpers.escapeHtml(macro.name)}</span>
                    ${isAdded
                        ? '<span class="picker-item-badge">Added</span>'
                        : `<button class="btn btn-sm btn-primary picker-add-btn" data-type="macro" data-id="${macro.id}">Add</button>`
                    }
                </div>
            `;
        }).join('');

        container.innerHTML = html;
        this.attachPickerListeners(container);
    }

    /**
     * Attach click listeners to picker items
     */
    attachPickerListeners(container) {
        container.querySelectorAll('.picker-add-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const type = e.target.dataset.type;
                const id = e.target.dataset.id;

                try {
                    await window.api.addDashboardCard(type, id);
                    toast.success('Card added to dashboard');

                    // Reload dashboard layout
                    await window.state.loadDashboardLayout();

                    // Re-render the current tab
                    this.renderTab(this.modal.querySelector('.picker-tab-btn.active').dataset.tab);

                    // Refresh dashboard
                    if (window.dashboardManager) {
                        window.dashboardManager.renderCards();
                    }
                } catch (error) {
                    toast.error(`Failed to add card: ${error.message}`);
                }
            });
        });
    }
}

// Create global instance
window.dashboardCardPicker = new DashboardCardPicker();
