import { io } from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 5000; // 5 seconds
  }

  connect() {
    if (this.socket?.connected) {
      return;
    }

    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
    
    this.socket = io(wsUrl, {
      transports: ['websocket'],
      timeout: 20000,
      forceNew: true,
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.isConnected = true;
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      this.isConnected = false;
      
      if (reason === 'io server disconnect') {
        // Server disconnected, try to reconnect
        this.handleReconnect();
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.handleReconnect();
    });

    // Chat events
    this.socket.on('chat_response', (data) => {
      console.log('Chat response received:', data);
    });

    this.socket.on('typing', (data) => {
      console.log('Typing indicator:', data);
    });

    this.socket.on('tool_result', (data) => {
      console.log('Tool execution result:', data);
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectInterval);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  // Chat methods
  sendChatMessage(message) {
    if (this.socket?.connected) {
      this.socket.emit('chat', { content: message });
    } else {
      console.warn('WebSocket not connected');
    }
  }

  // Tool execution
  executeTool(toolName, toolArguments) {
    if (this.socket?.connected) {
      this.socket.emit('tool_execute', {
        tool_name: toolName,
        arguments: toolArguments,
      });
    } else {
      console.warn('WebSocket not connected');
    }
  }

  // Event listeners
  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  off(event, callback) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  emit(event, data) {
    if (this.socket?.connected) {
      this.socket.emit(event, data);
    } else {
      console.warn('WebSocket not connected');
    }
  }

  // Connection status
  get connected() {
    return this.isConnected && this.socket?.connected;
  }

  // Ping/pong for connection health
  ping() {
    if (this.socket?.connected) {
      this.socket.emit('ping');
    }
  }
}

// Create singleton instance
const socket = new WebSocketService();

export { socket };
export default socket;
