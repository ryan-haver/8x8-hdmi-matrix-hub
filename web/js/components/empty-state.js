/**
 * OREI Matrix Control - Empty State Component
 * Displays friendly messages when content is unavailable
 */

class EmptyState {
    /**
     * Create an empty state display
     * @param {Object} options - Configuration options
     * @param {string} options.icon - SVG icon or emoji
     * @param {string} options.title - Main message
     * @param {string} options.description - Optional detailed description
     * @param {Object} options.action - Optional action button {label, onClick}
     */
    constructor(options = {}) {
        this.icon = options.icon || '📭';
        this.title = options.title || 'No items found';
        this.description = options.description || '';
        this.action = options.action || null;
    }

    /**
     * Render empty state HTML
     * @returns {string} HTML string
     */
    render() {
        const iconHtml = this.icon.startsWith('<') 
            ? `<div class="empty-state__icon">${this.icon}</div>`
            : `<div class="empty-state__icon" style="font-size: 48px;">${this.icon}</div>`;
        
        const descHtml = this.description 
            ? `<p class="empty-state__description">${this.description}</p>`
            : '';
        
        const actionHtml = this.action
            ? `<div class="empty-state__action">
                 <button class="btn btn-primary btn-sm empty-state__btn">${this.action.label}</button>
               </div>`
            : '';

        return `
            <div class="empty-state">
                ${iconHtml}
                <h3 class="empty-state__title">${this.title}</h3>
                ${descHtml}
                ${actionHtml}
            </div>
        `;
    }

    /**
     * Mount to container and setup event handlers
     * @param {HTMLElement} container - Container element
     */
    mount(container) {
        if (!container) return;
        container.innerHTML = this.render();
        
        if (this.action?.onClick) {
            const btn = container.querySelector('.empty-state__btn');
            if (btn) {
                btn.addEventListener('click', this.action.onClick);
            }
        }
    }

    /**
     * Static presets for common scenarios
     */
    static presets = {
        noScenes: {
            icon: '🎬',
            title: 'No scenes yet',
            description: 'Create your first scene to save your current matrix configuration.',
            action: { label: 'Create Scene' }
        },
        noInputs: {
            icon: '📺',
            title: 'No inputs detected',
            description: 'Connect HDMI sources to see them here.'
        },
        noOutputs: {
            icon: '🖥️',
            title: 'No outputs detected',
            description: 'Connect HDMI displays to see them here.'
        },
        connectionLost: {
            icon: '🔌',
            title: 'Connection lost',
            description: 'Unable to reach the matrix device.',
            action: { label: 'Retry' }
        },
        searchNoResults: {
            icon: '🔍',
            title: 'No results found',
            description: 'Try adjusting your search terms.'
        }
    };

    /**
     * Create from preset
     * @param {string} presetName - Name of preset
     * @param {Object} overrides - Override preset values
     * @returns {EmptyState}
     */
    static fromPreset(presetName, overrides = {}) {
        const preset = EmptyState.presets[presetName] || {};
        return new EmptyState({ ...preset, ...overrides });
    }
}

// Export for use
window.EmptyState = EmptyState;
