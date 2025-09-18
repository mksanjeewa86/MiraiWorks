'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { API_CONFIG } from '@/config/api';
import AppLayout from '@/components/layout/AppLayout';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Search, Send, Smile, Paperclip, RefreshCw, X } from 'lucide-react';
import { messagesApi } from "@/api/messages";
import { usersApi } from "@/api/usersApi";
import type { Conversation, LegacyMessage as Message } from '@/types';
import type { MessagesPageState } from '@/types/pages';
import dynamic from 'next/dynamic';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

const EmojiPicker = dynamic(() => import('emoji-picker-react'), { 
  ssr: false,
  loading: () => <div>Loading...</div>
});

function MessagesPageContent() {
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageInputRef = useRef<HTMLInputElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isPageVisibleRef = useRef(true);
  
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
    hasMoreMessages: false,
    searchResults: [],
    isSearching: false,
    showSearchResults: false,
    showProfileModal: false,
    selectedContactProfile: null
  });

  // Use separate state for input to prevent message list refreshes while typing
  const [newMessage, setNewMessage] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<Array<{
    id: string;
    file_url: string;
    file_name: string;
    file_size: number;
    file_type: string;
  }>>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));
        const response = await messagesApi.getConversations();
        if (response.success && response.data) {
          const conversations = response.data || [];
          setState(prev => ({
            ...prev,
            conversations: conversations,
            loading: false,
            // Auto-select the first conversation (most recent) if none is selected
            activeConversationId: prev.activeConversationId === null && conversations.length > 0 
              ? conversations[0].other_user_id 
              : prev.activeConversationId
          }));
        } else {
          setState(prev => ({ 
            ...prev, 
            error: 'Failed to load conversations',
            loading: false 
          }));
        }
      } catch {
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
          messages: (response.data?.messages || []) as unknown as Message[],
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

  // Page visibility handling
  useEffect(() => {
    const handleVisibilityChange = () => {
      isPageVisibleRef.current = !document.hidden;
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  // Polling for new messages
  useEffect(() => {
    if (!state.activeConversationId || !user) {
      return;
    }

    const pollForMessages = async () => {
      // Only poll when page is visible
      if (!isPageVisibleRef.current) return;
      
      try {
        const response = await messagesApi.getMessages(state.activeConversationId!, 50);
        if (response.success && response.data?.messages) {
          const newMessages = response.data.messages as unknown as Message[];
          
          // Check if we have new messages by comparing lengths
          if (newMessages.length > state.messages.length) {
            setState(prev => ({
              ...prev,
              messages: newMessages,
              hasMoreMessages: response.data?.has_more || false
            }));
            
            // Scroll to bottom if there are new messages
            setTimeout(scrollToBottom, 100);
            
            // Refresh conversation list to update last message
            refreshConversationList();
          }
        }
      } catch (error) {
        // Check for authentication errors and handle them gracefully
        if (error instanceof Error && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
          setState(prev => ({
            ...prev,
            error: 'Session expired. Please refresh the page to continue.',
            loading: false
          }));
        }
      }
    };

    // Initial poll
    pollForMessages();

    // Set up polling interval (every 30 seconds)
    pollingIntervalRef.current = setInterval(pollForMessages, 30000);

    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [state.activeConversationId, state.messages.length, user]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const refreshConversationList = async () => {
    try {
      const response = await messagesApi.getConversations();
      if (response.success && response.data) {
        const serverConversations = response.data || [];

        setState(prev => {
          // Preserve any temporary conversations that might not be on server yet
          const tempConversations = prev.conversations.filter(conv =>
            !serverConversations.some(serverConv => serverConv.other_user_id === conv.other_user_id)
          );

          // Merge server conversations with temporary ones
          const mergedConversations = [...serverConversations, ...tempConversations];

          return {
            ...prev,
            conversations: mergedConversations
          };
        });
      }
    } catch (error) {
      // Silently handle refresh errors
    }
  };

  const handleSendMessage = async () => {
    if ((!newMessage.trim() && attachedFiles.length === 0) || !state.activeConversationId || state.sending) {
      return;
    }

    // Store original values for error restoration
    const originalText = newMessage.trim();
    const filesToSend = [...attachedFiles];

    // Clear input and files immediately for better UX
    setNewMessage('');
    setAttachedFiles([]);
    setState(prev => ({ ...prev, sending: true }));

    try {
      const messagesToSend = [];

      // If there's text, send text message first
      if (originalText) {
        const textContent = filesToSend.length > 0
          ? `${originalText}\n📁 ${filesToSend.length} file(s) attached`
          : originalText;

        messagesToSend.push({
          content: textContent,
          type: 'text' as const
        });
      }

      // Send each file as a separate message
      for (const file of filesToSend) {
        messagesToSend.push({
          content: `📎 ${file.file_name}`,
          type: 'file' as const,
          file_url: file.file_url,
          file_name: file.file_name,
          file_size: file.file_size,
          file_type: file.file_type
        });
      }

      // Send all messages
      const responses: Message[] = [];
      for (const messageData of messagesToSend) {
        const response = await messagesApi.sendMessage(state.activeConversationId, messageData);
        if (response.success && response.data) {
          responses.push(response.data as unknown as Message);
        }
      }

      if (responses.length > 0) {
        // Add all messages to local state
        setState(prev => ({
          ...prev,
          messages: [...prev.messages, ...responses]
        }));

        // Scroll to bottom after sending
        setTimeout(scrollToBottom, 100);

        // Refresh conversation list to update last message
        refreshConversationList();
      }
    } catch (error) {
      setNewMessage(originalText); // Restore original text on error
      setAttachedFiles(filesToSend); // Restore files on error

      // Show user-friendly error message
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      let friendlyMessage = errorMessage;

      if (errorMessage.includes('Super admin can only message company admins')) {
        friendlyMessage = 'As a super admin, you can only send messages to company administrators.';
      } else if (errorMessage.includes('Recipient not found')) {
        friendlyMessage = 'The selected contact is no longer available. Please try selecting a different contact.';
      } else if (errorMessage.includes('not found')) {
        friendlyMessage = 'Contact not found. Please refresh the page and try again.';
      } else if (errorMessage.includes('temporarily unavailable') || errorMessage.includes('not yet implemented')) {
        friendlyMessage = 'Message sending is temporarily unavailable. This feature is currently being developed.';
      }

      setState(prev => ({
        ...prev,
        error: friendlyMessage
      }));
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
    const files = event.target.files;
    if (!files || files.length === 0 || uploadingFile) return;

    // Check if adding these files would exceed the limit
    const selectedFiles = Array.from(files);
    if (attachedFiles.length + selectedFiles.length > 5) {
      setState(prev => ({
        ...prev,
        error: `You can only attach up to 5 files. Currently have ${attachedFiles.length} file(s).`
      }));
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      return;
    }

    setUploadingFile(true);
    try {
      const uploadedFiles: Array<{
        id: string;
        file_url: string;
        file_name: string;
        file_size: number;
        file_type: string;
      }> = [];

      // Upload each file
      for (const file of selectedFiles) {
        const uploadResponse = await messagesApi.uploadFile(file);
        if (!uploadResponse.success || !uploadResponse.data) {
          throw new Error(`Failed to upload ${file.name}`);
        }

        uploadedFiles.push({
          id: Date.now().toString() + Math.random().toString(), // Simple unique ID
          file_url: uploadResponse.data.file_url,
          file_name: uploadResponse.data.file_name,
          file_size: uploadResponse.data.file_size,
          file_type: uploadResponse.data.file_type
        });
      }

      // Add to existing files
      setAttachedFiles(prev => [...prev, ...uploadedFiles]);

    } catch (error) {
      setState(prev => ({
        ...prev,
        error: 'Failed to upload one or more files. Please try again.'
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

  const handleRemoveAttachment = (fileId: string) => {
    setAttachedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  const handleRemoveAllAttachments = () => {
    setAttachedFiles([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setNewMessage(value);
  };

  const handleFileDownload = async (fileUrl: string, fileName?: string) => {
    try {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        setState(prev => ({
          ...prev,
          error: 'Please log in to download files'
        }));
        return;
      }

      const response = await fetch(`${API_CONFIG.BASE_URL}${fileUrl}?download=true`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`Download failed: ${response.status}`);
      }

      // Create blob from response
      const blob = await response.blob();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName || 'download';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error('Download error:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to download file. Please try again.'
      }));
    }
  };

  // Profile modal handlers
  const handleContactProfileView = (contact: { id: number; email: string; full_name: string; company_name?: string }) => {
    setState(prev => ({
      ...prev,
      selectedContactProfile: contact,
      showProfileModal: true
    }));
  };

  const handleCloseProfileModal = () => {
    setState(prev => ({
      ...prev,
      showProfileModal: false,
      selectedContactProfile: null
    }));
  };

  const handleConversationSelect = async (userId: number, fromContact = false) => {
    // Debug: Log the selected contact details
    if (fromContact) {
      const contactExists = state.contacts.find(c => c.id === userId);
      if (!contactExists) {
        setState(prev => ({
          ...prev,
          error: 'This contact is not available for messaging. Please select a different contact.'
        }));
        return;
      }
    }

    // If selecting from contacts, create a temporary conversation entry if it doesn't exist
    if (fromContact) {
      const existingConversation = state.conversations.find(c => c.other_user_id === userId);
      if (!existingConversation) {
        // Find contact info to create temporary conversation entry
        const contactInfo = state.contacts.find(c => c.id === userId);
        if (contactInfo) {
          const tempConversation: Conversation = {
            other_user_id: userId,
            other_user_name: contactInfo.full_name,
            other_user_email: contactInfo.email,
            other_user_company: contactInfo.company_name,
            unread_count: 0,
            last_message: undefined,
            last_activity: new Date().toISOString()
          };

          setState(prev => ({
            ...prev,
            conversations: [tempConversation, ...prev.conversations]
          }));
        }
      }
    }

    // Set the active conversation and switch tabs if needed
    setState(prev => ({
      ...prev,
      activeConversationId: userId,
      messages: [],
      loading: true,
      error: null,
      // If selecting from contacts, switch to conversations tab
      activeTab: fromContact ? 'conversations' : prev.activeTab
    }));

    // Fetch messages for the selected conversation using the userId directly
    try {
      const response = await messagesApi.getMessages(userId, 50);
      if (response.success && response.data) {
        setState(prev => ({
          ...prev,
          messages: (response.data?.messages || []) as unknown as Message[],
          hasMoreMessages: response.data?.has_more || false,
          loading: false
        }));
        setTimeout(scrollToBottom, 100);
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        error: 'Failed to load messages',
        loading: false
      }));
    }

    // Focus message input when selecting a conversation, especially from contacts
    if (fromContact) {
      // Small delay to ensure the tab switch and render is complete
      setTimeout(() => {
        messageInputRef.current?.focus();
      }, 200);

      // Refresh conversations to show the updated conversation list
      // Delay this more to allow the temporary conversation to be established
      setTimeout(() => {
        refreshConversationList();
      }, 2000);
    }
  };

  const handleTabSwitch = async (tab: 'conversations' | 'contacts') => {
    setState(prev => ({ ...prev, activeTab: tab }));

    if (tab === 'contacts' && state.contacts.length === 0) {
      try {
        setState(prev => ({ ...prev, searchingContacts: true, error: null }));

        let participants: Array<{
          id: number;
          email: string;
          full_name: string;
          company_name?: string;
          is_online?: boolean;
        }> = [];

        // First try the regular participants endpoint
        try {
          const response = await messagesApi.searchParticipants();

          if (response.success && response.data) {
            participants = response.data?.participants || [];

            // Filter participants for super admin (same logic as users API)
            if (user?.roles?.some(role => role.role.name === 'super_admin') || user?.id === 7) {
              participants = participants.filter(p => {
                // For now, show participants with company_name (indicating they're company users)
                return p.company_name && p.company_name.trim() !== '';
              });
            }
          }
        } catch (participantsError) {
          // Silently continue to fallback
        }

        // If no participants found, try users API as fallback (especially for admin users)
        if (participants.length === 0) {
          try {
            // Try multiple user queries to find any users
            let usersResponse = await usersApi.getUsers({
              is_active: true,
              size: 100
            });

            // Query 2: If no active users, try all users (non-deleted)
            if (!usersResponse.data?.users?.length) {
              usersResponse = await usersApi.getUsers({
                size: 100,
                include_deleted: false
              });
            }

            // Query 3: If still nothing, try absolutely everything
            if (!usersResponse.data?.users?.length) {
              usersResponse = await usersApi.getUsers({
                size: 100
              });
            }

            if (usersResponse.data?.users?.length) {
              // Convert users to participant format and exclude current user
              let filteredUsers = usersResponse.data.users.filter(u => u.id !== user?.id);

              // For super admin, only show company admins (users who can receive messages)
              // Check multiple ways to identify super admin
              const isSuperAdmin = user?.roles?.some(role => role.role.name === 'super_admin') || user?.id === 7 ||
                                  (user && !user.company_id && user.is_admin); // Super admin typically has no company_id but is admin

              if (isSuperAdmin) {
                filteredUsers = filteredUsers.filter(u => {
                  const isCompanyAdmin = u.roles.includes('company_admin') || u.roles.includes('admin') || (u.is_admin === true && u.company_id);
                  return isCompanyAdmin;
                });
              }

              participants = filteredUsers.map(u => ({
                id: u.id,
                email: u.email,
                full_name: `${u.first_name} ${u.last_name}`,
                company_name: u.company_name || '', // Use company_name field
                is_online: false
              }));
            }
          } catch (usersError) {
            throw usersError;
          }
        }


        setState(prev => ({
          ...prev,
          contacts: participants,
          searchingContacts: false
        }));

      } catch (error) {
        setState(prev => ({
          ...prev,
          searchingContacts: false,
          error: error instanceof Error ? error.message : 'Failed to load contacts'
        }));
      }
    }
  };

  const handleSearch = async (query: string) => {
    setState(prev => ({ ...prev, conversationSearchQuery: query, isSearching: !!query }));

    if (!query.trim()) {
      setState(prev => ({ 
        ...prev, 
        searchResults: [], 
        showSearchResults: false,
        isSearching: false 
      }));
      return;
    }

    try {
      setState(prev => ({ ...prev, isSearching: true }));
      
      // Search messages across all conversations
      const response = await messagesApi.searchMessages(query);
      if (response.success && response.data) {
        setState(prev => ({ 
          ...prev, 
          searchResults: response.data?.messages || [],
          showSearchResults: true,
          isSearching: false
        }));
      }
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        isSearching: false,
        showSearchResults: false 
      }));
    }
  };

  const highlightText = (text: string, query: string) => {
    if (!query.trim()) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) => 
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 dark:bg-yellow-800 rounded px-1">
          {part}
        </mark>
      ) : (
        part
      )
    );
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

  // Create a fallback conversation if we have an active ID but no conversation found
  // This prevents the conversation from disappearing when switching from contacts
  const displayConversation = activeConversation || (state.activeConversationId ? {
    other_user_id: state.activeConversationId,
    other_user_name: state.contacts.find(c => c.id === state.activeConversationId)?.full_name || 'User',
    other_user_email: state.contacts.find(c => c.id === state.activeConversationId)?.email || '',
    other_user_company: state.contacts.find(c => c.id === state.activeConversationId)?.company_name,
    unread_count: 0,
    last_message: undefined,
    last_activity: new Date().toISOString()
  } as Conversation : null);


  if (state.loading) {
    return (
      <AppLayout>
        <div className="h-[calc(100vh-4rem)] flex bg-white dark:bg-gray-900">
          <div className="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              
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
                  value=""
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
                placeholder="Search messages, senders, or content..."
                value={state.conversationSearchQuery}
                onChange={(e) => handleSearch(e.target.value)}
                className="pl-10 bg-gray-50 dark:bg-gray-700 border-0 rounded-xl"
              />
            </div>
          </div>

          {/* Content based on active tab and search state */}
          <div className="flex-1 overflow-y-auto">
            {state.showSearchResults ? (
              // Search Results
              <div>
                <div className="p-3 border-b border-gray-200 dark:border-gray-700 bg-blue-50 dark:bg-blue-900/20">
                  <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100">
                    Search Results ({state.searchResults.length})
                  </h4>
                  <button 
                    onClick={() => setState(prev => ({ 
                      ...prev, 
                      showSearchResults: false, 
                      conversationSearchQuery: '',
                      searchResults: []
                    }))}
                    className="text-xs text-blue-700 dark:text-blue-300 hover:underline"
                  >
                    Clear search
                  </button>
                </div>
                {state.isSearching ? (
                  <div className="flex-1 flex items-center justify-center p-8">
                    <div className="text-center">
                      <LoadingSpinner className="w-6 h-6 mx-auto mb-2" />
                      <p className="text-sm text-gray-500">Searching messages...</p>
                    </div>
                  </div>
                ) : state.searchResults.length > 0 ? (
                  state.searchResults.map(message => (
                    <div
                      key={message.id}
                      onClick={() => {
                        // Navigate to conversation with this message
                        const otherUserId = message.sender_id === user?.id ? message.recipient_id : message.sender_id;
                        if (otherUserId) {
                          handleConversationSelect(otherUserId);
                          setState(prev => ({ ...prev, showSearchResults: false }));
                        }
                      }}
                      className="p-3 cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-gray-700"
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-sm ${getAvatarColor(message.sender_id === user?.id ? message.recipient_id : message.sender_id)}`}>
                          {getInitials(message.sender_id === user?.id ? message.recipient_name : message.sender_name)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <h3 className="font-semibold text-sm truncate" style={{ color: 'var(--text-primary)' }}>
                              {message.sender_id === user?.id ? message.recipient_name : message.sender_name}
                            </h3>
                            <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                              {formatTime(message.created_at)}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                            {highlightText(message.content, state.conversationSearchQuery)}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            {message.sender_id === user?.id ? 'You' : message.sender_name}: 
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-8 text-center">
                    <div className="text-4xl mb-4">🔍</div>
                    <p className="text-gray-500">No messages found for &quot;{state.conversationSearchQuery}&quot;</p>
                  </div>
                )}
              </div>
            ) : state.activeTab === 'conversations' ? (
              // Conversations Tab
              filteredConversations.length > 0 ? (
                filteredConversations.map(conversation => (
                  <div
                    key={conversation.other_user_id}
                    onClick={() => handleConversationSelect(conversation.other_user_id)}
                    className={`p-3 cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-gray-700 ${
                      state.activeConversationId === conversation.other_user_id
                        ? 'bg-blue-50 dark:bg-blue-900/20'
                        : ''
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-sm ${getAvatarColor(conversation.other_user_id)}`}>
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
              ) : state.error ? (
                <div className="p-8 text-center">
                  <div className="text-4xl mb-4">⚠️</div>
                  <p className="text-red-600 dark:text-red-400 mb-2">Error loading contacts</p>
                  <p className="text-sm text-gray-500 mb-4">{state.error}</p>
                  <Button
                    onClick={() => handleTabSwitch('contacts')}
                    size="sm"
                    className="bg-blue-500 hover:bg-blue-600 text-white"
                  >
                    Try Again
                  </Button>
                </div>
              ) : state.contacts.length > 0 ? (
                state.contacts.map(contact => (
                  <div
                    key={contact.id}
                    className="p-3 cursor-pointer transition-colors hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-sm ${getAvatarColor(contact.id)}`}>
                        {getInitials(contact.full_name)}
                      </div>

                      <div
                        className="flex-1 min-w-0 cursor-pointer"
                        onClick={() => handleContactProfileView(contact)}
                      >
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
          {state.activeConversationId && displayConversation ? (
            <>
              {/* Chat Header with refresh button */}
              <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-medium ${getAvatarColor(displayConversation.other_user_id)}`}>
                      {getInitials(displayConversation.other_user_name || '')}
                    </div>

                    <div>
                      <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {displayConversation.other_user_name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {displayConversation.other_user_email}
                      </p>
                    </div>
                  </div>
                  
                  <Button
                    onClick={fetchMessages}
                    variant="ghost"
                    size="sm"
                    className="flex items-center gap-2 text-gray-500 hover:text-gray-700"
                  >
                    <RefreshCw className="h-4 w-4" />
                    <span className="hidden sm:inline">Refresh</span>
                  </Button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6">
                {state.loading ? (
                  <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                      <LoadingSpinner className="w-8 h-8 mx-auto mb-4" />
                      <p className="text-gray-500">Loading messages...</p>
                    </div>
                  </div>
                ) : state.messages.length > 0 ? (
                  state.messages.map(message => (
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
                          <button
                            onClick={() => message.file_url && handleFileDownload(message.file_url, message.file_name)}
                            className={`inline-block px-3 py-1 text-xs rounded-full border transition-colors ${
                              message.sender_id === user?.id
                                ? 'border-white/30 hover:bg-white/20 text-white'
                                : 'border-gray-300 hover:bg-gray-100 text-gray-700 dark:border-gray-600 dark:hover:bg-gray-700 dark:text-gray-300'
                            }`}
                          >
                            Download
                          </button>
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
                  ))
                ) : (
                  <div className="flex-1 flex items-center justify-center">
                    <div className="text-center">
                      <div className="text-6xl mb-4">💬</div>
                      <p className="text-gray-500">Start your conversation!</p>
                      <p className="text-sm text-gray-400 mt-2">Send a message to begin chatting</p>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="p-6 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                {/* Error Display */}
                {state.error && (
                  <div className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg">
                    <div className="flex justify-between items-start">
                      <span>{state.error}</span>
                      <button
                        onClick={() => setState(prev => ({ ...prev, error: null }))}
                        className="text-red-500 hover:text-red-700 ml-2"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                )}

                {/* File Attachments Preview */}
                {attachedFiles.length > 0 && (
                  <div className="mb-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
                        {attachedFiles.length} file(s) attached
                      </span>
                      <button
                        onClick={handleRemoveAllAttachments}
                        className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                        title="Remove all attachments"
                      >
                        Remove all
                      </button>
                    </div>
                    <div className="space-y-2">
                      {attachedFiles.map((file) => (
                        <div key={file.id} className="flex items-center justify-between bg-white dark:bg-blue-800/50 rounded p-2">
                          <div className="flex items-center gap-2 flex-1 min-w-0">
                            <Paperclip className="h-3 w-3 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                            <span className="text-xs font-medium text-blue-900 dark:text-blue-100 truncate">
                              {file.file_name}
                            </span>
                            <span className="text-xs text-blue-600 dark:text-blue-400 flex-shrink-0">
                              ({(file.file_size / (1024 * 1024)).toFixed(2)} MB)
                            </span>
                          </div>
                          <button
                            onClick={() => handleRemoveAttachment(file.id)}
                            className="p-1 hover:bg-blue-100 dark:hover:bg-blue-700 rounded-full transition-colors ml-2"
                            title="Remove this file"
                          >
                            <X className="h-3 w-3 text-blue-600 dark:text-blue-400" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

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
                      multiple
                      value=""
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
                    onClick={() => {
                      handleSendMessage();
                    }}
                    disabled={(!newMessage.trim() && attachedFiles.length === 0) || state.sending}
                    className={`w-12 h-12 rounded-2xl p-0 ${
                      (!newMessage.trim() && attachedFiles.length === 0) || state.sending
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-blue-500 hover:bg-blue-600'
                    }`}
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

      {/* Contact Profile Modal */}
      {state.showProfileModal && state.selectedContactProfile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
            {/* Modal Header */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Contact Profile
              </h3>
              <button
                onClick={handleCloseProfileModal}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Profile Content */}
            <div className="space-y-4">
              {/* Avatar and Name */}
              <div className="flex items-center space-x-4">
                <div className={`w-16 h-16 rounded-full flex items-center justify-center text-white text-lg font-medium ${getAvatarColor(state.selectedContactProfile.id)}`}>
                  {getInitials(state.selectedContactProfile.full_name)}
                </div>
                <div>
                  <h4 className="text-xl font-semibold text-gray-900 dark:text-white">
                    {state.selectedContactProfile.full_name}
                  </h4>
                  <p className="text-gray-500 dark:text-gray-400">
                    {state.selectedContactProfile.email}
                  </p>
                </div>
              </div>

              {/* Company Info */}
              {state.selectedContactProfile.company_name && (
                <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                  <p className="text-sm text-gray-600 dark:text-gray-300">Company</p>
                  <p className="font-medium text-gray-900 dark:text-white">
                    {state.selectedContactProfile.company_name}
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-3 pt-4">
                <Button
                  onClick={() => {
                    handleConversationSelect(state.selectedContactProfile!.id, true);
                    handleCloseProfileModal();
                  }}
                  leftIcon={<Send className="h-4 w-4" />}
                  className="flex-1 bg-blue-500 hover:bg-blue-600 text-white"
                >
                  Send Message
                </Button>
                <Button
                  onClick={handleCloseProfileModal}
                  variant="outline"
                  className="flex-1"
                >
                  Close
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </AppLayout>
  );
}

export default function MessagesPage() {
  return (
    <ProtectedRoute>
      <MessagesPageContent />
    </ProtectedRoute>
  );
}