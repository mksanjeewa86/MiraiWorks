'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { userSettingsApi, UserSettings, UserProfile } from '@/services/userSettingsApi';
import AppLayout from '@/components/layout/AppLayout';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { 
  Save, 
  Shield, 
  Bell, 
  User, 
  Eye, 
  EyeOff,
  Smartphone,
  Mail,
  Globe,
  Moon,
  Sun,
  Monitor
} from 'lucide-react';

interface SettingsState {
  activeSection: 'account' | 'security' | 'notifications' | 'preferences';
  loading: boolean;
  saving: boolean;
  error: string | null;
  profile: UserProfile | null;
  settings: UserSettings | null;
  security: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  };
}

export default function SettingsPage() {
  const { user } = useAuth();
  
  const [state, setState] = useState<SettingsState>({
    activeSection: 'account',
    loading: true,
    saving: false,
    error: null,
    profile: null,
    settings: null,
    security: {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
  });

  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });

  useEffect(() => {
    const loadUserData = async () => {
      try {
        setState(prev => ({ ...prev, loading: true, error: null }));
        
        // Load user profile and settings in parallel
        const [profileResponse, settingsResponse] = await Promise.all([
          userSettingsApi.getProfile(),
          userSettingsApi.getSettings()
        ]);
        
        setState(prev => ({
          ...prev,
          profile: profileResponse.data,
          settings: settingsResponse.data,
          loading: false
        }));
      } catch (error) {
        console.error('Failed to load user data:', error);
        setState(prev => ({
          ...prev,
          error: 'Failed to load user data',
          loading: false
        }));
      }
    };

    if (user) {
      loadUserData();
    }
  }, [user]);

  const updateProfile = (field: string, value: string) => {
    setState(prev => ({
      ...prev,
      profile: prev.profile ? { ...prev.profile, [field]: value } : null
    }));
  };

  const updateSecurity = (field: string, value: string | boolean) => {
    if (field === 'two_factor_enabled') {
      setState(prev => ({
        ...prev,
        settings: prev.settings ? { ...prev.settings, two_factor_enabled: value as boolean } : null
      }));
    } else {
      setState(prev => ({
        ...prev,
        security: { ...prev.security, [field]: value }
      }));
    }
  };

  const updateNotifications = (field: string, value: boolean) => {
    setState(prev => ({
      ...prev,
      settings: prev.settings ? { ...prev.settings, [field]: value } : null
    }));
  };

  const updatePreferences = (field: string, value: string) => {
    setState(prev => ({
      ...prev,
      settings: prev.settings ? { ...prev.settings, [field]: value } : null
    }));
  };

  const handleSave = async () => {
    if (!state.profile || !state.settings) return;
    
    try {
      setState(prev => ({ ...prev, saving: true, error: null }));
      
      // Save profile and settings in parallel
      const [profileResponse, settingsResponse] = await Promise.all([
        userSettingsApi.updateProfile({
          first_name: state.profile!.first_name,
          last_name: state.profile!.last_name,
          phone: state.profile!.phone,
          job_title: state.profile!.job_title,
          bio: state.profile!.bio
        }),
        userSettingsApi.updateSettings(state.settings)
      ]);
      
      setState(prev => ({
        ...prev,
        profile: profileResponse.data,
        settings: settingsResponse.data,
        saving: false
      }));
      
      // Show success message (you could add a toast notification here)
      console.log('Settings saved successfully');
      
    } catch (error) {
      console.error('Failed to save settings:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to save settings',
        saving: false
      }));
    }
  };

  const sections = [
    { id: 'account', name: 'Account', icon: User, description: 'Personal information and profile' },
    { id: 'security', name: 'Security', icon: Shield, description: 'Password and authentication' },
    { id: 'notifications', name: 'Notifications', icon: Bell, description: 'Email, push, and SMS preferences' },
    { id: 'preferences', name: 'Preferences', icon: Globe, description: 'Theme, language, and display' }
  ];

  const renderAccountSection = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Account Settings</h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          Update your personal information and profile details
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="First Name"
          value={state.profile?.first_name || ''}
          onChange={(e) => updateProfile('first_name', e.target.value)}
          required
        />
        <Input
          label="Last Name"
          value={state.profile?.last_name || ''}
          onChange={(e) => updateProfile('last_name', e.target.value)}
          required
        />
        <Input
          label="Email"
          type="email"
          value={state.profile?.email || ''}
          onChange={(e) => updateProfile('email', e.target.value)}
          required
          disabled
        />
        <Input
          label="Phone"
          value={state.profile?.phone || ''}
          onChange={(e) => updateProfile('phone', e.target.value)}
        />
      </div>
      
      <Input
        label="Job Title"
        value={state.profile?.job_title || ''}
        onChange={(e) => updateProfile('job_title', e.target.value)}
      />

      <div>
        <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
          Bio
        </label>
        <textarea
          className="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
          style={{ color: 'var(--text-primary)' }}
          rows={4}
          value={state.profile?.bio || ''}
          onChange={(e) => updateProfile('bio', e.target.value)}
          placeholder="Tell us about yourself..."
        />
      </div>
    </div>
  );

  const renderSecuritySection = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Security Settings</h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          Manage your password and authentication settings
        </p>
      </div>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Change Password
        </h3>
        
        <div className="space-y-4">
          <div>
            <Input
              label="Current Password"
              type={showPasswords.current ? 'text' : 'password'}
              value={state.security.current_password}
              onChange={(e) => updateSecurity('current_password', e.target.value)}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                >
                  {showPasswords.current ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              }
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="New Password"
              type={showPasswords.new ? 'text' : 'password'}
              value={state.security.new_password}
              onChange={(e) => updateSecurity('new_password', e.target.value)}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                >
                  {showPasswords.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              }
            />
            <Input
              label="Confirm Password"
              type={showPasswords.confirm ? 'text' : 'password'}
              value={state.security.confirm_password}
              onChange={(e) => updateSecurity('confirm_password', e.target.value)}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                >
                  {showPasswords.confirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              }
            />
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Two-Factor Authentication
        </h3>
        
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
              Enable 2FA
            </p>
            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
              Add an extra layer of security to your account
            </p>
          </div>
          <div className="flex items-center">
            <input
              type="checkbox"
              id="two-factor"
              checked={state.settings?.two_factor_enabled || false}
              onChange={(e) => updateSecurity('two_factor_enabled', e.target.checked)}
              className="mr-2"
            />
            <label htmlFor="two-factor" className="cursor-pointer">
              {state.settings?.two_factor_enabled ? 'Enabled' : 'Disabled'}
            </label>
          </div>
        </div>
        
        {state.settings?.two_factor_enabled && (
          <div className="mt-4 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
              <Smartphone className="h-4 w-4" />
              <span className="text-sm font-medium">2FA is enabled</span>
            </div>
            <p className="text-sm mt-1 text-green-600 dark:text-green-400">
              Your account is protected with two-factor authentication
            </p>
          </div>
        )}
      </Card>
    </div>
  );

  const renderNotificationsSection = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Notification Settings</h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          Choose how you want to receive notifications
        </p>
      </div>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Notification Channels
        </h3>
        
        <div className="space-y-4">
          {[
            { key: 'email_notifications', label: 'Email Notifications', icon: Mail, description: 'Receive notifications via email' },
            { key: 'push_notifications', label: 'Push Notifications', icon: Bell, description: 'Browser push notifications' },
            { key: 'sms_notifications', label: 'SMS Notifications', icon: Smartphone, description: 'Text message notifications' }
          ].map(({ key, label, icon: Icon, description }) => (
            <div key={key} className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
              <div className="flex items-center gap-3">
                <Icon className="h-5 w-5" style={{ color: 'var(--text-muted)' }} />
                <div>
                  <p className="font-medium" style={{ color: 'var(--text-primary)' }}>{label}</p>
                  <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{description}</p>
                </div>
              </div>
              <input
                type="checkbox"
                checked={state.settings?.[key as keyof UserSettings] as boolean || false}
                onChange={(e) => updateNotifications(key, e.target.checked)}
                className="scale-110"
              />
            </div>
          ))}
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Event Notifications
        </h3>
        
        <div className="space-y-4">
          {[
            { key: 'interview_reminders', label: 'Interview Reminders', description: 'Get notified before scheduled interviews' },
            { key: 'application_updates', label: 'Application Updates', description: 'Updates on job applications and status changes' },
            { key: 'message_notifications', label: 'New Messages', description: 'Notifications for new messages and conversations' }
          ].map(({ key, label, description }) => (
            <div key={key} className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
              <div>
                <p className="font-medium" style={{ color: 'var(--text-primary)' }}>{label}</p>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{description}</p>
              </div>
              <input
                type="checkbox"
                checked={state.settings?.[key as keyof UserSettings] as boolean || false}
                onChange={(e) => updateNotifications(key, e.target.checked)}
                className="scale-110"
              />
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  const renderPreferencesSection = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>Preferences</h2>
        <p style={{ color: 'var(--text-secondary)' }}>
          Customize your experience and display settings
        </p>
      </div>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Appearance
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
              Theme
            </label>
            <div className="grid grid-cols-3 gap-3">
              {[
                { value: 'light', label: 'Light', icon: Sun },
                { value: 'dark', label: 'Dark', icon: Moon },
                { value: 'system', label: 'System', icon: Monitor }
              ].map(({ value, label, icon: Icon }) => (
                <button
                  key={value}
                  onClick={() => updatePreferences('theme', value)}
                  className={`p-3 rounded-lg border-2 transition-colors flex flex-col items-center gap-2 ${
                    state.settings?.theme === value
                      ? 'border-brand-primary bg-brand-primary/10'
                      : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span className="text-sm font-medium">{label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Localization
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
              Language
            </label>
            <select
              value={state.settings?.language || 'en'}
              onChange={(e) => updatePreferences('language', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
              style={{ color: 'var(--text-primary)' }}
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="ja">Japanese</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
              Timezone
            </label>
            <select
              value={state.settings?.timezone || 'America/New_York'}
              onChange={(e) => updatePreferences('timezone', e.target.value)}
              className="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
              style={{ color: 'var(--text-primary)' }}
            >
              <option value="America/New_York">Eastern Time (ET)</option>
              <option value="America/Chicago">Central Time (CT)</option>
              <option value="America/Denver">Mountain Time (MT)</option>
              <option value="America/Los_Angeles">Pacific Time (PT)</option>
              <option value="Europe/London">Greenwich Mean Time (GMT)</option>
              <option value="Asia/Tokyo">Japan Standard Time (JST)</option>
            </select>
          </div>
        </div>
        
        <div className="mt-4">
          <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
            Date Format
          </label>
          <select
            value={state.settings?.date_format || 'MM/DD/YYYY'}
            onChange={(e) => updatePreferences('date_format', e.target.value)}
            className="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
            style={{ color: 'var(--text-primary)' }}
          >
            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
            <option value="DD/MM/YYYY">DD/MM/YYYY</option>
            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
          </select>
        </div>
      </Card>
    </div>
  );

  const renderCurrentSection = () => {
    switch (state.activeSection) {
      case 'account':
        return renderAccountSection();
      case 'security':
        return renderSecuritySection();
      case 'notifications':
        return renderNotificationsSection();
      case 'preferences':
        return renderPreferencesSection();
      default:
        return null;
    }
  };

  if (state.loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner className="w-8 h-8" />
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
            <h1 className="text-3xl font-bold" style={{ color: 'var(--text-primary)' }}>Settings</h1>
            <p className="mt-1" style={{ color: 'var(--text-secondary)' }}>
              Manage your account settings and preferences
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {state.error && (
              <p className="text-red-600 text-sm">{state.error}</p>
            )}
            <Button 
              onClick={handleSave}
              disabled={state.saving || !state.profile || !state.settings}
              className="flex items-center gap-2"
            >
              {state.saving ? <LoadingSpinner className="w-4 h-4" /> : <Save className="h-4 w-4" />}
              {state.saving ? 'Saving...' : 'Save Changes'}
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
                  onClick={() => setState(prev => ({ ...prev, activeSection: section.id as 'account' | 'security' | 'notifications' | 'preferences' }))}
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