/**
 * OREI Matrix Control - HDMI Status Dropdown Component
 * Dropdown panel showing signal/connection status for all inputs and outputs
 * Triggered from a button in the header
 */

class HdmiStatusTray {
    constructor() {
        this.isOpen = false;
        this.dropdownElement = null;
        
        // Subscribe to state changes
        state.on('inputs', () => this.updateSummary());
        state.on('outputs', () => this.updateSummary());
        state.on('routing', () => {
            if (this.isOpen) this.renderContent();
        });
        
        // Close on outside click
        document.addEventListener('click', (e) => this.handleOutsideClick(e));
    }

    /**
     * Initialize the component - creates the button and dropdown in the header
     */
    init() {
        this.createHeaderButton();
        this.createDropdown();
        this.updateSummary();
    }

    /**
     * Create the header button
     */
    createHeaderButton() {
        const headerRight = document.querySelector('.header-right');
        if (!headerRight) return;
        
        // Find the quick-actions-btn to insert before it
        const quickActionsBtn = document.getElementById('quick-actions-btn');
        
        const button = document.createElement('button');
        button.id = 'hdmi-status-btn';
        button.className = 'btn-icon hdmi-status-header-btn';
        button.setAttribute('aria-label', 'HDMI Status');
        button.setAttribute('title', 'HDMI Status');
        button.innerHTML = `
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M2 8h20M2 8v10a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8M2 8V6a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v2"/>
                <circle cx="7" cy="13" r="1.5" fill="currentColor"/>
                <circle cx="12" cy="13" r="1.5" fill="currentColor"/>
                <circle cx="17" cy="13" r="1.5" fill="currentColor"/>
            </svg>
        `;
        
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        if (quickActionsBtn) {
            headerRight.insertBefore(button, quickActionsBtn);
        } else {
            headerRight.insertBefore(button, headerRight.firstChild);
        }
    }

    /**
     * Create the dropdown panel
     */
    createDropdown() {
        const dropdown = document.createElement('div');
        dropdown.id = 'hdmi-status-dropdown';
        dropdown.className = 'hdmi-status-dropdown';
        dropdown.innerHTML = '<div class="hdmi-dropdown-loading">Loading...</div>';
        
        document.body.appendChild(dropdown);
        this.dropdownElement = dropdown;
    }

    /**
     * Toggle dropdown visibility
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Open the dropdown
     */
    open() {
        this.isOpen = true;
        this.renderContent();
        this.positionDropdown();
        this.dropdownElement.classList.add('open');
        document.getElementById('hdmi-status-btn')?.classList.add('active');
    }

    /**
     * Close the dropdown
     */
    close() {
        this.isOpen = false;
        this.dropdownElement.classList.remove('open');
        document.getElementById('hdmi-status-btn')?.classList.remove('active');
    }

    /**
     * Position dropdown below the button
     */
    positionDropdown() {
        const button = document.getElementById('hdmi-status-btn');
        if (!button || !this.dropdownElement) return;
        
        const rect = button.getBoundingClientRect();
        const isMobile = window.innerWidth <= 480;
        
        if (isMobile) {
            // On mobile, CSS handles full-width positioning
            // Just set top position below button
            const topPos = rect.bottom + 8;
            const maxTop = window.innerHeight - 300; // Leave room for dropdown
            this.dropdownElement.style.top = `${Math.min(topPos, maxTop)}px`;
            this.dropdownElement.style.left = '';
        } else {
            const dropdownWidth = 320;
            
            // Position below button, aligned to right edge
            let left = rect.right - dropdownWidth;
            if (left < 10) left = 10;
            
            // Check if dropdown would go off bottom
            let top = rect.bottom + 8;
            const dropdownHeight = Math.min(400, window.innerHeight * 0.6);
            if (top + dropdownHeight > window.innerHeight - 20) {
                top = Math.max(10, window.innerHeight - dropdownHeight - 20);
            }
            
            this.dropdownElement.style.top = `${top}px`;
            this.dropdownElement.style.left = `${left}px`;
        }
    }

    /**
     * Handle clicks outside the dropdown
     */
    handleOutsideClick(e) {
        if (!this.isOpen) return;
        
        const dropdown = this.dropdownElement;
        const button = document.getElementById('hdmi-status-btn');
        
        if (!dropdown?.contains(e.target) && !button?.contains(e.target)) {
            this.close();
        }
    }

    /**
     * Update the summary badge in the header button
     */
    updateSummary() {
        const summary = this.getStatusSummary();
        const button = document.getElementById('hdmi-status-btn');
        
        // Update button tooltip
        if (button) {
            button.title = `HDMI Status: ${summary.activeInputs} inputs, ${summary.connectedOutputs} displays`;
        }
        
        // If dropdown is open, refresh content
        if (this.isOpen) {
            this.renderContent();
        }
    }

    /**
     * Get signal status summary
     */
    getStatusSummary() {
        let activeInputs = 0;
        let connectedOutputs = 0;
        
        for (let i = 1; i <= state.info.inputCount; i++) {
            // Count inputs with signal OR with cable connected (source detected)
            const input = state.inputs[i];
            if (input?.signalActive || input?.cableConnected) activeInputs++;
        }
        
        for (let o = 1; o <= state.info.outputCount; o++) {
            // Prefer Telnet-based cableConnected over HTTP displayConnected
            const output = state.outputs[o];
            const hasCable = output?.cableConnected !== null 
                ? output.cableConnected 
                : output?.displayConnected;
            if (hasCable) connectedOutputs++;
        }
        
        return { activeInputs, connectedOutputs };
    }

    /**
     * Render dropdown content
     */
    renderContent() {
        if (!this.dropdownElement) return;
        
        const summary = this.getStatusSummary();
        let inputsHtml = '';
        let outputsHtml = '';
        
        // Inputs - show source detection and signal status
        // sourceDetected (cableConnected) = HPD/5V from source device
        // signalActive = actual video signal present
        for (let i = 1; i <= state.info.inputCount; i++) {
            const input = state.inputs[i] || {};
            const name = state.getInputName(i);
            const hasSignal = input.signalActive;
            const sourceDetected = input.cableConnected; // HPD: null = unknown, true = source on, false = source off
            
            // Status priority: Signal > Source Detected > Off
            let statusClass = 'input-unknown';
            let statusLabel = 'Unknown';
            
            if (hasSignal) {
                statusClass = 'input-active';
                statusLabel = 'Active';
            } else if (sourceDetected === true) {
                statusClass = 'input-connected';
                statusLabel = 'Standby';
            } else if (sourceDetected === false) {
                statusClass = 'input-disconnected';
                statusLabel = 'Off';
            }
            
            inputsHtml += `
                <div class="hdmi-status-item ${statusClass}">
                    <span class="hdmi-status-num">${i}</span>
                    <span class="hdmi-status-name" title="${Helpers.escapeHtml(name)}">${Helpers.escapeHtml(name)}</span>
                    <span class="hdmi-status-label">${statusLabel}</span>
                </div>
            `;
        }
        
        // Outputs - show cable (direct) and signal (inferred from routed input)
        for (let o = 1; o <= state.info.outputCount; o++) {
            const output = state.outputs[o] || {};
            const name = state.getOutputName(o);
            const currentInput = state.routing[o] || 0;
            const inputName = state.getInputName(currentInput);
            // Prefer Telnet-based cableConnected over HTTP displayConnected
            const hasCable = output.cableConnected !== null ? output.cableConnected : output.displayConnected;
            const hasSignal = output.signalActive; // Inferred from cable + routed input signal
            const isEnabled = output.enabled !== false;
            
            // Cable/signal status takes priority over enabled status
            let statusClass = 'output-disabled';
            let statusLabel = 'Disabled';
            
            if (hasCable && hasSignal) {
                statusClass = 'output-active';
                statusLabel = 'Active';
            } else if (hasCable) {
                statusClass = 'output-connected';
                statusLabel = 'No Signal';
            } else if (hasCable === false) {
                // Explicitly no cable - show red
                statusClass = 'output-disconnected';
                statusLabel = 'No Cable';
            } else if (!isEnabled) {
                // Unknown cable status but disabled
                statusClass = 'output-disabled';
                statusLabel = 'Disabled';
            } else {
                // Unknown cable status, enabled - treat as disconnected
                statusClass = 'output-disconnected';
                statusLabel = 'No Cable';
            }
            
            outputsHtml += `
                <div class="hdmi-status-item ${statusClass}">
                    <span class="hdmi-status-num">${o}</span>
                    <span class="hdmi-status-name" title="${Helpers.escapeHtml(name)}">${Helpers.escapeHtml(name)}</span>
                    <span class="hdmi-status-source">← ${Helpers.escapeHtml(inputName)}</span>
                    <span class="hdmi-status-label">${statusLabel}</span>
                </div>
            `;
        }
        
        this.dropdownElement.innerHTML = `
            <div class="hdmi-dropdown-header">
                <span class="hdmi-dropdown-title">HDMI Status</span>
                <button class="hdmi-dropdown-close" id="hdmi-dropdown-close" aria-label="Close">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
            <div class="hdmi-dropdown-content">
                <div class="hdmi-status-section">
                    <h4 class="hdmi-section-title">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
                        </svg>
                        Inputs
                    </h4>
                    <div class="hdmi-status-grid">
                        ${inputsHtml}
                    </div>
                </div>
                <div class="hdmi-status-section">
                    <h4 class="hdmi-section-title">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="2" y="3" width="20" height="14" rx="2"/>
                            <path d="M8 21h8M12 17v4"/>
                        </svg>
                        Outputs
                    </h4>
                    <div class="hdmi-status-grid">
                        ${outputsHtml}
                    </div>
                </div>
            </div>
        `;
        
        // Attach close button listener
        const closeBtn = document.getElementById('hdmi-dropdown-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.close());
        }
    }

}
