/**
 * Observable store for ES modules.
 *
 * - on(event, handler) returns an unsubscribe function; off(event, handler)
 *   does the same. emit(event, data) calls every handler for that event.
 * - set(key, value) stores the value and, when it changed, emits
 *   `change:<key>` (value, previous) and `change` ({key, value, previous}).
 * - When the page's AppState (window.state, web/js/state.js) is loaded, the
 *   store is a view onto it: get/set read and write its properties, and
 *   on/emit use its event bus, so module code and classic scripts see the
 *   same state and the same events.
 */

export class MatrixState {
    /**
     * @param {Object} [options]
     * @param {Object} [options.target] - An AppState-like object to bridge to
     */
    constructor({ target = null } = {}) {
        this.target = target;
        this._values = target || Object.create(null);
        this._listeners = new Map(); // event -> Map(handler -> unsubscribe)
    }

    get bridged() {
        return !!this.target;
    }

    on(event, handler) {
        if (typeof handler !== 'function') throw new TypeError('handler must be a function');
        if (!this._listeners.has(event)) this._listeners.set(event, new Map());
        const handlers = this._listeners.get(event);
        if (!handlers.has(handler)) {
            let release = null;
            if (this.target && typeof this.target.on === 'function') {
                release = this.target.on(event, handler);
            }
            handlers.set(handler, typeof release === 'function' ? release : null);
        }
        return () => this.off(event, handler);
    }

    off(event, handler) {
        const handlers = this._listeners.get(event);
        if (!handlers || !handlers.has(handler)) return;
        const release = handlers.get(handler);
        handlers.delete(handler);
        if (handlers.size === 0) this._listeners.delete(event);
        if (release) release();
    }

    emit(event, data, ...rest) {
        if (this.target && typeof this.target.emit === 'function' && typeof this.target.on === 'function') {
            this.target.emit(event, data, ...rest);
            return;
        }
        const handlers = this._listeners.get(event);
        if (!handlers) return;
        for (const handler of [...handlers.keys()]) {
            try {
                handler(data, ...rest);
            } catch (error) {
                console.error(`Error in state listener for ${event}:`, error);
            }
        }
    }

    get(key) {
        return this._values[key];
    }

    set(key, value) {
        const previous = this._values[key];
        if (Object.is(previous, value)) return false;
        this._values[key] = value;
        this.emit(`change:${key}`, value, previous);
        this.emit('change', { key, value, previous });
        return true;
    }
}

export const state = new MatrixState({ target: (typeof window !== 'undefined' && window.state) || null });
