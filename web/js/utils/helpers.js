/**
 * Shared helper utilities for the OREI Matrix Web UI
 * Consolidates common functions to eliminate code duplication
 */

/**
 * Escapes HTML special characters to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped HTML-safe string
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const str = String(text);
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Sanitizes user input by trimming and limiting length
 * @param {string} input - Raw user input
 * @param {number} maxLength - Maximum allowed length (default: 255)
 * @returns {string} Sanitized input
 */
function sanitizeInput(input, maxLength = 255) {
    if (input === null || input === undefined) return '';
    return String(input).trim().slice(0, maxLength);
}

/**
 * Validates that a value is a safe integer within bounds
 * @param {*} value - Value to validate
 * @param {number} min - Minimum allowed value
 * @param {number} max - Maximum allowed value
 * @param {number} defaultValue - Default if invalid
 * @returns {number} Validated integer
 */
function validateInt(value, min, max, defaultValue) {
    const num = parseInt(value, 10);
    if (isNaN(num) || num < min || num > max) {
        return defaultValue;
    }
    return num;
}

/**
 * Safely get nested property from object
 * @param {Object} obj - Object to traverse
 * @param {string} path - Dot-notation path (e.g., 'a.b.c')
 * @param {*} defaultValue - Default if path not found
 * @returns {*} Value at path or default
 */
function getNestedValue(obj, path, defaultValue = undefined) {
    if (!obj || typeof path !== 'string') return defaultValue;
    return path.split('.').reduce((acc, part) => {
        return acc && acc[part] !== undefined ? acc[part] : defaultValue;
    }, obj);
}

/**
 * Debounce function to limit rapid calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Milliseconds to wait
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func.apply(this, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function to limit call frequency
 * @param {Function} func - Function to throttle
 * @param {number} limit - Milliseconds between calls
 * @returns {Function} Throttled function
 */
function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Format a timestamp for display
 * @param {Date|number|string} timestamp - Timestamp to format
 * @returns {string} Formatted time string
 */
function formatTime(timestamp) {
    const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
    if (isNaN(date.getTime())) return '';
    return date.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

/**
 * Generate a unique ID
 * @param {string} prefix - Optional prefix for the ID
 * @returns {string} Unique identifier
 */
function generateId(prefix = '') {
    return `${prefix}${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Check if running on mobile device
 * @returns {boolean} True if mobile
 */
function isMobile() {
    return window.innerWidth < 768;
}

/**
 * Check if running on tablet
 * @returns {boolean} True if tablet
 */
function isTablet() {
    return window.innerWidth >= 768 && window.innerWidth < 1024;
}

/**
 * Check if running on desktop
 * @returns {boolean} True if desktop
 */
function isDesktop() {
    return window.innerWidth >= 1024;
}

// Export for use in modules if needed
if (typeof window !== 'undefined') {
    window.Helpers = {
        escapeHtml,
        sanitizeInput,
        validateInt,
        getNestedValue,
        debounce,
        throttle,
        formatTime,
        generateId,
        isMobile,
        isTablet,
        isDesktop
    };
}
