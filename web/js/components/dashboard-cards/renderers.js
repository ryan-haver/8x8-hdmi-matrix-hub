/**
 * Dashboard Card Renderers (Phase 7)
 * Each card type has its own compact renderer function.
 *
 * UI-27 (WP-E1): no stylesheet ever had rules for the dashboard-card-*
 * classes, so the cards rendered as bare text and loose buttons. A card now
 * uses the Profiles tab's card structure and styles (scene-card, scene-icon,
 * scene-info / scene-name / scene-outputs, scene-actions: the card surface of
 * LOOK_AND_FEEL §3); the dashboard-card-* classes stay for the dashboard's
 * handlers (dashboard-manager.js attachCardEventListeners) and tests. The
 * "drag to reorder" handle is gone: card reordering was never implemented.
 */

const UNPIN_ICON = `<svg class="icon icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>`;

/** Lock shown in the icon slot of a passcode-protected card (UI-50: one indicator, icon-sized). */
const LOCK_ICON = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-label="Passcode protected" role="img"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>`;

/**
 * One dashboard card. Every value is escaped here; a protected card shows the
 * lock in its icon slot instead of its emoji (UI-50: it showed the emoji and an
 * oversized SVG lock next to the title).
 */
function dashboardCardHtml({ kind, key, type, id, icon, title, locked = false, meta = '', action }) {
    const e = Helpers.escapeHtml;
    return `
            <div class="dashboard-card dashboard-card-${kind} scene-card" data-card-key="${e(key)}">
                <div class="scene-icon dashboard-card-icon"${locked ? ' title="Passcode protected"' : ''}>${locked ? LOCK_ICON : e(icon)}</div>
                <div class="scene-info">
                    <span class="scene-name dashboard-card-title">${e(title)}</span>
                    ${meta ? `<span class="scene-outputs dashboard-card-meta">${e(meta)}</span>` : ''}
                </div>
                <div class="scene-actions">
                    <button class="btn btn-sm btn-primary dashboard-card-action" data-type="${e(type)}" data-id="${e(id)}">${e(action)}</button>
                    <button class="btn-icon dashboard-card-unpin" data-type="${e(type)}" data-id="${e(id)}" title="Remove from dashboard">
                        ${UNPIN_ICON}
                    </button>
                </div>
            </div>
        `;
}

window.dashboardCardRenderers = {
    /**
     * Render a profile recall card
     * @param {Object} card - Card data with type:'profile' and id
     * @param {Object} context - Provides state and action helpers
     */
    profile: function(card, context) {
        const profile = context.state.profiles.find(p => p.id === card.id);
        if (!profile) return ''; // Skip missing profiles

        return dashboardCardHtml({
            kind: 'profile', key: `${card.type}:${card.id}`, type: 'profile', id: profile.id,
            icon: profile.icon || '🎬', title: profile.name, action: 'Recall',
        });
    },

    /**
     * Render a hardware preset recall card
     * @param {Object} card - Card data with type:'preset' and id (preset number)
     * @param {Object} context - Provides state and action helpers
     */
    preset: function(card, context) {
        const presetNum = parseInt(card.id);
        const preset = context.state.presets[presetNum] || { name: `Preset ${presetNum}` };

        return dashboardCardHtml({
            kind: 'preset', key: `${card.type}:${card.id}`, type: 'preset', id: card.id,
            icon: '⚡', title: preset.name, action: 'Recall',
        });
    },

    /**
     * Render a system shortcut card
     * @param {Object} card - Card data with type:'system_shortcut' and id
     * @param {Object} context - Provides state and action helpers
     */
    system_shortcut: function(card, context) {
        const shortcut = context.state.systemShortcuts.find(s => s.id === card.id);
        if (!shortcut) return ''; // Skip missing shortcuts

        return dashboardCardHtml({
            kind: 'shortcut', key: `${card.type}:${card.id}`, type: 'system_shortcut', id: shortcut.id,
            icon: shortcut.icon || '⚡', title: shortcut.name, action: 'Execute',
        });
    },

    /**
     * Render a CEC macro card
     * @param {Object} card - Card data with type:'macro' and id
     * @param {Object} context - Provides state and action helpers
     */
    macro: function(card, context) {
        const macro = context.state.cecMacros.find(m => m.id === card.id);
        if (!macro) return ''; // Skip missing macros

        return dashboardCardHtml({
            kind: 'macro', key: `${card.type}:${card.id}`, type: 'macro', id: macro.id,
            icon: macro.icon || '⚡', title: macro.name, action: 'Run',
        });
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

        return dashboardCardHtml({
            kind: 'scene', key: `${card.type}:${card.id}`, type: 'scene', id: scene.id,
            icon: scene.icon || '🎬', title: scene.name, action: 'Execute', locked: !!isProtected,
            meta: `${stepCount} step${stepCount !== 1 ? 's' : ''}`,
        });
    }
};
