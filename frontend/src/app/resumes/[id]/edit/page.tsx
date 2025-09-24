'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/card';
import Button from '@/components/ui/button';
import LoadingSpinner from '@/components/ui/loading-spinner';
import { ArrowLeft, FileText, Upload, X, Edit } from 'lucide-react';
import {
  Resume,
  ResumeFormat,
  ResumeLanguage,
  WorkExperience,
  Education,
  Skill,
  Project,
  Certification,
  Language,
} from '@/types/resume';
import { resumesApi } from '@/api/resumes';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

interface ExtendedResume extends Resume {
  experiences?: WorkExperience[];
  educations?: Education[];
  skills?: Skill[];
  projects?: Project[];
  certifications?: Certification[];
  languages?: Language[];
}

function EditResumePageContent() {
  const router = useRouter();
  const params = useParams();
  const resumeId = params.id as string;

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [resume, setResume] = useState<ExtendedResume | null>(null);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('basic');

  useEffect(() => {
    fetchResume();
  }, [resumeId]);

  const fetchResume = async () => {
    try {
      setLoading(true);
      const response = await resumesApi.getById(parseInt(resumeId));

      if (!response.data) {
        throw new Error('Failed to fetch resume');
      }

      setResume(response.data);

      if (response.data.photo_path) {
        setPhotoPreview(response.data.photo_path);
      }
    } catch (error) {
      console.error('Error fetching resume:', error);
      alert('Failed to load resume. Please try again.');
      router.push('/resumes');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;

    if (!resume) return;

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setResume((prev) => (prev ? { ...prev, [name]: checked } : null));
    } else {
      setResume((prev) => (prev ? { ...prev, [name]: value } : null));
    }
  };

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        // 5MB limit
        alert('Photo size must be less than 5MB');
        return;
      }

      if (!file.type.startsWith('image/')) {
        alert('Please select a valid image file');
        return;
      }

      setPhotoFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setPhotoPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removePhoto = async () => {
    if (resume?.photo_path) {
      try {
        await resumesApi.removePhoto(parseInt(resumeId));
        setResume((prev) => (prev ? { ...prev, photo_path: undefined } : null));
      } catch (error) {
        console.error('Error removing photo:', error);
      }
    }

    setPhotoFile(null);
    setPhotoPreview(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!resume || !resume.title.trim() || !resume.full_name?.trim()) {
      alert('Please fill in the required fields: Title and Full Name');
      return;
    }

    try {
      setSaving(true);

      // Update the resume
      await resumesApi.update(parseInt(resumeId), resume);

      // Upload photo if provided
      if (photoFile) {
        try {
          await resumesApi.uploadPhoto(parseInt(resumeId), photoFile);
        } catch (error) {
          console.warn('Failed to upload photo, but resume was updated');
        }
      }

      alert('Resume updated successfully!');
      router.push('/resumes');
    } catch (error) {
      console.error('Error updating resume:', error);
      alert('Failed to update resume. Please try again.');
    } finally {
      setSaving(false);
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
          <p className="text-gray-600 mb-6">
            The resume you're looking for doesn't exist or you don't have permission to edit it.
          </p>
          <Button onClick={() => router.push('/resumes')}>Back to Resumes</Button>
        </div>
      </AppLayout>
    );
  }

  const isJapaneseFormat =
    resume.resume_format === ResumeFormat.RIREKISHO ||
    resume.resume_format === ResumeFormat.SHOKUMU_KEIREKISHO;

  const tabs = [
    { id: 'basic', label: 'Basic Info', icon: FileText },
    { id: 'experience', label: 'Experience', icon: Edit },
    { id: 'education', label: 'Education', icon: Edit },
    { id: 'skills', label: 'Skills', icon: Edit },
    { id: 'projects', label: 'Projects', icon: Edit },
  ];

  return (
    <AppLayout>
      <div className="p-6 max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center mb-8">
          <Button variant="ghost" onClick={() => router.back()} className="mr-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
              Edit Resume
            </h1>
            <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
              {resume.title} -{' '}
              {resume.resume_format === ResumeFormat.RIREKISHO
                ? '履歴書'
                : resume.resume_format === ResumeFormat.SHOKUMU_KEIREKISHO
                  ? '職務経歴書'
                  : resume.resume_format}
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => router.push(`/resumes/${resumeId}/preview`)}>
              Preview
            </Button>
            <Button onClick={handleSubmit} disabled={saving}>
              {saving ? 'Saving...' : 'Save Changes'}
            </Button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="border-b border-gray-200 mb-8">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="h-4 w-4" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information Tab */}
          {activeTab === 'basic' && (
            <div className="space-y-8">
              {/* Resume Format (Read-only) */}
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
                  Resume Format
                </h2>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center gap-3">
                    <FileText className="h-8 w-8" style={{ color: 'var(--brand-primary)' }} />
                    <div>
                      <div className="font-medium">
                        {resume.resume_format === ResumeFormat.RIREKISHO && '履歴書 (Rirekisho)'}
                        {resume.resume_format === ResumeFormat.SHOKUMU_KEIREKISHO &&
                          '職務経歴書 (Shokumu Keirekisho)'}
                        {resume.resume_format === ResumeFormat.INTERNATIONAL &&
                          'International Format'}
                        {resume.resume_format === ResumeFormat.MODERN && 'Modern Format'}
                      </div>
                      <div className="text-sm text-gray-600">
                        Resume format cannot be changed after creation
                      </div>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Basic Information */}
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
                  Basic Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      Resume Title *
                    </label>
                    <input
                      type="text"
                      name="title"
                      value={resume.title}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      Language
                    </label>
                    <select
                      name="resume_language"
                      value={resume.resume_language}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value={ResumeLanguage.ENGLISH}>English</option>
                      <option value={ResumeLanguage.JAPANESE}>Japanese</option>
                      <option value={ResumeLanguage.BILINGUAL}>Bilingual</option>
                    </select>
                  </div>

                  <div className="md:col-span-2">
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      Description
                    </label>
                    <textarea
                      name="description"
                      value={resume.description || ''}
                      onChange={handleInputChange}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </Card>

              {/* Personal Information */}
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
                  Personal Information
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      Full Name *
                    </label>
                    <input
                      type="text"
                      name="full_name"
                      value={resume.full_name || ''}
                      onChange={handleInputChange}
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {isJapaneseFormat && (
                    <div>
                      <label
                        className="block text-sm font-medium mb-2"
                        style={{ color: 'var(--text-primary)' }}
                      >
                        Furigana (フリガナ)
                      </label>
                      <input
                        type="text"
                        name="furigana_name"
                        value={resume.furigana_name || ''}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  )}

                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      Email
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={resume.email || ''}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      Phone
                    </label>
                    <input
                      type="tel"
                      name="phone"
                      value={resume.phone || ''}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      Location
                    </label>
                    <input
                      type="text"
                      name="location"
                      value={resume.location || ''}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {isJapaneseFormat && (
                    <>
                      <div>
                        <label
                          className="block text-sm font-medium mb-2"
                          style={{ color: 'var(--text-primary)' }}
                        >
                          Birth Date (生年月日)
                        </label>
                        <input
                          type="date"
                          name="birth_date"
                          value={
                            resume.birth_date
                              ? new Date(resume.birth_date).toISOString().split('T')[0]
                              : ''
                          }
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div>
                        <label
                          className="block text-sm font-medium mb-2"
                          style={{ color: 'var(--text-primary)' }}
                        >
                          Gender (性別)
                        </label>
                        <select
                          name="gender"
                          value={resume.gender || ''}
                          onChange={handleInputChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">選択してください</option>
                          <option value="男性">男性</option>
                          <option value="女性">女性</option>
                          <option value="その他">その他</option>
                        </select>
                      </div>
                    </>
                  )}

                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      Website
                    </label>
                    <input
                      type="url"
                      name="website"
                      value={resume.website || ''}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      LinkedIn URL
                    </label>
                    <input
                      type="url"
                      name="linkedin_url"
                      value={resume.linkedin_url || ''}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </Card>

              {/* Photo Upload */}
              {isJapaneseFormat && (
                <Card className="p-6">
                  <h2
                    className="text-xl font-semibold mb-4"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    Profile Photo (証明写真)
                  </h2>
                  <div className="flex items-start gap-6">
                    <div className="flex-1">
                      <label
                        className="block text-sm font-medium mb-2"
                        style={{ color: 'var(--text-primary)' }}
                      >
                        Upload Photo (Max 5MB)
                      </label>
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handlePhotoUpload}
                          className="hidden"
                          id="photo-upload"
                        />
                        <label htmlFor="photo-upload" className="cursor-pointer">
                          <Upload className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                          <p className="text-sm text-gray-600">
                            Click to upload a professional photo
                          </p>
                        </label>
                      </div>
                    </div>

                    {photoPreview && (
                      <div className="relative">
                        <img
                          src={photoPreview}
                          alt="Profile preview"
                          className="w-24 h-32 object-cover border rounded-lg"
                        />
                        <button
                          type="button"
                          onClick={removePhoto}
                          className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </div>
                    )}
                  </div>
                </Card>
              )}

              {/* Professional Summary */}
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
                  Professional Summary
                </h2>
                <div className="space-y-6">
                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      Professional Summary
                    </label>
                    <textarea
                      name="professional_summary"
                      value={resume.professional_summary || ''}
                      onChange={handleInputChange}
                      rows={5}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  {resume.resume_format === ResumeFormat.SHOKUMU_KEIREKISHO && (
                    <div>
                      <label
                        className="block text-sm font-medium mb-2"
                        style={{ color: 'var(--text-primary)' }}
                      >
                        Self-PR (自己PR)
                      </label>
                      <textarea
                        name="objective"
                        value={resume.objective || ''}
                        onChange={handleInputChange}
                        rows={5}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  )}
                </div>
              </Card>
            </div>
          )}

          {/* Other tabs would be implemented here for experience, education, skills, projects */}
          {activeTab !== 'basic' && (
            <Card className="p-12 text-center">
              <div className="text-6xl mb-4">🚧</div>
              <h3 className="text-xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
                Coming Soon
              </h3>
              <p className="text-gray-600">
                This section is under development. For now, please use the basic information tab.
              </p>
            </Card>
          )}
        </form>
      </div>
    </AppLayout>
  );
}

export default function EditResumePage() {
  return (
    <ProtectedRoute>
      <EditResumePageContent />
    </ProtectedRoute>
  );
}
