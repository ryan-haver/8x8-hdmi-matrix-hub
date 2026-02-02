/**
 * OREI Matrix Control - Scene CEC Configuration Modal
 * 
 * Allows users to configure CEC command routing for scenes:
 * - Navigation targets (D-pad, menu, back)
 * - Playback targets (play, pause, stop)
 * - Volume targets (volume up/down, mute)
 * - Power targets (power on/off)
 * 
 * Supports auto-resolution based on matrix state and manual overrides.
 */

class SceneCecModal {
    constructor() {
        this.modal = null;
        this.currentScene = null;
        this.cecConfig = null;
        this.createModal();
    }

    /**
     * CEC command categories with descriptions
     */
    static get CATEGORIES() {
        return {
            navigation: {
                label: 'Navigation',
                description: 'D-pad, Select, Back, Menu, Home',
                icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <polygon points="12 8 16 12 12 16 8 12"/>
                </svg>`,
                targetType: 'input'
            },
            playback: {
                label: 'Playback',
                description: 'Play, Pause, Stop, FF, Rewind',
                icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>`,
                targetType: 'input'
            },
            volume: {
                label: 'Volume',
                description: 'Volume Up/Down, Mute',
                icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
                </svg>`,
                targetType: 'output',
                autoResolve: true
            },
            power_on: {
                label: 'Power On',
                description: 'Turn on devices when scene activates',
                icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                </svg>`,
                targetType: 'both'
            },
            power_off: {
                label: 'Power Off',
                description: 'Turn off devices when leaving scene',
                icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18.36 6.64a9 9 0 1 1-12.73 0"/>
                    <line x1="12" y1="2" x2="12" y2="12"/>
                </svg>`,
                targetType: 'output'
            }
        };
    }

    /**
     * Create the modal DOM element
     */
    createModal() {
        this.modal = document.createElement('div');
        this.modal.id = 'scene-cec-modal';
        this.modal.className = 'settings-modal-overlay';
        this.modal.setAttribute('aria-hidden', 'true');
        
        this.modal.innerHTML = `
            <div class="settings-modal scene-cec-modal">
                <div class="settings-modal-header">
                    <h3>
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                            <line x1="8" y1="21" x2="16" y2="21"/>
                            <line x1="12" y1="17" x2="12" y2="21"/>
                        </svg>
                        CEC Configuration
                    </h3>
                    <button class="modal-close-btn" title="Close">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                
                <div class="settings-modal-body">
                    <div class="scene-cec-header">
                        <span class="scene-name-label">Scene: <strong id="cec-scene-name">--</strong></span>
                        <div class="auto-resolve-toggle">
                            <input type="checkbox" id="cec-auto-resolve" class="toggle-input">
                            <label for="cec-auto-resolve" class="toggle-slider"></label>
                            <span class="toggle-label">Auto-resolve targets</span>
                        </div>
                    </div>
                    
                    <div id="cec-categories-container" class="cec-categories">
                        <!-- Categories will be rendered here -->
                    </div>
                </div>
                
                <div class="settings-modal-footer">
                    <button id="cec-resolve-btn" class="btn btn-secondary" title="Auto-detect optimal targets">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 2v6h-6"/>
                            <path d="M3 12a9 9 0 0 1 15-6.7L21 8"/>
                        </svg>
                        Auto-Resolve
                    </button>
                    <div class="spacer"></div>
                    <button id="cec-cancel-btn" class="btn btn-secondary">Cancel</button>
                    <button id="cec-save-btn" class="btn btn-primary">Save</button>
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
        // Close button
        this.modal.querySelector('.modal-close-btn').addEventListener('click', () => this.close());
        
        // Cancel button
        this.modal.querySelector('#cec-cancel-btn').addEventListener('click', () => this.close());
        
        // Save button
        this.modal.querySelector('#cec-save-btn').addEventListener('click', () => this.save());
        
        // Auto-resolve button
        this.modal.querySelector('#cec-resolve-btn').addEventListener('click', () => this.autoResolve());
        
        // Auto-resolve toggle
        this.modal.querySelector('#cec-auto-resolve').addEventListener('change', (e) => {
            this.cecConfig.auto_resolved = e.target.checked;
            this.updateCategoriesState();
        });
        
        // Click outside to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
        
        // Escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });
    }

    /**
     * Check if modal is open
     */
    isOpen() {
        return this.modal.getAttribute('aria-hidden') === 'false';
    }

    /**
     * Open the modal for a scene
     * @param {Object} scene - The scene object
     */
    async open(scene) {
        this.currentScene = scene;
        
        // Get CEC config from scene or create default
        try {
            const result = await api.getSceneCecConfig(scene.id);
            this.cecConfig = result.cec_config || this.getDefaultConfig();
        } catch (error) {
            console.warn('Failed to load CEC config, using defaults:', error);
            this.cecConfig = this.getDefaultConfig();
        }
        
        // Update UI
        this.modal.querySelector('#cec-scene-name').textContent = scene.name;
        this.modal.querySelector('#cec-auto-resolve').checked = this.cecConfig.auto_resolved;
        
        this.renderCategories();
        this.updateCategoriesState();
        
        // Show modal
        this.modal.setAttribute('aria-hidden', 'false');
    }

    /**
     * Close the modal
     */
    close() {
        this.modal.setAttribute('aria-hidden', 'true');
        this.currentScene = null;
        this.cecConfig = null;
    }

    /**
     * Get default CEC config
     */
    getDefaultConfig() {
        return {
            nav_targets: [],
            playback_targets: [],
            volume_targets: [],
            power_on_targets: [],
            power_off_targets: [],
            auto_resolved: true
        };
    }

    /**
     * Render category configuration cards
     */
    renderCategories() {
        const container = this.modal.querySelector('#cec-categories-container');
        const categories = SceneCecModal.CATEGORIES;
        
        let html = '';
        
        for (const [key, category] of Object.entries(categories)) {
            const configKey = this.getCategoryConfigKey(key);
            const targets = this.cecConfig[configKey] || [];
            
            html += `
                <div class="cec-category-card" data-category="${key}">
                    <div class="category-header">
                        <div class="category-icon">${category.icon}</div>
                        <div class="category-info">
                            <div class="category-label">${category.label}</div>
                            <div class="category-description">${category.description}</div>
                        </div>
                    </div>
                    <div class="category-targets">
                        <div class="target-list" id="targets-${key}">
                            ${this.renderTargetChips(targets, category.targetType)}
                        </div>
                        <button class="add-target-btn" data-category="${key}" data-type="${category.targetType}">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="12" y1="5" x2="12" y2="19"/>
                                <line x1="5" y1="12" x2="19" y2="12"/>
                            </svg>
                            Add Target
                        </button>
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
        
        // Attach target management events
        container.querySelectorAll('.add-target-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const category = btn.dataset.category;
                const targetType = btn.dataset.type;
                this.showTargetPicker(category, targetType, btn);
            });
        });
        
        container.querySelectorAll('.target-chip-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const chip = btn.closest('.target-chip');
                const category = chip.closest('.cec-category-card').dataset.category;
                const target = chip.dataset.target;
                this.removeTarget(category, target);
            });
        });
    }

    /**
     * Get the config key for a category
     */
    getCategoryConfigKey(category) {
        const mapping = {
            navigation: 'nav_targets',
            playback: 'playback_targets',
            volume: 'volume_targets',
            power_on: 'power_on_targets',
            power_off: 'power_off_targets'
        };
        return mapping[category] || `${category}_targets`;
    }

    /**
     * Render target chips for a category
     */
    renderTargetChips(targets, targetType) {
        if (!targets || targets.length === 0) {
            return '<span class="no-targets">No targets selected</span>';
        }
        
        return targets.map(target => {
            const parsed = this.parseTarget(target);
            const name = this.getTargetDisplayName(parsed);
            const typeClass = parsed.type === 'input' ? 'input-target' : 'output-target';
            
            return `
                <span class="target-chip ${typeClass}" data-target="${target}">
                    <span class="chip-label">${Helpers.escapeHtml(name)}</span>
                    <button class="target-chip-remove" title="Remove">×</button>
                </span>
            `;
        }).join('');
    }

    /**
     * Parse a target string (e.g., "input_3" → { type: 'input', port: 3 })
     */
    parseTarget(target) {
        const parts = target.split('_');
        return {
            type: parts[0],
            port: parseInt(parts[1], 10)
        };
    }

    /**
     * Get display name for a target
     */
    getTargetDisplayName(parsed) {
        if (parsed.type === 'input') {
            return state.getInputName(parsed.port) || `Input ${parsed.port}`;
        } else {
            return state.getOutputName(parsed.port) || `Output ${parsed.port}`;
        }
    }

    /**
     * Show target picker dropdown
     */
    showTargetPicker(category, targetType, anchorElement) {
        // Remove any existing picker
        this.closeTargetPicker();
        
        const picker = document.createElement('div');
        picker.className = 'target-picker-dropdown';
        picker.id = 'target-picker';
        
        let options = '';
        
        // Add input options
        if (targetType === 'input' || targetType === 'both') {
            options += '<div class="picker-section-label">Inputs</div>';
            for (let i = 1; i <= 8; i++) {
                const target = `input_${i}`;
                const name = state.getInputName(i) || `Input ${i}`;
                const configKey = this.getCategoryConfigKey(category);
                const isSelected = (this.cecConfig[configKey] || []).includes(target);
                options += `
                    <button class="picker-option ${isSelected ? 'selected' : ''}" 
                            data-target="${target}" 
                            ${isSelected ? 'disabled' : ''}>
                        ${Helpers.escapeHtml(name)}
                        ${isSelected ? '<span class="check">✓</span>' : ''}
                    </button>
                `;
            }
        }
        
        // Add output options
        if (targetType === 'output' || targetType === 'both') {
            options += '<div class="picker-section-label">Outputs</div>';
            for (let i = 1; i <= 8; i++) {
                const target = `output_${i}`;
                const name = state.getOutputName(i) || `Output ${i}`;
                const configKey = this.getCategoryConfigKey(category);
                const isSelected = (this.cecConfig[configKey] || []).includes(target);
                
                // Add indicator for special outputs
                const outputInfo = state.outputs[i] || {};
                let badge = '';
                if (outputInfo.scaler === 5) { // Audio Only mode
                    badge = '<span class="output-badge audio-only">Audio</span>';
                } else if (outputInfo.arcEnabled) {
                    badge = '<span class="output-badge arc">ARC</span>';
                }
                
                options += `
                    <button class="picker-option ${isSelected ? 'selected' : ''}" 
                            data-target="${target}"
                            ${isSelected ? 'disabled' : ''}>
                        ${Helpers.escapeHtml(name)}
                        ${badge}
                        ${isSelected ? '<span class="check">✓</span>' : ''}
                    </button>
                `;
            }
        }
        
        picker.innerHTML = options;
        
        // Position near anchor
        const rect = anchorElement.getBoundingClientRect();
        picker.style.position = 'fixed';
        picker.style.top = `${rect.bottom + 4}px`;
        picker.style.left = `${rect.left}px`;
        picker.style.minWidth = `${rect.width}px`;
        
        document.body.appendChild(picker);
        
        // Handle selection
        picker.querySelectorAll('.picker-option:not([disabled])').forEach(opt => {
            opt.addEventListener('click', () => {
                this.addTarget(category, opt.dataset.target);
                this.closeTargetPicker();
            });
        });
        
        // Close on click outside
        setTimeout(() => {
            document.addEventListener('click', this.handleOutsideClick = (e) => {
                if (!picker.contains(e.target) && e.target !== anchorElement) {
                    this.closeTargetPicker();
                }
            });
        }, 0);
    }

    /**
     * Close target picker dropdown
     */
    closeTargetPicker() {
        const picker = document.getElementById('target-picker');
        if (picker) {
            picker.remove();
        }
        if (this.handleOutsideClick) {
            document.removeEventListener('click', this.handleOutsideClick);
            this.handleOutsideClick = null;
        }
    }

    /**
     * Add a target to a category
     */
    addTarget(category, target) {
        const configKey = this.getCategoryConfigKey(category);
        if (!this.cecConfig[configKey]) {
            this.cecConfig[configKey] = [];
        }
        
        if (!this.cecConfig[configKey].includes(target)) {
            this.cecConfig[configKey].push(target);
            this.cecConfig.auto_resolved = false;
            this.modal.querySelector('#cec-auto-resolve').checked = false;
            this.renderCategories();
            this.updateCategoriesState();
        }
    }

    /**
     * Remove a target from a category
     */
    removeTarget(category, target) {
        const configKey = this.getCategoryConfigKey(category);
        const targets = this.cecConfig[configKey] || [];
        const index = targets.indexOf(target);
        
        if (index > -1) {
            targets.splice(index, 1);
            this.cecConfig.auto_resolved = false;
            this.modal.querySelector('#cec-auto-resolve').checked = false;
            this.renderCategories();
            this.updateCategoriesState();
        }
    }

    /**
     * Update the enabled/disabled state of categories based on auto-resolve
     */
    updateCategoriesState() {
        const isAutoResolve = this.cecConfig.auto_resolved;
        const cards = this.modal.querySelectorAll('.cec-category-card');
        
        cards.forEach(card => {
            const category = card.dataset.category;
            const categoryInfo = SceneCecModal.CATEGORIES[category];
            
            // Volume is always auto-resolvable
            if (categoryInfo.autoResolve && isAutoResolve) {
                card.classList.add('auto-resolved');
            } else {
                card.classList.remove('auto-resolved');
            }
        });
    }

    /**
     * Auto-resolve targets based on scene configuration
     */
    async autoResolve() {
        if (!this.currentScene) return;
        
        try {
            const resolveBtn = this.modal.querySelector('#cec-resolve-btn');
            resolveBtn.disabled = true;
            resolveBtn.innerHTML = `
                <svg class="icon spinning" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                </svg>
                Resolving...
            `;
            
            const result = await api.autoResolveCecConfig(this.currentScene.id, false);
            
            if (result.success && result.resolved_cec_config) {
                this.cecConfig = result.resolved_cec_config;
                this.cecConfig.auto_resolved = true;
                this.modal.querySelector('#cec-auto-resolve').checked = true;
                this.renderCategories();
                this.updateCategoriesState();
                toast.success('CEC targets auto-resolved');
            } else {
                toast.error('Failed to auto-resolve targets');
            }
        } catch (error) {
            console.error('Auto-resolve failed:', error);
            toast.error(`Auto-resolve failed: ${error.message}`);
        } finally {
            const resolveBtn = this.modal.querySelector('#cec-resolve-btn');
            resolveBtn.disabled = false;
            resolveBtn.innerHTML = `
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 2v6h-6"/>
                    <path d="M3 12a9 9 0 0 1 15-6.7L21 8"/>
                </svg>
                Auto-Resolve
            `;
        }
    }

    /**
     * Save the CEC configuration
     */
    async save() {
        if (!this.currentScene || !this.cecConfig) return;
        
        try {
            const saveBtn = this.modal.querySelector('#cec-save-btn');
            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';
            
            await api.updateSceneCecConfig(this.currentScene.id, this.cecConfig);
            
            toast.success('CEC configuration saved');
            this.close();
            
            // Refresh scenes list
            const result = await api.listScenes();
            state.setScenes(result.scenes || []);
            
        } catch (error) {
            console.error('Save failed:', error);
            toast.error(`Failed to save: ${error.message}`);
        } finally {
            const saveBtn = this.modal.querySelector('#cec-save-btn');
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save';
        }
    }
}

// Create singleton instance
window.sceneCecModal = new SceneCecModal();
