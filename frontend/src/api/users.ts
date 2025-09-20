import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type { UserManagement } from '@/types/user';

export interface UserFilters {
  search?: string;
  company_id?: number;
  limit?: number;
  offset?: number;
  is_active?: boolean;
  size?: number;
  include_deleted?: boolean;
}

export const usersApi = {
  async getUsers(filters?: UserFilters): Promise<ApiResponse<{ users: UserManagement[]; total: number; pages: number; page: number; size: number; }>> {
    const params = new URLSearchParams();

    if (filters?.search) params.set('search', filters.search);
    if (filters?.company_id) params.set('company_id', filters.company_id.toString());
    if (filters?.limit) params.set('limit', filters.limit.toString());
    if (filters?.offset) params.set('offset', filters.offset.toString());
    if (filters?.is_active !== undefined) params.set('is_active', filters.is_active.toString());
    if (filters?.size) params.set('size', filters.size.toString());
    if (filters?.include_deleted !== undefined) params.set('include_deleted', filters.include_deleted.toString());

    const url = params.toString() ? `/api/admin/users?${params.toString()}` : '/api/admin/users';
    const response = await apiClient.get<{ users: UserManagement[]; total: number; pages: number; page: number; size: number; }>(url);
    return { data: response.data, success: true };
  },

  async getById(id: number): Promise<ApiResponse<UserManagement>> {
    const response = await apiClient.get<UserManagement>(`/api/admin/users/${id}`);
    return { data: response.data, success: true };
  },

  async create(userData: Partial<UserManagement>): Promise<ApiResponse<UserManagement>> {
    const response = await apiClient.post<UserManagement>('/api/admin/users', userData);
    return { data: response.data, success: true };
  },

  async update(id: number, userData: Partial<UserManagement>): Promise<ApiResponse<UserManagement>> {
    const response = await apiClient.put<UserManagement>(`/api/admin/users/${id}`, userData);
    return { data: response.data, success: true };
  },

  async delete(id: number): Promise<ApiResponse<void>> {
    await apiClient.delete<void>(`/api/admin/users/${id}`);
    return { data: undefined, success: true };
  },

  // Legacy method names for backward compatibility
  async getUser(id: number): Promise<ApiResponse<UserManagement>> {
    return this.getById(id);
  },

  async createUser(userData: Partial<UserManagement>): Promise<ApiResponse<UserManagement>> {
    return this.create(userData);
  },

  async updateUser(id: number, userData: Partial<UserManagement>): Promise<ApiResponse<UserManagement>> {
    return this.update(id, userData);
  },

  async deleteUser(id: number): Promise<ApiResponse<void>> {
    return this.delete(id);
  },

  async suspendUser(id: number): Promise<ApiResponse<UserManagement>> {
    const response = await apiClient.post<UserManagement>(`/api/admin/users/${id}/suspend`);
    return { data: response.data, success: true };
  },

  async unsuspendUser(id: number): Promise<ApiResponse<UserManagement>> {
    const response = await apiClient.post<UserManagement>(`/api/admin/users/${id}/unsuspend`);
    return { data: response.data, success: true };
  },

  async resetPassword(id: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>(`/api/admin/users/${id}/reset-password`);
    return { data: response.data, success: true };
  },

  async resendActivation(id: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>(`/api/admin/users/${id}/resend-activation`);
    return { data: response.data, success: true };
  },

  // Bulk operations
  async bulkDelete(userIds: number[]): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>('/api/admin/users/bulk/delete', { user_ids: userIds });
    return { data: response.data, success: true };
  },

  async bulkResetPassword(userIds: number[]): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>('/api/admin/users/bulk/reset-password', { user_ids: userIds });
    return { data: response.data, success: true };
  },

  async bulkResendActivation(userIds: number[]): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>('/api/admin/users/bulk/resend-activation', { user_ids: userIds });
    return { data: response.data, success: true };
  },

  async bulkSuspend(userIds: number[]): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>('/api/admin/users/bulk/suspend', { user_ids: userIds });
    return { data: response.data, success: true };
  },

  async bulkUnsuspend(userIds: number[]): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>('/api/admin/users/bulk/unsuspend', { user_ids: userIds });
    return { data: response.data, success: true };
  },
};