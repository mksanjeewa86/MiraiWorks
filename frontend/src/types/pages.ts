import type { Resume, CalendarEvent, UserProfile, UserSettings, Conversation, LegacyMessage as Message, DirectMessageInfo, CompanyType } from '@/types';

// ====================
// PAGE INFO & METADATA
// ====================

export interface PageInfo {
  title: string;
  description: string;
}

// ====================
// SETTINGS PAGE STATE
// ====================

export interface SettingsState {
  activeSection: 'account' | 'security' | 'notifications' | 'preferences' | 'calendar';
  loading: boolean;
  autoSaving: boolean;
  passwordSaving: boolean;
  error: string | null;
  profile: UserProfile | null;
  settings: UserSettings | null;
  security: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  };
}

// ====================
// MESSAGES PAGE STATE
// ====================

export interface MessagesPageState {
  conversations: Conversation[];
  activeConversationId: number | null;
  messages: Message[];
  loading: boolean;
  error: string | null;
  sending: boolean;
  conversationSearchQuery: string;
  activeTab: 'conversations' | 'contacts';
  contacts: Array<{
    id: number;
    email: string;
    full_name: string;
    company_name?: string;
  }>;
  searchingContacts: boolean;
  hasMoreMessages: boolean;
  searchResults: DirectMessageInfo[];
  isSearching: boolean;
  showSearchResults: boolean;
  showProfileModal: boolean;
  selectedContactProfile: {
    id: number;
    email: string;
    full_name: string;
    company_name?: string;
  } | null;
}

// ====================
// PROFILE PAGE DATA
// ====================

export interface ProfileData {
  personal_info: {
    full_name: string;
    email: string;
    phone: string;
    location: string;
    bio: string;
    avatar_url?: string;
    website?: string;
    linkedin?: string;
    github?: string;
  };
  professional_info: {
    current_title: string;
    current_company: string;
    experience_years: number;
    industry: string;
    specializations: string[];
  };
  education: Array<{
    institution: string;
    degree: string;
    field: string;
    year: string;
    gpa?: string;
  }>;
  experience: Array<{
    company: string;
    position: string;
    duration: string;
    description: string;
    current: boolean;
  }>;
  skills: {
    technical: string[];
    soft: string[];
    languages: Array<{
      name: string;
      proficiency: string;
    }>;
  };
  certifications: Array<{
    name: string;
    issuer: string;
    date: string;
    expiry?: string;
  }>;
  achievements: Array<{
    title: string;
    description: string;
    date: string;
    type: string;
  }>;
  stats: {
    profile_views: number;
    connections: number;
    endorsements: number;
    applications_sent: number;
    interviews_completed: number;
  };
}

// ====================
// RESUME BUILDER STATE
// ====================

export interface ResumeBuilderState {
  activeSection: 'template' | 'personal' | 'experience' | 'education' | 'skills' | 'certifications' | 'projects' | 'languages' | 'preview';
  resume: Partial<Resume>;
  saving: boolean;
  errors: Record<string, string>;
}

// ====================
// CALENDAR PAGE STATE
// ====================

export interface CalendarState {
  currentDate: Date;
  events: CalendarEvent[];
  loading: boolean;
  error: string;
  selectedDate: Date | null;
  viewMode: 'month' | 'week' | 'day';
}

// ====================
// COMPANIES PAGE FORM DATA
// ====================

export interface CompanyFormData {
  name: string;
  domain: string;
  type: CompanyType;
  email: string;
  phone: string;
  website: string;
  address: string;
  description: string;
}