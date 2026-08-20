/* ═══════════════════════════════════════════════════════
 * TerminalX — WebSocket Connection Manager
 * ═══════════════════════════════════════════════════════ */

type MessageHandler = (data: unknown) => void;

interface WSChannel {
  handlers: Set<MessageHandler>;
}

class WebSocketManager {
  private ws: WebSocket | null = null;
  private url: string;
  private channels: Map<string, WSChannel> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private isIntentionalClose = false;
  private _isConnected = false;
  private connectionListeners: Set<(connected: boolean) => void> = new Set();

  constructor() {
    const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.url = apiBase.replace(/^http/, 'ws') + '/ws';
  }

  get isConnected(): boolean {
    return this._isConnected;
  }

  onConnectionChange(listener: (connected: boolean) => void): () => void {
    this.connectionListeners.add(listener);
    return () => this.connectionListeners.delete(listener);
  }

  private setConnected(value: boolean): void {
    this._isConnected = value;
    this.connectionListeners.forEach((fn) => fn(value));
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    this.isIntentionalClose = false;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('[TerminalX WS] Connected');
        this.reconnectAttempts = 0;
        this.setConnected(true);

        // Re-subscribe to all channels
        this.channels.forEach((_channel, name) => {
          this.send({ type: 'subscribe', channel: name });
        });
      };

      this.ws.onmessage = (event: MessageEvent) => {
        try {
          const msg = JSON.parse(event.data as string) as { channel?: string; data?: unknown };
          if (msg.channel) {
            const channel = this.channels.get(msg.channel);
            if (channel) {
              channel.handlers.forEach((handler) => handler(msg.data));
            }
          }
        } catch (err) {
          console.error('[TerminalX WS] Failed to parse message:', err);
        }
      };

      this.ws.onclose = () => {
        console.log('[TerminalX WS] Disconnected');
        this.setConnected(false);
        if (!this.isIntentionalClose) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = (error) => {
        console.error('[TerminalX WS] Connection failed. Is the Python backend running on port 8000?');
        this.setConnected(false);
      };
    } catch (error) {
      console.error('[TerminalX WS] Connection failed:', error);
      this.scheduleReconnect();
    }
  }

  disconnect(): void {
    this.isIntentionalClose = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.setConnected(false);
  }

  subscribe(channel: string, handler: MessageHandler): () => void {
    let ch = this.channels.get(channel);
    if (!ch) {
      ch = { handlers: new Set() };
      this.channels.set(channel, ch);
      // Tell the server we want this channel
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'subscribe', channel });
      }
    }
    ch.handlers.add(handler);

    return () => {
      ch!.handlers.delete(handler);
      if (ch!.handlers.size === 0) {
        this.channels.delete(channel);
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.send({ type: 'unsubscribe', channel });
        }
      }
    };
  }

  send(message: unknown): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[TerminalX WS] Max reconnect attempts reached');
      return;
    }
    // Exponential backoff: 1s, 2s, 4s, 8s… capped at 30s
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    console.log(`[TerminalX WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1})`);
    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }
}

// Singleton
export const wsManager = new WebSocketManager();
