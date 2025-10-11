/**
 * Company connection types for company-based interactions
 */

export type CompanyConnectionSourceType = 'user' | 'company';

export interface CompanyConnection {
  id: number;
  source_type: CompanyConnectionSourceType;
  source_user_id: number | null;
  source_company_id: number | null;
  target_company_id: number;
  is_active: boolean;
  connection_type: string;
  can_message: boolean;
  can_view_profile: boolean;
  can_assign_tasks: boolean;
  creation_type: string;
  created_by: number | null;
  created_at: string;
  updated_at: string | null;
  source_display_name?: string;
  target_company_name?: string;
}

export interface UserToCompanyConnectionCreate {
  target_company_id: number;
  connection_type?: string;
  can_message?: boolean;
  can_view_profile?: boolean;
  can_assign_tasks?: boolean;
}

export interface CompanyToCompanyConnectionCreate {
  source_company_id: number;
  target_company_id: number;
  connection_type?: string;
  can_message?: boolean;
  can_view_profile?: boolean;
  can_assign_tasks?: boolean;
}

export interface CompanyConnectionUpdate {
  connection_type?: string;
  can_message?: boolean;
  can_view_profile?: boolean;
  can_assign_tasks?: boolean;
}

export interface CompanyConnectionFilters {
  source_type?: CompanyConnectionSourceType;
  is_active?: boolean;
  connection_type?: string;
}
