/**
 * OREI Matrix Control - Floatable Utility
 * 
 * NOTE: This utility is currently NOT in use. The cec-tray.js, quick-actions-drawer.js,
 * and routing-drawer.js components each implement their own drag functionality inline.
 * This file is kept for potential future refactoring to consolidate the duplicate code
 * (~150 lines duplicated across 3 components). See TD-12 in PROJECT_ROADMAP.md.
 * 
 * Adds drag-to-float functionality to panels and drawers.
 * Supports pinned (stays open) and undocked (draggable) states.
 */

class Floatable {
    /**
     * Initialize floatable behavior for a panel
     * @param {Object} options Configuration options
     * @param {HTMLElement} options.panel - The panel element to make floatable
     * @param {string} options.storageKey - LocalStorage key for position persistence
     * @param {Function} options.onStateChange - Callback when pin/undock state changes
     * @param {boolean} options.hideOnMobile - Whether to hide dock buttons on mobile (default: true)
     */
    constructor(options) {
        this.panel = options.panel;
        this.storageKey = options.storageKey;
        this.onStateChange = options.onStateChange || (() => {});
        this.hideOnMobile = options.hideOnMobile !== false;
        
        this.isPinned = false;
        this.isUndocked = false;
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };
        
        // Load saved state
        this.loadState();
        
        // Bind methods
        this.onMouseDown = this.onMouseDown.bind(this);
        this.onMouseMove = this.onMouseMove.bind(this);
        this.onMouseUp = this.onMouseUp.bind(this);
        this.onTouchStart = this.onTouchStart.bind(this);
        this.onTouchMove = this.onTouchMove.bind(this);
        this.onTouchEnd = this.onTouchEnd.bind(this);
    }

    /**
     * Load saved state from localStorage
     */
    loadState() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            if (saved) {
                const data = JSON.parse(saved);
                this.isPinned = data.isPinned || false;
                this.isUndocked = data.isUndocked || false;
                this.savedPosition = data.position || null;
            }
        } catch (e) {
            console.warn('Failed to load floatable state:', e);
        }
    }

    /**
     * Save state to localStorage
     */
    saveState() {
        try {
            const data = {
                isPinned: this.isPinned,
                isUndocked: this.isUndocked,
                position: this.savedPosition
            };
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        } catch (e) {
            console.warn('Failed to save floatable state:', e);
        }
    }

    /**
     * Toggle pinned state (stays open but anchored)
     */
    togglePin() {
        if (window.innerWidth < 768 && this.hideOnMobile) {
            toast.info('Pin is only available on larger screens');
            return false;
        }
        
        this.isPinned = !this.isPinned;
        this.updatePanelClasses();
        this.saveState();
        this.onStateChange('pin', this.isPinned);
        return this.isPinned;
    }

    /**
     * Toggle undocked state (floating and draggable)
     */
    toggleUndock() {
        if (window.innerWidth < 768 && this.hideOnMobile) {
            toast.info('Undock is only available on larger screens');
            return false;
        }
        
        this.isUndocked = !this.isUndocked;
        
        if (this.isUndocked) {
            // Also pin when undocking
            this.isPinned = true;
            this.enableDragging();
            
            // Apply saved position if available
            if (this.savedPosition) {
                this.applyPosition(this.savedPosition);
            } else {
                // Center the panel initially
                this.centerPanel();
            }
        } else {
            // Re-dock: remove custom positioning
            this.disableDragging();
            this.panel.style.removeProperty('left');
            this.panel.style.removeProperty('top');
            this.panel.style.removeProperty('right');
            this.panel.style.removeProperty('bottom');
            this.panel.style.removeProperty('transform');
        }
        
        this.updatePanelClasses();
        this.saveState();
        this.onStateChange('undock', this.isUndocked);
        return this.isUndocked;
    }

    /**
     * Update CSS classes on the panel
     */
    updatePanelClasses() {
        this.panel.classList.toggle('floatable-pinned', this.isPinned);
        this.panel.classList.toggle('floatable-undocked', this.isUndocked);
    }

    /**
     * Apply saved position to panel
     */
    applyPosition(pos) {
        // Ensure position is within viewport
        const rect = this.panel.getBoundingClientRect();
        const maxX = window.innerWidth - 50;
        const maxY = window.innerHeight - 50;
        
        const x = Math.max(0, Math.min(pos.x, maxX));
        const y = Math.max(0, Math.min(pos.y, maxY));
        
        this.panel.style.position = 'fixed';
        this.panel.style.left = `${x}px`;
        this.panel.style.top = `${y}px`;
        this.panel.style.right = 'auto';
        this.panel.style.bottom = 'auto';
        this.panel.style.transform = 'none';
    }

    /**
     * Center panel in viewport
     */
    centerPanel() {
        const rect = this.panel.getBoundingClientRect();
        const x = (window.innerWidth - rect.width) / 2;
        const y = (window.innerHeight - rect.height) / 2;
        
        this.savedPosition = { x, y };
        this.applyPosition(this.savedPosition);
    }

    /**
     * Enable drag functionality
     */
    enableDragging() {
        const header = this.panel.querySelector('.drawer-header, .cec-tray-header, .floatable-header');
        if (header) {
            header.style.cursor = 'grab';
            header.addEventListener('mousedown', this.onMouseDown);
            header.addEventListener('touchstart', this.onTouchStart, { passive: false });
        }
    }

    /**
     * Disable drag functionality
     */
    disableDragging() {
        const header = this.panel.querySelector('.drawer-header, .cec-tray-header, .floatable-header');
        if (header) {
            header.style.cursor = '';
            header.removeEventListener('mousedown', this.onMouseDown);
            header.removeEventListener('touchstart', this.onTouchStart);
        }
        document.removeEventListener('mousemove', this.onMouseMove);
        document.removeEventListener('mouseup', this.onMouseUp);
        document.removeEventListener('touchmove', this.onTouchMove);
        document.removeEventListener('touchend', this.onTouchEnd);
    }

    /**
     * Mouse down handler - start dragging
     */
    onMouseDown(e) {
        // Don't drag if clicking on buttons
        if (e.target.closest('button')) return;
        
        e.preventDefault();
        this.startDrag(e.clientX, e.clientY);
        
        document.addEventListener('mousemove', this.onMouseMove);
        document.addEventListener('mouseup', this.onMouseUp);
    }

    /**
     * Mouse move handler - dragging
     */
    onMouseMove(e) {
        if (!this.isDragging) return;
        e.preventDefault();
        this.drag(e.clientX, e.clientY);
    }

    /**
     * Mouse up handler - stop dragging
     */
    onMouseUp() {
        this.endDrag();
        document.removeEventListener('mousemove', this.onMouseMove);
        document.removeEventListener('mouseup', this.onMouseUp);
    }

    /**
     * Touch start handler
     */
    onTouchStart(e) {
        if (e.target.closest('button')) return;
        if (e.touches.length !== 1) return;
        
        e.preventDefault();
        const touch = e.touches[0];
        this.startDrag(touch.clientX, touch.clientY);
        
        document.addEventListener('touchmove', this.onTouchMove, { passive: false });
        document.addEventListener('touchend', this.onTouchEnd);
    }

    /**
     * Touch move handler
     */
    onTouchMove(e) {
        if (!this.isDragging) return;
        if (e.touches.length !== 1) return;
        
        e.preventDefault();
        const touch = e.touches[0];
        this.drag(touch.clientX, touch.clientY);
    }

    /**
     * Touch end handler
     */
    onTouchEnd() {
        this.endDrag();
        document.removeEventListener('touchmove', this.onTouchMove);
        document.removeEventListener('touchend', this.onTouchEnd);
    }

    /**
     * Start drag operation
     */
    startDrag(x, y) {
        const rect = this.panel.getBoundingClientRect();
        this.dragOffset = {
            x: x - rect.left,
            y: y - rect.top
        };
        this.isDragging = true;
        this.panel.classList.add('floatable-dragging');
        
        const header = this.panel.querySelector('.drawer-header, .cec-tray-header, .floatable-header');
        if (header) header.style.cursor = 'grabbing';
    }

    /**
     * During drag operation
     */
    drag(x, y) {
        const newX = x - this.dragOffset.x;
        const newY = y - this.dragOffset.y;
        
        // Keep within viewport bounds
        const rect = this.panel.getBoundingClientRect();
        const maxX = window.innerWidth - rect.width;
        const maxY = window.innerHeight - rect.height;
        
        const clampedX = Math.max(0, Math.min(newX, maxX));
        const clampedY = Math.max(0, Math.min(newY, maxY));
        
        this.panel.style.left = `${clampedX}px`;
        this.panel.style.top = `${clampedY}px`;
        this.panel.style.right = 'auto';
        this.panel.style.bottom = 'auto';
        this.panel.style.transform = 'none';
    }

    /**
     * End drag operation
     */
    endDrag() {
        if (!this.isDragging) return;
        
        this.isDragging = false;
        this.panel.classList.remove('floatable-dragging');
        
        const header = this.panel.querySelector('.drawer-header, .cec-tray-header, .floatable-header');
        if (header) header.style.cursor = 'grab';
        
        // Save position
        const rect = this.panel.getBoundingClientRect();
        this.savedPosition = { x: rect.left, y: rect.top };
        this.saveState();
    }

    /**
     * Apply initial state (call after panel is visible)
     */
    applyInitialState() {
        if (this.isUndocked) {
            this.enableDragging();
            if (this.savedPosition) {
                this.applyPosition(this.savedPosition);
            }
        }
        this.updatePanelClasses();
    }

    /**
     * Reset to docked state
     */
    reset() {
        this.isPinned = false;
        this.isUndocked = false;
        this.savedPosition = null;
        this.disableDragging();
        this.panel.style.removeProperty('left');
        this.panel.style.removeProperty('top');
        this.panel.style.removeProperty('right');
        this.panel.style.removeProperty('bottom');
        this.panel.style.removeProperty('transform');
        this.panel.style.removeProperty('position');
        this.updatePanelClasses();
        this.saveState();
    }

    /**
     * Create pin/undock button HTML
     * @param {boolean} showPin - Whether to show pin button
     * @param {boolean} showUndock - Whether to show undock button  
     */
    static createButtons(showPin = true, showUndock = true) {
        let html = '';
        
        if (showPin) {
            html += `
                <button class="floatable-pin-btn desktop-only" title="Pin panel open">
                    <svg class="icon pin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 17v5"/>
                        <path d="M9 11V6a3 3 0 0 1 6 0v5"/>
                        <path d="M5 11h14l-1.5 6h-11L5 11z"/>
                    </svg>
                </button>
            `;
        }
        
        if (showUndock) {
            html += `
                <button class="floatable-undock-btn desktop-only" title="Undock and float">
                    <svg class="icon undock-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2"/>
                        <path d="M9 3v18"/>
                        <path d="M14 9l3 3-3 3"/>
                    </svg>
                    <svg class="icon dock-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none;">
                        <rect x="3" y="3" width="18" height="18" rx="2"/>
                        <path d="M9 3v18"/>
                        <path d="M17 9l-3 3 3 3"/>
                    </svg>
                </button>
            `;
        }
        
        return html;
    }

    /**
     * Update button icons based on state
     */
    updateButtonIcons() {
        const pinBtn = this.panel.querySelector('.floatable-pin-btn');
        const undockBtn = this.panel.querySelector('.floatable-undock-btn');
        
        if (pinBtn) {
            pinBtn.classList.toggle('active', this.isPinned && !this.isUndocked);
            pinBtn.title = this.isPinned ? 'Unpin panel' : 'Pin panel open';
        }
        
        if (undockBtn) {
            const undockIcon = undockBtn.querySelector('.undock-icon');
            const dockIcon = undockBtn.querySelector('.dock-icon');
            
            if (this.isUndocked) {
                undockBtn.classList.add('active');
                undockBtn.title = 'Dock panel';
                if (undockIcon) undockIcon.style.display = 'none';
                if (dockIcon) dockIcon.style.display = '';
            } else {
                undockBtn.classList.remove('active');
                undockBtn.title = 'Undock and float';
                if (undockIcon) undockIcon.style.display = '';
                if (dockIcon) dockIcon.style.display = 'none';
            }
        }
    }
}

// Export for use
window.Floatable = Floatable;
