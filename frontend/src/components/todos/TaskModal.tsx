'use client';

import { useState, useEffect } from 'react';
import {
  CalendarClock,
  ClipboardList,
  MinusCircle,
  PlusCircle,
  Save,
  X,
  Paperclip,
  Eye,
  Download,
  Trash2,
} from 'lucide-react';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { Textarea } from '@/components/ui';
import { Badge } from '@/components/ui';
import { useToast } from '@/contexts/ToastContext';
import { useAuth } from '@/contexts/AuthContext';
import { todosApi } from '@/api/todos';
import { todoAttachmentAPI } from '@/api/todo-attachments';
import UserAssignment from './UserAssignment';
import AssignmentWorkflow from './AssignmentWorkflow';
import { getTodoPermissions } from '@/utils/todoPermissions';
import type {
  AssignableUser,
  TaskFormState,
  TaskModalProps,
  Todo,
  TodoAssignmentUpdate,
  TodoPayload,
  TodoWithAssignedUser,
  TodoViewersUpdate,
  TodoType,
  TodoPublishStatus,
} from '@/types/todo';
import type { TodoAttachment } from '@/types/todo-attachment';

const initialFormState: TaskFormState = {
  title: '',
  description: '',
  notes: '',
  dueDate: '',
  priority: '',
};

const formatDateForInput = (value?: string | null) => {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60_000);
  return local.toISOString().slice(0, 16);
};

const toISOStringIfPresent = (value?: string) =>
  value && value.trim() ? new Date(value).toISOString() : undefined;

export default function TaskModal({
  isOpen,
  onClose,
  onSuccess,
  editingTodo,
  workflowContext = false,
}: TaskModalProps) {
  const { showToast } = useToast();
  const { user } = useAuth();
  const [formState, setFormState] = useState<TaskFormState>(initialFormState);
  const [submitting, setSubmitting] = useState(false);
  const [assignableUsers, setAssignableUsers] = useState<AssignableUser[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [assignment, setAssignment] = useState<TodoAssignmentUpdate>({});
  const [viewers, setViewers] = useState<number[]>([]);
  const [attachments, setAttachments] = useState<TodoAttachment[]>([]);
  const [loadingAttachments, setLoadingAttachments] = useState(false);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [todoType, setTodoType] = useState<TodoType>('regular');
  const [publishStatus, setPublishStatus] = useState<TodoPublishStatus>('published');

  const isEditing = Boolean(editingTodo);
  const permissions = editingTodo ? getTodoPermissions(editingTodo as Todo, user) : null;
  // Always allow assignment during creation, check permissions only when editing
  const canAssign = !isEditing || (permissions?.canAssign ?? false);

  useEffect(() => {
    console.log('TaskModal useEffect - loading users', {
      isOpen,
      canAssign,
      user: user?.email || 'no user',
      isEditing,
      hasUser: !!user,
      isAuthenticated: user !== null,
    });

    // Only load users if modal is open, assignment is allowed, and user is authenticated
    if (isOpen && canAssign && user) {
      const loadUsers = async () => {
        console.log('Starting to load assignable users...');
        setLoadingUsers(true);
        try {
          const users = await todosApi.getAssignableUsers();
          console.log('Successfully loaded assignable users', users);
          setAssignableUsers(users);
        } catch (error: any) {
          console.error('Failed to load assignable users', {
            error,
            status: error?.response?.status,
            data: error?.response?.data,
            message: error?.message,
          });
          const errorMessage =
            error?.response?.status === 401
              ? 'Authentication required to load teammates'
              : 'Unable to load teammates for assignment';
          showToast({ type: 'error', title: errorMessage });
        } finally {
          setLoadingUsers(false);
        }
      };

      loadUsers();
    } else {
      // Clear users if conditions not met
      if (!user) {
        console.log('No user authenticated, clearing assignable users');
        setAssignableUsers([]);
        setLoadingUsers(false);
      }
    }
  }, [isOpen, canAssign, user, showToast]);

  useEffect(() => {
    if (!isOpen) return;

    if (editingTodo) {
      setFormState({
        title: editingTodo.title,
        description: editingTodo.description ?? '',
        notes: editingTodo.notes ?? '',
        dueDate: formatDateForInput(editingTodo.due_date),
        priority: editingTodo.priority ?? '',
      });
      setAssignment({
        assigned_user_id: editingTodo.assigned_user_id,
        visibility: editingTodo.visibility,
      });
      // Load viewers from existing todo
      const todoWithViewers = editingTodo as TodoWithAssignedUser;
      setViewers(todoWithViewers.viewers?.map((v) => v.user_id) || []);
      // Set assignment workflow fields
      setTodoType(editingTodo.todo_type || 'regular');
      setPublishStatus(editingTodo.publish_status || 'published');
      // Load attachments for existing todo
      loadAttachments(editingTodo.id);
    } else {
      setFormState(initialFormState);
      setAssignment({});
      setViewers([]);
      setAttachments([]);
      setPendingFiles([]);
      setTodoType('regular');
      setPublishStatus('published');
    }
  }, [isOpen, editingTodo]);

  const handleInputChange =
    (field: keyof TaskFormState) =>
    (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setFormState((prev) => ({ ...prev, [field]: event.target.value }));
    };

  const handleDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormState((prev) => ({ ...prev, dueDate: event.target.value }));
  };

  const handleAssignmentChange = (assignmentData: TodoAssignmentUpdate) => {
    setAssignment(assignmentData);
  };

  const handleViewersChange = (viewersData: TodoViewersUpdate) => {
    setViewers(viewersData.viewer_ids || []);
  };

  // Load attachments for existing todo
  const loadAttachments = async (todoId: number) => {
    if (!todoId) return;
    setLoadingAttachments(true);
    try {
      const result = await todoAttachmentAPI.getAttachments(todoId);
      setAttachments(result.attachments);
    } catch (error) {
      console.error('Failed to load attachments:', error);
    } finally {
      setLoadingAttachments(false);
    }
  };

  // Handle file upload success
  const handleUploadSuccess = (attachment: TodoAttachment) => {
    setAttachments((prev) => [attachment, ...prev]);
    showToast({
      type: 'success',
      title: `File "${attachment.original_filename}" uploaded successfully`,
    });
  };

  // Handle file upload error
  const handleUploadError = (error: string) => {
    showToast({ type: 'error', title: error });
  };

  // Handle attachment deletion
  const handleAttachmentDeleted = (attachmentId: number) => {
    setAttachments((prev) => prev.filter((att) => att.id !== attachmentId));
    showToast({ type: 'success', title: 'File deleted successfully' });
  };

  // Handle attachment update
  const handleAttachmentUpdated = (updatedAttachment: TodoAttachment) => {
    setAttachments((prev) =>
      prev.map((att) => (att.id === updatedAttachment.id ? updatedAttachment : att))
    );
    showToast({ type: 'success', title: 'File updated successfully' });
  };

  // Handle pending file selection (for new todos)
  const handlePendingFileSelect = (files: File[]) => {
    setPendingFiles((prev) => [...prev, ...files]);
    showToast({
      type: 'success',
      title: `${files.length} file(s) selected for upload after creation`,
    });
  };

  // Remove pending file
  const handleRemovePendingFile = (fileToRemove: File) => {
    setPendingFiles((prev) => prev.filter((file) => file !== fileToRemove));
  };

  // Upload pending files after todo creation
  const uploadPendingFiles = async (todoId: number) => {
    if (pendingFiles.length === 0) return;

    let successCount = 0;
    let errorCount = 0;

    for (const file of pendingFiles) {
      try {
        const response = await todoAttachmentAPI.uploadFile(todoId, file);
        setAttachments((prev) => [response.attachment, ...prev]);
        successCount++;
      } catch (error) {
        console.error('Failed to upload pending file:', error);
        errorCount++;
      }
    }

    if (successCount > 0) {
      showToast({
        type: 'success',
        title: `${successCount} file(s) uploaded successfully`,
      });
    }

    if (errorCount > 0) {
      showToast({
        type: 'error',
        title: `Failed to upload ${errorCount} file(s)`,
      });
    }

    setPendingFiles([]);
  };

  // Handle file actions
  const handleViewFile = async (attachment: TodoAttachment) => {
    if (!editingTodo?.id) return;

    try {
      const previewUrl = await todoAttachmentAPI.getPreviewUrl(editingTodo.id, attachment.id);
      window.open(previewUrl, '_blank');
    } catch (error) {
      console.error('Failed to get preview URL:', error);
      showToast({ type: 'error', title: 'Failed to preview file' });
    }
  };

  const handleDownloadFile = async (attachment: TodoAttachment) => {
    if (!editingTodo?.id) return;

    try {
      await todoAttachmentAPI.downloadFile(editingTodo.id, attachment.id);
      showToast({ type: 'success', title: 'File downloaded successfully' });
    } catch (error) {
      console.error('Failed to download file:', error);
      showToast({ type: 'error', title: 'Failed to download file' });
    }
  };

  const handleDeleteFile = async (attachment: TodoAttachment) => {
    if (!editingTodo?.id) return;

    try {
      await todoAttachmentAPI.deleteAttachment(editingTodo.id, attachment.id);
      handleAttachmentDeleted(attachment.id);
      showToast({ type: 'success', title: 'File deleted successfully' });
    } catch (error) {
      console.error('Failed to delete attachment:', error);
      showToast({ type: 'error', title: 'Failed to delete file' });
    }
  };

  const handleClose = () => {
    if (!submitting) {
      onClose();
    }
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
      due_date: toISOStringIfPresent(formState.dueDate),
      todo_type: todoType,
      publish_status: publishStatus,
      ...(canAssign && {
        assigned_user_id: assignment.assigned_user_id,
        visibility: assignment.visibility,
      }),
    };

    // If in workflow context, just return the payload without saving to DB
    if (workflowContext) {
      onSuccess(payload);
      onClose();
      return;
    }

    setSubmitting(true);

    try {
      if (isEditing && editingTodo) {
        await todosApi.update(editingTodo.id, payload);
        if (canAssign && editingTodo.id && (assignment.assigned_user_id || assignment.visibility)) {
          await todosApi.assignTodo(editingTodo.id, {
            assigned_user_id: assignment.assigned_user_id,
            visibility: assignment.visibility,
          });
        }
        if (canAssign && editingTodo.id && viewers.length >= 0) {
          await todosApi.updateViewers(editingTodo.id, {
            viewer_ids: viewers,
          });
        }
        onSuccess();
        showToast({ type: 'success', title: 'Task updated' });
      } else {
        const created = await todosApi.create(payload);
        if (canAssign && assignment.assigned_user_id) {
          await todosApi.assignTodo(created.id, {
            assigned_user_id: assignment.assigned_user_id,
            visibility: assignment.visibility ?? 'private',
          });
        }
        if (canAssign && viewers.length > 0) {
          await todosApi.updateViewers(created.id, {
            viewer_ids: viewers,
          });
        }

        // Upload pending files after todo creation
        await uploadPendingFiles(created.id);

        onSuccess();
        showToast({ type: 'success', title: 'Task created' });
      }

      onClose();
    } catch (error: any) {
      console.error('Failed to save task', error);
      const message = error?.response?.data?.detail || "We couldn't save the task.";
      showToast({ type: 'error', title: message });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent
        closeButton={false}
        className="flex flex-col h-[90vh] max-h-[90vh] w-full max-w-4xl md:max-w-3xl overflow-hidden rounded-3xl border border-slate-200 bg-white text-slate-900 shadow-[0_30px_80px_-20px_rgba(15,23,42,0.2)]"
      >
        <DialogHeader className="flex-shrink-0 px-6 pt-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                  <ClipboardList className="h-5 w-5" />
                </span>
                <div>
                  <DialogTitle className="text-xl font-semibold text-slate-900">
                    {isEditing ? 'Edit task' : 'Create a new task'}
                  </DialogTitle>
                  <DialogDescription className="text-sm text-slate-500">
                    {isEditing
                      ? 'Update the details, assignees, or due date for this work item.'
                      : 'Capture what needs to happen next and who should own it.'}
                  </DialogDescription>
                </div>
              </div>
            </div>
            <DialogClose className="rounded-lg border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700">
              <X className="h-4 w-4" />
            </DialogClose>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-1 flex-col min-h-0">
          <div className="flex-1 overflow-y-auto px-6 py-6 min-h-0">
            <div className="space-y-8">
              <div className="grid gap-6 rounded-2xl border border-slate-200 bg-slate-50 p-6">
                <Input
                  label="Title"
                  placeholder="Give the task a clear, action-oriented name"
                  value={formState.title}
                  onChange={handleInputChange('title')}
                  required
                />

                {/* Assignment Workflow Controls */}
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-slate-700">Task Type</label>
                    <select
                      value={todoType}
                      onChange={(e) => setTodoType(e.target.value as TodoType)}
                      className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                      <option value="regular">Regular Task</option>
                      <option value="assignment">Assignment</option>
                    </select>
                  </div>

                  {todoType === 'assignment' && (
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-slate-700">
                        Assignment Status
                      </label>
                      <select
                        value={publishStatus}
                        onChange={(e) => setPublishStatus(e.target.value as TodoPublishStatus)}
                        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                      >
                        <option value="draft">Draft (Not visible to assignee)</option>
                        <option value="published">Published (Visible to assignee)</option>
                      </select>
                    </div>
                  )}
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <Input
                    type="datetime-local"
                    label="Due date"
                    value={formState.dueDate}
                    onChange={handleDateChange}
                    leftIcon={<CalendarClock className="h-4 w-4" />}
                    helperText="Use your local time zone"
                  />
                  <Input
                    label="Priority"
                    placeholder="High, Medium, Low, or custom"
                    value={formState.priority}
                    onChange={handleInputChange('priority')}
                    leftIcon={<MinusCircle className="h-4 w-4" />}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Description</label>
                  <Textarea
                    placeholder="Outline context, expectations, or acceptance criteria."
                    rows={4}
                    value={formState.description}
                    onChange={handleInputChange('description')}
                    className="border border-slate-300 bg-white text-slate-900 focus-visible:ring-blue-500"
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-slate-700">Notes</label>
                    <div className="flex items-center gap-2">
                      <input
                        type="file"
                        multiple
                        onChange={(e) => {
                          const files = Array.from(e.target.files || []);
                          if (files.length > 0) {
                            if (isEditing && editingTodo?.id) {
                              // For editing todos, upload files immediately
                              files.forEach(async (file) => {
                                try {
                                  const response = await todoAttachmentAPI.uploadFile(
                                    editingTodo.id,
                                    file
                                  );
                                  handleUploadSuccess(response.attachment);
                                } catch (error) {
                                  console.error('Failed to upload file:', error);
                                  handleUploadError('Failed to upload file');
                                }
                              });
                            } else {
                              // For new todos, add to pending files
                              handlePendingFileSelect(files);
                            }
                          }
                          // Reset input
                          e.target.value = '';
                        }}
                        className="hidden"
                        id="file-input"
                      />
                      <label
                        htmlFor="file-input"
                        className="flex items-center gap-1 text-xs text-slate-500 hover:text-blue-600 transition-colors cursor-pointer"
                        title="Attach files"
                      >
                        <Paperclip className="h-4 w-4" />
                        <span>Attach files</span>
                      </label>
                    </div>
                  </div>
                  <Textarea
                    placeholder="Add quick reminders, meeting notes, or links."
                    rows={3}
                    value={formState.notes}
                    onChange={handleInputChange('notes')}
                    className="border border-slate-300 bg-white text-slate-900 focus-visible:ring-blue-500"
                  />

                  {/* Display attached files directly below Notes */}
                  {(attachments.length > 0 || pendingFiles.length > 0) && (
                    <div className="space-y-2 pt-2 border-t border-slate-200">
                      {/* Existing Attachments */}
                      {attachments.length > 0 && (
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-xs font-medium text-slate-600">
                            <Paperclip className="h-3 w-3" />
                            <span>Attached files ({attachments.length})</span>
                          </div>
                          <div className="space-y-1 ml-5">
                            {attachments.map((attachment) => (
                              <div
                                key={attachment.id}
                                className="flex items-center justify-between text-sm text-slate-700 bg-slate-50 px-3 py-2 rounded"
                              >
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2">
                                    <Paperclip className="h-3 w-3 text-slate-400 flex-shrink-0" />
                                    <span className="truncate font-medium">
                                      {attachment.original_filename}
                                    </span>
                                  </div>
                                  <div className="text-xs text-slate-500 ml-5">
                                    {(attachment.file_size / 1024 / 1024).toFixed(1)} MB
                                  </div>
                                </div>

                                {/* Action buttons */}
                                <div className="flex items-center gap-1 ml-3 flex-shrink-0">
                                  {/* View button */}
                                  <button
                                    type="button"
                                    onClick={() => handleViewFile(attachment)}
                                    className="p-1 text-blue-500 hover:text-blue-700 hover:bg-blue-50 rounded"
                                    title="View file"
                                  >
                                    <Eye className="h-3 w-3" />
                                  </button>

                                  {/* Download button */}
                                  <button
                                    type="button"
                                    onClick={() => handleDownloadFile(attachment)}
                                    className="p-1 text-green-500 hover:text-green-700 hover:bg-green-50 rounded"
                                    title="Download file"
                                  >
                                    <Download className="h-3 w-3" />
                                  </button>

                                  {/* Delete button - only when editing */}
                                  {isEditing && (
                                    <button
                                      type="button"
                                      onClick={() => handleDeleteFile(attachment)}
                                      className="p-1 text-red-500 hover:text-red-700 hover:bg-red-50 rounded"
                                      title="Delete file"
                                    >
                                      <Trash2 className="h-3 w-3" />
                                    </button>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Pending Files (for new todos) */}
                      {pendingFiles.length > 0 && (
                        <div className="space-y-1">
                          <div className="flex items-center gap-2 text-xs font-medium text-green-600">
                            <Paperclip className="h-3 w-3" />
                            <span>Selected for upload ({pendingFiles.length})</span>
                          </div>
                          <div className="space-y-1 ml-5">
                            {pendingFiles.map((file, index) => (
                              <div
                                key={`${file.name}-${index}`}
                                className="flex items-center justify-between text-sm text-green-700 bg-green-50 px-2 py-1 rounded"
                              >
                                <span className="truncate flex-1">{file.name}</span>
                                <div className="flex items-center gap-1 ml-2">
                                  <span className="text-xs text-green-600">
                                    {(file.size / 1024 / 1024).toFixed(1)} MB
                                  </span>
                                  <button
                                    type="button"
                                    onClick={() => handleRemovePendingFile(file)}
                                    className="text-red-500 hover:text-red-700 p-1"
                                    title="Remove file"
                                  >
                                    <X className="h-3 w-3" />
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {canAssign && (
                <div className="rounded-2xl border border-blue-200 bg-blue-50 p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-semibold text-blue-800">Assignment</h3>
                      <p className="text-xs text-blue-600">
                        Choose who should own this task and its visibility.
                      </p>
                    </div>
                    <Badge className="bg-blue-100 text-blue-700 ring-1 ring-inset ring-blue-200">
                      Teammate access
                    </Badge>
                  </div>
                  <UserAssignment
                    todo={
                      {
                        ...formState,
                        assigned_user_id: assignment.assigned_user_id,
                        visibility: assignment.visibility || 'private',
                        viewers: viewers.map((viewerId) => ({
                          id: viewerId,
                          user_id: viewerId,
                          user: assignableUsers.find((u) => u.id === viewerId) || {
                            id: viewerId,
                            first_name: 'Loading...',
                            last_name: '',
                            email: '',
                          },
                        })),
                      } as any
                    }
                    assignableUsers={assignableUsers}
                    onAssign={handleAssignmentChange}
                    onUpdateViewers={handleViewersChange}
                    isLoading={loadingUsers || submitting}
                  />
                </div>
              )}

              {/* Assignment Workflow - Only show for existing assignments */}
              {isEditing && editingTodo && editingTodo.is_assignment && (
                <AssignmentWorkflow
                  todo={editingTodo as TodoWithAssignedUser}
                  onUpdate={onSuccess}
                />
              )}
            </div>
          </div>
          <DialogFooter className="flex-shrink-0 gap-3 border-t border-slate-200 bg-white px-6 py-4">
            <Button
              type="button"
              variant="ghost"
              disabled={submitting}
              onClick={handleClose}
              className="min-w-[120px] border border-slate-300 bg-white text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              loading={submitting}
              leftIcon={
                isEditing ? <Save className="h-4 w-4" /> : <PlusCircle className="h-4 w-4" />
              }
              className="min-w-[160px] bg-blue-600 text-white shadow-lg shadow-blue-500/30 hover:bg-blue-600/90"
            >
              {workflowContext
                ? 'Save & Return to Workflow'
                : isEditing
                  ? 'Save changes'
                  : 'Create task'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
