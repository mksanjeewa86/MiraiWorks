'use client';
import { PublicResumeInfo } from '@/types/resume';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import DOMPurify from 'dompurify';
import { Download, Eye, Calendar, User, Globe, Share2, ExternalLink } from 'lucide-react';
import { ResumeFormat } from '@/types/resume';
import { resumesApi } from '@/api/resumes';
import { ROUTES } from '@/routes/config';

function PublicResumePageContent() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;

  const [loading, setLoading] = useState(true);
  const [resume, setResume] = useState<PublicResumeInfo | null>(null);
  const [previewHtml, setPreviewHtml] = useState<string>('');
  const [generatingPdf, setGeneratingPdf] = useState(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    fetchPublicResume();
  }, [slug]);

  const fetchPublicResume = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await resumesApi.getPublicResume(slug);

      if (response.data) {
        setResume(response.data.resume);
        setPreviewHtml(response.data.html);

        // Track view
        try {
          await resumesApi.trackPublicView(slug);
        } catch (error) {
          // Ignore view tracking errors
        }
      }
    } catch (error: any) {
      console.error('Error fetching public resume:', error);
      if (error.response?.status === 404) {
        setError('Resume not found');
      } else if (error.response?.status === 403) {
        setError('Resume is private');
      } else {
        setError('Failed to load resume');
      }
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

      const response = await resumesApi.downloadPublicPdf(slug);

      // Create download link
      const link = document.createElement('a');
      link.href = response.data?.pdf_url || '';
      link.download = `${resume.title}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to download PDF. Please try again.');
    } finally {
      setGeneratingPdf(false);
    }
  };

  const handleShare = async () => {
    const currentUrl = window.location.href;

    try {
      await navigator.clipboard.writeText(currentUrl);
      alert('Resume link copied to clipboard!');
    } catch (error) {
      console.error('Error copying link:', error);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = currentUrl;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      alert('Resume link copied to clipboard!');
    }
  };

  const getFormatDisplayName = (format: ResumeFormat) => {
    switch (format) {
      case ResumeFormat.RIREKISHO:
        return 'Rirekisho';
      case ResumeFormat.SHOKUMU_KEIREKISHO:
        return 'Shokumu Keirekisho';
      case ResumeFormat.INTERNATIONAL:
        return 'International Resume';
      case ResumeFormat.MODERN:
        return 'Modern Resume';
      default:
        return 'Resume';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="animate-spin h-12 w-12 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-gray-600">Loading resume...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !resume) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-8">
          <div className="text-6xl mb-4">
            {error === 'Resume not found'
              ? '404'
              : error === 'Resume is private'
                ? 'LOCKED'
                : 'ERROR'}
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {error === 'Resume not found'
              ? 'Resume Not Found'
              : error === 'Resume is private'
                ? 'Resume is Private'
                : 'Error Loading Resume'}
          </h1>
          <p className="text-gray-600 mb-6">
            {error === 'Resume not found'
              ? "The resume you're looking for doesn't exist or has been removed."
              : error === 'Resume is private'
                ? 'This resume is currently private and cannot be viewed publicly.'
                : 'Something went wrong while loading this resume.'}
          </p>
          <button
            onClick={() => router.push(ROUTES.HOME)}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            Go to Homepage
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-4">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {resume.full_name || resume.title}
                </h1>
                <p className="text-sm text-gray-600">
                  {resume.resume_format && getFormatDisplayName(resume.resume_format)}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <div className="flex items-center text-sm text-gray-500">
                <Eye className="h-4 w-4 mr-1" />
                {resume.view_count} views
              </div>

              <button
                onClick={handleShare}
                className="inline-flex items-center px-3 py-2 text-sm text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </button>

              {resume.can_download_pdf && (
                <button
                  onClick={handleDownloadPdf}
                  disabled={generatingPdf}
                  className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-blue-400 transition-colors"
                >
                  {generatingPdf ? (
                    <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full mr-2" />
                  ) : (
                    <Download className="h-4 w-4 mr-2" />
                  )}
                  {generatingPdf ? 'Generating...' : 'Download PDF'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Resume Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center">
              <User className="h-8 w-8 text-blue-600 mr-3" />
              <div>
                <div className="font-medium text-gray-900">Owner</div>
                <div className="text-sm text-gray-600">{resume.full_name || 'Anonymous'}</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center">
              <Globe className="h-8 w-8 text-green-600 mr-3" />
              <div>
                <div className="font-medium text-gray-900">Format</div>
                <div className="text-sm text-gray-600">
                  {resume.resume_format ? getFormatDisplayName(resume.resume_format) : 'N/A'}
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-sm">
            <div className="flex items-center">
              <Calendar className="h-8 w-8 text-purple-600 mr-3" />
              <div>
                <div className="font-medium text-gray-900">Last Updated</div>
                <div className="text-sm text-gray-600">
                  {resume.last_viewed_at
                    ? new Date(resume.last_viewed_at).toLocaleDateString()
                    : 'Recently'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Professional Summary */}
        {resume.professional_summary && (
          <div className="bg-white rounded-lg p-6 shadow-sm mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Professional Summary</h2>
            <p className="text-gray-700 leading-relaxed">{resume.professional_summary}</p>
          </div>
        )}

        {/* Resume Preview */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="border-b bg-gray-50 px-6 py-4">
            <h2 className="text-lg font-semibold text-gray-900">Resume</h2>
            <p className="text-sm text-gray-600">
              Public view - {resume.can_download_pdf ? 'Download available' : 'View only'}
            </p>
          </div>

          <div className="bg-white">
            {previewHtml ? (
              <div
                className="resume-preview-public"
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(previewHtml, {
                    ALLOWED_TAGS: ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'strong', 'em', 'br', 'section', 'article', 'header', 'footer', 'table', 'thead', 'tbody', 'tr', 'th', 'td'],
                    ALLOWED_ATTR: ['class', 'style', 'id'],
                    ALLOW_DATA_ATTR: false,
                  }),
                }}
                style={{
                  fontFamily: (resume as any).font_family || 'Inter',
                  ['--theme-color' as any]: (resume as any).theme_color || '#2563eb',
                }}
              />
            ) : (
              <div className="p-12 text-center">
                <div className="animate-spin h-8 w-8 border-4 border-gray-300 border-t-blue-600 rounded-full mx-auto mb-4"></div>
                <p className="text-gray-600">Loading resume content...</p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center text-sm text-gray-500">
            <Globe className="h-4 w-4 mr-2" />
            Powered by MiraiWorks Resume Builder
          </div>
          <div className="mt-2">
            <a
              href={ROUTES.HOME}
              className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700"
            >
              Create your own resume
              <ExternalLink className="h-3 w-3 ml-1" />
            </a>
          </div>
        </div>
      </div>

      <style jsx global>{`
        .resume-preview-public {
          max-width: 210mm;
          margin: 20px auto;
          background: white;
          padding: 20px;
          box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
          min-height: 297mm;
          border-radius: 8px;
        }

        .resume-preview-public img {
          max-width: 100%;
          height: auto;
        }

        .resume-preview-public table {
          width: 100%;
          border-collapse: collapse;
          margin: 15px 0;
        }

        .resume-preview-public td,
        .resume-preview-public th {
          border: 1px solid #ddd;
          padding: 12px 8px;
          vertical-align: top;
        }

        .resume-preview-public h1,
        .resume-preview-public h2,
        .resume-preview-public h3 {
          color: var(--theme-color, #2563eb);
        }

        .resume-preview-public .section-title {
          color: var(--theme-color, #2563eb);
          border-bottom: 2px solid var(--theme-color, #2563eb);
        }

        @media (max-width: 768px) {
          .resume-preview-public {
            margin: 10px;
            padding: 15px;
            box-shadow: none;
            border: 1px solid #e5e7eb;
          }
        }

        @media print {
          .resume-preview-public {
            box-shadow: none;
            margin: 0;
            padding: 0;
            max-width: none;
            border-radius: 0;
          }

          .bg-gray-50,
          .bg-white {
            background: white !important;
          }

          .shadow-sm {
            box-shadow: none !important;
          }
        }
      `}</style>
    </div>
  );
}

export default function PublicResumePage() {
  return <PublicResumePageContent />;
}
