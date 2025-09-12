// File Validation Types
export interface FileValidationOptions {
  maxSize?: number;
  allowedTypes?: string[];
  maxFiles?: number;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

// File Upload Types
export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface UploadOptions {
  chunkSize?: number;
  onProgress?: (progress: UploadProgress) => void;
  maxRetries?: number;
}