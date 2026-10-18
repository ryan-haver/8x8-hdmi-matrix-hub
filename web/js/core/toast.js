/**
 * Toast notifications with de-duplication.
 *
 * - A toast with the same (message, type) as one still on screen is not
 *   stacked again: the visible toast gets a repeat counter badge
 *   (.toast-count, "×2", "×3", ...) and its dismiss timer restarts.
 * - When the page's Toast (window.toast, web/js/components/toast.js) is
 *   loaded, it renders the toasts (same markup, icons and dismiss animation);
 *   this manager only decides when to show, coalesce and dismiss. Without it,
 *   toasts are rendered into #toast-container directly.
 */

import { html } from './html.js';

const GLYPHS = { success: '✓', error: '✕', warning: '!', info: 'i' };

export class ToastManager {
    /**
     * @param {Object} [options]
     * @param {Object} [options.delegate] - A Toast-like renderer with show(message, type, 0) and dismiss(el)
     * @param {Element} [options.container] - Where standalone toasts go (default #toast-container)
     * @param {Document} [options.document]
     * @param {number} [options.defaultDuration] - ms (default 3000)
     * @param {Object} [options.timers] - {setTimeout, clearTimeout} (tests)
     */
    constructor({ delegate = null, container = null, document: doc, defaultDuration = 3000, timers } = {}) {
        this.delegate = delegate;
        this.document = doc || globalThis.document || null;
        this._container = container;
        this.defaultDuration = defaultDuration;
        const t = timers || globalThis;
        this._setTimeout = t.setTimeout.bind(globalThis);
        this._clearTimeout = t.clearTimeout.bind(globalThis);
        this._active = new Map(); // key -> {element, count, timer, message, type}
    }

    get container() {
        return this._container || this.document?.getElementById?.('toast-container') || null;
    }

    static key(message, type) {
        return `${type}\u0000${message}`;
    }

    /**
     * Show a toast, or bump the counter of an identical one still visible.
     * @param {string} message
     * @param {string} type - 'success' | 'error' | 'warning' | 'info'
     * @param {number} duration - ms; 0 keeps it until dismissed
     * @returns {Element|null} the toast element
     */
    show(message, type = 'info', duration = this.defaultDuration) {
        const text = String(message ?? '');
        const key = ToastManager.key(text, type);
        const current = this._active.get(key);
        if (current && this._isVisible(current.element)) {
            current.count += 1;
            this._renderCount(current);
            this._arm(key, current, duration);
            return current.element;
        }
        if (current) this._forget(key);

        const element = this._render(text, type);
        if (!element) return null;
        const entry = { element, count: 1, timer: null, message: text, type };
        this._active.set(key, entry);
        element.addEventListener?.('click', () => this.dismiss(element));
        this._arm(key, entry, duration);
        return element;
    }

    success(message, duration) {
        return this.show(message, 'success', duration);
    }

    error(message, duration = 5000) {
        return this.show(message, 'error', duration);
    }

    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }

    info(message, duration) {
        return this.show(message, 'info', duration);
    }

    /** How many times the visible (message, type) toast has been shown; 0 if none. */
    count(message, type = 'info') {
        const entry = this._active.get(ToastManager.key(String(message ?? ''), type));
        return entry && this._isVisible(entry.element) ? entry.count : 0;
    }

    dismiss(element) {
        for (const [key, entry] of this._active) {
            if (entry.element === element) {
                this._forget(key);
                break;
            }
        }
        if (!element) return;
        if (this.delegate && typeof this.delegate.dismiss === 'function') {
            this.delegate.dismiss(element);
        } else {
            element.remove?.();
        }
    }

    dismissAll() {
        for (const entry of [...this._active.values()]) this.dismiss(entry.element);
    }

    _arm(key, entry, duration) {
        if (entry.timer !== null) this._clearTimeout(entry.timer);
        entry.timer = null;
        if (duration > 0) {
            entry.timer = this._setTimeout(() => {
                entry.timer = null;
                if (this._active.get(key) === entry) this.dismiss(entry.element);
            }, duration);
        }
    }

    _forget(key) {
        const entry = this._active.get(key);
        if (!entry) return;
        if (entry.timer !== null) this._clearTimeout(entry.timer);
        this._active.delete(key);
    }

    _isVisible(element) {
        if (!element || element.isConnected === false) return false;
        return !element.classList?.contains('toast-out');
    }

    _render(message, type) {
        if (this.delegate && typeof this.delegate.show === 'function') {
            // Duration 0: the delegate must not dismiss on its own; this manager owns the timer.
            return this.delegate.show(message, type, 0) || null;
        }
        const container = this.container;
        if (!container || !this.document?.createElement) return null;
        const element = this.document.createElement('div');
        element.className = `toast ${type}`;
        element.setAttribute?.('role', type === 'error' ? 'alert' : 'status');
        element.innerHTML = String(html`
            <span class="toast-icon" aria-hidden="true">${GLYPHS[type] || GLYPHS.info}</span>
            <span class="toast-message">${message}</span>
            <button class="toast-close" type="button" aria-label="Dismiss">×</button>
        `);
        container.appendChild(element);
        return element;
    }

    _renderCount(entry) {
        const { element, count } = entry;
        if (!element || !this.document?.createElement) return;
        let badge = element.querySelector?.('.toast-count');
        if (!badge) {
            badge = this.document.createElement('span');
            badge.className = 'toast-count';
            const anchor = element.querySelector?.('.toast-message');
            if (anchor && typeof anchor.after === 'function') anchor.after(badge);
            else element.appendChild(badge);
        }
        badge.textContent = `×${count}`;
        badge.setAttribute?.('aria-label', `shown ${count} times`);
    }
}

export const toast = new ToastManager({
    delegate: (typeof window !== 'undefined' && window.toast) || null,
});
