/**
 * OREI Matrix Control - Profile Editor Component
 * 
 * Provides a modal interface for creating and editing profiles:
 * - Create new profiles from current routing
 * - Edit existing profiles (name, icon, macros)
 * - Assign macros to profiles
 * - Configure power-on/power-off macros
 * - Quick access to CEC configuration
 */

class ProfileEditor {
    constructor() {
        this.modal = null;
        this.currentProfile = null;
        this.isEditing = false;
        this.availableMacros = [];
        this.createModal();
    }

    /**
     * Icon options for profiles
     */
    static get ICONS() {
        return [
            '📺', '🎬', '🎮', '🎵', '🏠', '💼', '🌙', '☀️', 
            '📽️', '🕹️', '🎧', '📻', '🖥️', '💡', '🔊', '⚡'
        ];
    }

    /**
     * Create the modal DOM
     */
    createModal() {
        this.modal = document.createElement('div');
        this.modal.id = 'profile-editor-modal';
        this.modal.className = 'settings-modal-overlay';
        this.modal.setAttribute('aria-hidden', 'true');
        
        this.modal.innerHTML = `
            <div class="settings-modal profile-editor-modal">
                <div class="settings-modal-header">
                    <h3>
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="23 7 16 12 23 17 23 7"/>
                            <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                        </svg>
                        <span id="profile-editor-title">New Profile</span>
                    </h3>
                    <button class="modal-close-btn" title="Close">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="settings-modal-body profile-editor-body">
                    <div class="profile-form">
                        <!-- Basic Info Section -->
                        <div class="form-section">
                            <label class="section-label">
                                <span class="section-icon">1</span>
                                Profile Details
                            </label>
                            <p class="section-help">Give your profile a name and icon for easy identification.</p>
                            <div class="form-row icon-name-row">
                                <div class="form-group icon-picker">
                                    <label>Icon</label>
                                    <div class="icon-options" id="profile-icon-options"></div>
                                </div>
                                <div class="form-group flex-grow">
                                    <label for="profile-name">Name <span class="required">*</span></label>
                                    <input type="text" id="profile-name" class="input" placeholder="e.g., Movie Night, Gaming, Work" maxlength="50">
                                </div>
                            </div>
                        </div>
                        
                        <!-- Routing Summary Section -->
                        <div class="form-section">
                            <label class="section-label">
                                <span class="section-icon">2</span>
                                Routing Configuration
                            </label>
                            <div class="routing-summary" id="profile-routing-summary">
                                <p class="section-help">
                                    <strong>The current matrix routing will be saved with this profile.</strong><br>
                                    Set up your desired input→output routing on the Matrix page first, then create the profile.
                                </p>
                            </div>
                            <div class="routing-preview" id="profile-routing-preview">
                                <!-- Routing preview will be rendered here -->
                            </div>
                        </div>
                        
                        <!-- Macro Assignment Section -->
                        <div class="form-section">
                            <label class="section-label">
                                <span class="section-icon">3</span>
                                Quick-Action Macros
                                <span class="optional-badge">Optional</span>
                            </label>
                            <p class="section-help">Select macros to show as quick-action buttons when this profile is active. These provide one-tap access to common CEC commands.</p>
                            <div class="macro-assignment" id="profile-macro-list">
                                <p class="empty-message">Loading macros...</p>
                            </div>
                        </div>
                        
                        <!-- Power Macros Section -->
                        <div class="form-section">
                            <label class="section-label">
                                <span class="section-icon">4</span>
                                Automation
                                <span class="optional-badge">Optional</span>
                            </label>
                            <p class="section-help">Automatically run a macro when activating or switching away from this profile. Useful for powering on/off devices.</p>
                            <div class="power-macros">
                                <div class="form-group">
                                    <label for="profile-power-on-macro">
                                        <span class="macro-label-icon">▶</span> On Activate
                                    </label>
                                    <select id="profile-power-on-macro" class="input">
                                        <option value="">None</option>
                                    </select>
                                    <span class="help-text">Runs automatically when this profile is recalled</span>
                                </div>
                                <div class="form-group">
                                    <label for="profile-power-off-macro">
                                        <span class="macro-label-icon">⏹</span> On Deactivate
                                    </label>
                                    <select id="profile-power-off-macro" class="input">
                                        <option value="">None</option>
                                    </select>
                                    <span class="help-text">Runs when switching to another profile</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="settings-modal-footer profile-editor-footer">
                    <button class="btn btn-danger" id="delete-profile-btn" style="display: none;">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                        Delete
                    </button>
                    <div class="action-spacer"></div>
                    <button class="btn btn-secondary" id="cancel-profile-btn">Cancel</button>
                    <button class="btn btn-primary" id="save-profile-btn">Save Profile</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.modal);
        this.attachEventListeners();
        this.renderIconPicker();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Close button
        this.modal.querySelector('.modal-close-btn').addEventListener('click', () => this.close());
        
        // Click outside to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });
        
        // Cancel button
        this.modal.querySelector('#cancel-profile-btn').addEventListener('click', () => this.close());
        
        // Save button
        this.modal.querySelector('#save-profile-btn').addEventListener('click', () => this.save());
        
        // Delete button
        this.modal.querySelector('#delete-profile-btn').addEventListener('click', () => this.delete());
        
        // Open CEC config button (if present)
        const cecBtn = this.modal.querySelector('#open-cec-config-btn');
        if (cecBtn) cecBtn.addEventListener('click', () => this.openCecConfig());
        
        // Escape to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.getAttribute('aria-hidden') === 'false') {
                this.close();
            }
        });
    }

    /**
     * Render icon picker
     */
    renderIconPicker() {
        const container = this.modal.querySelector('#profile-icon-options');
        container.innerHTML = ProfileEditor.ICONS.map(icon => 
            `<button class="icon-option" data-icon="${icon}" title="${icon}">${icon}</button>`
        ).join('');
        
        // Add click handlers
        container.querySelectorAll('.icon-option').forEach(btn => {
            btn.addEventListener('click', () => {
                container.querySelectorAll('.icon-option').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
            });
        });
        
        // Select first by default
        container.querySelector('.icon-option')?.classList.add('selected');
    }

    /**
     * Open modal for creating a new profile
     */
    async openNew() {
        this.isEditing = false;
        this.currentProfile = null;
        
        // Reset form
        this.modal.querySelector('#profile-editor-title').textContent = 'New Profile';
        this.modal.querySelector('#profile-name').value = '';
        this.modal.querySelector('#delete-profile-btn').style.display = 'none';
        const cecSection = this.modal.querySelector('#cec-config-section');
        if (cecSection) cecSection.style.display = 'none';
        
        // Reset icon selection
        const iconOptions = this.modal.querySelector('#profile-icon-options');
        iconOptions.querySelectorAll('.icon-option').forEach(b => b.classList.remove('selected'));
        iconOptions.querySelector('.icon-option')?.classList.add('selected');
        
        // Load macros and render
        await this.loadMacros();
        this.renderRoutingPreview();
        
        // Show modal
        this.modal.setAttribute('aria-hidden', 'false');
        this.modal.classList.add('visible');
        document.body.style.overflow = 'hidden';
        
        // Focus name input
        setTimeout(() => this.modal.querySelector('#profile-name').focus(), 100);
    }

    /**
     * Open modal for editing an existing profile
     */
    async openEdit(profile) {
        this.isEditing = true;
        this.currentProfile = profile;
        
        // Populate form
        this.modal.querySelector('#profile-editor-title').textContent = 'Edit Profile';
        this.modal.querySelector('#profile-name').value = profile.name || '';
        this.modal.querySelector('#delete-profile-btn').style.display = '';
        const cecSection = this.modal.querySelector('#cec-config-section');
        if (cecSection) cecSection.style.display = '';
        
        // Select icon
        const iconOptions = this.modal.querySelector('#profile-icon-options');
        iconOptions.querySelectorAll('.icon-option').forEach(b => {
            b.classList.toggle('selected', b.dataset.icon === (profile.icon || '📺'));
        });
        
        // Load macros and render with current selections
        await this.loadMacros();
        this.renderMacroList(profile.macros || []);
        this.selectPowerMacros(profile.power_on_macro, profile.power_off_macro);
        this.renderRoutingPreview(profile.outputs);
        
        // Show modal
        this.modal.setAttribute('aria-hidden', 'false');
        this.modal.classList.add('visible');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close modal
     */
    close() {
        this.modal.setAttribute('aria-hidden', 'true');
        this.modal.classList.remove('visible');
        document.body.style.overflow = '';
        this.currentProfile = null;
    }

    /**
     * Load available macros from API
     */
    async loadMacros() {
        try {
            const response = await api.getMacros();
            if (response?.success) {
                this.availableMacros = response.data?.macros || [];
            } else {
                this.availableMacros = [];
            }
        } catch (error) {
            console.error('Failed to load macros:', error);
            this.availableMacros = [];
        }
        
        this.renderMacroList();
        this.renderPowerMacroDropdowns();
    }

    /**
     * Render macro assignment checkboxes
     */
    renderMacroList(selectedMacros = []) {
        const container = this.modal.querySelector('#profile-macro-list');
        
        if (this.availableMacros.length === 0) {
            container.innerHTML = `
                <p class="empty-message">
                    No macros created yet. 
                    <a href="#" id="create-macro-link">Create a macro</a> to add quick-action buttons.
                </p>
            `;
            container.querySelector('#create-macro-link')?.addEventListener('click', (e) => {
                e.preventDefault();
                this.close();
                if (window.cecMacroEditor) {
                    window.cecMacroEditor.open();
                }
            });
            return;
        }
        
        container.innerHTML = this.availableMacros.map(macro => {
            const isChecked = selectedMacros.includes(macro.id);
            return `
                <label class="macro-checkbox">
                    <input type="checkbox" name="profile-macros" value="${macro.id}" ${isChecked ? 'checked' : ''}>
                    <span class="macro-icon">${macro.icon || '⚡'}</span>
                    <span class="macro-name">${Helpers.escapeHtml(macro.name)}</span>
                </label>
            `;
        }).join('');
    }

    /**
     * Render power macro dropdowns
     */
    renderPowerMacroDropdowns() {
        const powerOnSelect = this.modal.querySelector('#profile-power-on-macro');
        const powerOffSelect = this.modal.querySelector('#profile-power-off-macro');
        
        const options = '<option value="">None</option>' + 
            this.availableMacros.map(macro => 
                `<option value="${macro.id}">${macro.icon || '⚡'} ${Helpers.escapeHtml(macro.name)}</option>`
            ).join('');
        
        powerOnSelect.innerHTML = options;
        powerOffSelect.innerHTML = options;
    }

    /**
     * Select power macros in dropdowns
     */
    selectPowerMacros(powerOnMacro, powerOffMacro) {
        const powerOnSelect = this.modal.querySelector('#profile-power-on-macro');
        const powerOffSelect = this.modal.querySelector('#profile-power-off-macro');
        
        if (powerOnMacro) powerOnSelect.value = powerOnMacro;
        if (powerOffMacro) powerOffSelect.value = powerOffMacro;
    }

    /**
     * Render routing preview
     */
    renderRoutingPreview(outputs = null) {
        const container = this.modal.querySelector('#profile-routing-preview');
        
        // Get current routing from state if not provided
        if (!outputs) {
            outputs = {};
            for (let i = 1; i <= 8; i++) {
                const output = state.outputs[i];
                // Use output.input which is set by state.setRouting()
                // Also check state.routing as a fallback
                const inputNum = output?.input || state.routing[i];
                if (inputNum) {
                    outputs[i] = {
                        input: inputNum,
                        enabled: output?.enabled !== false,
                        audio_mute: output?.audioMuted || false
                    };
                }
            }
        }
        
        const outputEntries = Object.entries(outputs);
        if (outputEntries.length === 0) {
            container.innerHTML = `
                <div class="routing-empty-message">
                    <p class="empty-message">⚠️ No routing information available</p>
                    <p class="help-text">Please ensure the matrix is connected and status is loaded.</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <div class="routing-grid">
                ${outputEntries.map(([outNum, config]) => {
                    const inputName = state.inputs[config.input]?.name || `Input ${config.input}`;
                    const outputName = state.outputs[outNum]?.name || `Output ${outNum}`;
                    return `
                        <div class="routing-item ${config.enabled === false ? 'disabled' : ''}">
                            <span class="output-name">${Helpers.escapeHtml(outputName)}</span>
                            <span class="routing-arrow">←</span>
                            <span class="input-name">${Helpers.escapeHtml(inputName)}</span>
                            ${config.audio_mute ? '<span class="mute-badge" title="Audio muted">🔇</span>' : ''}
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    }

    /**
     * Get form values
     */
    getFormValues() {
        const name = this.modal.querySelector('#profile-name').value.trim();
        const selectedIcon = this.modal.querySelector('#profile-icon-options .icon-option.selected');
        const icon = selectedIcon?.dataset.icon || '📺';
        
        // Get selected macros
        const macros = [];
        this.modal.querySelectorAll('input[name="profile-macros"]:checked').forEach(checkbox => {
            macros.push(checkbox.value);
        });
        
        const powerOnMacro = this.modal.querySelector('#profile-power-on-macro').value || null;
        const powerOffMacro = this.modal.querySelector('#profile-power-off-macro').value || null;
        
        // Get current routing from state
        const outputs = {};
        for (let i = 1; i <= 8; i++) {
            const output = state.outputs[i];
            const inputNum = output?.input || state.routing[i];
            if (inputNum) {
                outputs[i] = {
                    input: inputNum,
                    enabled: output?.enabled !== false,
                    audio_mute: output?.audioMuted || false
                };
            }
        }
        
        return { name, icon, outputs, macros, powerOnMacro, powerOffMacro };
    }

    /**
     * Validate form
     */
    validate() {
        const { name } = this.getFormValues();
        
        if (!name) {
            toast.warning('Please enter a profile name');
            this.modal.querySelector('#profile-name').focus();
            return false;
        }
        
        return true;
    }

    /**
     * Generate profile ID from name
     */
    generateId(name) {
        return name.toLowerCase()
            .replace(/[^a-z0-9]+/g, '_')
            .replace(/^_+|_+$/g, '')
            .substring(0, 32) + '_' + Date.now().toString(36);
    }

    /**
     * Save profile
     */
    async save() {
        if (!this.validate()) return;
        
        const { name, icon, outputs, macros, powerOnMacro, powerOffMacro } = this.getFormValues();
        
        try {
            const saveBtn = this.modal.querySelector('#save-profile-btn');
            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';
            
            if (this.isEditing && this.currentProfile) {
                // Update existing profile
                const result = await api.updateProfile(this.currentProfile.id, {
                    name,
                    icon,
                    macros,
                    power_on_macro: powerOnMacro,
                    power_off_macro: powerOffMacro
                });
                
                if (result?.success) {
                    toast.success(`Profile "${name}" updated`);
                    state.updateProfile(this.currentProfile.id, result.data || result);
                } else {
                    throw new Error(result?.error || 'Failed to update profile');
                }
            } else {
                // Create new profile
                const id = this.generateId(name);
                const result = await api.createProfile({
                    id,
                    name,
                    icon,
                    outputs,
                    macros,
                    power_on_macro: powerOnMacro,
                    power_off_macro: powerOffMacro
                });
                
                if (result?.success) {
                    toast.success(`Profile "${name}" created`);
                    state.addScene(result.data || result);
                } else {
                    throw new Error(result?.error || 'Failed to create profile');
                }
            }
            
            // Refresh scenes list
            this.refreshProfilesList();
            this.close();
            
        } catch (error) {
            toast.error(`Failed to save profile: ${error.message}`);
        } finally {
            const saveBtn = this.modal.querySelector('#save-profile-btn');
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save Profile';
        }
    }

    /**
     * Delete profile
     */
    async delete() {
        if (!this.currentProfile) return;
        
        const name = this.currentProfile.name || 'this profile';
        if (!confirm(`Delete "${name}"? This cannot be undone.`)) {
            return;
        }
        
        try {
            const result = await api.deleteProfile(this.currentProfile.id);
            if (result?.success) {
                toast.success(`Profile "${name}" deleted`);
                state.removeScene(this.currentProfile.id);
                this.refreshProfilesList();
                this.close();
            } else {
                throw new Error(result?.error || 'Failed to delete profile');
            }
        } catch (error) {
            toast.error(`Failed to delete profile: ${error.message}`);
        }
    }

    /**
     * Open CEC configuration modal
     */
    async openCecConfig() {
        if (!this.currentProfile) return;
        
        // Close this modal first
        this.close();
        
        // Open CEC config modal
        if (window.sceneCecModal) {
            try {
                const fullProfile = await api.getScene(this.currentProfile.id);
                if (fullProfile?.success) {
                    window.sceneCecModal.open(fullProfile.data || fullProfile);
                } else {
                    toast.error('Failed to load profile details');
                }
            } catch (error) {
                toast.error(`Failed to open CEC config: ${error.message}`);
            }
        } else {
            toast.error('CEC configuration modal not available');
        }
    }

    /**
     * Refresh profiles list
     */
    async refreshProfilesList() {
        try {
            const result = await api.listScenes();
            state.setScenes(result.scenes || []);
        } catch (error) {
            console.error('Failed to refresh profiles:', error);
        }
    }
}

// Create global instance
window.profileEditor = new ProfileEditor();
