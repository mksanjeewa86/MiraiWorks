import { useEffect, useRef, useCallback } from 'react';

interface WebSocketMessage {
  type: 'new_message' | 'conversation_updated' | 'user_online' | 'user_offline' | 'typing' | 'connected' | 'pong' | 'error';
  data: Record<string, unknown>;
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
    if (isConnectingRef.current || !token || !url) {
      console.log('WebSocket connect skipped - isConnecting:', isConnectingRef.current, 'token:', !!token, 'url:', !!url);
      return;
    }
    
    isConnectingRef.current = true;
    
    try {
      // Create WebSocket connection with token (add Bearer prefix for backend auth)
      const wsUrl = `${url}?token=${encodeURIComponent(`Bearer ${token}`)}`;
      console.log('Attempting WebSocket connection to:', wsUrl.replace(/token=[^&]*/, 'token=***REDACTED***'));
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected successfully');
        isConnectingRef.current = false;
        onConnect?.();
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('WebSocket message received:', message);
          
          // DEBUG: Extra logging for file messages
          if (message.type === 'new_message' && message.data) {
            console.log('New message details:', {
              type: message.data.type,
              file_url: message.data.file_url,
              file_name: message.data.file_name,
              content: message.data.content
            });
          }
          
          onMessage?.(message);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err, 'Raw data:', event.data);
        }
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected - Code:', event.code, 'Reason:', event.reason, 'Clean:', event.wasClean);
        
        // Log specific error codes for debugging
        if (event.code === 4003) {
          console.warn('WebSocket closed: Access denied to conversation');
        } else if (event.code === 1006) {
          console.warn('WebSocket closed: Connection failed (possibly authentication or network issue)');
        } else if (event.code === 4000) {
          console.warn('WebSocket closed: Internal server error');
        }
        
        isConnectingRef.current = false;
        ws.current = null;
        onDisconnect?.();
        
        // Only auto-reconnect on unexpected closures (not clean disconnections or access denied)
        if (!event.wasClean && event.code !== 1000 && event.code !== 4003) {
          console.log('Scheduling WebSocket reconnection in 3 seconds...');
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 3000);
        }
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

  const sendMessage = useCallback((message: Record<string, unknown>) => {
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