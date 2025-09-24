// Exam System Types
// Centralized type definitions for the exam system

// ============================================================================
// ENUMS AND CONSTANTS
// ============================================================================

export enum ExamStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  ARCHIVED = 'archived',
}

export enum ExamType {
  APTITUDE = 'aptitude',
  SKILL = 'skill',
  KNOWLEDGE = 'knowledge',
  PERSONALITY = 'personality',
  CUSTOM = 'custom',
}

export enum QuestionType {
  MULTIPLE_CHOICE = 'multiple_choice',
  SINGLE_CHOICE = 'single_choice',
  TEXT_INPUT = 'text_input',
  ESSAY = 'essay',
  TRUE_FALSE = 'true_false',
  RATING = 'rating',
  MATCHING = 'matching',
}

export enum SessionStatus {
  NOT_STARTED = 'not_started',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  EXPIRED = 'expired',
  SUSPENDED = 'suspended',
}

// ============================================================================
// CORE EXAM INTERFACES
// ============================================================================

export interface Exam {
  id: number;
  title: string;
  description: string | null;
  exam_type: string;
  status: string;
  company_id: number;
  created_by: number | null;
  time_limit_minutes: number | null;
  max_attempts: number;
  passing_score: number | null;
  is_randomized: boolean;
  allow_web_usage: boolean;
  monitor_web_usage: boolean;
  require_face_verification: boolean;
  face_check_interval_minutes: number;
  show_results_immediately: boolean;
  show_correct_answers: boolean;
  show_score: boolean;
  instructions: string | null;
  created_at: string;
  updated_at: string;
  // Computed fields
  total_questions?: number | null;
  total_sessions?: number | null;
  completed_sessions?: number | null;
  average_score?: number | null;
}

export interface ExamInfo {
  id: number;
  title: string;
  description: string | null;
  exam_type: string;
  status: string;
  time_limit_minutes: number | null;
  max_attempts: number;
  passing_score: number | null;
  is_randomized: boolean;
  allow_web_usage: boolean;
  monitor_web_usage: boolean;
  require_face_verification: boolean;
  face_check_interval_minutes: number;
  show_results_immediately: boolean;
  show_correct_answers: boolean;
  show_score: boolean;
  instructions: string | null;
  created_at: string;
  total_questions: number;
}

// ============================================================================
// QUESTION INTERFACES
// ============================================================================

export interface Question {
  id: number;
  question_text: string;
  question_type: string;
  order_index: number;
  points: number;
  time_limit_seconds: number | null;
  is_required: boolean;
  options: Record<string, string> | null;
  correct_answers: string[] | null;
  max_length: number | null;
  min_length: number | null;
  rating_scale: number | null;
  explanation: string | null;
  tags: string[] | null;
}

export interface QuestionFormData {
  question_text: string;
  question_type: string;
  points: number;
  time_limit_seconds: number | null;
  is_required: boolean;
  options: Record<string, string>;
  correct_answers: string[];
  max_length: number | null;
  min_length: number | null;
  rating_scale: number | null;
  explanation: string;
  tags: string[];
}

// ============================================================================
// SESSION INTERFACES
// ============================================================================

export interface SessionInfo {
  id: number;
  exam_id: number;
  candidate_id: number;
  assignment_id: number | null;
  status: string;
  attempt_number: number;
  started_at: string | null;
  completed_at: string | null;
  expires_at: string | null;
  time_remaining_seconds: number | null;
  current_question_index: number;
  total_questions: number;
  questions_answered: number;
  score: number | null;
  max_score: number | null;
  percentage: number | null;
  passed: boolean | null;
  web_usage_detected: boolean;
  web_usage_count: number;
  face_verification_failed: boolean;
  face_check_count: number;
  exam_title: string;
  exam_type: string;
  require_face_verification: boolean;
  face_check_interval_minutes: number;
  monitor_web_usage: boolean;
  allow_web_usage: boolean;
  // Additional fields for results
  candidate_name?: string;
  candidate_email?: string;
  time_spent_minutes?: number | null;
}

export interface SessionSummary {
  id: number;
  candidate_name: string;
  candidate_email: string;
  attempt_number: number;
  status: string;
  started_at: string | null;
  completed_at: string | null;
  score: number | null;
  percentage: number | null;
  passed: boolean | null;
  web_usage_detected: boolean;
  face_verification_failed: boolean;
  time_spent_minutes: number | null;
}

// ============================================================================
// ANSWER INTERFACES
// ============================================================================

export interface Answer {
  question_id: number;
  answer_data?: Record<string, any>;
  answer_text?: string;
  selected_options?: string[];
  time_spent_seconds?: number;
}

export interface AnswerInfo {
  id: number;
  session_id: number;
  question_id: number;
  answer_data: Record<string, any> | null;
  answer_text: string | null;
  selected_options: string[] | null;
  is_correct: boolean | null;
  points_earned: number;
  points_possible: number;
  time_spent_seconds: number | null;
  answered_at: string;
}

// ============================================================================
// ASSIGNMENT INTERFACES
// ============================================================================

export interface ExamAssignment {
  id: number;
  exam_id: number;
  candidate_id: number;
  assigned_by: number | null;
  due_date: string | null;
  custom_time_limit_minutes: number | null;
  custom_max_attempts: number | null;
  is_active: boolean;
  completed: boolean;
  notification_sent: boolean;
  reminder_sent: boolean;
  created_at: string;
  updated_at: string;
  // Related info
  exam_title: string;
  exam_type: string;
  sessions_count: number;
  latest_session: {
    id: number;
    status: string;
    percentage: number | null;
    passed: boolean | null;
    started_at: string | null;
    completed_at: string | null;
  } | null;
}

// ============================================================================
// MONITORING INTERFACES
// ============================================================================

export interface MonitoringEvent {
  id: number;
  session_id: number;
  event_type: string;
  event_data: any;
  severity: string;
  timestamp: string;
}

// ============================================================================
// FORM DATA INTERFACES
// ============================================================================

export interface ExamFormData {
  title: string;
  description: string;
  exam_type: string;
  time_limit_minutes: number | null;
  max_attempts: number;
  passing_score: number | null;
  is_randomized: boolean;
  allow_web_usage: boolean;
  monitor_web_usage: boolean;
  require_face_verification: boolean;
  face_check_interval_minutes: number;
  show_results_immediately: boolean;
  show_correct_answers: boolean;
  show_score: boolean;
  instructions: string;
}

// ============================================================================
// API RESPONSE INTERFACES
// ============================================================================

export interface ExamListResponse {
  exams: Exam[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface ExamTakeResponse {
  session: SessionInfo;
  questions: Question[];
  current_question: Question | null;
  time_remaining_seconds: number | null;
  can_navigate: boolean;
}

export interface ExamResults {
  session: SessionInfo;
  answers: AnswerInfo[];
  questions?: Question[];
  monitoring_events?: MonitoringEvent[];
}

export interface ExamStatistics {
  exam_id: number;
  total_assigned: number;
  total_started: number;
  total_completed: number;
  completion_rate: number;
  average_score: number | null;
  min_score: number | null;
  max_score: number | null;
  average_time_minutes: number | null;
}

// ============================================================================
// COMPONENT PROP INTERFACES
// ============================================================================

export interface ExamQuestionProps {
  question: Question;
  answer?: Answer;
  onAnswerChange: (answer: Partial<Answer>) => void;
}

export interface ExamQuestionFormProps {
  question: QuestionFormData;
  onSave: (question: QuestionFormData) => void;
  onCancel: () => void;
}

export interface ExamTimerProps {
  timeRemaining: number; // in seconds
  onTimeUp: () => void;
}

export interface FaceVerificationProps {
  sessionId: number;
  onComplete: (success: boolean) => void;
}

export interface WebUsageMonitorProps {
  onWebUsageDetected: (eventType: string, eventData: any) => void;
  allowWebUsage: boolean;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type ExamStatusType = keyof typeof ExamStatus;
export type ExamTypeType = keyof typeof ExamType;
export type QuestionTypeType = keyof typeof QuestionType;
export type SessionStatusType = keyof typeof SessionStatus;
