import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { messagesApi } from '../../services/api';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import Badge from '../../components/ui/Badge';
import type { Conversation, Message, User } from '../../types';

interface MessagesPageState {
  conversations: Conversation[];
  activeConversation: Conversation | null;
  messages: Message[];
  loading: boolean;
  sending: boolean;
  error: string | null;
  newMessage: string;
  searchQuery: string;
  isConnected: boolean;
  typingUsers: User[];
}

export default function MessagesPage() {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const [state, setState] = useState<MessagesPageState>({
    conversations: [],
    activeConversation: null,
    messages: [],
    loading: true,
    sending: false,
    error: null,
    newMessage: '',
    searchQuery: '',
    isConnected: false,
    typingUsers: []
  });

  // Auto-scroll to bottom of messages
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  // WebSocket connection management
  const connectWebSocket = useCallback(() => {
    if (!conversationId || wsRef.current) return;

    const wsUrl = `${import.meta.env.VITE_WS_URL}/ws/messaging/${conversationId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setState(prev => ({ ...prev, isConnected: true }));
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      switch (data.type) {
        case 'message':
          setState(prev => ({
            ...prev,
            messages: [...prev.messages, data.message]
          }));
          scrollToBottom();
          break;
        case 'typing_start':
          setState(prev => ({
            ...prev,
            typingUsers: [...prev.typingUsers, data.user]
          }));
          break;
        case 'typing_stop':
          setState(prev => ({
            ...prev,
            typingUsers: prev.typingUsers.filter(u => u.id !== data.user.id)
          }));
          break;
        case 'message_read':
          setState(prev => ({
            ...prev,
            messages: prev.messages.map(msg => 
              msg.id === data.messageId 
                ? { ...msg, read_by: [...(msg.read_by || []), data.user] }
                : msg
            )
          }));
          break;
      }
    };

    ws.onclose = () => {
      setState(prev => ({ ...prev, isConnected: false }));
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setState(prev => ({ ...prev, isConnected: false }));
    };

    wsRef.current = ws;
  }, [conversationId, scrollToBottom]);

  // Load conversations
  const loadConversations = async () => {
    try {
      const response = await messagesApi.getConversations();
      setState(prev => ({ 
        ...prev, 
        conversations: response.data || [],
        loading: false 
      }));
    } catch (error: any) {
      setState(prev => ({ 
        ...prev, 
        error: error.response?.data?.message || 'Failed to load conversations',
        loading: false 
      }));
    }
  };

  // Load messages for active conversation
  const loadMessages = async (convId: string) => {
    try {
      const [conversationResponse, messagesResponse] = await Promise.all([
        messagesApi.getConversation(parseInt(convId)),
        messagesApi.getMessages(parseInt(convId))
      ]);

      setState(prev => ({
        ...prev,
        activeConversation: conversationResponse.data || null,
        messages: messagesResponse.data?.items || [],
        error: null
      }));

      scrollToBottom();

      // Mark conversation as read
      await messagesApi.markAsRead(parseInt(convId));
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        error: error.response?.data?.message || 'Failed to load messages'
      }));
    }
  };

  // Send message
  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!state.newMessage.trim() || !conversationId || state.sending) return;

    setState(prev => ({ ...prev, sending: true }));

    try {
      await messagesApi.sendMessage(
        parseInt(conversationId),
        state.newMessage.trim()
      );
      
      setState(prev => ({
        ...prev,
        newMessage: '',
        sending: false
      }));

      // Send via WebSocket for real-time update
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'message',
          content: state.newMessage.trim()
        }));
      }

      inputRef.current?.focus();
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        error: error.response?.data?.message || 'Failed to send message',
        sending: false
      }));
    }
  };

  // Handle typing indicator
  const handleTyping = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'typing_start'
      }));
    }
  }, []);

  const handleStopTyping = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'typing_stop'
      }));
    }
  }, []);

  // Effects
  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (conversationId) {
      loadMessages(conversationId);
      connectWebSocket();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [conversationId, connectWebSocket]);

  useEffect(() => {
    scrollToBottom();
  }, [state.messages, scrollToBottom]);

  // Utility functions
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

  if (state.loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner className="w-8 h-8" />
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Conversations Sidebar */}
      <div className="w-1/3 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Messages</h1>
          <Input
            type="text"
            placeholder="Search conversations..."
            value={state.searchQuery}
            onChange={(e) => setState(prev => ({ ...prev, searchQuery: e.target.value }))}
            className="w-full"
          />
        </div>

        <div className="flex-1 overflow-y-auto">
          {filteredConversations.length > 0 ? (
            <div className="divide-y divide-gray-100">
              {filteredConversations.map((conversation) => (
                <div
                  key={conversation.id}
                  onClick={() => navigate(`/dashboard/messages/${conversation.id}`)}
                  className={`p-4 cursor-pointer hover:bg-gray-50 ${
                    conversationId === conversation.id.toString() ? 'bg-blue-50 border-r-2 border-blue-500' : ''
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold text-gray-700">
                        {conversation.participants[0]?.user?.full_name?.charAt(0) || 'C'}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {conversation.title || 
                           conversation.participants
                             .filter(p => p.user.id !== user?.id)
                             .map(p => p.user.full_name)
                             .join(', ')
                          }
                        </p>
                        {conversation.last_message && (
                          <p className="text-xs text-gray-500">
                            {formatTime(conversation.last_message.created_at)}
                          </p>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 truncate">
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
              <p className="text-gray-500">No conversations found</p>
              <Button className="mt-4" onClick={() => navigate('/dashboard')}>
                Start New Conversation
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 flex flex-col">
        {state.activeConversation ? (
          <>
            {/* Chat Header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                    <span className="text-sm font-semibold text-gray-700">
                      {state.activeConversation.participants[0]?.user?.full_name?.charAt(0) || 'C'}
                    </span>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">
                      {state.activeConversation.title ||
                       state.activeConversation.participants
                         .filter(p => p.user.id !== user?.id)
                         .map(p => p.user.full_name)
                         .join(', ')
                      }
                    </h2>
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${state.isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                      <span className="text-sm text-gray-500">
                        {state.isConnected ? 'Connected' : 'Disconnected'}
                      </span>
                    </div>
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
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-200 text-gray-900'
                    }`}>
                      <p className="text-sm">{message.content}</p>
                      <div className="flex items-center justify-between mt-1">
                        <p className={`text-xs ${
                          isOwn ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {formatTime(message.created_at)}
                        </p>
                        {isOwn && message.read_by && message.read_by.length > 0 && (
                          <span className="text-xs text-blue-100">✓✓</span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Typing Indicator */}
              {state.typingUsers.length > 0 && (
                <div className="flex justify-start">
                  <div className="bg-gray-200 px-4 py-2 rounded-lg">
                    <p className="text-sm text-gray-600">
                      {state.typingUsers.map(u => u.full_name).join(', ')} {
                        state.typingUsers.length === 1 ? 'is' : 'are'
                      } typing...
                    </p>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <form onSubmit={sendMessage} className="bg-white border-t border-gray-200 p-4">
              <div className="flex items-center space-x-2">
                <Input
                  ref={inputRef}
                  type="text"
                  value={state.newMessage}
                  onChange={(e) => setState(prev => ({ ...prev, newMessage: e.target.value }))}
                  onKeyDown={handleTyping}
                  onBlur={handleStopTyping}
                  placeholder="Type a message..."
                  className="flex-1"
                  disabled={state.sending || !state.isConnected}
                />
                <Button 
                  type="submit" 
                  disabled={!state.newMessage.trim() || state.sending || !state.isConnected}
                  className="px-6"
                >
                  {state.sending ? <LoadingSpinner className="w-4 h-4" /> : 'Send'}
                </Button>
              </div>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <span className="text-6xl mb-4 block">💬</span>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Welcome to Messages</h2>
              <p className="text-gray-500 mb-4">
                Select a conversation from the sidebar to start messaging
              </p>
              <Button onClick={() => navigate('/dashboard')}>
                Start New Conversation
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Error Notification */}
      {state.error && (
        <div className="fixed bottom-4 right-4 bg-red-500 text-white p-4 rounded-lg shadow-lg">
          <div className="flex items-center space-x-2">
            <span>⚠️</span>
            <span>{state.error}</span>
            <button 
              onClick={() => setState(prev => ({ ...prev, error: null }))}
              className="ml-2 text-red-200 hover:text-white"
            >
              ✕
            </button>
          </div>
        </div>
      )}
    </div>
  );
}