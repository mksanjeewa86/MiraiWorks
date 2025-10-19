import { useMemo } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import type { Todo, TodoPermissions } from '@/types/todo';

export const useTodoPermissions = (todo: Todo): TodoPermissions => {
  const { user } = useAuth();

  return useMemo(() => {
    if (!user) {
      return {
        canView: false,
        canEdit: false,
        canDelete: false,
        canAssign: false,
        canChangeStatus: false,
        canAddAttachments: false,
        isOwner: false,
        isAssignee: false,
      };
    }

    const isOwner = todo.owner_id === user.id;
    const isAssignee = todo.todo_type === 'assignment' && todo.assignee_id === user.id;

    // Owner has all permissions
    if (isOwner) {
      return {
        canView: true,
        canEdit: true,
        canDelete: true,
        canAssign: true,
        canChangeStatus: true,
        canAddAttachments: true,
        isOwner: true,
        isAssignee: false,
      };
    }

    // Assignee has limited permissions
    if (isAssignee && todo.publish_status === 'published') {
      return {
        canView: true,
        canEdit: false, // Assignee can only edit notes, not other fields
        canDelete: false,
        canAssign: false,
        canChangeStatus: true, // Can complete/reopen
        canAddAttachments: true, // Assignee can add attachments
        isOwner: false,
        isAssignee: true,
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
      isOwner: false,
      isAssignee: false,
    };
  }, [user, todo]);
};

export default useTodoPermissions;
