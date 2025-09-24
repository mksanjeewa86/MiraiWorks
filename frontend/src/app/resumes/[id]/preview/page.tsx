'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/card';
import Button from '@/components/ui/button';
import LoadingSpinner from '@/components/ui/loading-spinner';
import { ArrowLeft, Download, Edit, Share2, Eye, Globe, FileText } from 'lucide-react';
import { Resume, ResumeFormat } from '@/types/resume';
import { resumesApi } from '@/api/resumes';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

function PreviewResumePageContent() {
  const router = useRouter();
  const params = useParams();
  const resumeId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [resume, setResume] = useState<Resume | null>(null);
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [generatingPdf, setGeneratingPdf] = useState(false);

  useEffect(() => {
    fetchResume();
    fetchPreview();
  }, [resumeId]);

  const fetchResume = async () => {
    try {
      const response = await resumesApi.getById(parseInt(resumeId));
      if (response.data) {
        setResume(response.data);
      }
    } catch (error) {
      console.error('Error fetching resume:', error);
      alert('Failed to load resume. Please try again.');
      router.push('/resumes');
    }
  };

  const fetchPreview = async () => {
    try {
      const response = await resumesApi.getPreview(parseInt(resumeId));
      if (response.data) {
        setPreviewHtml(response.data);
      }
    } catch (error) {
      console.error('Error fetching preview:', error);
      setPreviewHtml('<div class="p-8 text-center">Failed to load preview</div>');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!resume?.can_download_pdf) {
      alert('PDF download is not available for this resume.');
      return;
    }

    try {
      setGeneratingPdf(true);

      const response = await resumesApi.generatePdf(parseInt(resumeId), {
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
      setGeneratingPdf(false);
    }
  };

  const handleShare = async () => {
    if (!resume) return;

    if (!resume.is_public) {
      const makePublic = confirm(
        'This resume is currently private. Would you like to make it public to share it?'
      );

      if (makePublic) {
        try {
          const response = await resumesApi.togglePublic(parseInt(resumeId));

          if (response.data) {
            setResume(response.data);

            if (response.data.public_url_slug) {
              copyShareLink(response.data.public_url_slug);
            }
          }
        } catch (error) {
          console.error('Error making resume public:', error);
          alert('Failed to make resume public. Please try again.');
        }
      }
    } else if (resume.public_url_slug) {
      copyShareLink(resume.public_url_slug);
    }
  };

  const copyShareLink = async (slug: string) => {
    const shareUrl = `${window.location.origin}/public/resume/${slug}`;

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

  if (!resume) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center h-64">
          <div className="text-6xl mb-4">❌</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">Resume Not Found</h3>
          <p className="text-gray-600 mb-6">The resume you're looking for doesn't exist.</p>
          <Button onClick={() => router.push('/resumes')}>Back to Resumes</Button>
        </div>
      </AppLayout>
    );
  }

  const getFormatDisplayName = (format: ResumeFormat) => {
    switch (format) {
      case ResumeFormat.RIREKISHO:
        return '履歴書 (Rirekisho)';
      case ResumeFormat.SHOKUMU_KEIREKISHO:
        return '職務経歴書 (Shokumu Keirekisho)';
      case ResumeFormat.INTERNATIONAL:
        return 'International Format';
      case ResumeFormat.MODERN:
        return 'Modern Format';
      default:
        return format;
    }
  };

  return (
    <AppLayout>
      <div className="p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <Button variant="ghost" onClick={() => router.back()} className="mr-4">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                Resume Preview
              </h1>
              <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
                {resume.title} - {getFormatDisplayName(resume.resume_format)}
              </p>
            </div>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" onClick={() => router.push(`/resumes/${resumeId}/edit`)}>
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
            <Button variant="outline" onClick={handleShare}>
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
            <Button
              onClick={handleDownloadPdf}
              disabled={generatingPdf || !resume.can_download_pdf}
            >
              {generatingPdf ? (
                <div className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full mr-2" />
              ) : (
                <Download className="h-4 w-4 mr-2" />
              )}
              {generatingPdf ? 'Generating...' : 'Download PDF'}
            </Button>
          </div>
        </div>

        {/* Resume Info */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <FileText className="h-8 w-8" style={{ color: 'var(--brand-primary)' }} />
              <div>
                <div className="font-medium">Status</div>
                <div className="text-sm text-gray-600">{resume.status}</div>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center gap-3">
              {resume.is_public ? (
                <Globe className="h-8 w-8 text-green-600" />
              ) : (
                <Eye className="h-8 w-8 text-gray-400" />
              )}
              <div>
                <div className="font-medium">Visibility</div>
                <div className="text-sm text-gray-600">
                  {resume.is_public ? 'Public' : 'Private'}
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center gap-3">
              <Eye className="h-8 w-8 text-blue-600" />
              <div>
                <div className="font-medium">Views</div>
                <div className="text-sm text-gray-600">{resume.view_count || 0}</div>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center gap-3">
              <Download className="h-8 w-8 text-purple-600" />
              <div>
                <div className="font-medium">Downloads</div>
                <div className="text-sm text-gray-600">{resume.download_count || 0}</div>
              </div>
            </div>
          </Card>
        </div>

        {/* Preview */}
        <Card className="p-0 overflow-hidden">
          <div className="bg-gray-100 p-4 border-b">
            <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
              Preview
            </h2>
            <p className="text-sm text-gray-600">
              This is how your resume will appear when viewed or downloaded as PDF
            </p>
          </div>

          <div className="bg-white">
            {previewHtml ? (
              <div
                className="resume-preview"
                dangerouslySetInnerHTML={{ __html: previewHtml }}
                style={{
                  fontFamily: resume.font_family || 'Inter',
                  ['--theme-color' as any]: resume.theme_color || '#2563eb',
                }}
              />
            ) : (
              <div className="p-12 text-center">
                <LoadingSpinner className="w-8 h-8 mx-auto mb-4" />
                <p className="text-gray-600">Loading preview...</p>
              </div>
            )}
          </div>
        </Card>

        {/* Share Info */}
        {resume.is_public && resume.public_url_slug && (
          <Card className="p-6 mt-8">
            <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
              Public Share Link
            </h3>
            <div className="flex items-center gap-4">
              <div className="flex-1 bg-gray-50 p-3 rounded-md border">
                <code className="text-sm">
                  {`${window.location.origin}/public/resume/${resume.public_url_slug}`}
                </code>
              </div>
              <Button variant="outline" onClick={() => copyShareLink(resume.public_url_slug!)}>
                Copy Link
              </Button>
            </div>
            <p className="text-sm text-gray-600 mt-2">
              Anyone with this link can view your resume. To make it private, go to the edit page.
            </p>
          </Card>
        )}
      </div>

      <style jsx global>{`
        .resume-preview {
          max-width: 210mm;
          margin: 0 auto;
          background: white;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
          min-height: 297mm;
        }

        .resume-preview img {
          max-width: 100%;
          height: auto;
        }

        .resume-preview table {
          width: 100%;
          border-collapse: collapse;
        }

        .resume-preview td,
        .resume-preview th {
          border: 1px solid #000;
          padding: 8px;
          vertical-align: top;
        }

        @media print {
          .resume-preview {
            box-shadow: none;
            margin: 0;
            max-width: none;
          }
        }
      `}</style>
    </AppLayout>
  );
}

export default function PreviewResumePage() {
  return (
    <ProtectedRoute>
      <PreviewResumePageContent />
    </ProtectedRoute>
  );
}
