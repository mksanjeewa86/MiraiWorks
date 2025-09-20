import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type { Interview, InterviewsListResponse } from '@/types/interview';

export const interviewsApi = {
  async getAll(): Promise<ApiResponse<InterviewsListResponse<Interview>>> {
    const response = await apiClient.get<InterviewsListResponse<Interview>>(API_ENDPOINTS.INTERVIEWS.BASE);
    return { data: response.data, success: true };
  },

  async getById(id: number): Promise<ApiResponse<Interview>> {
    const response = await apiClient.get<Interview>(API_ENDPOINTS.INTERVIEWS.BY_ID(id));
    return { data: response.data, success: true };
  },

  async create(interviewData: Partial<Interview>): Promise<ApiResponse<Interview>> {
    const response = await apiClient.post<Interview>(API_ENDPOINTS.INTERVIEWS.BASE, interviewData);
    return { data: response.data, success: true };
  },

  async update(id: number, interviewData: Partial<Interview>): Promise<ApiResponse<Interview>> {
    const response = await apiClient.put<Interview>(API_ENDPOINTS.INTERVIEWS.BY_ID(id), interviewData);
    return { data: response.data, success: true };
  },

  async delete(id: number): Promise<ApiResponse<void>> {
    await apiClient.delete<void>(API_ENDPOINTS.INTERVIEWS.BY_ID(id));
    return { data: undefined, success: true };
  },

  async updateStatus(id: number, status: string): Promise<ApiResponse<Interview>> {
    const response = await apiClient.put<Interview>(API_ENDPOINTS.INTERVIEWS.STATUS(id), { status });
    return { data: response.data, success: true };
  },

  async schedule(id: number, scheduleData: {
    scheduledAt: string;
    duration: number;
    location?: string;
    meetingLink?: string;
  }): Promise<ApiResponse<Interview>> {
    const response = await apiClient.put<Interview>(API_ENDPOINTS.INTERVIEWS.SCHEDULE(id), scheduleData);
    return { data: response.data, success: true };
  },
};