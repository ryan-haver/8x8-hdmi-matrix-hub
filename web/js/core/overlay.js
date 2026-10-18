/**
 * Stack of open modals, drawers and pickers (UI-07).
 *
 * Unlike OverlayManager (web/js/utils/overlay-manager.js), which keeps one
 * overlay open at a time, this tracks overlays stacked on top of each other,
 * e.g. an icon picker over a modal over a drawer:
 *
 * - Escape closes only the top-most overlay. The keydown is consumed so the
 *   drawer underneath does not close too.
 * - Tab and Shift+Tab stay inside the top-most overlay's element.
 * - The element gets role="dialog" (unless it has a role) and
 *   aria-modal="true" while it is on the stack; both are restored on close.
 * - On close, focus returns to the element that had it when the overlay
 *   opened (or entry.triggerElement).
 *
 * Entry: {id, element?, onClose?(reason), triggerElement?, initialFocus?,
 *         autoFocus = true, trapFocus = true, closeOnEscape = true}
 * onClose is how the stack asks the component to hide itself (Escape,
 * closeTop, closeAll); a component closing on its own calls pop(id) instead.
 */

const FOCUSABLE = [
    'a[href]',
    'area[href]',
    'button:not([disabled])',
    'input:not([disabled]):not([type="hidden"])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    'iframe',
    '[contenteditable="true"]',
    '[tabindex]:not([tabindex="-1"])',
].join(',');

function focusableIn(element) {
    if (!element || typeof element.querySelectorAll !== 'function') return [];
    return [...element.querySelectorAll(FOCUSABLE)].filter((el) => {
        if (el.hidden || el.getAttribute?.('aria-hidden') === 'true') return false;
        if (typeof el.closest === 'function' && el.closest('[inert]')) return false;
        if (typeof el.getClientRects === 'function' && el.getClientRects().length === 0) return false;
        return true;
    });
}

function focus(el) {
    if (!el || typeof el.focus !== 'function') return false;
    try {
        el.focus({ preventScroll: true });
        return true;
    } catch {
        return false;
    }
}

function contains(container, el) {
    return !!container && !!el && (container === el || (typeof container.contains === 'function' && container.contains(el)));
}

export class OverlayStack {
    /**
     * @param {Object} [options]
     * @param {Document} [options.document] - Where keydown is listened for (default: the page's document)
     */
    constructor({ document: doc } = {}) {
        this.document = doc || globalThis.document || null;
        this._stack = [];
        this._onKeydown = (event) => this._handleKeydown(event);
        this._listening = false;
    }

    get size() {
        return this._stack.length;
    }

    /** The top-most entry, or null. */
    peek() {
        return this._stack[this._stack.length - 1] || null;
    }

    has(id) {
        return this._stack.some((entry) => entry.id === id);
    }

    /**
     * Put an overlay on top of the stack. Pushing an id that is already on the
     * stack moves it to the top.
     * @returns {Object} the stored entry
     */
    push(entry) {
        if (!entry || entry.id === undefined || entry.id === null) throw new TypeError('overlay entry needs an id');
        const existing = this._stack.findIndex((e) => e.id === entry.id);
        if (existing !== -1) this._stack.splice(existing, 1);

        const element = entry.element || null;
        const stored = {
            autoFocus: true,
            trapFocus: true,
            closeOnEscape: true,
            ...entry,
            element,
            triggerElement: entry.triggerElement || this.document?.activeElement || null,
            _savedAttrs: null,
        };
        if (element && typeof element.setAttribute === 'function') {
            stored._savedAttrs = {
                role: element.getAttribute('role'),
                'aria-modal': element.getAttribute('aria-modal'),
            };
            if (!stored._savedAttrs.role) element.setAttribute('role', 'dialog');
            element.setAttribute('aria-modal', 'true');
        }
        this._stack.push(stored);
        this._listen();

        if (element && stored.autoFocus) {
            const initial =
                typeof stored.initialFocus === 'string'
                    ? element.querySelector?.(stored.initialFocus)
                    : stored.initialFocus;
            if (!focus(initial) && !focus(focusableIn(element)[0])) this._focusContainer(element);
        }
        return stored;
    }

    /**
     * Take an overlay off the stack (the top one when id is omitted) without
     * calling its onClose. Restores its attributes and, if it was on top, the
     * focus it had taken. Returns the entry, or null.
     */
    pop(id) {
        const index = id === undefined ? this._stack.length - 1 : this._stack.findIndex((e) => e.id === id);
        if (index < 0) return null;
        const wasTop = index === this._stack.length - 1;
        const [entry] = this._stack.splice(index, 1);
        this._restoreAttrs(entry);
        if (this._stack.length === 0) this._unlisten();
        if (wasTop) this._restoreFocus(entry);
        return entry;
    }

    /** Close the top-most overlay: pop it, then call its onClose(reason). */
    closeTop(reason = 'programmatic') {
        const entry = this.pop();
        if (!entry) return null;
        if (typeof entry.onClose === 'function') {
            try {
                entry.onClose(reason);
            } catch (error) {
                console.error(`Error closing overlay ${entry.id}:`, error);
            }
        }
        return entry;
    }

    /** Close every overlay, top-most first. */
    closeAll(reason = 'programmatic') {
        const closed = [];
        while (this._stack.length) closed.push(this.closeTop(reason));
        return closed;
    }

    _restoreAttrs(entry) {
        const el = entry.element;
        const saved = entry._savedAttrs;
        if (!el || !saved) return;
        for (const [name, value] of Object.entries(saved)) {
            if (value === null) el.removeAttribute(name);
            else el.setAttribute(name, value);
        }
    }

    _restoreFocus(entry) {
        const trigger = entry.triggerElement;
        if (!trigger || trigger.isConnected === false) return;
        const body = this.document?.body;
        if (trigger === body) return;
        // Don't steal focus the user has already moved somewhere else.
        const active = this.document?.activeElement;
        if (!active || active === body || !entry.element || contains(entry.element, active)) focus(trigger);
    }

    _focusContainer(element) {
        if (typeof element.hasAttribute === 'function' && !element.hasAttribute('tabindex')) {
            element.setAttribute('tabindex', '-1');
        }
        focus(element);
    }

    _listen() {
        if (this._listening || !this.document?.addEventListener) return;
        this.document.addEventListener('keydown', this._onKeydown, true);
        this._listening = true;
    }

    _unlisten() {
        if (!this._listening) return;
        this.document.removeEventListener('keydown', this._onKeydown, true);
        this._listening = false;
    }

    _handleKeydown(event) {
        const top = this.peek();
        if (!top) return;
        if (event.key === 'Escape' || event.key === 'Esc') {
            if (!top.closeOnEscape) return;
            event.preventDefault?.();
            event.stopImmediatePropagation?.();
            event.stopPropagation?.();
            this.closeTop('escape');
            return;
        }
        if (event.key === 'Tab' && top.trapFocus && top.element) {
            this._trapTab(event, top.element);
        }
    }

    _trapTab(event, element) {
        const items = focusableIn(element);
        const active = this.document?.activeElement;
        if (items.length === 0) {
            event.preventDefault?.();
            this._focusContainer(element);
            return;
        }
        const first = items[0];
        const last = items[items.length - 1];
        const inside = contains(element, active);
        if (event.shiftKey) {
            if (!inside || active === first || active === element) {
                event.preventDefault?.();
                focus(last);
            }
        } else if (!inside || active === last) {
            event.preventDefault?.();
            focus(first);
        }
    }
}

export const overlayStack = new OverlayStack();

if (typeof window !== 'undefined') {
    window.overlayStack = overlayStack;
}
