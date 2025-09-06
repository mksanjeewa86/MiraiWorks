'use client';

import { Suspense, useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { 
  ArrowLeft, 
  Download, 
  Edit, 
  Share, 
  Mail,
  Phone,
  MapPin,
  Globe,
  Github,
  Linkedin,
  Calendar,
  Building
} from 'lucide-react';
import { resumesApi } from '@/services/api';
import type { Resume, Education, Skill } from '@/types';

function ResumePreviewContent() {
  const searchParams = useSearchParams();
  const resumeId = searchParams.get('id');
  
  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchResume = async () => {
      if (!resumeId) {
        setError('No resume ID provided');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError('');
        
        const response = await resumesApi.getById(parseInt(resumeId));
        setResume(response.data || null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load resume');
        console.error('Failed to fetch resume:', err);
        setResume(null);
      } finally {
        setLoading(false);
      }
    };

    fetchResume();
  }, [resumeId]);

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Present';
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'long',
      year: 'numeric'
    });
  };

  const handleDownload = async () => {
    if (!resume) return;
    
    try {
      // In a real implementation, this would generate/download a PDF
      console.log('Downloading resume:', resume.id);
      alert('Download functionality would be implemented here');
    } catch (err) {
      console.error('Failed to download resume:', err);
      alert('Failed to download resume');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner className="w-8 h-8" />
      </div>
    );
  }

  if (error || !resume) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="text-6xl mb-4">❌</div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">Error Loading Resume</h3>
        <p className="text-red-600 mb-6">{error || 'Resume not found'}</p>
        <Button onClick={() => window.location.reload()}>
          Try Again
        </Button>
      </div>
    );
  }

  return (
      <div className="p-6">
        {/* Header Actions */}
        <div className="flex items-center justify-between mb-8">
          <Button variant="ghost" className="flex items-center gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Resumes
          </Button>
          
          <div className="flex items-center gap-3">
            <Button variant="outline" className="flex items-center gap-2">
              <Share className="h-4 w-4" />
              Share
            </Button>
            <Button variant="outline" className="flex items-center gap-2">
              <Edit className="h-4 w-4" />
              Edit
            </Button>
            <Button onClick={handleDownload} className="flex items-center gap-2">
              <Download className="h-4 w-4" />
              Download PDF
            </Button>
          </div>
        </div>

        <div className="max-w-4xl mx-auto">
          <Card className="p-8">
            {/* Header Section */}
            <div className="border-b border-gray-200 dark:border-gray-700 pb-8 mb-8">
              <div className="text-center mb-6">
                <h1 className="text-3xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
                  {resume.full_name || 'No Name Provided'}
                </h1>
                <p className="text-lg" style={{ color: 'var(--text-secondary)' }}>
                  {resume.professional_summary || 'No summary provided'}
                </p>
              </div>
              
              <div className="flex flex-wrap justify-center gap-6 text-sm" style={{ color: 'var(--text-secondary)' }}>
                {resume.email && (
                  <div className="flex items-center gap-2">
                    <Mail className="h-4 w-4" />
                    <a href={`mailto:${resume.email}`} className="hover:underline">
                      {resume.email}
                    </a>
                  </div>
                )}
                {resume.phone && (
                  <div className="flex items-center gap-2">
                    <Phone className="h-4 w-4" />
                    <a href={`tel:${resume.phone}`} className="hover:underline">
                      {resume.phone}
                    </a>
                  </div>
                )}
                {resume.location && (
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    <span>{resume.location}</span>
                  </div>
                )}
                {resume.website && (
                  <div className="flex items-center gap-2">
                    <Globe className="h-4 w-4" />
                    <a href={resume.website} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      Website
                    </a>
                  </div>
                )}
                {resume.linkedin_url && (
                  <div className="flex items-center gap-2">
                    <Linkedin className="h-4 w-4" />
                    <a href={resume.linkedin_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      LinkedIn
                    </a>
                  </div>
                )}
                {resume.github_url && (
                  <div className="flex items-center gap-2">
                    <Github className="h-4 w-4" />
                    <a href={resume.github_url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                      GitHub
                    </a>
                  </div>
                )}
              </div>
            </div>

            {/* Experience Section */}
            {resume.experiences && resume.experiences.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
                  Work Experience
                </h2>
                <div className="space-y-6">
                  {resume.experiences
                    .sort((a, b) => (b.displayOrder || 0) - (a.displayOrder || 0))
                    .map(exp => (
                      <div key={exp.id} className="border-l-2 border-gray-200 dark:border-gray-700 pl-6">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
                              {exp.positionTitle}
                            </h3>
                            <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                              <Building className="h-4 w-4" />
                              <span>{exp.companyName}</span>
                              {exp.location && (
                                <>
                                  <span>•</span>
                                  <span>{exp.location}</span>
                                </>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-muted)' }}>
                            <Calendar className="h-4 w-4" />
                            <span>
                              {formatDate(exp.startDate)} - {exp.isCurrent ? 'Present' : formatDate(exp.endDate)}
                            </span>
                          </div>
                        </div>
                        
                        {exp.description && (
                          <p className="text-sm mb-3" style={{ color: 'var(--text-secondary)' }}>
                            {exp.description}
                          </p>
                        )}
                        
                        {exp.achievements && exp.achievements.length > 0 && (
                          <ul className="text-sm space-y-1" style={{ color: 'var(--text-secondary)' }}>
                            {exp.achievements.map((achievement, index) => (
                              <li key={index} className="flex items-start gap-2">
                                <span className="mt-1.5 w-1.5 h-1.5 bg-gray-400 rounded-full flex-shrink-0"></span>
                                <span>{achievement}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                        
                        {exp.technologies && exp.technologies.length > 0 && (
                          <div className="flex flex-wrap gap-2 mt-3">
                            {exp.technologies.map((tech, index) => (
                              <span
                                key={index}
                                className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300"
                              >
                                {tech}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Education Section */}
            {resume.educations && resume.educations.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
                  Education
                </h2>
                <div className="space-y-4">
                  {resume.educations
                    .sort((a: Education, b: Education) => (b.displayOrder || 0) - (a.displayOrder || 0))
                    .map((edu: Education) => (
                      <div key={edu.id} className="border-l-2 border-gray-200 dark:border-gray-700 pl-6">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                              {edu.degree} {edu.fieldOfStudy && `in ${edu.fieldOfStudy}`}
                            </h3>
                            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                              {edu.institutionName}
                            </p>
                            {edu.gpa && (
                              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                                GPA: {edu.gpa}
                              </p>
                            )}
                          </div>
                          <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-muted)' }}>
                            <Calendar className="h-4 w-4" />
                            <span>
                              {formatDate(edu.startDate)} - {edu.endDate ? formatDate(edu.endDate) : 'Present'}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}

            {/* Skills Section */}
            {resume.skills && resume.skills.length > 0 && (
              <div className="mb-8">
                <h2 className="text-xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
                  Skills
                </h2>
                <div className="flex flex-wrap gap-2">
                  {resume.skills.map((skill: Skill, index: number) => (
                    <span
                      key={skill.id || index}
                      className="px-3 py-1 text-sm rounded-full bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200"
                    >
                      {skill.name}
                      {skill.proficiencyLabel && skill.proficiencyLabel !== 'intermediate' && (
                        <span className="ml-1 text-xs opacity-75">
                          ({skill.proficiencyLabel})
                        </span>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>
  );
}

export default function ResumePreviewPage() {
  return (
    <AppLayout>
      <Suspense fallback={
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner className="w-8 h-8" />
        </div>
      }>
        <ResumePreviewContent />
      </Suspense>
    </AppLayout>
  );
}