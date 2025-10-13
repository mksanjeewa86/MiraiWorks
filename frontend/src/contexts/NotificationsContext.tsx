'use client';

import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { AppNotification } from '@/types/notification';
import { notificationsApi } from '@/api/notifications';
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
  const showNotification = (title: string, message: string) => {
    // This would typically integrate with a toast library like react-hot-toast
    if (window.Notification && Notification.permission === 'granted') {
      new window.Notification(title, {
        body: message,
        icon: '/favicon.ico',
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
  const refreshNotifications = useCallback(async () => {
    if (!user) return;

    try {
      const response = await notificationsApi.getNotifications(50);
      setNotifications(response.notifications);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  }, [user]);

  const refreshUnreadCount = useCallback(async () => {
    if (!user) return;

    try {
      const response = await notificationsApi.getUnreadCount();
      setUnreadCount(response.unread_count);
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  }, [user]);

  // Mark notifications as read
  const markAsRead = async (notificationIds: number[]) => {
    try {
      await notificationsApi.markNotificationsRead(notificationIds);

      // Update local state
      setNotifications((prev) =>
        prev.map((notification) =>
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
      setNotifications((prev) =>
        prev.map((notification) => ({
          ...notification,
          is_read: true,
          read_at: new Date().toISOString(),
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
    let consecutiveErrors = 0;

    // Delay first poll by 2 seconds to avoid racing with initial auth
    const INITIAL_DELAY = 2000;
    const POLL_INTERVAL = 30000; // 30 seconds

    const pollForNotifications = async () => {
      try {
        // Get latest notifications
        const response = await notificationsApi.getNotifications(10);
        const latestNotifications = response.notifications;

        // Reset error counter on successful request
        consecutiveErrors = 0;

        if (latestNotifications.length > 0) {
          const newestNotificationId = latestNotifications[0].id;

          // Check if we have new notifications
          if (lastNotificationId === 0) {
            // First poll - just set the baseline
            lastNotificationId = newestNotificationId;
          } else if (newestNotificationId > lastNotificationId) {
            // We have new notifications
            const newNotifications = latestNotifications.filter(
              (notif) => notif.id > lastNotificationId
            );

            // Add new notifications to the state
            setNotifications((prev) => [...newNotifications, ...prev]);

            // Show browser notifications for new ones
            newNotifications.forEach((notif) => {
              showNotification(notif.title, notif.message);
            });

            // Update the baseline
            lastNotificationId = newestNotificationId;

            // Refresh unread count
            await refreshUnreadCount();
          }
        }
      } catch (error: unknown) {
        consecutiveErrors++;

        // Check if it's an authentication/session error
        const isAuthError = error instanceof Error &&
          (error.message.includes('Authentication failed') ||
           error.message.includes('Unauthorized') ||
           error.message.includes('Session refresh failed') ||
           error.message.includes('Invalid or expired refresh token'));

        if (isAuthError) {
          // Authentication error - stop polling immediately
          console.warn('Authentication/session error in notification polling, stopping');
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          return; // Exit early for auth errors
        }

        console.error('Failed to poll for notifications:', error);

        // If we get too many consecutive errors, stop polling
        if (consecutiveErrors >= 3) {
          console.warn('Too many consecutive polling errors, stopping notifications polling');
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
        }
      }
    };

    // Delay initial poll to avoid racing with auth initialization
    const initialPollTimeout = setTimeout(() => {
      pollForNotifications();
    }, INITIAL_DELAY);

    // Set up polling interval (every 30 seconds) after initial delay
    const intervalStartTimeout = setTimeout(() => {
      pollingIntervalRef.current = setInterval(pollForNotifications, POLL_INTERVAL);
    }, INITIAL_DELAY);

    return () => {
      clearTimeout(initialPollTimeout);
      clearTimeout(intervalStartTimeout);
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    };
  }, [user, accessToken, refreshUnreadCount]);

  // Load initial data when user logs in
  useEffect(() => {
    if (user) {
      refreshNotifications();
      refreshUnreadCount();
    } else {
      setNotifications([]);
      setUnreadCount(0);
    }
  }, [user, refreshNotifications, refreshUnreadCount]);

  const value: NotificationsContextType = {
    notifications,
    unreadCount,
    showNotification,
    markAsRead,
    markAllAsRead,
    refreshNotifications,
    refreshUnreadCount,
  };

  return <NotificationsContext.Provider value={value}>{children}</NotificationsContext.Provider>;
};
