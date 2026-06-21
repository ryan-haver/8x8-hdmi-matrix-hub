/**
 * OREI Matrix Control - Overlay Manager
 * Ensures only one modal/drawer/dropdown is open at a time
 */

class OverlayManager {
    constructor() {
        this.activeOverlay = null;
        this.overlays = new Map();
    }

    /**
     * Register an overlay component
     * @param {string} name - Unique identifier for the overlay
     * @param {Object} options - { open: Function, close: Function, isOpen: () => boolean }
     */
    register(name, options) {
        this.overlays.set(name, options);
    }

    /**
     * Called when an overlay is opening
     * Closes any other open overlay first (with viewport-aware bypass for desktop side nav)
     * @param {string} name - Name of the overlay being opened
     */
    onOpen(name) {
        const isDesktop = window.innerWidth >= 768;

        if (isDesktop) {
            // On desktop/tablet, we allow the side nav drawer (Control Deck) to coexist with one right-side drawer.
            if (name === 'side-nav-drawer') {
                // Opening side-nav-drawer: do not close any right-side drawer.
            } else {
                // Opening a right-side drawer: close other right-side drawers to avoid overlays on the right.
                const rightSideDrawers = [
                    'quick-actions-drawer',
                    'routing-drawer',
                    'theme-drawer',
                    'general-drawer',
                    'hardware-drawer',
                    'interface-drawer',
                    'shortcuts-drawer',
                    'presets-drawer',
                ];
                if (rightSideDrawers.includes(name)) {
                    rightSideDrawers.forEach(d => {
                        if (d !== name) {
                            const overlay = this.overlays.get(d);
                            if (overlay?.isOpen && overlay.isOpen()) {
                                overlay.close();
                            }
                        }
                    });
                }
                // Do not close side-nav-drawer.
            }
        } else {
            // On mobile, close all other open overlays
            this.overlays.forEach((overlay, key) => {
                if (key !== name && overlay?.isOpen && overlay.isOpen()) {
                    overlay.close();
                }
            });
        }
        this.activeOverlay = name;
    }

    /**
     * Called when an overlay is closing
     * @param {string} name - Name of the overlay being closed
     */
    onClose(name) {
        if (this.activeOverlay === name) {
            this.activeOverlay = null;
        }
    }

    /**
     * Close the currently active overlay
     */
    closeActive() {
        if (this.activeOverlay) {
            const overlay = this.overlays.get(this.activeOverlay);
            if (overlay?.close) {
                overlay.close();
            }
            this.activeOverlay = null;
        }
    }

    /**
     * Close all registered overlays that are currently open
     */
    closeAll() {
        this.overlays.forEach(overlay => {
            if (overlay?.close && overlay?.isOpen && overlay.isOpen()) {
                overlay.close();
            }
        });
        this.activeOverlay = null;
    }

    /**
     * Check if any overlay is currently open
     */
    hasActiveOverlay() {
        return this.activeOverlay !== null;
    }
}

// Create global instance
window.overlayManager = new OverlayManager();
