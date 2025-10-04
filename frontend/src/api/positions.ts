import { API_ENDPOINTS } from './config';
import { apiClient, publicApiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type { Position, PositionCreate, PositionUpdate, PositionFilters } from '@/types/position';

// Helper to build query strings
const buildQueryString = (filters?: PositionFilters): string => {
  if (!filters) return '';

  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== '') {
      params.set(key, value.toString());
    }
  });

  return params.toString();
};

export const positionsApi = {
  // Public endpoints (no authentication required)
  async getPublic(
    filters?: PositionFilters
  ): Promise<ApiResponse<{ positions: Position[]; total: number; has_more?: boolean }>> {
    const publicFilters = { ...filters, status: 'published' };
    const query = buildQueryString(publicFilters);
    const url = query ? `${API_ENDPOINTS.POSITIONS.BASE}?${query}` : API_ENDPOINTS.POSITIONS.BASE;

    const response = await publicApiClient.get<{
      positions: Position[];
      total: number;
      has_more?: boolean;
    }>(url);
    return { data: response.data, success: true };
  },

  async getById(id: number, isAuthenticated = false): Promise<ApiResponse<Position>> {
    const client = isAuthenticated ? apiClient : publicApiClient;
    const response = await client.get<Position>(API_ENDPOINTS.POSITIONS.BY_ID(id));
    return { data: response.data, success: true };
  },

  async getBySlug(slug: string): Promise<ApiResponse<Position>> {
    const response = await publicApiClient.get<Position>(API_ENDPOINTS.POSITIONS.BY_SLUG(slug));
    return { data: response.data, success: true };
  },

  async getPopular(limit = 10): Promise<ApiResponse<Position[]>> {
    const query = `limit=${limit}`;
    const url = `${API_ENDPOINTS.POSITIONS.POPULAR}?${query}`;
    const response = await publicApiClient.get<Position[]>(url);
    return { data: response.data, success: true };
  },

  async getRecent(days = 7, limit = 100): Promise<ApiResponse<Position[]>> {
    const query = `days=${days}&limit=${limit}`;
    const url = `${API_ENDPOINTS.POSITIONS.RECENT}?${query}`;
    const response = await publicApiClient.get<Position[]>(url);
    return { data: response.data, success: true };
  },

  // Admin endpoints (authentication required)
  async getAll(
    filters?: PositionFilters
  ): Promise<ApiResponse<{ positions: Position[]; total: number; has_more?: boolean }>> {
    const query = buildQueryString(filters);
    const url = query ? `${API_ENDPOINTS.POSITIONS.BASE}?${query}` : API_ENDPOINTS.POSITIONS.BASE;

    const response = await apiClient.get<{
      positions: Position[];
      total: number;
      has_more?: boolean;
    }>(url);
    return { data: response.data, success: true };
  },

  async create(payload: PositionCreate): Promise<ApiResponse<Position>> {
    const response = await apiClient.post<Position>(API_ENDPOINTS.POSITIONS.BASE, payload);
    return { data: response.data, success: true };
  },

  async update(id: number, payload: PositionUpdate): Promise<ApiResponse<Position>> {
    const response = await apiClient.put<Position>(API_ENDPOINTS.POSITIONS.BY_ID(id), payload);
    return { data: response.data, success: true };
  },

  async updateStatus(id: number, status: string): Promise<ApiResponse<Position>> {
    const response = await apiClient.patch<Position>(API_ENDPOINTS.POSITIONS.STATUS(id), {
      status,
    });
    return { data: response.data, success: true };
  },

  async bulkUpdateStatus(positionIds: number[], status: string): Promise<ApiResponse<Position[]>> {
    const payload = { position_ids: positionIds, status };
    const response = await apiClient.patch<Position[]>(
      API_ENDPOINTS.POSITIONS.BULK_STATUS,
      payload
    );
    return { data: response.data, success: true };
  },

  async delete(id: number): Promise<ApiResponse<void>> {
    await apiClient.delete<void>(API_ENDPOINTS.POSITIONS.BY_ID(id));
    return { data: undefined, success: true };
  },

  async getCompanyPositions(
    companyId: number,
    skip = 0,
    limit = 100
  ): Promise<ApiResponse<Position[]>> {
    const query = `skip=${skip}&limit=${limit}`;
    const url = `${API_ENDPOINTS.POSITIONS.COMPANY(companyId)}?${query}`;
    const response = await apiClient.get<Position[]>(url);
    return { data: response.data, success: true };
  },

  async getExpiring(days = 7, limit = 100): Promise<ApiResponse<Position[]>> {
    const query = `days=${days}&limit=${limit}`;
    const url = `${API_ENDPOINTS.POSITIONS.EXPIRING}?${query}`;
    const response = await apiClient.get<Position[]>(url);
    return { data: response.data, success: true };
  },

  async getStatistics(): Promise<ApiResponse<Record<string, unknown>>> {
    const response = await apiClient.get<Record<string, unknown>>(
      API_ENDPOINTS.POSITIONS.STATISTICS
    );
    return { data: response.data, success: true };
  },
};
