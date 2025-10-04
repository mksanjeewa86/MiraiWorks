'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Button,
  Badge,
  Input,
  LoadingSpinner,
} from '@/components/ui';
import { Plus, Search, FileText, Globe, Lock } from 'lucide-react';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { toast } from 'sonner';

interface ExamTemplate {
  id: number;
  name: string;
  description?: string;
  exam_type: string;
  is_public: boolean;
  category?: string;
  created_at: string;
}

function ExamTemplatesPageContent() {
  const [templates, setTemplates] = useState<ExamTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      // TODO: Implement API call when backend is ready
      // const response = await examTemplateApi.getTemplates();
      // setTemplates(response.data.templates);

      // Placeholder data
      setTemplates([
        {
          id: 1,
          name: 'SPI Aptitude Test Template',
          description: 'Standard SPI test template with 40 questions',
          exam_type: 'spi',
          is_public: true,
          category: 'Japanese Aptitude',
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          name: 'Programming Skills Assessment',
          description: 'Technical coding assessment template',
          exam_type: 'programming_aptitude',
          is_public: false,
          category: 'Technical',
          created_at: new Date().toISOString(),
        },
      ]);
    } catch (error) {
      toast.error('Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const filteredTemplates = templates.filter((template) =>
    template.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <AppLayout>
      <div className="py-6">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Exam Templates</h1>
              <p className="text-gray-600 mt-1">Create and manage reusable exam templates</p>
            </div>
            <Button asChild>
              <Link href="/admin/exams/templates/create">
                <Plus className="h-4 w-4 mr-2" />
                Create Template
              </Link>
            </Button>
          </div>

          {/* Search */}
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Templates Grid */}
        {loading ? (
          <div className="flex items-center justify-center min-h-[400px]">
            <LoadingSpinner />
          </div>
        ) : filteredTemplates.length === 0 ? (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
                <p className="text-gray-600 mb-6">
                  {searchQuery
                    ? 'Try adjusting your search criteria'
                    : 'Get started by creating your first exam template'}
                </p>
                {!searchQuery && (
                  <Button asChild>
                    <Link href="/admin/exams/templates/create">
                      <Plus className="h-4 w-4 mr-2" />
                      Create Template
                    </Link>
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredTemplates.map((template) => (
              <Card key={template.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-lg">{template.name}</CardTitle>
                      {template.category && (
                        <Badge variant="outline" className="mt-2">
                          {template.category}
                        </Badge>
                      )}
                    </div>
                    <div title={template.is_public ? 'Public template' : 'Private template'}>
                      {template.is_public ? (
                        <Globe className="h-5 w-5 text-green-500" />
                      ) : (
                        <Lock className="h-5 w-5 text-gray-400" />
                      )}
                    </div>
                  </div>
                  <CardDescription className="mt-2 line-clamp-2">
                    {template.description || 'No description provided'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center justify-between">
                      <span>Type:</span>
                      <Badge variant="secondary">{template.exam_type}</Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Created:</span>
                      <span>{new Date(template.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <div className="mt-4 flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      Preview
                    </Button>
                    <Button size="sm" className="flex-1">
                      Use Template
                    </Button>
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

export default function ExamTemplatesPage() {
  return (
    <ProtectedRoute>
      <ExamTemplatesPageContent />
    </ProtectedRoute>
  );
}
