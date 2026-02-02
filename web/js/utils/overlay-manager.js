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
     * Closes any other open overlay first
     * @param {string} name - Name of the overlay being opened
     */
    onOpen(name) {
        // Close any other open overlay
        if (this.activeOverlay && this.activeOverlay !== name) {
            const previous = this.overlays.get(this.activeOverlay);
            if (previous?.close) {
                previous.close();
            }
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
     * Check if any overlay is currently open
     */
    hasActiveOverlay() {
        return this.activeOverlay !== null;
    }
}

// Create global instance
window.overlayManager = new OverlayManager();
