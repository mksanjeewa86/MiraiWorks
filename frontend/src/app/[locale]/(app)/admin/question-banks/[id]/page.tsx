'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ROUTES } from '@/routes/config';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  LoadingSpinner,
} from '@/components/ui';
import { ArrowLeft, Edit, Trash2, Copy, Globe, Building2 } from 'lucide-react';
import { questionBankApi } from '@/api/questionBank';
import type { QuestionBankDetail } from '@/types/questionBank';
import { toast } from 'sonner';

export default function QuestionBankDetailPage() {
  const params = useParams();
  const router = useRouter();
  const bankId = parseInt(params.id as string);

  const [bank, setBank] = useState<QuestionBankDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQuestionBank();
  }, [bankId]);

  const loadQuestionBank = async () => {
    setLoading(true);
    const response = await questionBankApi.getQuestionBank(bankId);

    if (response.success && response.data) {
      setBank(response.data);
    } else {
      toast.error(response.message || 'Failed to load question bank');
    }

    setLoading(false);
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this question bank?')) return;

    const response = await questionBankApi.deleteQuestionBank(bankId);

    if (response.success) {
      toast.success('Question bank deleted');
      router.push(ROUTES.ADMIN.QUESTION_BANKS.BASE);
    } else {
      toast.error(response.message || 'Failed to delete question bank');
    }
  };

  const handleClone = async () => {
    const response = await questionBankApi.cloneQuestionBank(bankId);

    if (response.success && response.data) {
      toast.success('Question bank cloned successfully');
      router.push(ROUTES.ADMIN.QUESTION_BANKS.BY_ID(response.data.id));
    } else {
      toast.error(response.message || 'Failed to clone question bank');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!bank) {
    return (
      <div className="container mx-auto py-6 px-4 max-w-4xl">
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Question bank not found
          </h2>
          <Button asChild>
            <Link href={ROUTES.ADMIN.QUESTION_BANKS.BASE}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Question Banks
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 px-4 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Button variant="ghost" asChild className="mb-2">
            <Link href={ROUTES.ADMIN.QUESTION_BANKS.BASE}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Question Banks
            </Link>
          </Button>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{bank.name}</h1>
            {bank.company_id === null && (
              <span className="inline-flex items-center px-3 py-1 rounded-md bg-blue-100 text-blue-700 text-sm">
                <Globe className="h-4 w-4 mr-1" />
                Global
              </span>
            )}
            {bank.is_public && (
              <span className="inline-flex items-center px-3 py-1 rounded-md bg-green-100 text-green-700 text-sm">
                <Building2 className="h-4 w-4 mr-1" />
                Public
              </span>
            )}
          </div>
          <p className="text-gray-600">{bank.description || 'No description'}</p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleClone}>
            <Copy className="h-4 w-4 mr-2" />
            Clone
          </Button>
          <Button variant="outline">
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="outline" onClick={handleDelete}>
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>

      {/* Bank Information */}
      <div className="grid gap-6 lg:grid-cols-3 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Exam Type</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold capitalize">{bank.exam_type}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Questions</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{bank.questions.length}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Difficulty</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold capitalize">
              {bank.difficulty || 'Mixed'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Questions List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Questions ({bank.questions.length})</CardTitle>
              <CardDescription>
                Questions in this bank
              </CardDescription>
            </div>
            <Button disabled>
              Add Questions (Coming Soon)
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {bank.questions.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No questions in this bank yet.
            </div>
          ) : (
            <div className="space-y-4">
              {bank.questions.map((question, index) => (
                <div
                  key={question.id}
                  className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-semibold text-gray-700">
                          Q{index + 1}.
                        </span>
                        <span className="text-sm text-gray-500 capitalize">
                          {question.question_type.replace('_', ' ')}
                        </span>
                        <span className="text-sm text-gray-500">
                          ({question.points} {question.points === 1 ? 'point' : 'points'})
                        </span>
                        {question.difficulty && (
                          <span
                            className={`text-xs px-2 py-1 rounded-full ${
                              question.difficulty === 'easy'
                                ? 'bg-green-100 text-green-700'
                                : question.difficulty === 'medium'
                                ? 'bg-yellow-100 text-yellow-700'
                                : 'bg-red-100 text-red-700'
                            }`}
                          >
                            {question.difficulty}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-900">{question.question_text}</p>
                      {question.tags && question.tags.length > 0 && (
                        <div className="flex gap-2 mt-2">
                          {question.tags.map((tag) => (
                            <span
                              key={tag}
                              className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
