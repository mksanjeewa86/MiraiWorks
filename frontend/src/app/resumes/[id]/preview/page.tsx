'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import DOMPurify from 'dompurify';
import AppLayout from '@/components/layout/AppLayout';
import { Card } from '@/components/ui';
import { Button } from '@/components/ui';
import { LoadingSpinner } from '@/components/ui';
import {
  ArrowLeft,
  Download,
  Edit,
  Share2,
  Eye,
  Globe,
  FileText,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
  RotateCcw,
  Printer,
} from 'lucide-react';
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

  // Enhanced preview controls
  const [zoomLevel, setZoomLevel] = useState(100);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showPreviewControls, setShowPreviewControls] = useState(true);
  const [previewMode, setPreviewMode] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');

  useEffect(() => {
    fetchResume();
    fetchPreview();
  }, [resumeId]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Only handle shortcuts when not typing in inputs
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key) {
        case 'f':
        case 'F':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            toggleFullscreen();
          }
          break;
        case '+':
        case '=':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            handleZoomIn();
          }
          break;
        case '-':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            handleZoomOut();
          }
          break;
        case '0':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            handleResetZoom();
          }
          break;
        case 'Escape':
          if (isFullscreen) {
            setIsFullscreen(false);
          }
          break;
        case 'p':
        case 'P':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            handlePrint();
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isFullscreen, zoomLevel]);

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

  // Enhanced preview control functions
  const handleZoomIn = () => {
    setZoomLevel((prev) => Math.min(prev + 25, 200));
  };

  const handleZoomOut = () => {
    setZoomLevel((prev) => Math.max(prev - 25, 50));
  };

  const handleResetZoom = () => {
    setZoomLevel(100);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  const handlePrint = () => {
    window.print();
  };

  const getPreviewModeStyles = () => {
    switch (previewMode) {
      case 'tablet':
        return { maxWidth: '768px', margin: '0 auto' };
      case 'mobile':
        return { maxWidth: '375px', margin: '0 auto' };
      default:
        return { maxWidth: '210mm', margin: '0 auto' };
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
            <Button variant="outline" onClick={handlePrint}>
              <Printer className="h-4 w-4 mr-2" />
              Print
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

        {/* Enhanced Preview Controls */}
        {showPreviewControls && (
          <Card className="p-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-700">Zoom:</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleZoomOut}
                    disabled={zoomLevel <= 50}
                  >
                    <ZoomOut className="h-4 w-4" />
                  </Button>
                  <span className="text-sm font-mono w-12 text-center">{zoomLevel}%</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleZoomIn}
                    disabled={zoomLevel >= 200}
                  >
                    <ZoomIn className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="sm" onClick={handleResetZoom}>
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                </div>

                <div className="flex items-center gap-2 border-l pl-4">
                  <span className="text-sm font-medium text-gray-700">View:</span>
                  <select
                    value={previewMode}
                    onChange={(e) =>
                      setPreviewMode(e.target.value as 'desktop' | 'tablet' | 'mobile')
                    }
                    className="text-sm border rounded px-2 py-1"
                  >
                    <option value="desktop">Desktop</option>
                    <option value="tablet">Tablet</option>
                    <option value="mobile">Mobile</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <div className="relative group">
                  <Button variant="ghost" size="sm" className="text-gray-500">
                    ⌨️ Shortcuts
                  </Button>
                  <div className="absolute top-full right-0 mt-2 w-64 bg-black text-white text-xs rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                    <div className="space-y-1">
                      <div>
                        <kbd className="bg-gray-700 px-1 rounded">Ctrl+F</kbd> - Toggle Fullscreen
                      </div>
                      <div>
                        <kbd className="bg-gray-700 px-1 rounded">Ctrl/Cmd + +</kbd> - Zoom In
                      </div>
                      <div>
                        <kbd className="bg-gray-700 px-1 rounded">Ctrl/Cmd + -</kbd> - Zoom Out
                      </div>
                      <div>
                        <kbd className="bg-gray-700 px-1 rounded">Ctrl/Cmd + 0</kbd> - Reset Zoom
                      </div>
                      <div>
                        <kbd className="bg-gray-700 px-1 rounded">Ctrl/Cmd + P</kbd> - Print
                      </div>
                      <div>
                        <kbd className="bg-gray-700 px-1 rounded">Esc</kbd> - Exit Fullscreen
                      </div>
                    </div>
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={toggleFullscreen}>
                  {isFullscreen ? (
                    <Minimize2 className="h-4 w-4" />
                  ) : (
                    <Maximize2 className="h-4 w-4" />
                  )}
                  {isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowPreviewControls(false)}
                  className="text-gray-500"
                >
                  Hide Controls
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Show Controls Button when hidden */}
        {!showPreviewControls && (
          <div className="mb-6 text-center">
            <Button variant="outline" size="sm" onClick={() => setShowPreviewControls(true)}>
              Show Preview Controls
            </Button>
          </div>
        )}

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

        {/* Enhanced Preview */}
        <Card
          className={`p-0 overflow-hidden ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : ''}`}
        >
          <div className="bg-gray-100 p-4 border-b">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                  Preview
                </h2>
                <p className="text-sm text-gray-600">
                  This is how your resume will appear when viewed or downloaded as PDF
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <span>Zoom: {zoomLevel}%</span>
                <span>•</span>
                <span>View: {previewMode}</span>
              </div>
            </div>
          </div>

          <div className={`bg-white ${isFullscreen ? 'h-screen overflow-auto' : ''}`}>
            {previewHtml ? (
              <div className="p-4">
                <div
                  className="resume-preview transition-transform duration-200"
                  dangerouslySetInnerHTML={{
                    __html: DOMPurify.sanitize(previewHtml, {
                      ALLOWED_TAGS: ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'strong', 'em', 'br', 'section', 'article', 'header', 'footer', 'table', 'thead', 'tbody', 'tr', 'th', 'td'],
                      ALLOWED_ATTR: ['class', 'style', 'id'],
                      ALLOW_DATA_ATTR: false,
                    }),
                  }}
                  style={{
                    fontFamily: resume.font_family || 'Inter',
                    ['--theme-color' as any]: resume.theme_color || '#2563eb',
                    transform: `scale(${zoomLevel / 100})`,
                    transformOrigin: 'top center',
                    ...getPreviewModeStyles(),
                  }}
                />
              </div>
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
          background: white;
          box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
          min-height: 297mm;
          border-radius: 8px;
          overflow: hidden;
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

        /* Enhanced responsive styles */
        @media (max-width: 768px) {
          .resume-preview {
            min-height: auto;
            box-shadow: none;
            border-radius: 0;
          }
        }

        /* Print styles */
        @media print {
          .resume-preview {
            box-shadow: none;
            margin: 0;
            max-width: none;
            transform: none !important;
          }

          /* Hide controls when printing */
          [class*='Button'],
          [class*='Card']:not(.resume-preview) {
            display: none !important;
          }
        }

        /* Fullscreen styles */
        .fixed.inset-0 {
          background: white;
        }

        /* Smooth transitions */
        .transition-transform {
          transition: transform 0.2s ease;
        }

        /* Preview mode specific styles */
        .resume-preview.mobile-preview {
          max-width: 375px;
          font-size: 14px;
        }

        .resume-preview.tablet-preview {
          max-width: 768px;
          font-size: 15px;
        }

        .resume-preview.desktop-preview {
          max-width: 210mm;
          font-size: 16px;
        }

        /* Zoom-specific adjustments */
        .resume-preview[style*='scale(0.5)'] {
          margin-bottom: -50%;
        }

        .resume-preview[style*='scale(0.75)'] {
          margin-bottom: -25%;
        }

        .resume-preview[style*='scale(1.25)'] {
          margin-bottom: 25%;
        }

        .resume-preview[style*='scale(1.5)'] {
          margin-bottom: 50%;
        }

        .resume-preview[style*='scale(1.75)'] {
          margin-bottom: 75%;
        }

        .resume-preview[style*='scale(2)'] {
          margin-bottom: 100%;
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
