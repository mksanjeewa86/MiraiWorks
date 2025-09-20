export interface Candidate {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  location?: string;
  title?: string;
  company?: string;
  experience_years?: number;
  skills: string[];
  status: 'active' | 'interviewing' | 'hired' | 'rejected' | 'withdrawn';
  rating?: number;
  source: 'website' | 'referral' | 'linkedin' | 'agency' | 'event' | 'other';
  applied_positions: number;
  last_activity: string;
  resume_url?: string;
  notes?: string;
  created_at: string;
}

export type CandidateStatus = Candidate['status'];
export type CandidateSource = Candidate['source'];

export interface CandidateFilters {
  search: string;
  status: 'all' | CandidateStatus;
  source: 'all' | CandidateSource;
  experience: 'all' | 'entry' | 'mid' | 'senior';
}

export interface CandidateListResponse {
  candidates: Candidate[];
  total: number;
  page: number;
  pages: number;
}