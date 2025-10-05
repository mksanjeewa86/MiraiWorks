// Question Bank Types
// Centralized type definitions for question bank system

export interface QuestionBankItem {
  id: number;
  bank_id: number;
  question_text: string;
  question_type: string;
  order_index: number;
  points: number;
  difficulty: 'easy' | 'medium' | 'hard' | null;
  options: Record<string, string> | null;
  correct_answers: string[] | null;
  explanation: string | null;
  tags: string[] | null;
  max_length: number | null;
  min_length: number | null;
  rating_scale: number | null;
  created_at: string;
  updated_at: string;
}

export interface QuestionBankItemFormData {
  question_text: string;
  question_type: string;
  order_index?: number;
  points?: number;
  difficulty?: 'easy' | 'medium' | 'hard' | null;
  options?: Record<string, string> | null;
  correct_answers?: string[] | null;
  explanation?: string | null;
  tags?: string[] | null;
  max_length?: number | null;
  min_length?: number | null;
  rating_scale?: number | null;
}

export interface QuestionBank {
  id: number;
  name: string;
  description: string | null;
  exam_type: string;
  category: string | null;
  difficulty: 'easy' | 'medium' | 'hard' | 'mixed' | null;
  is_public: boolean;
  company_id: number | null;
  created_by: number;
  created_at: string;
  updated_at: string;
  question_count?: number;
}

export interface QuestionBankDetail extends QuestionBank {
  questions: QuestionBankItem[];
}

export interface QuestionBankFormData {
  name: string;
  description?: string;
  exam_type: string;
  category?: string;
  difficulty?: 'easy' | 'medium' | 'hard' | 'mixed' | null;
  is_public: boolean;
  company_id?: number;
  questions?: QuestionBankItemFormData[];
}

export interface QuestionBankListResponse {
  banks: QuestionBank[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

export interface QuestionBankStats {
  bank_id: number;
  total_questions: number;
  questions_by_type: Record<string, number>;
  questions_by_difficulty: Record<string, number>;
  average_points: number;
  tags_used: string[];
  times_used_in_exams: number;
}
