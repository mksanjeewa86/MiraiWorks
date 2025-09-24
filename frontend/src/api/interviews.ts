import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type { Interview, InterviewsListResponse } from '@/types/interview';

export const interviewsApi = {
  async getAll(params: {
    recruiter_id: number;
    employer_company_id: number;
  }): Promise<ApiResponse<InterviewsListResponse<Interview>>> {
    let url = API_ENDPOINTS.INTERVIEWS.BASE;

    const searchParams = new URLSearchParams();
    searchParams.append('recruiter_id', params.recruiter_id.toString());
    searchParams.append('employer_company_id', params.employer_company_id.toString());
    url += `?${searchParams.toString()}`;

    const response = await apiClient.get<InterviewsListResponse<Interview>>(url);
    return { data: response.data, success: true };
  },

  // Get interviews for current user (works for both candidates and recruiters)
  async getMyInterviews(params?: {
    status?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    offset?: number;
  }): Promise<ApiResponse<InterviewsListResponse<Interview>>> {
    let url = API_ENDPOINTS.INTERVIEWS.BASE;

    if (params) {
      const searchParams = new URLSearchParams();
      if (params.status) searchParams.append('status', params.status);
      if (params.start_date) searchParams.append('start_date', params.start_date);
      if (params.end_date) searchParams.append('end_date', params.end_date);
      if (params.limit) searchParams.append('limit', params.limit.toString());
      if (params.offset) searchParams.append('offset', params.offset.toString());

      if (searchParams.toString()) {
        url += `?${searchParams.toString()}`;
      }
    }

    const response = await apiClient.get<InterviewsListResponse<Interview>>(url);
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
    const response = await apiClient.put<Interview>(
      API_ENDPOINTS.INTERVIEWS.BY_ID(id),
      interviewData
    );
    return { data: response.data, success: true };
  },

  async delete(id: number): Promise<ApiResponse<void>> {
    await apiClient.delete<void>(API_ENDPOINTS.INTERVIEWS.BY_ID(id));
    return { data: undefined, success: true };
  },

  async updateStatus(id: number, status: string): Promise<ApiResponse<Interview>> {
    const response = await apiClient.put<Interview>(API_ENDPOINTS.INTERVIEWS.STATUS(id), {
      status,
    });
    return { data: response.data, success: true };
  },

  async schedule(
    id: number,
    scheduleData: {
      scheduledAt: string;
      duration: number;
      location?: string;
      meetingLink?: string;
    }
  ): Promise<ApiResponse<Interview>> {
    const response = await apiClient.put<Interview>(
      API_ENDPOINTS.INTERVIEWS.SCHEDULE(id),
      scheduleData
    );
    return { data: response.data, success: true };
  },
};
