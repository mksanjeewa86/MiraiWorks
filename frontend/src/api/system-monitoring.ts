import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';
import type {
  SystemHealth,
  ServiceStatus,
  PerformanceMetrics,
  SystemConfiguration,
  SystemAlert,
  ResourceUsage,
} from '@/types/admin';

export const systemMonitoringApi = {
  // Health Monitoring
  async getSystemHealth(): Promise<ApiResponse<SystemHealth>> {
    const response = await apiClient.get<SystemHealth>(API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.HEALTH);
    return { data: response.data, success: true };
  },

  async getServiceStatus(serviceName: string): Promise<ApiResponse<ServiceStatus>> {
    const response = await apiClient.get<ServiceStatus>(
      API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.SERVICES(serviceName)
    );
    return { data: response.data, success: true };
  },

  async runHealthCheck(): Promise<ApiResponse<SystemHealth>> {
    const response = await apiClient.post<SystemHealth>(
      API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.HEALTH_CHECK
    );
    return { data: response.data, success: true };
  },

  // Performance Monitoring
  async getPerformanceMetrics(
    timeRange: '1h' | '24h' | '7d' | '30d' = '1h'
  ): Promise<ApiResponse<PerformanceMetrics>> {
    const response = await apiClient.get<PerformanceMetrics>(
      `${API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.PERFORMANCE}?range=${timeRange}`
    );
    return { data: response.data, success: true };
  },

  async getResourceUsage(
    timeRange: '1h' | '24h' | '7d' | '30d' = '1h'
  ): Promise<ApiResponse<ResourceUsage[]>> {
    const response = await apiClient.get<ResourceUsage[]>(
      `${API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.RESOURCES}?range=${timeRange}`
    );
    return { data: response.data, success: true };
  },

  // System Configuration
  async getSystemConfiguration(): Promise<ApiResponse<SystemConfiguration>> {
    const response = await apiClient.get<SystemConfiguration>(
      API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.CONFIGURATION
    );
    return { data: response.data, success: true };
  },

  async updateSystemConfiguration(
    config: Partial<SystemConfiguration>
  ): Promise<ApiResponse<SystemConfiguration>> {
    const response = await apiClient.put<SystemConfiguration>(
      API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.CONFIGURATION,
      config
    );
    return { data: response.data, success: true };
  },

  async toggleFeature(
    feature: keyof SystemConfiguration['features'],
    enabled: boolean
  ): Promise<ApiResponse<void>> {
    const response = await apiClient.patch<void>(API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.FEATURES, {
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
  ): Promise<
    ApiResponse<{
      alerts: SystemAlert[];
      total: number;
      page: number;
      size: number;
    }>
  > {
    const params = new URLSearchParams();
    params.set('page', page.toString());
    params.set('size', size.toString());
    if (resolved !== undefined) params.set('resolved', resolved.toString());

    const response = await apiClient.get<{
      alerts: SystemAlert[];
      total: number;
      page: number;
      size: number;
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.ALERTS}?${params.toString()}`);
    return { data: response.data, success: true };
  },

  async resolveAlert(alertId: number): Promise<ApiResponse<SystemAlert>> {
    const response = await apiClient.patch<SystemAlert>(
      `${API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.ALERTS}/${alertId}/resolve`
    );
    return { data: response.data, success: true };
  },

  async createAlert(alert: {
    type: SystemAlert['type'];
    title: string;
    message: string;
    component: string;
  }): Promise<ApiResponse<SystemAlert>> {
    const response = await apiClient.post<SystemAlert>(
      API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.ALERTS,
      alert
    );
    return { data: response.data, success: true };
  },

  // System Maintenance
  async getCacheStats(): Promise<
    ApiResponse<{
      redis_info: Record<string, any>;
      cache_hit_rate: number;
      memory_usage: number;
      connected_clients: number;
    }>
  > {
    const response = await apiClient.get<{
      redis_info: Record<string, any>;
      cache_hit_rate: number;
      memory_usage: number;
      connected_clients: number;
    }>(API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.CACHE.STATS);
    return { data: response.data, success: true };
  },

  async clearCache(cacheType?: string): Promise<
    ApiResponse<{
      cleared_keys: number;
      cache_types: string[];
    }>
  > {
    const params = cacheType ? `?type=${cacheType}` : '';
    const response = await apiClient.post<{
      cleared_keys: number;
      cache_types: string[];
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.CACHE.CLEAR}${params}`);
    return { data: response.data, success: true };
  },

  async getDatabaseStats(): Promise<
    ApiResponse<{
      connection_count: number;
      active_queries: number;
      database_size: number;
      table_stats: Array<{
        table_name: string;
        row_count: number;
        size_mb: number;
      }>;
    }>
  > {
    const response = await apiClient.get<{
      connection_count: number;
      active_queries: number;
      database_size: number;
      table_stats: Array<{
        table_name: string;
        row_count: number;
        size_mb: number;
      }>;
    }>(API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.DATABASE.STATS);
    return { data: response.data, success: true };
  },

  // Backup & Maintenance
  async createBackup(): Promise<
    ApiResponse<{
      backup_id: string;
      status: string;
      started_at: string;
    }>
  > {
    const response = await apiClient.post<{
      backup_id: string;
      status: string;
      started_at: string;
    }>(API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.BACKUP);
    return { data: response.data, success: true };
  },

  async getBackupStatus(backupId: string): Promise<
    ApiResponse<{
      backup_id: string;
      status: 'running' | 'completed' | 'failed';
      progress: number;
      started_at: string;
      completed_at?: string;
      file_size?: number;
      error_message?: string;
    }>
  > {
    const response = await apiClient.get<{
      backup_id: string;
      status: 'running' | 'completed' | 'failed';
      progress: number;
      started_at: string;
      completed_at?: string;
      file_size?: number;
      error_message?: string;
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.BACKUP}/${backupId}`);
    return { data: response.data, success: true };
  },

  async scheduleMaintenance(maintenance: {
    title: string;
    description: string;
    start_time: string;
    duration_minutes: number;
    notify_users: boolean;
  }): Promise<
    ApiResponse<{
      maintenance_id: string;
      scheduled_for: string;
    }>
  > {
    const response = await apiClient.post<{
      maintenance_id: string;
      scheduled_for: string;
    }>(API_ENDPOINTS.ADMIN_EXTENDED.SYSTEM.MAINTENANCE.SCHEDULE, maintenance);
    return { data: response.data, success: true };
  },
};
