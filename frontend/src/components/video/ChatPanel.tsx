import React, { useState, useRef, useEffect } from 'react';
import Button from '../ui/button';
import Input from '../ui/input';
import {
  PaperAirplaneIcon,
  LinkIcon,
  DocumentIcon,
} from '@heroicons/react/24/outline';

interface ChatMessage {
  id: string;
  senderId: number;
  senderName: string;
  message: string;
  timestamp: Date;
  type: 'text' | 'link' | 'code' | 'file';
}

interface ChatPanelProps {
  messages: ChatMessage[];
  onSendMessage: (message: string, type?: string) => void;
  currentUserId: number;
  isVisible: boolean;
  onToggleVisibility: () => void;
}

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
      minute: '2-digit' 
    });
  };

  const renderMessage = (message: ChatMessage) => {
    const isOwnMessage = message.senderId === currentUserId;
    
    return (
      <div
        key={message.id}
        className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-3`}
      >
        <div
          className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg ${
            isOwnMessage
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-900'
          }`}
        >
          {!isOwnMessage && (
            <div className="text-xs font-medium mb-1 opacity-75">
              {message.senderName}
            </div>
          )}
          
          <div className="text-sm">
            {message.type === 'link' ? (
              <div>
                {message.message.split(/(\bhttps?:\/\/\S+)/g).map((part, index) => 
                  /^https?:\/\//.test(part) ? (
                    <a
                      key={index}
                      href={part}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline hover:no-underline flex items-center space-x-1"
                    >
                      <LinkIcon className="h-4 w-4" />
                      <span>リンク</span>
                    </a>
                  ) : (
                    <span key={index}>{part}</span>
                  )
                )}
              </div>
            ) : message.type === 'code' ? (
              <pre className="bg-gray-800 text-green-400 p-2 rounded text-xs overflow-x-auto">
                <code>{message.message}</code>
              </pre>
            ) : (
              <span>{message.message}</span>
            )}
          </div>
          
          <div className="text-xs opacity-75 mt-1">
            {formatTimestamp(message.timestamp)}
          </div>
        </div>
      </div>
    );
  };

  // const copyToClipboard = (text: string) => {
  //   navigator.clipboard.writeText(text);
  // };

  const insertTemplate = (template: string) => {
    setMessageText(prev => prev + template);
    inputRef.current?.focus();
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="w-80 h-full bg-white border-l border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">チャット</h3>
          <Button
            variant="outline"
            size="sm"
            onClick={onToggleVisibility}
            className="text-gray-500 hover:text-gray-700"
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
            className="flex items-center space-x-1 text-xs"
          >
            <DocumentIcon className="h-3 w-3" />
            <span>コード</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => insertTemplate('参考リンク: ')}
            className="flex items-center space-x-1 text-xs"
          >
            <LinkIcon className="h-3 w-3" />
            <span>リンク</span>
          </Button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>メッセージはここに表示されます</p>
            <p className="text-sm mt-1">会話を開始してください</p>
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-900 px-3 py-2 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <Input
            ref={inputRef}
            value={messageText}
            onChange={(e) => setMessageText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="メッセージを入力..."
            className="flex-1"
            maxLength={500}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!messageText.trim()}
            className="px-3"
          >
            <PaperAirplaneIcon className="h-4 w-4" />
          </Button>
        </div>
        
        {/* Character Count */}
        <div className="text-xs text-gray-500 mt-1 text-right">
          {messageText.length}/500
        </div>

        {/* Helpful Tips */}
        <div className="text-xs text-gray-400 mt-2">
          <p>💡 ヒント: Enterで送信、Shift+Enterで改行</p>
        </div>
      </div>
    </div>
  );
};