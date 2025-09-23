import type { Todo, TodoPermissions, TodoWithAssignedUser } from '@/types/todo';
import type { User } from '@/types/auth';

export const getTodoPermissions = (todo: Todo | TodoWithAssignedUser, user: User | null): TodoPermissions => {
  if (!user) {
    return {
      canView: false,
      canEdit: false,
      canDelete: false,
      canAssign: false,
      canChangeStatus: false,
      canAddAttachments: false,
    };
  }

  const isCreator = todo.owner_id === user.id;
  const isAssignee = todo.assigned_user_id === user.id;

  // Creator (owner) has all permissions
  if (isCreator) {
    return {
      canView: true,
      canEdit: true,
      canDelete: true,
      canAssign: true, // Any creator can assign
      canChangeStatus: true,
      canAddAttachments: true,
    };
  }

  // Assignee permissions based on visibility
  if (isAssignee) {
    const canView = todo.visibility === 'public' || todo.visibility === 'viewer';
    const canInteract = todo.visibility === 'public'; // Only if PUBLIC, not VIEWER

    return {
      canView,
      canEdit: canInteract,
      canDelete: false, // Assignees can never delete
      canAssign: false,
      canChangeStatus: canInteract,
      canAddAttachments: canInteract,
    };
  }

  // Default: no permissions
  return {
    canView: false,
    canEdit: false,
    canDelete: false,
    canAssign: false,
    canChangeStatus: false,
    canAddAttachments: false,
  };
};