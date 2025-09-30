'use client';

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { API_CONFIG } from '@/api/config';
import AppLayout from '@/components/layout/AppLayout';
import Button from '@/components/ui/button';
import Input from '@/components/ui/input';
import LoadingSpinner from '@/components/ui/loading-spinner';
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
import { usersApi } from '@/api/users';
import type { Conversation, LegacyMessage as Message } from '@/types';
import type { MessagesPageState } from '@/types/pages';
import dynamic from 'next/dynamic';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import clsx from 'clsx';

const EmojiPicker = dynamic(() => import('emoji-picker-react').then(mod => ({ default: mod.default })), {
  ssr: false,
  loading: () => <div>Loading...</div>,
});

function MessagesPageContent() {
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messageInputRef = useRef<HTMLInputElement>(null);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const isPageVisibleRef = useRef(true);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [superAdminIds, setSuperAdminIds] = useState<number[]>([]);

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
  const isSuperAdminUser = useMemo(() => {
    if (!user) {
      return false;
    }

    const rawRoles = (user as { roles?: unknown[] })?.roles || [];
    const normalizedRoles = Array.isArray(rawRoles)
      ? rawRoles.map((role) => {
          if (typeof role === 'string') {
            return role;
          }
          if (role && typeof role === 'object' && 'role' in (role as Record<string, unknown>)) {
            return (role as { role?: { name?: string } }).role?.name;
          }
          return undefined;
        })
      : [];

    return Boolean(normalizedRoles.some((name) => name === 'super_admin') || user?.id === 7);
  }, [user]);

  const superAdminIdSet = useMemo(() => new Set(superAdminIds), [superAdminIds]);
  const superAdminKey = useMemo(
    () =>
      superAdminIds
        .slice()
        .sort((a, b) => a - b)
        .join(','),
    [superAdminIds]
  );

  const isUserRestricted = useCallback(
    (targetId?: number | null) => {
      if (!targetId) {
        return false;
      }
      if (isSuperAdminUser) {
        return true;
      }
      return superAdminIdSet.has(targetId);
    },
    [isSuperAdminUser, superAdminIdSet]
  );

  const allowedConversations = useMemo(
    () =>
      state.conversations.filter((conversation) => !isUserRestricted(conversation.other_user_id)),
    [state.conversations, isUserRestricted]
  );

  const visibleContacts = useMemo(
    () =>
      isSuperAdminUser ? [] : state.contacts.filter((contact) => !isUserRestricted(contact.id)),
    [isSuperAdminUser, state.contacts, isUserRestricted]
  );

  const visibleSearchResults = useMemo(() => {
    return state.searchResults.filter((message) => {
      const otherUserId = message.sender_id === user?.id ? message.recipient_id : message.sender_id;
      return !isUserRestricted(otherUserId ?? null);
    });
  }, [state.searchResults, user, isUserRestricted]);

  const isActiveConversationRestricted = useMemo(
    () => isUserRestricted(state.activeConversationId),
    [isUserRestricted, state.activeConversationId]
  );

  const messagingDisabledCopy = 'Messaging with super administrator accounts is disabled.';

  useEffect(() => {
    if (!user) {
      return;
    }

    const loadRestrictedUsers = async () => {
      try {
        const response = await messagesApi.getRestrictedUserIds();
        if (response.success && response.data?.restricted_user_ids) {
          setSuperAdminIds(response.data.restricted_user_ids);
        }
      } catch (error) {
        console.error('Failed to load restricted user list', error);
      }
    };

    loadRestrictedUsers();
  }, [user]);

  useEffect(() => {
    if (state.activeConversationId && isUserRestricted(state.activeConversationId)) {
      setState((prev) => ({
        ...prev,
        activeConversationId: null,
        messages: [],
      }));
    }
  }, [isUserRestricted, state.activeConversationId]);

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
  }, [user, superAdminKey]);

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
        error: messagingDisabledCopy,
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
        friendlyMessage = messagingDisabledCopy;
      } else if (errorMessage.includes('Super admin can only message company admins')) {
        friendlyMessage = messagingDisabledCopy;
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
        error: messagingDisabledCopy,
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
      if (isSuperAdminUser) {
        setState((prev) => ({ ...prev, contacts: [], searchingContacts: false }));
        return;
      }

      try {
        setState((prev) => ({ ...prev, searchingContacts: true, error: null }));

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
            if (user?.roles?.some((role) => role.role.name === 'super_admin') || user?.id === 7) {
              participants = participants.filter((p) => {
                // For now, show participants with company_name (indicating they're company users)
                return p.company_name && p.company_name.trim() !== '';
              });
            }
          }
        } catch {
          // Silently continue to fallback
        }

        // If no participants found, try users API as fallback (especially for admin users)
        if (participants.length === 0) {
          try {
            // Try multiple user queries to find any users
            let usersResponse = await usersApi.getUsers({
              is_active: true,
              size: 100,
            });

            // Query 2: If no active users, try all users (non-deleted)
            if (!usersResponse.data?.users?.length) {
              usersResponse = await usersApi.getUsers({
                size: 100,
                include_deleted: false,
              });
            }

            // Query 3: If still nothing, try absolutely everything
            if (!usersResponse.data?.users?.length) {
              usersResponse = await usersApi.getUsers({
                size: 100,
              });
            }

            if (usersResponse.data?.users?.length) {
              // Convert users to participant format and exclude current user
              let filteredUsers = usersResponse.data.users.filter((u) => u.id !== user?.id);
              filteredUsers = filteredUsers.filter((u) => !u.roles.includes('super_admin'));

              // For super admin, only show company admins (users who can receive messages)
              // Check multiple ways to identify super admin
              const isSuperAdmin =
                user?.roles?.some(
                  (role) => (role as { role: { name: string } }).role?.name === 'super_admin'
                ) ||
                user?.id === 7 ||
                (user && !user.company_id && user.is_admin); // Super admin typically has no company_id but is admin

              if (isSuperAdmin) {
                filteredUsers = filteredUsers.filter((u) => {
                  const isCompanyAdmin =
                    u.roles.includes('company_admin') ||
                    u.roles.includes('admin') ||
                    (u.is_admin === true && u.company_id);
                  return isCompanyAdmin;
                });
              }

              participants = filteredUsers.map((u) => ({
                id: u.id,
                email: u.email,
                full_name: `${u.first_name} ${u.last_name}`,
                company_name: u.company_name || '', // Use company_name field
                is_online: false,
              }));
            }
          } catch (usersError) {
            throw usersError;
          }
        }

        const availableParticipants = participants.filter(
          (participant) => !isUserRestricted(participant.id)
        );

        setState((prev) => ({
          ...prev,
          contacts: availableParticipants,
          searchingContacts: false,
        }));
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

  if (isSuperAdminUser) {
    return (
      <AppLayout>
        <div className="flex h-[calc(100vh-4rem)] flex-col items-center justify-center gap-6 bg-slate-50 px-6 text-center dark:bg-gray-950">
          <div className="space-y-3">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
              Messaging disabled
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Super administrator accounts cannot use direct messaging. Switch to a company or
              candidate account to chat.
            </p>
          </div>
        </div>
      </AppLayout>
    );
  }

  const sidebarClassName = clsx(
    'fixed inset-y-0 left-0 z-40 flex w-full max-w-xs flex-col bg-white dark:bg-gray-900 shadow-xl transition-transform duration-200 md:static md:z-auto md:w-80 md:translate-x-0 md:shadow-none md:border-r md:border-gray-200 md:dark:border-gray-800',
    isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
  );
  return (
    <AppLayout>
      <div className="relative flex h-[calc(100vh-4rem)] flex-col bg-slate-50 dark:bg-gray-950 md:flex-row">
        {isMobileSidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm md:hidden"
            onClick={() => setIsMobileSidebarOpen(false)}
            aria-hidden="true"
          />
        )}
        <aside className={sidebarClassName}>
          <div className="flex h-full flex-col">
            <div className="flex items-center justify-between border-b border-gray-200 px-4 py-4 dark:border-gray-800">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-gray-400">Inbox</p>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Conversations
                </h2>
              </div>
              <button
                type="button"
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-gray-200 text-gray-500 transition hover:border-gray-300 hover:text-gray-700 dark:border-gray-700 dark:text-gray-300 dark:hover:border-gray-600 dark:hover:text-white md:hidden"
                onClick={() => setIsMobileSidebarOpen(false)}
                aria-label="Close conversations panel"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
            </div>
            <div className="border-b border-gray-200 px-4 py-4 dark:border-gray-800">
              <div className="flex items-center gap-2 rounded-full bg-gray-100 p-1 text-sm font-medium dark:bg-gray-800/70">
                <button
                  type="button"
                  onClick={() => handleTabSwitch('conversations')}
                  className={clsx(
                    'flex-1 rounded-full px-4 py-2 transition',
                    state.activeTab === 'conversations'
                      ? 'bg-white text-gray-900 shadow-sm dark:bg-gray-900 dark:text-white'
                      : 'text-gray-500 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white'
                  )}
                >
                  Conversations
                </button>
                <button
                  type="button"
                  onClick={() => handleTabSwitch('contacts')}
                  className={clsx(
                    'flex-1 rounded-full px-4 py-2 transition',
                    state.activeTab === 'contacts'
                      ? 'bg-white text-gray-900 shadow-sm dark:bg-gray-900 dark:text-white'
                      : 'text-gray-500 hover:text-gray-800 dark:text-gray-300 dark:hover:text-white'
                  )}
                >
                  Contacts
                </button>
              </div>
              <div className="relative mt-4">
                <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search people or messages"
                  value={state.conversationSearchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="w-full rounded-full border border-transparent bg-gray-100 py-2 pl-10 pr-4 text-sm text-gray-700 transition focus:border-blue-400 focus:bg-white focus:outline-none dark:bg-gray-800 dark:text-gray-100 dark:focus:bg-gray-900"
                />
              </div>
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
                  <div className="space-y-2">
                    {filteredConversations.map((conversation) => (
                      <button
                        key={conversation.other_user_id}
                        type="button"
                        onClick={() => handleConversationSelect(conversation.other_user_id)}
                        className={`p-4 cursor-pointer rounded-2xl border border-transparent bg-white transition hover:border-blue-200 hover:bg-blue-50 dark:bg-gray-900 dark:hover:border-blue-500/40 dark:hover:bg-gray-800 ${
                          state.activeConversationId === conversation.other_user_id
                            ? 'border-blue-200 bg-blue-50 dark:border-blue-500/40 dark:bg-blue-900/20'
                            : ''
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold text-white ${getAvatarColor(conversation.other_user_id)}`}
                          >
                            {getInitials(conversation.other_user_name || '')}
                          </div>
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center justify-between">
                              <h3 className="truncate text-sm font-semibold text-gray-900 dark:text-gray-100">
                                {conversation.other_user_name}
                              </h3>
                              {conversation.last_message && (
                                <span className="text-xs text-gray-400">
                                  {formatTime(conversation.last_message.created_at)}
                                </span>
                              )}
                            </div>
                            <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
                              {conversation.last_message ? (
                                <>
                                  <span className="font-medium">
                                    {conversation.last_message.sender_id === user?.id
                                      ? 'You'
                                      : conversation.last_message.sender_name}
                                    :
                                  </span>{' '}
                                  {conversation.last_message.content}
                                </>
                              ) : (
                                conversation.other_user_email
                              )}
                            </p>
                            <div className="mt-1 flex items-center gap-2">
                              {conversation.other_user_company && (
                                <span className="text-xs text-gray-400">
                                  {conversation.other_user_company}
                                </span>
                              )}
                              {conversation.unread_count > 0 && (
                                <span className="flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-blue-500 px-2 text-xs font-semibold text-white">
                                  {conversation.unread_count}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="flex h-full flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-gray-300 bg-white/60 px-4 py-10 text-center text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-400">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 text-lg font-semibold text-gray-500">
                      ...
                    </div>
                    <p>No conversations yet</p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">
                      Start by messaging a contact
                    </p>
                  </div>
                )
              ) : state.searchingContacts ? (
                <div className="flex h-full flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-gray-300 bg-white/60 px-4 py-10 text-center text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-400">
                  <LoadingSpinner className="h-6 w-6" />
                  Loading contacts...
                </div>
              ) : visibleContacts.length > 0 ? (
                <div className="space-y-2">
                  {visibleContacts.map((contact) => (
                    <div
                      key={contact.id}
                      className="flex items-center gap-3 rounded-2xl border border-transparent bg-white p-4 shadow-sm transition hover:border-blue-200 hover:bg-blue-50 dark:bg-gray-900 dark:hover:border-blue-500/40 dark:hover:bg-gray-800"
                    >
                      <div
                        className={`flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold text-white ${getAvatarColor(contact.id)}`}
                      >
                        {getInitials(contact.full_name)}
                      </div>
                      <div
                        className="min-w-0 flex-1 cursor-pointer"
                        onClick={() => handleContactProfileView(contact)}
                      >
                        <h3 className="truncate text-sm font-semibold text-gray-900 dark:text-gray-100">
                          {contact.full_name}
                        </h3>
                        <p className="truncate text-sm text-gray-600 dark:text-gray-300">
                          {contact.email}
                        </p>
                        {contact.company_name && (
                          <p className="mt-1 text-xs text-gray-400">{contact.company_name}</p>
                        )}
                      </div>
                      <Button
                        size="sm"
                        className="rounded-full bg-blue-500 px-4 py-2 text-xs font-semibold text-white hover:bg-blue-600"
                        onClick={() => handleConversationSelect(contact.id, true)}
                      >
                        Message
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex h-full flex-col items-center justify-center gap-2 rounded-2xl border border-dashed border-gray-300 bg-white/60 px-4 py-10 text-center text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-900/40 dark:text-gray-400">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-100 text-lg font-semibold text-gray-500">
                    ++
                  </div>
                  <p>No contacts found</p>
                </div>
              )}
            </div>
          </div>
        </aside>
        <main className="flex flex-1 flex-col bg-white dark:bg-gray-900 min-h-0">
          {state.activeConversationId && displayConversation ? (
            <>
              <header className="flex items-center justify-between border-b border-gray-200 px-4 py-4 dark:border-gray-800 sm:px-6">
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-gray-200 text-gray-500 transition hover:border-gray-300 hover:text-gray-700 dark:border-gray-700 dark:text-gray-300 dark:hover:border-gray-600 dark:hover:text-white md:hidden"
                    onClick={() => setIsMobileSidebarOpen(true)}
                    aria-label="Open conversations panel"
                  >
                    <Menu className="h-5 w-5" />
                  </button>
                  <div
                    className={`hidden h-12 w-12 items-center justify-center rounded-full text-sm font-semibold text-white md:flex ${getAvatarColor(displayConversation.other_user_id)}`}
                  >
                    {getInitials(displayConversation.other_user_name || '')}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                      {displayConversation.other_user_name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {displayConversation.other_user_email}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    onClick={fetchMessages}
                    variant="ghost"
                    size="sm"
                    className="gap-2 rounded-full border border-transparent bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 transition hover:border-gray-200 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-200 dark:hover:border-gray-700 dark:hover:bg-gray-700"
                    leftIcon={<RefreshCw className="h-4 w-4" />}
                  >
                    Refresh
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="rounded-full px-4 py-2 text-sm"
                    onClick={() =>
                      handleContactProfileView({
                        id: displayConversation.other_user_id,
                        email: displayConversation.other_user_email || '',
                        full_name: displayConversation.other_user_name || 'User',
                        company_name: displayConversation.other_user_company || '',
                      })
                    }
                  >
                    View profile
                  </Button>
                </div>
              </header>

              <div className="flex flex-1 flex-col min-h-0 bg-gradient-to-b from-white via-slate-50 to-slate-100 dark:from-gray-900 dark:via-gray-900 dark:to-gray-950">
                <div
                  ref={messagesContainerRef}
                  className="flex-1 overflow-y-auto px-4 py-6 sm:px-8"
                >
                  {isActiveConversationRestricted ? (
                    <div className="flex h-full flex-col items-center justify-center gap-3 text-center text-sm text-gray-500 dark:text-gray-400">
                      <p>{messagingDisabledCopy}</p>
                    </div>
                  ) : state.messages.length === 0 ? (
                    <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
                      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-blue-50 text-3xl font-semibold text-blue-500">
                        Chat
                      </div>
                      <p className="text-base font-semibold text-gray-700 dark:text-gray-200">
                        Start your conversation
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Send a message to begin chatting
                      </p>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-6">
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
                        const senderInitials = getInitials(senderName);

                        return (
                          <div
                            key={message.id}
                            className={clsx(
                              'flex items-end gap-3',
                              isOwnMessage ? 'justify-end' : 'justify-start'
                            )}
                          >
                            <div className="hidden sm:block">
                              {isOwnMessage ? (
                                <div className="h-10 w-10" />
                              ) : (
                                <div
                                  className={`flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold text-white ${getAvatarColor(message.sender_id)}`}
                                >
                                  {senderInitials}
                                </div>
                              )}
                            </div>

                            <div
                              className={clsx(
                                'flex max-w-[80%] flex-col gap-1 sm:max-w-[65%]',
                                isOwnMessage ? 'items-end text-right' : 'items-start text-left'
                              )}
                            >
                              {!isOwnMessage && (
                                <span className="text-xs font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                                  {senderName}
                                </span>
                              )}

                              <div
                                className={clsx(
                                  'group relative rounded-3xl px-4 py-3 text-sm shadow-lg backdrop-blur',
                                  isOwnMessage
                                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-blue-500/30'
                                    : 'bg-white text-gray-900 shadow-gray-200 dark:bg-gray-800/90 dark:text-gray-100'
                                )}
                              >
                                {repliedMessage && (
                                  <div
                                    className={clsx(
                                      'mb-3 rounded-2xl border-l-4 px-3 py-2 text-xs',
                                      isOwnMessage
                                        ? 'border-white/60 bg-white/10 text-blue-100'
                                        : 'border-blue-200 bg-blue-50 text-blue-800 dark:border-blue-500/60 dark:bg-blue-900/40 dark:text-blue-100'
                                    )}
                                  >
                                    <p className="font-semibold">
                                      {repliedMessage.sender_id === user?.id
                                        ? 'You'
                                        : state.conversations.find(
                                            (c) => c.other_user_id === repliedMessage.sender_id
                                          )?.other_user_name ||
                                          repliedMessage.sender_name ||
                                          'User'}
                                    </p>
                                    <p className="mt-1">
                                      {repliedMessage.type === 'file'
                                        ? `File: ${repliedMessage.file_name}`
                                        : repliedMessage.content}
                                    </p>
                                  </div>
                                )}

                                {message.type === 'file' && message.file_url ? (
                                  <div className="flex flex-col gap-2 text-left">
                                    <div className="flex items-center gap-2">
                                      <Paperclip
                                        className={clsx(
                                          'h-4 w-4',
                                          isOwnMessage
                                            ? 'text-white/80'
                                            : 'text-blue-600 dark:text-blue-300'
                                        )}
                                      />
                                      <span className="font-medium">{message.file_name}</span>
                                    </div>
                                    {message.file_size && (
                                      <span
                                        className={clsx(
                                          'text-xs',
                                          isOwnMessage
                                            ? 'text-white/60'
                                            : 'text-gray-500 dark:text-gray-400'
                                        )}
                                      >
                                        {(message.file_size / (1024 * 1024)).toFixed(2)} MB
                                      </span>
                                    )}
                                    <button
                                      onClick={() =>
                                        message.file_url &&
                                        handleFileDownload(message.file_url, message.file_name)
                                      }
                                      className={clsx(
                                        'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold transition',
                                        isOwnMessage
                                          ? 'border-white/40 bg-white/10 text-white hover:bg-white/20'
                                          : 'border-blue-200 bg-blue-50 text-blue-700 hover:bg-blue-100 dark:border-blue-500/40 dark:bg-blue-900/30 dark:text-blue-200'
                                      )}
                                    >
                                      Download
                                    </button>
                                  </div>
                                ) : (
                                  <p className="leading-relaxed">{message.content}</p>
                                )}

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

                              <p
                                className={clsx(
                                  'text-xs',
                                  isOwnMessage
                                    ? 'text-blue-300'
                                    : 'text-gray-400 dark:text-gray-500'
                                )}
                              >
                                {formatTime(message.created_at)}
                              </p>
                            </div>
                          </div>
                        );
                      })}
                      <div ref={messagesEndRef} />
                    </div>
                  )}
                </div>

                <div className="border-t border-gray-200 bg-white/95 px-4 py-5 shadow-[0_-12px_30px_rgba(15,23,42,0.08)] backdrop-blur dark:border-gray-800 dark:bg-gray-900/95 sm:px-6">
                  {isActiveConversationRestricted ? (
                    <div className="rounded-2xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700 dark:border-blue-800 dark:bg-blue-900/30 dark:text-blue-100">
                      {messagingDisabledCopy}
                    </div>
                  ) : (
                    <>
                      {replyingTo && (
                        <div className="mb-4 rounded-2xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm dark:border-blue-800 dark:bg-blue-900/30">
                          <div className="flex items-start justify-between gap-3">
                            <div>
                              <div className="flex items-center gap-2 text-blue-700 dark:text-blue-200">
                                <Reply className="h-4 w-4" />
                                <span className="font-semibold">
                                  Replying to{' '}
                                  {replyingTo.sender_id === user?.id
                                    ? 'yourself'
                                    : state.conversations.find(
                                        (c) => c.other_user_id === replyingTo.sender_id
                                      )?.other_user_name || 'User'}
                                </span>
                              </div>
                              <p className="mt-2 text-sm text-blue-700/80 dark:text-blue-100">
                                {replyingTo.type === 'file'
                                  ? `File: ${replyingTo.file_name}`
                                  : replyingTo.content}
                              </p>
                            </div>
                            <button
                              onClick={handleCancelReply}
                              className="rounded-full border border-transparent p-1 text-blue-500 transition hover:border-blue-200 hover:bg-blue-100/60 dark:hover:bg-blue-800/40"
                              title="Cancel reply"
                            >
                              <X className="h-4 w-4" />
                            </button>
                          </div>
                        </div>
                      )}

                      {state.error && (
                        <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 dark:border-red-800 dark:bg-red-900/30 dark:text-red-300">
                          <div className="flex items-start justify-between gap-3">
                            <span>{state.error}</span>
                            <button
                              onClick={() => setState((prev) => ({ ...prev, error: null }))}
                              className="text-sm font-semibold text-red-500 hover:underline"
                            >
                              Dismiss
                            </button>
                          </div>
                        </div>
                      )}

                      {attachedFiles.length > 0 && (
                        <div className="mb-4 space-y-2 rounded-2xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm dark:border-blue-800 dark:bg-blue-900/30">
                          <div className="flex items-center justify-between text-blue-900 dark:text-blue-100">
                            <span>{attachedFiles.length} file(s) ready to send</span>
                            <button
                              onClick={handleRemoveAllAttachments}
                              className="text-xs font-semibold text-blue-600 hover:underline dark:text-blue-200"
                            >
                              Remove all
                            </button>
                          </div>
                          <div className="space-y-2">
                            {attachedFiles.map((file) => (
                              <div
                                key={file.id}
                                className="flex items-center justify-between gap-3 rounded-xl border border-blue-100 bg-white px-3 py-2 text-xs text-blue-800 shadow-sm dark:border-blue-700 dark:bg-blue-900/40 dark:text-blue-100"
                              >
                                <div className="flex min-w-0 flex-1 items-center gap-2">
                                  <Paperclip className="h-3.5 w-3.5 flex-shrink-0" />
                                  <span className="truncate font-medium">{file.file_name}</span>
                                  <span className="flex-shrink-0 text-blue-500 dark:text-blue-200">
                                    {(file.file_size / (1024 * 1024)).toFixed(2)} MB
                                  </span>
                                </div>
                                <button
                                  onClick={() => handleRemoveAttachment(file.id)}
                                  className="rounded-full border border-transparent p-1 text-blue-500 transition hover:border-blue-200 hover:bg-blue-100/60 dark:hover:bg-blue-800/40"
                                  title="Remove this file"
                                >
                                  <X className="h-3 w-3" />
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:gap-4">
                        <div className="relative flex-1">
                          <Input
                            ref={messageInputRef}
                            type="text"
                            placeholder="Write a message..."
                            value={newMessage}
                            onChange={handleInputChange}
                            onKeyPress={handleKeyPress}
                            className="w-full rounded-3xl border border-gray-200 bg-gray-50 py-3 pl-4 pr-24 text-sm text-gray-800 transition focus:border-blue-400 focus:bg-white focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                            disabled={state.sending}
                          />
                          <div className="absolute right-3 top-1/2 flex -translate-y-1/2 gap-2">
                            <Button
                              type="button"
                              onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                              className="h-9 w-9 rounded-full bg-white text-gray-500 shadow-sm transition hover:text-gray-700 dark:bg-gray-700 dark:text-gray-300 dark:hover:text-white"
                            >
                              <Smile className="h-4 w-4" />
                            </Button>
                            <Button
                              type="button"
                              onClick={handleAttachmentClick}
                              disabled={uploadingFile}
                              className="h-9 w-9 rounded-full bg-white text-gray-500 shadow-sm transition hover:text-gray-700 disabled:opacity-40 dark:bg-gray-700 dark:text-gray-300 dark:hover:text-white"
                            >
                              <Paperclip className="h-4 w-4" />
                            </Button>
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
                            <div className="absolute bottom-full right-0 mb-3 rounded-2xl border border-gray-200 bg-white p-2 shadow-xl dark:border-gray-700 dark:bg-gray-800">
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
                        <Button
                          onClick={handleSendMessage}
                          disabled={
                            (!newMessage.trim() && attachedFiles.length === 0) || state.sending
                          }
                          className={clsx(
                            'flex h-12 items-center justify-center rounded-full px-6 text-sm font-semibold transition sm:min-w-[120px]',
                            (!newMessage.trim() && attachedFiles.length === 0) || state.sending
                              ? 'bg-gray-300 text-gray-500 dark:bg-gray-700 dark:text-gray-400'
                              : 'bg-blue-500 text-white hover:bg-blue-600'
                          )}
                        >
                          {state.sending ? (
                            <LoadingSpinner className="h-4 w-4" />
                          ) : (
                            <Send className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                    </>
                  )}
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
