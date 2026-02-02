/**
 * OREI Matrix Control - Setup Wizard Component
 * Multi-step wizard for device configuration and onboarding
 */

class SetupWizard {
    /**
     * Create a setup wizard
     * @param {Object} options - Configuration options
     * @param {Array} options.steps - Array of step objects {id, title, icon, content, validate}
     * @param {Function} options.onComplete - Callback when wizard completes
     * @param {Function} options.onCancel - Callback when wizard is cancelled
     */
    constructor(options = {}) {
        this.steps = options.steps || [];
        this.onComplete = options.onComplete || (() => {});
        this.onCancel = options.onCancel || (() => {});
        
        this.currentStep = 0;
        this.data = {};
        this.element = null;
    }

    /**
     * Render the wizard HTML
     */
    render() {
        const step = this.steps[this.currentStep];
        const isFirst = this.currentStep === 0;
        const isLast = this.currentStep === this.steps.length - 1;

        return `
            <div class="setup-wizard" role="dialog" aria-modal="true" aria-labelledby="wizard-title">
                <div class="setup-wizard__backdrop"></div>
                <div class="setup-wizard__container glass-heavy">
                    <div class="setup-wizard__header">
                        <h2 id="wizard-title" class="setup-wizard__title">${step.title}</h2>
                        <button class="btn-icon setup-wizard__close" aria-label="Close wizard">
                            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                    
                    <div class="setup-wizard__progress">
                        ${this.renderProgress()}
                    </div>
                    
                    <div class="setup-wizard__content">
                        ${typeof step.content === 'function' ? step.content(this.data) : step.content}
                    </div>
                    
                    <div class="setup-wizard__footer">
                        <button class="btn btn-secondary setup-wizard__back" ${isFirst ? 'style="visibility: hidden"' : ''}>
                            Back
                        </button>
                        <button class="btn btn-accent setup-wizard__next">
                            ${isLast ? 'Finish' : 'Next'}
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render progress indicator
     */
    renderProgress() {
        return this.steps.map((step, index) => {
            let state = 'upcoming';
            if (index < this.currentStep) state = 'complete';
            if (index === this.currentStep) state = 'current';
            
            return `
                <div class="setup-wizard__step setup-wizard__step--${state}" data-step="${index}">
                    <div class="setup-wizard__step-indicator">
                        ${state === 'complete' 
                            ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>'
                            : `<span>${index + 1}</span>`
                        }
                    </div>
                    <span class="setup-wizard__step-label">${step.title}</span>
                </div>
            `;
        }).join('');
    }

    /**
     * Show the wizard
     */
    show() {
        // Create and mount wizard
        const wrapper = document.createElement('div');
        wrapper.innerHTML = this.render();
        this.element = wrapper.firstElementChild;
        document.body.appendChild(this.element);
        
        // Animate in
        requestAnimationFrame(() => {
            this.element.classList.add('setup-wizard--visible');
        });
        
        // Setup event listeners
        this.bindEvents();
        
        // Focus first input
        const firstInput = this.element.querySelector('input, select, textarea');
        if (firstInput) firstInput.focus();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        const closeBtn = this.element.querySelector('.setup-wizard__close');
        const backdrop = this.element.querySelector('.setup-wizard__backdrop');
        const backBtn = this.element.querySelector('.setup-wizard__back');
        const nextBtn = this.element.querySelector('.setup-wizard__next');
        
        closeBtn.addEventListener('click', () => this.cancel());
        backdrop.addEventListener('click', () => this.cancel());
        backBtn.addEventListener('click', () => this.goBack());
        nextBtn.addEventListener('click', () => this.goNext());
        
        // Keyboard support
        this.element.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.cancel();
        });
    }

    /**
     * Go to previous step
     */
    goBack() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.updateView();
        }
    }

    /**
     * Go to next step or complete
     */
    async goNext() {
        const step = this.steps[this.currentStep];
        
        // Collect data from current step
        this.collectStepData();
        
        // Validate if validation function exists
        if (step.validate) {
            const result = await step.validate(this.data);
            if (!result.valid) {
                this.showError(result.message);
                return;
            }
        }
        
        // Check if last step
        if (this.currentStep === this.steps.length - 1) {
            this.complete();
        } else {
            this.currentStep++;
            this.updateView();
        }
    }

    /**
     * Collect data from form inputs in current step
     */
    collectStepData() {
        const content = this.element.querySelector('.setup-wizard__content');
        const inputs = content.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            if (input.name) {
                if (input.type === 'checkbox') {
                    this.data[input.name] = input.checked;
                } else {
                    this.data[input.name] = input.value;
                }
            }
        });
    }

    /**
     * Update the wizard view
     */
    updateView() {
        const step = this.steps[this.currentStep];
        const isFirst = this.currentStep === 0;
        const isLast = this.currentStep === this.steps.length - 1;
        
        // Update title
        this.element.querySelector('.setup-wizard__title').textContent = step.title;
        
        // Update progress
        this.element.querySelector('.setup-wizard__progress').innerHTML = this.renderProgress();
        
        // Update content
        this.element.querySelector('.setup-wizard__content').innerHTML = 
            typeof step.content === 'function' ? step.content(this.data) : step.content;
        
        // Update buttons
        this.element.querySelector('.setup-wizard__back').style.visibility = isFirst ? 'hidden' : 'visible';
        this.element.querySelector('.setup-wizard__next').textContent = isLast ? 'Finish' : 'Next';
        
        // Focus first input
        const firstInput = this.element.querySelector('.setup-wizard__content input, .setup-wizard__content select');
        if (firstInput) firstInput.focus();
    }

    /**
     * Show error message
     */
    showError(message) {
        const content = this.element.querySelector('.setup-wizard__content');
        let errorEl = content.querySelector('.setup-wizard__error');
        
        if (!errorEl) {
            errorEl = document.createElement('div');
            errorEl.className = 'setup-wizard__error';
            content.insertBefore(errorEl, content.firstChild);
        }
        
        errorEl.textContent = message;
        errorEl.classList.add('setup-wizard__error--visible');
        
        setTimeout(() => {
            errorEl.classList.remove('setup-wizard__error--visible');
        }, 3000);
    }

    /**
     * Complete the wizard
     */
    complete() {
        this.collectStepData();
        this.close();
        this.onComplete(this.data);
    }

    /**
     * Cancel and close the wizard
     */
    cancel() {
        this.close();
        this.onCancel();
    }

    /**
     * Close the wizard
     */
    close() {
        if (!this.element) return;
        
        this.element.classList.remove('setup-wizard--visible');
        this.element.classList.add('setup-wizard--closing');
        
        setTimeout(() => {
            this.element?.remove();
            this.element = null;
        }, 200);
    }

    /**
     * Static helper to create connection setup wizard
     */
    static connectionSetup(onComplete) {
        const wizard = new SetupWizard({
            steps: [
                {
                    id: 'connection',
                    title: 'Matrix Connection',
                    content: (data) => `
                        <div class="setup-form">
                            <p class="setup-form__intro">
                                Enter the IP address and port of your OREI HDMI Matrix.
                            </p>
                            <div class="setup-form__field">
                                <label for="host">IP Address</label>
                                <input type="text" id="host" name="host" 
                                       value="${data.host || '192.168.1.100'}" 
                                       placeholder="192.168.1.100"
                                       pattern="^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$">
                            </div>
                            <div class="setup-form__field">
                                <label for="port">Port</label>
                                <input type="number" id="port" name="port" 
                                       value="${data.port || 23}" 
                                       placeholder="23" min="1" max="65535">
                            </div>
                        </div>
                    `,
                    validate: async (data) => {
                        if (!data.host || !/^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(data.host)) {
                            return { valid: false, message: 'Please enter a valid IP address' };
                        }
                        if (!data.port || data.port < 1 || data.port > 65535) {
                            return { valid: false, message: 'Please enter a valid port (1-65535)' };
                        }
                        return { valid: true };
                    }
                },
                {
                    id: 'test',
                    title: 'Test Connection',
                    content: (data) => `
                        <div class="setup-form">
                            <div class="connection-test">
                                <div class="connection-test__status">
                                    <div class="connection-test__spinner"></div>
                                    <p>Testing connection to ${data.host}:${data.port}...</p>
                                </div>
                            </div>
                        </div>
                    `
                },
                {
                    id: 'complete',
                    title: 'Setup Complete',
                    content: () => `
                        <div class="setup-form">
                            <div class="setup-complete">
                                <div class="setup-complete__icon">✓</div>
                                <h3>Connection Successful!</h3>
                                <p>Your OREI Matrix is ready to use.</p>
                            </div>
                        </div>
                    `
                }
            ],
            onComplete
        });
        
        wizard.show();
        return wizard;
    }
}

// Export for use
window.SetupWizard = SetupWizard;
