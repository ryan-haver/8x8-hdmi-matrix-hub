/**
 * OREI Matrix Control - REST API Client
 * Handles all communication with the matrix REST API
 */

class MatrixAPI {
    constructor(baseUrl = '') {
        // Always use same origin - the frontend talks to the backend REST API,
        // and the backend handles connecting to the physical matrix device.
        // Matrix host configuration is done via /api/settings/matrix-host
        this.baseUrl = baseUrl || window.location.origin;
    }

    /**
     * Get the API base URL (always same origin)
     * 
     * The frontend should always talk to the same origin (REST API server).
     * Matrix host configuration for the backend is done via /api/settings endpoints.
     */
    static getMatrixHost() {
        // Always use same origin - backend handles the matrix connection
        return window.location.origin;
    }

    /**
     * Set the matrix host URL - DEPRECATED
     * Matrix host is now configured via backend /api/settings/matrix-host
     * This method is kept for backward compatibility but clears any old localStorage values
     */
    static setMatrixHost(host) {
        // Clear any old localStorage value - frontend always uses same origin now
        const storageKey = Constants?.CONNECTION?.STORAGE_KEY || 'orei_matrix_host';
        localStorage.removeItem(storageKey);
        console.info('MatrixAPI.setMatrixHost is deprecated. Use /api/settings/matrix-host endpoint instead.');
        return window.location.origin;
    }

    /**
     * Clear the stored matrix host - DEPRECATED
     * Matrix host is now configured via backend /api/settings/matrix-host
     */
    static clearMatrixHost() {
        // Clear any old localStorage value
        const storageKey = Constants?.CONNECTION?.STORAGE_KEY || 'orei_matrix_host';
        localStorage.removeItem(storageKey);
    }

    /**
     * Clean up any legacy localStorage values on class load
     */
    static cleanupLegacyStorage() {
        const storageKey = Constants?.CONNECTION?.STORAGE_KEY || 'orei_matrix_host';
        if (localStorage.getItem(storageKey)) {
            console.info('Cleaning up legacy orei_matrix_host localStorage value');
            localStorage.removeItem(storageKey);
        }
    }

    // ===== Helper Methods =====
    
    /**
     * Retry helper for network operations.
     * @param {Function} operation - Async function to retry
     * @param {number} maxRetries - Maximum number of retry attempts
     * @param {number} delayMs - Initial delay between retries (doubles each retry)
     */
    async _retryOperation(operation, maxRetries = 3, delayMs = 500) {
        let lastError;
        for (let attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                return await operation();
            } catch (error) {
                lastError = error;
                if (attempt < maxRetries) {
                    // Don't retry on 4xx client errors (except 408, 429)
                    if (error.message && error.message.includes('HTTP 4')) {
                        const status = parseInt(error.message.match(/HTTP (\d+)/)?.[1] || '0');
                        if (status !== 408 && status !== 429 && status >= 400 && status < 500) {
                            throw error; // Don't retry client errors
                        }
                    }
                    const backoff = delayMs * Math.pow(2, attempt);
                    await new Promise((resolve) => setTimeout(resolve, backoff));
                }
            }
        }
        throw lastError;
    }

    async get(path, options = {}) {
        const { retries = 0 } = options;
        try {
            return await this._retryOperation(async () => {
                Logger.api('GET', path);
                const response = await fetch(`${this.baseUrl}${path}`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                const data = await response.json();
                Logger.apiResponse(path, data);
                return data;
            }, retries);
        } catch (error) {
            console.error(`API GET ${path} failed:`, error);
            throw error;
        }
    }

    async post(path, body = {}, options = {}) {
        const { retries = 0 } = options;
        try {
            return await this._retryOperation(async () => {
                Logger.api('POST', path, body);
                const response = await fetch(`${this.baseUrl}${path}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.error || `HTTP ${response.status}`);
                }
                const data = await response.json();
                Logger.apiResponse(path, data);
                return data;
            }, retries);
        } catch (error) {
            console.error(`API POST ${path} failed:`, error);
            throw error;
        }
    }

    async delete(path) {
        try {
            Logger.api('DELETE', path);
            const response = await fetch(`${this.baseUrl}${path}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            Logger.apiResponse(path, data);
            return data;
        } catch (error) {
            console.error(`API DELETE ${path} failed:`, error);
            throw error;
        }
    }

    async put(path, body = {}) {
        try {
            Logger.api('PUT', path, body);
            const response = await fetch(`${this.baseUrl}${path}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }
            const data = await response.json();
            Logger.apiResponse(path, data);
            return data;
        } catch (error) {
            console.error(`API PUT ${path} failed:`, error);
            throw error;
        }
    }

    // ===== System Info =====
    
    async getInfo() {
        return this.get('/api/info');
    }

    async getApiDocs() {
        return this.get('/api');
    }

    // ===== Status =====
    
    async getStatus() {
        return this.get('/api/status');
    }

    async getInputStatus() {
        return this.get('/api/status/inputs');
    }

    async getOutputStatus() {
        return this.get('/api/status/outputs');
    }

    // ===== Routing =====
    
    async switchInput(output, input) {
        return this.post(`/api/output/${output}/source`, { input });
    }

    async switchAll(input) {
        Logger.api('POST', '/api/switch', { input });
        const result = await this.post('/api/switch', { input });
        Logger.log('switchAll result:', result);
        return result;
    }

    // ===== Input Names =====
    
    async setInputName(input, name) {
        return this.post(`/api/input/${input}/name`, { name });
    }

    // ===== Output Names =====

    async setOutputName(output, name) {
        return this.post(`/api/output/${output}/name`, { name });
    }

    // ===== Audio Control =====
    
    async setAudioMute(output, muted) {
        return this.post(`/api/output/${output}/mute`, { muted });
    }

    async setOutputArc(output, enabled) {
        return this.post(`/api/output/${output}/arc`, { enabled });
    }

    // ===== HDR/HDCP Control =====
    
    async setHdrMode(output, mode) {
        return this.post(`/api/output/${output}/hdr`, { mode });
    }

    async setHdcpMode(output, mode) {
        return this.post(`/api/output/${output}/hdcp`, { mode });
    }

    async setScalerMode(output, mode) {
        return this.post(`/api/output/${output}/scaler`, { mode });
    }

    async setOutputEnable(output, enabled) {
        return this.post(`/api/output/${output}/enable`, { enabled });
    }

    // ===== Presets =====
    
    async getPresets() {
        return this.get('/api/presets');
    }

    async recallPreset(preset) {
        return this.post(`/api/preset/${preset}`);
    }

    async savePreset(preset) {
        return this.post(`/api/preset/${preset}/save`);
    }

    // ===== Scenes/Profiles =====
    // Note: "scenes" are now called "profiles" in the new API
    
    async listScenes() {
        // Use profiles API, transform response to maintain compatibility
        const result = await this.get('/api/profiles');
        if (result?.success && result?.data?.profiles) {
            // Transform profiles response to scenes format for backward compatibility
            return { scenes: result.data.profiles };
        }
        return { scenes: [] };
    }

    async getScene(id) {
        return this.get(`/api/profile/${id}`);
    }

    async createScene(name, outputs = null, cecConfig = null, id = null) {
        // Use profiles API
        const body = { name };
        if (id) {
            body.id = id;
        } else {
            // Generate ID from name
            body.id = name.toLowerCase().replace(/[^a-z0-9]+/g, '_').substring(0, 32) + '_' + Date.now().toString(36);
        }
        if (outputs) {
            body.outputs = outputs;
        }
        if (cecConfig) {
            body.cec_config = cecConfig;
        }
        return this.post('/api/profile', body);
    }

    async deleteScene(id) {
        return this.delete(`/api/profile/${id}`);
    }

    async recallScene(id) {
        return this.post(`/api/profile/${id}/recall`);
    }

    async saveCurrentAsScene(name) {
        // For backwards compatibility, create a profile from current routing
        return this.post('/api/profile/save-current', { name });
    }

    // ===== Scene/Profile CEC Configuration =====
    
    async getSceneCecConfig(sceneId) {
        return this.get(`/api/profile/${sceneId}/cec`);
    }
    
    async updateSceneCecConfig(sceneId, cecConfig) {
        return this.post(`/api/profile/${sceneId}/cec`, { cec_config: cecConfig });
    }
    
    async autoResolveCecConfig(sceneId, apply = false) {
        const path = `/api/profile/${sceneId}/cec/auto-resolve${apply ? '?apply=true' : ''}`;
        return this.post(path);
    }

    // ===== Profiles (Enhanced Scenes) =====
    
    async listProfiles() {
        return this.get('/api/profiles');
    }

    async getProfile(id) {
        return this.get(`/api/profile/${id}`);
    }

    async createProfile(profile) {
        return this.post('/api/profile', profile);
    }

    async updateProfile(id, updates) {
        return this.put(`/api/profile/${id}`, updates);
    }

    async deleteProfile(id) {
        return this.delete(`/api/profile/${id}`);
    }

    async recallProfile(id) {
        return this.post(`/api/profile/${id}/recall`);
    }

    async getProfileCecConfig(profileId) {
        return this.get(`/api/profile/${profileId}/cec`);
    }

    async updateProfileCecConfig(profileId, cecConfig) {
        return this.post(`/api/profile/${profileId}/cec`, { cec_config: cecConfig });
    }

    async getProfileMacros(profileId) {
        return this.get(`/api/profile/${profileId}/macros`);
    }

    async updateProfileMacros(profileId, macros, powerOnMacro = null, powerOffMacro = null) {
        const body = { macros };
        if (powerOnMacro !== null) body.power_on_macro = powerOnMacro;
        if (powerOffMacro !== null) body.power_off_macro = powerOffMacro;
        return this.post(`/api/profile/${profileId}/macros`, body);
    }

    async reorderProfiles(profiles) {
        // profiles: array of { id, pin_order } or { id, pinned, pin_order }
        return this.post('/api/profiles/reorder', { profiles });
    }

    async updateScene(sceneId, updates) {
        // Wrapper for updating scene/profile properties like pinned, pin_order
        return this.put(`/api/profile/${sceneId}`, updates);
    }

    // ===== EDID Management =====
    
    async getEdidModes() {
        return this.get('/api/edid/modes');
    }

    async setEdidMode(input, mode) {
        return this.post(`/api/input/${input}/edid`, { mode });
    }

    // ===== LCD Settings =====
    
    async getLcdTimeoutModes() {
        return this.get('/api/system/lcd/modes');
    }
    
    async setLcdTimeout(mode) {
        return this.post('/api/system/lcd', { mode });
    }

    // ===== Power Control =====
    
    /**
     * Power on the matrix (wake from standby)
     */
    async powerOn() {
        return this.post('/api/power/on');
    }

    /**
     * Power off the matrix (enter standby)
     */
    async powerOff() {
        return this.post('/api/power/off');
    }

    /**
     * Ensure the matrix is awake. Call this at app startup.
     * Returns true if matrix is responsive, false otherwise.
     */
    async ensureAwake() {
        try {
            // First try to get status - if it works, matrix is awake
            const status = await this.getStatus();
            if (status?.success) {
                console.log('[Matrix] Already awake');
                return true;
            }
        } catch (e) {
            console.log('[Matrix] Status check failed, attempting power on...');
        }

        // Try to power on
        try {
            const result = await this.powerOn();
            if (result?.success) {
                console.log('[Matrix] Wake command sent successfully');
                // Wait a moment for the matrix to fully wake
                await new Promise(resolve => setTimeout(resolve, 1000));
                return true;
            }
        } catch (e) {
            console.error('[Matrix] Power on failed:', e);
        }

        return false;
    }

    async powerCycle() {
        return this.post('/api/system/power-cycle');
    }

    async reboot() {
        return this.post('/api/system/reboot');
    }

    // ===== CEC Control =====
    
    async sendCecCommand(type, port, command) {
        return this.post(`/api/cec/${type}/${port}/${command}`);
    }

    async getInputCapabilities(input) {
        return this.get(`/api/cec/input/${input}/capabilities`);
    }

    async getOutputCapabilities(output) {
        return this.get(`/api/cec/output/${output}/capabilities`);
    }

    async setCecEnabled(type, port, enabled) {
        return this.post(`/api/cec/${type}/${port}/enable`, { enabled });
    }

    // ===== CEC Macros =====
    
    async getMacros() {
        return this.get('/api/cec/macros');
    }

    async getMacro(macroId) {
        return this.get(`/api/cec/macro/${macroId}`);
    }

    async createMacro(macro) {
        return this.post('/api/cec/macro', macro);
    }

    async updateMacro(macroId, updates) {
        return this.put(`/api/cec/macro/${macroId}`, updates);
    }

    async deleteMacro(macroId) {
        return this.delete(`/api/cec/macro/${macroId}`);
    }

    async executeMacro(macroId) {
        return this.post(`/api/cec/macro/${macroId}/execute`);
    }

    async testMacro(macroId) {
        return this.post(`/api/cec/macro/${macroId}/test`);
    }

    // ===== External Audio =====
    
    async getExtAudioStatus() {
        return this.get('/api/status/ext-audio');
    }

    async getExtAudioModes() {
        return this.get('/api/ext-audio/modes');
    }

    async setExtAudioMode(mode) {
        return this.post('/api/ext-audio/mode', { mode });
    }

    async setExtAudioEnable(output, enabled) {
        return this.post(`/api/ext-audio/${output}/enable`, { enabled });
    }

    async setExtAudioSource(output, source) {
        return this.post(`/api/ext-audio/${output}/source`, { source });
    }

    // ===== Device Settings (Persistent Names/Icons) =====
    
    async getDeviceSettings() {
        return this.get('/api/device-settings');
    }

    async updateDeviceSettings(settings) {
        return this.post('/api/device-settings', settings);
    }

    async getInputSettings(input) {
        return this.get(`/api/device-settings/input/${input}`);
    }

    async updateInputSettings(input, settings) {
        return this.post(`/api/device-settings/input/${input}`, settings);
    }

    async getOutputSettings(output) {
        return this.get(`/api/device-settings/output/${output}`);
    }

    async updateOutputSettings(output, settings) {
        return this.post(`/api/device-settings/output/${output}`, settings);
    }

    // ===== UI Preferences (Custom tabs, sorting, pinning) =====

    async getUiPreferences() {
        return this.get('/api/ui/preferences');
    }

    async updateUiPreferences(prefs) {
        return this.put('/api/ui/preferences', prefs);
    }
}

// Clean up any legacy localStorage values before creating API instance
MatrixAPI.cleanupLegacyStorage();

// Create global API instance
window.api = new MatrixAPI();
