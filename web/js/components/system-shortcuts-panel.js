/**
 * OREI Matrix Control - System Shortcuts Panel
 * Management UI for system shortcuts (Phase 7)
 * Allows users to rename, reorder, enable/disable, favorite, and delete shortcuts.
 */

class SystemShortcutsPanel {
    constructor() {
        this.modal = null;
        this.shortcuts = [];
        this.listeners = [];
    }

    /**
     * Create the modal DOM
     */
    createModal() {
        this.modal = document.createElement('div');
        this.modal.id = 'system-shortcuts-panel';
        this.modal.className = 'settings-modal-overlay';
        this.modal.setAttribute('aria-hidden', 'true');

        this.modal.innerHTML = `
            <div class="settings-modal system-shortcuts-modal">
                <div class="settings-modal-header">
                    <h3>
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                        </svg>
                        System Shortcuts
                    </h3>
                    <button class="modal-close-btn" title="Close">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="settings-modal-body system-shortcuts-body">
                    <p class="section-help">
                        Configure system shortcuts for quick access. Shortcuts can be added to Quick Actions and the Dashboard.
                    </p>
                    <div class="shortcuts-list" id="shortcuts-list">
                        <p class="empty-message">Loading shortcuts...</p>
                    </div>
                </div>
                <div class="settings-modal-footer">
                    <button class="btn btn-secondary" id="add-shortcut-btn">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="12" y1="5" x2="12" y2="19"/>
                            <line x1="5" y1="12" x2="19" y2="12"/>
                        </svg>
                        Add Shortcut
                    </button>
                    <div class="action-spacer"></div>
                    <button class="btn btn-primary" id="close-shortcuts-btn">Done</button>
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
        this.modal.querySelector('#close-shortcuts-btn').addEventListener('click', () => this.close());
        this.modal.querySelector('#add-shortcut-btn').addEventListener('click', () => this.showAddForm());

        // Click outside to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });

        // Escape to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.getAttribute('aria-hidden') === 'false') {
                this.close();
            }
        });
    }

    /**
     * Open the panel
     */
    async open() {
        if (!this.modal) {
            this.createModal();
        }

        this.modal.setAttribute('aria-hidden', 'false');
        this.modal.classList.add('visible');
        document.body.style.overflow = 'hidden';

        await this.loadShortcuts();
        this.render();
    }

    /**
     * Close the panel
     */
    close() {
        this.modal.setAttribute('aria-hidden', 'true');
        this.modal.classList.remove('visible');
        document.body.style.overflow = '';
    }

    /**
     * Load shortcuts from server
     */
    async loadShortcuts() {
        try {
            const result = await window.api.listSystemShortcuts();
            if (result?.success) {
                this.shortcuts = result.data?.shortcuts || [];
            } else {
                this.shortcuts = [];
            }
        } catch (error) {
            console.error('Failed to load shortcuts:', error);
            this.shortcuts = [];
        }
    }

    /**
     * Render the shortcuts list
     */
    render() {
        const container = this.modal.querySelector('#shortcuts-list');
        if (!container) return;

        if (this.shortcuts.length === 0) {
            container.innerHTML = `
                <p class="empty-message">No shortcuts configured.</p>
            `;
            return;
        }

        let html = '';
        this.shortcuts.forEach((shortcut, index) => {
            const isBuiltIn = shortcut.builtin === true;
            const canDelete = !isBuiltIn;
            const canDisable = !isBuiltIn;

            html += `
                <div class="shortcut-item" data-id="${shortcut.id}">
                    <div class="shortcut-item-header">
                        <div class="shortcut-icon-preview" data-shortcut-icon="${shortcut.id}">
                            ${shortcut.icon || '⚡'}
                        </div>
                        <div class="shortcut-item-info">
                            <input type="text" class="shortcut-name-input"
                                value="${Helpers.escapeHtml(shortcut.name || '')}"
                                data-shortcut-id="${shortcut.id}"
                                ${isBuiltIn ? 'readonly' : ''}
                                placeholder="Shortcut name" />
                            <span class="shortcut-id-hint">${shortcut.id}</span>
                        </div>
                        <div class="shortcut-item-actions">
                            <button class="btn-icon shortcut-icon-btn"
                                data-shortcut-id="${shortcut.id}"
                                title="Change icon"
                                ${isBuiltIn ? 'style="display:none"' : ''}>
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="10"/>
                                    <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                                    <line x1="9" y1="9" x2="9.01" y2="9"/>
                                    <line x1="15" y1="9" x2="15.01" y2="9"/>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <div class="shortcut-item-toggles">
                        <label class="toggle-label-inline">
                            <input type="checkbox" class="shortcut-enabled-toggle"
                                data-shortcut-id="${shortcut.id}"
                                ${shortcut.enabled !== false ? 'checked' : ''}
                                ${canDisable ? '' : 'disabled'} />
                            <span>Enabled</span>
                        </label>
                        <label class="toggle-label-inline">
                            <input type="checkbox" class="shortcut-favorite-toggle"
                                data-shortcut-id="${shortcut.id}"
                                ${shortcut.favorite ? 'checked' : ''} />
                            <span>Quick Actions</span>
                        </label>
                        <label class="toggle-label-inline">
                            <input type="checkbox" class="shortcut-dashboard-toggle"
                                data-shortcut-id="${shortcut.id}"
                                ${shortcut.dashboard_visible ? 'checked' : ''} />
                            <span>Dashboard</span>
                        </label>
                    </div>
                    <div class="shortcut-item-footer">
                        <button class="btn btn-sm btn-secondary shortcut-execute-btn"
                            data-shortcut-id="${shortcut.id}">
                            Execute
                        </button>
                        <div class="shortcut-order-btns">
                            <button class="btn-icon shortcut-order-up"
                                data-shortcut-id="${shortcut.id}"
                                data-index="${index}"
                                title="Move up"
                                ${index === 0 ? 'disabled' : ''}>
                                <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="18 15 12 9 6 15"/>
                                </svg>
                            </button>
                            <button class="btn-icon shortcut-order-down"
                                data-shortcut-id="${shortcut.id}"
                                data-index="${index}"
                                title="Move down"
                                ${index === this.shortcuts.length - 1 ? 'disabled' : ''}>
                                <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="6 9 12 15 18 9"/>
                                </svg>
                            </button>
                        </div>
                        <button class="btn btn-sm btn-danger shortcut-delete-btn"
                            data-shortcut-id="${shortcut.id}"
                            ${canDelete ? '' : 'style="display:none"'}
                            title="${isBuiltIn ? 'Built-in shortcuts cannot be deleted' : 'Delete shortcut'}">
                            Delete
                        </button>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
        this.attachShortcutEventListeners();
    }

    /**
     * Attach event listeners to rendered shortcut items
     */
    attachShortcutEventListeners() {
        const container = this.modal.querySelector('#shortcuts-list');
        if (!container) return;

        // Name input (save on blur)
        container.querySelectorAll('.shortcut-name-input').forEach(input => {
            input.addEventListener('blur', async (e) => {
                const shortcutId = e.target.dataset.shortcutId;
                const newName = e.target.value.trim();
                const shortcut = this.shortcuts.find(s => s.id === shortcutId);
                if (shortcut && newName && newName !== shortcut.name) {
                    try {
                        await window.api.updateSystemShortcut(shortcutId, { name: newName });
                        shortcut.name = newName;
                        toast.success('Shortcut renamed');
                    } catch (error) {
                        toast.error(`Failed to rename: ${error.message}`);
                        e.target.value = shortcut.name || '';
                    }
                }
            });
        });

        // Icon button
        container.querySelectorAll('.shortcut-icon-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const shortcutId = e.currentTarget.dataset.shortcutId;
                this.promptForIcon(shortcutId);
            });
        });

        // Enabled toggle
        container.querySelectorAll('.shortcut-enabled-toggle').forEach(toggle => {
            toggle.addEventListener('change', async (e) => {
                const shortcutId = e.target.dataset.shortcutId;
                const enabled = e.target.checked;
                try {
                    await window.api.updateSystemShortcut(shortcutId, { enabled });
                    const shortcut = this.shortcuts.find(s => s.id === shortcutId);
                    if (shortcut) shortcut.enabled = enabled;
                    toast.success(enabled ? 'Shortcut enabled' : 'Shortcut disabled');
                } catch (error) {
                    e.target.checked = !enabled;
                    toast.error(`Failed to update: ${error.message}`);
                }
            });
        });

        // Favorite toggle
        container.querySelectorAll('.shortcut-favorite-toggle').forEach(toggle => {
            toggle.addEventListener('change', async (e) => {
                const shortcutId = e.target.dataset.shortcutId;
                try {
                    await window.api.toggleSystemShortcutFavorite(shortcutId);
                    await this.loadShortcuts();
                    toast.success(e.target.checked ? 'Added to Quick Actions' : 'Removed from Quick Actions');
                    this.render();
                } catch (error) {
                    e.target.checked = !e.target.checked;
                    toast.error(`Failed to update: ${error.message}`);
                }
            });
        });

        // Dashboard toggle
        container.querySelectorAll('.shortcut-dashboard-toggle').forEach(toggle => {
            toggle.addEventListener('change', async (e) => {
                const shortcutId = e.target.dataset.shortcutId;
                try {
                    await window.api.toggleSystemShortcutDashboard(shortcutId);
                    await this.loadShortcuts();
                    toast.success(e.target.checked ? 'Added to Dashboard' : 'Removed from Dashboard');
                    this.render();
                } catch (error) {
                    e.target.checked = !e.target.checked;
                    toast.error(`Failed to update: ${error.message}`);
                }
            });
        });

        // Execute button
        container.querySelectorAll('.shortcut-execute-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const shortcutId = e.currentTarget.dataset.shortcutId;
                try {
                    const result = await window.api.executeSystemShortcut(shortcutId);
                    if (result?.success) {
                        toast.success('Shortcut executed');
                    } else {
                        toast.error(result?.error || 'Failed to execute shortcut');
                    }
                } catch (error) {
                    toast.error(`Error: ${error.message}`);
                }
            });
        });

        // Order up
        container.querySelectorAll('.shortcut-order-up').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const index = parseInt(e.currentTarget.dataset.index);
                if (index > 0) {
                    await this.reorderShortcut(index, index - 1);
                }
            });
        });

        // Order down
        container.querySelectorAll('.shortcut-order-down').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const index = parseInt(e.currentTarget.dataset.index);
                if (index < this.shortcuts.length - 1) {
                    await this.reorderShortcut(index, index + 1);
                }
            });
        });

        // Delete button
        container.querySelectorAll('.shortcut-delete-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const shortcutId = e.currentTarget.dataset.shortcutId;
                const confirmed = await ConfirmDialog.confirm({
                    title: 'Delete Shortcut',
                    message: 'Delete this shortcut? This cannot be undone.',
                    confirmText: 'Delete',
                    cancelText: 'Keep',
                    variant: 'danger'
                });
                if (!confirmed) return;
                try {
                    const result = await window.api.deleteSystemShortcut(shortcutId);
                    if (result?.success) {
                        toast.success('Shortcut deleted');
                        await this.loadShortcuts();
                        this.render();
                    } else {
                        throw new Error(result?.error || 'Failed to delete');
                    }
                } catch (error) {
                    toast.error(`Error: ${error.message}`);
                }
            });
        });
    }

    /**
     * Reorder shortcuts by moving one index to another
     */
    async reorderShortcut(fromIndex, toIndex) {
        // Reorder locally
        const item = this.shortcuts.splice(fromIndex, 1)[0];
        this.shortcuts.splice(toIndex, 0, item);

        // Update data-index attributes on buttons
        const container = this.modal.querySelector('#shortcuts-list');
        container.querySelectorAll('.shortcut-order-up, .shortcut-order-down').forEach((btn, idx) => {
            btn.dataset.index = idx;
            btn.disabled = false;
        });

        // Disable first up and last down
        const upBtns = container.querySelectorAll('.shortcut-order-up');
        const downBtns = container.querySelectorAll('.shortcut-order-down');
        if (upBtns[0]) upBtns[0].disabled = true;
        if (downBtns[downBtns.length - 1]) downBtns[downBtns.length - 1].disabled = true;

        // Save new order to server
        try {
            const orderedIds = this.shortcuts.map(s => s.id);
            await window.api.reorderSystemShortcuts(orderedIds);
        } catch (error) {
            toast.error(`Failed to save order: ${error.message}`);
            // Reload to restore correct order
            await this.loadShortcuts();
            this.render();
        }
    }

    /**
     * Prompt user for a new icon (simple emoji picker)
     */
    promptForIcon(shortcutId) {
        const icons = ['⚡', '📺', '🎬', '🎮', '🎵', '🏠', '💼', '🌙', '☀️', '📽️', '🕹️', '🎧', '📻', '🖥️', '💡', '🔊', '🔌', '📱', '💻', '🎥', '📺', '🖼️', '🎙️', '🔇'];
        const shortcut = this.shortcuts.find(s => s.id === shortcutId);
        if (!shortcut) return;

        const currentIcon = shortcut.icon || '⚡';
        const iconHtml = icons.map(icon =>
            `<button class="icon-option ${icon === currentIcon ? 'selected' : ''}" data-icon="${icon}">${icon}</button>`
        ).join('');

        const popup = document.createElement('div');
        popup.className = 'icon-picker-popup';
        popup.innerHTML = `
            <div class="icon-picker-grid">${iconHtml}</div>
        `;
        popup.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:var(--bg-secondary);border:1px solid var(--border-color);border-radius:8px;padding:12px;z-index:10000;box-shadow:0 4px 20px rgba(0,0,0,0.5);';

        const closePopup = () => popup.remove();

        popup.querySelectorAll('.icon-option').forEach(btn => {
            btn.style.cssText = 'font-size:24px;padding:8px;cursor:pointer;border:2px solid transparent;border-radius:4px;background:transparent;';
            btn.addEventListener('click', async () => {
                const newIcon = btn.dataset.icon;
                try {
                    await window.api.updateSystemShortcut(shortcutId, { icon: newIcon });
                    shortcut.icon = newIcon;
                    // Update icon preview
                    const preview = document.querySelector(`[data-shortcut-icon="${shortcutId}"]`);
                    if (preview) preview.textContent = newIcon;
                    closePopup();
                    toast.success('Icon updated');
                } catch (error) {
                    toast.error(`Failed to update icon: ${error.message}`);
                }
            });
        });

        document.body.appendChild(popup);

        // Close on click outside
        setTimeout(() => {
            document.addEventListener('click', function handler(e) {
                if (!popup.contains(e.target)) {
                    closePopup();
                    document.removeEventListener('click', handler);
                }
            });
        }, 100);
    }

    /**
     * Show add shortcut form (inline in the list)
     */
    showAddForm() {
        const container = this.modal.querySelector('#shortcuts-list');
        const formHtml = `
            <div class="shortcut-item shortcut-add-form" id="shortcut-add-form">
                <div class="shortcut-item-header">
                    <div class="shortcut-icon-preview" style="font-size:24px">⚡</div>
                    <div class="shortcut-item-info">
                        <input type="text" id="new-shortcut-name" class="shortcut-name-input" placeholder="Shortcut name" />
                        <input type="text" id="new-shortcut-id" class="shortcut-name-input" placeholder="shortcut-id" style="font-size:12px;margin-top:4px;" />
                    </div>
                </div>
                <div class="shortcut-item-footer" style="margin-top:8px;">
                    <button class="btn btn-sm btn-primary" id="confirm-add-shortcut">Create</button>
                    <button class="btn btn-sm btn-secondary" id="cancel-add-shortcut">Cancel</button>
                </div>
            </div>
        `;

        // Insert at top of list
        container.insertAdjacentHTML('afterbegin', formHtml);

        const form = document.getElementById('shortcut-add-form');
        const nameInput = document.getElementById('new-shortcut-name');
        const idInput = document.getElementById('new-shortcut-id');
        const confirmBtn = document.getElementById('confirm-add-shortcut');
        const cancelBtn = document.getElementById('cancel-add-shortcut');

        nameInput.focus();

        confirmBtn.addEventListener('click', async () => {
            const name = nameInput.value.trim();
            const id = idInput.value.trim().toLowerCase().replace(/[^a-z0-9_]/g, '_') || 'custom_' + Date.now().toString(36);

            if (!name) {
                toast.warning('Please enter a shortcut name');
                nameInput.focus();
                return;
            }

            try {
                const result = await window.api.updateSystemShortcut(id, { name, icon: '⚡', enabled: true });
                if (result?.success || result?.data) {
                    toast.success('Shortcut created');
                    await this.loadShortcuts();
                    this.render();
                } else {
                    throw new Error(result?.error || 'Failed to create shortcut');
                }
            } catch (error) {
                toast.error(`Error: ${error.message}`);
            }
        });

        cancelBtn.addEventListener('click', () => {
            form.remove();
        });

        idInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') confirmBtn.click();
            if (e.key === 'Escape') cancelBtn.click();
        });

        nameInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') idInput.focus();
        });
    }
}

// Create global instance
window.systemShortcutsPanel = new SystemShortcutsPanel();
