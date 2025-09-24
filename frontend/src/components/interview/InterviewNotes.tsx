'use client';

import React, { useState, useEffect } from 'react';
import { StickyNote, Edit3, Save, X, Trash2 } from 'lucide-react';
import { useInterviewNote } from '@/hooks/useInterviewNote';
import { useToast } from '@/contexts/ToastContext';

interface InterviewNotesProps {
  interviewId: number;
  className?: string;
}

const InterviewNotes: React.FC<InterviewNotesProps> = ({ interviewId, className = '' }) => {
  const { note, loading, error, updateNote, deleteNote } = useInterviewNote(interviewId);
  const { showToast } = useToast();

  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    if (note && note.content) {
      setEditContent(note.content);
    }
  }, [note]);

  const handleSave = async () => {
    try {
      await updateNote(editContent);
      setIsEditing(false);
      showToast({
        type: 'success',
        title: 'Note Saved',
        message: 'Your private note has been saved successfully.',
      });
    } catch {
      showToast({
        type: 'error',
        title: 'Save Failed',
        message: 'Failed to save your note. Please try again.',
      });
    }
  };

  const handleCancel = () => {
    setEditContent(note?.content || '');
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (
      window.confirm(
        'Are you sure you want to delete your private note? This action cannot be undone.'
      )
    ) {
      try {
        await deleteNote();
        setEditContent('');
        setIsEditing(false);
        showToast({
          type: 'success',
          title: 'Note Deleted',
          message: 'Your private note has been deleted.',
        });
      } catch {
        showToast({
          type: 'error',
          title: 'Delete Failed',
          message: 'Failed to delete your note. Please try again.',
        });
      }
    }
  };

  const hasContent = note && note.content && note.content.trim().length > 0;

  if (loading) {
    return (
      <div className={`bg-yellow-50 border border-yellow-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2">
          <StickyNote className="h-5 w-5 text-yellow-600" />
          <span className="text-sm text-yellow-800">Loading your private notes...</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-yellow-50 border border-yellow-200 rounded-lg ${className}`}>
      {/* Header */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <StickyNote className="h-5 w-5 text-yellow-600" />
          <span className="text-sm font-medium text-yellow-800">My Private Notes</span>
          {hasContent && (
            <span className="text-xs bg-yellow-200 text-yellow-700 px-2 py-0.5 rounded-full">
              Note saved
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {!isEditing && hasContent && (
            <>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setIsEditing(true);
                  setIsExpanded(true);
                }}
                className="p-1 hover:bg-yellow-200 rounded"
                title="Edit note"
              >
                <Edit3 className="h-4 w-4 text-yellow-600" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete();
                }}
                className="p-1 hover:bg-red-200 rounded"
                title="Delete note"
              >
                <Trash2 className="h-4 w-4 text-red-600" />
              </button>
            </>
          )}
          <span className="text-yellow-600">{isExpanded ? '−' : '+'}</span>
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="px-4 pb-4">
          <div className="text-xs text-yellow-700 mb-2">
            📝 Only you can see and edit this note. It&apos;s private to you and won&apos;t be
            visible to other participants.
          </div>

          {isEditing ? (
            <div className="space-y-3">
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                placeholder="Add your private notes about this interview..."
                className="w-full h-32 p-3 border border-yellow-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                autoFocus
              />
              <div className="flex items-center gap-2">
                <button
                  onClick={handleSave}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white bg-yellow-600 hover:bg-yellow-700 rounded-lg transition-colors duration-200"
                >
                  <Save className="h-4 w-4" />
                  Save Note
                </button>
                <button
                  onClick={handleCancel}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors duration-200"
                >
                  <X className="h-4 w-4" />
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {hasContent ? (
                <div className="bg-white p-3 rounded-lg border border-yellow-300">
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                    {note.content}
                  </pre>
                </div>
              ) : (
                <div className="text-center py-6">
                  <StickyNote className="h-8 w-8 text-yellow-400 mx-auto mb-2" />
                  <p className="text-sm text-yellow-700 mb-3">
                    No private notes yet. Click below to add your thoughts about this interview.
                  </p>
                  <button
                    onClick={() => setIsEditing(true)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-yellow-700 bg-yellow-100 hover:bg-yellow-200 rounded-lg transition-colors duration-200"
                  >
                    <Edit3 className="h-4 w-4" />
                    Add Note
                  </button>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
              {error}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default InterviewNotes;
