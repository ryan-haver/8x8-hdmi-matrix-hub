/**
 * OREI Matrix Control - Tooltip Component
 * Lightweight tooltips with positioning and delay
 */

class Tooltip {
    static activeTooltip = null;
    static showTimeout = null;
    static hideTimeout = null;
    
    /**
     * Initialize tooltips on elements with data-tooltip attribute
     */
    static init() {
        // Create tooltip element
        if (!document.getElementById('tooltip')) {
            const tooltip = document.createElement('div');
            tooltip.id = 'tooltip';
            tooltip.className = 'tooltip';
            tooltip.setAttribute('role', 'tooltip');
            document.body.appendChild(tooltip);
        }
        
        // Delegate events for dynamic content
        document.addEventListener('mouseenter', Tooltip.handleMouseEnter, true);
        document.addEventListener('mouseleave', Tooltip.handleMouseLeave, true);
        document.addEventListener('focus', Tooltip.handleFocus, true);
        document.addEventListener('blur', Tooltip.handleBlur, true);
    }

    /**
     * Handle mouse enter
     */
    static handleMouseEnter(e) {
        const target = e.target.closest('[data-tooltip]');
        if (target) {
            Tooltip.scheduleShow(target);
        }
    }

    /**
     * Handle mouse leave
     */
    static handleMouseLeave(e) {
        const target = e.target.closest('[data-tooltip]');
        if (target) {
            Tooltip.scheduleHide();
        }
    }

    /**
     * Handle focus (for keyboard accessibility)
     */
    static handleFocus(e) {
        const target = e.target.closest('[data-tooltip]');
        if (target) {
            Tooltip.show(target);
        }
    }

    /**
     * Handle blur
     */
    static handleBlur(e) {
        const target = e.target.closest('[data-tooltip]');
        if (target) {
            Tooltip.hide();
        }
    }

    /**
     * Schedule tooltip to show after delay
     */
    static scheduleShow(target) {
        clearTimeout(Tooltip.hideTimeout);
        clearTimeout(Tooltip.showTimeout);
        
        Tooltip.showTimeout = setTimeout(() => {
            Tooltip.show(target);
        }, 500);
    }

    /**
     * Schedule tooltip to hide after delay
     */
    static scheduleHide() {
        clearTimeout(Tooltip.showTimeout);
        clearTimeout(Tooltip.hideTimeout);
        
        Tooltip.hideTimeout = setTimeout(() => {
            Tooltip.hide();
        }, 100);
    }

    /**
     * Show tooltip for target element
     */
    static show(target) {
        const tooltip = document.getElementById('tooltip');
        if (!tooltip) return;
        
        const text = target.dataset.tooltip;
        if (!text) return;
        
        const position = target.dataset.tooltipPosition || 'top';
        
        tooltip.textContent = text;
        tooltip.className = `tooltip tooltip--${position}`;
        
        // Position tooltip
        Tooltip.position(tooltip, target, position);
        
        // Show
        requestAnimationFrame(() => {
            tooltip.classList.add('tooltip--visible');
        });
        
        Tooltip.activeTooltip = target;
    }

    /**
     * Position tooltip relative to target
     */
    static position(tooltip, target, position) {
        const rect = target.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        const gap = 8;
        
        let top, left;
        
        switch (position) {
            case 'top':
                top = rect.top - tooltipRect.height - gap;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'bottom':
                top = rect.bottom + gap;
                left = rect.left + (rect.width - tooltipRect.width) / 2;
                break;
            case 'left':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.left - tooltipRect.width - gap;
                break;
            case 'right':
                top = rect.top + (rect.height - tooltipRect.height) / 2;
                left = rect.right + gap;
                break;
        }
        
        // Keep within viewport
        const padding = 8;
        left = Math.max(padding, Math.min(left, window.innerWidth - tooltipRect.width - padding));
        top = Math.max(padding, Math.min(top, window.innerHeight - tooltipRect.height - padding));
        
        tooltip.style.top = `${top}px`;
        tooltip.style.left = `${left}px`;
    }

    /**
     * Hide tooltip
     */
    static hide() {
        const tooltip = document.getElementById('tooltip');
        if (tooltip) {
            tooltip.classList.remove('tooltip--visible');
        }
        Tooltip.activeTooltip = null;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => Tooltip.init());
} else {
    Tooltip.init();
}

// Export for use
window.Tooltip = Tooltip;
