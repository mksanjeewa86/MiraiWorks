'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import Badge from '@/components/ui/Badge';
import { Search, Send } from 'lucide-react';
import type { Conversation, Message, User } from '@/types';

interface MessagesPageState {
  conversations: Conversation[];
  activeConversationId: number | null;
  messages: Message[];
  loading: boolean;
  sending: boolean;
  error: string | null;
  newMessage: string;
  searchQuery: string;
}

// Mock data for development - moved outside component to prevent re-creation
const mockConversations: Conversation[] = [
  {
    id: 1,
    title: 'Tech Interview Discussion',
    is_group: false,
    created_by: 1,
    participants: [
      { 
        id: 1,
        conversation_id: 1,
        user_id: 2,
        joined_at: '2024-01-15T10:30:00.000Z',
        user: { 
          id: 2, 
          email: 'jane.smith@techcorp.com', 
          first_name: 'Jane',
          last_name: 'Smith',
          full_name: 'Jane Smith',
          phone: '+1-555-0123',
          company_id: 1,
          is_active: true,
          is_admin: false,
          require_2fa: false,
          last_login: '2024-01-15T09:00:00.000Z',
          created_at: '2023-12-01T10:00:00.000Z',
          updated_at: '2024-01-15T09:00:00.000Z',
          roles: [],
          company: {
            id: 1,
            name: 'TechCorp',
            domain: 'techcorp.com',
            industry: 'Technology',
            is_active: true,
            created_at: '2023-11-01T10:00:00.000Z',
            updated_at: '2023-12-01T10:00:00.000Z'
          }
        } as User
      }
    ],
    last_message: {
      id: 1,
      content: 'Thanks for your interest in the Senior Developer position. Let\'s schedule a call to discuss further.',
      sender_id: 2,
      conversation_id: 1,
      message_type: 'text',
      is_read: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      sender: { 
        id: 2, 
        email: 'jane.smith@techcorp.com', 
        first_name: 'Jane',
        last_name: 'Smith',
        full_name: 'Jane Smith',
        phone: '+1-555-0123',
        company_id: 1,
        is_active: true,
        is_admin: false,
        require_2fa: false,
        last_login: '2024-01-15T09:00:00.000Z',
        created_at: '2023-12-01T10:00:00.000Z',
        updated_at: '2024-01-15T09:00:00.000Z',
        roles: [],
        company: {
          id: 1,
          name: 'TechCorp',
          domain: 'techcorp.com',
          industry: 'Technology',
          is_active: true,
          created_at: '2023-11-01T10:00:00.000Z',
          updated_at: '2023-12-01T10:00:00.000Z'
        }
      } as User
    } as Message,
    unread_count: 2,
    created_at: new Date().toISOString()
  },
  {
    id: 2,
    title: 'Resume Feedback',
    is_group: false,
    created_by: 3,
    participants: [
      { 
        id: 2,
        conversation_id: 2,
        user_id: 3,
        joined_at: '2024-01-16T14:20:00.000Z',
        user: { 
          id: 3, 
          email: 'mike.johnson@startupco.com', 
          first_name: 'Mike',
          last_name: 'Johnson',
          full_name: 'Mike Johnson',
          phone: '+1-555-0456',
          company_id: 2,
          is_active: true,
          is_admin: false,
          require_2fa: false,
          last_login: '2024-01-16T13:30:00.000Z',
          created_at: '2023-11-15T10:00:00.000Z',
          updated_at: '2024-01-16T13:30:00.000Z',
          roles: [],
          company: {
            id: 2,
            name: 'StartupCo',
            domain: 'startupco.com',
            industry: 'Technology',
            is_active: true,
            created_at: '2023-10-15T10:00:00.000Z',
            updated_at: '2023-11-15T10:00:00.000Z'
          }
        } as User
      }
    ],
    last_message: {
      id: 2,
      content: 'Your resume looks great! I\'d like to move forward with an interview.',
      sender_id: 3,
      conversation_id: 2,
      message_type: 'text',
      is_read: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      sender: { 
        id: 3, 
        email: 'mike.johnson@startupco.com', 
        first_name: 'Mike',
        last_name: 'Johnson',
        full_name: 'Mike Johnson',
        phone: '+1-555-0456',
        company_id: 2,
        is_active: true,
        is_admin: false,
        require_2fa: false,
        last_login: '2024-01-16T13:30:00.000Z',
        created_at: '2023-11-15T10:00:00.000Z',
        updated_at: '2024-01-16T13:30:00.000Z',
        roles: [],
        company: {
          id: 2,
          name: 'StartupCo',
          domain: 'startupco.com',
          industry: 'Technology',
          is_active: true,
          created_at: '2023-10-15T10:00:00.000Z',
          updated_at: '2023-11-15T10:00:00.000Z'
        }
      } as User
    } as Message,
    unread_count: 0,
    created_at: new Date().toISOString()
  }
];

const createMockMessages = (user: User | null): Message[] => {
  const mockCurrentUser: User = {
    id: user?.id || 1,
    email: 'current@example.com',
    first_name: 'Current',
    last_name: 'User',
    full_name: 'Current User',
    phone: '+1-555-0789',
    company_id: 3,
    is_active: true,
    is_admin: false,
    require_2fa: false,
    last_login: new Date().toISOString(),
    created_at: '2023-10-01T10:00:00.000Z',
    updated_at: new Date().toISOString(),
    roles: [],
    company: {
      id: 3,
      name: 'Current Company',
      domain: 'example.com',
      industry: 'Technology',
      is_active: true,
      created_at: '2023-09-01T10:00:00.000Z',
      updated_at: '2023-10-01T10:00:00.000Z'
    }
  };

  const mockRecruiter: User = {
    id: 2,
    email: 'jane.smith@techcorp.com',
    first_name: 'Jane',
    last_name: 'Smith',
    full_name: 'Jane Smith',
    phone: '+1-555-0123',
    company_id: 1,
    is_active: true,
    is_admin: false,
    require_2fa: false,
    last_login: '2024-01-15T09:00:00.000Z',
    created_at: '2023-12-01T10:00:00.000Z',
    updated_at: '2024-01-15T09:00:00.000Z',
    roles: [],
    company: {
      id: 1,
      name: 'TechCorp',
      domain: 'techcorp.com',
      industry: 'Technology',
      is_active: true,
      created_at: '2023-11-01T10:00:00.000Z',
      updated_at: '2023-12-01T10:00:00.000Z'
    }
  };

  return [
    {
      id: 1,
      content: 'Hello! I saw your job posting for the Senior Developer role and I\'m very interested.',
      sender_id: mockCurrentUser.id,
      conversation_id: 1,
      message_type: 'text',
      is_read: true,
      created_at: new Date(Date.now() - 3600000).toISOString(),
      updated_at: new Date(Date.now() - 3600000).toISOString(),
      sender: mockCurrentUser
    } as Message,
    {
      id: 2,
      content: 'Thanks for your interest in the Senior Developer position. Let\'s schedule a call to discuss further.',
      sender_id: 2,
      conversation_id: 1,
      message_type: 'text',
      is_read: true,
      created_at: new Date(Date.now() - 1800000).toISOString(),
      updated_at: new Date(Date.now() - 1800000).toISOString(),
      sender: mockRecruiter
    } as Message,
    {
      id: 3,
      content: 'That sounds great! I\'m available for a call this week. What time works best for you?',
      sender_id: mockCurrentUser.id,
      conversation_id: 1,
      message_type: 'text',
      is_read: true,
      created_at: new Date(Date.now() - 900000).toISOString(),
      updated_at: new Date(Date.now() - 900000).toISOString(),
      sender: mockCurrentUser
    } as Message
  ];
};

export default function MessagesPage() {
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const [state, setState] = useState<MessagesPageState>({
    conversations: [],
    activeConversationId: null,
    messages: [],
    loading: true,
    sending: false,
    error: null,
    newMessage: '',
    searchQuery: '',
  });

  useEffect(() => {
    // Simulate API load
    setTimeout(() => {
      setState(prev => ({
        ...prev,
        conversations: mockConversations,
        loading: false
      }));
    }, 1000);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [state.messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleConversationSelect = (conversationId: number) => {
    setState(prev => ({ ...prev, activeConversationId: conversationId }));
    
    // Load messages for this conversation (mock)
    const mockMessages = createMockMessages(user);
    const conversationMessages = mockMessages.filter(msg => msg.conversation_id === conversationId);
    setState(prev => ({ ...prev, messages: conversationMessages }));
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!state.newMessage.trim() || !state.activeConversationId || state.sending) return;

    setState(prev => ({ ...prev, sending: true }));

    // Mock sending message
    const currentUserMock: User = {
      id: user?.id || 1,
      email: user?.email || 'current@example.com',
      first_name: user?.first_name || 'Current',
      last_name: user?.last_name || 'User',
      full_name: user?.full_name || 'Current User',
      phone: '+1-555-0789',
      company_id: 3,
      is_active: true,
      is_admin: false,
      require_2fa: false,
      last_login: new Date().toISOString(),
      created_at: '2023-10-01T10:00:00.000Z',
      updated_at: new Date().toISOString(),
      roles: [],
      company: {
        id: 3,
        name: 'Current Company',
        domain: 'example.com',
        industry: 'Technology',
        is_active: true,
        created_at: '2023-09-01T10:00:00.000Z',
        updated_at: '2023-10-01T10:00:00.000Z'
      }
    };

    const newMessage: Message = {
      id: Date.now(),
      content: state.newMessage.trim(),
      sender_id: user?.id || 1,
      conversation_id: state.activeConversationId!,
      message_type: 'text',
      is_read: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      sender: currentUserMock
    };

    setTimeout(() => {
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, newMessage],
        newMessage: '',
        sending: false
      }));
    }, 500);
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getConversationPreview = (conversation: Conversation) => {
    if (!conversation.last_message) return 'No messages yet';
    const maxLength = 50;
    return conversation.last_message.content.length > maxLength
      ? conversation.last_message.content.substring(0, maxLength) + '...'
      : conversation.last_message.content;
  };

  const filteredConversations = state.conversations.filter(conv =>
    conv.title?.toLowerCase().includes(state.searchQuery.toLowerCase()) ||
    conv.participants.some(p => 
      p.user.full_name?.toLowerCase().includes(state.searchQuery.toLowerCase())
    )
  );

  const activeConversation = state.conversations.find(c => c.id === state.activeConversationId);

  if (state.loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner className="w-8 h-8" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex h-[calc(100vh-4rem)] bg-gray-50 dark:bg-gray-950">
        {/* Conversations Sidebar */}
        <div className="w-1/3 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h1 className="text-2xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>Messages</h1>
            <Input
              type="text"
              placeholder="Search conversations..."
              value={state.searchQuery}
              onChange={(e) => setState(prev => ({ ...prev, searchQuery: e.target.value }))}
              leftIcon={<Search className="h-4 w-4" />}
              className="w-full"
            />
          </div>

          <div className="flex-1 overflow-y-auto">
            {filteredConversations.length > 0 ? (
              <div className="divide-y divide-gray-100 dark:divide-gray-700">
                {filteredConversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    onClick={() => handleConversationSelect(conversation.id)}
                    className={`p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                      state.activeConversationId === conversation.id 
                        ? 'bg-blue-50 dark:bg-blue-900/20 border-r-2 border-brand-primary' 
                        : ''
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--brand-muted-bg)' }}>
                        <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                          {conversation.participants[0]?.user?.full_name?.charAt(0) || 'C'}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                            {conversation.title || 
                             conversation.participants
                               .filter(p => p.user.id !== user?.id)
                               .map(p => p.user.full_name)
                               .join(', ')
                            }
                          </p>
                          {conversation.last_message && (
                            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                              {formatTime(conversation.last_message.created_at)}
                            </p>
                          )}
                        </div>
                        <p className="text-sm truncate" style={{ color: 'var(--text-secondary)' }}>
                          {getConversationPreview(conversation)}
                        </p>
                        {conversation.unread_count > 0 && (
                          <Badge variant="primary" className="mt-1">
                            {conversation.unread_count}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center">
                <span className="text-4xl mb-4 block">💬</span>
                <p style={{ color: 'var(--text-muted)' }}>No conversations found</p>
                <Button className="mt-4">
                  Start New Conversation
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 flex flex-col">
          {activeConversation ? (
            <>
              {/* Chat Header */}
              <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ backgroundColor: 'var(--brand-muted-bg)' }}>
                    <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {activeConversation.participants[0]?.user?.full_name?.charAt(0) || 'C'}
                    </span>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {activeConversation.title ||
                       activeConversation.participants
                         .filter(p => p.user.id !== user?.id)
                         .map(p => p.user.full_name)
                         .join(', ')
                      }
                    </h2>
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-green-500" />
                      <span className="text-sm" style={{ color: 'var(--text-muted)' }}>Online</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {state.messages.map((message) => {
                  const isOwn = message.sender_id === user?.id;
                  return (
                    <div
                      key={message.id}
                      className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        isOwn 
                          ? 'bg-brand-primary text-white' 
                          : 'bg-gray-200 dark:bg-gray-700'
                      }`}>
                        <p className={`text-sm ${isOwn ? 'text-white' : ''}`} style={{ color: isOwn ? 'white' : 'var(--text-primary)' }}>
                          {message.content}
                        </p>
                        <p className={`text-xs mt-1 ${
                          isOwn ? 'text-blue-100' : ''
                        }`} style={{ color: isOwn ? 'rgba(255,255,255,0.7)' : 'var(--text-muted)' }}>
                          {formatTime(message.created_at)}
                        </p>
                      </div>
                    </div>
                  );
                })}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <form onSubmit={handleSendMessage} className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
                <div className="flex items-center space-x-2">
                  <Input
                    type="text"
                    value={state.newMessage}
                    onChange={(e) => setState(prev => ({ ...prev, newMessage: e.target.value }))}
                    placeholder="Type a message..."
                    className="flex-1"
                    disabled={state.sending}
                  />
                  <Button 
                    type="submit" 
                    disabled={!state.newMessage.trim() || state.sending}
                    className="px-4 py-2 flex items-center gap-2"
                  >
                    {state.sending ? <LoadingSpinner className="w-4 h-4" /> : <Send className="w-4 h-4" />}
                  </Button>
                </div>
              </form>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <span className="text-6xl mb-4 block">💬</span>
                <h2 className="text-xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>Welcome to Messages</h2>
                <p className="mb-4" style={{ color: 'var(--text-secondary)' }}>
                  Select a conversation from the sidebar to start messaging
                </p>
                <Button>
                  Start New Conversation
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}