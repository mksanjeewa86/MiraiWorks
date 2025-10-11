/**
 * System Updates API Client
 */

import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ApiResponse } from '@/types';
import type {
  SystemUpdate,
  SystemUpdateWithCreator,
  SystemUpdateCreateData,
  SystemUpdateUpdateData,
  SystemUpdateFilters,
} from '@/types/system-update';

export const systemUpdatesApi = {
  /**
   * Get all system updates
   */
  async getAll(filters?: SystemUpdateFilters): Promise<ApiResponse<SystemUpdate[]>> {
    try {
      const params = new URLSearchParams();
      if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
      if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());
      if (filters?.tags && filters.tags.length > 0) {
        filters.tags.forEach(tag => params.append('tags', tag));
      }

      const url = params.toString()
        ? `${API_ENDPOINTS.SYSTEM_UPDATES.BASE}?${params.toString()}`
        : API_ENDPOINTS.SYSTEM_UPDATES.BASE;

      const response = await apiClient.get<SystemUpdate[]>(url);
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to fetch system updates',
      };
    }
  },

  /**
   * Get a specific system update by ID with creator information
   */
  async getById(id: number): Promise<ApiResponse<SystemUpdateWithCreator>> {
    try {
      const response = await apiClient.get<SystemUpdateWithCreator>(
        API_ENDPOINTS.SYSTEM_UPDATES.BY_ID(id)
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to fetch system update',
      };
    }
  },

  /**
   * Create a new system update (super admin only)
   */
  async create(data: SystemUpdateCreateData): Promise<ApiResponse<SystemUpdate>> {
    try {
      const response = await apiClient.post<SystemUpdate>(
        API_ENDPOINTS.SYSTEM_UPDATES.BASE,
        data
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to create system update',
      };
    }
  },

  /**
   * Update an existing system update (super admin only)
   */
  async update(
    id: number,
    data: SystemUpdateUpdateData
  ): Promise<ApiResponse<SystemUpdate>> {
    try {
      const response = await apiClient.put<SystemUpdate>(
        API_ENDPOINTS.SYSTEM_UPDATES.BY_ID(id),
        data
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to update system update',
      };
    }
  },

  /**
   * Deactivate a system update (soft delete, super admin only)
   */
  async deactivate(id: number): Promise<ApiResponse<void>> {
    try {
      await apiClient.delete(API_ENDPOINTS.SYSTEM_UPDATES.BY_ID(id));
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to deactivate system update',
      };
    }
  },

  /**
   * Activate a previously deactivated system update (super admin only)
   */
  async activate(id: number): Promise<ApiResponse<SystemUpdate>> {
    try {
      const response = await apiClient.post<SystemUpdate>(
        API_ENDPOINTS.SYSTEM_UPDATES.ACTIVATE(id)
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to activate system update',
      };
    }
  },
};
