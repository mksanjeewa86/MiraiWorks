import { API_ENDPOINTS } from './config';
import { apiClient } from './apiClient';
import type {
  MBTIQuestion,
  MBTIAnswerSubmit,
  MBTITestStart,
  MBTITestSubmit,
  MBTITestResult,
  MBTITestSummary,
  MBTITestProgress,
  MBTITypeInfo
} from '@/types/mbti';

export const mbtiApi = {
  // Test lifecycle
  async startTest(testData: MBTITestStart): Promise<MBTITestProgress> {
    const response = await apiClient.post<MBTITestProgress>(
      API_ENDPOINTS.MBTI.START,
      testData
    );
    return response.data;
  },

  async getQuestions(language: 'en' | 'ja' = 'ja'): Promise<MBTIQuestion[]> {
    const params = new URLSearchParams({ language });
    const response = await apiClient.get<MBTIQuestion[]>(
      `${API_ENDPOINTS.MBTI.QUESTIONS}?${params}`
    );
    return response.data;
  },

  async submitAnswer(answer: MBTIAnswerSubmit): Promise<MBTITestProgress> {
    const response = await apiClient.post<MBTITestProgress>(
      API_ENDPOINTS.MBTI.ANSWER,
      answer
    );
    return response.data;
  },

  async submitTest(submission: MBTITestSubmit): Promise<MBTITestResult> {
    const response = await apiClient.post<MBTITestResult>(
      API_ENDPOINTS.MBTI.SUBMIT,
      submission
    );
    return response.data;
  },

  // Results
  async getResult(): Promise<MBTITestResult> {
    const response = await apiClient.get<MBTITestResult>(
      API_ENDPOINTS.MBTI.RESULT
    );
    return response.data;
  },

  async getSummary(language: 'en' | 'ja' = 'ja'): Promise<MBTITestSummary> {
    const params = new URLSearchParams({ language });
    const response = await apiClient.get<MBTITestSummary>(
      `${API_ENDPOINTS.MBTI.SUMMARY}?${params}`
    );
    return response.data;
  },

  async getProgress(): Promise<MBTITestProgress> {
    const response = await apiClient.get<MBTITestProgress>(
      API_ENDPOINTS.MBTI.PROGRESS
    );
    return response.data;
  },

  // Type information
  async getAllTypes(): Promise<MBTITypeInfo[]> {
    const response = await apiClient.get<MBTITypeInfo[]>(
      API_ENDPOINTS.MBTI.TYPES
    );
    return response.data;
  },

  async getTypeDetails(type: string): Promise<MBTITypeInfo> {
    const response = await apiClient.get<MBTITypeInfo>(
      API_ENDPOINTS.MBTI.TYPE_DETAILS(type)
    );
    return response.data;
  }
};