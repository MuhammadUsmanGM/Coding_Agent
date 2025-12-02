import io from 'socket.io-client';

const SOCKET_URL = 'http://localhost:8080';

class SocketService {
  constructor() {
    this.socket = null;
    this.listeners = {};
    this.connected = false;
  }

  connect() {
    if (this.socket) {
      return; // Already connected
    }

    this.socket = io(SOCKET_URL);
    
    this.socket.on('connect', () => {
      console.log('✅ Socket connected');
      this.connected = true;
    });

    this.socket.on('disconnect', () => {
      console.log('❌ Socket disconnected');
      this.connected = false;
    });

    this.socket.on('reconnect_attempt', () => {
      console.log('🔄 Attempting to reconnect...');
    });

    this.socket.on('reconnect_failed', () => {
      console.error('❌ Failed to reconnect');
    });
  }

  on(event, callback) {
    if (!this.socket) {
      console.warn('Socket not initialized. Call connect() first.');
      return;
    }
    
    this.socket.on(event, callback);
    this.listeners[event] = callback;
  }

  off(event) {
    if (this.socket && this.listeners[event]) {
      this.socket.off(event, this.listeners[event]);
      delete this.listeners[event];
    }
  }

  emit(event, data) {
    if (!this.socket) {
      console.error('Socket not initialized');
      return;
    }

    if (!this.connected) {
      console.warn('Socket not connected, event may not be sent');
    }

    this.socket.emit(event, data);
  }

  disconnect() {
    if (this.socket) {
      // Remove all listeners
      Object.keys(this.listeners).forEach(event => this.off(event));
      
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }

  isConnected() {
    return this.connected && this.socket?.connected;
  }
}

// Export singleton instance
export default new SocketService();
