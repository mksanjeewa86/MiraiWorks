'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Plus, FileText, Eye, Download, Edit, Trash2, Star, Calendar, Share } from 'lucide-react';
import type { Resume } from '@/types';

export default function ResumesPage() {
  const { user } = useAuth();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);

  // Mock resume data
  const mockResumes: Resume[] = [
    {
      id: '1',
      title: 'Senior Frontend Developer Resume',
      description: 'Comprehensive resume for senior frontend positions with React and TypeScript experience',
      template_id: 'modern',
      personal_info: {
        full_name: user?.full_name || 'John Doe',
        email: user?.email || 'john.doe@example.com',
        phone: '+1 (555) 123-4567',
        address: 'San Francisco, CA',
        linkedin: 'linkedin.com/in/johndoe',
        website: 'johndoe.dev'
      },
      experience: [
        {
          company: 'TechCorp Inc.',
          position: 'Senior Frontend Developer',
          start_date: '2022-01',
          end_date: null,
          description: 'Led development of React-based applications with TypeScript, mentored junior developers, and improved application performance by 40%.',
          location: 'San Francisco, CA'
        },
        {
          company: 'StartupCo',
          position: 'Frontend Developer',
          start_date: '2020-03',
          end_date: '2021-12',
          description: 'Developed responsive web applications using React, Redux, and modern CSS frameworks.',
          location: 'Remote'
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
      skills: ['React', 'TypeScript', 'JavaScript', 'Node.js', 'Python', 'AWS', 'Docker', 'GraphQL'],
      certifications: [
        {
          name: 'AWS Certified Developer',
          issuer: 'Amazon Web Services',
          date: '2023-06',
          credential_id: 'AWS-12345'
        }
      ],
      projects: [
        {
          name: 'E-commerce Platform',
          description: 'Built a full-stack e-commerce platform using React, Node.js, and PostgreSQL',
          technologies: ['React', 'Node.js', 'PostgreSQL', 'Stripe'],
          url: 'https://github.com/johndoe/ecommerce'
        }
      ],
      languages: [
        { name: 'English', proficiency: 'native' },
        { name: 'Spanish', proficiency: 'intermediate' }
      ],
      is_primary: true,
      is_public: false,
      created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(), // 30 days ago
      updated_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days ago
      user_id: user?.id || '1'
    },
    {
      id: '2',
      title: 'Product Manager Resume',
      description: 'Product management focused resume highlighting leadership and strategy experience',
      template_id: 'professional',
      personal_info: {
        full_name: user?.full_name || 'John Doe',
        email: user?.email || 'john.doe@example.com',
        phone: '+1 (555) 123-4567',
        address: 'San Francisco, CA'
      },
      experience: [
        {
          company: 'Enterprise Corp',
          position: 'Associate Product Manager',
          start_date: '2021-06',
          end_date: '2023-12',
          description: 'Managed product roadmap for B2B SaaS platform, conducted user research, and coordinated with engineering teams.',
          location: 'San Francisco, CA'
        }
      ],
      education: [
        {
          institution: 'Stanford University',
          degree: 'MBA',
          start_date: '2019-09',
          end_date: '2021-05',
          location: 'Stanford, CA'
        }
      ],
      skills: ['Product Strategy', 'User Research', 'Agile', 'SQL', 'Analytics', 'Leadership'],
      certifications: [],
      projects: [],
      languages: [
        { name: 'English', proficiency: 'native' }
      ],
      is_primary: false,
      is_public: true,
      created_at: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(), // 60 days ago
      updated_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(), // 14 days ago
      user_id: user?.id || '1'
    },
    {
      id: '3',
      title: 'Full-Stack Developer Resume',
      description: 'Comprehensive full-stack development resume for diverse tech roles',
      template_id: 'creative',
      personal_info: {
        full_name: user?.full_name || 'John Doe',
        email: user?.email || 'john.doe@example.com',
        phone: '+1 (555) 123-4567',
        address: 'San Francisco, CA',
        github: 'github.com/johndoe'
      },
      experience: [
        {
          company: 'Freelance',
          position: 'Full-Stack Developer',
          start_date: '2023-01',
          end_date: null,
          description: 'Developed custom web applications for various clients using modern tech stacks.',
          location: 'Remote'
        }
      ],
      education: [],
      skills: ['React', 'Node.js', 'Python', 'PostgreSQL', 'MongoDB', 'AWS', 'Docker'],
      certifications: [],
      projects: [
        {
          name: 'Task Management App',
          description: 'Built a collaborative task management application with real-time updates',
          technologies: ['React', 'Node.js', 'Socket.io', 'MongoDB'],
          url: 'https://taskapp.dev'
        }
      ],
      languages: [
        { name: 'English', proficiency: 'native' }
      ],
      is_primary: false,
      is_public: false,
      created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(), // 15 days ago
      updated_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days ago
      user_id: user?.id || '1'
    }
  ];

  useEffect(() => {
    // Simulate loading resumes
    setTimeout(() => {
      setResumes(mockResumes);
      setLoading(false);
    }, 1000);
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getTemplateColor = (templateId: string) => {
    switch (templateId) {
      case 'modern':
        return 'primary';
      case 'professional':
        return 'success';
      case 'creative':
        return 'warning';
      default:
        return 'secondary';
    }
  };

  const getTemplateDisplayName = (templateId: string) => {
    switch (templateId) {
      case 'modern':
        return 'Modern';
      case 'professional':
        return 'Professional';
      case 'creative':
        return 'Creative';
      default:
        return templateId;
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

  return (
    <AppLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>My Resumes</h1>
            <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
              Create, manage, and share your professional resumes
            </p>
          </div>
          <Button className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Create New Resume
          </Button>
        </div>

        {/* Resume Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--brand-primary)', opacity: 0.1 }}>
                <FileText className="h-6 w-6" style={{ color: 'var(--brand-primary)' }} />
              </div>
              <div>
                <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>{resumes.length}</p>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Total Resumes</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--brand-primary)', opacity: 0.1 }}>
                <Star className="h-6 w-6" style={{ color: 'var(--brand-primary)' }} />
              </div>
              <div>
                <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                  {resumes.filter(r => r.is_primary).length}
                </p>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Primary Resume</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--brand-primary)', opacity: 0.1 }}>
                <Share className="h-6 w-6" style={{ color: 'var(--brand-primary)' }} />
              </div>
              <div>
                <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                  {resumes.filter(r => r.is_public).length}
                </p>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Public Resumes</p>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-lg" style={{ backgroundColor: 'var(--brand-primary)', opacity: 0.1 }}>
                <Calendar className="h-6 w-6" style={{ color: 'var(--brand-primary)' }} />
              </div>
              <div>
                <p className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                  {resumes.filter(r => {
                    const updatedDate = new Date(r.updated_at);
                    const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
                    return updatedDate > weekAgo;
                  }).length}
                </p>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Recent Updates</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Resume Grid */}
        {resumes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {resumes.map(resume => (
              <Card key={resume.id} className="p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Badge variant={getTemplateColor(resume.template_id)}>
                      {getTemplateDisplayName(resume.template_id)}
                    </Badge>
                    {resume.is_primary && (
                      <Badge variant="success">
                        <Star className="h-3 w-3 mr-1" />
                        Primary
                      </Badge>
                    )}
                  </div>
                  {resume.is_public && (
                    <Badge variant="secondary">
                      <Share className="h-3 w-3 mr-1" />
                      Public
                    </Badge>
                  )}
                </div>

                <div className="space-y-3">
                  <div>
                    <h3 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
                      {resume.title}
                    </h3>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                      {resume.description}
                    </p>
                  </div>

                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between" style={{ color: 'var(--text-secondary)' }}>
                      <span>Created:</span>
                      <span>{formatDate(resume.created_at)}</span>
                    </div>
                    <div className="flex items-center justify-between" style={{ color: 'var(--text-secondary)' }}>
                      <span>Updated:</span>
                      <span>{formatDate(resume.updated_at)}</span>
                    </div>
                    <div className="flex items-center justify-between" style={{ color: 'var(--text-secondary)' }}>
                      <span>Experience:</span>
                      <span>{resume.experience?.length || 0} positions</span>
                    </div>
                    <div className="flex items-center justify-between" style={{ color: 'var(--text-secondary)' }}>
                      <span>Skills:</span>
                      <span>{resume.skills?.length || 0} skills</span>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Eye className="h-4 w-4 mr-1" />
                      Preview
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1">
                      <Edit className="h-4 w-4 mr-1" />
                      Edit
                    </Button>
                  </div>

                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Download className="h-4 w-4 mr-1" />
                      Download PDF
                    </Button>
                    <Button variant="outline" size="sm">
                      <Trash2 className="h-4 w-4" />
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
              Create your first professional resume to get started with job applications.
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