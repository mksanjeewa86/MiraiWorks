export type CompanyType = 'recruiter' | 'employer';

export interface Company {
  id: number;
  name: string;
  type: CompanyType;
  email: string;
  phone: string;
  website?: string;
  postal_code?: string;
  prefecture?: string;
  city?: string;
  description?: string;
  is_active: boolean;
  user_count: number;
  position_count: number;
  job_count?: number; // Legacy compatibility
  is_deleted: boolean;
  deleted_at?: string;
  deleted_by?: number;
  created_at: string;
  updated_at: string;
}

export interface CompanyCreate {
  name: string;
  type: CompanyType;
  email: string;
  phone: string;
  website?: string;
  postal_code?: string;
  prefecture?: string;
  city?: string;
  description?: string;
  plan_id?: number;
  is_trial?: boolean;
  trial_days?: number;
}

export interface CompanyUpdate {
  name?: string;
  type?: CompanyType;
  email?: string;
  phone?: string;
  website?: string;
  postal_code?: string;
  prefecture?: string;
  city?: string;
  description?: string;
  is_active?: boolean;
}

export interface CompanyListResponse {
  companies: Company[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CompanyFilters {
  page?: number;
  size?: number;
  search?: string;
  company_type?: CompanyType;
  is_active?: boolean;
  include_deleted?: boolean;
}

// Position Application Types
export interface PositionApplication {
  id: number;
  position_id: number;
  user_id: number;
  candidate_id?: number;
  status:
    | 'applied'
    | 'under_review'
    | 'phone_screen'
    | 'interview'
    | 'technical_test'
    | 'final_interview'
    | 'offer_sent'
    | 'hired'
    | 'rejected'
    | 'withdrawn';
  cover_letter?: string;
  application_answers?: Record<string, unknown>[];
  resume_id?: number;
  source?: string;
  notes?: string;
  last_contacted_at?: string;
  applied_at: string;
  updated_at: string;
  position?: import('./position').Position;
  applicant?: import('./auth').User;
}
