import type { 
  ApiResponse, 
  DashboardStats,
} from '@/types';

// Dashboard API
export const dashboardApi = {
  getStats: async (): Promise<ApiResponse<DashboardStats>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch('http://localhost:8001/api/dashboard/stats', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data };
  },
  
  getRecentActivity: async (limit?: number): Promise<ApiResponse<any[]>> => {
    const token = localStorage.getItem('accessToken');
    const url = new URL('http://localhost:8001/api/dashboard/activity');
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
    return { data };
  },
};