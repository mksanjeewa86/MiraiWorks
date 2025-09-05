'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Badge from '@/components/ui/Badge';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { 
  Edit, 
  MapPin, 
  Mail, 
  Phone, 
  Globe, 
  Linkedin, 
  Github,
  Calendar,
  Award,
  Briefcase,
  GraduationCap,
  Users,
  Star,
  ExternalLink,
  Camera,
  Upload
} from 'lucide-react';

interface ProfileData {
  personal_info: {
    full_name: string;
    email: string;
    phone: string;
    location: string;
    bio: string;
    avatar_url?: string;
    website?: string;
    linkedin?: string;
    github?: string;
  };
  professional_info: {
    current_title: string;
    current_company: string;
    experience_years: number;
    industry: string;
    specializations: string[];
  };
  education: Array<{
    institution: string;
    degree: string;
    field: string;
    year: string;
    gpa?: string;
  }>;
  experience: Array<{
    company: string;
    position: string;
    duration: string;
    description: string;
    current: boolean;
  }>;
  skills: {
    technical: string[];
    soft: string[];
    languages: Array<{ name: string; proficiency: string }>;
  };
  achievements: Array<{
    title: string;
    description: string;
    date: string;
    type: 'certification' | 'award' | 'project';
  }>;
  stats: {
    profile_views: number;
    connections: number;
    endorsements: number;
    applications_sent: number;
    interviews_completed: number;
  };
}

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);

  // Mock profile data
  const mockProfile: ProfileData = {
    personal_info: {
      full_name: user?.full_name || 'John Doe',
      email: user?.email || 'john.doe@example.com',
      phone: '+1 (555) 123-4567',
      location: 'San Francisco, CA',
      bio: 'Passionate full-stack developer with 5+ years of experience building scalable web applications. Expertise in React, Node.js, and cloud technologies. Always eager to learn new technologies and solve complex problems.',
      website: 'johndoe.dev',
      linkedin: 'linkedin.com/in/johndoe',
      github: 'github.com/johndoe'
    },
    professional_info: {
      current_title: 'Senior Frontend Developer',
      current_company: 'TechCorp Inc.',
      experience_years: 5,
      industry: 'Technology',
      specializations: ['Frontend Development', 'React', 'TypeScript', 'Node.js', 'AWS']
    },
    education: [
      {
        institution: 'University of California, Berkeley',
        degree: 'Bachelor of Science',
        field: 'Computer Science',
        year: '2020',
        gpa: '3.8'
      },
      {
        institution: 'Stanford University',
        degree: 'Certificate',
        field: 'Machine Learning',
        year: '2022'
      }
    ],
    experience: [
      {
        company: 'TechCorp Inc.',
        position: 'Senior Frontend Developer',
        duration: '2022 - Present',
        description: 'Lead frontend development for React-based applications, mentor junior developers, and improved application performance by 40%.',
        current: true
      },
      {
        company: 'StartupCo',
        position: 'Frontend Developer',
        duration: '2020 - 2022',
        description: 'Developed responsive web applications using React, Redux, and modern CSS frameworks.',
        current: false
      }
    ],
    skills: {
      technical: ['React', 'TypeScript', 'JavaScript', 'Node.js', 'Python', 'AWS', 'Docker', 'GraphQL', 'PostgreSQL'],
      soft: ['Leadership', 'Problem Solving', 'Communication', 'Team Collaboration', 'Project Management'],
      languages: [
        { name: 'English', proficiency: 'Native' },
        { name: 'Spanish', proficiency: 'Intermediate' },
        { name: 'French', proficiency: 'Beginner' }
      ]
    },
    achievements: [
      {
        title: 'AWS Certified Developer',
        description: 'Amazon Web Services certification for cloud development',
        date: '2023-06',
        type: 'certification'
      },
      {
        title: 'Best Innovation Award',
        description: 'Awarded for developing the real-time collaboration feature',
        date: '2023-03',
        type: 'award'
      },
      {
        title: 'Open Source Project: React Components Library',
        description: 'Created and maintain a popular React components library with 2k+ stars',
        date: '2022-12',
        type: 'project'
      }
    ],
    stats: {
      profile_views: 234,
      connections: 89,
      endorsements: 42,
      applications_sent: 15,
      interviews_completed: 8
    }
  };

  useEffect(() => {
    // Simulate loading profile data
    setTimeout(() => {
      setProfile(mockProfile);
      setLoading(false);
    }, 1000);
  }, []);

  const getAchievementIcon = (type: string) => {
    switch (type) {
      case 'certification':
        return <Award className="h-5 w-5 text-blue-500" />;
      case 'award':
        return <Star className="h-5 w-5 text-yellow-500" />;
      case 'project':
        return <Github className="h-5 w-5 text-green-500" />;
      default:
        return <Award className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    const [year, month] = dateString.split('-');
    return `${month ? new Date(parseInt(year), parseInt(month) - 1).toLocaleDateString('en-US', { month: 'short' }) + ' ' : ''}${year}`;
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

  if (!profile) {
    return (
      <AppLayout>
        <div className="p-6">
          <div className="text-center py-16">
            <h1 className="text-2xl font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
              Profile not found
            </h1>
            <Button>Create Profile</Button>
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
          <div>
            <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Profile</h1>
            <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
              Manage your professional profile and showcase your skills
            </p>
          </div>
          
          <Button 
            onClick={() => setEditing(!editing)}
            className="flex items-center gap-2"
          >
            <Edit className="h-4 w-4" />
            {editing ? 'Save Changes' : 'Edit Profile'}
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Profile Card */}
          <div className="lg:col-span-2 space-y-6">
            {/* Personal Information */}
            <Card className="p-8">
              <div className="flex items-start gap-6">
                {/* Avatar */}
                <div className="relative">
                  <div className="w-24 h-24 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                    {profile.personal_info.full_name.split(' ').map(n => n[0]).join('')}
                  </div>
                  {editing && (
                    <button className="absolute -bottom-1 -right-1 bg-white dark:bg-gray-800 rounded-full p-2 shadow-lg border">
                      <Camera className="h-4 w-4" />
                    </button>
                  )}
                </div>

                {/* Basic Info */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h2 className="text-2xl font-bold mb-1" style={{ color: 'var(--text-primary)' }}>
                        {profile.personal_info.full_name}
                      </h2>
                      <p className="text-lg font-medium text-blue-600 mb-2">
                        {profile.professional_info.current_title} at {profile.professional_info.current_company}
                      </p>
                      <div className="flex items-center gap-4 text-gray-600 text-sm">
                        <div className="flex items-center gap-1">
                          <MapPin className="h-4 w-4" />
                          {profile.personal_info.location}
                        </div>
                        <div className="flex items-center gap-1">
                          <Briefcase className="h-4 w-4" />
                          {profile.professional_info.experience_years} years experience
                        </div>
                      </div>
                    </div>
                  </div>

                  <p className="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">
                    {profile.personal_info.bio}
                  </p>

                  {/* Contact Links */}
                  <div className="flex flex-wrap items-center gap-4 text-sm">
                    <div className="flex items-center gap-1 text-gray-600">
                      <Mail className="h-4 w-4" />
                      {profile.personal_info.email}
                    </div>
                    <div className="flex items-center gap-1 text-gray-600">
                      <Phone className="h-4 w-4" />
                      {profile.personal_info.phone}
                    </div>
                    {profile.personal_info.website && (
                      <a 
                        href={`https://${profile.personal_info.website}`}
                        className="flex items-center gap-1 text-blue-600 hover:underline"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Globe className="h-4 w-4" />
                        {profile.personal_info.website}
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                    {profile.personal_info.linkedin && (
                      <a 
                        href={`https://${profile.personal_info.linkedin}`}
                        className="flex items-center gap-1 text-blue-600 hover:underline"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Linkedin className="h-4 w-4" />
                        LinkedIn
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                    {profile.personal_info.github && (
                      <a 
                        href={`https://${profile.personal_info.github}`}
                        className="flex items-center gap-1 text-blue-600 hover:underline"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Github className="h-4 w-4" />
                        GitHub
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </Card>

            {/* Experience */}
            <Card className="p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                <Briefcase className="h-5 w-5" />
                Experience
              </h3>
              <div className="space-y-6">
                {profile.experience.map((exp, index) => (
                  <div key={index} className="border-l-2 border-blue-500 pl-4 relative">
                    <div className="absolute -left-2 top-0 w-4 h-4 bg-blue-500 rounded-full"></div>
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
                          {exp.position}
                        </h4>
                        <p className="text-blue-600 font-medium">{exp.company}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-gray-600 text-sm">{exp.duration}</p>
                        {exp.current && (
                          <Badge variant="success" size="sm">Current</Badge>
                        )}
                      </div>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300">{exp.description}</p>
                  </div>
                ))}
              </div>
            </Card>

            {/* Education */}
            <Card className="p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                <GraduationCap className="h-5 w-5" />
                Education
              </h3>
              <div className="space-y-4">
                {profile.education.map((edu, index) => (
                  <div key={index} className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {edu.degree} in {edu.field}
                      </h4>
                      <p className="text-blue-600">{edu.institution}</p>
                      {edu.gpa && <p className="text-gray-600 text-sm">GPA: {edu.gpa}</p>}
                    </div>
                    <p className="text-gray-600">{edu.year}</p>
                  </div>
                ))}
              </div>
            </Card>

            {/* Achievements */}
            <Card className="p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                <Award className="h-5 w-5" />
                Achievements
              </h3>
              <div className="space-y-4">
                {profile.achievements.map((achievement, index) => (
                  <div key={index} className="flex items-start gap-3">
                    {getAchievementIcon(achievement.type)}
                    <div className="flex-1">
                      <h4 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {achievement.title}
                      </h4>
                      <p className="text-gray-700 dark:text-gray-300 text-sm mb-1">
                        {achievement.description}
                      </p>
                      <p className="text-gray-500 text-xs">{formatDate(achievement.date)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Stats */}
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
                Profile Stats
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Profile Views</span>
                  <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                    {profile.stats.profile_views}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Connections</span>
                  <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                    {profile.stats.connections}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Endorsements</span>
                  <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                    {profile.stats.endorsements}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Applications</span>
                  <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                    {profile.stats.applications_sent}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-600">Interviews</span>
                  <span className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                    {profile.stats.interviews_completed}
                  </span>
                </div>
              </div>
            </Card>

            {/* Skills */}
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
                Skills
              </h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                    Technical Skills
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {profile.skills.technical.map((skill, index) => (
                      <Badge key={index} variant="primary" size="sm">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                    Soft Skills
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {profile.skills.soft.map((skill, index) => (
                      <Badge key={index} variant="secondary" size="sm">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                    Languages
                  </h4>
                  <div className="space-y-2">
                    {profile.skills.languages.map((lang, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-gray-700 dark:text-gray-300">{lang.name}</span>
                        <Badge variant="success" size="sm">
                          {lang.proficiency}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </Card>

            {/* Specializations */}
            <Card className="p-6">
              <h3 className="text-lg font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
                Specializations
              </h3>
              <div className="space-y-2">
                {profile.professional_info.specializations.map((spec, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-gray-700 dark:text-gray-300">{spec}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}