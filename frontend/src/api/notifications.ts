import {
  AppNotification,
  NotificationsResponse,
  UnreadCountResponse
} from '../types/notification';

const API_BASE_URL = 'http://localhost:8000';

export const notificationsApi = {
  async getNotifications(limit = 50, unreadOnly = false): Promise<NotificationsResponse> {
    const token = localStorage.getItem('accessToken');
    const url = new URL(`${API_BASE_URL}/api/notifications`);
    url.searchParams.set('limit', limit.toString());
    url.searchParams.set('unread_only', unreadOnly.toString());

    const response = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  async getUnreadCount(): Promise<UnreadCountResponse> {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/notifications/unread-count`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  async markNotificationsRead(notificationIds: number[]): Promise<{ message: string }> {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/notifications/mark-read`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(notificationIds),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  async markAllNotificationsRead(): Promise<{ message: string }> {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/notifications/mark-all-read`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
};