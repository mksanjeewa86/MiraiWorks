import { API_ENDPOINTS, API_CONFIG } from './config';
import { apiClient } from './apiClient';
import type { ApiResponse, DashboardStats, ActivityItem } from '@/types';

export const dashboardApi = {
  async getStats(token?: string): Promise<ApiResponse<DashboardStats>> {
    // Handle optional token for special auth cases
    if (token) {
      const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.DASHBOARD.STATS}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { data, success: true };
    }

    const response = await apiClient.get<DashboardStats>(API_ENDPOINTS.DASHBOARD.STATS);
    return { data: response.data, success: true };
  },

  async getRecentActivity(limit?: number, token?: string): Promise<ApiResponse<ActivityItem[]>> {
    // Handle optional token for special auth cases
    if (token) {
      const url = new URL(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.DASHBOARD.ACTIVITY}`);
      if (limit) url.searchParams.set('limit', limit.toString());

      const response = await fetch(url.toString(), {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { data, success: true };
    }

    const url = limit ? `${API_ENDPOINTS.DASHBOARD.ACTIVITY}?limit=${limit}` : API_ENDPOINTS.DASHBOARD.ACTIVITY;
    const response = await apiClient.get<ActivityItem[]>(url);
    return { data: response.data, success: true };
  },
};