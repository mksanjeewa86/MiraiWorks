/**
 * Recruiter profile types
 */

export interface RecruiterProfile {
  id: number;
  user_id: number;
  years_of_experience: number | null;
  specializations: string | null;
  bio: string | null;
  company_description: string | null;
  industries: string | null;
  job_types: string | null;
  locations: string | null;
  experience_levels: string | null;
  calendar_link: string | null;
  linkedin_url: string | null;
  jobs_posted: number | null;
  candidates_placed: number | null;
  active_openings: number | null;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface RecruiterProfileCreate {
  years_of_experience?: number | null;
  specializations?: string | null;
  bio?: string | null;
  company_description?: string | null;
  industries?: string | null;
  job_types?: string | null;
  locations?: string | null;
  experience_levels?: string | null;
  calendar_link?: string | null;
  linkedin_url?: string | null;
  jobs_posted?: number | null;
  candidates_placed?: number | null;
  active_openings?: number | null;
  display_order?: number;
}

export interface RecruiterProfileUpdate {
  years_of_experience?: number | null;
  specializations?: string | null;
  bio?: string | null;
  company_description?: string | null;
  industries?: string | null;
  job_types?: string | null;
  locations?: string | null;
  experience_levels?: string | null;
  calendar_link?: string | null;
  linkedin_url?: string | null;
  jobs_posted?: number | null;
  candidates_placed?: number | null;
  active_openings?: number | null;
  display_order?: number;
}

export interface EmployerProfile {
  user_id: number;
  full_name: string;
  email: string;
  phone: string | null;
  job_title: string | null;
  bio: string | null;
  company_name: string | null;
  company_logo_url: string | null;
  linkedin_url: string | null;
}
