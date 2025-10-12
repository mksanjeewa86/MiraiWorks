'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Card, LoadingSpinner } from '@/components/ui';
import { recruiterProfileApi } from '@/api/recruiterProfile';
import type { RecruiterProfile } from '@/types/recruiter';
import { AlertCircle, Briefcase, Building, MapPin, Calendar, Users, TrendingUp } from 'lucide-react';

interface RecruiterProfileViewProps {
  userId?: number;
  isOwnProfile?: boolean;
  readOnly?: boolean;
}

export default function RecruiterProfileView({
  userId,
  isOwnProfile = true,
  readOnly = false,
}: RecruiterProfileViewProps) {
  const t = useTranslations('profile');
  const [profile, setProfile] = useState<RecruiterProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        if (isOwnProfile) {
          const data = await recruiterProfileApi.getMyProfile();
          setProfile(data);
        } else if (userId) {
          const data = await recruiterProfileApi.getProfileByUserId(userId);
          setProfile(data);
        }
      } catch (err: any) {
        console.error('Error fetching recruiter profile:', err);
        setError(err.message || 'Failed to load recruiter profile');
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [userId, isOwnProfile]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner className="w-8 h-8" />
      </div>
    );
  }

  if (error || !profile) {
    return (
      <Card className="p-6">
        <div className="flex items-center gap-2 text-yellow-600 dark:text-yellow-400">
          <AlertCircle className="h-5 w-5" />
          <p>No recruiter profile found. {isOwnProfile && 'Create one to get started!'}</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* About Section */}
      {profile.bio && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            About
          </h2>
          <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
            {profile.bio}
          </p>

          {profile.years_of_experience && (
            <div className="flex items-center gap-2 mt-4 text-sm" style={{ color: 'var(--text-muted)' }}>
              <Calendar className="h-4 w-4" />
              <span>{profile.years_of_experience} years of recruitment experience</span>
            </div>
          )}
        </Card>
      )}

      {/* Specializations */}
      {profile.specializations && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Briefcase className="h-5 w-5" />
            Specializations
          </h2>
          <div className="flex flex-wrap gap-2">
            {profile.specializations.split(',').map((spec, index) => (
              <span
                key={index}
                className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
              >
                {spec.trim()}
              </span>
            ))}
          </div>
        </Card>
      )}

      {/* Recruitment Focus */}
      {(profile.industries || profile.job_types || profile.locations || profile.experience_levels) && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <TrendingUp className="h-5 w-5" />
            Recruitment Focus
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {profile.industries && (
              <div>
                <h3 className="font-medium text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
                  Industries
                </h3>
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  {profile.industries}
                </p>
              </div>
            )}

            {profile.job_types && (
              <div>
                <h3 className="font-medium text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
                  Job Types
                </h3>
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  {profile.job_types}
                </p>
              </div>
            )}

            {profile.locations && (
              <div>
                <h3 className="font-medium text-sm mb-2 flex items-center gap-1" style={{ color: 'var(--text-secondary)' }}>
                  <MapPin className="h-4 w-4" />
                  Locations
                </h3>
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  {profile.locations}
                </p>
              </div>
            )}

            {profile.experience_levels && (
              <div>
                <h3 className="font-medium text-sm mb-2" style={{ color: 'var(--text-secondary)' }}>
                  Experience Levels
                </h3>
                <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  {profile.experience_levels}
                </p>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Activity Stats */}
      {(profile.jobs_posted !== null || profile.candidates_placed !== null || profile.active_openings !== null) && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Users className="h-5 w-5" />
            Activity
          </h2>
          <div className="grid grid-cols-3 gap-4 text-center">
            {profile.jobs_posted !== null && (
              <div>
                <div className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>
                  {profile.jobs_posted}
                </div>
                <div className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  Jobs Posted
                </div>
              </div>
            )}

            {profile.candidates_placed !== null && (
              <div>
                <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {profile.candidates_placed}
                </div>
                <div className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  Candidates Placed
                </div>
              </div>
            )}

            {profile.active_openings !== null && (
              <div>
                <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {profile.active_openings}
                </div>
                <div className="text-sm" style={{ color: 'var(--text-muted)' }}>
                  Active Openings
                </div>
              </div>
            )}
          </div>
        </Card>
      )}

      {/* Company Description */}
      {profile.company_description && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
            <Building className="h-5 w-5" />
            Company
          </h2>
          <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
            {profile.company_description}
          </p>
        </Card>
      )}

      {/* Contact Links */}
      {(profile.linkedin_url || profile.calendar_link) && (
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Connect
          </h2>
          <div className="flex flex-col gap-3">
            {profile.linkedin_url && (
              <a
                href={profile.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline"
              >
                LinkedIn Profile →
              </a>
            )}

            {profile.calendar_link && (
              <a
                href={profile.calendar_link}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline"
              >
                <Calendar className="h-4 w-4" />
                Schedule a Meeting →
              </a>
            )}
          </div>
        </Card>
      )}
    </div>
  );
}
