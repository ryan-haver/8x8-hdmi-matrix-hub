/**
 * OREI Matrix Control - CEC Macro Editor Component
 * 
 * Provides a modal interface for creating and editing CEC macros:
 * - List all saved macros
 * - Create new macros with step builder
 * - Edit existing macros
 * - Test/execute macros
 * - Delete macros
 */

class CecMacroEditor {
    constructor() {
        this.modal = null;
        this.macros = [];
        this.currentMacro = null;
        this.isEditing = false;
        this.availableCommands = null;
        this.createModal();
    }

    /**
     * Available CEC commands organized by category
     */
    static get COMMANDS() {
        return {
            power: {
                label: 'Power',
                commands: [
                    { id: 'POWER_ON', name: 'Power On', icon: '⚡' },
                    { id: 'POWER_OFF', name: 'Power Off', icon: '⭘' },
                    { id: 'POWER_TOGGLE', name: 'Power Toggle', icon: '⏻' },
                ]
            },
            playback: {
                label: 'Playback',
                commands: [
                    { id: 'PLAY', name: 'Play', icon: '▶' },
                    { id: 'PAUSE', name: 'Pause', icon: '⏸' },
                    { id: 'STOP', name: 'Stop', icon: '⏹' },
                    { id: 'REWIND', name: 'Rewind', icon: '⏪' },
                    { id: 'FAST_FORWARD', name: 'Fast Forward', icon: '⏩' },
                    { id: 'PREVIOUS', name: 'Previous', icon: '⏮' },
                    { id: 'NEXT', name: 'Next', icon: '⏭' },
                ]
            },
            navigation: {
                label: 'Navigation',
                commands: [
                    { id: 'UP', name: 'Up', icon: '▲' },
                    { id: 'DOWN', name: 'Down', icon: '▼' },
                    { id: 'LEFT', name: 'Left', icon: '◀' },
                    { id: 'RIGHT', name: 'Right', icon: '▶' },
                    { id: 'SELECT', name: 'Select/OK', icon: '⏺' },
                    { id: 'BACK', name: 'Back', icon: '↩' },
                    { id: 'MENU', name: 'Menu', icon: '☰' },
                    { id: 'HOME', name: 'Home', icon: '🏠' },
                ]
            },
            volume: {
                label: 'Volume',
                commands: [
                    { id: 'VOLUME_UP', name: 'Volume Up', icon: '🔊' },
                    { id: 'VOLUME_DOWN', name: 'Volume Down', icon: '🔉' },
                    { id: 'MUTE', name: 'Mute', icon: '🔇' },
                ]
            }
        };
    }

    /**
     * Icon options for macros
     */
    static get ICONS() {
        return ['⚡', '🎬', '🎮', '📺', '🔊', '🏠', '🌙', '☀️', '🎵', '📽️', '🕹️', '💤'];
    }

    /**
     * Create the modal DOM
     */
    createModal() {
        this.modal = document.createElement('div');
        this.modal.id = 'cec-macro-modal';
        this.modal.className = 'settings-modal-overlay';
        this.modal.setAttribute('aria-hidden', 'true');
        
        this.modal.innerHTML = `
            <div class="settings-modal macro-editor-modal">
                <div class="settings-modal-header">
                    <h3>
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                            <path d="M2 17l10 5 10-5"/>
                            <path d="M2 12l10 5 10-5"/>
                        </svg>
                        CEC Macros
                    </h3>
                    <button class="modal-close-btn" title="Close">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="settings-modal-body macro-editor-body">
                    <div class="macro-list-view">
                        <div class="macro-list-header">
                            <span>Saved Macros</span>
                            <button class="btn btn-primary btn-sm" id="new-macro-btn">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="12" y1="5" x2="12" y2="19"/>
                                    <line x1="5" y1="12" x2="19" y2="12"/>
                                </svg>
                                New Macro
                            </button>
                        </div>
                        <div class="macro-list" id="macro-list">
                            <!-- Macros will be rendered here -->
                        </div>
                    </div>
                    <div class="macro-edit-view" style="display: none;">
                        <div class="macro-edit-header">
                            <button class="btn btn-text" id="back-to-list-btn">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="19" y1="12" x2="5" y2="12"/>
                                    <polyline points="12 19 5 12 12 5"/>
                                </svg>
                                Back
                            </button>
                            <span class="macro-edit-title">New Macro</span>
                        </div>
                        <div class="macro-form">
                            <div class="form-row">
                                <div class="form-group icon-picker">
                                    <label>Icon</label>
                                    <div class="icon-options" id="icon-options"></div>
                                </div>
                                <div class="form-group flex-grow">
                                    <label for="macro-name">Name</label>
                                    <input type="text" id="macro-name" placeholder="e.g., Movie Night Power On">
                                </div>
                            </div>
                            <div class="form-group">
                                <label for="macro-description">Description (optional)</label>
                                <input type="text" id="macro-description" placeholder="e.g., Powers on TV, soundbar, and Apple TV">
                            </div>
                            <div class="form-group">
                                <label>Steps</label>
                                <div class="step-list" id="step-list">
                                    <!-- Steps will be rendered here -->
                                </div>
                                <button class="btn btn-secondary btn-sm" id="add-step-btn">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <line x1="12" y1="5" x2="12" y2="19"/>
                                        <line x1="5" y1="12" x2="19" y2="12"/>
                                    </svg>
                                    Add Step
                                </button>
                            </div>
                        </div>
                        <div class="macro-edit-actions">
                            <button class="btn btn-secondary" id="test-macro-btn">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="5 3 19 12 5 21 5 3"/>
                                </svg>
                                Test
                            </button>
                            <div class="action-spacer"></div>
                            <button class="btn btn-secondary" id="cancel-edit-btn">Cancel</button>
                            <button class="btn btn-primary" id="save-macro-btn">Save Macro</button>
                        </div>
                    </div>
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
        
        // Click outside to close
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });
        
        // New macro button
        this.modal.querySelector('#new-macro-btn').addEventListener('click', () => this.showEditView());
        
        // Back to list button
        this.modal.querySelector('#back-to-list-btn').addEventListener('click', () => this.showListView());
        
        // Cancel edit button
        this.modal.querySelector('#cancel-edit-btn').addEventListener('click', () => this.showListView());
        
        // Add step button
        this.modal.querySelector('#add-step-btn').addEventListener('click', () => this.addStep());
        
        // Save macro button
        this.modal.querySelector('#save-macro-btn').addEventListener('click', () => this.saveMacro());
        
        // Test macro button
        this.modal.querySelector('#test-macro-btn').addEventListener('click', () => this.testMacro());
        
        // Escape to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.getAttribute('aria-hidden') === 'false') {
                this.close();
            }
        });
    }

    /**
     * Open the modal
     */
    async open() {
        this.modal.setAttribute('aria-hidden', 'false');
        this.modal.classList.add('visible');
        document.body.style.overflow = 'hidden';
        await this.loadMacros();
        this.showListView();
    }

    /**
     * Close the modal
     */
    close() {
        this.modal.setAttribute('aria-hidden', 'true');
        this.modal.classList.remove('visible');
        document.body.style.overflow = '';
        this.currentMacro = null;
        this.isEditing = false;
    }

    /**
     * Load macros from API
     */
    async loadMacros() {
        try {
            const response = await api.getMacros();
            if (response?.success) {
                this.macros = response.data?.macros || [];
                this.renderMacroList();
            } else {
                toast.error('Failed to load macros');
            }
        } catch (error) {
            console.error('Error loading macros:', error);
            toast.error('Failed to load macros');
        }
    }

    /**
     * Show the macro list view
     */
    showListView() {
        this.modal.querySelector('.macro-list-view').style.display = '';
        this.modal.querySelector('.macro-edit-view').style.display = 'none';
        this.currentMacro = null;
        this.isEditing = false;
    }

    /**
     * Show the edit view
     */
    showEditView(macro = null) {
        this.modal.querySelector('.macro-list-view').style.display = 'none';
        this.modal.querySelector('.macro-edit-view').style.display = '';
        
        this.isEditing = !!macro;
        this.currentMacro = macro ? { ...macro, steps: [...(macro.steps || [])] } : {
            icon: '⚡',
            name: '',
            description: '',
            steps: []
        };
        
        // Update title
        this.modal.querySelector('.macro-edit-title').textContent = 
            this.isEditing ? `Edit: ${macro.name}` : 'New Macro';
        
        // Populate form
        this.renderIconPicker();
        this.modal.querySelector('#macro-name').value = this.currentMacro.name || '';
        this.modal.querySelector('#macro-description').value = this.currentMacro.description || '';
        this.renderSteps();
    }

    /**
     * Render the macro list
     */
    renderMacroList() {
        const container = this.modal.querySelector('#macro-list');
        
        if (this.macros.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                        <path d="M2 17l10 5 10-5"/>
                        <path d="M2 12l10 5 10-5"/>
                    </svg>
                    <p>No macros yet</p>
                    <span>Create a macro to save CEC command sequences</span>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.macros.map(macro => `
            <div class="macro-item" data-id="${macro.id}">
                <div class="macro-icon">${macro.icon || '⚡'}</div>
                <div class="macro-info">
                    <div class="macro-name">${Helpers.escapeHtml(macro.name)}</div>
                    <div class="macro-meta">${macro.step_count} step${macro.step_count !== 1 ? 's' : ''}</div>
                </div>
                <div class="macro-actions">
                    <button class="btn btn-icon btn-execute" title="Execute">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="5 3 19 12 5 21 5 3"/>
                        </svg>
                    </button>
                    <button class="btn btn-icon btn-edit" title="Edit">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                    </button>
                    <button class="btn btn-icon btn-delete" title="Delete">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="3 6 5 6 21 6"/>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                        </svg>
                    </button>
                </div>
            </div>
        `).join('');
        
        // Attach event listeners
        container.querySelectorAll('.macro-item').forEach(item => {
            const macroId = item.dataset.id;
            
            item.querySelector('.btn-execute').addEventListener('click', (e) => {
                e.stopPropagation();
                this.executeMacro(macroId);
            });
            
            item.querySelector('.btn-edit').addEventListener('click', (e) => {
                e.stopPropagation();
                this.editMacro(macroId);
            });
            
            item.querySelector('.btn-delete').addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteMacro(macroId);
            });
        });
    }

    /**
     * Render icon picker
     */
    renderIconPicker() {
        const container = this.modal.querySelector('#icon-options');
        container.innerHTML = CecMacroEditor.ICONS.map(icon => `
            <button class="icon-option ${icon === this.currentMacro.icon ? 'selected' : ''}" 
                    data-icon="${icon}">${icon}</button>
        `).join('');
        
        container.querySelectorAll('.icon-option').forEach(btn => {
            btn.addEventListener('click', () => {
                container.querySelectorAll('.icon-option').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                this.currentMacro.icon = btn.dataset.icon;
            });
        });
    }

    /**
     * Render steps
     */
    renderSteps() {
        const container = this.modal.querySelector('#step-list');
        
        if (!this.currentMacro.steps || this.currentMacro.steps.length === 0) {
            container.innerHTML = `
                <div class="empty-steps">
                    <span>No steps added. Click "Add Step" to begin.</span>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.currentMacro.steps.map((step, index) => `
            <div class="step-item" data-index="${index}">
                <div class="step-number">${index + 1}</div>
                <div class="step-config">
                    <div class="step-row">
                        <select class="step-command" data-field="command">
                            ${this.renderCommandOptions(step.command)}
                        </select>
                        <select class="step-targets" data-field="targets" multiple>
                            ${this.renderTargetOptions(step.targets || [])}
                        </select>
                    </div>
                    <div class="step-row delay-row">
                        <label>Delay after:</label>
                        <input type="number" class="step-delay" data-field="delay_ms" 
                               value="${step.delay_ms || 0}" min="0" max="10000" step="100">
                        <span>ms</span>
                    </div>
                </div>
                <button class="btn btn-icon btn-remove-step" title="Remove step">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
        `).join('');
        
        // Attach event listeners
        container.querySelectorAll('.step-item').forEach(item => {
            const index = parseInt(item.dataset.index);
            
            item.querySelector('.step-command').addEventListener('change', (e) => {
                this.currentMacro.steps[index].command = e.target.value;
            });
            
            item.querySelector('.step-targets').addEventListener('change', (e) => {
                const selected = Array.from(e.target.selectedOptions).map(o => o.value);
                this.currentMacro.steps[index].targets = selected;
            });
            
            item.querySelector('.step-delay').addEventListener('change', (e) => {
                this.currentMacro.steps[index].delay_ms = parseInt(e.target.value) || 0;
            });
            
            item.querySelector('.btn-remove-step').addEventListener('click', () => {
                this.removeStep(index);
            });
        });
    }

    /**
     * Render command dropdown options
     */
    renderCommandOptions(selectedCommand) {
        let html = '<option value="">Select command...</option>';
        
        for (const [category, data] of Object.entries(CecMacroEditor.COMMANDS)) {
            html += `<optgroup label="${data.label}">`;
            for (const cmd of data.commands) {
                const selected = cmd.id === selectedCommand ? 'selected' : '';
                html += `<option value="${cmd.id}" ${selected}>${cmd.icon} ${cmd.name}</option>`;
            }
            html += '</optgroup>';
        }
        
        return html;
    }

    /**
     * Render target dropdown options
     */
    renderTargetOptions(selectedTargets) {
        let html = '';
        
        // Input targets
        html += '<optgroup label="Inputs (Sources)">';
        for (let i = 1; i <= 8; i++) {
            const value = `input_${i}`;
            const selected = selectedTargets.includes(value) ? 'selected' : '';
            const name = state?.getInputName?.(i) || `Input ${i}`;
            html += `<option value="${value}" ${selected}>${name}</option>`;
        }
        html += '</optgroup>';
        
        // Output targets
        html += '<optgroup label="Outputs (Displays)">';
        for (let i = 1; i <= 8; i++) {
            const value = `output_${i}`;
            const selected = selectedTargets.includes(value) ? 'selected' : '';
            const name = state?.getOutputName?.(i) || `Output ${i}`;
            html += `<option value="${value}" ${selected}>${name}</option>`;
        }
        html += '</optgroup>';
        
        return html;
    }

    /**
     * Add a new step
     */
    addStep() {
        if (!this.currentMacro.steps) {
            this.currentMacro.steps = [];
        }
        this.currentMacro.steps.push({
            command: '',
            targets: [],
            delay_ms: 500
        });
        this.renderSteps();
    }

    /**
     * Remove a step
     */
    removeStep(index) {
        this.currentMacro.steps.splice(index, 1);
        this.renderSteps();
    }

    /**
     * Edit a macro
     */
    async editMacro(macroId) {
        try {
            const response = await api.getMacro(macroId);
            if (response?.success) {
                this.showEditView(response.data);
            } else {
                toast.error('Failed to load macro');
            }
        } catch (error) {
            console.error('Error loading macro:', error);
            toast.error('Failed to load macro');
        }
    }

    /**
     * Save the current macro
     */
    async saveMacro() {
        const name = this.modal.querySelector('#macro-name').value.trim();
        const description = this.modal.querySelector('#macro-description').value.trim();
        
        if (!name) {
            toast.error('Please enter a macro name');
            return;
        }
        
        if (!this.currentMacro.steps || this.currentMacro.steps.length === 0) {
            toast.error('Please add at least one step');
            return;
        }
        
        // Validate steps
        for (let i = 0; i < this.currentMacro.steps.length; i++) {
            const step = this.currentMacro.steps[i];
            if (!step.command) {
                toast.error(`Step ${i + 1}: Please select a command`);
                return;
            }
            if (!step.targets || step.targets.length === 0) {
                toast.error(`Step ${i + 1}: Please select at least one target`);
                return;
            }
        }
        
        const macroData = {
            name,
            description,
            icon: this.currentMacro.icon || '⚡',
            steps: this.currentMacro.steps
        };
        
        try {
            let response;
            if (this.isEditing && this.currentMacro.id) {
                response = await api.updateMacro(this.currentMacro.id, macroData);
            } else {
                response = await api.createMacro(macroData);
            }
            
            if (response?.success) {
                toast.success(`Macro "${name}" saved`);
                await this.loadMacros();
                this.showListView();
            } else {
                toast.error(response?.error || 'Failed to save macro');
            }
        } catch (error) {
            console.error('Error saving macro:', error);
            toast.error('Failed to save macro');
        }
    }

    /**
     * Test a macro (dry run)
     */
    async testMacro() {
        if (!this.currentMacro.id) {
            toast.info('Save the macro first to test it');
            return;
        }
        
        try {
            const response = await api.testMacro(this.currentMacro.id);
            if (response?.success) {
                const result = response.data;
                if (result.success) {
                    toast.success(`Macro valid: ${result.step_count} steps, ~${result.estimated_duration_ms}ms`);
                } else {
                    toast.error(`Validation issues: ${result.issues.join(', ')}`);
                }
            } else {
                toast.error(response?.error || 'Test failed');
            }
        } catch (error) {
            console.error('Error testing macro:', error);
            toast.error('Test failed');
        }
    }

    /**
     * Execute a macro
     */
    async executeMacro(macroId) {
        const macro = this.macros.find(m => m.id === macroId);
        const name = macro?.name || macroId;
        
        try {
            toast.info(`Executing "${name}"...`);
            const response = await api.executeMacro(macroId);
            
            if (response?.success) {
                const result = response.data;
                if (result.success) {
                    toast.success(`"${name}" executed successfully`);
                } else {
                    toast.warning(`"${name}" completed with issues`);
                }
            } else {
                toast.error(response?.error || 'Execution failed');
            }
        } catch (error) {
            console.error('Error executing macro:', error);
            toast.error('Execution failed');
        }
    }

    /**
     * Delete a macro
     */
    async deleteMacro(macroId) {
        const macro = this.macros.find(m => m.id === macroId);
        const name = macro?.name || macroId;
        
        if (!confirm(`Delete macro "${name}"?`)) {
            return;
        }
        
        try {
            const response = await api.deleteMacro(macroId);
            if (response?.success) {
                toast.success(`Macro "${name}" deleted`);
                await this.loadMacros();
            } else {
                toast.error(response?.error || 'Failed to delete macro');
            }
        } catch (error) {
            console.error('Error deleting macro:', error);
            toast.error('Failed to delete macro');
        }
    }
}

// Global instance
const cecMacroEditor = new CecMacroEditor();
