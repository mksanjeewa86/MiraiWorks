import type { ApiResponse, Conversation, Message } from '@/types';

const API_BASE_URL = 'http://localhost:8000';

// Messages API
export const messagesApi = {
  getConversations: async (token?: string): Promise<ApiResponse<Conversation[]>> => {
    const authToken = token || localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messaging/conversations`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const responseData = await response.json();
    return { data: responseData.conversations || [], success: true };
  },

  markConversationAsRead: async (conversationId: number, token?: string): Promise<ApiResponse<unknown>> => {
    const authToken = token || localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messaging/conversations/${conversationId}/read`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  getConversation: async (id: number): Promise<ApiResponse<Conversation>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messaging/conversations/${id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  getMessages: async (conversationId: number, page = 1, limit = 50): Promise<ApiResponse<{
    messages: Message[];
    total: number;
    page: number;
    totalPages: number;
  }>> => {
    const token = localStorage.getItem('accessToken');
    const url = new URL(`${API_BASE_URL}/api/messaging/conversations/${conversationId}/messages`);
    url.searchParams.set('page', page.toString());
    url.searchParams.set('limit', limit.toString());
    
    const response = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  sendMessage: async (conversationId: number, messageData: {
    content: string;
    type?: 'text' | 'file' | 'system';
    attachmentUrl?: string;
  }): Promise<ApiResponse<Message>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messaging/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(messageData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  createConversation: async (conversationData: {
    title?: string;
    participantIds: number[];
    isGroup?: boolean;
  }): Promise<ApiResponse<Conversation>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messaging/conversations`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(conversationData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  markAsRead: async (conversationId: number): Promise<ApiResponse<void>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messaging/conversations/${conversationId}/read`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return { data: undefined, success: true };
  },

  deleteMessage: async (messageId: number): Promise<ApiResponse<void>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messages/${messageId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    return { data: undefined, success: true };
  },
};