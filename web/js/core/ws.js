/**
 * Hub WebSocket client for ES modules: the /ws contract of web/js/websocket.js
 * (docs/api/WEBSOCKET.md, protocol 1) with sturdier reconnects (UI-09).
 *
 * - Messages are {event, data}; each reaches onMessage as {type, data}.
 * - Reconnect backoff doubles from baseDelay and is capped at 30 s, whatever
 *   maxDelay is passed. At most one reconnect timer is pending: scheduling
 *   always clears the previous one first.
 * - When the tab becomes visible again or the browser goes back online, a
 *   pending reconnect is replaced by an immediate one (backoff reset).
 * - Every successful reconnect (not the first connect) calls onResync, so the
 *   page can reload anything it may have missed while offline. The hub also
 *   sends `connected` and a `status` snapshot on every connect.
 * - Heartbeat: {command: 'ping'} every 25 s; a socket silent for 60 s is
 *   closed and reconnected.
 */

export const MAX_RECONNECT_DELAY_MS = 30000;
const PING_INTERVAL_MS = 25000;
const SILENCE_LIMIT_MS = 60000;
const OPEN = 1;
const CONNECTING = 0;

const noop = () => {};

export class MatrixWebSocket {
    /**
     * @param {Object} [options]
     * @param {string} [options.url] - Defaults to ws(s)://<page host>/ws
     * @param {Function} [options.onMessage] - ({type, data})
     * @param {Function} [options.onStatusChange] - (connected: boolean)
     * @param {Function} [options.onReconnecting] - ({attempt, delayMs})
     * @param {Function} [options.onResync] - ({attempts}) after a reconnect succeeds
     * @param {Function} [options.onError]
     * @param {number} [options.baseDelay] - First reconnect delay in ms (default 1000)
     * @param {number} [options.maxDelay] - Backoff ceiling in ms, never above 30000
     * @param {Function} [options.WebSocketImpl] - WebSocket constructor (tests)
     * @param {Object} [options.timers] - {setTimeout, clearTimeout, setInterval, clearInterval} (tests)
     */
    constructor(options = {}) {
        this.onMessage = options.onMessage || noop;
        this.onStatusChange = options.onStatusChange || noop;
        this.onReconnecting = options.onReconnecting || noop;
        this.onResync = options.onResync || noop;
        this.onError = options.onError || noop;

        this.url = options.url || null;
        this.baseDelay = Math.max(1, options.baseDelay ?? 1000);
        this.maxDelay = Math.min(options.maxDelay ?? MAX_RECONNECT_DELAY_MS, MAX_RECONNECT_DELAY_MS);
        this.WebSocketImpl = options.WebSocketImpl || null;
        const t = options.timers || globalThis;
        this.timers = {
            setTimeout: t.setTimeout.bind(globalThis),
            clearTimeout: t.clearTimeout.bind(globalThis),
            setInterval: t.setInterval.bind(globalThis),
            clearInterval: t.clearInterval.bind(globalThis),
        };

        this.ws = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.reconnectDelay = this.baseDelay;
        this.reconnectTimer = null;
        this.pingInterval = null;
        this.lastMessageAt = 0;
        this.stopped = false;
        this.hasConnected = false;
        this.status = 'disconnected'; // 'disconnected' | 'connecting' | 'connected' | 'reconnecting'

        this._onVisibility = () => {
            if (globalThis.document?.visibilityState === 'visible') this.reconnectNow();
        };
        this._onOnline = () => this.reconnectNow();
        this._lifecycleBound = false;
    }

    /** Backoff before reconnect attempt `attempt` (1-based), capped at 30 s. */
    static backoffDelay(attempt, baseDelay = 1000, maxDelay = MAX_RECONNECT_DELAY_MS) {
        const cap = Math.min(maxDelay, MAX_RECONNECT_DELAY_MS);
        return Math.min(baseDelay * 2 ** Math.max(0, attempt - 1), cap);
    }

    _defaultUrl() {
        const loc = globalThis.location;
        const protocol = loc?.protocol === 'https:' ? 'wss:' : 'ws:';
        return `${protocol}//${loc?.host}/ws`;
    }

    connect() {
        if (this.ws && (this.ws.readyState === OPEN || this.ws.readyState === CONNECTING)) return;
        this.stopped = false;
        this._bindLifecycle();
        if (!this.url) this.url = this._defaultUrl();
        this.status = this.reconnectAttempts > 0 ? 'reconnecting' : 'connecting';
        const Impl = this.WebSocketImpl || globalThis.WebSocket;
        try {
            this.ws = new Impl(this.url);
            this._setupEventHandlers(this.ws);
        } catch (error) {
            this.ws = null;
            this.onError(error);
            this.scheduleReconnect();
        }
    }

    _setupEventHandlers(ws) {
        ws.onopen = () => {
            if (ws !== this.ws) return;
            const resync = this.hasConnected;
            const attempts = this.reconnectAttempts;
            this.connected = true;
            this.hasConnected = true;
            this.status = 'connected';
            this.reconnectAttempts = 0;
            this.reconnectDelay = this.baseDelay;
            this.lastMessageAt = Date.now();
            this.onStatusChange(true);
            this._startPing();
            if (resync) this.onResync({ attempts });
        };

        ws.onmessage = (event) => {
            if (ws !== this.ws) return;
            let msg;
            try {
                msg = JSON.parse(event.data);
            } catch {
                return;
            }
            this.lastMessageAt = Date.now();
            if (!msg || typeof msg.event !== 'string' || msg.event === 'pong') return;
            const data = msg.data && typeof msg.data === 'object' ? msg.data : {};
            this.onMessage({ type: msg.event, data });
        };

        ws.onclose = () => {
            if (ws !== this.ws) return;
            this.ws = null;
            const wasConnected = this.connected;
            this.connected = false;
            this._stopPing();
            if (wasConnected) this.onStatusChange(false);
            if (!this.stopped) this.scheduleReconnect();
        };

        ws.onerror = (error) => {
            if (ws !== this.ws) return;
            this.onError(error);
        };
    }

    /** Schedule the next reconnect, replacing any pending one. */
    scheduleReconnect() {
        if (this.stopped) return;
        this._clearReconnectTimer();
        this.reconnectAttempts++;
        this.status = 'reconnecting';
        const delayMs = Math.min(this.reconnectDelay, this.maxDelay);
        this.onReconnecting({ attempt: this.reconnectAttempts, delayMs });
        this.reconnectTimer = this.timers.setTimeout(() => {
            this.reconnectTimer = null;
            this.connect();
        }, delayMs);
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxDelay);
    }

    /** Skip the remaining backoff and reconnect now (tab visible again, network back). */
    reconnectNow() {
        if (this.stopped || this.isConnected()) return;
        if (this.ws && this.ws.readyState === CONNECTING) return;
        this._clearReconnectTimer();
        this.reconnectDelay = this.baseDelay;
        this.connect();
    }

    _clearReconnectTimer() {
        if (this.reconnectTimer !== null) {
            this.timers.clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }

    _bindLifecycle() {
        if (this._lifecycleBound) return;
        globalThis.document?.addEventListener?.('visibilitychange', this._onVisibility);
        globalThis.window?.addEventListener?.('online', this._onOnline);
        this._lifecycleBound = true;
    }

    _unbindLifecycle() {
        if (!this._lifecycleBound) return;
        globalThis.document?.removeEventListener?.('visibilitychange', this._onVisibility);
        globalThis.window?.removeEventListener?.('online', this._onOnline);
        this._lifecycleBound = false;
    }

    _startPing() {
        this._stopPing();
        this.pingInterval = this.timers.setInterval(() => {
            if (!this.isConnected()) return;
            if (Date.now() - this.lastMessageAt > SILENCE_LIMIT_MS) {
                this.ws.close(4000, 'No messages from the hub');
                return;
            }
            this.send({ command: 'ping' });
        }, PING_INTERVAL_MS);
    }

    _stopPing() {
        if (this.pingInterval !== null) {
            this.timers.clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    send(data) {
        if (!this.isConnected()) return false;
        this.ws.send(JSON.stringify(data));
        return true;
    }

    /** Ask the hub for a fresh `status` snapshot. */
    requestStatus() {
        return this.send({ command: 'get_status' });
    }

    /** Close the socket and stop reconnecting. */
    disconnect() {
        this.stopped = true;
        this._stopPing();
        this._clearReconnectTimer();
        this._unbindLifecycle();
        const ws = this.ws;
        this.ws = null;
        if (ws) ws.close(1000, 'Client disconnect');
        const wasConnected = this.connected;
        this.connected = false;
        this.status = 'disconnected';
        this.reconnectAttempts = 0;
        this.reconnectDelay = this.baseDelay;
        if (wasConnected) this.onStatusChange(false);
    }

    isConnected() {
        return this.connected && !!this.ws && this.ws.readyState === OPEN;
    }
}

export const ws = new MatrixWebSocket();
