/**
 * OREI Matrix Control - API Endpoint Copy Utility
 * 
 * Provides easy access to API endpoints for external integrations like Flic buttons.
 * Adds copy-to-clipboard functionality for endpoints throughout the UI.
 * 
 * @version 1.0.0
 */

class ApiCopyUtil {
    constructor() {
        this.modal = null;
        this.baseUrl = `http://${window.location.hostname}:8080`;
        // Defer modal creation until needed
    }
    
    /**
     * Ensure modal is created (lazy initialization)
     */
    ensureModal() {
        if (!this.modal) {
            this.createModal();
        }
    }

    /**
     * Create the API endpoint modal
     */
    createModal() {
        this.modal = document.createElement('div');
        this.modal.className = 'api-modal-backdrop';
        this.modal.id = 'api-copy-modal';
        this.modal.innerHTML = `
            <div class="api-modal">
                <div class="api-modal-header">
                    <h3>
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                        </svg>
                        API Endpoint
                    </h3>
                    <button class="btn-icon api-modal-close" aria-label="Close">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="api-modal-body">
                    <div class="api-modal-section">
                        <label>Item Name</label>
                        <div class="api-item-name" id="api-item-name"></div>
                    </div>
                    
                    <div class="api-modal-section">
                        <label>HTTP Method</label>
                        <span class="api-method" id="api-method">POST</span>
                    </div>
                    
                    <div class="api-modal-section">
                        <label>
                            Endpoint URL
                            <button class="btn-copy" data-copy="url" title="Copy URL">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                                </svg>
                            </button>
                        </label>
                        <code class="api-url" id="api-url"></code>
                    </div>
                    
                    <div class="api-modal-section" id="api-body-section" style="display: none;">
                        <label>
                            Request Body (JSON)
                            <button class="btn-copy" data-copy="body" title="Copy Body">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                                </svg>
                            </button>
                        </label>
                        <pre class="api-body" id="api-body"></pre>
                    </div>
                    
                    <div class="api-modal-section">
                        <label>
                            Full curl Command
                            <button class="btn-copy" data-copy="curl" title="Copy curl">
                                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                                </svg>
                            </button>
                        </label>
                        <pre class="api-curl" id="api-curl"></pre>
                    </div>
                    
                    <div class="api-modal-section api-flic-section">
                        <label>
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <circle cx="12" cy="12" r="6"/>
                                <circle cx="12" cy="12" r="2"/>
                            </svg>
                            Flic Button Configuration
                        </label>
                        <div class="api-flic-hint">
                            <p>In the Flic app, create an "Internet Request" action:</p>
                            <ol>
                                <li>Set URL to the endpoint above</li>
                                <li>Set Method to <strong id="flic-method">POST</strong></li>
                                <li id="flic-body-step" style="display: none;">Set Body to the JSON above</li>
                                <li>Set Content-Type to <code>application/json</code></li>
                            </ol>
                        </div>
                    </div>
                </div>
                <div class="api-modal-footer">
                    <button class="btn btn-primary copy-all-btn">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                        </svg>
                        Copy curl Command
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(this.modal);
        
        // Attach event listeners
        this.modal.querySelector('.api-modal-close').addEventListener('click', () => this.close());
        this.modal.querySelector('.api-modal-backdrop').addEventListener('click', (e) => {
            if (e.target === this.modal) this.close();
        });
        this.modal.querySelector('.copy-all-btn').addEventListener('click', () => this.copyField('curl'));
        
        // Copy buttons
        this.modal.querySelectorAll('.btn-copy').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const field = btn.dataset.copy;
                this.copyField(field);
            });
        });
        
        // Keyboard close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('open')) {
                this.close();
            }
        });
    }

    /**
     * Show the API modal with endpoint details
     * @param {Object} config - Endpoint configuration
     * @param {string} config.name - Display name of the item
     * @param {string} config.method - HTTP method (GET, POST, etc.)
     * @param {string} config.endpoint - API endpoint path (e.g., /api/preset/1)
     * @param {Object} [config.body] - Optional request body
     * @param {string} [config.description] - Optional description
     */
    show(config) {
        // Ensure modal is created (lazy init)
        this.ensureModal();
        
        const { name, method = 'POST', endpoint, body = null, description } = config;
        
        const fullUrl = `${this.baseUrl}${endpoint}`;
        
        // Update modal content
        this.modal.querySelector('#api-item-name').textContent = name;
        this.modal.querySelector('#api-method').textContent = method;
        this.modal.querySelector('#api-method').className = `api-method method-${method.toLowerCase()}`;
        this.modal.querySelector('#api-url').textContent = fullUrl;
        this.modal.querySelector('#flic-method').textContent = method;
        
        // Body section
        const bodySection = this.modal.querySelector('#api-body-section');
        const flicBodyStep = this.modal.querySelector('#flic-body-step');
        if (body) {
            const bodyJson = JSON.stringify(body, null, 2);
            this.modal.querySelector('#api-body').textContent = bodyJson;
            bodySection.style.display = 'block';
            flicBodyStep.style.display = 'list-item';
        } else {
            bodySection.style.display = 'none';
            flicBodyStep.style.display = 'none';
        }
        
        // Build curl command
        let curlCmd = `curl -X ${method} "${fullUrl}"`;
        if (body) {
            curlCmd += ` \\\n  -H "Content-Type: application/json" \\\n  -d '${JSON.stringify(body)}'`;
        }
        this.modal.querySelector('#api-curl').textContent = curlCmd;
        
        // Store current config for copying
        this._currentConfig = { fullUrl, method, body, curlCmd };
        
        // Show modal
        this.modal.classList.add('open');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close the modal
     */
    close() {
        this.modal.classList.remove('open');
        document.body.style.overflow = '';
    }

    /**
     * Copy a specific field to clipboard
     * @param {string} field - Field to copy: 'url', 'body', 'curl'
     */
    async copyField(field) {
        if (!this._currentConfig) return;
        
        let text = '';
        let label = '';
        
        switch (field) {
            case 'url':
                text = this._currentConfig.fullUrl;
                label = 'URL';
                break;
            case 'body':
                text = this._currentConfig.body ? JSON.stringify(this._currentConfig.body) : '';
                label = 'Body';
                break;
            case 'curl':
                text = this._currentConfig.curlCmd;
                label = 'curl command';
                break;
        }
        
        try {
            await navigator.clipboard.writeText(text);
            window.toast?.show(`${label} copied to clipboard!`, 'success', 2000);
        } catch (err) {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            window.toast?.show(`${label} copied to clipboard!`, 'success', 2000);
        }
    }

    /**
     * Create an API copy button element
     * @param {Object} config - Same config as show()
     * @returns {HTMLElement} Button element
     */
    createButton(config) {
        const btn = document.createElement('button');
        btn.className = 'btn-icon btn-api-copy';
        btn.title = 'Get API endpoint for Flic/automation';
        btn.innerHTML = `
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
            </svg>
        `;
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            this.show(config);
        });
        return btn;
    }

    // ========================================
    // Convenience methods for common endpoints
    // ========================================

    /**
     * Show API for a profile
     * @param {string} id - Profile ID
     * @param {string} name - Profile name
     */
    showProfile(id, name) {
        this.show({
            name: `Profile: ${name}`,
            method: 'POST',
            endpoint: `/api/profile/${encodeURIComponent(id)}/recall`,
            description: 'Activates this profile (sets routing and runs power-on macro if configured)'
        });
    }

    /**
     * Show API for a hardware preset
     * @param {number} preset - Preset number (1-8)
     * @param {string} [name] - Optional preset name
     */
    showPreset(preset, name = null) {
        this.show({
            name: name ? `Preset: ${name}` : `Hardware Preset ${preset}`,
            method: 'POST',
            endpoint: `/api/preset/${preset}`,
            description: 'Recalls this hardware preset on the matrix'
        });
    }

    /**
     * Show API for a CEC macro
     * @param {string} id - Macro ID
     * @param {string} name - Macro name
     */
    showMacro(id, name) {
        this.show({
            name: `Macro: ${name}`,
            method: 'POST',
            endpoint: `/api/cec/macro/${encodeURIComponent(id)}/execute`,
            description: 'Executes this CEC macro sequence'
        });
    }

    /**
     * Show API for switching input
     * @param {number} input - Input number (1-8)
     * @param {number} output - Output number (1-8)
     * @param {string} [inputName] - Optional input name
     * @param {string} [outputName] - Optional output name
     */
    showSwitch(input, output, inputName = null, outputName = null) {
        const name = inputName && outputName 
            ? `${inputName} → ${outputName}` 
            : `Input ${input} → Output ${output}`;
        this.show({
            name: `Route: ${name}`,
            method: 'POST',
            endpoint: '/api/switch',
            body: { input, output },
            description: 'Routes this input to this output'
        });
    }

    /**
     * Show API for cycling to next input
     * @param {number} output - Output number (1-8)
     * @param {string} [outputName] - Optional output name
     */
    showNextInput(output, outputName = null) {
        this.show({
            name: outputName ? `Next Input on ${outputName}` : `Next Input on Output ${output}`,
            method: 'POST',
            endpoint: `/api/input/next?output=${output}`,
            description: 'Cycles to the next available input on this output'
        });
    }

    /**
     * Show API for cycling to previous input
     * @param {number} output - Output number (1-8)
     * @param {string} [outputName] - Optional output name
     */
    showPreviousInput(output, outputName = null) {
        this.show({
            name: outputName ? `Previous Input on ${outputName}` : `Previous Input on Output ${output}`,
            method: 'POST',
            endpoint: `/api/input/previous?output=${output}`,
            description: 'Cycles to the previous available input on this output'
        });
    }

    /**
     * Show API for CEC command
     * @param {string} targetType - 'input' or 'output'
     * @param {number} port - Port number
     * @param {string} command - CEC command (e.g., 'power_on', 'play')
     * @param {string} [portName] - Optional port name
     */
    showCecCommand(targetType, port, command, portName = null) {
        const name = portName 
            ? `CEC ${command} → ${portName}` 
            : `CEC ${command} → ${targetType} ${port}`;
        this.show({
            name,
            method: 'POST',
            endpoint: `/api/cec/${targetType}/${port}/${command}`,
            description: `Sends ${command} CEC command to this ${targetType}`
        });
    }

    /**
     * Show API for power control
     * @param {boolean} on - Power on (true) or off (false)
     */
    showPower(on) {
        this.show({
            name: on ? 'Matrix Power On' : 'Matrix Power Off',
            method: 'POST',
            endpoint: `/api/power/${on ? 'on' : 'off'}`,
            description: on ? 'Powers on the matrix' : 'Powers off the matrix (standby)'
        });
    }

    /**
     * Show API for scene/profile recall (legacy)
     * @param {string} id - Scene ID
     * @param {string} name - Scene name
     */
    showScene(id, name) {
        // Redirect to profile API (scenes are now profiles)
        this.showProfile(id, name);
    }
    
    /**
     * Initialize the modal - called when DOM is ready
     */
    init() {
        if (!this.modal) {
            this.createModal();
        }
    }
}

// Create global instance immediately (class is defined, modal created lazily)
window.apiCopy = new ApiCopyUtil();
