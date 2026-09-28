/**
 * Hub WebSocket client: the browser side of the /ws contract
 * (docs/api/WEBSOCKET.md, protocol 1). Used by the web UI (app.js) and the
 * kiosk (kiosk.html).
 *
 * - Messages are {event, data}; every one is handed to onMessage as
 *   {type: <event>, data: <payload>} (payloads are passed through unchanged).
 * - Reconnects for as long as the page is open (1 s doubling to 30 s). On
 *   every (re)connect the hub sends `connected` and a `status` snapshot, so a
 *   reconnect also resyncs the page (UI-03).
 * - Heartbeat: {command: 'ping'} every 25 s; a socket that has received
 *   nothing for 60 s is closed and reconnected. The hub also sends protocol
 *   pings, which the browser answers by itself (API-10).
 * - Tracks the matrix link the hub reports (`connected.matrix`,
 *   `matrix_connection`, `status`) and reports it through onMatrixStatus, so
 *   the page can tell "hub unreachable" from "matrix unreachable".
 */

const WS_PING_INTERVAL_MS = 25000;
const WS_SILENCE_LIMIT_MS = 60000;

class MatrixWebSocket {
    constructor(options = {}) {
        this.onMessage = options.onMessage || (() => {});
        this.onStatusChange = options.onStatusChange || (() => {});
        this.onMatrixStatus = options.onMatrixStatus || (() => {});
        this.onError = options.onError || (() => {});
        this.onReconnecting = options.onReconnecting || (() => {});

        this.ws = null;
        this.connected = false;
        this.reconnectDelay = 1000;
        this.maxReconnectDelay = 30000;
        this.reconnectAttempts = 0;
        this.reconnectTimer = null;
        this.pingInterval = null;
        this.url = null;
        this.protocol = null;
        this.lastMessageAt = 0;
        this.stopped = false;
        /** The matrix link as the hub last reported it: {connected, state, host} or null (not known yet). */
        this.matrix = null;
        this.status = 'disconnected'; // 'disconnected' | 'connecting' | 'connected' | 'reconnecting'
    }

    log(...args) {
        if (window.Logger && typeof window.Logger.log === 'function') window.Logger.log(...args);
    }

    /**
     * Connect to the hub's /ws
     */
    connect() {
        if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
            return;
        }
        this.stopped = false;
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.url = `${protocol}//${window.location.host}/ws`;
        this.status = this.reconnectAttempts > 0 ? 'reconnecting' : 'connecting';
        this.log(`Connecting to WebSocket: ${this.url}`);

        try {
            this.ws = new WebSocket(this.url);
            this.setupEventHandlers(this.ws);
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    }

    setupEventHandlers(ws) {
        ws.onopen = () => {
            if (ws !== this.ws) return;
            this.log('WebSocket connected');
            this.connected = true;
            this.status = 'connected';
            this.reconnectDelay = 1000;
            this.reconnectAttempts = 0;
            this.lastMessageAt = Date.now();
            this.onStatusChange(true);
            this.startPingInterval();
        };

        ws.onmessage = (event) => {
            if (ws !== this.ws) return;
            let msg;
            try {
                msg = JSON.parse(event.data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
                return;
            }
            this.handleMessage(msg);
        };

        ws.onclose = (event) => {
            if (ws !== this.ws) return;
            this.log(`WebSocket closed: code=${event.code}, reason=${event.reason}`);
            this.ws = null;
            this.connected = false;
            this.stopPingInterval();
            this.onStatusChange(false);
            if (!this.stopped) this.scheduleReconnect();
        };

        ws.onerror = (error) => {
            if (ws !== this.ws) return;
            this.onError(error);
        };
    }

    /**
     * One hub message: {event, data} (docs/api/WEBSOCKET.md)
     */
    handleMessage(msg) {
        this.lastMessageAt = Date.now();
        if (window.Logger && typeof window.Logger.ws === 'function') window.Logger.ws('RX', msg);
        const type = msg && msg.event;
        if (typeof type !== 'string') return;
        const data = msg.data && typeof msg.data === 'object' ? msg.data : {};

        switch (type) {
            case 'pong':
                return;
            case 'connected':
                this.protocol = data.protocol ?? null;
                if (data.matrix) this.setMatrix(data.matrix);
                break;
            case 'matrix_connection':
                this.setMatrix(data);
                break;
            case 'status':
                this.setMatrix({ connected: data.connected, state: data.state, host: data.host });
                break;
        }
        this.onMessage({ type, data });
    }

    setMatrix(link) {
        const next = {
            connected: link.connected === true,
            state: link.state || (link.connected ? 'connected' : 'disconnected'),
            host: link.host ?? null,
        };
        const prev = this.matrix;
        this.matrix = next;
        if (!prev || prev.connected !== next.connected || prev.state !== next.state) {
            this.onMatrixStatus(next);
        }
    }

    /** Ask the hub for a fresh `status` snapshot (e.g. after a failed command). */
    requestStatus() {
        this.send({ command: 'get_status' });
    }

    scheduleReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        this.reconnectAttempts++;
        this.status = 'reconnecting';
        const delayMs = this.reconnectDelay;
        this.log(`Scheduling reconnect in ${delayMs}ms (attempt ${this.reconnectAttempts})`);
        this.onReconnecting({ attempt: this.reconnectAttempts, delayMs });

        this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            this.connect();
        }, delayMs);

        this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
    }

    startPingInterval() {
        this.stopPingInterval();
        this.pingInterval = setInterval(() => {
            if (!this.isConnected()) return;
            if (Date.now() - this.lastMessageAt > WS_SILENCE_LIMIT_MS) {
                this.log('WebSocket silent for too long; reconnecting');
                this.ws.close(4000, 'No messages from the hub');
                return;
            }
            this.send({ command: 'ping' });
        }, WS_PING_INTERVAL_MS);
    }

    stopPingInterval() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    send(data) {
        if (this.isConnected()) {
            this.ws.send(JSON.stringify(data));
        }
    }

    /**
     * Close the socket and stop reconnecting
     */
    disconnect() {
        this.stopped = true;
        this.stopPingInterval();
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        const ws = this.ws;
        this.ws = null;
        if (ws) ws.close(1000, 'Client disconnect');
        const wasConnected = this.connected;
        this.connected = false;
        this.status = 'disconnected';
        if (wasConnected) this.onStatusChange(false);
    }

    isConnected() {
        return this.connected && !!this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

window.MatrixWebSocket = MatrixWebSocket;
