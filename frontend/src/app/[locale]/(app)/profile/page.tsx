'use client';

import { useState, useEffect, useRef } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Card } from '@/components/ui';
import { Button } from '@/components/ui';
import { LoadingSpinner } from '@/components/ui';
import { userSettingsApi } from '@/api/userSettings';
import { UserProfile, UserProfileUpdate } from '@/types';
import { API_ENDPOINTS } from '@/api/config';
import {
  Edit,
  MapPin,
  Mail,
  Phone,
  Camera,
  Eye,
  BarChart3,
} from 'lucide-react';
import { makeAuthenticatedRequest } from '@/api/apiClient';
import { useTranslations } from 'next-intl';
import ImageCropModal from '@/components/ui/ImageCropModal';
import UnifiedProfileView from '@/components/profile/UnifiedProfileView';
import ProfilePreviewModal from '@/components/profile/ProfilePreviewModal';

function ProfilePageContent() {
  const { user } = useAuth();
  const router = useRouter();
  const t = useTranslations('profile');
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState<UserProfileUpdate>({});
  const [error, setError] = useState<string | null>(null);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [cropModalOpen, setCropModalOpen] = useState(false);
  const [imageToCrop, setImageToCrop] = useState<string>('');
  const [originalFileName, setOriginalFileName] = useState<string>('');

  // Cover photo states
  const [uploadingCover, setUploadingCover] = useState(false);
  const [coverPhotoUrl, setCoverPhotoUrl] = useState<string | null>(null);
  const coverInputRef = useRef<HTMLInputElement>(null);
  const [coverCropModalOpen, setCoverCropModalOpen] = useState(false);
  const [coverImageToCrop, setCoverImageToCrop] = useState<string>('');
  const [coverOriginalFileName, setCoverOriginalFileName] = useState<string>('');

  // Profile preview modal state
  const [previewModalOpen, setPreviewModalOpen] = useState(false);

  useEffect(() => {
    const loadProfileData = async () => {
      if (!user) {
        setLoading(false);
        return;
      }

      try {
        const response = await userSettingsApi.getProfile();
        setUserProfile(response.data);
        setAvatarUrl(response.data.avatar_url ?? null);
        setCoverPhotoUrl(response.data.cover_photo_url ?? null);
        setEditForm({
          first_name: response.data.first_name,
          last_name: response.data.last_name,
          phone: response.data.phone,
          job_title: response.data.job_title,
          bio: response.data.bio,
        });
      } catch (err) {
        console.error('Failed to load profile data:', err);
        setError(t('errors.failedToLoad'));
      } finally {
        setLoading(false);
      }
    };

    loadProfileData();
  }, [user]);

  const handleSaveProfile = async () => {
    if (!userProfile) return;

    setSaving(true);
    setError(null);

    try {
      const response = await userSettingsApi.updateProfile(editForm);
      setUserProfile(response.data);
      setEditing(false);
    } catch (err) {
      console.error('Failed to update profile:', err);
      setError(t('errors.failedToUpdate'));
    } finally {
      setSaving(false);
    }
  };

  const handleCancelEdit = () => {
    if (userProfile) {
      setEditForm({
        first_name: userProfile.first_name,
        last_name: userProfile.last_name,
        phone: userProfile.phone,
        job_title: userProfile.job_title,
        bio: userProfile.bio,
      });
    }
    setEditing(false);
    setError(null);
  };

  const handleAvatarUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validImageTypes = [
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/gif',
      'image/webp',
      'image/svg+xml'
    ];
    const validExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'];
    const fileName = file.name.toLowerCase();
    const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
    const hasValidMimeType = validImageTypes.includes(file.type.toLowerCase()) || file.type.startsWith('image/');

    if (!hasValidMimeType && !hasValidExtension) {
      setError(t('errors.invalidFileType'));
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      setError(t('errors.fileTooLarge'));
      return;
    }

    setError(null);
    setUploadingAvatar(true);

    try {
      const ext = fileName.split('.').pop()?.toLowerCase();

      // HEIC/HEIF files are not supported in browsers
      // Show helpful error message
      if (ext === 'heic' || ext === 'heif') {
        setError('HEIC/HEIF format is not supported. Please convert your image to JPG or PNG format first, or take a new photo in a different format.');
        setUploadingAvatar(false);
        return;
      }

      // Create image URL for cropping
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        setImageToCrop(result);
        setOriginalFileName(file.name);
        setCropModalOpen(true);
        setUploadingAvatar(false);
      };
      reader.onerror = () => {
        setError('Failed to read image file');
        setUploadingAvatar(false);
      };
      reader.readAsDataURL(file);
    } catch (err) {
      console.error('Error processing image:', err);
      setError('Failed to process image. Please try a different file.');
      setUploadingAvatar(false);
    }

    // Clear the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleCropComplete = async (croppedBlob: Blob, croppedUrl: string) => {
    setUploadingAvatar(true);
    setError(null);

    try {
      // Create FormData for file upload with cropped image
      const formData = new FormData();
      const croppedFile = new File([croppedBlob], originalFileName, { type: 'image/jpeg' });
      formData.append('file', croppedFile);

      // Upload to files API
      const response = await makeAuthenticatedRequest<{
        file_url: string;
        file_name: string;
        file_size: number;
        file_type: string;
        s3_key: string;
        success: boolean;
      }>(API_ENDPOINTS.FILES.UPLOAD, {
        method: 'POST',
        body: formData,
        headers: {}, // Don't set Content-Type for FormData
      });

      if (response.data.success) {
        const newAvatarUrl = response.data.file_url;
        setAvatarUrl(newAvatarUrl);

        // Save avatar URL to backend
        try {
          await makeAuthenticatedRequest(API_ENDPOINTS.USER.UPDATE_PROFILE, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              avatar_url: newAvatarUrl,
            }),
          });
        } catch (err) {
          console.error('Failed to save avatar URL:', err);
          setError(t('errors.avatarSaveFailed'));
        }
      }
    } catch (err) {
      console.error('Failed to upload avatar:', err);
      setError(t('errors.avatarUploadFailed'));
    } finally {
      setUploadingAvatar(false);
    }
  };

  const handleAvatarClick = () => {
    if (editing && fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Cover photo handlers
  const handleCoverPhotoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validImageTypes = [
      'image/jpeg',
      'image/jpg',
      'image/png',
      'image/gif',
      'image/webp',
      'image/svg+xml'
    ];
    const validExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'];
    const fileName = file.name.toLowerCase();
    const hasValidExtension = validExtensions.some(ext => fileName.endsWith(ext));
    const hasValidMimeType = validImageTypes.includes(file.type.toLowerCase()) || file.type.startsWith('image/');

    if (!hasValidMimeType && !hasValidExtension) {
      setError(t('errors.invalidFileType'));
      return;
    }

    // Validate file size (10MB max for cover photos)
    if (file.size > 10 * 1024 * 1024) {
      setError(t('errors.fileTooLarge'));
      return;
    }

    setError(null);
    setUploadingCover(true);

    try {
      const ext = fileName.split('.').pop()?.toLowerCase();

      // HEIC/HEIF files are not supported in browsers
      if (ext === 'heic' || ext === 'heif') {
        setError('HEIC/HEIF format is not supported. Please convert your image to JPG or PNG format first, or take a new photo in a different format.');
        setUploadingCover(false);
        return;
      }

      // Create image URL for cropping
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        setCoverImageToCrop(result);
        setCoverOriginalFileName(file.name);
        setCoverCropModalOpen(true);
        setUploadingCover(false);
      };
      reader.onerror = () => {
        setError('Failed to read image file');
        setUploadingCover(false);
      };
      reader.readAsDataURL(file);
    } catch (err) {
      console.error('Error processing image:', err);
      setError('Failed to process image. Please try a different file.');
      setUploadingCover(false);
    }

    // Clear the file input
    if (coverInputRef.current) {
      coverInputRef.current.value = '';
    }
  };

  const handleCoverCropComplete = async (croppedBlob: Blob, croppedUrl: string) => {
    setUploadingCover(true);
    setError(null);

    try {
      // Create FormData for file upload with cropped image
      const formData = new FormData();
      const croppedFile = new File([croppedBlob], coverOriginalFileName, { type: 'image/jpeg' });
      formData.append('file', croppedFile);

      // Upload to files API
      const response = await makeAuthenticatedRequest<{
        file_url: string;
        file_name: string;
        file_size: number;
        file_type: string;
        s3_key: string;
        success: boolean;
      }>(API_ENDPOINTS.FILES.UPLOAD, {
        method: 'POST',
        body: formData,
        headers: {}, // Don't set Content-Type for FormData
      });

      if (response.data.success) {
        const newCoverPhotoUrl = response.data.file_url;
        setCoverPhotoUrl(newCoverPhotoUrl);

        // Save cover photo URL to backend
        try {
          await makeAuthenticatedRequest(API_ENDPOINTS.USER.UPDATE_PROFILE, {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              cover_photo_url: newCoverPhotoUrl,
            }),
          });
        } catch (err) {
          console.error('Failed to save cover photo URL:', err);
          setError(t('errors.avatarSaveFailed'));
        }
      }
    } catch (err) {
      console.error('Failed to upload cover photo:', err);
      setError(t('errors.avatarUploadFailed'));
    } finally {
      setUploadingCover(false);
    }
  };

  const handleCoverPhotoClick = () => {
    if (editing && coverInputRef.current) {
      coverInputRef.current.click();
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

  if (!userProfile) {
    return (
      <AppLayout>
        <div className="flex flex-col items-center justify-center h-64">
          <div className="text-6xl mb-4">👤</div>
          <h3 className="text-xl font-bold text-gray-900 mb-2">{t('emptyStates.noProfileData')}</h3>
          <p className="text-gray-600 mb-6">{t('emptyStates.loginRequired')}</p>
          <Button>{t('emptyStates.createProfile')}</Button>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
        {/* Cover Photo Section */}
        <div className="relative h-48 lg:h-60 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500">
          {coverPhotoUrl ? (
            <Image
              src={coverPhotoUrl}
              alt="Cover photo"
              fill
              unoptimized
              className="object-cover"
              priority
              loading="eager"
            />
          ) : null}
          {editing && (
            <button
              onClick={handleCoverPhotoClick}
              disabled={uploadingCover}
              className="absolute top-4 right-4 inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border border-gray-200/50 dark:border-gray-700/50 text-gray-700 dark:text-gray-300 text-sm font-semibold hover:bg-white dark:hover:bg-gray-900 hover:shadow-lg hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
            >
              <Camera className="h-4 w-4" />
              <span>{uploadingCover ? t('actions.uploading') : t('actions.editCover')}</span>
            </button>
          )}
          <input
            ref={coverInputRef}
            type="file"
            accept="image/jpeg,image/jpg,image/png,image/gif,image/webp,.jpg,.jpeg,.png,.gif,.webp"
            onChange={handleCoverPhotoUpload}
            className="hidden"
          />
        </div>

        {/* Main Content Container */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Profile Header Card - Overlaps cover photo */}
          <div className="relative -mt-16 lg:-mt-20">
            <Card className="p-6">
              <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
                {/* Avatar and Basic Info */}
                <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
                  {/* Avatar */}
                  <div className="relative">
                    {avatarUrl ? (
                      <Image
                        src={avatarUrl}
                        alt="Profile picture"
                        width={160}
                        height={160}
                        unoptimized
                        className="w-32 h-32 lg:w-40 lg:h-40 rounded-full object-cover border-4 border-white dark:border-gray-800 shadow-lg"
                        priority
                        loading="eager"
                      />
                    ) : (
                      <div className="w-32 h-32 lg:w-40 lg:h-40 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-4xl font-bold border-4 border-white dark:border-gray-800 shadow-lg">
                        {userProfile.full_name
                          .split(' ')
                          .map((n) => n[0])
                          .join('')}
                      </div>
                    )}
                    {editing && (
                      <Button
                        size="sm"
                        className="absolute bottom-0 right-0 rounded-full p-2 shadow-lg"
                        onClick={handleAvatarClick}
                        disabled={uploadingAvatar}
                      >
                        <Camera className="h-4 w-4" />
                      </Button>
                    )}
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/jpeg,image/jpg,image/png,image/gif,image/webp,.jpg,.jpeg,.png,.gif,.webp"
                      onChange={handleAvatarUpload}
                      className="hidden"
                    />
                  </div>

                  {/* Name and Title Section */}
                  <div className="flex-1 text-center sm:text-left">
                    {editing ? (
                      <div className="space-y-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                          <div>
                            <label
                              className="block text-sm font-medium mb-1"
                              style={{ color: 'var(--text-primary)' }}
                            >
                              {t('overview.firstName')}
                            </label>
                            <input
                              type="text"
                              className="input w-full"
                              value={editForm.first_name || ''}
                              onChange={(e) =>
                                setEditForm({ ...editForm, first_name: e.target.value })
                              }
                            />
                          </div>
                          <div>
                            <label
                              className="block text-sm font-medium mb-1"
                              style={{ color: 'var(--text-primary)' }}
                            >
                              {t('overview.lastName')}
                            </label>
                            <input
                              type="text"
                              className="input w-full"
                              value={editForm.last_name || ''}
                              onChange={(e) =>
                                setEditForm({ ...editForm, last_name: e.target.value })
                              }
                            />
                          </div>
                        </div>
                        <div>
                          <label
                            className="block text-sm font-medium mb-1"
                            style={{ color: 'var(--text-primary)' }}
                          >
                            {t('overview.jobTitle')}
                          </label>
                          <input
                            type="text"
                            className="input w-full"
                            value={editForm.job_title || ''}
                            onChange={(e) => setEditForm({ ...editForm, job_title: e.target.value })}
                          />
                        </div>
                        <div>
                          <label
                            className="block text-sm font-medium mb-1"
                            style={{ color: 'var(--text-primary)' }}
                          >
                            {t('overview.contact.phone')}
                          </label>
                          <input
                            type="tel"
                            className="input w-full"
                            value={editForm.phone || ''}
                            onChange={(e) => setEditForm({ ...editForm, phone: e.target.value })}
                          />
                        </div>
                        <div>
                          <label
                            className="block text-sm font-medium mb-1"
                            style={{ color: 'var(--text-primary)' }}
                          >
                            {t('overview.bio')}
                          </label>
                          <textarea
                            className="input w-full"
                            rows={4}
                            value={editForm.bio || ''}
                            onChange={(e) => setEditForm({ ...editForm, bio: e.target.value })}
                            placeholder={t('overview.bioPlaceholder')}
                          />
                        </div>
                      </div>
                    ) : (
                      <>
                        <h1
                          className="text-2xl lg:text-3xl font-bold mb-2"
                          style={{ color: 'var(--text-primary)' }}
                        >
                          {userProfile.full_name}
                        </h1>
                        <p className="text-lg lg:text-xl mb-3" style={{ color: 'var(--text-secondary)' }}>
                          {userProfile.job_title || 'Professional'}
                        </p>
                        {user?.company && (
                          <div
                            className="flex flex-wrap items-center justify-center sm:justify-start gap-2 text-sm mb-3"
                            style={{ color: 'var(--text-muted)' }}
                          >
                            <div className="flex items-center gap-1">
                              <MapPin className="h-4 w-4" />
                              <span>{user.company.name}</span>
                            </div>
                          </div>
                        )}
                        {userProfile.bio && (
                          <p className="text-sm mt-4 text-center sm:text-left" style={{ color: 'var(--text-secondary)' }}>
                            {userProfile.bio}
                          </p>
                        )}
                      </>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex flex-col gap-2 items-stretch">
                  {!editing ? (
                    <div className="flex flex-col sm:flex-row gap-2 flex-wrap">
                      {/* View Analytics button - primary blue - double width */}
                      <button
                        onClick={() => router.push('/profile/analytics')}
                        className="flex-[2] min-w-[140px] inline-flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg bg-blue-600 dark:bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 dark:hover:bg-blue-700"
                      >
                        <BarChart3 className="h-4 w-4" />
                        <span>View Analytics</span>
                      </button>
                      {/* Edit button - light gray - normal width */}
                      <button
                        onClick={() => setEditing(true)}
                        className="flex-1 min-w-[100px] inline-flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 text-sm font-semibold hover:bg-gray-200 dark:hover:bg-gray-700"
                      >
                        <Edit className="h-4 w-4" />
                        <span>Edit</span>
                      </button>
                      {/* View As button - light gray - normal width */}
                      <button
                        onClick={() => user?.id && setPreviewModalOpen(true)}
                        className="flex-1 min-w-[100px] inline-flex items-center justify-center gap-2 px-3 py-1.5 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 text-sm font-semibold hover:bg-gray-200 dark:hover:bg-gray-700"
                      >
                        <Eye className="h-4 w-4" />
                        <span>View As</span>
                      </button>
                    </div>
                  ) : (
                    <>
                      <button
                        onClick={handleCancelEdit}
                        disabled={saving}
                        className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border border-gray-200/50 dark:border-gray-700/50 text-gray-700 dark:text-gray-300 text-sm font-semibold hover:bg-white dark:hover:bg-gray-900 hover:shadow-lg hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                      >
                        {t('actions.cancel')}
                      </button>
                      <button
                        onClick={handleSaveProfile}
                        disabled={saving}
                        className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-blue-600 dark:bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 dark:hover:bg-blue-700 hover:shadow-lg hover:scale-105 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                      >
                        <Edit className="h-4 w-4" />
                        <span>{saving ? t('actions.saving') : t('actions.saveProfile')}</span>
                      </button>
                    </>
                  )}
                </div>
              </div>

              {/* Contact Info Bar */}
              {!editing && (
                <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex flex-wrap gap-6">
                    <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                      <Mail className="h-4 w-4" />
                      <span>{userProfile.email}</span>
                    </div>
                    {userProfile.phone && (
                      <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                        <Phone className="h-4 w-4" />
                        <span>{userProfile.phone}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </Card>
          </div>

          {error && (
            <div className="mt-4 p-4 rounded-lg bg-red-50 border border-red-200 dark:bg-red-900/20 dark:border-red-800">
              <p className="text-red-600 dark:text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* Profile Sections using UnifiedProfileView */}
          <div className="mt-6 space-y-6 pb-8">
            <UnifiedProfileView isOwnProfile={true} readOnly={false} />
          </div>
        </div>
      </div>

      {/* Avatar Crop Modal */}
      <ImageCropModal
        isOpen={cropModalOpen}
        imageSrc={imageToCrop}
        onClose={() => setCropModalOpen(false)}
        onCropComplete={handleCropComplete}
        aspect={1}
        cropShape="round"
        title="Crop Profile Photo"
      />

      {/* Cover Photo Crop Modal */}
      <ImageCropModal
        isOpen={coverCropModalOpen}
        imageSrc={coverImageToCrop}
        onClose={() => setCoverCropModalOpen(false)}
        onCropComplete={handleCoverCropComplete}
        aspect={16 / 5}
        cropShape="rect"
        title="Crop Cover Photo"
      />

      {/* Profile Preview Modal */}
      {user?.id && (
        <ProfilePreviewModal
          isOpen={previewModalOpen}
          onClose={() => setPreviewModalOpen(false)}
          userId={user.id}
        />
      )}
    </AppLayout>
  );
}

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfilePageContent />
    </ProtectedRoute>
  );
}
