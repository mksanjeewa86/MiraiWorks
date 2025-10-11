/**
 * System Update Types
 *
 * Types for system-wide updates that are visible to all users.
 */

export enum SystemUpdateTag {
  SECURITY = 'security',
  TODO = 'todo',
  INTERVIEW = 'interview',
  EXAM = 'exam',
  CALENDAR = 'calendar',
  WORKFLOW = 'workflow',
  MESSAGING = 'messaging',
  PROFILE = 'profile',
  GENERAL = 'general',
  MAINTENANCE = 'maintenance',
  FEATURE = 'feature',
  BUGFIX = 'bugfix',
}

export interface SystemUpdate {
  id: number;
  title: string;
  message: string;
  tags: SystemUpdateTag[];
  is_active: boolean;
  created_by_id: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface SystemUpdateWithCreator extends SystemUpdate {
  created_by_name: string | null;
}

export interface SystemUpdateCreateData {
  title: string;
  message: string;
  tags: SystemUpdateTag[];
}

export interface SystemUpdateUpdateData {
  title?: string;
  message?: string;
  tags?: SystemUpdateTag[];
  is_active?: boolean;
}

export interface SystemUpdateFilters {
  tags?: SystemUpdateTag[];
  skip?: number;
  limit?: number;
}
