'use client';

import { useState, useEffect, useRef } from 'react';
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
  Info,
  ChevronDown,
  CheckCircle2,
  RotateCcw,
  Clock,
  RefreshCw,
} from 'lucide-react';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  ConfirmationModal,
} from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { Textarea } from '@/components/ui';
import { Badge } from '@/components/ui';
import { useToast } from '@/contexts/ToastContext';
import { useAuth } from '@/contexts/AuthContext';
import { todosApi } from '@/api/todos';
import { todoAttachmentAPI } from '@/api/todo-attachments';
import { userConnectionsApi } from '@/api/userConnections';
import { todoExtensionsApi } from '@/api/todo-extensions';
import { todoViewersApi } from '@/api/todo-viewers';
import AssignmentWorkflow from './AssignmentWorkflow';
import TodoViewerManager from './TodoViewerManager';
import { getTodoPermissions } from '@/utils/todoPermissions';
import { utcToLocalDateTimeParts, localDateTimePartsToUTC } from '@/utils/dateTimeUtils';
import type {
  TaskFormState,
  TaskModalProps,
  Todo,
  TodoPayload,
  TodoWithAssignedUser,
  TodoType,
  TodoPublishStatus,
  VisibilityStatus,
} from '@/types/todo';
import type { TodoAttachment } from '@/types/todo-attachment';
import type { ConnectedUser } from '@/types';

const initialFormState: TaskFormState = {
  title: '',
  description: '',
  assignee_memo: '',
  viewer_memo: '',
  dueDate: '',
  dueTime: '',
  priority: 'mid',
};

export default function TaskModal({
  isOpen,
  onClose,
  onSuccess,
  editingTodo,
  workflowContext = false,
  onComplete,
  onReopen,
  onDelete,
  onRestore,
  onRequestExtension,
}: TaskModalProps) {
  const { showToast } = useToast();
  const { user } = useAuth();
  const [formState, setFormState] = useState<TaskFormState>(initialFormState);
  const [submitting, setSubmitting] = useState(false);
  const [attachments, setAttachments] = useState<TodoAttachment[]>([]);
  const [loadingAttachments, setLoadingAttachments] = useState(false);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [todoType, setTodoType] = useState<TodoType>('regular');
  const [publishStatus, setPublishStatus] = useState<TodoPublishStatus>('published');
  const [assigneeId, setAssigneeId] = useState<number | null>(null);
  const [visibilityStatus, setVisibilityStatus] = useState<VisibilityStatus>('visible');
  const [connectedUsers, setConnectedUsers] = useState<ConnectedUser[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [assigneeSearch, setAssigneeSearch] = useState('');
  const [showAssigneeDropdown, setShowAssigneeDropdown] = useState(false);
  const [showTaskTypeDropdown, setShowTaskTypeDropdown] = useState(false);
  const [showVisibilityDropdown, setShowVisibilityDropdown] = useState(false);
  const [showPriorityDropdown, setShowPriorityDropdown] = useState(false);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);
  const [showValidationDialog, setShowValidationDialog] = useState(false);
  const [viewerRemoveConfirm, setViewerRemoveConfirm] = useState<{
    userId: number;
    userName: string;
    refetchFn: () => Promise<void>;
  } | null>(null);
  const [attachmentDeleteConfirm, setAttachmentDeleteConfirm] = useState<TodoAttachment | null>(null);

  const assigneeDropdownRef = useRef<HTMLDivElement>(null);
  const taskTypeDropdownRef = useRef<HTMLDivElement>(null);
  const visibilityDropdownRef = useRef<HTMLDivElement>(null);
  const priorityDropdownRef = useRef<HTMLDivElement>(null);

  const isEditing = Boolean(editingTodo);
  const permissions = editingTodo ? getTodoPermissions(editingTodo as Todo, user) : null;
  const isAssignee = permissions?.isAssignee || false;
  // Check if this is a viewer-only todo
  const isViewerOnly = editingTodo && (editingTodo as any).isViewerOnly === true;
  const canEditAllFields = !isAssignee && !isViewerOnly; // Assignees and viewers can only view

  // Check if we're within 1 day before due datetime (for extension request)
  const isWithinExtensionWindow = (dueDatetime?: string | null) => {
    if (!dueDatetime) return false;
    const due = new Date(dueDatetime);
    if (Number.isNaN(due.getTime())) return false;

    const now = new Date();
    const oneDayBeforeDue = new Date(due);
    oneDayBeforeDue.setDate(due.getDate() - 1);
    return now >= oneDayBeforeDue && now < due;
  };

  useEffect(() => {
    if (!isOpen) return;

    if (editingTodo) {
      // Convert UTC datetime to local date and time parts for form inputs
      const { date, time } = utcToLocalDateTimeParts(editingTodo.due_datetime);

      setFormState({
        title: editingTodo.title,
        description: editingTodo.description ?? '',
        assignee_memo: editingTodo.assignee_memo ?? '',
        viewer_memo: editingTodo.viewer_memo ?? '',
        dueDate: date,
        dueTime: time,
        priority: editingTodo.priority ?? 'mid',
      });
      // Set assignment workflow fields
      setTodoType(editingTodo.todo_type || 'regular');
      setPublishStatus(editingTodo.publish_status || 'published');
      setAssigneeId(editingTodo.assignee_id || null);
      setVisibilityStatus(editingTodo.visibility_status || 'visible');
      setAssigneeSearch(''); // Reset search, will be set after users load
      // Load attachments for existing todo
      loadAttachments(editingTodo.id);

      // Fetch connected users if this is an assignment
      if (editingTodo.todo_type === 'assignment') {
        fetchConnectedUsers();
      }
    } else {
      setFormState(initialFormState);
      setAttachments([]);
      setPendingFiles([]);
      setTodoType('regular');
      setPublishStatus('published');
      setAssigneeId(null);
      setVisibilityStatus('visible');
      setAssigneeSearch('');
      setShowAssigneeDropdown(false);
    }
  }, [isOpen, editingTodo]);

  // Fetch connected users when todo type is assignment
  useEffect(() => {
    if (todoType === 'assignment' && connectedUsers.length === 0) {
      fetchConnectedUsers();
    }
  }, [todoType]);

  // Set assignee search value after users are loaded
  useEffect(() => {
    if (connectedUsers.length > 0 && assigneeId && !assigneeSearch) {
      const assignee = connectedUsers.find(u => u.id === assigneeId);
      if (assignee) {
        setAssigneeSearch(assignee.full_name || `${assignee.first_name} ${assignee.last_name}`);
      }
    }
  }, [connectedUsers, assigneeId, assigneeSearch]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        assigneeDropdownRef.current &&
        !assigneeDropdownRef.current.contains(event.target as Node)
      ) {
        setShowAssigneeDropdown(false);
      }
      if (
        taskTypeDropdownRef.current &&
        !taskTypeDropdownRef.current.contains(event.target as Node)
      ) {
        setShowTaskTypeDropdown(false);
      }
      if (
        visibilityDropdownRef.current &&
        !visibilityDropdownRef.current.contains(event.target as Node)
      ) {
        setShowVisibilityDropdown(false);
      }
      if (
        priorityDropdownRef.current &&
        !priorityDropdownRef.current.contains(event.target as Node)
      ) {
        setShowPriorityDropdown(false);
      }
    };

    if (showAssigneeDropdown || showTaskTypeDropdown || showVisibilityDropdown || showPriorityDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showAssigneeDropdown, showTaskTypeDropdown, showVisibilityDropdown, showPriorityDropdown]);

  const fetchConnectedUsers = async () => {
    setLoadingUsers(true);
    try {
      const response = await userConnectionsApi.getMyConnections();
      if (response.success && response.data) {
        setConnectedUsers(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch connected users:', error);
    } finally {
      setLoadingUsers(false);
    }
  };

  // Filter connected users by search term
  const filteredUsers = connectedUsers.filter((user) => {
    const fullName = user.full_name || `${user.first_name} ${user.last_name}`;
    return fullName.toLowerCase().includes(assigneeSearch.toLowerCase());
  });

  // Handle assignee selection
  const handleSelectAssignee = (user: ConnectedUser | null) => {
    if (user) {
      setAssigneeId(user.id);
      setAssigneeSearch(user.full_name || `${user.first_name} ${user.last_name}`);
    } else {
      setAssigneeId(null);
      setAssigneeSearch('');
    }
    setShowAssigneeDropdown(false);
  };

  const handleInputChange =
    (field: keyof TaskFormState) =>
    (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      setFormState((prev) => ({ ...prev, [field]: event.target.value }));
    };

  const handleDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormState((prev) => ({ ...prev, dueDate: event.target.value }));
  };

  const handleTimeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormState((prev) => ({ ...prev, dueTime: event.target.value }));
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

  const handleDeleteFile = (attachment: TodoAttachment) => {
    setAttachmentDeleteConfirm(attachment);
  };

  const confirmDeleteAttachment = async () => {
    if (!attachmentDeleteConfirm || !editingTodo?.id) return;

    try {
      await todoAttachmentAPI.deleteAttachment(editingTodo.id, attachmentDeleteConfirm.id);
      handleAttachmentDeleted(attachmentDeleteConfirm.id);
      showToast({ type: 'success', title: 'File deleted successfully' });
      setAttachmentDeleteConfirm(null);
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

  // Check validation before opening extension request modal
  const handleViewerRemove = (userId: number, userName: string, refetchFn: () => Promise<void>) => {
    setViewerRemoveConfirm({ userId, userName, refetchFn });
  };

  const confirmViewerRemove = async () => {
    if (!viewerRemoveConfirm || !editingTodo) return;

    try {
      await todoViewersApi.removeViewer(editingTodo.id, viewerRemoveConfirm.userId);
      showToast({ type: 'success', title: 'Viewer removed successfully' });
      // Refresh the viewers list
      await viewerRemoveConfirm.refetchFn();
      setViewerRemoveConfirm(null);
    } catch (err) {
      console.error(err);
      showToast({
        type: 'error',
        title: err instanceof Error ? err.message : 'Failed to remove viewer',
      });
    }
  };

  const handleRequestExtension = async (todo: Todo) => {
    if (!todo.due_datetime) return;

    try {
      // Parse the current due datetime (in UTC)
      const dueDate = new Date(todo.due_datetime);
      if (Number.isNaN(dueDate.getTime())) return;

      // Calculate tomorrow at the same time (default requested date)
      const tomorrow = new Date(dueDate);
      tomorrow.setDate(tomorrow.getDate() + 1);

      // Call validation endpoint
      const validation = await todoExtensionsApi.validateExtensionRequest(
        todo.id,
        tomorrow.toISOString()
      );

      if (!validation.can_request_extension) {
        // Show validation message in dialog
        setValidationMessage(validation.reason || 'Cannot request extension for this todo');
        setShowValidationDialog(true);
      } else {
        // Open the extension request modal
        if (onRequestExtension) {
          onRequestExtension(todo);
          handleClose();
        }
      }
    } catch (error: any) {
      console.error('Failed to validate extension request:', error);
      const message = error?.response?.data?.detail || 'Failed to check extension eligibility';
      showToast({ type: 'error', title: message });
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedTitle = formState.title.trim();
    if (!trimmedTitle) {
      showToast({ type: 'error', title: 'Title is required' });
      return;
    }

    // Convert local date and time to UTC ISO string for API
    const dueDatetime = localDateTimePartsToUTC(formState.dueDate, formState.dueTime);

    // If assignee, only allow updating assignee_memo
    const updatePayload: Partial<TodoPayload> = isAssignee
      ? {
          assignee_memo: formState.assignee_memo.trim() || undefined,
        }
      : {
          title: trimmedTitle,
          description: formState.description.trim() || undefined,
          assignee_memo: formState.assignee_memo.trim() || undefined,
          priority: formState.priority || undefined,
          due_datetime: dueDatetime || undefined,
          todo_type: todoType,
          publish_status: publishStatus,
          assignee_id: todoType === 'assignment' ? assigneeId : undefined,
          visibility_status: todoType === 'assignment' ? visibilityStatus : undefined,
        };

    // Full payload for creation (never called by assignees)
    const createPayload: TodoPayload = {
      title: trimmedTitle,
      description: formState.description.trim() || undefined,
      assignee_memo: formState.assignee_memo.trim() || undefined,
      priority: formState.priority || undefined,
      due_datetime: dueDatetime || undefined,
      todo_type: todoType,
      publish_status: publishStatus,
      assignee_id: todoType === 'assignment' ? assigneeId : undefined,
      visibility_status: todoType === 'assignment' ? visibilityStatus : undefined,
    };

    // If in workflow context, just return the payload without saving to DB
    if (workflowContext) {
      onSuccess(isEditing ? updatePayload : createPayload);
      onClose();
      return;
    }

    setSubmitting(true);

    try {
      if (isEditing && editingTodo) {
        // If viewer-only, only update their private memo
        if (isViewerOnly) {
          // Viewer can only update their private memo
          await todosApi.updateViewerMemo(editingTodo.id, {
            memo: formState.viewer_memo.trim() || null,
          });
          onSuccess();
          showToast({ type: 'success', title: 'Your private notes updated' });
        } else {
          // Update the main todo
          await todosApi.update(editingTodo.id, updatePayload);

          // Update viewer memo separately (if changed)
          if (formState.viewer_memo !== (editingTodo.viewer_memo ?? '')) {
            await todosApi.updateViewerMemo(editingTodo.id, {
              memo: formState.viewer_memo.trim() || null,
            });
          }

          onSuccess();
          showToast({ type: 'success', title: 'Task updated' });
        }
      } else {
        const created = await todosApi.create(createPayload);

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
                      ? isViewerOnly
                        ? 'You have view-only access to this task. All fields are read-only.'
                        : isAssignee
                        ? 'View task details and update your progress notes.'
                        : 'Update the details, assignees, or due date for this work item.'
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
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <label className="text-sm font-medium text-slate-700">Title <span className="text-red-500">*</span></label>
                    {isViewerOnly && (
                      <div className="group relative">
                        <Info className="h-4 w-4 text-slate-400 hover:text-blue-600 cursor-help transition-colors" />
                        <div className="invisible group-hover:visible absolute left-0 top-6 z-[99999] w-64 rounded-lg bg-slate-900 p-3 text-xs text-white shadow-2xl">
                          <div className="font-semibold text-amber-300 mb-1">Read-Only Field</div>
                          <div className="text-slate-300">
                            This field is read-only. You have view-only access to this task.
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  <Input
                    placeholder="Give the task a clear, action-oriented name"
                    value={formState.title}
                    onChange={handleInputChange('title')}
                    required
                    disabled={!!(isAssignee || isViewerOnly)}
                  />
                </div>

                {/* Assignment Workflow Controls - Only show for owners */}
                {canEditAllFields && (
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2" ref={taskTypeDropdownRef}>
                    <div className="flex items-center gap-2">
                      <label className="text-sm font-medium text-slate-700">Task Type</label>
                      <div className="group relative">
                        <Info className="h-4 w-4 text-slate-400 hover:text-blue-600 cursor-help transition-colors" />
                        <div className="invisible group-hover:visible absolute left-0 top-6 z-[99999] w-72 rounded-lg bg-slate-900 p-4 text-xs text-white shadow-2xl">
                          <div className="space-y-3">
                            <div>
                              <div className="font-semibold text-blue-300 mb-1">Regular Task</div>
                              <div className="text-slate-300">
                                A personal task visible only to you. Cannot be assigned to others.
                              </div>
                            </div>
                            <div className="border-t border-slate-700 pt-2">
                              <div className="font-semibold text-green-300 mb-1">Assignment</div>
                              <div className="text-slate-300">
                                A task that can be assigned to team members with controlled visibility and tracking.
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="relative">
                      <button
                        type="button"
                        onClick={() => setShowTaskTypeDropdown(!showTaskTypeDropdown)}
                        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 pr-8 text-sm text-slate-900 text-left focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 flex items-center justify-between"
                      >
                        <span>{todoType === 'regular' ? 'Regular Task' : 'Assignment'}</span>
                        <ChevronDown className="h-4 w-4 text-slate-400 absolute right-2" />
                      </button>
                      {showTaskTypeDropdown && (
                        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-300 rounded-lg shadow-xl z-50">
                          <button
                            type="button"
                            onClick={() => {
                              setTodoType('regular');
                              setShowTaskTypeDropdown(false);
                            }}
                            className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition-colors ${
                              todoType === 'regular' ? 'bg-blue-100 text-blue-900' : 'text-slate-900'
                            }`}
                          >
                            Regular Task
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setTodoType('assignment');
                              setShowTaskTypeDropdown(false);
                            }}
                            className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition-colors ${
                              todoType === 'assignment' ? 'bg-blue-100 text-blue-900' : 'text-slate-900'
                            }`}
                          >
                            Assignment
                          </button>
                        </div>
                      )}
                    </div>
                  </div>

                  {todoType === 'assignment' && (
                    <div className="space-y-2" ref={visibilityDropdownRef}>
                      <div className="flex items-center gap-2">
                        <label className="text-sm font-medium text-slate-700">
                          Visibility Status
                        </label>
                        <div className="group relative">
                          <Info className="h-4 w-4 text-slate-400 hover:text-blue-600 cursor-help transition-colors" />
                          <div className="invisible group-hover:visible absolute right-0 top-6 z-[99999] w-72 rounded-lg bg-slate-900 p-4 text-xs text-white shadow-2xl">
                            <div className="space-y-3">
                              <div>
                                <div className="font-semibold text-green-300 mb-1">Visible</div>
                                <div className="text-slate-300">
                                  The assignee can view and work on this task. They will see it in their todo list.
                                </div>
                              </div>
                              <div className="border-t border-slate-700 pt-2">
                                <div className="font-semibold text-amber-300 mb-1">Hidden</div>
                                <div className="text-slate-300">
                                  The task is hidden from the assignee's view. Useful for drafts or tasks not ready to be worked on.
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="relative">
                        <button
                          type="button"
                          onClick={() => setShowVisibilityDropdown(!showVisibilityDropdown)}
                          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 pr-8 text-sm text-slate-900 text-left focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 flex items-center justify-between"
                        >
                          <span>{visibilityStatus === 'visible' ? 'Visible' : 'Hidden'}</span>
                          <ChevronDown className="h-4 w-4 text-slate-400 absolute right-2" />
                        </button>
                        {showVisibilityDropdown && (
                          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-300 rounded-lg shadow-xl z-50">
                            <button
                              type="button"
                              onClick={() => {
                                setVisibilityStatus('visible');
                                setShowVisibilityDropdown(false);
                              }}
                              className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition-colors ${
                                visibilityStatus === 'visible' ? 'bg-blue-100 text-blue-900' : 'text-slate-900'
                              }`}
                            >
                              Visible
                            </button>
                            <button
                              type="button"
                              onClick={() => {
                                setVisibilityStatus('hidden');
                                setShowVisibilityDropdown(false);
                              }}
                              className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition-colors ${
                                visibilityStatus === 'hidden' ? 'bg-blue-100 text-blue-900' : 'text-slate-900'
                              }`}
                            >
                              Hidden
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
                )}

                {/* Assignee Selection - Only show for assignment type and owners */}
                {canEditAllFields && todoType === 'assignment' && (
                  <div className="space-y-2 relative" ref={assigneeDropdownRef}>
                    <label className="text-sm font-medium text-slate-700">
                      Assign to
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        value={assigneeSearch}
                        onChange={(e) => {
                          setAssigneeSearch(e.target.value);
                          setShowAssigneeDropdown(true);
                        }}
                        onFocus={() => setShowAssigneeDropdown(true)}
                        placeholder={loadingUsers ? 'Loading...' : 'Search users...'}
                        disabled={loadingUsers}
                        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:bg-slate-100 disabled:cursor-not-allowed"
                      />
                      {showAssigneeDropdown && (
                        <div className="absolute top-full left-0 right-0 mt-1 max-h-60 overflow-y-auto bg-white border border-slate-300 rounded-lg shadow-2xl z-[9999]">
                          {filteredUsers.length > 0 ? (
                            <>
                              {filteredUsers.map((user) => (
                                <button
                                  key={user.id}
                                  type="button"
                                  onClick={() => handleSelectAssignee(user)}
                                  className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition-colors ${
                                    assigneeId === user.id ? 'bg-blue-100 text-blue-900' : 'text-slate-900'
                                  }`}
                                >
                                  <div className="font-medium">
                                    {user.full_name || `${user.first_name} ${user.last_name}`}
                                  </div>
                                  <div className="text-xs text-slate-500">{user.email}</div>
                                </button>
                              ))}
                            </>
                          ) : (
                            <div className="px-3 py-4 text-sm text-slate-500 text-center">
                              {loadingUsers ? 'Loading users...' : assigneeSearch ? 'No users found' : 'No connected users'}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    {!loadingUsers && connectedUsers.length === 0 && !showAssigneeDropdown && (
                      <p className="text-xs text-slate-500">
                        No connected users. Assignment will default to you.
                      </p>
                    )}
                  </div>
                )}

                <div className="grid gap-4 md:grid-cols-3">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <label className="text-sm font-medium text-slate-700">Due date</label>
                      {isViewerOnly && (
                        <div className="group relative">
                          <Info className="h-4 w-4 text-slate-400 hover:text-blue-600 cursor-help transition-colors" />
                          <div className="invisible group-hover:visible absolute left-0 top-6 z-[99999] w-64 rounded-lg bg-slate-900 p-3 text-xs text-white shadow-2xl">
                            <div className="font-semibold text-amber-300 mb-1">Read-Only Field</div>
                            <div className="text-slate-300">
                              This field is read-only. You have view-only access to this task.
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    <Input
                      type="date"
                      value={formState.dueDate}
                      onChange={handleDateChange}
                      leftIcon={<CalendarClock className="h-4 w-4" />}
                      disabled={!!(isAssignee || isViewerOnly)}
                    />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <label className="text-sm font-medium text-slate-700">Due time (optional)</label>
                      {isViewerOnly && (
                        <div className="group relative">
                          <Info className="h-4 w-4 text-slate-400 hover:text-blue-600 cursor-help transition-colors" />
                          <div className="invisible group-hover:visible absolute left-0 top-6 z-[99999] w-64 rounded-lg bg-slate-900 p-3 text-xs text-white shadow-2xl">
                            <div className="font-semibold text-amber-300 mb-1">Read-Only Field</div>
                            <div className="text-slate-300">
                              This field is read-only. You have view-only access to this task.
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    <Input
                      type="time"
                      value={formState.dueTime}
                      onChange={handleTimeChange}
                      leftIcon={<CalendarClock className="h-4 w-4" />}
                      disabled={!!(isAssignee || isViewerOnly)}
                    />
                  </div>
                  <div className="space-y-2" ref={priorityDropdownRef}>
                    <div className="flex items-center gap-2">
                      <label className="text-sm font-medium text-slate-700">Priority</label>
                      {isViewerOnly && (
                        <div className="group relative">
                          <Info className="h-4 w-4 text-slate-400 hover:text-blue-600 cursor-help transition-colors" />
                          <div className="invisible group-hover:visible absolute right-0 top-6 z-[99999] w-64 rounded-lg bg-slate-900 p-3 text-xs text-white shadow-2xl">
                            <div className="font-semibold text-amber-300 mb-1">Read-Only Field</div>
                            <div className="text-slate-300">
                              This field is read-only. You have view-only access to this task.
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="relative" ref={priorityDropdownRef}>
                      <button
                        type="button"
                        onClick={() => !isAssignee && !isViewerOnly && setShowPriorityDropdown(!showPriorityDropdown)}
                        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 pr-8 text-sm text-slate-900 text-left focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 flex items-center justify-between disabled:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-500"
                        disabled={!!(isAssignee || isViewerOnly)}
                      >
                        <span className="capitalize">{formState.priority}</span>
                        <ChevronDown className="h-4 w-4 text-slate-400 absolute right-2" />
                      </button>
                      {showPriorityDropdown && !isAssignee && !isViewerOnly && (
                        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-300 rounded-lg shadow-xl z-50">
                          <button
                            type="button"
                            onClick={() => {
                              setFormState((prev) => ({ ...prev, priority: 'low' }));
                              setShowPriorityDropdown(false);
                            }}
                            className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition-colors ${
                              formState.priority === 'low' ? 'bg-blue-100 text-blue-900' : 'text-slate-900'
                            }`}
                          >
                            Low
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setFormState((prev) => ({ ...prev, priority: 'mid' }));
                              setShowPriorityDropdown(false);
                            }}
                            className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition-colors ${
                              formState.priority === 'mid' ? 'bg-blue-100 text-blue-900' : 'text-slate-900'
                            }`}
                          >
                            Mid
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setFormState((prev) => ({ ...prev, priority: 'high' }));
                              setShowPriorityDropdown(false);
                            }}
                            className={`w-full text-left px-3 py-2 text-sm hover:bg-blue-50 transition-colors ${
                              formState.priority === 'high' ? 'bg-blue-100 text-blue-900' : 'text-slate-900'
                            }`}
                          >
                            High
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <label className="text-sm font-medium text-slate-700">Description</label>
                    {(isAssignee || isViewerOnly) && (
                      <div className="group relative">
                        <Info className="h-4 w-4 text-slate-400 hover:text-blue-600 cursor-help transition-colors" />
                        <div className="invisible group-hover:visible absolute left-0 top-6 z-[99999] w-64 rounded-lg bg-slate-900 p-3 text-xs text-white shadow-2xl">
                          <div className="font-semibold text-amber-300 mb-1">Read-Only Field</div>
                          <div className="text-slate-300">
                            {isViewerOnly
                              ? 'This field is read-only. You have view-only access to this task.'
                              : 'This field is read-only for assignees. You can view and scroll through the content but cannot edit it. Use the Notes field below to add your updates.'}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  <Textarea
                    placeholder="Outline context, expectations, or acceptance criteria."
                    rows={4}
                    value={formState.description}
                    onChange={handleInputChange('description')}
                    className="border border-slate-300 bg-white text-slate-900 focus-visible:ring-blue-500"
                    readOnly={isAssignee || isViewerOnly || undefined}
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <label className="text-sm font-medium text-slate-700">
                        Notes {isAssignee && !isViewerOnly && <span className="text-xs text-slate-500">(you can edit)</span>}
                      </label>
                      {isViewerOnly && (
                        <div className="group relative">
                          <Info className="h-4 w-4 text-slate-400 hover:text-blue-600 cursor-help transition-colors" />
                          <div className="invisible group-hover:visible absolute left-0 top-6 z-[99999] w-64 rounded-lg bg-slate-900 p-3 text-xs text-white shadow-2xl">
                            <div className="font-semibold text-amber-300 mb-1">Read-Only Field</div>
                            <div className="text-slate-300">
                              This field is read-only. You have view-only access to this task.
                            </div>
                          </div>
                        </div>
                      )}
                      {!isViewerOnly && !isAssignee && isEditing && editingTodo?.assignee_id && (
                        <div className="group relative">
                          <Info className="h-4 w-4 text-slate-400 hover:text-blue-600 cursor-help transition-colors" />
                          <div className="invisible group-hover:visible absolute left-0 top-6 z-[99999] w-64 rounded-lg bg-slate-900 p-3 text-xs text-white shadow-2xl">
                            <div className="font-semibold text-amber-300 mb-1">Read-Only Field</div>
                            <div className="text-slate-300">
                              This field is read-only for creators. Only the assignee can edit their notes. You can view the content to track their progress.
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    {!isViewerOnly && !(isEditing && editingTodo?.assignee_id && !isAssignee) && (
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
                    )}
                  </div>
                  <Textarea
                    placeholder="Add quick reminders, meeting notes, or links."
                    rows={3}
                    value={formState.assignee_memo}
                    onChange={handleInputChange('assignee_memo')}
                    className="border border-slate-300 bg-white text-slate-900 focus-visible:ring-blue-500"
                    readOnly={isViewerOnly || (!isAssignee && isEditing && !!editingTodo?.assignee_id)}
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

                                  {/* Delete button - only when editing and user uploaded it or is owner, not for viewers */}
                                  {isEditing && !isViewerOnly && (canEditAllFields || attachment.uploaded_by === user?.id) && (
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

                {/* Viewer Private Notes - shown for all users on existing todos */}
                {isEditing && editingTodo && (
                  <div className="space-y-2 mt-4 pt-4 border-t border-slate-200">
                    <div className="flex items-center gap-2">
                      <label className="text-sm font-medium text-slate-700">
                        My Private Notes
                      </label>
                      <div className="group relative">
                        <Info className="h-4 w-4 text-slate-400 hover:text-blue-600 cursor-help transition-colors" />
                        <div className="invisible group-hover:visible absolute left-0 top-6 z-[99999] w-64 rounded-lg bg-slate-900 p-3 text-xs text-white shadow-2xl">
                          <div className="font-semibold text-blue-300 mb-1">Private Notes</div>
                          <div className="text-slate-300">
                            These notes are completely private and only visible to you. Use them to track your own thoughts, reminders, or follow-ups about this task.
                          </div>
                        </div>
                      </div>
                    </div>
                    <Textarea
                      placeholder="Add your private notes here. Only you can see these notes."
                      rows={3}
                      value={formState.viewer_memo}
                      onChange={handleInputChange('viewer_memo')}
                      className="border border-slate-300 bg-blue-50 text-slate-900 focus-visible:ring-blue-500"
                      readOnly={false}
                    />
                  </div>
                )}
              </div>


              {/* Assignment Workflow - Only show for existing assignments */}
              {isEditing && editingTodo && editingTodo.is_assignment && (
                <AssignmentWorkflow
                  todo={editingTodo as TodoWithAssignedUser}
                  onUpdate={onSuccess}
                />
              )}

              {/* Viewer Management - Only show for existing todos when user is creator */}
              {isEditing && editingTodo && permissions?.isOwner && (
                <div className="mt-6">
                  <TodoViewerManager
                    todoId={editingTodo.id}
                    isCreator={permissions.isOwner}
                    availableUsers={connectedUsers}
                    assigneeId={editingTodo.assignee_id}
                    onRemoveViewer={handleViewerRemove}
                  />
                </div>
              )}
            </div>
          </div>
          <DialogFooter className="flex-shrink-0 gap-3 border-t border-slate-200 bg-white px-6 py-4">
            <div className="flex items-center justify-between w-full">
              {/* Action buttons - only show when editing and not viewer-only */}
              {isEditing && editingTodo && !isViewerOnly && (
                <div className="flex items-center gap-2">
                  {editingTodo.is_deleted ? (
                    // Restore button for deleted todos
                    onRestore && (
                      <Button
                        type="button"
                        variant="ghost"
                        onClick={() => {
                          onRestore(editingTodo as Todo);
                          handleClose();
                        }}
                        className="border border-green-300 bg-green-50 text-green-700 hover:bg-green-100"
                        leftIcon={<RefreshCw className="h-4 w-4" />}
                      >
                        Restore
                      </Button>
                    )
                  ) : (
                    <>
                      {/* Complete button - show when todo is not completed and user can change status */}
                      {editingTodo.status !== 'completed' && permissions?.canChangeStatus && onComplete && (
                        <Button
                          type="button"
                          variant="ghost"
                          onClick={() => {
                            onComplete(editingTodo as Todo);
                          }}
                          className="border border-green-300 bg-green-50 text-green-700 hover:bg-green-100"
                          leftIcon={<CheckCircle2 className="h-4 w-4" />}
                        >
                          Complete
                        </Button>
                      )}

                      {/* Reopen button - show when todo is completed and user can change status */}
                      {editingTodo.status === 'completed' && permissions?.canChangeStatus && onReopen && (
                        <Button
                          type="button"
                          variant="ghost"
                          onClick={() => {
                            onReopen(editingTodo as Todo);
                            handleClose();
                          }}
                          className="border border-blue-300 bg-blue-50 text-blue-700 hover:bg-blue-100"
                          leftIcon={<RotateCcw className="h-4 w-4" />}
                        >
                          Reopen
                        </Button>
                      )}

                      {/* Request Extension button - only for assignees in assignments, within 1 day before due datetime */}
                      {isAssignee &&
                       editingTodo.todo_type === 'assignment' &&
                       editingTodo.status !== 'completed' &&
                       editingTodo.due_datetime &&
                       !editingTodo.is_expired &&
                       isWithinExtensionWindow(editingTodo.due_datetime) &&
                       onRequestExtension && (
                        <Button
                          type="button"
                          variant="ghost"
                          onClick={() => handleRequestExtension(editingTodo as Todo)}
                          className="border border-amber-300 bg-amber-50 text-amber-700 hover:bg-amber-100"
                          leftIcon={<Clock className="h-4 w-4" />}
                        >
                          Request Extension
                        </Button>
                      )}

                      {/* Delete button - show when user is owner */}
                      {permissions?.canDelete && onDelete && (
                        <Button
                          type="button"
                          variant="ghost"
                          onClick={() => {
                            onDelete(editingTodo as Todo);
                          }}
                          className="border border-red-300 bg-red-50 text-red-700 hover:bg-red-100"
                          leftIcon={<Trash2 className="h-4 w-4" />}
                        >
                          Delete
                        </Button>
                      )}
                    </>
                  )}
                </div>
              )}

              {/* Cancel and Save buttons */}
              <div className="flex items-center gap-3 ml-auto">
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
                  {isViewerOnly
                    ? 'Save my notes'
                    : workflowContext
                    ? 'Save & Return to Workflow'
                    : isEditing
                      ? 'Save changes'
                      : 'Create task'}
                </Button>
              </div>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>

      {/* Validation Dialog - show message when extension request is not allowed */}
      {showValidationDialog && (
        <Dialog open={showValidationDialog} onOpenChange={setShowValidationDialog}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <div className="flex items-start gap-4">
                <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-amber-100 text-amber-600">
                  <Info className="h-6 w-6" />
                </div>
                <div className="flex-1">
                  <DialogTitle className="text-lg font-semibold text-slate-900">
                    Extension Request Not Available
                  </DialogTitle>
                  <DialogDescription className="mt-2 text-sm text-slate-600">
                    {validationMessage}
                  </DialogDescription>
                </div>
              </div>
            </DialogHeader>
            <DialogFooter className="mt-6">
              <Button
                type="button"
                onClick={() => setShowValidationDialog(false)}
                className="flex-1 sm:flex-none"
              >
                OK
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {/* Viewer Remove Confirmation Modal */}
      <ConfirmationModal
        isOpen={!!viewerRemoveConfirm}
        onClose={() => setViewerRemoveConfirm(null)}
        onConfirm={confirmViewerRemove}
        title="Remove Viewer"
        message={`Are you sure you want to remove ${viewerRemoveConfirm?.userName} as a viewer? They will no longer be able to view this todo.`}
        confirmText="Remove"
        cancelText="Cancel"
        dangerous={true}
        icon={<Trash2 className="h-6 w-6 text-red-600" />}
      />

      {/* Attachment Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={!!attachmentDeleteConfirm}
        onClose={() => setAttachmentDeleteConfirm(null)}
        onConfirm={confirmDeleteAttachment}
        title="Delete Attachment"
        message={`Are you sure you want to delete "${attachmentDeleteConfirm?.original_filename}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        dangerous={true}
        icon={<Trash2 className="h-6 w-6 text-red-600" />}
      />
    </Dialog>
  );
}
