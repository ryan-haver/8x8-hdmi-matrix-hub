/**
 * OREI Matrix Control - Overlay Manager
 * Ensures only one modal/drawer/dropdown is open at a time
 */

class OverlayManager {
    constructor() {
        this.activeOverlay = null;
        this.overlays = new Map();
        this.stack = [];
        this.triggerElements = new Map();

        this.rightSideDrawers = [
            'quick-actions-drawer',
            'routing-drawer',
            'theme-drawer',
            'general-drawer',
            'hardware-drawer',
            'interface-drawer',
            'shortcuts-drawer',
            'presets-drawer',
            'settings-drawer',
            'integrations-drawer',
            'unified-settings-drawer',
        ];

        this.stackableModals = [
            'icon-picker',
            'confirm-dialog',
            'scene-editor',
            'profile-editor',
            'cec-macro-editor',
            'scene-cec-modal',
            'input-settings-modal',
            'output-settings-modal',
            'dashboard-card-picker',
            'about-dialog',
        ];

        this.boundHandleKeyDown = (event) => this.handleKeyDown(event);
        if (typeof document !== 'undefined' && typeof document.addEventListener === 'function') {
            document.addEventListener('keydown', this.boundHandleKeyDown);
        }
    }

    /**
     * Determine whether an overlay is a modal/picker/dialog that stacks above drawers
     * @param {string} name - Overlay identifier
     * @returns {boolean}
     */
    isStackableModal(name) {
        if (!name || typeof name !== 'string') return false;
        if (this.stackableModals.includes(name)) return true;
        if (
            name.endsWith('-modal') ||
            name.endsWith('-dialog') ||
            name.endsWith('-picker') ||
            name.endsWith('-editor')
        ) {
            return true;
        }
        const options = this.overlays.get(name);
        return Boolean(options?.stackable || options?.type === 'modal');
    }

    /**
     * Remove an overlay name from the internal stack without side effects
     * @param {string} name
     */
    _removeFromStack(name) {
        let idx = this.stack.lastIndexOf(name);
        while (idx !== -1) {
            this.stack.splice(idx, 1);
            idx = this.stack.lastIndexOf(name);
        }
    }

    /**
     * Check whether a saved trigger element is still attached to the document
     * @param {Element|Object} el
     * @returns {boolean}
     */
    _isElementInDocument(el) {
        if (!el) return false;
        if (typeof el.isConnected === 'boolean' && !el.isConnected) {
            return false;
        }
        if (typeof document !== 'undefined') {
            if (typeof document.contains === 'function') {
                return Boolean(document.contains(el));
            }
            if (document.body && typeof document.body.contains === 'function') {
                return Boolean(document.body.contains(el));
            }
        }
        return true;
    }

    /**
     * Register an overlay component
     * @param {string} name - Unique identifier for the overlay
     * @param {Object} options - { open: Function, close: Function, isOpen: () => boolean }
     */
    register(name, options) {
        this.overlays.set(name, options);
        // Keep .routing-drawer elements before .settings-drawer in document.body so
        // equal z-index (var(--z-drawer)) preserves closed-drawer shadow stacking order.
        if (name === 'routing-drawer' || name === 'shortcuts-drawer' || name === 'presets-drawer') {
            const firstSettings = document.body?.querySelector('.settings-drawer-backdrop, .settings-drawer');
            if (firstSettings) {
                for (const el of document.body.querySelectorAll('.routing-backdrop, .routing-drawer')) {
                    if (firstSettings.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING) {
                        document.body.insertBefore(el, firstSettings);
                    }
                }
            }
        }
    }

    /**
     * Called when an overlay is opening
     * Closes any other open overlay first (with viewport-aware bypass for desktop side nav
     * and modal stacking above drawers per UI-07)
     * @param {string} name - Name of the overlay being opened
     */
    onOpen(name) {
        if (typeof document !== 'undefined' && document.activeElement) {
            this.triggerElements.set(name, document.activeElement);
        }

        const isDesktop = (typeof window !== 'undefined' ? window.innerWidth : 1024) >= 768;
        const isModal = this.isStackableModal(name);

        if (isModal) {
            // Stacked modals/pickers push onto the stack above any open drawer without closing it.
        } else if (isDesktop) {
            // On desktop/tablet, we allow the side nav drawer (Control Deck) to coexist with one right-side drawer.
            if (name === 'side-nav-drawer') {
                // Opening side-nav-drawer: do not close any right-side drawer.
            } else {
                // Opening a right-side drawer: close other right-side drawers to avoid overlays on the right.
                if (this.rightSideDrawers.includes(name)) {
                    this.rightSideDrawers.forEach(d => {
                        if (d !== name) {
                            const overlay = this.overlays.get(d);
                            const isOpen = (overlay?.isOpen && overlay.isOpen()) || this.stack.includes(d);
                            if (isOpen) {
                                if (overlay?.close) {
                                    overlay.close();
                                }
                                if (this.stack.includes(d)) {
                                    this._removeFromStack(d);
                                }
                            }
                        }
                    });
                }
                // Do not close side-nav-drawer.
            }
        } else {
            // On mobile, close all other open overlays when a drawer opens
            this.overlays.forEach((overlay, key) => {
                if (key !== name && ((overlay?.isOpen && overlay.isOpen()) || this.stack.includes(key))) {
                    if (overlay?.close) {
                        overlay.close();
                    }
                    if (this.stack.includes(key)) {
                        this._removeFromStack(key);
                    }
                }
            });
            for (const existing of [...this.stack]) {
                if (existing !== name) {
                    this._removeFromStack(existing);
                }
            }
        }

        this._removeFromStack(name);
        this.stack.push(name);
        this.activeOverlay = name;
    }

    /**
     * Called when an overlay is closing
     * @param {string} name - Name of the overlay being closed
     */
    onClose(name) {
        this._removeFromStack(name);
        if (this.activeOverlay === name || (this.activeOverlay && !this.stack.includes(this.activeOverlay))) {
            this.activeOverlay = this.stack.length > 0 ? this.stack[this.stack.length - 1] : null;
        }

        const triggerEl = this.triggerElements.get(name);
        this.triggerElements.delete(name);
        if (triggerEl && typeof triggerEl.focus === 'function' && this._isElementInDocument(triggerEl)) {
            try {
                triggerEl.focus();
            } catch {
                // Ignore focus errors in non-interactive environments
            }
        }
    }

    /**
     * Return the name of the top-most active overlay
     * @returns {string|null}
     */
    getTopOverlay() {
        return this.stack.length > 0 ? this.stack[this.stack.length - 1] : this.activeOverlay;
    }

    /**
     * Return a shallow copy of the current overlay stack
     * @returns {string[]}
     */
    getStack() {
        return [...this.stack];
    }

    /**
     * Close ONLY the top-most overlay on the stack without closing underlying drawers (UI-07)
     * @returns {string|null} Name of the closed overlay, or null if none was open
     */
    closeTop() {
        const topName = this.getTopOverlay();
        if (!topName) {
            return null;
        }
        const overlay = this.overlays.get(topName);
        if (overlay?.close) {
            overlay.close();
        }
        if (this.stack.includes(topName) || this.activeOverlay === topName) {
            this.onClose(topName);
        }
        return topName;
    }

    /**
     * Handle Escape keydown to close only the top-most overlay (UI-07)
     * @param {KeyboardEvent} event
     * @returns {boolean} True if an overlay was closed
     */
    handleKeyDown(event) {
        if (!event || event.key !== 'Escape' || event.defaultPrevented) {
            return false;
        }
        const topName = this.getTopOverlay();
        if (!topName) {
            return false;
        }
        if (
            topName === 'theme-drawer' &&
            typeof window !== 'undefined' &&
            window.themeDrawer &&
            window.themeDrawer.editingPreset !== null
        ) {
            return false;
        }
        this.closeTop();
        if (typeof event.preventDefault === 'function') {
            event.preventDefault();
        }
        if (typeof event.stopImmediatePropagation === 'function') {
            event.stopImmediatePropagation();
        }
        return true;
    }

    /**
     * Close the currently active (top-most) overlay
     */
    closeActive() {
        return this.closeTop();
    }

    /**
     * Close all registered overlays that are currently open
     */
    closeAll() {
        this.overlays.forEach((overlay, key) => {
            if (overlay?.close && ((overlay?.isOpen && overlay.isOpen()) || this.stack.includes(key))) {
                overlay.close();
            }
        });
        while (this.stack.length > 0) {
            this.onClose(this.stack[this.stack.length - 1]);
        }
        this.activeOverlay = null;
    }

    /**
     * Check if any overlay is currently open
     */
    hasActiveOverlay() {
        return this.activeOverlay !== null || this.stack.length > 0;
    }
}

// Create global instance
window.overlayManager = new OverlayManager();
