/**
 * OREI Matrix Control - Output Settings Modal Component
 * Provides settings for HDR, HDCP, Scaler, ARC, and output enable/disable
 */

class OutputSettingsModal {
    constructor() {
        this.currentOutput = null;
        this.modal = null;
        this.currentIcon = null;      // Current selected icon
        this.suggestedIcon = null;    // Auto-suggested icon
        this.createModal();
    }

    /**
     * HDR mode options
     */
    getHdrModes() {
        return [
            { value: 1, label: 'Passthrough' },
            { value: 2, label: 'HDR → SDR' },
            { value: 3, label: 'Auto (Follow Sink)' }
        ];
    }

    /**
     * HDCP mode options
     */
    getHdcpModes() {
        return [
            { value: 1, label: 'HDCP 1.4' },
            { value: 2, label: 'HDCP 2.2' },
            { value: 3, label: 'Follow Sink' },
            { value: 4, label: 'Follow Source' },
            { value: 5, label: 'User Mode' }
        ];
    }

    /**
     * Scaler mode options
     */
    getScalerModes() {
        return [
            { value: 1, label: 'Passthrough' },
            { value: 2, label: '8K → 4K' },
            { value: 3, label: '8K/4K → 1080p' },
            { value: 4, label: 'Auto' },
            { value: 5, label: 'Audio Only' }
        ];
    }

    /**
     * Create the modal DOM element
     */
    createModal() {
        this.modal = document.createElement('div');
        this.modal.id = 'output-settings-modal';
        this.modal.className = 'settings-modal-overlay';
        this.modal.innerHTML = `
            <div class="settings-modal">
                <div class="settings-modal-header">
                    <h3><span class="output-name">Output</span> Settings</h3>
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
                            <button class="icon-preview-btn" id="output-icon-btn" type="button">
                                <span class="icon-preview" id="output-icon-preview"></span>
                            </button>
                            <div class="icon-selector-info">
                                <span class="icon-label" id="output-icon-label">Generic Output</span>
                                <button class="btn btn-sm btn-secondary" id="output-icon-change" type="button">Change Icon</button>
                            </div>
                        </div>
                    </div>

                    <!-- Output Name -->
                    <div class="setting-group">
                        <label class="setting-label">Name</label>
                        <input type="text" id="output-name-field" class="setting-input" maxlength="20" placeholder="Enter output name">
                        <div class="setting-suggestion hidden" id="output-icon-suggestion">
                            <span class="suggestion-icon" id="output-suggestion-preview"></span>
                            <span class="suggestion-text">Suggested icon:</span>
                            <button class="btn btn-xs btn-accent" id="output-suggestion-apply">Apply</button>
                        </div>
                    </div>

                    <!-- Output Enable -->
                    <div class="setting-group">
                        <label class="setting-label">Output Stream</label>
                        <div class="toggle-switch">
                            <input type="checkbox" id="output-enable-toggle" class="toggle-input">
                            <label for="output-enable-toggle" class="toggle-slider"></label>
                            <span class="toggle-label">Enabled</span>
                        </div>
                    </div>

                    <!-- HDR Mode -->
                    <div class="setting-group">
                        <label class="setting-label">HDR Mode</label>
                        <select id="hdr-mode-select" class="setting-select">
                            ${this.getHdrModes().map(m => `<option value="${m.value}">${m.label}</option>`).join('')}
                        </select>
                    </div>

                    <!-- HDCP Mode -->
                    <div class="setting-group">
                        <label class="setting-label">HDCP Mode</label>
                        <select id="hdcp-mode-select" class="setting-select">
                            ${this.getHdcpModes().map(m => `<option value="${m.value}">${m.label}</option>`).join('')}
                        </select>
                    </div>

                    <!-- Scaler Mode -->
                    <div class="setting-group">
                        <label class="setting-label">Scaler / Resolution</label>
                        <select id="scaler-mode-select" class="setting-select">
                            ${this.getScalerModes().map(m => `<option value="${m.value}">${m.label}</option>`).join('')}
                        </select>
                    </div>

                    <!-- ARC Enable -->
                    <div class="setting-group">
                        <label class="setting-label">ARC (Audio Return Channel)</label>
                        <div class="toggle-switch">
                            <input type="checkbox" id="arc-enable-toggle" class="toggle-input">
                            <label for="arc-enable-toggle" class="toggle-slider"></label>
                            <span class="toggle-label">Enabled</span>
                        </div>
                    </div>

                    <!-- Audio Mute -->
                    <div class="setting-group">
                        <label class="setting-label">Audio Mute</label>
                        <div class="toggle-switch">
                            <input type="checkbox" id="audio-mute-toggle" class="toggle-input">
                            <label for="audio-mute-toggle" class="toggle-slider"></label>
                            <span class="toggle-label">Muted</span>
                        </div>
                    </div>

                    <!-- CEC Enable -->
                    <div class="setting-group">
                        <label class="setting-label">CEC Control</label>
                        <div class="toggle-switch">
                            <input type="checkbox" id="output-cec-toggle" class="toggle-input">
                            <label for="output-cec-toggle" class="toggle-slider"></label>
                            <span class="toggle-label">Enabled</span>
                        </div>
                        <p class="setting-hint">Enable CEC commands to be sent to this display.</p>
                    </div>

                    <!-- Status Info -->
                    <div class="setting-group setting-info">
                        <div class="info-row">
                            <span class="info-label">Display Connected:</span>
                            <span class="info-value" id="display-connected-info">—</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Current Source:</span>
                            <span class="info-value" id="current-source-info">—</span>
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
        this.modal.querySelector('#output-icon-btn').addEventListener('click', () => this.openIconPicker());
        this.modal.querySelector('#output-icon-change').addEventListener('click', () => this.openIconPicker());
        
        // Auto-suggest icon on name change
        const nameField = this.modal.querySelector('#output-name-field');
        let debounceTimer;
        nameField.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                this.handleNameChange(e.target.value);
            }, 300);
        });
        
        // Apply suggestion
        this.modal.querySelector('#output-suggestion-apply').addEventListener('click', () => {
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
        const preview = this.modal.querySelector('#output-icon-preview');
        const label = this.modal.querySelector('#output-icon-label');
        
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
        
        const suggested = IconLibrary.suggestIcon(name, true); // isOutput = true
        
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
        const suggestion = this.modal.querySelector('#output-icon-suggestion');
        const preview = this.modal.querySelector('#output-suggestion-preview');
        
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
        const suggestion = this.modal.querySelector('#output-icon-suggestion');
        suggestion.classList.add('hidden');
    }

    /**
     * Open the modal for a specific output
     */
    open(outputNumber) {
        this.currentOutput = outputNumber;
        const output = state.outputs[outputNumber] || {};
        const outputName = state.getOutputName(outputNumber);
        const currentInput = state.routing[outputNumber] || 0;
        const inputName = state.getInputName(currentInput);

        // Update header
        this.modal.querySelector('.output-name').textContent = `Output ${outputNumber}`;

        // Set current values
        this.modal.querySelector('#output-name-field').value = outputName;
        this.modal.querySelector('#output-enable-toggle').checked = output.enabled !== false;
        this.modal.querySelector('#hdr-mode-select').value = output.hdrMode || 3;
        this.modal.querySelector('#hdcp-mode-select').value = output.hdcpMode || 3;
        this.modal.querySelector('#scaler-mode-select').value = output.scalerMode || 1;
        this.modal.querySelector('#arc-enable-toggle').checked = output.arcEnabled || false;
        this.modal.querySelector('#audio-mute-toggle').checked = output.audioMuted || false;
        this.modal.querySelector('#output-cec-toggle').checked = output.cecEnabled !== false;
        
        // Load current icon
        this.currentIcon = state.getOutputIcon(outputNumber);
        this.setIcon(this.currentIcon);
        this.hideSuggestion();

        // Update info - prefer Telnet-based cableConnected over HTTP displayConnected
        const hasCable = output.cableConnected !== null ? output.cableConnected : output.displayConnected;
        this.modal.querySelector('#display-connected-info').textContent = 
            hasCable ? '✓ Yes' : '✗ No';
        this.modal.querySelector('#display-connected-info').className = 
            'info-value ' + (hasCable ? 'connected' : 'disconnected');
        this.modal.querySelector('#current-source-info').textContent = inputName;

        // Show modal
        this.modal.classList.add('visible');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close the modal
     */
    close() {
        this.modal.classList.remove('visible');
        document.body.style.overflow = '';
        this.currentOutput = null;
    }

    /**
     * Apply changes
     */
    async applyChanges() {
        if (!this.currentOutput) return;

        const output = this.currentOutput;
        const currentState = state.outputs[output] || {};
        const currentName = state.getOutputName(output);
        
        // Gather new values
        const newName = this.modal.querySelector('#output-name-field').value.trim();
        const newEnabled = this.modal.querySelector('#output-enable-toggle').checked;
        const newHdr = parseInt(this.modal.querySelector('#hdr-mode-select').value);
        const newHdcp = parseInt(this.modal.querySelector('#hdcp-mode-select').value);
        const newScaler = parseInt(this.modal.querySelector('#scaler-mode-select').value);
        const newArc = this.modal.querySelector('#arc-enable-toggle').checked;
        const newMute = this.modal.querySelector('#audio-mute-toggle').checked;
        const newCec = this.modal.querySelector('#output-cec-toggle').checked;

        const changes = [];

        try {
            // Apply name change if different
            if (newName && newName !== currentName) {
                changes.push(
                    api.setOutputName(output, newName).then(() => {
                        state.setOutputName(output, newName);
                    })
                );
            }
            
            // Apply changes only if different from current
            if (newEnabled !== (currentState.enabled !== false)) {
                changes.push(api.setOutputEnable(output, newEnabled));
            }
            if (newHdr !== (currentState.hdrMode || 3)) {
                changes.push(api.setHdrMode(output, newHdr));
            }
            if (newHdcp !== (currentState.hdcpMode || 3)) {
                changes.push(api.setHdcpMode(output, newHdcp));
            }
            if (newScaler !== (currentState.scalerMode || 1)) {
                changes.push(api.setScalerMode(output, newScaler));
            }
            if (newArc !== (currentState.arcEnabled || false)) {
                changes.push(api.setOutputArc(output, newArc));
            }
            if (newMute !== (currentState.audioMuted || false)) {
                changes.push(api.setAudioMute(output, newMute));
            }
            if (newCec !== (currentState.cecEnabled !== false)) {
                changes.push(api.setCecEnabled('output', output, newCec));
            }
            
            // Persist name and icon to backend device settings
            const currentIcon = state.getOutputIcon(output);
            const nameChanged = newName && newName !== currentName;
            const iconChanged = this.currentIcon && this.currentIcon !== currentIcon;
            
            if (nameChanged || iconChanged) {
                const settings = {};
                if (nameChanged) settings.name = newName;
                if (iconChanged) settings.icon = this.currentIcon;
                
                changes.push(
                    api.updateOutputSettings(output, settings).then(() => {
                        if (iconChanged) {
                            state.setOutputIcon(output, this.currentIcon);
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
            state.outputs[output] = {
                ...currentState,
                enabled: newEnabled,
                hdrMode: newHdr,
                hdcpMode: newHdcp,
                scalerMode: newScaler,
                arcEnabled: newArc,
                audioMuted: newMute,
                cecEnabled: newCec,
                icon: this.currentIcon
            };
            state.emit('outputs');

            toast.success(`Output ${output} settings updated`);
            this.close();

        } catch (error) {
            toast.error(`Failed to apply settings: ${error.message}`);
        }
    }
}

// Export
window.OutputSettingsModal = OutputSettingsModal;
