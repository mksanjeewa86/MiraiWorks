export interface Position {
  id: number;
  title: string;
  description?: string;
  summary?: string;
  department?: string;
  location?: string;
  country?: string;
  city?: string;
  job_type: 'full_time' | 'part_time' | 'contract' | 'temporary' | 'internship' | 'freelance';
  experience_level: 'entry_level' | 'mid_level' | 'senior_level' | 'executive' | 'internship';
  remote_type: 'on_site' | 'remote' | 'hybrid';
  requirements?: string;
  preferred_skills?: string[];
  required_skills?: string[];
  benefits?: string[];
  perks?: string[];
  salary_min?: number;
  salary_max?: number;
  salary_type?: 'hourly' | 'daily' | 'monthly' | 'annual' | 'project';
  salary_currency?: string;
  show_salary?: boolean;
  application_deadline?: string;
  external_apply_url?: string;
  application_questions?: Record<string, unknown>[];
  status: 'draft' | 'published' | 'paused' | 'closed' | 'archived';
  is_featured?: boolean;
  is_urgent?: boolean;
  view_count?: number;
  application_count?: number;
  published_at?: string;
  expires_at?: string;
  posted_by?: number;
  created_at?: string;
  updated_at?: string;
  slug?: string;
  company_id: number;
  company_name?: string;
  company_logo_url?: string;
  is_active?: boolean;
  days_since_published?: number;
  salary_range_display?: string;
  seo_title?: string;
  seo_description?: string;
  social_image_url?: string;
}

export interface PositionCreate {
  title: string;
  description: string;
  summary?: string;
  department?: string;
  location?: string;
  country?: string;
  city?: string;
  job_type?: 'full_time' | 'part_time' | 'contract' | 'temporary' | 'internship' | 'freelance';
  experience_level?: 'entry_level' | 'mid_level' | 'senior_level' | 'executive' | 'internship';
  remote_type?: 'on_site' | 'remote' | 'hybrid';
  requirements?: string;
  preferred_skills?: string[];
  required_skills?: string[];
  benefits?: string[];
  perks?: string[];
  salary_min?: number;
  salary_max?: number;
  salary_type?: 'hourly' | 'daily' | 'monthly' | 'annual' | 'project';
  salary_currency?: string;
  show_salary?: boolean;
  application_deadline?: string;
  external_apply_url?: string;
  application_questions?: Record<string, unknown>[];
  is_featured?: boolean;
  is_urgent?: boolean;
  seo_title?: string;
  seo_description?: string;
  social_image_url?: string;
  company_id: number;
  posted_by?: number;
}

export interface PositionUpdate {
  title?: string;
  description?: string;
  summary?: string;
  department?: string;
  location?: string;
  country?: string;
  city?: string;
  job_type?: 'full_time' | 'part_time' | 'contract' | 'temporary' | 'internship' | 'freelance';
  experience_level?: 'entry_level' | 'mid_level' | 'senior_level' | 'executive' | 'internship';
  remote_type?: 'on_site' | 'remote' | 'hybrid';
  requirements?: string;
  preferred_skills?: string[];
  required_skills?: string[];
  benefits?: string[];
  perks?: string[];
  salary_min?: number;
  salary_max?: number;
  salary_type?: 'hourly' | 'daily' | 'monthly' | 'annual' | 'project';
  salary_currency?: string;
  show_salary?: boolean;
  application_deadline?: string;
  external_apply_url?: string;
  application_questions?: Record<string, unknown>[];
  status?: 'draft' | 'published' | 'paused' | 'closed' | 'archived';
  is_featured?: boolean;
  is_urgent?: boolean;
  seo_title?: string;
  seo_description?: string;
  social_image_url?: string;
}

// Position Filter Types
export type PositionFilterValue = string | number | boolean | undefined;
export type PositionFilters = Record<string, PositionFilterValue>;

// ============================================================================
// POSITION FORMS & EXTENSIONS
// ============================================================================

// New Position Form Data (from app/positions/page.tsx)
export interface NewPositionFormData {
  title: string;
  department: string;
  location: string;
  job_type: Position['job_type'];
  experience_level: Position['experience_level'];
  salaryMin: string;
  salaryMax: string;
  status: Position['status'];
  postedDate: string;
  deadline: string;
  description: string;
  requirements: string;
  benefits: string;
  remote_type: Position['remote_type'];
  is_urgent: boolean;
}

// Local Position (UI-specific extended type from app/positions/page.tsx)
export interface LocalPosition {
  id: number;
  title: string;
  company: string;
  applications: number;
  views: number;
  postedDate: string;
  deadline: string;
  requirements: string[];
  remote: boolean;
  urgent: boolean;
  type: 'full-time' | 'part-time' | 'contract' | 'internship' | 'freelance' | 'temporary';
  level: 'entry' | 'mid' | 'senior' | 'executive';
  salaryMin: number;
  salaryMax: number;
  location?: string;
  department?: string;
  description?: string;
  status: Position['status'];
  job_type: Position['job_type'];
  experience_level: Position['experience_level'];
  company_id: number;
}
