'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Input,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
  Switch,
  LoadingSpinner,
} from '@/components/ui';
import { ArrowLeft, Save, Trash2, Plus } from 'lucide-react';
import Link from 'next/link';
import {
  useExam,
  useExamMutations,
  useExamQuestions,
  useQuestionMutations,
} from '@/hooks/useExams';
import { ExamType, ExamStatus, QuestionType } from '@/types/exam';
import type { ExamFormData, QuestionFormData } from '@/types/exam';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { toast } from 'sonner';

function EditExamContent() {
  const params = useParams();
  const router = useRouter();
  const examId = parseInt(params.id as string);

  const { exam, loading: examLoading } = useExam(examId);
  const {
    questions,
    loading: questionsLoading,
    refetch: refetchQuestions,
  } = useExamQuestions(examId);
  const { updateExam, loading: updating } = useExamMutations();
  const { updateQuestion, deleteQuestion, addQuestion } = useQuestionMutations();

  const [examData, setExamData] = useState<Partial<ExamFormData>>({
    title: '',
    description: '',
    exam_type: ExamType.CUSTOM,
    time_limit_minutes: null,
    max_attempts: 3,
    passing_score: null,
    is_randomized: false,
    allow_web_usage: false,
    monitor_web_usage: true,
    require_face_verification: false,
    face_check_interval_minutes: 5,
    show_results_immediately: true,
    show_correct_answers: false,
    show_score: true,
    instructions: '',
  });

  const [editingQuestionId, setEditingQuestionId] = useState<number | null>(null);
  const [showAddQuestion, setShowAddQuestion] = useState(false);

  useEffect(() => {
    if (exam) {
      setExamData({
        title: exam.title,
        description: exam.description || '',
        exam_type: exam.exam_type,
        time_limit_minutes: exam.time_limit_minutes,
        max_attempts: exam.max_attempts,
        passing_score: exam.passing_score,
        is_randomized: exam.is_randomized,
        allow_web_usage: exam.allow_web_usage,
        monitor_web_usage: exam.monitor_web_usage,
        require_face_verification: exam.require_face_verification,
        face_check_interval_minutes: exam.face_check_interval_minutes,
        show_results_immediately: exam.show_results_immediately,
        show_correct_answers: exam.show_correct_answers,
        show_score: exam.show_score,
        instructions: exam.instructions || '',
      });
    }
  }, [exam]);

  const handleSaveExam = async () => {
    try {
      await updateExam(examId, examData);
      router.push('/admin/exams');
    } catch (error) {
      // Error already handled by hook
    }
  };

  const handleDeleteQuestion = async (questionId: number) => {
    if (!confirm('Are you sure you want to delete this question?')) return;

    try {
      await deleteQuestion(questionId);
      refetchQuestions();
      toast.success('Question deleted');
    } catch (error) {
      // Error already handled by hook
    }
  };

  if (examLoading || questionsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner />
      </div>
    );
  }

  if (!exam) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Exam not found</h2>
        <Button asChild>
          <Link href="/admin/exams">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Exams
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <AppLayout>
      <div className="py-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <Button variant="ghost" asChild className="mb-2">
              <Link href="/admin/exams">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Exams
              </Link>
            </Button>
            <h1 className="text-3xl font-bold text-gray-900">Edit Exam</h1>
            <p className="text-gray-600">Update exam settings and questions</p>
          </div>
          <Button onClick={handleSaveExam} disabled={updating}>
            <Save className="h-4 w-4 mr-2" />
            {updating ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
                <CardDescription>Update exam title, description, and type</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="title">Exam Title *</Label>
                  <Input
                    id="title"
                    value={examData.title}
                    onChange={(e) => setExamData({ ...examData, title: e.target.value })}
                    placeholder="e.g., JavaScript Fundamentals Assessment"
                  />
                </div>

                <div>
                  <Label htmlFor="exam_type">Exam Type</Label>
                  <Select
                    value={examData.exam_type}
                    onValueChange={(value) => setExamData({ ...examData, exam_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={ExamType.APTITUDE}>Aptitude Test</SelectItem>
                      <SelectItem value={ExamType.SKILL}>Skill Test</SelectItem>
                      <SelectItem value={ExamType.KNOWLEDGE}>Knowledge Test</SelectItem>
                      <SelectItem value={ExamType.PERSONALITY}>Personality Test</SelectItem>
                      <SelectItem value={ExamType.CUSTOM}>Custom Test</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={examData.description}
                    onChange={(e) => setExamData({ ...examData, description: e.target.value })}
                    placeholder="Brief description of the exam"
                    rows={3}
                  />
                </div>

                <div>
                  <Label htmlFor="instructions">Instructions</Label>
                  <Textarea
                    id="instructions"
                    value={examData.instructions}
                    onChange={(e) => setExamData({ ...examData, instructions: e.target.value })}
                    placeholder="Instructions for candidates taking this exam"
                    rows={4}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Questions */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Questions ({questions.length})</CardTitle>
                    <CardDescription>Manage exam questions</CardDescription>
                  </div>
                  <Button onClick={() => setShowAddQuestion(true)} size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Question
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {questions.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No questions added yet. Click "Add Question" to get started.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {questions.map((question, index) => (
                      <div
                        key={question.id}
                        className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="font-semibold text-gray-700">Q{index + 1}.</span>
                              <span className="text-sm text-gray-500">
                                {question.question_type} • {question.points} pts
                              </span>
                            </div>
                            <p className="text-gray-900">{question.question_text}</p>
                            {question.options && (
                              <div className="mt-2 space-y-1">
                                {Object.entries(question.options).map(([key, value]) => (
                                  <div key={key} className="text-sm text-gray-600 ml-4">
                                    {key}. {value}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteQuestion(question.id)}
                            >
                              <Trash2 className="h-4 w-4 text-red-600" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            {/* Settings */}
            <Card>
              <CardHeader>
                <CardTitle>Exam Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="time_limit">Time Limit (minutes)</Label>
                  <Input
                    id="time_limit"
                    type="number"
                    value={examData.time_limit_minutes || ''}
                    onChange={(e) =>
                      setExamData({
                        ...examData,
                        time_limit_minutes: e.target.value ? parseInt(e.target.value) : null,
                      })
                    }
                    placeholder="No limit"
                  />
                </div>

                <div>
                  <Label htmlFor="max_attempts">Maximum Attempts</Label>
                  <Input
                    id="max_attempts"
                    type="number"
                    value={examData.max_attempts}
                    onChange={(e) =>
                      setExamData({ ...examData, max_attempts: parseInt(e.target.value) })
                    }
                    min={1}
                  />
                </div>

                <div>
                  <Label htmlFor="passing_score">Passing Score (%)</Label>
                  <Input
                    id="passing_score"
                    type="number"
                    value={examData.passing_score || ''}
                    onChange={(e) =>
                      setExamData({
                        ...examData,
                        passing_score: e.target.value ? parseInt(e.target.value) : null,
                      })
                    }
                    placeholder="No passing score"
                    min={0}
                    max={100}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="is_randomized">Randomize Questions</Label>
                  <Switch
                    id="is_randomized"
                    checked={examData.is_randomized}
                    onCheckedChange={(checked) =>
                      setExamData({ ...examData, is_randomized: checked })
                    }
                  />
                </div>
              </CardContent>
            </Card>

            {/* Monitoring */}
            <Card>
              <CardHeader>
                <CardTitle>Monitoring & Security</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="allow_web_usage">Allow Web Usage</Label>
                  <Switch
                    id="allow_web_usage"
                    checked={examData.allow_web_usage}
                    onCheckedChange={(checked) =>
                      setExamData({ ...examData, allow_web_usage: checked })
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="monitor_web_usage">Monitor Web Usage</Label>
                  <Switch
                    id="monitor_web_usage"
                    checked={examData.monitor_web_usage}
                    onCheckedChange={(checked) =>
                      setExamData({ ...examData, monitor_web_usage: checked })
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="require_face_verification">Face Verification</Label>
                  <Switch
                    id="require_face_verification"
                    checked={examData.require_face_verification}
                    onCheckedChange={(checked) =>
                      setExamData({ ...examData, require_face_verification: checked })
                    }
                  />
                </div>

                {examData.require_face_verification && (
                  <div>
                    <Label htmlFor="face_check_interval">Face Check Interval (minutes)</Label>
                    <Input
                      id="face_check_interval"
                      type="number"
                      value={examData.face_check_interval_minutes}
                      onChange={(e) =>
                        setExamData({
                          ...examData,
                          face_check_interval_minutes: parseInt(e.target.value),
                        })
                      }
                      min={1}
                    />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Results Display */}
            <Card>
              <CardHeader>
                <CardTitle>Results Display</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="show_results_immediately">Show Results Immediately</Label>
                  <Switch
                    id="show_results_immediately"
                    checked={examData.show_results_immediately}
                    onCheckedChange={(checked) =>
                      setExamData({ ...examData, show_results_immediately: checked })
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="show_correct_answers">Show Correct Answers</Label>
                  <Switch
                    id="show_correct_answers"
                    checked={examData.show_correct_answers}
                    onCheckedChange={(checked) =>
                      setExamData({ ...examData, show_correct_answers: checked })
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <Label htmlFor="show_score">Show Score</Label>
                  <Switch
                    id="show_score"
                    checked={examData.show_score}
                    onCheckedChange={(checked) => setExamData({ ...examData, show_score: checked })}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}

export default function EditExamPage() {
  return (
    <ProtectedRoute>
      <EditExamContent />
    </ProtectedRoute>
  );
}
