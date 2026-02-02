/**
 * OREI Matrix Control - CEC Controls Component
 * Provides CEC power/navigation/playback controls for inputs and outputs
 */

class CecControls {
    constructor() {
        this.activeDropdown = null;
        this.activeType = null;
        this.activePort = null;
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (this.activeDropdown && !e.target.closest('.cec-dropdown') && !e.target.closest('.cec-btn')) {
                this.closeDropdown();
            }
        });
    }

    /**
     * Show CEC control dropdown for a device
     * @param {string} type - 'input' or 'output'
     * @param {number} port - Port number (1-8)
     * @param {HTMLElement} anchorElement - Element to anchor dropdown to
     */
    showDropdown(type, port, anchorElement) {
        // Close any existing dropdown
        this.closeDropdown();
        
        const isInput = type === 'input';
        const name = isInput ? state.getInputName(port) : state.getOutputName(port);
        
        // Create dropdown element
        const dropdown = document.createElement('div');
        dropdown.className = 'cec-dropdown';
        dropdown.innerHTML = this.renderDropdownContent(type, port, name, isInput);
        
        // Position dropdown
        const rect = anchorElement.getBoundingClientRect();
        const isMobile = window.innerWidth <= 480;
        
        dropdown.style.position = 'fixed';
        dropdown.style.zIndex = '1000';
        
        if (isMobile) {
            // On mobile, let CSS handle the full-width positioning
            // Just set a reasonable top position
            const topPos = rect.bottom + 4;
            const maxTop = window.innerHeight - 250;
            dropdown.style.top = `${Math.min(topPos, maxTop)}px`;
        } else {
            dropdown.style.top = `${rect.bottom + 4}px`;
            dropdown.style.left = `${rect.left}px`;
        }
        
        document.body.appendChild(dropdown);
        this.activeDropdown = dropdown;
        this.activeType = type;
        this.activePort = port;
        
        // Attach event listeners
        this.attachDropdownListeners(dropdown, type, port);
        
        // Adjust if off-screen (desktop only)
        if (!isMobile) {
            const dropdownRect = dropdown.getBoundingClientRect();
            if (dropdownRect.right > window.innerWidth) {
                dropdown.style.left = `${window.innerWidth - dropdownRect.width - 8}px`;
            }
            if (dropdownRect.left < 10) {
                dropdown.style.left = '10px';
            }
            if (dropdownRect.bottom > window.innerHeight) {
                dropdown.style.top = `${rect.top - dropdownRect.height - 4}px`;
            }
        }
    }

    /**
     * Close active dropdown
     */
    closeDropdown() {
        if (this.activeDropdown) {
            this.activeDropdown.remove();
            this.activeDropdown = null;
            this.activeType = null;
            this.activePort = null;
        }
    }

    /**
     * Render dropdown content
     */
    renderDropdownContent(type, port, name, isInput) {
        return `
            <div class="cec-dropdown-header">
                <span class="cec-device-name">${Helpers.escapeHtml(name)}</span>
                <span class="cec-device-type">${isInput ? 'Source' : 'Display'} CEC</span>
            </div>
            
            <div class="cec-section">
                <div class="cec-section-title">Power</div>
                <div class="cec-btn-group">
                    <button class="cec-cmd-btn" data-cmd="power_on" title="Power On">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <line x1="12" y1="6" x2="12" y2="12"/>
                        </svg>
                        On
                    </button>
                    <button class="cec-cmd-btn" data-cmd="power_off" title="Power Off">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18.36 6.64a9 9 0 1 1-12.73 0"/>
                            <line x1="12" y1="2" x2="12" y2="12"/>
                        </svg>
                        Off
                    </button>
                </div>
            </div>
            
            <div class="cec-section">
                <div class="cec-section-title">Navigation</div>
                <div class="cec-dpad">
                    <button class="cec-cmd-btn dpad-up" data-cmd="up" title="Up">▲</button>
                    <button class="cec-cmd-btn dpad-left" data-cmd="left" title="Left">◀</button>
                    <button class="cec-cmd-btn dpad-center" data-cmd="select" title="Select">OK</button>
                    <button class="cec-cmd-btn dpad-right" data-cmd="right" title="Right">▶</button>
                    <button class="cec-cmd-btn dpad-down" data-cmd="down" title="Down">▼</button>
                </div>
                <div class="cec-btn-group nav-extra">
                    <button class="cec-cmd-btn" data-cmd="menu" title="Menu">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="3" y1="12" x2="21" y2="12"/>
                            <line x1="3" y1="6" x2="21" y2="6"/>
                            <line x1="3" y1="18" x2="21" y2="18"/>
                        </svg>
                        Menu
                    </button>
                    <button class="cec-cmd-btn" data-cmd="back" title="Back">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="19" y1="12" x2="5" y2="12"/>
                            <polyline points="12 19 5 12 12 5"/>
                        </svg>
                        Back
                    </button>
                </div>
            </div>
            
            ${isInput ? `
            <div class="cec-section">
                <div class="cec-section-title">Playback</div>
                <div class="cec-btn-group">
                    <button class="cec-cmd-btn" data-cmd="previous" title="Previous">⏮</button>
                    <button class="cec-cmd-btn" data-cmd="rewind" title="Rewind">⏪</button>
                    <button class="cec-cmd-btn" data-cmd="play" title="Play">▶</button>
                    <button class="cec-cmd-btn" data-cmd="pause" title="Pause">⏸</button>
                    <button class="cec-cmd-btn" data-cmd="stop" title="Stop">⏹</button>
                    <button class="cec-cmd-btn" data-cmd="fast_forward" title="Fast Forward">⏩</button>
                    <button class="cec-cmd-btn" data-cmd="next" title="Next">⏭</button>
                </div>
            </div>
            ` : ''}
            
            <div class="cec-section">
                <div class="cec-section-title">Volume</div>
                <div class="cec-btn-group">
                    <button class="cec-cmd-btn" data-cmd="volume_down" title="Volume Down">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                        </svg>
                        −
                    </button>
                    <button class="cec-cmd-btn" data-cmd="mute" title="Mute">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                            <line x1="23" y1="9" x2="17" y2="15"/>
                            <line x1="17" y1="9" x2="23" y2="15"/>
                        </svg>
                        Mute
                    </button>
                    <button class="cec-cmd-btn" data-cmd="volume_up" title="Volume Up">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
                        </svg>
                        +
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Attach event listeners to dropdown buttons
     */
    attachDropdownListeners(dropdown, type, port) {
        dropdown.querySelectorAll('.cec-cmd-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const cmd = e.currentTarget.dataset.cmd;
                await this.sendCommand(type, port, cmd);
            });
        });
    }

    /**
     * Send CEC command
     */
    async sendCommand(type, port, command) {
        const name = type === 'input' ? state.getInputName(port) : state.getOutputName(port);
        
        try {
            const result = await api.sendCecCommand(type, port, command);
            if (result?.success) {
                toast.success(`CEC: ${command.replace('_', ' ')} sent to ${name}`);
            } else {
                toast.error(`CEC command failed: ${result?.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('CEC command error:', error);
            toast.error(`CEC error: ${error.message}`);
        }
    }
}

// Global instance
const cecControls = new CecControls();
