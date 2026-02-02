/**
 * OREI Matrix Control - Scenes/Profiles Panel Component
 * 
 * Note: Internally uses "scene" terminology for backward compatibility,
 * but displays "Profile" in user-facing labels.
 */

class ScenesPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        
        // Subscribe to state changes
        state.on('scenes', () => this.render());
        state.on('activeProfile', () => this.render());
    }

    /**
     * Initialize the panel
     */
    init() {
        this.render();
        this.setupModal();
    }

    /**
     * Render the scenes list
     */
    render() {
        // Filter to only show pinned profiles, sorted by pin_order
        const pinnedProfiles = state.scenes
            .filter(p => p.pinned !== false)
            .sort((a, b) => (a.pin_order || 0) - (b.pin_order || 0));
        
        if (pinnedProfiles.length === 0) {
            if (state.scenes.length === 0) {
                this.container.innerHTML = '<p class="empty-message">No profiles yet. Click + to create one.</p>';
            } else {
                this.container.innerHTML = '<p class="empty-message">No pinned profiles. Click ⚙ to manage.</p>';
            }
            return;
        }

        let html = '';
        
        pinnedProfiles.forEach(scene => {
            const outputCount = scene.output_count || Object.keys(scene.outputs || {}).length;
            const icon = scene.icon || '📺';
            const hasMacros = scene.macro_count > 0 || (scene.macros && scene.macros.length > 0) || scene.power_on_macro || scene.power_off_macro;
            const isActive = state.activeProfile && state.activeProfile.id === scene.id;
            
            html += `
                <div class="scene-card ${hasMacros ? 'has-macros' : ''}${isActive ? ' active' : ''}" data-scene-id="${scene.id}">
                    <div class="scene-icon">${icon}</div>
                    <div class="scene-info">
                        <span class="scene-name">${Helpers.escapeHtml(scene.name)}</span>
                        <span class="scene-outputs">${outputCount} outputs</span>
                    </div>
                    <div class="scene-actions">
                        <button class="btn-icon btn-api-copy api-copy-btn" data-scene-id="${scene.id}" data-scene-name="${Helpers.escapeHtml(scene.name)}" title="Get API endpoint for Flic/automation">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                            </svg>
                        </button>
                        <button class="btn-icon edit-scene-btn" data-scene-id="${scene.id}" title="Edit profile">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                            </svg>
                        </button>
                        <button class="btn btn-sm btn-primary recall-scene-btn" data-scene-id="${scene.id}" title="Activate profile">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="5 3 19 12 5 21 5 3"/>
                            </svg>
                        </button>
                        <button class="btn-icon delete-scene-btn" data-scene-id="${scene.id}" title="Delete profile">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"/>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                        </button>
                    </div>
                </div>
            `;
        });
        
        this.container.innerHTML = html;
        this.attachEventListeners();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Recall buttons
        this.container.querySelectorAll('.recall-scene-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const sceneId = e.currentTarget.dataset.sceneId;
                this.recallScene(sceneId);
            });
        });
        
        // API Copy buttons - show API endpoint for Flic/automation
        this.container.querySelectorAll('.api-copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const sceneId = e.currentTarget.dataset.sceneId;
                const sceneName = e.currentTarget.dataset.sceneName;
                if (window.apiCopy) {
                    window.apiCopy.showProfile(sceneId, sceneName);
                } else {
                    toast.error('API copy utility not loaded');
                }
            });
        });
        
        // Edit buttons
        this.container.querySelectorAll('.edit-scene-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const sceneId = e.currentTarget.dataset.sceneId;
                this.editProfile(sceneId);
            });
        });
        
        // Delete buttons
        this.container.querySelectorAll('.delete-scene-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const sceneId = e.currentTarget.dataset.sceneId;
                this.deleteScene(sceneId);
            });
        });
    }
    
    /**
     * Open profile editor for editing
     */
    async editProfile(sceneId) {
        const scene = state.scenes.find(s => s.id === sceneId);
        if (!scene) {
            toast.error('Profile not found');
            return;
        }
        
        try {
            // Get full profile details
            const fullProfile = await api.getScene(sceneId);
            if (fullProfile?.success) {
                const profileData = fullProfile.data || fullProfile;
                if (window.profileEditor) {
                    window.profileEditor.openEdit(profileData);
                } else {
                    toast.error('Profile editor not loaded');
                }
            } else {
                toast.error('Failed to load profile details');
            }
        } catch (error) {
            toast.error(`Failed to load profile: ${error.message}`);
        }
    }
    
    /**
     * Open CEC configuration modal for a profile
     */
    async openCecConfig(sceneId) {
        const scene = state.scenes.find(s => s.id === sceneId);
        if (!scene) {
            toast.error('Profile not found');
            return;
        }
        
        // Get full profile details if needed
        try {
            const fullScene = await api.getScene(sceneId);
            if (fullScene.success) {
                if (window.sceneCecModal) {
                    window.sceneCecModal.open(fullScene);
                } else {
                    toast.error('CEC modal not loaded');
                }
            } else {
                toast.error('Failed to load profile details');
            }
        } catch (error) {
            toast.error(`Failed to load profile: ${error.message}`);
        }
    }

    /**
     * Setup save profile button - opens profile editor
     */
    setupModal() {
        const saveBtn = document.getElementById('save-scene-btn');
        
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                // Use profile editor for new profiles
                if (window.profileEditor) {
                    window.profileEditor.openNew();
                } else {
                    // Fallback to simple modal if editor not loaded
                    this.openSimpleSaveModal();
                }
            });
        }
        
        // Setup simple modal as fallback
        this.setupSimpleModal();
    }
    
    /**
     * Setup simple save modal (fallback)
     */
    setupSimpleModal() {
        const modal = document.getElementById('save-scene-modal');
        const confirmBtn = document.getElementById('save-scene-confirm');
        const nameInput = document.getElementById('scene-name');
        
        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => {
                this.saveCurrentScene(nameInput.value);
                this.closeModal(modal);
            });
        }
        
        if (nameInput) {
            nameInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.saveCurrentScene(nameInput.value);
                    this.closeModal(modal);
                }
            });
        }
        
        // Modal close handlers
        modal?.querySelectorAll('.modal-close, .modal-backdrop').forEach(el => {
            el.addEventListener('click', () => this.closeModal(modal));
        });
    }

    /**
     * Open modal
     */
    openModal(modal) {
        if (modal) {
            modal.setAttribute('aria-hidden', 'false');
        }
    }

    /**
     * Close modal
     */
    closeModal(modal) {
        if (modal) {
            modal.setAttribute('aria-hidden', 'true');
        }
    }

    /**
     * Save current routing as a new profile
     */
    async saveCurrentScene(name) {
        const trimmedName = name.trim();
        if (!trimmedName) {
            toast.warning('Please enter a profile name');
            return;
        }
        
        try {
            const result = await api.saveCurrentAsScene(trimmedName);
            state.addScene(result.scene || { id: Date.now().toString(), name: trimmedName, outputs: {} });
            toast.success(`Profile "${trimmedName}" saved`);
            
            // Refresh profiles list
            this.loadScenes();
        } catch (error) {
            toast.error(`Failed to save profile: ${error.message}`);
        }
    }

    /**
     * Recall/activate a profile
     */
    async recallScene(sceneId) {
        const scene = state.scenes.find(s => s.id === sceneId);
        const sceneName = scene?.name || 'Profile';
        
        try {
            await api.recallScene(sceneId);
            toast.success(`"${sceneName}" activated`);
            
            // Set this as the active profile for CEC tray integration
            state.setActiveScene(scene);
            state.setActiveProfile(scene);
            
            // Refresh status
            const status = await api.getStatus();
            state.applyStatus(status);
        } catch (error) {
            toast.error(`Failed to recall scene: ${error.message}`);
        }
    }

    /**
     * Delete a profile
     */
    async deleteScene(sceneId) {
        const scene = state.scenes.find(s => s.id === sceneId);
        const sceneName = scene?.name || 'Profile';
        
        if (!confirm(`Delete "${sceneName}"?`)) {
            return;
        }
        
        try {
            await api.deleteScene(sceneId);
            state.removeScene(sceneId);
            toast.success(`"${sceneName}" deleted`);
        } catch (error) {
            toast.error(`Failed to delete profile: ${error.message}`);
        }
    }

    /**
     * Load profiles from API
     */
    async loadScenes() {
        try {
            const result = await api.listScenes();
            state.setScenes(result.scenes || []);
        } catch (error) {
            console.error('Failed to load profiles:', error);
        }
    }
}

// Export
window.ScenesPanel = ScenesPanel;
