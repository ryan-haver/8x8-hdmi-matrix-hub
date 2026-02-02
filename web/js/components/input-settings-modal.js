/**
 * OREI Matrix Control - Input Settings Modal Component
 * Provides settings for EDID mode, CEC enable, and input name
 */

class InputSettingsModal {
    constructor() {
        this.currentInput = null;
        this.modal = null;
        this.edidModes = [];
        this.currentIcon = null;      // Current selected icon
        this.suggestedIcon = null;    // Auto-suggested icon
        this.createModal();
        this.loadEdidModes();
    }

    /**
     * Load available EDID modes from API
     */
    async loadEdidModes() {
        try {
            const result = await api.getEdidModes();
            if (result?.success && result?.data?.modes) {
                // API returns {modes: {1: "label", 2: "label", ...}}
                // Convert to array format [{value, label}, ...]
                const modesObj = result.data.modes;
                this.edidModes = Object.entries(modesObj).map(([value, label]) => ({
                    value: parseInt(value),
                    label: label
                })).sort((a, b) => a.value - b.value);
                this.updateEdidSelect();
            }
        } catch (error) {
            console.error('Failed to load EDID modes:', error);
            // Use fallback modes
            this.edidModes = [
                { value: 1, label: '1080p 2CH' },
                { value: 9, label: '4K60 2CH' },
                { value: 12, label: '4K60 4:4:4 2CH' },
                { value: 15, label: 'Copy Output 1' },
                { value: 36, label: '4K60 HDR Atmos' }
            ];
            this.updateEdidSelect();
        }
    }

    /**
     * Update the EDID select dropdown with loaded modes
     */
    updateEdidSelect() {
        const select = this.modal?.querySelector('#input-edid-select');
        if (select && this.edidModes.length > 0) {
            select.innerHTML = this.edidModes.map(m => 
                `<option value="${m.value}">${m.label}</option>`
            ).join('');
        }
    }

    /**
     * Create the modal DOM element
     */
    createModal() {
        this.modal = document.createElement('div');
        this.modal.id = 'input-settings-modal';
        this.modal.className = 'settings-modal-overlay';
        this.modal.innerHTML = `
            <div class="settings-modal">
                <div class="settings-modal-header">
                    <h3><span class="input-name">Input</span> Settings</h3>
                    <button class="modal-close-btn" title="Close">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="settings-modal-body">
                    <!-- Device Icon -->
                    <div class="setting-group setting-group-icon">
                        <label class="setting-label">Device Icon</label>
                        <div class="icon-selector-row">
                            <button class="icon-preview-btn" id="input-icon-btn" type="button">
                                <span class="icon-preview" id="input-icon-preview"></span>
                            </button>
                            <div class="icon-selector-info">
                                <span class="icon-label" id="input-icon-label">Generic Input</span>
                                <button class="btn btn-sm btn-secondary" id="input-icon-change" type="button">Change Icon</button>
                            </div>
                        </div>
                    </div>

                    <!-- Input Name -->
                    <div class="setting-group">
                        <label class="setting-label">Name</label>
                        <input type="text" id="input-name-field" class="setting-input" maxlength="20" placeholder="Enter input name">
                        <div class="setting-suggestion hidden" id="input-icon-suggestion">
                            <span class="suggestion-icon" id="input-suggestion-preview"></span>
                            <span class="suggestion-text">Suggested icon:</span>
                            <button class="btn btn-xs btn-accent" id="input-suggestion-apply">Apply</button>
                        </div>
                    </div>

                    <!-- EDID Mode -->
                    <div class="setting-group">
                        <label class="setting-label">EDID Mode</label>
                        <select id="input-edid-select" class="setting-select">
                            <option value="">Loading...</option>
                        </select>
                        <p class="setting-hint">EDID determines the video capabilities reported to the source device.</p>
                    </div>

                    <!-- CEC Enable -->
                    <div class="setting-group">
                        <label class="setting-label">CEC Control</label>
                        <div class="toggle-switch">
                            <input type="checkbox" id="input-cec-toggle" class="toggle-input">
                            <label for="input-cec-toggle" class="toggle-slider"></label>
                            <span class="toggle-label">Enabled</span>
                        </div>
                        <p class="setting-hint">Enable CEC commands to be sent to this input device.</p>
                    </div>

                    <!-- Status Info -->
                    <div class="setting-group setting-info">
                        <div class="info-row">
                            <span class="info-label">Signal Status:</span>
                            <span class="info-value" id="input-signal-info">—</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Source Detected:</span>
                            <span class="info-value" id="input-source-info">—</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Routed To:</span>
                            <span class="info-value" id="input-routing-info">—</span>
                        </div>
                    </div>
                </div>
                <div class="settings-modal-footer">
                    <button class="btn btn-secondary modal-cancel-btn">Cancel</button>
                    <button class="btn btn-primary modal-apply-btn">Apply Changes</button>
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
        this.modal.querySelector('.modal-cancel-btn').addEventListener('click', () => this.close());
        
        // Apply button
        this.modal.querySelector('.modal-apply-btn').addEventListener('click', () => this.applyChanges());
        
        // Close on overlay click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('visible')) {
                this.close();
            }
        });
        
        // Icon picker button
        this.modal.querySelector('#input-icon-btn').addEventListener('click', () => this.openIconPicker());
        this.modal.querySelector('#input-icon-change').addEventListener('click', () => this.openIconPicker());
        
        // Auto-suggest icon on name change
        const nameField = this.modal.querySelector('#input-name-field');
        let debounceTimer;
        nameField.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                this.handleNameChange(e.target.value);
            }, 300);
        });
        
        // Apply suggestion
        this.modal.querySelector('#input-suggestion-apply').addEventListener('click', () => {
            if (this.suggestedIcon) {
                this.setIcon(this.suggestedIcon);
                this.hideSuggestion();
            }
        });
    }
    
    /**
     * Open the icon picker modal
     */
    openIconPicker() {
        if (window.iconPicker) {
            window.iconPicker.open(this.currentIcon, (iconId) => {
                this.setIcon(iconId);
            });
        }
    }
    
    /**
     * Set the current icon
     */
    setIcon(iconId) {
        this.currentIcon = iconId;
        
        // Update preview
        const preview = this.modal.querySelector('#input-icon-preview');
        const label = this.modal.querySelector('#input-icon-label');
        
        if (typeof IconLibrary !== 'undefined') {
            preview.innerHTML = IconLibrary.getSvg(iconId, 32);
            const meta = IconLibrary.getMeta(iconId);
            label.textContent = meta.label;
        }
    }
    
    /**
     * Handle name change for auto-suggest
     */
    handleNameChange(name) {
        if (typeof IconLibrary === 'undefined') return;
        
        const suggested = IconLibrary.suggestIcon(name, false);
        
        // Only show suggestion if it's different from current and not generic
        if (suggested && suggested !== this.currentIcon && !suggested.startsWith('generic-')) {
            this.suggestedIcon = suggested;
            this.showSuggestion(suggested);
        } else {
            this.hideSuggestion();
        }
    }
    
    /**
     * Show icon suggestion
     */
    showSuggestion(iconId) {
        const suggestion = this.modal.querySelector('#input-icon-suggestion');
        const preview = this.modal.querySelector('#input-suggestion-preview');
        
        if (typeof IconLibrary !== 'undefined') {
            preview.innerHTML = IconLibrary.getSvg(iconId, 20);
            const meta = IconLibrary.getMeta(iconId);
            suggestion.querySelector('.suggestion-text').textContent = `Suggested: ${meta.label}`;
        }
        
        suggestion.classList.remove('hidden');
    }
    
    /**
     * Hide icon suggestion
     */
    hideSuggestion() {
        this.suggestedIcon = null;
        const suggestion = this.modal.querySelector('#input-icon-suggestion');
        suggestion.classList.add('hidden');
    }

    /**
     * Open the modal for a specific input
     */
    open(inputNumber) {
        this.currentInput = inputNumber;
        const input = state.inputs[inputNumber] || {};
        const inputName = state.getInputName(inputNumber);
        const outputs = this.getOutputsForInput(inputNumber);

        // Update header
        this.modal.querySelector('.input-name').textContent = `Input ${inputNumber}`;

        // Set current values
        this.modal.querySelector('#input-name-field').value = inputName;
        
        // EDID - need to get current EDID from state/API if available
        const currentEdid = input.edid || input.edidMode || 1;
        this.modal.querySelector('#input-edid-select').value = currentEdid;
        
        // CEC enabled
        this.modal.querySelector('#input-cec-toggle').checked = input.cecEnabled !== false;
        
        // Load current icon
        this.currentIcon = state.getInputIcon(inputNumber);
        this.setIcon(this.currentIcon);
        this.hideSuggestion();

        // Update status info
        const hasSignal = input.signalActive;
        const sourceDetected = input.cableConnected;
        
        // Signal status
        const signalInfo = this.modal.querySelector('#input-signal-info');
        if (hasSignal) {
            signalInfo.textContent = '✓ Active';
            signalInfo.className = 'info-value connected';
        } else {
            signalInfo.textContent = '✗ No Signal';
            signalInfo.className = 'info-value disconnected';
        }
        
        // Source detected
        const sourceInfo = this.modal.querySelector('#input-source-info');
        if (sourceDetected === true) {
            sourceInfo.textContent = '✓ Yes';
            sourceInfo.className = 'info-value connected';
        } else if (sourceDetected === false) {
            sourceInfo.textContent = '✗ No';
            sourceInfo.className = 'info-value disconnected';
        } else {
            sourceInfo.textContent = '—';
            sourceInfo.className = 'info-value';
        }
        
        // Routing info
        const routingInfo = this.modal.querySelector('#input-routing-info');
        if (outputs.length > 0) {
            routingInfo.textContent = outputs.map(o => state.getOutputName(o)).join(', ');
        } else {
            routingInfo.textContent = 'Not routed';
        }

        // Show modal
        this.modal.classList.add('visible');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Get list of outputs that are showing this input
     */
    getOutputsForInput(input) {
        const outputs = [];
        for (let o = 1; o <= state.info.outputCount; o++) {
            if (state.routing[o] === input) {
                outputs.push(o);
            }
        }
        return outputs;
    }

    /**
     * Close the modal
     */
    close() {
        this.modal.classList.remove('visible');
        document.body.style.overflow = '';
        this.currentInput = null;
    }

    /**
     * Apply changes
     */
    async applyChanges() {
        if (!this.currentInput) return;

        const input = this.currentInput;
        const currentState = state.inputs[input] || {};
        const currentName = state.getInputName(input);
        
        // Gather new values
        const newName = this.modal.querySelector('#input-name-field').value.trim();
        const newEdid = parseInt(this.modal.querySelector('#input-edid-select').value);
        const newCec = this.modal.querySelector('#input-cec-toggle').checked;

        const changes = [];

        try {
            // Apply name change if different
            if (newName && newName !== currentName) {
                changes.push(
                    api.setInputName(input, newName).then(() => {
                        state.setInputName(input, newName);
                    })
                );
            }
            
            // Apply EDID change if different
            const currentEdid = currentState.edid || currentState.edidMode || 1;
            if (newEdid && newEdid !== currentEdid) {
                changes.push(api.setEdidMode(input, newEdid));
            }
            
            // Apply CEC change if different
            if (newCec !== (currentState.cecEnabled !== false)) {
                changes.push(api.setCecEnabled('input', input, newCec));
            }
            
            // Persist name and icon to backend device settings
            const currentIcon = state.getInputIcon(input);
            const nameChanged = newName && newName !== currentName;
            const iconChanged = this.currentIcon && this.currentIcon !== currentIcon;
            
            if (nameChanged || iconChanged) {
                const settings = {};
                if (nameChanged) settings.name = newName;
                if (iconChanged) settings.icon = this.currentIcon;
                
                changes.push(
                    api.updateInputSettings(input, settings).then(() => {
                        if (iconChanged) {
                            state.setInputIcon(input, this.currentIcon);
                        }
                    })
                );
            }

            if (changes.length === 0) {
                toast.info('No changes to apply');
                this.close();
                return;
            }

            // Apply all changes
            await Promise.all(changes);

            // Update local state
            state.inputs[input] = {
                ...currentState,
                edid: newEdid,
                edidMode: newEdid,
                cecEnabled: newCec,
                icon: this.currentIcon
            };
            state.emit('inputs');

            toast.success(`Input ${input} settings updated`);
            this.close();

        } catch (error) {
            toast.error(`Failed to apply settings: ${error.message}`);
        }
    }
}

// Export
window.InputSettingsModal = InputSettingsModal;
