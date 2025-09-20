import { useEffect, useRef, useCallback } from 'react';
import { SSEMessage, UseSSEOptions } from '@/types';

export const useServerSentEvents = ({
  url,
  token,
  onMessage,
  onConnect,
  onError
}: UseSSEOptions) => {
  const eventSourceRef = useRef<EventSource | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const connect = useCallback(() => {
    if (!token || eventSourceRef.current) return;
    
    try {
      // Create SSE connection with token
      const sseUrl = `${url}?token=${encodeURIComponent(token)}`;
      eventSourceRef.current = new EventSource(sseUrl);

      eventSourceRef.current.onopen = () => {
        onConnect?.();
      };

      eventSourceRef.current.onmessage = (event) => {
        try {
          const message: SSEMessage = JSON.parse(event.data);
          onMessage?.(message);
        } catch (err) {
          console.error('Failed to parse SSE message:', err);
        }
      };

      eventSourceRef.current.onerror = (error) => {
        console.error('SSE error:', error);
        onError?.(error);
        
        // Clean up and attempt to reconnect after 5 seconds
        if (eventSourceRef.current) {
          eventSourceRef.current.close();
          eventSourceRef.current = null;
        }
        
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 5000);
      };
    } catch (err) {
      console.error('Failed to create SSE connection:', err);
    }
  }, [url, token, onMessage, onConnect, onError]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
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
    isConnected: eventSourceRef.current?.readyState === EventSource.OPEN,
    disconnect
  };
};