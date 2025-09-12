// Resume Types
export interface Resume {
  id: number;
  user_id: number;
  title: string;
  description?: string;
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  website?: string;
  linkedin_url?: string;
  github_url?: string;
  professional_summary?: string;
  objective?: string;
  status: 'draft' | 'published' | 'archived';
  visibility: 'private' | 'public' | 'unlisted';
  template_id: string;
  theme_color: string;
  font_family: string;
  custom_css?: string;
  is_primary: boolean;
  is_public: boolean;
  view_count: number;
  download_count: number;
  last_viewed_at?: string;
  slug: string;
  share_token: string;
  created_at: string;
  updated_at: string;
  sections: ResumeSection[];
  experiences: WorkExperience[];
  educations: Education[];
  skills: Skill[];
  projects: Project[];
  certifications: Certification[];
  languages: Language[];
  references: Reference[];
}

export interface ResumeSection {
  id: number;
  resumeId: number;
  sectionType: 'summary' | 'experience' | 'education' | 'skills' | 'projects' | 'certifications' | 'languages' | 'references' | 'custom';
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
}