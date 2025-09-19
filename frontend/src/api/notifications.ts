import {
  NotificationsResponse,
  UnreadCountResponse
} from '../types/notification';
import { API_ENDPOINTS } from '@/config/api';
import { apiClient } from './apiClient';

export const notificationsApi = {
  async getNotifications(limit = 50, unreadOnly = false): Promise<NotificationsResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      unread_only: unreadOnly.toString(),
    });

    const response = await apiClient.get(`${API_ENDPOINTS.NOTIFICATIONS.BASE}?${params.toString()}`);
    return response.data as NotificationsResponse;
  },

  async getUnreadCount(): Promise<UnreadCountResponse> {
    const response = await apiClient.get(`${API_ENDPOINTS.NOTIFICATIONS.BASE}/unread-count`);
    return response.data as UnreadCountResponse;
  },

  async markNotificationsRead(notificationIds: number[]): Promise<{ message: string }> {
    const response = await apiClient.put(`${API_ENDPOINTS.NOTIFICATIONS.BASE}/mark-read`, notificationIds);
    return response.data as { message: string };
  },

  async markAllNotificationsRead(): Promise<{ message: string }> {
    const response = await apiClient.put(`${API_ENDPOINTS.NOTIFICATIONS.BASE}/mark-all-read`);
    return response.data as { message: string };
  }
};
