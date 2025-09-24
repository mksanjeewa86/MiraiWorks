import { useState, useEffect, useCallback } from 'react';
import { interviewNotesApi } from '../api/interviewNotes';
import type { InterviewNote, InterviewNoteUpdate } from '../types/interviewNote';

interface UseInterviewNoteResult {
  note: InterviewNote | null;
  loading: boolean;
  error: string | null;
  updateNote: (content: string) => Promise<void>;
  deleteNote: () => Promise<void>;
  refreshNote: () => Promise<void>;
}

export const useInterviewNote = (interviewId: number): UseInterviewNoteResult => {
  const [note, setNote] = useState<InterviewNote | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNote = useCallback(async () => {
    try {
      setLoading(true);
      const response = await interviewNotesApi.getNote(interviewId);
      setNote(response.data || null);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch note');
    } finally {
      setLoading(false);
    }
  }, [interviewId]);

  const updateNote = async (content: string) => {
    try {
      const noteData: InterviewNoteUpdate = { content };
      const response = await interviewNotesApi.updateNote(interviewId, noteData);
      setNote(response.data || null);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update note');
      throw err;
    }
  };

  const deleteNote = async () => {
    try {
      await interviewNotesApi.deleteNote(interviewId);
      setNote(null);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete note');
      throw err;
    }
  };

  const refreshNote = async () => {
    await fetchNote();
  };

  useEffect(() => {
    if (interviewId) {
      fetchNote();
    }
  }, [interviewId, fetchNote]);

  return {
    note,
    loading,
    error,
    updateNote,
    deleteNote,
    refreshNote,
  };
};
