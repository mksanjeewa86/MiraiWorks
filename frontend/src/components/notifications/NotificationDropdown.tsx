'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Bell, CheckCheck, Megaphone, Sparkles } from 'lucide-react';
import { useNotifications } from '@/contexts/NotificationsContext';
import { useAuth } from '@/contexts/AuthContext';
import { useLocaleRouter } from '@/hooks/useLocaleRouter';
import { ROUTES } from '@/routes/config';
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
        className="relative p-2.5 text-slate-600 hover:text-slate-900 rounded-xl hover:bg-slate-100/80 transition-all duration-200"
        aria-label="Notifications"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-gradient-to-br from-rose-500 to-pink-600 text-white text-xs font-bold rounded-full min-w-[20px] h-[20px] flex items-center justify-center shadow-lg border-2 border-white z-10">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-[380px] bg-white border border-slate-200 rounded-2xl shadow-xl z-50 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 px-3 py-2.5 border-b border-slate-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                  <Bell className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900">Notifications</h3>
                  <p className="text-xs text-slate-600">
                    {activeTab === 'notifications'
                      ? notifications.length > 0
                        ? `${notifications.length} ${notifications.length === 1 ? 'notification' : 'notifications'}`
                        : 'All caught up!'
                      : systemUpdates.length > 0
                        ? `${systemUpdates.length} ${systemUpdates.length === 1 ? 'update' : 'updates'}`
                        : 'No updates'
                    }
                  </p>
                </div>
              </div>
            </div>

            {/* Tabs - only show if both types have content */}
            {notifications.length > 0 && systemUpdates.length > 0 && (
              <div className="flex gap-1 mt-2 p-0.5 bg-white/60 rounded-lg">
                <button
                  onClick={() => setActiveTab('notifications')}
                  className={`flex-1 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                    activeTab === 'notifications'
                      ? 'bg-white text-slate-900 shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <span>Notifications</span>
                  {notifications.length > 0 && (
                    <span className={`ml-1 ${activeTab === 'notifications' ? 'text-blue-600' : 'text-slate-400'}`}>
                      {notifications.length}
                    </span>
                  )}
                </button>
                <button
                  onClick={() => setActiveTab('updates')}
                  className={`flex-1 px-3 py-1.5 rounded-md text-xs font-semibold transition-all ${
                    activeTab === 'updates'
                      ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  <Sparkles className="inline h-3 w-3 mr-0.5" />
                  <span>Updates</span>
                  {systemUpdates.length > 0 && (
                    <span className={`ml-1 ${activeTab === 'updates' ? 'text-white' : 'text-slate-400'}`}>
                      {systemUpdates.length}
                    </span>
                  )}
                </button>
              </div>
            )}

            {/* Mark All Read Button */}
            {unreadCount > 0 && activeTab === 'notifications' && (
              <button
                onClick={handleMarkAllRead}
                className="w-full mt-2 flex items-center justify-center gap-1.5 px-3 py-1.5 bg-white/60 text-slate-700 rounded-lg text-xs font-medium border border-slate-200 hover:bg-white hover:border-slate-300"
              >
                <CheckCheck className="h-3.5 w-3.5 text-blue-600" />
                <span>Mark all as read</span>
              </button>
            )}
          </div>

          {/* Notifications List - Fixed Height */}
          <div className="h-[320px] overflow-y-auto">
            {/* System Updates Tab */}
            {activeTab === 'updates' && systemUpdates.length > 0 && (
              <>
                {systemUpdates.slice(0, 5).map((update, index) => (
                  <div
                    key={`update-${update.id}`}
                    onClick={() => handleSystemUpdateClick(update.id)}
                    className="group px-3 py-2.5 cursor-pointer border-b border-slate-100 hover:bg-gradient-to-r hover:from-purple-50/50 hover:to-blue-50/50"
                  >
                    <div className="flex items-start gap-2">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-gradient-to-br from-purple-500 to-blue-500">
                          <Megaphone className="h-4 w-4 text-white" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-slate-900 line-clamp-1">
                          {update.title}
                        </p>
                        <p className="text-xs text-slate-600 line-clamp-2 mt-0.5">
                          {update.message}
                        </p>
                        <p className="text-xs text-slate-500 font-medium mt-1">
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
                {notifications.slice(0, 5).map((notification) => (
                  <div
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification)}
                    className={`group px-3 py-2.5 cursor-pointer border-b border-slate-100 ${
                      !notification.is_read
                        ? 'bg-gradient-to-r from-blue-50/50 to-indigo-50/50 hover:from-blue-50 hover:to-indigo-50'
                        : 'hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-start gap-2">
                      <div className="flex-shrink-0">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm ${
                          !notification.is_read
                            ? 'bg-gradient-to-br from-blue-500 to-indigo-600'
                            : 'bg-slate-100'
                        }`}>
                          {notification.type === 'new_message' && <span className={!notification.is_read ? 'text-white' : 'text-slate-600'}>💬</span>}
                          {notification.type === 'interview_scheduled' && <span className={!notification.is_read ? 'text-white' : 'text-slate-600'}>📅</span>}
                          {notification.type === 'exam_assigned' && <span className={!notification.is_read ? 'text-white' : 'text-slate-600'}>📝</span>}
                          {notification.type === 'application_update' && <span className={!notification.is_read ? 'text-white' : 'text-slate-600'}>📋</span>}
                          {!['new_message', 'interview_scheduled', 'exam_assigned', 'application_update'].includes(notification.type) && <span className={!notification.is_read ? 'text-white' : 'text-slate-600'}>🔔</span>}
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <p className={`text-sm font-semibold text-slate-900 line-clamp-1 flex-1 ${!notification.is_read ? 'group-hover:text-blue-600' : ''}`}>
                            {notification.title}
                          </p>
                          {!notification.is_read && (
                            <div className="flex-shrink-0">
                              <div className="w-2 h-2 bg-gradient-to-br from-rose-400 to-pink-500 rounded-full animate-pulse" />
                            </div>
                          )}
                        </div>
                        <p className="text-xs text-slate-600 line-clamp-1 mt-0.5">
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between mt-1">
                          <p className="text-xs text-slate-500 font-medium">
                            {formatTime(notification.created_at)}
                          </p>
                          {!notification.is_read && (
                            <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded-full">New</span>
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
              <div className="flex flex-col items-center justify-center h-full text-center px-4">
                <div className="w-12 h-12 bg-gradient-to-br from-slate-100 to-slate-200 rounded-lg flex items-center justify-center mb-3">
                  <Bell className="h-6 w-6 text-slate-400" />
                </div>
                <p className="text-sm font-semibold text-slate-900 mb-1">All caught up!</p>
                <p className="text-xs text-slate-600">No new notifications</p>
              </div>
            )}
          </div>

          {/* Footer */}
          {((activeTab === 'notifications' && notifications.length > 5) ||
            (activeTab === 'updates' && systemUpdates.length > 0)) && (
            <div className="px-3 py-2 border-t border-slate-100 bg-slate-50/50">
              <button
                onClick={handleViewAll}
                className={`w-full px-3 py-2 ${
                  activeTab === 'updates'
                    ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white'
                    : 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white'
                } text-xs font-semibold rounded-lg hover:opacity-90 transition-opacity`}
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
