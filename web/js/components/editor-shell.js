/** Shared, opt-in editor chrome. Existing editors keep their baseline markup. */
(() => {
    let sequence = 0;
    const stack = [];
    const element = (tag, text, className) => {
        const node = document.createElement(tag);
        if (text !== undefined) node.textContent = text;
        if (className) node.className = className;
        return node;
    };

    class EditorShell {
        constructor(options = {}) {
            this.options = options;
            this.modal = element('div', undefined, 'editor-shell');
            this.modal.style.cssText = 'position:fixed;inset:0;z-index:11000;display:grid;place-items:center;background:#0009;padding:16px';
            this.dialog = element('section', undefined, 'editor-shell-dialog');
            this.dialog.style.cssText = `display:flex;flex-direction:column;width:min(100%,640px);max-height:90dvh;background:var(--bg-secondary,#202530);color:var(--text-primary,#fff);border-radius:12px;overflow:hidden;${options.drawer ? 'height:100%;margin-left:auto' : ''}`;
            this.dialog.setAttribute('role', 'dialog');
            this.dialog.setAttribute('aria-modal', 'true');
            const titleId = `editor-shell-title-${++sequence}`;
            this.dialog.setAttribute('aria-labelledby', titleId);
            const header = element('header', undefined, 'editor-shell-header');
            header.style.cssText = 'display:flex;align-items:center;gap:12px;padding:16px';
            const icon = element('span', options.icon || '✎');
            icon.setAttribute('aria-hidden', 'true');
            const title = element('h2', options.title || 'Editor');
            title.id = titleId;
            title.style.cssText = 'flex:1;margin:0;font-size:1.25rem';
            const close = this.button('×', () => this.cancel());
            close.setAttribute('aria-label', 'Close');
            header.append(icon, title, close);
            this.validation = element('div', undefined, 'editor-shell-validation');
            this.validation.setAttribute('role', 'alert');
            this.validation.style.cssText = 'padding:12px 16px;color:var(--error-color,#ffb4ab)';
            this.validation.hidden = true;
            this.body = element('div', undefined, 'editor-shell-body');
            this.body.style.cssText = 'overflow:auto;min-height:0;flex:1;padding:16px';
            if (options.body instanceof Node) this.body.append(options.body);
            const footer = element('footer', undefined, 'editor-shell-footer');
            footer.style.cssText = 'position:sticky;bottom:0;display:flex;gap:8px;padding:16px;background:inherit;flex-shrink:0';
            this.deleteButton = this.button('Delete', () => this.run(options.onDelete));
            this.deleteButton.hidden = !options.onDelete;
            const spacer = element('span');
            spacer.style.flex = '1';
            this.cancelButton = this.button('Cancel', () => this.cancel());
            this.saveButton = this.button(options.saveLabel || 'Save', () => this.run(options.onSave), 'btn btn-primary');
            this.saveButton.hidden = options.showSave === false;
            footer.append(this.deleteButton, spacer, this.cancelButton, this.saveButton);
            this.dialog.append(header, this.validation, this.body, footer);
            const style = element('style', '.editor-shell [hidden] { display: none !important; }');
            this.modal.append(style, this.dialog);
            this.modal.addEventListener('click', event => {
                if (event.target === this.modal) this.cancel();
            });
            this.keyHandler = event => {
                if (stack.at(-1) !== this) return;
                if (event.key === 'Escape') {
                    event.preventDefault();
                    event.stopImmediatePropagation();
                    this.cancel();
                } else if (event.key === 'Tab') {
                    const nodes = [...this.dialog.querySelectorAll('button,input,select,textarea,[tabindex="0"]')]
                        .filter(node => !node.disabled && !node.hidden && node.getClientRects().length);
                    const index = nodes.indexOf(document.activeElement);
                    if (nodes.length) {
                        event.preventDefault();
                        nodes[(index + (event.shiftKey ? -1 : 1) + nodes.length) % nodes.length].focus();
                    }
                }
            };
        }

        button(label, onClick, className = 'btn btn-secondary') {
            const button = element('button', label, className);
            button.type = 'button';
            button.addEventListener('click', onClick);
            return button;
        }

        async run(callback) {
            if (!callback || this.busy) return;
            this.busy = true;
            this.saveButton.disabled = this.deleteButton.disabled = true;
            this.clearValidationErrors();
            try {
                if (await callback(this) !== false) this.close();
            } catch (error) {
                this.showValidationErrors([error.message || String(error)]);
            } finally {
                this.busy = false;
                this.saveButton.disabled = this.deleteButton.disabled = false;
            }
        }

        showValidationErrors(errors) {
            this.validation.replaceChildren();
            const messages = (Array.isArray(errors) ? errors : [errors]).filter(Boolean);
            const list = element('ul');
            messages.forEach(error => list.append(element('li', error.message || String(error))));
            this.validation.append(list);
            this.validation.hidden = !messages.length;
        }

        clearValidationErrors() {
            this.validation.replaceChildren();
            this.validation.hidden = true;
        }

        open() {
            if (this.modal.isConnected) return this;
            this.previousFocus = document.activeElement;
            if (!stack.length) EditorShell.previousOverflow = document.body.style.overflow;
            stack.push(this);
            document.body.style.overflow = 'hidden';
            document.body.append(this.modal);
            document.addEventListener('keydown', this.keyHandler, true);
            (this.body.querySelector('input,select,textarea,button') || this.cancelButton).focus();
            return this;
        }

        cancel() {
            if (this.busy) return;
            this.options.onCancel?.(this);
            this.close();
        }

        close() {
            const index = stack.indexOf(this);
            if (index < 0) return;
            stack.splice(index, 1);
            this.modal.remove();
            document.removeEventListener('keydown', this.keyHandler, true);
            if (!stack.length) document.body.style.overflow = EditorShell.previousOverflow;
            if (this.previousFocus?.isConnected) this.previousFocus.focus();
            this.options.onClose?.(this);
        }

        /** Items may be strings or {id, label/name, description, keywords}. */
        static openPicker({ title = 'Choose a command', items = [], placeholder = 'Search…', onSelect } = {}) {
            const shell = new EditorShell({ title, showSave: false });
            const search = element('input');
            const list = element('div', undefined, 'editor-picker-list');
            const listId = `editor-picker-list-${++sequence}`;
            list.id = listId;
            list.setAttribute('role', 'listbox');
            list.setAttribute('aria-label', title);
            search.type = 'search';
            search.placeholder = placeholder;
            search.setAttribute('aria-label', placeholder);
            search.setAttribute('role', 'combobox');
            search.setAttribute('aria-controls', listId);
            search.setAttribute('aria-expanded', 'true');
            search.setAttribute('aria-autocomplete', 'list');
            search.style.cssText = 'width:100%;margin-bottom:12px';
            let filtered = [];
            let active = 0;
            const select = index => {
                const item = filtered[index];
                if (item === undefined) return;
                shell.close();
                onSelect?.(item);
            };
            const highlight = () => {
                [...list.children].forEach((row, index) => {
                    if (row.getAttribute('role') !== 'option') return;
                    row.setAttribute('aria-selected', String(index === active));
                    row.style.background = index === active ? 'var(--accent-color,#3265aa)' : '';
                });
                if (filtered.length) {
                    search.setAttribute('aria-activedescendant', `${listId}-${active}`);
                    list.children[active]?.scrollIntoView({ block: 'nearest' });
                } else search.removeAttribute('aria-activedescendant');
            };
            const filter = () => {
                const query = search.value.trim().toLocaleLowerCase();
                filtered = items.filter(item => {
                    const text = typeof item === 'string' ? item : [item.label, item.name, item.id, item.description, item.keywords].join(' ');
                    return text.toLocaleLowerCase().includes(query);
                });
                active = 0;
                list.replaceChildren();
                filtered.forEach((item, index) => {
                    const row = element('div', typeof item === 'string' ? item : item.label || item.name || item.id);
                    row.id = `${listId}-${index}`;
                    row.setAttribute('role', 'option');
                    row.style.cssText = 'padding:12px;cursor:pointer;border-radius:6px';
                    row.addEventListener('click', () => select(index));
                    list.append(row);
                });
                if (!filtered.length) list.append(element('p', 'No matches'));
                highlight();
            };
            search.addEventListener('input', filter);
            search.addEventListener('keydown', event => {
                if (['ArrowDown', 'ArrowUp', 'Enter'].includes(event.key)) {
                    event.preventDefault();
                    if (event.key === 'Enter') select(active);
                    else if (filtered.length) {
                        active = (active + (event.key === 'ArrowDown' ? 1 : -1) + filtered.length) % filtered.length;
                        highlight();
                    }
                }
            });
            shell.body.append(search, list);
            filter();
            return shell.open();
        }

        /** Bridge the existing scene editor without changing its DOM or source. */
        static installSceneEditor(editor, appState) {
            if (!editor) return;
            editor.addStep = function(type) {
                this.sceneData.name = document.getElementById('scene-editor-name').value;
                this.sceneData.description = document.getElementById('scene-desc').value;
                this.sceneData.password_protected = document.getElementById('scene-password-protected').checked;
                const scene = this.sceneData;
                if (type === 'wait') {
                    const duration = element('input');
                    duration.type = 'number'; duration.min = '0.5'; duration.max = '30'; duration.step = 'any'; duration.value = '1';
                    duration.setAttribute('aria-label', 'Wait duration in seconds');
                    const shell = new EditorShell({ title: 'Add wait', onSave: () => {
                        const seconds = Number(duration.value);
                        if (!Number.isFinite(seconds) || seconds < 0.5 || seconds > 30) {
                            shell.showValidationErrors(['Wait must be between 0.5 and 30 seconds']);
                            return false;
                        }
                        if (this.sceneData === scene) {
                            scene.steps.push({ type, id: '', params: { seconds } });
                            this.render();
                        }
                    } });
                    shell.body.append(duration);
                    return shell.open();
                }
                const sources = { profile: appState.profiles, system_action: appState.systemActions, macro: appState.cecMacros };
                const items = (sources[type] || []).map(item => ({ ...item, id: item.id || item.key, label: item.name }));
                return EditorShell.openPicker({
                    title: `Add ${type.replace('_', ' ')}`, items,
                    onSelect: item => {
                        if (this.sceneData !== scene) return;
                        scene.steps.push({ type, id: item.id });
                        this.render();
                        if (type === 'profile') this.validateScene();
                    }
                });
            };
        }
    }

    class CecMacroEditor {
        constructor({ legacy } = {}) {
            this.legacy = legacy;
        }

        async open(macroId) {
            if (window.cecSettings?.showMacroModal) return window.cecSettings.showMacroModal(macroId);
            if (this.legacy) return this.legacy.open(macroId);
            this.shell?.close();
            const macro = { name: '', description: '', icon: '⚡', steps: [] };
            const shell = new EditorShell({
                title: macroId ? 'Edit CEC Macro' : 'New CEC Macro', icon: '⚡',
                onSave: async () => {
                    macro.name = name.value.trim();
                    macro.description = description.value.trim();
                    const errors = [];
                    if (!macro.name) errors.push('Please enter a macro name');
                    if (!macro.steps.length) errors.push('Please add at least one step');
                    macro.steps.forEach((step, i) => {
                        if (!step.command) errors.push(`Step ${i + 1}: Please select a command`);
                        if (!step.targets.length) errors.push(`Step ${i + 1}: Please select at least one target`);
                        if (!Number.isFinite(step.delay_ms) || step.delay_ms < 0 || step.delay_ms > 10000) errors.push(`Step ${i + 1}: Delay must be 0–10000 ms`);
                    });
                    if (errors.length) { shell.showValidationErrors(errors); return false; }
                    const payload = { name: macro.name, description: macro.description, icon: macro.icon, steps: macro.steps };
                    const result = macroId ? await window.api.updateMacro(macroId, payload) : await window.api.createMacro(payload);
                    if (!result?.success) throw new Error(result?.error || 'Failed to save macro');
                },
                onDelete: macroId ? async () => {
                    const result = await window.api.deleteMacro(macroId);
                    if (!result?.success) throw new Error(result?.error || 'Failed to delete macro');
                } : undefined
            });
            this.shell = shell;
            const field = (label, control) => {
                const wrapper = element('label', label);
                wrapper.style.cssText = 'display:block;margin-bottom:12px';
                wrapper.append(control);
                return wrapper;
            };
            const name = element('input');
            const description = element('input');
            const steps = element('div');
            const renderSteps = () => {
                steps.replaceChildren();
                macro.steps.forEach((step, index) => {
                    const row = element('div');
                    row.append(element('span', `${index + 1}. ${step.command} `));
                    const targets = element('select');
                    targets.multiple = true;
                    for (const type of ['input', 'output']) {
                        for (let port = 1; port <= 8; port++) {
                            const option = element('option', `${type} ${port}`);
                            option.value = `${type}_${port}`;
                            option.selected = step.targets.includes(option.value);
                            targets.append(option);
                        }
                    }
                    targets.setAttribute('aria-label', `Step ${index + 1} targets`);
                    targets.addEventListener('change', () => { step.targets = [...targets.selectedOptions].map(option => option.value); });
                    const delay = element('input');
                    delay.type = 'number'; delay.min = '0'; delay.max = '10000'; delay.value = step.delay_ms;
                    delay.setAttribute('aria-label', `Step ${index + 1} delay in milliseconds`);
                    delay.addEventListener('input', () => { step.delay_ms = Number(delay.value); });
                    row.append(targets, delay, shell.button('Remove', () => { macro.steps.splice(index, 1); renderSteps(); }));
                    steps.append(row);
                });
            };
            shell.body.append(field('Name', name), field('Description', description), steps,
                shell.button('Add Step', () => EditorShell.openPicker({
                    title: 'Choose CEC command',
                    items: ['POWER_ON', 'POWER_OFF', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'SELECT', 'BACK', 'MENU', 'PLAY', 'PAUSE', 'STOP', 'PREVIOUS', 'NEXT', 'REWIND', 'FAST_FORWARD', 'VOLUME_UP', 'VOLUME_DOWN', 'MUTE', 'ACTIVE'],
                    onSelect: command => { macro.steps.push({ command, targets: [], delay_ms: 500 }); renderSteps(); }
                })));
            shell.open();
            if (macroId) {
                shell.saveButton.disabled = shell.deleteButton.disabled = true;
                try {
                    const response = await window.api.getMacro(macroId);
                    if (!response?.success || !response.data) throw new Error(response?.error || 'Failed to load macro');
                    if (this.shell !== shell || !shell.modal.isConnected) return shell;
                    Object.assign(macro, response.data);
                    macro.steps = (macro.steps || []).map(step => ({ ...step, targets: [...(step.targets || [])] }));
                    name.value = macro.name || '';
                    description.value = macro.description || '';
                    renderSteps();
                    shell.saveButton.disabled = shell.deleteButton.disabled = false;
                } catch (error) { shell.showValidationErrors([error.message]); }
            }
            return shell;
        }

        close() { this.legacy ? this.legacy.close() : this.shell?.close(); }
    }

    window.EditorShell = EditorShell;
    window.CecMacroEditor = CecMacroEditor;
    window.cecMacroEditor = new CecMacroEditor({ legacy: window.cecMacroEditor });
})();
