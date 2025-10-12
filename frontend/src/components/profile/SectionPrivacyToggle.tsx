'use client';

import { useState, useEffect } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { privacyApi, PrivacySettingsUpdate } from '@/api/privacy';
import { useTranslations } from 'next-intl';

interface SectionPrivacyToggleProps {
  sectionKey: 'show_work_experience' | 'show_education' | 'show_skills' | 'show_certifications' | 'show_projects' | 'show_resume';
  isOwnProfile: boolean;
  readOnly?: boolean;
}

export default function SectionPrivacyToggle({
  sectionKey,
  isOwnProfile,
  readOnly = false
}: SectionPrivacyToggleProps) {
  const t = useTranslations('profile');
  const [isVisible, setIsVisible] = useState(true);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPrivacySettings = async () => {
      try {
        const settings = await privacyApi.getMySettings();
        setIsVisible(settings[sectionKey]);
      } catch (err) {
        console.error('Failed to load privacy settings:', err);
      }
    };

    if (isOwnProfile) {
      fetchPrivacySettings();
    }
  }, [sectionKey, isOwnProfile]);

  const handleToggle = async () => {
    if (readOnly || !isOwnProfile) return;

    setLoading(true);
    try {
      const newValue = !isVisible;
      await privacyApi.updateMySettings({
        [sectionKey]: newValue,
      } as PrivacySettingsUpdate);
      setIsVisible(newValue);
    } catch (err) {
      console.error('Failed to update privacy settings:', err);
    } finally {
      setLoading(false);
    }
  };

  // Don't show toggle if not own profile or in read-only mode
  if (!isOwnProfile || readOnly) {
    return null;
  }

  return (
    <button
      onClick={handleToggle}
      disabled={loading}
      className={`
        flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium
        transition-all duration-200
        ${isVisible
          ? 'bg-green-50 text-green-700 hover:bg-green-100 dark:bg-green-900/20 dark:text-green-400'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400'
        }
        ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      title={isVisible ? t('privacy.visibleToOthers') : t('privacy.hiddenFromOthers')}
    >
      {isVisible ? (
        <Eye className="h-4 w-4" />
      ) : (
        <EyeOff className="h-4 w-4" />
      )}
      <span className="hidden sm:inline">
        {isVisible ? t('privacy.visible') : t('privacy.hidden')}
      </span>
    </button>
  );
}
