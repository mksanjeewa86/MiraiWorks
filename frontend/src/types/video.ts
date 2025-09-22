export interface VideoCall {
  id: number;
  job_id?: number;
  interview_id?: number;
  interviewer_id: number;
  candidate_id: number;
  scheduled_at: string;
  started_at?: string;
  ended_at?: string;
  status: VideoCallStatus;
  room_id: string;
  recording_url?: string;
  transcription_enabled: boolean;
  transcription_language: string;
  created_at: string;
  updated_at: string;
}

export type VideoCallStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled';

export type ConnectionQuality = 'excellent' | 'good' | 'fair' | 'poor';

export type TranscriptionStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface VideoCallToken {
  room_id: string;
  token: string;
  expires_at: string;
}

export interface TranscriptionSegment {
  id: number;
  video_call_id: number;
  speaker_id: number;
  speaker_name?: string;
  segment_text: string;
  start_time: number;
  end_time: number;
  confidence?: number;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  senderId: number;
  senderName: string;
  message: string;
  timestamp: Date;
  type: 'text' | 'link' | 'code' | 'file';
}

export interface RecordingConsent {
  id: number;
  video_call_id: number;
  user_id: number;
  consented: boolean;
  consented_at?: string;
}

export interface CallParticipant {
  id: number;
  video_call_id: number;
  user_id: number;
  joined_at?: string;
  left_at?: string;
  connection_quality?: ConnectionQuality;
  device_info?: Record<string, unknown>;
}

export interface WebRTCState {
  localStream: MediaStream | null;
  remoteStream: MediaStream | null;
  isConnected: boolean;
  connectionQuality: ConnectionQuality;
  isMuted: boolean;
  isVideoOn: boolean;
  isScreenSharing: boolean;
}

export interface TranscriptionState {
  segments: TranscriptionSegment[];
  isTranscribing: boolean;
  language: string;
  searchQuery: string;
  highlightedSegments: number[];
}