/**
 * Dashboard Card Renderers (Phase 7)
 * Each card type has its own compact renderer function.
 */

window.dashboardCardRenderers = {
    /**
     * Render a profile recall card
     * @param {Object} card - Card data with type:'profile' and id
     * @param {Object} context - Provides state and action helpers
     */
    profile: function(card, context) {
        const profile = context.state.profiles.find(p => p.id === card.id);
        if (!profile) return ''; // Skip missing profiles

        return `
            <div class="dashboard-card dashboard-card-profile" data-card-key="${card.type}:${card.id}">
                <div class="dashboard-card-header">
                    <span class="dashboard-card-drag-handle" title="Drag to reorder">⋮⋮</span>
                    <span class="dashboard-card-icon">${profile.icon || '🎬'}</span>
                    <span class="dashboard-card-title">${Helpers.escapeHtml(profile.name)}</span>
                    <button class="dashboard-card-unpin btn-icon" data-type="profile" data-id="${profile.id}" title="Remove from dashboard">
                        <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="dashboard-card-body">
                    <button class="btn btn-sm btn-primary dashboard-card-action" data-type="profile" data-id="${profile.id}">
                        Recall
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Render a hardware preset recall card
     * @param {Object} card - Card data with type:'preset' and id (preset number)
     * @param {Object} context - Provides state and action helpers
     */
    preset: function(card, context) {
        const presetNum = parseInt(card.id);
        const preset = context.state.presets[presetNum] || { name: `Preset ${presetNum}` };

        return `
            <div class="dashboard-card dashboard-card-preset" data-card-key="${card.type}:${card.id}">
                <div class="dashboard-card-header">
                    <span class="dashboard-card-drag-handle" title="Drag to reorder">⋮⋮</span>
                    <span class="dashboard-card-icon">⚡</span>
                    <span class="dashboard-card-title">${Helpers.escapeHtml(preset.name)}</span>
                    <button class="dashboard-card-unpin btn-icon" data-type="preset" data-id="${card.id}" title="Remove from dashboard">
                        <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="dashboard-card-body">
                    <button class="btn btn-sm btn-primary dashboard-card-action" data-type="preset" data-id="${card.id}">
                        Recall
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Render a system shortcut card
     * @param {Object} card - Card data with type:'system_shortcut' and id
     * @param {Object} context - Provides state and action helpers
     */
    system_shortcut: function(card, context) {
        const shortcut = context.state.systemShortcuts.find(s => s.id === card.id);
        if (!shortcut) return ''; // Skip missing shortcuts

        return `
            <div class="dashboard-card dashboard-card-shortcut" data-card-key="${card.type}:${card.id}">
                <div class="dashboard-card-header">
                    <span class="dashboard-card-drag-handle" title="Drag to reorder">⋮⋮</span>
                    <span class="dashboard-card-icon">${shortcut.icon || '⚡'}</span>
                    <span class="dashboard-card-title">${Helpers.escapeHtml(shortcut.name)}</span>
                    <button class="dashboard-card-unpin btn-icon" data-type="system_shortcut" data-id="${shortcut.id}" title="Remove from dashboard">
                        <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="dashboard-card-body">
                    <button class="btn btn-sm btn-primary dashboard-card-action" data-type="system_shortcut" data-id="${shortcut.id}">
                        Execute
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Render a CEC macro card
     * @param {Object} card - Card data with type:'macro' and id
     * @param {Object} context - Provides state and action helpers
     */
    macro: function(card, context) {
        const macro = context.state.cecMacros.find(m => m.id === card.id);
        if (!macro) return ''; // Skip missing macros

        return `
            <div class="dashboard-card dashboard-card-macro" data-card-key="${card.type}:${card.id}">
                <div class="dashboard-card-header">
                    <span class="dashboard-card-drag-handle" title="Drag to reorder">⋮⋮</span>
                    <span class="dashboard-card-icon">${macro.icon || '⚡'}</span>
                    <span class="dashboard-card-title">${Helpers.escapeHtml(macro.name)}</span>
                    <button class="dashboard-card-unpin btn-icon" data-type="macro" data-id="${macro.id}" title="Remove from dashboard">
                        <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="dashboard-card-body">
                    <button class="btn btn-sm btn-primary dashboard-card-action" data-type="macro" data-id="${macro.id}">
                        Run
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Render a Phase 8 Scene card (unified scene with profiles + system actions + macros)
     * @param {Object} card - Card data with type:'scene' and id
     * @param {Object} context - Provides state and action helpers
     */
    scene: function(card, context) {
        const scene = (context.state.phase8Scenes || []).find(s => s.id === card.id);
        if (!scene) return ''; // Skip missing scenes

        const stepCount = scene.steps?.length || 0;
        const isProtected = scene.password_protected;

        return `
            <div class="dashboard-card dashboard-card-scene" data-card-key="${card.type}:${card.id}">
                <div class="dashboard-card-header">
                    <span class="dashboard-card-drag-handle" title="Drag to reorder">⋮⋮</span>
                    <span class="dashboard-card-icon">${scene.icon || '🎬'}</span>
                    <span class="dashboard-card-title">
                        ${Helpers.escapeHtml(scene.name)}
                        ${isProtected ? `<svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" title="Password protected"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>` : ''}
                    </span>
                    <button class="dashboard-card-unpin btn-icon" data-type="scene" data-id="${scene.id}" title="Remove from dashboard">
                        <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="dashboard-card-body">
                    <span class="dashboard-card-meta">${stepCount} step${stepCount !== 1 ? 's' : ''}</span>
                    <button class="btn btn-sm btn-primary dashboard-card-action" data-type="scene" data-id="${scene.id}">
                        Execute
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Render an aggregate widget card (legacy compatibility)
     * @param {Object} card - Card data with type:'aggregate_widget' and widget_id
     * @param {Object} context - Provides state and action helpers
     */
    aggregate_widget: function(card, context) {
        const widget = context.dashboardManager.registeredWidgets.get(card.widget_id);
        if (!widget) return ''; // Skip missing widgets

        // Use the widget's own render function
        const content = widget.render();

        return `
            <div class="dashboard-card dashboard-card-widget" data-card-key="${card.type}:${card.widget_id}">
                <div class="dashboard-card-header">
                    <span class="dashboard-card-drag-handle" title="Drag to reorder">⋮⋮</span>
                    <span class="dashboard-card-icon">${widget.icon}</span>
                    <span class="dashboard-card-title">${widget.name}</span>
                    <button class="dashboard-card-unpin btn-icon" data-type="aggregate_widget" data-id="${card.widget_id}" title="Remove from dashboard">
                        <svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="dashboard-card-body">
                    ${content}
                </div>
            </div>
        `;
    }
};
