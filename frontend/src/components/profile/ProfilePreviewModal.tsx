'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Image from 'next/image';
import {
  Dialog,
  DialogContent,
} from '@/components/ui/dialog';
import { Card } from '@/components/ui';
import UnifiedProfileView from './UnifiedProfileView';
import { X, MapPin, Mail, Phone } from 'lucide-react';
import { usersApi } from '@/api/users';
import { userSettingsApi } from '@/api/userSettings';
import { profileViewsApi } from '@/api/profileViews';
import type { UserManagement } from '@/types/user';
import type { UserProfile } from '@/types';

interface ProfilePreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  userId: number;
  viewAsRole?: string; // Optional: to simulate viewing as a specific role
}

export default function ProfilePreviewModal({
  isOpen,
  onClose,
  userId,
  viewAsRole,
}: ProfilePreviewModalProps) {
  const t = useTranslations('profile');
  const [user, setUser] = useState<UserManagement | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewStartTime] = useState<number>(Date.now());

  // Fetch user data when modal opens
  useEffect(() => {
    if (isOpen && userId) {
      const fetchUser = async () => {
        setLoading(true);
        setError(null);
        try {
          // Fetch basic user data
          const userResponse = await usersApi.getById(userId);
          if (userResponse.data) {
            setUser(userResponse.data);
          }

          // Try to fetch profile data (avatar, cover photo, etc.)
          try {
            const profileResponse = await userSettingsApi.getProfile();
            if (profileResponse.data) {
              setUserProfile(profileResponse.data);
            }
          } catch (profileErr) {
            console.log('Profile data not available:', profileErr);
            // Profile data is optional, continue without it
          }

          // Record profile view (async, don't wait for it)
          profileViewsApi.recordView({
            profile_user_id: userId,
            referrer: window.location.href,
          }).catch((err) => {
            console.log('Failed to record profile view:', err);
            // Don't show error to user, view tracking is background functionality
          });
        } catch (err: any) {
          console.error('Error fetching user:', err);
          setError('Failed to load profile');
        } finally {
          setLoading(false);
        }
      };

      fetchUser();
    }
  }, [isOpen, userId]);

  // Record view duration when modal closes
  useEffect(() => {
    return () => {
      if (isOpen && userId) {
        const viewDuration = Math.floor((Date.now() - viewStartTime) / 1000);

        // Only record duration if user spent at least 3 seconds viewing
        if (viewDuration >= 3) {
          profileViewsApi.recordView({
            profile_user_id: userId,
            view_duration: viewDuration,
            referrer: window.location.href,
          }).catch((err) => {
            console.log('Failed to record view duration:', err);
          });
        }
      }
    };
  }, [isOpen, userId, viewStartTime]);

  const getInitials = (firstName?: string, lastName?: string) => {
    if (!firstName && !lastName) return 'U';
    return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-7xl max-h-[95vh] overflow-hidden p-0">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-50 p-2 rounded-full bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm hover:bg-white dark:hover:bg-gray-900 transition-colors shadow-lg"
        >
          <X className="h-5 w-5 text-gray-700 dark:text-gray-300" />
        </button>

        {/* Scrollable content */}
        <div className="overflow-y-auto max-h-[95vh]">
          {loading && (
            <div className="flex items-center justify-center py-20">
              <div className="loading-spinner" />
            </div>
          )}

          {error && (
            <div className="flex items-center justify-center py-20">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {!loading && !error && user && (
            <div className="bg-gray-50 dark:bg-gray-900 min-h-screen">
              {/* Cover Photo Section - Same as main profile */}
              <div className="relative h-48 lg:h-60 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500">
                {userProfile?.cover_photo_url && (
                  <Image
                    src={userProfile.cover_photo_url}
                    alt="Cover photo"
                    fill
                    unoptimized
                    className="object-cover"
                    priority
                  />
                )}
                {/* Preview Mode Badge - Top Right */}
                <div className="absolute top-4 right-16 inline-flex items-center px-4 py-2 rounded-lg bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border border-blue-200 dark:border-blue-700 shadow-lg">
                  <span className="text-sm font-semibold text-blue-700 dark:text-blue-300">
                    Preview Mode
                  </span>
                </div>
              </div>

              {/* Main Content Container - Same as main profile */}
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Profile Header Card - Overlaps cover photo */}
                <div className="relative -mt-16 lg:-mt-20">
                  <Card className="p-6">
                    <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
                      {/* Avatar and Basic Info */}
                      <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
                        {/* Avatar - Same size and styling as main profile */}
                        <div className="relative">
                          {userProfile?.avatar_url ? (
                            <Image
                              src={userProfile.avatar_url}
                              alt="Profile picture"
                              width={160}
                              height={160}
                              unoptimized
                              className="w-32 h-32 lg:w-40 lg:h-40 rounded-full object-cover border-4 border-white dark:border-gray-800 shadow-lg"
                            />
                          ) : (
                            <div className="w-32 h-32 lg:w-40 lg:h-40 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-4xl font-bold border-4 border-white dark:border-gray-800 shadow-lg">
                              {getInitials(user.first_name, user.last_name)}
                            </div>
                          )}
                        </div>

                        {/* Name and Title Section */}
                        <div className="flex-1 text-center sm:text-left">
                          <h1
                            className="text-2xl lg:text-3xl font-bold mb-2"
                            style={{ color: 'var(--text-primary)' }}
                          >
                            {user.first_name} {user.last_name}
                          </h1>
                          <p className="text-lg lg:text-xl mb-3" style={{ color: 'var(--text-secondary)' }}>
                            {userProfile?.job_title || 'Professional'}
                          </p>
                          {user.company_name && (
                            <div
                              className="flex flex-wrap items-center justify-center sm:justify-start gap-2 text-sm mb-3"
                              style={{ color: 'var(--text-muted)' }}
                            >
                              <div className="flex items-center gap-1">
                                <MapPin className="h-4 w-4" />
                                <span>{user.company_name}</span>
                              </div>
                            </div>
                          )}
                          {userProfile?.bio && (
                            <p className="text-sm mt-4 text-center sm:text-left" style={{ color: 'var(--text-secondary)' }}>
                              {userProfile.bio}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Contact Info Bar */}
                    <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                      <div className="flex flex-wrap gap-6">
                        {userProfile?.email && (
                          <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                            <Mail className="h-4 w-4" />
                            <span>{userProfile.email}</span>
                          </div>
                        )}
                        {userProfile?.phone && (
                          <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
                            <Phone className="h-4 w-4" />
                            <span>{userProfile.phone}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </Card>
                </div>

                {/* Profile Sections using UnifiedProfileView */}
                <div className="mt-6 space-y-6 pb-8">
                  <UnifiedProfileView
                    userId={userId}
                    isOwnProfile={false}
                    readOnly={true}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
