'use client';

import React, { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import AppLayout from '@/components/layout/AppLayout';
import { Card } from '@/components/ui';
import { Button } from '@/components/ui';
import { ArrowLeft, FileText, Upload, X, Plus, Trash2 } from 'lucide-react';
import { ResumeFormat, ResumeLanguage, ResumeStatus, ResumeVisibility } from '@/types/resume';
import { resumesApi } from '@/api/resumes';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { PREFECTURES } from '@/utils/prefectures';

interface WorkExperience {
  id: string;
  company_name: string;
  position_title: string;
  location: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  description: string;
  achievements: string[];
  technologies: string[];
}

interface Education {
  id: string;
  institution_name: string;
  degree: string;
  field_of_study: string;
  location: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  gpa?: string;
  description?: string;
}

interface ResumeFormData {
  title: string;
  description: string;
  last_name: string;
  first_name: string;
  furigana_last_name?: string;
  furigana_first_name?: string;
  email: string;
  phone: string;
  postal_code: string;
  prefecture: string;
  city: string;
  address_line: string;
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
  status: ResumeStatus;
  work_experiences: WorkExperience[];
  educations: Education[];
}

// Common nationalities
const NATIONALITIES = [
  '日本',
  'アメリカ',
  'カナダ',
  'イギリス',
  'オーストラリア',
  '韓国',
  '中国',
  'フランス',
  'ドイツ',
  'イタリア',
  'スペイン',
  'ブラジル',
  'インド',
  'その他',
];

function CreateResumePageContent() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [photoFile, setPhotoFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [croppedPhoto, setCroppedPhoto] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [formData, setFormData] = useState<ResumeFormData>({
    title: '',
    description: '',
    last_name: '',
    first_name: '',
    email: '',
    phone: '',
    postal_code: '',
    prefecture: '',
    city: '',
    address_line: '',
    professional_summary: '',
    resume_format: ResumeFormat.RIREKISHO,
    resume_language: ResumeLanguage.JAPANESE,
    status: ResumeStatus.DRAFT,
    work_experiences: [],
    educations: [],
  });

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target;

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  // Photo cropping functionality
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
        cropPhoto(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const cropPhoto = (imageSrc: string) => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');

    if (!canvas || !ctx) return;

    const img = new Image();
    img.onload = () => {
      // 3cm x 4cm at 300 DPI = 354px x 472px
      const targetWidth = 354;
      const targetHeight = 472;

      canvas.width = targetWidth;
      canvas.height = targetHeight;

      // Calculate aspect ratios
      const imgAspect = img.width / img.height;
      const targetAspect = targetWidth / targetHeight;

      let drawWidth, drawHeight, offsetX, offsetY;

      if (imgAspect > targetAspect) {
        // Image is wider than target
        drawHeight = img.height;
        drawWidth = drawHeight * targetAspect;
        offsetX = (img.width - drawWidth) / 2;
        offsetY = 0;
      } else {
        // Image is taller than target
        drawWidth = img.width;
        drawHeight = drawWidth / targetAspect;
        offsetX = 0;
        offsetY = (img.height - drawHeight) / 2;
      }

      ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight, 0, 0, targetWidth, targetHeight);

      const croppedImageData = canvas.toDataURL('image/jpeg', 0.8);
      setCroppedPhoto(croppedImageData);
    };
    img.src = imageSrc;
  };

  // Work experience functions
  const addWorkExperience = () => {
    const newExp: WorkExperience = {
      id: Date.now().toString(),
      company_name: '',
      position_title: '',
      location: '',
      start_date: '',
      end_date: '',
      is_current: false,
      description: '',
      achievements: [''],
      technologies: [''],
    };
    setFormData((prev) => ({
      ...prev,
      work_experiences: [...prev.work_experiences, newExp],
    }));
  };

  const removeWorkExperience = (id: string) => {
    setFormData((prev) => ({
      ...prev,
      work_experiences: prev.work_experiences.filter((exp) => exp.id !== id),
    }));
  };

  const updateWorkExperience = (id: string, field: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      work_experiences: prev.work_experiences.map((exp) =>
        exp.id === id ? { ...exp, [field]: value } : exp
      ),
    }));
  };

  // Education functions
  const addEducation = () => {
    const newEd: Education = {
      id: Date.now().toString(),
      institution_name: '',
      degree: '',
      field_of_study: '',
      location: '',
      start_date: '',
      end_date: '',
      is_current: false,
      gpa: '',
      description: '',
    };
    setFormData((prev) => ({
      ...prev,
      educations: [...prev.educations, newEd],
    }));
  };

  const removeEducation = (id: string) => {
    setFormData((prev) => ({
      ...prev,
      educations: prev.educations.filter((ed) => ed.id !== id),
    }));
  };

  const updateEducation = (id: string, field: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      educations: prev.educations.map((ed) => (ed.id === id ? { ...ed, [field]: value } : ed)),
    }));
  };

  const removePhoto = () => {
    setPhotoFile(null);
    setPhotoPreview(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title.trim() || !formData.last_name.trim() || !formData.first_name.trim()) {
      alert('Please fill in the required fields: Title, Last Name, and First Name');
      return;
    }

    try {
      setLoading(true);

      // Combine name fields for API compatibility and exclude arrays that should be added separately
      const { work_experiences, educations, ...resumeDataOnly } = formData;

      const submitData = {
        ...resumeDataOnly,
        full_name: `${formData.last_name} ${formData.first_name}`,
        location: `${formData.postal_code} ${formData.prefecture}${formData.city}${formData.address_line}`,
        // Auto-set visibility and download settings based on status
        visibility:
          formData.status === ResumeStatus.PUBLISHED
            ? ResumeVisibility.PUBLIC
            : ResumeVisibility.PRIVATE,
        is_public: formData.status === ResumeStatus.PUBLISHED,
        can_download_pdf: formData.status === ResumeStatus.PUBLISHED,
      };

      // First create the resume
      const resumeResponse = await resumesApi.create(submitData);

      if (!resumeResponse.data) {
        throw new Error('Failed to create resume');
      }

      // Upload photo if provided
      if (croppedPhoto) {
        try {
          // Convert base64 to blob
          const response = await fetch(croppedPhoto);
          const blob = await response.blob();
          const file = new File([blob], 'photo.jpg', { type: 'image/jpeg' });
          await resumesApi.uploadPhoto(resumeResponse.data.id, file);
        } catch (error) {
          console.warn('Failed to upload photo, but resume was created');
        }
      }

      // Add work experiences if any
      if (formData.work_experiences.length > 0) {
        for (const exp of formData.work_experiences) {
          if (exp.company_name && exp.position_title) {
            try {
              // Convert frontend format to API format
              const expData = {
                company_name: exp.company_name,
                position_title: exp.position_title,
                location: exp.location,
                start_date: exp.start_date,
                end_date: exp.is_current ? null : exp.end_date,
                is_current: exp.is_current,
                description: exp.description,
                achievements: exp.achievements.filter((a) => a.trim()),
                technologies: exp.technologies.filter((t) => t.trim()),
              };
              await resumesApi.addExperience(resumeResponse.data.id, expData);
            } catch (error) {
              console.warn('Failed to add work experience, but resume was created');
            }
          }
        }
      }

      // Add education if any
      if (formData.educations.length > 0) {
        for (const edu of formData.educations) {
          if (edu.institution_name && edu.degree) {
            try {
              // Convert frontend format to API format
              const eduData = {
                institution_name: edu.institution_name,
                degree: edu.degree,
                field_of_study: edu.field_of_study,
                location: edu.location,
                start_date: edu.start_date,
                end_date: edu.is_current ? null : edu.end_date,
                is_current: edu.is_current,
                gpa: edu.gpa,
                description: edu.description,
              };
              await resumesApi.addEducation(resumeResponse.data.id, eduData);
            } catch (error) {
              console.warn('Failed to add education, but resume was created');
            }
          }
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

  const isJapaneseFormat =
    formData.resume_format === ResumeFormat.RIREKISHO ||
    formData.resume_format === ResumeFormat.SHOKUMU_KEIREKISHO;

  return (
    <AppLayout>
      <div className="p-6 max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center mb-8">
          <Button variant="ghost" onClick={() => router.back()} className="mr-4">
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
              {Object.values(ResumeFormat)
                .filter((format) => format !== ResumeFormat.CREATIVE)
                .map((format) => (
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
                      <FileText
                        className="h-8 w-8 mx-auto mb-2"
                        style={{ color: 'var(--brand-primary)' }}
                      />
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
                        {format === ResumeFormat.MODERN && 'Modern layout'}
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
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
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
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
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
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
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
              {/* Japanese Name Fields */}
              <div>
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
                  Last Name (性) *
                </label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="山田"
                />
              </div>

              <div>
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
                  First Name (名) *
                </label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="太郎"
                />
              </div>

              {/* Furigana Fields */}
              <div>
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
                  Furigana Last Name (フリガナ性)
                </label>
                <input
                  type="text"
                  name="furigana_last_name"
                  value={formData.furigana_last_name || ''}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="ヤマダ"
                />
              </div>

              <div>
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
                  Furigana First Name (フリガナ名)
                </label>
                <input
                  type="text"
                  name="furigana_first_name"
                  value={formData.furigana_first_name || ''}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="タロウ"
                />
              </div>

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
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="your@email.com"
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
                  value={formData.phone}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder={isJapaneseFormat ? '090-1234-5678' : '+1 (555) 123-4567'}
                />
              </div>

              {/* Address Fields */}
              <div>
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
                  Postal Code (郵便番号)
                </label>
                <input
                  type="text"
                  name="postal_code"
                  value={formData.postal_code}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="123-4567"
                  pattern="[0-9]{3}-[0-9]{4}"
                />
              </div>

              <div>
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
                  Prefecture (都道府県)
                </label>
                <select
                  name="prefecture"
                  value={formData.prefecture}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">選択してください</option>
                  {PREFECTURES.map((prefecture) => (
                    <option key={prefecture.code} value={prefecture.nameJa}>
                      {prefecture.nameJa}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
                  City (市区町村)
                </label>
                <input
                  type="text"
                  name="city"
                  value={formData.city}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="渋谷区"
                />
              </div>

              <div>
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
                  Address Line (住所)
                </label>
                <input
                  type="text"
                  name="address_line"
                  value={formData.address_line}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="神南1-2-3 神南マンション101号"
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
                      value={formData.birth_date || ''}
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
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      Nationality (国籍)
                    </label>
                    <select
                      name="nationality"
                      value={formData.nationality || ''}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">選択してください</option>
                      {NATIONALITIES.map((nationality) => (
                        <option key={nationality} value={nationality}>
                          {nationality}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label
                      className="block text-sm font-medium mb-2"
                      style={{ color: 'var(--text-primary)' }}
                    >
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
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
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
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
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
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
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

          {/* Photo Upload with 3cm x 4cm Cropping */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
              Profile Photo (証明写真) - 3cm x 4cm
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
                    <p className="text-sm text-gray-600">Click to upload a professional photo</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Photo will be automatically cropped to 3cm x 4cm
                    </p>
                  </label>
                </div>
              </div>

              <div className="flex gap-4">
                {photoPreview && (
                  <div className="relative">
                    <p className="text-xs text-center mb-2">Original</p>
                    <img
                      src={photoPreview}
                      alt="Original preview"
                      className="w-20 h-24 object-cover border rounded-lg"
                    />
                  </div>
                )}

                {croppedPhoto && (
                  <div className="relative">
                    <p className="text-xs text-center mb-2">Cropped (3cm x 4cm)</p>
                    <img
                      src={croppedPhoto}
                      alt="Cropped preview"
                      className="w-16 h-21 object-cover border rounded-lg"
                      style={{ width: '48px', height: '64px' }}
                    />
                    <button
                      type="button"
                      onClick={removePhoto}
                      className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center shadow-lg transition-all duration-200 hover:shadow-xl hover:scale-110 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                      title="Remove Photo"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                )}
              </div>
            </div>
            <canvas ref={canvasRef} className="hidden" />
          </Card>

          {/* Work Experience Section */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                Work Experience (職歴)
              </h2>
              <button
                type="button"
                onClick={addWorkExperience}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow-sm transition-all duration-200 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <Plus className="h-4 w-4" />
                Add Experience
              </button>
            </div>

            {formData.work_experiences.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No work experience added yet. Click "Add Experience" to get started.
              </p>
            ) : (
              <div className="space-y-6">
                {formData.work_experiences.map((exp, index) => (
                  <div key={exp.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium">Experience {index + 1}</h3>
                      <button
                        type="button"
                        onClick={() => removeWorkExperience(exp.id)}
                        className="inline-flex items-center justify-center w-8 h-8 text-red-500 hover:text-white hover:bg-red-500 rounded-full transition-all duration-200 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                        title="Remove Experience"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">Company Name</label>
                        <input
                          type="text"
                          value={exp.company_name}
                          onChange={(e) =>
                            updateWorkExperience(exp.id, 'company_name', e.target.value)
                          }
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="株式会社例"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">Position Title</label>
                        <input
                          type="text"
                          value={exp.position_title}
                          onChange={(e) =>
                            updateWorkExperience(exp.id, 'position_title', e.target.value)
                          }
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="ソフトウェアエンジニア"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">Location</label>
                        <input
                          type="text"
                          value={exp.location}
                          onChange={(e) => updateWorkExperience(exp.id, 'location', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="東京都渋谷区"
                        />
                      </div>

                      <div>
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={exp.is_current}
                            onChange={(e) =>
                              updateWorkExperience(exp.id, 'is_current', e.target.checked)
                            }
                            className="mr-2"
                          />
                          <span className="text-sm">Current Position</span>
                        </label>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">Start Date</label>
                        <input
                          type="month"
                          value={exp.start_date}
                          onChange={(e) =>
                            updateWorkExperience(exp.id, 'start_date', e.target.value)
                          }
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      {!exp.is_current && (
                        <div>
                          <label className="block text-sm font-medium mb-1">End Date</label>
                          <input
                            type="month"
                            value={exp.end_date}
                            onChange={(e) =>
                              updateWorkExperience(exp.id, 'end_date', e.target.value)
                            }
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          />
                        </div>
                      )}
                    </div>

                    <div className="mt-4">
                      <label className="block text-sm font-medium mb-1">Description</label>
                      <textarea
                        value={exp.description}
                        onChange={(e) =>
                          updateWorkExperience(exp.id, 'description', e.target.value)
                        }
                        rows={3}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="仕事内容や責任を説明してください..."
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Education Section */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
                Education (学歴)
              </h2>
              <button
                type="button"
                onClick={addEducation}
                className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-lg shadow-sm transition-all duration-200 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
              >
                <Plus className="h-4 w-4" />
                Add Education
              </button>
            </div>

            {formData.educations.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No education added yet. Click "Add Education" to get started.
              </p>
            ) : (
              <div className="space-y-6">
                {formData.educations.map((edu, index) => (
                  <div key={edu.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-medium">Education {index + 1}</h3>
                      <button
                        type="button"
                        onClick={() => removeEducation(edu.id)}
                        className="inline-flex items-center justify-center w-8 h-8 text-red-500 hover:text-white hover:bg-red-500 rounded-full transition-all duration-200 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                        title="Remove Education"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">Institution Name</label>
                        <input
                          type="text"
                          value={edu.institution_name}
                          onChange={(e) =>
                            updateEducation(edu.id, 'institution_name', e.target.value)
                          }
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="東京大学"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">Degree</label>
                        <input
                          type="text"
                          value={edu.degree}
                          onChange={(e) => updateEducation(edu.id, 'degree', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="学士"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">Field of Study</label>
                        <input
                          type="text"
                          value={edu.field_of_study}
                          onChange={(e) =>
                            updateEducation(edu.id, 'field_of_study', e.target.value)
                          }
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="情報工学"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">Location</label>
                        <input
                          type="text"
                          value={edu.location}
                          onChange={(e) => updateEducation(edu.id, 'location', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="東京都"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">Start Date</label>
                        <input
                          type="month"
                          value={edu.start_date}
                          onChange={(e) => updateEducation(edu.id, 'start_date', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">
                          {edu.is_current ? 'Expected Graduation' : 'End Date'}
                        </label>
                        <input
                          type="month"
                          value={edu.end_date}
                          onChange={(e) => updateEducation(edu.id, 'end_date', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>

                      <div>
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={edu.is_current}
                            onChange={(e) =>
                              updateEducation(edu.id, 'is_current', e.target.checked)
                            }
                            className="mr-2"
                          />
                          <span className="text-sm">Currently Studying</span>
                        </label>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-1">GPA (Optional)</label>
                        <input
                          type="text"
                          value={edu.gpa || ''}
                          onChange={(e) => updateEducation(edu.id, 'gpa', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                          placeholder="3.8/4.0"
                        />
                      </div>
                    </div>

                    <div className="mt-4">
                      <label className="block text-sm font-medium mb-1">
                        Description (Optional)
                      </label>
                      <textarea
                        value={edu.description || ''}
                        onChange={(e) => updateEducation(edu.id, 'description', e.target.value)}
                        rows={2}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="特記事項、卒業論文、取得した資格など..."
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>

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
                  value={formData.professional_summary}
                  onChange={handleInputChange}
                  rows={5}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="ご自身の経験やスキルについて簡潔にまとめてください..."
                />
              </div>

              <div>
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
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
            </div>
          </Card>

          {/* Settings with Status and Visibility Explanation */}
          <Card className="p-6">
            <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
              Resume Settings
            </h2>

            {/* Status Explanation */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h3 className="font-semibold text-blue-800 mb-2">📝 Resume Status Explanation</h3>
              <div className="text-sm text-blue-700 space-y-2">
                <div>
                  <strong>Status Options:</strong>
                  <ul className="ml-4 mt-1">
                    <li>
                      • <strong>Draft (下書き):</strong> Resume is private, only you can see it
                    </li>
                    <li>
                      • <strong>Published (公開中):</strong> Resume is public, searchable, and
                      downloadable by others
                    </li>
                  </ul>
                </div>
                <div className="mt-3 p-2 bg-green-50 border border-green-200 rounded">
                  <strong className="text-green-800">📢 Note:</strong>
                  <span className="text-green-700">
                    {' '}
                    When you publish your resume, it becomes searchable by employers and allows PDF
                    downloads automatically.
                  </span>
                </div>
              </div>
            </div>

            <div className="max-w-md">
              <div>
                <label
                  className="block text-sm font-medium mb-2"
                  style={{ color: 'var(--text-primary)' }}
                >
                  Resume Status (ステータス)
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={ResumeStatus.DRAFT}>📝 Draft (下書き) - Private only</option>
                  <option value={ResumeStatus.PUBLISHED}>
                    🌐 Published (公開中) - Public & Searchable
                  </option>
                </select>
              </div>

              {/* Status indicator */}
              <div className="mt-3 p-3 rounded-lg border">
                {formData.status === ResumeStatus.DRAFT ? (
                  <div className="flex items-center gap-2 text-gray-600">
                    <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                    <span className="text-sm">Private - Only visible to you</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 text-green-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm">Public - Searchable & Downloadable by employers</span>
                  </div>
                )}
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
            <Button type="submit" disabled={loading}>
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
