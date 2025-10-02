import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ApiResponse } from '@/types';
import type {
  AuditLogEntry,
  AuditLogFilters,
  AuditLogStats,
  SystemActivity,
} from '@/types/admin';

export const auditLogsApi = {
  // Core Audit Log Functions
  async getAuditLogs(
    page = 1,
    size = 20,
    filters?: AuditLogFilters
  ): Promise<ApiResponse<{
    logs: AuditLogEntry[];
    total: number;
    page: number;
    size: number;
  }>> {
    const params = new URLSearchParams();
    params.set('page', page.toString());
    params.set('size', size.toString());

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.set(key, value.toString());
        }
      });
    }

    const response = await apiClient.get<{
      logs: AuditLogEntry[];
      total: number;
      page: number;
      size: number;
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.BASE}?${params.toString()}`);
    return { data: response.data, success: true };
  },

  async getAuditLogById(logId: number): Promise<ApiResponse<AuditLogEntry>> {
    const response = await apiClient.get<AuditLogEntry>(`${API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.BASE}/${logId}`);
    return { data: response.data, success: true };
  },

  async getAuditLogStats(
    startDate?: string,
    endDate?: string
  ): Promise<ApiResponse<AuditLogStats>> {
    const params = new URLSearchParams();
    if (startDate) params.set('start_date', startDate);
    if (endDate) params.set('end_date', endDate);

    const query = params.toString();
    const url = query ? `${API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.STATS}?${query}` : API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.STATS;

    const response = await apiClient.get<AuditLogStats>(url);
    return { data: response.data, success: true };
  },

  async getSystemActivity(
    startDate?: string,
    endDate?: string
  ): Promise<ApiResponse<SystemActivity>> {
    const params = new URLSearchParams();
    if (startDate) params.set('start_date', startDate);
    if (endDate) params.set('end_date', endDate);

    const query = params.toString();
    const url = query ? `${API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.ACTIVITY}?${query}` : API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.ACTIVITY;

    const response = await apiClient.get<SystemActivity>(url);
    return { data: response.data, success: true };
  },

  // Entity-specific audit logs
  async getEntityAuditHistory(
    entityType: string,
    entityId: number,
    page = 1,
    size = 20
  ): Promise<ApiResponse<{
    logs: AuditLogEntry[];
    total: number;
    page: number;
    size: number;
  }>> {
    const params = new URLSearchParams();
    params.set('page', page.toString());
    params.set('size', size.toString());

    const response = await apiClient.get<{
      logs: AuditLogEntry[];
      total: number;
      page: number;
      size: number;
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.BASE}/entity/${entityType}/${entityId}?${params.toString()}`);
    return { data: response.data, success: true };
  },

  // User activity tracking
  async getUserActivity(
    userId: number,
    page = 1,
    size = 20,
    startDate?: string,
    endDate?: string
  ): Promise<ApiResponse<{
    logs: AuditLogEntry[];
    total: number;
    page: number;
    size: number;
  }>> {
    const params = new URLSearchParams();
    params.set('page', page.toString());
    params.set('size', size.toString());
    if (startDate) params.set('start_date', startDate);
    if (endDate) params.set('end_date', endDate);

    const response = await apiClient.get<{
      logs: AuditLogEntry[];
      total: number;
      page: number;
      size: number;
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.BASE}/user/${userId}?${params.toString()}`);
    return { data: response.data, success: true };
  },

  // Security-focused queries
  async getSecurityEvents(
    page = 1,
    size = 20,
    severity?: 'low' | 'medium' | 'high' | 'critical'
  ): Promise<ApiResponse<{
    events: AuditLogEntry[];
    total: number;
    page: number;
    size: number;
  }>> {
    const params = new URLSearchParams();
    params.set('page', page.toString());
    params.set('size', size.toString());
    if (severity) params.set('severity', severity);

    const response = await apiClient.get<{
      events: AuditLogEntry[];
      total: number;
      page: number;
      size: number;
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.BASE}/security?${params.toString()}`);
    return { data: response.data, success: true };
  },

  async getFailedLoginAttempts(
    page = 1,
    size = 20,
    hours = 24
  ): Promise<ApiResponse<{
    attempts: AuditLogEntry[];
    total: number;
    page: number;
    size: number;
  }>> {
    const params = new URLSearchParams();
    params.set('page', page.toString());
    params.set('size', size.toString());
    params.set('hours', hours.toString());

    const response = await apiClient.get<{
      attempts: AuditLogEntry[];
      total: number;
      page: number;
      size: number;
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.BASE}/failed-logins?${params.toString()}`);
    return { data: response.data, success: true };
  },

  // Export functionality
  async exportAuditLogs(
    filters?: AuditLogFilters,
    format: 'csv' | 'json' = 'csv'
  ): Promise<ApiResponse<{
    download_url: string;
    expires_at: string;
  }>> {
    const params = new URLSearchParams();
    params.set('format', format);

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.set(key, value.toString());
        }
      });
    }

    const response = await apiClient.post<{
      download_url: string;
      expires_at: string;
    }>(API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.EXPORT, params);
    return { data: response.data, success: true };
  },

  // Available filter options
  async getFilterOptions(): Promise<ApiResponse<{
    actions: string[];
    entity_types: string[];
  }>> {
    const response = await apiClient.get<{
      actions: string[];
      entity_types: string[];
    }>(API_ENDPOINTS.ADMIN_EXTENDED.AUDIT_LOGS.FILTER_OPTIONS);
    return { data: response.data, success: true };
  },
};
