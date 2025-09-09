'use client';

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Search, Send, Plus, Phone, Video, MoreHorizontal, Smile, Paperclip } from 'lucide-react';
import { messagesApi } from '@/services/api';
import { useWebSocket } from '@/hooks/useWebSocket';
import type { Conversation, Message } from '@/types';
import dynamic from 'next/dynamic';

const EmojiPicker = dynamic(() => import('emoji-picker-react'), { 
  ssr: false,
  loading: () => <div>Loading...</div>
});

interface MessagesPageState {
  conversations: Conversation[];
  activeConversationId: number | null;
  messages: Message[];
  loading: boolean;
  error: string | null;
  sending: boolean;
  conversationSearchQuery: string;
  activeTab: 'conversations' | 'contacts';
  contacts: Array<{
    id: number;
    email: string;
    full_name: string;
    company_name?: string;
  }>;
  searchingContacts: boolean;
  hasMoreMessages: boolean;
}

export default function MessagesPage() {
  const { user, accessToken } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messageInputRef = useRef<HTMLInputElement>(null);
  
  const [state, setState] = useState<MessagesPageState>({
    conversations: [],
    activeConversationId: null,
    messages: [],
    loading: true,
    error: null,
    sending: false,
    conversationSearchQuery: '',
    activeTab: 'conversations',
    contacts: [],
    searchingContacts: false,
    hasMoreMessages: false
  });

  // Use separate state for input to prevent message list refreshes while typing
  const [newMessage, setNewMessage] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));
        const response = await messagesApi.getConversations();
        if (response.success && response.data) {
          setState(prev => ({
            ...prev,
            conversations: response.data || [],
            loading: false
          }));
        } else {
          setState(prev => ({ 
            ...prev, 
            error: 'Failed to load conversations',
            loading: false 
          }));
        }
      } catch (error) {
        setState(prev => ({ 
          ...prev, 
          error: 'Network error loading conversations',
          loading: false 
        }));
      }
    };

    if (user) {
      fetchConversations();
    }
  }, [user]);

  const fetchMessages = async () => {
    if (!state.activeConversationId) return;
    
    try {
      setState(prev => ({ ...prev, loading: true }));
      const response = await messagesApi.getMessages(state.activeConversationId, 50);
      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          messages: response.data?.messages || [],
          hasMoreMessages: response.data?.has_more || false,
          loading: false
        }));
        setTimeout(scrollToBottom, 100);
      }
    } catch (error) {
      setState(prev => ({ ...prev, error: 'Failed to load messages', loading: false }));
    }
  };

  useEffect(() => {
    if (state.activeConversationId) {
      fetchMessages();
    }
  }, [state.activeConversationId]);

  // Memoize WebSocket connection to prevent reconnections during typing
  const webSocketConfig = useMemo(() => {
    const shouldConnect = !!(user && accessToken && state.activeConversationId);
    return {
      url: shouldConnect 
        ? `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/ws/direct/${state.activeConversationId}`
        : '',
      token: shouldConnect ? accessToken : '',
    };
  }, [user, accessToken, state.activeConversationId]);
  
  const { isConnected, sendMessage } = useWebSocket({
    ...webSocketConfig,
    onMessage: (message) => {
      if (message.type === 'new_message') {
        setState(prev => ({
          ...prev,
          messages: [...prev.messages, message.data as unknown as Message]
        }));
        setTimeout(scrollToBottom, 100);
        refreshConversationList();
      }
    }
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const refreshConversationList = async () => {
    try {
      const response = await messagesApi.getConversations();
      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          conversations: response.data || []
        }));
      }
    } catch (error) {
      console.error('Failed to refresh conversations:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !state.activeConversationId || state.sending) return;

    const messageContent = newMessage.trim();
    
    // Clear input immediately for better UX
    setNewMessage('');
    setState(prev => ({ ...prev, sending: true }));

    try {
      const response = await messagesApi.sendMessage(state.activeConversationId, {
        content: messageContent,
        type: 'text'
      });
      if (response.success && response.data) {
        // Add message to local state immediately
        setState(prev => ({
          ...prev,
          messages: [...prev.messages, response.data as unknown as Message]
        }));
        
        // Scroll to bottom after sending
        setTimeout(scrollToBottom, 100);
        
        // Refresh conversation list to update last message
        refreshConversationList();
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setNewMessage(messageContent); // Restore message on error
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

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !state.activeConversationId || uploadingFile) return;

    setUploadingFile(true);
    try {
      // First upload the file to the server
      const uploadResponse = await messagesApi.uploadFile(file);
      if (!uploadResponse.success || !uploadResponse.data) {
        throw new Error('File upload failed');
      }

      // Then send a message with the file information
      const response = await messagesApi.sendMessage(state.activeConversationId, {
        content: `📎 ${uploadResponse.data.file_name}`,
        type: 'file',
        file_url: uploadResponse.data.file_url,
        file_name: uploadResponse.data.file_name,
        file_size: uploadResponse.data.file_size,
        file_type: uploadResponse.data.file_type
      });

      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          messages: [...prev.messages, response.data as unknown as Message]
        }));
        setTimeout(scrollToBottom, 100);
        refreshConversationList();
      }
    } catch (error) {
      console.error('File upload failed:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to upload file. Please try again.'
      }));
    } finally {
      setUploadingFile(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleAttachmentClick = () => {
    fileInputRef.current?.click();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setNewMessage(value);
    
    // Send typing indicator (only if WebSocket is connected)
    if (isConnected && state.activeConversationId && sendMessage) {
      sendMessage({
        type: 'typing',
        data: { is_typing: value.length > 0 }
      });
      
      // Clear typing indicator after 3 seconds of no typing
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      if (value.length > 0) {
        typingTimeoutRef.current = setTimeout(() => {
          if (isConnected && sendMessage) {
            sendMessage({
              type: 'typing', 
              data: { is_typing: false }
            });
          }
        }, 3000);
      }
    }
  };

  const handleConversationSelect = async (userId: number, fromContact = false) => {
    setState(prev => ({ 
      ...prev, 
      activeConversationId: userId, 
      messages: [],
      // If selecting from contacts, switch to conversations tab
      activeTab: fromContact ? 'conversations' : prev.activeTab
    }));

    // Fetch messages for the selected conversation
    await fetchMessages();

    // Focus message input when selecting a conversation, especially from contacts
    if (fromContact) {
      // Small delay to ensure the tab switch and render is complete
      setTimeout(() => {
        messageInputRef.current?.focus();
      }, 100);
      
      // Refresh conversations to show the new conversation if it wasn't there before
      refreshConversationList();
    }
  };

  const handleTabSwitch = async (tab: 'conversations' | 'contacts') => {
    setState(prev => ({ ...prev, activeTab: tab }));
    
    if (tab === 'contacts' && state.contacts.length === 0) {
      try {
        setState(prev => ({ ...prev, searchingContacts: true }));
        const response = await messagesApi.searchParticipants();
        if (response.success && response.data) {
          setState(prev => ({
            ...prev,
            contacts: response.data?.participants || [],
            searchingContacts: false
          }));
        }
      } catch (error) {
        setState(prev => ({ ...prev, searchingContacts: false }));
      }
    }
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0).toUpperCase())
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
          <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>Chats</h1>
                </div>
              </div>
              
              <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1 mb-4">
                <button className="flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm">
                  Conversations
                </button>
                <button className="flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
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

            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <LoadingSpinner className="w-8 h-8 mx-auto mb-4" />
                <p className="text-gray-500">Loading conversations...</p>
              </div>
            </div>
          </div>

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
              </div>
            </div>
            
            {/* Tab Navigation */}
            <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1 mb-4">
              <button
                onClick={() => handleTabSwitch('conversations')}
                className={`flex-1 py-2 px-3 text-sm font-medium rounded-md transition-colors ${
                  state.activeTab === 'conversations'
                    ? 'bg-white dark:bg-gray-600 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Conversations
              </button>
              <button
                onClick={() => handleTabSwitch('contacts')}
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
                placeholder="Search messages or senders..."
                value={state.conversationSearchQuery}
                onChange={(e) => setState(prev => ({ ...prev, conversationSearchQuery: e.target.value }))}
                className="pl-10 bg-gray-50 dark:bg-gray-700 border-0 rounded-xl"
              />
            </div>
          </div>

          {/* Content based on active tab */}
          <div className="flex-1 overflow-y-auto">
            {state.activeTab === 'conversations' ? (
              // Conversations Tab
              filteredConversations.length > 0 ? (
                filteredConversations.map(conversation => (
                  <div
                    key={conversation.other_user_id}
                    onClick={() => handleConversationSelect(conversation.other_user_id)}
                    className={`mx-3 my-1 p-4 rounded-2xl cursor-pointer transition-all hover:bg-gray-50 dark:hover:bg-gray-700 ${
                      state.activeConversationId === conversation.other_user_id 
                        ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800' 
                        : ''
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-medium ${getAvatarColor(conversation.other_user_id)}`}>
                        {getInitials(conversation.other_user_name || '')}
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <h3 className="font-semibold text-sm truncate" style={{ color: 'var(--text-primary)' }}>
                            {conversation.other_user_name}
                          </h3>
                          {conversation.last_message && (
                            <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                              {formatTime(conversation.last_message.created_at)}
                            </span>
                          )}
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <p className="text-sm text-gray-500 truncate">
                            {conversation.last_message ? (
                              <>
                                <span className="font-medium">
                                  {conversation.last_message.sender_id === user?.id ? 'You' : conversation.last_message.sender_name}:
                                </span>
                                {' ' + conversation.last_message.content}
                              </>
                            ) : (
                              conversation.other_user_email
                            )}
                          </p>
                          {conversation.unread_count > 0 && (
                            <div className="bg-blue-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center ml-2 flex-shrink-0">
                              {conversation.unread_count}
                            </div>
                          )}
                        </div>
                        
                        {conversation.other_user_company && (
                          <p className="text-xs text-gray-400 truncate mt-1">
                            {conversation.other_user_company}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center">
                  <div className="text-4xl mb-4">💬</div>
                  <p className="text-gray-500">No conversations yet</p>
                </div>
              )
            ) : (
              // Contacts Tab
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
                    onClick={() => handleConversationSelect(contact.id, true)}
                    className="mx-3 my-1 p-4 rounded-2xl cursor-pointer transition-all hover:bg-gray-50 dark:hover:bg-gray-700 group relative"
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

                      {/* Send Message Button - Shows on hover */}
                      <Button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleConversationSelect(contact.id, true);
                        }}
                        size="sm"
                        title="Send message"
                        className="opacity-0 group-hover:opacity-100 transition-all duration-200 bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded-lg shadow-sm hover:shadow-md transform hover:scale-105"
                      >
                        <Send className="h-4 w-4" />
                      </Button>
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
          {state.activeConversationId && activeConversation ? (
            <>
              {/* Chat Header */}
              <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-medium ${getAvatarColor(activeConversation.other_user_id)}`}>
                    {getInitials(activeConversation.other_user_name || '')}
                  </div>
                  
                  <div>
                    <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                      {activeConversation.other_user_name}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {activeConversation.other_user_email}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center gap-2">
                  <Button size="sm" className="w-10 h-10 rounded-full p-0 bg-transparent hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400">
                    <Phone className="h-4 w-4" />
                  </Button>
                  <Button size="sm" className="w-10 h-10 rounded-full p-0 bg-transparent hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400">
                    <Video className="h-4 w-4" />
                  </Button>
                  <Button size="sm" className="w-10 h-10 rounded-full p-0 bg-transparent hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-400">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6">
                {state.messages.map(message => (
                  <div
                    key={message.id}
                    className={`flex mb-4 ${message.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                      message.sender_id === user?.id
                        ? 'bg-blue-500 text-white'
                        : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
                    }`}>
                      {message.type === 'file' && message.file_url ? (
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Paperclip className="h-4 w-4" />
                            <span className="text-sm font-medium">{message.file_name}</span>
                          </div>
                          {message.file_size && (
                            <p className="text-xs opacity-75">
                              {(message.file_size / (1024 * 1024)).toFixed(2)} MB
                            </p>
                          )}
                          <a
                            href={`http://localhost:8000${message.file_url}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`inline-block px-3 py-1 text-xs rounded-full border transition-colors ${
                              message.sender_id === user?.id
                                ? 'border-white/30 hover:bg-white/20 text-white'
                                : 'border-gray-300 hover:bg-gray-100 text-gray-700 dark:border-gray-600 dark:hover:bg-gray-700 dark:text-gray-300'
                            }`}
                          >
                            Download
                          </a>
                        </div>
                      ) : (
                        <p className="text-sm">{message.content}</p>
                      )}
                      <p className={`text-xs mt-1 ${
                        message.sender_id === user?.id ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {formatTime(message.created_at)}
                      </p>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-6 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                <div className="flex gap-4 items-end">
                  <div className="flex-1 relative">
                    <Input
                      ref={messageInputRef}
                      type="text"
                      placeholder="Type a message..."
                      value={newMessage}
                      onChange={handleInputChange}
                      onKeyPress={handleKeyPress}
                      className="pr-20 rounded-2xl border-gray-300 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={state.sending}
                    />
                    
                    {/* Emoji and Attachment buttons */}
                    <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex gap-2">
                      <Button
                        type="button"
                        onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                        className="w-8 h-8 p-0 bg-transparent hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700"
                      >
                        <Smile className="h-4 w-4" />
                      </Button>
                      <Button
                        type="button"
                        onClick={handleAttachmentClick}
                        disabled={uploadingFile}
                        className="w-8 h-8 p-0 bg-transparent hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 hover:text-gray-700"
                      >
                        <Paperclip className="h-4 w-4" />
                      </Button>
                    </div>

                    {/* Hidden File Input */}
                    <input
                      ref={fileInputRef}
                      type="file"
                      onChange={handleFileUpload}
                      className="hidden"
                      accept="image/*,audio/*,video/*,.pdf,.doc,.docx,.txt"
                    />

                    {/* Emoji Picker */}
                    {showEmojiPicker && (
                      <div className="absolute bottom-full right-0 mb-2 z-10">
                        <EmojiPicker
                          onEmojiClick={(emojiData) => {
                            setNewMessage(prev => prev + emojiData.emoji);
                            setShowEmojiPicker(false);
                          }}
                          width={300}
                          height={400}
                        />
                      </div>
                    )}
                  </div>
                  <Button 
                    onClick={handleSendMessage}
                    disabled={!newMessage.trim() || state.sending}
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
              </div>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}