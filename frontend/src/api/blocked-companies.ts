/**
 * Blocked Companies API Client
 *
 * API functions for managing blocked companies list
 */

import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type {
  BlockedCompany,
  BlockedCompanyCreate,
  CompanySearchResult,
} from '@/types/blocked-company';
import type { ApiResponse } from '@/types';

/**
 * Get all blocked companies for the current user
 */
export async function getBlockedCompanies(): Promise<ApiResponse<BlockedCompany[]>> {
  try {
    const response = await apiClient.get<BlockedCompany[]>(API_ENDPOINTS.BLOCKED_COMPANIES.BASE);
    return {
      success: true,
      data: response.data,
    };
  } catch (error: any) {
    return {
      success: false,
      errors: [error.response?.data?.detail || 'Failed to fetch blocked companies'],
    };
  }
}

/**
 * Block a company
 */
export async function blockCompany(
  companyData: BlockedCompanyCreate
): Promise<ApiResponse<BlockedCompany>> {
  try {
    const response = await apiClient.post<BlockedCompany>(
      API_ENDPOINTS.BLOCKED_COMPANIES.BASE,
      companyData
    );
    return {
      success: true,
      data: response.data,
    };
  } catch (error: any) {
    return {
      success: false,
      errors: [error.response?.data?.detail || 'Failed to block company'],
    };
  }
}

/**
 * Unblock a company
 */
export async function unblockCompany(blockedCompanyId: number): Promise<ApiResponse<void>> {
  try {
    await apiClient.delete(API_ENDPOINTS.BLOCKED_COMPANIES.BY_ID(blockedCompanyId));
    return {
      success: true,
    };
  } catch (error: any) {
    return {
      success: false,
      errors: [error.response?.data?.detail || 'Failed to unblock company'],
    };
  }
}

/**
 * Search for companies by name (for autocomplete)
 */
export async function searchCompanies(
  query: string,
  limit: number = 10
): Promise<ApiResponse<CompanySearchResult[]>> {
  try {
    const url = `${API_ENDPOINTS.BLOCKED_COMPANIES.SEARCH}?q=${encodeURIComponent(query)}&limit=${limit}`;
    const response = await apiClient.get<CompanySearchResult[]>(url);
    return {
      success: true,
      data: response.data,
    };
  } catch (error: any) {
    return {
      success: false,
      errors: [error.response?.data?.detail || 'Failed to search companies'],
    };
  }
}
