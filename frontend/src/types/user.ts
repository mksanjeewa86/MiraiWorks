export interface UserManagement {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  is_active: boolean;
  is_admin: boolean;
  require_2fa: boolean;
  last_login?: string;
  company_id?: number;
  company_name?: string;
  roles: string[];
  created_at: string;
  updated_at: string;
  is_suspended: boolean;
  suspended_at?: string;
  suspended_by?: number;
  is_deleted: boolean;
  deleted_at?: string;
  deleted_by?: number;
}

export interface UserCreate {
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  company_id?: number;
  roles: string[];
  is_admin?: boolean;
  require_2fa?: boolean;
  send_activation_email?: boolean;
}

export interface UserUpdate {
  email?: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  is_active?: boolean;
  is_admin?: boolean;
  require_2fa?: boolean;
  roles?: string[];
}

export interface UserListResponse {
  users: UserManagement[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface UserFilters {
  page?: number;
  size?: number;
  search?: string;
  company_id?: number;
  is_active?: boolean;
  is_admin?: boolean;
  is_suspended?: boolean;
  require_2fa?: boolean;
  role?: string;
  status_filter?: string;
  include_deleted?: boolean;
}

export interface PasswordResetRequest {
  temporary_password: string;
  message: string;
}

export interface BulkUserOperation {
  user_ids: number[];
  send_email?: boolean;
}
