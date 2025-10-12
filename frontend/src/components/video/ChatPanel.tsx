import React, { useState, useRef, useEffect } from 'react';
import { ChatMessage } from '@/types/video';
import Button from '../ui/button';
import Input from '../ui/input';
import {
  PaperAirplaneIcon,
  LinkIcon,
  DocumentIcon,
  CheckIcon,
} from '@heroicons/react/24/outline';
import { CheckIcon as CheckIconSolid } from '@heroicons/react/24/solid';
import type { ChatPanelProps } from '@/types/components';

export const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  onSendMessage,
  currentUserId,
  isVisible,
  onToggleVisibility,
}) => {
  const [messageText, setMessageText] = useState('');
  const [isTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when panel becomes visible
  useEffect(() => {
    if (isVisible && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isVisible]);

  const handleSendMessage = () => {
    if (messageText.trim()) {
      const messageType = detectMessageType(messageText);
      onSendMessage(messageText.trim(), messageType);
      setMessageText('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const detectMessageType = (text: string): string => {
    if (text.includes('http://') || text.includes('https://')) {
      return 'link';
    }
    if (text.includes('```') || text.includes('`')) {
      return 'code';
    }
    return 'text';
  };

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString('ja-JP', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const renderMessage = (message: ChatMessage) => {
    const isOwnMessage = message.senderId === currentUserId;

    return (
      <div
        key={message.id}
        className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}
      >
        <div className={`flex ${isOwnMessage ? 'flex-row-reverse' : 'flex-row'} items-end gap-2 max-w-[75%]`}>
          {/* Avatar */}
          {!isOwnMessage && (
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-xs font-semibold">
              {message.senderName?.charAt(0).toUpperCase() || 'U'}
            </div>
          )}

          {/* Message Bubble Container */}
          <div className={`flex flex-col ${isOwnMessage ? 'items-end' : 'items-start'}`}>
            {/* Sender Name for received messages */}
            {!isOwnMessage && (
              <div className="text-xs font-medium text-gray-600 mb-1 px-1">
                {message.senderName}
              </div>
            )}

            {/* Message Bubble with Tail */}
            <div className="relative group">
              <div
                className={`relative px-4 py-2.5 rounded-2xl shadow-sm transition-all duration-200 hover:shadow-md ${
                  isOwnMessage
                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-br-md'
                    : 'bg-white text-gray-800 border border-gray-200 rounded-bl-md'
                }`}
              >
                {/* Message Content */}
                <div className="text-[15px] leading-relaxed break-words">
                  {message.type === 'link' ? (
                    <div>
                      {message.message.split(/(\bhttps?:\/\/\S+)/g).map((part, index) =>
                        /^https?:\/\//.test(part) ? (
                          <a
                            key={index}
                            href={part}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={`underline hover:no-underline inline-flex items-center gap-1 ${
                              isOwnMessage ? 'text-blue-100' : 'text-blue-600'
                            }`}
                          >
                            <LinkIcon className="h-3.5 w-3.5" />
                            <span className="text-sm">リンク</span>
                          </a>
                        ) : (
                          <span key={index}>{part}</span>
                        )
                      )}
                    </div>
                  ) : message.type === 'code' ? (
                    <pre className="bg-gray-900 text-green-400 p-3 rounded-lg text-xs overflow-x-auto font-mono my-1">
                      <code>{message.message}</code>
                    </pre>
                  ) : (
                    <span className="whitespace-pre-wrap">{message.message}</span>
                  )}
                </div>

                {/* Timestamp and Status */}
                <div
                  className={`flex items-center gap-1 mt-1 text-[11px] ${
                    isOwnMessage ? 'text-blue-100' : 'text-gray-500'
                  }`}
                >
                  <span>{formatTimestamp(message.timestamp)}</span>
                  {isOwnMessage && (
                    <div className="flex items-center">
                      <CheckIconSolid className="h-3.5 w-3.5 text-blue-200" />
                      <CheckIconSolid className="h-3.5 w-3.5 -ml-2 text-blue-200" />
                    </div>
                  )}
                </div>
              </div>

              {/* Chat Bubble Tail */}
              <div
                className={`absolute bottom-0 ${
                  isOwnMessage ? 'right-0 -mr-1' : 'left-0 -ml-1'
                }`}
              >
                <svg
                  width="12"
                  height="20"
                  viewBox="0 0 12 20"
                  className={isOwnMessage ? 'rotate-180' : ''}
                >
                  <path
                    d="M0,0 L12,0 Q0,10 0,20 Z"
                    className={
                      isOwnMessage
                        ? 'fill-blue-600'
                        : 'fill-white stroke-gray-200 stroke-1'
                    }
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // const copyToClipboard = (text: string) => {
  //   navigator.clipboard.writeText(text);
  // };

  const insertTemplate = (template: string) => {
    setMessageText((prev) => prev + template);
    inputRef.current?.focus();
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="w-80 h-full bg-gradient-to-b from-gray-50 to-gray-100 border-l border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">チャット</h3>
            <p className="text-xs text-gray-500 mt-0.5">
              {messages.length > 0 ? `${messages.length}件のメッセージ` : 'メッセージなし'}
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={onToggleVisibility}
            className="text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors"
          >
            ×
          </Button>
        </div>

        {/* Quick Actions */}
        <div className="flex space-x-2 mt-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => insertTemplate('コードを共有: ```\n\n```')}
            className="flex items-center space-x-1 text-xs hover:bg-blue-50 hover:text-blue-600 hover:border-blue-300 transition-colors"
          >
            <DocumentIcon className="h-3.5 w-3.5" />
            <span>コード</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => insertTemplate('参考リンク: ')}
            className="flex items-center space-x-1 text-xs hover:bg-blue-50 hover:text-blue-600 hover:border-blue-300 transition-colors"
          >
            <LinkIcon className="h-3.5 w-3.5" />
            <span>リンク</span>
          </Button>
        </div>
      </div>

      {/* Messages */}
      <div
        className="flex-1 overflow-y-auto p-4 space-y-1"
        style={{
          backgroundImage:
            'radial-gradient(circle at 20px 20px, rgba(0,0,0,0.02) 1px, transparent 0)',
          backgroundSize: '40px 40px',
        }}
      >
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-16">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-100 to-purple-100 rounded-full mb-4">
              <svg
                className="w-8 h-8 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <p className="text-base font-medium">メッセージはここに表示されます</p>
            <p className="text-sm mt-1 text-gray-400">会話を開始してください</p>
          </div>
        ) : (
          messages.map(renderMessage)
        )}

        {isTyping && (
          <div className="flex justify-start mb-4 animate-fade-in">
            <div className="flex items-end gap-2">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-gray-300 to-gray-400 flex items-center justify-center text-white text-xs">
                <span className="animate-pulse">•••</span>
              </div>
              <div className="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-bl-md shadow-sm">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.15s' }}
                  ></div>
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0.3s' }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="p-4 bg-white border-t border-gray-200 shadow-lg">
        <div className="flex space-x-2">
          <Input
            ref={inputRef}
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="メッセージを入力..."
            className="flex-1 rounded-full border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
            maxLength={500}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!messageText.trim()}
            className="px-4 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 disabled:from-gray-300 disabled:to-gray-400 transition-all shadow-md hover:shadow-lg disabled:shadow-none"
          >
            <PaperAirplaneIcon className="h-4 w-4 transform rotate-45" />
          </Button>
        </div>

        {/* Character Count */}
        <div className="flex items-center justify-between mt-2">
          <div className="text-xs text-gray-400">
            <span className="inline-flex items-center gap-1">
              💡 <span>Enterで送信、Shift+Enterで改行</span>
            </span>
          </div>
          <div
            className={`text-xs font-medium ${
              messageText.length > 450 ? 'text-orange-500' : 'text-gray-500'
            }`}
          >
            {messageText.length}/500
          </div>
        </div>
      </div>
    </div>
  );
};
