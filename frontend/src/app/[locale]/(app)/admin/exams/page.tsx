'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ROUTES } from '@/routes/config';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  Input,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui';
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
  Copy,
  Send,
  FileDown,
  FileSpreadsheet,
} from 'lucide-react';
import { LoadingSpinner } from '@/components/ui';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui';
import { Exam, ExamStatus, ExamType } from '@/types/exam';
import { useExams, useExamMutations } from '@/hooks/useExams';
import { examApi } from '@/api/exam';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { ExamTypeBadge } from '@/components/exam/ExamTypeBadge';
import { CloneExamDialog } from '@/components/exam/CloneExamDialog';
import { toast } from 'sonner';

function AdminExamsPageContent() {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [ownershipFilter, setOwnershipFilter] = useState<string>('all');
  const [cloneExam, setCloneExam] = useState<Exam | null>(null);

  const { exams, loading, refetch } = useExams({
    status: statusFilter !== 'all' ? statusFilter : undefined,
  });
  const { deleteExam, duplicateExam } = useExamMutations();

  const handleDeleteExam = async (examId: number) => {
    if (!confirm('Are you sure you want to delete this exam? This action cannot be undone.')) {
      return;
    }

    try {
      await deleteExam(examId);
      refetch();
    } catch (error) {
      // Error already handled by hook
    }
  };

  const handleDuplicateExam = async (examId: number, title: string) => {
    const newTitle = prompt('Enter title for duplicated exam:', `${title} (Copy)`);
    if (!newTitle) return;

    try {
      await duplicateExam(examId, newTitle);
      refetch();
    } catch (error) {
      // Error already handled by hook
    }
  };

  const handleExportPDF = async (examId: number) => {
    try {
      toast.loading('Generating PDF report...');
      const blob = await examApi.exportResultsPDF(examId);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `exam_${examId}_results.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.dismiss();
      toast.success('PDF report downloaded successfully');
    } catch (error) {
      toast.dismiss();
      toast.error('Failed to generate PDF report');
    }
  };

  const handleExportExcel = async (examId: number) => {
    try {
      toast.loading('Generating Excel report...');
      const blob = await examApi.exportResultsExcel(examId);

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `exam_${examId}_results.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.dismiss();
      toast.success('Excel report downloaded successfully');
    } catch (error) {
      toast.dismiss();
      toast.error('Failed to generate Excel report');
    }
  };

  // Client-side filtering
  const filteredExams = exams.filter((exam) => {
    const matchesSearch =
      !searchQuery ||
      exam.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (exam.description && exam.description.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesType = typeFilter === 'all' || exam.exam_type === typeFilter;

    const matchesOwnership =
      ownershipFilter === 'all' ||
      (ownershipFilter === 'own' && exam.company_id === user?.company_id) ||
      (ownershipFilter === 'global' && exam.company_id === null && exam.is_public) ||
      (ownershipFilter === 'public' && exam.is_public && exam.company_id !== user?.company_id);

    return matchesSearch && matchesType && matchesOwnership;
  });

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
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Exam Management</h1>
            <p className="text-gray-600">Create and manage recruitment exams</p>
          </div>
          <Button asChild>
            <Link href={ROUTES.ADMIN.EXAMS.CREATE}>
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

              <Select value={ownershipFilter} onValueChange={setOwnershipFilter}>
                <SelectTrigger className="w-full sm:w-48">
                  <SelectValue placeholder="Filter by ownership" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Exams</SelectItem>
                  <SelectItem value="own">My Company</SelectItem>
                  <SelectItem value="global">🌍 Global</SelectItem>
                  <SelectItem value="public">🔓 Public</SelectItem>
                </SelectContent>
              </Select>

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
        {filteredExams.length === 0 ? (
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
                  <Link href={ROUTES.ADMIN.EXAMS.CREATE}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Your First Exam
                  </Link>
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredExams.map((exam) => (
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
                          <Link href={ROUTES.ADMIN.EXAMS.PREVIEW(exam.id)}>
                            <Eye className="h-4 w-4 mr-2" />
                            Preview
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem asChild>
                          <Link href={ROUTES.ADMIN.EXAMS.EDIT(exam.id)}>
                            <Edit className="h-4 w-4 mr-2" />
                            Edit
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem asChild>
                          <Link href={ROUTES.ADMIN.EXAMS.ASSIGN(exam.id)}>
                            <Send className="h-4 w-4 mr-2" />
                            Assign to Candidates
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem asChild>
                          <Link href={ROUTES.ADMIN.EXAMS.ANALYTICS(exam.id)}>
                            <BarChart3 className="h-4 w-4 mr-2" />
                            Analytics
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleExportPDF(exam.id)}>
                          <FileDown className="h-4 w-4 mr-2" />
                          Export PDF
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleExportExcel(exam.id)}>
                          <FileSpreadsheet className="h-4 w-4 mr-2" />
                          Export Excel
                        </DropdownMenuItem>
                        {exam.is_public && exam.company_id !== user?.company_id && (
                          <DropdownMenuItem onClick={() => setCloneExam(exam)}>
                            <Copy className="h-4 w-4 mr-2" />
                            Clone to My Company
                          </DropdownMenuItem>
                        )}
                        {exam.company_id === user?.company_id && (
                          <DropdownMenuItem onClick={() => handleDuplicateExam(exam.id, exam.title)}>
                            <Copy className="h-4 w-4 mr-2" />
                            Duplicate
                          </DropdownMenuItem>
                        )}
                        {exam.company_id === user?.company_id && (
                          <DropdownMenuItem
                            onClick={() => handleDeleteExam(exam.id)}
                            className="text-red-600"
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        )}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>

                  <div className="flex items-center gap-2 mt-2 flex-wrap">
                    <ExamTypeBadge exam={exam} currentCompanyId={user?.company_id} />
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
                          <span className="font-medium">
                            {exam.average_score?.toFixed(1) ?? 'N/A'}%
                          </span>
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
                      <Link href={ROUTES.ADMIN.EXAMS.PREVIEW(exam.id)}>
                        <Eye className="h-4 w-4 mr-1" />
                        Preview
                      </Link>
                    </Button>

                    <Button asChild size="sm" className="flex-1">
                      <Link href={ROUTES.ADMIN.EXAMS.ASSIGN(exam.id)}>
                        <Send className="h-4 w-4 mr-1" />
                        Assign
                      </Link>
                    </Button>

                    <Button asChild variant="outline" size="sm" className="flex-1">
                      <Link href={ROUTES.ADMIN.EXAMS.EDIT(exam.id)}>
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
      </div>

      {/* Clone Dialog */}
      {cloneExam && (
        <CloneExamDialog
          exam={cloneExam}
          isOpen={!!cloneExam}
          onClose={() => setCloneExam(null)}
          onSuccess={() => {
            setCloneExam(null);
            refetch();
            toast.success('Exam cloned successfully');
          }}
        />
      )}
    </AppLayout>
  );
}

export default function AdminExamsPage() {
  return (
    <ProtectedRoute>
      <AdminExamsPageContent />
    </ProtectedRoute>
  );
}
