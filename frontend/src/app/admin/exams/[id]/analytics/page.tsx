'use client';

import { useState, useEffect, useMemo } from 'react';
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
  TrendingUp,
  Users,
  Clock,
  Award,
  BarChart3,
  PieChart,
  Target,
} from 'lucide-react';
import Link from 'next/link';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { examApi } from '@/api/exam';
import type { ExamStatistics, ExamInfo } from '@/types/exam';
import { toast } from 'sonner';

function ExamAnalyticsContent() {
  const params = useParams();
  const router = useRouter();
  const examId = parseInt(params.id as string);

  const [exam, setExam] = useState<ExamInfo | null>(null);
  const [statistics, setStatistics] = useState<ExamStatistics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, [examId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [examResponse, statsResponse] = await Promise.all([
        examApi.getExam(examId),
        examApi.getExamStatistics(examId),
      ]);

      if (examResponse.data) setExam(examResponse.data);
      if (statsResponse.data) setStatistics(statsResponse.data);
    } catch (error) {
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const metrics = useMemo(() => {
    if (!statistics) return [];

    return [
      {
        label: 'Total Assigned',
        value: statistics.total_assigned,
        icon: <Users className="h-6 w-6 text-indigo-500" />,
        color: 'bg-indigo-100',
      },
      {
        label: 'Total Started',
        value: statistics.total_started,
        icon: <Clock className="h-6 w-6 text-blue-500" />,
        color: 'bg-blue-100',
      },
      {
        label: 'Completion Rate',
        value: `${statistics.completion_rate.toFixed(1)}%`,
        icon: <Target className="h-6 w-6 text-green-500" />,
        color: 'bg-green-100',
      },
      {
        label: 'Average Score',
        value: statistics.average_score ? `${statistics.average_score.toFixed(1)}%` : 'N/A',
        icon: <Award className="h-6 w-6 text-amber-500" />,
        color: 'bg-amber-100',
      },
    ];
  }, [statistics]);

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <LoadingSpinner />
        </div>
      </AppLayout>
    );
  }

  if (!exam || !statistics) {
    return (
      <AppLayout>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Exam not found</h2>
          <Button asChild>
            <Link href="/admin/exams">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Exams
            </Link>
          </Button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="py-6">
        {/* Header */}
        <div className="mb-6">
          <Button variant="ghost" asChild className="mb-2">
            <Link href="/admin/exams">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Exams
            </Link>
          </Button>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Exam Analytics</h1>
              <p className="text-gray-600">{exam.title}</p>
            </div>
            <Badge variant={exam.status === 'published' ? 'success' : 'secondary'}>
              {exam.status}
            </Badge>
          </div>
        </div>

        {/* Metrics Grid */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-6">
          {metrics.map((metric) => (
            <Card key={metric.label}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{metric.label}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-2">{metric.value}</p>
                  </div>
                  <div className={`p-3 rounded-full ${metric.color}`}>{metric.icon}</div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Performance Overview */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Overview</CardTitle>
              <CardDescription>Detailed performance metrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-600">Average Time</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {statistics.average_time_minutes
                      ? `${statistics.average_time_minutes.toFixed(1)} min`
                      : 'N/A'}
                  </div>
                </div>
                <Clock className="h-8 w-8 text-gray-400" />
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-600">Pass Rate</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {statistics.pass_rate !== null ? `${statistics.pass_rate.toFixed(1)}%` : 'N/A'}
                  </div>
                </div>
                <TrendingUp className="h-8 w-8 text-gray-400" />
              </div>

              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-600">Completion Rate</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {statistics.completion_rate.toFixed(1)}%
                  </div>
                </div>
                <Target className="h-8 w-8 text-gray-400" />
              </div>

              {exam.passing_score && (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <div className="text-sm text-gray-600">Passing Score Threshold</div>
                    <div className="text-lg font-semibold text-gray-900">{exam.passing_score}%</div>
                  </div>
                  <Award className="h-8 w-8 text-gray-400" />
                </div>
              )}
            </CardContent>
          </Card>

          {/* Question Statistics */}
          <Card>
            <CardHeader>
              <CardTitle>Question Performance</CardTitle>
              <CardDescription>Performance by question</CardDescription>
            </CardHeader>
            <CardContent>
              {statistics.question_statistics.length === 0 ? (
                <div className="text-center py-8 text-gray-500">No question data available</div>
              ) : (
                <div className="space-y-3 max-h-[400px] overflow-y-auto">
                  {statistics.question_statistics.map((qStat, index) => (
                    <div
                      key={index}
                      className="border rounded-lg p-3 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-gray-900">
                          Question {qStat.question_number || index + 1}
                        </span>
                        <Badge variant="outline">{qStat.question_type}</Badge>
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-500">Correct Rate:</span>
                          <span className="ml-2 font-medium">
                            {qStat.correct_percentage?.toFixed(1)}%
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-500">Avg Time:</span>
                          <span className="ml-2 font-medium">
                            {qStat.average_time_seconds
                              ? `${(qStat.average_time_seconds / 60).toFixed(1)} min`
                              : 'N/A'}
                          </span>
                        </div>
                      </div>

                      {/* Difficulty indicator */}
                      <div className="mt-2">
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-500">Difficulty:</span>
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full ${
                                (qStat.correct_percentage || 0) > 70
                                  ? 'bg-green-500'
                                  : (qStat.correct_percentage || 0) > 40
                                    ? 'bg-yellow-500'
                                    : 'bg-red-500'
                              }`}
                              style={{ width: `${100 - (qStat.correct_percentage || 0)}%` }}
                            />
                          </div>
                          <span className="text-xs font-medium">
                            {(qStat.correct_percentage || 0) > 70
                              ? 'Easy'
                              : (qStat.correct_percentage || 0) > 40
                                ? 'Medium'
                                : 'Hard'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Exam Configuration */}
          <Card>
            <CardHeader>
              <CardTitle>Exam Configuration</CardTitle>
              <CardDescription>Current exam settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Exam Type:</span>
                <span className="font-medium">{exam.exam_type}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Total Questions:</span>
                <span className="font-medium">{exam.total_questions}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Time Limit:</span>
                <span className="font-medium">
                  {exam.time_limit_minutes ? `${exam.time_limit_minutes} minutes` : 'No limit'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Max Attempts:</span>
                <span className="font-medium">{exam.max_attempts}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Shuffle Questions:</span>
                <span className="font-medium">{exam.is_randomized ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Show Results:</span>
                <span className="font-medium">
                  {exam.show_results_immediately ? 'Immediately' : 'After review'}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Insights */}
          <Card>
            <CardHeader>
              <CardTitle>Insights</CardTitle>
              <CardDescription>Performance insights and recommendations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {statistics.completion_rate < 50 && (
                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-start gap-2">
                    <TrendingUp className="h-5 w-5 text-yellow-600 mt-0.5" />
                    <div>
                      <div className="font-medium text-yellow-900">Low Completion Rate</div>
                      <div className="text-sm text-yellow-700 mt-1">
                        Only {statistics.completion_rate.toFixed(1)}% of started exams are
                        completed. Consider reviewing exam difficulty or time limit.
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {statistics.average_score && statistics.average_score < 60 && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-start gap-2">
                    <Award className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                      <div className="font-medium text-red-900">Low Average Score</div>
                      <div className="text-sm text-red-700 mt-1">
                        Average score is {statistics.average_score.toFixed(1)}%. The exam might be
                        too difficult or require additional study materials.
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {statistics.completion_rate >= 80 &&
                statistics.average_score &&
                statistics.average_score >= 75 && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-start gap-2">
                      <Target className="h-5 w-5 text-green-600 mt-0.5" />
                      <div>
                        <div className="font-medium text-green-900">Excellent Performance</div>
                        <div className="text-sm text-green-700 mt-1">
                          High completion rate ({statistics.completion_rate.toFixed(1)}%) and strong
                          average score ({statistics.average_score.toFixed(1)}%). Exam is
                          well-balanced.
                        </div>
                      </div>
                    </div>
                  </div>
                )}
            </CardContent>
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}

export default function ExamAnalyticsPage() {
  return (
    <ProtectedRoute>
      <ExamAnalyticsContent />
    </ProtectedRoute>
  );
}
