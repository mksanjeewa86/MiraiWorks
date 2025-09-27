"use client";

import { useState, useEffect } from "react";
import { CalendarClock, ClipboardList, MinusCircle, PlusCircle, Save, X, Paperclip } from "lucide-react";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import Button from "@/components/ui/button";
import Input from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import Badge from "@/components/ui/badge";
import { useToast } from "@/contexts/ToastContext";
import { useAuth } from "@/contexts/AuthContext";
import { todosApi } from "@/api/todos";
import { todoAttachmentAPI } from "@/api/todo-attachments";
import UserAssignment from "./UserAssignment";
import { FileUpload } from "./FileUpload";
import { AttachmentList } from "./AttachmentList";
import { getTodoPermissions } from "@/utils/todoPermissions";
import type {
  AssignableUser,
  TaskFormState,
  TaskModalProps,
  Todo,
  TodoAssignmentUpdate,
  TodoPayload,
} from "@/types/todo";
import type { TodoAttachment } from "@/types/todo-attachment";

const initialFormState: TaskFormState = {
  title: "",
  description: "",
  notes: "",
  dueDate: "",
  priority: "",
};

const formatDateForInput = (value?: string | null) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  const offset = date.getTimezoneOffset();
  const local = new Date(date.getTime() - offset * 60_000);
  return local.toISOString().slice(0, 16);
};

const toISOStringIfPresent = (value?: string) =>
  value && value.trim() ? new Date(value).toISOString() : undefined;

export default function TaskModal({ isOpen, onClose, onSuccess, editingTodo }: TaskModalProps) {
  const { showToast } = useToast();
  const { user } = useAuth();
  const [formState, setFormState] = useState<TaskFormState>(initialFormState);
  const [submitting, setSubmitting] = useState(false);
  const [assignableUsers, setAssignableUsers] = useState<AssignableUser[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);
  const [assignment, setAssignment] = useState<TodoAssignmentUpdate>({});
  const [attachments, setAttachments] = useState<TodoAttachment[]>([]);
  const [loadingAttachments, setLoadingAttachments] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);

  const isEditing = Boolean(editingTodo);
  const permissions = editingTodo ? getTodoPermissions(editingTodo as Todo, user) : null;
  const canAssign = permissions?.canAssign || !isEditing;

  useEffect(() => {
    console.log("TaskModal useEffect - loading users", { isOpen, canAssign, user: user?.email || 'no user' });
    if (isOpen && canAssign) {
      const loadUsers = async () => {
        console.log("Starting to load assignable users...");
        setLoadingUsers(true);
        try {
          const users = await todosApi.getAssignableUsers();
          console.log("Successfully loaded assignable users", users);
          setAssignableUsers(users);
        } catch (error: any) {
          console.error("Failed to load assignable users", {
            error,
            status: error?.response?.status,
            data: error?.response?.data,
            message: error?.message
          });
          const errorMessage = error?.response?.status === 401
            ? "Authentication required to load teammates"
            : "Unable to load teammates for assignment";
          showToast({ type: "error", title: errorMessage });
        } finally {
          setLoadingUsers(false);
        }
      };

      loadUsers();
    }
  }, [isOpen, canAssign, showToast]);

  useEffect(() => {
    if (!isOpen) return;

    if (editingTodo) {
      setFormState({
        title: editingTodo.title,
        description: editingTodo.description ?? "",
        notes: editingTodo.notes ?? "",
        dueDate: formatDateForInput(editingTodo.due_date),
        priority: editingTodo.priority ?? "",
      });
      setAssignment({
        assigned_user_id: editingTodo.assigned_user_id,
        visibility: editingTodo.visibility,
      });
      // Load attachments for existing todo
      loadAttachments(editingTodo.id);
    } else {
      setFormState(initialFormState);
      setAssignment({});
      setAttachments([]);
      setShowFileUpload(false);
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

  const handleClose = () => {
    if (!submitting) {
      onClose();
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const trimmedTitle = formState.title.trim();
    if (!trimmedTitle) {
      showToast({ type: "error", title: "Title is required" });
      return;
    }

    const payload: TodoPayload = {
      title: trimmedTitle,
      description: formState.description.trim() || undefined,
      notes: formState.notes.trim() || undefined,
      priority: formState.priority.trim() || undefined,
      due_date: toISOStringIfPresent(formState.dueDate),
      ...(canAssign && {
        assigned_user_id: assignment.assigned_user_id,
        visibility: assignment.visibility,
      }),
    };

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
        onSuccess();
        showToast({ type: "success", title: "Task updated" });
      } else {
        const created = await todosApi.create(payload);
        if (canAssign && assignment.assigned_user_id) {
          await todosApi.assignTodo(created.id, {
            assigned_user_id: assignment.assigned_user_id,
            visibility: assignment.visibility ?? "private",
          });
        }
        onSuccess();
        showToast({ type: "success", title: "Task created" });
      }

      onClose();
    } catch (error: any) {
      console.error("Failed to save task", error);
      const message = error?.response?.data?.detail || "We couldn't save the task.";
      showToast({ type: "error", title: message });
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
                    {isEditing ? "Edit task" : "Create a new task"}
                  </DialogTitle>
                  <DialogDescription className="text-sm text-slate-500">
                    {isEditing
                      ? "Update the details, assignees, or due date for this work item."
                      : "Capture what needs to happen next and who should own it."}
                  </DialogDescription>
                </div>
              </div>
            </div>
            <DialogClose className="rounded-full border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700">
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
                  onChange={handleInputChange("title")}
                  required
                />

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
                    onChange={handleInputChange("priority")}
                    leftIcon={<MinusCircle className="h-4 w-4" />}
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700">Description</label>
                  <Textarea
                    placeholder="Outline context, expectations, or acceptance criteria."
                    rows={4}
                    value={formState.description}
                    onChange={handleInputChange("description")}
                    className="border border-slate-300 bg-white text-slate-900 focus-visible:ring-blue-500"
                  />
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-sm font-medium text-slate-700">Notes</label>
                    <button
                      type="button"
                      onClick={() => setShowFileUpload(!showFileUpload)}
                      className="flex items-center gap-1 text-xs text-slate-500 hover:text-blue-600 transition-colors"
                    >
                      <Paperclip className="h-3 w-3" />
                      {attachments.length > 0 ? `${attachments.length} files` : 'Attach files'}
                    </button>
                  </div>
                  <Textarea
                    placeholder="Add quick reminders, meeting notes, or links."
                    rows={3}
                    value={formState.notes}
                    onChange={handleInputChange("notes")}
                    className="border border-slate-300 bg-white text-slate-900 focus-visible:ring-blue-500"
                  />

                  {/* File Upload Section */}
                  {showFileUpload && (
                    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-medium text-slate-700">File Attachments</h4>
                          <button
                            type="button"
                            onClick={() => setShowFileUpload(false)}
                            className="text-slate-400 hover:text-slate-600"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>

                        {/* File Upload (only for existing todos) */}
                        {isEditing && editingTodo?.id ? (
                          <FileUpload
                            todoId={editingTodo.id}
                            onUploadSuccess={handleUploadSuccess}
                            onUploadError={handleUploadError}
                            disabled={submitting}
                          />
                        ) : (
                          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                            <p className="text-sm text-blue-700">
                              📎 Files can be attached after creating the task
                            </p>
                          </div>
                        )}

                        {/* Attachment List */}
                        {attachments.length > 0 && (
                          <div className="space-y-2">
                            <h5 className="text-xs font-medium text-slate-600 uppercase tracking-wide">
                              Attached Files ({attachments.length})
                            </h5>
                            <AttachmentList
                              todoId={editingTodo?.id || 0}
                              attachments={attachments}
                              onAttachmentDeleted={handleAttachmentDeleted}
                              onAttachmentUpdated={handleAttachmentUpdated}
                              showActions={isEditing}
                              className="max-h-48 overflow-y-auto"
                            />
                          </div>
                        )}

                        {loadingAttachments && (
                          <div className="text-center py-4">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mx-auto"></div>
                            <p className="text-xs text-slate-500 mt-2">Loading attachments...</p>
                          </div>
                        )}
                      </div>
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
                    todo={{
                      ...formState,
                      assigned_user_id: assignment.assigned_user_id,
                      visibility: assignment.visibility || "private",
                    } as any}
                    assignableUsers={assignableUsers}
                    onAssign={handleAssignmentChange}
                    isLoading={loadingUsers || submitting}
                  />
                </div>
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
              leftIcon={isEditing ? <Save className="h-4 w-4" /> : <PlusCircle className="h-4 w-4" />}
              className="min-w-[160px] bg-blue-600 text-white shadow-lg shadow-blue-500/30 hover:bg-blue-600/90"
            >
              {isEditing ? "Save changes" : "Create task"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
