'use client';

import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui';
import { Button } from '@/components/ui';
import { Badge } from '@/components/ui';
import { Calendar, Clock, Users, BookOpen, Play, Eye } from 'lucide-react';
import { ExamAssignment } from '@/types/exam';
import { LoadingSpinner } from '@/components/ui';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useMyAssignments } from '@/hooks/useExams';

const ExamStatus = {
  NOT_STARTED: 'not_started',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  EXPIRED: 'expired',
  SUSPENDED: 'suspended',
} as const;

const ExamType = {
  APTITUDE: 'aptitude',
  SKILL: 'skill',
  KNOWLEDGE: 'knowledge',
  PERSONALITY: 'personality',
  CUSTOM: 'custom',
} as const;

function ExamsPageContent() {
  const { assignments, loading, error } = useMyAssignments();

  const getExamTypeLabel = (type: string) => {
    const labels = {
      [ExamType.APTITUDE]: '適性検査',
      [ExamType.SKILL]: 'Skill Test',
      [ExamType.KNOWLEDGE]: 'Knowledge Test',
      [ExamType.PERSONALITY]: 'Personality Test',
      [ExamType.CUSTOM]: 'Custom Test',
    };
    return labels[type as keyof typeof labels] || type;
  };

  const getStatusColor = (assignment: ExamAssignment) => {
    if (assignment.completed) {
      return assignment.latest_session?.passed
        ? 'bg-green-100 text-green-800'
        : 'bg-red-100 text-red-800';
    }
    if (assignment.latest_session?.status === ExamStatus.IN_PROGRESS) {
      return 'bg-yellow-100 text-yellow-800';
    }
    if (assignment.due_date && new Date(assignment.due_date) < new Date()) {
      return 'bg-red-100 text-red-800';
    }
    return 'bg-blue-100 text-blue-800';
  };

  const getStatusText = (assignment: ExamAssignment) => {
    if (assignment.completed) {
      return assignment.latest_session?.passed ? 'Passed' : 'Failed';
    }
    if (assignment.latest_session?.status === ExamStatus.IN_PROGRESS) {
      return 'In Progress';
    }
    if (assignment.due_date && new Date(assignment.due_date) < new Date()) {
      return 'Overdue';
    }
    return 'Pending';
  };

  const canStartExam = (assignment: ExamAssignment) => {
    return (
      assignment.is_active &&
      !assignment.completed &&
      assignment.latest_session?.status !== ExamStatus.IN_PROGRESS &&
      (!assignment.due_date || new Date(assignment.due_date) > new Date())
    );
  };

  const canResumeExam = (assignment: ExamAssignment) => {
    return assignment.latest_session?.status === ExamStatus.IN_PROGRESS;
  };

  const canViewResults = (assignment: ExamAssignment) => {
    return assignment.completed && assignment.latest_session?.status === ExamStatus.COMPLETED;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <AppLayout>
      <div className="py-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Exams</h1>
          <p className="text-gray-600">View and take your assigned exams</p>
        </div>

        {assignments.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <BookOpen className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No exams assigned</h3>
              <p className="text-gray-600">You don't have any exams assigned at the moment.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {assignments.map((assignment) => (
              <Card key={assignment.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg mb-2">{assignment.exam_title}</CardTitle>
                      <CardDescription className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">
                          {getExamTypeLabel(assignment.exam_type)}
                        </Badge>
                      </CardDescription>
                    </div>
                    <Badge className={getStatusColor(assignment)}>
                      {getStatusText(assignment)}
                    </Badge>
                  </div>
                </CardHeader>

                <CardContent className="space-y-4">
                  <div className="space-y-2 text-sm text-gray-600">
                    {assignment.due_date && (
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4" />
                        <span>Due: {new Date(assignment.due_date).toLocaleDateString()}</span>
                      </div>
                    )}

                    {assignment.custom_time_limit_minutes && (
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        <span>Time Limit: {assignment.custom_time_limit_minutes} minutes</span>
                      </div>
                    )}

                    {assignment.custom_max_attempts && (
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        <span>
                          Attempts: {assignment.sessions_count} / {assignment.custom_max_attempts}
                        </span>
                      </div>
                    )}
                  </div>

                  {assignment.latest_session && assignment.latest_session.percentage !== null && (
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-sm font-medium text-gray-700 mb-1">Latest Score</div>
                      <div className="text-2xl font-bold text-gray-900">
                        {assignment.latest_session.percentage.toFixed(1)}%
                      </div>
                    </div>
                  )}

                  <div className="flex gap-2 pt-2">
                    {canResumeExam(assignment) && (
                      <Button asChild className="flex-1">
                        <Link
                          href={`/exams/take/${assignment.exam_id}?assignment=${assignment.id}`}
                        >
                          <Play className="h-4 w-4 mr-2" />
                          Resume
                        </Link>
                      </Button>
                    )}

                    {canStartExam(assignment) && (
                      <Button asChild className="flex-1">
                        <Link
                          href={`/exams/take/${assignment.exam_id}?assignment=${assignment.id}`}
                        >
                          <Play className="h-4 w-4 mr-2" />
                          Start Exam
                        </Link>
                      </Button>
                    )}

                    {canViewResults(assignment) && (
                      <Button asChild variant="outline" className="flex-1">
                        <Link href={`/exams/results/${assignment.latest_session?.id}`}>
                          <Eye className="h-4 w-4 mr-2" />
                          View Results
                        </Link>
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}

export default function ExamsPage() {
  return (
    <ProtectedRoute>
      <ExamsPageContent />
    </ProtectedRoute>
  );
}
