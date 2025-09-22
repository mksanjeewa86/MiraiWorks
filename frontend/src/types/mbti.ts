// MBTI personality test types

export type MBTIType = 
  | 'INTJ' | 'INTP' | 'ENTJ' | 'ENTP'  // Analysts (NT)
  | 'INFJ' | 'INFP' | 'ENFJ' | 'ENFP'  // Diplomats (NF)
  | 'ISTJ' | 'ISFJ' | 'ESTJ' | 'ESFJ'  // Sentinels (SJ)
  | 'ISTP' | 'ISFP' | 'ESTP' | 'ESFP'; // Explorers (SP)

export type MBTITestStatus = 'not_taken' | 'in_progress' | 'completed';

export interface MBTIQuestion {
  id: number;
  question_number: number;
  dimension: string;
  question_text: string;
  option_a: string;
  option_b: string;
}

export interface MBTIAnswerSubmit {
  question_id: number;
  answer: 'A' | 'B';
}

export interface MBTITestStart {
  language: 'en' | 'ja';
}

export interface MBTITestSubmit {
  answers: Record<number, 'A' | 'B'>;
}

export interface MBTITestResult {
  id: number;
  user_id: number;
  status: MBTITestStatus;
  mbti_type?: string;
  extraversion_introversion_score?: number;
  sensing_intuition_score?: number;
  thinking_feeling_score?: number;
  judging_perceiving_score?: number;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  is_completed: boolean;
  completion_percentage: number;
  dimension_preferences: Record<string, string>;
  strength_scores: Record<string, number>;
}

export interface MBTITestSummary {
  mbti_type: string;
  completed_at: string;
  dimension_preferences: Record<string, string>;
  strength_scores: Record<string, number>;
  type_name_en: string;
  type_name_ja: string;
  type_description_en: string;
  type_description_ja: string;
  temperament: string;
}

export interface MBTITestProgress {
  status: MBTITestStatus;
  completion_percentage: number;
  current_question?: number;
  total_questions: number;
  started_at?: string;
}

export interface MBTITypeInfo {
  type_code: MBTIType;
  name_en: string;
  name_ja: string;
  description_en: string;
  description_ja: string;
  temperament: string;
  strengths_en: string[];
  strengths_ja: string[];
  weaknesses_en: string[];
  weaknesses_ja: string[];
  careers_en: string[];
  careers_ja: string[];
}

// Component props
export interface MBTITestModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (result: MBTITestResult) => void;
}

export interface MBTIResultCardProps {
  summary: MBTITestSummary;
  language?: 'en' | 'ja';
  showDetails?: boolean;
}

export interface MBTIProgressProps {
  progress: MBTITestProgress;
  onStart?: () => void;
  onContinue?: () => void;
}

// MBTI Type Colors and Icons
export const MBTI_TYPE_COLORS: Record<string, string> = {
  // Analysts (NT) - Purple
  'INTJ': '#8B5CF6',
  'INTP': '#A855F7', 
  'ENTJ': '#7C3AED',
  'ENTP': '#9333EA',
  
  // Diplomats (NF) - Green
  'INFJ': '#10B981',
  'INFP': '#14B8A6',
  'ENFJ': '#059669',
  'ENFP': '#0D9488',
  
  // Sentinels (SJ) - Blue
  'ISTJ': '#3B82F6',
  'ISFJ': '#60A5FA',
  'ESTJ': '#2563EB',
  'ESFJ': '#1D4ED8',
  
  // Explorers (SP) - Orange/Yellow
  'ISTP': '#F59E0B',
  'ISFP': '#FBBF24',
  'ESTP': '#D97706',
  'ESFP': '#F97316'
};

export const MBTI_TEMPERAMENTS: Record<string, { name_en: string; name_ja: string; color: string }> = {
  'NT': { name_en: 'Analysts', name_ja: '分析家', color: '#8B5CF6' },
  'NF': { name_en: 'Diplomats', name_ja: '外交官', color: '#10B981' },
  'SJ': { name_en: 'Sentinels', name_ja: '番人', color: '#3B82F6' },
  'SP': { name_en: 'Explorers', name_ja: '探検家', color: '#F59E0B' }
};