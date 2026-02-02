/**
 * OREI Matrix Control - Toast Notifications
 */

class Toast {
    constructor() {
        this.container = document.getElementById('toast-container');
        this.toasts = [];
        this.defaultDuration = 3000;
    }

    /**
     * Show a toast notification
     * @param {string} message - Message to display
     * @param {string} type - Toast type: 'success', 'error', 'warning', 'info'
     * @param {number} duration - Duration in ms (0 for persistent)
     */
    show(message, type = 'info', duration = this.defaultDuration) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = this.getIcon(type);
        
        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-message">${Helpers.escapeHtml(message)}</span>
            <button class="toast-close" aria-label="Dismiss">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
        `;

        // Close button handler
        toast.querySelector('.toast-close').addEventListener('click', () => {
            this.dismiss(toast);
        });

        // Click to dismiss
        toast.addEventListener('click', (e) => {
            if (e.target.closest('.toast-close')) return;
            this.dismiss(toast);
        });

        this.container.appendChild(toast);
        this.toasts.push(toast);

        // Auto dismiss
        if (duration > 0) {
            setTimeout(() => {
                this.dismiss(toast);
            }, duration);
        }

        return toast;
    }

    /**
     * Dismiss a toast
     */
    dismiss(toast) {
        if (!toast || !toast.parentNode) return;
        
        toast.classList.add('toast-out');
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
            this.toasts = this.toasts.filter(t => t !== toast);
        }, 200);
    }

    /**
     * Dismiss all toasts
     */
    dismissAll() {
        this.toasts.forEach(toast => this.dismiss(toast));
    }

    /**
     * Success toast
     */
    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    /**
     * Error toast
     */
    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    /**
     * Warning toast
     */
    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    /**
     * Info toast
     */
    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    /**
     * Get icon SVG for toast type
     */
    getIcon(type) {
        const icons = {
            success: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>`,
            error: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>`,
            warning: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>`,
            info: `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
            </svg>`
        };
        return icons[type] || icons.info;
    }

}

// Create global toast instance
window.toast = new Toast();
