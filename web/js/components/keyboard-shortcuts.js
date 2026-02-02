/**
 * OREI Matrix Control - Keyboard Shortcuts Handler
 * Global keyboard shortcuts for quick actions
 */

class KeyboardShortcuts {
    static shortcuts = new Map();
    static enabled = true;
    static helpVisible = false;

    /**
     * Initialize keyboard shortcuts
     */
    static init() {
        document.addEventListener('keydown', KeyboardShortcuts.handleKeydown);
        KeyboardShortcuts.registerDefaults();
    }

    /**
     * Register default shortcuts
     */
    static registerDefaults() {
        // Navigation
        KeyboardShortcuts.register('1', 'Switch to Matrix view', () => {
            document.querySelector('[data-tab="matrix"]')?.click();
        });
        KeyboardShortcuts.register('2', 'Switch to Inputs view', () => {
            document.querySelector('[data-tab="inputs"]')?.click();
        });
        KeyboardShortcuts.register('3', 'Switch to Outputs view', () => {
            document.querySelector('[data-tab="outputs"]')?.click();
        });
        KeyboardShortcuts.register('4', 'Switch to Scenes view', () => {
            document.querySelector('[data-tab="scenes"]')?.click();
        });

        // Actions
        KeyboardShortcuts.register('n', 'Create new profile', () => {
            window.profileEditor?.openNew();
        });
        KeyboardShortcuts.register('s', 'Open settings', () => {
            if (window.settingsPanel) {
                window.settingsPanel.toggle();
            }
        });
        KeyboardShortcuts.register('r', 'Refresh status', () => {
            if (window.app) {
                window.app.loadInitialData();
            }
        });

        // Help
        KeyboardShortcuts.register('?', 'Show keyboard shortcuts', () => {
            KeyboardShortcuts.toggleHelp();
        });
        KeyboardShortcuts.register('Escape', 'Close dialogs/menus', () => {
            // Close any open modals, menus, etc.
            ContextMenu?.closeAll();
            KeyboardShortcuts.hideHelp();
        });
    }

    /**
     * Register a keyboard shortcut
     * @param {string} key - Key or key combo (e.g., 'n', 'ctrl+s')
     * @param {string} description - Human-readable description
     * @param {Function} handler - Handler function
     * @param {Object} options - Additional options
     */
    static register(key, description, handler, options = {}) {
        const parsed = KeyboardShortcuts.parseKey(key);
        const id = KeyboardShortcuts.keyToId(parsed);
        
        KeyboardShortcuts.shortcuts.set(id, {
            key: parsed,
            description,
            handler,
            ...options
        });
    }

    /**
     * Parse key string into parts
     */
    static parseKey(key) {
        const parts = key.toLowerCase().split('+');
        return {
            ctrl: parts.includes('ctrl'),
            shift: parts.includes('shift'),
            alt: parts.includes('alt'),
            meta: parts.includes('meta'),
            key: parts[parts.length - 1]
        };
    }

    /**
     * Convert parsed key to ID
     */
    static keyToId(parsed) {
        const modifiers = [];
        if (parsed.ctrl) modifiers.push('ctrl');
        if (parsed.shift) modifiers.push('shift');
        if (parsed.alt) modifiers.push('alt');
        if (parsed.meta) modifiers.push('meta');
        modifiers.push(parsed.key);
        return modifiers.join('+');
    }

    /**
     * Handle keydown event
     */
    static handleKeydown = (e) => {
        if (!KeyboardShortcuts.enabled) return;
        
        // Ignore if typing in input/textarea
        const target = e.target;
        if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
            // Only allow Escape
            if (e.key !== 'Escape') return;
        }
        
        const parsed = {
            ctrl: e.ctrlKey,
            shift: e.shiftKey,
            alt: e.altKey,
            meta: e.metaKey,
            key: e.key.toLowerCase()
        };
        
        const id = KeyboardShortcuts.keyToId(parsed);
        const shortcut = KeyboardShortcuts.shortcuts.get(id);
        
        if (shortcut) {
            e.preventDefault();
            shortcut.handler(e);
        }
    };

    /**
     * Enable/disable shortcuts
     */
    static setEnabled(enabled) {
        KeyboardShortcuts.enabled = enabled;
    }

    /**
     * Toggle help overlay
     */
    static toggleHelp() {
        if (KeyboardShortcuts.helpVisible) {
            KeyboardShortcuts.hideHelp();
        } else {
            KeyboardShortcuts.showHelp();
        }
    }

    /**
     * Show help overlay
     */
    static showHelp() {
        if (KeyboardShortcuts.helpVisible) return;
        
        const shortcuts = Array.from(KeyboardShortcuts.shortcuts.entries())
            .filter(([_, s]) => !s.hidden)
            .map(([id, s]) => `
                <div class="shortcut-help__item">
                    <kbd class="shortcut-help__key">${KeyboardShortcuts.formatKey(id)}</kbd>
                    <span class="shortcut-help__desc">${s.description}</span>
                </div>
            `).join('');
        
        const overlay = document.createElement('div');
        overlay.className = 'shortcut-help';
        overlay.innerHTML = `
            <div class="shortcut-help__backdrop"></div>
            <div class="shortcut-help__content glass-heavy">
                <h2 class="shortcut-help__title">Keyboard Shortcuts</h2>
                <div class="shortcut-help__grid">
                    ${shortcuts}
                </div>
                <p class="shortcut-help__hint">Press <kbd>?</kbd> or <kbd>Esc</kbd> to close</p>
            </div>
        `;
        
        document.body.appendChild(overlay);
        
        requestAnimationFrame(() => {
            overlay.classList.add('shortcut-help--visible');
        });
        
        overlay.querySelector('.shortcut-help__backdrop').addEventListener('click', () => {
            KeyboardShortcuts.hideHelp();
        });
        
        KeyboardShortcuts.helpVisible = true;
    }

    /**
     * Hide help overlay
     */
    static hideHelp() {
        if (!KeyboardShortcuts.helpVisible) return;
        
        const overlay = document.querySelector('.shortcut-help');
        if (overlay) {
            overlay.classList.remove('shortcut-help--visible');
            setTimeout(() => overlay.remove(), 200);
        }
        
        KeyboardShortcuts.helpVisible = false;
    }

    /**
     * Format key for display
     */
    static formatKey(id) {
        return id.split('+').map(part => {
            const map = {
                'ctrl': 'Ctrl',
                'shift': 'Shift',
                'alt': 'Alt',
                'meta': '⌘',
                'escape': 'Esc',
                '?': '?'
            };
            return map[part] || part.toUpperCase();
        }).join(' + ');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => KeyboardShortcuts.init());
} else {
    KeyboardShortcuts.init();
}

// Export for use
window.KeyboardShortcuts = KeyboardShortcuts;
