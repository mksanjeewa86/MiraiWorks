'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { Plus, FileText, Eye, Download, Edit, Trash2, Star, Calendar, Share } from 'lucide-react';
import type { Resume, User } from '@/types';

// Mock resume data - moved outside component to prevent re-creation
const createMockResumes = (user: User | null): Resume[] => [
  {
    id: 1,
    title: 'Senior Frontend Developer Resume',
    description: 'Comprehensive resume for senior frontend positions with React and TypeScript experience',
    user_id: user?.id || 1,
    template_id: 'modern',
    theme_color: '#3b82f6',
    font_family: 'Inter',
    status: 'published',
    visibility: 'private',
    slug: 'senior-frontend-developer-resume',
    share_token: 'abc123',
    view_count: 25,
    download_count: 8,
    full_name: user?.full_name || 'John Doe',
    email: user?.email || 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    linkedin_url: 'https://linkedin.com/in/johndoe',
    website: 'https://johndoe.dev',
    professional_summary: 'Experienced frontend developer with 5+ years building scalable web applications using React, TypeScript, and modern development practices.',
    experiences: [
      {
        id: 1,
        resumeId: 1,
        companyName: 'TechCorp Inc.',
        positionTitle: 'Senior Frontend Developer',
        startDate: '2022-01-01',
        endDate: undefined,
        isCurrent: true,
        description: 'Led development of React-based applications with TypeScript, mentored junior developers, and improved application performance by 40%.',
        location: 'San Francisco, CA',
        achievements: ['Improved app performance by 40%', 'Mentored 3 junior developers', 'Led migration to TypeScript'],
        technologies: ['React', 'TypeScript', 'Node.js', 'AWS'],
        isVisible: true,
        displayOrder: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      },
      {
        id: 2,
        resumeId: 1,
        companyName: 'StartupCo',
        positionTitle: 'Frontend Developer',
        startDate: '2020-03-01',
        endDate: '2021-12-31',
        isCurrent: false,
        description: 'Developed responsive web applications using React, Redux, and modern CSS frameworks.',
        location: 'Remote',
        achievements: ['Built 5 client applications', 'Implemented responsive design system'],
        technologies: ['React', 'Redux', 'CSS3', 'JavaScript'],
        isVisible: true,
        displayOrder: 2,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ],
    educations: [
      {
        id: 1,
        resumeId: 1,
        institutionName: 'University of California, Berkeley',
        degree: 'Bachelor of Science in Computer Science',
        fieldOfStudy: 'Computer Science',
        startDate: '2016-09-01',
        endDate: '2020-05-31',
        isCurrent: false,
        gpa: '3.8',
        location: 'Berkeley, CA',
        description: 'Focused on software engineering, algorithms, and data structures.',
        courses: ['Data Structures', 'Algorithms', 'Software Engineering', 'Database Systems'],
        isVisible: true,
        displayOrder: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ],
    skills: [
      { id: 1, resumeId: 1, name: 'React', category: 'Frontend', proficiencyLevel: 5, proficiencyLabel: 'Expert', isVisible: true, displayOrder: 1, createdAt: new Date().toISOString() },
      { id: 2, resumeId: 1, name: 'TypeScript', category: 'Programming Languages', proficiencyLevel: 5, proficiencyLabel: 'Expert', isVisible: true, displayOrder: 2, createdAt: new Date().toISOString() },
      { id: 3, resumeId: 1, name: 'JavaScript', category: 'Programming Languages', proficiencyLevel: 5, proficiencyLabel: 'Expert', isVisible: true, displayOrder: 3, createdAt: new Date().toISOString() },
      { id: 4, resumeId: 1, name: 'Node.js', category: 'Backend', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 4, createdAt: new Date().toISOString() },
      { id: 5, resumeId: 1, name: 'Python', category: 'Programming Languages', proficiencyLevel: 3, proficiencyLabel: 'Intermediate', isVisible: true, displayOrder: 5, createdAt: new Date().toISOString() },
      { id: 6, resumeId: 1, name: 'AWS', category: 'Cloud', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 6, createdAt: new Date().toISOString() },
      { id: 7, resumeId: 1, name: 'Docker', category: 'DevOps', proficiencyLevel: 3, proficiencyLabel: 'Intermediate', isVisible: true, displayOrder: 7, createdAt: new Date().toISOString() },
      { id: 8, resumeId: 1, name: 'GraphQL', category: 'APIs', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 8, createdAt: new Date().toISOString() }
    ],
    certifications: [
      {
        id: 1,
        resumeId: 1,
        name: 'AWS Certified Developer - Associate',
        issuingOrganization: 'Amazon Web Services',
        credentialId: 'AWS-12345',
        credentialUrl: 'https://aws.amazon.com/certification/',
        issueDate: '2023-06-01',
        expirationDate: '2026-06-01',
        doesNotExpire: false,
        description: 'Validates technical expertise in developing and maintaining applications on the AWS platform.',
        isVisible: true,
        displayOrder: 1,
        createdAt: new Date().toISOString()
      }
    ],
    projects: [
      {
        id: 1,
        resumeId: 1,
        name: 'E-commerce Platform',
        description: 'Built a full-stack e-commerce platform using React, Node.js, and PostgreSQL with features like payment processing, inventory management, and real-time notifications.',
        projectUrl: 'https://ecommerce-demo.johndoe.dev',
        githubUrl: 'https://github.com/johndoe/ecommerce',
        demoUrl: 'https://ecommerce-demo.johndoe.dev',
        startDate: '2023-01-01',
        endDate: '2023-06-30',
        isOngoing: false,
        technologies: ['React', 'Node.js', 'PostgreSQL', 'Stripe', 'Redux'],
        role: 'Full-Stack Developer',
        isVisible: true,
        displayOrder: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ],
    languages: [
      {
        id: 1,
        resumeId: 1,
        name: 'English',
        proficiency: 'native',
        isVisible: true,
        displayOrder: 1,
        createdAt: new Date().toISOString()
      },
      {
        id: 2,
        resumeId: 1,
        name: 'Spanish',
        proficiency: 'intermediate',
        isVisible: true,
        displayOrder: 2,
        createdAt: new Date().toISOString()
      }
    ],
    sections: [],
    references: [],
    is_primary: true,
    is_public: false,
    last_viewed_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    id: 2,
    title: 'Product Manager Resume',
    description: 'Product management focused resume highlighting leadership and strategy experience',
    user_id: user?.id || 1,
    template_id: 'professional',
    theme_color: '#059669',
    font_family: 'Inter',
    status: 'published',
    visibility: 'public',
    slug: 'product-manager-resume',
    share_token: 'def456',
    view_count: 42,
    download_count: 15,
    full_name: user?.full_name || 'John Doe',
    email: user?.email || 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    professional_summary: 'Strategic product manager with MBA and 3+ years experience in B2B SaaS platforms.',
    experiences: [
      {
        id: 3,
        resumeId: 2,
        companyName: 'Enterprise Corp',
        positionTitle: 'Associate Product Manager',
        startDate: '2021-06-01',
        endDate: '2023-12-31',
        isCurrent: false,
        description: 'Managed product roadmap for B2B SaaS platform, conducted user research, and coordinated with engineering teams.',
        location: 'San Francisco, CA',
        achievements: ['Increased user engagement by 25%', 'Led 3 successful product launches', 'Managed $2M product budget'],
        technologies: ['SQL', 'Tableau', 'Figma', 'Jira'],
        isVisible: true,
        displayOrder: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ],
    educations: [
      {
        id: 2,
        resumeId: 2,
        institutionName: 'Stanford University',
        degree: 'MBA',
        fieldOfStudy: 'Business Administration',
        startDate: '2019-09-01',
        endDate: '2021-05-31',
        isCurrent: false,
        location: 'Stanford, CA',
        description: 'Focus on product management and strategy.',
        courses: ['Product Strategy', 'Data Analytics', 'Leadership', 'Finance'],
        isVisible: true,
        displayOrder: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ],
    skills: [
      { id: 9, resumeId: 2, name: 'Product Strategy', category: 'Product Management', proficiencyLevel: 5, proficiencyLabel: 'Expert', isVisible: true, displayOrder: 1, createdAt: new Date().toISOString() },
      { id: 10, resumeId: 2, name: 'User Research', category: 'Research', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 2, createdAt: new Date().toISOString() },
      { id: 11, resumeId: 2, name: 'Agile', category: 'Methodology', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 3, createdAt: new Date().toISOString() },
      { id: 12, resumeId: 2, name: 'SQL', category: 'Data', proficiencyLevel: 3, proficiencyLabel: 'Intermediate', isVisible: true, displayOrder: 4, createdAt: new Date().toISOString() },
      { id: 13, resumeId: 2, name: 'Analytics', category: 'Data', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 5, createdAt: new Date().toISOString() },
      { id: 14, resumeId: 2, name: 'Leadership', category: 'Management', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 6, createdAt: new Date().toISOString() }
    ],
    certifications: [],
    projects: [],
    languages: [
      {
        id: 3,
        resumeId: 2,
        name: 'English',
        proficiency: 'native',
        isVisible: true,
        displayOrder: 1,
        createdAt: new Date().toISOString()
      }
    ],
    sections: [],
    references: [],
    is_primary: false,
    is_public: true,
    last_viewed_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString()
  },
  {
    id: 3,
    title: 'Full-Stack Developer Resume',
    description: 'Comprehensive full-stack development resume for diverse tech roles',
    user_id: user?.id || 1,
    template_id: 'creative',
    theme_color: '#dc2626',
    font_family: 'Inter',
    status: 'draft',
    visibility: 'private',
    slug: 'fullstack-developer-resume',
    share_token: 'ghi789',
    view_count: 18,
    download_count: 3,
    full_name: user?.full_name || 'John Doe',
    email: user?.email || 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    github_url: 'https://github.com/johndoe',
    professional_summary: 'Full-stack developer with expertise in React, Node.js, and cloud technologies. Passionate about building scalable web applications.',
    experiences: [
      {
        id: 4,
        resumeId: 3,
        companyName: 'Freelance',
        positionTitle: 'Full-Stack Developer',
        startDate: '2023-01-01',
        endDate: undefined,
        isCurrent: true,
        description: 'Developed custom web applications for various clients using modern tech stacks.',
        location: 'Remote',
        achievements: ['Completed 15+ client projects', 'Built scalable applications', 'Maintained 98% client satisfaction'],
        technologies: ['React', 'Node.js', 'MongoDB', 'AWS', 'Docker'],
        isVisible: true,
        displayOrder: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ],
    educations: [],
    skills: [
      { id: 15, resumeId: 3, name: 'React', category: 'Frontend', proficiencyLevel: 5, proficiencyLabel: 'Expert', isVisible: true, displayOrder: 1, createdAt: new Date().toISOString() },
      { id: 16, resumeId: 3, name: 'Node.js', category: 'Backend', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 2, createdAt: new Date().toISOString() },
      { id: 17, resumeId: 3, name: 'Python', category: 'Programming Languages', proficiencyLevel: 3, proficiencyLabel: 'Intermediate', isVisible: true, displayOrder: 3, createdAt: new Date().toISOString() },
      { id: 18, resumeId: 3, name: 'PostgreSQL', category: 'Database', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 4, createdAt: new Date().toISOString() },
      { id: 19, resumeId: 3, name: 'MongoDB', category: 'Database', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 5, createdAt: new Date().toISOString() },
      { id: 20, resumeId: 3, name: 'AWS', category: 'Cloud', proficiencyLevel: 3, proficiencyLabel: 'Intermediate', isVisible: true, displayOrder: 6, createdAt: new Date().toISOString() },
      { id: 21, resumeId: 3, name: 'Docker', category: 'DevOps', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 7, createdAt: new Date().toISOString() }
    ],
    certifications: [],
    projects: [
      {
        id: 2,
        resumeId: 3,
        name: 'Task Management App',
        description: 'Built a collaborative task management application with real-time updates, user authentication, and team collaboration features.',
        projectUrl: 'https://taskapp.dev',
        githubUrl: 'https://github.com/johndoe/taskapp',
        demoUrl: 'https://taskapp-demo.dev',
        startDate: '2023-03-01',
        endDate: '2023-08-31',
        isOngoing: false,
        technologies: ['React', 'Node.js', 'Socket.io', 'MongoDB', 'JWT'],
        role: 'Solo Developer',
        isVisible: true,
        displayOrder: 1,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ],
    languages: [
      {
        id: 4,
        resumeId: 3,
        name: 'English',
        proficiency: 'native',
        isVisible: true,
        displayOrder: 1,
        createdAt: new Date().toISOString()
      }
    ],
    sections: [],
    references: [],
    is_primary: false,
    is_public: false,
    last_viewed_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
  }
];

export default function ResumesPage() {
  const { user } = useAuth();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading resumes
    const mockResumes = createMockResumes(user);
    setTimeout(() => {
      setResumes(mockResumes);
      setLoading(false);
    }, 1000);
  }, [user]);

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
                      <span>{resume.experiences?.length || 0} positions</span>
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