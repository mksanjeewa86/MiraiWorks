'use client';

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { API_CONFIG } from '@/api/config';
import AppLayout from '@/components/layout/AppLayout';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { LoadingSpinner } from '@/components/ui';
import {
  ChevronLeft,
  Menu,
  Paperclip,
  RefreshCw,
  Reply,
  Search,
  Send,
  Smile,
  X,
} from 'lucide-react';
import { messagesApi } from '@/api/messages';
import { userConnectionsApi } from '@/api/userConnections';
import type { Conversation, LegacyMessage as Message } from '@/types';
import type { MessagesPageState } from '@/types/pages';
import dynamic from 'next/dynamic';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import clsx from 'clsx';

const EmojiPicker = dynamic(
  () => import('emoji-picker-react').then((mod) => ({ default: mod.default })),
  {
    ssr: false,
    loading: () => <div>Loading...</div>,
  }
);

function MessagesPageContent() {
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageInputRef = useRef<HTMLInputElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isPageVisibleRef = useRef(true);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

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
    selectedContactProfile: null,
  });

  // Use separate state for input to prevent message list refreshes while typing
  const [newMessage, setNewMessage] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const [replyingTo, setReplyingTo] = useState<Message | null>(null);
  const [attachedFiles, setAttachedFiles] = useState<
    Array<{
      id: string;
      file_url: string;
      file_name: string;
      file_size: number;
      file_type: string;
    }>
  >([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  const isUserRestricted = useCallback(
    (targetId?: number | null) => {
      if (!targetId) {
        return false;
      }
      // Super admins can message everyone - no restrictions
      return false;
    },
    []
  );

  const allowedConversations = useMemo(
    () =>
      state.conversations.filter((conversation) => !isUserRestricted(conversation.other_user_id)),
    [state.conversations, isUserRestricted]
  );

  const visibleContacts = useMemo(
    () => state.contacts.filter((contact) => !isUserRestricted(contact.id)),
    [state.contacts, isUserRestricted]
  );

  const visibleSearchResults = useMemo(() => {
    return state.searchResults.filter((message) => {
      const otherUserId = message.sender_id === user?.id ? message.recipient_id : message.sender_id;
      return !isUserRestricted(otherUserId ?? null);
    });
  }, [state.searchResults, user, isUserRestricted]);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        const response = await messagesApi.getConversations();
        if (response.success && response.data) {
          const serverConversations = response.data || [];
          const filteredConversations = serverConversations.filter(
            (conv) => !isUserRestricted(conv.other_user_id)
          );
          setState((prev) => ({
            ...prev,
            conversations: filteredConversations,
            loading: false,
            // Auto-select the first conversation (most recent) if none is selected
            activeConversationId:
              prev.activeConversationId === null && filteredConversations.length > 0
                ? filteredConversations[0].other_user_id
                : prev.activeConversationId && isUserRestricted(prev.activeConversationId)
                  ? null
                  : prev.activeConversationId,
          }));
        } else {
          setState((prev) => ({
            ...prev,
            error: 'Failed to load conversations',
            loading: false,
          }));
        }
      } catch {
        setState((prev) => ({
          ...prev,
          error: 'Network error loading conversations',
          loading: false,
        }));
      }
    };

    if (user) {
      fetchConversations();
    }
  }, [user]);

  const scrollToBottom = useCallback(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTo({
        top: messagesContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, []);

  const fetchMessages = useCallback(async () => {
    if (!state.activeConversationId || isUserRestricted(state.activeConversationId)) return;

    try {
      setState((prev) => ({ ...prev, loading: true }));
      const response = await messagesApi.getMessages(state.activeConversationId, 50);
      if (response.success && response.data) {
        setState((prev) => ({
          ...prev,
          messages: (response.data?.messages || []) as unknown as Message[],
          hasMoreMessages: response.data?.has_more || false,
          loading: false,
        }));
        setTimeout(scrollToBottom, 100);
      }
    } catch {
      setState((prev) => ({ ...prev, error: 'Failed to load messages', loading: false }));
    }
  }, [state.activeConversationId, scrollToBottom, isUserRestricted]);

  useEffect(() => {
    if (state.activeConversationId) {
      fetchMessages();
    }
  }, [state.activeConversationId, fetchMessages]);

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

    if (isUserRestricted(state.activeConversationId)) {
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
            setState((prev) => ({
              ...prev,
              messages: newMessages,
              hasMoreMessages: response.data?.has_more || false,
            }));

            // Scroll to bottom if there are new messages
            setTimeout(scrollToBottom, 100);

            // Refresh conversation list to update last message
            refreshConversationList();
          }
        }
      } catch (error) {
        // Check for authentication errors and handle them gracefully
        if (
          error instanceof Error &&
          (error.message.includes('401') || error.message.includes('Unauthorized'))
        ) {
          setState((prev) => ({
            ...prev,
            error: 'Session expired. Please refresh the page to continue.',
            loading: false,
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
  }, [state.activeConversationId, state.messages.length, user, scrollToBottom, isUserRestricted]);

  const refreshConversationList = async () => {
    try {
      const response = await messagesApi.getConversations();
      if (response.success && response.data) {
        const serverConversations = (response.data || []).filter(
          (conv) => !isUserRestricted(conv.other_user_id)
        );

        setState((prev) => {
          // Preserve any temporary conversations that might not be on server yet
          const tempConversations = prev.conversations.filter(
            (conv) =>
              !serverConversations.some(
                (serverConv) => serverConv.other_user_id === conv.other_user_id
              )
          );

          // Merge server conversations with temporary ones
          const mergedConversations = [...serverConversations, ...tempConversations].filter(
            (conv) => !isUserRestricted(conv.other_user_id)
          );

          const nextActiveId =
            prev.activeConversationId && isUserRestricted(prev.activeConversationId)
              ? null
              : prev.activeConversationId;

          return {
            ...prev,
            conversations: mergedConversations,
            activeConversationId: nextActiveId,
          };
        });
      }
    } catch {
      // Silently handle refresh errors
    }
  };

  const handleSendMessage = async () => {
    if (
      (!newMessage.trim() && attachedFiles.length === 0) ||
      !state.activeConversationId ||
      state.sending
    ) {
      return;
    }

    if (isUserRestricted(state.activeConversationId)) {
      setState((prev) => ({
        ...prev,
        error: 'You can only message users you are connected with.',
      }));
      return;
    }

    // Store original values for error restoration
    const originalText = newMessage.trim();
    const filesToSend = [...attachedFiles];
    const originalReplyingTo = replyingTo;

    // Clear input and files immediately for better UX
    setNewMessage('');
    setAttachedFiles([]);
    setReplyingTo(null);
    setState((prev) => ({ ...prev, sending: true }));

    try {
      const messagesToSend = [];

      // If there's text, send text message first
      if (originalText) {
        const textContent =
          filesToSend.length > 0
            ? `${originalText}\nAttached files: ${filesToSend.length}`
            : originalText;

        messagesToSend.push({
          content: textContent,
          type: 'text' as const,
          reply_to_id: replyingTo?.id,
        });
      }

      // Send each file as a separate message
      for (const file of filesToSend) {
        messagesToSend.push({
          content: `File: ${file.file_name}`,
          type: 'file' as const,
          file_url: file.file_url,
          file_name: file.file_name,
          file_size: file.file_size,
          file_type: file.file_type,
          reply_to_id: replyingTo?.id,
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
        setState((prev) => ({
          ...prev,
          messages: [...prev.messages, ...responses],
        }));

        // Scroll to bottom after sending
        setTimeout(scrollToBottom, 100);

        // Refresh conversation list to update last message
        refreshConversationList();
      }
    } catch (error) {
      setNewMessage(originalText); // Restore original text on error
      setAttachedFiles(filesToSend); // Restore files on error
      setReplyingTo(originalReplyingTo); // Restore reply state on error

      // Show user-friendly error message
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      let friendlyMessage = errorMessage;

      if (isUserRestricted(state.activeConversationId)) {
        friendlyMessage = 'You can only message users you are connected with.';
      } else if (errorMessage.includes('You can only message users you are connected with')) {
        friendlyMessage = 'You can only message users you are connected with.';
      } else if (errorMessage.includes('Recipient not found')) {
        friendlyMessage =
          'The selected contact is no longer available. Please try selecting a different contact.';
      } else if (errorMessage.includes('not found')) {
        friendlyMessage = 'Contact not found. Please refresh the page and try again.';
      } else if (
        errorMessage.includes('temporarily unavailable') ||
        errorMessage.includes('not yet implemented')
      ) {
        friendlyMessage =
          'Message sending is temporarily unavailable. This feature is currently being developed.';
      }

      setState((prev) => ({
        ...prev,
        error: friendlyMessage,
      }));
    } finally {
      setState((prev) => ({ ...prev, sending: false }));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    } else if (e.key === 'Escape' && replyingTo) {
      e.preventDefault();
      handleCancelReply();
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0 || uploadingFile) return;

    // Check if adding these files would exceed the limit
    const selectedFiles = Array.from(files);
    if (attachedFiles.length + selectedFiles.length > 5) {
      setState((prev) => ({
        ...prev,
        error: `You can only attach up to 5 files. Currently have ${attachedFiles.length} file(s).`,
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
          file_type: uploadResponse.data.file_type,
        });
      }

      // Add to existing files
      setAttachedFiles((prev) => [...prev, ...uploadedFiles]);
    } catch {
      setState((prev) => ({
        ...prev,
        error: 'Failed to upload one or more files. Please try again.',
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
    setAttachedFiles((prev) => prev.filter((file) => file.id !== fileId));
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
        setState((prev) => ({
          ...prev,
          error: 'Please log in to download files',
        }));
        return;
      }

      const response = await fetch(`${API_CONFIG.BASE_URL}${fileUrl}?download=true`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
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
      setState((prev) => ({
        ...prev,
        error: 'Failed to download file. Please try again.',
      }));
    }
  };

  // Profile modal handlers
  const handleContactProfileView = (contact: {
    id: number;
    email: string;
    full_name: string;
    company_name?: string;
  }) => {
    setState((prev) => ({
      ...prev,
      selectedContactProfile: contact,
      showProfileModal: true,
    }));
  };

  const handleCloseProfileModal = () => {
    setState((prev) => ({
      ...prev,
      showProfileModal: false,
      selectedContactProfile: null,
    }));
  };

  const handleConversationSelect = async (userId: number, fromContact = false) => {
    if (isUserRestricted(userId)) {
      setIsMobileSidebarOpen(false);
      setState((prev) => ({
        ...prev,
        error: 'You can only message users you are connected with.',
      }));
      return;
    }

    // Debug: Log the selected contact details
    if (fromContact) {
      const contactExists = state.contacts.find((c) => c.id === userId);
      if (!contactExists) {
        setState((prev) => ({
          ...prev,
          error: 'This contact is not available for messaging. Please select a different contact.',
        }));
        return;
      }
    }

    // If selecting from contacts, create a temporary conversation entry if it doesn't exist
    if (fromContact) {
      const existingConversation = state.conversations.find((c) => c.other_user_id === userId);
      if (!existingConversation) {
        // Find contact info to create temporary conversation entry
        const contactInfo = state.contacts.find((c) => c.id === userId);
        if (contactInfo) {
          const tempConversation: Conversation = {
            other_user_id: userId,
            other_user_name: contactInfo.full_name,
            other_user_email: contactInfo.email,
            other_user_company: contactInfo.company_name,
            unread_count: 0,
            last_message: undefined,
            last_activity: new Date().toISOString(),
          };

          setState((prev) => ({
            ...prev,
            conversations: [tempConversation, ...prev.conversations],
          }));
        }
      }
    }

    // Close the drawer on mobile once a conversation is chosen
    setIsMobileSidebarOpen(false);

    // Set the active conversation and switch tabs if needed
    setState((prev) => ({
      ...prev,
      activeConversationId: userId,
      messages: [],
      loading: true,
      error: null,
      // If selecting from contacts, switch to conversations tab
      activeTab: fromContact ? 'conversations' : prev.activeTab,
    }));

    // Clear reply state when switching conversations
    setReplyingTo(null);

    // Fetch messages for the selected conversation using the userId directly
    try {
      const response = await messagesApi.getMessages(userId, 50);
      if (response.success && response.data) {
        setState((prev) => ({
          ...prev,
          messages: (response.data?.messages || []) as unknown as Message[],
          hasMoreMessages: response.data?.has_more || false,
          loading: false,
        }));
        setTimeout(scrollToBottom, 100);
      }
    } catch {
      setState((prev) => ({
        ...prev,
        error: 'Failed to load messages',
        loading: false,
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
    setState((prev) => ({ ...prev, activeTab: tab }));

    if (tab === 'contacts' && state.contacts.length === 0) {
      try {
        setState((prev) => ({ ...prev, searchingContacts: true, error: null }));

        // Get connected users from user_connections table
        const response = await userConnectionsApi.getMyConnections();

        if (response.success && response.data) {
          const participants = response.data.map((connectedUser) => ({
            id: connectedUser.id,
            email: connectedUser.email,
            full_name: connectedUser.full_name,
            company_name: connectedUser.company_name || undefined,
            is_online: false,
          }));

          setState((prev) => ({
            ...prev,
            contacts: participants,
            searchingContacts: false,
          }));
        } else {
          setState((prev) => ({
            ...prev,
            contacts: [],
            searchingContacts: false,
          }));
        }
      } catch (error) {
        setState((prev) => ({
          ...prev,
          searchingContacts: false,
          error: error instanceof Error ? error.message : 'Failed to load contacts',
        }));
      }
    }
  };

  const handleSearch = async (query: string) => {
    setState((prev) => ({ ...prev, conversationSearchQuery: query, isSearching: !!query }));

    if (!query.trim()) {
      setState((prev) => ({
        ...prev,
        searchResults: [],
        showSearchResults: false,
        isSearching: false,
      }));
      return;
    }

    try {
      setState((prev) => ({ ...prev, isSearching: true }));

      // Search messages across all conversations
      const response = await messagesApi.searchMessages(query);
      if (response.success && response.data) {
        const matchedMessages = (response.data?.messages || []).filter((message) => {
          const otherUserId =
            message.sender_id === user?.id ? message.recipient_id : message.sender_id;
          return !isUserRestricted(otherUserId ?? null);
        });

        setState((prev) => ({
          ...prev,
          searchResults: matchedMessages,
          showSearchResults: true,
          isSearching: false,
        }));
      }
    } catch {
      setState((prev) => ({
        ...prev,
        isSearching: false,
        showSearchResults: false,
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
      .map((word) => word.charAt(0).toUpperCase())
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
      'bg-red-500',
    ];
    return colors[id % colors.length];
  };

  const findReplyMessage = (replyToId: number): Message | undefined => {
    return state.messages.find((msg) => msg.id === replyToId);
  };

  const handleReplyToMessage = (message: Message) => {
    setReplyingTo(message);
    messageInputRef.current?.focus();
  };

  const handleCancelReply = () => {
    setReplyingTo(null);
  };

  const scrollToMessage = (messageId: number) => {
    const messageElement = document.getElementById(`message-${messageId}`);
    if (messageElement) {
      messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
      // Add highlight animation with a small delay to ensure scroll completes
      setTimeout(() => {
        messageElement.classList.add('highlight-message');
        setTimeout(() => {
          messageElement.classList.remove('highlight-message');
        }, 1500);
      }, 300);
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const filteredConversations = allowedConversations.filter(
    (conversation) =>
      conversation.other_user_name
        ?.toLowerCase()
        .includes(state.conversationSearchQuery.toLowerCase()) ||
      conversation.other_user_email
        ?.toLowerCase()
        .includes(state.conversationSearchQuery.toLowerCase()) ||
      conversation.other_user_company
        ?.toLowerCase()
        .includes(state.conversationSearchQuery.toLowerCase())
  );

  const activeConversation = allowedConversations.find(
    (c) => c.other_user_id === state.activeConversationId
  );

  // Create a fallback conversation if we have an active ID but no conversation found
  // This prevents the conversation from disappearing when switching from contacts
  const displayConversation =
    activeConversation ||
    (state.activeConversationId
      ? ({
          other_user_id: state.activeConversationId,
          other_user_name:
            state.contacts.find((c) => c.id === state.activeConversationId)?.full_name || 'User',
          other_user_email:
            visibleContacts.find((c) => c.id === state.activeConversationId)?.email || '',
          other_user_company: visibleContacts.find((c) => c.id === state.activeConversationId)
            ?.company_name,
          unread_count: 0,
          last_message: undefined,
          last_activity: new Date().toISOString(),
        } as Conversation)
      : null);

  if (state.loading) {
    return (
      <AppLayout>
        <div className="flex h-[calc(100vh-4rem)] items-center justify-center bg-slate-50 dark:bg-gray-950">
          <div className="flex flex-col items-center gap-3 text-center">
            <LoadingSpinner className="h-8 w-8 text-blue-500" />
            <p className="text-sm text-gray-500 dark:text-gray-400">Preparing your messages...</p>
          </div>
        </div>
      </AppLayout>
    );
  }

  const isFatalError =
    state.error &&
    state.conversations.length === 0 &&
    state.messages.length === 0 &&
    !state.loading;

  if (isFatalError) {
    return (
      <AppLayout>
        <div className="flex h-[calc(100vh-4rem)] flex-col items-center justify-center gap-4 bg-slate-50 dark:bg-gray-950">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-3xl font-semibold text-red-600">
            !
          </div>
          <div className="space-y-2 text-center">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              We couldn't load your messages
            </h3>
            <p className="text-sm text-red-500 dark:text-red-400">{state.error}</p>
          </div>
          <Button
            onClick={() => window.location.reload()}
            leftIcon={<RefreshCw className="h-4 w-4" />}
          >
            Try again
          </Button>
        </div>
      </AppLayout>
    );
  }

  const sidebarClassName = clsx(
    'fixed inset-y-0 left-0 z-40 flex w-full max-w-xs flex-col overflow-hidden bg-white dark:bg-gray-900 shadow-xl transition-transform duration-200 md:static md:z-auto md:w-80 md:translate-x-0 md:shadow-none md:border-r md:border-gray-200 md:dark:border-gray-800',
    isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
  );
  return (
    <AppLayout>
      <style jsx global>{`
        html, body {
          overflow: hidden !important;
          height: 100vh;
        }

        @keyframes highlightJump {
          0% {
            background-color: transparent;
            transform: scale(1);
          }
          10% {
            background-color: rgba(59, 130, 246, 0.3);
            transform: scale(1.02);
          }
          20% {
            transform: scale(0.98);
          }
          30% {
            transform: scale(1.01);
          }
          40% {
            transform: scale(1);
          }
          60% {
            background-color: rgba(59, 130, 246, 0.3);
          }
          100% {
            background-color: transparent;
            transform: scale(1);
          }
        }

        .highlight-message {
          animation: highlightJump 1.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
      `}</style>
      <div className="relative flex h-[calc(100vh-80px)] -mx-6 -mb-6 flex-col overflow-hidden bg-slate-50 dark:bg-gray-950 md:flex-row">
        {isMobileSidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm md:hidden"
            onClick={() => setIsMobileSidebarOpen(false)}
            aria-hidden="true"
          />
        )}
        {/* WhatsApp-style Sidebar */}
        <aside className={sidebarClassName}>
          <div className="flex h-full flex-col bg-white">
            {/* WhatsApp-style Sidebar Header */}
            <div className="flex items-center justify-between bg-[#F0F0F0] px-4 py-3">
              <h2 className="text-xl font-semibold text-gray-800">
                Chats
              </h2>
              <button
                type="button"
                className="inline-flex h-9 w-9 items-center justify-center rounded-full text-gray-600 transition hover:bg-gray-200 md:hidden"
                onClick={() => setIsMobileSidebarOpen(false)}
                aria-label="Close conversations panel"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
            </div>

            {/* Search Bar */}
            <div className="border-b border-gray-200 px-3 py-2">
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
                <Input
                  type="text"
                  placeholder="Search or start new chat"
                  value={state.conversationSearchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="w-full rounded-lg border-none bg-[#F0F0F0] py-2 pl-10 pr-4 text-sm text-gray-800 focus:outline-none focus:ring-0"
                />
              </div>
            </div>

            {/* WhatsApp-style Tabs */}
            <div className="flex border-b border-gray-200">
              <button
                onClick={() => handleTabSwitch('conversations')}
                className={clsx(
                  'flex-1 py-3 text-sm font-medium transition-colors relative',
                  state.activeTab === 'conversations'
                    ? 'text-[#075E54]'
                    : 'text-gray-500 hover:text-gray-700'
                )}
              >
                Chats
                {state.activeTab === 'conversations' && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#075E54]" />
                )}
              </button>
              <button
                onClick={() => handleTabSwitch('contacts')}
                className={clsx(
                  'flex-1 py-3 text-sm font-medium transition-colors relative',
                  state.activeTab === 'contacts'
                    ? 'text-[#075E54]'
                    : 'text-gray-500 hover:text-gray-700'
                )}
              >
                Contacts
                {state.activeTab === 'contacts' && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#075E54]" />
                )}
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-3 pb-6 pt-4">
              {state.showSearchResults ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-between rounded-2xl border border-blue-100 bg-blue-50/70 px-4 py-3 dark:border-blue-900/40 dark:bg-blue-900/30">
                    <div>
                      <h4 className="text-sm font-semibold text-blue-900 dark:text-blue-100">
                        Search results ({visibleSearchResults.length})
                      </h4>
                      <p className="text-xs text-blue-700/80 dark:text-blue-200/80">
                        Matching messages across your inbox
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={() =>
                        setState((prev) => ({
                          ...prev,
                          showSearchResults: false,
                          conversationSearchQuery: '',
                          searchResults: [],
                        }))
                      }
                      className="text-xs font-semibold text-blue-700 hover:underline dark:text-blue-200"
                    >
                      Clear
                    </button>
                  </div>
                  {state.isSearching ? (
                    <div className="flex h-40 items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-white/80 dark:border-gray-700 dark:bg-gray-900/40">
                      <div className="flex flex-col items-center gap-2 text-sm text-gray-500 dark:text-gray-300">
                        <LoadingSpinner className="h-5 w-5" />
                        Searching messages...
                      </div>
                    </div>
                  ) : visibleSearchResults.length > 0 ? (
                    visibleSearchResults.map((message) => (
                      <button
                        key={message.id}
                        type="button"
                        onClick={() => {
                          const otherUserId =
                            message.sender_id === user?.id
                              ? message.recipient_id
                              : message.sender_id;
                          if (otherUserId) {
                            handleConversationSelect(otherUserId);
                            setState((prev) => ({ ...prev, showSearchResults: false }));
                          }
                        }}
                        className="w-full rounded-2xl border border-transparent bg-white p-4 text-left shadow-sm transition hover:border-blue-200 hover:bg-blue-50 dark:bg-gray-900 dark:hover:border-blue-500/40 dark:hover:bg-gray-800"
                      >
                        <div className="flex items-start gap-3">
                          <div
                            className={`flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold text-white ${getAvatarColor(message.sender_id === user?.id ? message.recipient_id : message.sender_id)}`}
                          >
                            {getInitials(
                              message.sender_id === user?.id
                                ? message.recipient_name
                                : message.sender_name
                            )}
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center justify-between">
                              <h3 className="truncate text-sm font-semibold text-gray-900 dark:text-gray-100">
                                {message.sender_id === user?.id
                                  ? message.recipient_name
                                  : message.sender_name}
                              </h3>
                              <span className="text-xs text-gray-400">
                                {formatTime(message.created_at)}
                              </span>
                            </div>
                            <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                              {highlightText(message.content, state.conversationSearchQuery)}
                            </p>
                            <p className="mt-2 text-xs uppercase tracking-wide text-gray-400">
                              {message.sender_id === user?.id ? 'You' : message.sender_name}
                            </p>
                          </div>
                        </div>
                      </button>
                    ))
                  ) : (
                    <div className="flex flex-col items-center gap-2 rounded-2xl border border-dashed border-gray-300 px-4 py-8 text-center text-sm text-gray-500 dark:border-gray-700 dark:text-gray-400">
                      <Search className="h-8 w-8 text-gray-400" />
                      <p>No messages found for "{state.conversationSearchQuery}"</p>
                    </div>
                  )}
                </div>
              ) : state.activeTab === 'conversations' ? (
                filteredConversations.length > 0 ? (
                  <div className="space-y-0">
                    {filteredConversations.map((conversation) => (
                      <button
                        key={conversation.other_user_id}
                        type="button"
                        onClick={() => handleConversationSelect(conversation.other_user_id)}
                        className={clsx(
                          'w-full group relative flex items-center gap-3 py-3 px-4 transition-colors text-left border-b border-gray-100',
                          state.activeConversationId === conversation.other_user_id
                            ? 'bg-[#F0F0F0]'
                            : 'hover:bg-[#F5F5F5]'
                        )}
                      >
                        {/* Avatar */}
                        <div className="relative flex-shrink-0">
                          <div
                            className={`flex h-12 w-12 items-center justify-center rounded-full text-sm font-semibold text-white ${getAvatarColor(conversation.other_user_id)}`}
                          >
                            {getInitials(conversation.other_user_name || '')}
                          </div>
                          {conversation.unread_count > 0 && (
                            <div className="absolute -right-1 -top-1 flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-[#25D366] px-1.5 text-[11px] font-bold text-white">
                              {conversation.unread_count > 9 ? '9+' : conversation.unread_count}
                            </div>
                          )}
                        </div>

                        {/* Content */}
                        <div className="min-w-0 flex-1">
                          <div className="flex items-baseline justify-between gap-2 mb-1">
                            <h3 className="truncate text-[15px] font-medium text-gray-900">
                              {conversation.other_user_name}
                            </h3>
                            {conversation.last_message && (
                              <span className="flex-shrink-0 text-[12px] text-gray-500">
                                {formatTime(conversation.last_message.created_at)}
                              </span>
                            )}
                          </div>
                          <p className="truncate text-[13px] leading-tight text-gray-500">
                            {conversation.last_message ? (
                              <>
                                {conversation.last_message.sender_id === user?.id && (
                                  <span className="text-gray-500">
                                    <svg className="inline w-4 h-4 mr-1 -mt-0.5" fill="currentColor" viewBox="0 0 16 15">
                                      <path d="M15.01 3.316l-.478-.372a.365.365 0 0 0-.51.063L8.666 9.879a.32.32 0 0 1-.484.033l-.358-.325a.319.319 0 0 0-.484.032l-.378.483a.418.418 0 0 0 .036.541l1.32 1.266c.143.14.361.125.484-.033l6.272-8.048a.366.366 0 0 0-.064-.512zm-4.1 0l-.478-.372a.365.365 0 0 0-.51.063L4.566 9.879a.32.32 0 0 1-.484.033L1.891 7.769a.366.366 0 0 0-.515.006l-.423.433a.364.364 0 0 0 .006.514l3.258 3.185c.143.14.361.125.484-.033l6.272-8.048a.365.365 0 0 0-.063-.51z"/>
                                    </svg>
                                  </span>
                                )}
                                {conversation.last_message.content}
                              </>
                            ) : (
                              <span className="text-gray-400">Click to start chatting</span>
                            )}
                          </p>
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="flex h-full flex-col items-center justify-center gap-3 px-4 py-10 text-center">
                    <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
                      <svg className="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </div>
                    <p className="text-sm text-gray-600">No conversations yet</p>
                    <p className="text-xs text-gray-400">
                      Start by messaging a contact
                    </p>
                  </div>
                )
              ) : state.searchingContacts ? (
                <div className="flex h-full flex-col items-center justify-center gap-3 px-4 py-10 text-center">
                  <LoadingSpinner className="h-6 w-6 text-gray-400" />
                  <p className="text-sm text-gray-600">Loading contacts...</p>
                </div>
              ) : visibleContacts.length > 0 ? (
                <div className="space-y-0">
                  {visibleContacts.map((contact) => (
                    <button
                      key={contact.id}
                      type="button"
                      onClick={() => handleConversationSelect(contact.id, true)}
                      className="group relative flex w-full items-center gap-3 py-3 px-4 text-left transition-colors border-b border-gray-100 hover:bg-[#F5F5F5]"
                    >
                      {/* Avatar */}
                      <div className="relative flex-shrink-0">
                        <div
                          className={`flex h-12 w-12 items-center justify-center rounded-full text-sm font-semibold text-white ${getAvatarColor(contact.id)}`}
                        >
                          {getInitials(contact.full_name)}
                        </div>
                      </div>

                      {/* Content */}
                      <div className="min-w-0 flex-1">
                        <h3 className="truncate text-[15px] font-medium text-gray-900">
                          {contact.full_name}
                        </h3>
                        <p className="truncate text-[13px] leading-tight text-gray-500">
                          {contact.company_name || contact.email}
                        </p>
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <div className="flex h-full flex-col items-center justify-center gap-3 px-4 py-10 text-center">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-100">
                    <svg className="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                  <p className="text-sm text-gray-600">No contacts found</p>
                </div>
              )}
            </div>
          </div>
        </aside>
        <main className="flex flex-1 flex-col overflow-hidden bg-white dark:bg-gray-900 min-h-0">
          {state.activeConversationId && displayConversation ? (
            <>
              {/* WhatsApp-style Header */}
              <header className="flex items-center justify-between bg-[#075E54] px-4 py-3 sm:px-6">
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    className="inline-flex h-10 w-10 items-center justify-center rounded-full text-white transition hover:bg-white/10 md:hidden"
                    onClick={() => setIsMobileSidebarOpen(true)}
                    aria-label="Open conversations panel"
                  >
                    <Menu className="h-5 w-5" />
                  </button>
                  <div
                    className={`h-10 w-10 items-center justify-center rounded-full text-sm font-semibold text-white flex ${getAvatarColor(displayConversation.other_user_id)}`}
                  >
                    {getInitials(displayConversation.other_user_name || '')}
                  </div>
                  <div>
                    <p className="text-base font-medium text-white">
                      {displayConversation.other_user_name}
                    </p>
                    <p className="text-xs text-white/80">
                      {displayConversation.other_user_email}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    onClick={fetchMessages}
                    variant="ghost"
                    size="sm"
                    className="h-10 w-10 rounded-full p-0 text-white hover:bg-white/10"
                    title="Refresh"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </Button>
                </div>
              </header>

              {/* WhatsApp-style Chat Background */}
              <div className="flex flex-1 flex-col overflow-hidden min-h-0 bg-[#E5DDD5]">
                <div
                  ref={messagesContainerRef}
                  className="flex-1 overflow-y-auto px-4 py-6 sm:px-8"
                  style={{
                    backgroundImage:
                      'url("data:image/svg+xml,%3Csvg width=\'100\' height=\'100\' viewBox=\'0 0 100 100\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cpath d=\'M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z\' fill=\'%23d9d9d9\' fill-opacity=\'0.1\' fill-rule=\'evenodd\'/%3E%3C/svg%3E")',
                    backgroundColor: '#E5DDD5',
                  }}
                >
                  {state.messages.length === 0 ? (
                    <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
                      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/80 shadow-lg">
                        <svg className="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                      </div>
                      <p className="text-base font-semibold text-gray-700">
                        Start a conversation
                      </p>
                      <p className="text-sm text-gray-500">
                        Send a message to begin chatting
                      </p>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-1.5">
                      {state.messages.map((message) => {
                        const repliedMessage = (message as any).reply_to_id
                          ? findReplyMessage((message as any).reply_to_id)
                          : undefined;
                        const isOwnMessage = message.sender_id === user?.id;
                        const senderName =
                          message.sender_id === user?.id
                            ? 'You'
                            : message.sender_name ||
                              state.conversations.find((c) => c.other_user_id === message.sender_id)
                                ?.other_user_name ||
                              'User';

                        return (
                          <div
                            key={message.id}
                            id={`message-${message.id}`}
                            className={clsx(
                              'flex animate-fade-in gap-2 transition-all duration-300',
                              isOwnMessage ? 'justify-end' : 'justify-start'
                            )}
                          >
                            <div
                              className={clsx(
                                'flex gap-2 max-w-[75%] sm:max-w-[65%]',
                                isOwnMessage ? 'flex-row-reverse items-end' : 'flex-row items-start'
                              )}
                            >
                              {/* Avatar */}
                              <div className="flex-shrink-0">
                                <div
                                  className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold text-white ${
                                    isOwnMessage
                                      ? getAvatarColor(user?.id || 0)
                                      : getAvatarColor(message.sender_id)
                                  }`}
                                >
                                  {isOwnMessage
                                    ? getInitials(user?.full_name || 'You')
                                    : getInitials(senderName)}
                                </div>
                              </div>

                              {/* Message bubble */}
                              <div className="relative group overflow-visible">
                                <div
                                  className={clsx(
                                    'relative px-3 py-2 shadow-md rounded-lg max-w-full',
                                    isOwnMessage
                                      ? 'bg-[#DCF8C6] text-gray-900'
                                      : 'bg-white text-gray-900'
                                  )}
                                >
                                {repliedMessage && (
                                  <div
                                    onClick={() => scrollToMessage(repliedMessage.id)}
                                    className={clsx(
                                      'mb-3 rounded-lg border-l-4 px-3 py-2 text-xs cursor-pointer transition-all hover:opacity-80',
                                      isOwnMessage
                                        ? 'border-green-600 bg-green-700/20 text-gray-800'
                                        : 'border-gray-400 bg-gray-100 text-gray-800'
                                    )}
                                  >
                                    <p className="font-semibold text-gray-900">
                                      {repliedMessage.sender_id === user?.id
                                        ? 'You'
                                        : state.conversations.find(
                                            (c) => c.other_user_id === repliedMessage.sender_id
                                          )?.other_user_name ||
                                          repliedMessage.sender_name ||
                                          'User'}
                                    </p>
                                    <p className="mt-1 text-gray-700 line-clamp-2">
                                      {repliedMessage.type === 'file'
                                        ? `File: ${repliedMessage.file_name}`
                                        : repliedMessage.content}
                                    </p>
                                  </div>
                                )}

                                  {/* Message Content with inline timestamp */}
                                  <div className="text-[14.2px] leading-[19px]">
                                    {message.type === 'file' && message.file_url ? (
                                      <div className="flex flex-col gap-3 min-w-[250px]">
                                        <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                                          <div className="flex-shrink-0 flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg">
                                            <Paperclip className="h-5 w-5 text-blue-600" />
                                          </div>
                                          <div className="flex-1 min-w-0">
                                            <p className="font-medium text-gray-900 text-sm truncate">{message.file_name || 'Attached File'}</p>
                                            {message.file_size && (
                                              <p className="text-xs text-gray-500 mt-0.5">
                                                {(message.file_size / (1024 * 1024)).toFixed(2)} MB
                                              </p>
                                            )}
                                          </div>
                                        </div>
                                        <button
                                          onClick={() =>
                                            message.file_url &&
                                            handleFileDownload(message.file_url, message.file_name)
                                          }
                                          className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 transition-colors"
                                        >
                                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                          </svg>
                                          Download File
                                        </button>
                                        {/* Timestamp for file messages */}
                                        <div className="flex items-center gap-1 text-[11px] text-gray-500">
                                          {formatTime(message.created_at)}
                                          {isOwnMessage && (
                                            <svg className="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 16 15">
                                              <path d="M15.01 3.316l-.478-.372a.365.365 0 0 0-.51.063L8.666 9.879a.32.32 0 0 1-.484.033l-.358-.325a.319.319 0 0 0-.484.032l-.378.483a.418.418 0 0 0 .036.541l1.32 1.266c.143.14.361.125.484-.033l6.272-8.048a.366.366 0 0 0-.064-.512zm-4.1 0l-.478-.372a.365.365 0 0 0-.51.063L4.566 9.879a.32.32 0 0 1-.484.033L1.891 7.769a.366.366 0 0 0-.515.006l-.423.433a.364.364 0 0 0 .006.514l3.258 3.185c.143.14.361.125.484-.033l6.272-8.048a.365.365 0 0 0-.063-.51z"/>
                                            </svg>
                                          )}
                                        </div>
                                      </div>
                                    ) : (
                                      <div className="inline">
                                        <span className="whitespace-pre-wrap">{message.content}</span>
                                        {/* WhatsApp-style inline timestamp */}
                                        <span className="inline-flex items-center gap-1 ml-2 text-[11px] text-gray-500 whitespace-nowrap align-bottom">
                                          {formatTime(message.created_at)}
                                          {isOwnMessage && (
                                            <svg className="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 16 15">
                                              <path d="M15.01 3.316l-.478-.372a.365.365 0 0 0-.51.063L8.666 9.879a.32.32 0 0 1-.484.033l-.358-.325a.319.319 0 0 0-.484.032l-.378.483a.418.418 0 0 0 .036.541l1.32 1.266c.143.14.361.125.484-.033l6.272-8.048a.366.366 0 0 0-.064-.512zm-4.1 0l-.478-.372a.365.365 0 0 0-.51.063L4.566 9.879a.32.32 0 0 1-.484.033L1.891 7.769a.366.366 0 0 0-.515.006l-.423.433a.364.364 0 0 0 .006.514l3.258 3.185c.143.14.361.125.484-.033l6.272-8.048a.365.365 0 0 0-.063-.51z"/>
                                            </svg>
                                          )}
                                        </span>
                                      </div>
                                    )}
                                  </div>
                                </div>

                                {/* Reply Button */}
                                {!isOwnMessage && (
                                  <button
                                    onClick={() => handleReplyToMessage(message)}
                                    className="absolute -right-4 top-1 hidden h-8 w-8 items-center justify-center rounded-full bg-white text-gray-400 shadow-lg transition hover:text-gray-600 group-hover:flex dark:bg-gray-700 dark:text-gray-300 dark:hover:text-white"
                                    title="Reply to this message"
                                  >
                                    <Reply className="h-3.5 w-3.5" />
                                  </button>
                                )}
                              </div>
                            </div>
                          </div>
                        );
                      })}
                      <div ref={messagesEndRef} />
                    </div>
                  )}
                </div>

                {/* WhatsApp-style Input Area */}
                <div className="bg-[#F0F0F0] px-3 py-2 sm:px-4">
                  {replyingTo && (
                    <div className="mb-2 rounded-lg bg-white px-3 py-2 text-sm shadow-sm">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 text-gray-700">
                            <Reply className="h-3.5 w-3.5" />
                            <span className="text-xs font-semibold">
                              {replyingTo.sender_id === user?.id
                                ? 'You'
                                : state.conversations.find(
                                    (c) => c.other_user_id === replyingTo.sender_id
                                  )?.other_user_name || 'User'}
                            </span>
                          </div>
                          <p className="mt-1 text-xs text-gray-600 line-clamp-1">
                            {replyingTo.type === 'file'
                              ? `File: ${replyingTo.file_name}`
                              : replyingTo.content}
                          </p>
                        </div>
                        <button
                          onClick={handleCancelReply}
                          className="rounded-full p-1 text-gray-500 transition hover:bg-gray-100"
                        >
                          <X className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </div>
                  )}

                  {state.error && (
                    <div className="mb-2 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600">
                      <div className="flex items-start justify-between gap-2">
                        <span>{state.error}</span>
                        <button
                          onClick={() => setState((prev) => ({ ...prev, error: null }))}
                          className="text-xs font-semibold hover:underline"
                        >
                          ×
                        </button>
                      </div>
                    </div>
                  )}

                  {/* File Attachments Preview */}
                  {attachedFiles.length > 0 && (
                    <div className="mb-2 rounded-lg bg-white px-3 py-2 shadow-sm">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-semibold text-gray-700">
                          Attached Files ({attachedFiles.length})
                        </span>
                        <button
                          onClick={handleRemoveAllAttachments}
                          className="text-xs font-semibold text-red-600 hover:underline"
                        >
                          Remove All
                        </button>
                      </div>
                      <div className="space-y-2">
                        {attachedFiles.map((file) => (
                          <div
                            key={file.id}
                            className="flex items-center gap-2 p-2 bg-gray-50 rounded border border-gray-200"
                          >
                            <div className="flex-shrink-0 flex items-center justify-center w-8 h-8 bg-blue-100 rounded">
                              <Paperclip className="h-4 w-4 text-blue-600" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-xs font-medium text-gray-900 truncate">
                                {file.file_name}
                              </p>
                              <p className="text-xs text-gray-500">
                                {(file.file_size / (1024 * 1024)).toFixed(2)} MB
                              </p>
                            </div>
                            <button
                              onClick={() => handleRemoveAttachment(file.id)}
                              className="flex-shrink-0 rounded-full p-1 text-red-600 hover:bg-red-50 transition"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex items-end gap-2">
                    <div className="relative flex-1">
                      <Input
                        ref={messageInputRef}
                        type="text"
                        placeholder="Type a message"
                        value={newMessage}
                        onChange={handleInputChange}
                        onKeyPress={handleKeyPress}
                        className="w-full rounded-full border-none bg-white py-2.5 pl-4 pr-20 text-sm text-gray-900 shadow-sm focus:outline-none focus:ring-0"
                        disabled={state.sending}
                      />
                      <div className="absolute right-2 top-1/2 flex -translate-y-1/2 gap-1">
                        <button
                          type="button"
                          onClick={handleAttachmentClick}
                          disabled={uploadingFile}
                          className="rounded-full p-1.5 text-gray-600 transition hover:bg-gray-100 disabled:opacity-40"
                        >
                          <Paperclip className="h-5 w-5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                          className="rounded-full p-1.5 text-gray-600 transition hover:bg-gray-100"
                        >
                          <Smile className="h-5 w-5" />
                        </button>
                      </div>

                      <input
                        ref={fileInputRef}
                        type="file"
                        onChange={handleFileUpload}
                        className="hidden"
                        accept="image/*,audio/*,video/*,.pdf,.doc,.docx,.txt"
                        multiple
                      />

                      {showEmojiPicker && (
                        <div className="absolute bottom-full right-0 mb-2 rounded-2xl border border-gray-200 bg-white p-2 shadow-xl">
                          <EmojiPicker
                            onEmojiClick={(emojiData) => {
                              setNewMessage((prev) => prev + emojiData.emoji);
                              setShowEmojiPicker(false);
                            }}
                            width={320}
                            height={420}
                          />
                        </div>
                      )}
                    </div>
                    <button
                      onClick={handleSendMessage}
                      disabled={
                        (!newMessage.trim() && attachedFiles.length === 0) || state.sending
                      }
                      className={clsx(
                        'flex h-11 w-11 items-center justify-center rounded-full transition',
                        (!newMessage.trim() && attachedFiles.length === 0) || state.sending
                          ? 'bg-gray-300 text-gray-500'
                          : 'bg-[#25D366] text-white hover:bg-[#20BA5A]'
                      )}
                    >
                      {state.sending ? (
                        <LoadingSpinner className="h-5 w-5" />
                      ) : (
                        <Send className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="flex flex-1 flex-col items-center justify-center gap-3 px-6 text-center">
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-blue-50 text-3xl font-semibold text-blue-500">
                :)
              </div>
              <h3 className="text-2xl font-semibold text-gray-800 dark:text-gray-100">
                Pick a conversation
              </h3>
              <p className="max-w-sm text-sm text-gray-500 dark:text-gray-400">
                Open the inbox to select an existing thread or start messaging a contact from the
                list.
              </p>
              <Button
                onClick={() => setIsMobileSidebarOpen(true)}
                className="mt-2 rounded-full bg-blue-500 px-6 py-2 text-sm font-semibold text-white hover:bg-blue-600 md:hidden"
              >
                Browse conversations
              </Button>
            </div>
          )}
        </main>
      </div>

      {state.showProfileModal && state.selectedContactProfile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl dark:bg-gray-800">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Contact profile
              </h3>
              <button
                onClick={handleCloseProfileModal}
                className="rounded-full p-2 text-gray-400 transition hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-700 dark:hover:text-gray-200"
                aria-label="Close profile"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="mt-6 space-y-5">
              <div className="flex items-center gap-4">
                <div
                  className={`flex h-16 w-16 items-center justify-center rounded-full text-lg font-semibold text-white ${getAvatarColor(state.selectedContactProfile.id)}`}
                >
                  {getInitials(state.selectedContactProfile.full_name)}
                </div>
                <div>
                  <p className="text-xl font-semibold text-gray-900 dark:text-white">
                    {state.selectedContactProfile.full_name}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-300">
                    {state.selectedContactProfile.email}
                  </p>
                </div>
              </div>

              {state.selectedContactProfile.company_name && (
                <div className="rounded-2xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/60">
                  <p className="text-xs uppercase tracking-wide text-gray-400">Company</p>
                  <p className="mt-2 font-medium text-gray-900 dark:text-gray-100">
                    {state.selectedContactProfile.company_name}
                  </p>
                </div>
              )}

              <div className="flex gap-3">
                <Button
                  onClick={() => {
                    handleConversationSelect(state.selectedContactProfile!.id, true);
                    handleCloseProfileModal();
                  }}
                  leftIcon={<Send className="h-4 w-4" />}
                  className="flex-1 rounded-full bg-blue-500 py-2 text-sm font-semibold text-white hover:bg-blue-600"
                >
                  Send message
                </Button>
                <Button
                  onClick={handleCloseProfileModal}
                  variant="outline"
                  className="flex-1 rounded-full py-2 text-sm"
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
