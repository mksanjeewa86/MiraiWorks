import React, { useState } from 'react';
import {
  DocumentIcon,
  PhotoIcon,
  VideoCameraIcon,
  SpeakerWaveIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { TodoAttachment, formatFileSize, AttachmentListProps } from '../../types/todo-attachment';
import { todoAttachmentAPI } from '../../api/todo-attachments';

export const AttachmentList: React.FC<AttachmentListProps> = ({
  todoId,
  attachments,
  onAttachmentDeleted,
  onAttachmentUpdated,
  className = '',
  showActions = true
}) => {
  const [editingDescription, setEditingDescription] = useState<number | null>(null);
  const [tempDescription, setTempDescription] = useState('');
  const [isDeleting, setIsDeleting] = useState<number | null>(null);

  // Get appropriate icon for file type
  const getFileIcon = (attachment: TodoAttachment) => {
    const iconClass = "h-6 w-6";
    
    switch (attachment.file_category) {
      case 'image':
        return <PhotoIcon className={`${iconClass} text-blue-500`} />;
      case 'video':
        return <VideoCameraIcon className={`${iconClass} text-purple-500`} />;
      case 'audio':
        return <SpeakerWaveIcon className={`${iconClass} text-green-500`} />;
      case 'document':
        return <DocumentIcon className={`${iconClass} text-red-500`} />;
      default:
        return <DocumentIcon className={`${iconClass} text-gray-500`} />;
    }
  };

  // Handle file download
  const handleDownload = async (attachment: TodoAttachment) => {
    try {
      await todoAttachmentAPI.downloadFile(todoId, attachment.id);
    } catch (error) {
      console.error('Download failed:', error);
      // You might want to show a toast notification here
    }
  };

  // Handle file preview
  const handlePreview = async (attachment: TodoAttachment) => {
    if (!attachment.preview_url) return;
    
    try {
      const url = await todoAttachmentAPI.getPreviewUrl(todoId, attachment.id);
      window.open(url, '_blank');
    } catch (error) {
      console.error('Preview failed:', error);
    }
  };

  // Start editing description
  const startEditingDescription = (attachment: TodoAttachment) => {
    setEditingDescription(attachment.id);
    setTempDescription(attachment.description || '');
  };

  // Save description
  const saveDescription = async (attachmentId: number) => {
    try {
      const updated = await todoAttachmentAPI.updateAttachment(
        todoId, 
        attachmentId, 
        tempDescription
      );
      onAttachmentUpdated(updated);
      setEditingDescription(null);
      setTempDescription('');
    } catch (error) {
      console.error('Failed to update description:', error);
    }
  };

  // Cancel editing
  const cancelEditing = () => {
    setEditingDescription(null);
    setTempDescription('');
  };

  // Delete attachment
  const handleDelete = async (attachmentId: number) => {
    if (!confirm('Are you sure you want to delete this file?')) {
      return;
    }

    setIsDeleting(attachmentId);
    
    try {
      await todoAttachmentAPI.deleteAttachment(todoId, attachmentId);
      onAttachmentDeleted(attachmentId);
    } catch (error) {
      console.error('Delete failed:', error);
    } finally {
      setIsDeleting(null);
    }
  };

  // Format upload date
  const formatUploadDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (attachments.length === 0) {
    return (
      <div className={`text-center py-6 text-gray-500 ${className}`}>
        <DocumentIcon className="mx-auto h-12 w-12 text-gray-300" />
        <p className="mt-2 text-sm">No files attached</p>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {attachments.map((attachment) => (
        <div
          key={attachment.id}
          className="flex items-start space-x-3 p-4 bg-white border border-gray-200 rounded-lg hover:shadow-sm transition-shadow"
        >
          {/* File Icon */}
          <div className="flex-shrink-0 mt-1">
            {getFileIcon(attachment)}
          </div>

          {/* File Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-medium text-gray-900 truncate">
                  {attachment.original_filename}
                </h4>
                
                <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                  <span>{formatFileSize(attachment.file_size)}</span>
                  <span className="capitalize">{attachment.file_category}</span>
                  <span>Uploaded {formatUploadDate(attachment.uploaded_at)}</span>
                </div>

                {/* Description */}
                <div className="mt-2">
                  {editingDescription === attachment.id ? (
                    <div className="flex items-center space-x-2">
                      <input
                        type="text"
                        value={tempDescription}
                        onChange={(e) => setTempDescription(e.target.value)}
                        placeholder="Add description..."
                        className="flex-1 text-sm border border-gray-300 rounded px-2 py-1"
                        autoFocus
                      />
                      <button
                        onClick={() => saveDescription(attachment.id)}
                        className="p-1 text-green-600 hover:text-green-800"
                      >
                        <CheckIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={cancelEditing}
                        className="p-1 text-gray-400 hover:text-gray-600"
                      >
                        <XMarkIcon className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <p className="text-xs text-gray-600 flex-1">
                        {attachment.description || 'No description'}
                      </p>
                      {showActions && (
                        <button
                          onClick={() => startEditingDescription(attachment)}
                          className="p-1 text-gray-400 hover:text-gray-600"
                        >
                          <PencilIcon className="h-3 w-3" />
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Actions */}
              {showActions && editingDescription !== attachment.id && (
                <div className="flex items-center space-x-1 ml-4">
                  {/* Preview Button (for images and PDFs) */}
                  {attachment.preview_url && (
                    <button
                      onClick={() => handlePreview(attachment)}
                      className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                      title="Preview file"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                  )}

                  {/* Download Button */}
                  <button
                    onClick={() => handleDownload(attachment)}
                    className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded"
                    title="Download file"
                  >
                    <ArrowDownTrayIcon className="h-4 w-4" />
                  </button>

                  {/* Delete Button */}
                  <button
                    onClick={() => handleDelete(attachment.id)}
                    disabled={isDeleting === attachment.id}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded disabled:opacity-50"
                    title="Delete file"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};