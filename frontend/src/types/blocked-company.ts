/**
 * Blocked Company Types
 *
 * Types for managing blocked companies list
 */

export interface BlockedCompany {
  id: number;
  user_id: number;
  company_id: number | null;
  company_name: string | null;
  reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface BlockedCompanyCreate {
  company_id?: number | null;
  company_name?: string | null;
  reason?: string | null;
}

export interface CompanySearchResult {
  id: number;
  name: string;
}

export interface BlockedCompaniesFilters {
  search?: string;
}
