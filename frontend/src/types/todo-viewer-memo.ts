export interface TodoViewerMemo {
  id: number;
  todo_id: number;
  user_id: number;
  memo?: string | null;
  created_at: string;
  updated_at: string;
}

export interface TodoViewerMemoUpdate {
  memo?: string | null;
}
