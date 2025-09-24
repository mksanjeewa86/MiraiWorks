'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Play,
  Eye,
  Clock,
  BookOpen,
  Shield,
  Info,
  CheckCircle,
  Target,
  Globe,
} from 'lucide-react';
import Link from 'next/link';

export default function DemoExamPage() {
  const [setSelectedExamType] = useState<string>('aptitude');

  const demoExams = [
    {
      id: 'demo-aptitude',
      title: '適性検査 Demo (Aptitude Test)',
      description:
        'Experience a sample aptitude test with various question types including logical reasoning, numerical analysis, and language comprehension.',
      exam_type: 'aptitude',
      time_limit_minutes: 15,
      total_questions: 10,
      features: ['Multiple Choice', 'Logical Reasoning', 'Numerical Analysis', 'Time Tracking'],
      difficulty: 'Beginner',
      estimated_time: '10-15 minutes',
    },
    {
      id: 'demo-skill',
      title: 'Technical Skill Assessment Demo',
      description:
        'Practice with programming and technical questions to understand the format of skill-based assessments.',
      exam_type: 'skill',
      time_limit_minutes: 20,
      total_questions: 8,
      features: ['Code Review', 'Technical Concepts', 'Problem Solving', 'Essay Questions'],
      difficulty: 'Intermediate',
      estimated_time: '15-20 minutes',
    },
    {
      id: 'demo-personality',
      title: 'Personality Assessment Demo',
      description:
        'Sample personality and behavioral assessment to help you understand what employers might evaluate.',
      exam_type: 'personality',
      time_limit_minutes: 10,
      total_questions: 15,
      features: ['Rating Scales', 'Behavioral Scenarios', 'Self Assessment', 'Quick Response'],
      difficulty: 'Easy',
      estimated_time: '8-12 minutes',
    },
  ];

  const getExamTypeColor = (type: string) => {
    switch (type) {
      case 'aptitude':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'skill':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'personality':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy':
        return 'text-green-600';
      case 'beginner':
        return 'text-blue-600';
      case 'intermediate':
        return 'text-orange-600';
      case 'advanced':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const startDemoExam = (examId: string) => {
    // This would route to a special demo exam interface
    window.location.href = `/exams/demo/${examId}`;
  };

  return (
    <div className="container mx-auto py-6 px-4 max-w-6xl">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Practice Exams</h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Get familiar with our exam platform by taking these practice tests. Experience different
          question types and features before taking your actual recruitment exam.
        </p>
      </div>

      {/* Benefits Section */}
      <Alert className="mb-8 bg-blue-50 border-blue-200">
        <Info className="h-4 w-4" />
        <AlertDescription className="text-blue-800">
          <strong>Why take practice exams?</strong> Familiarize yourself with the interface,
          understand different question types, practice time management, and reduce test anxiety.
          These demo exams don't affect your actual results.
        </AlertDescription>
      </Alert>

      {/* Demo Exams Grid */}
      <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-3 mb-8">
        {demoExams.map((exam) => (
          <Card key={exam.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between mb-2">
                <CardTitle className="text-lg">{exam.title}</CardTitle>
                <Badge className={getExamTypeColor(exam.exam_type)}>{exam.exam_type}</Badge>
              </div>
              <CardDescription className="text-sm">{exam.description}</CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              {/* Exam Stats */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <BookOpen className="h-4 w-4 text-gray-400" />
                  <span>{exam.total_questions} questions</span>
                </div>

                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <span>{exam.time_limit_minutes} min limit</span>
                </div>

                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-gray-400" />
                  <span className={getDifficultyColor(exam.difficulty)}>{exam.difficulty}</span>
                </div>

                <div className="flex items-center gap-2">
                  <Globe className="h-4 w-4 text-gray-400" />
                  <span>{exam.estimated_time}</span>
                </div>
              </div>

              {/* Features */}
              <div>
                <div className="text-sm font-medium text-gray-700 mb-2">Features included:</div>
                <div className="flex flex-wrap gap-1">
                  {exam.features.map((feature) => (
                    <Badge key={feature} variant="secondary" className="text-xs">
                      {feature}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Action Button */}
              <Button onClick={() => startDemoExam(exam.id)} className="w-full" size="lg">
                <Play className="h-4 w-4 mr-2" />
                Start Practice Exam
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Features Overview */}
      <div className="grid gap-6 md:grid-cols-2 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-600" />
              Security Features You'll Experience
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <div className="font-medium">Time Management</div>
                <div className="text-sm text-gray-600">Real-time countdown timer with warnings</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <div className="font-medium">Web Usage Monitoring</div>
                <div className="text-sm text-gray-600">
                  Experience how tab switching is detected
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <div className="font-medium">Question Navigation</div>
                <div className="text-sm text-gray-600">Practice moving between questions</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <div className="font-medium">Auto-Save</div>
                <div className="text-sm text-gray-600">
                  Answers are automatically saved as you type
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-green-600" />
              Question Types You'll Practice
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <div className="font-medium">Multiple Choice Questions</div>
                <div className="text-sm text-gray-600">Select one or more correct answers</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <div className="font-medium">Text Input & Essays</div>
                <div className="text-sm text-gray-600">Practice writing detailed responses</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <div className="font-medium">Rating Scales</div>
                <div className="text-sm text-gray-600">Use slider controls for assessments</div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <div className="font-medium">True/False Questions</div>
                <div className="text-sm text-gray-600">Quick binary choice questions</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tips Section */}
      <Card className="bg-green-50 border-green-200">
        <CardHeader>
          <CardTitle className="text-green-800">Tips for Success</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                1
              </div>
              <div>
                <div className="font-medium text-green-800">Prepare Your Environment</div>
                <div className="text-sm text-green-700">
                  Find a quiet space with stable internet connection
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                2
              </div>
              <div>
                <div className="font-medium text-green-800">Read Instructions Carefully</div>
                <div className="text-sm text-green-700">
                  Take time to understand each question type
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                3
              </div>
              <div>
                <div className="font-medium text-green-800">Manage Your Time</div>
                <div className="text-sm text-green-700">
                  Keep an eye on the timer and pace yourself
                </div>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-sm font-bold">
                4
              </div>
              <div>
                <div className="font-medium text-green-800">Stay Focused</div>
                <div className="text-sm text-green-700">
                  Avoid switching tabs or opening other applications
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Call to Action */}
      <div className="text-center mt-8">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Ready for your actual exam?</h3>
        <p className="text-gray-600 mb-4">
          Once you've practiced with these demos, check your assigned exams.
        </p>
        <Button asChild size="lg">
          <Link href="/exams">
            <Eye className="h-4 w-4 mr-2" />
            View My Assigned Exams
          </Link>
        </Button>
      </div>
    </div>
  );
}
