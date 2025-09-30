import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';

// File Security Management Types
export interface FileSecurityInfo {
  id: number;
  filename: string;
  file_path: string;
  file_size: number;
  uploaded_by: {
    id: number;
    full_name: string;
    email: string;
  };
  virus_status: 'pending' | 'clean' | 'infected' | 'error';
  virus_scan_result?: string;
  scanned_at?: string;
  is_quarantined: boolean;
  uploaded_at: string;
}

export interface SecurityStats {
  total_files: number;
  clean_files: number;
  infected_files: number;
  pending_scans: number;
  error_scans: number;
  quarantined_files: number;
  scan_success_rate: number;
}

export interface VirusScanResult {
  file_id: number;
  status: 'clean' | 'infected' | 'error';
  result_message: string;
  scanned_at: string;
}

export interface BulkSecurityAction {
  file_ids: number[];
  action: 'scan' | 'quarantine' | 'delete' | 'restore';
  reason?: string;
}

export interface SecurityLog {
  id: number;
  action: string;
  file_id: number;
  filename: string;
  performed_by: {
    id: number;
    full_name: string;
    email: string;
  };
  details: string;
  timestamp: string;
}

export const adminSecurityApi = {
  // File Security Management
  async getSecurityStats(): Promise<ApiResponse<SecurityStats>> {
    const response = await apiClient.get<SecurityStats>('/api/admin/security/stats');
    return { data: response.data, success: true };
  },

  async getSecurityFiles(
    page = 1,
    size = 20,
    status?: string,
    search?: string
  ): Promise<ApiResponse<{
    files: FileSecurityInfo[];
    total: number;
    page: number;
    size: number;
  }>> {
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
    }>(`/api/admin/security/files?${params.toString()}`);
    return { data: response.data, success: true };
  },

  async scanFile(fileId: number): Promise<ApiResponse<VirusScanResult>> {
    const response = await apiClient.post<VirusScanResult>(
      `/api/admin/security/files/${fileId}/scan`
    );
    return { data: response.data, success: true };
  },

  async quarantineFile(fileId: number, reason: string): Promise<ApiResponse<void>> {
    const response = await apiClient.post<void>(
      `/api/admin/security/files/${fileId}/quarantine`,
      { reason }
    );
    return { data: response.data, success: true };
  },

  async restoreFile(fileId: number): Promise<ApiResponse<void>> {
    const response = await apiClient.post<void>(
      `/api/admin/security/files/${fileId}/restore`
    );
    return { data: response.data, success: true };
  },

  async deleteInfectedFile(fileId: number): Promise<ApiResponse<void>> {
    const response = await apiClient.delete<void>(
      `/api/admin/security/files/${fileId}`
    );
    return { data: response.data, success: true };
  },

  async bulkSecurityAction(action: BulkSecurityAction): Promise<ApiResponse<{
    success_count: number;
    error_count: number;
    errors: string[];
  }>> {
    const response = await apiClient.post<{
      success_count: number;
      error_count: number;
      errors: string[];
    }>('/api/admin/security/bulk-action', action);
    return { data: response.data, success: true };
  },

  async getSecurityLogs(
    page = 1,
    size = 20,
    action?: string
  ): Promise<ApiResponse<{
    logs: SecurityLog[];
    total: number;
    page: number;
    size: number;
  }>> {
    const params = new URLSearchParams();
    params.set('page', page.toString());
    params.set('size', size.toString());
    if (action) params.set('action', action);

    const response = await apiClient.get<{
      logs: SecurityLog[];
      total: number;
      page: number;
      size: number;
    }>(`/api/admin/security/logs?${params.toString()}`);
    return { data: response.data, success: true };
  },

  // Antivirus Service Management
  async getAntivirusStatus(): Promise<ApiResponse<{
    service_available: boolean;
    last_check: string;
    version?: string;
    database_version?: string;
  }>> {
    const response = await apiClient.get<{
      service_available: boolean;
      last_check: string;
      version?: string;
      database_version?: string;
    }>('/api/admin/security/antivirus/status');
    return { data: response.data, success: true };
  },

  async runBulkScan(limit = 10): Promise<ApiResponse<{
    scanned_count: number;
    results: VirusScanResult[];
  }>> {
    const response = await apiClient.post<{
      scanned_count: number;
      results: VirusScanResult[];
    }>('/api/admin/security/antivirus/bulk-scan', { limit });
    return { data: response.data, success: true };
  },
};