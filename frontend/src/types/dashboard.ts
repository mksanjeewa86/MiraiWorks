// Dashboard Types
export interface RecentInterview {
  id: string;
  title: string;
  company_name: string;
  scheduled_at: string;
  status: string;
}

export interface RecentResume {
  id: string;
  title: string;
  updated_at: string;
  status: string;
  is_public: boolean;
}

export interface TopCandidate {
  id: string;
  name: string;
  email: string;
  score: number;
}

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

// Role-specific Dashboard Stats
export interface CandidateStats {
  activeApplications: number;
  upcomingInterviews: number;
  unreadMessages: number;
  resumeCompleteness: number;
  totalApplications: number;
  interviewsCompleted: number;
  offersReceived: number;
}

export interface CandidateDashboardStats extends DashboardStats {
  total_applications: number;
  interviews_scheduled: number;
  interviews_completed: number;
  resumes_created: number;
  recent_interviews: RecentInterview[];
  recent_resumes: RecentResume[];
  application_stats: {
    status: string;
    count: number;
  }[];
}

export interface RecruiterStats extends DashboardStats {
  active_candidates: number;
  interviews_this_week: number;
  pending_proposals: number;
  placement_rate: number;
  recent_interviews: RecentInterview[];
  top_candidates: TopCandidate[];
  interview_pipeline: {
    stage: string;
    count: number;
    conversion_rate: number;
  }[];
}

export interface EmployerStats extends DashboardStats {
  open_positions: number;
  applications_received: number;
  interviews_scheduled: number;
  hires_made: number;
}

export interface CompanyAdminStats {
  total_employees: number;
  active_employees: number;
  pending_employees: number;
  total_positions: number;
  active_positions: number;
  total_applications: number;
  interviews_scheduled: number;
  total_recruiters: number;
  recent_activities: {
    id: string;
    type: string;
    description: string;
    timestamp: string;
    user_name: string;
  }[];
}

export interface SuperAdminStats {
  total_companies: number;
  active_companies: number;
  total_users: number;
  active_users: number;
  total_positions: number;
  total_applications: number;
  platform_metrics: {
    daily_signups: number;
    weekly_signups: number;
    monthly_signups: number;
    monthly_active_users: number;
    conversion_rate: number;
    system_uptime: number;
  };
  system_health: {
    database_status: 'healthy' | 'warning' | 'error';
    api_response_time: number;
    active_sessions: number;
    error_rate: number;
  };
  recent_system_logs: {
    id: string;
    level: 'info' | 'warning' | 'error';
    message: string;
    source: string;
    timestamp: string;
  }[];
}

// Activity and Application Types
export interface ApplicationActivity {
  name: string;
  applications: number;
  interviews: number;
}

export interface RecentActivity {
  id: number;
  type: 'application' | 'interview' | 'message' | 'offer';
  title: string;
  description: string;
  time: string;
  status?: 'pending' | 'completed' | 'scheduled';
}
