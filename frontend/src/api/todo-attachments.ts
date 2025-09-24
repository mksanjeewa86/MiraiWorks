// API functions for todo file attachments

import { API_ENDPOINTS, API_CONFIG } from './config';
import { apiClient } from './apiClient';
import {
  TodoAttachment,
  TodoAttachmentList,
  FileUploadResponse,
  AttachmentStats,
  BulkDeleteResponse,
} from '../types/todo-attachment';

class TodoAttachmentAPI {
  /**
   * Upload a file attachment to a todo
   */
  async uploadFile(
    todoId: number,
    file: File,
    description?: string,
    onProgress?: (progress: number) => void
  ): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // Track upload progress
      if (onProgress) {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable) {
            const progress = (e.loaded / e.total) * 100;
            onProgress(progress);
          }
        });
      }

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch {
            reject(new Error('Invalid response format'));
          }
        } else {
          try {
            const error = JSON.parse(xhr.responseText);
            reject(new Error(error.detail || 'Upload failed'));
          } catch {
            reject(new Error(`Upload failed with status ${xhr.status}`));
          }
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Network error during upload'));
      });

      xhr.addEventListener('timeout', () => {
        reject(new Error('Upload timeout'));
      });

      xhr.open('POST', `${API_CONFIG.BASE_URL}${API_ENDPOINTS.TODOS.ATTACHMENTS.UPLOAD(todoId)}`);

      // Add authorization header if available
      const token = localStorage.getItem('accessToken');
      if (token) {
        xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      }

      xhr.timeout = 5 * 60 * 1000; // 5 minutes timeout
      xhr.send(formData);
    });
  }

  /**
   * Get all attachments for a todo
   */
  async getAttachments(
    todoId: number,
    skip: number = 0,
    limit: number = 100
  ): Promise<TodoAttachmentList> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });

    const url = `${API_ENDPOINTS.TODOS.ATTACHMENTS.BASE(todoId)}?${params}`;
    const response = await apiClient.get<TodoAttachmentList>(url);
    return response.data;
  }

  /**
   * Get attachment details
   */
  async getAttachment(todoId: number, attachmentId: number): Promise<TodoAttachment> {
    const url = API_ENDPOINTS.TODOS.ATTACHMENTS.BY_ID(todoId, attachmentId);
    const response = await apiClient.get<TodoAttachment>(url);
    return response.data;
  }

  /**
   * Download an attachment file
   */
  async downloadFile(todoId: number, attachmentId: number): Promise<void> {
    const token = localStorage.getItem('accessToken');
    const headers: Record<string, string> = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(
      `${API_CONFIG.BASE_URL}${API_ENDPOINTS.TODOS.ATTACHMENTS.DOWNLOAD(todoId, attachmentId)}`,
      { headers }
    );

    if (!response.ok) {
      throw new Error('Download failed');
    }

    // Get filename from Content-Disposition header or use default
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = 'download';

    if (contentDisposition) {
      const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
      if (matches != null && matches[1]) {
        filename = matches[1].replace(/['"]/g, '');
      }
    }

    // Create blob and download
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }

  /**
   * Get preview URL for supported file types
   */
  async getPreviewUrl(todoId: number, attachmentId: number): Promise<string> {
    const token = localStorage.getItem('accessToken');
    const authParam = token ? `?token=${encodeURIComponent(token)}` : '';
    return `${API_CONFIG.BASE_URL}${API_ENDPOINTS.TODOS.ATTACHMENTS.PREVIEW(todoId, attachmentId)}${authParam}`;
  }

  /**
   * Update attachment description
   */
  async updateAttachment(
    todoId: number,
    attachmentId: number,
    description?: string
  ): Promise<TodoAttachment> {
    const formData = new FormData();
    if (description !== undefined) {
      formData.append('description', description);
    }

    // Use fetch directly for FormData to avoid JSON serialization
    const token = localStorage.getItem('accessToken');
    const headers: Record<string, string> = {};

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(
      `${API_CONFIG.BASE_URL}${API_ENDPOINTS.TODOS.ATTACHMENTS.BY_ID(todoId, attachmentId)}`,
      {
        method: 'PUT',
        headers,
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Update failed' }));
      throw new Error(error.detail || 'Update failed');
    }

    return response.json();
  }

  /**
   * Delete an attachment
   */
  async deleteAttachment(todoId: number, attachmentId: number): Promise<void> {
    const url = API_ENDPOINTS.TODOS.ATTACHMENTS.BY_ID(todoId, attachmentId);
    await apiClient.delete(url);
  }

  /**
   * Delete multiple attachments
   */
  async bulkDeleteAttachments(
    todoId: number,
    attachmentIds: number[]
  ): Promise<BulkDeleteResponse> {
    const url = API_ENDPOINTS.TODOS.ATTACHMENTS.BULK_DELETE(todoId);
    const response = await apiClient.post<BulkDeleteResponse>(url, {
      attachment_ids: attachmentIds,
    });
    return response.data;
  }

  /**
   * Get attachment statistics for a todo
   */
  async getAttachmentStats(todoId: number): Promise<AttachmentStats> {
    const url = API_ENDPOINTS.TODOS.ATTACHMENTS.STATS(todoId);
    const response = await apiClient.get<AttachmentStats>(url);
    return response.data;
  }

  /**
   * Get user's uploaded attachments
   */
  async getMyUploads(skip: number = 0, limit: number = 100): Promise<TodoAttachment[]> {
    const params = new URLSearchParams({
      skip: skip.toString(),
      limit: limit.toString(),
    });

    const url = `${API_ENDPOINTS.TODOS.ATTACHMENTS.MY_UPLOADS}?${params}`;
    const response = await apiClient.get<TodoAttachment[]>(url);
    return response.data;
  }
}

// Export singleton instance
export const todoAttachmentAPI = new TodoAttachmentAPI();
