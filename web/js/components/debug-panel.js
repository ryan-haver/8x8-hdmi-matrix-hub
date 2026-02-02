/**
 * OREI Matrix Control - Debug Panel Component
 * Provides visibility into state, API responses, and WebSocket events
 */

class DebugPanel {
    constructor() {
        this.isOpen = false;
        this.logs = [];
        this.maxLogs = 100;
        this.container = null;
        this.fabVisible = this.loadFabVisibility();
        
        // Intercept console.log for state-related logs
        this.originalLog = console.log;
        this.interceptLogs();
        
        // Create the debug panel UI
        this.createPanel();
        
        // Subscribe to state changes
        this.subscribeToState();
        
        // Setup three-finger tap gesture for mobile
        this.setupThreeFingerTap();
    }
    
    /**
     * Load FAB visibility setting from localStorage
     */
    loadFabVisibility() {
        return localStorage.getItem('debug-fab-visible') === 'true';
    }
    
    /**
     * Save FAB visibility setting to localStorage
     */
    saveFabVisibility(visible) {
        this.fabVisible = visible;
        localStorage.setItem('debug-fab-visible', visible ? 'true' : 'false');
        this.updateFabVisibility();
    }
    
    /**
     * Update FAB button visibility based on setting
     */
    updateFabVisibility() {
        const toggleBtn = document.getElementById('debug-toggle');
        if (toggleBtn) {
            toggleBtn.style.display = this.fabVisible ? 'flex' : 'none';
        }
    }
    
    /**
     * Toggle FAB visibility (used by three-finger tap)
     */
    toggleFabVisibility() {
        this.saveFabVisibility(!this.fabVisible);
        if (this.fabVisible) {
            toast.success('Debug panel enabled');
        } else {
            toast.info('Debug panel hidden');
            this.close();
        }
    }
    
    /**
     * Setup three-finger tap gesture for mobile
     */
    setupThreeFingerTap() {
        let touchCount = 0;
        let touchTimer = null;
        
        document.addEventListener('touchstart', (e) => {
            if (e.touches.length === 3) {
                touchCount++;
                
                // Clear existing timer
                if (touchTimer) clearTimeout(touchTimer);
                
                // Reset count after 500ms of no touches
                touchTimer = setTimeout(() => {
                    touchCount = 0;
                }, 500);
                
                // Toggle on single three-finger tap
                if (touchCount === 1) {
                    // Small delay to confirm it's a tap not a gesture
                    setTimeout(() => {
                        if (touchCount === 1) {
                            this.toggleFabVisibility();
                        }
                        touchCount = 0;
                    }, 300);
                }
            }
        }, { passive: true });
    }

    /**
     * Create the debug panel UI
     */
    createPanel() {
        const panel = document.createElement('div');
        panel.id = 'debug-panel';
        panel.className = 'debug-panel';
        panel.innerHTML = `
            <div class="debug-header">
                <h3>🔧 Debug Panel</h3>
                <div class="debug-actions">
                    <button id="debug-refresh" class="debug-btn" title="Refresh state">🔄</button>
                    <button id="debug-clear" class="debug-btn" title="Clear logs">🗑️</button>
                    <button id="debug-close" class="debug-btn" title="Close">✕</button>
                </div>
            </div>
            <div class="debug-tabs">
                <button class="debug-tab active" data-tab="state">State</button>
                <button class="debug-tab" data-tab="routing">Routing</button>
                <button class="debug-tab" data-tab="names">Names</button>
                <button class="debug-tab" data-tab="logs">API Logs</button>
            </div>
            <div class="debug-content">
                <div id="debug-state" class="debug-section active">
                    <pre id="debug-state-json"></pre>
                </div>
                <div id="debug-routing" class="debug-section">
                    <pre id="debug-routing-json"></pre>
                </div>
                <div id="debug-names" class="debug-section">
                    <pre id="debug-names-json"></pre>
                </div>
                <div id="debug-logs" class="debug-section">
                    <div id="debug-logs-list"></div>
                </div>
            </div>
        `;
        
        // Add toggle button to header
        const toggleBtn = document.createElement('button');
        toggleBtn.id = 'debug-toggle';
        toggleBtn.className = 'btn-icon debug-toggle';
        toggleBtn.title = 'Toggle Debug Panel';
        toggleBtn.innerHTML = '🔧';
        toggleBtn.style.display = this.fabVisible ? 'flex' : 'none';
        
        document.body.appendChild(panel);
        document.body.appendChild(toggleBtn);
        
        this.container = panel;
        this.attachEventListeners();
        
        // Add styles
        this.injectStyles();
    }

    /**
     * Inject debug panel styles
     */
    injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .debug-toggle {
                position: fixed;
                bottom: 20px;
                left: 20px;
                width: 56px;
                height: 56px;
                border-radius: 50%;
                background: linear-gradient(145deg, var(--primary-color, #3b82f6), var(--primary-dark, #2563eb));
                color: white;
                border: none;
                font-size: 24px;
                cursor: pointer;
                z-index: 900;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4),
                            0 2px 4px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            .debug-toggle:hover {
                transform: scale(1.05);
                box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5),
                            0 4px 8px rgba(0, 0, 0, 0.15);
            }
            .debug-toggle:active {
                transform: scale(0.95);
            }
            
            .debug-panel {
                position: fixed;
                bottom: 88px;
                left: 20px;
                width: 450px;
                max-height: 500px;
                background: var(--card-background, #1e293b);
                border: 1px solid var(--border-color, #334155);
                border-radius: 12px;
                z-index: 9998;
                display: none;
                flex-direction: column;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 12px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            }
            .debug-panel.open {
                display: flex;
            }
            
            .debug-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                border-bottom: 1px solid var(--border-color, #334155);
                background: rgba(0,0,0,0.2);
                border-radius: 12px 12px 0 0;
            }
            .debug-header h3 {
                margin: 0;
                font-size: 14px;
                color: var(--text-color, #f1f5f9);
            }
            
            .debug-actions {
                display: flex;
                gap: 8px;
            }
            .debug-btn {
                background: none;
                border: none;
                padding: 4px 8px;
                cursor: pointer;
                border-radius: 4px;
                font-size: 14px;
            }
            .debug-btn:hover {
                background: rgba(255,255,255,0.1);
            }
            
            .debug-tabs {
                display: flex;
                border-bottom: 1px solid var(--border-color, #334155);
            }
            .debug-tab {
                flex: 1;
                padding: 8px;
                border: none;
                background: none;
                color: var(--text-muted, #94a3b8);
                cursor: pointer;
                font-size: 11px;
                font-weight: 500;
            }
            .debug-tab.active {
                color: var(--primary-color, #3b82f6);
                border-bottom: 2px solid var(--primary-color, #3b82f6);
            }
            
            .debug-content {
                flex: 1;
                overflow: auto;
                max-height: 350px;
            }
            
            .debug-section {
                display: none;
                padding: 12px;
            }
            .debug-section.active {
                display: block;
            }
            
            .debug-section pre {
                margin: 0;
                white-space: pre-wrap;
                word-break: break-all;
                color: var(--text-color, #f1f5f9);
                font-size: 11px;
                line-height: 1.5;
            }
            
            .debug-log-entry {
                padding: 6px 8px;
                border-bottom: 1px solid var(--border-color, #334155);
                font-size: 11px;
            }
            .debug-log-entry:last-child {
                border-bottom: none;
            }
            .debug-log-entry.api { color: #22c55e; }
            .debug-log-entry.state { color: #3b82f6; }
            .debug-log-entry.error { color: #ef4444; }
            .debug-log-entry.ws { color: #eab308; }
            
            .debug-log-time {
                color: var(--text-muted, #94a3b8);
                margin-right: 8px;
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .debug-panel {
                    left: 10px;
                    right: 10px;
                    width: auto;
                    bottom: 140px;
                    max-height: 55vh;
                }
                .debug-toggle {
                    /* Match CEC FAB mobile positioning */
                    bottom: 80px;
                    left: 16px;
                    width: 50px;
                    height: 50px;
                    font-size: 20px;
                }
            }
            
            @media (max-width: 480px) {
                .debug-toggle {
                    /* Match CEC FAB on smaller screens */
                    bottom: 80px;
                    left: 16px;
                    width: 50px;
                    height: 50px;
                }
                .debug-panel {
                    bottom: 140px;
                    max-height: calc(100vh - 200px);
                }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Toggle button
        document.getElementById('debug-toggle').addEventListener('click', () => this.toggle());
        
        // Close button
        document.getElementById('debug-close').addEventListener('click', () => this.close());
        
        // Refresh button
        document.getElementById('debug-refresh').addEventListener('click', () => this.refresh());
        
        // Clear logs button
        document.getElementById('debug-clear').addEventListener('click', () => this.clearLogs());
        
        // Tab switching
        this.container.querySelectorAll('.debug-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });
    }

    /**
     * Subscribe to state changes
     */
    subscribeToState() {
        if (window.state) {
            state.on('routing', () => this.updateRoutingDisplay());
            state.on('inputs', () => this.updateNamesDisplay());
            state.on('outputs', () => this.updateNamesDisplay());
            state.on('connected', () => this.updateStateDisplay());
        }
    }

    /**
     * Intercept console logs for debugging
     */
    interceptLogs() {
        const self = this;
        console.log = function(...args) {
            self.originalLog.apply(console, args);
            
            // Capture state/API related logs
            const message = args.map(a => 
                typeof a === 'object' ? JSON.stringify(a, null, 2) : String(a)
            ).join(' ');
            
            // Skip Logger-originated messages (they're sent directly to debug panel)
            if (message.startsWith('[Matrix API]') || 
                message.startsWith('[Matrix WS') || 
                message.startsWith('[Matrix State]')) {
                return;
            }
            
            let type = 'info';
            if (message.includes('API') || message.includes('fetch') || message.includes('status')) {
                type = 'api';
            } else if (message.includes('state') || message.includes('Applying') || message.includes('Setting')) {
                type = 'state';
            } else if (message.includes('WebSocket') || message.includes('WS')) {
                type = 'ws';
            }
            
            self.addLog(message, type);
        };
        
        // Also intercept errors
        const originalError = console.error;
        console.error = function(...args) {
            originalError.apply(console, args);
            const message = args.map(a => 
                typeof a === 'object' ? JSON.stringify(a, null, 2) : String(a)
            ).join(' ');
            self.addLog(message, 'error');
        };
    }

    /**
     * Add a log entry
     */
    addLog(message, type = 'info') {
        const now = new Date();
        const time = now.toLocaleTimeString('en-US', { hour12: false });
        
        this.logs.unshift({ time, message, type });
        
        // Limit log size
        if (this.logs.length > this.maxLogs) {
            this.logs.pop();
        }
        
        this.updateLogsDisplay();
    }

    /**
     * Toggle panel visibility
     */
    toggle() {
        this.isOpen = !this.isOpen;
        this.container.classList.toggle('open', this.isOpen);
        if (this.isOpen) {
            this.refresh();
        }
    }

    /**
     * Close panel
     */
    close() {
        this.isOpen = false;
        this.container.classList.remove('open');
    }

    /**
     * Refresh all displays
     */
    refresh() {
        this.updateStateDisplay();
        this.updateRoutingDisplay();
        this.updateNamesDisplay();
        this.updateLogsDisplay();
    }

    /**
     * Clear logs
     */
    clearLogs() {
        this.logs = [];
        this.updateLogsDisplay();
    }

    /**
     * Switch between tabs
     */
    switchTab(tab) {
        this.container.querySelectorAll('.debug-tab').forEach(t => {
            t.classList.toggle('active', t.dataset.tab === tab);
        });
        this.container.querySelectorAll('.debug-section').forEach(s => {
            s.classList.toggle('active', s.id === `debug-${tab}`);
        });
    }

    /**
     * Update state display
     */
    updateStateDisplay() {
        if (!window.state) return;
        
        const stateJson = {
            connected: state.connected,
            wsConnected: state.wsConnected,
            info: state.info,
            ui: state.ui,
            presetCount: Object.keys(state.presets).length,
            inputCount: Object.keys(state.inputs).length,
            outputCount: Object.keys(state.outputs).length
        };
        
        const el = document.getElementById('debug-state-json');
        if (el) {
            el.textContent = JSON.stringify(stateJson, null, 2);
        }
    }

    /**
     * Update routing display
     */
    updateRoutingDisplay() {
        if (!window.state) return;
        
        const routingInfo = {
            routing: state.routing,
            routingTable: Object.entries(state.routing).map(([out, inp]) => ({
                output: parseInt(out),
                outputName: state.getOutputName(parseInt(out)),
                input: inp,
                inputName: state.getInputName(inp)
            }))
        };
        
        const el = document.getElementById('debug-routing-json');
        if (el) {
            el.textContent = JSON.stringify(routingInfo, null, 2);
        }
    }

    /**
     * Update names display
     */
    updateNamesDisplay() {
        if (!window.state) return;
        
        const namesInfo = {
            inputs: Object.entries(state.inputs).map(([num, data]) => ({
                number: parseInt(num),
                name: data.name || `Input ${num}`,
                enabled: data.enabled
            })),
            outputs: Object.entries(state.outputs).map(([num, data]) => ({
                number: parseInt(num),
                name: data.name || `Output ${num}`,
                audioMuted: data.audioMuted
            })),
            presets: Object.entries(state.presets).map(([num, data]) => ({
                number: parseInt(num),
                name: data.name || `Preset ${num}`
            }))
        };
        
        const el = document.getElementById('debug-names-json');
        if (el) {
            el.textContent = JSON.stringify(namesInfo, null, 2);
        }
    }

    /**
     * Update logs display
     */
    updateLogsDisplay() {
        const el = document.getElementById('debug-logs-list');
        if (!el) return;
        
        if (this.logs.length === 0) {
            el.innerHTML = '<div class="debug-log-entry">No logs yet. API calls and state changes will appear here.</div>';
            return;
        }
        
        el.innerHTML = this.logs.map(log => `
            <div class="debug-log-entry ${log.type}">
                <span class="debug-log-time">${log.time}</span>
                ${Helpers.escapeHtml(log.message.substring(0, 500))}${log.message.length > 500 ? '...' : ''}
            </div>
        `).join('');
    }

    /**
     * Manual log API response
     */
    logApiCall(endpoint, response) {
        this.addLog(`API ${endpoint}: ${JSON.stringify(response).substring(0, 200)}`, 'api');
    }
}

// Create global debug panel instance
document.addEventListener('DOMContentLoaded', () => {
    window.debugPanel = new DebugPanel();
});
