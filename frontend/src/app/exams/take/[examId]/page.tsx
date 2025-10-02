'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { Button } from '@/components/ui';
import { Progress } from '@/components/ui';
import { Badge } from '@/components/ui';
import {
  AlertTriangle,
  Clock,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { LoadingSpinner } from '@/components/ui';
import { toast } from 'sonner';
import { ExamQuestion } from './exam-question';
import { ExamTimer } from './exam-timer';
import { FaceVerification } from './face-verification';
import { WebUsageMonitor } from './web-usage-monitor';
import { Question, SessionInfo, ExamTakeResponse, Answer } from '@/types/exam';





export default function TakeExamPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const examId = params.examId as string;
  const assignmentId = searchParams.get('assignment');
  const testMode = searchParams.get('mode') === 'test';

  const [examData, setExamData] = useState<ExamTakeResponse | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, Answer>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const [questionStartTime, setQuestionStartTime] = useState<number>(Date.now());
  const [showFaceVerification, setShowFaceVerification] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [lastFaceCheck, setLastFaceCheck] = useState<number>(Date.now());

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const faceCheckRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    startExam();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (faceCheckRef.current) clearInterval(faceCheckRef.current);
    };
  }, []);

  useEffect(() => {
    if (examData?.session.require_face_verification) {
      setShowFaceVerification(true);
      scheduleFaceChecks();
    }
  }, [examData]);

  useEffect(() => {
    if (examData?.session.monitor_web_usage) {
      // Request fullscreen for better monitoring
      if (!document.fullscreenElement && !isFullscreen) {
        document.documentElement
          .requestFullscreen()
          .then(() => {
            setIsFullscreen(true);
          })
          .catch(() => {
            // Fullscreen not supported or denied
            toast.warning('For better security, please avoid switching tabs during the exam');
          });
      }
    }
  }, [examData, isFullscreen]);

  const startExam = async () => {
    try {
      const response = await fetch('/api/exam/exams/take', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          exam_id: parseInt(examId),
          assignment_id: assignmentId ? parseInt(assignmentId) : null,
          test_mode: testMode,
          user_agent: navigator.userAgent,
          screen_resolution: `${screen.width}x${screen.height}`,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to start exam');
      }

      const data: ExamTakeResponse = await response.json();
      setExamData(data);
      setCurrentQuestionIndex(data.session.current_question_index);
      setTimeRemaining(data.time_remaining_seconds);
      setQuestionStartTime(Date.now());

      // Start timer
      if (data.time_remaining_seconds) {
        startTimer(data.time_remaining_seconds);
      }
    } catch (error) {
      console.error('Error starting exam:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to start exam');
      router.push('/exams');
    } finally {
      setLoading(false);
    }
  };

  const startTimer = (initialTime: number) => {
    setTimeRemaining(initialTime);

    timerRef.current = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev === null || prev <= 1) {
          // Time's up - auto submit
          submitExam();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const scheduleFaceChecks = () => {
    if (!examData?.session.require_face_verification) return;

    const interval = examData.session.face_check_interval_minutes * 60 * 1000;

    faceCheckRef.current = setInterval(() => {
      setShowFaceVerification(true);
      setLastFaceCheck(Date.now());
    }, interval);
  };

  const handleAnswerChange = useCallback((questionId: number, answerData: Partial<Answer>) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: {
        ...prev[questionId],
        ...answerData,
        question_id: questionId,
      },
    }));
  }, []);

  const saveAnswer = async (questionId: number, answer: Answer) => {
    try {
      const timeSpent = Math.floor((Date.now() - questionStartTime) / 1000);

      await fetch(`/api/exam/sessions/${examData?.session.id}/answers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          ...answer,
          time_spent_seconds: timeSpent,
        }),
      });
    } catch (error) {
      console.error('Error saving answer:', error);
      toast.error('Failed to save answer');
    }
  };

  const navigateToQuestion = async (index: number) => {
    if (!examData || index < 0 || index >= examData.questions.length) return;

    // Save current answer if exists
    const currentQuestion = examData.questions[currentQuestionIndex];
    const currentAnswer = answers[currentQuestion.id];
    if (currentAnswer) {
      await saveAnswer(currentQuestion.id, currentAnswer);
    }

    setCurrentQuestionIndex(index);
    setQuestionStartTime(Date.now());
  };

  const submitExam = async () => {
    if (!examData || submitting) return;

    setSubmitting(true);
    try {
      // Save current answer
      const currentQuestion = examData.questions[currentQuestionIndex];
      const currentAnswer = answers[currentQuestion.id];
      if (currentAnswer) {
        await saveAnswer(currentQuestion.id, currentAnswer);
      }

      // Complete the exam
      await fetch(`/api/exam/sessions/${examData.session.id}/complete`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      toast.success('Exam submitted successfully!');

      // Exit fullscreen
      if (document.fullscreenElement) {
        document.exitFullscreen();
      }

      if (testMode) {
        router.push(`/admin/exams/${examData.session.exam_id}/preview`);
      } else {
        router.push(`/exams/results/${examData.session.id}`);
      }
    } catch (error) {
      console.error('Error submitting exam:', error);
      toast.error('Failed to submit exam');
    } finally {
      setSubmitting(false);
    }
  };

  const handleWebUsageDetected = async (eventType: string, eventData: any) => {
    if (!examData?.session.monitor_web_usage) return;

    try {
      await fetch(`/api/exam/sessions/${examData.session.id}/monitoring`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          event_type: eventType,
          event_data: eventData,
          severity: eventType === 'tab_switch' ? 'warning' : 'info',
        }),
      });

      if (eventType === 'tab_switch' && !examData.session.allow_web_usage) {
        toast.warning('Tab switching detected. This has been recorded.');
      }
    } catch (error) {
      console.error('Error recording monitoring event:', error);
    }
  };

  const handleFaceVerificationComplete = async (success: boolean) => {
    setShowFaceVerification(false);

    if (!success && examData?.session.require_face_verification) {
      toast.error('Face verification failed. This has been recorded.');

      // Record failed verification
      await handleWebUsageDetected('face_verification_failed', {
        timestamp: new Date().toISOString(),
        reason: 'verification_failed',
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (!examData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 mx-auto text-red-500 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to load exam</h2>
          <p className="text-gray-600 mb-4">There was an error loading the exam data.</p>
          <Button onClick={() => router.push('/exams')}>Back to Exams</Button>
        </div>
      </div>
    );
  }

  const currentQuestion = examData.questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / examData.questions.length) * 100;
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Web Usage Monitor */}
      {examData.session.monitor_web_usage && (
        <WebUsageMonitor
          onWebUsageDetected={handleWebUsageDetected}
          allowWebUsage={examData.session.allow_web_usage}
        />
      )}

      {/* Face Verification Modal */}
      {showFaceVerification && examData.session.require_face_verification && (
        <FaceVerification
          sessionId={examData.session.id}
          onComplete={handleFaceVerificationComplete}
        />
      )}

      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                {testMode && <span className="text-blue-600 mr-2">[TEST MODE]</span>}
                {examData.session.exam_title}
              </h1>
              <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                <span>
                  Question {currentQuestionIndex + 1} of {examData.questions.length}
                </span>
                <span>•</span>
                <span>{answeredCount} answered</span>
                {testMode && (
                  <>
                    <span>•</span>
                    <span className="text-blue-600 font-medium">
                      Practice Mode - No scores saved
                    </span>
                  </>
                )}
              </div>
            </div>

            <div className="flex items-center gap-4">
              {timeRemaining !== null && (
                <ExamTimer timeRemaining={timeRemaining} onTimeUp={submitExam} />
              )}

              <Button
                onClick={submitExam}
                disabled={submitting}
                className="bg-green-600 hover:bg-green-700"
              >
                {submitting ? <LoadingSpinner size="sm" /> : 'Submit Exam'}
              </Button>
            </div>
          </div>

          <div className="mt-4">
            <Progress value={progress} className="h-2" />
          </div>
        </div>
      </div>

      {/* Question Content */}
      <div className="container mx-auto px-4 py-6">
        <div className="max-w-4xl mx-auto">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Question {currentQuestionIndex + 1}</CardTitle>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">
                    {currentQuestion.points} {currentQuestion.points === 1 ? 'point' : 'points'}
                  </Badge>
                  {currentQuestion.time_limit_seconds && (
                    <Badge variant="secondary">
                      <Clock className="h-3 w-3 mr-1" />
                      {Math.floor(currentQuestion.time_limit_seconds / 60)}m
                    </Badge>
                  )}
                  {currentQuestion.is_required && <Badge variant="destructive">Required</Badge>}
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-6">
              <ExamQuestion
                question={currentQuestion}
                answer={answers[currentQuestion.id]}
                onAnswerChange={(answerData) => handleAnswerChange(currentQuestion.id, answerData)}
              />
            </CardContent>
          </Card>

          {/* Navigation */}
          <div className="flex items-center justify-between mt-6">
            <Button
              variant="outline"
              onClick={() => navigateToQuestion(currentQuestionIndex - 1)}
              disabled={currentQuestionIndex === 0}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>

            <div className="flex items-center gap-2">
              {/* Question navigation dots */}
              <div className="flex gap-1">
                {examData.questions.slice(0, 10).map((_, index) => (
                  <button
                    key={index}
                    onClick={() => navigateToQuestion(index)}
                    className={`w-8 h-8 rounded-full text-xs font-medium transition-colors ${
                      index === currentQuestionIndex
                        ? 'bg-blue-600 text-white'
                        : answers[examData.questions[index].id]
                          ? 'bg-green-100 text-green-700 border border-green-300'
                          : 'bg-gray-100 text-gray-700 border border-gray-300 hover:bg-gray-200'
                    }`}
                  >
                    {index + 1}
                  </button>
                ))}
                {examData.questions.length > 10 && <span className="text-gray-500 px-2">...</span>}
              </div>
            </div>

            <Button
              onClick={() => navigateToQuestion(currentQuestionIndex + 1)}
              disabled={currentQuestionIndex === examData.questions.length - 1}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
