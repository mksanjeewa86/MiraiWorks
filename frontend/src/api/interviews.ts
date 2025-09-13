import type { ApiResponse, Interview } from '@/types';
import { API_CONFIG } from '@/config/api';

// Interviews API
export const interviewsApi = {
  getAll: async (): Promise<ApiResponse<Interview[]>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews`, {
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
  },

  getById: async (id: number): Promise<ApiResponse<Interview>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/${id}`, {
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
  },

  create: async (interviewData: Partial<Interview>): Promise<ApiResponse<Interview>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(interviewData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  update: async (id: number, interviewData: Partial<Interview>): Promise<ApiResponse<Interview>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(interviewData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  delete: async (id: number): Promise<ApiResponse<void>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return { data: undefined, success: true };
  },

  updateStatus: async (id: number, status: string): Promise<ApiResponse<Interview>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/${id}/status`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  schedule: async (id: number, scheduleData: {
    scheduledAt: string;
    duration: number;
    location?: string;
    meetingLink?: string;
  }): Promise<ApiResponse<Interview>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/interviews/${id}/schedule`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(scheduleData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },
};