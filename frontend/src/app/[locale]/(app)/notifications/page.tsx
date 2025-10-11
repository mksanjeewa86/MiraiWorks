'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Bell, CheckCheck, Trash2, Filter, ArrowLeft, Plus, Megaphone } from 'lucide-react';
import { useNotifications } from '@/contexts/NotificationsContext';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { systemUpdatesApi } from '@/api/systemUpdates';
import CreateSystemUpdateModal from '@/components/admin/CreateSystemUpdateModal';
import SystemUpdateCard from '@/components/system-updates/SystemUpdateCard';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import type { AppNotification } from '@/types/notification';
import type { SystemUpdate } from '@/types/system-update';

function NotificationsPageContent() {
  const t = useTranslations('notifications');
  const router = useRouter();
  const { user } = useAuth();
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications();
  const [activeTab, setActiveTab] = useState<'notifications' | 'updates'>('notifications');
  const [notificationFilter, setNotificationFilter] = useState<'all' | 'unread'>('all');
  const [systemUpdates, setSystemUpdates] = useState<SystemUpdate[]>([]);
  const [isLoadingUpdates, setIsLoadingUpdates] = useState(false);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [highlightId, setHighlightId] = useState<string | null>(null);

  // Check if user is system admin
  const isSystemAdmin = user?.roles?.some(
    (userRole) => userRole.role.name === 'system_admin'
  ) ?? false;

  // Handle URL query parameters for highlighting and filtering
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const highlight = params.get('highlight');
      const filterParam = params.get('filter');

      if (highlight) {
        setHighlightId(highlight);
        // Auto-clear highlight after 3 seconds
        setTimeout(() => setHighlightId(null), 3000);
      }

      if (filterParam === 'updates') {
        setActiveTab('updates');
      }
    }
  }, []);

  // Load system updates when Updates tab is selected
  useEffect(() => {
    if (activeTab === 'updates') {
      loadSystemUpdates();
    }
  }, [activeTab]);

  // Auto-hide success message after 5 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  // Scroll to highlighted item
  useEffect(() => {
    if (highlightId && typeof window !== 'undefined') {
      setTimeout(() => {
        const element = document.getElementById(highlightId);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }, 300); // Delay to ensure content is loaded
    }
  }, [highlightId, systemUpdates, notifications]);

  const loadSystemUpdates = async () => {
    setIsLoadingUpdates(true);
    const response = await systemUpdatesApi.getAll({ limit: 100 });
    if (response.success && response.data) {
      setSystemUpdates(response.data);
    }
    setIsLoadingUpdates(false);
  };

  const handleUpdateCreated = () => {
    loadSystemUpdates();
    setSuccessMessage(t('systemUpdates.createSuccess'));
  };

  const filteredNotifications = notificationFilter === 'unread'
    ? notifications.filter(n => !n.is_read)
    : notifications;

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) return t('time.justNow');
    if (minutes < 60) return t('time.minutesAgo', { count: minutes });
    if (hours < 24) return t('time.hoursAgo', { count: hours });
    if (days < 7) return t('time.daysAgo', { count: days });
    return date.toLocaleDateString();
  };

  const handleNotificationClick = async (notification: AppNotification) => {
    if (!notification.is_read) {
      await markAsRead([notification.id]);
    }

    // Handle navigation based on notification payload
    if (
      notification.payload &&
      typeof notification.payload === 'object' &&
      'conversation_url' in notification.payload
    ) {
      window.location.href = (
        notification.payload as { conversation_url: string }
      ).conversation_url;
    }
  };

  const handleMarkAllRead = async () => {
    await markAllAsRead();
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'new_message':
        return '💬';
      case 'interview_scheduled':
        return '📅';
      case 'exam_assigned':
        return '📝';
      case 'application_update':
        return '📋';
      default:
        return '🔔';
    }
  };

  return (
    <AppLayout>
      <div className="max-w-4xl mx-auto">
        <style jsx>{`
          @keyframes pulse-highlight {
            0%, 100% {
              box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7);
              border-color: rgb(96, 165, 250);
            }
            50% {
              box-shadow: 0 0 0 10px rgba(59, 130, 246, 0);
              border-color: rgb(147, 197, 253);
            }
          }
          @keyframes pulse-highlight-purple {
            0%, 100% {
              box-shadow: 0 0 0 0 rgba(168, 85, 247, 0.7);
              border-color: rgb(192, 132, 252);
            }
            50% {
              box-shadow: 0 0 0 10px rgba(168, 85, 247, 0);
              border-color: rgb(216, 180, 254);
            }
          }
          .animate-pulse-highlight {
            animation: pulse-highlight 1.5s ease-in-out 2;
          }
          .animate-pulse-highlight-purple {
            animation: pulse-highlight-purple 1.5s ease-in-out 2;
          }
        `}</style>
        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-400 px-4 py-3 rounded-lg flex items-center justify-between animate-in fade-in slide-in-from-top-2">
            <div className="flex items-center gap-2">
              <CheckCheck className="h-5 w-5" />
              <span className="font-medium">{successMessage}</span>
            </div>
            <button
              onClick={() => setSuccessMessage(null)}
              className="text-green-700 dark:text-green-400 hover:text-green-900 dark:hover:text-green-200"
            >
              ×
            </button>
          </div>
        )}

        {/* Header */}
        <div className="mb-8 mt-6">
          <button
            onClick={() => router.back()}
            className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors mb-4 group"
          >
            <ArrowLeft className="h-5 w-5 group-hover:-translate-x-1 transition-transform" />
            <span className="text-sm font-medium">{t('back')}</span>
          </button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {t('title')}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {t('description')}
          </p>
        </div>

        {/* Tabs and Actions Bar */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 mb-6 overflow-hidden">
          {/* Tab Headers */}
          <div className="border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between px-6 pt-6 pb-4">
              <div className="flex gap-2">
                <button
                  onClick={() => setActiveTab('notifications')}
                  className={`px-6 py-3 rounded-t-lg text-sm font-semibold transition-all ${
                    activeTab === 'notifications'
                      ? 'bg-blue-600 text-white shadow-lg'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  <Bell className="h-4 w-4 inline mr-2" />
                  {t('tabs.notifications')} ({notifications.length})
                </button>
                <button
                  onClick={() => setActiveTab('updates')}
                  className={`px-6 py-3 rounded-t-lg text-sm font-semibold transition-all ${
                    activeTab === 'updates'
                      ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                >
                  <Megaphone className="h-4 w-4 inline mr-2" />
                  {t('tabs.updates')}
                </button>
              </div>
            </div>
          </div>

          {/* Tab Content - Filters and Actions */}
          <div className="p-6">
            {activeTab === 'notifications' ? (
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                {/* Stats */}
                <div className="flex items-center gap-6">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{t('stats.total')}</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {notifications.length}
                    </p>
                  </div>
                  <div className="h-12 w-px bg-gray-200 dark:bg-gray-700"></div>
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{t('stats.unread')}</p>
                    <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                      {unreadCount}
                    </p>
                  </div>
                </div>

                {/* Notification Filters and Actions */}
                <div className="flex items-center gap-3">
                  {/* All/Unread Filter */}
                  <div className="flex gap-2">
                    <button
                      onClick={() => setNotificationFilter('all')}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        notificationFilter === 'all'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      <Filter className="h-4 w-4 inline mr-1" />
                      {t('filters.all')}
                    </button>
                    <button
                      onClick={() => setNotificationFilter('unread')}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        notificationFilter === 'unread'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                      }`}
                    >
                      {t('filters.unread')}
                      {unreadCount > 0 && (
                        <span className="ml-2 bg-blue-600 text-white text-xs font-bold rounded-full px-2 py-0.5">
                          {unreadCount}
                        </span>
                      )}
                    </button>
                  </div>

                  {/* Mark All Read Button */}
                  {unreadCount > 0 && (
                    <button
                      onClick={handleMarkAllRead}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                    >
                      <CheckCheck className="h-4 w-4" />
                      {t('actions.markAllRead')}
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                {/* System Updates Info */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                    {t('systemUpdates.title')}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {t('systemUpdates.description')}
                  </p>
                </div>

                {/* Create Update Button (Super Admin Only) */}
                {isSystemAdmin && (
                  <button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all text-sm font-medium shadow-lg hover:shadow-xl"
                  >
                    <Plus className="h-4 w-4" />
                    {t('actions.createUpdate')}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Notifications/Updates List */}
        <div className="space-y-3">
          {activeTab === 'updates' ? (
            /* System Updates */
            isLoadingUpdates ? (
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-12">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
                  <p className="mt-4 text-gray-600 dark:text-gray-400">
                    {t('systemUpdates.loading')}
                  </p>
                </div>
              </div>
            ) : systemUpdates.length > 0 ? (
              systemUpdates.map((update) => (
                <div
                  key={update.id}
                  id={`update-${update.id}`}
                  className={highlightId === `update-${update.id}` ? 'animate-pulse-highlight-purple' : ''}
                >
                  <SystemUpdateCard update={update} />
                </div>
              ))
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-12">
                <div className="text-center">
                  <Megaphone className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {t('systemUpdates.noUpdates')}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    {t('systemUpdates.noUpdatesDescription')}
                  </p>
                </div>
              </div>
            )
          ) : filteredNotifications.length > 0 ? (
            /* Regular Notifications */
            filteredNotifications.map((notification) => (
              <div
                key={notification.id}
                id={`notification-${notification.id}`}
                onClick={() => handleNotificationClick(notification)}
                className={`bg-white dark:bg-gray-800 rounded-2xl shadow-sm border cursor-pointer hover:shadow-md transition-all duration-200 ${
                  !notification.is_read
                    ? 'border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-700'
                } ${highlightId === `notification-${notification.id}` ? 'animate-pulse-highlight' : ''}`}
              >
                <div className="p-6">
                  <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div
                      className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-2xl ${
                        !notification.is_read
                          ? 'bg-blue-100 dark:bg-blue-900/50'
                          : 'bg-gray-100 dark:bg-gray-700'
                      }`}
                    >
                      {getNotificationIcon(notification.type)}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">
                            {notification.title}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                            {notification.message}
                          </p>
                        </div>

                        {/* Unread indicator */}
                        {!notification.is_read && (
                          <div className="flex-shrink-0">
                            <div className="w-3 h-3 bg-blue-500 rounded-full" />
                          </div>
                        )}
                      </div>

                      {/* Time */}
                      <div className="mt-3 flex items-center justify-between">
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatTime(notification.created_at)}
                        </p>

                        {/* Actions (show on hover) */}
                        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                          {!notification.is_read && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                markAsRead([notification.id]);
                              }}
                              className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
                            >
                              {t('actions.markRead')}
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-12">
              <div className="text-center">
                <Bell className="h-16 w-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {notificationFilter === 'unread' ? t('empty.noUnread') : t('empty.noNotifications')}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {notificationFilter === 'unread'
                    ? t('empty.noUnreadDescription')
                    : t('empty.noNotificationsDescription')}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Create System Update Modal */}
        <CreateSystemUpdateModal
          isOpen={isCreateModalOpen}
          onClose={() => setIsCreateModalOpen(false)}
          onSuccess={handleUpdateCreated}
        />
      </div>
    </AppLayout>
  );
}

export default function NotificationsPage() {
  return (
    <ProtectedRoute>
      <NotificationsPageContent />
    </ProtectedRoute>
  );
}
