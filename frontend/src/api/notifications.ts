import {
  NotificationsResponse,
  UnreadCountResponse
} from '../types/notification';
import { API_CONFIG } from '@/config/api';
import { apiClient } from './apiClient';

export const notificationsApi = {
  async getNotifications(limit = 50, unreadOnly = false): Promise<NotificationsResponse> {
    const url = new URL(`${API_CONFIG.BASE_URL}/api/notifications`);
    url.searchParams.set('limit', limit.toString());
    url.searchParams.set('unread_only', unreadOnly.toString());

    const response = await apiClient.get(url.toString());
    return response.data as NotificationsResponse;
  },

  async getUnreadCount(): Promise<UnreadCountResponse> {
    const response = await apiClient.get(`${API_CONFIG.BASE_URL}/api/notifications/unread-count`);
    return response.data as UnreadCountResponse;
  },

  async markNotificationsRead(notificationIds: number[]): Promise<{ message: string }> {
    const response = await apiClient.put(`${API_CONFIG.BASE_URL}/api/notifications/mark-read`, notificationIds);
    return response.data as { message: string };
  },

  async markAllNotificationsRead(): Promise<{ message: string }> {
    const response = await apiClient.put(`${API_CONFIG.BASE_URL}/api/notifications/mark-all-read`);
    return response.data as { message: string };
  }
};