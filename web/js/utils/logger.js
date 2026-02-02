/**
 * OREI Matrix Control - Logger Utility
 * 
 * Provides debug logging that can be toggled on/off.
 * Debug logs are disabled by default in production.
 * 
 * Enable debug logging in browser console:
 *   localStorage.setItem('matrix-debug', 'true');
 *   location.reload();
 * 
 * Disable debug logging:
 *   localStorage.removeItem('matrix-debug');
 *   location.reload();
 */

const Logger = {
    // Check if debug mode is enabled
    get debug() {
        return localStorage.getItem('matrix-debug') === 'true';
    },

    /**
     * Log debug messages (only when debug mode is enabled)
     * @param {...any} args - Arguments to log
     */
    log(...args) {
        if (this.debug) {
            console.log('[Matrix]', ...args);
        }
    },

    /**
     * Log info messages (always shown)
     * @param {...any} args - Arguments to log
     */
    info(...args) {
        console.info('[Matrix]', ...args);
    },

    /**
     * Log warning messages (always shown)
     * @param {...any} args - Arguments to log
     */
    warn(...args) {
        console.warn('[Matrix]', ...args);
    },

    /**
     * Log error messages (always shown)
     * @param {...any} args - Arguments to log
     */
    error(...args) {
        console.error('[Matrix]', ...args);
    },

    /**
     * Log API calls - always sends to debug panel, console only in debug mode
     * @param {string} method - HTTP method
     * @param {string} path - API path
     * @param {any} body - Request body (optional)
     */
    api(method, path, body) {
        const message = body !== undefined 
            ? `[Matrix API] ${method} ${path} ${JSON.stringify(body)}`
            : `[Matrix API] ${method} ${path}`;
        
        // Always send to debug panel if available
        if (window.debugPanel) {
            window.debugPanel.addLog(message, 'api');
        }
        
        // Only log to console in debug mode
        if (this.debug) {
            if (body !== undefined) {
                console.log(`[Matrix API] ${method} ${path}`, body);
            } else {
                console.log(`[Matrix API] ${method} ${path}`);
            }
        }
    },

    /**
     * Log API responses - always sends to debug panel, console only in debug mode
     * @param {string} path - API path
     * @param {any} data - Response data
     */
    apiResponse(path, data) {
        // Truncate large responses for display
        const dataStr = JSON.stringify(data);
        const truncated = dataStr.length > 500 ? dataStr.substring(0, 500) + '...' : dataStr;
        const message = `[Matrix API] Response ${path}: ${truncated}`;
        
        // Always send to debug panel if available
        if (window.debugPanel) {
            window.debugPanel.addLog(message, 'api');
        }
        
        // Only log to console in debug mode
        if (this.debug) {
            console.log(`[Matrix API] Response ${path}:`, data);
        }
    },

    /**
     * Log WebSocket messages - always sends to debug panel, console only in debug mode
     * @param {string} direction - 'TX' for sent, 'RX' for received
     * @param {any} data - Message data
     */
    ws(direction, data) {
        const dataStr = typeof data === 'object' ? JSON.stringify(data) : String(data);
        const truncated = dataStr.length > 300 ? dataStr.substring(0, 300) + '...' : dataStr;
        const message = `[Matrix WS ${direction}] ${truncated}`;
        
        // Always send to debug panel if available
        if (window.debugPanel) {
            window.debugPanel.addLog(message, 'ws');
        }
        
        // Only log to console in debug mode
        if (this.debug) {
            console.log(`[Matrix WS ${direction}]`, data);
        }
    },

    /**
     * Log state changes - always sends to debug panel, console only in debug mode
     * @param {string} key - State key being changed
     * @param {any} value - New value
     */
    state(key, value) {
        const valueStr = typeof value === 'object' ? JSON.stringify(value) : String(value);
        const truncated = valueStr.length > 200 ? valueStr.substring(0, 200) + '...' : valueStr;
        const message = `[Matrix State] ${key}: ${truncated}`;
        
        // Always send to debug panel if available
        if (window.debugPanel) {
            window.debugPanel.addLog(message, 'state');
        }
        
        // Only log to console in debug mode
        if (this.debug) {
            console.log(`[Matrix State] ${key}:`, value);
        }
    }
};

// Make Logger available globally
window.Logger = Logger;
