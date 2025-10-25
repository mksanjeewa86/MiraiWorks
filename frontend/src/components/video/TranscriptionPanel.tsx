import React, { useState, useRef, useEffect } from 'react';
import { TranscriptionSegment } from '@/types/video';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { LanguageSelector } from './LanguageSelector';
import { apiClient } from '../../api/apiClient';
import { API_ENDPOINTS } from '../../api/config';
import { MagnifyingGlassIcon, ArrowDownTrayIcon, XMarkIcon } from '@heroicons/react/24/outline';
import type { TranscriptionPanelProps } from '@/types/components';

export const TranscriptionPanel: React.FC<TranscriptionPanelProps> = ({
  segments,
  isTranscribing,
  language,
  onLanguageChange,
  callId,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [highlightedSegments, setHighlightedSegments] = useState<number[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest segment
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [segments]);

  // Search functionality
  useEffect(() => {
    if (searchQuery.trim()) {
      const matchingSegments = segments
        .filter((segment) => segment.segment_text.toLowerCase().includes(searchQuery.toLowerCase()))
        .map((segment) => segment.id);
      setHighlightedSegments(matchingSegments);
    } else {
      setHighlightedSegments([]);
    }
  }, [searchQuery, segments]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const highlightText = (text: string, query: string) => {
    if (!query.trim()) return text;

    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, index) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={index} className="bg-yellow-200 px-1 rounded">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  const handleExport = async (format: 'txt' | 'pdf' | 'srt') => {
    if (!callId) {
      console.error('No call ID available for export');
      return;
    }

    try {
      const response = await apiClient.get<{ download_url: string }>(
        `${API_ENDPOINTS.VIDEO_CALLS.TRANSCRIPT_DOWNLOAD(callId)}?format=${format}`
      );
      window.open(response.data.download_url, '_blank');
    } catch (error) {
      console.error('Failed to export transcript:', error);
    }
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">実時間転写</h3>
          <div className="flex items-center space-x-2">
            {isTranscribing && (
              <div className="flex items-center space-x-1 text-sm text-green-600">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>転写中</span>
              </div>
            )}
          </div>
        </div>

        {/* Language Selector */}
        <div className="mb-3">
          <LanguageSelector value={language} onChange={onLanguageChange} />
        </div>

        {/* Search */}
        <div className="relative">
          <Input
            placeholder="転写を検索..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 transform -translate-y-1/2"
            >
              <XMarkIcon className="h-4 w-4 text-gray-400 hover:text-gray-600" />
            </button>
          )}
        </div>

        {/* Export Options */}
        <div className="flex space-x-2 mt-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport('txt')}
            className="flex items-center space-x-1"
          >
            <ArrowDownTrayIcon className="h-4 w-4" />
            <span>TXT</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport('pdf')}
            className="flex items-center space-x-1"
          >
            <ArrowDownTrayIcon className="h-4 w-4" />
            <span>PDF</span>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport('srt')}
            className="flex items-center space-x-1"
          >
            <ArrowDownTrayIcon className="h-4 w-4" />
            <span>SRT</span>
          </Button>
        </div>
      </div>

      {/* Transcription Content */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
        {segments.length === 0 ? (
          <div className="text-center text-gray-500 mt-8">
            <p>転写はここに表示されます</p>
            <p className="text-sm mt-1">会話を開始してください</p>
          </div>
        ) : (
          segments.map((segment) => (
            <div
              key={segment.id}
              className={`p-3 rounded-lg border ${
                highlightedSegments.includes(segment.id)
                  ? 'border-yellow-300 bg-yellow-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              {/* Speaker and Time */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  {segment.speaker_name || `話者 ${segment.speaker_id}`}
                </span>
                <span className="text-xs text-gray-500">{formatTime(segment.start_time)}</span>
              </div>

              {/* Transcript Text */}
              <p className="text-sm text-gray-900 leading-relaxed">
                {highlightText(segment.segment_text, searchQuery)}
              </p>

              {/* Confidence Score */}
              {segment.confidence && (
                <div className="mt-2 flex items-center space-x-2">
                  <span className="text-xs text-gray-500">信頼度:</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-1">
                    <div
                      className="bg-green-500 h-1 rounded-full"
                      style={{ width: `${segment.confidence * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500">
                    {Math.round(segment.confidence * 100)}%
                  </span>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Status Bar */}
      <div className="p-3 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>{segments.length} セグメント</span>
          {searchQuery && <span>{highlightedSegments.length} 件の検索結果</span>}
        </div>
      </div>
    </div>
  );
};
