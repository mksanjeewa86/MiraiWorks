import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';

// System Health Types
export interface SystemHealth {
  overall_status: 'healthy' | 'warning' | 'critical';
  services: {
    database: ServiceStatus;
    redis: ServiceStatus;
    storage: ServiceStatus;
    email: ServiceStatus;
    antivirus?: ServiceStatus;
    external_apis: Record<string, ServiceStatus>;
  };
  system_metrics: {
    uptime: number;
    memory_usage: number;
    cpu_usage: number;
    disk_usage: number;
    active_connections: number;
  };
  last_check: string;
}

export interface ServiceStatus {
  status: 'healthy' | 'degraded' | 'down';
  response_time?: number;
  last_check: string;
  error_message?: string;
  metadata?: Record<string, any>;
}

export interface PerformanceMetrics {
  response_times: {
    average: number;
    p50: number;
    p95: number;
    p99: number;
  };
  request_rates: {
    current: number;
    average_1h: number;
    average_24h: number;
  };
  error_rates: {
    current: number;
    average_1h: number;
    average_24h: number;
  };
  database_metrics: {
    active_connections: number;
    query_time_avg: number;
    slow_queries_count: number;
  };
}

export interface SystemConfiguration {
  features: {
    two_factor_auth: boolean;
    file_virus_scanning: boolean;
    audit_logging: boolean;
    rate_limiting: boolean;
    email_notifications: boolean;
    real_time_updates: boolean;
  };
  limits: {
    max_file_size: number;
    max_files_per_user: number;
    session_timeout: number;
    max_login_attempts: number;
    password_min_length: number;
  };
  security: {
    require_https: boolean;
    strict_transport_security: boolean;
    content_security_policy: boolean;
    cors_origins: string[];
  };
}

export interface SystemAlert {
  id: number;
  type: 'info' | 'warning' | 'error' | 'critical';
  title: string;
  message: string;
  component: string;
  created_at: string;
  resolved_at?: string;
  resolved_by?: {
    id: number;
    full_name: string;
  };
}

export interface ResourceUsage {
  timestamp: string;
  memory_usage: number;
  cpu_usage: number;
  disk_usage: number;
  network_io: {
    bytes_in: number;
    bytes_out: number;
  };
  active_users: number;
  database_connections: number;
}

export const systemMonitoringApi = {
  // Health Monitoring
  async getSystemHealth(): Promise<ApiResponse<SystemHealth>> {
    const response = await apiClient.get<SystemHealth>('/api/admin/system/health');
    return { data: response.data, success: true };
  },

  async getServiceStatus(serviceName: string): Promise<ApiResponse<ServiceStatus>> {
    const response = await apiClient.get<ServiceStatus>(`/api/admin/system/services/${serviceName}`);
    return { data: response.data, success: true };
  },

  async runHealthCheck(): Promise<ApiResponse<SystemHealth>> {
    const response = await apiClient.post<SystemHealth>('/api/admin/system/health-check');
    return { data: response.data, success: true };
  },

  // Performance Monitoring
  async getPerformanceMetrics(
    timeRange: '1h' | '24h' | '7d' | '30d' = '1h'
  ): Promise<ApiResponse<PerformanceMetrics>> {
    const response = await apiClient.get<PerformanceMetrics>(
      `/api/admin/system/performance?range=${timeRange}`
    );
    return { data: response.data, success: true };
  },

  async getResourceUsage(
    timeRange: '1h' | '24h' | '7d' | '30d' = '1h'
  ): Promise<ApiResponse<ResourceUsage[]>> {
    const response = await apiClient.get<ResourceUsage[]>(
      `/api/admin/system/resources?range=${timeRange}`
    );
    return { data: response.data, success: true };
  },

  // System Configuration
  async getSystemConfiguration(): Promise<ApiResponse<SystemConfiguration>> {
    const response = await apiClient.get<SystemConfiguration>('/api/admin/system/configuration');
    return { data: response.data, success: true };
  },

  async updateSystemConfiguration(
    config: Partial<SystemConfiguration>
  ): Promise<ApiResponse<SystemConfiguration>> {
    const response = await apiClient.put<SystemConfiguration>(
      '/api/admin/system/configuration',
      config
    );
    return { data: response.data, success: true };
  },

  async toggleFeature(
    feature: keyof SystemConfiguration['features'],
    enabled: boolean
  ): Promise<ApiResponse<void>> {
    const response = await apiClient.patch<void>('/api/admin/system/features', {
      feature,
      enabled,
    });
    return { data: response.data, success: true };
  },

  // System Alerts
  async getSystemAlerts(
    page = 1,
    size = 20,
    resolved?: boolean
  ): Promise<ApiResponse<{
    alerts: SystemAlert[];
    total: number;
    page: number;
    size: number;
  }>> {
    const params = new URLSearchParams();
    params.set('page', page.toString());
    params.set('size', size.toString());
    if (resolved !== undefined) params.set('resolved', resolved.toString());

    const response = await apiClient.get<{
      alerts: SystemAlert[];
      total: number;
      page: number;
      size: number;
    }>(`/api/admin/system/alerts?${params.toString()}`);
    return { data: response.data, success: true };
  },

  async resolveAlert(alertId: number): Promise<ApiResponse<SystemAlert>> {
    const response = await apiClient.patch<SystemAlert>(
      `/api/admin/system/alerts/${alertId}/resolve`
    );
    return { data: response.data, success: true };
  },

  async createAlert(alert: {
    type: SystemAlert['type'];
    title: string;
    message: string;
    component: string;
  }): Promise<ApiResponse<SystemAlert>> {
    const response = await apiClient.post<SystemAlert>('/api/admin/system/alerts', alert);
    return { data: response.data, success: true };
  },

  // System Maintenance
  async getCacheStats(): Promise<ApiResponse<{
    redis_info: Record<string, any>;
    cache_hit_rate: number;
    memory_usage: number;
    connected_clients: number;
  }>> {
    const response = await apiClient.get<{
      redis_info: Record<string, any>;
      cache_hit_rate: number;
      memory_usage: number;
      connected_clients: number;
    }>('/api/admin/system/cache/stats');
    return { data: response.data, success: true };
  },

  async clearCache(cacheType?: string): Promise<ApiResponse<{
    cleared_keys: number;
    cache_types: string[];
  }>> {
    const params = cacheType ? `?type=${cacheType}` : '';
    const response = await apiClient.post<{
      cleared_keys: number;
      cache_types: string[];
    }>(`/api/admin/system/cache/clear${params}`);
    return { data: response.data, success: true };
  },

  async getDatabaseStats(): Promise<ApiResponse<{
    connection_count: number;
    active_queries: number;
    database_size: number;
    table_stats: Array<{
      table_name: string;
      row_count: number;
      size_mb: number;
    }>;
  }>> {
    const response = await apiClient.get<{
      connection_count: number;
      active_queries: number;
      database_size: number;
      table_stats: Array<{
        table_name: string;
        row_count: number;
        size_mb: number;
      }>;
    }>('/api/admin/system/database/stats');
    return { data: response.data, success: true };
  },

  // Backup & Maintenance
  async createBackup(): Promise<ApiResponse<{
    backup_id: string;
    status: string;
    started_at: string;
  }>> {
    const response = await apiClient.post<{
      backup_id: string;
      status: string;
      started_at: string;
    }>('/api/admin/system/backup');
    return { data: response.data, success: true };
  },

  async getBackupStatus(backupId: string): Promise<ApiResponse<{
    backup_id: string;
    status: 'running' | 'completed' | 'failed';
    progress: number;
    started_at: string;
    completed_at?: string;
    file_size?: number;
    error_message?: string;
  }>> {
    const response = await apiClient.get<{
      backup_id: string;
      status: 'running' | 'completed' | 'failed';
      progress: number;
      started_at: string;
      completed_at?: string;
      file_size?: number;
      error_message?: string;
    }>(`/api/admin/system/backup/${backupId}`);
    return { data: response.data, success: true };
  },

  async scheduleMaintenance(maintenance: {
    title: string;
    description: string;
    start_time: string;
    duration_minutes: number;
    notify_users: boolean;
  }): Promise<ApiResponse<{
    maintenance_id: string;
    scheduled_for: string;
  }>> {
    const response = await apiClient.post<{
      maintenance_id: string;
      scheduled_for: string;
    }>('/api/admin/system/maintenance/schedule', maintenance);
    return { data: response.data, success: true };
  },
};