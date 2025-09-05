'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { 
  ArrowLeft, 
  Download, 
  Edit, 
  Share, 
  Eye,
  Mail,
  Phone,
  MapPin,
  Globe,
  Github,
  Linkedin,
  Calendar,
  Building
} from 'lucide-react';
import type { Resume } from '@/types';

export default function ResumePreviewPage() {
  const { user } = useAuth();
  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(true);

  // Mock resume data for preview
  const mockResume: Resume = {
    id: '1',
    title: 'Senior Frontend Developer Resume',
    description: 'Comprehensive resume for senior frontend positions with React and TypeScript experience',
    template_id: 'modern',
    personal_info: {
      full_name: 'John Doe',
      email: 'john.doe@example.com',
      phone: '+1 (555) 123-4567',
      address: 'San Francisco, CA',
      linkedin: 'linkedin.com/in/johndoe',
      website: 'johndoe.dev',
      github: 'github.com/johndoe'
    },
    experience: [
      {
        company: 'TechCorp Inc.',
        position: 'Senior Frontend Developer',
        start_date: '2022-01',
        end_date: null,
        description: 'Led development of React-based applications with TypeScript, mentored junior developers, and improved application performance by 40%. Collaborated with cross-functional teams to deliver high-quality user experiences.',
        location: 'San Francisco, CA'
      },
      {
        company: 'StartupCo',
        position: 'Frontend Developer',
        start_date: '2020-03',
        end_date: '2021-12',
        description: 'Developed responsive web applications using React, Redux, and modern CSS frameworks. Implemented component libraries and design systems that reduced development time by 30%.',
        location: 'Remote'
      },
      {
        company: 'WebAgency',
        position: 'Junior Developer',
        start_date: '2019-06',
        end_date: '2020-02',
        description: 'Built client websites using HTML, CSS, JavaScript, and WordPress. Gained experience with modern development workflows and agile methodologies.',
        location: 'New York, NY'
      }
    ],
    education: [
      {
        institution: 'University of California, Berkeley',
        degree: 'Bachelor of Science in Computer Science',
        start_date: '2016-09',
        end_date: '2020-05',
        gpa: '3.8',
        location: 'Berkeley, CA'
      }
    ],
    skills: [
      'React', 'TypeScript', 'JavaScript', 'Node.js', 'Python', 'AWS', 
      'Docker', 'GraphQL', 'Redux', 'Next.js', 'Tailwind CSS', 'Git',
      'Jest', 'Cypress', 'Webpack', 'MongoDB', 'PostgreSQL'
    ],
    certifications: [
      {
        name: 'AWS Certified Developer - Associate',
        issuer: 'Amazon Web Services',
        date: '2023-06',
        credential_id: 'AWS-12345'
      },
      {
        name: 'React Developer Certification',
        issuer: 'Meta',
        date: '2022-11',
        credential_id: 'META-67890'
      }
    ],
    projects: [
      {
        name: 'E-commerce Platform',
        description: 'Built a full-stack e-commerce platform using React, Node.js, and PostgreSQL with features like payment processing, inventory management, and real-time notifications.',
        technologies: ['React', 'Node.js', 'PostgreSQL', 'Stripe', 'Socket.io'],
        url: 'https://github.com/johndoe/ecommerce'
      },
      {
        name: 'Task Management App',
        description: 'Developed a collaborative task management application with real-time updates, drag-and-drop functionality, and team collaboration features.',
        technologies: ['React', 'TypeScript', 'MongoDB', 'Express', 'Socket.io'],
        url: 'https://taskapp.dev'
      }
    ],
    languages: [
      { name: 'English', proficiency: 'native' },
      { name: 'Spanish', proficiency: 'intermediate' },
      { name: 'French', proficiency: 'beginner' }
    ],
    is_primary: true,
    is_public: false,
    created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    user_id: user?.id || '1'
  };

  useEffect(() => {
    // Simulate loading resume data
    setTimeout(() => {
      setResume(mockResume);
      setLoading(false);
    }, 1000);
  }, []);

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Present';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  };

  const getLanguageProficiency = (proficiency: string) => {
    switch (proficiency) {
      case 'native':
        return 'Native';
      case 'fluent':
        return 'Fluent';
      case 'intermediate':
        return 'Intermediate';
      case 'beginner':
        return 'Beginner';
      default:
        return proficiency;
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
        <div className="p-6">
          <div className="text-center py-16">
            <h1 className="text-2xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
              Resume not found
            </h1>
            <Button>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Resumes
            </Button>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Resumes
            </Button>
            <div>
              <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                {resume.title}
              </h1>
              <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
                Preview your resume before downloading or sharing
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="outline">
              <Edit className="h-4 w-4 mr-2" />
              Edit Resume
            </Button>
            <Button variant="outline">
              <Share className="h-4 w-4 mr-2" />
              Share
            </Button>
            <Button>
              <Download className="h-4 w-4 mr-2" />
              Download PDF
            </Button>
          </div>
        </div>

        {/* Resume Preview */}
        <div className="max-w-4xl mx-auto">
          <Card className="p-8 bg-white shadow-lg">
            {/* Personal Information Header */}
            <div className="border-b border-gray-200 pb-6 mb-8">
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                {resume.personal_info.full_name}
              </h1>
              
              <div className="flex flex-wrap items-center gap-4 text-gray-600">
                {resume.personal_info.email && (
                  <div className="flex items-center gap-1">
                    <Mail className="h-4 w-4" />
                    <span>{resume.personal_info.email}</span>
                  </div>
                )}
                {resume.personal_info.phone && (
                  <div className="flex items-center gap-1">
                    <Phone className="h-4 w-4" />
                    <span>{resume.personal_info.phone}</span>
                  </div>
                )}
                {resume.personal_info.address && (
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    <span>{resume.personal_info.address}</span>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-4 mt-2 text-gray-600">
                {resume.personal_info.website && (
                  <div className="flex items-center gap-1">
                    <Globe className="h-4 w-4" />
                    <a href={`https://${resume.personal_info.website}`} className="hover:underline">
                      {resume.personal_info.website}
                    </a>
                  </div>
                )}
                {resume.personal_info.linkedin && (
                  <div className="flex items-center gap-1">
                    <Linkedin className="h-4 w-4" />
                    <a href={`https://${resume.personal_info.linkedin}`} className="hover:underline">
                      LinkedIn
                    </a>
                  </div>
                )}
                {resume.personal_info.github && (
                  <div className="flex items-center gap-1">
                    <Github className="h-4 w-4" />
                    <a href={`https://${resume.personal_info.github}`} className="hover:underline">
                      GitHub
                    </a>
                  </div>
                )}
              </div>
            </div>

            {/* Experience Section */}
            {resume.experience && resume.experience.length > 0 && (
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Building className="h-6 w-6" />
                  Work Experience
                </h2>
                <div className="space-y-6">
                  {resume.experience.map((exp, index) => (
                    <div key={index} className="border-l-2 border-blue-500 pl-6 relative">
                      <div className="absolute -left-2 top-0 w-4 h-4 bg-blue-500 rounded-full"></div>
                      <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                        <div>
                          <h3 className="text-xl font-semibold text-gray-900">{exp.position}</h3>
                          <p className="text-lg text-blue-600 font-medium">{exp.company}</p>
                        </div>
                        <div className="text-right text-gray-600">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4" />
                            <span>{formatDate(exp.start_date)} - {formatDate(exp.end_date)}</span>
                          </div>
                          {exp.location && (
                            <div className="flex items-center gap-1 mt-1">
                              <MapPin className="h-4 w-4" />
                              <span>{exp.location}</span>
                            </div>
                          )}
                        </div>
                      </div>
                      <p className="text-gray-700 leading-relaxed">{exp.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Education Section */}
            {resume.education && resume.education.length > 0 && (
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Education</h2>
                <div className="space-y-4">
                  {resume.education.map((edu, index) => (
                    <div key={index} className="flex flex-wrap items-start justify-between gap-2">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{edu.degree}</h3>
                        <p className="text-blue-600 font-medium">{edu.institution}</p>
                        {edu.location && <p className="text-gray-600">{edu.location}</p>}
                      </div>
                      <div className="text-right text-gray-600">
                        <p>{formatDate(edu.start_date)} - {formatDate(edu.end_date)}</p>
                        {edu.gpa && <p>GPA: {edu.gpa}</p>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Skills Section */}
            {resume.skills && resume.skills.length > 0 && (
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Skills</h2>
                <div className="flex flex-wrap gap-2">
                  {resume.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Projects Section */}
            {resume.projects && resume.projects.length > 0 && (
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Projects</h2>
                <div className="space-y-4">
                  {resume.projects.map((project, index) => (
                    <div key={index}>
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{project.name}</h3>
                        {project.url && (
                          <a
                            href={project.url}
                            className="text-blue-600 hover:underline text-sm"
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            View Project
                          </a>
                        )}
                      </div>
                      <p className="text-gray-700 mb-2">{project.description}</p>
                      <div className="flex flex-wrap gap-1">
                        {project.technologies?.map((tech, techIndex) => (
                          <span
                            key={techIndex}
                            className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Certifications Section */}
            {resume.certifications && resume.certifications.length > 0 && (
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Certifications</h2>
                <div className="space-y-3">
                  {resume.certifications.map((cert, index) => (
                    <div key={index} className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="font-semibold text-gray-900">{cert.name}</h3>
                        <p className="text-blue-600">{cert.issuer}</p>
                        {cert.credential_id && (
                          <p className="text-sm text-gray-600">ID: {cert.credential_id}</p>
                        )}
                      </div>
                      <p className="text-gray-600">{formatDate(cert.date)}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Languages Section */}
            {resume.languages && resume.languages.length > 0 && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Languages</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {resume.languages.map((lang, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="font-medium text-gray-900">{lang.name}</span>
                      <span className="text-gray-600 text-sm">
                        {getLanguageProficiency(lang.proficiency)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </div>
      </div>
    </AppLayout>
  );
}