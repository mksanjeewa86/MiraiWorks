'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { ArrowLeft, Plus, Trash2, Save } from 'lucide-react';
import { LoadingSpinner } from '@/components/ui/loading-spinner';
import { toast } from 'sonner';
import { ExamQuestionForm } from './exam-question-form';

interface ExamFormData {
  title: string;
  description: string;
  exam_type: string;
  time_limit_minutes: number | null;
  max_attempts: number;
  passing_score: number | null;
  is_randomized: boolean;
  allow_web_usage: boolean;
  monitor_web_usage: boolean;
  require_face_verification: boolean;
  face_check_interval_minutes: number;
  show_results_immediately: boolean;
  show_correct_answers: boolean;
  show_score: boolean;
  instructions: string;
}

interface QuestionFormData {
  question_text: string;
  question_type: string;
  points: number;
  time_limit_seconds: number | null;
  is_required: boolean;
  options: Record<string, string>;
  correct_answers: string[];
  max_length: number | null;
  min_length: number | null;
  rating_scale: number | null;
  explanation: string;
  tags: string[];
}

const ExamType = {
  APTITUDE: 'aptitude',
  SKILL: 'skill',
  KNOWLEDGE: 'knowledge',
  PERSONALITY: 'personality',
  CUSTOM: 'custom',
} as const;

const QuestionType = {
  MULTIPLE_CHOICE: 'multiple_choice',
  SINGLE_CHOICE: 'single_choice',
  TEXT_INPUT: 'text_input',
  ESSAY: 'essay',
  TRUE_FALSE: 'true_false',
  RATING: 'rating',
} as const;

export default function CreateExamPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'basic' | 'questions' | 'settings'>('basic');

  const [examData, setExamData] = useState<ExamFormData>({
    title: '',
    description: '',
    exam_type: ExamType.CUSTOM,
    time_limit_minutes: null,
    max_attempts: 1,
    passing_score: null,
    is_randomized: false,
    allow_web_usage: true,
    monitor_web_usage: false,
    require_face_verification: false,
    face_check_interval_minutes: 5,
    show_results_immediately: true,
    show_correct_answers: false,
    show_score: true,
    instructions: '',
  });

  const [questions, setQuestions] = useState<QuestionFormData[]>([]);
  const [editingQuestionIndex, setEditingQuestionIndex] = useState<number | null>(null);

  const handleExamDataChange = (field: keyof ExamFormData, value: any) => {
    setExamData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const addQuestion = () => {
    const newQuestion: QuestionFormData = {
      question_text: '',
      question_type: QuestionType.SINGLE_CHOICE,
      points: 1,
      time_limit_seconds: null,
      is_required: true,
      options: {},
      correct_answers: [],
      max_length: null,
      min_length: null,
      rating_scale: 5,
      explanation: '',
      tags: [],
    };

    setQuestions([...questions, newQuestion]);
    setEditingQuestionIndex(questions.length);
    setActiveTab('questions');
  };

  const updateQuestion = (index: number, questionData: QuestionFormData) => {
    const updatedQuestions = [...questions];
    updatedQuestions[index] = questionData;
    setQuestions(updatedQuestions);
    setEditingQuestionIndex(null);
  };

  const removeQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index));
    if (editingQuestionIndex === index) {
      setEditingQuestionIndex(null);
    }
  };

  const validateForm = (): string | null => {
    if (!examData.title.trim()) {
      return 'Exam title is required';
    }

    if (questions.length === 0) {
      return 'At least one question is required';
    }

    for (let i = 0; i < questions.length; i++) {
      const question = questions[i];
      if (!question.question_text.trim()) {
        return `Question ${i + 1} text is required`;
      }

      if (
        [
          QuestionType.SINGLE_CHOICE,
          QuestionType.MULTIPLE_CHOICE,
          QuestionType.TRUE_FALSE,
        ].includes(question.question_type as any)
      ) {
        if (Object.keys(question.options).length < 2) {
          return `Question ${i + 1} needs at least 2 options`;
        }
        if (question.correct_answers.length === 0) {
          return `Question ${i + 1} needs correct answer(s) selected`;
        }
      }
    }

    return null;
  };

  const createExam = async () => {
    const validationError = validateForm();
    if (validationError) {
      toast.error(validationError);
      return;
    }

    setLoading(true);
    try {
      // Get current user's company_id (this would normally come from auth context)
      const userResponse = await fetch('/api/auth/me', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!userResponse.ok) {
        throw new Error('Failed to get user info');
      }

      const userData = await userResponse.json();
      const company_id = userData.company_id;

      if (!company_id) {
        throw new Error('User must be associated with a company');
      }

      // Prepare exam data
      const examPayload = {
        ...examData,
        company_id,
      };

      // Prepare questions data
      const questionsPayload = questions.map((question, index) => ({
        ...question,
        order_index: index,
        exam_id: 0, // Will be set by the API
      }));

      const response = await fetch('/api/exam/exams', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          ...examPayload,
          questions: questionsPayload,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to create exam');
      }

      const createdExam = await response.json();
      toast.success('Exam created successfully!');
      router.push(`/admin/exams/${createdExam.id}`);
    } catch (error) {
      console.error('Error creating exam:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to create exam');
    } finally {
      setLoading(false);
    }
  };

  const saveDraft = async () => {
    const validationError = validateForm();
    if (validationError) {
      toast.error(validationError);
      return;
    }

    // Set status to draft and create
    const originalData = examData;
    setExamData((prev) => ({ ...prev, status: 'draft' }));
    await createExam();
    setExamData(originalData);
  };

  return (
    <div className="container mx-auto py-6 px-4 max-w-6xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button variant="outline" asChild>
          <Link href="/admin/exams">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Exams
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create New Exam</h1>
          <p className="text-gray-600">Set up a new recruitment exam</p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 mb-6">
        <button
          onClick={() => setActiveTab('basic')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'basic'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Basic Information
        </button>
        <button
          onClick={() => setActiveTab('questions')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'questions'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Questions ({questions.length})
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            activeTab === 'settings'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Settings & Security
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'basic' && (
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>Set up the basic details for your exam</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="title">Exam Title *</Label>
                <Input
                  id="title"
                  value={examData.title}
                  onChange={(e) => handleExamDataChange('title', e.target.value)}
                  placeholder="Enter exam title"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="exam_type">Exam Type</Label>
                <Select
                  value={examData.exam_type}
                  onValueChange={(value) => handleExamDataChange('exam_type', value)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={ExamType.APTITUDE}>適性検査 (Aptitude Test)</SelectItem>
                    <SelectItem value={ExamType.SKILL}>Skill Test</SelectItem>
                    <SelectItem value={ExamType.KNOWLEDGE}>Knowledge Test</SelectItem>
                    <SelectItem value={ExamType.PERSONALITY}>Personality Test</SelectItem>
                    <SelectItem value={ExamType.CUSTOM}>Custom Test</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={examData.description}
                onChange={(e) => handleExamDataChange('description', e.target.value)}
                placeholder="Describe what this exam tests for"
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="instructions">Instructions for Candidates</Label>
              <Textarea
                id="instructions"
                value={examData.instructions}
                onChange={(e) => handleExamDataChange('instructions', e.target.value)}
                placeholder="Provide instructions that candidates will see before starting the exam"
                rows={4}
              />
            </div>

            <div className="grid gap-6 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="time_limit">Time Limit (minutes)</Label>
                <Input
                  id="time_limit"
                  type="number"
                  value={examData.time_limit_minutes || ''}
                  onChange={(e) =>
                    handleExamDataChange(
                      'time_limit_minutes',
                      e.target.value ? parseInt(e.target.value) : null
                    )
                  }
                  placeholder="No limit"
                  min="1"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="max_attempts">Max Attempts</Label>
                <Input
                  id="max_attempts"
                  type="number"
                  value={examData.max_attempts}
                  onChange={(e) =>
                    handleExamDataChange('max_attempts', parseInt(e.target.value) || 1)
                  }
                  min="1"
                  max="10"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="passing_score">Passing Score (%)</Label>
                <Input
                  id="passing_score"
                  type="number"
                  value={examData.passing_score || ''}
                  onChange={(e) =>
                    handleExamDataChange(
                      'passing_score',
                      e.target.value ? parseFloat(e.target.value) : null
                    )
                  }
                  placeholder="No requirement"
                  min="0"
                  max="100"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {activeTab === 'questions' && (
        <div className="space-y-6">
          {/* Questions List */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Questions ({questions.length})</CardTitle>
                  <CardDescription>Add and manage exam questions</CardDescription>
                </div>
                <Button onClick={addQuestion}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Question
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {questions.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-500 mb-4">No questions added yet</p>
                  <Button onClick={addQuestion} variant="outline">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Your First Question
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {questions.map((question, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <span className="font-medium">Q{index + 1}</span>
                            <span className="text-sm text-gray-500">
                              {question.question_type.replace('_', ' ')}
                            </span>
                            <span className="text-sm text-gray-500">
                              ({question.points} {question.points === 1 ? 'point' : 'points'})
                            </span>
                          </div>
                          <p className="text-gray-900 line-clamp-2">
                            {question.question_text || 'No question text'}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setEditingQuestionIndex(index)}
                          >
                            Edit
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => removeQuestion(index)}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Question Editor */}
          {editingQuestionIndex !== null && (
            <ExamQuestionForm
              question={questions[editingQuestionIndex]}
              onSave={(questionData) => updateQuestion(editingQuestionIndex, questionData)}
              onCancel={() => setEditingQuestionIndex(null)}
            />
          )}
        </div>
      )}

      {activeTab === 'settings' && (
        <div className="space-y-6">
          {/* Display Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Result Display Settings</CardTitle>
              <CardDescription>
                Control what candidates can see after completing the exam
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Show Results Immediately</Label>
                  <p className="text-sm text-gray-500">
                    Allow candidates to see their results right after completion
                  </p>
                </div>
                <Switch
                  checked={examData.show_results_immediately}
                  onCheckedChange={(checked: boolean) =>
                    handleExamDataChange('show_results_immediately', checked)
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Show Correct Answers</Label>
                  <p className="text-sm text-gray-500">
                    Display correct answers and explanations to candidates
                  </p>
                </div>
                <Switch
                  checked={examData.show_correct_answers}
                  onCheckedChange={(checked: boolean) =>
                    handleExamDataChange('show_correct_answers', checked)
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Show Score</Label>
                  <p className="text-sm text-gray-500">
                    Display the numerical score and percentage to candidates
                  </p>
                </div>
                <Switch
                  checked={examData.show_score}
                  onCheckedChange={(checked: boolean) =>
                    handleExamDataChange('show_score', checked)
                  }
                />
              </div>
            </CardContent>
          </Card>

          {/* Question Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Question Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Randomize Question Order</Label>
                  <p className="text-sm text-gray-500">
                    Show questions in random order for each candidate
                  </p>
                </div>
                <Switch
                  checked={examData.is_randomized}
                  onCheckedChange={(checked: boolean) =>
                    handleExamDataChange('is_randomized', checked)
                  }
                />
              </div>
            </CardContent>
          </Card>

          {/* Security Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Security & Monitoring</CardTitle>
              <CardDescription>
                Configure security measures and monitoring during the exam
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Allow Web Usage</Label>
                  <p className="text-sm text-gray-500">
                    Allow candidates to switch tabs or use other browser features
                  </p>
                </div>
                <Switch
                  checked={examData.allow_web_usage}
                  onCheckedChange={(checked: boolean) =>
                    handleExamDataChange('allow_web_usage', checked)
                  }
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Monitor Web Usage</Label>
                  <p className="text-sm text-gray-500">
                    Track and record when candidates switch tabs or lose focus
                  </p>
                </div>
                <Switch
                  checked={examData.monitor_web_usage}
                  onCheckedChange={(checked: boolean) =>
                    handleExamDataChange('monitor_web_usage', checked)
                  }
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div>
                  <Label>Require Face Verification</Label>
                  <p className="text-sm text-gray-500">
                    Periodically verify candidate identity using camera
                  </p>
                </div>
                <Switch
                  checked={examData.require_face_verification}
                  onCheckedChange={(checked: boolean) =>
                    handleExamDataChange('require_face_verification', checked)
                  }
                />
              </div>

              {examData.require_face_verification && (
                <div className="space-y-2">
                  <Label htmlFor="face_check_interval">Face Check Interval (minutes)</Label>
                  <Input
                    id="face_check_interval"
                    type="number"
                    value={examData.face_check_interval_minutes}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                      handleExamDataChange(
                        'face_check_interval_minutes',
                        parseInt(e.target.value) || 5
                      )
                    }
                    min="1"
                    max="60"
                    fullWidth={false}
                    className="w-32"
                  />
                  <p className="text-sm text-gray-500">How often to request face verification</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-6 border-t">
        <div className="text-sm text-gray-500">
          {questions.length} question{questions.length !== 1 ? 's' : ''} added
        </div>

        <div className="flex gap-3">
          <Button variant="outline" onClick={saveDraft} disabled={loading}>
            Save as Draft
          </Button>

          <Button onClick={createExam} disabled={loading}>
            {loading ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Creating...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Create Exam
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
