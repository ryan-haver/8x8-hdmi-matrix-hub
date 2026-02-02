/**
 * OREI Matrix Control - Output Panel Component
 */

class OutputPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        
        // Subscribe to state changes
        state.on('outputs', () => this.render());
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
     * Render the output list
     */
    render() {
        // Only show loading spinner if loading AND no cached data
        // This keeps the UI intact during refreshes
        const hasData = Object.keys(state.outputs).length > 0;
        if (state.ui.loading && !hasData) {
            this.container.innerHTML = '<div class="matrix-loading"><div class="spinner"></div></div>';
            return;
        }

        let html = '';
        
        for (let o = 1; o <= state.info.outputCount; o++) {
            const currentInput = state.routing[o] || 0;
            const inputName = state.getInputName(currentInput);
            const output = state.outputs[o] || {};
            const outputName = state.getOutputName(o);
            const isMuted = output.audioMuted;
            // Prefer Telnet-based cableConnected over HTTP displayConnected for physical cable detection
            const hasCable = output.cableConnected !== null ? output.cableConnected : output.displayConnected;
            const hasSignal = output.signalActive; // Inferred: cable + routed input has signal
            const isEnabled = output.enabled !== false;
            
            // Determine overall status class
            // Cable/signal status takes priority over enabled status
            let statusClass = 'output-disabled';
            let statusTitle = 'Output disabled';
            
            if (hasCable && hasSignal) {
                statusClass = 'output-active';
                statusTitle = 'Cable connected, signal active';
            } else if (hasCable) {
                statusClass = 'output-connected';
                statusTitle = 'Cable connected, no signal';
            } else if (hasCable === false) {
                // Explicitly no cable - show red
                statusClass = 'output-disconnected';
                statusTitle = 'No cable detected';
            } else if (!isEnabled) {
                // Unknown cable status but disabled
                statusClass = 'output-disabled';
                statusTitle = 'Output disabled';
            } else {
                // Unknown cable status, enabled - treat as disconnected
                statusClass = 'output-disconnected';
                statusTitle = 'No cable detected';
            }
            
            html += `
                <div class="io-card ${statusClass}" data-output="${o}">
                    <div class="io-number">${o}</div>
                    <div class="io-info">
                        <div class="io-name">${Helpers.escapeHtml(outputName)}</div>
                        <div class="io-status">
                            ← ${Helpers.escapeHtml(inputName)}
                            ${isMuted ? '<span class="muted-badge"> 🔇</span>' : ''}
                        </div>
                    </div>
                    <div class="io-actions">
                        <button class="btn-icon cec-btn" data-output="${o}" title="CEC Control">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                                <line x1="8" y1="21" x2="16" y2="21"/>
                                <line x1="12" y1="17" x2="12" y2="21"/>
                            </svg>
                        </button>
                        <button class="btn-icon mute-btn ${isMuted ? 'active' : ''}" 
                                data-output="${o}" 
                                title="${isMuted ? 'Unmute audio' : 'Mute audio'}">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                ${isMuted ? `
                                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                                    <line x1="23" y1="9" x2="17" y2="15"/>
                                    <line x1="17" y1="9" x2="23" y2="15"/>
                                ` : `
                                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                                    <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
                                `}
                            </svg>
                        </button>
                        <button class="btn-icon output-settings-btn" data-output="${o}" title="Output settings">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="3"/>
                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                            </svg>
                        </button>
                    </div>
                </div>
            `;
        }
        
        this.container.innerHTML = html;
        this.attachEventListeners();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Mute buttons
        this.container.querySelectorAll('.mute-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const output = parseInt(e.currentTarget.dataset.output);
                this.toggleMute(output);
            });
        });
        
        // CEC buttons
        this.container.querySelectorAll('.cec-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const output = parseInt(e.currentTarget.dataset.output);
                cecControls.showDropdown('output', output, e.currentTarget);
            });
        });
        
        // Settings buttons
        this.container.querySelectorAll('.output-settings-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const output = parseInt(e.currentTarget.dataset.output);
                this.showOutputSettings(output);
            });
        });
    }

    /**
     * Toggle audio mute for an output
     */
    async toggleMute(output) {
        const currentlyMuted = state.outputs[output]?.audioMuted || false;
        const newMuted = !currentlyMuted;
        
        try {
            await api.setAudioMute(output, newMuted);
            state.setOutputMute(output, newMuted);
            toast.success(newMuted ? `Output ${output} muted` : `Output ${output} unmuted`);
        } catch (error) {
            toast.error(`Failed to ${newMuted ? 'mute' : 'unmute'}: ${error.message}`);
        }
    }

    /**
     * Show output settings modal
     */
    showOutputSettings(output) {
        // Open the settings modal
        if (window.outputSettingsModal) {
            window.outputSettingsModal.open(output);
        } else {
            toast.error('Settings modal not available');
        }
    }
}

// Export
window.OutputPanel = OutputPanel;
