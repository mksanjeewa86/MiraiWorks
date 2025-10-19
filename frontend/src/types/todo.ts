export type TodoStatus = 'pending' | 'in_progress' | 'completed' | 'expired';
export type TodoVisibility = 'private' | 'public' | 'viewer';
export type TodoType = 'regular' | 'assignment';
export type TodoPublishStatus = 'draft' | 'published';
export type TodoPriority = 'low' | 'mid' | 'high';
export type VisibilityStatus = 'visible' | 'hidden';

export interface Todo {
  id: number;
  owner_id: number;
  title: string;
  description?: string | null;
  notes?: string | null;
  status: TodoStatus;
  priority?: TodoPriority | null;
  // Due datetime in UTC (ISO 8601 string with timezone)
  due_datetime?: string | null;
  completed_at?: string | null;
  expired_at?: string | null;
  is_deleted: boolean;
  deleted_at?: string | null;
  created_at: string;
  updated_at: string;
  is_expired: boolean;
  // Assignment workflow fields
  todo_type?: TodoType;
  publish_status?: TodoPublishStatus;
  assignee_id?: number | null;
  visibility_status?: VisibilityStatus | null;
  assignment_assessment?: string | null;
  assignment_score?: number | null;
  submitted_at?: string | null;
  reviewed_at?: string | null;
  reviewed_by?: number | null;
  is_assignment?: boolean;
  is_published?: boolean;
  is_draft?: boolean;
  can_be_edited_by_assignee?: boolean;
}

export interface TodoListResponse {
  items: Todo[];
  total: number;
}

export interface TodoPayload {
  title: string;
  description?: string | null;
  notes?: string | null;
  priority?: TodoPriority | null;
  // Due datetime in UTC (ISO 8601 string with timezone)
  due_datetime?: string | null;
  status?: TodoStatus;
  todo_type?: TodoType;
  publish_status?: TodoPublishStatus;
  assignee_id?: number | null;
  visibility_status?: VisibilityStatus | null;
}

export interface TodoListParams {
  includeCompleted?: boolean;
  includeDeleted?: boolean;
  status?: TodoStatus | 'pending' | 'in_progress' | 'completed' | 'expired';
  limit?: number;
  offset?: number;
}

// UI-related types
export type ViewFilter = 'all' | 'active' | 'completed' | 'expired' | 'deleted';

export interface TodoItemProps {
  todo: Todo | TodoWithAssignedUser;
  onToggleComplete?: (todo: Todo) => void;
  onEdit: (todo: Todo) => void;
  onComplete?: (todo: Todo) => void;
  onReopen?: (todo: Todo) => void;
  onDelete: (todo: Todo) => void;
  onRestore?: (todo: Todo) => void;
  onViewAttachments?: (todo: Todo) => void;
  attachmentCount?: number;
  totalAttachmentSize?: number;
  loadingId?: number | null;
}

// TaskModal component types
export interface TaskFormState {
  title: string;
  description: string;
  notes: string;
  // Due datetime in local timezone (will be converted to UTC for API)
  dueDate: string;  // Date part in YYYY-MM-DD format
  dueTime?: string;  // Time part in HH:MM format
  priority: TodoPriority;
}

export interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (todo?: any) => void;
  editingTodo?: Todo | null;
  workflowContext?: boolean;
  onComplete?: (todo: Todo) => void;
  onReopen?: (todo: Todo) => void;
  onDelete?: (todo: Todo) => void;
  onRestore?: (todo: Todo) => void;
  onRequestExtension?: (todo: Todo) => void;
}

// Assignment-related types
export interface AssignableUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  full_name?: string;
}

export interface TodoWithAssignedUser extends Todo {
  assigned_user?: AssignableUser | null;
  viewers?: TodoViewer[];
}

export interface TodoAssignmentUpdate {
  assigned_user_id?: number | null;
  visibility?: TodoVisibility;
}

export interface TodoViewer {
  id: number;
  user_id: number;
  todo_id: number;
  added_at: string;
  user: AssignableUser;
}

export interface TodoViewersUpdate {
  viewer_ids: number[];
}

// Permission-related types
export interface TodoPermissions {
  canView: boolean;
  canEdit: boolean;
  canDelete: boolean;
  canAssign: boolean;
  canChangeStatus: boolean;
  canAddAttachments: boolean;
  isOwner: boolean;
  isAssignee: boolean;
}

// Assignment component props
export interface UserAssignmentProps {
  todo: Todo | TodoWithAssignedUser;
  assignableUsers: AssignableUser[];
  onAssign: (assignment: TodoAssignmentUpdate) => void;
  onUpdateViewers?: (viewers: TodoViewersUpdate) => void;
  isLoading?: boolean;
}

// Assignment workflow types
export interface AssignmentSubmission {
  notes?: string;
}

export interface AssignmentReview {
  approved: boolean;
  assessment?: string;
  score?: number;
}

export interface AssignmentWorkflowResponse {
  success: boolean;
  message: string;
  todo: Todo;
}

export interface AssignmentStatusProps {
  todo: TodoWithAssignedUser;
  permissions: TodoPermissions;
}

// Extension request types
export type ExtensionRequestStatus = 'pending' | 'approved' | 'rejected';

export interface TodoExtensionValidation {
  can_request_extension: boolean;
  max_allowed_due_date?: string | null;
  days_extension_allowed: number;
  reason?: string | null; // Reason why extension cannot be requested
}

export interface TodoExtensionRequestCreate {
  requested_due_date: string; // ISO date string
  reason: string;
}

export interface TodoExtensionRequestResponse {
  status: ExtensionRequestStatus;
  response_reason?: string;
  new_due_date?: string; // ISO datetime string for date change approval
}

export interface TodoExtensionRequest {
  id: number;
  todo_id: number;
  requested_by_id: number;
  creator_id: number;
  requested_due_date: string;
  reason: string;
  status: ExtensionRequestStatus;
  response_reason?: string;
  responded_at?: string;
  responded_by_id?: number;
  created_at: string;
  updated_at: string;
  // Related objects
  requested_by: AssignableUser;
  creator: AssignableUser;
  responded_by?: AssignableUser;
  todo: Todo;
}

export interface TodoExtensionRequestList {
  items: TodoExtensionRequest[];
  total: number;
  pending_count: number;
  approved_count: number;
  rejected_count: number;
}

// Extension request component props
export interface ExtensionRequestModalProps {
  isOpen: boolean;
  onClose: () => void;
  todo: Todo;
  onSuccess: () => void;
}

export interface ExtensionRequestListProps {
  requests: TodoExtensionRequest[];
  onRespond?: (requestId: number, response: TodoExtensionRequestResponse) => void;
  showActions?: boolean;
}

// Additional component props
export interface AssignedTodosProps {
  onEditTodo?: (todo: Todo) => void;
  onViewAttachments?: (todo: Todo) => void;
}
