/**
 * OREI Matrix Control - Floating CEC Tray Component
 * 
 * Unified CEC remote with auto-detection of targets based on current routing.
 * Supports manual target override, position customization, and scene-based CEC profiles.
 */

class CECTray {
    constructor() {
        this.isExpanded = false;
        this.position = this.loadPosition();
        this.macros = [];  // Loaded CEC macros
        
        // CEC target configuration (manual overrides)
        this.targets = {
            navigation: { type: 'auto', port: null },
            playback: { type: 'auto', port: null },
            volume: { type: 'auto', port: null },
            power: { inputs: [], outputs: [] }
        };
        
        // Resolved targets (after auto-detection or scene config)
        this.resolvedTargets = {
            navigation: null,  // { type: 'input', port: 1, name: 'Apple TV' }
            playback: null,
            volume: null,
            power_on: [],
            power_off: []
        };
        
        // Active scene CEC config (if any)
        this.activeSceneConfig = null;
        this.activeSceneName = null;
        
        // Create DOM elements
        this.createElements();
        this.attachEventListeners();
        
        // Register as dashboard widget
        this.registerAsWidget();
        
        // Subscribe to state changes for auto-detection
        state.on('routing', () => this.updateAutoTargets());
        state.on('inputs', () => this.updateAutoTargets());
        state.on('outputs', () => this.updateAutoTargets());
        state.on('activeScene', (scene) => this.onActiveSceneChanged(scene));
        
        // Initial target resolution
        this.updateAutoTargets();
    }

    /**
     * Register as a dashboard widget
     */
    registerAsWidget() {
        if (typeof window.dashboardManager !== 'undefined') {
            window.dashboardManager.registerWidget({
                id: 'cec-remote',
                name: 'CEC Remote',
                icon: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                    <line x1="8" y1="21" x2="16" y2="21"/>
                    <line x1="12" y1="17" x2="12" y2="21"/>
                </svg>`,
                render: () => this.renderWidgetContent(),
                onMount: (el) => this.attachWidgetEventListeners(el),
                onUnmount: () => {},
                component: this
            });
        }
    }

    /**
     * Render content for the dashboard widget (compact version)
     */
    renderWidgetContent() {
        const navTarget = this.resolvedTargets.navigation;
        const volTarget = this.resolvedTargets.volume;
        
        const navName = navTarget ? navTarget.name : 'Not detected';
        const volName = volTarget ? volTarget.name : 'Not detected';
        
        // Get scene display if available
        let sceneDisplay = '';
        if (this.activeScene) {
            sceneDisplay = `<span class="scene-indicator widget-scene">${Helpers.escapeHtml(this.activeScene.name || 'Scene')}</span>`;
        }
        
        return `
            <div class="cec-widget">
                <!-- Widget Header with targets -->
                <div class="cec-widget-header">
                    <div class="cec-widget-targets">
                        <div class="cec-target-group">
                            <span class="cec-target-label">Nav</span>
                            <button class="cec-widget-target-btn" data-target="navigation" title="Navigation target: ${Helpers.escapeHtml(navName)}">
                                <svg class="icon icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"/>
                                </svg>
                                <span class="target-abbrev">${Helpers.escapeHtml(this.abbreviateName(navName))}</span>
                            </button>
                        </div>
                        <div class="cec-target-group">
                            <span class="cec-target-label">Vol</span>
                            <button class="cec-widget-target-btn" data-target="volume" title="Volume target: ${Helpers.escapeHtml(volName)}">
                                <svg class="icon icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                                    <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
                                </svg>
                                <span class="target-abbrev">${Helpers.escapeHtml(this.abbreviateName(volName))}</span>
                            </button>
                        </div>
                    </div>
                </div>
                
                <!-- Power Section -->
                <div class="cec-widget-section">
                    <div class="cec-widget-section-title">Power</div>
                    <div class="cec-widget-btn-row">
                        <button class="cec-widget-cmd-btn power-on" data-action="power" data-cmd="power_on" title="Power On">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <line x1="12" y1="6" x2="12" y2="12"/>
                            </svg>
                            <span>On</span>
                        </button>
                        <button class="cec-widget-cmd-btn power-off" data-action="power" data-cmd="power_off" title="Power Off">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18.36 6.64a9 9 0 1 1-12.73 0"/>
                                <line x1="12" y1="2" x2="12" y2="12"/>
                            </svg>
                            <span>Off</span>
                        </button>
                    </div>
                </div>
                
                <!-- Navigation Section with D-pad/Trackpad -->
                <div class="cec-widget-section">
                    <div class="cec-widget-section-title">Navigation</div>
                    <!-- D-pad for desktop (visible on desktop, hidden on mobile) -->
                    <div class="cec-widget-dpad desktop-only" id="cec-widget-dpad">
                        <button class="cec-widget-cmd-btn dpad-up" data-action="nav" data-cmd="up" title="Up">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="18 15 12 9 6 15"/>
                            </svg>
                        </button>
                        <button class="cec-widget-cmd-btn dpad-left" data-action="nav" data-cmd="left" title="Left">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="15 18 9 12 15 6"/>
                            </svg>
                        </button>
                        <button class="cec-widget-cmd-btn dpad-center" data-action="nav" data-cmd="select" title="Select/OK">OK</button>
                        <button class="cec-widget-cmd-btn dpad-right" data-action="nav" data-cmd="right" title="Right">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="9 18 15 12 9 6"/>
                            </svg>
                        </button>
                        <button class="cec-widget-cmd-btn dpad-down" data-action="nav" data-cmd="down" title="Down">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="6 9 12 15 18 9"/>
                            </svg>
                        </button>
                    </div>
                    <!-- Trackpad for mobile (visible on mobile, hidden on desktop) -->
                    <div class="cec-trackpad cec-widget-trackpad mobile-only" id="cec-widget-trackpad">
                        <div class="trackpad-surface">
                            <div class="trackpad-hint">Swipe to navigate<br>Tap to select</div>
                            <div class="trackpad-feedback"></div>
                        </div>
                    </div>
                    <div class="cec-widget-btn-row nav-secondary">
                        <button class="cec-widget-cmd-btn" data-action="nav" data-cmd="menu" title="Menu">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="3" y1="12" x2="21" y2="12"/>
                                <line x1="3" y1="6" x2="21" y2="6"/>
                                <line x1="3" y1="18" x2="21" y2="18"/>
                            </svg>
                            <span>Menu</span>
                        </button>
                        <button class="cec-widget-cmd-btn" data-action="nav" data-cmd="back" title="Back">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="19" y1="12" x2="5" y2="12"/>
                                <polyline points="12 19 5 12 12 5"/>
                            </svg>
                            <span>Back</span>
                        </button>
                        <button class="cec-widget-cmd-btn" data-action="nav" data-cmd="home" title="Home">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                                <polyline points="9 22 9 12 15 12 15 22"/>
                            </svg>
                            <span>Home</span>
                        </button>
                    </div>
                </div>
                
                <!-- Playback Section -->
                <div class="cec-widget-section">
                    <div class="cec-widget-section-title">Playback</div>
                    <div class="cec-widget-btn-row playback-row">
                        <button class="cec-widget-cmd-btn" data-action="playback" data-cmd="previous" title="Previous">⏮</button>
                        <button class="cec-widget-cmd-btn" data-action="playback" data-cmd="rewind" title="Rewind">⏪</button>
                        <button class="cec-widget-cmd-btn play-btn" data-action="playback" data-cmd="play" title="Play">▶</button>
                        <button class="cec-widget-cmd-btn" data-action="playback" data-cmd="pause" title="Pause">⏸</button>
                        <button class="cec-widget-cmd-btn" data-action="playback" data-cmd="stop" title="Stop">⏹</button>
                        <button class="cec-widget-cmd-btn" data-action="playback" data-cmd="fast_forward" title="Fast Forward">⏩</button>
                        <button class="cec-widget-cmd-btn" data-action="playback" data-cmd="next" title="Next">⏭</button>
                    </div>
                </div>
                
                <!-- Volume Section -->
                <div class="cec-widget-section">
                    <div class="cec-widget-section-title">Volume</div>
                    <div class="cec-widget-btn-row volume-row">
                        <button class="cec-widget-cmd-btn vol-btn" data-action="volume" data-cmd="volume_down" title="Volume Down">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                            </svg>
                            <span>−</span>
                        </button>
                        <button class="cec-widget-cmd-btn vol-btn" data-action="volume" data-cmd="mute" title="Mute">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                                <line x1="23" y1="9" x2="17" y2="15"/>
                                <line x1="17" y1="9" x2="23" y2="15"/>
                            </svg>
                            <span>Mute</span>
                        </button>
                        <button class="cec-widget-cmd-btn vol-btn" data-action="volume" data-cmd="volume_up" title="Volume Up">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                                <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
                            </svg>
                            <span>+</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Attach event listeners to widget buttons
     */
    attachWidgetEventListeners(widgetEl) {
        if (!widgetEl) return;
        
        // Command buttons
        widgetEl.querySelectorAll('.cec-widget-cmd-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = btn.dataset.action;
                const cmd = btn.dataset.cmd;
                if (action && cmd) {
                    this.executeCommand(action, cmd);
                }
            });
        });
        
        // Target buttons
        widgetEl.querySelectorAll('.cec-widget-target-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const targetType = btn.dataset.target;
                if (targetType) {
                    this.showWidgetTargetSelector(btn, targetType);
                }
            });
        });
        
        // Initialize trackpad for widget
        this.initWidgetTrackpad(widgetEl);
    }
    
    /**
     * Initialize trackpad gesture handling for widget
     */
    initWidgetTrackpad(widgetEl) {
        const trackpad = widgetEl.querySelector('#cec-widget-trackpad');
        if (!trackpad) return;
        
        const surface = trackpad.querySelector('.trackpad-surface');
        const feedback = trackpad.querySelector('.trackpad-feedback');
        
        let startX = 0;
        let startY = 0;
        let startTime = 0;
        let isActive = false;
        
        const SWIPE_THRESHOLD = 30;
        const TAP_THRESHOLD = 10;
        const TAP_TIME = 300;
        
        const showFeedback = (direction) => {
            feedback.className = 'trackpad-feedback';
            feedback.classList.add('active', direction);
            setTimeout(() => {
                feedback.classList.remove('active', direction);
            }, 200);
        };
        
        const handleGestureEnd = (endX, endY) => {
            if (!isActive) return;
            isActive = false;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            const deltaTime = Date.now() - startTime;
            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
            
            if (deltaTime < TAP_TIME && distance < TAP_THRESHOLD) {
                showFeedback('tap');
                this.sendNavCommand('select');
                return;
            }
            
            if (distance >= SWIPE_THRESHOLD) {
                const absX = Math.abs(deltaX);
                const absY = Math.abs(deltaY);
                
                if (absX > absY) {
                    if (deltaX > 0) {
                        showFeedback('right');
                        this.sendNavCommand('right');
                    } else {
                        showFeedback('left');
                        this.sendNavCommand('left');
                    }
                } else {
                    if (deltaY > 0) {
                        showFeedback('down');
                        this.sendNavCommand('down');
                    } else {
                        showFeedback('up');
                        this.sendNavCommand('up');
                    }
                }
            }
        };
        
        // Touch events
        surface.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
            startTime = Date.now();
            isActive = true;
            surface.classList.add('touching');
        }, { passive: false });
        
        surface.addEventListener('touchend', (e) => {
            surface.classList.remove('touching');
            if (e.changedTouches.length > 0) {
                const touch = e.changedTouches[0];
                handleGestureEnd(touch.clientX, touch.clientY);
            }
        });
        
        surface.addEventListener('touchcancel', () => {
            surface.classList.remove('touching');
            isActive = false;
        });
        
        // Mouse events
        surface.addEventListener('mousedown', (e) => {
            startX = e.clientX;
            startY = e.clientY;
            startTime = Date.now();
            isActive = true;
            surface.classList.add('touching');
        });
        
        surface.addEventListener('mouseup', (e) => {
            surface.classList.remove('touching');
            handleGestureEnd(e.clientX, e.clientY);
        });
        
        surface.addEventListener('mouseleave', () => {
            surface.classList.remove('touching');
            isActive = false;
        });
    }
    
    /**
     * Show target selector dropdown for widget
     */
    showWidgetTargetSelector(btn, targetType) {
        // Reuse existing target selector logic with widget-specific positioning
        this.currentTargetType = targetType;
        this.showTargetSelector(targetType, btn);
    }

    /**
     * Called when state changes - refresh widget if pinned
     */
    onStateChange() {
        if (window.dashboardManager && window.dashboardManager.isWidgetPinned('cec-remote')) {
            window.dashboardManager.refreshWidget('cec-remote');
        }
    }

    /**
     * Check if CEC Remote is pinned/visible on dashboard
     */
    isPinnedToDashboard() {
        return window.dashboardManager && window.dashboardManager.isWidgetPinned('cec-remote');
    }

    /**
     * Toggle dashboard pin state (pin on desktop, hide on mobile)
     */
    toggleDashboardPin() {
        if (window.dashboardManager) {
            if (this.isPinnedToDashboard()) {
                // Already pinned/visible - unpin/hide it
                window.dashboardManager.unpinWidget('cec-remote');
            } else {
                // Not pinned/visible - pin/show it
                if (window.dashboardManager.pinWidget('cec-remote')) {
                    this.collapse();
                }
            }
        }
    }

    /**
     * Load saved position from localStorage
     */
    loadPosition() {
        try {
            return localStorage.getItem('orei_cec_tray_position') || 'bottom-right';
        } catch (e) {
            return 'bottom-right';
        }
    }

    /**
     * Save position to localStorage
     */
    savePosition(position) {
        this.position = position;
        try {
            localStorage.setItem('orei_cec_tray_position', position);
        } catch (e) {
            console.warn('Failed to save CEC tray position:', e);
        }
        this.updatePosition();
    }

    /**
     * Load pinned state from localStorage
     */
    loadPinnedState() {
        try {
            return localStorage.getItem('orei_cec_tray_pinned') === 'true';
        } catch (e) {
            return false;
        }
    }

    /**
     * Create DOM elements for the tray
     */
    createElements() {
        // Create container
        this.container = document.createElement('div');
        this.container.className = 'cec-tray';
        this.container.id = 'cec-tray';
        
        // Create FAB button
        this.fab = document.createElement('button');
        this.fab.className = 'cec-tray-fab';
        this.fab.innerHTML = `
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
        `;
        this.fab.title = 'CEC Remote Control';
        
        // Create expanded panel
        this.panel = document.createElement('div');
        this.panel.className = 'cec-tray-panel';
        this.panel.innerHTML = this.renderPanel();
        
        // Add to container
        this.container.appendChild(this.fab);
        this.container.appendChild(this.panel);
        
        // Add to document
        document.body.appendChild(this.container);
        
        // Apply position
        this.updatePosition();
    }

    /**
     * Render the panel content
     */
    renderPanel() {
        const navTarget = this.resolvedTargets.navigation;
        const volTarget = this.resolvedTargets.volume;
        
        const navName = navTarget ? navTarget.name : 'Not set';
        const volName = volTarget ? volTarget.name : 'Not set';
        
        const sceneDisplay = this.activeSceneName 
            ? `<span class="scene-indicator" title="Using CEC config from profile">${Helpers.escapeHtml(this.activeSceneName)}</span>`
            : '';
        
        return `
            <div class="cec-tray-header">
                <div class="cec-tray-header-targets">
                    <div class="cec-target-group">
                        <span class="cec-target-label">Nav</span>
                        <button class="cec-header-target-btn" data-target="navigation" title="Navigation target: ${Helpers.escapeHtml(navName)}">
                            <svg class="icon icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"/>
                            </svg>
                            <span class="target-abbrev">${Helpers.escapeHtml(this.abbreviateName(navName))}</span>
                        </button>
                    </div>
                    <div class="cec-target-group">
                        <span class="cec-target-label">Vol</span>
                        <button class="cec-header-target-btn" data-target="volume" title="Volume target: ${Helpers.escapeHtml(volName)}">
                            <svg class="icon icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                                <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
                            </svg>
                            <span class="target-abbrev">${Helpers.escapeHtml(this.abbreviateName(volName))}</span>
                        </button>
                    </div>
                </div>
                <div class="cec-tray-actions">
                    <button class="cec-tray-dashboard-btn" title="Pin to dashboard">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="3" width="18" height="18" rx="2"/>
                            <line x1="9" y1="3" x2="9" y2="21"/>
                            <line x1="15" y1="3" x2="15" y2="21"/>
                            <line x1="3" y1="9" x2="21" y2="9"/>
                            <line x1="3" y1="15" x2="21" y2="15"/>
                        </svg>
                    </button>
                    <button class="cec-tray-close-btn" title="Close">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/>
                            <line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="cec-tray-section">
                <div class="cec-tray-section-title">Power</div>
                <div class="cec-tray-btn-row">
                    <button class="cec-tray-cmd-btn power-on" data-action="power" data-cmd="power_on" title="Power On">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"/>
                            <line x1="12" y1="6" x2="12" y2="12"/>
                        </svg>
                        <span>On</span>
                    </button>
                    <button class="cec-tray-cmd-btn power-off" data-action="power" data-cmd="power_off" title="Power Off">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M18.36 6.64a9 9 0 1 1-12.73 0"/>
                            <line x1="12" y1="2" x2="12" y2="12"/>
                        </svg>
                        <span>Off</span>
                    </button>
                </div>
            </div>
            
            <div class="cec-tray-section">
                <div class="cec-tray-section-title">Navigation</div>
                <!-- D-pad for desktop (visible on desktop, hidden on mobile) -->
                <div class="cec-tray-dpad desktop-only" id="cec-dpad">
                    <button class="cec-tray-cmd-btn dpad-up" data-action="nav" data-cmd="up" title="Up">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="18 15 12 9 6 15"/>
                        </svg>
                    </button>
                    <button class="cec-tray-cmd-btn dpad-left" data-action="nav" data-cmd="left" title="Left">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="15 18 9 12 15 6"/>
                        </svg>
                    </button>
                    <button class="cec-tray-cmd-btn dpad-center" data-action="nav" data-cmd="select" title="Select/OK">OK</button>
                    <button class="cec-tray-cmd-btn dpad-right" data-action="nav" data-cmd="right" title="Right">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="9 18 15 12 9 6"/>
                        </svg>
                    </button>
                    <button class="cec-tray-cmd-btn dpad-down" data-action="nav" data-cmd="down" title="Down">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="6 9 12 15 18 9"/>
                        </svg>
                    </button>
                </div>
                <!-- Trackpad for mobile (visible on mobile, hidden on desktop) -->
                <div class="cec-trackpad mobile-only" id="cec-trackpad">
                    <div class="trackpad-surface">
                        <div class="trackpad-hint">Swipe to navigate<br>Tap to select</div>
                        <div class="trackpad-feedback"></div>
                    </div>
                </div>
                <div class="cec-tray-btn-row nav-secondary">
                    <button class="cec-tray-cmd-btn" data-action="nav" data-cmd="menu" title="Menu">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="3" y1="12" x2="21" y2="12"/>
                            <line x1="3" y1="6" x2="21" y2="6"/>
                            <line x1="3" y1="18" x2="21" y2="18"/>
                        </svg>
                        <span>Menu</span>
                    </button>
                    <button class="cec-tray-cmd-btn" data-action="nav" data-cmd="back" title="Back">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="19" y1="12" x2="5" y2="12"/>
                            <polyline points="12 19 5 12 12 5"/>
                        </svg>
                        <span>Back</span>
                    </button>
                    <button class="cec-tray-cmd-btn" data-action="nav" data-cmd="home" title="Home">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                            <polyline points="9 22 9 12 15 12 15 22"/>
                        </svg>
                        <span>Home</span>
                    </button>
                </div>
            </div>
            
            <div class="cec-tray-section">
                <div class="cec-tray-section-title">Playback</div>
                <div class="cec-tray-btn-row playback-row">
                    <button class="cec-tray-cmd-btn" data-action="playback" data-cmd="previous" title="Previous">⏮</button>
                    <button class="cec-tray-cmd-btn" data-action="playback" data-cmd="rewind" title="Rewind">⏪</button>
                    <button class="cec-tray-cmd-btn play-btn" data-action="playback" data-cmd="play" title="Play">▶</button>
                    <button class="cec-tray-cmd-btn" data-action="playback" data-cmd="pause" title="Pause">⏸</button>
                    <button class="cec-tray-cmd-btn" data-action="playback" data-cmd="stop" title="Stop">⏹</button>
                    <button class="cec-tray-cmd-btn" data-action="playback" data-cmd="fast_forward" title="Fast Forward">⏩</button>
                    <button class="cec-tray-cmd-btn" data-action="playback" data-cmd="next" title="Next">⏭</button>
                </div>
            </div>
            
            <div class="cec-tray-section">
                <div class="cec-tray-section-title">Volume</div>
                <div class="cec-tray-btn-row volume-row">
                    <button class="cec-tray-cmd-btn vol-btn" data-action="volume" data-cmd="volume_down" title="Volume Down">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                        </svg>
                        <span>−</span>
                    </button>
                    <button class="cec-tray-cmd-btn vol-btn" data-action="volume" data-cmd="mute" title="Mute">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                            <line x1="23" y1="9" x2="17" y2="15"/>
                            <line x1="17" y1="9" x2="23" y2="15"/>
                        </svg>
                        <span>Mute</span>
                    </button>
                    <button class="cec-tray-cmd-btn vol-btn" data-action="volume" data-cmd="volume_up" title="Volume Up">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
                            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"/>
                        </svg>
                        <span>+</span>
                    </button>
                </div>
            </div>
            
            <div class="cec-tray-footer">
                <div class="cec-tray-section-header">
                    <span class="cec-tray-section-title">Macros</span>
                    <button class="cec-tray-edit-macros-btn" title="Edit Macros">
                        <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                        </svg>
                    </button>
                </div>
                <div class="cec-tray-macros" id="cec-tray-macros">
                    ${this.renderMacroButtons()}
                </div>
            </div>
        `;
    }
    
    /**
     * Abbreviate a device name for compact header display
     */
    abbreviateName(name) {
        if (!name || name === 'Not set' || name === 'Not detected') return '—';
        // Shorten common words
        let abbrev = name
            .replace(/Living Room/i, 'LR')
            .replace(/Bedroom/i, 'BR')
            .replace(/Kitchen/i, 'Kit')
            .replace(/Output/i, 'Out')
            .replace(/Input/i, 'In')
            .replace(/Television/i, 'TV')
            .replace(/Soundbar/i, 'SB')
            .replace(/Receiver/i, 'Rcvr');
        // Truncate if still too long
        if (abbrev.length > 8) {
            abbrev = abbrev.substring(0, 7) + '…';
        }
        return abbrev;
    }

    /**
     * Render macro buttons
     */
    renderMacroButtons() {
        if (!this.macros || this.macros.length === 0) {
            return `<span class="macros-empty">No macros saved</span>`;
        }
        
        // Show up to 4 macros as quick buttons
        const displayMacros = this.macros.slice(0, 4);
        
        return displayMacros.map(macro => `
            <div class="cec-tray-macro-item">
                <button class="cec-tray-macro-btn" data-macro-id="${macro.id}" title="${Helpers.escapeHtml(macro.name)}">
                    <span class="macro-icon">${macro.icon || '⚡'}</span>
                    <span class="macro-name">${Helpers.escapeHtml(macro.name)}</span>
                </button>
                <button class="btn-icon btn-api-copy macro-api-btn" data-macro-id="${macro.id}" data-macro-name="${Helpers.escapeHtml(macro.name)}" title="Get API endpoint">
                    <svg class="icon icon-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                    </svg>
                </button>
            </div>
        `).join('') + (this.macros.length > 4 ? `
            <button class="cec-tray-macro-more" title="View all macros">
                +${this.macros.length - 4} more
            </button>
        ` : '');
    }

    /**
     * Load macros from API
     */
    async loadMacros() {
        try {
            const response = await api.getMacros();
            if (response?.success) {
                this.macros = response.data?.macros || [];
                this.updateMacroButtons();
            }
        } catch (error) {
            console.warn('Failed to load macros:', error);
        }
    }

    /**
     * Update macro buttons in the tray
     */
    updateMacroButtons() {
        const container = this.panel.querySelector('#cec-tray-macros');
        if (container) {
            container.innerHTML = this.renderMacroButtons();
        }
    }

    /**
     * Execute a macro
     */
    async executeMacro(macroId) {
        const macro = this.macros.find(m => m.id === macroId);
        const name = macro?.name || macroId;
        
        try {
            toast.info(`Running "${name}"...`);
            const response = await api.executeMacro(macroId);
            
            if (response?.success) {
                toast.success(`"${name}" completed`);
            } else {
                toast.error(response?.error || 'Macro failed');
            }
        } catch (error) {
            console.error('Macro execution error:', error);
            toast.error('Macro failed');
        }
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // FAB click to toggle
        this.fab.addEventListener('click', () => this.toggle());
        
        // Close button
        this.panel.addEventListener('click', (e) => {
            if (e.target.closest('.cec-tray-close-btn')) {
                this.collapse();
            }
        });
        
        // Dashboard pin button (toggles pin state)
        this.panel.addEventListener('click', (e) => {
            if (e.target.closest('.cec-tray-dashboard-btn')) {
                this.toggleDashboardPin();
            }
        });
        
        // Target selection buttons (both old and new header style)
        this.panel.addEventListener('click', (e) => {
            const targetBtn = e.target.closest('.cec-target-btn, .cec-header-target-btn');
            if (targetBtn) {
                const targetType = targetBtn.dataset.target;
                this.showTargetSelector(targetType, targetBtn);
            }
        });
        
        // Command buttons
        this.panel.addEventListener('click', (e) => {
            const cmdBtn = e.target.closest('.cec-tray-cmd-btn');
            if (cmdBtn) {
                const action = cmdBtn.dataset.action;
                const cmd = cmdBtn.dataset.cmd;
                this.executeCommand(action, cmd);
            }
        });
        
        // Macro buttons
        this.panel.addEventListener('click', (e) => {
            const macroBtn = e.target.closest('.cec-tray-macro-btn');
            if (macroBtn) {
                const macroId = macroBtn.dataset.macroId;
                this.executeMacro(macroId);
            }
        });
        
        // Macro API copy buttons
        this.panel.addEventListener('click', (e) => {
            const apiBtn = e.target.closest('.macro-api-btn');
            if (apiBtn) {
                e.stopPropagation();
                const macroId = apiBtn.dataset.macroId;
                const macroName = apiBtn.dataset.macroName;
                if (window.apiCopy) {
                    window.apiCopy.showMacro(macroId, macroName);
                } else {
                    toast.error('API copy utility not loaded');
                }
            }
        });
        
        // Edit macros button
        this.panel.addEventListener('click', (e) => {
            if (e.target.closest('.cec-tray-edit-macros-btn') || e.target.closest('.cec-tray-macro-more')) {
                if (typeof cecMacroEditor !== 'undefined') {
                    cecMacroEditor.open();
                }
            }
        });
        
        // Handle escape key - close panel
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isExpanded) {
                this.collapse();
            }
        });
        
        // Handle window resize for pinned state
        window.addEventListener('resize', () => {
            if (this.isPinned && window.innerWidth < 1024) {
                // Unpin on mobile
                this.isPinned = false;
                this.container.classList.remove('pinned');
                this.savePinnedState();
            }
        });
    }

    /**
     * Handle active scene change
     */
    async onActiveSceneChanged(scene) {
        if (scene && scene.id) {
            try {
                // Load CEC config for this scene
                const result = await api.getSceneCecConfig(scene.id);
                if (result.success && result.cec_config) {
                    this.activeSceneConfig = result.cec_config;
                    this.activeSceneName = scene.name;
                    this.container.classList.add('scene-active');
                } else {
                    this.clearSceneConfig();
                }
            } catch (error) {
                console.warn('Failed to load scene CEC config:', error);
                this.clearSceneConfig();
            }
        } else {
            this.clearSceneConfig();
        }
        
        this.updateAutoTargets();
        this.updateSceneIndicator();
    }
    
    /**
     * Clear active scene configuration
     */
    clearSceneConfig() {
        this.activeSceneConfig = null;
        this.activeSceneName = null;
        this.container.classList.remove('scene-active');
    }
    
    /**
     * Update scene indicator in the tray header
     */
    updateSceneIndicator() {
        const indicator = this.panel.querySelector('.scene-indicator');
        if (indicator) {
            if (this.activeSceneName) {
                indicator.textContent = this.activeSceneName;
                indicator.style.display = 'block';
            } else {
                indicator.style.display = 'none';
            }
        }
    }

    /**
     * Update auto-detected targets based on current routing or scene config
     */
    updateAutoTargets() {
        // If we have an active scene with CEC config, use it
        if (this.activeSceneConfig && !this.activeSceneConfig.auto_resolved) {
            this.applySceneCecConfig();
            return;
        }
        
        // Get current routing
        const routing = state.routing || {};
        
        // Find the primary output (Output 1 by default, or first connected)
        let primaryOutput = 1;
        for (let o = 1; o <= 8; o++) {
            const output = state.outputs[o];
            if (output && output.displayConnected) {
                primaryOutput = o;
                break;
            }
        }
        
        // Get the input routed to primary output
        const primaryInput = routing[primaryOutput] || 1;
        const inputName = state.getInputName(primaryInput);
        
        // Resolve navigation target
        if (this.targets.navigation.type === 'auto') {
            this.resolvedTargets.navigation = {
                type: 'input',
                port: primaryInput,
                name: inputName
            };
        } else {
            const port = this.targets.navigation.port;
            const name = this.targets.navigation.type === 'input' 
                ? state.getInputName(port)
                : state.getOutputName(port);
            this.resolvedTargets.navigation = {
                type: this.targets.navigation.type,
                port: port,
                name: name
            };
        }
        
        // Resolve playback target (same as navigation by default)
        if (this.targets.playback.type === 'auto') {
            this.resolvedTargets.playback = { ...this.resolvedTargets.navigation };
        } else {
            const port = this.targets.playback.port;
            const name = this.targets.playback.type === 'input' 
                ? state.getInputName(port)
                : state.getOutputName(port);
            this.resolvedTargets.playback = {
                type: this.targets.playback.type,
                port: port,
                name: name
            };
        }
        
        // Resolve volume target
        // Priority: 
        // 1. Output with ARC enabled (soundbar/receiver) - doesn't need displayConnected
        // 2. Primary connected output (TV that may handle audio)
        // 3. Fall back to the input device (some sources have volume control)
        if (this.targets.volume.type === 'auto') {
            let volumeTarget = null;
            
            // First, look for any output with ARC enabled (audio device like soundbar)
            for (let o = 1; o <= 8; o++) {
                const output = state.outputs[o];
                if (output && output.arcEnabled) {
                    volumeTarget = {
                        type: 'output',
                        port: o,
                        name: state.getOutputName(o)
                    };
                    break;
                }
            }
            
            // If no ARC output found, use the primary connected output
            if (!volumeTarget) {
                volumeTarget = {
                    type: 'output',
                    port: primaryOutput,
                    name: state.getOutputName(primaryOutput)
                };
            }
            
            this.resolvedTargets.volume = volumeTarget;
        } else {
            const port = this.targets.volume.port;
            const name = this.targets.volume.type === 'input' 
                ? state.getInputName(port)
                : state.getOutputName(port);
            this.resolvedTargets.volume = {
                type: this.targets.volume.type,
                port: port,
                name: name
            };
        }
        
        // Clear scene-based power targets when not using scene config
        this.resolvedTargets.power_on = [];
        this.resolvedTargets.power_off = [];
        
        // Update panel display if expanded
        if (this.isExpanded) {
            this.updateTargetDisplay();
        }
        
        // Refresh widget if pinned (for dynamic updates)
        this.refreshDashboardWidget();
    }
    
    /**
     * Refresh the dashboard widget if it's pinned
     */
    refreshDashboardWidget() {
        if (window.dashboardManager && window.dashboardManager.isWidgetPinned('cec-remote')) {
            window.dashboardManager.refreshWidget('cec-remote');
        }
    }
    
    /**
     * Called by DashboardManager when pin state changes
     */
    onDashboardPinChange(isPinned) {
        // Hide/show the FAB and tray based on pin state (all viewport modes)
        if (this.fab) {
            if (isPinned) {
                this.fab.style.display = 'none';
                // Also collapse and hide the tray if open
                if (this.isExpanded) {
                    this.collapse();
                }
                if (this.tray) {
                    this.tray.style.display = 'none';
                }
            } else {
                this.fab.style.display = '';
                if (this.tray) {
                    this.tray.style.display = '';
                }
            }
        }
    }
    
    /**
     * Apply CEC configuration from active scene
     */
    applySceneCecConfig() {
        const config = this.activeSceneConfig;
        if (!config) return;
        
        // Resolve navigation targets
        const navTargets = config.nav_targets || [];
        if (navTargets.length > 0) {
            const parsed = this.parseTargetString(navTargets[0]);
            if (parsed) {
                this.resolvedTargets.navigation = {
                    type: parsed.type,
                    port: parsed.port,
                    name: this.getTargetName(parsed)
                };
            }
        } else {
            this.resolvedTargets.navigation = null;
        }
        
        // Resolve playback targets
        const playbackTargets = config.playback_targets || [];
        if (playbackTargets.length > 0) {
            const parsed = this.parseTargetString(playbackTargets[0]);
            if (parsed) {
                this.resolvedTargets.playback = {
                    type: parsed.type,
                    port: parsed.port,
                    name: this.getTargetName(parsed)
                };
            }
        } else {
            // Default to navigation target
            this.resolvedTargets.playback = this.resolvedTargets.navigation 
                ? { ...this.resolvedTargets.navigation } 
                : null;
        }
        
        // Resolve volume targets
        const volumeTargets = config.volume_targets || [];
        if (volumeTargets.length > 0) {
            const parsed = this.parseTargetString(volumeTargets[0]);
            if (parsed) {
                this.resolvedTargets.volume = {
                    type: parsed.type,
                    port: parsed.port,
                    name: this.getTargetName(parsed)
                };
            }
        } else {
            this.resolvedTargets.volume = null;
        }
        
        // Store power targets for power commands
        this.resolvedTargets.power_on = (config.power_on_targets || [])
            .map(t => this.parseTargetString(t))
            .filter(t => t !== null)
            .map(parsed => ({
                type: parsed.type,
                port: parsed.port,
                name: this.getTargetName(parsed)
            }));
        
        this.resolvedTargets.power_off = (config.power_off_targets || [])
            .map(t => this.parseTargetString(t))
            .filter(t => t !== null)
            .map(parsed => ({
                type: parsed.type,
                port: parsed.port,
                name: this.getTargetName(parsed)
            }));
        
        // Update panel display if expanded
        if (this.isExpanded) {
            this.updateTargetDisplay();
        }
    }
    
    /**
     * Parse a target string like "input_3" or "output_2"
     */
    parseTargetString(target) {
        if (!target || typeof target !== 'string') return null;
        const parts = target.split('_');
        if (parts.length !== 2) return null;
        const port = parseInt(parts[1], 10);
        if (isNaN(port)) return null;
        return { type: parts[0], port };
    }
    
    /**
     * Get display name for a parsed target
     */
    getTargetName(parsed) {
        if (parsed.type === 'input') {
            return state.getInputName(parsed.port) || `Input ${parsed.port}`;
        } else {
            return state.getOutputName(parsed.port) || `Output ${parsed.port}`;
        }
    }

    /**
     * Update the target display in the panel
     */
    updateTargetDisplay() {
        const navBtn = this.panel.querySelector('[data-target="navigation"]');
        const volBtn = this.panel.querySelector('[data-target="volume"]');
        
        if (navBtn) {
            const navName = this.resolvedTargets.navigation?.name || 'Not detected';
            navBtn.querySelector('.target-name').textContent = navName;
        }
        
        if (volBtn) {
            const volName = this.resolvedTargets.volume?.name || 'Not detected';
            volBtn.querySelector('.target-name').textContent = volName;
        }
        
        // Update scene indicator
        this.updateSceneIndicator();
        
        // Also refresh widget if pinned to dashboard
        if (window.dashboardManager && window.dashboardManager.isWidgetPinned('cec-remote')) {
            window.dashboardManager.refreshWidget('cec-remote');
        }
    }

    /**
     * Show target selector dropdown
     */
    showTargetSelector(targetType, anchorElement) {
        // Remove any existing selector
        this.hideTargetSelector();
        
        const selector = document.createElement('div');
        selector.className = 'cec-target-selector';
        selector.innerHTML = this.renderTargetSelector(targetType);
        
        // Position near anchor
        const rect = anchorElement.getBoundingClientRect();
        selector.style.position = 'fixed';
        selector.style.top = `${rect.bottom + 4}px`;
        selector.style.left = `${rect.left}px`;
        selector.style.zIndex = '1001';
        
        document.body.appendChild(selector);
        this.activeSelector = selector;
        
        // Attach selector events
        selector.addEventListener('click', (e) => {
            const option = e.target.closest('.target-option');
            if (option) {
                const type = option.dataset.type;
                const port = option.dataset.port ? parseInt(option.dataset.port) : null;
                this.setTarget(targetType, type, port);
                this.hideTargetSelector();
            }
        });
        
        // Close on outside click (delayed to avoid immediate close)
        setTimeout(() => {
            const closeHandler = (e) => {
                if (!selector.contains(e.target) && !anchorElement.contains(e.target)) {
                    this.hideTargetSelector();
                    document.removeEventListener('click', closeHandler);
                }
            };
            document.addEventListener('click', closeHandler);
        }, 10);
    }

    /**
     * Render target selector options
     */
    renderTargetSelector(targetType) {
        const currentTarget = this.targets[targetType];
        const isAuto = currentTarget.type === 'auto';
        
        let html = `
            <div class="target-selector-header">Select ${targetType} target</div>
            <div class="target-option ${isAuto ? 'selected' : ''}" data-type="auto">
                <span class="target-option-indicator">●</span>
                <span>Auto-detect</span>
            </div>
            <div class="target-selector-divider"></div>
            <div class="target-selector-group-title">Inputs</div>
        `;
        
        // Add input options
        for (let i = 1; i <= 8; i++) {
            const name = state.getInputName(i);
            const isSelected = currentTarget.type === 'input' && currentTarget.port === i;
            html += `
                <div class="target-option ${isSelected ? 'selected' : ''}" data-type="input" data-port="${i}">
                    <span class="target-option-indicator">●</span>
                    <span>${Helpers.escapeHtml(name)}</span>
                </div>
            `;
        }
        
        // Add output options for volume
        if (targetType === 'volume') {
            html += `
                <div class="target-selector-divider"></div>
                <div class="target-selector-group-title">Outputs</div>
            `;
            
            for (let o = 1; o <= 8; o++) {
                const name = state.getOutputName(o);
                const isSelected = currentTarget.type === 'output' && currentTarget.port === o;
                html += `
                    <div class="target-option ${isSelected ? 'selected' : ''}" data-type="output" data-port="${o}">
                        <span class="target-option-indicator">●</span>
                        <span>${Helpers.escapeHtml(name)}</span>
                    </div>
                `;
            }
        }
        
        return html;
    }

    /**
     * Hide target selector
     */
    hideTargetSelector() {
        if (this.activeSelector) {
            this.activeSelector.remove();
            this.activeSelector = null;
        }
    }

    /**
     * Set a target
     */
    setTarget(targetType, type, port) {
        this.targets[targetType] = { type, port };
        this.updateAutoTargets();
        
        toast.success(`${targetType.charAt(0).toUpperCase() + targetType.slice(1)} target updated`);
    }

    /**
     * Execute a CEC command
     */
    async executeCommand(action, cmd) {
        let target;
        
        switch (action) {
            case 'nav':
                target = this.resolvedTargets.navigation;
                break;
            case 'playback':
                target = this.resolvedTargets.playback;
                break;
            case 'volume':
                target = this.resolvedTargets.volume;
                break;
            case 'power':
                // Power commands go to both input and volume targets
                await this.executePowerCommand(cmd);
                return;
            default:
                console.warn('Unknown CEC action:', action);
                return;
        }
        
        if (!target) {
            toast.error('No target device configured');
            return;
        }
        
        try {
            const result = await api.sendCecCommand(target.type, target.port, cmd);
            if (result?.success) {
                // Visual feedback on button
                toast.success(`${cmd.replace('_', ' ')} → ${target.name}`);
            } else {
                toast.error(`CEC failed: ${result?.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('CEC command error:', error);
            toast.error(`CEC error: ${error.message}`);
        }
    }

    /**
     * Execute power command to configured targets
     */
    async executePowerCommand(cmd) {
        let targets = [];
        
        // Check if we have scene-based power targets
        if (cmd === 'power_on' && this.resolvedTargets.power_on?.length > 0) {
            targets = [...this.resolvedTargets.power_on];
        } else if (cmd === 'power_off' && this.resolvedTargets.power_off?.length > 0) {
            targets = [...this.resolvedTargets.power_off];
        } else {
            // Fall back to default behavior: nav target + volume target
            const navTarget = this.resolvedTargets.navigation;
            const volTarget = this.resolvedTargets.volume;
            
            // Add navigation target (input device)
            if (navTarget) {
                targets.push(navTarget);
            }
            
            // Add volume target if different
            if (volTarget && 
                (volTarget.type !== navTarget?.type || volTarget.port !== navTarget?.port)) {
                targets.push(volTarget);
            }
        }
        
        if (targets.length === 0) {
            toast.error('No target devices configured');
            return;
        }
        
        // Execute commands
        const results = await Promise.allSettled(
            targets.map(t => api.sendCecCommand(t.type, t.port, cmd))
        );
        
        const succeeded = results.filter(r => r.status === 'fulfilled' && r.value?.success).length;
        const failed = targets.length - succeeded;
        
        if (failed === 0) {
            toast.success(`${cmd.replace('_', ' ')} sent to ${targets.length} device(s)`);
        } else if (succeeded > 0) {
            toast.warning(`${cmd.replace('_', ' ')}: ${succeeded} succeeded, ${failed} failed`);
        } else {
            toast.error(`${cmd.replace('_', ' ')} failed`);
        }
    }

    /**
     * Toggle expanded state
     */
    toggle() {
        if (this.isExpanded) {
            this.collapse();
        } else {
            this.expand();
        }
    }

    /**
     * Update the dashboard pin button to show correct state
     */
    updateDashboardButton() {
        const btn = this.panel?.querySelector('.cec-tray-dashboard-btn');
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
     * Expand the panel
     */
    expand() {
        this.isExpanded = true;
        this.container.classList.add('expanded');
        this.panel.innerHTML = this.renderPanel();
        this.updateDashboardButton();
        this.updateAutoTargets();
        this.loadMacros();  // Load macros when tray expands
        this.initTrackpad();  // Initialize trackpad gestures
    }
    
    /**
     * Initialize trackpad gesture handling
     */
    initTrackpad() {
        const trackpad = this.panel.querySelector('#cec-trackpad');
        if (!trackpad) return;
        
        const surface = trackpad.querySelector('.trackpad-surface');
        const feedback = trackpad.querySelector('.trackpad-feedback');
        
        let startX = 0;
        let startY = 0;
        let startTime = 0;
        let isActive = false;
        
        const SWIPE_THRESHOLD = 30;  // Minimum distance for swipe
        const TAP_THRESHOLD = 10;    // Max movement for tap
        const TAP_TIME = 300;        // Max time for tap (ms)
        
        const showFeedback = (direction) => {
            feedback.className = 'trackpad-feedback';
            feedback.classList.add('active', direction);
            setTimeout(() => {
                feedback.classList.remove('active', direction);
            }, 200);
        };
        
        const handleGestureEnd = (endX, endY) => {
            if (!isActive) return;
            isActive = false;
            
            const deltaX = endX - startX;
            const deltaY = endY - startY;
            const deltaTime = Date.now() - startTime;
            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
            
            // Check for tap (short time, minimal movement)
            if (deltaTime < TAP_TIME && distance < TAP_THRESHOLD) {
                showFeedback('tap');
                this.sendNavCommand('select');
                return;
            }
            
            // Check for swipe
            if (distance >= SWIPE_THRESHOLD) {
                const absX = Math.abs(deltaX);
                const absY = Math.abs(deltaY);
                
                if (absX > absY) {
                    // Horizontal swipe
                    if (deltaX > 0) {
                        showFeedback('right');
                        this.sendNavCommand('right');
                    } else {
                        showFeedback('left');
                        this.sendNavCommand('left');
                    }
                } else {
                    // Vertical swipe
                    if (deltaY > 0) {
                        showFeedback('down');
                        this.sendNavCommand('down');
                    } else {
                        showFeedback('up');
                        this.sendNavCommand('up');
                    }
                }
            }
        };
        
        // Touch events
        surface.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
            startTime = Date.now();
            isActive = true;
            surface.classList.add('touching');
        }, { passive: false });
        
        surface.addEventListener('touchend', (e) => {
            surface.classList.remove('touching');
            if (e.changedTouches.length > 0) {
                const touch = e.changedTouches[0];
                handleGestureEnd(touch.clientX, touch.clientY);
            }
        });
        
        surface.addEventListener('touchcancel', () => {
            surface.classList.remove('touching');
            isActive = false;
        });
        
        // Mouse events (for desktop testing)
        surface.addEventListener('mousedown', (e) => {
            startX = e.clientX;
            startY = e.clientY;
            startTime = Date.now();
            isActive = true;
            surface.classList.add('touching');
        });
        
        surface.addEventListener('mouseup', (e) => {
            surface.classList.remove('touching');
            handleGestureEnd(e.clientX, e.clientY);
        });
        
        surface.addEventListener('mouseleave', () => {
            surface.classList.remove('touching');
            isActive = false;
        });
    }
    
    /**
     * Send a navigation command via CEC
     */
    sendNavCommand(cmd) {
        const target = this.resolvedTargets.navigation;
        if (!target) {
            toast.warning('No navigation target selected');
            return;
        }
        this.sendCommand('nav', cmd);
    }

    /**
     * Collapse the panel
     */
    collapse() {
        this.isExpanded = false;
        this.container.classList.remove('expanded');
        this.hideTargetSelector();
    }

    /**
     * Update container position based on settings
     */
    updatePosition() {
        // Remove all position classes
        this.container.classList.remove(
            'position-bottom-right',
            'position-bottom-left',
            'position-top-right',
            'position-panel-right'
        );
        
        // Add current position class
        this.container.classList.add(`position-${this.position}`);
    }

    /**
     * Destroy the tray
     */
    destroy() {
        if (this.container) {
            this.container.remove();
        }
    }
}

// Global instance
let cecTray = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for state to be initialized
    setTimeout(() => {
        cecTray = new CECTray();
        // Expose on window for settings-panel access
        window.cecTray = cecTray;
    }, 100);
});
