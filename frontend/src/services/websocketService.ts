import { WS_URL } from '../api/endpoints';
import { OrderResponse } from '../types/order';

export type WSEventCallback = (payload: { event: string, order?: OrderResponse }) => void;

class WebSocketService {
  private socket: WebSocket | null = null;
  private listeners: WSEventCallback[] = [];
  private isConnecting = false;
  private reconnectTimeout: number | null = null;

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;
    this.socket = new WebSocket(`${WS_URL}/orders`);

    this.socket.onopen = () => {
      this.isConnecting = false;
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
        this.reconnectTimeout = null;
      }
      // Keep alive
      setInterval(() => {
        if (this.socket?.readyState === WebSocket.OPEN) {
          this.socket.send('ping');
        }
      }, 30000);
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'pong') return;
        
        this.listeners.forEach(listener => listener(data));
      } catch (err) {
        console.error("Error parsing WS message", err);
      }
    };

    this.socket.onclose = () => {
      this.isConnecting = false;
      this.socket = null;
      this.reconnectTimeout = window.setTimeout(() => this.connect(), 5000);
    };

    this.socket.onerror = (err) => {
      console.error('WebSocket Error:', err);
      this.socket?.close();
    };
  }

  disconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  subscribe(callback: WSEventCallback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(cb => cb !== callback);
    };
  }
}

export const websocketService = new WebSocketService();
