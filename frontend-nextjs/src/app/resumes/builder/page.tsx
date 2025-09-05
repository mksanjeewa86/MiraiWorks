'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { 
  Save, 
  Eye, 
  Download, 
  ArrowLeft, 
  Plus, 
  Trash2, 
  User, 
  Briefcase, 
  GraduationCap, 
  Award,
  Code,
  Globe,
  FileText,
  Palette
} from 'lucide-react';
import type { Resume, Experience, Education, Certification, Project, Language } from '@/types';

interface ResumeBuilderState {
  activeSection: 'template' | 'personal' | 'experience' | 'education' | 'skills' | 'certifications' | 'projects' | 'languages' | 'preview';
  resume: Partial<Resume>;
  saving: boolean;
  errors: Record<string, string>;
}

export default function ResumeBuilderPage() {
  const { user } = useAuth();
  
  const [state, setState] = useState<ResumeBuilderState>({
    activeSection: 'template',
    resume: {
      title: '',
      description: '',
      template_id: 'modern',
      personal_info: {
        full_name: user?.full_name || '',
        email: user?.email || '',
        phone: '',
        address: '',
        linkedin: '',
        website: '',
        github: ''
      },
      experience: [],
      education: [],
      skills: [],
      certifications: [],
      projects: [],
      languages: [],
      is_primary: false,
      is_public: false
    },
    saving: false,
    errors: {}
  });

  const templates = [
    { id: 'modern', name: 'Modern', description: 'Clean and contemporary design with subtle colors', preview: '🎨' },
    { id: 'professional', name: 'Professional', description: 'Classic business-friendly layout', preview: '👔' },
    { id: 'creative', name: 'Creative', description: 'Bold design for creative professionals', preview: '✨' },
    { id: 'minimal', name: 'Minimal', description: 'Simple and elegant with focus on content', preview: '📝' }
  ];

  const sections = [
    { id: 'template', name: 'Template', icon: Palette, description: 'Choose your resume design' },
    { id: 'personal', name: 'Personal Info', icon: User, description: 'Contact information' },
    { id: 'experience', name: 'Experience', icon: Briefcase, description: 'Work history' },
    { id: 'education', name: 'Education', icon: GraduationCap, description: 'Academic background' },
    { id: 'skills', name: 'Skills', icon: Code, description: 'Technical & soft skills' },
    { id: 'certifications', name: 'Certifications', icon: Award, description: 'Professional certifications' },
    { id: 'projects', name: 'Projects', icon: FileText, description: 'Notable projects' },
    { id: 'languages', name: 'Languages', icon: Globe, description: 'Language proficiency' },
    { id: 'preview', name: 'Preview', icon: Eye, description: 'Review your resume' }
  ];

  const updateResume = (updates: Partial<Resume>) => {
    setState(prev => ({
      ...prev,
      resume: { ...prev.resume, ...updates }
    }));
  };

  const updatePersonalInfo = (field: string, value: string) => {
    setState(prev => ({
      ...prev,
      resume: {
        ...prev.resume,
        personal_info: {
          ...prev.resume.personal_info!,
          [field]: value
        }
      }
    }));
  };

  const addExperience = () => {
    const newExperience: Experience = {
      company: '',
      position: '',
      start_date: '',
      end_date: null,
      description: '',
      location: ''
    };
    
    setState(prev => ({
      ...prev,
      resume: {
        ...prev.resume,
        experience: [...(prev.resume.experience || []), newExperience]
      }
    }));
  };

  const updateExperience = (index: number, field: string, value: string | null) => {
    setState(prev => {
      const experience = [...(prev.resume.experience || [])];
      experience[index] = { ...experience[index], [field]: value };
      return {
        ...prev,
        resume: { ...prev.resume, experience }
      };
    });
  };

  const removeExperience = (index: number) => {
    setState(prev => ({
      ...prev,
      resume: {
        ...prev.resume,
        experience: prev.resume.experience?.filter((_, i) => i !== index)
      }
    }));
  };

  const addEducation = () => {
    const newEducation: Education = {
      institution: '',
      degree: '',
      start_date: '',
      end_date: '',
      location: ''
    };
    
    setState(prev => ({
      ...prev,
      resume: {
        ...prev.resume,
        education: [...(prev.resume.education || []), newEducation]
      }
    }));
  };

  const updateEducation = (index: number, field: string, value: string) => {
    setState(prev => {
      const education = [...(prev.resume.education || [])];
      education[index] = { ...education[index], [field]: value };
      return {
        ...prev,
        resume: { ...prev.resume, education }
      };
    });
  };

  const removeEducation = (index: number) => {
    setState(prev => ({
      ...prev,
      resume: {
        ...prev.resume,
        education: prev.resume.education?.filter((_, i) => i !== index)
      }
    }));
  };

  const addSkill = (skill: string) => {
    if (skill.trim() && !state.resume.skills?.includes(skill.trim())) {
      setState(prev => ({
        ...prev,
        resume: {
          ...prev.resume,
          skills: [...(prev.resume.skills || []), skill.trim()]
        }
      }));
    }
  };

  const removeSkill = (skill: string) => {
    setState(prev => ({
      ...prev,
      resume: {
        ...prev.resume,
        skills: prev.resume.skills?.filter(s => s !== skill)
      }
    }));
  };

  const handleSave = async () => {
    setState(prev => ({ ...prev, saving: true }));
    
    // Simulate saving
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setState(prev => ({ ...prev, saving: false }));
  };

  const renderTemplateSection = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Choose Template</h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          Select a template that matches your style and industry
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {templates.map(template => (
          <Card 
            key={template.id}
            className={`p-6 cursor-pointer transition-all ${
              state.resume.template_id === template.id 
                ? 'ring-2 ring-brand-primary border-brand-primary' 
                : 'hover:shadow-md'
            }`}
            onClick={() => updateResume({ template_id: template.id })}
          >
            <div className="flex items-start gap-4">
              <div className="text-4xl">{template.preview}</div>
              <div className="flex-1">
                <h3 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
                  {template.name}
                </h3>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  {template.description}
                </p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="space-y-4">
        <Input
          label="Resume Title"
          value={state.resume.title || ''}
          onChange={(e) => updateResume({ title: e.target.value })}
          placeholder="e.g., Senior Frontend Developer Resume"
          required
        />
        <Input
          label="Description"
          value={state.resume.description || ''}
          onChange={(e) => updateResume({ description: e.target.value })}
          placeholder="Brief description of this resume"
        />
      </div>
    </div>
  );

  const renderPersonalSection = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Personal Information</h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          Enter your contact details and professional links
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Full Name"
          value={state.resume.personal_info?.full_name || ''}
          onChange={(e) => updatePersonalInfo('full_name', e.target.value)}
          required
        />
        <Input
          label="Email"
          type="email"
          value={state.resume.personal_info?.email || ''}
          onChange={(e) => updatePersonalInfo('email', e.target.value)}
          required
        />
        <Input
          label="Phone"
          value={state.resume.personal_info?.phone || ''}
          onChange={(e) => updatePersonalInfo('phone', e.target.value)}
        />
        <Input
          label="Address"
          value={state.resume.personal_info?.address || ''}
          onChange={(e) => updatePersonalInfo('address', e.target.value)}
        />
        <Input
          label="LinkedIn"
          value={state.resume.personal_info?.linkedin || ''}
          onChange={(e) => updatePersonalInfo('linkedin', e.target.value)}
          placeholder="linkedin.com/in/yourprofile"
        />
        <Input
          label="Website"
          value={state.resume.personal_info?.website || ''}
          onChange={(e) => updatePersonalInfo('website', e.target.value)}
          placeholder="yourwebsite.com"
        />
      </div>
      
      <Input
        label="GitHub (optional)"
        value={state.resume.personal_info?.github || ''}
        onChange={(e) => updatePersonalInfo('github', e.target.value)}
        placeholder="github.com/yourusername"
      />
    </div>
  );

  const renderExperienceSection = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Work Experience</h2>
          <p style={{ color: 'var(--text-secondary)' }}>
            List your professional work history
          </p>
        </div>
        <Button onClick={addExperience} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          Add Experience
        </Button>
      </div>

      <div className="space-y-6">
        {state.resume.experience?.map((exp, index) => (
          <Card key={index} className="p-6">
            <div className="flex items-start justify-between mb-4">
              <h3 className="font-semibold" style={{ color: 'var(--text-primary)' }}>
                Experience {index + 1}
              </h3>
              <Button
                variant="outline"
                size="sm"
                onClick={() => removeExperience(index)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Company"
                value={exp.company}
                onChange={(e) => updateExperience(index, 'company', e.target.value)}
                required
              />
              <Input
                label="Position"
                value={exp.position}
                onChange={(e) => updateExperience(index, 'position', e.target.value)}
                required
              />
              <Input
                label="Start Date"
                type="month"
                value={exp.start_date}
                onChange={(e) => updateExperience(index, 'start_date', e.target.value)}
                required
              />
              <Input
                label="End Date"
                type="month"
                value={exp.end_date || ''}
                onChange={(e) => updateExperience(index, 'end_date', e.target.value || null)}
                helperText="Leave blank if current position"
              />
            </div>
            
            <div className="mt-4 space-y-4">
              <Input
                label="Location"
                value={exp.location || ''}
                onChange={(e) => updateExperience(index, 'location', e.target.value)}
              />
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Description
                </label>
                <textarea
                  className="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
                  style={{ color: 'var(--text-primary)' }}
                  rows={4}
                  value={exp.description}
                  onChange={(e) => updateExperience(index, 'description', e.target.value)}
                  placeholder="Describe your responsibilities and achievements..."
                />
              </div>
            </div>
          </Card>
        )) || (
          <div className="text-center py-8">
            <Briefcase className="h-12 w-12 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
            <p style={{ color: 'var(--text-secondary)' }}>No work experience added yet</p>
            <Button onClick={addExperience} className="mt-4">
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Experience
            </Button>
          </div>
        )}
      </div>
    </div>
  );

  const renderSkillsSection = () => {
    const [newSkill, setNewSkill] = useState('');

    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Skills</h2>
          <p style={{ color: 'var(--text-secondary)' }}>
            Add your technical and soft skills
          </p>
        </div>

        <div className="flex gap-2">
          <Input
            value={newSkill}
            onChange={(e) => setNewSkill(e.target.value)}
            placeholder="Enter a skill"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                addSkill(newSkill);
                setNewSkill('');
              }
            }}
          />
          <Button 
            onClick={() => {
              addSkill(newSkill);
              setNewSkill('');
            }}
            disabled={!newSkill.trim()}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex flex-wrap gap-2">
          {state.resume.skills?.map((skill, index) => (
            <div
              key={index}
              className="flex items-center gap-2 px-3 py-1 bg-gray-100 dark:bg-gray-800 rounded-full"
            >
              <span className="text-sm" style={{ color: 'var(--text-primary)' }}>{skill}</span>
              <button
                onClick={() => removeSkill(skill)}
                className="text-red-500 hover:text-red-700"
              >
                <Trash2 className="h-3 w-3" />
              </button>
            </div>
          )) || (
            <p style={{ color: 'var(--text-secondary)' }}>No skills added yet</p>
          )}
        </div>
      </div>
    );
  };

  const renderPreviewSection = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Resume Preview</h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          Review your resume before saving
        </p>
      </div>

      <Card className="p-8 bg-white border-2 border-dashed border-gray-300">
        <div className="text-center py-16">
          <Eye className="h-16 w-16 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
          <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
            Resume Preview
          </h3>
          <p style={{ color: 'var(--text-secondary)' }}>
            Preview functionality will be implemented with PDF generation
          </p>
        </div>
      </Card>

      <div className="flex gap-4">
        <Button className="flex-1">
          <Save className="h-4 w-4 mr-2" />
          Save Resume
        </Button>
        <Button variant="outline" className="flex-1">
          <Download className="h-4 w-4 mr-2" />
          Download PDF
        </Button>
      </div>
    </div>
  );

  const renderCurrentSection = () => {
    switch (state.activeSection) {
      case 'template':
        return renderTemplateSection();
      case 'personal':
        return renderPersonalSection();
      case 'experience':
        return renderExperienceSection();
      case 'skills':
        return renderSkillsSection();
      case 'preview':
        return renderPreviewSection();
      default:
        return (
          <div className="text-center py-16">
            <FileText className="h-16 w-16 mx-auto mb-4" style={{ color: 'var(--text-muted)' }} />
            <p style={{ color: 'var(--text-secondary)' }}>
              Section "{state.activeSection}" is under development
            </p>
          </div>
        );
    }
  };

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
              <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Resume Builder</h1>
              <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
                Create your professional resume step by step
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button 
              variant="outline" 
              onClick={handleSave}
              disabled={state.saving}
            >
              {state.saving ? <LoadingSpinner className="w-4 h-4 mr-2" /> : <Save className="h-4 w-4 mr-2" />}
              {state.saving ? 'Saving...' : 'Save Draft'}
            </Button>
            <Button>
              <Eye className="h-4 w-4 mr-2" />
              Preview
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Navigation */}
          <div className="space-y-2">
            {sections.map((section) => {
              const IconComponent = section.icon;
              const isActive = state.activeSection === section.id;
              
              return (
                <button
                  key={section.id}
                  onClick={() => setState(prev => ({ ...prev, activeSection: section.id as any }))}
                  className={`w-full text-left p-3 rounded-lg transition-colors flex items-center gap-3 ${
                    isActive
                      ? 'bg-brand-primary text-white'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  <IconComponent className="h-5 w-5" />
                  <div>
                    <div className="font-medium">{section.name}</div>
                    <div className={`text-xs ${isActive ? 'text-white/80' : 'text-gray-500'}`}>
                      {section.description}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <Card className="p-8">
              {renderCurrentSection()}
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}