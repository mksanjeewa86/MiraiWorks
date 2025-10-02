import { API_ENDPOINTS, API_CONFIG } from './config';
import { apiClient } from './apiClient';
import type { ApiResponse, Conversation, Message, MessageInfo } from '@/types';

// Helper to build query strings
const buildQueryString = (params?: Record<string, string | number | undefined>): string => {
  if (!params) return '';

  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) {
      searchParams.set(key, value.toString());
    }
  });

  return searchParams.toString();
};

export const messagesApi = {
  async getConversations(token?: string): Promise<ApiResponse<Conversation[]>> {
    // Handle optional token for special auth cases
    if (token) {
      const response = await fetch(
        `${API_CONFIG.BASE_URL}${API_ENDPOINTS.MESSAGES.CONVERSATIONS}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const responseData = await response.json();
      return { data: responseData.conversations || [], success: true };
    }

    const response = await apiClient.get<{ conversations: Conversation[] }>(
      API_ENDPOINTS.MESSAGES.CONVERSATIONS
    );
    return { data: response.data.conversations || [], success: true };
  },

  async markConversationAsRead(otherUserId: number, token?: string): Promise<ApiResponse<unknown>> {
    // Handle optional token for special auth cases
    if (token) {
      const response = await fetch(
        `${API_CONFIG.BASE_URL}${API_ENDPOINTS.MESSAGES.MARK_READ(otherUserId)}`,
        {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { data, success: true };
    }

    const response = await apiClient.put<unknown>(API_ENDPOINTS.MESSAGES.MARK_READ(otherUserId));
    return { data: response.data, success: true };
  },

  async getConversation(otherUserId: number): Promise<ApiResponse<Conversation>> {
    const response = await apiClient.get<Conversation>(
      API_ENDPOINTS.MESSAGES.WITH_USER(otherUserId)
    );
    return { data: response.data, success: true };
  },

  async getMessages(
    otherUserId: number,
    limit = 50,
    beforeId?: number
  ): Promise<
    ApiResponse<{
      messages: Message[];
      total: number;
      has_more: boolean;
    }>
  > {
    const query = buildQueryString({ limit, before_id: beforeId });
    const url = query
      ? `${API_ENDPOINTS.MESSAGES.WITH_USER(otherUserId)}?${query}`
      : API_ENDPOINTS.MESSAGES.WITH_USER(otherUserId);

    const response = await apiClient.get<{
      messages: Message[];
      total: number;
      has_more: boolean;
    }>(url);
    return { data: response.data, success: true };
  },

  async sendMessage(
    recipientId: number,
    messageData: {
      content: string;
      type?: 'text' | 'file' | 'system';
      reply_to_id?: number;
      file_url?: string;
      file_name?: string;
      file_size?: number;
      file_type?: string;
    }
  ): Promise<ApiResponse<Message>> {
    const requestBody = {
      recipient_id: recipientId,
      content: messageData.content,
      type: messageData.type || 'text',
      reply_to_id: messageData.reply_to_id,
      file_url: messageData.file_url,
      file_name: messageData.file_name,
      file_size: messageData.file_size,
      file_type: messageData.file_type,
    };

    const response = await apiClient.post<Message>(API_ENDPOINTS.MESSAGES.SEND, requestBody);
    return { data: response.data, success: true };
  },

  async markAsRead(otherUserId: number): Promise<ApiResponse<void>> {
    await apiClient.put<void>(API_ENDPOINTS.MESSAGES.MARK_READ(otherUserId));
    return { data: undefined, success: true };
  },

  async deleteMessage(messageId: number): Promise<ApiResponse<void>> {
    await apiClient.delete<void>(API_ENDPOINTS.MESSAGES.BY_ID(messageId));
    return { data: undefined, success: true };
  },

  async searchMessages(
    query: string,
    withUserId?: number
  ): Promise<
    ApiResponse<{
      messages: MessageInfo[];
    }>
  > {
    const requestBody = {
      query,
      with_user_id: withUserId,
      limit: 50,
      offset: 0,
    };

    const response = await apiClient.post<{ messages: MessageInfo[] }>(
      API_ENDPOINTS.MESSAGES.SEARCH,
      requestBody
    );
    return { data: { messages: response.data.messages || [] }, success: true };
  },

  async searchParticipants(query?: string): Promise<
    ApiResponse<{
      participants: Array<{
        id: number;
        email: string;
        full_name: string;
        company_name?: string;
        is_online?: boolean;
      }>;
    }>
  > {
    try {
      const url = query
        ? `${API_ENDPOINTS.MESSAGES.PARTICIPANTS}?query=${encodeURIComponent(query)}`
        : API_ENDPOINTS.MESSAGES.PARTICIPANTS;
      const response = await apiClient.get<{
        participants?: Array<{
          id: number;
          email: string;
          full_name: string;
          company_name?: string;
          is_online?: boolean;
        }>;
      }>(url);
      return { data: { participants: response.data.participants || [] }, success: true };
    } catch (error) {
      console.error('Error in searchParticipants:', error);
      throw new Error(error instanceof Error ? error.message : 'Failed to load participants');
    }
  },

  async uploadFile(file: File): Promise<
    ApiResponse<{
      file_url: string;
      file_name: string;
      file_size: number;
      file_type: string;
    }>
  > {
    // File upload needs special handling with FormData
    const token = localStorage.getItem('accessToken');
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_CONFIG.BASE_URL}${API_ENDPOINTS.FILES.UPLOAD}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { data, success: true };
  },

  async getRestrictedUserIds(): Promise<ApiResponse<{ restricted_user_ids: number[] }>> {
    const response = await apiClient.get<{ restricted_user_ids: number[] }>(
      API_ENDPOINTS.MESSAGES_EXTENDED.RESTRICTED_USERS
    );
    return { data: response.data, success: true };
  },
};
