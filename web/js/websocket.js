/**
 * OREI Matrix Control - WebSocket Handler
 * Handles real-time updates from the matrix
 */

class MatrixWebSocket {
    constructor(options = {}) {
        this.onMessage = options.onMessage || (() => {});
        this.onStatusChange = options.onStatusChange || (() => {});
        this.onError = options.onError || (() => {});
        
        this.ws = null;
        this.connected = false;
        this.reconnectDelay = 1000;
        this.maxReconnectDelay = 30000;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 50;
        this.reconnectTimer = null;
        this.pingInterval = null;
        this.url = null;
    }

    /**
     * Connect to the WebSocket server
     */
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            Logger.log('WebSocket already connected');
            return;
        }

        // Build WebSocket URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.url = `${protocol}//${window.location.host}/ws`;

        Logger.log(`Connecting to WebSocket: ${this.url}`);

        try {
            this.ws = new WebSocket(this.url);
            this.setupEventHandlers();
        } catch (error) {
            console.error('WebSocket connection error:', error);
            this.scheduleReconnect();
        }
    }

    /**
     * Set up WebSocket event handlers
     */
    setupEventHandlers() {
        this.ws.onopen = () => {
            Logger.log('WebSocket connected');
            this.connected = true;
            this.reconnectDelay = 1000;
            this.reconnectAttempts = 0;
            this.onStatusChange(true);
            
            // Start ping interval to keep connection alive
            this.startPingInterval();
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        this.ws.onclose = (event) => {
            Logger.log(`WebSocket closed: code=${event.code}, reason=${event.reason}`);
            this.connected = false;
            this.onStatusChange(false);
            this.stopPingInterval();
            
            // Don't reconnect if closed intentionally
            if (event.code !== 1000) {
                this.scheduleReconnect();
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.onError(error);
        };
    }

    /**
     * Handle incoming WebSocket message
     */
    handleMessage(rawData) {
        Logger.ws('RX', rawData);
        
        // Normalize message format - server broadcasts use {"event": "...", "data": {...}}
        // Direct messages use {"type": "...", ...}
        let msgType = rawData.type || rawData.event;
        let data = rawData.data || rawData;
        
        // Handle different message types
        switch (msgType) {
            case 'status':
                // Full status update
                this.onMessage({ type: 'status', data: data });
                break;
                
            case 'switch':
                // Single route change
                this.onMessage({
                    type: 'switch',
                    output: data.output,
                    input: data.input
                });
                break;
            
            case 'switch_all':
                // All outputs routed to single input
                this.onMessage({
                    type: 'switch_all',
                    input: data.input,
                    outputs: data.outputs
                });
                break;
                
            case 'audio_mute':
                // Audio mute change
                this.onMessage({
                    type: 'audio_mute',
                    output: data.output,
                    muted: data.muted
                });
                break;
                
            case 'preset_recall':
                // Preset was recalled - need full refresh
                this.onMessage({
                    type: 'preset_recall',
                    preset: data.preset
                });
                break;
                
            case 'scene_recall':
                // Scene was recalled - need full refresh
                this.onMessage({
                    type: 'scene_recall',
                    scene: data.scene
                });
                break;
            
            case 'routing_change':
                // Routing changed from driver polling
                this.onMessage({
                    type: 'switch',
                    output: data.output,
                    input: data.input
                });
                break;
            
            case 'signal_change':
                // Input signal changed
                this.onMessage({
                    type: 'signal_change',
                    input: data.input,
                    active: data.active
                });
                break;
                
            case 'pong':
                // Ping response - connection is alive
                break;
                
            default:
                // Pass through unknown messages
                this.onMessage(rawData);
        }
    }

    /**
     * Schedule a reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }

        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('Max reconnection attempts reached');
            this.onError(new Error('Unable to connect to server'));
            return;
        }

        this.reconnectAttempts++;
        Logger.log(`Scheduling reconnect in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts})`);

        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, this.reconnectDelay);

        // Exponential backoff
        this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
    }

    /**
     * Start ping interval to keep connection alive
     */
    startPingInterval() {
        this.stopPingInterval();
        this.pingInterval = setInterval(() => {
            if (this.connected && this.ws.readyState === WebSocket.OPEN) {
                this.send({ type: 'ping' });
            }
        }, 30000);
    }

    /**
     * Stop ping interval
     */
    stopPingInterval() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }

    /**
     * Send a message to the server
     */
    send(data) {
        if (this.connected && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.warn('Cannot send - WebSocket not connected');
        }
    }

    /**
     * Disconnect from the WebSocket server
     */
    disconnect() {
        this.stopPingInterval();
        
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }

        if (this.ws) {
            this.ws.close(1000, 'Client disconnect');
            this.ws = null;
        }

        this.connected = false;
        this.onStatusChange(false);
    }

    /**
     * Check if connected
     */
    isConnected() {
        return this.connected && this.ws && this.ws.readyState === WebSocket.OPEN;
    }
}

// Export for use
window.MatrixWebSocket = MatrixWebSocket;
