/**
 * OREI Matrix Control - Focus Trap Utility
 *
 * Provides accessible focus trapping for modal dialogs.
 * When a modal is open, Tab/Shift+Tab should cycle within the modal.
 * Escape should close the modal (caller provides handler).
 *
 * Usage:
 *   const trap = new FocusTrap(modalElement, () => closeModal());
 *   trap.activate();
 *   // later:
 *   trap.deactivate();
 */
class FocusTrap {
    /**
     * Create a focus trap for a modal element.
     * @param {HTMLElement} modal - The modal element to trap focus within
     * @param {Function} onEscape - Optional callback when Escape is pressed
     */
    constructor(modal, onEscape = null) {
        this.modal = modal;
        this.onEscape = onEscape;
        this.previousActiveElement = null;
        this.isActive = false;
        this.boundHandleKeyDown = this.handleKeyDown.bind(this);
    }

    /**
     * Get all focusable elements within the modal.
     * @returns {HTMLElement[]} Array of focusable elements
     */
    getFocusableElements() {
        if (!this.modal) return [];

        const selector = [
            'a[href]',
            'button:not([disabled])',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            '[tabindex]:not([tabindex="-1"])',
            'audio[controls]',
            'video[controls]',
        ].join(',');

        return Array.from(this.modal.querySelectorAll(selector)).filter((el) => {
            // Check if element is visible
            return el.offsetWidth > 0 || el.offsetHeight > 0 || el === document.activeElement;
        });
    }

    /**
     * Handle keydown events to trap focus.
     * @param {KeyboardEvent} event
     */
    handleKeyDown(event) {
        if (!this.isActive || !this.modal) return;

        if (event.key === 'Escape' && this.onEscape) {
            event.preventDefault();
            this.onEscape();
            return;
        }

        if (event.key !== 'Tab') return;

        const focusable = this.getFocusableElements();
        if (focusable.length === 0) {
            // No focusable elements, prevent tab navigation
            event.preventDefault();
            return;
        }

        const firstElement = focusable[0];
        const lastElement = focusable[focusable.length - 1];
        const activeElement = document.activeElement;

        // If Shift+Tab on first element, move to last
        if (event.shiftKey && activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
        }
        // If Tab on last element, move to first
        else if (!event.shiftKey && activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
        }
        // If focus has escaped the modal, restore it
        else if (!this.modal.contains(activeElement)) {
            event.preventDefault();
            firstElement.focus();
        }
    }

    /**
     * Activate the focus trap.
     * Stores current focus, focuses first element, and listens for keydown.
     */
    activate() {
        if (!this.modal || this.isActive) return;

        this.previousActiveElement = document.activeElement;
        this.isActive = true;
        document.addEventListener('keydown', this.boundHandleKeyDown);

        // Focus the first focusable element
        const focusable = this.getFocusableElements();
        if (focusable.length > 0) {
            // Slight delay to ensure modal is fully rendered
            setTimeout(() => focusable[0].focus(), 10);
        } else {
            // No focusable elements, focus the modal itself
            this.modal.setAttribute('tabindex', '-1');
            this.modal.focus();
        }
    }

    /**
     * Deactivate the focus trap.
     * Restores focus to the previously active element.
     */
    deactivate() {
        if (!this.isActive) return;

        this.isActive = false;
        document.removeEventListener('keydown', this.boundHandleKeyDown);

        // Restore focus to the element that opened the modal
        if (this.previousActiveElement && this.previousActiveElement.focus) {
            this.previousActiveElement.focus();
        }
    }
}

// Export for use
window.FocusTrap = FocusTrap;
