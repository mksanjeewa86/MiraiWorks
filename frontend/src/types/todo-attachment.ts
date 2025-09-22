// TypeScript types for todo file attachments

export interface TodoAttachment {
  id: number;
  todo_id: number;
  original_filename: string;
  file_size: number;
  mime_type: string;
  file_extension?: string;
  description?: string;
  uploaded_by?: number;
  uploaded_at: string;
  updated_at: string;
  
  // Computed properties
  file_size_mb: number;
  file_category: 'image' | 'document' | 'video' | 'audio' | 'other';
  file_icon: string;
  download_url: string;
  preview_url?: string;
  is_image: boolean;
  is_document: boolean;
  is_video: boolean;
  is_audio: boolean;
}

export interface TodoAttachmentList {
  attachments: TodoAttachment[];
  total_count: number;
  total_size_mb: number;
}

export interface FileUploadResponse {
  message: string;
  attachment: TodoAttachment;
}

export interface FileUploadRequest {
  description?: string;
}

export interface AttachmentStats {
  total_attachments: number;
  total_size_mb: number;
  file_type_counts: Record<string, number>;
  largest_file?: TodoAttachment;
  recent_attachments: TodoAttachment[];
}

export interface BulkDeleteRequest {
  attachment_ids: number[];
}

export interface BulkDeleteResponse {
  message: string;
  deleted_count: number;
  failed_deletions: Array<{
    attachment_id: number;
    filename: string;
    error: string;
  }>;
}

// File upload progress tracking
export interface FileUploadProgress {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
  attachment?: TodoAttachment;
}

// File validation result
export interface FileValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

// Upload configuration
export interface UploadConfig {
  maxFileSize: number; // in bytes (25MB = 26214400)
  allowedTypes?: string[]; // MIME types, if empty = all types allowed
  maxFiles?: number; // max files per todo, if empty = unlimited
}

// File category icons mapping
export const FILE_CATEGORY_ICONS = {
  image: 'PhotoIcon',
  document: 'DocumentTextIcon', 
  video: 'VideoCameraIcon',
  audio: 'SpeakerWaveIcon',
  other: 'DocumentIcon'
} as const;

// File size formatting utility
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
};

// File type checking utilities
export const isImageFile = (mimeType: string): boolean => {
  return mimeType.startsWith('image/');
};

export const isDocumentFile = (mimeType: string): boolean => {
  const documentTypes = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain',
    'text/csv'
  ];
  return documentTypes.includes(mimeType);
};

export const isVideoFile = (mimeType: string): boolean => {
  return mimeType.startsWith('video/');
};

export const isAudioFile = (mimeType: string): boolean => {
  return mimeType.startsWith('audio/');
};

export const getFileCategory = (mimeType: string): TodoAttachment['file_category'] => {
  if (isImageFile(mimeType)) return 'image';
  if (isDocumentFile(mimeType)) return 'document';
  if (isVideoFile(mimeType)) return 'video';
  if (isAudioFile(mimeType)) return 'audio';
  return 'other';
};

// File validation utilities
export const validateFile = (file: File, config: UploadConfig): FileValidationResult => {
  const result: FileValidationResult = {
    valid: true,
    errors: [],
    warnings: []
  };

  // Check file size
  if (file.size > config.maxFileSize) {
    result.valid = false;
    result.errors.push(
      `File size ${formatFileSize(file.size)} exceeds maximum allowed size of ${formatFileSize(config.maxFileSize)}`
    );
  }

  if (file.size === 0) {
    result.valid = false;
    result.errors.push('File is empty');
  }

  // Check file type if restrictions exist
  if (config.allowedTypes && config.allowedTypes.length > 0) {
    if (!config.allowedTypes.includes(file.type)) {
      result.valid = false;
      result.errors.push(`File type '${file.type}' is not allowed`);
    }
  }

  // Add warnings for large files
  if (file.size > 10 * 1024 * 1024) { // 10MB
    result.warnings.push('Large file may take longer to upload');
  }

  return result;
};

// Default upload configuration
export const DEFAULT_UPLOAD_CONFIG: UploadConfig = {
  maxFileSize: 25 * 1024 * 1024, // 25MB
  allowedTypes: [], // All types allowed
  maxFiles: undefined // No limit
};

// Component Props Interfaces
export interface AttachmentListProps {
  todoId: number;
  attachments: TodoAttachment[];
  onAttachmentDeleted: (attachmentId: number) => void;
  onAttachmentUpdated: (attachment: TodoAttachment) => void;
  className?: string;
  showActions?: boolean;
}

export interface FileUploadProps {
  todoId: number;
  onUploadSuccess: (attachment: TodoAttachment) => void;
  onUploadError: (error: string) => void;
  className?: string;
  disabled?: boolean;
}