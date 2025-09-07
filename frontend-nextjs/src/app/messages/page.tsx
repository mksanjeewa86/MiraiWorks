'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Search, Send, Plus, X, User, Phone, Video, MoreHorizontal, RefreshCw } from 'lucide-react';
import { messagesApi } from '@/services/api';
import type { Conversation, Message } from '@/types';

interface MessagesPageState {
  conversations: Conversation[];
  activeConversationId: number | null;
  messages: Message[];
  loading: boolean;
  sending: boolean;
  error: string | null;
  newMessage: string;
  activeTab: 'conversations' | 'contacts';
  conversationSearchQuery: string;
  contactSearchQuery: string;
  searchingContacts: boolean;
  contacts: Array<{
    id: number;
    email: string;
    full_name: string;
    company_name?: string;
    is_online?: boolean;
  }>;
}

export default function MessagesPage() {
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const isPageVisible = useRef(true);
  
  const [state, setState] = useState<MessagesPageState>({
    conversations: [],
    activeConversationId: null,
    messages: [],
    loading: true,
    sending: false,
    error: null,
    newMessage: '',
    activeTab: 'conversations',
    conversationSearchQuery: '',
    contactSearchQuery: '',
    searchingContacts: false,
    contacts: []
  });

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));
        const response = await messagesApi.getConversations();
        const conversations = response.data || [];
        
        setState(prev => ({
          ...prev,
          conversations,
          loading: false,
          // Auto-select the most recent conversation if exists
          activeConversationId: conversations.length > 0 && !prev.activeConversationId
            ? conversations[0].other_user_id 
            : prev.activeConversationId
        }));
      } catch (err) {
        setState(prev => ({
          ...prev,
          error: err instanceof Error ? err.message : 'Failed to load conversations',
          loading: false
        }));
        console.error('Failed to fetch conversations:', err);
      }
    };

    fetchConversations();

    // No polling - we'll use WebSocket events and manual refreshes instead
    return () => {
      // Cleanup will be handled by WebSocket connection
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [state.messages]);

  // Fetch contacts when contacts tab is selected
  useEffect(() => {
    const fetchContacts = async () => {
      if (state.activeTab !== 'contacts') return;
      
      try {
        setState(prev => ({ ...prev, searchingContacts: true }));
        const response = await messagesApi.searchParticipants(state.contactSearchQuery);
        setState(prev => ({
          ...prev,
          contacts: response.data?.participants || [],
          searchingContacts: false
        }));
      } catch (err) {
        console.error('Failed to fetch contacts:', err);
        setState(prev => ({
          ...prev,
          contacts: [],
          searchingContacts: false
        }));
      }
    };

    fetchContacts();
  }, [state.activeTab, state.contactSearchQuery]);

  useEffect(() => {
    const fetchMessages = async () => {
      if (!state.activeConversationId) return;
      
      try {
        const response = await messagesApi.getMessages(state.activeConversationId);
        setState(prev => ({
          ...prev,
          messages: response.data?.messages || []
        }));
      } catch (err) {
        console.error('Failed to fetch messages:', err);
        setState(prev => ({
          ...prev,
          messages: []
        }));
      }
    };

    fetchMessages();

    // No polling for messages - only load once when conversation changes
    // New messages will be received via WebSocket
    return () => {
      // No cleanup needed for polling
    };
  }, [state.activeConversationId, state.sending]);

  // Handle page visibility changes - just track visibility, no automatic refreshing
  useEffect(() => {
    const handleVisibilityChange = () => {
      isPageVisible.current = !document.hidden;
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  // Manual refresh for conversation list only (no automatic refreshing)
  const refreshConversationList = useCallback(async () => {
    try {
      const response = await messagesApi.getConversations();
      setState(prev => ({
        ...prev,
        conversations: response.data || prev.conversations
      }));
    } catch (err) {
      console.error('Failed to refresh conversation list:', err);
    }
  }, []);


  // Function to add a new message to current conversation (for real-time updates)
  const addNewMessage = useCallback((newMessage: Message) => {
    setState(prev => {
      // Only add if it's for the currently active conversation
      if (prev.activeConversationId === newMessage.sender_id || 
          prev.activeConversationId === newMessage.recipient_id) {
        // Check if message already exists to avoid duplicates
        const messageExists = prev.messages.some(msg => msg.id === newMessage.id);
        if (!messageExists) {
          return {
            ...prev,
            messages: [...prev.messages, newMessage]
          };
        }
      }
      return prev;
    });

    // Always refresh conversation list when new message arrives
    refreshConversationList();
    
    // Scroll to bottom if new message is in active conversation
    setTimeout(scrollToBottom, 100);
  }, [refreshConversationList]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleConversationSelect = (conversationId: number) => {
    setState(prev => ({ ...prev, activeConversationId: conversationId }));
    
    // Mark conversation as read
    messagesApi.markAsRead(conversationId).then(() => {
      // Update the local state to reflect the conversation is now read
      setState(prev => ({
        ...prev,
        conversations: prev.conversations.map(conv => 
          conv.other_user_id === conversationId 
            ? { ...conv, unread_count: 0 }
            : conv
        )
      }));
    }).catch(err => {
      console.error('Failed to mark conversation as read:', err);
    });
  };

  const handleSendMessage = async () => {
    if (!state.newMessage.trim() || !state.activeConversationId || state.sending) return;

    try {
      setState(prev => ({ ...prev, sending: true }));
      
      const response = await messagesApi.sendMessage(state.activeConversationId, {
        content: state.newMessage.trim(),
        type: 'text'
      });

      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          messages: [...prev.messages, response.data as Message],
          newMessage: ''
        }));
        
        // Refresh conversation list after sending
        refreshConversationList(); // Update conversation list after sending
        
        // Scroll to bottom after sending
        setTimeout(scrollToBottom, 100);
      }
    } catch (err) {
      console.error('Failed to send message:', err);
    } finally {
      setState(prev => ({ ...prev, sending: false }));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const searchParticipants = async (query: string) => {
    if (!query.trim()) {
      setState(prev => ({ ...prev, participants: [] }));
      return;
    }

    try {
      setState(prev => ({ ...prev, searchingParticipants: true }));
      const response = await messagesApi.searchParticipants(query);
      setState(prev => ({
        ...prev,
        participants: response.data?.participants || [],
        searchingParticipants: false
      }));
    } catch (err) {
      console.error('Failed to search participants:', err);
      setState(prev => ({
        ...prev,
        participants: [],
        searchingParticipants: false
      }));
    }
  };

  const handleNewChat = () => {
    setState(prev => ({ 
      ...prev, 
      showNewChatModal: true, 
      participantSearch: '',
      participants: []
    }));
    // Load initial participants
    searchParticipants('');
  };

  const handleStartChat = async (participantId: number) => {
    try {
      // In direct messaging, just set the active conversation to the participant ID
      // The conversation will be created when the first message is sent
      // Messages will be loaded automatically via useEffect
      setState(prev => ({
        ...prev,
        activeConversationId: participantId,
        showNewChatModal: false
      }));
    } catch (err) {
      console.error('Failed to start chat:', err);
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getAvatarColor = (id: number) => {
    const colors = [
      'bg-blue-500',
      'bg-green-500', 
      'bg-purple-500',
      'bg-pink-500',
      'bg-indigo-500',
      'bg-teal-500',
      'bg-orange-500',
      'bg-red-500'
    ];
    return colors[id % colors.length];
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };


  const filteredConversations = state.conversations.filter(conversation =>
    conversation.other_user_name?.toLowerCase().includes(state.conversationSearchQuery.toLowerCase()) ||
    conversation.other_user_email?.toLowerCase().includes(state.conversationSearchQuery.toLowerCase()) ||
    conversation.other_user_company?.toLowerCase().includes(state.conversationSearchQuery.toLowerCase())
  );

  const activeConversation = state.conversations.find(c => c.other_user_id === state.activeConversationId);

  if (state.loading) {
    return (
      <AppLayout>
        <div className="h-[calc(100vh-4rem)] flex bg-white dark:bg-gray-900">
          {/* Conversations List - Loading State */}
          <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
            {/* Header */}
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Chats</h1>
                  <p className="text-xs text-gray-500 mt-1">Active tab: conversations</p>
                </div>
                <div className="flex items-center gap-2">
                  <Button 
                    onClick={refreshConversationList}
                    size="sm" 
                    variant="ghost"
                    className="w-10 h-10 rounded-full p-0 flex items-center justify-center"
                    title="Refresh conversations"
                    disabled
                  >
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                  <Button 
                    onClick={handleNewChat}
                    size="sm" 
                    className="w-10 h-10 rounded-full p-0 flex items-center justify-center"
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
              {/* Tab Navigation */}
              <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1 mb-4">
                <button
                  className="flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm"
                >
                  Conversations
                </button>
                <button
                  className="flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                >
                  Contacts
                </button>
              </div>
              
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search messages or senders..."
                  className="pl-10 bg-gray-50 dark:bg-gray-700 border-0 rounded-xl"
                  disabled
                />
              </div>
            </div>

            {/* Loading Content */}
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <LoadingSpinner className="w-8 h-8 mx-auto mb-4" />
                <p className="text-gray-500">Loading conversations...</p>
              </div>
            </div>
          </div>

          {/* Messages Area - Loading State */}
          <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-900">
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl mb-4">💬</div>
                <p className="text-gray-500">Loading messages...</p>
              </div>
            </div>
          </div>
        </div>
      </AppLayout>
    );
  }

  if (state.error) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center h-64">
          <div className="text-6xl mb-4">❌</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Error Loading Messages</h3>
          <p className="text-red-600 mb-6">{state.error}</p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="h-[calc(100vh-4rem)] flex bg-white dark:bg-gray-900">
        {/* Conversations List */}
        <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          {/* Header */}
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Chats</h1>
                <p className="text-xs text-gray-500 mt-1">Active tab: {state.activeTab}</p>
              </div>
              <div className="flex items-center gap-2">
                <Button 
                  onClick={refreshConversationList}
                  size="sm" 
                  variant="ghost"
                  className="w-10 h-10 rounded-full p-0 flex items-center justify-center"
                  title="Refresh conversations"
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
                <Button 
                  onClick={handleNewChat}
                  size="sm" 
                  className="w-10 h-10 rounded-full p-0 flex items-center justify-center"
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            {/* Tab Navigation */}
            <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1 mb-4">
              <button
                onClick={() => {
                  console.log('Conversations tab clicked');
                  setState(prev => ({ ...prev, activeTab: 'conversations' }));
                }}
                className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                  state.activeTab === 'conversations'
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Conversations
              </button>
              <button
                onClick={() => {
                  console.log('Contacts tab clicked');
                  setState(prev => ({ ...prev, activeTab: 'contacts' }));
                }}
                className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                  state.activeTab === 'contacts'
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Contacts
              </button>
            </div>
            
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                type="text"
                placeholder={state.activeTab === 'conversations' ? 'Search messages or senders...' : 'Search contacts or companies...'}
                value={state.activeTab === 'conversations' ? state.conversationSearchQuery : state.contactSearchQuery}
                onChange={(e) => {
                  const value = e.target.value;
                  if (state.activeTab === 'conversations') {
                    setState(prev => ({ ...prev, conversationSearchQuery: value }));
                  } else {
                    setState(prev => ({ ...prev, contactSearchQuery: value }));
                  }
                }}
                className="pl-10 bg-gray-50 dark:bg-gray-700 border-0 rounded-xl"
              />
            </div>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto">
            {state.activeTab === 'conversations' ? (
              /* Conversations Tab */
              filteredConversations.length > 0 ? (
                filteredConversations.map(conversation => {
                  const lastMessage = conversation.last_message;
                  const isActive = conversation.other_user_id === state.activeConversationId;
                  
                  return (
                    <div
                      key={conversation.other_user_id}
                      onClick={() => handleConversationSelect(conversation.other_user_id)}
                      className={`mx-3 my-1 p-4 rounded-2xl cursor-pointer transition-all hover:bg-gray-50 dark:hover:bg-gray-700 ${
                        isActive ? 'bg-blue-50 dark:bg-blue-900/20 shadow-sm' : ''
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-medium ${getAvatarColor(conversation.other_user_id || 0)}`}>
                          {conversation.other_user_name ? getInitials(conversation.other_user_name) : '?'}
                        </div>
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <h3 className="font-semibold text-sm truncate" style={{ color: 'var(--text-primary)' }}>
                              {conversation.other_user_name || 'Unknown Contact'}
                            </h3>
                            <div className="flex items-center gap-2">
                              {lastMessage && (
                                <span className="text-xs text-gray-400">
                                  {formatTime(lastMessage.created_at)}
                                </span>
                              )}
                              {conversation.unread_count > 0 && (
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                              )}
                            </div>
                          </div>
                          
                          <p className="text-xs text-gray-500 mb-1">
                            {conversation.other_user_company || conversation.other_user_email || ''}
                          </p>
                          
                          {lastMessage && (
                            <p className="text-sm text-gray-600 dark:text-gray-300 truncate">
                              {lastMessage.content}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="p-8 text-center">
                  <div className="text-4xl mb-4">💬</div>
                  <p className="text-gray-500">No conversations yet</p>
                  <Button onClick={handleNewChat} className="mt-4" size="sm">
                    Start a new chat
                  </Button>
                </div>
              )
            ) : (
              /* Contacts Tab */
              state.searchingContacts ? (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <LoadingSpinner className="w-8 h-8 mx-auto mb-4" />
                    <p className="text-gray-500">Loading contacts...</p>
                  </div>
                </div>
              ) : state.contacts.length > 0 ? (
                state.contacts.map(contact => (
                  <div
                    key={contact.id}
                    onClick={() => handleConversationSelect(contact.id)}
                    className="mx-3 my-1 p-4 rounded-2xl cursor-pointer transition-all hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-medium ${getAvatarColor(contact.id)}`}>
                        {getInitials(contact.full_name)}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-sm truncate" style={{ color: 'var(--text-primary)' }}>
                          {contact.full_name}
                        </h3>
                        <p className="text-sm text-gray-500 truncate">
                          {contact.email}
                        </p>
                        {contact.company_name && (
                          <p className="text-xs text-gray-400 truncate">
                            {contact.company_name}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center">
                  <div className="text-4xl mb-4">👥</div>
                  <p className="text-gray-500">No contacts found</p>
                </div>
              )
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-900">
          {state.activeConversationId ? (
            <>
              {/* Chat Header */}
              <div className="p-6 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    {/* Avatar */}
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-medium ${getAvatarColor(activeConversation?.other_user_id || 0)}`}>
                      {activeConversation?.other_user_name 
                        ? getInitials(activeConversation.other_user_name) 
                        : '?'}
                    </div>
                    
                    <div>
                      <h2 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {activeConversation?.other_user_name || 'Conversation'}
                      </h2>
                      <p className="text-sm text-gray-500">
                        {activeConversation?.other_user_company || activeConversation?.other_user_email || 'Online'}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" className="w-10 h-10 rounded-full p-0">
                      <Phone className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" className="w-10 h-10 rounded-full p-0">
                      <Video className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" className="w-10 h-10 rounded-full p-0">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {state.messages.map((message, index) => {
                  const isCurrentUser = message.sender_id === user?.id;
                  const showAvatar = !isCurrentUser && (index === 0 || state.messages[index - 1].sender_id !== message.sender_id);
                  
                  return (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${isCurrentUser ? 'justify-end' : 'justify-start'}`}
                    >
                      {!isCurrentUser && (
                        <div className="w-8">
                          {showAvatar && (
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-medium ${getAvatarColor(message.sender?.id || 0)}`}>
                              {message.sender?.full_name ? getInitials(message.sender.full_name) : '?'}
                            </div>
                          )}
                        </div>
                      )}
                      
                      <div className={`max-w-md ${isCurrentUser ? 'items-end' : 'items-start'} flex flex-col`}>
                        <div
                          className={`px-4 py-3 rounded-2xl max-w-fit ${
                            isCurrentUser
                              ? 'bg-blue-500 text-white rounded-br-md'
                              : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-bl-md border border-gray-200 dark:border-gray-600'
                          }`}
                        >
                          <p className="text-sm leading-relaxed">{message.content}</p>
                        </div>
                        <div className={`text-xs text-gray-400 mt-1 ${isCurrentUser ? 'text-right' : 'text-left'}`}>
                          {formatTime(message.created_at)}
                        </div>
                      </div>
                    </div>
                  );
                })}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-6 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                <div className="flex gap-4 items-end">
                  <div className="flex-1 relative">
                    <Input
                      type="text"
                      placeholder="Type a message..."
                      value={state.newMessage}
                      onChange={(e) => setState(prev => ({ ...prev, newMessage: e.target.value }))}
                      onKeyPress={handleKeyPress}
                      className="pr-12 rounded-2xl border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={state.sending}
                    />
                  </div>
                  <Button 
                    onClick={handleSendMessage}
                    disabled={!state.newMessage.trim() || state.sending}
                    className="w-12 h-12 rounded-2xl p-0 bg-blue-500 hover:bg-blue-600"
                  >
                    {state.sending ? (
                      <LoadingSpinner className="w-4 h-4" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="text-8xl mb-6">💬</div>
                <h3 className="text-2xl font-semibold mb-3" style={{ color: 'var(--text-primary)' }}>
                  Start a conversation
                </h3>
                <p className="text-gray-500 mb-6 max-w-md">
                  Select a conversation from the sidebar or start a new chat to begin messaging
                </p>
                <Button onClick={handleNewChat}>
                  <Plus className="h-4 w-4 mr-2" />
                  New Chat
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

    </AppLayout>
  );
}