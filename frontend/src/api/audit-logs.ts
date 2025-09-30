import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';

// Audit Log Types
export interface AuditLogEntry {
  id: number;
  actor_id?: number;
  action: string;
  entity_type: string;
  entity_id?: number;
  entity_data?: Record<string, any>;
  changes?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  timestamp: string;
  actor?: {
    id: number;
    full_name: string;
    email: string;
  };
}

export interface AuditLogFilters {
  actor_id?: number;
  action?: string;
  entity_type?: string;
  entity_id?: number;
  start_date?: string;
  end_date?: string;
  ip_address?: string;
  search?: string;
}

export interface AuditLogStats {
  total_entries: number;
  unique_actors: number;
  actions_today: number;
  top_actions: Array<{
    action: string;
    count: number;
  }>;
  top_entity_types: Array<{
    entity_type: string;
    count: number;
  }>;
  recent_activity_trend: Array<{
    date: string;
    count: number;
  }>;
}

export interface SystemActivity {
  login_attempts: {
    successful: number;
    failed: number;
    unique_users: number;
  };
  data_changes: {
    creates: number;
    updates: number;
    deletes: number;
  };
  security_events: {
    suspicious_activities: number;
    blocked_attempts: number;
    admin_actions: number;
  };
}

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
    }>(`/api/admin/audit-logs?${params.toString()}`);
    return { data: response.data, success: true };
  },

  async getAuditLogById(logId: number): Promise<ApiResponse<AuditLogEntry>> {
    const response = await apiClient.get<AuditLogEntry>(`/api/admin/audit-logs/${logId}`);
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
    const url = query ? `/api/admin/audit-logs/stats?${query}` : '/api/admin/audit-logs/stats';

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
    const url = query ? `/api/admin/audit-logs/activity?${query}` : '/api/admin/audit-logs/activity';

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
    }>(`/api/admin/audit-logs/entity/${entityType}/${entityId}?${params.toString()}`);
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
    }>(`/api/admin/audit-logs/user/${userId}?${params.toString()}`);
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
    }>(`/api/admin/audit-logs/security?${params.toString()}`);
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
    }>(`/api/admin/audit-logs/failed-logins?${params.toString()}`);
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
    }>('/api/admin/audit-logs/export', params);
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
    }>('/api/admin/audit-logs/filter-options');
    return { data: response.data, success: true };
  },
};