'use client';

import React, { useState } from 'react';
import { X, Plus, Tag as TagIcon } from 'lucide-react';
import { systemUpdatesApi } from '@/api/systemUpdates';
import { SystemUpdateTag } from '@/types/system-update';

interface CreateSystemUpdateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const TAG_LABELS: Record<SystemUpdateTag, string> = {
  [SystemUpdateTag.SECURITY]: 'Security',
  [SystemUpdateTag.TODO]: 'Todo',
  [SystemUpdateTag.INTERVIEW]: 'Interview',
  [SystemUpdateTag.EXAM]: 'Exam',
  [SystemUpdateTag.CALENDAR]: 'Calendar',
  [SystemUpdateTag.WORKFLOW]: 'Workflow',
  [SystemUpdateTag.MESSAGING]: 'Messaging',
  [SystemUpdateTag.PROFILE]: 'Profile',
  [SystemUpdateTag.GENERAL]: 'General',
  [SystemUpdateTag.MAINTENANCE]: 'Maintenance',
  [SystemUpdateTag.FEATURE]: 'Feature',
  [SystemUpdateTag.BUGFIX]: 'Bug Fix',
};

const TAG_COLORS: Record<SystemUpdateTag, string> = {
  [SystemUpdateTag.SECURITY]: 'bg-red-100 text-red-700 border-red-300',
  [SystemUpdateTag.TODO]: 'bg-blue-100 text-blue-700 border-blue-300',
  [SystemUpdateTag.INTERVIEW]: 'bg-purple-100 text-purple-700 border-purple-300',
  [SystemUpdateTag.EXAM]: 'bg-indigo-100 text-indigo-700 border-indigo-300',
  [SystemUpdateTag.CALENDAR]: 'bg-cyan-100 text-cyan-700 border-cyan-300',
  [SystemUpdateTag.WORKFLOW]: 'bg-teal-100 text-teal-700 border-teal-300',
  [SystemUpdateTag.MESSAGING]: 'bg-green-100 text-green-700 border-green-300',
  [SystemUpdateTag.PROFILE]: 'bg-pink-100 text-pink-700 border-pink-300',
  [SystemUpdateTag.GENERAL]: 'bg-gray-100 text-gray-700 border-gray-300',
  [SystemUpdateTag.MAINTENANCE]: 'bg-orange-100 text-orange-700 border-orange-300',
  [SystemUpdateTag.FEATURE]: 'bg-emerald-100 text-emerald-700 border-emerald-300',
  [SystemUpdateTag.BUGFIX]: 'bg-amber-100 text-amber-700 border-amber-300',
};

export default function CreateSystemUpdateModal({
  isOpen,
  onClose,
  onSuccess,
}: CreateSystemUpdateModalProps) {
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [selectedTags, setSelectedTags] = useState<SystemUpdateTag[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleTagToggle = (tag: SystemUpdateTag) => {
    setSelectedTags((prev) =>
      prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    if (!message.trim()) {
      setError('Message is required');
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await systemUpdatesApi.create({
        title: title.trim(),
        message: message.trim(),
        tags: selectedTags,
      });

      if (response.success) {
        // Reset form
        setTitle('');
        setMessage('');
        setSelectedTags([]);
        onSuccess();
        onClose();
      } else {
        setError(response.message || 'Failed to create system update');
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setTitle('');
      setMessage('');
      setSelectedTags([]);
      setError(null);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-white">Create System Update</h2>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors disabled:opacity-50"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Title */}
          <div>
            <label
              htmlFor="title"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="Enter update title..."
              required
              maxLength={255}
              disabled={isSubmitting}
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {title.length}/255 characters
            </p>
          </div>

          {/* Message */}
          <div>
            <label
              htmlFor="message"
              className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Message <span className="text-red-500">*</span>
            </label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              rows={6}
              className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
              placeholder="Enter update message..."
              required
              disabled={isSubmitting}
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {message.length} characters
            </p>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              <TagIcon className="inline h-4 w-4 mr-1" />
              Tags (select multiple)
            </label>
            <div className="flex flex-wrap gap-2">
              {Object.entries(TAG_LABELS).map(([tag, label]) => (
                <button
                  key={tag}
                  type="button"
                  onClick={() => handleTagToggle(tag as SystemUpdateTag)}
                  disabled={isSubmitting}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium border-2 transition-all ${
                    selectedTags.includes(tag as SystemUpdateTag)
                      ? TAG_COLORS[tag as SystemUpdateTag]
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {label}
                </button>
              ))}
            </div>
            <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
              {selectedTags.length > 0
                ? `${selectedTags.length} tag${selectedTags.length > 1 ? 's' : ''} selected`
                : 'No tags selected'}
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={handleClose}
              disabled={isSubmitting}
              className="flex-1 px-6 py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !title.trim() || !message.trim()}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-medium disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Creating...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <Plus className="h-5 w-5" />
                  Create Update
                </span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
