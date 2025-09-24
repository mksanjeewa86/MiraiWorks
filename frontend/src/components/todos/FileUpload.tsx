import React, { useState, useCallback, useRef } from 'react';
import {
  CloudArrowUpIcon,
  DocumentIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import {
  TodoAttachment,
  FileUploadProgress,
  validateFile,
  formatFileSize,
  DEFAULT_UPLOAD_CONFIG,
  FileUploadProps,
} from '../../types/todo-attachment';
import { todoAttachmentAPI } from '../../api/todo-attachments';

export const FileUpload: React.FC<FileUploadProps> = ({
  todoId,
  onUploadSuccess,
  onUploadError,
  className = '',
  disabled = false,
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [uploads, setUploads] = useState<FileUploadProgress[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle drag events
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  // Handle drop event
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (disabled) return;

      const files = Array.from(e.dataTransfer.files);
      handleFiles(files);
    },
    [disabled]
  );

  // Handle file input change
  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (disabled) return;

      const files = Array.from(e.target.files || []);
      handleFiles(files);

      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
    [disabled]
  );

  // Process selected files
  const handleFiles = useCallback(
    async (files: File[]) => {
      if (files.length === 0) return;

      // Validate and create upload progress entries
      const newUploads: FileUploadProgress[] = files.map((file) => {
        const validation = validateFile(file, DEFAULT_UPLOAD_CONFIG);
        return {
          file,
          progress: 0,
          status: validation.valid ? 'pending' : 'error',
          error: validation.valid ? undefined : validation.errors.join(', '),
        };
      });

      setUploads((prev) => [...prev, ...newUploads]);

      // Upload valid files
      for (const upload of newUploads) {
        if (upload.status === 'pending') {
          await uploadFile(upload);
        }
      }
    },
    [todoId, onUploadSuccess, onUploadError]
  );

  // Upload individual file
  const uploadFile = async (upload: FileUploadProgress) => {
    try {
      // Update status to uploading
      setUploads((prev) =>
        prev.map((u) => (u.file === upload.file ? { ...u, status: 'uploading', progress: 0 } : u))
      );

      const response = await todoAttachmentAPI.uploadFile(
        todoId,
        upload.file,
        undefined, // description
        (progress) => {
          // Update progress
          setUploads((prev) => prev.map((u) => (u.file === upload.file ? { ...u, progress } : u)));
        }
      );

      // Update status to success
      setUploads((prev) =>
        prev.map((u) =>
          u.file === upload.file
            ? {
                ...u,
                status: 'success',
                progress: 100,
                attachment: response.attachment,
              }
            : u
        )
      );

      onUploadSuccess(response.attachment);

      // Remove successful upload after delay
      setTimeout(() => {
        setUploads((prev) => prev.filter((u) => u.file !== upload.file));
      }, 3000);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';

      // Update status to error
      setUploads((prev) =>
        prev.map((u) =>
          u.file === upload.file ? { ...u, status: 'error', error: errorMessage } : u
        )
      );

      onUploadError(errorMessage);
    }
  };

  // Remove upload from list
  const removeUpload = useCallback((file: File) => {
    setUploads((prev) => prev.filter((u) => u.file !== file));
  }, []);

  // Open file picker
  const openFilePicker = useCallback(() => {
    if (disabled) return;
    fileInputRef.current?.click();
  }, [disabled]);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Drop Zone */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-6 text-center
          transition-colors duration-200 cursor-pointer
          ${dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={openFilePicker}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileInput}
          className="hidden"
          disabled={disabled}
        />

        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm text-gray-600">
          <span className="font-medium text-blue-600">Click to upload files</span> or drag and drop
        </p>
        <p className="text-xs text-gray-500">
          Any file type • Maximum 25MB per file • No file limit
        </p>
      </div>

      {/* Upload Progress */}
      {uploads.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-900">Uploading Files ({uploads.length})</h4>

          {uploads.map((upload, index) => (
            <div
              key={`${upload.file.name}-${index}`}
              className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
            >
              {/* File Icon */}
              <div className="flex-shrink-0">
                {upload.status === 'error' ? (
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
                ) : (
                  <DocumentIcon className="h-5 w-5 text-gray-400" />
                )}
              </div>

              {/* File Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">{upload.file.name}</p>
                <p className="text-xs text-gray-500">{formatFileSize(upload.file.size)}</p>

                {/* Progress Bar */}
                {upload.status === 'uploading' && (
                  <div className="mt-1">
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${upload.progress}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {Math.round(upload.progress)}% uploaded
                    </p>
                  </div>
                )}

                {/* Error Message */}
                {upload.status === 'error' && upload.error && (
                  <p className="text-xs text-red-600 mt-1">{upload.error}</p>
                )}

                {/* Success Message */}
                {upload.status === 'success' && (
                  <p className="text-xs text-green-600 mt-1">✓ Upload complete</p>
                )}
              </div>

              {/* Remove Button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeUpload(upload.file);
                }}
                className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
