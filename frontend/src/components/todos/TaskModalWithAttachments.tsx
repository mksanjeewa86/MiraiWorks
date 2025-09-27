'use client';

import { useState, useEffect } from 'react';
import { X, Plus, Save, ClipboardList, Paperclip } from 'lucide-react';
import Button from '@/components/ui/button';
import Input from '@/components/ui/input';
import Badge from '@/components/ui/badge';
import DatePicker from 'react-datepicker';
import "react-datepicker/dist/react-datepicker.css";
import '@/styles/datepicker.css';
import { useToast } from '@/contexts/ToastContext';
import { todosApi } from '@/api/todos';
import { todoAttachmentAPI } from '@/api/todo-attachments';
import { FileUpload } from './FileUpload';
import { AttachmentList } from './AttachmentList';
import type { Todo, TodoPayload, TaskFormState, TaskModalProps } from '@/types/todo';
import type { TodoAttachment, TodoAttachmentList } from '@/types/todo-attachment';

const initialFormState: TaskFormState = {
  title: '',
  description: '',
  notes: '',
  dueDate: '',
  priority: '',
};

function formatDateForInput(input?: string | null): string {
  if (!input) return '';
  const date = new Date(input);
  if (Number.isNaN(date.getTime())) return '';
  const off = date.getTimezoneOffset();
  const local = new Date(date.getTime() - off * 60_000);
  return local.toISOString().slice(0, 16);
}

export default function TaskModalWithAttachments({
  isOpen,
  onClose,
  onSuccess,
  editingTodo,
}: TaskModalProps) {
  const { showToast } = useToast();
  const [formState, setFormState] = useState<TaskFormState>(initialFormState);
  const [submitting, setSubmitting] = useState(false);
  const [showAttachments, setShowAttachments] = useState(false);
  const [attachments, setAttachments] = useState<TodoAttachment[]>([]);
  const [loadingAttachments, setLoadingAttachments] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState(false);

  const isEditing = !!editingTodo;
  const todoId = editingTodo?.id;

  // Reset form when modal opens/closes or when editing todo changes
  useEffect(() => {
    if (isOpen) {
      if (editingTodo) {
        setFormState({
          title: editingTodo.title,
          description: editingTodo.description ?? '',
          notes: editingTodo.notes ?? '',
          dueDate: formatDateForInput(editingTodo.due_date),
          priority: editingTodo.priority ?? '',
        });
        // Load attachments for existing todo
        loadAttachments(editingTodo.id);
      } else {
        setFormState(initialFormState);
        setAttachments([]);
        setShowAttachments(false);
      }
    }
  }, [isOpen, editingTodo]);

  // Load attachments for the todo
  const loadAttachments = async (todoId: number) => {
    if (!todoId) return;

    setLoadingAttachments(true);
    try {
      const result = await todoAttachmentAPI.getAttachments(todoId);
      setAttachments(result.attachments);
      // Show attachments section if there are any
      if (result.attachments.length > 0) {
        setShowAttachments(true);
      }
    } catch (error) {
      console.error('Failed to load attachments:', error);
      // Don't show error toast as attachments are optional
    } finally {
      setLoadingAttachments(false);
    }
  };

  const handleInputChange =
    (field: keyof TaskFormState) =>
    (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setFormState((prev) => ({ ...prev, [field]: event.target.value }));
    };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedTitle = formState.title.trim();
    if (!trimmedTitle) {
      showToast({ type: 'error', title: 'Title is required' });
      return;
    }

    const payload: TodoPayload = {
      title: trimmedTitle,
      description: formState.description.trim() || undefined,
      notes: formState.notes.trim() || undefined,
      priority: formState.priority.trim() || undefined,
      due_date: formState.dueDate ? new Date(formState.dueDate).toISOString() : undefined,
    };

    setSubmitting(true);
    try {
      if (isEditing && editingTodo) {
        await todosApi.update(editingTodo.id, payload);
        showToast({ type: 'success', title: 'Task updated successfully' });
      } else {
        await todosApi.create(payload);
        showToast({ type: 'success', title: 'Task created successfully' });
      }
      onSuccess();
      onClose();
    } catch (err) {
      console.error(err);
      showToast({
        type: 'error',
        title:
          err instanceof Error ? err.message : `Failed to ${isEditing ? 'update' : 'create'} task`,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!submitting && !uploadingFiles) {
      onClose();
    }
  };

  // File attachment handlers
  const handleUploadSuccess = (attachment: TodoAttachment) => {
    setAttachments((prev) => [attachment, ...prev]);
    showToast({
      type: 'success',
      title: `File "${attachment.original_filename}" uploaded successfully`,
    });
  };

  const handleUploadError = (error: string) => {
    showToast({ type: 'error', title: error });
  };

  const handleAttachmentDeleted = (attachmentId: number) => {
    setAttachments((prev) => prev.filter((att) => att.id !== attachmentId));
    showToast({ type: 'success', title: 'File deleted successfully' });
  };

  const handleAttachmentUpdated = (updatedAttachment: TodoAttachment) => {
    setAttachments((prev) =>
      prev.map((att) => (att.id === updatedAttachment.id ? updatedAttachment : att))
    );
    showToast({ type: 'success', title: 'File updated successfully' });
  };

  const toggleAttachments = () => {
    setShowAttachments(!showAttachments);
  };

  // Calculate total attachment size
  const totalAttachmentSize = attachments.reduce((sum, att) => sum + att.file_size_mb, 0);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen p-4">
        {/* Backdrop */}
        <div
          className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
          onClick={handleClose}
        />

        {/* Modal */}
        <div className="relative bg-white dark:bg-gray-800 rounded-2xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-700">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-500/20 text-blue-600 dark:bg-blue-500/25 dark:text-blue-200">
                <ClipboardList className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  {isEditing ? 'Update Task' : 'Create New Task'}
                </h2>
                {isEditing && (
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="secondary" size="sm">
                      Editing
                    </Badge>
                    {attachments.length > 0 && (
                      <Badge variant="outline" size="sm">
                        {attachments.length} file{attachments.length !== 1 ? 's' : ''} 窶｢{' '}
                        {totalAttachmentSize.toFixed(1)}MB
                      </Badge>
                    )}
                  </div>
                )}
              </div>
            </div>
            <button
              onClick={handleClose}
              disabled={submitting || uploadingFiles}
              className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-50"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="flex">
            {/* Main Form */}
            <div className={`${showAttachments ? 'w-1/2' : 'w-full'} transition-all duration-300`}>
              <form onSubmit={handleSubmit} className="p-6 space-y-6">
                <div>
                  <Input
                    label="Title"
                    placeholder="What needs to get done?"
                    value={formState.title}
                    onChange={handleInputChange('title')}
                    required
                    autoFocus
                  />
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Due Date
                    </label>
                    <DatePicker
                      selected={formState.dueDate ? new Date(formState.dueDate) : null}
                      onChange={(date) => {
                        if (date) {
                          const formatted = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}T${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
                          setFormState((prev) => ({ ...prev, dueDate: formatted }));
                        } else {
                          setFormState((prev) => ({ ...prev, dueDate: '' }));
                        }
                      }}
                      showTimeSelect
                      timeFormat="HH:mm"
                      timeIntervals={15}
                      dateFormat="yyyy-MM-dd HH:mm"
                      placeholderText="Select due date"
                      isClearable
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                  </div>
                  <div>
                    <Input
                      label="Priority"
                      placeholder="e.g., High, Medium, Low"
                      value={formState.priority}
                      onChange={handleInputChange('priority')}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={formState.description}
                    onChange={handleInputChange('description')}
                    placeholder="Add more context and details..."
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Notes
                  </label>
                  <textarea
                    value={formState.notes}
                    onChange={handleInputChange('notes')}
                    placeholder="Quick reminders or additional notes..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white resize-none"
                  />
                </div>

                {/* Attachments Toggle */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    type="button"
                    onClick={toggleAttachments}
                    className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                  >
                    <Paperclip className="h-4 w-4" />
                    {attachments.length > 0
                      ? `${attachments.length} attachment${attachments.length !== 1 ? 's' : ''}`
                      : 'Add attachments'}
                  </button>
                  {isEditing && (
                    <span className="text-xs text-gray-500">
                      Files can be added to existing tasks
                    </span>
                  )}
                </div>

                {/* Footer */}
                <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={handleClose}
                    disabled={submitting || uploadingFiles}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    loading={submitting}
                    leftIcon={
                      isEditing ? <Save className="h-4 w-4" /> : <Plus className="h-4 w-4" />
                    }
                    disabled={uploadingFiles}
                  >
                    {isEditing ? 'Save Changes' : 'Create Task'}
                  </Button>
                </div>
              </form>
            </div>

            {/* Attachments Panel */}
            {showAttachments && (
              <div className="w-1/2 border-l border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      File Attachments
                    </h3>
                    <button
                      onClick={() => setShowAttachments(false)}
                      className="p-1 text-gray-400 hover:text-gray-600 rounded"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>

                  {/* File Upload (only for existing todos) */}
                  {isEditing && todoId && (
                    <div className="mb-6">
                      <FileUpload
                        todoId={todoId}
                        onUploadSuccess={handleUploadSuccess}
                        onUploadError={handleUploadError}
                        disabled={!isEditing}
                      />
                    </div>
                  )}

                  {/* New Task Info */}
                  {!isEditing && (
                    <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                      <p className="text-sm text-blue-700 dark:text-blue-300">
                        庁 Files can be attached after creating the task
                      </p>
                    </div>
                  )}

                  {/* Attachment List */}
                  {loadingAttachments ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="text-sm text-gray-500 mt-2">Loading attachments...</p>
                    </div>
                  ) : (
                    <AttachmentList
                      todoId={todoId || 0}
                      attachments={attachments}
                      onAttachmentDeleted={handleAttachmentDeleted}
                      onAttachmentUpdated={handleAttachmentUpdated}
                      showActions={isEditing}
                      className="max-h-96 overflow-y-auto"
                    />
                  )}

                  {/* Attachment Stats */}
                  {attachments.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                      <div className="text-xs text-gray-500 space-y-1">
                        <div>Total: {attachments.length} files</div>
                        <div>Size: {totalAttachmentSize.toFixed(2)} MB</div>
                        <div>
                          Types: {[...new Set(attachments.map((a) => a.file_category))].join(', ')}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

