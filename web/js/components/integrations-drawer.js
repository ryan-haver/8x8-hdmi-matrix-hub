/**
 * OREI Matrix Control - Integrations Drawer Component
 * Handles onboarding instructions and pairing/assignment utilities for:
 * - Flic Smart Buttons (Internet Request & Hub SDK Javascript generator)
 * - Home Assistant (HACS Component & REST commands YAML generator)
 * - Unfolded Circle Remote 3 (mDNS / manual driver info)
 */

class IntegrationsDrawer {
    constructor() {
        this.isOpen = false;
        this.container = null;
        this.backdrop = null;
        this.activeTab = 'flic'; // Default tab

        this.discoveredButtons = [];

        // Helper state
        this.flicConfig = {
            buttonType: 'button', // 'button', 'twist', 'duo'
            buttonIdentifier: '', // Optional name/bdaddr filtering
            targetType: 'preset', // 'preset', 'profile', 'switch_all', 'switch_output', 'cycle_input', 'volume_control', 'power', 'cec'
            presetNum: 1,
            profileId: '',
            inputNum: 1,
            outputNum: 1,
            cycleDir: 'next',
            volDir: 'volume_up',
            cecCmd: 'power_on',
            cecTargetType: 'input',
            cecTargetPort: 1,
            powerCmd: 'on',
            gesture: 'single' // 'single', 'double', 'hold', 'rotate_cw', 'rotate_ccw', and duo variations
        };

        this.haConfig = {
            includePresets: true,
            includePower: true,
            includeInputCycling: true,
            includeRouting: false
        };

        // Listen for state changes that might affect dropdown lists
        state.on('profiles', () => this.updateDynamicInputs());
        
        this.createDrawer();
    }

    /**
     * Create the drawer structure in the DOM
     */
    createDrawer() {
        // Create backdrop
        this.backdrop = document.createElement("div");
        this.backdrop.id = "integrations-drawer-backdrop";
        this.backdrop.className = "settings-drawer-backdrop";
        this.backdrop.addEventListener("click", () => this.close());
        document.body.appendChild(this.backdrop);

        // Create drawer aside container
        const drawer = document.createElement("aside");
        drawer.id = "integrations-drawer";
        drawer.className = "settings-drawer integrations-drawer";
        drawer.setAttribute("aria-hidden", "true");
        drawer.setAttribute("role", "dialog");
        drawer.setAttribute("aria-label", "System Integrations");
        
        drawer.innerHTML = `
            <div class="drawer-header">
                <h3>
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M18 8h1a4 4 0 0 1 0 8h-1" />
                        <path d="M6 8h-1a4 4 0 0 0 0 8h1" />
                        <line x1="2" y1="12" x2="5" y2="12" />
                        <line x1="19" y1="12" x2="22" y2="12" />
                        <rect x="6" y="5" width="12" height="14" rx="2" />
                    </svg>
                    System Integrations
                </h3>
                <button class="btn-icon drawer-close" aria-label="Close drawer" title="Close">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                </button>
            </div>

            <div class="drawer-tabs">
                <button class="drawer-tab-btn active" data-tab="flic">Flic Buttons</button>
                <button class="drawer-tab-btn" data-tab="ha">Home Assistant</button>
                <button class="drawer-tab-btn" data-tab="uc">Unfolded Circle</button>
            </div>

            <div class="drawer-content" id="integrations-drawer-content">
                <!-- Tab pane content rendered dynamically -->
            </div>
        `;

        document.body.appendChild(drawer);
        this.container = drawer;

        this.setupTabListeners();
        this.registerWithOverlayManager();
    }

    /**
     * Set up tab switching listeners
     */
    setupTabListeners() {
        this.container.querySelector(".drawer-close").addEventListener("click", () => this.close());

        this.container.querySelectorAll(".drawer-tab-btn").forEach(btn => {
            btn.addEventListener("click", (e) => {
                this.activeTab = e.target.dataset.tab;
                this.container.querySelectorAll(".drawer-tab-btn").forEach(b => b.classList.toggle("active", b === e.target));
                this.render();
            });
        });

        // Escape key close
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && this.isOpen) {
                this.close();
            }
        });
    }

    /**
     * Register with the app's global overlay manager
     */
    registerWithOverlayManager() {
        if (window.overlayManager) {
            window.overlayManager.register("integrations-drawer", {
                open: () => this.open(),
                close: () => this.close(),
                isOpen: () => this.isOpen,
            });
        }
    }

    async open() {
        if (window.overlayManager) {
            window.overlayManager.onOpen("integrations-drawer");
        }
        this.isOpen = true;
        this.container.classList.add("open");
        this.container.setAttribute("aria-hidden", "false");
        this.backdrop.classList.add("open");
        document.body.style.overflow = "hidden";

        await this.fetchDiscoveredButtons();
        this.render();

        if (window.FocusTrap) {
            this.focusTrap = new window.FocusTrap(this.container, () => this.close());
            this.focusTrap.activate();
        }
    }

    close() {
        if (window.overlayManager) {
            window.overlayManager.onClose("integrations-drawer");
        }
        this.isOpen = false;
        this.container.classList.remove("open");
        this.container.setAttribute("aria-hidden", "true");
        this.backdrop.classList.remove("open");
        document.body.style.overflow = "";

        if (this.focusTrap) {
            this.focusTrap.deactivate();
        }
    }

    async fetchDiscoveredButtons() {
        try {
            const res = await fetch("/api/integrations/flic/buttons");
            const data = await res.json();
            if (data && data.success) {
                this.discoveredButtons = data.buttons || [];
            }
        } catch (err) {
            console.error("Failed to fetch discovered Flic buttons:", err);
            this.discoveredButtons = [];
        }
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Render active tab's pane content
     */
    render() {
        if (!this.isOpen) return;
        const contentEl = this.container.querySelector("#integrations-drawer-content");
        if (!contentEl) return;

        if (this.activeTab === 'flic') {
            this.renderFlicTab(contentEl);
        } else if (this.activeTab === 'ha') {
            this.renderHaTab(contentEl);
        } else if (this.activeTab === 'uc') {
            this.renderUcTab(contentEl);
        }

        this.attachGlobalCopyListeners();
    }

    /**
     * Set up global copy click listeners for elements with class .btn-copy-action
     */
    attachGlobalCopyListeners() {
        this.container.querySelectorAll(".btn-copy-action").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const button = e.currentTarget;
                const targetId = button.dataset.target;
                const el = this.container.querySelector(`#${targetId}`);
                if (el) {
                    navigator.clipboard.writeText(el.innerText || el.textContent);
                    const originalText = button.textContent;
                    button.textContent = "Copied!";
                    button.classList.add("btn-success");
                    setTimeout(() => {
                        button.textContent = originalText;
                        button.classList.remove("btn-success");
                    }, 2000);
                }
            });
        });
    }

    // ==========================================
    // FLIC INTEGRATION TAB RENDER
    // ==========================================
    renderFlicTab(container) {
        container.innerHTML = `
            <div class="settings-section">
                <h4>Option A: Flic Mobile App (Internet Request)</h4>
                <p class="settings-hint">Configure simple, direct HTTP requests via the Flic App on your phone.</p>
                <ol class="onboarding-steps">
                    <li>Launch the <strong>Flic App</strong> on your mobile device.</li>
                    <li>Add or select your Flic button (Original, Duo, or Twist).</li>
                    <li>Tap the action you want to configure (e.g. Single Click, Rotate).</li>
                    <li>Choose <strong>Internet Request</strong> from the Tools menu.</li>
                    <li>Use the request builder below to generate the parameters, then copy and paste them into the Flic app.</li>
                </ol>
                
                <div class="form-row" style="margin-top: var(--space-4);">
                    <label for="flic-button-type">Button Type</label>
                    <select id="flic-button-type" class="select">
                        <option value="button" ${this.flicConfig.buttonType === 'button' ? 'selected' : ''}>Flic Button (Original / Flic 2)</option>
                        <option value="twist" ${this.flicConfig.buttonType === 'twist' ? 'selected' : ''}>Flic Twist</option>
                        <option value="duo" ${this.flicConfig.buttonType === 'duo' ? 'selected' : ''}>Flic Duo</option>
                    </select>
                </div>

                <div class="form-row">
                    <label for="flic-btn-select">Button Link / Select</label>
                    <select id="flic-btn-select" class="select">
                        <!-- Loaded dynamically via updateButtonSelectOptions() -->
                    </select>
                </div>

                <div class="form-row hidden" id="flic-custom-identifier-row">
                    <label for="flic-btn-identifier">Custom Button Identifier</label>
                    <input type="text" id="flic-btn-identifier" class="input" 
                           placeholder="e.g. Living Room or 90:88:a9:5b:10:62" 
                           value="${this.flicConfig.buttonIdentifier || ''}" />
                </div>
                <p class="settings-hint" style="margin-top: 4px; margin-bottom: 0; font-size: var(--font-size-xs);">
                    Filter by a specific button. Choose "Trigger on All Buttons", select a discovered button, or specify a custom name/MAC.
                </p>

                <div class="form-row">
                    <label for="flic-target-type">Action Target</label>
                    <select id="flic-target-type" class="select">
                        <option value="preset" ${this.flicConfig.targetType === 'preset' ? 'selected' : ''}>Recall Hardware Preset</option>
                        <option value="profile" ${this.flicConfig.targetType === 'profile' ? 'selected' : ''}>Recall Custom Profile</option>
                        <option value="switch_all" ${this.flicConfig.targetType === 'switch_all' ? 'selected' : ''}>Switch All Outputs to Input</option>
                        <option value="switch_output" ${this.flicConfig.targetType === 'switch_output' ? 'selected' : ''}>Switch Output to Input</option>
                        <option value="cycle_input" ${this.flicConfig.targetType === 'cycle_input' ? 'selected' : ''}>Cycle Inputs (Next/Previous)</option>
                        <option value="volume_control" ${this.flicConfig.targetType === 'volume_control' ? 'selected' : ''}>Volume Control (CEC)</option>
                        <option value="power" ${this.flicConfig.targetType === 'power' ? 'selected' : ''}>Matrix Power</option>
                        <option value="cec" ${this.flicConfig.targetType === 'cec' ? 'selected' : ''}>Send Direct CEC Command</option>
                    </select>
                </div>

                <div id="flic-dynamic-inputs">
                    <!-- Injected based on selected target type -->
                </div>

                <div class="form-row">
                    <label for="flic-gesture">Button Gesture</label>
                    <select id="flic-gesture" class="select">
                        <!-- Loaded dynamically via updateGestureOptions() -->
                    </select>
                </div>

                <div class="builder-output-box">
                    <div class="output-row">
                        <span class="output-label">HTTP Method</span>
                        <div class="output-value-container">
                            <code class="output-code" id="flic-out-method">POST</code>
                            <button class="btn btn-xs btn-secondary btn-copy-action" data-target="flic-out-method">Copy</button>
                        </div>
                    </div>
                    <div class="output-row">
                        <span class="output-label">Request URL</span>
                        <div class="output-value-container">
                            <code class="output-code" id="flic-out-url">http://192.168.0.100:8080/api/preset/1</code>
                            <button class="btn btn-xs btn-secondary btn-copy-action" data-target="flic-out-url">Copy</button>
                        </div>
                    </div>
                    <div class="output-row" id="flic-out-body-row">
                        <span class="output-label">JSON Body</span>
                        <div class="output-value-container">
                            <code class="output-code" id="flic-out-body">{"input": 1}</code>
                            <button class="btn btn-xs btn-secondary btn-copy-action" data-target="flic-out-body">Copy</button>
                        </div>
                    </div>
                    <div class="output-row" id="flic-out-content-type-row">
                        <span class="output-label">Content-Type</span>
                        <div class="output-value-container">
                            <code class="output-code">application/json</code>
                        </div>
                    </div>
                </div>
            </div>

            <div class="settings-section">
                <div class="section-title-row">
                    <h4>Option B: Flic Hub Studio (JS SDK Module)</h4>
                    <button class="btn btn-xs btn-primary btn-copy-action" data-target="flic-sdk-code-block">Copy Script</button>
                </div>
                <p class="settings-hint">Run local, ultra-low latency JavaScript code directly on your Flic Hub.</p>
                <ol class="onboarding-steps">
                    <li>In the Flic mobile app, select your Hub, go to settings, and toggle <strong>Enable SDK Access</strong> ON.</li>
                    <li>Ensure your computer is on the same local network as your Hub.</li>
                    <li>Go to the online IDE at <a href="https://hubsdk.flic.io/" target="_blank">hubsdk.flic.io</a> and connect to your Hub's IP address.</li>
                    <li>Create a new package or open your module's <code>main.js</code>.</li>
                    <li>Paste the copied script below and click <strong>Save & Run</strong>.</li>
                </ol>
                <div class="code-container">
                    <pre><code id="flic-sdk-code-block" class="javascript-code"></code></pre>
                </div>
            </div>
        `;

        this.updateDynamicInputs();
        this.updateGestureOptions();
        this.updateButtonSelectOptions();
        this.attachFlicBuilderListeners();
    }

    /**
     * Attach event handlers inside Flic Builder section
     */
    attachFlicBuilderListeners() {
        const buttonTypeSelect = this.container.querySelector("#flic-button-type");
        const targetTypeSelect = this.container.querySelector("#flic-target-type");
        const gestureSelect = this.container.querySelector("#flic-gesture");

        buttonTypeSelect?.addEventListener("change", (e) => {
            this.flicConfig.buttonType = e.target.value;
            
            // Set sensible default gesture when button type changes
            if (this.flicConfig.buttonType === 'duo') {
                this.flicConfig.gesture = 'left_single';
            } else if (this.flicConfig.buttonType === 'twist' && (this.flicConfig.targetType === 'cycle_input' || this.flicConfig.targetType === 'volume_control')) {
                this.flicConfig.gesture = 'rotate_cw';
            } else {
                this.flicConfig.gesture = 'single';
            }

            this.updateGestureOptions();
            this.updateFlicOutput();
        });

        targetTypeSelect?.addEventListener("change", (e) => {
            this.flicConfig.targetType = e.target.value;
            
            // Set sensible default gestures
            if (this.flicConfig.targetType === 'cycle_input' || this.flicConfig.targetType === 'volume_control') {
                if (this.flicConfig.buttonType === 'twist') {
                    this.flicConfig.gesture = 'rotate_cw';
                } else if (this.flicConfig.buttonType === 'duo') {
                    this.flicConfig.gesture = 'left_single';
                } else {
                    this.flicConfig.gesture = 'single';
                }
            } else if (this.flicConfig.gesture.startsWith('rotate') && this.flicConfig.buttonType !== 'twist') {
                this.flicConfig.gesture = 'single';
            }

            this.updateDynamicInputs();
            this.updateGestureOptions();
            this.updateFlicOutput();
        });

        const btnSelect = this.container.querySelector("#flic-btn-select");
        const btnIdentifierInput = this.container.querySelector("#flic-btn-identifier");
        const customRow = this.container.querySelector("#flic-custom-identifier-row");

        btnSelect?.addEventListener("change", (e) => {
            const val = e.target.value;
            if (val === 'custom') {
                customRow?.classList.remove("hidden");
                if (btnIdentifierInput) {
                    this.flicConfig.buttonIdentifier = btnIdentifierInput.value;
                }
            } else {
                customRow?.classList.add("hidden");
                this.flicConfig.buttonIdentifier = val;
            }
            this.updateFlicOutput();
        });

        btnIdentifierInput?.addEventListener("input", (e) => {
            this.flicConfig.buttonIdentifier = e.target.value;
            this.updateFlicOutput();
        });

        gestureSelect?.addEventListener("change", (e) => {
            this.flicConfig.gesture = e.target.value;
            this.updateFlicOutput();
        });
    }

    /**
     * Dynamically populate button gestures based on selected button type
     */
    updateGestureOptions() {
        const gestureSelect = this.container.querySelector("#flic-gesture");
        if (!gestureSelect) return;

        const buttonType = this.flicConfig.buttonType || 'button';
        let optionsHtml = '';

        if (buttonType === 'button') {
            optionsHtml = `
                <option value="single" ${this.flicConfig.gesture === 'single' ? 'selected' : ''}>Single Click</option>
                <option value="double" ${this.flicConfig.gesture === 'double' ? 'selected' : ''}>Double Click</option>
                <option value="hold" ${this.flicConfig.gesture === 'hold' ? 'selected' : ''}>Hold</option>
            `;
        } else if (buttonType === 'twist') {
            optionsHtml = `
                <option value="single" ${this.flicConfig.gesture === 'single' ? 'selected' : ''}>Single Click / Press</option>
                <option value="double" ${this.flicConfig.gesture === 'double' ? 'selected' : ''}>Double Click</option>
                <option value="hold" ${this.flicConfig.gesture === 'hold' ? 'selected' : ''}>Hold</option>
                <option value="rotate_cw" ${this.flicConfig.gesture === 'rotate_cw' ? 'selected' : ''}>Rotate Clockwise (Twist)</option>
                <option value="rotate_ccw" ${this.flicConfig.gesture === 'rotate_ccw' ? 'selected' : ''}>Rotate Counter-Clockwise (Twist)</option>
            `;
        } else if (buttonType === 'duo') {
            optionsHtml = `
                <option value="left_single" ${this.flicConfig.gesture === 'left_single' ? 'selected' : ''}>Left Button - Single Click</option>
                <option value="left_double" ${this.flicConfig.gesture === 'left_double' ? 'selected' : ''}>Left Button - Double Click</option>
                <option value="left_hold" ${this.flicConfig.gesture === 'left_hold' ? 'selected' : ''}>Left Button - Hold</option>
                <option value="right_single" ${this.flicConfig.gesture === 'right_single' ? 'selected' : ''}>Right Button - Single Click</option>
                <option value="right_double" ${this.flicConfig.gesture === 'right_double' ? 'selected' : ''}>Right Button - Double Click</option>
                <option value="right_hold" ${this.flicConfig.gesture === 'right_hold' ? 'selected' : ''}>Right Button - Hold</option>
            `;
        }

        gestureSelect.innerHTML = optionsHtml;
    }

    /**
     * Dynamically populate button select dropdown options
     */
    updateButtonSelectOptions() {
        const btnSelect = this.container.querySelector("#flic-btn-select");
        if (!btnSelect) return;

        const currentId = this.flicConfig.buttonIdentifier || '';
        let optionsHtml = `<option value="" ${currentId === '' ? 'selected' : ''}>Trigger on All Buttons</option>`;
        
        let isCustom = currentId !== '';
        
        if (this.discoveredButtons && this.discoveredButtons.length > 0) {
            this.discoveredButtons.forEach(btn => {
                const isSelected = (currentId === btn.bdaddr || currentId === btn.name);
                if (isSelected) isCustom = false;
                optionsHtml += `<option value="${btn.bdaddr}" ${isSelected ? 'selected' : ''}>${btn.name} (${btn.bdaddr})</option>`;
            });
        }
        
        optionsHtml += `<option value="custom" ${isCustom ? 'selected' : ''}>Custom Identifier...</option>`;
        btnSelect.innerHTML = optionsHtml;

        // Toggle custom identifier input row visibility
        const customRow = this.container.querySelector("#flic-custom-identifier-row");
        if (customRow) {
            if (isCustom) {
                customRow.classList.remove("hidden");
            } else {
                customRow.classList.add("hidden");
            }
        }
    }

    /**
     * Inject appropriate input fields based on Flic Action Target selected
     */
    updateDynamicInputs() {
        const div = this.container.querySelector("#flic-dynamic-inputs");
        if (!div) return;

        let html = "";
        const target = this.flicConfig.targetType;

        if (target === 'preset') {
            html = `
                <div class="form-row">
                    <label for="flic-preset-num">Preset Number</label>
                    <select id="flic-preset-num" class="select select-sm">
                        ${[1,2,3,4,5,6,7,8].map(n => `<option value="${n}" ${this.flicConfig.presetNum === n ? 'selected' : ''}>Preset ${n} (${state.presets[n]?.name || 'Unnamed'})</option>`).join('')}
                    </select>
                </div>
            `;
        } else if (target === 'profile') {
            const profiles = state.profiles || [];
            if (profiles.length === 0) {
                html = `<div class="form-row"><p class="text-warning">No Profiles created yet. Create a profile in the Profiles tab first.</p></div>`;
            } else {
                html = `
                    <div class="form-row">
                        <label for="flic-profile-id">Select Profile</label>
                        <select id="flic-profile-id" class="select select-sm">
                            ${profiles.map(p => `<option value="${p.id}" ${this.flicConfig.profileId === p.id ? 'selected' : ''}>${p.icon || '🎬'} ${p.name}</option>`).join('')}
                        </select>
                    </div>
                `;
            }
        } else if (target === 'switch_all') {
            html = `
                <div class="form-row">
                    <label for="flic-input-num">Select Input Source</label>
                    <select id="flic-input-num" class="select select-sm">
                        ${[1,2,3,4,5,6,7,8].map(n => `<option value="${n}" ${this.flicConfig.inputNum === n ? 'selected' : ''}>Input ${n} (${state.getInputName(n)})</option>`).join('')}
                    </select>
                </div>
            `;
        } else if (target === 'switch_output') {
            html = `
                <div class="form-row">
                    <label for="flic-output-num">Select Output Display</label>
                    <select id="flic-output-num" class="select select-sm">
                        ${[1,2,3,4,5,6,7,8].map(n => `<option value="${n}" ${this.flicConfig.outputNum === n ? 'selected' : ''}>Output ${n} (${state.getOutputName(n)})</option>`).join('')}
                    </select>
                </div>
                <div class="form-row">
                    <label for="flic-input-num">Route Source</label>
                    <select id="flic-input-num" class="select select-sm">
                        ${[1,2,3,4,5,6,7,8].map(n => `<option value="${n}" ${this.flicConfig.inputNum === n ? 'selected' : ''}>Input ${n} (${state.getInputName(n)})</option>`).join('')}
                    </select>
                </div>
            `;
        } else if (target === 'cycle_input') {
            html = `
                <div class="form-row">
                    <label for="flic-output-num">Target Output</label>
                    <select id="flic-output-num" class="select select-sm">
                        ${[1,2,3,4,5,6,7,8].map(n => `<option value="${n}" ${this.flicConfig.outputNum === n ? 'selected' : ''}>Output ${n} (${state.getOutputName(n)})</option>`).join('')}
                    </select>
                </div>
                <div class="form-row">
                    <label for="flic-cycle-dir">Direction</label>
                    <select id="flic-cycle-dir" class="select select-sm">
                        <option value="next" ${this.flicConfig.cycleDir === 'next' ? 'selected' : ''}>Next Input</option>
                        <option value="previous" ${this.flicConfig.cycleDir === 'previous' ? 'selected' : ''}>Previous Input</option>
                    </select>
                </div>
            `;
        } else if (target === 'volume_control') {
            html = `
                <div class="form-row">
                    <label for="flic-output-num">Target Output (CEC Display)</label>
                    <select id="flic-output-num" class="select select-sm">
                        ${[1,2,3,4,5,6,7,8].map(n => `<option value="${n}" ${this.flicConfig.outputNum === n ? 'selected' : ''}>Output ${n} (${state.getOutputName(n)})</option>`).join('')}
                    </select>
                </div>
                <div class="form-row">
                    <label for="flic-vol-dir">Action</label>
                    <select id="flic-vol-dir" class="select select-sm">
                        <option value="volume_up" ${this.flicConfig.volDir === 'volume_up' ? 'selected' : ''}>Volume Up</option>
                        <option value="volume_down" ${this.flicConfig.volDir === 'volume_down' ? 'selected' : ''}>Volume Down</option>
                        <option value="mute" ${this.flicConfig.volDir === 'mute' ? 'selected' : ''}>Mute Toggle</option>
                    </select>
                </div>
            `;
        } else if (target === 'power') {
            html = `
                <div class="form-row">
                    <label for="flic-power-cmd">Command</label>
                    <select id="flic-power-cmd" class="select select-sm">
                        <option value="on" ${this.flicConfig.powerCmd === 'on' ? 'selected' : ''}>Power On Matrix</option>
                        <option value="off" ${this.flicConfig.powerCmd === 'off' ? 'selected' : ''}>Power Off Matrix</option>
                    </select>
                </div>
            `;
        } else if (target === 'cec') {
            html = `
                <div class="form-row">
                    <label for="flic-cec-target-type">Port Type</label>
                    <select id="flic-cec-target-type" class="select select-sm">
                        <option value="input" ${this.flicConfig.cecTargetType === 'input' ? 'selected' : ''}>Source Device (Input)</option>
                        <option value="output" ${this.flicConfig.cecTargetType === 'output' ? 'selected' : ''}>Display Device (Output)</option>
                    </select>
                </div>
                <div id="flic-cec-port-row" class="form-row">
                    <!-- Loaded below dynamically -->
                </div>
                <div class="form-row">
                    <label for="flic-cec-cmd">CEC Command</label>
                    <select id="flic-cec-cmd" class="select select-sm">
                        <option value="power_on" ${this.flicConfig.cecCmd === 'power_on' ? 'selected' : ''}>Power On</option>
                        <option value="power_off" ${this.flicConfig.cecCmd === 'power_off' ? 'selected' : ''}>Power Off / Standby</option>
                        <option value="play" ${this.flicConfig.cecCmd === 'play' ? 'selected' : ''}>Play</option>
                        <option value="pause" ${this.flicConfig.cecCmd === 'pause' ? 'selected' : ''}>Pause</option>
                        <option value="mute" ${this.flicConfig.cecCmd === 'mute' ? 'selected' : ''}>Mute Toggle</option>
                        <option value="volume_up" ${this.flicConfig.cecCmd === 'volume_up' ? 'selected' : ''}>Volume Up</option>
                        <option value="volume_down" ${this.flicConfig.cecCmd === 'volume_down' ? 'selected' : ''}>Volume Down</option>
                    </select>
                </div>
            `;
        }

        div.innerHTML = html;

        // Populate first Profile if available
        if (target === 'profile' && state.profiles?.length > 0 && !this.flicConfig.profileId) {
            this.flicConfig.profileId = state.profiles[0].id;
        }

        this.updateCecPortDropdown();
        this.attachDynamicInputListeners();
        this.updateFlicOutput();
    }

    updateCecPortDropdown() {
        const row = this.container.querySelector("#flic-cec-port-row");
        if (!row) return;

        const isInput = this.flicConfig.cecTargetType === 'input';
        row.innerHTML = `
            <label for="flic-cec-port">Port Number</label>
            <select id="flic-cec-port" class="select select-sm">
                ${[1,2,3,4,5,6,7,8].map(n => `
                    <option value="${n}" ${this.flicConfig.cecTargetPort === n ? 'selected' : ''}>
                        Port ${n} (${isInput ? state.getInputName(n) : state.getOutputName(n)})
                    </option>
                `).join('')}
            </select>
        `;

        row.querySelector("select")?.addEventListener("change", (e) => {
            this.flicConfig.cecTargetPort = Number(e.target.value);
            this.updateFlicOutput();
        });
    }

    /**
     * Event handlers for dynamically injected inputs
     */
    attachDynamicInputListeners() {
        this.container.querySelector("#flic-preset-num")?.addEventListener("change", (e) => {
            this.flicConfig.presetNum = Number(e.target.value);
            this.updateFlicOutput();
        });

        this.container.querySelector("#flic-profile-id")?.addEventListener("change", (e) => {
            this.flicConfig.profileId = e.target.value;
            this.updateFlicOutput();
        });

        this.container.querySelector("#flic-input-num")?.addEventListener("change", (e) => {
            this.flicConfig.inputNum = Number(e.target.value);
            this.updateFlicOutput();
        });

        this.container.querySelector("#flic-output-num")?.addEventListener("change", (e) => {
            this.flicConfig.outputNum = Number(e.target.value);
            this.updateFlicOutput();
        });

        this.container.querySelector("#flic-cycle-dir")?.addEventListener("change", (e) => {
            this.flicConfig.cycleDir = e.target.value;
            this.updateFlicOutput();
        });

        this.container.querySelector("#flic-vol-dir")?.addEventListener("change", (e) => {
            this.flicConfig.volDir = e.target.value;
            this.updateFlicOutput();
        });

        this.container.querySelector("#flic-power-cmd")?.addEventListener("change", (e) => {
            this.flicConfig.powerCmd = e.target.value;
            this.updateFlicOutput();
        });

        this.container.querySelector("#flic-cec-target-type")?.addEventListener("change", (e) => {
            this.flicConfig.cecTargetType = e.target.value;
            this.updateCecPortDropdown();
            this.updateFlicOutput();
        });

        this.container.querySelector("#flic-cec-cmd")?.addEventListener("change", (e) => {
            this.flicConfig.cecCmd = e.target.value;
            this.updateFlicOutput();
        });
    }

    /**
     * Compute and display HTTP values and Hub SDK JavaScript
     */
    updateFlicOutput() {
        const origin = window.location.origin;
        let urlPath = "";
        let bodyObj = null;
        let method = "POST";

        const config = this.flicConfig;

        switch (config.targetType) {
            case 'preset':
                urlPath = `/api/preset/${config.presetNum}`;
                break;
            case 'profile':
                urlPath = `/api/profile/${config.profileId}/recall`;
                break;
            case 'switch_all':
                urlPath = `/api/input/${config.inputNum}`;
                break;
            case 'switch_output':
                urlPath = `/api/output/${config.outputNum}/source`;
                bodyObj = { input: config.inputNum };
                break;
            case 'cycle_input':
                urlPath = `/api/input/${config.cycleDir}?output=${config.outputNum}`;
                break;
            case 'volume_control':
                urlPath = `/api/cec/output/${config.outputNum}/${config.volDir}`;
                break;
            case 'power':
                urlPath = `/api/power/${config.powerCmd}`;
                break;
            case 'cec':
                urlPath = `/api/cec/${config.cecTargetType}/${config.cecTargetPort}/${config.cecCmd}`;
                break;
        }

        const methodEl = this.container.querySelector("#flic-out-method");
        const urlEl = this.container.querySelector("#flic-out-url");
        const bodyEl = this.container.querySelector("#flic-out-body");
        const bodyRow = this.container.querySelector("#flic-out-body-row");
        const contentTypeRow = this.container.querySelector("#flic-out-content-type-row");

        if (methodEl) methodEl.textContent = method;
        if (urlEl) urlEl.textContent = `${origin}${urlPath}`;

        if (bodyObj) {
            if (bodyEl) bodyEl.textContent = JSON.stringify(bodyObj);
            if (bodyRow) bodyRow.classList.remove("hidden");
            if (contentTypeRow) contentTypeRow.classList.remove("hidden");
        } else {
            if (bodyRow) bodyRow.classList.add("hidden");
            if (contentTypeRow) contentTypeRow.classList.add("hidden");
        }

        // Update JavaScript snippet
        this.updateFlicSdkSnippet(origin, urlPath, bodyObj);
    }

    /**
     * Render copy-pasteable Hub SDK snippet
     */
    updateFlicSdkSnippet(origin, path, bodyObj) {
        const codeBlock = this.container.querySelector("#flic-sdk-code-block");
        if (!codeBlock) return;

        const gesture = this.flicConfig.gesture;
        let eventName = 'buttonSingleOrDoubleClickOrHold';
        let triggerCondition = '';

        if (gesture === 'left_single') {
            triggerCondition = 'obj.buttonNumber === 0 && obj.isSingleClick';
        } else if (gesture === 'left_double') {
            triggerCondition = 'obj.buttonNumber === 0 && obj.isDoubleClick';
        } else if (gesture === 'left_hold') {
            triggerCondition = 'obj.buttonNumber === 0 && obj.isHold';
        } else if (gesture === 'right_single') {
            triggerCondition = 'obj.buttonNumber === 1 && obj.isSingleClick';
        } else if (gesture === 'right_double') {
            triggerCondition = 'obj.buttonNumber === 1 && obj.isDoubleClick';
        } else if (gesture === 'right_hold') {
            triggerCondition = 'obj.buttonNumber === 1 && obj.isHold';
        } else {
            triggerCondition = 
                gesture === 'single' ? 'obj.isSingleClick' :
                gesture === 'double' ? 'obj.isDoubleClick' :
                gesture === 'hold' ? 'obj.isHold' : 
                gesture === 'rotate_cw' ? 'obj.direction > 0' : 'obj.direction < 0';

            eventName = gesture.startsWith('rotate') ? 'buttonRotate' : 'buttonSingleOrDoubleClickOrHold';
        }
        const method = 'POST';

        let actionCode = `        http.makeRequest({
            url: API_BASE + "${path}",
            method: "${method}"${bodyObj ? `,\n            headers: {"Content-Type": "application/json"},\n            content: JSON.stringify(${JSON.stringify(bodyObj)})` : ''}
        }, function(err, res) {
            console.log(err ? "Request failed" : "Matrix updated successfully!");
        });`;

        const modelName = state.info.model || 'HDMI Matrix';
        const identifier = this.flicConfig.buttonIdentifier ? this.flicConfig.buttonIdentifier.trim() : '';
        let handlerBody = '';

        if (identifier) {
            handlerBody = `    var button = buttonManager.getButton(obj.bdaddr);
    if (button && (button.name === "${identifier}" || obj.bdaddr === "${identifier}")) {
        if (${triggerCondition}) {
            console.log("Flic Button trigger detected - updating ${modelName}");
${actionCode}
        }
    }`;
        } else {
            handlerBody = `    if (${triggerCondition}) {
        console.log("Flic Button trigger detected - updating ${modelName}");
${actionCode}
    }`;
        }

        let fullScript = `// ${modelName} Hub - Flic Hub SDK Integration Script
// Paste this in the Flic Hub IDE (https://hubsdk.flic.io/)

var buttonManager = require("buttons");
var http = require("http");

var API_BASE = "${origin}";

// Automatically register all paired buttons with the ${modelName} Hub server on startup
try {
    var buttons = buttonManager.getButtons().map(function(btn) {
        return { name: btn.name, bdaddr: btn.bdaddr, serial: btn.serialNumber || "" };
    });
    http.makeRequest({
        url: API_BASE + "/api/integrations/flic/register",
        method: "POST",
        headers: {"Content-Type": "application/json"},
        content: JSON.stringify({buttons: buttons})
    }, function(err, res) {
        console.log(err ? "Failed to register buttons with ${modelName} Hub" : "Buttons registered successfully!");
    });
} catch (e) {
    console.log("Startup registration failed: " + e);
}

buttonManager.on("${eventName}", function(obj) {
${handlerBody}
});

console.log("${modelName} Control script loaded successfully!");
`;

        codeBlock.textContent = fullScript;
    }

    // ==========================================
    // HOME ASSISTANT TAB RENDER
    // ==========================================
    renderHaTab(container) {
        const modelName = state.info.model || 'HDMI Matrix';
        const driverName = state.info.driverName || 'HDMI Matrix';
        container.innerHTML = `
            <div class="settings-section">
                <h4>Option A: HACS Custom Component (Full UI Integration)</h4>
                <p class="settings-hint">The most feature-rich option. Creates native entities for routing, switches, and buttons.</p>
                <ol class="onboarding-steps">
                    <li>Copy or link the folder <code>custom_components/hdmi_matrix</code> into your Home Assistant <code>/config/custom_components/</code> directory.</li>
                    <li>Restart Home Assistant.</li>
                    <li>Go to <strong>Settings -> Devices & Services -> Add Integration</strong>.</li>
                    <li>Search for <strong>"${Helpers.escapeHtml(driverName)}"</strong> (representing your ${Helpers.escapeHtml(modelName)}).</li>
                    <li>Enter this Hub's IP/URL when prompted: <code id="ha-hacs-host"></code></li>
                </ol>
            </div>

            <div class="settings-section">
                <div class="section-title-row">
                    <h4>Option B: REST Commands (YAML Configuration)</h4>
                    <button class="btn btn-xs btn-primary btn-copy-action" data-target="ha-yaml-output">Copy YAML</button>
                </div>
                <p class="settings-hint">Add direct HTTP request buttons to your Lovelace dashboard via <code>configuration.yaml</code>.</p>
                
                <div class="yaml-config-options">
                    <label class="checkbox-container">
                        <input type="checkbox" id="ha-opt-presets" ${this.haConfig.includePresets ? 'checked' : ''} />
                        Include Presets 1-8
                    </label>
                    <label class="checkbox-container">
                        <input type="checkbox" id="ha-opt-power" ${this.haConfig.includePower ? 'checked' : ''} />
                        Include Power ON/OFF
                    </label>
                    <label class="checkbox-container">
                        <input type="checkbox" id="ha-opt-cycling" ${this.haConfig.includeInputCycling ? 'checked' : ''} />
                        Include Input Cycling (Next/Prev)
                    </label>
                    <label class="checkbox-container">
                        <input type="checkbox" id="ha-opt-routing" ${this.haConfig.includeRouting ? 'checked' : ''} />
                        Include Output Routing Service
                    </label>
                </div>

                <div class="code-container">
                    <pre><code id="ha-yaml-output" class="yaml-code"></code></pre>
                </div>
            </div>
        `;

        const hostEl = this.container.querySelector("#ha-hacs-host");
        if (hostEl) hostEl.textContent = window.location.origin;

        this.updateHaYaml();
        this.attachHaListeners();
    }

    attachHaListeners() {
        const checkPresets = this.container.querySelector("#ha-opt-presets");
        const checkPower = this.container.querySelector("#ha-opt-power");
        const checkCycling = this.container.querySelector("#ha-opt-cycling");
        const checkRouting = this.container.querySelector("#ha-opt-routing");

        const updateHa = () => {
            this.haConfig.includePresets = checkPresets?.checked || false;
            this.haConfig.includePower = checkPower?.checked || false;
            this.haConfig.includeInputCycling = checkCycling?.checked || false;
            this.haConfig.includeRouting = checkRouting?.checked || false;
            this.updateHaYaml();
        };

        checkPresets?.addEventListener("change", updateHa);
        checkPower?.addEventListener("change", updateHa);
        checkCycling?.addEventListener("change", updateHa);
        checkRouting?.addEventListener("change", updateHa);
    }

    updateHaYaml() {
        const yamlEl = this.container.querySelector("#ha-yaml-output");
        if (!yamlEl) return;

        const origin = window.location.origin;
        const modelSlug = (state.info.model || 'hdmi_matrix')
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '_')
            .replace(/(^_+|_+$)/g, '');

        let yaml = `# Copy and paste this into your configuration.yaml\nrest_command:\n`;

        if (this.haConfig.includePresets) {
            yaml += `  # Recall Matrix Presets (1-8)\n`;
            for (let i = 1; i <= 8; i++) {
                yaml += `  ${modelSlug}_preset_${i}:\n`;
                yaml += `    url: "${origin}/api/preset/${i}"\n`;
                yaml += `    method: POST\n`;
            }
            yaml += `\n`;
        }

        if (this.haConfig.includePower) {
            yaml += `  # Power control\n`;
            yaml += `  ${modelSlug}_power_on:\n`;
            yaml += `    url: "${origin}/api/power/on"\n`;
            yaml += `    method: POST\n`;
            yaml += `  ${modelSlug}_power_off:\n`;
            yaml += `    url: "${origin}/api/power/off"\n`;
            yaml += `    method: POST\n`;
            yaml += `\n`;
        }

        if (this.haConfig.includeInputCycling) {
            yaml += `  # Input cycling (Next/Previous)\n`;
            yaml += `  ${modelSlug}_input_next:\n`;
            yaml += `    url: "${origin}/api/input/next?output={{ output }}"\n`;
            yaml += `    method: POST\n`;
            yaml += `  ${modelSlug}_input_previous:\n`;
            yaml += `    url: "${origin}/api/input/previous?output={{ output }}"\n`;
            yaml += `    method: POST\n`;
            yaml += `\n`;
        }

        if (this.haConfig.includeRouting) {
            yaml += `  # Route Output to Input dynamically\n`;
            yaml += `  ${modelSlug}_set_output_source:\n`;
            yaml += `    url: "${origin}/api/output/{{ output }}/source"\n`;
            yaml += `    method: POST\n`;
            yaml += `    content_type: "application/json"\n`;
            yaml += `    payload: '{"input": {{ input }}}'\n`;
        }

        yamlEl.textContent = yaml;
    }

    // ==========================================
    // UNFOLDED CIRCLE REMOTE 3 TAB RENDER
    // ==========================================
    renderUcTab(container) {
        const origin = window.location.origin;
        // Strip http:// or https:// and port to get the IP address
        const ip = origin.replace(/https?:\/\//, "").split(":")[0];
        const driverPort = 9095; // Default WebSocket server port for driver

        const modelName = state.info.model || 'HDMI Matrix';
        const driverName = state.info.driverName || 'HDMI Matrix';
        const driverId = state.info.driverId || 'orei_hdmi_matrix';

        container.innerHTML = `
            <div class="settings-section">
                <h4>Unfolded Circle Integration Guide</h4>
                <p class="settings-hint">The Matrix Hub has a built-in integration driver that runs in the background to serve entities directly to the Remote 3.</p>
                <ol class="onboarding-steps">
                    <li>Ensure this Hub server is running on the <strong>same network</strong> as your Remote.</li>
                    <li>On the Remote, go to <strong>Settings -> Integrations -> Add Integration</strong>.</li>
                    <li>If discovery is active, the Remote will show <strong>"${Helpers.escapeHtml(driverName)}"</strong> (representing your ${Helpers.escapeHtml(modelName)}) under discovered integrations.</li>
                    <li>If it doesn't appear, choose <strong>Manual Setup</strong> and enter:
                        <ul>
                            <li><strong>IP Address:</strong> <code>${ip}</code></li>
                            <li><strong>Port:</strong> <code>${driverPort}</code></li>
                        </ul>
                    </li>
                    <li>In the Remote's setup wizard, enter the physical HDMI Matrix Switch IP address.</li>
                    <li>Map the resulting entity buttons (presets, CEC commands, or input sources) to your Remote's dashboard screens.</li>
                </ol>
            </div>

            <div class="settings-section">
                <h4>Active Driver Metadata</h4>
                <div class="info-grid">
                    <span class="info-label">Driver Port:</span>
                    <span class="info-value">9095</span>
                    <span class="info-label">mDNS Identifier:</span>
                    <span class="info-value">${Helpers.escapeHtml(driverId)}</span>
                    <span class="info-label">Discovery URL:</span>
                    <span class="info-value">http://${ip}:${driverPort}/</span>
                    <span class="info-label">Status:</span>
                    <span class="info-value text-success">✓ Driver Active</span>
                </div>
            </div>
        `;
    }
}

// Create global instance
window.integrationsDrawer = new IntegrationsDrawer();
