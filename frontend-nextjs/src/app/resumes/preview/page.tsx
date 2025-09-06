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
  Mail,
  Phone,
  MapPin,
  Globe,
  Github,
  Linkedin,
  Calendar,
  Building
} from 'lucide-react';
import type { Resume, User } from '@/types';

// Mock resume data for preview - moved outside component to prevent re-creation
const createMockResume = (user: User | null): Resume => ({
  id: 1,
  title: 'Senior Frontend Developer Resume',
  description: 'Comprehensive resume for senior frontend positions with React and TypeScript experience',
  user_id: user?.id || 1,
  template_id: 'modern',
  theme_color: '#3b82f6',
  font_family: 'Inter',
  status: 'published',
  visibility: 'private',
  slug: 'senior-frontend-developer-preview',
  share_token: 'preview123',
  view_count: 156,
  download_count: 23,
  full_name: 'John Doe',
  email: 'john.doe@example.com',
  phone: '+1 (555) 123-4567',
  location: 'San Francisco, CA',
  linkedin_url: 'https://linkedin.com/in/johndoe',
  website: 'https://johndoe.dev',
  github_url: 'https://github.com/johndoe',
  professional_summary: 'Senior Frontend Developer with 5+ years of experience building scalable web applications using React, TypeScript, and modern development practices.',
  experiences: [
    {
      id: 1,
      resumeId: 1,
      companyName: 'TechCorp Inc.',
      positionTitle: 'Senior Frontend Developer',
      startDate: '2022-01-01',
      endDate: undefined,
      isCurrent: true,
      description: 'Led development of React-based applications with TypeScript, mentored junior developers, and improved application performance by 40%. Collaborated with cross-functional teams to deliver high-quality user experiences.',
      location: 'San Francisco, CA',
      achievements: ['Improved app performance by 40%', 'Mentored 5 junior developers', 'Led migration to TypeScript'],
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
      description: 'Developed responsive web applications using React, Redux, and modern CSS frameworks. Implemented component libraries and design systems that reduced development time by 30%.',
      location: 'Remote',
      achievements: ['Reduced development time by 30%', 'Built component library', 'Implemented design system'],
      technologies: ['React', 'Redux', 'CSS3', 'JavaScript'],
      isVisible: true,
      displayOrder: 2,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    },
    {
      id: 3,
      resumeId: 1,
      companyName: 'WebAgency',
      positionTitle: 'Junior Developer',
      startDate: '2019-06-01',
      endDate: '2020-02-28',
      isCurrent: false,
      description: 'Built client websites using HTML, CSS, JavaScript, and WordPress. Gained experience with modern development workflows and agile methodologies.',
      location: 'New York, NY',
      achievements: ['Delivered 10+ client projects', 'Learned agile methodologies', 'Gained web development foundation'],
      technologies: ['HTML', 'CSS', 'JavaScript', 'WordPress'],
      isVisible: true,
      displayOrder: 3,
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
      courses: ['Data Structures', 'Algorithms', 'Software Engineering', 'Database Systems', 'Computer Networks'],
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
    { id: 8, resumeId: 1, name: 'GraphQL', category: 'APIs', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 8, createdAt: new Date().toISOString() },
    { id: 9, resumeId: 1, name: 'Redux', category: 'State Management', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 9, createdAt: new Date().toISOString() },
    { id: 10, resumeId: 1, name: 'Next.js', category: 'Frontend', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 10, createdAt: new Date().toISOString() },
    { id: 11, resumeId: 1, name: 'Tailwind CSS', category: 'CSS', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 11, createdAt: new Date().toISOString() },
    { id: 12, resumeId: 1, name: 'Git', category: 'Version Control', proficiencyLevel: 5, proficiencyLabel: 'Expert', isVisible: true, displayOrder: 12, createdAt: new Date().toISOString() },
    { id: 13, resumeId: 1, name: 'Jest', category: 'Testing', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 13, createdAt: new Date().toISOString() },
    { id: 14, resumeId: 1, name: 'Cypress', category: 'Testing', proficiencyLevel: 3, proficiencyLabel: 'Intermediate', isVisible: true, displayOrder: 14, createdAt: new Date().toISOString() },
    { id: 15, resumeId: 1, name: 'Webpack', category: 'Build Tools', proficiencyLevel: 3, proficiencyLabel: 'Intermediate', isVisible: true, displayOrder: 15, createdAt: new Date().toISOString() },
    { id: 16, resumeId: 1, name: 'MongoDB', category: 'Database', proficiencyLevel: 3, proficiencyLabel: 'Intermediate', isVisible: true, displayOrder: 16, createdAt: new Date().toISOString() },
    { id: 17, resumeId: 1, name: 'PostgreSQL', category: 'Database', proficiencyLevel: 4, proficiencyLabel: 'Advanced', isVisible: true, displayOrder: 17, createdAt: new Date().toISOString() }
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
    },
    {
      id: 2,
      resumeId: 1,
      name: 'React Developer Certification',
      issuingOrganization: 'Meta',
      credentialId: 'META-67890',
      credentialUrl: 'https://developers.facebook.com/certificate/',
      issueDate: '2022-11-01',
      expirationDate: undefined,
      doesNotExpire: true,
      description: 'Professional certification for React development skills and best practices.',
      isVisible: true,
      displayOrder: 2,
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
      endDate: '2023-08-31',
      isOngoing: false,
      technologies: ['React', 'Node.js', 'PostgreSQL', 'Stripe', 'Socket.io'],
      role: 'Full-Stack Developer',
      isVisible: true,
      displayOrder: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    },
    {
      id: 2,
      resumeId: 1,
      name: 'Task Management App',
      description: 'Developed a collaborative task management application with real-time updates, drag-and-drop functionality, and team collaboration features.',
      projectUrl: 'https://taskapp.dev',
      githubUrl: 'https://github.com/johndoe/taskapp',
      demoUrl: 'https://taskapp-demo.dev',
      startDate: '2022-09-01',
      endDate: '2022-12-31',
      isOngoing: false,
      technologies: ['React', 'TypeScript', 'MongoDB', 'Express', 'Socket.io'],
      role: 'Frontend Developer',
      isVisible: true,
      displayOrder: 2,
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
    },
    {
      id: 3,
      resumeId: 1,
      name: 'French',
      proficiency: 'beginner',
      isVisible: true,
      displayOrder: 3,
      createdAt: new Date().toISOString()
    }
  ],
  sections: [],
  references: [],
  is_primary: true,
  is_public: false,
  last_viewed_at: new Date().toISOString(),
  created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
  updated_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString()
});

export default function ResumePreviewPage() {
  const { user } = useAuth();
  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading resume data
    const mockResume = createMockResume(user);
    setTimeout(() => {
      setResume(mockResume);
      setLoading(false);
    }, 1000);
  }, [user]);

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
                {resume.full_name}
              </h1>
              
              <div className="flex flex-wrap items-center gap-4 text-gray-600">
                {resume.email && (
                  <div className="flex items-center gap-1">
                    <Mail className="h-4 w-4" />
                    <span>{resume.email}</span>
                  </div>
                )}
                {resume.phone && (
                  <div className="flex items-center gap-1">
                    <Phone className="h-4 w-4" />
                    <span>{resume.phone}</span>
                  </div>
                )}
                {resume.location && (
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    <span>{resume.location}</span>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-4 mt-2 text-gray-600">
                {resume.website && (
                  <div className="flex items-center gap-1">
                    <Globe className="h-4 w-4" />
                    <a href={resume.website} className="hover:underline">
                      {resume.website.replace('https://', '').replace('http://', '')}
                    </a>
                  </div>
                )}
                {resume.linkedin_url && (
                  <div className="flex items-center gap-1">
                    <Linkedin className="h-4 w-4" />
                    <a href={resume.linkedin_url} className="hover:underline">
                      LinkedIn
                    </a>
                  </div>
                )}
                {resume.github_url && (
                  <div className="flex items-center gap-1">
                    <Github className="h-4 w-4" />
                    <a href={resume.github_url} className="hover:underline">
                      GitHub
                    </a>
                  </div>
                )}
              </div>
            </div>

            {/* Experience Section */}
            {resume.experiences && resume.experiences.length > 0 && (
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <Building className="h-6 w-6" />
                  Work Experience
                </h2>
                <div className="space-y-6">
                  {resume.experiences.map((exp, index) => (
                    <div key={index} className="border-l-2 border-blue-500 pl-6 relative">
                      <div className="absolute -left-2 top-0 w-4 h-4 bg-blue-500 rounded-full"></div>
                      <div className="flex flex-wrap items-start justify-between gap-2 mb-2">
                        <div>
                          <h3 className="text-xl font-semibold text-gray-900">{exp.positionTitle}</h3>
                          <p className="text-lg text-blue-600 font-medium">{exp.companyName}</p>
                        </div>
                        <div className="text-right text-gray-600">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4" />
                            <span>{formatDate(exp.startDate)} - {formatDate(exp.endDate || null)}</span>
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
            {resume.educations && resume.educations.length > 0 && (
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Education</h2>
                <div className="space-y-4">
                  {resume.educations.map((edu, index) => (
                    <div key={index} className="flex flex-wrap items-start justify-between gap-2">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{edu.degree}</h3>
                        <p className="text-blue-600 font-medium">{edu.institutionName}</p>
                        {edu.location && <p className="text-gray-600">{edu.location}</p>}
                      </div>
                      <div className="text-right text-gray-600">
                        <p>{formatDate(edu.startDate)} - {formatDate(edu.endDate || null)}</p>
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
                      {skill.name}
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
                        {project.projectUrl && (
                          <a
                            href={project.projectUrl}
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
                        <p className="text-blue-600">{cert.issuingOrganization}</p>
                        {cert.credentialId && (
                          <p className="text-sm text-gray-600">ID: {cert.credentialId}</p>
                        )}
                      </div>
                      <p className="text-gray-600">{formatDate(cert.issueDate)}</p>
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