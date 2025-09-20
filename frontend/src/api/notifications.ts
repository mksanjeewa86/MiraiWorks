import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type { NotificationsResponse, UnreadCountResponse } from '@/types/notification';

export const notificationsApi = {
  async getNotifications(limit = 50, unreadOnly = false): Promise<NotificationsResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      unread_only: unreadOnly.toString(),
    });

    const url = `${API_ENDPOINTS.NOTIFICATIONS.BASE}?${params.toString()}`;
    const response = await apiClient.get<NotificationsResponse>(url);
    return response.data;
  },

  async getUnreadCount(): Promise<UnreadCountResponse> {
    const response = await apiClient.get<UnreadCountResponse>(API_ENDPOINTS.NOTIFICATIONS.UNREAD_COUNT);
    return response.data;
  },

  async markNotificationsRead(notificationIds: number[]): Promise<{ message: string }> {
    const response = await apiClient.put<{ message: string }>(API_ENDPOINTS.NOTIFICATIONS.MARK_READ, notificationIds);
    return response.data;
  },

  async markAllNotificationsRead(): Promise<{ message: string }> {
    const response = await apiClient.put<{ message: string }>(API_ENDPOINTS.NOTIFICATIONS.MARK_ALL_READ);
    return response.data;
  }
};