import type { 
  ApiResponse, 
  DashboardStats,
  ActivityItem,
} from '@/types';

const API_BASE_URL = 'http://localhost:8000';

// Dashboard API
export const dashboardApi = {
  getStats: async (token?: string): Promise<ApiResponse<DashboardStats>> => {
    const authToken = token || localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },
  
  getRecentActivity: async (limit?: number, token?: string): Promise<ApiResponse<ActivityItem[]>> => {
    const authToken = token || localStorage.getItem('accessToken');
    const url = new URL(`${API_BASE_URL}/api/dashboard/activity`);
    if (limit) url.searchParams.set('limit', limit.toString());
    
    const response = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },
};