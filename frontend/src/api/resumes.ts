import type { ApiResponse, Resume, WorkExperience, Education, Skill } from '@/types';

const API_BASE_URL = 'http://localhost:8000';

// Resumes API
export const resumesApi = {
  getAll: async (): Promise<ApiResponse<Resume[]>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/resumes`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const responseData = await response.json();
    return { data: responseData.resumes, success: true };
  },

  getById: async (id: number): Promise<ApiResponse<Resume>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/resumes/${id}`, {
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

  getBySlug: async (slug: string): Promise<ApiResponse<Resume>> => {
    const response = await fetch(`${API_BASE_URL}/api/public/resumes/${slug}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  create: async (resumeData: Partial<Resume>): Promise<ApiResponse<Resume>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/resumes`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(resumeData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  update: async (id: number, resumeData: Partial<Resume>): Promise<ApiResponse<Resume>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/resumes/${id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(resumeData),
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
    const response = await fetch(`${API_BASE_URL}/api/resumes/${id}`, {
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

  // Work Experience endpoints
  addExperience: async (resumeId: number, experience: Partial<WorkExperience>): Promise<ApiResponse<WorkExperience>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/resumes/${resumeId}/experiences`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(experience),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  updateExperience: async (experienceId: number, experience: Partial<WorkExperience>): Promise<ApiResponse<WorkExperience>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/experiences/${experienceId}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(experience),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  deleteExperience: async (experienceId: number): Promise<ApiResponse<void>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/experiences/${experienceId}`, {
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

  // Education endpoints
  addEducation: async (resumeId: number, education: Partial<Education>): Promise<ApiResponse<Education>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/resumes/${resumeId}/education`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(education),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  // Skills endpoints
  addSkill: async (resumeId: number, skill: Partial<Skill>): Promise<ApiResponse<Skill>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/resumes/${resumeId}/skills`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(skill),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },
};