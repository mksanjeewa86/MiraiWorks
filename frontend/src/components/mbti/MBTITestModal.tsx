import React, { useState, useEffect, useCallback } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { XMarkIcon, ChevronLeftIcon, ChevronRightIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { mbtiApi } from '@/api/mbti';
import type { MBTIQuestion, MBTITestResult, MBTITestModalProps } from '@/types/mbti';

const MBTITestModal: React.FC<MBTITestModalProps> = ({
  isOpen,
  onClose,
  onComplete
}) => {
  const [questions, setQuestions] = useState<MBTIQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, 'A' | 'B'>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [language, setLanguage] = useState<'en' | 'ja'>('ja');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadQuestions();
    }
  }, [isOpen, language]);

  const loadQuestions = async () => {
    try {
      setLoading(true);
      setError(null);
      const questionsData = await mbtiApi.getQuestions(language);
      setQuestions(questionsData);
    } catch (err) {
      console.error('Failed to load questions:', err);
      const errorMessage = language === 'ja'
        ? 'MBTI質問の読み込みに失敗しました。管理者がまだMBTI質問を設定していない可能性があります。'
        : 'Failed to load MBTI questions. The administrator may not have set up MBTI questions yet.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = useCallback((answer: 'A' | 'B') => {
    if (!questions[currentQuestionIndex]) return;
    
    const questionId = questions[currentQuestionIndex].id;
    setAnswers(prev => ({ ...prev, [questionId]: answer }));

    // Auto-advance to next question after a short delay
    setTimeout(() => {
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(prev => prev + 1);
      }
    }, 300);
  }, [currentQuestionIndex, questions]);

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const isQuestionAnswered = (index: number): boolean => {
    const question = questions[index];
    return question ? answers[question.id] !== undefined : false;
  };

  const handleSubmit = async () => {
    try {
      setSubmitting(true);
      setError(null);
      
      // Submit all answers
      const result = await mbtiApi.submitTest({ answers });
      
      // Notify parent component
      onComplete(result);
      
      // Reset state
      setAnswers({});
      setCurrentQuestionIndex(0);
      
      // Close modal
      onClose();
    } catch (err) {
      console.error('Failed to submit test:', err);
      setError(language === 'ja' ? 'テストの提出に失敗しました' : 'Failed to submit test');
    } finally {
      setSubmitting(false);
    }
  };

  const progress = questions.length > 0 
    ? Math.round((Object.keys(answers).length / questions.length) * 100)
    : 0;

  const currentQuestion = questions[currentQuestionIndex];
  const allQuestionsAnswered = questions.length > 0 && Object.keys(answers).length === questions.length;

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                  <Dialog.Title className="text-2xl font-bold text-gray-900">
                    {language === 'ja' ? 'MBTI性格診断' : 'MBTI Personality Test'}
                  </Dialog.Title>
                  <div className="flex items-center space-x-4">
                    {/* Language Toggle */}
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setLanguage('ja')}
                        className={`px-3 py-1 rounded ${
                          language === 'ja' 
                            ? 'bg-blue-600 text-white' 
                            : 'bg-gray-200 text-gray-700'
                        }`}
                      >
                        日本語
                      </button>
                      <button
                        onClick={() => setLanguage('en')}
                        className={`px-3 py-1 rounded ${
                          language === 'en' 
                            ? 'bg-blue-600 text-white' 
                            : 'bg-gray-200 text-gray-700'
                        }`}
                      >
                        English
                      </button>
                    </div>
                    <button
                      onClick={onClose}
                      className="text-gray-400 hover:text-gray-500"
                    >
                      <XMarkIcon className="h-6 w-6" />
                    </button>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-6">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>
                      {language === 'ja' ? '進捗' : 'Progress'}: {progress}%
                    </span>
                    <span>
                      {language === 'ja' 
                        ? `${Object.keys(answers).length} / ${questions.length} 問完了`
                        : `${Object.keys(answers).length} / ${questions.length} Completed`
                      }
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>

                {/* Content */}
                {loading ? (
                  <div className="flex justify-center items-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
                  </div>
                ) : error ? (
                  <div className="text-center py-12">
                    <p className="text-red-600 mb-4">{error}</p>
                    <button
                      onClick={loadQuestions}
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      {language === 'ja' ? '再試行' : 'Retry'}
                    </button>
                  </div>
                ) : currentQuestion ? (
                  <div className="space-y-6">
                    {/* Question */}
                    <div className="text-center py-6">
                      <p className="text-sm text-gray-500 mb-2">
                        {language === 'ja' 
                          ? `質問 ${currentQuestionIndex + 1} / ${questions.length}`
                          : `Question ${currentQuestionIndex + 1} / ${questions.length}`
                        }
                      </p>
                      <h3 className="text-xl font-semibold text-gray-900">
                        {currentQuestion.question_text}
                      </h3>
                    </div>

                    {/* Options */}
                    <div className="space-y-4">
                      <button
                        onClick={() => handleAnswer('A')}
                        className={`w-full p-6 text-left rounded-lg border-2 transition-all ${
                          answers[currentQuestion.id] === 'A'
                            ? 'border-blue-600 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center">
                          <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold mr-4">
                            A
                          </span>
                          <span className="text-gray-900">
                            {currentQuestion.option_a}
                          </span>
                          {answers[currentQuestion.id] === 'A' && (
                            <CheckCircleIcon className="h-5 w-5 text-blue-600 ml-auto" />
                          )}
                        </div>
                      </button>

                      <button
                        onClick={() => handleAnswer('B')}
                        className={`w-full p-6 text-left rounded-lg border-2 transition-all ${
                          answers[currentQuestion.id] === 'B'
                            ? 'border-blue-600 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        <div className="flex items-center">
                          <span className="flex-shrink-0 w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold mr-4">
                            B
                          </span>
                          <span className="text-gray-900">
                            {currentQuestion.option_b}
                          </span>
                          {answers[currentQuestion.id] === 'B' && (
                            <CheckCircleIcon className="h-5 w-5 text-blue-600 ml-auto" />
                          )}
                        </div>
                      </button>
                    </div>

                    {/* Navigation */}
                    <div className="flex justify-between items-center pt-6">
                      <button
                        onClick={handlePrevious}
                        disabled={currentQuestionIndex === 0}
                        className={`flex items-center space-x-2 px-4 py-2 rounded ${
                          currentQuestionIndex === 0
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        <ChevronLeftIcon className="h-5 w-5" />
                        <span>{language === 'ja' ? '前へ' : 'Previous'}</span>
                      </button>

                      {currentQuestionIndex === questions.length - 1 && allQuestionsAnswered ? (
                        <button
                          onClick={handleSubmit}
                          disabled={submitting}
                          className="flex items-center space-x-2 px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <CheckCircleIcon className="h-5 w-5" />
                          <span>
                            {submitting 
                              ? (language === 'ja' ? '提出中...' : 'Submitting...')
                              : (language === 'ja' ? '診断を完了' : 'Complete Test')
                            }
                          </span>
                        </button>
                      ) : (
                        <button
                          onClick={handleNext}
                          disabled={currentQuestionIndex === questions.length - 1 || !isQuestionAnswered(currentQuestionIndex)}
                          className={`flex items-center space-x-2 px-4 py-2 rounded ${
                            currentQuestionIndex === questions.length - 1 || !isQuestionAnswered(currentQuestionIndex)
                              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                              : 'bg-blue-600 text-white hover:bg-blue-700'
                          }`}
                        >
                          <span>{language === 'ja' ? '次へ' : 'Next'}</span>
                          <ChevronRightIcon className="h-5 w-5" />
                        </button>
                      )}
                    </div>

                    {/* Question Navigation Dots */}
                    <div className="flex flex-wrap justify-center gap-2 pt-4">
                      {questions.map((q, index) => (
                        <button
                          key={q.id}
                          onClick={() => setCurrentQuestionIndex(index)}
                          className={`w-8 h-8 rounded-full text-xs font-medium ${
                            index === currentQuestionIndex
                              ? 'bg-blue-600 text-white'
                              : isQuestionAnswered(index)
                              ? 'bg-green-100 text-green-700'
                              : 'bg-gray-200 text-gray-600'
                          }`}
                        >
                          {index + 1}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : null}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default MBTITestModal;