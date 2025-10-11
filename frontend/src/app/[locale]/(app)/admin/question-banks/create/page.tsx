'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ROUTES } from '@/routes/config';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Input,
  Textarea,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Switch,
  Label,
  LoadingSpinner,
} from '@/components/ui';
import { ArrowLeft, Save, Globe, Building2 } from 'lucide-react';
import { questionBankApi } from '@/api/questionBank';
import type { QuestionBankFormData } from '@/types/questionBank';
import { toast } from 'sonner';
import { useAuth } from '@/contexts/AuthContext';

export default function CreateQuestionBankPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState<QuestionBankFormData>({
    name: '',
    description: '',
    exam_type: 'custom',
    category: '',
    difficulty: null,
    is_public: false,
    company_id: undefined,
  });

  const isSystemAdmin = user?.roles?.some(r => r.role.name === 'system_admin');
  const isGlobal = formData.company_id === undefined && isSystemAdmin;

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      toast.error('Please enter a name for the question bank');
      return;
    }

    setLoading(true);

    const response = await questionBankApi.createQuestionBank(formData);

    if (response.success && response.data) {
      toast.success('Question bank created successfully');
      router.push(ROUTES.ADMIN.QUESTION_BANKS.BY_ID(response.data.id));
    } else {
      toast.error(response.message || 'Failed to create question bank');
    }

    setLoading(false);
  };

  return (
    <div className="container mx-auto py-6 px-4 max-w-4xl">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button variant="outline" asChild>
          <Link href={ROUTES.ADMIN.QUESTION_BANKS.BASE}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Question Banks
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Create Question Bank</h1>
          <p className="text-gray-600">Set up a new collection of reusable questions</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Question Bank Information</CardTitle>
          <CardDescription>
            Configure the basic settings for your question bank
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name">Name *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., JavaScript Fundamentals Questions"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of this question bank"
              rows={3}
            />
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="exam_type">Exam Type</Label>
              <Select
                value={formData.exam_type}
                onValueChange={(value) => setFormData({ ...formData, exam_type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="aptitude">Aptitude</SelectItem>
                  <SelectItem value="skill">Skill</SelectItem>
                  <SelectItem value="knowledge">Knowledge</SelectItem>
                  <SelectItem value="personality">Personality</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="category">Category (Optional)</Label>
              <Input
                id="category"
                value={formData.category || ''}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="e.g., Programming, Mathematics"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="difficulty">Difficulty Level</Label>
            <Select
              value={formData.difficulty || 'mixed'}
              onValueChange={(value) =>
                setFormData({
                  ...formData,
                  difficulty: value === 'mixed' ? null : (value as any),
                })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="easy">Easy</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="hard">Hard</SelectItem>
                <SelectItem value="mixed">Mixed</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="border-t pt-6 space-y-4">
            <h3 className="text-sm font-medium">Visibility & Access</h3>

            <div className="flex items-center justify-between">
              <div className="flex items-start gap-3">
                <Building2 className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <Label>Public Question Bank</Label>
                  <p className="text-sm text-gray-500">
                    Make this question bank visible to all companies
                  </p>
                </div>
              </div>
              <Switch
                checked={formData.is_public}
                onCheckedChange={(checked) =>
                  setFormData({ ...formData, is_public: checked })
                }
              />
            </div>

            {isSystemAdmin && (
              <div className="flex items-center justify-between p-4 border border-blue-200 bg-blue-50 rounded-lg">
                <div className="flex items-start gap-3">
                  <Globe className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div>
                    <Label className="text-blue-900">
                      Global Question Bank (System Admin Only)
                    </Label>
                    <p className="text-sm text-blue-700">
                      Create a system-wide question bank accessible to all companies
                    </p>
                  </div>
                </div>
                <Switch
                  checked={isGlobal}
                  onCheckedChange={(checked) => {
                    setFormData({
                      ...formData,
                      company_id: checked ? undefined : user?.company_id,
                      is_public: checked ? true : formData.is_public,
                    });
                  }}
                />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex items-center justify-end gap-3 mt-6">
        <Button variant="outline" asChild disabled={loading}>
          <Link href={ROUTES.ADMIN.QUESTION_BANKS.BASE}>Cancel</Link>
        </Button>

        <Button onClick={handleSubmit} disabled={loading}>
          {loading ? (
            <>
              <LoadingSpinner size="sm" className="mr-2" />
              Creating...
            </>
          ) : (
            <>
              <Save className="h-4 w-4 mr-2" />
              Create Question Bank
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
