/**
 * WebSocket Chat Handler
 * Handles real-time chat communication using Django Channels
 */

class ChatWebSocket {
    constructor(roomId, onMessageReceived, onStatusChanged) {
        this.roomId = roomId;
        this.onMessageReceived = onMessageReceived;
        this.onStatusChanged = onStatusChanged;
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // 3 seconds
    }

    /**
     * Initialize WebSocket connection
     */
    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${this.roomId}/`;
        
        console.log(`🔌 Attempting to connect to WebSocket: ${wsUrl}`);
        
        try {
            this.socket = new WebSocket(wsUrl);
            this.setupEventHandlers();
        } catch (error) {
            console.error('❌ WebSocket connection failed:', error);
            this.handleConnectionError();
        }
    }

    /**
     * Setup WebSocket event handlers
     */
    setupEventHandlers() {
        this.socket.onopen = (e) => this.handleOpen(e);
        this.socket.onmessage = (e) => this.handleMessage(e);
        this.socket.onerror = (e) => this.handleError(e);
        this.socket.onclose = (e) => this.handleClose(e);
    }

    /**
     * Handle WebSocket connection opened
     */
    handleOpen(event) {
        console.log('✅ WebSocket connection established');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        
        if (this.onStatusChanged) {
            this.onStatusChanged({
                status: 'connected',
                message: '✅ Connected'
            });
        }
    }

    /**
     * Handle incoming messages
     */
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            console.log('📨 Message received:', data);

            if (this.onMessageReceived) {
                this.onMessageReceived(data);
            }
        } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
        }
    }

    /**
     * Handle WebSocket errors
     */
    handleError(error) {
        console.error('❌ WebSocket error:', error);
        
        if (this.onStatusChanged) {
            this.onStatusChanged({
                status: 'error',
                message: '❌ Connection Error'
            });
        }
    }

    /**
     * Handle WebSocket connection closed
     */
    handleClose(event) {
        console.warn('⚠️ WebSocket connection closed');
        this.isConnected = false;
        
        if (this.onStatusChanged) {
            this.onStatusChanged({
                status: 'disconnected',
                message: '❌ Disconnected'
            });
        }

        // Attempt to reconnect
        this.attemptReconnect();
    }

    /**
     * Attempt to reconnect with exponential backoff
     */
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            
            console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            if (this.onStatusChanged) {
                this.onStatusChanged({
                    status: 'reconnecting',
                    message: `🔄 Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`
                });
            }

            setTimeout(() => this.connect(), delay);
        } else {
            console.error('❌ Max reconnection attempts reached');
            
            if (this.onStatusChanged) {
                this.onStatusChanged({
                    status: 'failed',
                    message: '❌ Connection Failed - Please refresh the page'
                });
            }
        }
    }

    /**
     * Handle connection errors
     */
    handleConnectionError() {
        if (this.onStatusChanged) {
            this.onStatusChanged({
                status: 'error',
                message: '❌ Connection Error'
            });
        }
        this.attemptReconnect();
    }

    /**
     * Send message to WebSocket
     */
    sendMessage(message) {
        if (!this.isConnected || !this.socket) {
            console.error('❌ WebSocket is not connected');
            return false;
        }

        try {
            this.socket.send(JSON.stringify({
                'message': message
            }));
            console.log('📤 Message sent:', message);
            return true;
        } catch (error) {
            console.error('❌ Error sending message:', error);
            return false;
        }
    }

    /**
     * Close WebSocket connection
     */
    close() {
        if (this.socket) {
            this.socket.close();
            this.isConnected = false;
        }
    }

    /**
     * Get connection status
     */
    getStatus() {
        return this.isConnected ? 'connected' : 'disconnected';
    }
}

// Export for use in templates
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatWebSocket;
}
