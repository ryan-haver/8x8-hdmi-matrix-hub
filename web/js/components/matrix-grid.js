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
        const breakpoints = [360, 390, 428, 768];
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
        this.render();
    }

    /**
     * Render the matrix grid
     */
    render() {
        // Only show loading spinner if loading AND no cached data
        // This keeps the UI intact during refreshes - data will update when it arrives
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

        this.container.className = 'matrix-grid loaded';
        
        let html = '';
        
        // Get responsive truncation length based on viewport
        // With horizontal scroll, we can use more generous lengths
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
            // Prefer Telnet-based cableConnected over HTTP displayConnected
            const hasCable = output.cableConnected !== null ? output.cableConnected : output.displayConnected;
            const hasSignal = output.signalActive;
            
            // Determine status class: signal (green) > cable (orange) > disconnected (red)
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
            // sourceDetected = HPD/5V from source device (device is powered on)
            const sourceDetected = input.cableConnected;
            
            // Status: signal (green) > source detected (orange) > off (red)
            let statusClass = 'status-disconnected';
            if (hasSignal) {
                statusClass = 'status-signal';
            } else if (sourceDetected === true) {
                statusClass = 'status-cable';
            } else if (sourceDetected === null) {
                statusClass = 'status-unknown';
            }
            
            // Input label with status color
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
        
        this.container.innerHTML = html;
        
        // Add click handlers
        this.container.querySelectorAll('.matrix-route').forEach(cell => {
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
