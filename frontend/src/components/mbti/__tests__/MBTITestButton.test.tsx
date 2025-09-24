import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { mbtiApi } from '@/api/mbti';
import MBTITestButton from '../MBTITestButton';
import type { MBTITestProgress } from '@/types/mbti';

// Mock the MBTI API
jest.mock('@/api/mbti', () => ({
  mbtiApi: {
    getProgress: jest.fn(),
    startTest: jest.fn(),
  },
}));

const mockMbtiApi = mbtiApi as jest.Mocked<typeof mbtiApi>;

describe('MBTITestButton', () => {
  const mockOnStartTest = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('🟢 Success Scenarios', () => {
    it('should render start button for new user (not_taken status)', async () => {
      const progressData: MBTITestProgress = {
        status: 'not_taken',
        completion_percentage: 0,
        current_question: null,
        total_questions: 60,
        started_at: undefined,
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);

      render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByText('MBTI診断を開始')).toBeInTheDocument();
      });

      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-blue-600');
      expect(screen.getByTestId('play-icon') || screen.querySelector('svg')).toBeInTheDocument();
    });

    it('should render continue button for in-progress test', async () => {
      const progressData: MBTITestProgress = {
        status: 'in_progress',
        completion_percentage: 35,
        current_question: 21,
        total_questions: 60,
        started_at: '2023-01-01T00:00:00Z',
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);

      render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

      await waitFor(() => {
        expect(screen.getByText('診断を続ける (35%)')).toBeInTheDocument();
      });

      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-orange-600');

      // Check progress bar
      expect(screen.getByText('進捗')).toBeInTheDocument();
      expect(screen.getByText('21/60')).toBeInTheDocument();

      const progressBar =
        screen.getByRole('progressbar') || document.querySelector('[style*="width: 35%"]');
      expect(progressBar).toBeInTheDocument();
    });

    it('should render retake button for completed test', async () => {
      const progressData: MBTITestProgress = {
        status: 'completed',
        completion_percentage: 100,
        current_question: null,
        total_questions: 60,
        started_at: '2023-01-01T00:00:00Z',
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);

      render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

      await waitFor(() => {
        expect(screen.getByText('診断を再実行')).toBeInTheDocument();
      });

      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-green-600');

      expect(
        screen.getByText('診断が完了しました！結果をプロフィールで確認できます。')
      ).toBeInTheDocument();
    });

    it('should handle English language correctly', async () => {
      const progressData: MBTITestProgress = {
        status: 'not_taken',
        completion_percentage: 0,
        current_question: null,
        total_questions: 60,
        started_at: undefined,
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);

      render(<MBTITestButton onStartTest={mockOnStartTest} language="en" />);

      await waitFor(() => {
        expect(screen.getByText('Start MBTI Test')).toBeInTheDocument();
      });
    });

    it('should successfully start test when button is clicked', async () => {
      const progressData: MBTITestProgress = {
        status: 'not_taken',
        completion_percentage: 0,
        current_question: null,
        total_questions: 60,
        started_at: undefined,
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);
      mockMbtiApi.startTest.mockResolvedValue({
        status: 'in_progress',
        completion_percentage: 0,
        total_questions: 60,
        started_at: '2023-01-01T00:00:00Z',
      });

      render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

      await waitFor(() => {
        expect(screen.getByText('MBTI診断を開始')).toBeInTheDocument();
      });

      const button = screen.getByRole('button');
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockMbtiApi.startTest).toHaveBeenCalledWith({ language: 'ja' });
        expect(mockOnStartTest).toHaveBeenCalled();
      });
    });
  });

  describe('🔴 Error Scenarios', () => {
    it('should handle API error when loading progress', async () => {
      mockMbtiApi.getProgress.mockRejectedValue(new Error('API Error'));

      render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

      await waitFor(() => {
        expect(screen.getByText('MBTI診断を開始')).toBeInTheDocument();
      });

      // Should fallback to not_taken state
      const button = screen.getByRole('button');
      expect(button).toHaveClass('bg-blue-600');
    });

    it('should handle API error when starting test', async () => {
      const progressData: MBTITestProgress = {
        status: 'not_taken',
        completion_percentage: 0,
        current_question: null,
        total_questions: 60,
        started_at: undefined,
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);
      mockMbtiApi.startTest.mockRejectedValue(new Error('Start test failed'));

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

      await waitFor(() => {
        expect(screen.getByText('MBTI診断を開始')).toBeInTheDocument();
      });

      const button = screen.getByRole('button');
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockMbtiApi.startTest).toHaveBeenCalled();
        expect(consoleSpy).toHaveBeenCalledWith('Failed to start MBTI test:', expect.any(Error));
        // onStartTest should not be called if API fails
        expect(mockOnStartTest).not.toHaveBeenCalled();
      });

      consoleSpy.mockRestore();
    });
  });

  describe('🎯 Loading States', () => {
    it('should show loading spinner initially', () => {
      mockMbtiApi.getProgress.mockReturnValue(new Promise(() => {})); // Never resolves

      render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

      expect(
        screen.getByTestId('loading-spinner') || document.querySelector('[class*="animate-spin"]')
      ).toBeInTheDocument();
    });

    it('should disable button during test start', async () => {
      const progressData: MBTITestProgress = {
        status: 'not_taken',
        completion_percentage: 0,
        current_question: null,
        total_questions: 60,
        started_at: undefined,
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);
      mockMbtiApi.startTest.mockReturnValue(new Promise(() => {})); // Never resolves

      render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

      await waitFor(() => {
        expect(screen.getByText('MBTI診断を開始')).toBeInTheDocument();
      });

      const button = screen.getByRole('button');
      fireEvent.click(button);

      await waitFor(() => {
        expect(button).toBeDisabled();
        expect(button).toHaveClass('disabled:opacity-50');
      });
    });
  });

  describe('🌐 Internationalization', () => {
    it('should display Japanese text correctly', async () => {
      const progressData: MBTITestProgress = {
        status: 'in_progress',
        completion_percentage: 50,
        current_question: 30,
        total_questions: 60,
        started_at: '2023-01-01T00:00:00Z',
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);

      render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

      await waitFor(() => {
        expect(screen.getByText('診断を続ける (50%)')).toBeInTheDocument();
        expect(screen.getByText('進捗')).toBeInTheDocument();
      });
    });

    it('should display English text correctly', async () => {
      const progressData: MBTITestProgress = {
        status: 'in_progress',
        completion_percentage: 50,
        current_question: 30,
        total_questions: 60,
        started_at: '2023-01-01T00:00:00Z',
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);

      render(<MBTITestButton onStartTest={mockOnStartTest} language="en" />);

      await waitFor(() => {
        expect(screen.getByText('Continue Test (50%)')).toBeInTheDocument();
        expect(screen.getByText('Progress')).toBeInTheDocument();
      });
    });

    it('should handle all test statuses in both languages', async () => {
      const testCases = [
        { status: 'not_taken', ja: 'MBTI診断を開始', en: 'Start MBTI Test' },
        { status: 'completed', ja: '診断を再実行', en: 'Retake Test' },
      ] as const;

      for (const testCase of testCases) {
        const progressData: MBTITestProgress = {
          status: testCase.status,
          completion_percentage: testCase.status === 'completed' ? 100 : 0,
          current_question: null,
          total_questions: 60,
          started_at: testCase.status !== 'not_taken' ? '2023-01-01T00:00:00Z' : undefined,
        };

        mockMbtiApi.getProgress.mockResolvedValue(progressData);

        // Test Japanese
        const { unmount: unmountJa } = render(
          <MBTITestButton onStartTest={mockOnStartTest} language="ja" />
        );

        await waitFor(() => {
          expect(screen.getByText(testCase.ja)).toBeInTheDocument();
        });

        unmountJa();

        // Test English
        const { unmount: unmountEn } = render(
          <MBTITestButton onStartTest={mockOnStartTest} language="en" />
        );

        await waitFor(() => {
          expect(screen.getByText(testCase.en)).toBeInTheDocument();
        });

        unmountEn();
      }
    });
  });

  describe('🎨 Visual States', () => {
    it('should apply correct CSS classes for different states', async () => {
      const testCases = [
        { status: 'not_taken', expectedColor: 'bg-blue-600' },
        { status: 'in_progress', expectedColor: 'bg-orange-600' },
        { status: 'completed', expectedColor: 'bg-green-600' },
      ] as const;

      for (const testCase of testCases) {
        const progressData: MBTITestProgress = {
          status: testCase.status,
          completion_percentage:
            testCase.status === 'completed' ? 100 : testCase.status === 'in_progress' ? 35 : 0,
          current_question: testCase.status === 'in_progress' ? 21 : null,
          total_questions: 60,
          started_at: testCase.status !== 'not_taken' ? '2023-01-01T00:00:00Z' : undefined,
        };

        mockMbtiApi.getProgress.mockResolvedValue(progressData);

        const { unmount } = render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

        await waitFor(() => {
          const button = screen.getByRole('button');
          expect(button).toHaveClass(testCase.expectedColor);
        });

        unmount();
      }
    });

    it('should apply custom className prop', async () => {
      const progressData: MBTITestProgress = {
        status: 'not_taken',
        completion_percentage: 0,
        current_question: null,
        total_questions: 60,
        started_at: undefined,
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);

      render(
        <MBTITestButton onStartTest={mockOnStartTest} className="custom-test-class" language="ja" />
      );

      await waitFor(() => {
        const container = screen.getByRole('button').closest('div');
        expect(container).toHaveClass('custom-test-class');
      });
    });
  });

  describe('🔄 Component Lifecycle', () => {
    it('should call loadProgress on mount', async () => {
      const progressData: MBTITestProgress = {
        status: 'not_taken',
        completion_percentage: 0,
        current_question: null,
        total_questions: 60,
        started_at: undefined,
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);

      render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

      expect(mockMbtiApi.getProgress).toHaveBeenCalledTimes(1);
    });

    it('should handle component unmount gracefully', async () => {
      const progressData: MBTITestProgress = {
        status: 'not_taken',
        completion_percentage: 0,
        current_question: null,
        total_questions: 60,
        started_at: undefined,
      };

      mockMbtiApi.getProgress.mockResolvedValue(progressData);

      const { unmount } = render(<MBTITestButton onStartTest={mockOnStartTest} language="ja" />);

      await waitFor(() => {
        expect(screen.getByText('MBTI診断を開始')).toBeInTheDocument();
      });

      // Should not throw error when unmounted
      expect(() => unmount()).not.toThrow();
    });
  });
});
