'use client';

import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { type Notification, notificationsApi } from '@/services/notificationsApi';
import { useAuth } from './AuthContext';

interface NotificationsContextType {
  notifications: Notification[];
  unreadCount: number;
  showNotification: (title: string, message: string, type?: string) => void;
  markAsRead: (notificationIds: number[]) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  refreshNotifications: () => Promise<void>;
  refreshUnreadCount: () => Promise<void>;
}

const NotificationsContext = createContext<NotificationsContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationsContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationsProvider');
  }
  return context;
};

interface NotificationsProviderProps {
  children: React.ReactNode;
}

export const NotificationsProvider: React.FC<NotificationsProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const { user, accessToken } = useAuth();
  const wsRef = useRef<WebSocket | null>(null);

  // Show toast notification
  const showNotification = (title: string, message: string, type = 'info') => {
    // This would typically integrate with a toast library like react-hot-toast
    if (window.Notification && Notification.permission === 'granted') {
      new window.Notification(title, {
        body: message,
        icon: '/favicon.ico'
      });
    }
  };

  // Request notification permission
  useEffect(() => {
    if (window.Notification && Notification.permission === 'default') {
      window.Notification.requestPermission();
    }
  }, []);

  // Fetch initial notifications and unread count
  const refreshNotifications = async () => {
    if (!user) return;
    
    try {
      const response = await notificationsApi.getNotifications(50);
      setNotifications(response.notifications);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const refreshUnreadCount = async () => {
    if (!user) return;
    
    try {
      const response = await notificationsApi.getUnreadCount();
      setUnreadCount(response.unread_count);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  };

  // Mark notifications as read
  const markAsRead = async (notificationIds: number[]) => {
    try {
      await notificationsApi.markNotificationsRead(notificationIds);
      
      // Update local state
      setNotifications(prev => 
        prev.map(notification => 
          notificationIds.includes(notification.id)
            ? { ...notification, is_read: true, read_at: new Date().toISOString() }
            : notification
        )
      );
      
      await refreshUnreadCount();
    } catch (error) {
      console.error('Failed to mark notifications as read:', error);
    }
  };

  // Mark all notifications as read
  const markAllAsRead = async () => {
    try {
      await notificationsApi.markAllNotificationsRead();
      
      // Update local state
      setNotifications(prev => 
        prev.map(notification => ({ 
          ...notification, 
          is_read: true, 
          read_at: new Date().toISOString() 
        }))
      );
      
      setUnreadCount(0);
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error);
    }
  };

  // WebSocket connection for real-time notifications
  useEffect(() => {
    if (!user || !accessToken) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }

    const connectWebSocket = () => {
      const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/status?token=${accessToken}`;
      
      try {
        wsRef.current = new WebSocket(wsUrl);

        wsRef.current.onopen = () => {
          console.log('Notifications WebSocket connected');
        };

        wsRef.current.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            
            if (message.type === 'notification') {
              const notification = message.data;
              
              // Add to notifications list
              setNotifications(prev => [notification, ...prev]);
              
              // Increment unread count
              setUnreadCount(prev => prev + 1);
              
              // Show browser notification
              showNotification(notification.title, notification.message);
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        wsRef.current.onclose = () => {
          console.log('Notifications WebSocket disconnected');
          // Reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };

        wsRef.current.onerror = (error) => {
          console.error('Notifications WebSocket error:', error);
        };
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [user, accessToken]);

  // Load initial data when user logs in
  useEffect(() => {
    if (user) {
      refreshNotifications();
      refreshUnreadCount();
    } else {
      setNotifications([]);
      setUnreadCount(0);
    }
  }, [user]);

  const value: NotificationsContextType = {
    notifications,
    unreadCount,
    showNotification,
    markAsRead,
    markAllAsRead,
    refreshNotifications,
    refreshUnreadCount,
  };

  return (
    <NotificationsContext.Provider value={value}>
      {children}
    </NotificationsContext.Provider>
  );
};