/**
 * Todo Viewer types
 *
 * Viewers have read-only access to todos.
 * Only the creator can add/remove viewers.
 * Viewers cannot see other viewers or the assignee.
 */

import type { UserInfo } from './user';

export interface TodoViewer {
  id: number;
  todo_id: number;
  user_id: number;
  added_by: number | null;
  created_at: string;
}

export interface TodoViewerWithUser extends TodoViewer {
  user: UserInfo;
}

export interface TodoViewerListResponse {
  items: TodoViewerWithUser[];
  total: number;
}

export interface TodoViewerCreate {
  user_id: number;
}
