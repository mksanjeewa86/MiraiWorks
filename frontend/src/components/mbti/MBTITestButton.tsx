import React, { useState, useEffect } from 'react';
import { PuzzlePieceIcon, PlayIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { mbtiApi } from '@/api/mbti';
import type { MBTITestProgress } from '@/types/mbti';

interface MBTITestButtonProps {
  onStartTest: () => void;
  className?: string;
  language?: 'en' | 'ja';
}

const MBTITestButton: React.FC<MBTITestButtonProps> = ({
  onStartTest,
  className = '',
  language = 'ja'
}) => {
  const [progress, setProgress] = useState<MBTITestProgress | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      const progressData = await mbtiApi.getProgress();
      setProgress(progressData);
    } catch (error) {
      console.error('Failed to load MBTI progress:', error);
      // If user hasn't started test yet, this is expected
      setProgress({
        status: 'not_taken',
        completion_percentage: 0,
        total_questions: 60,
        started_at: undefined
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStartTest = async () => {
    try {
      setLoading(true);

      // Always try to start/restart the test
      await mbtiApi.startTest({ language });

      // Reload progress after starting
      await loadProgress();

      // Open the test modal
      onStartTest();
    } catch (error) {
      console.error('Failed to start MBTI test:', error);
      alert(language === 'ja'
        ? 'テストの開始に失敗しました。しばらく時間をおいて再度お試しください。'
        : 'Failed to start test. Please try again later.'
      );
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`flex items-center justify-center p-4 ${className}`}>
        <ArrowPathIcon className="h-5 w-5 animate-spin text-gray-500" />
      </div>
    );
  }

  const getButtonText = () => {
    if (!progress) {
      return language === 'ja' ? 'MBTI診断を開始' : 'Start MBTI Test';
    }

    switch (progress.status) {
      case 'not_taken':
        return language === 'ja' ? 'MBTI診断を開始' : 'Start MBTI Test';
      case 'in_progress':
        return language === 'ja' 
          ? `診断を続ける (${progress.completion_percentage}%)`
          : `Continue Test (${progress.completion_percentage}%)`;
      case 'completed':
        return language === 'ja' ? '診断を再実行' : 'Retake Test';
      default:
        return language === 'ja' ? 'MBTI診断' : 'MBTI Test';
    }
  };

  const getButtonColor = () => {
    if (!progress || progress.status === 'not_taken') {
      return 'bg-blue-600 hover:bg-blue-700';
    }
    if (progress.status === 'in_progress') {
      return 'bg-orange-600 hover:bg-orange-700';
    }
    return 'bg-green-600 hover:bg-green-700';
  };

  const getIcon = () => {
    if (!progress || progress.status === 'not_taken') {
      return <PlayIcon className="h-5 w-5" />;
    }
    if (progress.status === 'in_progress') {
      return <ArrowPathIcon className="h-5 w-5" />;
    }
    return <PuzzlePieceIcon className="h-5 w-5" />;
  };

  return (
    <div className={className}>
      <button
        onClick={handleStartTest}
        disabled={loading}
        className={`
          flex items-center space-x-2 px-6 py-3 rounded-lg text-white font-medium
          transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed
          ${getButtonColor()}
        `}
      >
        {getIcon()}
        <span>{getButtonText()}</span>
      </button>
      
      {progress && progress.status === 'in_progress' && (
        <div className="mt-2">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>
              {language === 'ja' ? '進捗' : 'Progress'}
            </span>
            <span>
              {progress.current_question && `${progress.current_question}/${progress.total_questions}`}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-orange-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress.completion_percentage}%` }}
            />
          </div>
        </div>
      )}
      
      {progress && progress.status === 'completed' && (
        <p className="mt-2 text-sm text-green-600">
          {language === 'ja' 
            ? '診断が完了しました！結果をプロフィールで確認できます。'
            : 'Test completed! View your results in your profile.'
          }
        </p>
      )}
    </div>
  );
};

export default MBTITestButton;