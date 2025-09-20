import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type { UserManagement, UserListResponse } from '@/types/user';
import type { CandidateApiFilters } from '@/types/candidate';

export const candidatesApi = {
  async getCandidates(filters?: CandidateApiFilters): Promise<ApiResponse<UserListResponse>> {
    const params = new URLSearchParams();

    // Set default role to candidate
    params.set('role', 'candidate');

    if (filters?.page) params.set('page', filters.page.toString());
    if (filters?.size) params.set('size', filters.size.toString());
    if (filters?.search) params.set('search', filters.search);
    if (filters?.company_id) params.set('company_id', filters.company_id.toString());
    if (filters?.is_active !== undefined) params.set('is_active', filters.is_active.toString());
    if (filters?.include_deleted) params.set('include_deleted', filters.include_deleted.toString());

    const url = `${API_ENDPOINTS.ADMIN.USERS}?${params.toString()}`;
    const response = await apiClient.get<UserListResponse>(url);
    return { data: response.data, success: true };
  },

  async getCandidateById(id: string | number): Promise<ApiResponse<UserManagement>> {
    const response = await apiClient.get<UserManagement>(API_ENDPOINTS.ADMIN.USER_BY_ID(id));
    return { data: response.data, success: true };
  },

  async deleteCandidate(id: string | number): Promise<ApiResponse<void>> {
    await apiClient.delete(API_ENDPOINTS.ADMIN.USER_BY_ID(id));
    return { success: true, data: undefined };
  },

  async updateCandidate(id: string | number, updates: Partial<UserManagement>): Promise<ApiResponse<UserManagement>> {
    const response = await apiClient.put<UserManagement>(API_ENDPOINTS.ADMIN.USER_BY_ID(id), updates);
    return { data: response.data, success: true };
  },
};