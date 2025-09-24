'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Trophy,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Eye,
  EyeOff,
  ArrowLeft,
  Calendar,
  BookOpen,
  Target,
} from 'lucide-react';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { toast } from 'sonner';

interface Question {
  id: number;
  question_text: string;
  question_type: string;
  order_index: number;
  points: number;
  options: Record<string, string> | null;
  correct_answers: string[] | null;
  explanation: string | null;
}

interface Answer {
  id: number;
  question_id: number;
  answer_text: string | null;
  selected_options: string[] | null;
  is_correct: boolean | null;
  points_earned: number;
  points_possible: number;
  time_spent_seconds: number | null;
  answered_at: string;
}

interface SessionInfo {
  id: number;
  exam_id: number;
  status: string;
  attempt_number: number;
  started_at: string;
  completed_at: string;
  score: number;
  max_score: number;
  percentage: number;
  passed: boolean | null;
  total_questions: number;
  questions_answered: number;
  web_usage_detected: boolean;
  web_usage_count: number;
  face_verification_failed: boolean;
  face_check_count: number;
  exam_title: string;
  exam_type: string;
}

interface MonitoringEvent {
  id: number;
  event_type: string;
  event_data: any;
  severity: string;
  timestamp: string;
}

interface ExamResults {
  session: SessionInfo;
  answers: Answer[];
  questions?: Question[];
  monitoring_events?: MonitoringEvent[];
}

export default function ExamResultsPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [results, setResults] = useState<ExamResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCorrectAnswers, setShowCorrectAnswers] = useState(false);

  useEffect(() => {
    fetchResults();
  }, [sessionId]);

  const fetchResults = async () => {
    try {
      const response = await fetch(`/api/exam/sessions/${sessionId}/results`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch results');
      }

      const data = await response.json();
      setResults(data);
      setShowCorrectAnswers(!!data.questions); // Show if correct answers are available
    } catch (error) {
      console.error('Error fetching results:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to load results');
      router.push('/exams');
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (startTime: string, endTime: string) => {
    const start = new Date(startTime);
    const end = new Date(endTime);
    const durationMs = end.getTime() - start.getTime();
    const minutes = Math.floor(durationMs / 60000);
    const seconds = Math.floor((durationMs % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  };

  const getScoreColor = (percentage: number) => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPassStatus = (session: SessionInfo) => {
    if (session.passed === null) return null;
    return session.passed
      ? {
          icon: CheckCircle,
          text: 'Passed',
          color: 'bg-green-100 text-green-800 border-green-200',
        }
      : {
          icon: XCircle,
          text: 'Failed',
          color: 'bg-red-100 text-red-800 border-red-200',
        };
  };

  const getQuestionResult = (answer: Answer, question?: Question) => {
    if (answer.is_correct === null) {
      return { icon: AlertTriangle, color: 'text-yellow-600', text: 'Pending Review' };
    }
    return answer.is_correct
      ? { icon: CheckCircle, color: 'text-green-600', text: 'Correct' }
      : { icon: XCircle, color: 'text-red-600', text: 'Incorrect' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (!results) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 mx-auto text-red-500 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Results not available</h2>
          <p className="text-gray-600 mb-4">Unable to load exam results.</p>
          <Button asChild>
            <Link href="/exams">Back to Exams</Link>
          </Button>
        </div>
      </div>
    );
  }

  const { session, answers, questions, monitoring_events } = results;
  const passStatus = getPassStatus(session);
  const correctAnswers = answers.filter((a) => a.is_correct === true).length;
  const incorrectAnswers = answers.filter((a) => a.is_correct === false).length;
  const pendingAnswers = answers.filter((a) => a.is_correct === null).length;

  return (
    <div className="container mx-auto py-6 px-4 max-w-6xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button variant="outline" asChild>
          <Link href="/exams">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Exams
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{session.exam_title}</h1>
          <p className="text-gray-600">Exam Results - Attempt #{session.attempt_number}</p>
        </div>
      </div>

      {/* Results Overview */}
      <div className="grid gap-6 md:grid-cols-3 mb-8">
        {/* Score Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Final Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <div className={`text-3xl font-bold ${getScoreColor(session.percentage)}`}>
                  {session.percentage.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-500">
                  {session.score} / {session.max_score} points
                </div>
              </div>
              <div className="flex flex-col items-center">
                <Trophy className={`h-8 w-8 ${getScoreColor(session.percentage)}`} />
                {passStatus && (
                  <Badge className={`mt-2 ${passStatus.color}`}>
                    <passStatus.icon className="h-3 w-3 mr-1" />
                    {passStatus.text}
                  </Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Time Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Duration</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {formatDuration(session.started_at, session.completed_at)}
                </div>
                <div className="text-sm text-gray-500">
                  {session.questions_answered} / {session.total_questions} answered
                </div>
              </div>
              <Clock className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        {/* Performance Card */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-green-600">Correct: {correctAnswers}</span>
                <span className="text-red-600">Incorrect: {incorrectAnswers}</span>
              </div>
              {pendingAnswers > 0 && (
                <div className="text-sm text-yellow-600">Pending Review: {pendingAnswers}</div>
              )}
              <Progress value={(correctAnswers / answers.length) * 100} className="h-2" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Security Monitoring (if any issues) */}
      {(session.web_usage_detected || session.face_verification_failed) && (
        <Card className="mb-8 border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="text-orange-800 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Security Monitoring Report
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {session.web_usage_detected && (
                <div className="flex items-center justify-between p-3 bg-white rounded-lg border">
                  <div>
                    <div className="font-medium text-gray-900">Web Usage Detected</div>
                    <div className="text-sm text-gray-600">
                      {session.web_usage_count} incidents recorded
                    </div>
                  </div>
                  <Badge variant="outline" className="text-orange-700 border-orange-300">
                    {session.web_usage_count}
                  </Badge>
                </div>
              )}

              {session.face_verification_failed && (
                <div className="flex items-center justify-between p-3 bg-white rounded-lg border">
                  <div>
                    <div className="font-medium text-gray-900">Face Verification Issues</div>
                    <div className="text-sm text-gray-600">
                      {session.face_check_count} failed checks
                    </div>
                  </div>
                  <Badge variant="outline" className="text-orange-700 border-orange-300">
                    {session.face_check_count}
                  </Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Question-by-Question Results */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Question Results</CardTitle>
            {questions && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowCorrectAnswers(!showCorrectAnswers)}
              >
                {showCorrectAnswers ? (
                  <>
                    <EyeOff className="h-4 w-4 mr-2" />
                    Hide Answers
                  </>
                ) : (
                  <>
                    <Eye className="h-4 w-4 mr-2" />
                    Show Correct Answers
                  </>
                )}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {answers.map((answer, index) => {
              const question = questions?.find((q) => q.id === answer.question_id);
              const result = getQuestionResult(answer, question);

              return (
                <div key={answer.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline">Q{index + 1}</Badge>
                        <Badge
                          className={`border ${
                            result.icon === CheckCircle
                              ? 'bg-green-100 text-green-800 border-green-200'
                              : result.icon === XCircle
                                ? 'bg-red-100 text-red-800 border-red-200'
                                : 'bg-yellow-100 text-yellow-800 border-yellow-200'
                          }`}
                        >
                          <result.icon className="h-3 w-3 mr-1" />
                          {result.text}
                        </Badge>
                      </div>

                      {question && (
                        <div className="text-gray-900 mb-2">{question.question_text}</div>
                      )}
                    </div>

                    <div className="text-right">
                      <div className="font-medium">
                        {answer.points_earned} / {answer.points_possible}
                      </div>
                      {answer.time_spent_seconds && (
                        <div className="text-sm text-gray-500">
                          {Math.floor(answer.time_spent_seconds / 60)}:
                          {(answer.time_spent_seconds % 60).toString().padStart(2, '0')}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Your Answer */}
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-700">Your Answer:</div>
                    <div className="bg-gray-50 p-3 rounded">
                      {answer.selected_options && answer.selected_options.length > 0 ? (
                        <div className="space-y-1">
                          {answer.selected_options.map((option) => (
                            <div key={option} className="flex items-center gap-2">
                              <Badge variant="outline" className="text-xs">
                                {option}
                              </Badge>
                              {question?.options?.[option] && (
                                <span className="text-sm">{question.options[option]}</span>
                              )}
                            </div>
                          ))}
                        </div>
                      ) : answer.answer_text ? (
                        <div className="text-sm">{answer.answer_text}</div>
                      ) : (
                        <div className="text-sm text-gray-500 italic">No answer provided</div>
                      )}
                    </div>
                  </div>

                  {/* Correct Answer (if available and toggled on) */}
                  {showCorrectAnswers && question?.correct_answers && (
                    <div className="space-y-2 mt-3">
                      <div className="text-sm font-medium text-green-700">Correct Answer:</div>
                      <div className="bg-green-50 p-3 rounded border border-green-200">
                        {question.correct_answers.map((option) => (
                          <div key={option} className="flex items-center gap-2">
                            <Badge variant="outline" className="text-xs bg-green-100">
                              {option}
                            </Badge>
                            {question.options?.[option] && (
                              <span className="text-sm">{question.options[option]}</span>
                            )}
                          </div>
                        ))}
                      </div>

                      {question.explanation && (
                        <div className="mt-2">
                          <div className="text-sm font-medium text-gray-700">Explanation:</div>
                          <div className="text-sm text-gray-600 mt-1">{question.explanation}</div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Session Details */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle className="text-sm font-medium text-gray-600">Session Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 text-sm">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <span>Started: {new Date(session.started_at).toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-400" />
              <span>Completed: {new Date(session.completed_at).toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-gray-400" />
              <span>Exam Type: {session.exam_type}</span>
            </div>
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-gray-400" />
              <span>Attempt: #{session.attempt_number}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
