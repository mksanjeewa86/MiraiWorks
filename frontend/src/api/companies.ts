import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type { ApiResponse, Company, CompanyFilters, CompanyListResponse } from '@/types';

export const companiesApi = {
  async getAll(): Promise<ApiResponse<Company[]>> {
    const response = await apiClient.get<Company[]>(API_ENDPOINTS.COMPANIES.BASE);
    return { data: response.data, success: true };
  },

  async getById(id: number): Promise<ApiResponse<Company>> {
    const response = await apiClient.get<Company>(API_ENDPOINTS.COMPANIES.BY_ID(id.toString()));
    return { data: response.data, success: true };
  },

  // Legacy method names for backward compatibility
  async getCompanies(filters?: CompanyFilters): Promise<ApiResponse<CompanyListResponse>> {
    const params = new URLSearchParams();

    if (filters?.page) params.set('page', filters.page.toString());
    if (filters?.size) params.set('size', filters.size.toString());
    if (filters?.search) params.set('search', filters.search);
    if (filters?.company_type) params.set('company_type', filters.company_type);
    if (filters?.is_active !== undefined) params.set('is_active', filters.is_active.toString());
    if (filters?.is_demo !== undefined) params.set('is_demo', filters.is_demo.toString());
    if (filters?.include_deleted !== undefined)
      params.set('include_deleted', filters.include_deleted.toString());

    const url = params.toString()
      ? `${API_ENDPOINTS.COMPANIES.BASE}?${params.toString()}`
      : API_ENDPOINTS.COMPANIES.BASE;
    const response = await apiClient.get<CompanyListResponse>(url);
    return { data: response.data, success: true };
  },

  async getCompany(id: number): Promise<ApiResponse<Company>> {
    return this.getById(id);
  },

  async createCompany(companyData: Partial<Company>): Promise<ApiResponse<Company>> {
    const response = await apiClient.post<Company>(API_ENDPOINTS.COMPANIES.BASE, companyData);
    return { data: response.data, success: true };
  },

  async updateCompany(id: number, companyData: Partial<Company>): Promise<ApiResponse<Company>> {
    const response = await apiClient.put<Company>(
      API_ENDPOINTS.COMPANIES.BY_ID(id.toString()),
      companyData
    );
    return { data: response.data, success: true };
  },

  async deleteCompany(id: number): Promise<ApiResponse<void>> {
    await apiClient.delete<void>(API_ENDPOINTS.COMPANIES.BY_ID(id.toString()));
    return { data: undefined, success: true };
  },
};
