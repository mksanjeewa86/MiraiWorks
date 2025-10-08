'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  Progress,
} from '@/components/ui';
import {
  ArrowLeft,
  Users,
  TrendingUp,
  Clock,
  Target,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Download,
  Eye,
} from 'lucide-react';
import { ExamStatistics, SessionSummary, ExamInfo } from '@/types/exam';
import { LoadingSpinner } from '@/components/ui';
import { toast } from 'sonner';
import { apiClient } from '@/api/apiClient';
import { API_ENDPOINTS, buildApiUrl } from '@/api/config';

export default function ExamStatisticsPage() {
  const params = useParams();
  const router = useRouter();
  const examId = params.id as string;

  const [examInfo, setExamInfo] = useState<ExamInfo | null>(null);
  const [statistics, setStatistics] = useState<ExamStatistics | null>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchExamData();
    fetchStatistics();
    fetchSessions();
  }, [examId]);

  const fetchExamData = async () => {
    try {
      const response = await apiClient.get<ExamInfo>(API_ENDPOINTS.EXAMS.BY_ID(examId));
      setExamInfo(response.data);
    } catch (error) {
      console.error('Error fetching exam:', error);
      toast.error('Failed to load exam details');
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await apiClient.get<ExamStatistics>(API_ENDPOINTS.EXAMS.STATISTICS(examId));
      setStatistics(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
      toast.error('Failed to load statistics');
    }
  };

  const fetchSessions = async () => {
    try {
      const response = await apiClient.get<{ sessions: SessionSummary[] }>(
        API_ENDPOINTS.EXAMS.SESSIONS(examId)
      );
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Error fetching sessions:', error);
      toast.error('Failed to load session data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'in_progress':
        return 'text-blue-600';
      case 'expired':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getPassedColor = (passed: boolean | null) => {
    if (passed === null) return 'text-gray-600';
    return passed ? 'text-green-600' : 'text-red-600';
  };

  const formatDuration = (minutes: number | null) => {
    if (!minutes) return 'N/A';
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const exportResults = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch(buildApiUrl(API_ENDPOINTS.EXAMS.EXPORT_EXCEL(examId)), {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to export results');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `exam-${examId}-results.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success('Results exported successfully');
    } catch (error) {
      console.error('Error exporting results:', error);
      toast.error('Failed to export results');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (!examInfo || !statistics) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 mx-auto text-red-500 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Data not available</h2>
          <p className="text-gray-600 mb-4">Unable to load exam statistics.</p>
          <Button asChild>
            <Link href="/admin/exams">Back to Exams</Link>
          </Button>
        </div>
      </div>
    );
  }

  const passedCount = sessions.filter((s) => s.passed === true).length;
  const failedCount = sessions.filter((s) => s.passed === false).length;
  const securityIssuesCount = sessions.filter(
    (s) => s.web_usage_detected || s.face_verification_failed
  ).length;

  return (
    <div className="container mx-auto py-6 px-4 max-w-7xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button variant="outline" asChild>
          <Link href="/admin/exams">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Exams
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{examInfo.title}</h1>
          <p className="text-gray-600">Exam Statistics & Analytics</p>
        </div>
        <div className="ml-auto">
          <Button onClick={exportResults} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Results
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Total Assigned</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="text-2xl font-bold text-gray-900">{statistics.total_assigned}</div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Completion Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {statistics.completion_rate.toFixed(1)}%
                </div>
                <div className="text-sm text-gray-500">
                  {statistics.total_completed} / {statistics.total_started}
                </div>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Average Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {statistics.average_score ? `${statistics.average_score.toFixed(1)}%` : 'N/A'}
                </div>
              </div>
              <Target className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">Average Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">
                  {formatDuration(statistics.average_time_minutes)}
                </div>
                {examInfo.time_limit_minutes && (
                  <div className="text-sm text-gray-500">Limit: {examInfo.time_limit_minutes}m</div>
                )}
              </div>
              <Clock className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pass/Fail Distribution */}
      {examInfo.passing_score && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Pass/Fail Distribution</CardTitle>
            <CardDescription>Based on passing score of {examInfo.passing_score}%</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-3">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">{passedCount}</div>
                <div className="text-sm text-gray-600 mb-2">Passed</div>
                <Progress
                  value={
                    statistics.total_completed > 0
                      ? (passedCount / statistics.total_completed) * 100
                      : 0
                  }
                  className="h-2"
                />
              </div>

              <div className="text-center">
                <div className="text-3xl font-bold text-red-600 mb-2">{failedCount}</div>
                <div className="text-sm text-gray-600 mb-2">Failed</div>
                <Progress
                  value={
                    statistics.total_completed > 0
                      ? (failedCount / statistics.total_completed) * 100
                      : 0
                  }
                  className="h-2"
                />
              </div>

              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600 mb-2">
                  {statistics.total_completed - passedCount - failedCount}
                </div>
                <div className="text-sm text-gray-600 mb-2">Pending Review</div>
                <Progress
                  value={
                    statistics.total_completed > 0
                      ? ((statistics.total_completed - passedCount - failedCount) /
                          statistics.total_completed) *
                        100
                      : 0
                  }
                  className="h-2"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Security Monitoring */}
      {(examInfo.monitor_web_usage || examInfo.require_face_verification) && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Security Monitoring
            </CardTitle>
            <CardDescription>Sessions with detected security issues</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-orange-600">{securityIssuesCount}</div>
                <div className="text-sm text-gray-600">
                  Sessions with issues (
                  {statistics.total_completed > 0
                    ? Math.round((securityIssuesCount / statistics.total_completed) * 100)
                    : 0}
                  %)
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">
                  Web Usage: {sessions.filter((s) => s.web_usage_detected).length} sessions
                </div>
                <div className="text-sm text-gray-600">
                  Face Verification: {sessions.filter((s) => s.face_verification_failed).length}{' '}
                  sessions
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Session Results */}
      <Card>
        <CardHeader>
          <CardTitle>Individual Results</CardTitle>
          <CardDescription>Detailed results for each exam session</CardDescription>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <div className="text-center py-8">
              <Users className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No sessions yet</h3>
              <p className="text-gray-600">
                Sessions will appear here once candidates start taking the exam.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-2">Candidate</th>
                    <th className="text-left py-3 px-2">Attempt</th>
                    <th className="text-left py-3 px-2">Status</th>
                    <th className="text-left py-3 px-2">Score</th>
                    <th className="text-left py-3 px-2">Result</th>
                    <th className="text-left py-3 px-2">Duration</th>
                    <th className="text-left py-3 px-2">Started</th>
                    <th className="text-left py-3 px-2">Issues</th>
                    <th className="text-left py-3 px-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {sessions.map((session) => (
                    <tr key={session.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-2">
                        <div>
                          <div className="font-medium text-gray-900">{session.candidate_name}</div>
                          <div className="text-sm text-gray-500">{session.candidate_email}</div>
                        </div>
                      </td>
                      <td className="py-3 px-2">
                        <Badge variant="outline">#{session.attempt_number}</Badge>
                      </td>
                      <td className="py-3 px-2">
                        <span className={`font-medium ${getStatusColor(session.status)}`}>
                          {session.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-3 px-2">
                        {session.percentage !== null ? (
                          <span className="font-medium">{session.percentage.toFixed(1)}%</span>
                        ) : (
                          <span className="text-gray-500">-</span>
                        )}
                      </td>
                      <td className="py-3 px-2">
                        {session.passed !== null ? (
                          <div className="flex items-center gap-1">
                            {session.passed ? (
                              <CheckCircle className="h-4 w-4 text-green-600" />
                            ) : (
                              <XCircle className="h-4 w-4 text-red-600" />
                            )}
                            <span className={getPassedColor(session.passed)}>
                              {session.passed ? 'Passed' : 'Failed'}
                            </span>
                          </div>
                        ) : (
                          <span className="text-gray-500">Pending</span>
                        )}
                      </td>
                      <td className="py-3 px-2">{formatDuration(session.time_spent_minutes)}</td>
                      <td className="py-3 px-2">
                        {session.started_at ? (
                          <div className="text-sm">
                            {new Date(session.started_at).toLocaleDateString()}
                          </div>
                        ) : (
                          <span className="text-gray-500">Not started</span>
                        )}
                      </td>
                      <td className="py-3 px-2">
                        <div className="flex gap-1">
                          {session.web_usage_detected && (
                            <Badge
                              variant="secondary"
                              className="text-xs bg-orange-100 text-orange-800"
                            >
                              Web
                            </Badge>
                          )}
                          {session.face_verification_failed && (
                            <Badge variant="secondary" className="text-xs bg-red-100 text-red-800">
                              Face
                            </Badge>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-2">
                        <Button size="sm" variant="outline" asChild>
                          <Link href={`/exams/results/${session.id}`}>
                            <Eye className="h-4 w-4" />
                          </Link>
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
