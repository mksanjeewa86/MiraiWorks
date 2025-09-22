"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import { ArrowLeft, FileText, Upload, X } from 'lucide-react';
import { ResumeFormat, ResumeLanguage, ResumeStatus, ResumeVisibility } from '@/types/resume';
import { resumesApi } from '@/api/resumes';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

interface ResumeFormData {
  title: string;
  description: string;
  full_name: string;
  furigana_name?: string;
  email: string;
  phone: string;
  location: string;
  website?: string;
  linkedin_url?: string;
  github_url?: string;
  birth_date?: string;
  gender?: string;
  nationality?: string;
  marital_status?: string;
  professional_summary: string;
  objective?: string;
  resume_format: ResumeFormat;
  resume_language: ResumeLanguage;
  theme_color: string;
  font_family: string;
  status: ResumeStatus;
  visibility: ResumeVisibility;
  is_public: boolean;
  can_download_pdf: boolean;
}

function CreateResumePageContent() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [formData, setFormData] = useState<ResumeFormData>({
    title: '',
    description: '',
    full_name: '',
    email: '',
    phone: '',
    location: '',
    professional_summary: '',
    resume_format: ResumeFormat.INTERNATIONAL,
    resume_language: ResumeLanguage.ENGLISH,
    theme_color: '#2563eb',
    font_family: 'Inter',
    status: ResumeStatus.DRAFT,
    visibility: ResumeVisibility.PRIVATE,
    is_public: false,
    can_download_pdf: true,
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData(prev => ({ ...prev, [name]: checked }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
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

  const removePhoto = () => {
    setPhotoFile(null);
    setPhotoPreview(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.full_name.trim()) {
      alert('Please fill in the required fields: Title and Full Name');
      return;
    }

    try {
      setLoading(true);

      // First create the resume
      const resumeResponse = await resumesApi.create(formData);
      
      if (!resumeResponse.data) {
        throw new Error('Failed to create resume');
      }

      // Upload photo if provided
      if (photoFile) {
        try {
          await resumesApi.uploadPhoto(resumeResponse.data.id, photoFile);
        } catch (error) {
          console.warn('Failed to upload photo, but resume was created');
        }
      }

      router.push('/resumes');
    } catch (error) {
      console.error('Error creating resume:', error);
      alert('Failed to create resume. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const isJapaneseFormat = formData.resume_format === ResumeFormat.RIREKISHO || 
                          formData.resume_format === ResumeFormat.SHOKUMU_KEIREKISHO;

  return (
    <AppLayout>
      <div className="p-6 max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center mb-8">
          <Button 
            variant="ghost" 
            onClick={() => router.back()}
            className="mr-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
              Create New Resume
            </h1>
            <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
              Choose your format and fill in your professional information
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Resume Format Selection */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
              Resume Format
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Object.values(ResumeFormat).map((format) => (
                <label
                  key={format}
                  className={`border-2 rounded-lg p-4 cursor-pointer transition-colors ${
                    formData.resume_format === format
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="resume_format"
                    value={format}
                    checked={formData.resume_format === format}
                    onChange={handleInputChange}
                    className="sr-only"
                  />
                  <div className="text-center">
                    <FileText className="h-8 w-8 mx-auto mb-2" style={{ color: 'var(--brand-primary)' }} />
                    <div className="font-medium">
                      {format === ResumeFormat.RIREKISHO && '履歴書'}
                      {format === ResumeFormat.SHOKUMU_KEIREKISHO && '職務経歴書'}
                      {format === ResumeFormat.INTERNATIONAL && 'International'}
                      {format === ResumeFormat.MODERN && 'Modern'}
                    </div>
                    <div className="text-sm text-gray-600 mt-1">
                      {format === ResumeFormat.RIREKISHO && 'Traditional Japanese resume'}
                      {format === ResumeFormat.SHOKUMU_KEIREKISHO && 'Japanese career history'}
                      {format === ResumeFormat.INTERNATIONAL && 'Standard format'}
                      {format === ResumeFormat.MODERN && 'Creative layout'}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </Card>

          {/* Basic Information */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
              Basic Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Resume Title *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Software Engineer Resume"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Language
                </label>
                <select
                  name="resume_language"
                  value={formData.resume_language}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={ResumeLanguage.ENGLISH}>English</option>
                  <option value={ResumeLanguage.JAPANESE}>Japanese</option>
                  <option value={ResumeLanguage.BILINGUAL}>Bilingual</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Brief description of this resume"
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
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Full Name *
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Your full name"
                />
              </div>

              {isJapaneseFormat && (
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                    Furigana (フリガナ)
                  </label>
                  <input
                    type="text"
                    name="furigana_name"
                    value={formData.furigana_name || ''}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="タナカタロウ"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Email
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="your@email.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Phone
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder={isJapaneseFormat ? "090-1234-5678" : "+1 (555) 123-4567"}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Location
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder={isJapaneseFormat ? "東京都渋谷区" : "New York, NY"}
                />
              </div>

              {isJapaneseFormat && (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                      Birth Date (生年月日)
                    </label>
                    <input
                      type="date"
                      name="birth_date"
                      value={formData.birth_date || ''}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                      Gender (性別)
                    </label>
                    <select
                      name="gender"
                      value={formData.gender || ''}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">選択してください</option>
                      <option value="男性">男性</option>
                      <option value="女性">女性</option>
                      <option value="その他">その他</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                      Nationality (国籍)
                    </label>
                    <input
                      type="text"
                      name="nationality"
                      value={formData.nationality || ''}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="日本"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                      Marital Status (婚姻状況)
                    </label>
                    <select
                      name="marital_status"
                      value={formData.marital_status || ''}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">選択してください</option>
                      <option value="独身">独身</option>
                      <option value="既婚">既婚</option>
                      <option value="離婚">離婚</option>
                      <option value="死別">死別</option>
                    </select>
                  </div>
                </>
              )}

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Website
                </label>
                <input
                  type="url"
                  name="website"
                  value={formData.website || ''}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://yourwebsite.com"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  LinkedIn URL
                </label>
                <input
                  type="url"
                  name="linkedin_url"
                  value={formData.linkedin_url || ''}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://linkedin.com/in/yourname"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  GitHub URL
                </label>
                <input
                  type="url"
                  name="github_url"
                  value={formData.github_url || ''}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="https://github.com/yourusername"
                />
              </div>
            </div>
          </Card>

          {/* Photo Upload */}
          {isJapaneseFormat && (
            <Card className="p-6">
              <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
                Profile Photo (証明写真)
              </h2>
              <div className="flex items-start gap-6">
                <div className="flex-1">
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
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
                      <p className="text-xs text-gray-500 mt-1">
                        Recommended: 3cm x 4cm (passport style)
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
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Professional Summary
                </label>
                <textarea
                  name="professional_summary"
                  value={formData.professional_summary}
                  onChange={handleInputChange}
                  rows={5}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder={isJapaneseFormat 
                    ? "ご自身の経験やスキルについて簡潔にまとめてください..."
                    : "Briefly describe your professional background and key achievements..."
                  }
                />
              </div>

              {formData.resume_format === ResumeFormat.SHOKUMU_KEIREKISHO && (
                <div>
                  <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                    Self-PR (自己PR)
                  </label>
                  <textarea
                    name="objective"
                    value={formData.objective || ''}
                    onChange={handleInputChange}
                    rows={5}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="自己PRを記入してください..."
                  />
                </div>
              )}
            </div>
          </Card>

          {/* Settings */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
              Resume Settings
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Status
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={ResumeStatus.DRAFT}>Draft</option>
                  <option value={ResumeStatus.PUBLISHED}>Published</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Visibility
                </label>
                <select
                  name="visibility"
                  value={formData.visibility}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={ResumeVisibility.PRIVATE}>Private</option>
                  <option value={ResumeVisibility.PUBLIC}>Public</option>
                  <option value={ResumeVisibility.UNLISTED}>Unlisted</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Theme Color
                </label>
                <input
                  type="color"
                  name="theme_color"
                  value={formData.theme_color}
                  onChange={handleInputChange}
                  className="w-full h-10 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Font Family
                </label>
                <select
                  name="font_family"
                  value={formData.font_family}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Inter">Inter</option>
                  <option value="Roboto">Roboto</option>
                  <option value="Open Sans">Open Sans</option>
                  {isJapaneseFormat && (
                    <>
                      <option value="MS Gothic">MS Gothic</option>
                      <option value="Yu Gothic">Yu Gothic</option>
                      <option value="Hiragino Kaku Gothic ProN">Hiragino Kaku Gothic ProN</option>
                    </>
                  )}
                </select>
              </div>

              <div className="md:col-span-2 space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_public"
                    checked={formData.is_public}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  <span className="text-sm">Make this resume publicly shareable</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="can_download_pdf"
                    checked={formData.can_download_pdf}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  <span className="text-sm">Allow PDF downloads</span>
                </label>
              </div>
            </div>
          </Card>

          {/* Submit Buttons */}
          <div className="flex gap-4 justify-end">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Resume'}
            </Button>
          </div>
        </form>
      </div>
    </AppLayout>
  );
}

export default function CreateResumePage() {
  return (
    <ProtectedRoute>
      <CreateResumePageContent />
    </ProtectedRoute>
  );
}