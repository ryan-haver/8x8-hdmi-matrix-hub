/**
 * OREI Matrix Control - Scene Editor Component (Phase 8)
 * Modal editor for creating/editing Phase 8 scenes with steps and overrides.
 */

class SceneEditor {
    constructor() {
        this.modal = null;
        this.sceneId = null;
        this.sceneData = null;
        this.conflicts = [];
        this.createModal();
    }

    createModal() {
        this.modal = document.createElement('div');
        this.modal.className = 'modal';
        this.modal.id = 'scene-editor-modal';
        this.modal.setAttribute('aria-hidden', 'true');
        this.modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content modal-lg">
                <div class="modal-header">
                    <h2 class="modal-title" id="scene-editor-title">New Scene</h2>
                    <button class="modal-close" aria-label="Close">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>
                <div class="modal-body" id="scene-editor-body">
                    <!-- Form rendered dynamically -->
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" id="scene-editor-cancel">Cancel</button>
                    <button class="btn btn-primary" id="scene-editor-save">Save</button>
                </div>
            </div>
        `;

        this.modal.querySelector('.modal-close').addEventListener('click', () => this.close());
        this.modal.querySelector('.modal-backdrop').addEventListener('click', () => this.close());
        this.modal.querySelector('#scene-editor-cancel').addEventListener('click', () => this.close());
        this.modal.querySelector('#scene-editor-save').addEventListener('click', () => this.save());

        document.body.appendChild(this.modal);
    }

    async open(sceneId) {
        this.sceneId = sceneId;
        this.conflicts = [];

        if (sceneId) {
            // Load existing scene
            const result = await api.getScene(sceneId);
            this.sceneData = result.data?.scene || result.data;
            document.getElementById('scene-editor-title').textContent = 'Edit Scene';
        } else {
            // New scene
            this.sceneData = {
                name: '',
                description: '',
                password_protected: false,
                steps: [],
                overrides: {}
            };
            document.getElementById('scene-editor-title').textContent = 'New Scene';
        }

        this.render();
        this.modal.classList.add('open');
        this.modal.setAttribute('aria-hidden', 'false');
    }

    close() {
        this.modal.classList.remove('open');
        this.modal.setAttribute('aria-hidden', 'true');
        this.sceneId = null;
        this.sceneData = null;
        this.conflicts = [];
    }

    render() {
        const body = document.getElementById('scene-editor-body');
        const d = this.sceneData;

        body.innerHTML = `
            <div class="form-group">
                <label for="scene-name">Name</label>
                <input type="text" id="scene-name" class="form-control" value="${Helpers.escapeHtml(d.name || '')}" placeholder="Scene name">
            </div>
            <div class="form-group">
                <label for="scene-desc">Description</label>
                <textarea id="scene-desc" class="form-control" rows="2" placeholder="Optional description">${Helpers.escapeHtml(d.description || '')}</textarea>
            </div>
            <div class="form-group">
                <label class="checkbox-label">
                    <input type="checkbox" id="scene-password-protected" ${d.password_protected ? 'checked' : ''}>
                    Password protect
                </label>
            </div>
            <div class="form-group" id="scene-passcode-group" style="display:${d.password_protected ? 'block' : 'none'}">
                <label for="scene-passcode">Passcode (4-8 digits)</label>
                <input type="password" id="scene-passcode" class="form-control" maxlength="8" placeholder="1234">
            </div>

            <div class="scene-steps-section">
                <div class="section-header">
                    <h4>Steps</h4>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-secondary" id="add-profile-step-btn">+ Profile</button>
                        <button class="btn btn-sm btn-secondary" id="add-action-step-btn">+ System Action</button>
                        <button class="btn btn-sm btn-secondary" id="add-macro-step-btn">+ Macro</button>
                    </div>
                </div>
                <div id="scene-steps-list">
                    ${this.renderStepsList()}
                </div>
            </div>

            ${this.conflicts.length > 0 ? `
            <div class="conflict-warnings">
                <h4>⚠️ Conflicts Detected</h4>
                <p class="conflict-help">Multiple profiles set different values for the same output setting. Select which settings to <strong>skip</strong> during scene execution.</p>
                <div class="conflict-list">
                    ${this.renderConflictsList()}
                </div>
            </div>` : ''}

            ${(this.sceneData.overrides && Object.keys(this.sceneData.overrides).length > 0) ? `
            <div class="overrides-section">
                <h4>Active Overrides</h4>
                <p class="section-help">These settings will be skipped during scene execution.</p>
                <div class="overrides-list">
                    ${this.renderOverridesList()}
                </div>
            </div>` : ''}
        `;

        // Password toggle
        document.getElementById('scene-password-protected').addEventListener('change', (e) => {
            document.getElementById('scene-passcode-group').style.display = e.target.checked ? 'block' : 'none';
        });

        // Add step buttons
        document.getElementById('add-profile-step-btn').addEventListener('click', () => this.addStep('profile'));
        document.getElementById('add-action-step-btn').addEventListener('click', () => this.addStep('system_action'));
        document.getElementById('add-macro-step-btn').addEventListener('click', () => this.addStep('macro'));

        // Remove step buttons (delegated)
        body.addEventListener('click', (e) => {
            if (e.target.closest('.remove-step-btn')) {
                const idx = parseInt(e.target.closest('.remove-step-btn').dataset.index);
                this.sceneData.steps.splice(idx, 1);
                this.render();
                return;
            }
            // Clear override buttons
            if (e.target.closest('.clear-override-btn')) {
                const btn = e.target.closest('.clear-override-btn');
                const pid = btn.dataset.pid;
                const output = parseInt(btn.dataset.output);
                const setting = btn.dataset.setting;
                if (this.sceneData.overrides?.[pid]?.[output]?.[setting]) {
                    delete this.sceneData.overrides[pid][output][setting];
                    if (Object.keys(this.sceneData.overrides[pid][output]).length === 0) {
                        delete this.sceneData.overrides[pid][output];
                    }
                    if (Object.keys(this.sceneData.overrides[pid]).length === 0) {
                        delete this.sceneData.overrides[pid];
                    }
                }
                this.render();
                this.persistOverrides();
            }
        });

        // Conflict checkbox changes (delegated)
        body.addEventListener('change', (e) => {
            if (e.target.matches('.conflict-choice input[type="checkbox"]')) {
                const cb = e.target;
                const pid = cb.dataset.pid;
                const output = parseInt(cb.dataset.output);
                const setting = cb.dataset.setting;
                if (!this.sceneData.overrides) this.sceneData.overrides = {};
                if (!this.sceneData.overrides[pid]) this.sceneData.overrides[pid] = {};
                if (!this.sceneData.overrides[pid][output]) this.sceneData.overrides[pid][output] = {};
                this.sceneData.overrides[pid][output][setting] = cb.checked;
                this.render();
                this.persistOverrides();
            }
        });
    }

    /**
     * Persist overrides to the backend (if scene exists).
     */
    async persistOverrides() {
        if (!this.sceneId) return;
        try {
            // Send the full override set; backend merges per-key
            for (const [pid, outMap] of Object.entries(this.sceneData.overrides || {})) {
                for (const [output, settings] of Object.entries(outMap)) {
                    for (const [setting, disabled] of Object.entries(settings)) {
                        await api.setOverride(this.sceneId, {
                            profile_id: pid,
                            output_num: parseInt(output),
                            setting_key: setting,
                            disabled: !!disabled,
                        });
                    }
                }
            }
        } catch (err) {
            console.warn('Failed to persist overrides:', err);
        }
    }

    renderStepsList() {
        const steps = this.sceneData.steps || [];
        if (steps.length === 0) {
            return '<p class="empty-hint">No steps yet. Add profiles, system actions, or macros above.</p>';
        }

        return steps.map((step, idx) => {
            let icon, name, typeLabel;

            if (step.type === 'profile') {
                icon = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/></svg>`;
                name = state.profiles?.find(p => p.id === step.id)?.name || step.id;
                typeLabel = 'Profile';
            } else if (step.type === 'system_action') {
                icon = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>`;
                name = state.systemActions?.find(a => a.key === step.id)?.name || step.id;
                typeLabel = 'System Action';
            } else if (step.type === 'macro') {
                icon = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>`;
                name = state.cecMacros?.find(m => m.id === step.id)?.name || step.id;
                typeLabel = 'Macro';
            } else {
                icon = `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>`;
                name = step.id;
                typeLabel = step.type;
            }

            return `
                <div class="step-item" data-index="${idx}">
                    <span class="step-icon">${icon}</span>
                    <span class="step-name">${Helpers.escapeHtml(name)}</span>
                    <span class="step-type">${typeLabel}</span>
                    <button class="btn-icon remove-step-btn" data-index="${idx}" title="Remove">
                        <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                        </svg>
                    </button>
                </div>`;
        }).join('');
    }

    addStep(type) {
        if (type === 'profile') {
            const profiles = state.profiles || [];
            const id = prompt(`Enter profile ID:\n${profiles.map(p => `${p.id}: ${p.name}`).join('\n')}`);
            if (id) {
                this.sceneData.steps.push({ type: 'profile', id });
                this.render();
                this.validateScene();
            }
        } else if (type === 'system_action') {
            const actions = state.systemActions || [];
            const id = prompt(`Enter system action key:\n${actions.map(a => `${a.key}: ${a.name}`).join('\n')}`);
            if (id) {
                this.sceneData.steps.push({ type: 'system_action', id });
                this.render();
            }
        } else if (type === 'macro') {
            const macros = state.cecMacros || [];
            const id = prompt(`Enter macro ID:\n${macros.map(m => `${m.id}: ${m.name}`).join('\n')}`);
            if (id) {
                this.sceneData.steps.push({ type: 'macro', id });
                this.render();
            }
        }
    }

    /**
     * Render conflict list with override checkboxes (Phase 8).
     * Each conflict shows the output + setting + conflicting profiles + values.
     * Checking a box adds an override to skip that profile's setting.
     */
    renderConflictsList() {
        if (!this.conflicts.length) return '';
        return this.conflicts.map((conflict, cIdx) => {
            const output = conflict.output || conflict.output_num;
            const setting = conflict.setting || conflict.setting_key;
            const profiles = conflict.profiles || [];

            return `
                <div class="conflict-group">
                    <div class="conflict-header">
                        Output ${output} → <strong>${Helpers.escapeHtml(setting)}</strong>
                    </div>
                    <div class="conflict-choices">
                        ${profiles.map(p => {
                            const isOverridden = this.sceneData.overrides?.[p.id]?.[output]?.[setting] === true;
                            return `
                                <label class="conflict-choice ${isOverridden ? 'overridden' : ''}">
                                    <input type="checkbox"
                                           data-cidx="${cIdx}"
                                           data-pid="${Helpers.escapeHtml(p.id)}"
                                           data-output="${output}"
                                           data-setting="${Helpers.escapeHtml(setting)}"
                                           ${isOverridden ? 'checked' : ''}>
                                    <span class="conflict-profile">${Helpers.escapeHtml(p.name || p.id)}</span>
                                    <span class="conflict-value">= ${JSON.stringify(p.value)}</span>
                                    <span class="conflict-action">${isOverridden ? '(skipped)' : '(apply)'}</span>
                                </label>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Render active overrides list with clear buttons.
     */
    renderOverridesList() {
        const overrides = this.sceneData.overrides || {};
        const entries = [];
        for (const [profileId, outMap] of Object.entries(overrides)) {
            for (const [output, settings] of Object.entries(outMap)) {
                for (const [setting, disabled] of Object.entries(settings)) {
                    if (disabled) {
                        const profileName = state.profiles?.find(p => p.id === profileId)?.name || profileId;
                        entries.push({ profileId, profileName, output, setting });
                    }
                }
            }
        }
        if (entries.length === 0) return '';
        return entries.map(e => `
            <div class="override-item">
                <span class="override-desc">
                    ${Helpers.escapeHtml(e.profileName)} → output ${e.output} → <strong>${Helpers.escapeHtml(e.setting)}</strong> skipped
                </span>
                <button class="btn-icon clear-override-btn"
                        data-pid="${Helpers.escapeHtml(e.profileId)}"
                        data-output="${e.output}"
                        data-setting="${Helpers.escapeHtml(e.setting)}"
                        title="Clear override">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </svg>
                </button>
            </div>
        `).join('');
    }

    async validateScene() {
        if (!this.sceneId) return;
        try {
            const result = await api.validateScene(this.sceneId);
            this.conflicts = result.data?.conflicts || [];
            this.render();
        } catch (err) {
            // Validation endpoint may not exist yet - ignore
        }
    }

    async save() {
        const name = document.getElementById('scene-name').value.trim();
        if (!name) {
            toast.error('Scene name is required');
            return;
        }

        const data = {
            name,
            description: document.getElementById('scene-desc').value.trim(),
            password_protected: document.getElementById('scene-password-protected').checked,
            steps: this.sceneData.steps,
            overrides: this.sceneData.overrides || {}
        };

        const passcode = document.getElementById('scene-passcode').value;
        if (data.password_protected && passcode) {
            data.passcode = passcode;
        }

        try {
            if (this.sceneId) {
                await api.updateScene(this.sceneId, data);
                toast.success('Scene updated');
            } else {
                await api.createScene(data);
                toast.success('Scene created');
            }
            state.loadPhase8Scenes();
            this.close();
        } catch (err) {
            toast.error('Failed to save scene');
        }
    }
}

window.sceneEditor = new SceneEditor();
