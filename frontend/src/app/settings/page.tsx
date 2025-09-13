'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { userSettingsApi } from "@/api/userSettings";
import { UserSettings } from "@/types";
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import Card from '@/components/ui/Card';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import Toggle from '@/components/ui/Toggle';
import { 
  Save, 
  Shield, 
  Bell, 
  User, 
  Eye, 
  EyeOff,
  Smartphone,
  Mail,
  Globe
} from 'lucide-react';
import type { SettingsState } from '@/types/pages';

function SettingsPageContent() {
  const { user } = useAuth();
  
  const [state, setState] = useState<SettingsState>({
    activeSection: 'account',
    loading: true,
    autoSaving: false,
    passwordSaving: false,
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

  const [debounceTimers, setDebounceTimers] = useState<{ [key: string]: NodeJS.Timeout }>({});

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
    // Update local state immediately
    setState(prev => ({
      ...prev,
      profile: prev.profile ? { ...prev.profile, [field]: value } : null
    }));
    
    // Clear existing debounce timer for this field
    if (debounceTimers[field]) {
      clearTimeout(debounceTimers[field]);
    }
    
    // Set new debounce timer
    const timer = setTimeout(() => {
      autoSaveProfile(field, value);
    }, 1000); // 1 second delay
    
    setDebounceTimers(prev => ({
      ...prev,
      [field]: timer
    }));
  };

  const autoSaveProfile = async (field: string, value: string) => {
    if (!state.profile) return;
    
    try {
      setState(prev => ({ ...prev, autoSaving: true, error: null }));
      
      const updatedProfile = { ...state.profile, [field]: value };
      await userSettingsApi.updateProfile({
        first_name: updatedProfile.first_name,
        last_name: updatedProfile.last_name,
        phone: updatedProfile.phone,
        job_title: updatedProfile.job_title,
        bio: updatedProfile.bio
      });
      
      setState(prev => ({ ...prev, autoSaving: false }));
    } catch (error) {
      console.error('Failed to auto-save profile:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to save changes',
        autoSaving: false
      }));
    }
  };

  const updateSecurity = async (field: string, value: string | boolean) => {
    if (field === 'require_2fa') {
      setState(prev => ({
        ...prev,
        settings: prev.settings ? { ...prev.settings, require_2fa: value as boolean } : null
      }));
      
      // Auto-save 2FA setting
      await autoSaveSettings('require_2fa', value as boolean);
    } else {
      setState(prev => ({
        ...prev,
        security: { ...prev.security, [field]: value }
      }));
    }
  };

  const updateNotifications = async (field: string, value: boolean) => {
    // Special handling for SMS notifications
    if (field === 'sms_notifications' && value && (!state.profile?.phone || !state.profile.phone.trim())) {
      setState(prev => ({ ...prev, error: 'SMS notifications require a phone number. Please add your phone number in your profile first.' }));
      return;
    }

    setState(prev => ({
      ...prev,
      settings: prev.settings ? { ...prev.settings, [field]: value } : null,
      error: null // Clear any previous errors
    }));
    
    // Auto-save notification setting
    await autoSaveSettings(field, value);
  };

  const updatePreferences = async (field: string, value: string) => {
    setState(prev => ({
      ...prev,
      settings: prev.settings ? { ...prev.settings, [field]: value } : null
    }));
    
    // Auto-save preference setting
    await autoSaveSettings(field, value);
  };

  const autoSaveSettings = async (field: string, value: string | boolean) => {
    if (!state.settings) return;
    
    try {
      setState(prev => ({ ...prev, autoSaving: true, error: null }));
      
      const updatedSettings = { ...state.settings, [field]: value };
      await userSettingsApi.updateSettings(updatedSettings);
      
      setState(prev => ({ ...prev, autoSaving: false }));
    } catch (error) {
      console.error('Failed to auto-save settings:', error);
      const errorMessage = (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to save changes';
      setState(prev => ({
        ...prev,
        error: errorMessage,
        autoSaving: false,
        // If it was SMS notification and failed, revert the setting
        settings: field === 'sms_notifications' && errorMessage.includes('phone number') 
          ? { ...prev.settings!, sms_notifications: false }
          : prev.settings
      }));
    }
  };

  const handlePasswordSave = async () => {
    const { current_password, new_password, confirm_password } = state.security;
    
    // Validation
    if (!current_password || !new_password || !confirm_password) {
      setState(prev => ({ ...prev, error: 'All password fields are required' }));
      return;
    }
    
    if (new_password !== confirm_password) {
      setState(prev => ({ ...prev, error: 'New passwords do not match' }));
      return;
    }
    
    if (new_password.length < 8) {
      setState(prev => ({ ...prev, error: 'New password must be at least 8 characters' }));
      return;
    }
    
    try {
      setState(prev => ({ ...prev, passwordSaving: true, error: null }));
      
      // TODO: Add password change API endpoint
      // await userSettingsApi.changePassword({
      //   current_password,
      //   new_password
      // });
      
      // Clear password fields on success
      setState(prev => ({
        ...prev,
        passwordSaving: false,
        security: {
          current_password: '',
          new_password: '',
          confirm_password: ''
        }
      }));
      
      console.log('Password changed successfully');
      
    } catch (error) {
      console.error('Failed to change password:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to change password',
        passwordSaving: false
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
          
          <div className="flex justify-end">
            <Button 
              onClick={handlePasswordSave}
              disabled={state.passwordSaving || !state.security.current_password || !state.security.new_password || !state.security.confirm_password}
              className="flex items-center gap-2"
            >
              {state.passwordSaving ? <LoadingSpinner className="w-4 h-4" /> : <Save className="h-4 w-4" />}
              {state.passwordSaving ? 'Changing Password...' : 'Change Password'}
            </Button>
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
          <div className="flex items-center gap-3">
            <Toggle
              id="two-factor"
              checked={state.settings?.require_2fa || false}
              onChange={(checked) => updateSecurity('require_2fa', checked)}
              size="md"
            />
            <span className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>
              {state.settings?.require_2fa ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        </div>
        
        {state.settings?.require_2fa && (
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
          ].map(({ key, label, icon: Icon, description }) => {
            const isSmsWithoutPhone = key === 'sms_notifications' && (!state.profile?.phone || !state.profile.phone.trim());
            const displayDescription = isSmsWithoutPhone 
              ? 'Requires phone number (add in profile first)' 
              : description;
            
            return (
              <div key={key} className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
                <div className="flex items-center gap-3">
                  <Icon className={`h-5 w-5 ${isSmsWithoutPhone ? 'opacity-50' : ''}`} style={{ color: 'var(--text-muted)' }} />
                  <div>
                    <p className={`font-medium ${isSmsWithoutPhone ? 'opacity-50' : ''}`} style={{ color: 'var(--text-primary)' }}>{label}</p>
                    <p className={`text-sm ${isSmsWithoutPhone ? 'opacity-50 text-orange-600 dark:text-orange-400' : ''}`} style={{ color: isSmsWithoutPhone ? undefined : 'var(--text-secondary)' }}>{displayDescription}</p>
                  </div>
                </div>
                <Toggle
                  checked={state.settings?.[key as keyof UserSettings] as boolean || false}
                  onChange={(checked) => updateNotifications(key, checked)}
                  disabled={isSmsWithoutPhone}
                  size="md"
                />
              </div>
            );
          })}
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
              <Toggle
                checked={state.settings?.[key as keyof UserSettings] as boolean || false}
                onChange={(checked) => updateNotifications(key, checked)}
                size="md"
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
            {state.autoSaving && (
              <div className="flex items-center gap-2 text-green-600 text-sm">
                <LoadingSpinner className="w-4 h-4" />
                <span>Saving...</span>
              </div>
            )}
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

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsPageContent />
    </ProtectedRoute>
  );
}