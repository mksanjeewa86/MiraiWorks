import { apiClient } from './apiClient';
import type { ApiResponse } from '@/types';

// Bulk Operations Types
export interface BulkOperation {
  id: string;
  type: 'import' | 'export' | 'delete' | 'update' | 'migrate';
  entity_type: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  total_items: number;
  processed_items: number;
  success_count: number;
  error_count: number;
  created_by: {
    id: number;
    full_name: string;
    email: string;
  };
  created_at: string;
  started_at?: string;
  completed_at?: string;
  file_url?: string;
  error_details?: string[];
}

export interface BulkImportRequest {
  entity_type: 'users' | 'companies' | 'positions' | 'interviews' | 'candidates';
  file: File;
  options: {
    skip_duplicates?: boolean;
    update_existing?: boolean;
    validate_only?: boolean;
    batch_size?: number;
  };
}

export interface BulkExportRequest {
  entity_type: 'users' | 'companies' | 'positions' | 'interviews' | 'audit_logs' | 'messages';
  filters?: Record<string, any>;
  format: 'csv' | 'excel' | 'json';
  include_deleted?: boolean;
  date_range?: {
    start_date: string;
    end_date: string;
  };
}

export interface BulkUpdateRequest {
  entity_type: string;
  entity_ids: number[];
  updates: Record<string, any>;
  options: {
    validate_before_update?: boolean;
    send_notifications?: boolean;
  };
}

export interface BulkDeleteRequest {
  entity_type: string;
  entity_ids: number[];
  options: {
    hard_delete?: boolean;
    cascade?: boolean;
    backup_before_delete?: boolean;
  };
}

export interface ImportValidationResult {
  valid_rows: number;
  invalid_rows: number;
  warnings: Array<{
    row: number;
    field: string;
    message: string;
    severity: 'warning' | 'error';
  }>;
  preview: Array<Record<string, any>>;
}

export interface DataMigrationJob {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  log_entries: Array<{
    timestamp: string;
    level: 'info' | 'warning' | 'error';
    message: string;
  }>;
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export const bulkOperationsApi = {
  // Bulk Import Operations
  async importData(request: BulkImportRequest): Promise<ApiResponse<BulkOperation>> {
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('entity_type', request.entity_type);
    formData.append('options', JSON.stringify(request.options));

    const response = await apiClient.post<BulkOperation>('/api/admin/bulk/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return { data: response.data, success: true };
  },

  async validateImport(request: BulkImportRequest): Promise<ApiResponse<ImportValidationResult>> {
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('entity_type', request.entity_type);

    const response = await apiClient.post<ImportValidationResult>(
      '/api/admin/bulk/validate-import',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return { data: response.data, success: true };
  },

  async getImportTemplate(entityType: string): Promise<ApiResponse<{
    download_url: string;
    expires_at: string;
  }>> {
    const response = await apiClient.get<{
      download_url: string;
      expires_at: string;
    }>(`/api/admin/bulk/import-template/${entityType}`);
    return { data: response.data, success: true };
  },

  // Bulk Export Operations
  async exportData(request: BulkExportRequest): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.post<BulkOperation>('/api/admin/bulk/export', request);
    return { data: response.data, success: true };
  },

  async getExportFormats(entityType: string): Promise<ApiResponse<{
    formats: Array<{
      format: string;
      description: string;
      supported_features: string[];
    }>;
  }>> {
    const response = await apiClient.get<{
      formats: Array<{
        format: string;
        description: string;
        supported_features: string[];
      }>;
    }>(`/api/admin/bulk/export-formats/${entityType}`);
    return { data: response.data, success: true };
  },

  // Bulk Update Operations
  async bulkUpdate(request: BulkUpdateRequest): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.post<BulkOperation>('/api/admin/bulk/update', request);
    return { data: response.data, success: true };
  },

  async previewBulkUpdate(request: BulkUpdateRequest): Promise<ApiResponse<{
    affected_items: Array<{
      id: number;
      current_values: Record<string, any>;
      new_values: Record<string, any>;
      warnings?: string[];
    }>;
    total_affected: number;
  }>> {
    const response = await apiClient.post<{
      affected_items: Array<{
        id: number;
        current_values: Record<string, any>;
        new_values: Record<string, any>;
        warnings?: string[];
      }>;
      total_affected: number;
    }>('/api/admin/bulk/preview-update', request);
    return { data: response.data, success: true };
  },

  // Bulk Delete Operations
  async bulkDelete(request: BulkDeleteRequest): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.post<BulkOperation>('/api/admin/bulk/delete', request);
    return { data: response.data, success: true };
  },

  async previewBulkDelete(request: BulkDeleteRequest): Promise<ApiResponse<{
    items_to_delete: Array<{
      id: number;
      display_name: string;
      dependencies: Array<{
        entity_type: string;
        count: number;
      }>;
      warnings?: string[];
    }>;
    total_to_delete: number;
    cascade_effects: Record<string, number>;
  }>> {
    const response = await apiClient.post<{
      items_to_delete: Array<{
        id: number;
        display_name: string;
        dependencies: Array<{
          entity_type: string;
          count: number;
        }>;
        warnings?: string[];
      }>;
      total_to_delete: number;
      cascade_effects: Record<string, number>;
    }>('/api/admin/bulk/preview-delete', request);
    return { data: response.data, success: true };
  },

  // Operation Management
  async getBulkOperations(
    page = 1,
    size = 20,
    type?: string,
    status?: string
  ): Promise<ApiResponse<{
    operations: BulkOperation[];
    total: number;
    page: number;
    size: number;
  }>> {
    const params = new URLSearchParams();
    params.set('page', page.toString());
    params.set('size', size.toString());
    if (type) params.set('type', type);
    if (status) params.set('status', status);

    const response = await apiClient.get<{
      operations: BulkOperation[];
      total: number;
      page: number;
      size: number;
    }>(`/api/admin/bulk/operations?${params.toString()}`);
    return { data: response.data, success: true };
  },

  async getBulkOperation(operationId: string): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.get<BulkOperation>(`/api/admin/bulk/operations/${operationId}`);
    return { data: response.data, success: true };
  },

  async cancelBulkOperation(operationId: string): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.post<BulkOperation>(
      `/api/admin/bulk/operations/${operationId}/cancel`
    );
    return { data: response.data, success: true };
  },

  async retryBulkOperation(operationId: string): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.post<BulkOperation>(
      `/api/admin/bulk/operations/${operationId}/retry`
    );
    return { data: response.data, success: true };
  },

  async downloadOperationResult(operationId: string): Promise<void> {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(
      `/api/admin/bulk/operations/${operationId}/download`,
      {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }
    );

    if (!response.ok) throw new Error('Download failed');

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `operation-${operationId}-results.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  // Data Migration Jobs
  async getDataMigrationJobs(): Promise<ApiResponse<DataMigrationJob[]>> {
    const response = await apiClient.get<DataMigrationJob[]>('/api/admin/data-migration/jobs');
    return { data: response.data, success: true };
  },

  async startDataMigration(jobName: string, parameters?: Record<string, any>): Promise<ApiResponse<DataMigrationJob>> {
    const response = await apiClient.post<DataMigrationJob>('/api/admin/data-migration/start', {
      job_name: jobName,
      parameters: parameters || {},
    });
    return { data: response.data, success: true };
  },

  async getDataMigrationStatus(jobId: string): Promise<ApiResponse<DataMigrationJob>> {
    const response = await apiClient.get<DataMigrationJob>(`/api/admin/data-migration/jobs/${jobId}`);
    return { data: response.data, success: true };
  },

  // Batch Processing Utilities
  async getEntityCounts(): Promise<ApiResponse<Record<string, number>>> {
    const response = await apiClient.get<Record<string, number>>('/api/admin/bulk/entity-counts');
    return { data: response.data, success: true };
  },

  async validateEntityIds(
    entityType: string,
    entityIds: number[]
  ): Promise<ApiResponse<{
    valid_ids: number[];
    invalid_ids: number[];
    warnings: string[];
  }>> {
    const response = await apiClient.post<{
      valid_ids: number[];
      invalid_ids: number[];
      warnings: string[];
    }>('/api/admin/bulk/validate-ids', {
      entity_type: entityType,
      entity_ids: entityIds,
    });
    return { data: response.data, success: true };
  },

  async getBulkOperationQuota(): Promise<ApiResponse<{
    monthly_operations: number;
    monthly_limit: number;
    concurrent_operations: number;
    concurrent_limit: number;
    next_reset: string;
  }>> {
    const response = await apiClient.get<{
      monthly_operations: number;
      monthly_limit: number;
      concurrent_operations: number;
      concurrent_limit: number;
      next_reset: string;
    }>('/api/admin/bulk/quota');
    return { data: response.data, success: true };
  },
};