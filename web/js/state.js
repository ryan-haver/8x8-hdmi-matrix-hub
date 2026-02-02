/**
 * OREI Matrix Control - State Management
 * Centralized application state with event-based updates
 */

class AppState {
    constructor() {
        // Connection state
        this.connected = false;
        this.wsConnected = false;
        
        // System info
        this.info = {
            model: '',
            firmwareVersion: '',
            apiVersion: '',
            inputCount: 8,
            outputCount: 8
        };
        
        // Current routing: output -> input
        this.routing = {};
        
        // Input names and status
        this.inputs = {};
        
        // Output states
        this.outputs = {};
        
        // Hardware presets
        this.presets = {};
        
        // Software scenes (legacy)
        this.scenes = [];
        
        // Profiles (enhanced scenes with macros)
        this.profiles = [];
        
        // Currently active scene (after recall) - legacy
        this.activeScene = null;
        
        // Currently active profile (after recall)
        this.activeProfile = null;
        
        // Currently active hardware preset (after recall)
        this.activePreset = null;
        
        // UI state
        this.ui = {
            activeTab: 'matrix',
            selectedOutput: null,
            selectedInput: null,
            sidebarOpen: false,
            loading: false,  // Start with loading=false so UI renders immediately with defaults
            dataLoaded: false  // Track when real data has been fetched
        };
        
        // Event listeners
        this.listeners = new Map();
        
        // Initialize default state
        this.initializeDefaults();
    }

    /**
     * Initialize default values for inputs/outputs
     */
    initializeDefaults() {
        const inputCount = Constants?.MATRIX?.INPUT_COUNT || 8;
        const outputCount = Constants?.MATRIX?.OUTPUT_COUNT || 8;
        
        for (let i = 1; i <= inputCount; i++) {
            this.inputs[i] = {
                name: `Input ${i}`,
                enabled: true,
                signalActive: false,  // true = signal detected (from matrix inactive array)
                cableConnected: null, // true/false/null - null means unknown (inferred: if signal, cable must be connected)
                edidMode: 0,
                icon: 'generic-input'  // Device icon ID (Phase 2)
            };
            
            this.outputs[i] = {
                name: `Output ${i}`,
                input: i,
                audioMuted: false,
                hdrMode: 'auto',
                hdcpMode: 'auto',
                displayConnected: false,  // true = sink detected (HTTP HPD)
                cableConnected: null,     // true/false/null - null means unknown (Telnet-based)
                signalActive: false,      // true = receiving signal (inferred: cable connected AND routed input has signal)
                enabled: true,            // output stream enabled
                arcEnabled: false,
                scalerMode: 1,
                icon: 'generic-output'    // Device icon ID (Phase 2)
            };
            
            this.routing[i] = i;
        }
        
        const presetCount = Constants?.MATRIX?.PRESET_COUNT || 8;
        for (let i = 1; i <= presetCount; i++) {
            this.presets[i] = {
                name: `Preset ${i}`,
                routing: {}
            };
        }
        
        // Quick actions favorites (preset/scene IDs)
        this.favorites = {
            presets: [],
            scenes: []
        };
        
        // CEC Tray state
        this.cecTray = {
            position: 'bottom-right', // 'bottom-right', 'bottom-left', 'top-right', 'panel-right'
            pinned: false,
            targets: {
                navigation: { type: 'auto', port: null },
                playback: { type: 'auto', port: null },
                volume: { type: 'auto', port: null }
            }
        };
        
        // CEC Macros (Phase 1B)
        this.cecMacros = [];
        
        // Profiles (Phase 2)
        this.profiles = [];
        
        // Recently used icons (Phase 2)
        this.recentIcons = [];
        this.loadRecentIcons();
        
        // Load cached state from localStorage (overrides defaults)
        this.loadCachedState();
    }
    
    /**
     * Save current state to localStorage for instant UI loading
     */
    saveCachedState() {
        try {
            const cacheData = {
                routing: this.routing,
                inputs: this.inputs,
                outputs: this.outputs,
                presets: this.presets,
                scenes: this.scenes,
                info: this.info,
                timestamp: Date.now()
            };
            localStorage.setItem('orei_state_cache', JSON.stringify(cacheData));
        } catch (e) {
            console.warn('Failed to save state cache:', e);
        }
    }
    
    /**
     * Load cached state from localStorage for instant UI
     */
    loadCachedState() {
        try {
            const saved = localStorage.getItem('orei_state_cache');
            if (saved) {
                const cached = JSON.parse(saved);
                
                // Check if cache is reasonably fresh (less than 24 hours old)
                const maxAge = 24 * 60 * 60 * 1000; // 24 hours
                if (cached.timestamp && (Date.now() - cached.timestamp) < maxAge) {
                    // Apply cached data
                    if (cached.routing) {
                        // Convert string keys to numbers for routing
                        for (const [key, value] of Object.entries(cached.routing)) {
                            this.routing[parseInt(key)] = value;
                        }
                    }
                    if (cached.inputs) {
                        // Merge cached inputs with defaults to preserve structure
                        for (const [key, value] of Object.entries(cached.inputs)) {
                            const numKey = parseInt(key);
                            if (this.inputs[numKey]) {
                                this.inputs[numKey] = { ...this.inputs[numKey], ...value };
                            }
                        }
                    }
                    if (cached.outputs) {
                        // Merge cached outputs with defaults to preserve structure
                        for (const [key, value] of Object.entries(cached.outputs)) {
                            const numKey = parseInt(key);
                            if (this.outputs[numKey]) {
                                this.outputs[numKey] = { ...this.outputs[numKey], ...value };
                            }
                        }
                    }
                    if (cached.presets) {
                        this.presets = cached.presets;
                    }
                    if (cached.scenes && Array.isArray(cached.scenes)) {
                        this.scenes = cached.scenes;
                        // Emit so UI renders immediately
                        this.emit('scenes', this.scenes);
                    }
                    if (cached.info) {
                        this.info = { ...this.info, ...cached.info };
                    }
                    
                    console.log('[State] Loaded cached state from localStorage');
                } else {
                    console.log('[State] Cache expired, using defaults');
                    localStorage.removeItem('orei_state_cache');
                }
            } else {
                console.log('[State] No cached state found, using defaults');
            }
        } catch (e) {
            console.warn('[State] Failed to load state cache:', e);
        }
    }

    /**
     * Get primary connected output (first with displayConnected)
     */
    getPrimaryOutput() {
        for (let o = 1; o <= this.info.outputCount; o++) {
            if (this.outputs[o]?.displayConnected) {
                return o;
            }
        }
        return 1; // Fallback to output 1
    }
    
    /**
     * Get the input currently routed to a specific output
     */
    getRoutedInput(output) {
        return this.routing[output] || 1;
    }
    
    /**
     * Get the primary output with ARC enabled (for volume control)
     */
    getArcOutput() {
        for (let o = 1; o <= this.info.outputCount; o++) {
            if (this.outputs[o]?.arcEnabled && this.outputs[o]?.displayConnected) {
                return o;
            }
        }
        return this.getPrimaryOutput();
    }
    
    /**
     * Auto-detect CEC navigation target based on current routing
     */
    getAutoNavTarget() {
        const primaryOutput = this.getPrimaryOutput();
        const primaryInput = this.getRoutedInput(primaryOutput);
        return {
            type: 'input',
            port: primaryInput,
            name: this.getInputName(primaryInput)
        };
    }
    
    /**
     * Auto-detect CEC volume target based on current routing
     */
    getAutoVolumeTarget() {
        const arcOutput = this.getArcOutput();
        return {
            type: 'output',
            port: arcOutput,
            name: this.getOutputName(arcOutput)
        };
    }
    
    /**
     * Update CEC tray position
     */
    setCecTrayPosition(position) {
        this.cecTray.position = position;
        this.emit('cecTrayPosition', position);
        this.saveCecTraySettings();
    }
    
    /**
     * Update CEC tray pinned state
     */
    setCecTrayPinned(pinned) {
        this.cecTray.pinned = pinned;
        this.emit('cecTrayPinned', pinned);
        this.saveCecTraySettings();
    }
    
    /**
     * Update CEC target configuration
     */
    setCecTarget(targetType, type, port) {
        this.cecTray.targets[targetType] = { type, port };
        this.emit('cecTarget', { targetType, type, port });
        this.saveCecTraySettings();
    }
    
    /**
     * Save CEC tray settings to localStorage
     */
    saveCecTraySettings() {
        try {
            localStorage.setItem('orei_cec_tray', JSON.stringify(this.cecTray));
        } catch (e) {
            console.warn('Failed to save CEC tray settings:', e);
        }
    }
    
    /**
     * Load CEC tray settings from localStorage
     */
    loadCecTraySettings() {
        try {
            const saved = localStorage.getItem('orei_cec_tray');
            if (saved) {
                const parsed = JSON.parse(saved);
                this.cecTray = { ...this.cecTray, ...parsed };
            }
        } catch (e) {
            console.warn('Failed to load CEC tray settings:', e);
        }
    }
    
    /**
     * Update input signal status
     */
    setInputSignal(input, signalActive) {
        if (this.inputs[input]) {
            this.inputs[input].signalActive = signalActive;
            this.emit('inputSignal', { input, signalActive });
            this.emit('inputs', this.inputs);
        }
    }
    
    /**
     * Update all input signal statuses at once
     */
    setInputSignals(inactive) {
        // inactive array from matrix: 1 = signal present, 0 = no signal
        inactive.forEach((val, idx) => {
            const inputNum = idx + 1;
            if (this.inputs[inputNum]) {
                const hasSignal = val === 1;
                this.inputs[inputNum].signalActive = hasSignal;
                // Infer cable: if signal present, cable must be connected
                // If no signal, we can't tell (could be unplugged or device off)
                this.inputs[inputNum].cableConnected = hasSignal ? true : null;
            }
        });
        // After updating inputs, recalculate output signals
        this.updateOutputSignals();
        this.emit('inputs', this.inputs);
    }
    
    /**
     * Update output display connection status
     */
    setOutputConnected(output, connected) {
        if (this.outputs[output]) {
            this.outputs[output].displayConnected = connected;
            this.emit('outputConnected', { output, connected });
            this.emit('outputs', this.outputs);
        }
    }
    
    /**
     * Update all output statuses from API response
     */
    setOutputStatuses(data) {
        // data contains: allconnect, allout, allaudiomute, allarc, allhdr, allhdcp, allscaler
        if (data.allconnect) {
            data.allconnect.forEach((val, idx) => {
                const outNum = idx + 1;
                if (this.outputs[outNum]) {
                    this.outputs[outNum].displayConnected = val === 1;
                }
            });
        }
        if (data.allout) {
            data.allout.forEach((val, idx) => {
                const outNum = idx + 1;
                if (this.outputs[outNum]) {
                    this.outputs[outNum].enabled = val === 1;
                }
            });
        }
        if (data.allaudiomute) {
            data.allaudiomute.forEach((val, idx) => {
                const outNum = idx + 1;
                if (this.outputs[outNum]) {
                    this.outputs[outNum].audioMuted = val === 1;
                }
            });
        }
        if (data.allarc) {
            data.allarc.forEach((val, idx) => {
                const outNum = idx + 1;
                if (this.outputs[outNum]) {
                    this.outputs[outNum].arcEnabled = val === 1;
                }
            });
        }
        // Recalculate output signals after updating connection status
        this.updateOutputSignals();
    }
    
    /**
     * Toggle favorite preset
     */
    toggleFavoritePreset(presetId) {
        const idx = this.favorites.presets.indexOf(presetId);
        if (idx >= 0) {
            this.favorites.presets.splice(idx, 1);
        } else {
            this.favorites.presets.push(presetId);
        }
        this.emit('favorites', this.favorites);
        this.saveFavorites();
    }
    
    /**
     * Toggle favorite scene
     */
    toggleFavoriteScene(sceneId) {
        const idx = this.favorites.scenes.indexOf(sceneId);
        if (idx >= 0) {
            this.favorites.scenes.splice(idx, 1);
        } else {
            this.favorites.scenes.push(sceneId);
        }
        this.emit('favorites', this.favorites);
        this.saveFavorites();
    }
    
    /**
     * Save favorites to localStorage
     */
    saveFavorites() {
        try {
            localStorage.setItem('orei_favorites', JSON.stringify(this.favorites));
        } catch (e) {
            console.warn('Failed to save favorites:', e);
        }
    }
    
    /**
     * Load favorites from localStorage
     */
    loadFavorites() {
        try {
            const saved = localStorage.getItem('orei_favorites');
            if (saved) {
                this.favorites = JSON.parse(saved);
            }
        } catch (e) {
            console.warn('Failed to load favorites:', e);
        }
        
        // Also load CEC tray settings
        this.loadCecTraySettings();
    }
    
    // ==========================================
    // Icon Management (Phase 2)
    // ==========================================
    
    /**
     * Get icon for an input device
     * @param {number} input - Input number
     * @returns {string} Icon ID
     */
    getInputIcon(input) {
        return this.inputs[input]?.icon || 'generic-input';
    }
    
    /**
     * Set icon for an input device
     * @param {number} input - Input number
     * @param {string} iconId - Icon identifier
     */
    setInputIcon(input, iconId) {
        if (!this.inputs[input]) {
            this.inputs[input] = {};
        }
        this.inputs[input].icon = iconId;
        this.addRecentIcon(iconId);
        this.emit('inputs');
        this.saveCachedState();
    }
    
    /**
     * Get icon for an output device
     * @param {number} output - Output number
     * @returns {string} Icon ID
     */
    getOutputIcon(output) {
        return this.outputs[output]?.icon || 'generic-output';
    }
    
    /**
     * Set icon for an output device
     * @param {number} output - Output number
     * @param {string} iconId - Icon identifier
     */
    setOutputIcon(output, iconId) {
        if (!this.outputs[output]) {
            this.outputs[output] = {};
        }
        this.outputs[output].icon = iconId;
        this.addRecentIcon(iconId);
        this.emit('outputs');
        this.saveCachedState();
    }
    
    /**
     * Load recently used icons from localStorage
     */
    loadRecentIcons() {
        try {
            const saved = localStorage.getItem('orei_recent_icons');
            if (saved) {
                this.recentIcons = JSON.parse(saved);
            }
        } catch (e) {
            console.warn('Failed to load recent icons:', e);
            this.recentIcons = [];
        }
    }
    
    /**
     * Add an icon to the recently used list
     * @param {string} iconId - Icon identifier
     */
    addRecentIcon(iconId) {
        // Don't track generic icons
        if (iconId.startsWith('generic-')) return;
        
        // Add to front, remove duplicates, limit to 8
        this.recentIcons = [iconId, ...this.recentIcons.filter(i => i !== iconId)].slice(0, 8);
        
        try {
            localStorage.setItem('orei_recent_icons', JSON.stringify(this.recentIcons));
        } catch (e) {
            console.warn('Failed to save recent icons:', e);
        }
    }
    
    /**
     * Get recently used icons
     * @returns {Array} Array of icon IDs
     */
    getRecentIcons() {
        return this.recentIcons || [];
    }
    
    /**
     * Load device settings from backend (persisted names, icons, colors)
     * Called during app initialization to restore saved customizations
     */
    async loadDeviceSettings() {
        try {
            console.log('[State] Loading device settings from backend...');
            const result = await api.getDeviceSettings();
            
            if (result?.success && result?.data) {
                const settings = result.data;
                
                // Apply input settings
                if (settings.inputs) {
                    for (const [key, value] of Object.entries(settings.inputs)) {
                        const inputNum = parseInt(key);
                        if (this.inputs[inputNum]) {
                            if (value.name) this.inputs[inputNum].name = value.name;
                            if (value.icon) this.inputs[inputNum].icon = value.icon;
                            if (value.color) this.inputs[inputNum].color = value.color;
                        }
                    }
                }
                
                // Apply output settings
                if (settings.outputs) {
                    for (const [key, value] of Object.entries(settings.outputs)) {
                        const outputNum = parseInt(key);
                        if (this.outputs[outputNum]) {
                            if (value.name) this.outputs[outputNum].name = value.name;
                            if (value.icon) this.outputs[outputNum].icon = value.icon;
                            if (value.color) this.outputs[outputNum].color = value.color;
                        }
                    }
                }
                
                // Emit updates
                this.emit('inputs', this.inputs);
                this.emit('outputs', this.outputs);
                
                // Save to cache
                this.saveCachedState();
                
                console.log('[State] Device settings loaded successfully');
                return true;
            }
        } catch (error) {
            console.warn('[State] Failed to load device settings:', error);
        }
        return false;
    }

    /**
     * Subscribe to state changes
     * @param {string} event - Event name
     * @param {Function} callback - Callback function
     * @returns {Function} Unsubscribe function
     */
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, new Set());
        }
        this.listeners.get(event).add(callback);
        
        return () => {
            this.listeners.get(event).delete(callback);
        };
    }

    /**
     * Emit an event to all listeners
     * @param {string} event - Event name
     * @param {*} data - Event data
     */
    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }

    /**
     * Update connection status
     */
    setConnected(connected) {
        this.connected = connected;
        this.emit('connection', connected);
    }

    /**
     * Update WebSocket connection status
     */
    setWsConnected(connected) {
        this.wsConnected = connected;
        this.emit('wsConnection', connected);
    }

    /**
     * Update system info
     */
    setInfo(info) {
        this.info = { ...this.info, ...info };
        this.emit('info', this.info);
    }

    /**
     * Update a single route
     */
    setRoute(output, input) {
        const oldInput = this.routing[output];
        if (oldInput !== input) {
            this.routing[output] = input;
            if (this.outputs[output]) {
                this.outputs[output].input = input;
            }
            this.emit('route', { output, input, oldInput });
            this.emit('routing', this.routing);
            
            // Clear active scene when routing changes manually
            if (this.activeScene) {
                this.setActiveScene(null);
            }
            
            // Save to cache so next page load shows correct state
            this.saveCachedState();
        }
    }

    /**
     * Update all routing at once
     */
    setRouting(routing) {
        this.routing = { ...routing };
        // Also update outputs
        Object.entries(routing).forEach(([output, input]) => {
            if (this.outputs[output]) {
                this.outputs[output].input = input;
            }
        });
        // Recalculate output signals based on new routing
        this.updateOutputSignals();
        this.emit('routing', this.routing);
        this.saveCachedState();
    }

    /**
     * Recalculate output signal status based on cable connection and routed input signal
     * Output has signal = (cable connected) AND (routed input has signal)
     */
    updateOutputSignals() {
        for (let o = 1; o <= this.info.outputCount; o++) {
            if (this.outputs[o]) {
                const routedInput = this.routing[o] || 0;
                // Prefer Telnet-based cableConnected over HTTP displayConnected
                const cableConnected = this.outputs[o].cableConnected !== null 
                    ? this.outputs[o].cableConnected 
                    : this.outputs[o].displayConnected;
                const inputHasSignal = routedInput > 0 && this.inputs[routedInput]?.signalActive;
                
                // Output receives signal only if cable is connected AND routed input has signal
                this.outputs[o].signalActive = cableConnected && inputHasSignal;
            }
        }
        this.emit('outputs', this.outputs);
    }

    /**
     * Update input name
     */
    setInputName(input, name) {
        if (this.inputs[input]) {
            this.inputs[input].name = name;
            this.emit('inputName', { input, name });
            this.emit('inputs', this.inputs);
            this.saveCachedState();
        }
    }

    /**
     * Update all input names
     */
    setInputNames(names) {
        Object.entries(names).forEach(([input, name]) => {
            if (this.inputs[input]) {
                this.inputs[input].name = name;
            }
        });
        this.emit('inputs', this.inputs);
        this.saveCachedState();
    }

    /**
     * Update output name
     */
    setOutputName(output, name) {
        if (this.outputs[output]) {
            this.outputs[output].name = name;
            this.emit('outputName', { output, name });
            this.emit('outputs', this.outputs);
            this.saveCachedState();
        }
    }

    /**
     * Update output audio mute
     */
    setOutputMute(output, muted) {
        if (this.outputs[output]) {
            this.outputs[output].audioMuted = muted;
            this.emit('outputMute', { output, muted });
            this.emit('outputs', this.outputs);
        }
    }

    /**
     * Update output HDR mode
     */
    setOutputHdr(output, mode) {
        if (this.outputs[output]) {
            this.outputs[output].hdrMode = mode;
            this.emit('outputHdr', { output, mode });
        }
    }

    /**
     * Update output HDCP mode
     */
    setOutputHdcp(output, mode) {
        if (this.outputs[output]) {
            this.outputs[output].hdcpMode = mode;
            this.emit('outputHdcp', { output, mode });
        }
    }

    /**
     * Update full output status
     */
    setOutputStatus(output, status) {
        if (this.outputs[output]) {
            this.outputs[output] = { ...this.outputs[output], ...status };
            this.emit('output', { output, status: this.outputs[output] });
        }
    }

    /**
     * Update scenes list
     */
    setScenes(scenes) {
        this.scenes = scenes;
        this.emit('scenes', this.scenes);
        // Cache scenes for instant loading on refresh
        this.saveCachedState();
    }

    /**
     * Add a new scene
     */
    addScene(scene) {
        this.scenes.push(scene);
        this.emit('scenes', this.scenes);
        this.saveCachedState();
    }

    /**
     * Remove a scene
     */
    removeScene(sceneId) {
        this.scenes = this.scenes.filter(s => s.id !== sceneId);
        this.emit('scenes', this.scenes);
        this.saveCachedState();
        
        // Clear active scene if it was removed
        if (this.activeScene && this.activeScene.id === sceneId) {
            this.setActiveScene(null);
        }
    }

    /**
     * Set the currently active scene
     * @param {Object|null} scene - The scene object or null to clear
     */
    setActiveScene(scene) {
        this.activeScene = scene;
        this.emit('activeScene', scene);
    }

    /**
     * Get the currently active scene
     */
    getActiveScene() {
        return this.activeScene;
    }

    // ===== Profile Management (Enhanced Scenes) =====

    /**
     * Update profiles list
     */
    setProfiles(profiles) {
        this.profiles = profiles;
        this.emit('profiles', this.profiles);
    }

    /**
     * Add a new profile
     */
    addProfile(profile) {
        this.profiles.push(profile);
        this.emit('profiles', this.profiles);
    }

    /**
     * Update an existing profile
     */
    updateProfile(profileId, updates) {
        const idx = this.profiles.findIndex(p => p.id === profileId);
        if (idx !== -1) {
            this.profiles[idx] = { ...this.profiles[idx], ...updates };
            this.emit('profiles', this.profiles);
        }
    }

    /**
     * Remove a profile
     */
    removeProfile(profileId) {
        this.profiles = this.profiles.filter(p => p.id !== profileId);
        this.emit('profiles', this.profiles);
        
        // Clear active profile if it was removed
        if (this.activeProfile && this.activeProfile.id === profileId) {
            this.setActiveProfile(null);
        }
    }

    /**
     * Set the currently active profile
     * @param {Object|null} profile - The profile object or null to clear
     */
    setActiveProfile(profile) {
        this.activeProfile = profile;
        // Also set activeScene for backward compatibility
        this.activeScene = profile;
        // Clear active preset when a profile is activated
        if (profile) {
            this.activePreset = null;
            this.emit('activePreset', null);
        }
        this.emit('activeProfile', profile);
        this.emit('activeScene', profile);
    }

    /**
     * Set the currently active hardware preset
     * @param {number|null} presetNumber - The preset number (1-8) or null to clear
     */
    setActivePreset(presetNumber) {
        this.activePreset = presetNumber;
        // Clear active profile when a preset is activated
        if (presetNumber) {
            this.activeProfile = null;
            this.activeScene = null;
            this.emit('activeProfile', null);
            this.emit('activeScene', null);
        }
        this.emit('activePreset', presetNumber);
    }

    /**
     * Get the currently active preset
     */
    getActivePreset() {
        return this.activePreset;
    }

    /**
     * Get the currently active profile
     */
    getActiveProfile() {
        return this.activeProfile;
    }

    /**
     * Get a profile by ID
     */
    getProfile(profileId) {
        return this.profiles.find(p => p.id === profileId);
    }

    /**
     * Update presets
     */
    setPresets(presets) {
        this.presets = presets;
        this.emit('presets', this.presets);
    }

    /**
     * Set active tab
     */
    setActiveTab(tab) {
        this.ui.activeTab = tab;
        this.emit('activeTab', tab);
    }

    /**
     * Set selected output
     */
    setSelectedOutput(output) {
        this.ui.selectedOutput = output;
        this.emit('selectedOutput', output);
    }

    /**
     * Set loading state
     */
    setLoading(loading) {
        this.ui.loading = loading;
        this.emit('loading', loading);
    }

    /**
     * Get input name with fallback
     */
    getInputName(input) {
        return this.inputs[input]?.name || `Input ${input}`;
    }

    /**
     * Get output name with fallback
     */
    getOutputName(output) {
        return this.outputs[output]?.name || `Output ${output}`;
    }

    /**
     * Apply full status update from API
     */
    applyStatus(status) {
        Logger.state('status', status);
        
        // Handle both direct response and nested data
        const data = status.data || status;
        
        // Update routing from map format {output: input}
        if (data.routing && typeof data.routing === 'object') {
            Logger.state('routing (map)', data.routing);
            this.setRouting(data.routing);
        }
        
        // Update outputs array to routing map (legacy format)
        if (data.outputs && Array.isArray(data.outputs)) {
            const routing = {};
            data.outputs.forEach((input, index) => {
                routing[index + 1] = input;
            });
            Logger.state('routing (array)', routing);
            this.setRouting(routing);
        }
        
        // Update input names from map format {input: name}
        if (data.input_names && typeof data.input_names === 'object') {
            Logger.state('input_names', data.input_names);
            this.setInputNames(data.input_names);
        }
        
        // Update output names
        if (data.output_names && typeof data.output_names === 'object') {
            for (const [output, name] of Object.entries(data.output_names)) {
                if (this.outputs[output]) {
                    this.outputs[output].name = name;
                }
            }
            this.emit('outputs', this.outputs);
        }
        
        // Update preset names
        if (data.preset_names && typeof data.preset_names === 'object') {
            for (const [preset, name] of Object.entries(data.preset_names)) {
                this.presets[preset] = { name, routing: {} };
            }
            this.emit('presets', this.presets);
        }
        
        // Mark as loaded
        this.setLoading(false);
        this.setConnected(true);
        
        // Save state to cache for instant loading next time
        this.saveCachedState();
    }

    /**
     * Apply info update from API
     */
    applyInfo(info) {
        Logger.state('info', info);
        
        // Handle both direct response and nested data
        const data = info.data || info;
        
        this.setInfo({
            model: data.model || 'BK-808',
            firmwareVersion: data.firmware_version || data.version || '',
            apiVersion: data.api_version || '',
            matrixHost: data.matrix_host || '',
            inputCount: data.input_count || 8,
            outputCount: data.output_count || 8
        });
    }
}

// Create global state instance
window.state = new AppState();
