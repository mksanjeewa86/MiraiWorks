import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ApiResponse } from '@/types';
import type {
  FileSecurityInfo,
  SecurityStats,
  VirusScanResult,
  BulkSecurityAction,
  SecurityLog,
} from '@/types/admin';

export const adminSecurityApi = {
  // File Security Management
  async getSecurityStats(): Promise<ApiResponse<SecurityStats>> {
    const response = await apiClient.get<SecurityStats>(
      API_ENDPOINTS.ADMIN_EXTENDED.SECURITY.STATS
    );
    return { data: response.data, success: true };
  },

  async getSecurityFiles(
    page = 1,
    size = 20,
    status?: string,
    search?: string
  ): Promise<
    ApiResponse<{
      files: FileSecurityInfo[];
      total: number;
      page: number;
      size: number;
    }>
  > {
    const params = new URLSearchParams();
    params.set('page', page.toString());
    params.set('size', size.toString());
    if (status) params.set('status', status);
    if (search) params.set('search', search);

    const response = await apiClient.get<{
      files: FileSecurityInfo[];
      total: number;
      page: number;
      size: number;
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.SECURITY.FILES}?${params.toString()}`);
    return { data: response.data, success: true };
  },

  async scanFile(fileId: number): Promise<ApiResponse<VirusScanResult>> {
    const response = await apiClient.post<VirusScanResult>(
      API_ENDPOINTS.ADMIN_EXTENDED.SECURITY.SCAN_FILE(fileId)
    );
    return { data: response.data, success: true };
  },

  async quarantineFile(fileId: number, reason: string): Promise<ApiResponse<void>> {
    const response = await apiClient.post<void>(
      API_ENDPOINTS.ADMIN_EXTENDED.SECURITY.QUARANTINE_FILE(fileId),
      { reason }
    );
    return { data: response.data, success: true };
  },

  async restoreFile(fileId: number): Promise<ApiResponse<void>> {
    const response = await apiClient.post<void>(
      API_ENDPOINTS.ADMIN_EXTENDED.SECURITY.RESTORE_FILE(fileId)
    );
    return { data: response.data, success: true };
  },

  async deleteInfectedFile(fileId: number): Promise<ApiResponse<void>> {
    const response = await apiClient.delete<void>(
      API_ENDPOINTS.ADMIN_EXTENDED.SECURITY.FILE_BY_ID(fileId)
    );
    return { data: response.data, success: true };
  },

  async bulkSecurityAction(action: BulkSecurityAction): Promise<
    ApiResponse<{
      success_count: number;
      error_count: number;
      errors: string[];
    }>
  > {
    const response = await apiClient.post<{
      success_count: number;
      error_count: number;
      errors: string[];
    }>(API_ENDPOINTS.ADMIN_EXTENDED.SECURITY.BULK_ACTION, action);
    return { data: response.data, success: true };
  },

  async getSecurityLogs(
    page = 1,
    size = 20,
    action?: string
  ): Promise<
    ApiResponse<{
      logs: SecurityLog[];
      total: number;
      page: number;
      size: number;
    }>
  > {
    const params = new URLSearchParams();
    params.set('page', page.toString());
    params.set('size', size.toString());
    if (action) params.set('action', action);

    const response = await apiClient.get<{
      logs: SecurityLog[];
      total: number;
      page: number;
      size: number;
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.SECURITY.LOGS}?${params.toString()}`);
    return { data: response.data, success: true };
  },

  // Antivirus Service Management
  async getAntivirusStatus(): Promise<
    ApiResponse<{
      service_available: boolean;
      last_check: string;
      version?: string;
      database_version?: string;
    }>
  > {
    const response = await apiClient.get<{
      service_available: boolean;
      last_check: string;
      version?: string;
      database_version?: string;
    }>(API_ENDPOINTS.ADMIN_EXTENDED.SECURITY.ANTIVIRUS.STATUS);
    return { data: response.data, success: true };
  },

  async runBulkScan(limit = 10): Promise<
    ApiResponse<{
      scanned_count: number;
      results: VirusScanResult[];
    }>
  > {
    const response = await apiClient.post<{
      scanned_count: number;
      results: VirusScanResult[];
    }>(API_ENDPOINTS.ADMIN_EXTENDED.SECURITY.ANTIVIRUS.BULK_SCAN, { limit });
    return { data: response.data, success: true };
  },
};
