/**
 * Profile-related types for user profiles
 * Matches backend schemas from backend/app/schemas/
 */

// ================== WORK EXPERIENCE ==================

export interface WorkExperience {
  id: number;
  user_id: number;
  company_name: string;
  company_logo_url: string | null;
  position_title: string;
  employment_type: string | null;
  location: string | null;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  description: string | null;
  skills: string | null; // Comma-separated skills
  display_order: number;
}

export interface WorkExperienceCreate {
  company_name: string;
  company_logo_url?: string | null;
  position_title: string;
  employment_type?: string | null;
  location?: string | null;
  start_date: string;
  end_date?: string | null;
  is_current?: boolean;
  description?: string | null;
  skills?: string | null;
  display_order?: number;
}

export interface WorkExperienceUpdate {
  company_name?: string;
  company_logo_url?: string | null;
  position_title?: string;
  employment_type?: string | null;
  location?: string | null;
  start_date?: string;
  end_date?: string | null;
  is_current?: boolean;
  description?: string | null;
  skills?: string | null;
  display_order?: number;
}

// Employment type constants
export const EmploymentType = {
  FULL_TIME: 'Full-time',
  PART_TIME: 'Part-time',
  CONTRACT: 'Contract',
  FREELANCE: 'Freelance',
  INTERNSHIP: 'Internship',
} as const;

// ================== EDUCATION ==================

export interface Education {
  id: number;
  user_id: number;
  institution_name: string;
  institution_logo_url: string | null;
  degree_type: string;
  field_of_study: string;
  start_date: string | null;
  end_date: string | null;
  graduation_year: number | null;
  gpa: number | null;
  gpa_max: number | null;
  honors_awards: string | null;
  description: string | null;
  display_order: number;
}

export interface EducationCreate {
  institution_name: string;
  institution_logo_url?: string | null;
  degree_type: string;
  field_of_study: string;
  start_date?: string | null;
  end_date?: string | null;
  graduation_year?: number | null;
  gpa?: number | null;
  gpa_max?: number | null;
  honors_awards?: string | null;
  description?: string | null;
  display_order?: number;
}

export interface EducationUpdate {
  institution_name?: string;
  institution_logo_url?: string | null;
  degree_type?: string;
  field_of_study?: string;
  start_date?: string | null;
  end_date?: string | null;
  graduation_year?: number | null;
  gpa?: number | null;
  gpa_max?: number | null;
  honors_awards?: string | null;
  description?: string | null;
  display_order?: number;
}

// Degree type constants
export const DegreeType = {
  HIGH_SCHOOL: 'High School',
  ASSOCIATE: 'Associate Degree',
  BACHELOR: "Bachelor's Degree",
  MASTER: "Master's Degree",
  DOCTORATE: 'Doctorate (PhD)',
  MBA: 'MBA',
  CERTIFICATE: 'Certificate',
  DIPLOMA: 'Diploma',
  OTHER: 'Other',
} as const;

// ================== SKILLS ==================

export interface Skill {
  id: number;
  user_id: number;
  skill_name: string;
  category: string | null;
  proficiency_level: string | null;
  years_of_experience: number | null;
  endorsement_count: number;
  display_order: number;
}

export interface SkillCreate {
  skill_name: string;
  category?: string | null;
  proficiency_level?: string | null;
  years_of_experience?: number | null;
  endorsement_count?: number;
  display_order?: number;
}

export interface SkillUpdate {
  skill_name?: string;
  category?: string | null;
  proficiency_level?: string | null;
  years_of_experience?: number | null;
  endorsement_count?: number;
  display_order?: number;
}

// Skill category constants
export const SkillCategory = {
  TECHNICAL: 'Technical',
  SOFT_SKILL: 'Soft Skill',
  LANGUAGE: 'Language',
  TOOL: 'Tool',
  FRAMEWORK: 'Framework',
  OTHER: 'Other',
} as const;

// Proficiency level constants
export const ProficiencyLevel = {
  BEGINNER: 'Beginner',
  INTERMEDIATE: 'Intermediate',
  ADVANCED: 'Advanced',
  EXPERT: 'Expert',
  NATIVE: 'Native', // For languages
} as const;

// ================== CERTIFICATIONS ==================

export interface Certification {
  id: number;
  user_id: number;
  certification_name: string;
  issuing_organization: string;
  issue_date: string | null;
  expiry_date: string | null;
  does_not_expire: boolean;
  credential_id: string | null;
  credential_url: string | null;
  certificate_image_url: string | null;
  description: string | null;
  display_order: number;
}

export interface CertificationCreate {
  certification_name: string;
  issuing_organization: string;
  issue_date?: string | null;
  expiry_date?: string | null;
  does_not_expire?: boolean;
  credential_id?: string | null;
  credential_url?: string | null;
  certificate_image_url?: string | null;
  description?: string | null;
  display_order?: number;
}

export interface CertificationUpdate {
  certification_name?: string;
  issuing_organization?: string;
  issue_date?: string | null;
  expiry_date?: string | null;
  does_not_expire?: boolean;
  credential_id?: string | null;
  credential_url?: string | null;
  certificate_image_url?: string | null;
  description?: string | null;
  display_order?: number;
}

// ================== PROJECTS ==================

export interface Project {
  id: number;
  user_id: number;
  project_name: string;
  description: string | null;
  role: string | null;
  technologies: string | null; // Comma-separated
  project_url: string | null;
  github_url: string | null;
  image_urls: string | null; // Comma-separated
  start_date: string | null;
  end_date: string | null;
  display_order: number;
}

export interface ProjectCreate {
  project_name: string;
  description?: string | null;
  role?: string | null;
  technologies?: string | null;
  project_url?: string | null;
  github_url?: string | null;
  image_urls?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  display_order?: number;
}

export interface ProjectUpdate {
  project_name?: string;
  description?: string | null;
  role?: string | null;
  technologies?: string | null;
  project_url?: string | null;
  github_url?: string | null;
  image_urls?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  display_order?: number;
}

// ================== JOB PREFERENCES ==================

export interface JobPreference {
  id: number;
  user_id: number;
  desired_job_types: string | null; // Comma-separated
  desired_salary_min: number | null;
  desired_salary_max: number | null;
  salary_currency: string;
  salary_period: string;
  willing_to_relocate: boolean;
  preferred_locations: string | null; // Comma-separated
  work_mode_preferences: string | null; // Comma-separated
  available_from: string | null;
  notice_period_days: number | null;
  job_search_status: string;
  preferred_industries: string | null; // Comma-separated
  preferred_company_sizes: string | null; // Comma-separated
  other_preferences: string | null;
}

export interface JobPreferenceCreate {
  desired_job_types?: string | null;
  desired_salary_min?: number | null;
  desired_salary_max?: number | null;
  salary_currency?: string;
  salary_period?: string;
  willing_to_relocate?: boolean;
  preferred_locations?: string | null;
  work_mode_preferences?: string | null;
  available_from?: string | null;
  notice_period_days?: number | null;
  job_search_status?: string;
  preferred_industries?: string | null;
  preferred_company_sizes?: string | null;
  other_preferences?: string | null;
}

export interface JobPreferenceUpdate {
  desired_job_types?: string | null;
  desired_salary_min?: number | null;
  desired_salary_max?: number | null;
  salary_currency?: string | null;
  salary_period?: string | null;
  willing_to_relocate?: boolean;
  preferred_locations?: string | null;
  work_mode_preferences?: string | null;
  available_from?: string | null;
  notice_period_days?: number | null;
  job_search_status?: string | null;
  preferred_industries?: string | null;
  preferred_company_sizes?: string | null;
  other_preferences?: string | null;
}

// Job search status constants
export const JobSearchStatus = {
  ACTIVELY_LOOKING: 'actively_looking',
  OPEN_TO_OPPORTUNITIES: 'open_to_opportunities',
  NOT_LOOKING: 'not_looking',
} as const;

// Salary period constants
export const SalaryPeriod = {
  YEARLY: 'yearly',
  MONTHLY: 'monthly',
  HOURLY: 'hourly',
} as const;

// Work mode constants
export const WorkMode = {
  REMOTE: 'Remote',
  HYBRID: 'Hybrid',
  ONSITE: 'Onsite',
} as const;

// Company size constants
export const CompanySize = {
  STARTUP: 'Startup',
  SME: 'SME',
  ENTERPRISE: 'Enterprise',
} as const;

// ================== PROFILE COMPLETENESS ==================

export interface ProfileCompleteness {
  percentage: number;
  missing_sections: string[];
  completed_sections: string[];
}

// ================== RECRUITER PROFILE ==================

export interface RecruiterProfile {
  id: number;
  user_id: number;
  years_of_experience: number | null;
  specializations: string | null; // Comma-separated (e.g., "Tech Recruitment,Executive Search")
  bio: string | null;
  company_description: string | null;
  industries: string | null; // Comma-separated
  job_types: string | null; // Comma-separated
  locations: string | null; // Comma-separated
  experience_levels: string | null; // Comma-separated
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

// Recruiter specialization constants
export const RecruiterSpecialization = {
  TECH_RECRUITMENT: 'Tech Recruitment',
  EXECUTIVE_SEARCH: 'Executive Search',
  VOLUME_HIRING: 'Volume Hiring',
  CONTRACT_STAFFING: 'Contract Staffing',
  TEMP_TO_PERM: 'Temp-to-Perm',
  HEALTHCARE: 'Healthcare Recruitment',
  FINANCE: 'Finance Recruitment',
  SALES_MARKETING: 'Sales & Marketing',
  ENGINEERING: 'Engineering',
  CUSTOMER_SERVICE: 'Customer Service',
} as const;

// Experience level constants
export const ExperienceLevel = {
  ENTRY: 'Entry Level',
  JUNIOR: 'Junior',
  MID: 'Mid Level',
  SENIOR: 'Senior',
  LEAD: 'Lead',
  MANAGER: 'Manager',
  DIRECTOR: 'Director',
  EXECUTIVE: 'Executive',
} as const;

// ================== EMPLOYER PROFILE ==================

// Employers use minimal profile info - mostly from User and Company tables
// No separate EmployerProfile model needed, just type for display

export interface EmployerProfileView {
  user_id: number;
  full_name: string;
  profile_picture_url: string | null;
  job_title: string | null;
  role_in_company: string | null;
  department: string | null;
  bio: string | null;
  email: string;
  phone: string | null;
  linkedin_url: string | null;

  // Company info (from Company table)
  company_id: number | null;
  company_name: string | null;
  company_logo_url: string | null;
  company_industry: string | null;

  // Activity stats
  jobs_posted?: number;
  active_openings?: number;
}
