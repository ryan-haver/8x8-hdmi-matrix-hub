/**
 * OREI Matrix Control - Input Panel Component
 */

class InputPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.editingInput = null;
        
        // Subscribe to state changes
        state.on('inputs', () => this.render());
        state.on('routing', () => this.render());
        state.on('loading', (loading) => {
            if (!loading) this.render();
        });
    }

    /**
     * Initialize the panel
     */
    init() {
        this.render();
    }

    /**
     * Render the input list
     */
    render() {
        // Only show loading spinner if loading AND no cached data
        // This keeps the UI intact during refreshes
        const hasData = Object.keys(state.inputs).length > 0;
        if (state.ui.loading && !hasData) {
            this.container.innerHTML = '<div class="matrix-loading"><div class="spinner"></div></div>';
            return;
        }

        let html = '';
        
        for (let i = 1; i <= state.info.inputCount; i++) {
            const name = state.getInputName(i);
            const input = state.inputs[i] || {};
            const hasSignal = input.signalActive;
            // sourceDetected = HPD/5V from source device (device is powered on)
            // This is NOT physical cable detection - requires source device to be on
            const sourceDetected = input.cableConnected; // true = source on, false = source off/no cable
            const outputs = this.getOutputsForInput(i);
            const outputRanges = this.formatOutputRanges(outputs);
            const outputText = outputs.length > 0 
                ? `→ Out ${outputRanges}` 
                : 'Not routed';
            
            // Status priority: Signal > Source Detected > Off
            // - Green (active): Video signal present
            // - Orange (connected): Source device on but no video signal (standby)
            // - Red (disconnected): Source device off or no cable
            let statusClass = 'input-disabled';
            let statusTitle = 'Unknown status';
            
            if (hasSignal) {
                // Video signal present - device is on and outputting video
                statusClass = 'input-active';
                statusTitle = 'Signal active - source outputting video';
            } else if (sourceDetected === true) {
                // HPD detected but no signal - device is on but in standby/not outputting
                statusClass = 'input-connected';
                statusTitle = 'Source detected - device on but no video signal';
            } else if (sourceDetected === false) {
                // No HPD - device is off or no cable connected
                statusClass = 'input-disconnected';
                statusTitle = 'No source detected - device off or disconnected';
            } else {
                // Unknown (telnet unavailable)
                statusClass = 'input-unknown';
                statusTitle = 'Status unknown';
            }
            
            html += `
                <div class="io-card ${statusClass}" data-input="${i}" title="${statusTitle}">
                    <div class="io-number">${i}</div>
                    <div class="io-info">
                        ${this.editingInput === i ? `
                            <input type="text" 
                                   class="io-name-input" 
                                   value="${Helpers.escapeHtml(name)}"
                                   data-input="${i}"
                                   maxlength="20"
                                   autofocus>
                        ` : `
                            <div class="io-name">${Helpers.escapeHtml(name)}</div>
                        `}
                        <div class="io-status">${outputText}</div>
                    </div>
                    <div class="io-actions">
                        ${this.editingInput === i ? `
                            <button class="btn-icon save-name-btn" data-input="${i}" title="Save">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="20 6 9 17 4 12"/>
                                </svg>
                            </button>
                            <button class="btn-icon cancel-edit-btn" data-input="${i}" title="Cancel">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="18" y1="6" x2="6" y2="18"/>
                                    <line x1="6" y1="6" x2="18" y2="18"/>
                                </svg>
                            </button>
                        ` : `
                            <button class="btn-icon cec-btn" data-input="${i}" title="CEC Control">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                                    <line x1="8" y1="21" x2="16" y2="21"/>
                                    <line x1="12" y1="17" x2="12" y2="21"/>
                                </svg>
                            </button>
                            <button class="btn-icon settings-btn" data-input="${i}" title="Input Settings">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="3"/>
                                    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                                </svg>
                            </button>
                        `}
                    </div>
                </div>
            `;
        }
        
        this.container.innerHTML = html;
        this.attachEventListeners();
        
        // Focus input if editing
        if (this.editingInput !== null) {
            const input = this.container.querySelector('.io-name-input');
            if (input) {
                input.focus();
                input.select();
            }
        }
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
     * Format output numbers as compact ranges
     * e.g., [1, 3, 4, 5, 7] -> "1, 3-5, 7"
     */
    formatOutputRanges(outputs) {
        if (outputs.length === 0) return '';
        if (outputs.length === 1) return outputs[0].toString();
        
        // Sort outputs numerically
        const sorted = [...outputs].sort((a, b) => a - b);
        const ranges = [];
        let rangeStart = sorted[0];
        let rangeEnd = sorted[0];
        
        for (let i = 1; i < sorted.length; i++) {
            if (sorted[i] === rangeEnd + 1) {
                // Continue the range
                rangeEnd = sorted[i];
            } else {
                // End current range and start new one
                ranges.push(rangeStart === rangeEnd 
                    ? rangeStart.toString() 
                    : `${rangeStart}-${rangeEnd}`);
                rangeStart = sorted[i];
                rangeEnd = sorted[i];
            }
        }
        
        // Add the last range
        ranges.push(rangeStart === rangeEnd 
            ? rangeStart.toString() 
            : `${rangeStart}-${rangeEnd}`);
        
        return ranges.join(', ');
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // CEC button
        this.container.querySelectorAll('.cec-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const input = parseInt(e.currentTarget.dataset.input);
                cecControls.showDropdown('input', input, e.currentTarget);
            });
        });
        
        // Settings button - opens input settings modal
        this.container.querySelectorAll('.settings-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const input = parseInt(e.currentTarget.dataset.input);
                if (window.inputSettingsModal) {
                    window.inputSettingsModal.open(input);
                }
            });
        });
        
        // Save button (for inline editing if still used)
        this.container.querySelectorAll('.save-name-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const input = parseInt(e.currentTarget.dataset.input);
                this.saveName(input);
            });
        });
        
        // Cancel button
        this.container.querySelectorAll('.cancel-edit-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.cancelEditing();
            });
        });
        
        // Input field events
        this.container.querySelectorAll('.io-name-input').forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    this.saveName(parseInt(input.dataset.input));
                } else if (e.key === 'Escape') {
                    this.cancelEditing();
                }
            });
        });
    }

    /**
     * Start editing an input name
     */
    startEditing(input) {
        this.editingInput = input;
        this.render();
    }

    /**
     * Cancel editing
     */
    cancelEditing() {
        this.editingInput = null;
        this.render();
    }

    /**
     * Save the edited name
     */
    async saveName(input) {
        const inputField = this.container.querySelector(`.io-name-input[data-input="${input}"]`);
        if (!inputField) return;
        
        const newName = inputField.value.trim();
        if (!newName) {
            toast.warning('Name cannot be empty');
            return;
        }
        
        try {
            await api.setInputName(input, newName);
            state.setInputName(input, newName);
            toast.success(`Renamed Input ${input} to "${newName}"`);
        } catch (error) {
            toast.error(`Failed to rename: ${error.message}`);
        }
        
        this.editingInput = null;
        this.render();
    }
}

// Export
window.InputPanel = InputPanel;
