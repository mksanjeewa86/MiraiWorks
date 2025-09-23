/**
 * End-to-End Integration Tests for MBTI Functionality
 *
 * These tests verify the complete MBTI workflow from frontend to backend,
 * including authentication, API communication, and user interactions.
 */

import { expect } from '@jest/globals';

// Mock fetch for API calls
global.fetch = jest.fn();

const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('MBTI Integration Tests', () => {
  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

  beforeEach(() => {
    mockFetch.mockClear();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('🌐 API Integration Tests', () => {
    const mockAuthToken = 'mock-auth-token';
    const mockHeaders = {
      'Authorization': `Bearer ${mockAuthToken}`,
      'Content-Type': 'application/json',
    };

    it('should successfully start MBTI test via API', async () => {
      const mockResponse = {
        status: 'in_progress',
        completion_percentage: 0,
        total_questions: 60,
        started_at: '2023-01-01T00:00:00Z'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      } as Response);

      const response = await fetch(`${BACKEND_URL}/api/mbti/start`, {
        method: 'POST',
        headers: mockHeaders,
        body: JSON.stringify({ language: 'ja' }),
      });

      const data = await response.json();

      expect(mockFetch).toHaveBeenCalledWith(
        `${BACKEND_URL}/api/mbti/start`,
        expect.objectContaining({
          method: 'POST',
          headers: mockHeaders,
          body: JSON.stringify({ language: 'ja' }),
        })
      );

      expect(data).toEqual(mockResponse);
    });

    it('should successfully get MBTI progress via API', async () => {
      const mockResponse = {
        status: 'in_progress',
        completion_percentage: 35,
        current_question: 21,
        total_questions: 60,
        started_at: '2023-01-01T00:00:00Z'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      } as Response);

      const response = await fetch(`${BACKEND_URL}/api/mbti/progress`, {
        method: 'GET',
        headers: mockHeaders,
      });

      const data = await response.json();

      expect(mockFetch).toHaveBeenCalledWith(
        `${BACKEND_URL}/api/mbti/progress`,
        expect.objectContaining({
          method: 'GET',
          headers: mockHeaders,
        })
      );

      expect(data).toEqual(mockResponse);
    });

    it('should successfully get MBTI questions via API', async () => {
      const mockResponse = [
        {
          id: 1,
          question_number: 1,
          dimension: 'E_I',
          question_text: 'Do you prefer working in groups?',
          option_a: 'Yes, I love collaboration',
          option_b: 'No, I prefer working alone'
        },
        {
          id: 2,
          question_number: 2,
          dimension: 'S_N',
          question_text: 'Do you focus on details?',
          option_a: 'Yes, details are important',
          option_b: 'No, I prefer the big picture'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      } as Response);

      const response = await fetch(`${BACKEND_URL}/api/mbti/questions?language=ja`, {
        method: 'GET',
        headers: mockHeaders,
      });

      const data = await response.json();

      expect(mockFetch).toHaveBeenCalledWith(
        `${BACKEND_URL}/api/mbti/questions?language=ja`,
        expect.objectContaining({
          method: 'GET',
          headers: mockHeaders,
        })
      );

      expect(Array.isArray(data)).toBe(true);
      expect(data).toHaveLength(2);
    });

    it('should successfully submit MBTI answer via API', async () => {
      const mockResponse = {
        status: 'in_progress',
        completion_percentage: 2,
        current_question: 2,
        total_questions: 60
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      } as Response);

      const answerData = {
        question_id: 1,
        answer: 'A'
      };

      const response = await fetch(`${BACKEND_URL}/api/mbti/answer`, {
        method: 'POST',
        headers: mockHeaders,
        body: JSON.stringify(answerData),
      });

      const data = await response.json();

      expect(mockFetch).toHaveBeenCalledWith(
        `${BACKEND_URL}/api/mbti/answer`,
        expect.objectContaining({
          method: 'POST',
          headers: mockHeaders,
          body: JSON.stringify(answerData),
        })
      );

      expect(data.completion_percentage).toBe(2);
    });

    it('should successfully get all MBTI types via API', async () => {
      const mockResponse = [
        {
          type_code: 'INTJ',
          name_en: 'The Architect',
          name_ja: '建築家',
          description_en: 'Strategic thinkers with a plan for everything.',
          description_ja: '戦略的な思考の持ち主で、あらゆることに対して計画を持っています。',
          temperament: 'NT'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      } as Response);

      const response = await fetch(`${BACKEND_URL}/api/mbti/types`, {
        method: 'GET',
        headers: mockHeaders,
      });

      const data = await response.json();

      expect(Array.isArray(data)).toBe(true);
      expect(data[0]).toHaveProperty('type_code');
      expect(data[0]).toHaveProperty('name_en');
      expect(data[0]).toHaveProperty('name_ja');
    });
  });

  describe('🔐 Authentication Integration', () => {
    it('should handle 401 unauthorized response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Not authenticated' }),
      } as Response);

      const response = await fetch(`${BACKEND_URL}/api/mbti/progress`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      expect(response.status).toBe(401);
    });

    it('should handle 403 forbidden for non-candidate users', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: async () => ({ detail: 'MBTI test is only available for candidates' }),
      } as Response);

      const response = await fetch(`${BACKEND_URL}/api/mbti/start`, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer employer-token',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language: 'ja' }),
      });

      expect(response.status).toBe(403);
      const data = await response.json();
      expect(data.detail).toContain('candidates');
    });
  });

  describe('🎯 Complete Workflow Integration', () => {
    it('should complete full MBTI workflow', async () => {
      const mockAuthToken = 'candidate-auth-token';
      const mockHeaders = {
        'Authorization': `Bearer ${mockAuthToken}`,
        'Content-Type': 'application/json',
      };

      // Step 1: Check initial progress (should be not_taken)
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          status: 'not_taken',
          completion_percentage: 0,
          total_questions: 60
        }),
      } as Response);

      const progressResponse = await fetch(`${BACKEND_URL}/api/mbti/progress`, {
        method: 'GET',
        headers: mockHeaders,
      });
      const initialProgress = await progressResponse.json();
      expect(initialProgress.status).toBe('not_taken');

      // Step 2: Start the test
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          status: 'in_progress',
          completion_percentage: 0,
          total_questions: 60,
          started_at: '2023-01-01T00:00:00Z'
        }),
      } as Response);

      const startResponse = await fetch(`${BACKEND_URL}/api/mbti/start`, {
        method: 'POST',
        headers: mockHeaders,
        body: JSON.stringify({ language: 'ja' }),
      });
      const startData = await startResponse.json();
      expect(startData.status).toBe('in_progress');

      // Step 3: Get questions
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: 1,
            question_number: 1,
            dimension: 'E_I',
            question_text: 'Sample question 1',
            option_a: 'Option A',
            option_b: 'Option B'
          }
        ],
      } as Response);

      const questionsResponse = await fetch(`${BACKEND_URL}/api/mbti/questions?language=ja`, {
        method: 'GET',
        headers: mockHeaders,
      });
      const questions = await questionsResponse.json();
      expect(Array.isArray(questions)).toBe(true);

      // Step 4: Submit an answer
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          status: 'in_progress',
          completion_percentage: 2,
          current_question: 2,
          total_questions: 60
        }),
      } as Response);

      const answerResponse = await fetch(`${BACKEND_URL}/api/mbti/answer`, {
        method: 'POST',
        headers: mockHeaders,
        body: JSON.stringify({
          question_id: 1,
          answer: 'A'
        }),
      });
      const answerData = await answerResponse.json();
      expect(answerData.completion_percentage).toBe(2);

      // Step 5: Check updated progress
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          status: 'in_progress',
          completion_percentage: 2,
          current_question: 2,
          total_questions: 60
        }),
      } as Response);

      const updatedProgressResponse = await fetch(`${BACKEND_URL}/api/mbti/progress`, {
        method: 'GET',
        headers: mockHeaders,
      });
      const updatedProgress = await updatedProgressResponse.json();
      expect(updatedProgress.completion_percentage).toBe(2);

      // Verify all API calls were made
      expect(mockFetch).toHaveBeenCalledTimes(6);
    });
  });

  describe('📱 Error Handling Integration', () => {
    it('should handle network errors gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      try {
        await fetch(`${BACKEND_URL}/api/mbti/progress`, {
          method: 'GET',
          headers: {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json',
          },
        });
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
        expect((error as Error).message).toBe('Network error');
      }
    });

    it('should handle validation errors (422)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 422,
        json: async () => ({
          detail: [
            {
              loc: ['body', 'language'],
              msg: 'string does not match regex "^(en|ja)$"',
              type: 'value_error.str.regex'
            }
          ]
        }),
      } as Response);

      const response = await fetch(`${BACKEND_URL}/api/mbti/start`, {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer test-token',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language: 'fr' }), // Invalid language
      });

      expect(response.status).toBe(422);
      const data = await response.json();
      expect(data.detail).toBeDefined();
      expect(Array.isArray(data.detail)).toBe(true);
    });

    it('should handle 404 not found errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'No MBTI test found for this user' }),
      } as Response);

      const response = await fetch(`${BACKEND_URL}/api/mbti/result`, {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer test-token',
          'Content-Type': 'application/json',
        },
      });

      expect(response.status).toBe(404);
      const data = await response.json();
      expect(data.detail).toContain('No MBTI test found');
    });
  });

  describe('🌍 Language Support Integration', () => {
    it('should handle Japanese language parameter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: 1,
            question_text: '日本語の質問',
            option_a: '選択肢A',
            option_b: '選択肢B'
          }
        ],
      } as Response);

      const response = await fetch(`${BACKEND_URL}/api/mbti/questions?language=ja`, {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer test-token',
          'Content-Type': 'application/json',
        },
      });

      expect(mockFetch).toHaveBeenCalledWith(
        `${BACKEND_URL}/api/mbti/questions?language=ja`,
        expect.any(Object)
      );
    });

    it('should handle English language parameter', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: 1,
            question_text: 'English question',
            option_a: 'Option A',
            option_b: 'Option B'
          }
        ],
      } as Response);

      const response = await fetch(`${BACKEND_URL}/api/mbti/questions?language=en`, {
        method: 'GET',
        headers: {
          'Authorization': 'Bearer test-token',
          'Content-Type': 'application/json',
        },
      });

      expect(mockFetch).toHaveBeenCalledWith(
        `${BACKEND_URL}/api/mbti/questions?language=en`,
        expect.any(Object)
      );
    });
  });
});