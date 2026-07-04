/**
 * OREI Matrix Control - Matrix Grid Component
 * Interactive 8x8 routing matrix
 */

class MatrixGrid {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.inputCount = 8;
        this.outputCount = 8;
        this.pendingRoutes = new Set(); // Track pending route changes
        this.lastViewportWidth = window.innerWidth;
        this.viewMode = localStorage.getItem('matrix-view-mode') || (window.innerWidth < 1024 ? 'cards' : 'grid');
        this.activeOutputForSheet = null; // Track which output bottom sheet is open for
        
        // Subscribe to state changes
        state.on('routing', () => this.render());
        state.on('inputs', () => this.render());
        state.on('outputs', () => this.render());
        state.on('loading', (loading) => {
            if (!loading) this.render();
        });
        
        // Re-render on resize for responsive text truncation
        window.addEventListener('resize', this.handleResize.bind(this));
    }
    
    /**
     * Handle window resize - re-render if breakpoint crossed
     */
    handleResize() {
        const width = window.innerWidth;
        const breakpoints = [360, 390, 428, 768, 1024];
        const lastBreakpoint = breakpoints.find(bp => this.lastViewportWidth < bp) || Infinity;
        const currentBreakpoint = breakpoints.find(bp => width < bp) || Infinity;
        
        if (lastBreakpoint !== currentBreakpoint) {
            this.lastViewportWidth = width;
            this.render();
        }
    }

    /**
     * Initialize the grid
     */
    init() {
        this.setupViewToggle();
        this.setupBottomSheetEvents();
        this.render();
    }

    /**
     * Setup grid / cards view switcher in section title row
     */
    setupViewToggle() {
        const btnCards = document.getElementById('btn-view-cards');
        const btnGrid = document.getElementById('btn-view-grid');

        if (btnCards && btnGrid) {
            // Apply active class to current view mode button
            btnCards.classList.toggle('active', this.viewMode === 'cards');
            btnGrid.classList.toggle('active', this.viewMode === 'grid');

            btnCards.addEventListener('click', () => this.setViewMode('cards'));
            btnGrid.addEventListener('click', () => this.setViewMode('grid'));
        }
    }

    /**
     * Update active view mode, save to localStorage, and trigger re-render
     */
    setViewMode(mode) {
        if (this.viewMode === mode) return;
        this.viewMode = mode;
        localStorage.setItem('matrix-view-mode', mode);

        const btnCards = document.getElementById('btn-view-cards');
        const btnGrid = document.getElementById('btn-view-grid');
        if (btnCards && btnGrid) {
            btnCards.classList.toggle('active', mode === 'cards');
            btnGrid.classList.toggle('active', mode === 'grid');
        }

        this.render();
    }

    /**
     * Setup backdrop and escape key listeners for bottom sheet routing modal
     */
    setupBottomSheetEvents() {
        const sheet = document.getElementById('mobile-routing-sheet');
        if (!sheet) return;

        const backdrop = sheet.querySelector('.bottom-sheet-backdrop');
        if (backdrop) {
            backdrop.addEventListener('click', () => this.closeBottomSheet());
        }

        const handle = sheet.querySelector('.bottom-sheet-drag-handle');
        if (handle) {
            handle.addEventListener('click', () => this.closeBottomSheet());
        }

        // Close on escape key press
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sheet.classList.contains('open')) {
                this.closeBottomSheet();
            }
        });
    }

    /**
     * Open bottom sheet to select input source for specified output
     */
    openBottomSheet(outputNum) {
        this.activeOutputForSheet = outputNum;
        const sheet = document.getElementById('mobile-routing-sheet');
        if (!sheet) return;

        const outputName = state.getOutputName(outputNum);
        const titleEl = document.getElementById('mobile-routing-output-name');
        if (titleEl) {
            titleEl.textContent = outputName;
        }

        const inputsContainer = document.getElementById('mobile-routing-inputs');
        if (inputsContainer) {
            let html = '';
            const currentInput = state.routing[outputNum] || 0;

            for (let i = 1; i <= this.inputCount; i++) {
                const inputName = state.getInputName(i);
                const input = state.inputs[i] || {};
                const hasSignal = input.signalActive;
                const sourceDetected = input.cableConnected;
                const isActive = currentInput === i;

                let statusClass = 'status-disconnected';
                let statusText = 'Off';
                if (hasSignal) {
                    statusClass = 'status-signal';
                    statusText = 'Signal';
                } else if (sourceDetected === true) {
                    statusClass = 'status-cable';
                    statusText = 'Standby';
                }

                html += `
                    <div class="mobile-input-item ${isActive ? 'active' : ''}" data-input="${i}" role="button" tabindex="0">
                        <div class="mobile-input-item-info">
                            <span class="mobile-input-item-number">${i}</span>
                            <span class="mobile-input-item-name">${Helpers.escapeHtml(inputName)}</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: var(--space-2);">
                            <span class="mobile-input-item-badge ${statusClass}">${statusText}</span>
                            <span class="mobile-input-item-checkmark">✓</span>
                        </div>
                    </div>
                `;
            }
            inputsContainer.innerHTML = html;

            // Attach listeners
            inputsContainer.querySelectorAll('.mobile-input-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    const inputNum = parseInt(e.currentTarget.dataset.input);
                    this.selectInputFromSheet(inputNum);
                });
                item.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        const inputNum = parseInt(e.currentTarget.dataset.input);
                        this.selectInputFromSheet(inputNum);
                    }
                });
            });
        }

        sheet.classList.add('open');
        sheet.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';

        // Focus the active item for keyboard accessibility
        setTimeout(() => {
            const activeItem = inputsContainer?.querySelector('.mobile-input-item.active');
            if (activeItem) activeItem.focus();
        }, 50);
    }

    /**
     * Close the mobile routing bottom sheet
     */
    closeBottomSheet() {
        const sheet = document.getElementById('mobile-routing-sheet');
        if (sheet) {
            sheet.classList.remove('open');
            sheet.setAttribute('aria-hidden', 'true');
        }
        document.body.style.overflow = '';
        this.activeOutputForSheet = null;
    }

    /**
     * Execute routing switch command from bottom sheet item select
     */
    async selectInputFromSheet(inputNum) {
        const outputNum = this.activeOutputForSheet;
        if (!outputNum) return;

        // Close immediately if active
        if (state.routing[outputNum] === inputNum) {
            this.closeBottomSheet();
            return;
        }

        // Toggle active visuals on clicked option
        const items = document.querySelectorAll('.mobile-input-item');
        items.forEach(item => {
            const isTarget = parseInt(item.dataset.input) === inputNum;
            item.classList.toggle('active', isTarget);
        });

        // 180ms delay for visual selection animation response before slide close
        setTimeout(async () => {
            this.closeBottomSheet();
            try {
                await api.switchInput(outputNum, inputNum);
                state.setRoute(outputNum, inputNum);
                toast.success(`Routed Input ${inputNum} → Output ${outputNum}`);
            } catch (error) {
                toast.error(`Failed to switch: ${error.message}`);
                this.render();
            }
        }, 180);
    }

    /**
     * Mute action delegator linking to OutputPanel helper
     */
    toggleMute(output) {
        if (window.app && window.app.components.outputPanel) {
            window.app.components.outputPanel.toggleMute(output);
        }
    }

    /**
     * Settings modal delegator linking to OutputPanel helper
     */
    showOutputSettings(output) {
        if (window.app && window.app.components.outputPanel) {
            window.app.components.outputPanel.showOutputSettings(output);
        }
    }

    /**
     * Render the active layout layout container
     */
    render() {
        const hasData = Object.keys(state.routing).length > 0;
        if (state.ui.loading && !hasData) {
            this.container.innerHTML = `
                <div class="matrix-loading">
                    <div class="spinner"></div>
                    <p>Loading matrix...</p>
                </div>
            `;
            return;
        }

        const gridEl = document.getElementById('matrix-grid');
        const cardsEl = document.getElementById('matrix-mobile-view');

        if (!gridEl || !cardsEl) return;

        // Render appropriate container and trigger view builder
        if (this.viewMode === 'cards') {
            gridEl.classList.add('hidden');
            cardsEl.classList.remove('hidden');
            this.renderOutputCards(cardsEl);
        } else {
            cardsEl.classList.add('hidden');
            gridEl.classList.remove('hidden');
            gridEl.className = 'matrix-grid loaded';
            this.renderGrid(gridEl);
        }
    }

    /**
     * Render classic 8x8 Grid Matrix View
     */
    renderGrid(container) {
        let html = '';
        
        const viewportWidth = window.innerWidth;
        let outputTruncLen = 8;
        let inputTruncLen = 10;
        
        if (viewportWidth < 360) {
            outputTruncLen = 5;
            inputTruncLen = 6;
        } else if (viewportWidth < 390) {
            outputTruncLen = 5;
            inputTruncLen = 7;
        } else if (viewportWidth < 428) {
            outputTruncLen = 6;
            inputTruncLen = 8;
        } else if (viewportWidth < 768) {
            outputTruncLen = 6;
            inputTruncLen = 8;
        }
        
        // Header row with output labels
        html += '<div class="matrix-cell matrix-header corner"></div>';
        for (let o = 1; o <= this.outputCount; o++) {
            const outputName = state.getOutputName(o);
            const shortName = this.truncateName(outputName, outputTruncLen);
            const output = state.outputs[o] || {};
            const hasCable = output.cableConnected !== null ? output.cableConnected : output.displayConnected;
            const hasSignal = output.signalActive;
            
            let statusClass = 'status-disconnected';
            if (hasSignal) {
                statusClass = 'status-signal';
            } else if (hasCable) {
                statusClass = 'status-cable';
            }
            
            html += `<div class="matrix-cell matrix-header ${statusClass}" title="${Helpers.escapeHtml(outputName)}">
                ${Helpers.escapeHtml(shortName)}
            </div>`;
        }
        
        // Input rows
        for (let i = 1; i <= this.inputCount; i++) {
            const inputName = state.getInputName(i);
            const shortName = this.truncateName(inputName, inputTruncLen);
            const input = state.inputs[i] || {};
            const hasSignal = input.signalActive;
            const sourceDetected = input.cableConnected;
            
            let statusClass = 'status-disconnected';
            if (hasSignal) {
                statusClass = 'status-signal';
            } else if (sourceDetected === true) {
                statusClass = 'status-cable';
            } else if (sourceDetected === null) {
                statusClass = 'status-unknown';
            }
            
            html += `<div class="matrix-cell matrix-input-label ${statusClass}" title="${Helpers.escapeHtml(inputName)}">
                ${Helpers.escapeHtml(shortName)}
            </div>`;
            
            // Route cells
            for (let o = 1; o <= this.outputCount; o++) {
                const isActive = state.routing[o] === i;
                const isPending = this.pendingRoutes.has(`${o}-${i}`);
                const cellClass = isPending ? 'pending' : (isActive ? 'active' : '');
                
                html += `
                    <div class="matrix-cell matrix-route ${cellClass}" 
                         data-input="${i}" 
                         data-output="${o}"
                         title="Route Input ${i} to Output ${o}"
                         role="button"
                         tabindex="0">
                        <span class="matrix-dot"></span>
                    </div>
                `;
            }
        }
        
        container.innerHTML = html;
        
        // Add click handlers
        container.querySelectorAll('.matrix-route').forEach(cell => {
            cell.addEventListener('click', (e) => this.handleCellClick(e));
            cell.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.handleCellClick(e);
                }
            });
        });
    }

    /**
     * Render responsive list/grid output cards for Mobile & Tablet
     */
    renderOutputCards(container) {
        let html = '';
        
        for (let o = 1; o <= this.outputCount; o++) {
            const currentInput = state.routing[o] || 0;
            const inputName = state.getInputName(currentInput);
            const output = state.outputs[o] || {};
            const outputName = state.getOutputName(o);
            const isMuted = output.audioMuted;
            const hasCable = output.cableConnected !== null ? output.cableConnected : output.displayConnected;
            const hasSignal = output.signalActive;
            const isEnabled = output.enabled !== false;
            
            let statusClass = 'output-disconnected';
            let statusText = 'No Cable';
            
            if (hasCable && hasSignal) {
                statusClass = 'output-active';
                statusText = 'Active Signal';
            } else if (hasCable) {
                statusClass = 'output-connected';
                statusText = 'Connected';
            } else if (hasCable === false) {
                statusClass = 'output-disconnected';
                statusText = 'Disconnected';
            } else if (!isEnabled) {
                statusClass = 'output-disabled';
                statusText = 'Disabled';
            }
            
            html += `
                <div class="io-card ${statusClass} routing-card" data-output="${o}">
                    <div class="io-number">${o}</div>
                    <div class="io-info">
                        <div class="io-name">${Helpers.escapeHtml(outputName)}</div>
                        <div class="io-status-row">
                            <span class="status-dot" style="background-color: var(--status-${hasCable && hasSignal ? 'active' : (hasCable ? 'standby' : 'disconnected')});"></span>
                            <span class="io-status-text">${statusText}</span>
                            ${isMuted ? '<span class="muted-badge" style="margin-left: 4px;">🔇</span>' : ''}
                        </div>
                        
                        <div class="io-card-route-selector" data-output="${o}" role="button" tabindex="0" title="Select input source">
                            <div style="display: flex; flex-direction: column; align-items: flex-start;">
                                <span class="io-card-route-selector-label">Active Source</span>
                                <span class="io-card-route-selector-value">${Helpers.escapeHtml(inputName)}</span>
                            </div>
                            <span class="io-card-route-selector-arrow">▼</span>
                        </div>
                    </div>
                    <div class="io-actions">
                        <button class="btn-icon card-cec-btn" data-output="${o}" title="CEC Control">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                                <line x1="8" y1="21" x2="16" y2="21"/>
                                <line x1="12" y1="17" x2="12" y2="21"/>
                            </svg>
                        </button>
                        <button class="btn-icon card-mute-btn ${isMuted ? 'active' : ''}" 
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
                        <button class="btn-icon card-settings-btn" data-output="${o}" title="Output settings">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="3"/>
                                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                            </svg>
                        </button>
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
        
        // Attach source selector events
        container.querySelectorAll('.io-card-route-selector').forEach(selector => {
            selector.addEventListener('click', (e) => {
                const outputNum = parseInt(e.currentTarget.dataset.output);
                this.openBottomSheet(outputNum);
            });
            selector.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const outputNum = parseInt(e.currentTarget.dataset.output);
                    this.openBottomSheet(outputNum);
                }
            });
        });
        
        // Attach card actions
        container.querySelectorAll('.card-mute-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const output = parseInt(e.currentTarget.dataset.output);
                this.toggleMute(output);
            });
        });
        
        container.querySelectorAll('.card-cec-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const output = parseInt(e.currentTarget.dataset.output);
                cecControls.showDropdown('output', output, e.currentTarget);
            });
        });
        
        container.querySelectorAll('.card-settings-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const output = parseInt(e.currentTarget.dataset.output);
                this.showOutputSettings(output);
            });
        });
    }

    /**
     * Handle matrix cell click
     */
    async handleCellClick(event) {
        const cell = event.target.closest('.matrix-route');
        if (!cell) return;
        
        const input = parseInt(cell.dataset.input);
        const output = parseInt(cell.dataset.output);
        
        // Don't do anything if already active
        if (state.routing[output] === input) {
            return;
        }
        
        // Mark as pending
        const pendingKey = `${output}-${input}`;
        this.pendingRoutes.add(pendingKey);
        this.render();
        
        try {
            await api.switchInput(output, input);
            state.setRoute(output, input);
            toast.success(`Routed Input ${input} → Output ${output}`);
        } catch (error) {
            toast.error(`Failed to switch: ${error.message}`);
        } finally {
            this.pendingRoutes.delete(pendingKey);
            this.render();
        }
    }

    /**
     * Route all outputs to a single input
     */
    async routeAll(input) {
        toast.info(`Routing Input ${input} to all outputs...`);
        
        try {
            await api.switchAll(input);
            
            // Update local state
            for (let o = 1; o <= this.outputCount; o++) {
                state.setRoute(o, input);
            }
            
            toast.success(`All outputs now showing Input ${input}`);
        } catch (error) {
            toast.error(`Failed to route all: ${error.message}`);
        }
    }

    /**
     * Truncate name to max length
     */
    truncateName(name, maxLength) {
        if (name.length <= maxLength) return name;
        return name.substring(0, maxLength - 1) + '…';
    }
}

// Export
window.MatrixGrid = MatrixGrid;
