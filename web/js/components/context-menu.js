/**
 * OREI Matrix Control - Context Menu Component
 * Reusable right-click context menus for various elements
 */

class ContextMenu {
    /**
     * Create a context menu
     * @param {Object} options - Configuration options
     * @param {Array} options.items - Menu items [{label, icon, action, disabled, divider}]
     * @param {HTMLElement} options.target - Target element that triggers the menu
     */
    constructor(options = {}) {
        this.items = options.items || [];
        this.element = null;
        this.isOpen = false;
    }

    /**
     * Render menu HTML
     */
    render() {
        const itemsHtml = this.items.map((item, index) => {
            if (item.divider) {
                return '<div class="context-menu__divider"></div>';
            }
            
            const disabledClass = item.disabled ? 'context-menu__item--disabled' : '';
            const dangerClass = item.danger ? 'context-menu__item--danger' : '';
            
            return `
                <button class="context-menu__item ${disabledClass} ${dangerClass}" 
                        data-action="${index}"
                        ${item.disabled ? 'disabled' : ''}>
                    ${item.icon ? `<span class="context-menu__icon">${item.icon}</span>` : ''}
                    <span class="context-menu__label">${item.label}</span>
                    ${item.shortcut ? `<span class="context-menu__shortcut">${item.shortcut}</span>` : ''}
                </button>
            `;
        }).join('');

        return `
            <div class="context-menu glass-heavy" role="menu">
                ${itemsHtml}
            </div>
        `;
    }

    /**
     * Show menu at position
     * @param {number} x - X position
     * @param {number} y - Y position
     */
    show(x, y) {
        // Close any existing menu
        ContextMenu.closeAll();
        
        // Create and mount menu
        const wrapper = document.createElement('div');
        wrapper.innerHTML = this.render();
        this.element = wrapper.firstElementChild;
        document.body.appendChild(this.element);
        
        // Position menu, adjusting for screen edges
        const rect = this.element.getBoundingClientRect();
        const maxX = window.innerWidth - rect.width - 8;
        const maxY = window.innerHeight - rect.height - 8;
        
        this.element.style.left = `${Math.min(x, maxX)}px`;
        this.element.style.top = `${Math.min(y, maxY)}px`;
        
        // Animate in
        requestAnimationFrame(() => {
            this.element.classList.add('context-menu--visible');
        });
        
        this.isOpen = true;
        
        // Setup event listeners
        this.bindEvents();
        
        // Track open menu
        ContextMenu._openMenu = this;
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Item clicks
        this.element.querySelectorAll('.context-menu__item').forEach(item => {
            item.addEventListener('click', (e) => {
                const index = parseInt(e.currentTarget.dataset.action);
                const menuItem = this.items[index];
                
                if (menuItem && !menuItem.disabled && menuItem.action) {
                    menuItem.action();
                }
                
                this.close();
            });
        });
        
        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', this.handleOutsideClick);
            document.addEventListener('contextmenu', this.handleOutsideClick);
        }, 10);
        
        // Close on escape
        document.addEventListener('keydown', this.handleKeydown);
    }

    /**
     * Handle outside click
     */
    handleOutsideClick = (e) => {
        if (this.element && !this.element.contains(e.target)) {
            this.close();
        }
    };

    /**
     * Handle keydown
     */
    handleKeydown = (e) => {
        if (e.key === 'Escape') {
            this.close();
        }
    };

    /**
     * Close the menu
     */
    close() {
        if (!this.element || !this.isOpen) return;
        
        document.removeEventListener('click', this.handleOutsideClick);
        document.removeEventListener('contextmenu', this.handleOutsideClick);
        document.removeEventListener('keydown', this.handleKeydown);
        
        this.element.classList.remove('context-menu--visible');
        this.element.classList.add('context-menu--closing');
        
        setTimeout(() => {
            this.element?.remove();
            this.element = null;
        }, 150);
        
        this.isOpen = false;
        ContextMenu._openMenu = null;
    }

    /**
     * Close any open menu
     */
    static closeAll() {
        if (ContextMenu._openMenu) {
            ContextMenu._openMenu.close();
        }
    }

    /**
     * Static reference to open menu
     */
    static _openMenu = null;

    /**
     * Create profile context menu
     * @param {Object} profile - Profile object
     * @param {Object} callbacks - Callback functions {onEdit, onDuplicate, onExport, onDelete}
     */
    static forProfile(profile, callbacks = {}) {
        return new ContextMenu({
            items: [
                {
                    label: 'Edit',
                    icon: '✏️',
                    action: () => callbacks.onEdit?.(profile)
                },
                {
                    label: 'Duplicate',
                    icon: '📋',
                    action: () => callbacks.onDuplicate?.(profile)
                },
                {
                    label: 'Export',
                    icon: '📤',
                    action: () => callbacks.onExport?.(profile)
                },
                { divider: true },
                {
                    label: 'Delete',
                    icon: '🗑️',
                    danger: true,
                    action: () => callbacks.onDelete?.(profile)
                }
            ]
        });
    }

    /**
     * Create input context menu
     * @param {Object} input - Input object
     * @param {Object} callbacks - Callback functions
     */
    static forInput(input, callbacks = {}) {
        return new ContextMenu({
            items: [
                {
                    label: 'Settings',
                    icon: '⚙️',
                    action: () => callbacks.onSettings?.(input)
                },
                {
                    label: 'Rename',
                    icon: '✏️',
                    action: () => callbacks.onRename?.(input)
                },
                { divider: true },
                {
                    label: 'Route to all outputs',
                    icon: '📺',
                    action: () => callbacks.onRouteAll?.(input)
                }
            ]
        });
    }

    /**
     * Create output context menu
     * @param {Object} output - Output object
     * @param {Object} callbacks - Callback functions
     */
    static forOutput(output, callbacks = {}) {
        return new ContextMenu({
            items: [
                {
                    label: 'Settings',
                    icon: '⚙️',
                    action: () => callbacks.onSettings?.(output)
                },
                {
                    label: 'Rename',
                    icon: '✏️',
                    action: () => callbacks.onRename?.(output)
                },
                { divider: true },
                {
                    label: 'Power On',
                    icon: '🔌',
                    action: () => callbacks.onPowerOn?.(output)
                },
                {
                    label: 'Power Off',
                    icon: '⏻',
                    action: () => callbacks.onPowerOff?.(output)
                }
            ]
        });
    }
}

// Export for use
window.ContextMenu = ContextMenu;
