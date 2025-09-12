import type { User } from './auth';

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