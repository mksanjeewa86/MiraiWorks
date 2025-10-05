import { apiClient } from './apiClient';
import { API_ENDPOINTS } from './config';
import type { ApiResponse } from '@/types';
import type {
  Exam,
  ExamInfo,
  ExamFormData,
  ExamListResponse,
  ExamAssignment,
  ExamStatistics,
  ExamTakeResponse,
  SessionInfo,
  Question,
  Answer,
  AnswerInfo,
  ExamResults,
  MonitoringEvent,
  QuestionFormData,
} from '@/types/exam';

// ============================================================================
// EXAM MANAGEMENT API (Admin/Recruiter/System Admin)
// ============================================================================

export const examApi = {
  /**
   * Create a new exam with questions
   * @param examData - Exam configuration data
   * @param questions - Array of questions
   * @param companyId - Company ID (optional for system admin, required for company admin)
   */
  async createExam(
    examData: ExamFormData & { company_id?: number | null },
    questions: QuestionFormData[]
  ): Promise<ApiResponse<ExamInfo>> {
    const response = await apiClient.post<ExamInfo>(API_ENDPOINTS.EXAMS.BASE, {
      ...examData,
      questions_data: questions,
    });
    return { data: response.data, success: true };
  },

  /**
   * Get list of exams for company or all system (system admin)
   * @param filters - Optional filters (status, skip, limit, include_global)
   */
  async getExams(filters?: {
    status?: string;
    skip?: number;
    limit?: number;
    include_global?: boolean;
  }): Promise<ApiResponse<ExamListResponse>> {
    // Build query string
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());

    // Include global/public exams by default
    const includeGlobal = filters?.include_global !== false;
    params.append('include_global', includeGlobal.toString());

    const queryString = params.toString();
    const url = queryString
      ? `${API_ENDPOINTS.EXAMS.BASE}?${queryString}`
      : API_ENDPOINTS.EXAMS.BASE;

    const response = await apiClient.get<ExamListResponse>(url);
    return { data: response.data, success: true };
  },

  /**
   * Get exam details by ID
   * @param examId - Exam ID
   */
  async getExam(examId: number): Promise<ApiResponse<ExamInfo>> {
    const response = await apiClient.get<ExamInfo>(API_ENDPOINTS.EXAMS.BY_ID(examId));
    return { data: response.data, success: true };
  },

  /**
   * Update exam details
   * @param examId - Exam ID
   * @param examData - Updated exam data
   */
  async updateExam(
    examId: number,
    examData: Partial<ExamFormData>
  ): Promise<ApiResponse<ExamInfo>> {
    const response = await apiClient.put<ExamInfo>(API_ENDPOINTS.EXAMS.BY_ID(examId), examData);
    return { data: response.data, success: true };
  },

  /**
   * Delete an exam
   * @param examId - Exam ID
   */
  async deleteExam(examId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.delete<{ message: string }>(API_ENDPOINTS.EXAMS.BY_ID(examId));
    return { data: response.data, success: true };
  },

  /**
   * Get exam statistics
   * @param examId - Exam ID
   */
  async getExamStatistics(examId: number): Promise<ApiResponse<ExamStatistics>> {
    const response = await apiClient.get<ExamStatistics>(API_ENDPOINTS.EXAMS.STATISTICS(examId));
    return { data: response.data, success: true };
  },

  /**
   * Duplicate an exam
   * @param examId - Exam ID to duplicate
   * @param newTitle - New title for duplicated exam
   */
  async duplicateExam(examId: number, newTitle: string): Promise<ApiResponse<ExamInfo>> {
    // First get the exam details
    const examResponse = await examApi.getExam(examId);
    if (!examResponse.data) {
      throw new Error('Exam not found');
    }

    const questionsResponse = await questionApi.getQuestions(examId);
    if (!questionsResponse.data) {
      throw new Error('Questions not found');
    }

    // Create new exam with same settings but new title
    const { id, created_at, total_questions, status, created_by, updated_at, company_id, ...examData } = examResponse.data;
    const newExamData: ExamFormData & { company_id?: number } = {
      ...examData,
      title: newTitle,
      description: examData.description || '',
      instructions: examData.instructions || '',
      is_public: examData.is_public || false,
    };

    const questions = questionsResponse.data.map((q) => {
      const { id, ...questionData } = q;
      return questionData;
    });

    return examApi.createExam(newExamData, questions as QuestionFormData[]);
  },

  /**
   * Clone a global or public exam to current company
   * @param examId - ID of exam to clone
   */
  async cloneExam(examId: number): Promise<ApiResponse<ExamInfo>> {
    try {
      const response = await apiClient.post<ExamInfo>(
        `/api/exams/${examId}/clone`
      );
      return { data: response.data, success: true };
    } catch (error: any) {
      return {
        success: false,
        message: error.response?.data?.detail || 'Failed to clone exam',
        errors: [error.response?.data?.detail || 'Failed to clone exam'],
      };
    }
  },

  /**
   * Export exam results as PDF
   * @param examId - Exam ID
   * @param includeAnswers - Whether to include individual answers
   */
  async exportResultsPDF(examId: number, includeAnswers: boolean = false): Promise<Blob> {
    const url = `${API_ENDPOINTS.EXAMS.EXPORT_PDF(examId)}?include_answers=${includeAnswers}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to export PDF');
    }

    return await response.blob();
  },

  /**
   * Export exam results as Excel
   * @param examId - Exam ID
   * @param includeAnswers - Whether to include individual answers
   */
  async exportResultsExcel(examId: number, includeAnswers: boolean = false): Promise<Blob> {
    const url = `${API_ENDPOINTS.EXAMS.EXPORT_EXCEL(examId)}?include_answers=${includeAnswers}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to export Excel');
    }

    return await response.blob();
  },
};

// ============================================================================
// QUESTION MANAGEMENT API
// ============================================================================

export const questionApi = {
  /**
   * Get all questions for an exam
   * @param examId - Exam ID
   */
  async getQuestions(examId: number): Promise<ApiResponse<Question[]>> {
    const response = await apiClient.get<Question[]>(API_ENDPOINTS.EXAMS.QUESTIONS(examId));
    return { data: response.data, success: true };
  },

  /**
   * Add a question to an exam
   * @param examId - Exam ID
   * @param questionData - Question data
   */
  async addQuestion(
    examId: number,
    questionData: QuestionFormData
  ): Promise<ApiResponse<Question>> {
    const response = await apiClient.post<Question>(
      API_ENDPOINTS.EXAMS.QUESTIONS(examId),
      questionData
    );
    return { data: response.data, success: true };
  },

  /**
   * Update a question
   * @param questionId - Question ID
   * @param questionData - Updated question data
   */
  async updateQuestion(
    questionId: number,
    questionData: Partial<QuestionFormData>
  ): Promise<ApiResponse<Question>> {
    const response = await apiClient.put<Question>(
      API_ENDPOINTS.EXAM_QUESTIONS.BY_ID(questionId),
      questionData
    );
    return { data: response.data, success: true };
  },

  /**
   * Delete a question
   * @param questionId - Question ID
   */
  async deleteQuestion(questionId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.delete<{ message: string }>(
      API_ENDPOINTS.EXAM_QUESTIONS.BY_ID(questionId)
    );
    return { data: response.data, success: true };
  },
};

// ============================================================================
// ASSIGNMENT MANAGEMENT API
// ============================================================================

export const assignmentApi = {
  /**
   * Assign exam to candidates
   * @param examId - Exam ID
   * @param assignmentData - Assignment configuration and candidate IDs
   * @param sendEmail - Whether to send email notifications (default: true)
   */
  async createAssignments(
    examId: number,
    assignmentData: {
      candidate_ids: number[];
      due_date?: string | null;
      custom_time_limit_minutes?: number | null;
      custom_max_attempts?: number | null;
    },
    sendEmail: boolean = true
  ): Promise<ApiResponse<ExamAssignment[]>> {
    const response = await apiClient.post<ExamAssignment[]>(
      `${API_ENDPOINTS.EXAMS.ASSIGNMENTS(examId)}?send_email=${sendEmail}`,
      assignmentData
    );
    return { data: response.data, success: true };
  },

  /**
   * Get assignments for an exam
   * @param examId - Exam ID
   */
  async getExamAssignments(examId: number): Promise<ApiResponse<ExamAssignment[]>> {
    const response = await apiClient.get<ExamAssignment[]>(API_ENDPOINTS.EXAMS.ASSIGNMENTS(examId));
    return { data: response.data, success: true };
  },

  /**
   * Get current user's exam assignments
   */
  async getMyAssignments(): Promise<ApiResponse<ExamAssignment[]>> {
    const response = await apiClient.get<ExamAssignment[]>(API_ENDPOINTS.EXAMS.MY_ASSIGNMENTS);
    return { data: response.data, success: true };
  },

  /**
   * Update assignment
   * @param assignmentId - Assignment ID
   * @param assignmentData - Updated assignment data
   */
  async updateAssignment(
    assignmentId: number,
    assignmentData: {
      due_date?: string | null;
      custom_time_limit_minutes?: number | null;
      custom_max_attempts?: number | null;
      is_active?: boolean;
    }
  ): Promise<ApiResponse<ExamAssignment>> {
    const response = await apiClient.put<ExamAssignment>(
      API_ENDPOINTS.EXAM_ASSIGNMENTS.BY_ID(assignmentId),
      assignmentData
    );
    return { data: response.data, success: true };
  },

  /**
   * Delete assignment
   * @param assignmentId - Assignment ID
   */
  async deleteAssignment(assignmentId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.delete<{ message: string }>(
      API_ENDPOINTS.EXAM_ASSIGNMENTS.BY_ID(assignmentId)
    );
    return { data: response.data, success: true };
  },
};

// ============================================================================
// EXAM TAKING API (Candidate)
// ============================================================================

export const examTakingApi = {
  /**
   * Start or resume an exam
   * @param examId - Exam ID
   * @param assignmentId - Assignment ID (optional)
   * @param testMode - Test mode flag (doesn't count towards attempts)
   */
  async startExam(
    examId: number,
    assignmentId?: number,
    testMode: boolean = false
  ): Promise<ApiResponse<ExamTakeResponse>> {
    const response = await apiClient.post<ExamTakeResponse>(API_ENDPOINTS.EXAMS.TAKE, {
      exam_id: examId,
      assignment_id: assignmentId,
      test_mode: testMode,
      user_agent: navigator.userAgent,
      screen_resolution: `${window.screen.width}x${window.screen.height}`,
    });
    return { data: response.data, success: true };
  },

  /**
   * Submit an answer
   * @param sessionId - Session ID
   * @param answerData - Answer data
   */
  async submitAnswer(
    sessionId: number,
    answerData: {
      question_id: number;
      answer_text?: string;
      selected_options?: string[];
      answer_data?: Record<string, any>;
      time_spent_seconds?: number;
    }
  ): Promise<ApiResponse<AnswerInfo>> {
    const response = await apiClient.post<AnswerInfo>(
      API_ENDPOINTS.EXAM_SESSIONS.ANSWERS(sessionId),
      answerData
    );
    return { data: response.data, success: true };
  },

  /**
   * Complete an exam session
   * @param sessionId - Session ID
   */
  async completeExam(sessionId: number): Promise<ApiResponse<SessionInfo>> {
    const response = await apiClient.post<SessionInfo>(
      API_ENDPOINTS.EXAM_SESSIONS.COMPLETE(sessionId)
    );
    return { data: response.data, success: true };
  },

  /**
   * Get exam results
   * @param sessionId - Session ID
   */
  async getResults(sessionId: number): Promise<ApiResponse<ExamResults>> {
    const response = await apiClient.get<ExamResults>(
      API_ENDPOINTS.EXAM_SESSIONS.RESULTS(sessionId)
    );
    return { data: response.data, success: true };
  },

  /**
   * Get session details
   * @param sessionId - Session ID
   */
  async getSession(sessionId: number): Promise<ApiResponse<SessionInfo>> {
    const response = await apiClient.get<SessionInfo>(API_ENDPOINTS.EXAM_SESSIONS.BY_ID(sessionId));
    return { data: response.data, success: true };
  },
};

// ============================================================================
// MONITORING API
// ============================================================================

export const monitoringApi = {
  /**
   * Create monitoring event
   * @param sessionId - Session ID
   * @param eventData - Event data
   */
  async createEvent(
    sessionId: number,
    eventData: {
      event_type: string;
      event_data?: any;
      severity?: 'info' | 'warning' | 'critical';
    }
  ): Promise<ApiResponse<MonitoringEvent>> {
    const response = await apiClient.post<MonitoringEvent>(
      API_ENDPOINTS.EXAM_SESSIONS.MONITORING(sessionId),
      eventData
    );
    return { data: response.data, success: true };
  },

  /**
   * Submit face verification
   * @param sessionId - Session ID
   * @param faceData - Face verification data
   */
  async submitFaceVerification(
    sessionId: number,
    faceData: {
      image_data: string;
      verification_type: 'initial' | 'periodic';
      timestamp: string;
    }
  ): Promise<
    ApiResponse<{
      verified: boolean;
      confidence_score: number;
      message: string;
      requires_human_review: boolean;
    }>
  > {
    const response = await apiClient.post<{
      verified: boolean;
      confidence_score: number;
      message: string;
      requires_human_review: boolean;
    }>(API_ENDPOINTS.EXAM_SESSIONS.FACE_VERIFICATION(sessionId), faceData);
    return { data: response.data, success: true };
  },

  /**
   * Get monitoring events for a session
   * @param sessionId - Session ID
   */
  async getEvents(sessionId: number): Promise<ApiResponse<MonitoringEvent[]>> {
    const response = await apiClient.get<MonitoringEvent[]>(
      API_ENDPOINTS.EXAM_SESSIONS.MONITORING(sessionId)
    );
    return { data: response.data, success: true };
  },
};

// ============================================================================
// SESSION MANAGEMENT API (Admin/Recruiter)
// ============================================================================

export const sessionApi = {
  /**
   * Get all sessions for an exam
   * @param examId - Exam ID
   * @param filters - Optional filters
   */
  async getExamSessions(
    examId: number,
    filters?: {
      skip?: number;
      limit?: number;
      status?: string;
    }
  ): Promise<ApiResponse<{ sessions: SessionInfo[]; total: number }>> {
    // Build query string
    const params = new URLSearchParams();
    if (filters?.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters?.limit !== undefined) params.append('limit', filters.limit.toString());
    if (filters?.status) params.append('status', filters.status);

    const queryString = params.toString();
    const url = queryString
      ? `${API_ENDPOINTS.EXAMS.SESSIONS(examId)}?${queryString}`
      : API_ENDPOINTS.EXAMS.SESSIONS(examId);

    const response = await apiClient.get<{ sessions: SessionInfo[]; total: number }>(url);
    return { data: response.data, success: true };
  },

  /**
   * Get session details with full information
   * @param sessionId - Session ID
   */
  async getSessionDetails(sessionId: number): Promise<ApiResponse<ExamResults>> {
    const response = await apiClient.get<ExamResults>(
      API_ENDPOINTS.EXAM_SESSIONS.DETAILS(sessionId)
    );
    return { data: response.data, success: true };
  },

  /**
   * Suspend a session
   * @param sessionId - Session ID
   * @param reason - Suspension reason
   */
  async suspendSession(
    sessionId: number,
    reason: string
  ): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>(
      API_ENDPOINTS.EXAM_SESSIONS.SUSPEND(sessionId),
      { reason }
    );
    return { data: response.data, success: true };
  },

  /**
   * Reset a session (allow retry)
   * @param sessionId - Session ID
   */
  async resetSession(sessionId: number): Promise<ApiResponse<{ message: string }>> {
    const response = await apiClient.post<{ message: string }>(
      API_ENDPOINTS.EXAM_SESSIONS.RESET(sessionId)
    );
    return { data: response.data, success: true };
  },
};
