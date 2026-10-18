/** Shared remote renderer and event controller; can also bind existing markup. */
(() => {
    const bindings = new WeakMap();
    const gestures = new WeakMap();
    const outputCommands = new Set(['power_on', 'power_off', 'active', 'volume_up', 'volume_down', 'mute']);
    const commands = {
        nav: [['up', '▲'], ['left', '◀'], ['select', 'OK'], ['right', '▶'], ['down', '▼'], ['menu', 'Menu'], ['back', 'Back']],
        playback: [['previous', '⏮'], ['rewind', '⏪'], ['play', '▶'], ['pause', '⏸'], ['stop', '⏹'], ['fast_forward', '⏩'], ['next', '⏭']],
        volume: [['volume_down', 'Volume −'], ['mute', 'Mute'], ['volume_up', 'Volume +']],
        power: [['power_on', 'Power On'], ['power_off', 'Power Off']]
    };

    class CecRemote {
        /** New mounts use this renderer. Legacy mounts may call attachEvents only. */
        static render(container, options = {}) {
            container.replaceChildren();
            const root = document.createElement('div');
            root.className = 'cec-remote';
            root.innerHTML = `
                <style>.cec-remote [hidden] { display: none !important; }</style>
                <div role="group" aria-label="Remote mode">
                    <button type="button" class="btn btn-secondary" data-cec-mode="buttons">Buttons</button>
                    <button type="button" class="btn btn-secondary" data-cec-mode="trackpad">Trackpad</button>
                </div>
                <label>Target <select data-cec-target aria-label="CEC target"></select></label>
                <div class="cec-quick-targets" role="group" aria-label="Quick targets"></div>
                <div data-cec-buttons></div>
                <div data-cec-trackpad hidden>
                    <div class="trackpad-surface" tabindex="0" role="group" aria-label="Swipe to navigate, tap to select" style="touch-action:none;user-select:none;min-height:160px;display:grid;place-items:center;border:1px solid currentColor;border-radius:12px">
                        Swipe or tap
                        <span class="trackpad-feedback" aria-live="polite"></span>
                    </div>
                </div>
                <div data-cec-status role="status"></div>`;
            const select = root.querySelector('[data-cec-target]');
            for (const type of ['input', 'output']) {
                for (let port = 1; port <= (options.portCount || 8); port++) {
                    const option = document.createElement('option');
                    option.value = `${type}:${port}`;
                    option.textContent = options.getTargetName?.(type, port) || `${type === 'input' ? 'Input' : 'Output'} ${port}`;
                    select.append(option);
                }
            }
            for (const target of options.quickTargets || [{ type: 'input', port: 1 }, { type: 'output', port: 1 }]) {
                const pill = document.createElement('button');
                pill.type = 'button';
                pill.className = 'btn btn-secondary';
                pill.dataset.cecQuickTarget = `${target.type}:${target.port}`;
                pill.textContent = target.name || `${target.type} ${target.port}`;
                root.querySelector('.cec-quick-targets').append(pill);
            }
            const buttons = root.querySelector('[data-cec-buttons]');
            for (const [action, entries] of Object.entries(commands)) {
                const group = document.createElement('div');
                group.setAttribute('role', 'group');
                group.setAttribute('aria-label', action === 'nav' ? 'Navigation' : action);
                if (action === 'nav') group.style.cssText = 'display:grid;grid-template-columns:repeat(3,1fr);gap:6px';
                for (const [cmd, label] of entries) {
                    const button = document.createElement('button');
                    button.type = 'button';
                    button.className = 'btn btn-secondary';
                    button.dataset.cmd = cmd;
                    button.dataset.action = action;
                    button.textContent = label;
                    button.setAttribute('aria-label', cmd.replaceAll('_', ' '));
                    const position = { up: '1 / 2', left: '2 / 1', select: '2 / 2', right: '2 / 3', down: '3 / 2' }[cmd];
                    if (position) button.style.gridArea = position;
                    group.append(button);
                }
                buttons.append(group);
            }
            container.append(root);
            return CecRemote.attachEvents(root, options);
        }

        /** onCommand(cmd, action, button) lets legacy hosts retain target routing. */
        static attachEvents(container, options = {}) {
            bindings.get(container)?.destroy();
            const controller = new AbortController();
            const signal = controller.signal;
            let target = { type: 'input', port: 1, ...options.target };
            let mode = options.mode === 'trackpad' ? 'trackpad' : 'buttons';
            const report = error => {
                const status = container.querySelector('[data-cec-status]');
                if (status) status.textContent = error.message || String(error);
                options.onError?.(error);
            };
            const dispatch = async (cmd, action = 'nav', button) => {
                try {
                    const current = options.getTarget?.(action) || target;
                    if (!options.onCommand) {
                        if (!['input', 'output'].includes(current.type) || !Number.isInteger(Number(current.port)) || Number(current.port) < 1 || Number(current.port) > (options.portCount || 8)) throw new Error('No active target port for command');
                        if (current.type === 'output' && !outputCommands.has(cmd)) throw new Error('Command is not supported by displays');
                    }
                    const result = options.onCommand
                        ? await options.onCommand(cmd, action, button)
                        : await window.api.sendCecCommand(current.type, Number(current.port), cmd);
                    if (result?.success === false) throw new Error(result.error || 'CEC command failed');
                    options.onResult?.(result, cmd);
                    return result;
                } catch (error) { report(error); }
            };
            const update = () => {
                const select = container.querySelector('[data-cec-target]');
                if (select) select.value = `${target.type}:${target.port}`;
                container.querySelectorAll('[data-cec-mode]').forEach(button => {
                    button.setAttribute('aria-pressed', String(button.dataset.cecMode === (target.type === 'output' ? 'buttons' : mode)));
                    button.disabled = target.type === 'output' && button.dataset.cecMode === 'trackpad';
                });
                const buttons = container.querySelector('[data-cec-buttons]');
                const trackpad = container.querySelector('[data-cec-trackpad]');
                if (buttons) buttons.hidden = mode !== 'buttons' && target.type !== 'output';
                if (trackpad) trackpad.hidden = mode !== 'trackpad' || target.type === 'output';
                container.querySelectorAll('[data-cec-buttons] [data-cmd]').forEach(button => {
                    button.hidden = target.type === 'output' && !outputCommands.has(button.dataset.cmd);
                });
                container.querySelectorAll('[data-cec-quick-target]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.cecQuickTarget === `${target.type}:${target.port}`)));
            };
            const setTarget = next => { target = { ...next, port: Number(next.port) }; update(); options.onTargetChange?.(target); };
            container.addEventListener('change', event => {
                if (event.target.matches('[data-cec-target]')) {
                    const [type, port] = event.target.value.split(':');
                    setTarget({ type, port });
                }
            }, { signal });
            container.addEventListener('click', event => {
                const button = event.target.closest('button');
                if (!button || !container.contains(button) || button.disabled) return;
                if (button.dataset.cecMode) { mode = button.dataset.cecMode; update(); }
                else if (button.dataset.cecQuickTarget) {
                    const [type, port] = button.dataset.cecQuickTarget.split(':');
                    setTarget({ type, port });
                } else if (button.matches(options.commandSelector || '[data-cmd]')) {
                    dispatch(button.dataset.cmd, button.dataset.action, button);
                }
            }, { signal });
            const cleanup = CecRemote.attachTrackpad(container.querySelector(options.trackpadSelector || '.trackpad-surface'), cmd => dispatch(cmd));
            const binding = { dispatch, setTarget, destroy: () => { controller.abort(); cleanup(); bindings.delete(container); } };
            bindings.set(container, binding);
            update();
            return binding;
        }

        /** Pointer events cover touch, pen and mouse without synthetic double taps. */
        static attachTrackpad(surface, onCommand) {
            if (!surface) return () => {};
            gestures.get(surface)?.();
            const controller = new AbortController();
            const signal = controller.signal;
            const previousTouchAction = surface.style.touchAction;
            surface.style.touchAction = 'none';
            const feedback = surface.querySelector('.trackpad-feedback') || surface.parentElement.querySelector('.trackpad-feedback');
            let start = null;
            let timer;
            const cancel = () => { start = null; surface.classList.remove('touching'); };
            surface.addEventListener('pointerdown', event => {
                if (event.isPrimary === false || event.button !== 0 || start) return;
                event.preventDefault();
                start = { x: event.clientX, y: event.clientY, time: Date.now(), id: event.pointerId };
                surface.setPointerCapture?.(event.pointerId);
                surface.classList.add('touching');
            }, { signal });
            const send = cmd => {
                if (feedback) {
                    clearTimeout(timer);
                    feedback.className = `trackpad-feedback active ${cmd === 'select' ? 'tap' : cmd}`;
                    feedback.textContent = cmd === 'select' ? 'OK' : { up: '↑', down: '↓', left: '←', right: '→' }[cmd];
                    timer = setTimeout(() => { feedback.className = 'trackpad-feedback'; feedback.textContent = ''; }, 200);
                }
                Promise.resolve().then(() => onCommand(cmd)).catch(error => console.error('CEC gesture failed:', error));
            };
            surface.addEventListener('pointerup', event => {
                if (!start || event.pointerId !== start.id) return;
                const dx = event.clientX - start.x;
                const dy = event.clientY - start.y;
                const distance = Math.hypot(dx, dy);
                const elapsed = Date.now() - start.time;
                cancel();
                if (distance < 10 && elapsed < 300) send('select');
                else if (distance >= 30) send(Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up'));
            }, { signal });
            surface.addEventListener('pointercancel', cancel, { signal });
            surface.addEventListener('lostpointercapture', cancel, { signal });
            surface.addEventListener('keydown', event => {
                const cmd = { ArrowUp: 'up', ArrowDown: 'down', ArrowLeft: 'left', ArrowRight: 'right', Enter: 'select', ' ': 'select' }[event.key];
                if (cmd) { event.preventDefault(); send(cmd); }
            }, { signal });
            const cleanup = () => {
                controller.abort(); clearTimeout(timer); cancel(); gestures.delete(surface);
                surface.style.touchAction = previousTouchAction;
                if (feedback) { feedback.className = 'trackpad-feedback'; feedback.textContent = ''; }
            };
            gestures.set(surface, cleanup);
            return cleanup;
        }
    }

    window.CecRemote = CecRemote;
})();
