"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  ArrowLeft, 
  Play, 
  Eye, 
  Clock, 
  Users, 
  BookOpen,
  Settings,
  Shield,
  Info,
  AlertTriangle
} from "lucide-react";
import { LoadingSpinner } from "@/components/ui/loading-spinner";
import { toast } from "sonner";

interface ExamInfo {
  id: number;
  title: string;
  description: string | null;
  exam_type: string;
  status: string;
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
  instructions: string | null;
  created_at: string;
  total_questions: number;
}

interface Question {
  id: number;
  question_text: string;
  question_type: string;
  order_index: number;
  points: number;
  time_limit_seconds: number | null;
  is_required: boolean;
  options: Record<string, string> | null;
  correct_answers: string[] | null;
  max_length: number | null;
  min_length: number | null;
  rating_scale: number | null;
  explanation: string | null;
  tags: string[] | null;
}

const ExamType = {
  APTITUDE: "aptitude",
  SKILL: "skill",
  KNOWLEDGE: "knowledge",
  PERSONALITY: "personality",
  CUSTOM: "custom",
} as const;

const QuestionType = {
  MULTIPLE_CHOICE: "multiple_choice",
  SINGLE_CHOICE: "single_choice",
  TEXT_INPUT: "text_input",
  ESSAY: "essay",
  TRUE_FALSE: "true_false",
  RATING: "rating",
} as const;

export default function ExamPreviewPage() {
  const params = useParams();
  const router = useRouter();
  const examId = params.id as string;

  const [examInfo, setExamInfo] = useState<ExamInfo | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [previewMode, setPreviewMode] = useState<"overview" | "questions">("overview");

  useEffect(() => {
    fetchExamData();
    fetchQuestions();
  }, [examId]);

  const fetchExamData = async () => {
    try {
      const response = await fetch(`/api/exam/exams/${examId}`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch exam details");
      }

      const data = await response.json();
      setExamInfo(data);
    } catch (error) {
      console.error("Error fetching exam:", error);
      toast.error("Failed to load exam details");
    }
  };

  const fetchQuestions = async () => {
    try {
      const response = await fetch(`/api/exam/exams/${examId}/questions`, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch questions");
      }

      const data = await response.json();
      setQuestions(data);
    } catch (error) {
      console.error("Error fetching questions:", error);
      toast.error("Failed to load questions");
    } finally {
      setLoading(false);
    }
  };

  const startTestExam = () => {
    // Start exam in test mode - this would create a special test session
    router.push(`/exams/take/${examId}?mode=test`);
  };

  const getExamTypeLabel = (type: string) => {
    const labels = {
      [ExamType.APTITUDE]: "適性検査",
      [ExamType.SKILL]: "Skill Test",
      [ExamType.KNOWLEDGE]: "Knowledge Test",
      [ExamType.PERSONALITY]: "Personality Test",
      [ExamType.CUSTOM]: "Custom Test",
    };
    return labels[type as keyof typeof labels] || type;
  };

  const getQuestionTypeLabel = (type: string) => {
    const labels = {
      [QuestionType.MULTIPLE_CHOICE]: "Multiple Choice",
      [QuestionType.SINGLE_CHOICE]: "Single Choice",
      [QuestionType.TEXT_INPUT]: "Text Input",
      [QuestionType.ESSAY]: "Essay",
      [QuestionType.TRUE_FALSE]: "True/False",
      [QuestionType.RATING]: "Rating Scale",
    };
    return labels[type as keyof typeof labels] || type;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800 border-green-200";
      case "draft":
        return "bg-gray-100 text-gray-800 border-gray-200";
      case "archived":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (!examInfo) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 mx-auto text-red-500 mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Exam not found</h2>
          <p className="text-gray-600 mb-4">The exam you're looking for doesn't exist.</p>
          <Button asChild>
            <Link href="/admin/exams">Back to Exams</Link>
          </Button>
        </div>
      </div>
    );
  }

  const totalPoints = questions.reduce((sum, q) => sum + q.points, 0);
  const requiredQuestions = questions.filter(q => q.is_required).length;

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
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-gray-900">{examInfo.title}</h1>
          <p className="text-gray-600">Exam Preview & Test</p>
        </div>
        <div className="flex gap-3">
          <Button onClick={startTestExam} className="bg-blue-600 hover:bg-blue-700">
            <Play className="h-4 w-4 mr-2" />
            Take Test Exam
          </Button>
          <Button asChild variant="outline">
            <Link href={`/admin/exams/${examId}/edit`}>
              <Settings className="h-4 w-4 mr-2" />
              Edit Exam
            </Link>
          </Button>
        </div>
      </div>

      {/* Status Alert */}
      {examInfo.status !== "active" && (
        <Alert className="mb-6">
          <Info className="h-4 w-4" />
          <AlertDescription>
            This exam is currently in <strong>{examInfo.status}</strong> status. 
            {examInfo.status === "draft" && " It needs to be activated before candidates can take it."}
            {examInfo.status === "archived" && " It is no longer available to candidates."}
          </AlertDescription>
        </Alert>
      )}

      {/* Tab Navigation */}
      <div className="flex space-x-1 bg-gray-100 rounded-lg p-1 mb-6">
        <button
          onClick={() => setPreviewMode("overview")}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            previewMode === "overview" 
              ? "bg-white text-gray-900 shadow-sm" 
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setPreviewMode("questions")}
          className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
            previewMode === "questions" 
              ? "bg-white text-gray-900 shadow-sm" 
              : "text-gray-600 hover:text-gray-900"
          }`}
        >
          Questions Preview ({questions.length})
        </button>
      </div>

      {previewMode === "overview" && (
        <div className="space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Basic Information</CardTitle>
                <Badge className={getStatusColor(examInfo.status)}>
                  {examInfo.status.charAt(0).toUpperCase() + examInfo.status.slice(1)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label className="text-sm font-medium text-gray-600">Type</Label>
                  <div className="text-gray-900">{getExamTypeLabel(examInfo.exam_type)}</div>
                </div>
                <div>
                  <Label className="text-sm font-medium text-gray-600">Created</Label>
                  <div className="text-gray-900">{new Date(examInfo.created_at).toLocaleDateString()}</div>
                </div>
              </div>

              {examInfo.description && (
                <div>
                  <Label className="text-sm font-medium text-gray-600">Description</Label>
                  <div className="text-gray-900 whitespace-pre-wrap">{examInfo.description}</div>
                </div>
              )}

              {examInfo.instructions && (
                <div>
                  <Label className="text-sm font-medium text-gray-600">Instructions for Candidates</Label>
                  <div className="text-gray-900 whitespace-pre-wrap bg-blue-50 p-4 rounded-lg border border-blue-200">
                    {examInfo.instructions}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Exam Configuration */}
          <div className="grid gap-6 md:grid-cols-2">
            {/* Timing & Attempts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Timing & Attempts
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Time Limit</span>
                  <span className="font-medium">
                    {examInfo.time_limit_minutes ? `${examInfo.time_limit_minutes} minutes` : "No limit"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Max Attempts</span>
                  <span className="font-medium">{examInfo.max_attempts}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Passing Score</span>
                  <span className="font-medium">
                    {examInfo.passing_score ? `${examInfo.passing_score}%` : "No requirement"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Question Order</span>
                  <span className="font-medium">
                    {examInfo.is_randomized ? "Randomized" : "Fixed"}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Questions Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5" />
                  Questions Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Questions</span>
                  <span className="font-medium">{questions.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Required Questions</span>
                  <span className="font-medium">{requiredQuestions}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Points</span>
                  <span className="font-medium">{totalPoints}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Average Points/Question</span>
                  <span className="font-medium">
                    {questions.length > 0 ? (totalPoints / questions.length).toFixed(1) : "0"}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Security Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Security & Monitoring
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Web Usage</span>
                    <Badge variant={examInfo.allow_web_usage ? "secondary" : "destructive"}>
                      {examInfo.allow_web_usage ? "Allowed" : "Blocked"}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Web Monitoring</span>
                    <Badge variant={examInfo.monitor_web_usage ? "default" : "secondary"}>
                      {examInfo.monitor_web_usage ? "Enabled" : "Disabled"}
                    </Badge>
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Face Verification</span>
                    <Badge variant={examInfo.require_face_verification ? "default" : "secondary"}>
                      {examInfo.require_face_verification ? "Required" : "Not Required"}
                    </Badge>
                  </div>
                  {examInfo.require_face_verification && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Check Interval</span>
                      <span className="font-medium">{examInfo.face_check_interval_minutes} minutes</span>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Result Display Settings */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Result Display Settings
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Show Results</span>
                  <Badge variant={examInfo.show_results_immediately ? "default" : "secondary"}>
                    {examInfo.show_results_immediately ? "Immediately" : "Manual"}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Show Answers</span>
                  <Badge variant={examInfo.show_correct_answers ? "default" : "secondary"}>
                    {examInfo.show_correct_answers ? "Yes" : "No"}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Show Score</span>
                  <Badge variant={examInfo.show_score ? "default" : "secondary"}>
                    {examInfo.show_score ? "Yes" : "No"}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {previewMode === "questions" && (
        <div className="space-y-6">
          {questions.length === 0 ? (
            <Card>
              <CardContent className="p-8 text-center">
                <BookOpen className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No questions added</h3>
                <p className="text-gray-600 mb-4">Add questions to this exam to enable testing.</p>
                <Button asChild>
                  <Link href={`/admin/exams/${examId}/edit`}>
                    Add Questions
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ) : (
            questions.map((question, index) => (
              <Card key={question.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-lg">Question {index + 1}</CardTitle>
                      <CardDescription>
                        {getQuestionTypeLabel(question.question_type)} • {question.points} {question.points === 1 ? "point" : "points"}
                        {question.time_limit_seconds && ` • ${Math.floor(question.time_limit_seconds / 60)}m limit`}
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      {question.is_required && (
                        <Badge variant="destructive">Required</Badge>
                      )}
                      <Badge variant="outline">{getQuestionTypeLabel(question.question_type)}</Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Question Text */}
                  <div className="prose prose-gray max-w-none">
                    <div className="text-gray-900 whitespace-pre-wrap">
                      {question.question_text}
                    </div>
                  </div>

                  {/* Options for Choice Questions */}
                  {question.options && Object.keys(question.options).length > 0 && (
                    <div className="space-y-2">
                      <Label className="text-sm font-medium text-gray-600">Options:</Label>
                      <div className="space-y-2">
                        {Object.entries(question.options).map(([key, value]) => (
                          <div key={key} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                            <Badge variant="outline" className="text-xs">{key}</Badge>
                            <span className="flex-1">{value}</span>
                            {question.correct_answers?.includes(key) && (
                              <Badge variant="default" className="bg-green-100 text-green-800">
                                Correct
                              </Badge>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Rating Scale */}
                  {question.question_type === QuestionType.RATING && question.rating_scale && (
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Rating Scale:</Label>
                      <div className="text-gray-900">1 to {question.rating_scale}</div>
                    </div>
                  )}

                  {/* Text Limits */}
                  {[QuestionType.TEXT_INPUT, QuestionType.ESSAY].includes(question.question_type as any) && (
                    <div className="grid gap-2 md:grid-cols-2">
                      {question.min_length && (
                        <div>
                          <Label className="text-sm font-medium text-gray-600">Minimum Length:</Label>
                          <div className="text-gray-900">{question.min_length} characters</div>
                        </div>
                      )}
                      {question.max_length && (
                        <div>
                          <Label className="text-sm font-medium text-gray-600">Maximum Length:</Label>
                          <div className="text-gray-900">{question.max_length} characters</div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Explanation */}
                  {question.explanation && (
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Explanation:</Label>
                      <div className="text-gray-900 bg-blue-50 p-3 rounded-lg border border-blue-200">
                        {question.explanation}
                      </div>
                    </div>
                  )}

                  {/* Tags */}
                  {question.tags && question.tags.length > 0 && (
                    <div>
                      <Label className="text-sm font-medium text-gray-600">Tags:</Label>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {question.tags.map(tag => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* Test Exam Call to Action */}
      <Card className="mt-8 bg-blue-50 border-blue-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                Ready to test this exam?
              </h3>
              <p className="text-blue-700">
                Take a test run to experience the exam from a candidate's perspective. 
                Test sessions don't count towards statistics and are marked as practice.
              </p>
            </div>
            <Button onClick={startTestExam} size="lg" className="bg-blue-600 hover:bg-blue-700">
              <Play className="h-5 w-5 mr-2" />
              Start Test Exam
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function Label({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={className}>{children}</div>;
}