// Hook-related interfaces and types

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
