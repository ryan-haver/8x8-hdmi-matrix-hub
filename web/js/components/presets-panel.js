/**
 * OREI Matrix Control - Presets Panel Component
 */

class PresetsPanel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.presetCount = 8;  // BK-808 has 8 hardware presets
        
        // Subscribe to state changes
        state.on('presets', () => this.render());
        state.on('activePreset', () => this.render());
    }

    /**
     * Initialize the panel
     */
    init() {
        this.render();
    }

    /**
     * Render the presets grid
     */
    render() {
        let html = '';
        
        for (let p = 1; p <= this.presetCount; p++) {
            const preset = state.presets[p] || { name: `Preset ${p}` };
            const presetName = preset.name || `Preset ${p}`;
            const isActive = state.activePreset === p;
            
            html += `
                <div class="preset-item">
                    <button class="preset-btn${isActive ? ' active' : ''}" data-preset="${p}" title="Click to recall, long-press to save">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                            <line x1="9" y1="3" x2="9" y2="21"/>
                            <line x1="15" y1="3" x2="15" y2="21"/>
                            <line x1="3" y1="9" x2="21" y2="9"/>
                            <line x1="3" y1="15" x2="21" y2="15"/>
                        </svg>
                        <span>${Helpers.escapeHtml(presetName)}</span>
                    </button>
                    <div class="preset-item-actions">
                        <button class="btn-icon btn-settings preset-settings-btn" data-preset="${p}" title="Preset settings">
                            <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="3"/>
                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                            </svg>
                        </button>
                        <button class="btn-icon btn-api-copy preset-api-btn" data-preset="${p}" data-preset-name="${Helpers.escapeHtml(presetName)}" title="Get API endpoint for Flic/automation">
                            <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
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
        this.container.querySelectorAll('.preset-btn').forEach(btn => {
            let pressTimer = null;
            let isLongPress = false;
            
            // Click (short press) = recall
            btn.addEventListener('click', (e) => {
                if (isLongPress) {
                    isLongPress = false;
                    return;
                }
                const preset = parseInt(e.currentTarget.dataset.preset);
                this.recallPreset(preset);
            });
            
            // Long press = save
            btn.addEventListener('mousedown', (e) => {
                const preset = parseInt(e.currentTarget.dataset.preset);
                pressTimer = setTimeout(() => {
                    isLongPress = true;
                    this.savePreset(preset);
                }, 800);
            });
            
            btn.addEventListener('mouseup', () => {
                clearTimeout(pressTimer);
            });
            
            btn.addEventListener('mouseleave', () => {
                clearTimeout(pressTimer);
            });
            
            // Touch events for mobile
            btn.addEventListener('touchstart', (e) => {
                const preset = parseInt(e.currentTarget.dataset.preset);
                pressTimer = setTimeout(() => {
                    isLongPress = true;
                    this.savePreset(preset);
                }, 800);
            }, { passive: true });
            
            btn.addEventListener('touchend', () => {
                clearTimeout(pressTimer);
            });
        });
        
        // API copy buttons for presets
        this.container.querySelectorAll('.preset-api-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const preset = parseInt(e.currentTarget.dataset.preset);
                const presetName = e.currentTarget.dataset.presetName;
                if (window.apiCopy) {
                    window.apiCopy.showPreset(preset, presetName);
                } else {
                    toast.error('API copy utility not loaded');
                }
            });
        });

        // Settings buttons for presets
        this.container.querySelectorAll('.preset-settings-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const preset = parseInt(e.currentTarget.dataset.preset);
                if (window.presetSettingsModal) {
                    window.presetSettingsModal.open(preset);
                } else {
                    toast.error('Preset settings modal not loaded');
                }
            });
        });
    }

    /**
     * Recall a preset
     */
    async recallPreset(preset) {
        try {
            await api.recallPreset(preset);
            toast.success(`Preset ${preset} recalled`);
            
            // Set this as the active preset
            state.setActivePreset(preset);
            
            // Refresh status to get new routing
            const status = await api.getStatus();
            state.applyStatus(status);
        } catch (error) {
            toast.error(`Failed to recall preset: ${error.message}`);
        }
    }

    /**
     * Save current routing to a preset
     */
    async savePreset(preset) {
        try {
            await api.savePreset(preset);
            toast.success(`Current routing saved to Preset ${preset}`);
        } catch (error) {
            toast.error(`Failed to save preset: ${error.message}`);
        }
    }
}

// Export
window.PresetsPanel = PresetsPanel;
