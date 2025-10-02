import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ApiResponse } from '@/types';
import type {
  BulkOperation,
  BulkImportRequest,
  BulkExportRequest,
  BulkUpdateRequest,
  BulkDeleteRequest,
  ImportValidationResult,
  DataMigrationJob,
} from '@/types/admin';

export const bulkOperationsApi = {
  // Bulk Import Operations
  async importData(request: BulkImportRequest): Promise<ApiResponse<BulkOperation>> {
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('entity_type', request.entity_type);
    formData.append('options', JSON.stringify(request.options));

    const response = await apiClient.post<BulkOperation>(API_ENDPOINTS.ADMIN_EXTENDED.BULK.IMPORT, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return { data: response.data, success: true };
  },

  async validateImport(request: BulkImportRequest): Promise<ApiResponse<ImportValidationResult>> {
    const formData = new FormData();
    formData.append('file', request.file);
    formData.append('entity_type', request.entity_type);

    const response = await apiClient.post<ImportValidationResult>(
      API_ENDPOINTS.ADMIN_EXTENDED.BULK.VALIDATE_IMPORT,
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
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.BULK.IMPORT}/template/${entityType}`);
    return { data: response.data, success: true };
  },

  // Bulk Export Operations
  async exportData(request: BulkExportRequest): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.post<BulkOperation>(API_ENDPOINTS.ADMIN_EXTENDED.BULK.EXPORT, request);
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
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.BULK.EXPORT}/formats/${entityType}`);
    return { data: response.data, success: true };
  },

  // Bulk Update Operations
  async bulkUpdate(request: BulkUpdateRequest): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.post<BulkOperation>(API_ENDPOINTS.ADMIN_EXTENDED.BULK.UPDATE, request);
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
    }>(API_ENDPOINTS.ADMIN_EXTENDED.BULK.PREVIEW_UPDATE, request);
    return { data: response.data, success: true };
  },

  // Bulk Delete Operations
  async bulkDelete(request: BulkDeleteRequest): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.post<BulkOperation>(API_ENDPOINTS.ADMIN_EXTENDED.BULK.DELETE, request);
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
    }>(API_ENDPOINTS.ADMIN_EXTENDED.BULK.PREVIEW_DELETE, request);
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
    }>(`${API_ENDPOINTS.ADMIN_EXTENDED.BULK.IMPORT}/operations?${params.toString()}`);
    return { data: response.data, success: true };
  },

  async getBulkOperation(operationId: string): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.get<BulkOperation>(`${API_ENDPOINTS.ADMIN_EXTENDED.BULK.IMPORT}/operations/${operationId}`);
    return { data: response.data, success: true };
  },

  async cancelBulkOperation(operationId: string): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.post<BulkOperation>(
      `${API_ENDPOINTS.ADMIN_EXTENDED.BULK.IMPORT}/operations/${operationId}/cancel`
    );
    return { data: response.data, success: true };
  },

  async retryBulkOperation(operationId: string): Promise<ApiResponse<BulkOperation>> {
    const response = await apiClient.post<BulkOperation>(
      `${API_ENDPOINTS.ADMIN_EXTENDED.BULK.IMPORT}/operations/${operationId}/retry`
    );
    return { data: response.data, success: true };
  },

  async downloadOperationResult(operationId: string): Promise<void> {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(
      `${API_ENDPOINTS.ADMIN_EXTENDED.BULK.IMPORT}/operations/${operationId}/download`,
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
    const response = await apiClient.get<DataMigrationJob[]>(API_ENDPOINTS.ADMIN_EXTENDED.DATA_MIGRATION.JOBS);
    return { data: response.data, success: true };
  },

  async startDataMigration(jobName: string, parameters?: Record<string, any>): Promise<ApiResponse<DataMigrationJob>> {
    const response = await apiClient.post<DataMigrationJob>(API_ENDPOINTS.ADMIN_EXTENDED.DATA_MIGRATION.START, {
      job_name: jobName,
      parameters: parameters || {},
    });
    return { data: response.data, success: true };
  },

  async getDataMigrationStatus(jobId: string): Promise<ApiResponse<DataMigrationJob>> {
    const response = await apiClient.get<DataMigrationJob>(`${API_ENDPOINTS.ADMIN_EXTENDED.DATA_MIGRATION.JOBS}/${jobId}`);
    return { data: response.data, success: true };
  },

  // Batch Processing Utilities
  async getEntityCounts(): Promise<ApiResponse<Record<string, number>>> {
    const response = await apiClient.get<Record<string, number>>(API_ENDPOINTS.ADMIN_EXTENDED.BULK.ENTITY_COUNTS);
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
    }>(API_ENDPOINTS.ADMIN_EXTENDED.BULK.VALIDATE_IDS, {
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
    }>(API_ENDPOINTS.ADMIN_EXTENDED.BULK.QUOTA);
    return { data: response.data, success: true };
  },
};
