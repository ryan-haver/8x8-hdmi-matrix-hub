/**
 * XSS-safe HTML templating (SEC-08, UI-07).
 *
 *   el.innerHTML = html`<li title="${name}">${name}</li>`;
 *
 * - Every interpolated value is HTML-escaped, so markup in user or hub data
 *   (input names, profile names, error text) is shown as text, never parsed.
 * - Arrays are rendered item by item (each item escaped) and joined with ''.
 * - null, undefined and false render as '' so `${cond && html`...`}` works.
 * - html`` results and raw(...) values are inserted unescaped, so templates
 *   nest without double escaping. Only wrap markup you built yourself in raw().
 *
 * The raw marker is checked against a module-private brand, not just the
 * `__rawHtml` property, so a JSON payload such as {"__rawHtml": "<img ...>"}
 * from the hub cannot smuggle markup through.
 *
 * Classic (non-module) scripts get the same helpers as window.OrcaHtml.
 */

const trusted = new WeakSet();

/**
 * Escape text for use in element content or a quoted attribute value.
 * Same rules as Helpers.escapeHtml (SEC-07: quotes are escaped too).
 * @param {*} str - Value to escape; null and undefined become ''
 * @returns {string}
 */
export function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

/**
 * Mark markup as trusted so html`` inserts it unescaped.
 * @param {*} trustedHtml - Markup built by the app (never user or hub data)
 * @returns {{__rawHtml: string, toString: () => string}}
 */
export function raw(trustedHtml) {
    const value = Object.freeze({
        __rawHtml: String(trustedHtml ?? ''),
        toString() {
            return this.__rawHtml;
        },
    });
    trusted.add(value);
    return value;
}

/** True for values made by raw() or html`` (not for look-alike objects). */
export function isRaw(value) {
    return typeof value === 'object' && value !== null && trusted.has(value);
}

function render(value) {
    if (value === null || value === undefined || value === false) return '';
    if (isRaw(value)) return value.__rawHtml;
    if (Array.isArray(value)) return value.map(render).join('');
    return escapeHtml(value);
}

/**
 * Tagged template that escapes every interpolated value unless it is raw().
 * The result is itself raw, so it can be nested; String(result) or assigning
 * it to innerHTML gives the markup.
 */
export function html(strings, ...values) {
    let out = strings[0];
    for (let i = 0; i < values.length; i++) {
        out += render(values[i]) + strings[i + 1];
    }
    return raw(out);
}

if (typeof window !== 'undefined') {
    window.OrcaHtml = Object.freeze({ html, raw, escapeHtml });
}
