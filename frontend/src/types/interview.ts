// Interview Types
export interface Interview {
  id: number;
  assignee_id: number;
  recruiter_id: number;
  employer_company_id: number;
  title: string;
  description?: string;
  status:
    | 'pending_schedule'
    | 'scheduled'
    | 'confirmed'
    | 'in_progress'
    | 'completed'
    | 'cancelled';
  interview_type: 'video' | 'phone' | 'in_person';
  scheduled_start?: string;
  scheduled_end?: string;
  scheduled_at?: string;
  timezone?: string;
  location?: string;
  meeting_url?: string;
  video_call_type?: 'system_generated' | 'custom_url';
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
  assignee: {
    id: number;
    email: string;
    full_name: string;
    role: string;
    company_name?: string;
  };
  recruiter: {
    id: number;
    email: string;
    full_name: string;
    role: string;
    company_name?: string;
  };
  employer_company_name?: string;
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

export interface AttendeeInfo {
  id: number;
  user_id: number;
  email: string;
  response_status: 'pending' | 'accepted' | 'declined';
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
  organizerName?: string;
  meetingUrl?: string;
  attendees: string[] | AttendeeInfo[];
  status?: string;
  type?: string;
  createdAt: string;
  updatedAt: string;
}

// Interview List Response Types
export interface InterviewsListResponse<T = Interview> {
  interviews: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Page-specific Interview interface for simplified display
export interface InterviewListItem {
  id: number;
  title: string;
  assignee_name: string;
  recruiter_name: string;
  company_name: string;
  scheduled_date: string;
  start_time: string;
  end_time: string;
  location: string;
  type: 'phone' | 'video' | 'in_person';
  status: 'scheduled' | 'completed' | 'cancelled' | 'rescheduled' | 'in_progress';
  notes?: string;
  created_at: string;
  created_by?: number;
}

// Filter and sort types for interview pages
export type InterviewStatusFilter = 'all' | InterviewListItem['status'];
export type InterviewTypeFilter = 'all' | InterviewListItem['type'];
export type InterviewSortField = 'scheduled_date' | 'assignee_name' | 'status';

// Form data types for interview creation and editing
export interface InterviewFormData {
  title: string;
  description: string;
  assignee_id: string;
  interview_type: 'video' | 'phone' | 'in_person';
  scheduled_start: string;
  scheduled_end: string;
  timezone: string;
  location: string;
  meeting_url: string;
  video_call_type: 'system_generated' | 'custom_url';
  notes: string;
  preparation_notes: string;
}

export interface InterviewEditFormData {
  title: string;
  description: string;
  interview_type: 'video' | 'phone' | 'in_person';
  scheduled_start: string;
  scheduled_end: string;
  timezone: string;
  location: string;
  meeting_url: string;
  notes: string;
  preparation_notes: string;
  status: Interview['status'];
}
