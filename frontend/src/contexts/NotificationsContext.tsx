'use client';

import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { AppNotification } from "@/types/notification";
import { notificationsApi } from "@/api/notifications";
import { useAuth } from './AuthContext';
import type { NotificationsContextType, NotificationsProviderProps } from '@/types/contexts';

const NotificationsContext = createContext<NotificationsContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationsContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationsProvider');
  }
  return context;
};

export const NotificationsProvider: React.FC<NotificationsProviderProps> = ({ children }) => {
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const { user, accessToken } = useAuth();
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

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

  // Polling for real-time notifications
  useEffect(() => {
    if (!user || !accessToken) {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
      return;
    }

    let lastNotificationId = 0;

    const pollForNotifications = async () => {
      try {
        // Get latest notifications
        const response = await notificationsApi.getNotifications(10);
        const latestNotifications = response.notifications;
        
        if (latestNotifications.length > 0) {
          const newestNotificationId = latestNotifications[0].id;
          
          // Check if we have new notifications
          if (lastNotificationId === 0) {
            // First poll - just set the baseline
            lastNotificationId = newestNotificationId;
          } else if (newestNotificationId > lastNotificationId) {
            // We have new notifications
            const newNotifications = latestNotifications.filter(
              notif => notif.id > lastNotificationId
            );
            
            // Add new notifications to the state
            setNotifications(prev => [...newNotifications, ...prev]);
            
            // Show browser notifications for new ones
            newNotifications.forEach(notif => {
              showNotification(notif.title, notif.message);
            });
            
            // Update the baseline
            lastNotificationId = newestNotificationId;
            
            // Refresh unread count
            await refreshUnreadCount();
          }
        }
      } catch (error) {
        console.error('Failed to poll for notifications:', error);
      }
    };

    // Initial poll
    pollForNotifications();

    // Set up polling interval (every 30 seconds)
    pollingIntervalRef.current = setInterval(pollForNotifications, 30000);

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
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