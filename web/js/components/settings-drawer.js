/**
 * OREI Matrix Control - Settings Drawer Component (Phase 8)
 * Unified tabbed drawer replacing Quick Actions drawer.
 * Tabs: Profiles | Scenes | System
 */

class SettingsDrawer {
    constructor() {
        this.isOpen = false;
        this.container = null;
        this.backdrop = null;
        this.activeTab = 'profiles';

        // Subscribe to state changes
        state.on('profiles', () => this.render());
        state.on('phase8Scenes', () => this.render());
        state.on('systemActions', () => this.render());
        state.on('favorites', () => this.render());

        // Create drawer elements
        this.createDrawer();
    }

    createDrawer() {
        // Create backdrop
        this.backdrop = document.createElement('div');
        this.backdrop.className = 'drawer-backdrop';
        this.backdrop.addEventListener('click', () => this.close());
        document.body.appendChild(this.backdrop);

        // Create drawer container
        this.container = document.createElement('div');
        this.container.className = 'settings-drawer';
        this.container.id = 'settings-drawer';
        this.container.innerHTML = `
            <div class="drawer-header">
                <h2 class="drawer-title">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                    </svg>
                    Settings
                </h2>
                <button class="drawer-close-btn" aria-label="Close">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
            <div class="drawer-tabs">
                <button class="drawer-tab-btn active" data-tab="profiles">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/>
                    </svg>
                    Profiles
                </button>
                <button class="drawer-tab-btn" data-tab="scenes">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/><line x1="15" y1="3" x2="15" y2="21"/>
                    </svg>
                    Scenes
                </button>
                <button class="drawer-tab-btn" data-tab="system">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                    </svg>
                    System
                </button>
            </div>
            <div class="drawer-content" id="settings-drawer-content">
                <!-- Tab content rendered dynamically -->
            </div>
        `;

        // Tab switching
        this.container.querySelectorAll('.drawer-tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.activeTab = btn.dataset.tab;
                this.container.querySelectorAll('.drawer-tab-btn').forEach(b => b.classList.toggle('active', b === btn));
                this.render();
            });
        });

        // Close button
        this.container.querySelector('.drawer-close-btn').addEventListener('click', () => this.close());

        document.body.appendChild(this.container);
    }

    open() {
        this.isOpen = true;
        this.container.classList.add('open');
        this.backdrop.classList.add('open');
        document.body.style.overflow = 'hidden';
        this.render();
    }

    close() {
        this.isOpen = false;
        this.container.classList.remove('open');
        this.backdrop.classList.remove('open');
        document.body.style.overflow = '';
    }

    toggle() {
        if (this.isOpen) this.close();
        else this.open();
    }

    render() {
        if (!this.isOpen) return;
        const content = this.container.querySelector('#settings-drawer-content');
        if (!content) return;

        switch (this.activeTab) {
            case 'profiles': content.innerHTML = this.renderProfilesTab(); break;
            case 'scenes': content.innerHTML = this.renderScenesTab(); break;
            case 'system': content.innerHTML = this.renderSystemTab(); break;
        }

        this.attachEventListeners(content);
    }

    renderProfilesTab() {
        const profiles = state.profiles || [];
        if (profiles.length === 0) {
            return `<div class="drawer-empty">
                <p>No profiles yet. Create one in the Profiles panel.</p>
            </div>`;
        }

        let html = `<div class="drawer-section-title">All Profiles</div>
            <div class="settings-list">`;

        profiles.forEach(profile => {
            const isProtected = profile.password_protected;
            const isFavorite = state.favoriteProfiles?.some(p => p.id === profile.id);
            html += `
                <div class="settings-list-item" data-profile-id="${profile.id}">
                    <div class="item-info">
                        ${isProtected ? `<svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                        </svg>` : ''}
                        <span class="item-name">${Helpers.escapeHtml(profile.name || profile.id)}</span>
                    </div>
                    <div class="item-actions">
                        <button class="btn-icon execute-profile-btn" data-id="${profile.id}" title="Execute">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="5 3 19 12 5 21 5 3"/>
                            </svg>
                        </button>
                        <button class="btn-icon toggle-fav-btn ${isFavorite ? 'active' : ''}" data-id="${profile.id}" title="${isFavorite ? 'Remove from favorites' : 'Add to favorites'}">
                            <svg class="icon" viewBox="0 0 24 24" fill="${isFavorite ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                            </svg>
                        </button>
                    </div>
                </div>`;
        });

        html += `</div>`;
        return html;
    }

    renderScenesTab() {
        const scenes = state.phase8Scenes || [];
        if (scenes.length === 0) {
            return `<div class="drawer-empty">
                <p>No scenes yet.</p>
                <button class="btn btn-primary create-scene-btn">Create Scene</button>
            </div>`;
        }

        let html = `<div class="drawer-section-title">All Scenes
            <button class="btn btn-sm btn-primary create-scene-btn">+ New</button>
        </div>
            <div class="settings-list">`;

        scenes.forEach(scene => {
            const isProtected = scene.password_protected;
            const stepCount = scene.steps?.length || 0;
            html += `
                <div class="settings-list-item" data-scene-id="${scene.id}">
                    <div class="item-info">
                        ${isProtected ? `<svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                        </svg>` : ''}
                        <span class="item-name">${Helpers.escapeHtml(scene.name)}</span>
                        <span class="item-meta">${stepCount} step${stepCount !== 1 ? 's' : ''}</span>
                    </div>
                    <div class="item-actions">
                        <button class="btn-icon execute-scene-btn" data-id="${scene.id}" title="Execute">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="5 3 19 12 5 21 5 3"/>
                            </svg>
                        </button>
                        <button class="btn-icon edit-scene-btn" data-id="${scene.id}" title="Edit">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                            </svg>
                        </button>
                        <button class="btn-icon delete-scene-btn" data-id="${scene.id}" title="Delete">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                        </button>
                    </div>
                </div>`;
        });

        html += `</div>`;
        return html;
    }

    renderSystemTab() {
        const actions = state.systemActions || [];
        if (actions.length === 0) {
            return `<div class="drawer-empty">
                <p>No system actions available.</p>
            </div>`;
        }

        let html = `<div class="drawer-section-title">System Actions</div>
            <div class="settings-list">`;

        actions.forEach(action => {
            html += `
                <div class="settings-list-item" data-action-key="${action.key}">
                    <div class="item-info">
                        <span class="item-name">${Helpers.escapeHtml(action.name || action.key)}</span>
                        ${action.description ? `<span class="item-meta">${Helpers.escapeHtml(action.description)}</span>` : ''}
                    </div>
                    <div class="item-actions">
                        <button class="btn-icon execute-action-btn" data-key="${action.key}" title="Execute">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="5 3 19 12 5 21 5 3"/>
                            </svg>
                        </button>
                    </div>
                </div>`;
        });

        html += `</div>`;
        return html;
    }

    attachEventListeners(content) {
        // Profile execute
        content.querySelectorAll('.execute-profile-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const id = btn.dataset.id;
                try {
                    await api.executeProfile(id);
                    toast.success('Profile executed');
                } catch (err) {
                    if (err.status === 401) {
                        this.showPasscodePrompt('profile', id);
                    } else {
                        toast.error('Failed to execute profile');
                    }
                }
            });
        });

        // Profile favorite toggle
        content.querySelectorAll('.toggle-fav-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const id = btn.dataset.id;
                await window.api.toggleProfileFavorite(id);
                state.loadAllFavorites();
            });
        });

        // Scene execute
        content.querySelectorAll('.execute-scene-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const id = btn.dataset.id;
                try {
                    const result = await api.executeScene(id);
                    if (result.success) {
                        toast.success('Scene executed');
                    }
                } catch (err) {
                    if (err.status === 401) {
                        this.showPasscodePrompt('scene', id);
                    } else {
                        toast.error('Failed to execute scene');
                    }
                }
            });
        });

        // Scene edit
        content.querySelectorAll('.edit-scene-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = btn.dataset.id;
                if (window.sceneEditor) {
                    window.sceneEditor.open(id);
                }
            });
        });

        // Scene delete
        content.querySelectorAll('.delete-scene-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const id = btn.dataset.id;
                if (confirm('Delete this scene?')) {
                    await api.deleteScene(id);
                    state.loadPhase8Scenes();
                    toast.success('Scene deleted');
                }
            });
        });

        // Create scene
        content.querySelectorAll('.create-scene-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (window.sceneEditor) {
                    window.sceneEditor.open(null);
                }
            });
        });

        // System action execute
        content.querySelectorAll('.execute-action-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const key = btn.dataset.key;
                try {
                    await api.executeSystemAction(key);
                    toast.success('Action executed');
                } catch (err) {
                    toast.error('Failed to execute action');
                }
            });
        });
    }

    showPasscodePrompt(type, id) {
        const passcode = prompt('This scene is password protected. Enter passcode:');
        if (!passcode) return;

        if (type === 'scene') {
            api.executeScene(id, { passcode }).then(() => toast.success('Scene executed')).catch(() => toast.error('Invalid passcode'));
        } else {
            api.executeProfile(id, { passcode }).then(() => toast.success('Profile executed')).catch(() => toast.error('Invalid passcode'));
        }
    }
}

// Create global instance
window.settingsDrawer = new SettingsDrawer();
