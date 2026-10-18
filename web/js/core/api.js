/**
 * REST client for ES modules.
 *
 * - `api` is the page's existing window.api (web/js/api.js) when it is loaded,
 *   so modules and classic scripts share one client, its PIN prompts and its
 *   logging. Without it (kiosk, tests) `api` is a standalone MatrixApi.
 * - `ApiError` is window.ApiError when present, so `instanceof` holds for
 *   errors from either client.
 * - MatrixApi sends JSON, optionally an X-API-Key header, aborts after a
 *   timeout (UI-04) and rejects with ApiError {status, code, level, body}.
 *   A 401 (or a 403 asking for a PIN) dispatches `auth:required` on window
 *   with the same fields in event.detail, so one listener can prompt.
 */

const hasWindow = typeof window !== 'undefined';

const PIN_CODES = new Set(['admin_pin_required', 'control_pin_required']);

class StandaloneApiError extends Error {
    constructor(message, { status = 0, code = null, level = undefined, body = null, method = null, path = null } = {}) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.code = code;
        const resolvedLevel = level !== undefined ? level : StandaloneApiError.levelFrom(code, body);
        if (resolvedLevel !== undefined && resolvedLevel !== null) this.level = resolvedLevel;
        this.body = body;
        this.method = method;
        this.path = path;
    }

    /** The hub's machine-readable error code in an error body, if there is one. */
    static codeFrom(body) {
        const isCode = (v) => typeof v === 'string' && /^[a-z][a-z0-9_]*$/.test(v);
        if (isCode(body?.code)) return body.code;
        if (isCode(body?.data?.error)) return body.data.error;
        if (isCode(body?.error)) return body.error;
        return null;
    }

    /** The required access level ('admin' or 'control') for an auth error, if applicable. */
    static levelFrom(code, body) {
        if (body?.level === 'admin' || body?.level === 'control') return body.level;
        if (code === 'admin_pin_required') return 'admin';
        if (code === 'control_pin_required') return 'control';
        return undefined;
    }
}

export const ApiError = (hasWindow && typeof window.ApiError === 'function' && window.ApiError) || StandaloneApiError;

const codeFrom = (body) =>
    typeof ApiError.codeFrom === 'function' ? ApiError.codeFrom(body) : StandaloneApiError.codeFrom(body);

export class MatrixApi {
    static DEFAULT_TIMEOUT_MS = 30000;

    /**
     * @param {Object} [options]
     * @param {string} [options.baseUrl] - Defaults to the page's origin
     * @param {string|null} [options.apiKey] - Sent as X-API-Key when set
     * @param {number} [options.timeout] - Default request timeout in ms
     * @param {Function} [options.fetch] - fetch implementation (tests)
     * @param {EventTarget} [options.eventTarget] - Where auth:required is dispatched (default window)
     */
    constructor({ baseUrl, apiKey = null, timeout = MatrixApi.DEFAULT_TIMEOUT_MS, fetch: fetchImpl, eventTarget } = {}) {
        this.baseUrl = baseUrl ?? (hasWindow && window.location ? window.location.origin : '');
        this.apiKey = apiKey;
        this.timeout = timeout;
        this._fetch = fetchImpl || ((...args) => globalThis.fetch(...args));
        this._eventTarget = eventTarget || (hasWindow ? window : null);
    }

    setApiKey(apiKey) {
        this.apiKey = apiKey || null;
    }

    /**
     * One HTTP exchange. Resolves with the parsed JSON body of a 2xx answer
     * (null when it has none); rejects with an ApiError.
     */
    async request(method, path, { body, timeout = this.timeout, headers = {} } = {}) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), timeout);
        const init = { method, signal: controller.signal, headers: { Accept: 'application/json', ...headers } };
        if (this.apiKey) init.headers['X-API-Key'] = this.apiKey;
        if (body !== undefined) {
            init.headers['Content-Type'] = 'application/json';
            init.body = JSON.stringify(body);
        }
        try {
            let response;
            try {
                response = await this._fetch(`${this.baseUrl}${path}`, init);
            } catch (error) {
                throw MatrixApi._transportError(error, timeout, method, path);
            }
            const text = await response.text().catch(() => '');
            let data = null;
            if (text) {
                try {
                    data = JSON.parse(text);
                } catch {
                    data = response.ok ? null : { error: text.trim() };
                }
            }
            if (response.ok) return data;

            const code = codeFrom(data);
            const error = new ApiError(`HTTP ${response.status}`, { status: response.status, code, body: data, method, path });
            if (response.status === 401 || (response.status === 403 && PIN_CODES.has(code))) {
                this._dispatchAuthRequired(error);
            }
            throw error;
        } finally {
            clearTimeout(timer);
        }
    }

    _dispatchAuthRequired(error) {
        const target = this._eventTarget;
        if (!target || typeof target.dispatchEvent !== 'function' || typeof CustomEvent !== 'function') return;
        const { status, code, level, method, path } = error;
        target.dispatchEvent(new CustomEvent('auth:required', { detail: { status, code, level, method, path } }));
    }

    /** ApiError for a request that got no answer: timeout or network error. */
    static _transportError(error, timeout, method, path) {
        if (error instanceof ApiError) return error;
        if (error?.name === 'AbortError') {
            return new ApiError(`Request timed out after ${timeout / 1000} s`, { status: 0, code: 'timeout', method, path });
        }
        return new ApiError(error?.message || 'Network error', { status: 0, code: 'network', method, path });
    }

    get(path, options) {
        return this.request('GET', path, options);
    }

    post(path, body, options = {}) {
        return this.request('POST', path, { ...options, body });
    }

    put(path, body, options = {}) {
        return this.request('PUT', path, { ...options, body });
    }

    patch(path, body, options = {}) {
        return this.request('PATCH', path, { ...options, body });
    }

    delete(path, options) {
        return this.request('DELETE', path, options);
    }
}

export const api = (hasWindow && window.api) || new MatrixApi();
