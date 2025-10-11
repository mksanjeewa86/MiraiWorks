'use client';

import React, { useState } from 'react';
import { Megaphone, ChevronDown, ChevronUp } from 'lucide-react';
import type { SystemUpdate, SystemUpdateTag } from '@/types/system-update';

interface SystemUpdateCardProps {
  update: SystemUpdate;
}

const TAG_LABELS: Record<SystemUpdateTag, string> = {
  security: 'Security',
  todo: 'Todo',
  interview: 'Interview',
  exam: 'Exam',
  calendar: 'Calendar',
  workflow: 'Workflow',
  messaging: 'Messaging',
  profile: 'Profile',
  general: 'General',
  maintenance: 'Maintenance',
  feature: 'Feature',
  bugfix: 'Bug Fix',
};

const TAG_COLORS: Record<SystemUpdateTag, string> = {
  security: 'bg-red-100 text-red-700 border-red-300 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800',
  todo: 'bg-blue-100 text-blue-700 border-blue-300 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800',
  interview: 'bg-purple-100 text-purple-700 border-purple-300 dark:bg-purple-900/30 dark:text-purple-400 dark:border-purple-800',
  exam: 'bg-indigo-100 text-indigo-700 border-indigo-300 dark:bg-indigo-900/30 dark:text-indigo-400 dark:border-indigo-800',
  calendar: 'bg-cyan-100 text-cyan-700 border-cyan-300 dark:bg-cyan-900/30 dark:text-cyan-400 dark:border-cyan-800',
  workflow: 'bg-teal-100 text-teal-700 border-teal-300 dark:bg-teal-900/30 dark:text-teal-400 dark:border-teal-800',
  messaging: 'bg-green-100 text-green-700 border-green-300 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800',
  profile: 'bg-pink-100 text-pink-700 border-pink-300 dark:bg-pink-900/30 dark:text-pink-400 dark:border-pink-800',
  general: 'bg-gray-100 text-gray-700 border-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600',
  maintenance: 'bg-orange-100 text-orange-700 border-orange-300 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-800',
  feature: 'bg-emerald-100 text-emerald-700 border-emerald-300 dark:bg-emerald-900/30 dark:text-emerald-400 dark:border-emerald-800',
  bugfix: 'bg-amber-100 text-amber-700 border-amber-300 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800',
};

export default function SystemUpdateCard({ update }: SystemUpdateCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [shouldTruncate, setShouldTruncate] = useState(true);

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
  };

  // Check if message is long (more than 3 lines approximately)
  const isLongMessage = update.message.length > 200;

  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-2xl shadow-sm border-2 border-purple-200 dark:border-purple-800">
      <div className="p-6">
        <div className="flex items-start gap-4">
          {/* Icon */}
          <div className="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-2xl bg-gradient-to-br from-purple-500 to-blue-500 shadow-lg">
            <Megaphone className="h-6 w-6 text-white" />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            {/* Title and Tags */}
            <div className="flex items-start justify-between gap-4 mb-2">
              <h3 className="text-base font-semibold text-gray-900 dark:text-white">
                {update.title}
              </h3>
            </div>

            {/* Tags */}
            {update.tags && update.tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-3">
                {update.tags.map((tag) => (
                  <span
                    key={tag}
                    className={`px-2 py-0.5 rounded-full text-xs font-medium border ${
                      TAG_COLORS[tag as SystemUpdateTag] || TAG_COLORS.general
                    }`}
                  >
                    {TAG_LABELS[tag as SystemUpdateTag] || tag}
                  </span>
                ))}
              </div>
            )}

            {/* Message */}
            <div className="relative">
              <p
                className={`text-sm text-gray-600 dark:text-gray-400 leading-relaxed whitespace-pre-wrap ${
                  !isExpanded && isLongMessage && shouldTruncate ? 'line-clamp-3' : ''
                }`}
              >
                {update.message}
              </p>

              {/* View More/Less Button */}
              {isLongMessage && (
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="mt-2 flex items-center gap-1 text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 text-sm font-medium transition-colors"
                >
                  {isExpanded ? (
                    <>
                      <ChevronUp className="h-4 w-4" />
                      View less
                    </>
                  ) : (
                    <>
                      <ChevronDown className="h-4 w-4" />
                      View more
                    </>
                  )}
                </button>
              )}
            </div>

            {/* Time */}
            <div className="mt-3 flex items-center justify-between">
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {formatTime(update.created_at)}
              </p>
              <div className="flex items-center gap-2">
                <span className="text-xs text-purple-600 dark:text-purple-400 font-semibold">
                  System Update
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
