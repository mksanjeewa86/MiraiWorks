'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/card';
import Badge from '@/components/ui/badge';
import Button from '@/components/ui/button';
import LoadingSpinner from '@/components/ui/loading-spinner';
import {
  Plus,
  FileText,
  Eye,
  Download,
  Edit,
  Trash2,
  Star,
  Calendar,
  Share,
  Globe,
  Lock,
} from 'lucide-react';
import { resumesApi } from '@/api/resumes';
import { Resume, ResumeFormat } from '@/types/resume';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

function ResumesPageContent() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [generatingPdf, setGeneratingPdf] = useState<number | null>(null);

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

  const getFormatDisplayName = (format: ResumeFormat) => {
    switch (format) {
      case ResumeFormat.RIREKISHO:
        return '履歴書';
      case ResumeFormat.SHOKUMU_KEIREKISHO:
        return '職務経歴書';
      case ResumeFormat.INTERNATIONAL:
        return 'International';
      case ResumeFormat.MODERN:
        return 'Modern';
      default:
        return format;
    }
  };

  const getFormatColor = (format: ResumeFormat) => {
    switch (format) {
      case ResumeFormat.RIREKISHO:
        return 'primary';
      case ResumeFormat.SHOKUMU_KEIREKISHO:
        return 'success';
      case ResumeFormat.INTERNATIONAL:
        return 'warning';
      case ResumeFormat.MODERN:
        return 'secondary';
      default:
        return 'primary';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const handleDelete = async (resumeId: number) => {
    if (window.confirm('Are you sure you want to delete this resume?')) {
      try {
        await resumesApi.delete(resumeId);
        setResumes((prev) => prev.filter((r) => r.id !== resumeId));
      } catch (err) {
        console.error('Failed to delete resume:', err);
        alert('Failed to delete resume');
      }
    }
  };

  const handleDownloadPdf = async (resume: Resume) => {
    if (!resume.can_download_pdf) {
      alert('PDF download is not available for this resume.');
      return;
    }

    try {
      setGeneratingPdf(resume.id);

      const response = await resumesApi.generatePdf(resume.id, {
        format: 'A4',
        include_contact_info: true,
      });

      // Create download link
      const link = document.createElement('a');
      link.href = response.data?.pdf_url || '';
      link.download = `${resume.title}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      alert('PDF downloaded successfully.');
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to download PDF. Please try again.');
    } finally {
      setGeneratingPdf(null);
    }
  };

  const handleTogglePublic = async (resume: Resume) => {
    try {
      const response = await resumesApi.togglePublic(resume.id);
      if (response.data) {
        setResumes(resumes.map((r) => (r.id === resume.id ? response.data! : r)));
        alert(`Resume is now ${response.data.is_public ? 'public' : 'private'}.`);
      }
    } catch (error) {
      console.error('Error toggling public status:', error);
      alert('Failed to update resume visibility. Please try again.');
    }
  };

  const handleCopyShareLink = async (resume: Resume) => {
    if (!resume.is_public || !resume.public_url_slug) {
      alert('This resume must be public to generate a share link.');
      return;
    }

    const shareUrl = `${window.location.origin}/public/resume/${resume.public_url_slug}`;

    try {
      await navigator.clipboard.writeText(shareUrl);
      alert('Share link copied to clipboard!');
    } catch (error) {
      console.error('Error copying link:', error);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = shareUrl;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      alert('Share link copied to clipboard!');
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
          <Button onClick={() => window.location.reload()}>Try Again</Button>
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
            <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
              Resume Builder
            </h1>
            <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
              Create and manage professional resumes in Japanese and international formats
            </p>
          </div>
          <Link href="/resumes/create">
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Create Resume
            </Button>
          </Link>
        </div>

        {/* Resume Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6 text-center">
            <div className="text-2xl font-bold" style={{ color: 'var(--brand-primary)' }}>
              {resumes.length}
            </div>
            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Total Resumes
            </div>
          </Card>
          <Card className="p-6 text-center">
            <div className="text-2xl font-bold text-green-600">
              {resumes.filter((r) => r.status === 'published').length}
            </div>
            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Published
            </div>
          </Card>
          <Card className="p-6 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {resumes.reduce((sum, r) => sum + (r.view_count || 0), 0)}
            </div>
            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Total Views
            </div>
          </Card>
          <Card className="p-6 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {resumes.reduce((sum, r) => sum + (r.download_count || 0), 0)}
            </div>
            <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Downloads
            </div>
          </Card>
        </div>

        {/* Resumes Grid */}
        {resumes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resumes.map((resume) => (
              <Card key={resume.id} className="p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-2 flex-wrap">
                    <FileText className="h-5 w-5" style={{ color: 'var(--brand-primary)' }} />
                    <Badge variant={getStatusColor(resume.status)}>{resume.status}</Badge>
                    {resume.resume_format && (
                      <Badge variant={getFormatColor(resume.resume_format)}>
                        {getFormatDisplayName(resume.resume_format)}
                      </Badge>
                    )}
                    {resume.is_public && (
                      <Badge variant="secondary">
                        <Globe className="h-3 w-3 mr-1" />
                        Public
                      </Badge>
                    )}
                    {resume.is_primary && (
                      <Badge variant="warning">
                        <Star className="h-3 w-3 mr-1" />
                        Primary
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleTogglePublic(resume)}
                      title={resume.is_public ? 'Make Private' : 'Make Public'}
                    >
                      {resume.is_public ? (
                        <Lock className="h-4 w-4" />
                      ) : (
                        <Globe className="h-4 w-4" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(resume.id)}
                      disabled={!resume.can_delete}
                      title="Delete Resume"
                    >
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
                      {resume.full_name && <span className="font-medium">{resume.full_name}</span>}
                      {resume.description && <span className="block">{resume.description}</span>}
                    </p>
                  </div>

                  <div
                    className="flex items-center justify-between text-sm"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>Updated {formatDate(resume.updated_at)}</span>
                    </div>
                    <span>{getVisibilityText(resume.visibility)}</span>
                  </div>

                  <div
                    className="flex items-center justify-between text-sm"
                    style={{ color: 'var(--text-secondary)' }}
                  >
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
                    <Link href={`/resumes/${resume.id}/edit`} className="flex-1">
                      <Button size="sm" className="w-full">
                        <Edit className="h-4 w-4 mr-2" />
                        Edit
                      </Button>
                    </Link>
                    <Link href={`/resumes/${resume.id}/preview`} className="flex-1">
                      <Button variant="outline" size="sm" className="w-full">
                        <Eye className="h-4 w-4 mr-2" />
                        Preview
                      </Button>
                    </Link>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDownloadPdf(resume)}
                      disabled={generatingPdf === resume.id || !resume.can_download_pdf}
                      title="Download PDF"
                    >
                      {generatingPdf === resume.id ? (
                        <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                      ) : (
                        <Download className="h-4 w-4" />
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleCopyShareLink(resume)}
                      disabled={!resume.is_public}
                      title="Copy Share Link"
                    >
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
              No resumes yet
            </h3>
            <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>
              Create professional resumes in multiple formats including Japanese 履歴書 and
              職務経歴書, or international formats. Generate PDFs, share publicly, and manage all
              your career documents in one place.
            </p>
            <div className="flex flex-wrap justify-center gap-3 mb-6">
              <Badge variant="primary">履歴書 (Rirekisho)</Badge>
              <Badge variant="success">職務経歴書 (Shokumu)</Badge>
              <Badge variant="warning">International</Badge>
              <Badge variant="secondary">Modern</Badge>
            </div>
            <Link href="/resumes/create">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Your First Resume
              </Button>
            </Link>
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
