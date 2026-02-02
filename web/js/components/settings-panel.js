/**
 * OREI Matrix Control - Settings Panel Component
 */

class SettingsPanel {
    constructor() {
        this.modal = document.getElementById('settings-modal');
        this.edidModes = {};
        this.setupModal();
        
        // Subscribe to state changes
        state.on('info', () => this.updateInfo());
        state.on('system', () => this.updateSystemSettings());
    }

    /**
     * Initialize the panel
     */
    init() {
        this.setupEventListeners();
        this.generateEdidSettings();
    }

    /**
     * Setup modal open/close
     */
    setupModal() {
        const settingsBtn = document.getElementById('settings-btn');
        
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => this.open());
        }
        
        // Close handlers
        this.modal?.querySelectorAll('.modal-close, .modal-backdrop').forEach(el => {
            el.addEventListener('click', () => this.close());
        });
        
        // Close on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal?.getAttribute('aria-hidden') === 'false') {
                this.close();
            }
        });
    }

    /**
     * Setup event listeners for settings controls
     */
    setupEventListeners() {
        // LCD Timeout
        const lcdSelect = document.getElementById('lcd-timeout');
        if (lcdSelect) {
            lcdSelect.addEventListener('change', (e) => {
                this.setLcdTimeout(parseInt(e.target.value));
            });
        }

        // Beep toggle
        const beepToggle = document.getElementById('beep-enabled');
        if (beepToggle) {
            beepToggle.addEventListener('change', (e) => {
                this.setBeep(e.target.checked);
            });
        }

        // Power-on mode
        const powerOnSelect = document.getElementById('power-on-mode');
        if (powerOnSelect) {
            powerOnSelect.addEventListener('change', (e) => {
                this.setPowerOnMode(e.target.value);
            });
        }

        // External audio mode
        const extAudioSelect = document.getElementById('ext-audio-mode');
        if (extAudioSelect) {
            extAudioSelect.addEventListener('change', (e) => {
                this.setExtAudioMode(parseInt(e.target.value));
            });
        }

        // CEC buttons
        const cecPowerOnBtn = document.getElementById('cec-power-on-all');
        if (cecPowerOnBtn) {
            cecPowerOnBtn.addEventListener('click', () => this.cecPowerOnAll());
        }

        const cecStandbyBtn = document.getElementById('cec-standby-all');
        if (cecStandbyBtn) {
            cecStandbyBtn.addEventListener('click', () => this.cecStandbyAll());
        }
        
        // Power Cycle
        const powerCycleBtn = document.getElementById('power-cycle-btn');
        if (powerCycleBtn) {
            powerCycleBtn.addEventListener('click', () => this.powerCycle());
        }
        
        // Reboot
        const rebootBtn = document.getElementById('reboot-btn');
        if (rebootBtn) {
            rebootBtn.addEventListener('click', () => this.reboot());
        }
        
        // CEC Tray Position
        const cecTrayPositionSelect = document.getElementById('cec-tray-position');
        if (cecTrayPositionSelect) {
            // Load current position from state/localStorage
            const savedPosition = state.cecTray?.position || 'bottom-right';
            cecTrayPositionSelect.value = savedPosition;
            
            cecTrayPositionSelect.addEventListener('change', (e) => {
                const position = e.target.value;
                state.setCecTrayPosition(position);
                
                // Update the tray component
                if (window.cecTray) {
                    window.cecTray.savePosition(position);
                }
                
                toast.success(`CEC tray moved to ${position.replace('-', ' ')}`);
            });
        }
        
        // Debug FAB Toggle
        const debugFabToggle = document.getElementById('debug-fab-toggle');
        if (debugFabToggle) {
            // Load current state
            debugFabToggle.checked = localStorage.getItem('debug-fab-visible') === 'true';
            
            debugFabToggle.addEventListener('change', (e) => {
                if (window.debugPanel) {
                    window.debugPanel.saveFabVisibility(e.target.checked);
                }
            });
        }
        
        // TRON Animation Toggle
        const tronAnimationToggle = document.getElementById('tron-animation-toggle');
        if (tronAnimationToggle) {
            // Load current state
            tronAnimationToggle.checked = TronBackground.isEnabled();
            
            tronAnimationToggle.addEventListener('change', (e) => {
                TronBackground.setEnabled(e.target.checked);
                toast.success(e.target.checked ? 'Light cycle animation enabled' : 'Light cycle animation disabled');
            });
        }

        // Reduce Glow Toggle
        const reduceGlowToggle = document.getElementById('reduce-glow-toggle');
        if (reduceGlowToggle) {
            // Load current state from localStorage
            const glowReduced = localStorage.getItem('reduce-glow') === 'true';
            reduceGlowToggle.checked = glowReduced;
            if (glowReduced) {
                document.body.classList.add('reduced-glow');
            }
            
            reduceGlowToggle.addEventListener('change', (e) => {
                const reduced = e.target.checked;
                localStorage.setItem('reduce-glow', reduced);
                document.body.classList.toggle('reduced-glow', reduced);
                toast.success(reduced ? 'UI glow reduced' : 'Full UI glow restored');
            });
        }

        // Connection Settings
        this.setupConnectionSettings();
    }

    /**
     * Setup connection settings handlers
     */
    setupConnectionSettings() {
        const hostInput = document.getElementById('matrix-host-input');
        const saveBtn = document.getElementById('matrix-host-save');
        const testBtn = document.getElementById('matrix-host-test');
        const resetBtn = document.getElementById('matrix-host-reset');
        const statusEl = document.getElementById('matrix-connection-status');

        if (!hostInput) return;

        // Load current host value from backend
        this.loadMatrixHostFromBackend(hostInput);

        // Save button - sends new host to backend
        if (saveBtn) {
            saveBtn.addEventListener('click', async () => {
                const host = hostInput.value.trim();
                if (!host) {
                    toast.error('Please enter a valid IP address');
                    return;
                }
                
                this.updateConnectionStatus('Saving...', 'info');
                
                try {
                    const result = await api.post('/api/settings/matrix-host', { host });
                    if (result?.success) {
                        toast.success(`Matrix host set to ${host}`);
                        // Update state with new host info
                        if (result.data) {
                            state.setInfo({
                                ...state.info,
                                matrixHost: result.data.host
                            });
                        }
                        // Test the connection
                        await this.testConnection();
                    } else {
                        toast.error(result?.error || 'Failed to save host');
                        this.updateConnectionStatus(result?.error || 'Save failed', 'error');
                    }
                } catch (error) {
                    toast.error(`Failed to save: ${error.message}`);
                    this.updateConnectionStatus(`Error: ${error.message}`, 'error');
                }
            });
        }

        // Test button - tests backend's connection to matrix
        if (testBtn) {
            testBtn.addEventListener('click', () => this.testConnection());
        }

        // Reset button - clear input
        if (resetBtn) {
            resetBtn.addEventListener('click', async () => {
                hostInput.value = '';
                toast.info('Enter the matrix IP address');
                this.updateConnectionStatus('Enter matrix IP', 'info');
            });
        }

        // Set initial state - connection test happens when modal opens
        this.updateConnectionStatus('Connecting...', 'info');
    }

    /**
     * Load the current matrix host from the backend
     */
    async loadMatrixHostFromBackend(hostInput) {
        try {
            const result = await api.get('/api/settings');
            if (result?.success && result.data?.matrix_host) {
                hostInput.value = result.data.matrix_host;
            }
        } catch (e) {
            console.warn('Could not load matrix host from backend:', e);
        }
    }

    /**
     * Test connection to the matrix (via backend)
     */
    async testConnection() {
        this.updateConnectionStatus('Testing...', 'info');

        try {
            // Use the backend's test-connection endpoint
            const result = await api.post('/api/settings/test-connection', {});
            
            if (result?.success && result.data?.connected) {
                this.updateConnectionStatus('Connected ✓', 'success');
                // Update system info
                state.setInfo({
                    model: result.data.model || state.info.model,
                    firmwareVersion: result.data.firmware_version || state.info.firmwareVersion,
                    apiVersion: state.info.apiVersion,
                    matrixHost: result.data.host
                });
                this.updateInfo();
                return true;
            } else {
                const errorMsg = result?.data?.error || 'Connection failed';
                this.updateConnectionStatus(errorMsg, 'error');
                return false;
            }
        } catch (error) {
            this.updateConnectionStatus(`Error: ${error.message}`, 'error');
            return false;
        }
    }


    /**
     * Update connection status display
     */
    updateConnectionStatus(text, type = 'info') {
        const statusEl = document.getElementById('matrix-connection-status');
        if (statusEl) {
            statusEl.textContent = text;
            statusEl.className = 'info-value';
            if (type === 'success') statusEl.classList.add('text-success');
            else if (type === 'error') statusEl.classList.add('text-error');
        }
    }

    /**
     * Generate EDID settings for each input
     */
    async generateEdidSettings() {
        const container = document.getElementById('edid-settings');
        if (!container) return;

        // Load EDID modes
        try {
            const result = await api.getEdidModes();
            if (result?.success && result?.data?.modes) {
                this.edidModes = result.data.modes;
            } else {
                throw new Error('Invalid response format');
            }
        } catch (e) {
            console.warn('Could not load EDID modes:', e);
            this.edidModes = {
                1: '1080p 2CH',
                9: '4K60 2CH',
                12: '4K60 4:4:4 2CH',
                15: 'Copy Output 1',
                36: '4K60 HDR Atmos'
            };
        }

        let html = '';
        for (let i = 1; i <= 8; i++) {
            const inputName = state.inputs[i]?.name || `Input ${i}`;
            html += `
                <div class="port-setting">
                    <span class="port-setting-label">${inputName}</span>
                    <select class="select select-sm edid-select" data-input="${i}">
                        ${Object.entries(this.edidModes).map(([mode, name]) => 
                            `<option value="${mode}">${name}</option>`
                        ).join('')}
                    </select>
                </div>
            `;
        }
        container.innerHTML = html;

        // Add event listeners
        container.querySelectorAll('.edid-select').forEach(select => {
            select.addEventListener('change', (e) => {
                const input = parseInt(e.target.dataset.input);
                const mode = parseInt(e.target.value);
                this.setEdidMode(input, mode);
            });
        });
    }

    /**
     * Open settings modal
     */
    async open() {
        if (this.modal) {
            this.modal.setAttribute('aria-hidden', 'false');
            this.updateInfo();
            await this.loadCurrentSettings();
            // Automatically test connection when modal opens
            this.testConnection();
        }
    }

    /**
     * Close settings modal
     */
    close() {
        if (this.modal) {
            this.modal.setAttribute('aria-hidden', 'true');
        }
    }

    /**
     * Load current settings from API
     */
    async loadCurrentSettings() {
        try {
            const [systemStatus, extAudio] = await Promise.all([
                api.get('/api/status/system').catch(() => null),
                api.getExtAudioStatus().catch(() => null)
            ]);

            const sysData = systemStatus?.data;
            const extData = extAudio?.data;

            // Update LCD timeout - note: may need different endpoint
            // The system status doesn't include LCD timeout, 
            // so we skip this unless the endpoint returns it
            
            // Update beep
            if (sysData?.beep_enabled !== undefined) {
                const beepToggle = document.getElementById('beep-enabled');
                if (beepToggle) beepToggle.checked = sysData.beep_enabled;
            }

            // Update power-on mode - note: system status may not include this
            // keeping for compatibility if endpoint changes

            // Update ext audio mode
            if (extData?.mode !== undefined) {
                const extAudioSelect = document.getElementById('ext-audio-mode');
                if (extAudioSelect) extAudioSelect.value = extData.mode;
            }

            // Load current EDID settings for each input
            await this.loadCurrentEdidSettings();
        } catch (e) {
            console.warn('Could not load current settings:', e);
        }
    }

    /**
     * Load current EDID settings for each input
     */
    async loadCurrentEdidSettings() {
        try {
            const result = await api.get('/api/status/edid');
            if (result?.success && result?.data?.inputs) {
                result.data.inputs.forEach(input => {
                    const select = document.querySelector(`.edid-select[data-input="${input.number}"]`);
                    if (select && input.edid_mode !== null) {
                        select.value = input.edid_mode;
                    }
                });
            }
        } catch (e) {
            console.warn('Could not load current EDID settings:', e);
        }
    }

    /**
     * Update system info display
     */
    updateInfo() {
        const modelEl = document.getElementById('info-model');
        const firmwareEl = document.getElementById('info-firmware');
        const apiEl = document.getElementById('info-api');
        const serverIpEl = document.getElementById('info-server-ip');
        const matrixHostInput = document.getElementById('matrix-host-input');
        
        if (modelEl) modelEl.textContent = state.info.model || 'Unknown';
        if (firmwareEl) firmwareEl.textContent = state.info.firmwareVersion || 'Unknown';
        if (apiEl) apiEl.textContent = state.info.apiVersion || 'Unknown';
        
        // Server IP = this control software's address (the web app)
        if (serverIpEl) serverIpEl.textContent = window.location.origin || 'Unknown';
        
        // Matrix IP Address input = the configured matrix host being controlled
        if (matrixHostInput && state.info.matrixHost) {
            // Extract just the host/IP from the URL, removing protocol and port
            const matrixUrl = state.info.matrixHost || api.baseUrl || '';
            const hostOnly = matrixUrl.replace(/^https?:\/\//, '').replace(/:\d+$/, '');
            if (hostOnly && !matrixHostInput.value) {
                matrixHostInput.value = hostOnly;
            }
        }
    }

    /**
     * Update system settings display
     */
    updateSystemSettings() {
        // Called when system state changes
    }

    /**
     * Set LCD timeout mode
     */
    async setLcdTimeout(mode) {
        try {
            await api.setLcdTimeout(mode);
            const modeNames = ['Off', 'Always On', '15 seconds', '30 seconds', '60 seconds'];
            toast.success(`LCD timeout set to ${modeNames[mode] || mode}`);
        } catch (error) {
            toast.error(`Failed to set LCD timeout: ${error.message}`);
        }
    }

    /**
     * Set beep enabled
     */
    async setBeep(enabled) {
        try {
            await api.post('/api/system/beep', { enabled });
            toast.success(enabled ? 'Beep enabled' : 'Beep disabled');
        } catch (error) {
            toast.error(`Failed to set beep: ${error.message}`);
        }
    }

    /**
     * Set power-on mode
     */
    async setPowerOnMode(mode) {
        try {
            await api.post('/api/system/power-on-status', { status: mode });
            toast.success(`Power-on mode set to ${mode}`);
        } catch (error) {
            toast.error(`Failed to set power-on mode: ${error.message}`);
        }
    }

    /**
     * Set EDID mode for an input
     */
    async setEdidMode(input, mode) {
        try {
            await api.setEdidMode(input, mode);
            const modeName = this.edidModes[mode] || `Mode ${mode}`;
            toast.success(`Input ${input} EDID set to ${modeName}`);
        } catch (error) {
            toast.error(`Failed to set EDID: ${error.message}`);
        }
    }

    /**
     * Set external audio mode
     */
    async setExtAudioMode(mode) {
        try {
            await api.setExtAudioMode(mode);
            const modeNames = ['Follow Video', 'Independent', 'Mixer'];
            toast.success(`External audio mode set to ${modeNames[mode] || mode}`);
        } catch (error) {
            toast.error(`Failed to set external audio mode: ${error.message}`);
        }
    }

    /**
     * CEC power on all outputs
     */
    async cecPowerOnAll() {
        try {
            for (let i = 1; i <= 8; i++) {
                await api.sendCecCommand('output', i, 'power_on');
            }
            toast.success('Sent power on to all outputs');
        } catch (error) {
            toast.error(`CEC power on failed: ${error.message}`);
        }
    }

    /**
     * CEC standby all outputs
     */
    async cecStandbyAll() {
        try {
            for (let i = 1; i <= 8; i++) {
                await api.sendCecCommand('output', i, 'power_off');
            }
            toast.success('Sent standby to all outputs');
        } catch (error) {
            toast.error(`CEC standby failed: ${error.message}`);
        }
    }

    /**
     * Power cycle the matrix
     */
    async powerCycle() {
        if (!confirm('Power cycle the matrix? This will briefly disconnect all outputs.')) {
            return;
        }
        
        try {
            await api.powerCycle();
            toast.warning('Power cycling matrix...');
        } catch (error) {
            toast.error(`Failed to power cycle: ${error.message}`);
        }
    }

    /**
     * Reboot the matrix
     */
    async reboot() {
        if (!confirm('Reboot the matrix? This will take about 30 seconds.')) {
            return;
        }
        
        try {
            await api.reboot();
            toast.warning('Rebooting matrix... Please wait.');
            state.setConnected(false);
        } catch (error) {
            toast.error(`Failed to reboot: ${error.message}`);
        }
    }
}

// Export
window.SettingsPanel = SettingsPanel;
