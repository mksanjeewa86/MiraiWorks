// Import Company type for User interface
import type { Company } from './company';

// User and Authentication Types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone?: string;
  company_id: number;
  is_active: boolean;
  is_admin: boolean;
  require_2fa: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
  roles: UserRole[];
  company: Company;
}

export interface UserRole {
  id: number;
  user_id: number;
  role_id: number;
  assigned_at: string;
  assigned_by: number;
  role: Role;
}

export interface Role {
  id: number;
  name: string;
  description?: string;
  permissions: Permission[];
}

export interface Permission {
  id: number;
  name: string;
  description?: string;
  resource: string;
  action: string;
}

// Authentication Types
export interface LoginCredentials {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface RegisterData {
  email: string;
  password?: string;
  first_name: string;
  last_name: string;
  phone?: string;
  role?: string;
  company_name?: string;
  company_domain?: string;
  industry?: string;
}

export interface AuthResponse {
  user?: User;
  access_token: string;
  refresh_token: string;
  expires_in: number;
  require_2fa?: boolean;
}

export interface TwoFactorRequest {
  user_id?: number;
  code: string;
}
