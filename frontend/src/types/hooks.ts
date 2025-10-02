// Hook-related interfaces and types

// Video Call Hook Types
export interface UseVideoCallResult {
  videoCall: any | null;
  loading: boolean;
  error: string | null;
  joinCall: () => Promise<void>;
  endCall: () => Promise<{ message: string; call_ended: boolean } | undefined>;
  recordConsent: (consented: boolean) => Promise<void>;
  refreshCall: () => Promise<void>;
}

export interface UseVideoCallOptions {
  type?: 'id' | 'roomCode';
}

export interface UseWebRTCResult {
  localStream: MediaStream | null;
  remoteStream: MediaStream | null;
  isConnected: boolean;
  connectionQuality: 'excellent' | 'good' | 'fair' | 'poor';
  isMuted: boolean;
  isVideoOn: boolean;
  isScreenSharing: boolean;
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  toggleAudio: () => void;
  toggleVideo: () => void;
  startScreenShare: () => Promise<void>;
  stopScreenShare: () => void;
}

// Interview Note Hook (from hooks/useInterviewNote.ts)
export interface UseInterviewNoteResult {
  note: any | null;
  loading: boolean;
  error: string | null;
  updateNote: (content: string) => Promise<void>;
  deleteNote: () => Promise<void>;
  refreshNote: () => Promise<void>;
}

// Transcription Hook (from hooks/useTranscription.ts)
export interface UseTranscriptionResult {
  segments: any[];
  isTranscribing: boolean;
  language: string;
  searchQuery: string;
  highlightedSegments: number[];
  setTranscriptionLanguage: (language: string) => void;
  startTranscription: () => Promise<void>;
  stopTranscription: () => Promise<void>;
  addSegment: (segment: any) => void;
  searchTranscript: (query: string) => void;
  exportTranscript: (format: 'txt' | 'pdf' | 'srt') => Promise<string | null>;
}

// Server-Sent Events Hook Types
export interface SSEMessage {
  type: 'new_message' | 'conversation_updated';
  data: Record<string, unknown>;
}

export interface UseSSEOptions {
  url: string;
  token?: string;
  onMessage?: (message: SSEMessage) => void;
  onConnect?: () => void;
  onError?: (error: Event) => void;
}

// Messages Hook Types
export interface UseMessagesOptions {
  receiverId?: string;
  wsUrl: string;
  token: string;
}

// Message Edit Hook Types
export interface UseMessageEditOptions {
  messageId: string;
  editorId: string;
}

// Message Actions Hook Types
export interface UseMessageActionsOptions {
  userId: string;
}

// Message Search Hook Types
export interface UseMessageSearchOptions {
  initialTerm?: string;
  pageSize?: number;
}

// Thread Hook Types
export interface UseThreadOptions {
  parentMessageId?: string;
  threadId?: string;
  wsUrl: string;
  token: string;
}

// Message Pin Hook Types
export interface UseMessagePinOptions {
  userId: string;
}
