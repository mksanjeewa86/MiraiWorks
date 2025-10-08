'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  LoadingSpinner,
} from '@/components/ui';
import {
  ArrowLeft,
  Clock,
  CheckCircle,
  XCircle,
  Award,
  User,
  Calendar,
  FileText,
  AlertTriangle,
} from 'lucide-react';
import Link from 'next/link';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { examTakingApi, monitoringApi, examApi } from '@/api/exam';
import type { ExamResults, MonitoringEvent, ExamInfo } from '@/types/exam';
import { toast } from 'sonner';

function ExamSessionReviewContent() {
  const params = useParams();
  const router = useRouter();
  const sessionId = parseInt(params.sessionId as string);

  const [results, setResults] = useState<ExamResults | null>(null);
  const [exam, setExam] = useState<ExamInfo | null>(null);
  const [monitoringEvents, setMonitoringEvents] = useState<MonitoringEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [eventsLoading, setEventsLoading] = useState(true);

  useEffect(() => {
    fetchResults();
    fetchMonitoringEvents();
  }, [sessionId]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const response = await examTakingApi.getResults(sessionId);
      if (response.data) {
        setResults(response.data);
        // Fetch exam details
        const examResponse = await examApi.getExam(response.data.session.exam_id);
        if (examResponse.data) {
          setExam(examResponse.data);
        }
      }
    } catch (error) {
      toast.error('Failed to load session results');
    } finally {
      setLoading(false);
    }
  };

  const fetchMonitoringEvents = async () => {
    try {
      setEventsLoading(true);
      const response = await monitoringApi.getEvents(sessionId);
      if (response.data) {
        setMonitoringEvents(response.data);
      }
    } catch (error) {
      // Events are optional, don't show error
      console.error('Failed to load monitoring events:', error);
    } finally {
      setEventsLoading(false);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <LoadingSpinner />
        </div>
      </AppLayout>
    );
  }

  if (!results || !exam) {
    return (
      <AppLayout>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            {!results ? 'Session not found' : 'Loading exam details...'}
          </h2>
          {!results && (
            <Button asChild>
              <Link href="/admin/exams">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Exams
              </Link>
            </Button>
          )}
        </div>
      </AppLayout>
    );
  }

  const { session, answers, questions } = results;

  // Create a map of question_id to question for easy lookup
  const questionsMap = new Map(questions?.map((q) => [q.id, q]) || []);

  // Calculate time taken
  const timeTaken =
    session.started_at && session.completed_at
      ? Math.round(
          (new Date(session.completed_at).getTime() - new Date(session.started_at).getTime()) /
            60000
        )
      : null;

  // Get status badge color
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'warning';
      case 'suspended':
        return 'error';
      default:
        return 'secondary';
    }
  };

  // Get severity badge for monitoring events
  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <Badge variant="error">{severity}</Badge>;
      case 'warning':
        return <Badge variant="warning">{severity}</Badge>;
      default:
        return <Badge variant="secondary">{severity}</Badge>;
    }
  };

  return (
    <AppLayout>
      <div className="py-6">
        <div className="mb-6">
          <Button variant="ghost" asChild className="mb-2">
            <Link href="/admin/exams">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Exams
            </Link>
          </Button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Exam Session Review</h1>
              <p className="text-gray-600">
                Session #{session.id} - {exam.title}
              </p>
            </div>
            <Badge variant={getStatusColor(session.status)}>{session.status}</Badge>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Left column - Main info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Session Overview */}
            <Card>
              <CardHeader>
                <CardTitle>Session Overview</CardTitle>
                <CardDescription>General information about this exam session</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Candidate ID</div>
                    <div className="font-medium">{session.candidate_id}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Exam Type</div>
                    <div className="font-medium">{exam.exam_type}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Started At</div>
                    <div className="font-medium">
                      {session.started_at
                        ? new Date(session.started_at).toLocaleString()
                        : 'Not started'}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Completed At</div>
                    <div className="font-medium">
                      {session.completed_at
                        ? new Date(session.completed_at).toLocaleString()
                        : 'Not completed'}
                    </div>
                  </div>
                  {timeTaken && (
                    <div>
                      <div className="text-sm text-gray-500 mb-1">Time Taken</div>
                      <div className="font-medium flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {timeTaken} minutes
                      </div>
                    </div>
                  )}
                  {session.score !== null && (
                    <div>
                      <div className="text-sm text-gray-500 mb-1">Final Score</div>
                      <div className="font-medium flex items-center">
                        <Award className="h-4 w-4 mr-1" />
                        {session.score.toFixed(1)}%
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Answers */}
            <Card>
              <CardHeader>
                <CardTitle>Answers ({answers.length})</CardTitle>
                <CardDescription>Detailed breakdown of candidate answers</CardDescription>
              </CardHeader>
              <CardContent>
                {answers.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">No answers submitted yet</div>
                ) : (
                  <div className="space-y-4">
                    {answers.map((answer, index) => (
                      <div
                        key={answer.id}
                        className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900">Question {index + 1}</span>
                            {answer.is_correct !== null && (
                              <>
                                {answer.is_correct ? (
                                  <CheckCircle className="h-5 w-5 text-green-500" />
                                ) : (
                                  <XCircle className="h-5 w-5 text-red-500" />
                                )}
                              </>
                            )}
                          </div>
                          {answer.points_earned !== null && (
                            <Badge variant="outline">
                              {answer.points_earned} / {answer.points_possible} points
                            </Badge>
                          )}
                        </div>

                        <div className="text-sm text-gray-600 mb-2">
                          {questionsMap.get(answer.question_id)?.question_text ||
                            'Question not found'}
                        </div>

                        {answer.answer_text && (
                          <div className="mt-2 p-3 bg-gray-100 rounded-md">
                            <div className="text-xs text-gray-500 mb-1">Answer:</div>
                            <div className="text-sm">{answer.answer_text}</div>
                          </div>
                        )}

                        {answer.selected_options && answer.selected_options.length > 0 && (
                          <div className="mt-2">
                            <div className="text-xs text-gray-500 mb-1">Selected Options:</div>
                            <div className="flex flex-wrap gap-2">
                              {answer.selected_options.map((option, i) => (
                                <Badge key={i} variant="secondary">
                                  {option}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        {answer.time_spent_seconds && (
                          <div className="mt-2 text-xs text-gray-500">
                            Time spent: {Math.round(answer.time_spent_seconds / 60)} minutes
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right column - Monitoring & Stats */}
          <div className="space-y-6">
            {/* Score Summary */}
            {session.status === 'completed' && session.score !== null && (
              <Card>
                <CardHeader>
                  <CardTitle>Score Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    <div className="text-5xl font-bold text-indigo-600 mb-2">
                      {session.score.toFixed(1)}%
                    </div>
                    {exam.passing_score && (
                      <div className="mt-4">
                        {session.score >= exam.passing_score ? (
                          <Badge variant="success" className="text-lg py-2 px-4">
                            <CheckCircle className="h-5 w-5 mr-2" />
                            PASSED
                          </Badge>
                        ) : (
                          <Badge variant="error" className="text-lg py-2 px-4">
                            <XCircle className="h-5 w-5 mr-2" />
                            NOT PASSED
                          </Badge>
                        )}
                        <div className="text-sm text-gray-500 mt-2">
                          Passing score: {exam.passing_score}%
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Monitoring Events */}
            <Card>
              <CardHeader>
                <CardTitle>Monitoring Events</CardTitle>
                <CardDescription>Security and integrity events</CardDescription>
              </CardHeader>
              <CardContent>
                {eventsLoading ? (
                  <LoadingSpinner />
                ) : monitoringEvents.length === 0 ? (
                  <div className="text-center py-4 text-gray-500 text-sm">No events recorded</div>
                ) : (
                  <div className="space-y-2 max-h-[400px] overflow-y-auto">
                    {monitoringEvents.map((event) => (
                      <div key={event.id} className="border rounded-lg p-3 text-sm">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium text-gray-900">{event.event_type}</span>
                          {getSeverityBadge(event.severity)}
                        </div>
                        {event.event_data && (
                          <div className="text-xs text-gray-600 mt-1">
                            {JSON.stringify(event.event_data)}
                          </div>
                        )}
                        <div className="text-xs text-gray-400 mt-1">
                          {new Date(event.timestamp).toLocaleString()}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Exam Info */}
            <Card>
              <CardHeader>
                <CardTitle>Exam Configuration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Time Limit:</span>
                  <span className="font-medium">
                    {exam.time_limit_minutes ? `${exam.time_limit_minutes} min` : 'No limit'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Max Attempts:</span>
                  <span className="font-medium">{exam.max_attempts}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Passing Score:</span>
                  <span className="font-medium">
                    {exam.passing_score ? `${exam.passing_score}%` : 'Not set'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Shuffle Questions:</span>
                  <span className="font-medium">{exam.is_randomized ? 'Yes' : 'No'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Show Results:</span>
                  <span className="font-medium">
                    {exam.show_results_immediately ? 'Immediately' : 'After review'}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

export default function ExamSessionReviewPage() {
  return (
    <ProtectedRoute>
      <ExamSessionReviewContent />
    </ProtectedRoute>
  );
}
