// Resume Builder Types
// Enhanced with Japanese formats and sharing features

// ============================================================================
// ENUMS AND CONSTANTS
// ============================================================================

export enum ResumeStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
}

export enum ResumeVisibility {
  PRIVATE = 'private',
  PUBLIC = 'public',
  UNLISTED = 'unlisted',
}

export enum ResumeFormat {
  RIREKISHO = 'rirekisho', // Rirekisho (traditional Japanese resume)
  SHOKUMU_KEIREKISHO = 'shokumu_keirekisho', // Shokumu keirekisho (career history resume)
  INTERNATIONAL = 'international', // Standard international resume
  MODERN = 'modern', // Modern format
  CREATIVE = 'creative', // Creative format
}

export enum ResumeLanguage {
  JAPANESE = 'ja',
  ENGLISH = 'en',
  BILINGUAL = 'bilingual',
}

export enum SectionType {
  SUMMARY = 'summary',
  EXPERIENCE = 'experience',
  EDUCATION = 'education',
  SKILLS = 'skills',
  PROJECTS = 'projects',
  CERTIFICATIONS = 'certifications',
  LANGUAGES = 'languages',
  REFERENCES = 'references',
  CUSTOM = 'custom',
}

// ============================================================================
// CORE RESUME INTERFACES
// ============================================================================

export interface Resume {
  id: number;
  user_id: number;

  // Basic info
  title: string;
  description?: string;

  // Personal information
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  website?: string;
  linkedin_url?: string;
  github_url?: string;

  // Professional summary
  professional_summary?: string;
  objective?: string;

  // Template and styling
  template_id: string;
  resume_format: ResumeFormat;
  resume_language: ResumeLanguage;
  theme_color: string;
  font_family: string;
  custom_css?: string;

  // Japanese-specific fields
  furigana_name?: string;
  birth_date?: string;
  gender?: string;
  nationality?: string;
  marital_status?: string;
  emergency_contact?: Record<string, any>;
  photo_path?: string;

  // Status and visibility
  status: ResumeStatus;
  visibility: ResumeVisibility;
  is_primary: boolean;

  // Enhanced sharing and public access
  is_public: boolean;
  public_url_slug?: string;
  share_token: string;
  can_download_pdf: boolean;
  can_edit: boolean;
  can_delete: boolean;

  // Metadata
  view_count: number;
  download_count: number;
  last_viewed_at?: string;

  // File attachments
  pdf_file_path?: string;
  pdf_generated_at?: string;

  // Timestamps
  created_at: string;
  updated_at: string;

  // Related data
  sections?: ResumeSection[];
  experiences?: WorkExperience[];
  educations?: Education[];
  skills?: Skill[];
  projects?: Project[];
  certifications?: Certification[];
  languages?: Language[];
  references?: Reference[];
}

export interface ResumeSection {
  id: number;
  resumeId: number;
  sectionType:
    | 'summary'
    | 'experience'
    | 'education'
    | 'skills'
    | 'projects'
    | 'certifications'
    | 'languages'
    | 'references'
    | 'custom';
  title: string;
  content?: string;
  isVisible: boolean;
  displayOrder: number;
  customCss?: string;
  createdAt: string;
  updatedAt: string;
}

export interface WorkExperience {
  id: number;
  resumeId: number;
  companyName: string;
  positionTitle: string;
  location?: string;
  companyWebsite?: string;
  startDate: string;
  endDate?: string;
  isCurrent: boolean;
  description?: string;
  achievements: string[];
  technologies: string[];
  isVisible: boolean;
  displayOrder: number;
  createdAt: string;
  updatedAt: string;
}

export interface Education {
  id: number;
  resumeId: number;
  institutionName: string;
  degree: string;
  fieldOfStudy?: string;
  location?: string;
  startDate: string;
  endDate?: string;
  isCurrent: boolean;
  gpa?: string;
  honors?: string;
  description?: string;
  courses: string[];
  isVisible: boolean;
  displayOrder: number;
  createdAt: string;
  updatedAt: string;
}

export interface Skill {
  id: number;
  resumeId: number;
  name: string;
  category?: string;
  proficiencyLevel?: number;
  proficiencyLabel?: string;
  isVisible: boolean;
  displayOrder: number;
  createdAt: string;
}

export interface Project {
  id: number;
  resumeId: number;
  name: string;
  description: string;
  projectUrl?: string;
  githubUrl?: string;
  demoUrl?: string;
  startDate?: string;
  endDate?: string;
  isOngoing: boolean;
  technologies: string[];
  role?: string;
  isVisible: boolean;
  displayOrder: number;
  createdAt: string;
  updatedAt: string;
}

export interface Certification {
  id: number;
  resumeId: number;
  name: string;
  issuingOrganization: string;
  credentialId?: string;
  credentialUrl?: string;
  issueDate: string;
  expirationDate?: string;
  doesNotExpire: boolean;
  description?: string;
  isVisible: boolean;
  displayOrder: number;
  createdAt: string;
}

export interface Language {
  id: number;
  resumeId: number;
  name: string;
  proficiency: string;
  isVisible: boolean;
  displayOrder: number;
  createdAt: string;
}

export interface Reference {
  id: number;
  resumeId: number;
  fullName: string;
  positionTitle?: string;
  companyName?: string;
  email?: string;
  phone?: string;
  relationship?: string;
  isVisible: boolean;
  displayOrder: number;
  createdAt: string;
  updatedAt: string;
}

export interface ResumeTemplate {
  id: number;
  name: string;
  displayName: string;
  description?: string;
  category?: string;
  colorScheme: Record<string, string>;
  fontOptions: Record<string, string>;
  isPremium: boolean;
  usageCount: number;
  previewImageUrl?: string;
  supportsFormats: ResumeFormat[];
}

// ============================================================================
// JAPANESE RESUME SPECIFIC INTERFACES
// ============================================================================

export interface RirekishoData {
  personal_info: {
    full_name: string;
    furigana_name: string;
    birth_date: string;
    gender: string;
    nationality?: string;
    marital_status?: string;
    photo?: File | string;
    address: string;
    phone: string;
    email: string;
    emergency_contact?: Record<string, any>;
  };
  education_history: Array<{
    school_name: string;
    department?: string;
    entrance_date: string;
    graduation_date?: string;
    status: 'graduated' | 'enrolled' | 'withdrawn';
  }>;
  work_history: Array<{
    company_name: string;
    position: string;
    start_date: string;
    end_date?: string;
    employment_type: 'full_time' | 'contract' | 'part_time' | 'dispatch';
  }>;
  qualifications: Array<{
    name: string;
    issue_date: string;
    issuing_organization: string;
  }>;
  motivation?: string;
  commute_time?: string;
  spouse?: 'yes' | 'no';
  dependents?: string;
}

export interface ShokumuKeirekishoData {
  career_summary: string;
  detailed_experience: Array<{
    company_name: string;
    period: string;
    position: string;
    job_description: string;
    achievements: string[];
    technologies?: string[];
  }>;
  skills_and_expertise: {
    technical_skills: string[];
    soft_skills: string[];
    languages: Array<{
      name: string;
      level: string;
    }>;
    certifications: string[];
  };
  achievements: string[];
  self_pr: string;
}

export interface JapaneseResumeTemplate {
  format_type: ResumeFormat;
  sections: string[];
  field_mappings: Record<string, string[]>;
  validation_rules: Record<string, any>;
}

// ============================================================================
// PUBLIC SHARING INTERFACES
// ============================================================================

export interface PublicResumeInfo {
  id: number;
  title: string;
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  professional_summary?: string;
  resume_format?: ResumeFormat;
  resume_language?: ResumeLanguage;
  view_count?: number;
  last_viewed_at?: string;
  can_download_pdf?: boolean;
  created_at?: string;
  updated_at?: string;

  // Limited related data
  experiences?: WorkExperience[];
  work_experiences?: WorkExperience[];
  educations?: Education[];
  skills?: Skill[];
}

export interface ResumePublicSettings {
  is_public: boolean;
  custom_slug?: string;
  show_contact_info: boolean;
  allow_pdf_download: boolean;
  password_protect: boolean;
  password?: string;
}

// ============================================================================
// EMAIL AND MESSAGING INTERFACES
// ============================================================================

export interface EmailResumeRequest {
  recipient_emails: string[];
  subject?: string;
  message?: string;
  include_pdf: boolean;
  sender_name?: string;
}

export interface MessageAttachmentRequest {
  message_id: number;
  include_pdf: boolean;
  auto_attach: boolean;
}

export interface ResumeMessageAttachment {
  id: number;
  resume_id: number;
  message_id: number;
  auto_attached: boolean;
  attachment_format: string;
  created_at: string;
}

// ============================================================================
// PDF AND EXPORT INTERFACES
// ============================================================================

export interface PDFGenerationRequest {
  resume_id: number;
  format: 'A4' | 'Letter';
  include_contact_info: boolean;
  watermark?: string;
}

export interface PDFGenerationResponse {
  pdf_url: string;
  expires_at: string;
  file_size: number;
}

// ============================================================================
// API RESPONSE INTERFACES
// ============================================================================

export interface ResumeListResponse {
  resumes: Resume[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface ResumeStats {
  total_resumes: number;
  by_status: Record<string, number>;
  by_visibility: Record<string, number>;
  total_views: number;
  total_downloads: number;
  most_viewed_resume?: string;
  recent_activity: number;
}

// ============================================================================
// FORM DATA INTERFACES
// ============================================================================

export interface WorkExperienceFormData {
  company_name: string;
  position_title: string;
  location?: string;
  company_website?: string;
  start_date: string;
  end_date?: string;
  is_current: boolean;
  description?: string;
  achievements: string[];
  technologies: string[];
}

export interface EducationFormData {
  institution_name: string;
  degree: string;
  field_of_study?: string;
  location?: string;
  start_date: string;
  end_date?: string;
  is_current: boolean;
  gpa?: string;
  honors?: string;
  description?: string;
  courses: string[];
}

// ============================================================================
// COMPONENT PROP INTERFACES
// ============================================================================

export interface ResumeBuilderProps {
  resume?: Resume;
  onSave: (resume: Resume) => void;
  onCancel: () => void;
  mode: 'create' | 'edit';
}

export interface ResumeTemplatePreviewProps {
  resume: Resume;
  template?: string;
  format?: ResumeFormat;
  showEditControls?: boolean;
}

export interface ResumePublicViewProps {
  slug: string;
  allowDownload?: boolean;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type ResumeStatusType = keyof typeof ResumeStatus;
export type ResumeVisibilityType = keyof typeof ResumeVisibility;
export type ResumeFormatType = keyof typeof ResumeFormat;
export type ResumeLanguageType = keyof typeof ResumeLanguage;
export type SectionTypeType = keyof typeof SectionType;

// Form validation types
export type ResumeFormStep =
  | 'basic_info'
  | 'personal_details'
  | 'experience'
  | 'education'
  | 'skills'
  | 'projects'
  | 'certifications'
  | 'languages'
  | 'template_settings'
  | 'preview';

// Bulk operations
export interface BulkResumeAction {
  action: 'delete' | 'archive' | 'publish' | 'make_private' | 'make_public';
  resume_ids: number[];
}

export interface BulkActionResult {
  success_count: number;
  error_count: number;
  errors: string[];
}


// ============================================================================
// RESUME FORMS & EXTENSIONS
// ============================================================================

// Resume Form Data (from app/resumes/create/page.tsx)
export interface ResumeFormData {
  title: string;
  description: string;
  last_name: string;
  first_name: string;
  furigana_last_name?: string;
  furigana_first_name?: string;
  email: string;
  phone: string;
  postal_code: string;
  prefecture: string;
  city: string;
  address_line: string;
  website?: string;
  linkedin_url?: string;
  github_url?: string;
  professional_summary?: string;
  objective?: string;
  work_experiences: WorkExperience[];
  educations: Education[];
  skills: string[];
  template_id?: string;
  resume_format?: ResumeFormat;
  resume_language?: ResumeLanguage;
  birth_date?: string;
  gender?: string;
  nationality?: string;
  marital_status?: string;
}

// Extended Resume (from app/resumes/[id]/edit/page.tsx)
export interface ExtendedResume extends Resume {
  work_experiences?: WorkExperience[];
  educations?: Education[];
}

// Duplicate removed - using PublicResumeInfo from line 349
