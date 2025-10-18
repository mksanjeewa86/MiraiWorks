'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Bell, CheckCheck, Megaphone } from 'lucide-react';
import { useNotifications } from '@/contexts/NotificationsContext';
import { useAuth } from '@/contexts/AuthContext';
import { useLocaleRouter } from '@/hooks/useLocaleRouter';
import { ROUTES } from '@/routes/config';
import { getRoleColorScheme } from '@/utils/roleColorSchemes';
import { AppNotification } from '../../types/notification';
import { systemUpdatesApi } from '@/api/systemUpdates';
import type { SystemUpdate } from '@/types/system-update';

const NotificationDropdown: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useLocaleRouter();
  const { user, isLoading } = useAuth();
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications();
  const [systemUpdates, setSystemUpdates] = useState<SystemUpdate[]>([]);
  const [activeTab, setActiveTab] = useState<'notifications' | 'updates'>('notifications');

  // Get color scheme based on user role
  const colorScheme = getRoleColorScheme(user?.roles);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch system updates when dropdown opens
  useEffect(() => {
    // Wait for auth initialization to complete before fetching
    if (isLoading) {
      return;
    }

    const fetchSystemUpdates = async () => {
      if (isOpen && user) {
        const response = await systemUpdatesApi.getAll({ limit: 5 });
        if (response.success && response.data) {
          setSystemUpdates(response.data);
          // Set default tab based on available content
          if (response.data.length > 0 && notifications.length === 0) {
            setActiveTab('updates');
          } else {
            setActiveTab('notifications');
          }
        }
      }
    };

    fetchSystemUpdates();
  }, [isOpen, notifications.length, isLoading, user]);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  const handleNotificationClick = async (notification: AppNotification) => {
    if (!notification.is_read) {
      await markAsRead([notification.id]);
    }
    setIsOpen(false);
    router.push(`${ROUTES.NOTIFICATIONS.BASE}?highlight=notification-${notification.id}`);
  };

  const handleSystemUpdateClick = (updateId: number) => {
    setIsOpen(false);
    router.push(`${ROUTES.NOTIFICATIONS.BASE}?highlight=update-${updateId}&filter=updates`);
  };

  const handleMarkAllRead = async () => {
    await markAllAsRead();
  };

  const handleViewAll = () => {
    setIsOpen(false);
    if (activeTab === 'updates') {
      router.push(`${ROUTES.NOTIFICATIONS.BASE}?filter=updates`);
    } else {
      router.push(ROUTES.NOTIFICATIONS.BASE);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Notification Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        aria-label="Notifications"
      >
        <Bell className="h-6 w-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
          {/* Header */}
          <div className={`relative overflow-hidden ${colorScheme.background}`}>
            {/* Background Overlay */}
            <div className={`absolute inset-0 ${colorScheme.backgroundOverlay}`}></div>

            {/* Animated Pattern Overlay */}
            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djQtNCAzNmgtNHY0LTQtMzZoNHYzNnoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-30"></div>

            {/* Content */}
            <div className="relative p-3">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`w-8 h-8 ${colorScheme.brandAccent} rounded-lg flex items-center justify-center shadow-lg`}>
                    <Bell className={`h-4 w-4 ${colorScheme.textPrimary}`} />
                  </div>
                  <div>
                    <h3 className={`text-base font-bold ${colorScheme.textPrimary}`}>Notifications</h3>
                    <p className={`text-xs ${colorScheme.textSecondary}`}>
                      {activeTab === 'notifications'
                        ? notifications.length > 0
                          ? `${notifications.length} ${notifications.length === 1 ? 'notification' : 'notifications'}`
                          : 'No notifications'
                        : systemUpdates.length > 0
                          ? `${systemUpdates.length} ${systemUpdates.length === 1 ? 'update' : 'updates'}`
                          : 'No updates'
                      }
                    </p>
                  </div>
                </div>

                {unreadCount > 0 && activeTab === 'notifications' && (
                  <div className="flex items-center gap-2">
                    <div className={`px-2.5 py-1 ${colorScheme.activeIndicator} rounded-full shadow-lg`}>
                      <span className="text-xs font-bold text-white">{unreadCount} new</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Tabs - only show if both types have content */}
              {notifications.length > 0 && systemUpdates.length > 0 && (
                <div className="flex gap-2 mb-2">
                  <button
                    onClick={() => setActiveTab('notifications')}
                    className={`flex-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      activeTab === 'notifications'
                        ? `${colorScheme.buttonActive} ${colorScheme.textPrimary}`
                        : `${colorScheme.buttonHover} backdrop-blur-sm ${colorScheme.textSecondary}`
                    }`}
                  >
                    Notifications ({notifications.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('updates')}
                    className={`flex-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                      activeTab === 'updates'
                        ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
                        : `${colorScheme.buttonHover} backdrop-blur-sm ${colorScheme.textSecondary}`
                    }`}
                  >
                    Updates ({systemUpdates.length})
                  </button>
                </div>
              )}

              {/* Actions Row */}
              {unreadCount > 0 && activeTab === 'notifications' && (
                <button
                  onClick={handleMarkAllRead}
                  className={`w-full flex items-center justify-center gap-2 px-3 py-2 ${colorScheme.buttonHover} backdrop-blur-sm ${colorScheme.textPrimary} rounded-lg transition-all duration-200 border ${colorScheme.buttonBorder} group`}
                >
                  <CheckCheck className="h-3.5 w-3.5 group-hover:scale-110 transition-transform" />
                  <span className="text-xs font-medium">Mark all as read</span>
                </button>
              )}
            </div>
          </div>

          {/* Notifications List */}
          <div className="min-h-[400px]">
            {/* System Updates Tab */}
            {activeTab === 'updates' && systemUpdates.length > 0 && (
              <>
                {systemUpdates.slice(0, 5).map((update, index) => (
                  <div
                    key={`update-${update.id}`}
                    onClick={() => handleSystemUpdateClick(update.id)}
                    className="group p-2.5 cursor-pointer transition-all duration-200 border-b border-gray-100 dark:border-gray-700 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/10 dark:to-blue-900/10 hover:from-purple-100 hover:to-blue-100 dark:hover:from-purple-900/20 dark:hover:to-blue-900/20"
                  >
                    <div className="flex items-start gap-2">
                      <div className="flex-shrink-0">
                        <div className="w-7 h-7 rounded-lg flex items-center justify-center text-sm transition-transform group-hover:scale-110 bg-gradient-to-br from-purple-500 to-blue-500">
                          <Megaphone className="h-4 w-4 text-white" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-semibold text-gray-900 dark:text-white line-clamp-1 transition-colors leading-tight">
                          {update.title}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5 line-clamp-2 leading-tight">
                          {update.message}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 leading-tight">
                          {formatTime(update.created_at)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </>
            )}

            {/* Regular Notifications Tab */}
            {activeTab === 'notifications' && notifications.length > 0 && (
              <>
                {notifications.slice(0, 5).map((notification, index) => (
                  <div
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification)}
                    className={`group p-2.5 cursor-pointer transition-all duration-200 ${
                      index !== Math.min(5, notifications.length) - 1 ? 'border-b border-gray-100 dark:border-gray-700' : ''
                    } ${
                      !notification.is_read
                        ? `${colorScheme.buttonActive} bg-opacity-10 dark:bg-opacity-5 ${colorScheme.buttonHover}`
                        : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <div className="flex-shrink-0">
                        <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-sm transition-transform group-hover:scale-110 ${
                          !notification.is_read
                            ? colorScheme.brandAccent
                            : 'bg-gray-100 dark:bg-gray-700'
                        }`}>
                          {notification.type === 'new_message' && '💬'}
                          {notification.type === 'interview_scheduled' && '📅'}
                          {notification.type === 'exam_assigned' && '📝'}
                          {notification.type === 'application_update' && '📋'}
                          {!['new_message', 'interview_scheduled', 'exam_assigned', 'application_update'].includes(notification.type) && '🔔'}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-1.5">
                          <p className={`text-xs font-semibold text-gray-900 dark:text-white line-clamp-1 transition-colors leading-tight ${!notification.is_read ? `group-hover:${colorScheme.activeIndicator.replace('bg-', 'text-')}` : ''}`}>
                            {notification.title}
                          </p>
                          {!notification.is_read && (
                            <div className="flex-shrink-0">
                              <div className={`w-1.5 h-1.5 ${colorScheme.activeIndicator} rounded-full animate-pulse shadow-lg ${colorScheme.activeIndicatorShadow}`} />
                            </div>
                          )}
                        </div>
                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-0.5 line-clamp-1 leading-tight">
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between mt-1">
                          <p className="text-xs text-gray-500 dark:text-gray-400 leading-tight">
                            {formatTime(notification.created_at)}
                          </p>
                          {!notification.is_read && (
                            <span className={`text-xs font-semibold leading-tight ${colorScheme.activeIndicator.replace('bg-', 'text-')}`}>New</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </>
            )}

            {/* Empty State */}
            {((activeTab === 'notifications' && notifications.length === 0) ||
              (activeTab === 'updates' && systemUpdates.length === 0) ||
              (systemUpdates.length === 0 && notifications.length === 0)) && (
              <div className="p-8 text-center">
                <div className="w-12 h-12 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-800 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <Bell className="h-6 w-6 text-gray-400 dark:text-gray-500" />
                </div>
                <p className="text-sm font-medium text-gray-900 dark:text-white mb-1">No notifications yet</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">We'll notify you when something arrives</p>
              </div>
            )}
          </div>

          {/* Footer */}
          {((activeTab === 'notifications' && notifications.length > 5) ||
            (activeTab === 'updates' && systemUpdates.length > 0)) && (
            <div className={`p-3 border-t ${colorScheme.border} ${colorScheme.headerBackground}`}>
              <button
                onClick={handleViewAll}
                className={`w-full px-3 py-2 ${
                  activeTab === 'updates'
                    ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
                    : `${colorScheme.buttonActive} ${colorScheme.textPrimary}`
                } text-sm font-medium rounded-lg transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-[1.02]`}
              >
                View all {activeTab === 'updates' ? 'updates' : 'notifications'}
                {activeTab === 'updates' && systemUpdates.length > 5 && ` (${systemUpdates.length})`}
                {activeTab === 'notifications' && ` (${notifications.length})`}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NotificationDropdown;
