// User and Authentication Types
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  phone?: string;
  company_id: number;
  is_active: boolean;
  is_admin: boolean;
  require_2fa: boolean;
  last_login?: string;
  created_at: string;
  updated_at: string;
  roles: UserRole[];
  company: Company;
}

export interface UserRole {
  id: number;
  user_id: number;
  role_id: number;
  assigned_at: string;
  assigned_by: number;
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
  is_active: boolean;
  created_at: string;
  updated_at: string;
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
  applicant: User;
}

// Authentication Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  company_name: string;
  company_domain: string;
  industry?: string;
}

export interface AuthResponse {
  user?: User;
  access_token: string;
  refresh_token: string;
  expires_in: number;
  require_2fa?: boolean;
}

export interface TwoFactorRequest {
  user_id?: number;
  code: string;
}

// Message Types
export interface Message {
  id: number;
  conversation_id: number;
  sender_id: number;
  content: string;
  message_type: 'text' | 'file' | 'system';
  attachment_id?: number;
  is_read: boolean;
  created_at: string;
  updated_at: string;
  sender: User;
  attachment?: MessageAttachment;
  read_by?: User[];
}

export interface MessageAttachment {
  id: number;
  filename: string;
  original_name: string;
  mime_type: string;
  size: number;
  virus_status: 'pending' | 'clean' | 'infected' | 'error';
  uploaded_at: string;
}

export interface Conversation {
  id: number;
  title?: string;
  is_group: boolean;
  created_by: number;
  last_message_at?: string;
  created_at: string;
  participants: ConversationParticipant[];
  last_message?: Message;
  unread_count: number;
}

export interface ConversationParticipant {
  id: number;
  conversation_id: number;
  user_id: number;
  joined_at: string;
  last_read_at?: string;
  user: User;
}

// Interview Types
export interface Interview {
  id: number;
  candidate_id: number;
  recruiter_id: number;
  employer_company_id: number;
  title: string;
  description?: string;
  position_title?: string;
  status: 'pending_schedule' | 'scheduled' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled';
  interview_type: 'video' | 'phone' | 'in_person';
  scheduled_start?: string;
  scheduled_end?: string;
  scheduled_at?: string;
  timezone?: string;
  location?: string;
  meeting_url?: string;
  duration_minutes?: number;
  notes?: string;
  preparation_notes?: string;
  created_by?: number;
  confirmed_by?: number;
  confirmed_at?: string;
  cancelled_by?: number;
  cancelled_at?: string;
  cancellation_reason?: string;
  created_at: string;
  updated_at: string;
  candidate: User;
  recruiter: User;
  candidate_name?: string;
  company_name?: string;
  proposals: InterviewProposal[];
  active_proposal_count: number;
}

export interface InterviewProposal {
  id: number;
  interview_id: number;
  proposed_by: number;
  proposer_name: string;
  proposer_role: string;
  start_datetime: string;
  end_datetime: string;
  timezone: string;
  location?: string;
  notes?: string;
  status: 'pending' | 'accepted' | 'declined' | 'expired';
  responded_by?: number;
  responder_name?: string;
  responded_at?: string;
  response_notes?: string;
  expires_at?: string;
  created_at: string;
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

// API Response Types
export interface ApiResponse<T = unknown> {
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
  data?: Record<string, unknown>;
  isRead: boolean;
  createdAt: string;
}

// WebSocket Types
export interface WebSocketMessage {
  type: string;
  payload: unknown;
  timestamp: string;
}

// Meeting Types
export const MeetingType = {
  CASUAL: 'casual' as const,
  MAIN: 'main' as const
} as const;

export type MeetingTypeValue = typeof MeetingType[keyof typeof MeetingType];

export const MeetingStatus = {
  SCHEDULED: 'scheduled' as const,
  STARTING: 'starting' as const, 
  IN_PROGRESS: 'in_progress' as const,
  COMPLETED: 'completed' as const,
  CANCELLED: 'cancelled' as const,
  FAILED: 'failed' as const
} as const;

export type MeetingStatusValue = typeof MeetingStatus[keyof typeof MeetingStatus];

export const ParticipantRole = {
  HOST: 'host' as const,
  PARTICIPANT: 'participant' as const,
  OBSERVER: 'observer' as const
} as const;

export type ParticipantRoleValue = typeof ParticipantRole[keyof typeof ParticipantRole];

export const ParticipantStatus = {
  INVITED: 'invited' as const,
  JOINED: 'joined' as const,
  LEFT: 'left' as const,
  DISCONNECTED: 'disconnected' as const
} as const;

export type ParticipantStatusValue = typeof ParticipantStatus[keyof typeof ParticipantStatus];

export interface MeetingParticipant {
  id: number;
  meeting_id: number;
  user_id: number;
  role: ParticipantRoleValue;
  status: ParticipantStatusValue;
  joined_at?: string;
  left_at?: string;
  can_record: boolean;
  recording_consent?: boolean;
  created_at: string;
  updated_at: string;
  user?: User;
}

export interface Meeting {
  id: number;
  interview_id?: number;
  title: string;
  description?: string;
  meeting_type: MeetingTypeValue;
  status: MeetingStatusValue;
  room_id: string;
  access_code?: string;
  scheduled_start: string;
  scheduled_end: string;
  actual_start?: string;
  actual_end?: string;
  recording_enabled: boolean;
  recording_status: string;
  recording_consent_required: boolean;
  transcription_enabled: boolean;
  auto_summary: boolean;
  company_id: number;
  created_by: number;
  created_at: string;
  updated_at: string;
  duration_minutes?: number;
  is_active: boolean;
  can_join: boolean;
  participants: MeetingParticipant[];
  recordings: MeetingRecording[];
  transcripts: MeetingTranscript[];
  summaries: MeetingSummary[];
}

export interface MeetingRecording {
  id: number;
  meeting_id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  duration_seconds?: number;
  storage_path: string;
  mime_type: string;
  status: string;
  processing_started_at?: string;
  processing_completed_at?: string;
  processing_error?: string;
  is_public: boolean;
  access_expires_at?: string;
  recorded_by: number;
  created_at: string;
  updated_at: string;
  download_url?: string;
}

export interface MeetingTranscript {
  id: number;
  meeting_id: number;
  recording_id?: number;
  transcript_text: string;
  transcript_json?: string;
  language: string;
  confidence_score?: number;
  stt_service: string;
  processing_duration_seconds?: number;
  word_count?: number;
  speaker_count?: number;
  speakers_identified: boolean;
  status: string;
  processing_error?: string;
  created_at: string;
  updated_at: string;
}

export interface MeetingSummary {
  id: number;
  meeting_id: number;
  transcript_id?: number;
  summary_text: string;
  key_points?: string;
  action_items?: string;
  sentiment_analysis?: string;
  ai_model: string;
  prompt_version: string;
  generation_duration_seconds?: number;
  confidence_score?: number;
  summary_length_words?: number;
  compression_ratio?: number;
  status: string;
  processing_error?: string;
  is_final: boolean;
  reviewed_by?: number;
  reviewed_at?: string;
  created_at: string;
  updated_at: string;
}

// WebRTC Types
export interface RTCIceServer {
  urls: string | string[];
  username?: string;
  credential?: string;
}

export interface WebRTCSignal {
  type: string;
  data: unknown;
  target_user_id?: number;
  sender_id?: number;
  room_id: string;
}

export interface MeetingJoinResponse {
  success: boolean;
  room_id: string;
  participant_id: number;
  meeting: Meeting;
  turn_servers: RTCIceServer[];
  error?: string;
}

// Dashboard Types
export interface DashboardStats {
  totalUsers?: number;
  totalCompanies?: number;
  totalInterviews?: number;
  totalResumes?: number;
  activeConversations?: number;
  recentActivity?: ActivityItem[];
}

export interface ActivityItem {
  id: string;
  type: 'interview' | 'message' | 'resume' | 'user' | 'company';
  title: string;
  description: string;
  timestamp: string;
  userId?: number;
  metadata?: Record<string, unknown>;
}