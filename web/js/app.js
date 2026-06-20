/**
 * OREI Matrix Control - Main Application
 * Initializes all components and handles app-level logic
 */

class MatrixApp {
    constructor() {
        this.components = {};
        this.ws = null;
        this.isInitialLoad = true; // Track if this is the first load (page refresh)
    }

    /**
     * Initialize the application
     */
    async init() {
        Logger.info('OREI Matrix Control initializing...');

        // Phase 7: Migrate localStorage favorites/dashboard to server before initial load
        await this.migrateLocalStorageToServer();

        // Initialize components first - renders UI immediately with default/cached state
        this.initComponents();

        // Setup event handlers
        this.setupEventHandlers();

        // Load UI Preferences & side navigation drawer
        if (window.sideNavDrawer) {
            await window.sideNavDrawer.init();
            this.applyUiPreferences(window.sideNavDrawer.preferences);
        }

        // Connect WebSocket for real-time updates
        this.connectWebSocket();

        // Load initial data in background - don't block UI rendering
        // Components will update automatically via state events when data arrives
        this.loadInitialData();

        Logger.info('OREI Matrix Control ready');
    }

    /**
     * Migrate localStorage favorites/dashboard config to server (Phase 7)
     * Runs once on first load after Phase 7 migration flag is set
     */
    async migrateLocalStorageToServer() {
        const migrationKey = 'orei_phase7_migration_done';
        if (localStorage.getItem(migrationKey)) return;

        try {
            // Migrate favorites
            const favRaw = localStorage.getItem('orei_favorites');
            if (favRaw) {
                const favs = JSON.parse(favRaw);
                // POST each preset favorite
                if (Array.isArray(favs.presets)) {
                    for (const presetNum of favs.presets) {
                        await window.api.toggleFavoritePreset(Number(presetNum)).catch(() => {});
                    }
                }
                // POST each scene (profile) favorite
                if (Array.isArray(favs.scenes)) {
                    for (const profileId of favs.scenes) {
                        await window.api.toggleProfileFavorite(profileId).catch(() => {});
                    }
                }
                localStorage.removeItem('orei_favorites');
                console.info('Phase 7: migrated favorites from localStorage to server');
            }

            // Migrate dashboard config (if dashboard_manager stored anything)
            const dashRaw = localStorage.getItem('orei_dashboard_config');
            if (dashRaw) {
                // The 3 legacy aggregate widgets may have been unpinned
                // We just clear localStorage; server already has the default layout
                localStorage.removeItem('orei_dashboard_config');
                console.info('Phase 7: cleared legacy dashboard localStorage config');
            }

            localStorage.setItem(migrationKey, 'true');
        } catch (err) {
            console.warn('Phase 7 migration failed (non-fatal):', err);
        }
    }

    /**
     * Initialize all UI components
     */
    initComponents() {
        // Dashboard Manager (must be early so widgets can register)
        if (window.dashboardManager) {
            window.dashboardManager.init();
        }
        
        // HDMI Status Tray (header button with dropdown)
        this.components.hdmiStatusTray = new HdmiStatusTray();
        this.components.hdmiStatusTray.init();
        
        // Quick Actions Drawer
        this.components.quickActionsDrawer = new QuickActionsDrawer();
        this.components.quickActionsDrawer.init();
        
        // Route All Drawer
        this.components.routeAllDrawer = new RouteAllDrawer();
        this.components.routeAllDrawer.init();
        
        // Matrix grid
        this.components.matrixGrid = new MatrixGrid('matrix-grid');
        this.components.matrixGrid.init();
        
        // Input panel
        this.components.inputPanel = new InputPanel('inputs-list');
        this.components.inputPanel.init();
        
        // Output panel
        this.components.outputPanel = new OutputPanel('outputs-list');
        this.components.outputPanel.init();
        
        // Output settings modal
        window.outputSettingsModal = new OutputSettingsModal();
        
        // Input settings modal
        window.inputSettingsModal = new InputSettingsModal();
        
        // Scenes panel
        this.components.scenesPanel = new ScenesPanel('scenes-list');
        this.components.scenesPanel.init();
        
        // Settings panel
        this.components.settingsPanel = new SettingsPanel();
        this.components.settingsPanel.init();
    }

    /**
     * Setup global event handlers
     */
    setupEventHandlers() {
        // Triple 3-finger tap to enter kiosk mode
        this.setupKioskGesture();

        // Listen for UI Preference changes
        window.addEventListener('uiPreferencesChanged', (e) => {
            this.applyUiPreferences(e.detail);
        });
        
        // Connection status updates
        state.on('wsConnection', (connected) => {
            this.updateConnectionStatus(connected);
        });

        // Horizontal swipe navigation setup
        this.setupSwipeGestures();

        // Recalculate slider translation position on window resize with dynamic slide centering
        window.addEventListener('resize', () => {
            const activeTab = state.ui.activeTab || 'matrix';
            const slider = document.querySelector('.sections-slider');
            const activeSection = document.getElementById(`${activeTab}-section`);
            if (slider && activeSection) {
                slider.style.transition = 'none'; // Prevent animation bounce during resize
                
                let translation = -activeSection.offsetLeft;
                const viewportWidth = slider.parentElement.clientWidth;
                const sectionWidth = activeSection.clientWidth;
                if (viewportWidth > sectionWidth) {
                    translation += (viewportWidth - sectionWidth) / 2;
                }
                slider.style.transform = `translateX(${translation}px)`;
                
                // Force a layout reflow before restoring CSS transition
                slider.offsetHeight;
                slider.style.transition = '';
            }
        });
    }

    /**
     * Setup double 2-finger tap gesture to enter kiosk mode
     * Uses 2 fingers with double tap to avoid conflict with debug panel's single 3-finger tap
     */
    setupKioskGesture() {
        const gesture = {
            tapCount: 0,
            lastTapTime: 0,
            TAP_TIMEOUT: 400,      // Max time between taps (ms)
            REQUIRED_FINGERS: 2,
            REQUIRED_TAPS: 2
        };

        document.addEventListener('touchstart', (e) => {
            // Only trigger on 2-finger touch
            if (e.touches.length !== gesture.REQUIRED_FINGERS) {
                return;
            }

            const now = Date.now();
            
            // Reset if too much time passed since last tap
            if (now - gesture.lastTapTime > gesture.TAP_TIMEOUT) {
                gesture.tapCount = 0;
            }

            gesture.tapCount++;
            gesture.lastTapTime = now;

            if (gesture.tapCount >= gesture.REQUIRED_TAPS) {
                gesture.tapCount = 0;
                toast.info('Entering kiosk mode...');
                setTimeout(() => {
                    window.location.href = '/kiosk';
                }, 300);
            }
        }, { passive: true });
    }

    /**
     * Switch active tab (mobile view)
     */
    switchTab(tab) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            const isActive = btn.dataset.tab === tab;
            btn.classList.toggle('active', isActive);
            btn.setAttribute('aria-selected', isActive ? 'true' : 'false');
        });
        
        // Update sections active state and out-of-focus styling (adjacent cover flow)
        document.querySelectorAll('.section').forEach(section => {
            const isActive = section.id === `${tab}-section`;
            section.classList.toggle('active', isActive);
            section.classList.toggle('out-of-focus', !isActive);
        });

        // Scroll sections slider horizontally with dynamic slide centering on desktop
        const slider = document.querySelector('.sections-slider');
        const activeSection = document.getElementById(`${tab}-section`);
        if (slider && activeSection) {
            let translation = -activeSection.offsetLeft;
            const viewportWidth = slider.parentElement.clientWidth;
            const sectionWidth = activeSection.clientWidth;
            if (viewportWidth > sectionWidth) {
                translation += (viewportWidth - sectionWidth) / 2;
            }
            slider.style.transform = `translateX(${translation}px)`;
        }
        
        state.setActiveTab(tab);
    }

    /**
     * Dynamically build tab buttons and reorder section elements in DOM based on UI preferences
     */
    applyUiPreferences(prefs) {
        this.preferences = prefs;
        
        const mobileContainer = document.querySelector('.mobile-tabs');
        const desktopContainer = document.querySelector('.desktop-tab-container');
        const slider = document.querySelector('.sections-slider');
        
        if (!prefs || !prefs.pinnedTabs || !prefs.tabOrder || !slider) return;

        // 1. Re-order standard section panel elements in DOM to match tabOrder
        prefs.tabOrder.forEach(tabId => {
            const sec = document.getElementById(`${tabId}-section`);
            if (sec) {
                slider.appendChild(sec);
            }
        });

        // Make sure the mobile widget container is always appended at the end
        const mobileWidgetSec = document.getElementById('mobile-widget-content');
        if (mobileWidgetSec) {
            slider.appendChild(mobileWidgetSec);
        }

        // 2. Render top (desktop) and bottom (mobile) tab buttons
        const specs = window.sideNavDrawer ? window.sideNavDrawer.getTabSpecs() : [];
        
        // Sort tab specs according to user's tabOrder
        const sortedSpecs = [...specs].sort((a, b) => {
            let idxA = prefs.tabOrder.indexOf(a.id);
            let idxB = prefs.tabOrder.indexOf(b.id);
            if (idxA === -1) idxA = 99;
            if (idxB === -1) idxB = 99;
            return idxA - idxB;
        });

        const activeTab = state.ui.activeTab || 'matrix';
        
        let mobileHtml = "";
        let desktopHtml = "";

        sortedSpecs.forEach(tab => {
            const isPinned = prefs.pinnedTabs.includes(tab.id);
            
            // Set hidden class in DOM on sections
            const sec = document.getElementById(`${tab.id}-section`);
            if (sec) {
                sec.classList.toggle('hidden', !isPinned);
            }

            if (!isPinned) return;

            const isActive = tab.id === activeTab;
            
            // Hide dashboard tab button dynamically if it is pinned but contains no widgets
            const isDashboardHidden = tab.id === 'dashboard' && window.dashboardManager && !window.dashboardManager.hasPinnedWidgets();
            const hideClass = isDashboardHidden ? 'hidden' : '';

            const btnMarkup = `
                <button class="tab-btn ${isActive ? 'active' : ''} ${hideClass}" data-tab="${tab.id}" role="tab" aria-selected="${isActive ? 'true' : 'false'}">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        ${tab.icon}
                    </svg>
                    <span>${tab.name.split(' ')[0]}</span>
                </button>
            `;

            mobileHtml += btnMarkup;
            desktopHtml += btnMarkup;
        });

        if (mobileContainer) mobileContainer.innerHTML = mobileHtml;
        if (desktopContainer) desktopContainer.innerHTML = desktopHtml;

        // Re-attach click listeners to new tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(tab);
            });
        });

        // Ensure we switch to a pinned tab if the active one was unpinned
        if (!prefs.pinnedTabs.includes(activeTab)) {
            const firstPinned = prefs.pinnedTabs.find(id => {
                if (id === 'dashboard') {
                    return window.dashboardManager && window.dashboardManager.hasPinnedWidgets();
                }
                return true;
            }) || 'matrix';
            this.switchTab(firstPinned);
        } else {
            this.switchTab(activeTab);
        }
    }

    /**
     * Setup touch swipe gesture handlers to navigate tabs
     */
    setupSwipeGestures() {
        const slider = document.querySelector('.sections-slider');
        if (!slider) return;

        let startX = 0;
        let startY = 0;
        let isSwiping = false;

        slider.addEventListener('touchstart', (e) => {
            // Ignore if multi-touch or initiated inside a horizontal scroll container
            if (e.touches.length !== 1 || e.target.closest('.matrix-container, .cec-actions, .presets-panel')) {
                return;
            }
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isSwiping = true;
        }, { passive: true });

        slider.addEventListener('touchend', (e) => {
            if (!isSwiping) return;
            isSwiping = false;

            const diffX = startX - e.changedTouches[0].clientX;
            const diffY = startY - e.changedTouches[0].clientY;

            // Verify swipe horizontal intent and minimum pixel travel (80px)
            if (Math.abs(diffX) > Math.abs(diffY) * 1.8 && Math.abs(diffX) > 80) {
                const tabButtons = Array.from(document.querySelectorAll('.tab-btn:not(.hidden)'));
                const currentActiveIndex = tabButtons.findIndex(btn => btn.classList.contains('active'));
                
                if (currentActiveIndex === -1) return;

                if (diffX > 0 && currentActiveIndex < tabButtons.length - 1) {
                    // Swiped left -> Switch to next tab
                    const nextTab = tabButtons[currentActiveIndex + 1].dataset.tab;
                    this.switchTab(nextTab);
                } else if (diffX < 0 && currentActiveIndex > 0) {
                    // Swiped right -> Switch to previous tab
                    const prevTab = tabButtons[currentActiveIndex - 1].dataset.tab;
                    this.switchTab(prevTab);
                }
            }
        }, { passive: true });
    }

    /**
     * Open modal
     */
    openModal(modal) {
        if (modal) {
            modal.setAttribute('aria-hidden', 'false');
        }
    }

    /**
     * Close modal
     */
    closeModal(modal) {
        if (modal) {
            modal.setAttribute('aria-hidden', 'true');
        }
    }

    /**
     * Connect to WebSocket for real-time updates
     */
    connectWebSocket() {
        this.ws = new MatrixWebSocket({
            onMessage: (data) => this.handleWebSocketMessage(data),
            onStatusChange: (connected) => state.setWsConnected(connected),
            onError: (error) => console.error('WebSocket error:', error)
        });
        
        this.ws.connect();
    }

    /**
     * Handle WebSocket messages
     */
    handleWebSocketMessage(data) {
        Logger.ws('RX', data);
        
        switch (data.type) {
            case 'switch':
                state.setRoute(data.output, data.input);
                // Show toast for optimistic feedback
                if (data.optimistic && window.toast) {
                    const inputName = state.getInputName(data.input);
                    const outputName = state.getOutputName(data.output);
                    window.toast.show(`Routing ${inputName} → ${outputName}`, 'info', 2000);
                }
                break;
            
            case 'switch_all':
                // All outputs switched to single input
                const routing = {};
                for (let o = 1; o <= state.info.outputCount; o++) {
                    routing[o] = data.input;
                }
                state.setRouting(routing);
                // Show toast for optimistic feedback
                if (data.optimistic && window.toast) {
                    const inputName = state.getInputName(data.input);
                    window.toast.show(`Routing ${inputName} → All Outputs`, 'info', 2000);
                }
                break;
            
            case 'signal_change':
                // Input signal status changed
                if (state.inputs[data.input]) {
                    state.inputs[data.input].signalActive = data.active;
                    state.emit('inputs', state.inputs);
                }
                break;
                
            case 'audio_mute':
                state.setOutputMute(data.output, data.muted);
                // Show toast for optimistic feedback
                if (data.optimistic && window.toast) {
                    const outputName = state.getOutputName(data.output);
                    const muteText = data.muted ? 'Muting' : 'Unmuting';
                    window.toast.show(`${muteText} ${outputName}`, 'info', 2000);
                }
                break;
                
            case 'preset_recall':
            case 'scene_recall':
                // Show toast for optimistic feedback
                if (data.optimistic && window.toast) {
                    window.toast.show(`Loading Preset ${data.preset}...`, 'info', 2000);
                }
                // Full refresh needed
                this.refresh();
                break;
                
            case 'status':
                if (data.data) {
                    state.applyStatus(data.data);
                }
                break;
            
            case 'cec_command':
                // Optimistic update for CEC commands (power on/off)
                this.handleCecCommand(data);
                break;
        }
    }
    
    /**
     * Handle optimistic CEC command updates
     */
    handleCecCommand(data) {
        const { type, port, command, name } = data;
        
        if (command === 'power_on' || command === 'power_off') {
            const isOn = command === 'power_on';
            const action = isOn ? 'Powering on' : 'Powering off';
            const targetName = name || `${type === 'output' ? 'Output' : 'Input'} ${port}`;
            
            // Show toast notification
            if (window.toast) {
                window.toast.show(`${action} ${targetName}...`, 'info', 2000);
            }
            
            if (type === 'output' && state.outputs[port]) {
                // Update output power state optimistically
                state.outputs[port].enabled = isOn;
                state.emit('outputs', state.outputs);
            } else if (type === 'input' && state.inputs[port]) {
                // Could track input device power state if needed
                // For now, just trigger a refresh of input panel
                state.emit('inputs', state.inputs);
            }
        }
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            statusEl.classList.toggle('connected', connected);
            statusEl.classList.toggle('disconnected', !connected);
            statusEl.title = connected ? 'Connected' : 'Disconnected';
            
            const textEl = statusEl.querySelector('.status-text');
            if (textEl) {
                textEl.textContent = connected ? 'Online' : 'Offline';
            }
        }
    }

    /**
     * Load initial data from API
     */
    async loadInitialData() {
        state.setLoading(true);
        
        try {
            // First, ensure the matrix is awake (not in standby)
            // This sends a power-on command if the status check fails
            const isAwake = await api.ensureAwake();
            if (!isAwake) {
                console.warn('Matrix may be in standby or unreachable');
                // Continue anyway - the API calls below will provide more info
            }
            
            // Load info and status in parallel
            const [info, status, scenesResult, inputStatus, outputStatus, deviceSettings, shortcutsResult] = await Promise.all([
                api.getInfo().catch(() => null),
                api.getStatus().catch(() => null),
                api.listScenes().catch(() => ({ scenes: [] })),
                api.getInputStatus().catch(() => null),
                api.getOutputStatus().catch(() => null),
                state.loadDeviceSettings().catch(() => false),
                state.loadSystemShortcuts().catch(() => [])
            ]);
            
            if (info) {
                state.applyInfo(info);
            }
            
            if (status) {
                state.applyStatus(status);
            }
            
            if (scenesResult?.scenes) {
                state.setScenes(scenesResult.scenes);
            }
            
            // Apply HDMI status data
            if (inputStatus?.data?.inputs) {
                this.applyInputStatus(inputStatus.data.inputs);
            }
            
            if (outputStatus?.data?.outputs) {
                this.applyOutputStatus(outputStatus.data.outputs);
            }

            // Phase 7: Load server-backed favorites and dashboard
            await Promise.all([
                state.loadAllFavorites().catch(() => {}),
                state.loadDashboardLayout().catch(() => {}),
                state.loadDashboardPresets().catch(() => {})
            ]);

            state.setConnected(true);
            state.ui.dataLoaded = true;
            
            // Only show toast on reconnection, not on initial page load
            if (!this.isInitialLoad) {
                toast.success('Connected to matrix');
            }
            this.isInitialLoad = false;
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
            state.setConnected(false);
            toast.error('Failed to connect to matrix');
        } finally {
            state.setLoading(false);
        }
    }
    
    /**
     * Apply input status data (signal detection)
     */
    applyInputStatus(inputs) {
        if (!Array.isArray(inputs)) {
            console.warn('applyInputStatus: inputs is not an array', inputs);
            return;
        }
        
        Logger.state('inputStatus', inputs);
        
        inputs.forEach(input => {
            const num = input.number;
            if (state.inputs[num]) {
                // Set input name from API
                if (input.name) {
                    state.inputs[num].name = input.name;
                }
                
                // Use the API's signalActive field if available (preferred),
                // otherwise fall back to deriving from inactive
                // NOTE: The matrix's 'inactive' field reports cable/+5V/HPD presence,
                // NOT active video sync. Devices in standby often still provide +5V.
                const hasSignal = input.signalActive !== undefined 
                    ? input.signalActive 
                    : (input.inactive === false);
                state.inputs[num].signalActive = hasSignal;
                
                // Use Telnet-based cable detection if available
                // cableConnected from Telnet is more reliable than HTTP for physical connection
                // null means telnet not available, we can still infer from signal
                if (input.cableConnected !== undefined && input.cableConnected !== null) {
                    state.inputs[num].cableConnected = input.cableConnected;
                } else {
                    // Infer: if signal present, cable must be connected
                    state.inputs[num].cableConnected = hasSignal ? true : null;
                }
                
                state.inputs[num].edidMode = input.edid || 0;
                Logger.log(`Input ${num}: signalActive=${hasSignal}, cableConnected=${state.inputs[num].cableConnected}`);
            }
        });
        state.emit('inputs', state.inputs);
    }
    
    /**
     * Apply output status data (connection detection)
     */
    applyOutputStatus(outputs) {
        if (!Array.isArray(outputs)) return;
        
        outputs.forEach(output => {
            const num = output.number;
            if (state.outputs[num]) {
                // Set output name from API
                if (output.name) {
                    state.outputs[num].name = output.name;
                }
                
                // Use HTTP-based connected (sink detection)
                state.outputs[num].displayConnected = output.connected === true;
                
                // Use Telnet-based cable detection if available (more reliable for physical connection)
                if (output.cableConnected !== undefined && output.cableConnected !== null) {
                    state.outputs[num].cableConnected = output.cableConnected;
                } else {
                    // Fall back to displayConnected
                    state.outputs[num].cableConnected = output.connected === true ? true : null;
                }
                
                state.outputs[num].enabled = output.enabled !== false;
                state.outputs[num].audioMuted = output.muted === true;
                state.outputs[num].arcEnabled = output.arc === true;
                if (output.hdcp !== undefined) state.outputs[num].hdcpMode = output.hdcp;
                if (output.hdr !== undefined) state.outputs[num].hdrMode = output.hdr;
                if (output.scaler !== undefined) state.outputs[num].scalerMode = output.scaler;
            }
        });
        state.emit('outputs', state.outputs);
    }

    /**
     * Refresh all data
     */
    async refresh() {
        toast.info('Refreshing...');
        
        try {
            const [status, scenesResult, inputStatus, outputStatus] = await Promise.all([
                api.getStatus().catch(e => {
                    console.warn('Status refresh failed:', e);
                    return null;
                }),
                api.listScenes().catch(() => ({ scenes: [] })),
                api.getInputStatus().catch(() => null),
                api.getOutputStatus().catch(() => null)
            ]);
            
            if (status) {
                state.applyStatus(status);
            }
            
            state.setScenes(scenesResult?.scenes || []);
            
            // Refresh HDMI status
            if (inputStatus?.data?.inputs) {
                this.applyInputStatus(inputStatus.data.inputs);
            }
            
            if (outputStatus?.data?.outputs) {
                this.applyOutputStatus(outputStatus.data.outputs);
            }
            
            toast.success('Refreshed');
        } catch (error) {
            console.error('Refresh failed:', error);
            toast.error('Refresh failed');
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new MatrixApp();
    window.app.init();
});
