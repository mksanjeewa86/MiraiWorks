import { MessageMetadata } from '@/types/messages';
import { UploadProgress, UploadOptions, FileValidationOptions, ValidationResult } from '@/types/file';

export class FileService {
    // Upload service constants
    private readonly MAX_CHUNK_SIZE = 1024 * 1024; // 1MB
    private readonly DEFAULT_MAX_RETRIES = 3;

    // Validation service constants
    private readonly DEFAULT_MAX_SIZE = 10 * 1024 * 1024; // 10MB
    private readonly DEFAULT_MAX_FILES = 10;
    private readonly DEFAULT_ALLOWED_TYPES = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    ];

    // ===================
    // FILE UPLOAD METHODS
    // ===================

    public async uploadFile(
        file: File,
        options: UploadOptions = {}
    ): Promise<MessageMetadata> {
        const {
            chunkSize = this.MAX_CHUNK_SIZE,
            onProgress,
            maxRetries = this.DEFAULT_MAX_RETRIES
        } = options;

        if (file.size <= chunkSize) {
            return this.uploadSingleChunk(file, onProgress);
        }

        return this.uploadMultipleChunks(file, {
            chunkSize,
            onProgress: onProgress || (() => {}),
            maxRetries
        });
    }

    private async uploadSingleChunk(
        file: File,
        onProgress?: (progress: UploadProgress) => void
    ): Promise<MessageMetadata> {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await new Promise<Response>((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/api/messages/upload');

                xhr.upload.onprogress = (e: ProgressEvent) => {
                    if (onProgress && e.lengthComputable) {
                        onProgress({
                            loaded: e.loaded,
                            total: e.total,
                            percentage: (e.loaded / e.total) * 100
                        });
                    }
                };

                xhr.onload = () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve(new Response(xhr.response, {
                            status: xhr.status,
                            statusText: xhr.statusText
                        }));
                    } else {
                        reject(new Error(`HTTP ${xhr.status} - ${xhr.statusText}`));
                    }
                };

                xhr.onerror = () => reject(new Error('Network request failed'));
                xhr.send(formData);
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const result = await response.json();
            return {
                fileUrl: result.url,
                fileName: file.name,
                fileType: file.type,
                fileSize: file.size
            };
        } catch (error) {
            console.error('File upload failed:', error);
            throw error;
        }
    }

    private async uploadMultipleChunks(
        file: File,
        options: Required<UploadOptions>
    ): Promise<MessageMetadata> {
        const { chunkSize, onProgress, maxRetries } = options;
        const chunks = Math.ceil(file.size / chunkSize);
        const uploadId = crypto.randomUUID();
        let uploadedChunks = 0;

        for (let i = 0; i < chunks; i++) {
            const start = i * chunkSize;
            const end = Math.min(start + chunkSize, file.size);
            const chunk = file.slice(start, end);
            let retries = 0;

            while (retries < maxRetries) {
                try {
                    await this.uploadChunk(chunk, {
                        uploadId,
                        chunkIndex: i,
                        totalChunks: chunks,
                        fileName: file.name
                    });
                    
                    uploadedChunks++;
                    if (onProgress) {
                        onProgress({
                            loaded: uploadedChunks * chunkSize,
                            total: file.size,
                            percentage: (uploadedChunks / chunks) * 100
                        });
                    }
                    break;
                } catch {
                    retries++;
                    if (retries === maxRetries) {
                        throw new Error(`Failed to upload chunk ${i} after ${maxRetries} retries`);
                    }
                    await new Promise(resolve => setTimeout(resolve, 1000 * retries));
                }
            }
        }

        const response = await fetch(`/api/messages/upload/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ uploadId, fileName: file.name })
        });

        if (!response.ok) {
            throw new Error('Failed to complete multipart upload');
        }

        const result = await response.json();
        return {
            fileUrl: result.url,
            fileName: file.name,
            fileType: file.type,
            fileSize: file.size
        };
    }

    private async uploadChunk(
        chunk: Blob,
        params: {
            uploadId: string;
            chunkIndex: number;
            totalChunks: number;
            fileName: string;
        }
    ): Promise<void> {
        const formData = new FormData();
        formData.append('chunk', chunk);
        formData.append('params', JSON.stringify(params));

        const response = await fetch('/api/messages/upload/chunk', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Chunk upload failed: ${response.statusText}`);
        }
    }

    // =====================
    // FILE VALIDATION METHODS
    // =====================

    public validateFiles(files: File[], options: FileValidationOptions = {}): ValidationResult {
        const maxSize = options.maxSize || this.DEFAULT_MAX_SIZE;
        const maxFiles = options.maxFiles || this.DEFAULT_MAX_FILES;
        const allowedTypes = options.allowedTypes || this.DEFAULT_ALLOWED_TYPES;
        const errors: string[] = [];

        if (files.length > maxFiles) {
            errors.push(`Maximum ${maxFiles} files allowed`);
        }

        files.forEach(file => {
            if (file.size > maxSize) {
                errors.push(`File ${file.name} exceeds maximum size of ${maxSize / 1024 / 1024}MB`);
            }

            if (!allowedTypes.includes(file.type)) {
                errors.push(`File type ${file.type} is not allowed for ${file.name}`);
            }
        });

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    public async validateFileContent(file: File): Promise<ValidationResult> {
        const errors: string[] = [];

        // Check for malicious content or corrupted files
        try {
            if (file.type.startsWith('image/')) {
                await this.validateImage(file);
            } else if (file.type === 'application/pdf') {
                await this.validatePDF(file);
            }
        } catch {
            errors.push(`File ${file.name} appears to be corrupted or invalid`);
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    private async validateImage(file: File): Promise<void> {
        return new Promise((resolve, reject) => {
            const img = new Image();
            const url = URL.createObjectURL(file);

            img.onload = () => {
                URL.revokeObjectURL(url);
                resolve();
            };

            img.onerror = () => {
                URL.revokeObjectURL(url);
                reject(new Error('Invalid image file'));
            };

            img.src = url;
        });
    }

    private async validatePDF(file: File): Promise<void> {
        const reader = new FileReader();
        return new Promise((resolve, reject) => {
            reader.onload = () => {
                const arr = new Uint8Array(reader.result as ArrayBuffer).subarray(0, 5);
                const header = String.fromCharCode.apply(null, Array.from(arr));
                if (header.indexOf('%PDF-') !== 0) {
                    reject(new Error('Invalid PDF file'));
                }
                resolve();
            };

            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsArrayBuffer(file);
        });
    }

    // ======================
    // COMBINED UTILITY METHODS
    // ======================

    /**
     * Validates and uploads a file in one operation
     */
    public async validateAndUpload(
        file: File, 
        validationOptions: FileValidationOptions = {},
        uploadOptions: UploadOptions = {}
    ): Promise<MessageMetadata> {
        // Validate basic file properties
        const basicValidation = this.validateFiles([file], validationOptions);
        if (!basicValidation.isValid) {
            throw new Error(basicValidation.errors.join(', '));
        }

        // Validate file content
        const contentValidation = await this.validateFileContent(file);
        if (!contentValidation.isValid) {
            throw new Error(contentValidation.errors.join(', '));
        }

        // Upload the file
        return this.uploadFile(file, uploadOptions);
    }
}

// Export singleton instance
export const fileService = new FileService();