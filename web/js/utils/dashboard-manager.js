/**
 * OREI Matrix Control - Dashboard Manager
 * 
 * Manages pinnable widgets that can be added to the main grid layout.
 * 
 * Behavior by screen size:
 * - Mobile/Tablet (< 768px): Add widget tabs alongside standard tabs (horizontal scroll, all reorderable)
 * - Desktop (768px+): Show widgets in grid-based dashboard section, tabs hidden by CSS
 */

class DashboardManager {
    constructor() {
        // Registered widgets available for pinning
        this.registeredWidgets = new Map();
        
        // Currently pinned widgets (ordered array for positioning) - desktop only
        this.pinnedWidgets = new Set();
        
        // Hidden widgets on mobile (user explicitly unpinned) - mobile only
        this.hiddenMobileWidgets = new Set();
        
        // Widget order (array of widget IDs) - for desktop grid
        this.widgetOrder = [];
        
        // Unified tab order (both standard tab IDs and widget IDs) - for mobile/tablet
        // Standard tabs use 'tab:matrix', 'tab:inputs', etc. Widgets use 'widget:cec-remote', etc.
        this.unifiedTabOrder = [];
        
        // Default standard tabs in order
        this.defaultStandardTabs = ['tab:matrix', 'tab:inputs', 'tab:outputs', 'tab:scenes'];
        
        // Dashboard container element (desktop)
        this.container = null;
        
        // Mobile tabs container
        this.mobileTabsContainer = null;
        
        // Standard tabs (cached for DOM reference)
        this.standardTabsCache = new Map();
        
        // Active widget tab (mobile)
        this.activeWidgetTab = null;
        
        // Mobile widget content container
        this.mobileWidgetContent = null;
        
        // Drag state (desktop)
        this.dragState = {
            isDragging: false,
            draggedWidget: null,
            placeholder: null,
            startIndex: -1
        };
        
        // Mobile tab drag state
        this.tabDragState = {
            isDragging: false,
            draggedTab: null,
            startX: 0,
            startIndex: -1,
            tabType: null // 'standard' or 'widget'
        };
        
        // Breakpoints - match CSS media queries
        this.DESKTOP_MIN = 768;
        
        // Storage key
        this.storageKey = 'orei_dashboard_config';
        
        // Load saved configuration
        this.loadConfig();
    }

    /**
     * Initialize the dashboard
     */
    init() {
        this.initDashboardContainer();
        this.initMobileTabsContainer();
        this.restorePinnedWidgets();
        this.setupResizeHandler();
        this.setupContainerDragHandlers();
    }

    /**
     * Initialize the dashboard container (desktop - already exists in HTML)
     */
    initDashboardContainer() {
        this.container = document.getElementById('dashboard-widgets');
        this.updateDashboardVisibility();
    }

    /**
     * Initialize mobile tabs container
     */
    initMobileTabsContainer() {
        this.mobileTabsContainer = document.querySelector('.mobile-tabs');
        if (this.mobileTabsContainer) {
            // Cache standard tabs for reference
            this.cacheStandardTabs();
            // Initialize unified tab order if empty
            this.initializeUnifiedTabOrder();
        }
        
        // Create mobile widget content container (for showing widget content full screen)
        this.createMobileWidgetContentContainer();
    }

    /**
     * Cache the standard tabs (Matrix, Inputs, Outputs, Profiles)
     */
    cacheStandardTabs() {
        const tabs = this.mobileTabsContainer.querySelectorAll('.tab-btn:not(.tab-widget)');
        tabs.forEach(tab => {
            if (tab.dataset.tab && tab.dataset.tab !== 'dashboard') {
                this.standardTabsCache.set(`tab:${tab.dataset.tab}`, tab);
            }
        });
    }

    /**
     * Initialize unified tab order with defaults if not set
     */
    initializeUnifiedTabOrder() {
        if (this.unifiedTabOrder.length === 0) {
            // Start with default standard tabs
            this.unifiedTabOrder = [...this.defaultStandardTabs];
        }
        
        // Ensure all standard tabs are in the order
        this.defaultStandardTabs.forEach(tabId => {
            if (!this.unifiedTabOrder.includes(tabId)) {
                this.unifiedTabOrder.push(tabId);
            }
        });
        
        // Ensure all pinned widgets are in the order
        this.pinnedWidgets.forEach(widgetId => {
            const widgetTabId = `widget:${widgetId}`;
            if (!this.unifiedTabOrder.includes(widgetTabId)) {
                this.unifiedTabOrder.push(widgetTabId);
            }
        });
    }

    /**
     * Create mobile widget content container
     */
    createMobileWidgetContentContainer() {
        this.mobileWidgetContent = document.getElementById('mobile-widget-content');
        if (!this.mobileWidgetContent) {
            this.mobileWidgetContent = document.createElement('section');
            this.mobileWidgetContent.id = 'mobile-widget-content';
            this.mobileWidgetContent.className = 'section section-mobile-widget';
            this.mobileWidgetContent.innerHTML = '<div class="mobile-widget-inner"></div>';
            
            // Insert after main content sections
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                mainContent.appendChild(this.mobileWidgetContent);
            }
        }
    }

    /**
     * Register a widget that can be pinned to the dashboard
     */
    registerWidget(config) {
        this.registeredWidgets.set(config.id, {
            id: config.id,
            name: config.name,
            icon: config.icon || '',
            render: config.render,
            onMount: config.onMount || (() => {}),
            onUnmount: config.onUnmount || (() => {}),
            component: config.component || null
        });
        
        const mode = this.getViewportMode();
        
        if (mode === 'desktop') {
            // Desktop: Auto-pin on first load, otherwise respect saved config
            const hasNoSavedConfig = !localStorage.getItem(this.storageKey);
            const shouldPin = hasNoSavedConfig || this.pinnedWidgets.has(config.id);
            
            if (shouldPin) {
                // Add to pinned set if first load
                if (hasNoSavedConfig && !this.pinnedWidgets.has(config.id)) {
                    this.pinnedWidgets.add(config.id);
                    if (!this.widgetOrder.includes(config.id)) {
                        this.widgetOrder.push(config.id);
                    }
                    // Save config so next load respects user's unpinned choices
                    this.saveConfig();
                }
                this.renderWidget(config.id);
                this.notifyWidgetPinChange(config.id, true);
            }
            // Update visibility after registering
            this.updateDashboardVisibility();
        } else {
            // Mobile: All widgets appear as tabs unless explicitly hidden
            // Add to unified tab order if not already there and not hidden
            const widgetTabId = `widget:${config.id}`;
            if (!this.hiddenMobileWidgets.has(config.id) && !this.unifiedTabOrder.includes(widgetTabId)) {
                this.unifiedTabOrder.push(widgetTabId);
            }
            this.updateMobileTabs();
            // On mobile, widgets are always "pinned" (visible) unless hidden
            if (!this.hiddenMobileWidgets.has(config.id)) {
                this.notifyWidgetPinChange(config.id, true);
            }
        }
    }

    /**
     * Unregister a widget
     */
    unregisterWidget(widgetId) {
        if (this.pinnedWidgets.has(widgetId)) {
            this.unpinWidget(widgetId);
        }
        this.registeredWidgets.delete(widgetId);
    }

    /**
     * Get current viewport mode
     */
    getViewportMode() {
        const width = window.innerWidth;
        // Match CSS media query: tabs hidden at 768px+
        if (width >= this.DESKTOP_MIN) return 'desktop';
        return 'mobile';
    }

    /**
     * Pin a widget to the dashboard (desktop) or show it (mobile)
     */
    pinWidget(widgetId) {
        if (!this.registeredWidgets.has(widgetId)) {
            console.warn(`Widget "${widgetId}" not registered`);
            return false;
        }
        
        const mode = this.getViewportMode();
        const widget = this.registeredWidgets.get(widgetId);
        
        if (mode === 'mobile') {
            // Mobile: Remove from hidden set (show the tab)
            if (!this.hiddenMobileWidgets.has(widgetId)) {
                return false; // Already visible
            }
            this.hiddenMobileWidgets.delete(widgetId);
            
            // Add back to unified tab order
            const widgetTabId = `widget:${widgetId}`;
            if (!this.unifiedTabOrder.includes(widgetTabId)) {
                this.unifiedTabOrder.push(widgetTabId);
            }
        } else {
            // Desktop: Add to pinned set
            if (this.pinnedWidgets.has(widgetId)) {
                return false; // Already pinned
            }
            
            this.pinnedWidgets.add(widgetId);
            if (!this.widgetOrder.includes(widgetId)) {
                this.widgetOrder.push(widgetId);
            }
            
            // Add to unified tab order
            const widgetTabId = `widget:${widgetId}`;
            if (!this.unifiedTabOrder.includes(widgetTabId)) {
                this.unifiedTabOrder.push(widgetTabId);
            }
            
            this.renderWidget(widgetId);
        }
        
        this.saveConfig();
        this.updateDashboardVisibility();
        this.updateMobileTabs();
        
        // Notify widget about pin state
        this.notifyWidgetPinChange(widgetId, true);
        
        toast.success(`${widget.name} pinned to dashboard`);
        
        return true;
    }

    /**
     * Unpin a widget from the dashboard (desktop) or hide it (mobile)
     */
    unpinWidget(widgetId) {
        const mode = this.getViewportMode();
        const widget = this.registeredWidgets.get(widgetId);
        
        if (mode === 'mobile') {
            // Mobile: Add to hidden set (hide the tab)
            if (this.hiddenMobileWidgets.has(widgetId)) {
                return false; // Already hidden
            }
            this.hiddenMobileWidgets.add(widgetId);
            
            // Remove from unified tab order
            const widgetTabId = `widget:${widgetId}`;
            this.unifiedTabOrder = this.unifiedTabOrder.filter(id => id !== widgetTabId);
            
            // Clear active widget tab if this was it
            if (this.activeWidgetTab === widgetId) {
                this.activeWidgetTab = null;
                this.switchToStandardTab();
            }
        } else {
            // Desktop: Remove from pinned set
            if (!this.pinnedWidgets.has(widgetId)) {
                return false;
            }
            
            if (widget) {
                widget.onUnmount();
            }
            
            // Remove from desktop DOM
            const widgetEl = document.getElementById(`dashboard-widget-${widgetId}`);
            if (widgetEl) {
                widgetEl.remove();
            }
            
            this.pinnedWidgets.delete(widgetId);
            this.widgetOrder = this.widgetOrder.filter(id => id !== widgetId);
            
            // Remove from unified tab order
            const widgetTabId = `widget:${widgetId}`;
            this.unifiedTabOrder = this.unifiedTabOrder.filter(id => id !== widgetTabId);
            
            // Clear active widget tab if this was it
            if (this.activeWidgetTab === widgetId) {
                this.activeWidgetTab = null;
                this.switchToStandardTab();
            }
        }
        
        this.saveConfig();
        this.updateDashboardVisibility();
        this.updateMobileTabs();
        
        // Notify widget about unpin state
        this.notifyWidgetPinChange(widgetId, false);
        
        if (widget) {
            toast.success(`${widget.name} unpinned from dashboard`);
        }
        
        return true;
    }

    /**
     * Notify widget components about pin state change
     */
    notifyWidgetPinChange(widgetId, isPinned) {
        const widget = this.registeredWidgets.get(widgetId);
        if (widget && widget.component && typeof widget.component.onDashboardPinChange === 'function') {
            widget.component.onDashboardPinChange(isPinned);
        }
        
        // Dispatch custom event for any listeners
        document.dispatchEvent(new CustomEvent('dashboardPinChange', {
            detail: { widgetId, isPinned }
        }));
    }

    /**
     * Toggle widget pinned/visible state
     */
    toggleWidget(widgetId) {
        if (this.isWidgetPinned(widgetId)) {
            this.unpinWidget(widgetId);
            return false;
        } else {
            return this.pinWidget(widgetId);
        }
    }

    /**
     * Check if a widget is pinned (or visible on mobile)
     */
    isWidgetPinned(widgetId) {
        const mode = this.getViewportMode();
        if (mode === 'mobile') {
            // On mobile, widgets are "pinned" (visible) unless explicitly hidden
            return this.registeredWidgets.has(widgetId) && !this.hiddenMobileWidgets.has(widgetId);
        }
        return this.pinnedWidgets.has(widgetId);
    }

    /**
     * Update mobile tabs based on registered widgets and viewport mode
     */
    updateMobileTabs() {
        if (!this.mobileTabsContainer) return;
        
        const mode = this.getViewportMode();
        
        if (mode === 'desktop') {
            // On desktop, restore standard tabs and hide widget tabs
            this.restoreStandardTabs();
            return;
        }
        
        // Get visible widgets (registered and not hidden)
        const visibleWidgets = Array.from(this.registeredWidgets.keys())
            .filter(id => !this.hiddenMobileWidgets.has(id));
        
        // If no widgets visible, just show standard tabs normally
        if (visibleWidgets.length === 0) {
            this.restoreStandardTabs();
            return;
        }
        
        // Mobile with widgets: Render all tabs in unified order
        this.renderUnifiedTabs();
    }

    /**
     * Restore standard tabs (desktop mode)
     */
    restoreStandardTabs() {
        if (!this.mobileTabsContainer) return;
        
        // Remove widget tabs
        this.mobileTabsContainer.querySelectorAll('.tab-widget').forEach(tab => tab.remove());
        
        // Remove overflow indicator
        const indicator = this.mobileTabsContainer.querySelector('.tab-overflow-indicator');
        if (indicator) indicator.remove();
        
        // Show all standard tabs in original order
        this.mobileTabsContainer.querySelectorAll('.tab-btn:not(.tab-widget)').forEach(tab => {
            if (tab.dataset.tab !== 'dashboard') {
                tab.classList.remove('hidden');
                tab.draggable = false;
                tab.classList.remove('tab-reorderable');
            }
        });
        
        // Hide old dashboard tab
        const dashboardTab = this.mobileTabsContainer.querySelector('.tab-dashboard');
        if (dashboardTab) {
            dashboardTab.classList.add('hidden');
        }
        
        // Remove scrollable class
        this.mobileTabsContainer.classList.remove('mobile-tabs-scrollable');
        this.mobileTabsContainer.classList.remove('can-scroll-left');
        this.mobileTabsContainer.classList.remove('can-scroll-right');
        
        // Hide mobile widget content
        if (this.mobileWidgetContent) {
            this.mobileWidgetContent.classList.remove('active');
        }
    }

    /**
     * Render all tabs (standard + widget) in unified order
     */
    renderUnifiedTabs() {
        if (!this.mobileTabsContainer) return;
        
        // Remove existing widget tabs
        this.mobileTabsContainer.querySelectorAll('.tab-widget').forEach(tab => tab.remove());
        
        // Hide old dashboard tab
        const dashboardTab = this.mobileTabsContainer.querySelector('.tab-dashboard');
        if (dashboardTab) {
            dashboardTab.classList.add('hidden');
        }
        
        // Ensure unified tab order is up to date
        this.initializeUnifiedTabOrder();
        
        // Get valid tab order (filter out invalid entries)
        const validTabOrder = this.unifiedTabOrder.filter(tabId => {
            if (tabId.startsWith('tab:')) {
                const dataTab = tabId.replace('tab:', '');
                return this.mobileTabsContainer.querySelector(`[data-tab="${dataTab}"]`) !== null;
            } else if (tabId.startsWith('widget:')) {
                const widgetId = tabId.replace('widget:', '');
                // Widget is visible if registered and not hidden
                return this.registeredWidgets.has(widgetId) && !this.hiddenMobileWidgets.has(widgetId);
            }
            return false;
        });
        
        // Show all tabs in single scrolling row
        const visibleTabs = validTabOrder;
        
        // Hide all standard tabs first (we'll show them in order)
        this.mobileTabsContainer.querySelectorAll('.tab-btn:not(.tab-widget)').forEach(tab => {
            if (tab.dataset.tab !== 'dashboard') {
                tab.classList.add('hidden');
            }
        });
        
        // Render tabs in unified order
        visibleTabs.forEach((tabId, index) => {
            if (tabId.startsWith('tab:')) {
                // Standard tab
                const dataTab = tabId.replace('tab:', '');
                const existingTab = this.mobileTabsContainer.querySelector(`[data-tab="${dataTab}"]`);
                if (existingTab) {
                    existingTab.classList.remove('hidden');
                    existingTab.classList.add('tab-reorderable');
                    existingTab.draggable = true;
                    existingTab.dataset.tabOrder = index;
                    existingTab.dataset.tabId = tabId;
                    
                    // Move to correct position
                    this.mobileTabsContainer.appendChild(existingTab);
                    
                    // Attach drag handlers if not already attached
                    if (!existingTab.hasAttribute('data-drag-attached')) {
                        this.attachUnifiedTabDragHandlers(existingTab, 'standard');
                        existingTab.setAttribute('data-drag-attached', 'true');
                    }
                }
            } else if (tabId.startsWith('widget:')) {
                // Widget tab
                const widgetId = tabId.replace('widget:', '');
                const widget = this.registeredWidgets.get(widgetId);
                if (!widget) return;
                
                const tab = document.createElement('button');
                tab.className = 'tab-btn tab-widget tab-reorderable';
                tab.dataset.widgetId = widgetId;
                tab.dataset.tabId = tabId;
                tab.dataset.tabOrder = index;
                tab.setAttribute('role', 'tab');
                tab.setAttribute('aria-selected', this.activeWidgetTab === widgetId ? 'true' : 'false');
                tab.draggable = true;
                
                if (this.activeWidgetTab === widgetId) {
                    tab.classList.add('active');
                }
                
                tab.innerHTML = `
                    ${widget.icon}
                    <span>${widget.name}</span>
                `;
                
                // Click handler
                tab.addEventListener('click', () => this.switchToWidgetTab(widgetId));
                
                // Drag handlers
                this.attachUnifiedTabDragHandlers(tab, 'widget');
                
                this.mobileTabsContainer.appendChild(tab);
            }
        });
        
        // Enable horizontal scrolling mode when we have extra tabs
        const hasExtraTabs = visibleTabs.length > 4;
        if (hasExtraTabs) {
            this.mobileTabsContainer.classList.add('mobile-tabs-scrollable');
            this.setupScrollIndicators();
        } else {
            this.mobileTabsContainer.classList.remove('mobile-tabs-scrollable');
        }
    }

    /**
     * Setup scroll indicators for horizontal tab scrolling
     */
    setupScrollIndicators() {
        if (!this.mobileTabsContainer) return;
        
        // Update scroll indicators on scroll
        const updateIndicators = () => {
            const { scrollLeft, scrollWidth, clientWidth } = this.mobileTabsContainer;
            const canScrollLeft = scrollLeft > 5;
            const canScrollRight = scrollLeft < scrollWidth - clientWidth - 5;
            
            this.mobileTabsContainer.classList.toggle('can-scroll-left', canScrollLeft);
            this.mobileTabsContainer.classList.toggle('can-scroll-right', canScrollRight);
        };
        
        // Remove old listener if exists
        this.mobileTabsContainer.removeEventListener('scroll', this._scrollHandler);
        
        // Store reference and add listener
        this._scrollHandler = updateIndicators;
        this.mobileTabsContainer.addEventListener('scroll', updateIndicators, { passive: true });
        
        // Initial update
        setTimeout(updateIndicators, 50);
    }

    /**
     * Switch to a widget tab (mobile/tablet)
     */
    switchToWidgetTab(widgetId) {
        const widget = this.registeredWidgets.get(widgetId);
        if (!widget) return;
        
        this.activeWidgetTab = widgetId;
        
        // Update tab button states
        this.mobileTabsContainer.querySelectorAll('.tab-btn').forEach(tab => {
            const isActive = tab.dataset.widgetId === widgetId;
            tab.classList.toggle('active', isActive);
            tab.setAttribute('aria-selected', isActive ? 'true' : 'false');
        });
        
        // Hide standard sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        
        // Show and render widget content
        if (this.mobileWidgetContent) {
            this.mobileWidgetContent.classList.add('active');
            const inner = this.mobileWidgetContent.querySelector('.mobile-widget-inner');
            if (inner) {
                inner.innerHTML = `
                    <div class="mobile-widget-header">
                        <h2>${widget.name}</h2>
                    </div>
                    <div class="mobile-widget-body">
                        ${widget.render()}
                    </div>
                `;
                
                // Call onMount
                widget.onMount(this.mobileWidgetContent);
            }
        }
    }

    /**
     * Switch to a standard tab (when no widgets or widget unpinned)
     */
    switchToStandardTab() {
        // Find first visible standard tab and click it
        const firstTab = this.mobileTabsContainer.querySelector('.tab-btn:not(.tab-widget):not(.hidden):not(.tab-dashboard)');
        if (firstTab) {
            firstTab.click();
        }
        
        // Hide mobile widget content
        if (this.mobileWidgetContent) {
            this.mobileWidgetContent.classList.remove('active');
        }
    }

    /**
     * Attach drag handlers to any tab (standard or widget) for unified reordering
     */
    attachUnifiedTabDragHandlers(tab, tabType) {
        tab.addEventListener('dragstart', (e) => {
            this.tabDragState.isDragging = true;
            this.tabDragState.draggedTab = tab;
            this.tabDragState.tabType = tabType;
            this.tabDragState.startIndex = parseInt(tab.dataset.tabOrder, 10);
            tab.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', tab.dataset.tabId);
        });

        tab.addEventListener('dragend', () => {
            this.tabDragState.isDragging = false;
            tab.classList.remove('dragging');
            this.tabDragState.draggedTab = null;
            this.tabDragState.tabType = null;
        });

        tab.addEventListener('dragover', (e) => {
            e.preventDefault();
            if (!this.tabDragState.isDragging || this.tabDragState.draggedTab === tab) return;
            
            const rect = tab.getBoundingClientRect();
            const midX = rect.left + rect.width / 2;
            
            if (e.clientX < midX) {
                tab.parentNode.insertBefore(this.tabDragState.draggedTab, tab);
            } else {
                tab.parentNode.insertBefore(this.tabDragState.draggedTab, tab.nextSibling);
            }
        });

        tab.addEventListener('drop', (e) => {
            e.preventDefault();
            this.updateUnifiedTabOrderFromDOM();
            this.saveConfig();
        });

        // Touch support for reordering
        let touchStartX = 0;
        let touchStartY = 0;
        let touchActive = false;
        
        tab.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
            touchActive = true;
            
            // Add visual feedback after short hold
            setTimeout(() => {
                if (touchActive && tab.matches(':hover') || touchActive) {
                    tab.classList.add('touch-dragging');
                }
            }, 200);
        }, { passive: true });

        tab.addEventListener('touchmove', (e) => {
            if (!touchActive) return;
            
            const deltaX = Math.abs(e.touches[0].clientX - touchStartX);
            const deltaY = Math.abs(e.touches[0].clientY - touchStartY);
            
            // If horizontal swipe is more than vertical, it's a reorder attempt
            if (deltaX > 30 && deltaX > deltaY) {
                tab.classList.add('touch-dragging');
                
                // Find all reorderable tabs and swap if crossed midpoint
                const tabs = Array.from(this.mobileTabsContainer.querySelectorAll('.tab-reorderable:not(.hidden)'));
                const currentIdx = tabs.indexOf(tab);
                const touchX = e.touches[0].clientX;
                
                tabs.forEach((otherTab, idx) => {
                    if (otherTab === tab) return;
                    const rect = otherTab.getBoundingClientRect();
                    const midX = rect.left + rect.width / 2;
                    
                    if (idx < currentIdx && touchX < midX) {
                        tab.parentNode.insertBefore(tab, otherTab);
                    } else if (idx > currentIdx && touchX > midX) {
                        tab.parentNode.insertBefore(tab, otherTab.nextSibling);
                    }
                });
            }
        }, { passive: true });

        tab.addEventListener('touchend', () => {
            touchActive = false;
            tab.classList.remove('touch-dragging');
            this.updateUnifiedTabOrderFromDOM();
            this.saveConfig();
        });
    }

    /**
     * Update unified tab order from current DOM order
     */
    updateUnifiedTabOrderFromDOM() {
        const tabs = Array.from(this.mobileTabsContainer.querySelectorAll('.tab-reorderable:not(.hidden)'));
        this.unifiedTabOrder = tabs.map(tab => tab.dataset.tabId).filter(id => id);
        
        // Ensure any hidden tabs are kept in the order at the end
        const hiddenTabs = Array.from(this.mobileTabsContainer.querySelectorAll('.tab-btn.hidden[data-tab-id]'));
        hiddenTabs.forEach(tab => {
            if (tab.dataset.tabId && !this.unifiedTabOrder.includes(tab.dataset.tabId)) {
                this.unifiedTabOrder.push(tab.dataset.tabId);
            }
        });
    }

    /**
     * Get tab index (legacy - kept for compatibility)
     */
    getTabIndex(tab) {
        const tabs = Array.from(this.mobileTabsContainer.querySelectorAll('.tab-reorderable:not(.hidden)'));
        return tabs.indexOf(tab);
    }

    /**
     * Update widget order from current tab order (legacy - kept for compatibility)
     */
    updateWidgetOrderFromTabs() {
        const tabs = Array.from(this.mobileTabsContainer.querySelectorAll('.tab-widget'));
        this.widgetOrder = tabs.map(tab => tab.dataset.widgetId);
    }

    /**
     * Render a single widget to the desktop dashboard
     */
    renderWidget(widgetId) {
        const widget = this.registeredWidgets.get(widgetId);
        if (!widget || !this.container) return;
        
        let widgetEl = document.getElementById(`dashboard-widget-${widgetId}`);
        if (!widgetEl) {
            widgetEl = document.createElement('div');
            widgetEl.id = `dashboard-widget-${widgetId}`;
            widgetEl.className = 'dashboard-widget';
            widgetEl.dataset.widgetId = widgetId;
            widgetEl.draggable = true;
            this.container.appendChild(widgetEl);
        }
        
        widgetEl.innerHTML = `
            <div class="dashboard-widget-header">
                <div class="dashboard-widget-drag-handle" title="Drag to reorder">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="9" cy="5" r="1"/><circle cx="9" cy="12" r="1"/><circle cx="9" cy="19" r="1"/>
                        <circle cx="15" cy="5" r="1"/><circle cx="15" cy="12" r="1"/><circle cx="15" cy="19" r="1"/>
                    </svg>
                </div>
                <div class="dashboard-widget-title">
                    ${widget.icon}
                    <span>${widget.name}</span>
                </div>
                <button class="dashboard-widget-unpin" data-widget-id="${widgetId}" title="Unpin from dashboard">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/>
                        <line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
            <div class="dashboard-widget-content">
                ${widget.render()}
            </div>
        `;
        
        this.attachDragHandlers(widgetEl);
        
        // Attach unpin button handler
        const unpinBtn = widgetEl.querySelector('.dashboard-widget-unpin');
        if (unpinBtn) {
            unpinBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const wId = unpinBtn.dataset.widgetId;
                this.unpinWidget(wId);
            });
        }
        
        widget.onMount(widgetEl);
    }

    /**
     * Re-render a specific widget (called when its content changes)
     */
    refreshWidget(widgetId) {
        if (!this.pinnedWidgets.has(widgetId)) return;
        
        const widget = this.registeredWidgets.get(widgetId);
        if (!widget) return;
        
        const mode = this.getViewportMode();
        
        if (mode === 'desktop') {
            // Update desktop widget
            const contentEl = document.querySelector(`#dashboard-widget-${widgetId} .dashboard-widget-content`);
            if (contentEl) {
                contentEl.innerHTML = widget.render();
                widget.onMount(document.getElementById(`dashboard-widget-${widgetId}`));
            }
        } else if (this.activeWidgetTab === widgetId && this.mobileWidgetContent) {
            // Update mobile widget if it's the active tab
            const bodyEl = this.mobileWidgetContent.querySelector('.mobile-widget-body');
            if (bodyEl) {
                bodyEl.innerHTML = widget.render();
                widget.onMount(this.mobileWidgetContent);
            }
        }
    }

    /**
     * Restore pinned widgets on page load
     */
    restorePinnedWidgets() {
        setTimeout(() => {
            const orderedWidgets = this.getOrderedWidgets();
            const mode = this.getViewportMode();
            
            if (mode === 'desktop') {
                orderedWidgets.forEach(widgetId => {
                    if (this.registeredWidgets.has(widgetId)) {
                        this.renderWidget(widgetId);
                    }
                });
            }
            
            this.updateDashboardVisibility();
            this.updateMobileTabs();
            
            // Notify components about restored pins
            orderedWidgets.forEach(widgetId => {
                this.notifyWidgetPinChange(widgetId, true);
            });
        }, 100);
    }

    /**
     * Get widgets in their saved order
     */
    getOrderedWidgets() {
        const ordered = this.widgetOrder.filter(id => this.pinnedWidgets.has(id));
        this.pinnedWidgets.forEach(id => {
            if (!ordered.includes(id)) {
                ordered.push(id);
            }
        });
        return ordered;
    }

    /**
     * Attach drag handlers to a desktop widget element
     */
    attachDragHandlers(widgetEl) {
        const handle = widgetEl.querySelector('.dashboard-widget-drag-handle');
        if (!handle) return;

        handle.addEventListener('mousedown', () => {
            widgetEl.draggable = true;
        });
        
        widgetEl.addEventListener('dragend', () => {
            widgetEl.draggable = true;
        });

        widgetEl.addEventListener('dragstart', (e) => {
            this.dragState.isDragging = true;
            this.dragState.draggedWidget = widgetEl;
            this.dragState.startIndex = this.getWidgetIndex(widgetEl);
            
            widgetEl.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', widgetEl.dataset.widgetId);
            
            this.dragState.placeholder = document.createElement('div');
            this.dragState.placeholder.className = 'dashboard-widget-placeholder';
            this.dragState.placeholder.style.height = `${widgetEl.offsetHeight}px`;
        });

        widgetEl.addEventListener('dragend', (e) => {
            this.dragState.isDragging = false;
            widgetEl.classList.remove('dragging');
            
            if (this.dragState.placeholder && this.dragState.placeholder.parentNode) {
                this.dragState.placeholder.remove();
            }
            
            this.dragState.draggedWidget = null;
            this.dragState.placeholder = null;
        });

        widgetEl.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            
            if (!this.dragState.isDragging || this.dragState.draggedWidget === widgetEl) return;
            
            const rect = widgetEl.getBoundingClientRect();
            const midY = rect.top + rect.height / 2;
            
            if (e.clientY < midY) {
                widgetEl.parentNode.insertBefore(this.dragState.placeholder, widgetEl);
            } else {
                widgetEl.parentNode.insertBefore(this.dragState.placeholder, widgetEl.nextSibling);
            }
        });

        widgetEl.addEventListener('drop', (e) => {
            e.preventDefault();
            
            if (!this.dragState.isDragging || !this.dragState.placeholder) return;
            
            this.dragState.placeholder.parentNode.insertBefore(
                this.dragState.draggedWidget, 
                this.dragState.placeholder
            );
            
            this.updateOrderFromDOM();
            this.saveConfig();
        });
    }

    /**
     * Get the current index of a widget in the container
     */
    getWidgetIndex(widgetEl) {
        const widgets = Array.from(this.container.querySelectorAll('.dashboard-widget'));
        return widgets.indexOf(widgetEl);
    }

    /**
     * Update widget order from current desktop DOM order
     */
    updateOrderFromDOM() {
        const widgets = Array.from(this.container.querySelectorAll('.dashboard-widget'));
        this.widgetOrder = widgets.map(w => w.dataset.widgetId);
    }

    /**
     * Update dashboard section visibility
     */
    updateDashboardVisibility() {
        const section = document.getElementById('dashboard-section');
        const dashboardTab = document.querySelector('.tab-dashboard');
        const widgetsContainer = document.getElementById('dashboard-widgets');
        const mainContent = document.querySelector('.main-content');
        
        // Check both the pinnedWidgets set AND actual rendered widgets in DOM
        const hasWidgetsInSet = this.pinnedWidgets.size > 0;
        const hasRenderedWidgets = widgetsContainer && widgetsContainer.children.length > 0;
        const hasWidgets = hasWidgetsInSet && hasRenderedWidgets;
        const mode = this.getViewportMode();
        
        // Hide old dashboard tab (we use widget tabs now)
        if (dashboardTab) {
            dashboardTab.classList.add('hidden');
        }
        
        if (section) {
            if (mode === 'desktop' && hasWidgets) {
                // Show dashboard section when has rendered widgets
                section.style.setProperty('display', 'block', 'important');
                section.classList.add('active');
            } else {
                // Hide dashboard section (no widgets or mobile mode)
                section.style.setProperty('display', 'none', 'important');
                section.classList.remove('active');
            }
        }
        
        // Toggle grid layout class to collapse dashboard row when empty
        if (mainContent) {
            if (hasWidgets) {
                mainContent.classList.remove('no-dashboard');
            } else {
                mainContent.classList.add('no-dashboard');
            }
        }
    }

    /**
     * Get list of available (unpinned) widgets
     */
    getAvailableWidgets() {
        const available = [];
        this.registeredWidgets.forEach((widget, id) => {
            if (!this.pinnedWidgets.has(id)) {
                available.push(widget);
            }
        });
        return available;
    }

    /**
     * Get list of pinned/visible widgets
     */
    getPinnedWidgets() {
        const pinned = [];
        const mode = this.getViewportMode();
        
        if (mode === 'mobile') {
            // On mobile, return all registered widgets that aren't hidden
            this.registeredWidgets.forEach((widget, id) => {
                if (!this.hiddenMobileWidgets.has(id)) {
                    pinned.push(widget);
                }
            });
        } else {
            // On desktop, return explicitly pinned widgets
            this.pinnedWidgets.forEach(id => {
                const widget = this.registeredWidgets.get(id);
                if (widget) {
                    pinned.push(widget);
                }
            });
        }
        return pinned;
    }

    /**
     * Load configuration from localStorage
     */
    loadConfig() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            if (saved) {
                const config = JSON.parse(saved);
                this.pinnedWidgets = new Set(config.pinnedWidgets || []);
                this.hiddenMobileWidgets = new Set(config.hiddenMobileWidgets || []);
                this.widgetOrder = config.widgetOrder || config.pinnedWidgets || [];
                this.unifiedTabOrder = config.unifiedTabOrder || [...this.defaultStandardTabs];
            }
        } catch (e) {
            console.warn('Failed to load dashboard config:', e);
        }
    }

    /**
     * Save configuration to localStorage
     */
    saveConfig() {
        try {
            const config = {
                pinnedWidgets: Array.from(this.pinnedWidgets),
                hiddenMobileWidgets: Array.from(this.hiddenMobileWidgets),
                widgetOrder: this.widgetOrder,
                unifiedTabOrder: this.unifiedTabOrder
            };
            localStorage.setItem(this.storageKey, JSON.stringify(config));
        } catch (e) {
            console.warn('Failed to save dashboard config:', e);
        }
    }

    /**
     * Handle window resize
     */
    setupResizeHandler() {
        let lastMode = this.getViewportMode();
        let resizeTimeout;
        
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                const newMode = this.getViewportMode();
                
                if (newMode !== lastMode) {
                    lastMode = newMode;
                    
                    // Re-render everything for new viewport mode
                    if (newMode === 'desktop') {
                        // Render desktop widgets (only explicitly pinned)
                        const orderedWidgets = this.getOrderedWidgets();
                        orderedWidgets.forEach(widgetId => {
                            if (this.registeredWidgets.has(widgetId)) {
                                this.renderWidget(widgetId);
                            }
                        });
                        
                        // Notify widgets about desktop pin state
                        this.registeredWidgets.forEach((widget, id) => {
                            this.notifyWidgetPinChange(id, this.pinnedWidgets.has(id));
                        });
                    } else {
                        // Clear desktop widgets
                        if (this.container) {
                            this.container.innerHTML = '';
                        }
                        
                        // On mobile, notify all non-hidden widgets they're "pinned" (visible)
                        this.registeredWidgets.forEach((widget, id) => {
                            const isVisible = !this.hiddenMobileWidgets.has(id);
                            this.notifyWidgetPinChange(id, isVisible);
                        });
                    }
                    
                    this.updateDashboardVisibility();
                    this.updateMobileTabs();
                }
            }, 150);
        });
    }

    /**
     * Setup drag handlers on the container for drops
     */
    setupContainerDragHandlers() {
        if (!this.container) return;

        this.container.addEventListener('dragover', (e) => {
            e.preventDefault();
            if (!this.dragState.isDragging) return;
            
            const widgets = this.container.querySelectorAll('.dashboard-widget:not(.dragging)');
            if (widgets.length === 0) {
                this.container.appendChild(this.dragState.placeholder);
            }
        });

        this.container.addEventListener('drop', (e) => {
            e.preventDefault();
            if (!this.dragState.isDragging || !this.dragState.placeholder) return;
            
            if (this.dragState.placeholder.parentNode) {
                this.dragState.placeholder.parentNode.insertBefore(
                    this.dragState.draggedWidget, 
                    this.dragState.placeholder
                );
            }
            
            this.updateOrderFromDOM();
            this.saveConfig();
        });
    }

    /**
     * Check if dashboard mode is active (desktop with widgets)
     */
    isDashboardActive() {
        return this.getViewportMode() === 'desktop' && this.pinnedWidgets.size > 0;
    }
}

// Create global instance
window.dashboardManager = new DashboardManager();
