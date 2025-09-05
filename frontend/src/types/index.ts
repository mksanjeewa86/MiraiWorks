// User and Authentication Types
export interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  fullName: string;
  phone?: string;
  companyId: number;
  isActive: boolean;
  isAdmin: boolean;
  require2fa: boolean;
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
  roles: UserRole[];
  company: Company;
}

export interface UserRole {
  id: number;
  userId: number;
  roleId: number;
  assignedAt: string;
  assignedBy: number;
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

export interface Company {
  id: number;
  name: string;
  domain: string;
  industry?: string;
  size?: string;
  description?: string;
  website?: string;
  logo?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

// Authentication Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  phone?: string;
  companyName: string;
  companyDomain: string;
  industry?: string;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export interface TwoFactorRequest {
  code: string;
}

// Message Types
export interface Message {
  id: number;
  conversationId: number;
  senderId: number;
  content: string;
  messageType: 'text' | 'file' | 'system';
  attachmentId?: number;
  isRead: boolean;
  createdAt: string;
  updatedAt: string;
  sender: User;
  attachment?: MessageAttachment;
}

export interface MessageAttachment {
  id: number;
  filename: string;
  originalName: string;
  mimeType: string;
  size: number;
  virusStatus: 'pending' | 'clean' | 'infected' | 'error';
  uploadedAt: string;
}

export interface Conversation {
  id: number;
  title?: string;
  isGroup: boolean;
  createdBy: number;
  lastMessageAt?: string;
  createdAt: string;
  participants: ConversationParticipant[];
  lastMessage?: Message;
  unreadCount: number;
}

export interface ConversationParticipant {
  id: number;
  conversationId: number;
  userId: number;
  joinedAt: string;
  lastReadAt?: string;
  user: User;
}

// Interview Types
export interface Interview {
  id: number;
  candidateId: number;
  recruiterId: number;
  employerCompanyId: number;
  title: string;
  description?: string;
  positionTitle?: string;
  status: 'pending_schedule' | 'scheduled' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled';
  interviewType: 'video' | 'phone' | 'in_person';
  scheduledStart?: string;
  scheduledEnd?: string;
  timezone?: string;
  location?: string;
  meetingUrl?: string;
  durationMinutes?: number;
  notes?: string;
  preparationNotes?: string;
  createdBy?: number;
  confirmedBy?: number;
  confirmedAt?: string;
  cancelledBy?: number;
  cancelledAt?: string;
  cancellationReason?: string;
  createdAt: string;
  updatedAt: string;
  candidate: User;
  recruiter: User;
  employerCompanyName: string;
  proposals: InterviewProposal[];
  activeProposalCount: number;
}

export interface InterviewProposal {
  id: number;
  interviewId: number;
  proposedBy: number;
  proposerName: string;
  proposerRole: string;
  startDatetime: string;
  endDatetime: string;
  timezone: string;
  location?: string;
  notes?: string;
  status: 'pending' | 'accepted' | 'declined' | 'expired';
  respondedBy?: number;
  responderName?: string;
  respondedAt?: string;
  responseNotes?: string;
  expiresAt?: string;
  createdAt: string;
}

// Calendar Types
export interface CalendarIntegration {
  id: number;
  provider: 'google' | 'microsoft';
  email: string;
  displayName?: string;
  calendarId?: string;
  calendarTimezone?: string;
  isActive: boolean;
  syncEnabled: boolean;
  lastSyncAt?: string;
  createdAt: string;
}

export interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  location?: string;
  startDatetime: string;
  endDatetime: string;
  timezone?: string;
  isAllDay: boolean;
  isRecurring: boolean;
  organizerEmail?: string;
  attendees: string[];
  status?: string;
  createdAt: string;
  updatedAt: string;
}

// Resume Types
export interface Resume {
  id: number;
  userId: number;
  title: string;
  description?: string;
  fullName?: string;
  email?: string;
  phone?: string;
  location?: string;
  website?: string;
  linkedinUrl?: string;
  githubUrl?: string;
  professionalSummary?: string;
  objective?: string;
  status: 'draft' | 'published' | 'archived';
  visibility: 'private' | 'public' | 'unlisted';
  templateId: string;
  themeColor: string;
  fontFamily: string;
  customCss?: string;
  isPrimary: boolean;
  viewCount: number;
  downloadCount: number;
  lastViewedAt?: string;
  slug: string;
  shareToken: string;
  createdAt: string;
  updatedAt: string;
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

// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  success: boolean;
  errors?: string[];
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

// Form Types
export interface FormError {
  field: string;
  message: string;
}

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

// Notification Types
export interface Notification {
  id: number;
  userId: number;
  type: string;
  title: string;
  message: string;
  data?: Record<string, any>;
  isRead: boolean;
  createdAt: string;
}

// WebSocket Types
export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: string;
}

// Dashboard Types
export interface DashboardStats {
  totalUsers?: number;
  totalCompanies?: number;
  totalInterviews?: number;
  totalResumes?: number;
  activeConversations?: number;
  recentActivity?: any[];
}

export interface ActivityItem {
  id: string;
  type: 'interview' | 'message' | 'resume' | 'user' | 'company';
  title: string;
  description: string;
  timestamp: string;
  userId?: number;
  metadata?: Record<string, any>;
}