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
  job_count: number;
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
}

// Job and Application Types
export interface Job {
  id: number;
  title: string;
  description: string;
  company: string;
  location: string;
  salary: string;
  type: string;
  category: string;
  requirements: string[];
  postedDate: string;
  featured: boolean;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface JobApplication {
  id: number;
  job_id: number;
  user_id: number;
  status: string;
  cover_letter?: string;
  resume_id?: number;
  applied_at: string;
  updated_at: string;
  job: Job;
  applicant: import('./auth').User;
}