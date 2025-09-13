'use client';

import { useState, useEffect } from 'react';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Plus, FileText, Eye, Download, Edit, Trash2, Star, Calendar, Share } from 'lucide-react';
import { resumesApi } from "@/api/resumes";
import type { Resume } from '@/types';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

function ResumesPageContent() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchResumes = async () => {
      try {
        setLoading(true);
        setError('');
        
        const response = await resumesApi.getAll();
        setResumes(response.data || []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load resumes');
        console.error('Failed to fetch resumes:', err);
        setResumes([]);
      } finally {
        setLoading(false);
      }
    };

    fetchResumes();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'success';
      case 'draft':
        return 'warning';
      case 'archived':
        return 'secondary';
      default:
        return 'primary';
    }
  };

  const getVisibilityText = (visibility: string) => {
    switch (visibility) {
      case 'public':
        return 'Public';
      case 'private':
        return 'Private';
      case 'unlisted':
        return 'Unlisted';
      default:
        return 'Private';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const handleDelete = async (resumeId: number) => {
    if (window.confirm('Are you sure you want to delete this resume?')) {
      try {
        await resumesApi.delete(resumeId);
        setResumes(prev => prev.filter(r => r.id !== resumeId));
      } catch (err) {
        console.error('Failed to delete resume:', err);
        alert('Failed to delete resume');
      }
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner className="w-8 h-8" />
        </div>
      </AppLayout>
    );
  }

  if (error) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center h-64">
          <div className="text-6xl mb-4">❌</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Error Loading Resumes</h3>
          <p className="text-red-600 mb-6">{error}</p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Resumes</h1>
            <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
              Create and manage your professional resumes
            </p>
          </div>
          <Button className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Create Resume
          </Button>
        </div>

        {/* Resume Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6 text-center">
            <div className="text-2xl font-bold" style={{ color: 'var(--brand-primary)' }}>
              {resumes.length}
            </div>
            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>Total Resumes</div>
          </Card>
          <Card className="p-6 text-center">
            <div className="text-2xl font-bold text-green-600">
              {resumes.filter(r => r.status === 'published').length}
            </div>
            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>Published</div>
          </Card>
          <Card className="p-6 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {resumes.reduce((sum, r) => sum + (r.view_count || 0), 0)}
            </div>
            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>Total Views</div>
          </Card>
          <Card className="p-6 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {resumes.reduce((sum, r) => sum + (r.download_count || 0), 0)}
            </div>
            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>Downloads</div>
          </Card>
        </div>

        {/* Resumes Grid */}
        {resumes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resumes.map(resume => (
              <Card key={resume.id} className="p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5" style={{ color: 'var(--brand-primary)' }} />
                    <Badge variant={getStatusColor(resume.status)}>
                      {resume.status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button variant="ghost" size="sm">
                      <Star className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(resume.id)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <h3 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
                      {resume.title}
                    </h3>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      {resume.description || 'No description provided'}
                    </p>
                  </div>

                  <div className="flex items-center justify-between text-sm" style={{ color: 'var(--text-muted)' }}>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>Updated {formatDate(resume.updated_at)}</span>
                    </div>
                    <span>{getVisibilityText(resume.visibility)}</span>
                  </div>

                  <div className="flex items-center justify-between text-sm" style={{ color: 'var(--text-secondary)' }}>
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1">
                        <Eye className="h-4 w-4" />
                        <span>{resume.view_count || 0}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Download className="h-4 w-4" />
                        <span>{resume.download_count || 0}</span>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-4">
                    <Button size="sm" className="flex-1">
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1">
                      <Eye className="h-4 w-4 mr-2" />
                      Preview
                    </Button>
                    <Button variant="outline" size="sm">
                      <Share className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="p-12 text-center">
            <FileText className="h-16 w-16 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
            <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
              No resumes found
            </h3>
            <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>
              Create your first resume to get started with your job search.
            </p>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Your First Resume
            </Button>
          </Card>
        )}
      </div>
    </AppLayout>
  );
}

export default function ResumesPage() {
  return (
    <ProtectedRoute>
      <ResumesPageContent />
    </ProtectedRoute>
  );
}