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
  Award,
  Briefcase,
  GraduationCap,
  Star,
  Camera
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

  useEffect(() => {
    const loadProfileData = () => {
      if (!user) {
        setLoading(false);
        return;
      }

      // Convert user data to profile format
      const profileData: ProfileData = {
        personal_info: {
          full_name: user.full_name || '',
          email: user.email || '',
          phone: user.phone || '',
          location: '', // This would come from user profile data in the database
          bio: 'Professional working in the technology sector.', // Default bio
          avatar_url: undefined,
          website: undefined,
          linkedin: undefined,
          github: undefined,
        },
        professional_info: {
          current_title: 'Developer', // This would come from user profile data
          current_company: user.company?.name || '',
          experience_years: 3, // This would come from user profile data
          industry: user.company?.industry || 'Technology',
          specializations: ['Web Development'], // This would come from user profile data
        },
        education: [
          // This would come from user education data in the database
          {
            institution: 'University',
            degree: 'Bachelor\'s Degree',
            field: 'Computer Science',
            year: '2020',
          }
        ],
        experience: [
          // This would come from user work experience data
          {
            company: user.company?.name || 'Tech Company',
            position: 'Developer',
            duration: '2021 - Present',
            description: 'Working on web applications and backend services.',
            current: true
          }
        ],
        skills: {
          // This would come from user skills data in the database
          technical: ['JavaScript', 'React', 'TypeScript', 'Node.js'],
          soft: ['Communication', 'Problem Solving', 'Teamwork'],
          languages: [
            { name: 'English', proficiency: 'Native' },
            { name: 'Spanish', proficiency: 'Intermediate' }
          ]
        },
        achievements: [
          // This would come from user achievements data in the database
          {
            title: 'Certified Developer',
            type: 'certification',
            date: '2023-06-01',
            description: 'Certified in modern web development technologies'
          }
        ],
        stats: {
          profile_views: 0, // This would come from analytics
          connections: 0,
          endorsements: 0,
          applications_sent: 0, // This would come from user applications
          interviews_completed: 0, // This would come from user interviews
        }
      };

      setProfile(profileData);
      setLoading(false);
    };

    loadProfileData();
  }, [user]);

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

  // Helper function for skill level styling (available for future use)
  // const getSkillLevel = (level: string) => {
  //   const levels: Record<string, string> = {
  //     'Expert': 'bg-green-100 text-green-800',
  //     'Advanced': 'bg-blue-100 text-blue-800', 
  //     'Intermediate': 'bg-yellow-100 text-yellow-800',
  //     'Beginner': 'bg-gray-100 text-gray-800'
  //   };
  //   return levels[level] || levels['Intermediate'];
  // };

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
        <div className="flex flex-col items-center justify-center h-64">
          <div className="text-6xl mb-4">👤</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">No Profile Data</h3>
          <p className="text-gray-600 mb-6">Please log in to view your profile</p>
          <Button>Create Profile</Button>
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
              Manage your professional profile and settings
            </p>
          </div>
          <Button 
            className="flex items-center gap-2"
            onClick={() => setEditing(!editing)}
          >
            <Edit className="h-4 w-4" />
            {editing ? 'Save Profile' : 'Edit Profile'}
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Profile Section */}
          <div className="lg:col-span-2 space-y-6">
            {/* Personal Info */}
            <Card className="p-6">
              <div className="flex items-start gap-6">
                <div className="relative">
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
                    {profile.personal_info.full_name.split(' ').map(n => n[0]).join('')}
                  </div>
                  {editing && (
                    <Button size="sm" className="absolute -bottom-2 -right-2 rounded-full p-2">
                      <Camera className="h-3 w-3" />
                    </Button>
                  )}
                </div>
                
                <div className="flex-1">
                  <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
                    {profile.personal_info.full_name}
                  </h2>
                  <p className="text-lg mb-4" style={{ color: 'var(--brand-primary)' }}>
                    {profile.professional_info.current_title}
                  </p>
                  
                  <div className="flex flex-wrap gap-4 text-sm" style={{ color: 'var(--text-secondary)' }}>
                    <div className="flex items-center gap-2">
                      <Mail className="h-4 w-4" />
                      {profile.personal_info.email}
                    </div>
                    {profile.personal_info.phone && (
                      <div className="flex items-center gap-2">
                        <Phone className="h-4 w-4" />
                        {profile.personal_info.phone}
                      </div>
                    )}
                    {profile.personal_info.location && (
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4" />
                        {profile.personal_info.location}
                      </div>
                    )}
                    <div className="flex items-center gap-2">
                      <Briefcase className="h-4 w-4" />
                      {profile.professional_info.current_company}
                    </div>
                  </div>

                  {profile.personal_info.bio && (
                    <p className="mt-4" style={{ color: 'var(--text-secondary)' }}>
                      {profile.personal_info.bio}
                    </p>
                  )}

                  <div className="flex gap-3 mt-4">
                    {profile.personal_info.website && (
                      <Button variant="outline" size="sm">
                        <Globe className="h-4 w-4" />
                      </Button>
                    )}
                    {profile.personal_info.linkedin && (
                      <Button variant="outline" size="sm">
                        <Linkedin className="h-4 w-4" />
                      </Button>
                    )}
                    {profile.personal_info.github && (
                      <Button variant="outline" size="sm">
                        <Github className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </Card>

            {/* Experience */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Experience</h3>
                {editing && <Button variant="outline" size="sm">Add Experience</Button>}
              </div>
              <div className="space-y-4">
                {profile.experience.map((exp, index) => (
                  <div key={index} className="border-l-2 border-blue-200 pl-4">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium" style={{ color: 'var(--text-primary)' }}>{exp.position}</h4>
                        <p className="text-sm" style={{ color: 'var(--brand-primary)' }}>{exp.company}</p>
                        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>{exp.duration}</p>
                        <p className="text-sm mt-2" style={{ color: 'var(--text-secondary)' }}>{exp.description}</p>
                      </div>
                      {exp.current && <Badge variant="primary" size="sm">Current</Badge>}
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Education */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Education</h3>
                {editing && <Button variant="outline" size="sm">Add Education</Button>}
              </div>
              <div className="space-y-4">
                {profile.education.map((edu, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <GraduationCap className="h-5 w-5 mt-1" style={{ color: 'var(--brand-primary)' }} />
                    <div>
                      <h4 className="font-medium" style={{ color: 'var(--text-primary)' }}>
                        {edu.degree} in {edu.field}
                      </h4>
                      <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{edu.institution}</p>
                      <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Class of {edu.year}</p>
                      {edu.gpa && (
                        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>GPA: {edu.gpa}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Skills */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Skills</h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>Technical Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {profile.skills.technical.map((skill, index) => (
                      <Badge key={index} variant="secondary">{skill}</Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>Soft Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {profile.skills.soft.map((skill, index) => (
                      <Badge key={index} variant="secondary">{skill}</Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-2" style={{ color: 'var(--text-secondary)' }}>Languages</h4>
                  <div className="flex flex-wrap gap-2">
                    {profile.skills.languages.map((lang, index) => (
                      <Badge key={index} variant="primary">
                        {lang.name} - {lang.proficiency}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Stats */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>Profile Stats</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Profile Views</span>
                  <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{profile.stats.profile_views}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Connections</span>
                  <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{profile.stats.connections}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Endorsements</span>
                  <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{profile.stats.endorsements}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Applications</span>
                  <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{profile.stats.applications_sent}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Interviews</span>
                  <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{profile.stats.interviews_completed}</span>
                </div>
              </div>
            </Card>

            {/* Achievements */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>Achievements</h3>
                {editing && <Button variant="outline" size="sm">Add</Button>}
              </div>
              <div className="space-y-3">
                {profile.achievements.map((achievement, index) => (
                  <div key={index} className="flex items-start gap-3">
                    {getAchievementIcon(achievement.type)}
                    <div className="flex-1">
                      <h4 className="font-medium text-sm" style={{ color: 'var(--text-primary)' }}>
                        {achievement.title}
                      </h4>
                      <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                        {achievement.description}
                      </p>
                      <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                        {new Date(achievement.date).toLocaleDateString()}
                      </p>
                    </div>
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