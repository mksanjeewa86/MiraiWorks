import { useEffect, useRef, useCallback } from 'react';

interface WebSocketMessage {
  type: 'new_message' | 'conversation_updated' | 'user_online' | 'user_offline';
  data: any;
}

interface UseWebSocketOptions {
  url: string;
  token?: string;
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export const useWebSocket = ({
  url,
  token,
  onMessage,
  onConnect,
  onDisconnect,
  onError
}: UseWebSocketOptions) => {
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isConnectingRef = useRef(false);

  const connect = useCallback(() => {
    if (isConnectingRef.current || !token) return;
    
    isConnectingRef.current = true;
    
    try {
      // Create WebSocket connection with token
      const wsUrl = `${url}?token=${encodeURIComponent(token)}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        isConnectingRef.current = false;
        onConnect?.();
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          onMessage?.(message);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        isConnectingRef.current = false;
        ws.current = null;
        onDisconnect?.();
        
        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        isConnectingRef.current = false;
        onError?.(error);
      };
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      isConnectingRef.current = false;
    }
  }, [url, token, onMessage, onConnect, onDisconnect, onError]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    
    isConnectingRef.current = false;
  }, []);

  const sendMessage = useCallback((message: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  useEffect(() => {
    if (token) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [token, connect, disconnect]);

  return {
    isConnected: ws.current?.readyState === WebSocket.OPEN,
    sendMessage,
    disconnect
  };
};