import type { ApiResponse, Conversation, Message, DirectMessageInfo } from '@/types';
import { API_CONFIG } from '@/config/api';

// Direct Messages API
export const messagesApi = {
  getConversations: async (token?: string): Promise<ApiResponse<Conversation[]>> => {
    const authToken = token || localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/direct_messages/conversations`, {
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
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/direct_messages/mark-conversation-read/${otherUserId}`, {
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

  getConversation: async (otherUserId: number): Promise<ApiResponse<Conversation>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/direct_messages/with/${otherUserId}`, {
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

  getMessages: async (otherUserId: number, limit = 50, beforeId?: number): Promise<ApiResponse<{
    messages: Message[];
    total: number;
    has_more: boolean;
  }>> => {
    const token = localStorage.getItem('accessToken');
    const url = new URL(`${API_CONFIG.BASE_URL}/api/direct_messages/with/${otherUserId}`);
    url.searchParams.set('limit', limit.toString());
    if (beforeId) {
      url.searchParams.set('before_id', beforeId.toString());
    }
    
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

  sendMessage: async (recipientId: number, messageData: {
    content: string;
    type?: 'text' | 'file' | 'system';
    reply_to_id?: number;
    file_url?: string;
    file_name?: string;
    file_size?: number;
    file_type?: string;
  }): Promise<ApiResponse<Message>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/direct_messages/send`, {
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
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/direct_messages/mark-conversation-read/${otherUserId}`, {
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
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/messages/${messageId}`, {
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
    messages: DirectMessageInfo[];
  }>> => {
    const token = localStorage.getItem('accessToken');
    const response = await fetch(`${API_CONFIG.BASE_URL}/api/direct_messages/search`, {
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
    const url = new URL(`${API_CONFIG.BASE_URL}/api/direct_messages/participants`);
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
    return { data: { participants: data.participants || [] }, success: true };
  },

  uploadFile: async (file: File): Promise<ApiResponse<{
    file_url: string;
    file_name: string;
    file_size: number;
    file_type: string;
  }>> => {
    const token = localStorage.getItem('accessToken');
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_CONFIG.BASE_URL}/api/files/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
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
};