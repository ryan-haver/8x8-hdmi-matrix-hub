/**
 * OREI Matrix Control - Profile Manager Panel
 * 
 * Slide-out panel for managing profile visibility and ordering.
 * Allows users to pin/unpin profiles and reorder pinned profiles.
 */

class ProfileManager {
    constructor() {
        this.isOpen = false;
        this.panel = null;
        this.backdrop = null;
        this.draggedItem = null;
        this.draggedOverItem = null;
        
        this.init();
    }

    /**
     * Initialize the panel
     */
    init() {
        this.createPanel();
        this.attachEventListeners();
        
        // Subscribe to state changes
        state.on('scenes', () => {
            if (this.isOpen) {
                this.renderProfileList();
            }
        });
    }

    /**
     * Create the panel DOM structure
     */
    createPanel() {
        // Create backdrop
        this.backdrop = document.createElement('div');
        this.backdrop.className = 'profile-manager-backdrop';
        this.backdrop.addEventListener('click', () => this.close());
        document.body.appendChild(this.backdrop);
        
        // Create panel
        this.panel = document.createElement('div');
        this.panel.className = 'profile-manager-panel';
        this.panel.innerHTML = `
            <div class="drawer-header">
                <h3>
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="3"/>
                        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                    </svg>
                    Manage Profiles
                </h3>
                <button class="btn-icon drawer-close-btn" title="Close">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
            <div class="drawer-body">
                <div class="profile-manager-info">
                    <span class="pin-count"><span id="pinned-count">0</span>/8 pinned</span>
                    <p class="profile-manager-hint">Drag to reorder. Click pin to show/hide on main screen.</p>
                </div>
                <div class="profile-manager-sections">
                    <div class="profile-manager-section">
                        <h4>Pinned Profiles</h4>
                        <div id="pinned-profiles-list" class="profile-manager-list sortable">
                            <!-- Pinned profiles rendered here -->
                        </div>
                    </div>
                    <div class="profile-manager-section">
                        <h4>Unpinned Profiles</h4>
                        <div id="unpinned-profiles-list" class="profile-manager-list">
                            <!-- Unpinned profiles rendered here -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(this.panel);
        
        // Close button
        this.panel.querySelector('.drawer-close-btn').addEventListener('click', () => this.close());
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Manage button in header
        const manageBtn = document.getElementById('manage-profiles-btn');
        if (manageBtn) {
            manageBtn.addEventListener('click', () => this.open());
        }
    }

    /**
     * Open the panel
     */
    open() {
        this.isOpen = true;
        this.backdrop.classList.add('visible');
        this.panel.classList.add('open');
        this.renderProfileList();
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close the panel
     */
    close() {
        this.isOpen = false;
        this.backdrop.classList.remove('visible');
        this.panel.classList.remove('open');
        document.body.style.overflow = '';
    }

    /**
     * Render the profile lists
     */
    renderProfileList() {
        const pinnedList = this.panel.querySelector('#pinned-profiles-list');
        const unpinnedList = this.panel.querySelector('#unpinned-profiles-list');
        const pinnedCount = this.panel.querySelector('#pinned-count');
        
        // Separate and sort profiles
        const pinned = state.scenes
            .filter(p => p.pinned !== false)
            .sort((a, b) => (a.pin_order || 0) - (b.pin_order || 0));
        
        const unpinned = state.scenes
            .filter(p => p.pinned === false);
        
        pinnedCount.textContent = pinned.length;
        
        // Render pinned profiles
        if (pinned.length === 0) {
            pinnedList.innerHTML = '<p class="empty-message">No pinned profiles</p>';
        } else {
            pinnedList.innerHTML = pinned.map((profile, index) => this.renderProfileItem(profile, true, index)).join('');
            this.attachDragListeners(pinnedList);
        }
        
        // Render unpinned profiles
        if (unpinned.length === 0) {
            unpinnedList.innerHTML = '<p class="empty-message">All profiles are pinned</p>';
        } else {
            unpinnedList.innerHTML = unpinned.map(profile => this.renderProfileItem(profile, false)).join('');
        }
        
        // Attach button listeners
        this.attachProfileButtons();
    }

    /**
     * Render a single profile item
     */
    renderProfileItem(profile, isPinned, index = 0) {
        const icon = profile.icon || '📺';
        const outputCount = profile.output_count || 0;
        
        return `
            <div class="profile-manager-item ${isPinned ? 'pinned' : ''}" 
                 data-profile-id="${profile.id}" 
                 data-pin-order="${profile.pin_order || index}"
                 draggable="${isPinned}">
                ${isPinned ? `
                    <div class="drag-handle" title="Drag to reorder">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="8" y1="6" x2="16" y2="6"/>
                            <line x1="8" y1="12" x2="16" y2="12"/>
                            <line x1="8" y1="18" x2="16" y2="18"/>
                        </svg>
                    </div>
                ` : ''}
                <div class="profile-icon">${icon}</div>
                <div class="profile-info">
                    <span class="profile-name">${Helpers.escapeHtml(profile.name)}</span>
                    <span class="profile-meta">${outputCount} outputs</span>
                </div>
                <div class="profile-actions">
                    <button class="btn-icon pin-toggle-btn ${isPinned ? 'pinned' : ''}" 
                            data-profile-id="${profile.id}"
                            data-pinned="${isPinned}"
                            title="${isPinned ? 'Unpin from main screen' : 'Pin to main screen'}">
                        <svg class="icon" viewBox="0 0 24 24" fill="${isPinned ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                            <path d="M12 2L12 22M12 2L8 6M12 2L16 6M12 22L8 18M12 22L16 18"/>
                        </svg>
                    </button>
                    <button class="btn-icon edit-profile-btn" data-profile-id="${profile.id}" title="Edit profile">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                    </button>
                    <button class="btn-icon delete-profile-btn" data-profile-id="${profile.id}" title="Delete profile">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Attach drag and drop listeners
     */
    attachDragListeners(container) {
        const items = container.querySelectorAll('.profile-manager-item');
        
        items.forEach(item => {
            item.addEventListener('dragstart', (e) => this.handleDragStart(e));
            item.addEventListener('dragend', (e) => this.handleDragEnd(e));
            item.addEventListener('dragover', (e) => this.handleDragOver(e));
            item.addEventListener('drop', (e) => this.handleDrop(e));
            item.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        });
    }

    /**
     * Handle drag start
     */
    handleDragStart(e) {
        this.draggedItem = e.target.closest('.profile-manager-item');
        this.draggedItem.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', this.draggedItem.dataset.profileId);
    }

    /**
     * Handle drag end
     */
    handleDragEnd(e) {
        if (this.draggedItem) {
            this.draggedItem.classList.remove('dragging');
        }
        
        // Remove all drag-over classes
        this.panel.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
        
        this.draggedItem = null;
        this.draggedOverItem = null;
    }

    /**
     * Handle drag over
     */
    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        
        const target = e.target.closest('.profile-manager-item');
        if (target && target !== this.draggedItem) {
            // Remove previous drag-over
            this.panel.querySelectorAll('.drag-over').forEach(el => el.classList.remove('drag-over'));
            target.classList.add('drag-over');
            this.draggedOverItem = target;
        }
    }

    /**
     * Handle drag leave
     */
    handleDragLeave(e) {
        const target = e.target.closest('.profile-manager-item');
        if (target) {
            target.classList.remove('drag-over');
        }
    }

    /**
     * Handle drop
     */
    async handleDrop(e) {
        e.preventDefault();
        
        if (!this.draggedItem || !this.draggedOverItem) return;
        if (this.draggedItem === this.draggedOverItem) return;
        
        const container = this.draggedItem.parentElement;
        const items = Array.from(container.querySelectorAll('.profile-manager-item'));
        
        const draggedIndex = items.indexOf(this.draggedItem);
        const targetIndex = items.indexOf(this.draggedOverItem);
        
        // Reorder in DOM
        if (draggedIndex < targetIndex) {
            this.draggedOverItem.after(this.draggedItem);
        } else {
            this.draggedOverItem.before(this.draggedItem);
        }
        
        // Update pin_order for all pinned profiles
        await this.saveOrder();
    }

    /**
     * Save the current order to the server
     */
    async saveOrder() {
        const pinnedList = this.panel.querySelector('#pinned-profiles-list');
        const items = pinnedList.querySelectorAll('.profile-manager-item');
        
        const profiles = Array.from(items).map((item, index) => ({
            id: item.dataset.profileId,
            pin_order: index,
        }));
        
        try {
            await api.reorderProfiles(profiles);
            
            // Update local state
            profiles.forEach(p => {
                const scene = state.scenes.find(s => s.id === p.id);
                if (scene) {
                    scene.pin_order = p.pin_order;
                }
            });
            
            // Emit change to refresh main UI
            state.emit('scenes', state.scenes);
            
        } catch (error) {
            toast.error('Failed to save order: ' + error.message);
        }
    }

    /**
     * Attach profile action buttons
     */
    attachProfileButtons() {
        // Pin/unpin toggles
        this.panel.querySelectorAll('.pin-toggle-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const profileId = e.currentTarget.dataset.profileId;
                const isPinned = e.currentTarget.dataset.pinned === 'true';
                await this.togglePin(profileId, !isPinned);
            });
        });
        
        // Edit buttons
        this.panel.querySelectorAll('.edit-profile-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const profileId = e.currentTarget.dataset.profileId;
                this.close();
                // Use existing profile editor
                if (window.scenesPanel) {
                    window.scenesPanel.editProfile(profileId);
                }
            });
        });
        
        // Delete buttons
        this.panel.querySelectorAll('.delete-profile-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const profileId = e.currentTarget.dataset.profileId;
                const profile = state.scenes.find(s => s.id === profileId);
                if (profile && confirm(`Delete profile "${profile.name}"?`)) {
                    try {
                        await api.deleteScene(profileId);
                        state.removeScene(profileId);
                        toast.success('Profile deleted');
                    } catch (error) {
                        toast.error('Failed to delete: ' + error.message);
                    }
                }
            });
        });
    }

    /**
     * Toggle pin state for a profile
     */
    async togglePin(profileId, pinned) {
        // Check if we're at max pinned
        if (pinned) {
            const pinnedCount = state.scenes.filter(p => p.pinned !== false).length;
            if (pinnedCount >= 8) {
                toast.error('Maximum 8 profiles can be pinned');
                return;
            }
        }
        
        try {
            // Find next available pin_order
            let pin_order = 0;
            if (pinned) {
                const usedOrders = state.scenes
                    .filter(p => p.pinned !== false)
                    .map(p => p.pin_order || 0);
                for (let i = 0; i < 8; i++) {
                    if (!usedOrders.includes(i)) {
                        pin_order = i;
                        break;
                    }
                }
            }
            
            await api.updateScene(profileId, { pinned, pin_order });
            
            // Update local state
            const scene = state.scenes.find(s => s.id === profileId);
            if (scene) {
                scene.pinned = pinned;
                scene.pin_order = pin_order;
            }
            
            state.emit('scenes', state.scenes);
            this.renderProfileList();
            
            toast.success(pinned ? 'Profile pinned' : 'Profile unpinned');
        } catch (error) {
            toast.error('Failed to update: ' + error.message);
        }
    }

}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.profileManager = new ProfileManager();
});
