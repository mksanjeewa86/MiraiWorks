'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Plus,
  Search,
  MoreVertical,
  Edit,
  Trash2,
  Users,
  BarChart3,
  Eye,
  Clock,
  BookOpen,
  Target,
} from 'lucide-react';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { toast } from 'sonner';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface Exam {
  id: number;
  title: string;
  description: string | null;
  exam_type: string;
  status: string;
  time_limit_minutes: number | null;
  max_attempts: number;
  passing_score: number | null;
  is_randomized: boolean;
  require_face_verification: boolean;
  monitor_web_usage: boolean;
  created_at: string;
  updated_at: string;
  total_questions: number | null;
  total_sessions: number | null;
  completed_sessions: number | null;
  average_score: number | null;
}

interface ExamListResponse {
  exams: Exam[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
}

const ExamStatus = {
  DRAFT: 'draft',
  ACTIVE: 'active',
  ARCHIVED: 'archived',
} as const;

const ExamType = {
  APTITUDE: 'aptitude',
  SKILL: 'skill',
  KNOWLEDGE: 'knowledge',
  PERSONALITY: 'personality',
  CUSTOM: 'custom',
} as const;

export default function AdminExamsPage() {
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);

  useEffect(() => {
    fetchExams();
  }, [page, statusFilter, typeFilter]);

  useEffect(() => {
    // Reset page when filters change
    if (page !== 1) {
      setPage(1);
    } else {
      fetchExams();
    }
  }, [searchQuery]);

  const fetchExams = async () => {
    try {
      const params = new URLSearchParams({
        skip: ((page - 1) * 20).toString(),
        limit: '20',
      });

      if (statusFilter !== 'all') {
        params.append('status', statusFilter);
      }

      const response = await fetch(`/api/exam/exams?${params}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch exams');
      }

      const data: ExamListResponse = await response.json();

      // Filter by search query and type on frontend for simplicity
      let filteredExams = data.exams;

      if (searchQuery) {
        filteredExams = filteredExams.filter(
          (exam) =>
            exam.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
            (exam.description && exam.description.toLowerCase().includes(searchQuery.toLowerCase()))
        );
      }

      if (typeFilter !== 'all') {
        filteredExams = filteredExams.filter((exam) => exam.exam_type === typeFilter);
      }

      setExams(page === 1 ? filteredExams : [...exams, ...filteredExams]);
      setHasMore(data.has_more);
    } catch (error) {
      console.error('Error fetching exams:', error);
      toast.error('Failed to load exams');
    } finally {
      setLoading(false);
    }
  };

  const deleteExam = async (examId: number) => {
    if (!confirm('Are you sure you want to delete this exam? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch(`/api/exam/exams/${examId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete exam');
      }

      setExams(exams.filter((exam) => exam.id !== examId));
      toast.success('Exam deleted successfully');
    } catch (error) {
      console.error('Error deleting exam:', error);
      toast.error('Failed to delete exam');
    }
  };

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

  const getStatusColor = (status: string) => {
    switch (status) {
      case ExamStatus.ACTIVE:
        return 'bg-green-100 text-green-800 border-green-200';
      case ExamStatus.DRAFT:
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case ExamStatus.ARCHIVED:
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getCompletionRate = (exam: Exam) => {
    if (!exam.total_sessions || exam.total_sessions === 0) return 0;
    return Math.round(((exam.completed_sessions || 0) / exam.total_sessions) * 100);
  };

  if (loading && page === 1) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 px-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Exam Management</h1>
          <p className="text-gray-600">Create and manage recruitment exams</p>
        </div>
        <Button asChild>
          <Link href="/admin/exams/create">
            <Plus className="h-4 w-4 mr-2" />
            Create Exam
          </Link>
        </Button>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search exams..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value={ExamStatus.ACTIVE}>Active</SelectItem>
                <SelectItem value={ExamStatus.DRAFT}>Draft</SelectItem>
                <SelectItem value={ExamStatus.ARCHIVED}>Archived</SelectItem>
              </SelectContent>
            </Select>

            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value={ExamType.APTITUDE}>適性検査</SelectItem>
                <SelectItem value={ExamType.SKILL}>Skill Test</SelectItem>
                <SelectItem value={ExamType.KNOWLEDGE}>Knowledge Test</SelectItem>
                <SelectItem value={ExamType.PERSONALITY}>Personality Test</SelectItem>
                <SelectItem value={ExamType.CUSTOM}>Custom Test</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Exams Grid */}
      {exams.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <BookOpen className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No exams found</h3>
            <p className="text-gray-600 mb-4">
              {searchQuery || statusFilter !== 'all' || typeFilter !== 'all'
                ? 'No exams match your current filters.'
                : 'Get started by creating your first exam.'}
            </p>
            {!searchQuery && statusFilter === 'all' && typeFilter === 'all' && (
              <Button asChild>
                <Link href="/admin/exams/create">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Your First Exam
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {exams.map((exam) => (
            <Card key={exam.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg mb-2 line-clamp-2">{exam.title}</CardTitle>
                    <CardDescription className="line-clamp-2">
                      {exam.description || 'No description provided'}
                    </CardDescription>
                  </div>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem asChild>
                        <Link href={`/admin/exams/${exam.id}`}>
                          <Eye className="h-4 w-4 mr-2" />
                          View Details
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link href={`/admin/exams/${exam.id}/edit`}>
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem asChild>
                        <Link href={`/admin/exams/${exam.id}/statistics`}>
                          <BarChart3 className="h-4 w-4 mr-2" />
                          Statistics
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={() => deleteExam(exam.id)}
                        className="text-red-600"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>

                <div className="flex items-center gap-2 mt-2">
                  <Badge className={getStatusColor(exam.status)}>
                    {exam.status.charAt(0).toUpperCase() + exam.status.slice(1)}
                  </Badge>
                  <Badge variant="outline">{getExamTypeLabel(exam.exam_type)}</Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Exam Stats */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4 text-gray-400" />
                    <span>{exam.total_questions || 0} questions</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-gray-400" />
                    <span>{exam.total_sessions || 0} attempts</span>
                  </div>

                  {exam.time_limit_minutes && (
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <span>{exam.time_limit_minutes}m limit</span>
                    </div>
                  )}

                  <div className="flex items-center gap-2">
                    <Target className="h-4 w-4 text-gray-400" />
                    <span>{exam.max_attempts} max attempts</span>
                  </div>
                </div>

                {/* Performance Metrics */}
                {exam.total_sessions && exam.total_sessions > 0 && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Completion Rate</span>
                      <span className="font-medium">{getCompletionRate(exam)}%</span>
                    </div>
                    {exam.average_score !== null && (
                      <div className="flex justify-between text-sm">
                        <span>Average Score</span>
                        <span className="font-medium">{exam.average_score.toFixed(1)}%</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Security Features */}
                <div className="flex flex-wrap gap-1">
                  {exam.require_face_verification && (
                    <Badge variant="secondary" className="text-xs">
                      Face Verification
                    </Badge>
                  )}
                  {exam.monitor_web_usage && (
                    <Badge variant="secondary" className="text-xs">
                      Web Monitoring
                    </Badge>
                  )}
                  {exam.is_randomized && (
                    <Badge variant="secondary" className="text-xs">
                      Randomized
                    </Badge>
                  )}
                  {exam.passing_score && (
                    <Badge variant="secondary" className="text-xs">
                      Pass: {exam.passing_score}%
                    </Badge>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 pt-2">
                  <Button asChild variant="outline" size="sm" className="flex-1">
                    <Link href={`/admin/exams/${exam.id}`}>
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Link>
                  </Button>

                  <Button asChild variant="outline" size="sm" className="flex-1">
                    <Link href={`/admin/exams/${exam.id}/statistics`}>
                      <BarChart3 className="h-4 w-4 mr-1" />
                      Stats
                    </Link>
                  </Button>

                  <Button asChild size="sm" className="flex-1">
                    <Link href={`/admin/exams/${exam.id}/edit`}>
                      <Edit className="h-4 w-4 mr-1" />
                      Edit
                    </Link>
                  </Button>
                </div>

                {/* Last Updated */}
                <div className="text-xs text-gray-500 pt-2 border-t">
                  Updated {new Date(exam.updated_at).toLocaleDateString()}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Load More */}
      {hasMore && (
        <div className="flex justify-center mt-8">
          <Button variant="outline" onClick={() => setPage(page + 1)} disabled={loading}>
            {loading ? <LoadingSpinner size="sm" className="mr-2" /> : null}
            Load More
          </Button>
        </div>
      )}
    </div>
  );
}
