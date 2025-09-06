'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import Badge from '@/components/ui/Badge';
import { Search, Send } from 'lucide-react';
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
  searchQuery: string;
}

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
    searchQuery: ''
  });

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));
        const response = await messagesApi.getConversations();
        setState(prev => ({
          ...prev,
          conversations: response.data || [],
          loading: false
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
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [state.messages]);

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
  }, [state.activeConversationId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleConversationSelect = (conversationId: number) => {
    setState(prev => ({ ...prev, activeConversationId: conversationId }));
    
    // Mark conversation as read
    messagesApi.markAsRead(conversationId).catch(err => {
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

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  const filteredConversations = state.conversations.filter(conversation =>
    conversation.title?.toLowerCase().includes(state.searchQuery.toLowerCase()) ||
    conversation.participants?.some(p => 
      p.user?.full_name?.toLowerCase().includes(state.searchQuery.toLowerCase())
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
      <div className="h-[calc(100vh-4rem)] flex">
        {/* Conversations List */}
        <div className="w-80 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h1 className="text-2xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>Messages</h1>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4" style={{ color: 'var(--text-muted)' }} />
              <Input
                type="text"
                placeholder="Search conversations..."
                value={state.searchQuery}
                onChange={(e) => setState(prev => ({ ...prev, searchQuery: e.target.value }))}
                className="pl-10"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {filteredConversations.length > 0 ? (
              filteredConversations.map(conversation => {
                const lastMessage = conversation.last_message;
                const isActive = conversation.id === state.activeConversationId;
                const participant = conversation.participants?.[0]?.user;
                
                return (
                  <div
                    key={conversation.id}
                    onClick={() => handleConversationSelect(conversation.id)}
                    className={`p-4 border-b border-gray-200 dark:border-gray-700 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors ${
                      isActive ? 'bg-blue-50 dark:bg-blue-900/20 border-r-2 border-r-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h3 className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                          {conversation.title || participant?.full_name || 'Unknown Contact'}
                        </h3>
                        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                          {participant?.company?.name || ''}
                        </p>
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        {lastMessage && (
                          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                            {formatDate(lastMessage.created_at)}
                          </span>
                        )}
                        {conversation.unread_count > 0 && (
                          <Badge variant="primary" size="sm">
                            {conversation.unread_count}
                          </Badge>
                        )}
                      </div>
                    </div>
                    {lastMessage && (
                      <p className="text-sm truncate" style={{ color: 'var(--text-secondary)' }}>
                        {lastMessage.content}
                      </p>
                    )}
                  </div>
                );
              })
            ) : (
              <div className="p-8 text-center">
                <p style={{ color: 'var(--text-muted)' }}>No conversations found</p>
              </div>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 flex flex-col">
          {state.activeConversationId ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                  <div>
                    <h2 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {activeConversation?.title || 'Conversation'}
                    </h2>
                    {activeConversation?.participants?.[0]?.user && (
                      <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                        {activeConversation.participants[0].user.full_name} • {activeConversation.participants[0].user.company?.name}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {state.messages.map(message => {
                  const isCurrentUser = message.sender_id === user?.id;
                  
                  return (
                    <div
                      key={message.id}
                      className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          isCurrentUser
                            ? 'text-white'
                            : 'bg-gray-200 dark:bg-gray-700'
                        }`}
                        style={isCurrentUser ? { backgroundColor: 'var(--brand-primary)' } : {}}
                      >
                        {!isCurrentUser && message.sender && (
                          <div className="text-xs font-medium mb-1" style={{ color: 'var(--text-muted)' }}>
                            {message.sender.full_name}
                          </div>
                        )}
                        <div>{message.content}</div>
                        <div className={`text-xs mt-1 ${isCurrentUser ? 'text-blue-100' : ''}`} style={!isCurrentUser ? { color: 'var(--text-muted)' } : {}}>
                          {formatTime(message.created_at)}
                        </div>
                      </div>
                    </div>
                  );
                })}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                <div className="flex gap-3">
                  <Input
                    type="text"
                    placeholder="Type a message..."
                    value={state.newMessage}
                    onChange={(e) => setState(prev => ({ ...prev, newMessage: e.target.value }))}
                    onKeyPress={handleKeyPress}
                    className="flex-1"
                    disabled={state.sending}
                  />
                  <Button 
                    onClick={handleSendMessage}
                    disabled={!state.newMessage.trim() || state.sending}
                    className="px-4"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4">💬</div>
                <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                  Select a conversation
                </h3>
                <p style={{ color: 'var(--text-secondary)' }}>
                  Choose a conversation from the list to start messaging
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}