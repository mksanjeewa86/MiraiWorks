import { useState, useEffect, useCallback, useMemo } from 'react';
import { examApi, questionApi, assignmentApi, sessionApi } from '@/api/exam';
import type {
  Exam,
  ExamInfo,
  ExamFormData,
  ExamAssignment,
  ExamStatistics,
  Question,
  QuestionFormData,
  SessionInfo,
} from '@/types/exam';
import { toast } from 'sonner';

// ============================================================================
// EXAM MANAGEMENT HOOKS
// ============================================================================

/**
 * Hook for fetching and managing exams list
 */
export function useExams(filters?: { status?: string; skip?: number; limit?: number }) {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  // Memoize filters to prevent infinite re-renders
  const memoizedFilters = useMemo(() => filters, [JSON.stringify(filters)]);

  const fetchExams = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await examApi.getExams(memoizedFilters);

      if (response.data) {
        setExams(response.data.exams);
        setTotal(response.data.total);
        setHasMore(response.data.has_more);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to load exams';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [memoizedFilters]);

  useEffect(() => {
    fetchExams();
  }, [fetchExams]);

  return { exams, loading, error, total, hasMore, refetch: fetchExams };
}

/**
 * Hook for fetching single exam details
 */
export function useExam(examId: number | null) {
  const [exam, setExam] = useState<ExamInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchExam = useCallback(async () => {
    if (!examId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await examApi.getExam(examId);
      if (response.data) {
        setExam(response.data);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load exam';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [examId]);

  useEffect(() => {
    fetchExam();
  }, [fetchExam]);

  return { exam, loading, error, refetch: fetchExam };
}

/**
 * Hook for exam CRUD operations
 */
export function useExamMutations() {
  const [loading, setLoading] = useState(false);

  const createExam = async (
    examData: ExamFormData & { company_id?: number | null },
    questions: QuestionFormData[]
  ) => {
    setLoading(true);
    try {
      const response = await examApi.createExam(examData, questions);
      toast.success('Exam created successfully');
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to create exam';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateExam = async (examId: number, examData: Partial<ExamFormData>) => {
    setLoading(true);
    try {
      const response = await examApi.updateExam(examId, examData);
      toast.success('Exam updated successfully');
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update exam';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteExam = async (examId: number) => {
    setLoading(true);
    try {
      await examApi.deleteExam(examId);
      toast.success('Exam deleted successfully');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete exam';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const duplicateExam = async (examId: number, newTitle: string) => {
    setLoading(true);
    try {
      const response = await examApi.duplicateExam(examId, newTitle);
      toast.success('Exam duplicated successfully');
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to duplicate exam';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createExam, updateExam, deleteExam, duplicateExam, loading };
}

// ============================================================================
// QUESTION MANAGEMENT HOOKS
// ============================================================================

/**
 * Hook for fetching exam questions
 */
export function useExamQuestions(examId: number | null) {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchQuestions = useCallback(async () => {
    if (!examId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await questionApi.getQuestions(examId);
      if (response.data) {
        setQuestions(response.data);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load questions';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [examId]);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  return { questions, loading, error, refetch: fetchQuestions };
}

/**
 * Hook for question CRUD operations
 */
export function useQuestionMutations() {
  const [loading, setLoading] = useState(false);

  const addQuestion = async (examId: number, questionData: QuestionFormData) => {
    setLoading(true);
    try {
      const response = await questionApi.addQuestion(examId, questionData);
      toast.success('Question added successfully');
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to add question';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateQuestion = async (questionId: number, questionData: Partial<QuestionFormData>) => {
    setLoading(true);
    try {
      const response = await questionApi.updateQuestion(questionId, questionData);
      toast.success('Question updated successfully');
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update question';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteQuestion = async (questionId: number) => {
    setLoading(true);
    try {
      await questionApi.deleteQuestion(questionId);
      toast.success('Question deleted successfully');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete question';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { addQuestion, updateQuestion, deleteQuestion, loading };
}

// ============================================================================
// ASSIGNMENT MANAGEMENT HOOKS
// ============================================================================

/**
 * Hook for fetching exam assignments
 */
export function useExamAssignments(examId: number | null) {
  const [assignments, setAssignments] = useState<ExamAssignment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAssignments = useCallback(async () => {
    if (!examId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await assignmentApi.getExamAssignments(examId);
      if (response.data) {
        setAssignments(response.data);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load assignments';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [examId]);

  useEffect(() => {
    fetchAssignments();
  }, [fetchAssignments]);

  return { assignments, loading, error, refetch: fetchAssignments };
}

/**
 * Hook for fetching candidate's exam assignments
 */
export function useMyAssignments() {
  const [assignments, setAssignments] = useState<ExamAssignment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAssignments = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await assignmentApi.getMyAssignments();
      if (response.data) {
        setAssignments(response.data);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load assignments';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAssignments();
  }, [fetchAssignments]);

  return { assignments, loading, error, refetch: fetchAssignments };
}

/**
 * Hook for assignment CRUD operations
 */
export function useAssignmentMutations() {
  const [loading, setLoading] = useState(false);

  const createAssignments = async (
    examId: number,
    assignmentData: {
      candidate_ids: number[];
      due_date?: string | null;
      custom_time_limit_minutes?: number | null;
      custom_max_attempts?: number | null;
    },
    sendEmail: boolean = true
  ) => {
    setLoading(true);
    try {
      const response = await assignmentApi.createAssignments(examId, assignmentData, sendEmail);
      const message = sendEmail
        ? `Exam assigned to ${assignmentData.candidate_ids.length} candidate(s) - Email notifications sent`
        : `Exam assigned to ${assignmentData.candidate_ids.length} candidate(s)`;
      toast.success(message);
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to create assignments';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateAssignment = async (
    assignmentId: number,
    assignmentData: {
      due_date?: string | null;
      custom_time_limit_minutes?: number | null;
      custom_max_attempts?: number | null;
      is_active?: boolean;
    }
  ) => {
    setLoading(true);
    try {
      const response = await assignmentApi.updateAssignment(assignmentId, assignmentData);
      toast.success('Assignment updated successfully');
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to update assignment';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteAssignment = async (assignmentId: number) => {
    setLoading(true);
    try {
      await assignmentApi.deleteAssignment(assignmentId);
      toast.success('Assignment deleted successfully');
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to delete assignment';
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { createAssignments, updateAssignment, deleteAssignment, loading };
}

// ============================================================================
// STATISTICS HOOKS
// ============================================================================

/**
 * Hook for fetching exam statistics
 */
export function useExamStatistics(examId: number | null) {
  const [statistics, setStatistics] = useState<ExamStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatistics = useCallback(async () => {
    if (!examId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await examApi.getExamStatistics(examId);
      if (response.data) {
        setStatistics(response.data);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load statistics';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [examId]);

  useEffect(() => {
    fetchStatistics();
  }, [fetchStatistics]);

  return { statistics, loading, error, refetch: fetchStatistics };
}

// ============================================================================
// SESSION MANAGEMENT HOOKS
// ============================================================================

/**
 * Hook for fetching exam sessions
 */
export function useExamSessions(
  examId: number | null,
  filters?: { skip?: number; limit?: number; status?: string }
) {
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  // Memoize filters to prevent infinite re-renders
  const memoizedFilters = useMemo(() => filters, [JSON.stringify(filters)]);

  const fetchSessions = useCallback(async () => {
    if (!examId) return;

    setLoading(true);
    setError(null);

    try {
      const response = await sessionApi.getExamSessions(examId, memoizedFilters);
      if (response.data) {
        setSessions(response.data.sessions);
        setTotal(response.data.total);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to load sessions';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [examId, memoizedFilters]);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  return { sessions, loading, error, total, refetch: fetchSessions };
}
