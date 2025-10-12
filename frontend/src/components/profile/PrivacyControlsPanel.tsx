'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Lock, Eye, EyeOff, Shield, Users, Building2 } from 'lucide-react';
import { toast } from 'sonner';

interface PrivacySettings {
  profileVisibility: 'public' | 'recruiters' | 'private';
  showEmail: boolean;
  showPhone: boolean;
  showWorkExperience: boolean;
  showEducation: boolean;
  showSkills: boolean;
  showCertifications: boolean;
  showProjects: boolean;
  showResume: boolean;
  searchable: boolean;
}

interface PrivacyControlsPanelProps {
  onSave?: (settings: PrivacySettings) => Promise<void>;
  initialSettings?: Partial<PrivacySettings>;
}

const defaultSettings: PrivacySettings = {
  profileVisibility: 'public',
  showEmail: false,
  showPhone: false,
  showWorkExperience: true,
  showEducation: true,
  showSkills: true,
  showCertifications: true,
  showProjects: true,
  showResume: true,
  searchable: true,
};

export default function PrivacyControlsPanel({
  onSave,
  initialSettings = {},
}: PrivacyControlsPanelProps) {
  const t = useTranslations('profile');
  const [settings, setSettings] = useState<PrivacySettings>({
    ...defaultSettings,
    ...initialSettings,
  });
  const [saving, setSaving] = useState(false);

  const handleVisibilityChange = (visibility: PrivacySettings['profileVisibility']) => {
    setSettings({ ...settings, profileVisibility: visibility });
  };

  const handleToggle = (key: keyof PrivacySettings) => {
    setSettings({ ...settings, [key]: !settings[key] });
  };

  const handleSave = async () => {
    if (!onSave) return;

    setSaving(true);
    try {
      await onSave(settings);
      toast.success('Privacy settings saved successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to save privacy settings');
    } finally {
      setSaving(false);
    }
  };

  const visibilityOptions = [
    {
      value: 'public' as const,
      icon: Eye,
      label: t('privacy.visibility.public'),
      description: 'Anyone can view your profile',
    },
    {
      value: 'recruiters' as const,
      icon: Users,
      label: t('privacy.visibility.recruiters'),
      description: 'Only recruiters can view your full profile',
    },
    {
      value: 'private' as const,
      icon: EyeOff,
      label: t('privacy.visibility.private'),
      description: 'Only you can view your profile',
    },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-blue-600" />
          <CardTitle>{t('privacy.title')}</CardTitle>
        </div>
        <CardDescription>
          Control who can see your profile information
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Profile Visibility */}
        <div className="space-y-3">
          <Label className="text-base font-semibold">{t('privacy.visibility.title')}</Label>
          <div className="grid gap-3">
            {visibilityOptions.map((option) => {
              const Icon = option.icon;
              const isSelected = settings.profileVisibility === option.value;

              return (
                <div
                  key={option.value}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    isSelected
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-900/20'
                      : 'border-gray-200 hover:border-gray-300 dark:border-gray-700'
                  }`}
                  onClick={() => handleVisibilityChange(option.value)}
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`p-2 rounded-lg ${
                        isSelected
                          ? 'bg-blue-100 dark:bg-blue-900/40'
                          : 'bg-gray-100 dark:bg-gray-800'
                      }`}
                    >
                      <Icon
                        className={`h-5 w-5 ${
                          isSelected ? 'text-blue-600' : 'text-gray-600 dark:text-gray-400'
                        }`}
                      />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium" style={{ color: 'var(--text-primary)' }}>
                        {option.label}
                      </div>
                      <div className="text-sm" style={{ color: 'var(--text-muted)' }}>
                        {option.description}
                      </div>
                    </div>
                    <div
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        isSelected
                          ? 'border-blue-600 bg-blue-600'
                          : 'border-gray-300 dark:border-gray-600'
                      }`}
                    >
                      {isSelected && <div className="w-2 h-2 rounded-full bg-white" />}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Searchability */}
        <div className="flex items-center justify-between p-4 rounded-lg bg-gray-50 dark:bg-gray-800">
          <div className="flex-1">
            <Label htmlFor="searchable" className="font-medium">
              {t('privacy.searchable')}
            </Label>
            <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
              Allow your profile to appear in search results
            </p>
          </div>
          <Switch
            id="searchable"
            checked={settings.searchable}
            onCheckedChange={() => handleToggle('searchable')}
          />
        </div>

        {/* Contact Information */}
        <div className="space-y-3">
          <Label className="text-base font-semibold">Contact Information</Label>

          <div className="flex items-center justify-between p-3 rounded-lg border">
            <div className="flex-1">
              <Label htmlFor="showEmail">{t('privacy.showEmail')}</Label>
            </div>
            <Switch
              id="showEmail"
              checked={settings.showEmail}
              onCheckedChange={() => handleToggle('showEmail')}
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg border">
            <div className="flex-1">
              <Label htmlFor="showPhone">{t('privacy.showPhone')}</Label>
            </div>
            <Switch
              id="showPhone"
              checked={settings.showPhone}
              onCheckedChange={() => handleToggle('showPhone')}
            />
          </div>
        </div>

        {/* Profile Sections */}
        <div className="space-y-3">
          <Label className="text-base font-semibold">Profile Sections</Label>

          <div className="flex items-center justify-between p-3 rounded-lg border">
            <Label htmlFor="showWorkExperience">Work Experience</Label>
            <Switch
              id="showWorkExperience"
              checked={settings.showWorkExperience}
              onCheckedChange={() => handleToggle('showWorkExperience')}
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg border">
            <Label htmlFor="showEducation">Education</Label>
            <Switch
              id="showEducation"
              checked={settings.showEducation}
              onCheckedChange={() => handleToggle('showEducation')}
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg border">
            <Label htmlFor="showSkills">Skills</Label>
            <Switch
              id="showSkills"
              checked={settings.showSkills}
              onCheckedChange={() => handleToggle('showSkills')}
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg border">
            <Label htmlFor="showCertifications">Certifications</Label>
            <Switch
              id="showCertifications"
              checked={settings.showCertifications}
              onCheckedChange={() => handleToggle('showCertifications')}
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg border">
            <Label htmlFor="showProjects">Projects</Label>
            <Switch
              id="showProjects"
              checked={settings.showProjects}
              onCheckedChange={() => handleToggle('showProjects')}
            />
          </div>

          <div className="flex items-center justify-between p-3 rounded-lg border">
            <Label htmlFor="showResume">{t('privacy.showResume')}</Label>
            <Switch
              id="showResume"
              checked={settings.showResume}
              onCheckedChange={() => handleToggle('showResume')}
            />
          </div>
        </div>

        {/* Save Button */}
        {onSave && (
          <div className="flex justify-end pt-4 border-t">
            <Button onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : 'Save Privacy Settings'}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
