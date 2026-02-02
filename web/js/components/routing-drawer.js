/**
 * OREI Matrix Control - Route All Drawer Component
 * Slide-out drawer with quick one-click routing of any input to all outputs
 * Also supports dashboard widget mode for pinned inline display
 */

class RouteAllDrawer {
    constructor() {
        this.isOpen = false;
        this.container = null;
        this.backdrop = null;
        
        // Subscribe to state changes for input names
        state.on('inputs', () => this.onStateChange());
        state.on('routing', () => this.onStateChange());
        
        // Create drawer elements
        this.createDrawer();
        
        // Register as dashboard widget
        this.registerAsWidget();
    }

    /**
     * Handle state changes - update drawer and widget
     */
    onStateChange() {
        this.render();
        // Also refresh widget if pinned to dashboard
        if (window.dashboardManager && window.dashboardManager.isWidgetPinned('routing-dashboard')) {
            window.dashboardManager.refreshWidget('routing-dashboard');
        }
    }

    /**
     * Register as a dashboard widget
     */
    registerAsWidget() {
        if (typeof window.dashboardManager !== 'undefined') {
            window.dashboardManager.registerWidget({
                id: 'routing-dashboard',
                name: 'Routing',
                icon: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"/>
                    <line x1="12" y1="22" x2="12" y2="15.5"/>
                    <polyline points="22 8.5 12 15.5 2 8.5"/>
                </svg>`,
                render: () => this.renderWidgetContent(),
                onMount: (el) => this.attachWidgetEventListeners(el),
                onUnmount: () => {},
                component: this
            });
        }
    }

    /**
     * Render content for the dashboard widget
     */
    renderWidgetContent() {
        const currentAllRouted = this.getCurrentAllRouted();
        
        let html = `<div class="routing-grid">`;
        
        for (let i = 1; i <= state.info.inputCount; i++) {
            const name = state.getInputName(i);
            const input = state.inputs[i] || {};
            const hasSignal = input.signalActive;
            const sourceDetected = input.cableConnected;
            const isActive = currentAllRouted === i;
            
            let statusClass = 'status-disconnected';
            if (hasSignal) {
                statusClass = 'status-signal';
            } else if (sourceDetected === true) {
                statusClass = 'status-cable';
            } else if (sourceDetected === null) {
                statusClass = 'status-unknown';
            }
            
            html += `
                <button class="routing-btn ${isActive ? 'active' : ''} ${statusClass}" 
                        data-input="${i}"
                        title="${isActive ? 'Currently active on all outputs' : `Route ${name} to all outputs`}">
                    <span class="input-number">${i}</span>
                    <span class="input-name">${Helpers.escapeHtml(name)}</span>
                </button>
            `;
        }
        
        html += `</div>`;
        return html;
    }

    /**
     * Attach event listeners to widget buttons
     */
    attachWidgetEventListeners(widgetEl) {
        if (!widgetEl) return;
        
        widgetEl.querySelectorAll('.routing-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const input = parseInt(e.currentTarget.dataset.input);
                this.routeToAll(input);
            });
        });
    }

    /**
     * Check if Route All is pinned to dashboard (visible on mobile)
     */
    isPinnedToDashboard() {
        return window.dashboardManager && window.dashboardManager.isWidgetPinned('routing-dashboard');
    }

    /**
     * Toggle dashboard pin state (pin on desktop, hide on mobile)
     */
    toggleDashboardPin() {
        if (window.dashboardManager) {
            if (this.isPinnedToDashboard()) {
                // Already pinned/visible - unpin/hide it
                window.dashboardManager.unpinWidget('routing-dashboard');
            } else {
                // Not pinned/visible - pin/show it
                if (window.dashboardManager.pinWidget('routing-dashboard')) {
                    this.close();
                }
            }
        }
    }

    /**
     * Initialize the component
     */
    init() {
        this.render();
    }

    /**
     * Create the drawer DOM elements
     */
    createDrawer() {
        // Backdrop
        const backdrop = document.createElement('div');
        backdrop.id = 'routing-backdrop';
        backdrop.className = 'routing-backdrop';
        backdrop.addEventListener('click', () => this.close());
        document.body.appendChild(backdrop);
        
        // Drawer
        const drawer = document.createElement('aside');
        drawer.id = 'routing-drawer';
        drawer.className = 'routing-drawer';
        drawer.innerHTML = `
            <div class="drawer-header">
                <h3>
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"/>
                        <line x1="12" y1="22" x2="12" y2="15.5"/>
                        <polyline points="22 8.5 12 15.5 2 8.5"/>
                    </svg>
                    Routing
                </h3>
                <div class="drawer-header-actions">
                    <button class="btn-icon drawer-pin-dashboard-btn" title="Pin to dashboard">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2"/>
                            <line x1="9" y1="3" x2="9" y2="21"/>
                            <line x1="15" y1="3" x2="15" y2="21"/>
                            <line x1="3" y1="9" x2="21" y2="9"/>
                            <line x1="3" y1="15" x2="21" y2="15"/>
                        </svg>
                    </button>
                    <button class="btn-icon drawer-close" aria-label="Close drawer">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="drawer-content" id="routing-content">
                <!-- Content rendered dynamically -->
            </div>
        `;
        document.body.appendChild(drawer);
        
        this.container = drawer;
        this.backdrop = backdrop;
        
        // Close button
        drawer.querySelector('.drawer-close').addEventListener('click', () => this.close());
        
        // Pin to dashboard button (toggles pin state)
        drawer.querySelector('.drawer-pin-dashboard-btn')?.addEventListener('click', () => this.toggleDashboardPin());
        
        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });

    }

    /**
     * Update the dashboard pin button to show correct state
     */
    updateDashboardButton() {
        const btn = this.container?.querySelector('.drawer-pin-dashboard-btn');
        if (!btn) return;
        
        const isPinned = this.isPinnedToDashboard();
        if (isPinned) {
            btn.title = 'Hide from tabs';
            btn.innerHTML = `
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <line x1="5" y1="5" x2="19" y2="19"/>
                </svg>
            `;
        } else {
            btn.title = 'Pin to dashboard';
            btn.innerHTML = `
                <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <line x1="9" y1="3" x2="9" y2="21"/>
                    <line x1="15" y1="3" x2="15" y2="21"/>
                    <line x1="3" y1="9" x2="21" y2="9"/>
                    <line x1="3" y1="15" x2="21" y2="15"/>
                </svg>
            `;
        }
    }

    /**
     * Open the drawer
     */
    open() {
        Logger.log('RouteAllDrawer: Opening drawer');
        this.isOpen = true;
        this.container.classList.add('open');
        this.backdrop.classList.add('open');
        document.body.style.overflow = 'hidden';
        this.updateDashboardButton();
        this.render();
    }

    /**
     * Close the drawer
     */
    close() {
        this.isOpen = false;
        this.container.classList.remove('open');
        this.backdrop.classList.remove('open');
        document.body.style.overflow = '';
    }

    /**
     * Toggle drawer open/closed
     */
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Route an input to all outputs
     */
    async routeToAll(input) {

        Logger.log('RouteAllDrawer: routeToAll called with input:', input);
        
        // Find and mark the clicked button as loading
        const btn = document.querySelector(`.routing-btn[data-input="${input}"]`);
        if (btn) {
            btn.classList.add('loading');
        }
        
        try {
            const inputName = state.getInputName(input);
            Logger.log('RouteAllDrawer: Calling api.switchAll for', inputName);
            
            // Optimistically update routing for all outputs
            const optimisticRouting = {};
            for (let o = 1; o <= state.info.outputCount; o++) {
                optimisticRouting[o] = input;
            }
            state.setRouting(optimisticRouting);
            
            // Make the API call
            await api.switchAll(input);
            toast.success(`Routed ${inputName} to all outputs`);
            this.close();
            
            // Verify with fresh status from matrix
            setTimeout(async () => {
                try {
                    const data = await api.getStatus();
                    if (data.success && data.data.routing) {
                        state.setRouting(data.data.routing);
                    }
                } catch (e) {
                    console.warn('Failed to refresh status:', e);
                }
            }, 300);
        } catch (err) {
            console.error('Failed to route all:', err);
            toast.error(`Failed to route all: ${err.message || err}`);
            
            // Revert - refresh actual state from matrix
            try {
                const data = await api.getStatus();
                if (data.success && data.data.routing) {
                    state.setRouting(data.data.routing);
                }
            } catch (e) {
                console.warn('Failed to refresh status after error:', e);
            }
        } finally {
            // Remove loading state
            if (btn) {
                btn.classList.remove('loading');
            }
        }
    }

    /**
     * Determine which input is currently routed to all outputs (if any)
     */
    getCurrentAllRouted() {
        const routing = state.routing;
        if (!routing || Object.keys(routing).length === 0) return null;
        
        const firstInput = routing[1];
        if (!firstInput) return null;
        
        for (let o = 1; o <= state.info.outputCount; o++) {
            if (routing[o] !== firstInput) return null;
        }
        
        return firstInput;
    }

    /**
     * Render the drawer content
     */
    render() {
        const content = document.getElementById('routing-content');
        if (!content) return;
        
        const currentAllRouted = this.getCurrentAllRouted();
        
        let html = `
            <p class="routing-description">
                Tap an input to route it to <strong>all ${state.info.outputCount} outputs</strong> simultaneously.
            </p>
            <div class="routing-grid">
        `;
        
        for (let i = 1; i <= state.info.inputCount; i++) {
            const name = state.getInputName(i);
            const input = state.inputs[i] || {};
            const hasSignal = input.signalActive;
            // sourceDetected = HPD/5V from source device
            const sourceDetected = input.cableConnected;
            const isActive = currentAllRouted === i;
            
            // Status: signal (green) > source detected (orange) > off (red)
            let statusClass = 'status-disconnected';
            if (hasSignal) {
                statusClass = 'status-signal';
            } else if (sourceDetected === true) {
                statusClass = 'status-cable';
            } else if (sourceDetected === null) {
                statusClass = 'status-unknown';
            }
            
            html += `
                <button class="routing-btn ${isActive ? 'active' : ''} ${statusClass}" 
                        data-input="${i}"
                        title="${isActive ? 'Currently active on all outputs' : `Route ${name} to all outputs`}">
                    <div class="routing-btn-number">${i}</div>
                    <div class="routing-btn-name">${Helpers.escapeHtml(name)}</div>
                    ${isActive ? '<div class="routing-active-badge">●</div>' : ''}
                </button>
            `;
        }
        
        html += `
            </div>
        `;
        
        content.innerHTML = html;
        this.attachEventListeners();
    }

    /**
     * Attach event listeners to buttons
     */
    attachEventListeners() {
        const content = document.getElementById('routing-content');
        if (!content) {
            console.error('RouteAllDrawer: routing-content not found');
            return;
        }
        
        const buttons = content.querySelectorAll('.routing-btn');
        Logger.log('RouteAllDrawer: Attaching listeners to', buttons.length, 'buttons');
        
        buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                Logger.log('RouteAllDrawer: Button clicked, input:', e.currentTarget.dataset.input);
                const input = parseInt(e.currentTarget.dataset.input);
                this.routeToAll(input);
            });
        });
    }

}
