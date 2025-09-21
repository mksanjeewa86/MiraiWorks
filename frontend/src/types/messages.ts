// Base message types
export interface Message {
    id: string;
    type: MessageType;
    content: string;
    senderId: string;
    receiverId: string;
    timestamp: number;
    status: MessageStatus;
    metadata?: MessageMetadata;
}

export type MessageType = 'text' | 'file' | 'image' | 'system';
export type MessageStatus = 'pending' | 'sent' | 'delivered' | 'read' | 'failed';

export interface MessageMetadata {
    fileType?: string;
    fileSize?: number;
    thumbnailUrl?: string;
    fileUrl?: string;
    fileName?: string;
}

// Queue types
export interface QueuedMessage extends Message {
    retryCount: number;
    lastRetryTime?: number;
}

// Edit types
export interface EditHistory {
    timestamp: number;
    content: string;
    editorId: string;
}

export interface EditedMessage extends Message {
    editHistory: EditHistory[];
    lastEditedAt?: number;
    editedBy?: string;
}

// Thread types
export interface Thread {
    id: string;
    parentMessageId: string;
    lastReplyAt: number;
    replyCount: number;
    participants: string[];
}

export interface ThreadMessage extends Message {
    threadId?: string;
    replyTo?: string;
}

export interface ThreadUpdate {
    threadId: string;
    messageId: string;
    type: 'new_reply' | 'reply_deleted';
    timestamp: number;
}

// Reaction types
export interface MessageReaction {
    emoji: string;
    userId: string;
    timestamp: number;
    removed?: boolean;
}

export interface ReactionUpdate {
    messageId: string;
    reaction: MessageReaction;
}

// Status types
export interface MessageStatusUpdate {
    messageId: string;
    status: MessageStatus;
    timestamp: number;
    userId?: string;
}

// Forward types
export interface ForwardedMessage extends Message {
    originalMessageId: string;
    originalSenderId: string;
    forwardedBy: string;
    forwardedAt: number;
}

// File validation types
export interface ValidationResult {
    isValid: boolean;
    errors: string[];
}


// Legacy Message Types from API
export interface LegacyMessage {
  id: number;
  conversation_id: number;
  sender_id: number;
  recipient_id?: number;
  content: string;
  type?: 'text' | 'file' | 'system';
  message_type?: 'text' | 'file' | 'system';
  attachment_id?: number;
  is_read: boolean;
  file_url?: string;
  file_name?: string;
  file_size?: number;
  file_type?: string;
  created_at: string;
  updated_at: string;
  sender?: Record<string, unknown>; // Avoiding circular import
  sender_name?: string;
  attachment?: MessageAttachment;
  read_by?: Record<string, unknown>[]; // Avoiding circular import
}

// Message info from backend
export interface MessageInfo {
  id: number;
  sender_id: number;
  recipient_id: number;
  sender_name: string;
  recipient_name: string;
  sender_email: string;
  recipient_email: string;
  content: string;
  type: 'text' | 'file' | 'system';
  is_read: boolean;
  reply_to_id?: number;
  file_url?: string;
  file_name?: string;
  file_size?: number;
  file_type?: string;
  created_at: string;
  read_at?: string;
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

// Conversation Types
export interface Conversation {
  other_user_id: number;
  other_user_name: string;
  other_user_email: string;
  other_user_company?: string;
  last_message?: MessageInfo;
  last_message_content?: string;
  last_message_at?: string;
  unread_count: number;
  last_activity: string;
}

export interface LegacyConversation {
  id: number;
  title?: string;
  is_group: boolean;
  created_by: number;
  last_message_at?: string;
  created_at: string;
  participants: ConversationParticipant[];
  last_message?: LegacyMessage;
  unread_count: number;
}

export interface ConversationParticipant {
  id: number;
  conversation_id: number;
  user_id: number;
  joined_at: string;
  last_read_at?: string;
  user: Record<string, unknown>; // Avoiding circular import
}