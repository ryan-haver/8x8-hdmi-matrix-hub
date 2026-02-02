/**
 * OREI Matrix Control - About Dialog Component
 * Shows application info, version, and system status
 */

class AboutDialog {
    static VERSION = '1.0.0';
    static element = null;

    /**
     * Show the about dialog
     */
    static show() {
        if (AboutDialog.element) {
            AboutDialog.close();
            return;
        }

        const wrapper = document.createElement('div');
        wrapper.innerHTML = AboutDialog.render();
        AboutDialog.element = wrapper.firstElementChild;
        document.body.appendChild(AboutDialog.element);

        // Animate in
        requestAnimationFrame(() => {
            AboutDialog.element.classList.add('about-dialog--visible');
        });

        // Bind events
        AboutDialog.bindEvents();
        
        // Load system info
        AboutDialog.loadSystemInfo();
    }

    /**
     * Render dialog HTML
     */
    static render() {
        return `
            <div class="about-dialog" role="dialog" aria-modal="true" aria-labelledby="about-title">
                <div class="about-dialog__backdrop"></div>
                <div class="about-dialog__content glass-heavy">
                    <button class="btn-icon about-dialog__close" aria-label="Close">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="icon">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                    
                    <div class="about-dialog__hero">
                        <div class="about-dialog__logo">
                            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <rect x="4" y="8" width="40" height="32" rx="4" stroke="currentColor" stroke-width="2"/>
                                <rect x="12" y="16" width="8" height="8" rx="1" fill="currentColor"/>
                                <rect x="28" y="16" width="8" height="8" rx="1" fill="currentColor"/>
                                <rect x="12" y="28" width="8" height="4" rx="1" fill="currentColor" opacity="0.5"/>
                                <rect x="28" y="28" width="8" height="4" rx="1" fill="currentColor" opacity="0.5"/>
                                <path d="M20 20h8M28 24l-8-4" stroke="currentColor" stroke-width="1.5"/>
                            </svg>
                        </div>
                        <h2 id="about-title" class="about-dialog__title">OREI Matrix Control</h2>
                        <p class="about-dialog__version">Version ${AboutDialog.VERSION}</p>
                    </div>
                    
                    <div class="about-dialog__info">
                        <div class="about-dialog__section">
                            <h3>System Status</h3>
                            <div class="about-dialog__status" id="about-status">
                                <div class="about-dialog__status-item">
                                    <span class="about-dialog__status-label">Matrix Connection</span>
                                    <span class="about-dialog__status-value" id="status-matrix">
                                        <span class="spinner spinner--sm"></span>
                                    </span>
                                </div>
                                <div class="about-dialog__status-item">
                                    <span class="about-dialog__status-label">WebSocket</span>
                                    <span class="about-dialog__status-value" id="status-websocket">
                                        <span class="spinner spinner--sm"></span>
                                    </span>
                                </div>
                                <div class="about-dialog__status-item">
                                    <span class="about-dialog__status-label">Model</span>
                                    <span class="about-dialog__status-value" id="status-model">—</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="about-dialog__section">
                            <h3>Credits</h3>
                            <p class="about-dialog__credits">
                                Integration for OREI BK-808 8×8 HDMI Matrix.<br>
                                Built for <a href="https://www.unfoldedcircle.com/" target="_blank" rel="noopener">Unfolded Circle</a> Remote.
                            </p>
                        </div>
                    </div>
                    
                    <div class="about-dialog__footer">
                        <button class="btn btn-secondary about-dialog__keyboard" data-tooltip="Press ? anytime">
                            ⌨️ Keyboard Shortcuts
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Bind event listeners
     */
    static bindEvents() {
        const closeBtn = AboutDialog.element.querySelector('.about-dialog__close');
        const backdrop = AboutDialog.element.querySelector('.about-dialog__backdrop');
        const keyboardBtn = AboutDialog.element.querySelector('.about-dialog__keyboard');

        closeBtn.addEventListener('click', () => AboutDialog.close());
        backdrop.addEventListener('click', () => AboutDialog.close());
        keyboardBtn.addEventListener('click', () => {
            AboutDialog.close();
            KeyboardShortcuts?.showHelp();
        });

        document.addEventListener('keydown', AboutDialog.handleKeydown);
    }

    /**
     * Handle keydown
     */
    static handleKeydown = (e) => {
        if (e.key === 'Escape') {
            AboutDialog.close();
        }
    };

    /**
     * Load system info
     */
    static async loadSystemInfo() {
        // Matrix connection status
        const matrixEl = document.getElementById('status-matrix');
        const wsEl = document.getElementById('status-websocket');
        const modelEl = document.getElementById('status-model');

        try {
            const response = await fetch('/api/status');
            if (response.ok) {
                const data = await response.json();
                if (matrixEl) {
                    matrixEl.innerHTML = '<span class="status-badge status-badge--success">Connected</span>';
                }
                if (modelEl && data.model) {
                    modelEl.textContent = data.model || 'OREI BK-808';
                }
            } else {
                if (matrixEl) {
                    matrixEl.innerHTML = '<span class="status-badge status-badge--error">Disconnected</span>';
                }
            }
        } catch (e) {
            if (matrixEl) {
                matrixEl.innerHTML = '<span class="status-badge status-badge--error">Error</span>';
            }
        }

        // WebSocket status
        if (wsEl) {
            const wsConnected = window.state?.wsStatus === 'connected';
            wsEl.innerHTML = wsConnected 
                ? '<span class="status-badge status-badge--success">Connected</span>'
                : '<span class="status-badge status-badge--warning">Disconnected</span>';
        }
    }

    /**
     * Close the dialog
     */
    static close() {
        if (!AboutDialog.element) return;

        document.removeEventListener('keydown', AboutDialog.handleKeydown);

        AboutDialog.element.classList.remove('about-dialog--visible');
        AboutDialog.element.classList.add('about-dialog--closing');

        setTimeout(() => {
            AboutDialog.element?.remove();
            AboutDialog.element = null;
        }, 200);
    }
}

// Export for use
window.AboutDialog = AboutDialog;
