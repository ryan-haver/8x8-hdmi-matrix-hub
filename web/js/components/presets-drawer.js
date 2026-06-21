/**
 * OREI Matrix Control - Presets Drawer Component
 * Slide-out drawer for managing and programming the 8 matrix hardware presets.
 */
class PresetsDrawer {
    constructor() {
        this.isOpen = false;
        this.container = null;
        this.backdrop = null;
        this.presets = [];
        this.editingPresetNum = null;
        this.expandedPresetNum = null;


        this.createDrawer();

        // Register with overlay manager if it exists
        if (window.overlayManager) {
            window.overlayManager.register('presets-drawer', {
                close: () => this.close(),
                isOpen: () => this.isOpen
            });
        }
    }

    createDrawer() {
        // Backdrop
        const backdrop = document.createElement('div');
        backdrop.id = 'presets-backdrop';
        backdrop.className = 'routing-backdrop';
        backdrop.addEventListener('click', () => {
            if (window.overlayManager) {
                window.overlayManager.closeAll();
            } else {
                this.close();
            }
        });
        document.body.appendChild(backdrop);

        // Drawer
        const drawer = document.createElement('aside');
        drawer.id = 'presets-drawer';
        drawer.className = 'routing-drawer';
        drawer.setAttribute('aria-hidden', 'true');
        drawer.setAttribute('role', 'dialog');
        drawer.setAttribute('aria-label', 'Matrix Presets');
        drawer.innerHTML = `
            <div class="drawer-header">
                <h3>
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                        <line x1="9" y1="3" x2="9" y2="21"/>
                        <line x1="15" y1="3" x2="15" y2="21"/>
                        <line x1="3" y1="9" x2="21" y2="9"/>
                        <line x1="3" y1="15" x2="21" y2="15"/>
                    </svg>
                    Matrix Presets
                </h3>
                <div class="drawer-header-actions">
                    <button class="btn-icon drawer-close" aria-label="Close drawer">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="drawer-content" id="presets-drawer-content">
                <p class="loading-hint">Loading presets...</p>
            </div>
            <div class="drawer-footer mobile-only">
                <button class="btn btn-primary btn-block back-to-deck-btn">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="19" y1="12" x2="5" y2="12"/>
                        <polyline points="12 19 5 12 12 5"/>
                    </svg>
                    Back to Control Deck
                </button>
            </div>
        `;
        document.body.appendChild(drawer);

        this.container = drawer;
        this.backdrop = backdrop;

        // Close button
        drawer.querySelector('.drawer-close').addEventListener('click', () => this.close());

        // Back to Control Deck button
        drawer.querySelector('.back-to-deck-btn')?.addEventListener('click', () => {
            this.close();
            if (window.sideNavDrawer) {
                window.sideNavDrawer.open();
            }
        });

        // Escape key close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    open(presetNum = null) {
        if (window.overlayManager) {
            window.overlayManager.onOpen('presets-drawer');
        }
        this.isOpen = true;
        this.container.classList.add('open');
        this.container.setAttribute('aria-hidden', 'false');
        this.backdrop.classList.add('open');
        document.body.style.overflow = 'hidden';
        
        if (presetNum !== null) {
            this.expandedPresetNum = parseInt(presetNum);
        }
        this.loadPresets();

        // Focus trap for accessibility
        if (window.FocusTrap) {
            this.focusTrap = new window.FocusTrap(this.container, () => this.close());
            this.focusTrap.activate();
        }
    }

    close() {
        if (window.overlayManager) {
            window.overlayManager.onClose('presets-drawer');
        }
        this.isOpen = false;
        this.container.classList.remove('open');
        this.container.setAttribute('aria-hidden', 'true');
        this.backdrop.classList.remove('open');
        document.body.style.overflow = '';
        this.editingPresetNum = null;

        if (this.focusTrap) {
            this.focusTrap.deactivate();
        }
    }

    toggle() {
        if (this.isOpen) this.close();
        else this.open();
    }

    async loadPresets() {
        try {
            const result = await api.getPresets();
            if (result?.success && result?.data?.presets) {
                this.presets = result.data.presets;
                // Update state's copy of preset names/routings too
                const statePresets = {};
                this.presets.forEach(p => {
                    statePresets[p.number] = {
                        name: p.name,
                        routing: p.routing
                    };
                });
                state.setPresets(statePresets);
            } else {
                // Fallback to state
                this.presets = [];
                for (let i = 1; i <= 8; i++) {
                    const preset = state.presets[i] || {};
                    this.presets.push({
                        number: i,
                        name: preset.name || `Preset ${i}`,
                        routing: preset.routing || {}
                    });
                }
            }
            this.render();
        } catch (err) {
            console.error('Failed to load presets in drawer:', err);
            const content = document.getElementById('presets-drawer-content');
            if (content) content.innerHTML = '<p class="error-hint">Failed to load presets.</p>';
        }
    }

    render() {
        if (!this.isOpen) return;
        const content = document.getElementById('presets-drawer-content');
        if (!content) return;

        let html = '';
        this.presets.forEach(p => {
            html += this.renderPresetRow(p);
        });

        content.innerHTML = html;
        this.attachEventListeners(content);
    }

    renderPresetRow(p) {
        const isExpanded = this.expandedPresetNum === p.number;
        const isEditing = this.editingPresetNum === p.number;
        const isActive = state.activePreset === p.number;
        
        // Build the routing details HTML if expanded
        let routingHtml = '';
        if (isExpanded) {
            routingHtml = `
                <div class="preset-routing-editor">
                    <div class="preset-routing-grid">
            `;
            
            // Generate selector dropdowns for outputs 1-8
            for (let out = 1; out <= 8; out++) {
                const currentInput = p.routing[String(out)] || p.routing[out] || out;
                const outputName = state.getOutputName(out);
                
                routingHtml += `
                    <div class="preset-routing-row">
                        <label class="preset-routing-label">${Helpers.escapeHtml(outputName)}</label>
                        <select class="select select-sm preset-routing-select" data-output="${out}">
                `;
                
                for (let input = 1; input <= 8; input++) {
                    const inputName = state.getInputName(input);
                    const selected = String(currentInput) === String(input) ? 'selected' : '';
                    routingHtml += `<option value="${input}" ${selected}>${Helpers.escapeHtml(inputName)}</option>`;
                }
                
                routingHtml += `
                        </select>
                    </div>
                `;
            }
            
            routingHtml += `
                    </div>
                    <div class="preset-routing-actions">
                        <button class="btn btn-sm btn-secondary btn-recall-preset" data-preset="${p.number}">
                            <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="5 3 19 12 5 21 5 3"/>
                            </svg>
                            Recall
                        </button>
                        <button class="btn btn-sm btn-secondary btn-overwrite-routing" data-preset="${p.number}">
                            <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                                <polyline points="17 21 17 13 7 13 7 21"/>
                                <polyline points="7 3 7 8 15 8"/>
                            </svg>
                            Overwrite
                        </button>
                        <button class="btn btn-sm btn-primary btn-save-custom" data-preset="${p.number}">
                            <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                                <polyline points="17 21 17 13 7 13 7 21"/>
                                <polyline points="7 3 7 8 15 8"/>
                            </svg>
                            Save Mapping
                        </button>
                    </div>
                </div>
            `;
        }

        return `
            <div class="preset-row ${isExpanded ? 'expanded' : ''} ${isActive ? 'active' : ''}" data-preset-number="${p.number}">
                <div class="preset-row-summary">
                    <div class="preset-row-info">
                        <span class="preset-badge">${p.number}</span>
                        ${isEditing ? `
                            <input type="text" class="preset-rename-input" value="${Helpers.escapeHtml(p.name)}" maxlength="30">
                        ` : `
                            <span class="preset-name">${Helpers.escapeHtml(p.name)}</span>
                        `}
                    </div>
                    <div class="preset-row-actions">
                        ${isEditing ? `
                            <button class="btn-icon preset-save-btn" data-preset="${p.number}" title="Save Name">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="20 6 9 17 4 12"/>
                                </svg>
                            </button>
                            <button class="btn-icon preset-cancel-btn" title="Cancel">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                                </svg>
                            </button>
                        ` : `
                            <button class="btn-icon preset-edit-btn" data-preset="${p.number}" title="Rename">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                </svg>
                            </button>
                            <button class="btn-icon preset-expand-btn" data-preset="${p.number}" title="${isExpanded ? 'Collapse' : 'Expand'}">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="transform: ${isExpanded ? 'rotate(180deg)' : 'none'}; transition: transform 0.2s ease;">
                                    <polyline points="6 9 12 15 18 9"/>
                                </svg>
                            </button>
                        `}
                    </div>
                </div>
                ${routingHtml}
            </div>
        `;
    }

    attachEventListeners(content) {
        // Toggle expand
        content.querySelectorAll('.preset-expand-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const presetNum = parseInt(btn.dataset.preset);
                if (this.expandedPresetNum === presetNum) {
                    this.expandedPresetNum = null;
                } else {
                    this.expandedPresetNum = presetNum;
                }
                this.render();
            });
        });

        // Click summary row to toggle expand (unless editing or clicking edit button)
        content.querySelectorAll('.preset-row-summary').forEach(rowSummary => {
            rowSummary.addEventListener('click', (e) => {
                // If clicked an input or button inside the summary, don't toggle
                if (e.target.closest('button') || e.target.closest('input')) return;
                
                const row = rowSummary.closest('.preset-row');
                const presetNum = parseInt(row.dataset.presetNumber);
                if (this.expandedPresetNum === presetNum) {
                    this.expandedPresetNum = null;
                } else {
                    this.expandedPresetNum = presetNum;
                }
                this.render();
            });
        });

        // Edit mode (rename)
        content.querySelectorAll('.preset-edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.editingPresetNum = parseInt(btn.dataset.preset);
                this.render();
                // Focus the input
                const input = content.querySelector('.preset-rename-input');
                if (input) {
                    input.focus();
                    input.select();
                }
            });
        });

        // Cancel rename
        content.querySelectorAll('.preset-cancel-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.editingPresetNum = null;
                this.render();
            });
        });

        // Save rename
        content.querySelectorAll('.preset-save-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const presetNum = parseInt(btn.dataset.preset);
                const input = content.querySelector(`.preset-row[data-preset-number="${presetNum}"] .preset-rename-input`);
                const newName = input ? input.value.trim() : '';
                if (!newName) return;
                try {
                    await api.renamePreset(presetNum, newName);
                    this.editingPresetNum = null;
                    await this.loadPresets();
                    toast.success('Preset renamed');
                } catch (err) {
                    toast.error('Failed to rename preset');
                }
            });
        });

        // Enter key to save rename
        content.querySelectorAll('.preset-rename-input').forEach(input => {
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const row = input.closest('.preset-row');
                    const saveBtn = row?.querySelector('.preset-save-btn');
                    saveBtn?.click();
                } else if (e.key === 'Escape') {
                    e.preventDefault();
                    this.editingPresetNum = null;
                    this.render();
                }
            });
        });

        // Recall preset
        content.querySelectorAll('.btn-recall-preset').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const presetNum = parseInt(btn.dataset.preset);
                try {
                    await api.recallPreset(presetNum);
                    state.setActivePreset(presetNum);
                    toast.success(`Preset ${presetNum} recalled`);
                    // Close drawer on recall to show the active routing screen
                    this.close();
                    // Reload matrix status
                    const status = await api.getStatus();
                    state.applyStatus(status);
                } catch (err) {
                    toast.error(`Failed to recall preset: ${err.message}`);
                }
            });
        });

        // Overwrite preset with current active routing
        content.querySelectorAll('.btn-overwrite-routing').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const presetNum = parseInt(btn.dataset.preset);
                if (!confirm(`Overwrite Preset ${presetNum} with the current HDMI matrix routing?`)) {
                    return;
                }
                try {
                    await api.savePreset(presetNum);
                    toast.success(`Active routing saved to Preset ${presetNum}`);
                    await this.loadPresets();
                } catch (err) {
                    toast.error(`Failed to save preset: ${err.message}`);
                }
            });
        });

        // Save custom routing mapping
        content.querySelectorAll('.btn-save-custom').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const presetNum = parseInt(btn.dataset.preset);
                const row = btn.closest('.preset-row');
                const selects = row.querySelectorAll('.preset-routing-select');
                
                const customRouting = {};
                selects.forEach(select => {
                    const output = select.dataset.output;
                    const input = select.value;
                    customRouting[output] = parseInt(input);
                });

                try {
                    await api.savePreset(presetNum, customRouting);
                    toast.success(`Custom routing saved to Preset ${presetNum}`);
                    await this.loadPresets();
                } catch (err) {
                    toast.error(`Failed to save preset: ${err.message}`);
                }
            });
        });
    }
}

// Create global instance
window.presetsDrawer = new PresetsDrawer();
