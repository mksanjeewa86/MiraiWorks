import type { ApiResponse, Conversation, Message } from '@/types';

const API_BASE_URL = 'http://localhost:8000';

// Direct Messages API
export const messagesApi = {
  getConversations: async (token?: string): Promise<ApiResponse<Conversation[]>> => {
    const authToken = token || localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messages/conversations`, {
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

  markConversationAsRead: async (otherUserId: number, token?: string): Promise<ApiResponse<unknown>> => {
    const authToken = token || localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messages/mark-read`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ other_user_id: otherUserId }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  getConversation: async (otherUserId: number): Promise<ApiResponse<Conversation>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messages/with/${otherUserId}`, {
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

  getMessages: async (otherUserId: number, limit = 50): Promise<ApiResponse<{
    messages: Message[];
    total: number;
    page: number;
    totalPages: number;
  }>> => {
    const token = localStorage.getItem('accessToken');
    const url = new URL(`${API_BASE_URL}/api/messages/with/${otherUserId}`);
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
    return { data: data.messages || [], success: true };
  },

  sendMessage: async (recipientId: number, messageData: {
    content: string;
    type?: 'text' | 'file' | 'system';
    reply_to_id?: number;
  }): Promise<ApiResponse<Message>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messages/send`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        recipient_id: recipientId,
        ...messageData,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data, success: true };
  },

  markAsRead: async (otherUserId: number): Promise<ApiResponse<void>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messages/mark-read`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ other_user_id: otherUserId }),
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

  searchMessages: async (query: string, withUserId?: number): Promise<ApiResponse<{
    messages: Message[];
  }>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_BASE_URL}/api/messages/search`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        with_user_id: withUserId,
        limit: 50,
        offset: 0,
      }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data: { messages: data.messages || [] }, success: true };
  },

  searchParticipants: async (query?: string): Promise<ApiResponse<{
    participants: Array<{
      id: number;
      email: string;
      full_name: string;
      company_name?: string;
      is_online?: boolean;
    }>;
  }>> => {
    const token = localStorage.getItem('accessToken');
    const url = new URL(`${API_BASE_URL}/api/public/users/search`);
    if (query) {
      url.searchParams.set('query', query);
    }
    
    const response = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return { data: { participants: data.users || [] }, success: true };
  },
};