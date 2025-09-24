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
  async addExperience(
    resumeId: number,
    experience: Partial<WorkExperience>
  ): Promise<ApiResponse<WorkExperience>> {
    const response = await apiClient.post<WorkExperience>(
      API_ENDPOINTS.RESUMES.EXPERIENCES(resumeId),
      experience
    );
    return { data: response.data, success: true };
  },

  async updateExperience(
    experienceId: number,
    experience: Partial<WorkExperience>
  ): Promise<ApiResponse<WorkExperience>> {
    const response = await apiClient.put<WorkExperience>(
      API_ENDPOINTS.RESUMES.EXPERIENCE_BY_ID(experienceId),
      experience
    );
    return { data: response.data, success: true };
  },

  async deleteExperience(experienceId: number): Promise<ApiResponse<void>> {
    await apiClient.delete<void>(API_ENDPOINTS.RESUMES.EXPERIENCE_BY_ID(experienceId));
    return { data: undefined, success: true };
  },

  // Education endpoints
  async addEducation(
    resumeId: number,
    education: Partial<Education>
  ): Promise<ApiResponse<Education>> {
    const response = await apiClient.post<Education>(
      API_ENDPOINTS.RESUMES.EDUCATION(resumeId),
      education
    );
    return { data: response.data, success: true };
  },

  // Skills endpoints
  async addSkill(resumeId: number, skill: Partial<Skill>): Promise<ApiResponse<Skill>> {
    const response = await apiClient.post<Skill>(API_ENDPOINTS.RESUMES.SKILLS(resumeId), skill);
    return { data: response.data, success: true };
  },

  // PDF and Preview endpoints
  async getPreview(id: number): Promise<ApiResponse<string>> {
    const response = await apiClient.get<string>(API_ENDPOINTS.RESUMES.PREVIEW(id));
    return { data: response.data, success: true };
  },

  async generatePdf(
    id: number,
    options?: { format?: string; include_contact_info?: boolean }
  ): Promise<ApiResponse<{ pdf_url: string; file_size: number; expires_at: string }>> {
    const response = await apiClient.post<{
      pdf_url: string;
      file_size: number;
      expires_at: string;
    }>(API_ENDPOINTS.RESUMES.GENERATE_PDF(id), options || {});
    return { data: response.data, success: true };
  },

  // Photo management
  async uploadPhoto(id: number, photoFile: File): Promise<ApiResponse<{ photo_path: string }>> {
    const formData = new FormData();
    formData.append('photo', photoFile);
    const response = await apiClient.post<{ photo_path: string }>(
      API_ENDPOINTS.RESUMES.UPLOAD_PHOTO(id),
      formData
    );
    return { data: response.data, success: true };
  },

  async removePhoto(id: number): Promise<ApiResponse<void>> {
    await apiClient.delete(API_ENDPOINTS.RESUMES.REMOVE_PHOTO(id));
    return { data: undefined, success: true };
  },

  // Public sharing
  async togglePublic(id: number): Promise<ApiResponse<Resume>> {
    const response = await apiClient.post<Resume>(API_ENDPOINTS.RESUMES.TOGGLE_PUBLIC(id));
    return { data: response.data, success: true };
  },

  async getPublicResume(slug: string): Promise<ApiResponse<{ resume: Resume; html: string }>> {
    const response = await publicApiClient.get<{ resume: Resume; html: string }>(
      API_ENDPOINTS.RESUMES.BY_SLUG(slug)
    );
    return { data: response.data, success: true };
  },

  async trackPublicView(slug: string): Promise<ApiResponse<void>> {
    await publicApiClient.post(API_ENDPOINTS.RESUMES.PUBLIC_VIEW(slug));
    return { data: undefined, success: true };
  },

  async downloadPublicPdf(slug: string): Promise<ApiResponse<{ pdf_url: string }>> {
    const response = await publicApiClient.post<{ pdf_url: string }>(
      API_ENDPOINTS.RESUMES.PUBLIC_DOWNLOAD(slug)
    );
    return { data: response.data, success: true };
  },

  // Format conversion
  async convertToRirekisho(id: number): Promise<ApiResponse<Resume>> {
    const response = await apiClient.post<Resume>(API_ENDPOINTS.RESUMES.CONVERT_RIREKISHO(id));
    return { data: response.data, success: true };
  },

  async convertToShokumu(id: number): Promise<ApiResponse<Resume>> {
    const response = await apiClient.post<Resume>(API_ENDPOINTS.RESUMES.CONVERT_SHOKUMU(id));
    return { data: response.data, success: true };
  },

  // Email functionality
  async sendByEmail(
    id: number,
    emailData: {
      recipient_emails: string[];
      subject?: string;
      message?: string;
      include_pdf: boolean;
    }
  ): Promise<ApiResponse<void>> {
    await apiClient.post(API_ENDPOINTS.RESUMES.SEND_EMAIL(id), emailData);
    return { data: undefined, success: true };
  },
};
