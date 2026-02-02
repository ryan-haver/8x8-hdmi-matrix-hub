/**
 * OREI Matrix Control - Confirm Dialog Component
 * Premium styled confirmation dialogs with glassmorphism
 */

class ConfirmDialog {
    /**
     * Create a confirm dialog
     * @param {Object} options - Configuration options
     * @param {string} options.title - Dialog title
     * @param {string} options.message - Confirmation message
     * @param {string} options.confirmText - Confirm button text (default: 'Confirm')
     * @param {string} options.cancelText - Cancel button text (default: 'Cancel')
     * @param {string} options.variant - Style variant: 'default', 'danger', 'warning'
     * @param {Function} options.onConfirm - Callback when confirmed
     * @param {Function} options.onCancel - Callback when cancelled
     */
    constructor(options = {}) {
        this.title = options.title || 'Confirm';
        this.message = options.message || 'Are you sure?';
        this.confirmText = options.confirmText || 'Confirm';
        this.cancelText = options.cancelText || 'Cancel';
        this.variant = options.variant || 'default';
        this.onConfirm = options.onConfirm || (() => {});
        this.onCancel = options.onCancel || (() => {});
        
        this.element = null;
        this.resolvePromise = null;
    }

    /**
     * Get variant-specific classes
     */
    getVariantClasses() {
        switch (this.variant) {
            case 'danger':
                return {
                    icon: `<svg class="confirm-dialog__icon confirm-dialog__icon--danger" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="15" y1="9" x2="9" y2="15"></line>
                        <line x1="9" y1="9" x2="15" y2="15"></line>
                    </svg>`,
                    confirmBtn: 'btn-danger'
                };
            case 'warning':
                return {
                    icon: `<svg class="confirm-dialog__icon confirm-dialog__icon--warning" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>`,
                    confirmBtn: 'btn-warning'
                };
            default:
                return {
                    icon: `<svg class="confirm-dialog__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12" y2="12"></line>
                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>`,
                    confirmBtn: 'btn-accent'
                };
        }
    }

    /**
     * Render dialog HTML
     */
    render() {
        const variant = this.getVariantClasses();
        
        return `
            <div class="confirm-dialog" role="alertdialog" aria-modal="true" aria-labelledby="confirm-title">
                <div class="confirm-dialog__backdrop"></div>
                <div class="confirm-dialog__content glass-heavy">
                    <div class="confirm-dialog__header">
                        ${variant.icon}
                        <h3 id="confirm-title" class="confirm-dialog__title">${this.title}</h3>
                    </div>
                    <p class="confirm-dialog__message">${this.message}</p>
                    <div class="confirm-dialog__actions">
                        <button class="btn btn-secondary confirm-dialog__cancel">${this.cancelText}</button>
                        <button class="btn ${variant.confirmBtn} confirm-dialog__confirm">${this.confirmText}</button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Show the dialog
     * @returns {Promise<boolean>} Resolves true if confirmed, false if cancelled
     */
    show() {
        return new Promise((resolve) => {
            this.resolvePromise = resolve;
            
            // Create and mount dialog
            const wrapper = document.createElement('div');
            wrapper.innerHTML = this.render();
            this.element = wrapper.firstElementChild;
            document.body.appendChild(this.element);
            
            // Animate in
            requestAnimationFrame(() => {
                this.element.classList.add('confirm-dialog--visible');
            });
            
            // Setup event listeners
            const confirmBtn = this.element.querySelector('.confirm-dialog__confirm');
            const cancelBtn = this.element.querySelector('.confirm-dialog__cancel');
            const backdrop = this.element.querySelector('.confirm-dialog__backdrop');
            
            confirmBtn.addEventListener('click', () => this.handleConfirm());
            cancelBtn.addEventListener('click', () => this.handleCancel());
            backdrop.addEventListener('click', () => this.handleCancel());
            
            // Keyboard support
            document.addEventListener('keydown', this.handleKeydown);
            
            // Focus confirm button
            confirmBtn.focus();
        });
    }

    /**
     * Handle keydown events
     */
    handleKeydown = (e) => {
        if (e.key === 'Escape') {
            this.handleCancel();
        } else if (e.key === 'Enter') {
            this.handleConfirm();
        }
    };

    /**
     * Handle confirm action
     */
    handleConfirm() {
        this.close();
        this.onConfirm();
        if (this.resolvePromise) {
            this.resolvePromise(true);
        }
    }

    /**
     * Handle cancel action
     */
    handleCancel() {
        this.close();
        this.onCancel();
        if (this.resolvePromise) {
            this.resolvePromise(false);
        }
    }

    /**
     * Close and cleanup dialog
     */
    close() {
        if (!this.element) return;
        
        document.removeEventListener('keydown', this.handleKeydown);
        
        this.element.classList.remove('confirm-dialog--visible');
        this.element.classList.add('confirm-dialog--closing');
        
        setTimeout(() => {
            this.element?.remove();
            this.element = null;
        }, 200);
    }

    /**
     * Static helper to show a confirm dialog
     * @param {Object} options - Dialog options
     * @returns {Promise<boolean>}
     */
    static async confirm(options) {
        const dialog = new ConfirmDialog(options);
        return dialog.show();
    }

    /**
     * Static helper for delete confirmations
     * @param {string} itemName - Name of item being deleted
     * @returns {Promise<boolean>}
     */
    static async confirmDelete(itemName) {
        return ConfirmDialog.confirm({
            title: 'Delete',
            message: `Are you sure you want to delete "${itemName}"? This action cannot be undone.`,
            confirmText: 'Delete',
            cancelText: 'Keep',
            variant: 'danger'
        });
    }
}

// Export for use
window.ConfirmDialog = ConfirmDialog;
