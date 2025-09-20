import { API_ENDPOINTS } from './config';
import { apiClient, publicApiClient } from './apiClient';
import type { ApiResponse, Resume, WorkExperience, Education, Skill } from '@/types';

export const resumesApi = {
  async getAll(): Promise<ApiResponse<Resume[]>> {
    const response = await apiClient.get<{ resumes: Resume[] }>(API_ENDPOINTS.RESUMES.BASE);
    return { data: response.data.resumes, success: true };
  },

  async getById(id: number): Promise<ApiResponse<Resume>> {
    const response = await apiClient.get<Resume>(API_ENDPOINTS.RESUMES.BY_ID(id));
    return { data: response.data, success: true };
  },

  async getBySlug(slug: string): Promise<ApiResponse<Resume>> {
    const response = await publicApiClient.get<Resume>(API_ENDPOINTS.RESUMES.BY_SLUG(slug));
    return { data: response.data, success: true };
  },

  async create(resumeData: Partial<Resume>): Promise<ApiResponse<Resume>> {
    const response = await apiClient.post<Resume>(API_ENDPOINTS.RESUMES.BASE, resumeData);
    return { data: response.data, success: true };
  },

  async update(id: number, resumeData: Partial<Resume>): Promise<ApiResponse<Resume>> {
    const response = await apiClient.put<Resume>(API_ENDPOINTS.RESUMES.BY_ID(id), resumeData);
    return { data: response.data, success: true };
  },

  async delete(id: number): Promise<ApiResponse<void>> {
    await apiClient.delete<void>(API_ENDPOINTS.RESUMES.BY_ID(id));
    return { data: undefined, success: true };
  },

  // Work Experience endpoints
  async addExperience(resumeId: number, experience: Partial<WorkExperience>): Promise<ApiResponse<WorkExperience>> {
    const response = await apiClient.post<WorkExperience>(API_ENDPOINTS.RESUMES.EXPERIENCES(resumeId), experience);
    return { data: response.data, success: true };
  },

  async updateExperience(experienceId: number, experience: Partial<WorkExperience>): Promise<ApiResponse<WorkExperience>> {
    const response = await apiClient.put<WorkExperience>(API_ENDPOINTS.RESUMES.EXPERIENCE_BY_ID(experienceId), experience);
    return { data: response.data, success: true };
  },

  async deleteExperience(experienceId: number): Promise<ApiResponse<void>> {
    await apiClient.delete<void>(API_ENDPOINTS.RESUMES.EXPERIENCE_BY_ID(experienceId));
    return { data: undefined, success: true };
  },

  // Education endpoints
  async addEducation(resumeId: number, education: Partial<Education>): Promise<ApiResponse<Education>> {
    const response = await apiClient.post<Education>(API_ENDPOINTS.RESUMES.EDUCATION(resumeId), education);
    return { data: response.data, success: true };
  },

  // Skills endpoints
  async addSkill(resumeId: number, skill: Partial<Skill>): Promise<ApiResponse<Skill>> {
    const response = await apiClient.post<Skill>(API_ENDPOINTS.RESUMES.SKILLS(resumeId), skill);
    return { data: response.data, success: true };
  },
};