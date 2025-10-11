'use client';

import { useState, useEffect } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { userSettingsApi } from '@/api/userSettings';
import { calendarApi } from '@/api/calendar';
import { subscriptionPlanApi, planChangeRequestApi } from '@/api/subscription';
import { UserSettings, CalendarConnection } from '@/types';
import { useMySubscription, useMyPlanChangeRequests, usePlanChangeRequestMutations, useSubscriptionPlans } from '@/hooks/useSubscription';
import AppLayout from '@/components/layout/AppLayout';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { Card } from '@/components/ui';
import { Button } from '@/components/ui';
import { Input } from '@/components/ui';
import { LoadingSpinner } from '@/components/ui';
import { Toggle } from '@/components/ui';
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
  Calendar,
  Trash2,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  ExternalLink,
  Building2,
  CreditCard,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  X,
  Star,
  Lock,
} from 'lucide-react';
import type { SettingsState } from '@/types/pages';

function SettingsPageContent() {
  const { user } = useAuth();
  const t = useTranslations('settings');
  const locale = useLocale();
  const router = useRouter();

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
      confirm_password: '',
    },
  });

  // Check if user is company admin (for subscription features)
  const isCompanyAdmin = user?.roles?.some(role => role.role.name === 'admin');
  const isCandidate = user?.roles?.some(role => role.role.name === 'candidate');

  // Subscription hooks (only for company admins, not candidates)
  const { subscription, refetch: refetchSubscription } = useMySubscription({
    enabled: isCompanyAdmin && !isCandidate
  });
  const { plans } = useSubscriptionPlans();
  const { requests, refetch: refetchRequests } = useMyPlanChangeRequests({
    enabled: isCompanyAdmin && !isCandidate
  });
  const { requestPlanChange } = usePlanChangeRequestMutations();

  const [showPlanChangeModal, setShowPlanChangeModal] = useState(false);
  const [selectedPlanForChange, setSelectedPlanForChange] = useState<number | null>(null);
  const [planChangeMessage, setPlanChangeMessage] = useState('');
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [requestToCancel, setRequestToCancel] = useState<number | null>(null);
  const [higherPlanFeatures, setHigherPlanFeatures] = useState<any[]>([]);
  const [minimumPlanFeatureIds, setMinimumPlanFeatureIds] = useState<Set<number>>(new Set());

  const [calendarState, setCalendarState] = useState({
    connections: [] as CalendarConnection[],
    loading: false,
    connecting: false,
    error: null as string | null,
  });

  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false,
  });

  const [debounceTimers, setDebounceTimers] = useState<{ [key: string]: NodeJS.Timeout }>({});

  useEffect(() => {
    const loadUserData = async () => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));

        // Load user profile and settings in parallel
        const [profileResponse, settingsResponse] = await Promise.all([
          userSettingsApi.getProfile(),
          userSettingsApi.getSettings(),
        ]);

        setState((prev) => ({
          ...prev,
          profile: profileResponse.data,
          settings: settingsResponse.data,
          loading: false,
        }));
      } catch (error) {
        console.error('Failed to load user data:', error);
        setState((prev) => ({
          ...prev,
          error: t('errors.loadUserData'),
          loading: false,
        }));
      }
    };

    if (user) {
      loadUserData();
    }
  }, [user]);

  // Load calendar connections when calendar section is active
  useEffect(() => {
    if (state.activeSection === 'calendar' && user) {
      loadCalendarConnections();
    }
  }, [state.activeSection, user]);

  // Fetch features for higher-priced plans
  useEffect(() => {
    const fetchHigherPlanFeatures = async () => {
      if (!subscription?.plan || !plans || plans.length === 0) {
        setHigherPlanFeatures([]);
        return;
      }

      try {
        const currentPlanPrice = parseFloat(subscription.plan.price_monthly.toString());

        // Get all plans with higher prices
        const higherPlans = plans.filter(
          p => parseFloat(p.price_monthly.toString()) > currentPlanPrice
        );

        if (higherPlans.length === 0) {
          setHigherPlanFeatures([]);
          return;
        }

        // Fetch features for each higher plan
        const featuresPromises = higherPlans.map(async plan => {
          const response = await subscriptionPlanApi.getPlanWithFeatures(plan.id);
          return {
            planId: plan.id,
            planName: plan.display_name,
            features: response.data?.features || []
          };
        });

        const allHigherPlansData = await Promise.all(featuresPromises);

        // Get current plan's feature IDs
        const currentFeatureIds = new Set(
          subscription.plan.features?.map(f => f.id) || []
        );

        // Collect all unique features from higher plans that current plan doesn't have
        const uniqueFeatures: any[] = [];
        const seenFeatureIds = new Set<number>();

        allHigherPlansData.forEach(planData => {
          planData.features.forEach((feature: any) => {
            // Only include if current plan doesn't have it and we haven't seen it yet
            if (!currentFeatureIds.has(feature.id) && !seenFeatureIds.has(feature.id)) {
              uniqueFeatures.push({
                ...feature,
                planName: planData.planName,
                planId: planData.planId
              });
              seenFeatureIds.add(feature.id);
            }
          });
        });

        setHigherPlanFeatures(uniqueFeatures);
      } catch (error) {
        console.error('Failed to fetch higher plan features:', error);
        setHigherPlanFeatures([]);
      }
    };

    fetchHigherPlanFeatures();
  }, [subscription, plans]);

  // Fetch features for minimum plan to identify premium-only features
  useEffect(() => {
    const fetchMinimumPlanFeatures = async () => {
      if (!plans || plans.length === 0) {
        setMinimumPlanFeatureIds(new Set());
        return;
      }

      try {
        // Find the minimum plan (lowest priced plan)
        const sortedPlans = [...plans].sort(
          (a, b) => parseFloat(a.price_monthly.toString()) - parseFloat(b.price_monthly.toString())
        );
        const minimumPlan = sortedPlans[0];

        if (!minimumPlan) {
          setMinimumPlanFeatureIds(new Set());
          return;
        }

        // Fetch features for minimum plan
        const response = await subscriptionPlanApi.getPlanWithFeatures(minimumPlan.id);
        const minimumFeatureIds = new Set(
          response.data?.features?.map((f: any) => f.id) || []
        );

        setMinimumPlanFeatureIds(minimumFeatureIds);
      } catch (error) {
        console.error('Failed to fetch minimum plan features:', error);
        setMinimumPlanFeatureIds(new Set());
      }
    };

    fetchMinimumPlanFeatures();
  }, [plans]);

  const loadCalendarConnections = async () => {
    try {
      setCalendarState((prev) => ({ ...prev, loading: true, error: null }));
      const response = await calendarApi.getConnections();
      setCalendarState((prev) => ({
        ...prev,
        connections: response.data || [],
        loading: false,
      }));
    } catch (error) {
      console.error('Failed to load calendar connections:', error);
      setCalendarState((prev) => ({
        ...prev,
        error: t('errors.loadCalendarConnections'),
        loading: false,
      }));
    }
  };

  const updateProfile = (field: string, value: string) => {
    // Update local state immediately
    setState((prev) => ({
      ...prev,
      profile: prev.profile ? { ...prev.profile, [field]: value } : null,
    }));

    // Clear existing debounce timer for this field
    if (debounceTimers[field]) {
      clearTimeout(debounceTimers[field]);
    }

    // Set new debounce timer
    const timer = setTimeout(() => {
      autoSaveProfile(field, value);
    }, 1000); // 1 second delay

    setDebounceTimers((prev) => ({
      ...prev,
      [field]: timer,
    }));
  };

  const autoSaveProfile = async (field: string, value: string) => {
    if (!state.profile) return;

    try {
      setState((prev) => ({ ...prev, autoSaving: true, error: null }));

      const updatedProfile = { ...state.profile, [field]: value };
      await userSettingsApi.updateProfile({
        first_name: updatedProfile.first_name,
        last_name: updatedProfile.last_name,
        phone: updatedProfile.phone,
        job_title: updatedProfile.job_title,
        bio: updatedProfile.bio,
      });

      setState((prev) => ({ ...prev, autoSaving: false }));
    } catch (error) {
      console.error('Failed to auto-save profile:', error);
      setState((prev) => ({
        ...prev,
        error: t('errors.saveChanges'),
        autoSaving: false,
      }));
    }
  };

  const updateSecurity = (field: string, value: string | boolean) => {
    if (field === 'require_2fa') {
      setState((prev) => ({
        ...prev,
        settings: prev.settings ? { ...prev.settings, require_2fa: value as boolean } : null,
      }));

      // Auto-save 2FA setting asynchronously without blocking
      autoSaveSettings('require_2fa', value as boolean).catch((error) => {
        console.error('Failed to save 2FA setting:', error);
        // Revert the state if save fails
        setState((prev) => ({
          ...prev,
          settings: prev.settings ? { ...prev.settings, require_2fa: !value as boolean } : null,
        }));
      });
    } else {
      setState((prev) => ({
        ...prev,
        security: { ...prev.security, [field]: value },
      }));
    }
  };

  const updateNotifications = async (field: string, value: boolean) => {
    // Special handling for SMS notifications
    if (
      field === 'sms_notifications' &&
      value &&
      (!state.profile?.phone || !state.profile.phone.trim())
    ) {
      setState((prev) => ({
        ...prev,
        error: t('notificationChannels.smsRequiresPhoneError'),
      }));
      return;
    }

    setState((prev) => ({
      ...prev,
      settings: prev.settings ? { ...prev.settings, [field]: value } : null,
      error: null, // Clear any previous errors
    }));

    // Auto-save notification setting
    await autoSaveSettings(field, value);
  };

  const updatePreferences = async (field: string, value: string) => {
    setState((prev) => ({
      ...prev,
      settings: prev.settings ? { ...prev.settings, [field]: value } : null,
    }));

    // Auto-save preference setting
    await autoSaveSettings(field, value);

    // If language changed, also update the UI locale
    if (field === 'language' && value !== locale) {
      // Get current pathname and replace locale segment
      const pathname = window.location.pathname;
      const segments = pathname.split('/');
      segments[1] = value; // Replace locale segment (e.g., /en/settings -> /ja/settings)
      const newPath = segments.join('/');

      // Use native Next.js router (not useLocaleRouter) to avoid double locale prefix
      router.push(newPath);
      router.refresh();
    }
  };

  const autoSaveSettings = async (field: string, value: string | boolean) => {
    if (!state.settings) return;

    try {
      setState((prev) => ({ ...prev, autoSaving: true, error: null }));

      // Get the current settings from state to avoid stale closure
      const currentSettings = state.settings;
      const updatedSettings = { ...currentSettings, [field]: value };

      const response = await userSettingsApi.updateSettings(updatedSettings);

      // Update the state with the response from the server to ensure consistency
      setState((prev) => ({
        ...prev,
        autoSaving: false,
        settings: response.data
      }));
    } catch (error) {
      console.error('Failed to auto-save settings:', error);
      const errorMessage =
        (error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        t('errors.saveChanges');
      setState((prev) => ({
        ...prev,
        error: errorMessage,
        autoSaving: false,
        // If it was SMS notification and failed, revert the setting
        settings:
          field === 'sms_notifications' && errorMessage.includes('phone number')
            ? { ...prev.settings!, sms_notifications: false }
            : prev.settings,
      }));
    }
  };

  // Calendar functions
  const handleConnectCalendar = async (provider: 'google' | 'outlook') => {
    try {
      setCalendarState((prev) => ({ ...prev, connecting: true, error: null }));

      const authResponse =
        provider === 'google'
          ? await calendarApi.getGoogleAuthUrl()
          : await calendarApi.getOutlookAuthUrl();

      // Open auth URL in new window
      if (authResponse.data?.auth_url) {
        window.open(authResponse.data.auth_url, '_blank', 'width=500,height=600');
      } else {
        throw new Error('No auth URL received');
      }

      setCalendarState((prev) => ({ ...prev, connecting: false }));

      // Refresh connections after a delay to allow for OAuth completion
      setTimeout(() => {
        loadCalendarConnections();
      }, 3000);
    } catch (error) {
      console.error(`Failed to connect ${provider} calendar:`, error);
      setCalendarState((prev) => ({
        ...prev,
        error: `Failed to connect ${provider} calendar`,
        connecting: false,
      }));
    }
  };

  const handleDisconnectCalendar = async (connectionId: number) => {
    try {
      setCalendarState((prev) => ({ ...prev, loading: true, error: null }));
      await calendarApi.deleteConnection(connectionId);
      await loadCalendarConnections();
    } catch (error) {
      console.error('Failed to disconnect calendar:', error);
      setCalendarState((prev) => ({
        ...prev,
        error: t('errors.disconnectCalendar'),
        loading: false,
      }));
    }
  };

  const handleSyncCalendar = async (connectionId: number) => {
    try {
      setCalendarState((prev) => ({ ...prev, error: null }));
      await calendarApi.syncCalendar(connectionId);
      await loadCalendarConnections();
    } catch (error) {
      console.error('Failed to sync calendar:', error);
      setCalendarState((prev) => ({
        ...prev,
        error: t('errors.syncCalendar'),
      }));
    }
  };

  const handleUpdateConnection = async (connectionId: number, updates: Record<string, unknown>) => {
    try {
      setCalendarState((prev) => ({ ...prev, error: null }));
      await calendarApi.updateConnection(connectionId, updates);
      await loadCalendarConnections();
    } catch (error) {
      console.error('Failed to update calendar connection:', error);
      setCalendarState((prev) => ({
        ...prev,
        error: t('errors.updateCalendarConnection'),
      }));
    }
  };

  const handlePasswordSave = async () => {
    const { current_password, new_password, confirm_password } = state.security;

    // Validation
    if (!current_password || !new_password || !confirm_password) {
      setState((prev) => ({ ...prev, error: 'All password fields are required' }));
      return;
    }

    if (new_password !== confirm_password) {
      setState((prev) => ({ ...prev, error: 'New passwords do not match' }));
      return;
    }

    if (new_password.length < 8) {
      setState((prev) => ({ ...prev, error: 'New password must be at least 8 characters' }));
      return;
    }

    try {
      setState((prev) => ({ ...prev, passwordSaving: true, error: null }));

      // TODO: Add password change API endpoint
      // await userSettingsApi.changePassword({
      //   current_password,
      //   new_password
      // });

      // Clear password fields on success
      setState((prev) => ({
        ...prev,
        passwordSaving: false,
        security: {
          current_password: '',
          new_password: '',
          confirm_password: '',
        },
      }));
    } catch (error) {
      console.error('Failed to change password:', error);
      setState((prev) => ({
        ...prev,
        error: t('errors.changePassword'),
        passwordSaving: false,
      }));
    }
  };

  // Sections configuration (isCompanyAdmin already defined at top)
  const sections = [
    { id: 'account', name: t('tabs.account'), icon: User, description: t('account.subtitle') },
    { id: 'security', name: t('tabs.security'), icon: Shield, description: t('security.subtitle') },
    {
      id: 'notifications',
      name: t('tabs.notifications'),
      icon: Bell,
      description: t('notifications.subtitle'),
    },
    {
      id: 'calendar',
      name: t('calendar.title'),
      icon: Calendar,
      description: t('calendar.subtitle'),
    },
    {
      id: 'preferences',
      name: t('preferences.title'),
      icon: Globe,
      description: t('preferences.subtitle'),
    },
    ...(isCompanyAdmin ? [{
      id: 'company-profile' as const,
      name: t('companyProfile.title'),
      icon: Building2,
      description: t('companyProfile.subtitle'),
    }] : []),
  ];

  const renderAccountSection = () => (
    <div className="space-y-8 relative">
      {/* Background Pattern & Floating Elements */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM5Q0EzQUYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0ibTM2IDM0IDIyLTIyIDQgMjIgNC0yIDAtMiAyLTQgMC0yem0wLTIyIDIwIDIwLTEyIDEyLTEyIDAgMC04IDEyLTEyem0yNCAyNCAxMi0xMiAwLTggMC0xMC00IDAgMCA0aC04djhoLTRsLTQgMCA0IDRoMTJ6bTAtMTYgOC04IDAgMCAwIDhoLTh6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-10 pointer-events-none rounded-3xl"></div>
      <div className="absolute top-10 left-10 w-32 h-32 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob pointer-events-none"></div>
      <div className="absolute top-20 right-10 w-32 h-32 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute bottom-10 left-20 w-32 h-32 bg-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-4000 pointer-events-none"></div>

      {/* Header */}
      <div className="relative z-10 animate-fade-in-up">
        <h2 className="text-3xl font-extrabold mb-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          {t('account.title')}
        </h2>
        <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
          {t('account.subtitle')}
        </p>
      </div>

      {/* Profile Information Card */}
      <div className="relative z-10 bg-gradient-to-br from-white/80 to-white/60 dark:from-gray-800/80 dark:to-gray-800/60 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/20 dark:border-gray-700/20 shadow-2xl transition-all duration-500 hover:shadow-blue-500/10 hover:border-blue-400/30 animate-fade-in-up">
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="animate-fade-in-up" style={{ animationDelay: '100ms' }}>
              <Input
                label={t('common.firstName')}
                value={state.profile?.first_name || ''}
                onChange={(e) => updateProfile('first_name', e.target.value)}
                required
              />
            </div>
            <div className="animate-fade-in-up" style={{ animationDelay: '200ms' }}>
              <Input
                label={t('common.lastName')}
                value={state.profile?.last_name || ''}
                onChange={(e) => updateProfile('last_name', e.target.value)}
                required
              />
            </div>
            <div className="animate-fade-in-up" style={{ animationDelay: '300ms' }}>
              <Input
                label={t('common.email')}
                type="email"
                value={state.profile?.email || ''}
                onChange={(e) => updateProfile('email', e.target.value)}
                required
                disabled
              />
            </div>
            <div className="animate-fade-in-up" style={{ animationDelay: '400ms' }}>
              <Input
                label={t('common.phone')}
                value={state.profile?.phone || ''}
                onChange={(e) => updateProfile('phone', e.target.value)}
              />
            </div>
          </div>

          <div className="animate-fade-in-up" style={{ animationDelay: '500ms' }}>
            <Input
              label={t('common.jobTitle')}
              value={state.profile?.job_title || ''}
              onChange={(e) => updateProfile('job_title', e.target.value)}
            />
          </div>

          <div className="animate-fade-in-up" style={{ animationDelay: '600ms' }}>
            <label className="block text-sm font-bold mb-3 text-blue-700 dark:text-blue-300">
              {t('common.bio')}
            </label>
            <textarea
              className="w-full p-4 border-2 border-blue-200/50 dark:border-blue-700/50 rounded-2xl bg-white/60 dark:bg-gray-700/60 backdrop-blur-lg focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 transition-all duration-300"
              style={{ color: 'var(--text-primary)' }}
              rows={4}
              value={state.profile?.bio || ''}
              onChange={(e) => updateProfile('bio', e.target.value)}
              placeholder={t('common.bioPlaceholder')}
            />
          </div>
        </div>
      </div>
    </div>
  );

  const renderSecuritySection = () => (
    <div className="space-y-8 relative">
      {/* Background Pattern & Floating Elements */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM5Q0EzQUYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0ibTM2IDM0IDIyLTIyIDQgMjIgNC0yIDAtMiAyLTQgMC0yem0wLTIyIDIwIDIwLTEyIDEyLTEyIDAgMC04IDEyLTEyem0yNCAyNCAxMi0xMiAwLTggMC0xMC00IDAgMCA0aC04djhoLTRsLTQgMCA0IDRoMTJ6bTAtMTYgOC04IDAgMCAwIDhoLTh6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-10 pointer-events-none rounded-3xl"></div>
      <div className="absolute top-10 left-10 w-32 h-32 bg-red-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob pointer-events-none"></div>
      <div className="absolute top-20 right-10 w-32 h-32 bg-orange-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute bottom-10 left-20 w-32 h-32 bg-yellow-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-4000 pointer-events-none"></div>

      {/* Header */}
      <div className="relative z-10 animate-fade-in-up">
        <h2 className="text-3xl font-extrabold mb-2 bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
          {t('security.title')}
        </h2>
        <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
          {t('security.subtitle')}
        </p>
      </div>

      {/* Change Password Card */}
      <div className="relative z-10 bg-gradient-to-br from-white/80 to-white/60 dark:from-gray-800/80 dark:to-gray-800/60 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/20 dark:border-gray-700/20 shadow-2xl transition-all duration-500 hover:shadow-red-500/10 hover:border-red-400/30 animate-fade-in-up">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-3" style={{ color: 'var(--text-primary)' }}>
          <Lock className="h-6 w-6 text-red-600" />
          {t('common.changePassword')}
        </h3>

        <div className="space-y-6">
          <div className="animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            <Input
              label={t('common.currentPassword')}
              type={showPasswords.current ? 'text' : 'password'}
              value={state.security.current_password}
              onChange={(e) => updateSecurity('current_password', e.target.value)}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowPasswords((prev) => ({ ...prev, current: !prev.current }))}
                  className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                  {showPasswords.current ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              }
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="animate-fade-in-up" style={{ animationDelay: '200ms' }}>
              <Input
                label={t('common.newPassword')}
                type={showPasswords.new ? 'text' : 'password'}
                value={state.security.new_password}
                onChange={(e) => updateSecurity('new_password', e.target.value)}
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowPasswords((prev) => ({ ...prev, new: !prev.new }))}
                    className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    {showPasswords.new ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                }
              />
            </div>
            <div className="animate-fade-in-up" style={{ animationDelay: '300ms' }}>
              <Input
                label={t('common.confirmPassword')}
                type={showPasswords.confirm ? 'text' : 'password'}
                value={state.security.confirm_password}
                onChange={(e) => updateSecurity('confirm_password', e.target.value)}
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowPasswords((prev) => ({ ...prev, confirm: !prev.confirm }))}
                    className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    {showPasswords.confirm ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                }
              />
            </div>
          </div>

          <div className="flex justify-end animate-fade-in-up" style={{ animationDelay: '400ms' }}>
            <button
              onClick={handlePasswordSave}
              disabled={
                state.passwordSaving ||
                !state.security.current_password ||
                !state.security.new_password ||
                !state.security.confirm_password
              }
              className="px-6 py-3 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 flex items-center gap-2"
            >
              {state.passwordSaving ? (
                <>
                  <LoadingSpinner className="w-4 h-4" />
                  {t('common.changingPassword')}
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  {t('common.changePassword')}
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Two-Factor Authentication Card */}
      <div className="relative z-10 bg-gradient-to-br from-white/80 to-white/60 dark:from-gray-800/80 dark:to-gray-800/60 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/20 dark:border-gray-700/20 shadow-2xl transition-all duration-500 hover:shadow-orange-500/10 hover:border-orange-400/30 animate-fade-in-up">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-3" style={{ color: 'var(--text-primary)' }}>
          <Smartphone className="h-6 w-6 text-orange-600" />
          {t('common.twoFactorAuth')}
        </h3>

        <div className="flex items-center justify-between p-6 bg-white/60 dark:bg-gray-700/60 backdrop-blur-lg rounded-2xl border-2 border-orange-200/30 dark:border-orange-700/30">
          <div>
            <p className="font-bold text-lg" style={{ color: 'var(--text-primary)' }}>
              {t('common.enable2FA')}
            </p>
            <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
              {t('common.twoFactorSubtitle')}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Toggle
              id="two-factor"
              checked={state.settings?.require_2fa || false}
              onChange={(checked) => updateSecurity('require_2fa', checked)}
              size="md"
            />
            <span className="text-sm font-bold" style={{ color: 'var(--text-primary)' }}>
              {state.settings?.require_2fa ? t('common.enabled') : t('common.disabled')}
            </span>
          </div>
        </div>

        {state.settings?.require_2fa && (
          <div className="mt-6 p-6 bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-2xl border-2 border-green-200/50 dark:border-green-700/50 animate-fade-in-up">
            <div className="flex items-center gap-3 text-green-600 dark:text-green-400">
              <div className="p-2 bg-green-100 dark:bg-green-900/50 rounded-full">
                <Smartphone className="h-5 w-5" />
              </div>
              <span className="text-sm font-bold">{t('common.twoFactorEnabled')}</span>
            </div>
            <p className="text-sm mt-3 text-green-700 dark:text-green-300 ml-11">
              {t('common.twoFactorDesc')}
            </p>
          </div>
        )}
      </div>
    </div>
  );

  const renderNotificationsSection = () => (
    <div className="space-y-8 relative">
      {/* Background Pattern & Floating Elements */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM5Q0EzQUYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0ibTM2IDM0IDIyLTIyIDQgMjIgNC0yIDAtMiAyLTQgMC0yem0wLTIyIDIwIDIwLTEyIDEyLTEyIDAgMC04IDEyLTEyem0yNCAyNCAxMi0xMiAwLTggMC0xMC00IDAgMCA0aC04djhoLTRsLTQgMCA0IDRoMTJ6bTAtMTYgOC04IDAgMCAwIDhoLTh6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-10 pointer-events-none rounded-3xl"></div>
      <div className="absolute top-10 left-10 w-32 h-32 bg-green-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob pointer-events-none"></div>
      <div className="absolute top-20 right-10 w-32 h-32 bg-teal-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute bottom-10 left-20 w-32 h-32 bg-cyan-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-4000 pointer-events-none"></div>

      {/* Header */}
      <div className="relative z-10 animate-fade-in-up">
        <h2 className="text-3xl font-extrabold mb-2 bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent">
          {t('notifications.title')}
        </h2>
        <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
          {t('notifications.subtitle')}
        </p>
      </div>

      {/* Notification Channels Card */}
      <div className="relative z-10 bg-gradient-to-br from-white/80 to-white/60 dark:from-gray-800/80 dark:to-gray-800/60 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/20 dark:border-gray-700/20 shadow-2xl transition-all duration-500 hover:shadow-green-500/10 hover:border-green-400/30 animate-fade-in-up">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-3" style={{ color: 'var(--text-primary)' }}>
          <Bell className="h-6 w-6 text-green-600" />
          {t('notificationChannels.title')}
        </h3>

        <div className="space-y-4">
          {[
            {
              key: 'email_notifications',
              label: t('notificationChannels.emailNotifications'),
              icon: Mail,
              description: t('notificationChannels.emailDesc'),
            },
            {
              key: 'push_notifications',
              label: t('notificationChannels.pushNotifications'),
              icon: Bell,
              description: t('notificationChannels.pushDesc'),
            },
            {
              key: 'sms_notifications',
              label: t('notificationChannels.smsNotifications'),
              icon: Smartphone,
              description: t('notificationChannels.smsDesc'),
            },
          ].map(({ key, label, icon: Icon, description }, index) => {
            const isSmsWithoutPhone =
              key === 'sms_notifications' && (!state.profile?.phone || !state.profile.phone.trim());
            const displayDescription = isSmsWithoutPhone
              ? t('notificationChannels.smsRequiresPhone')
              : description;

            return (
              <div
                key={key}
                className="flex items-center justify-between p-4 bg-white/60 dark:bg-gray-700/60 backdrop-blur-lg rounded-2xl border-2 border-green-200/30 dark:border-green-700/30 transition-all duration-300 hover:border-green-400/50 animate-fade-in-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-center gap-4">
                  <div className={`p-3 bg-gradient-to-br from-green-100 to-teal-100 dark:from-green-900/30 dark:to-teal-900/30 rounded-xl ${isSmsWithoutPhone ? 'opacity-50' : ''}`}>
                    <Icon className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <p className={`font-bold ${isSmsWithoutPhone ? 'opacity-50' : ''}`} style={{ color: 'var(--text-primary)' }}>
                      {label}
                    </p>
                    <p
                      className={`text-sm mt-0.5 ${isSmsWithoutPhone ? 'opacity-50 text-orange-600 dark:text-orange-400' : ''}`}
                      style={{ color: isSmsWithoutPhone ? undefined : 'var(--text-secondary)' }}
                    >
                      {displayDescription}
                    </p>
                  </div>
                </div>
                <Toggle
                  checked={(state.settings?.[key as keyof UserSettings] as boolean) || false}
                  onChange={(checked) => updateNotifications(key, checked)}
                  disabled={isSmsWithoutPhone}
                  size="md"
                />
              </div>
            );
          })}
        </div>
      </div>

      {/* Event Notifications Card */}
      <div className="relative z-10 bg-gradient-to-br from-white/80 to-white/60 dark:from-gray-800/80 dark:to-gray-800/60 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/20 dark:border-gray-700/20 shadow-2xl transition-all duration-500 hover:shadow-teal-500/10 hover:border-teal-400/30 animate-fade-in-up">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-3" style={{ color: 'var(--text-primary)' }}>
          <Bell className="h-6 w-6 text-teal-600" />
          {t('eventNotifications.title')}
        </h3>

        <div className="space-y-4">
          {[
            {
              key: 'interview_reminders',
              label: t('eventNotifications.interviewReminders'),
              description: t('eventNotifications.interviewDesc'),
            },
            {
              key: 'application_updates',
              label: t('eventNotifications.applicationUpdates'),
              description: t('eventNotifications.applicationDesc'),
            },
            {
              key: 'message_notifications',
              label: t('eventNotifications.messageNotifications'),
              description: t('eventNotifications.messageDesc'),
            },
          ].map(({ key, label, description }, index) => (
            <div
              key={key}
              className="flex items-center justify-between p-4 bg-white/60 dark:bg-gray-700/60 backdrop-blur-lg rounded-2xl border-2 border-teal-200/30 dark:border-teal-700/30 transition-all duration-300 hover:border-teal-400/50 animate-fade-in-up"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div>
                <p className="font-bold" style={{ color: 'var(--text-primary)' }}>
                  {label}
                </p>
                <p className="text-sm mt-0.5" style={{ color: 'var(--text-secondary)' }}>
                  {description}
                </p>
              </div>
              <Toggle
                checked={(state.settings?.[key as keyof UserSettings] as boolean) || false}
                onChange={(checked) => updateNotifications(key, checked)}
                size="md"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderPreferencesSection = () => (
    <div className="space-y-8 relative">
      {/* Background Pattern & Floating Elements */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM5Q0EzQUYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0ibTM2IDM0IDIyLTIyIDQgMjIgNC0yIDAtMiAyLTQgMC0yem0wLTIyIDIwIDIwLTEyIDEyLTEyIDAgMC04IDEyLTEyem0yNCAyNCAxMi0xMiAwLTggMC0xMC00IDAgMCA0aC04djhoLTRsLTQgMCA0IDRoMTJ6bTAtMTYgOC04IDAgMCAwIDhoLTh6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-10 pointer-events-none rounded-3xl"></div>
      <div className="absolute top-10 left-10 w-32 h-32 bg-indigo-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob pointer-events-none"></div>
      <div className="absolute top-20 right-10 w-32 h-32 bg-violet-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute bottom-10 left-20 w-32 h-32 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-4000 pointer-events-none"></div>

      {/* Header */}
      <div className="relative z-10 animate-fade-in-up">
        <h2 className="text-3xl font-extrabold mb-2 bg-gradient-to-r from-indigo-600 to-violet-600 bg-clip-text text-transparent">
          {t('preferences.title')}
        </h2>
        <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
          {t('preferences.subtitle')}
        </p>
      </div>

      {/* Localization Card */}
      <div className="relative z-10 bg-gradient-to-br from-white/80 to-white/60 dark:from-gray-800/80 dark:to-gray-800/60 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/20 dark:border-gray-700/20 shadow-2xl transition-all duration-500 hover:shadow-indigo-500/10 hover:border-indigo-400/30 animate-fade-in-up">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-3" style={{ color: 'var(--text-primary)' }}>
          <Globe className="h-6 w-6 text-indigo-600" />
          {t('preferences.localization.title')}
        </h3>

        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="animate-fade-in-up" style={{ animationDelay: '100ms' }}>
              <label className="block text-sm font-bold mb-3 text-indigo-700 dark:text-indigo-300">
                {t('preferences.localization.language')}
              </label>
              <select
                value={state.settings?.language || 'en'}
                onChange={(e) => updatePreferences('language', e.target.value)}
                className="w-full p-4 pr-10 border-2 border-indigo-200/50 dark:border-indigo-700/50 rounded-2xl bg-white/60 dark:bg-gray-700/60 backdrop-blur-lg appearance-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/20 transition-all duration-300 font-semibold"
                style={{
                  color: 'var(--text-primary)',
                  backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236366f1' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                  backgroundPosition: 'right 16px center',
                  backgroundRepeat: 'no-repeat',
                  backgroundSize: '20px',
                }}
              >
                <option value="en">English</option>
                <option value="ja">日本語 (Japanese)</option>
              </select>
            </div>

            <div className="animate-fade-in-up" style={{ animationDelay: '200ms' }}>
              <label className="block text-sm font-bold mb-3 text-indigo-700 dark:text-indigo-300">
                {t('preferences.localization.timezone')}
              </label>
              <select
                value={state.settings?.timezone || 'America/New_York'}
                onChange={(e) => updatePreferences('timezone', e.target.value)}
                className="w-full p-4 pr-10 border-2 border-indigo-200/50 dark:border-indigo-700/50 rounded-2xl bg-white/60 dark:bg-gray-700/60 backdrop-blur-lg appearance-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/20 transition-all duration-300 font-semibold"
                style={{
                  color: 'var(--text-primary)',
                  backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236366f1' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                  backgroundPosition: 'right 16px center',
                  backgroundRepeat: 'no-repeat',
                  backgroundSize: '20px',
                }}
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

          <div className="animate-fade-in-up" style={{ animationDelay: '300ms' }}>
            <label className="block text-sm font-bold mb-3 text-indigo-700 dark:text-indigo-300">
              {t('preferences.localization.dateFormat')}
            </label>
            <select
              value={state.settings?.date_format || 'MM/DD/YYYY'}
              onChange={(e) => updatePreferences('date_format', e.target.value)}
              className="w-full p-4 pr-10 border-2 border-indigo-200/50 dark:border-indigo-700/50 rounded-2xl bg-white/60 dark:bg-gray-700/60 backdrop-blur-lg appearance-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-400/20 transition-all duration-300 font-semibold"
              style={{
                color: 'var(--text-primary)',
                backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236366f1' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                backgroundPosition: 'right 16px center',
                backgroundRepeat: 'no-repeat',
                backgroundSize: '20px',
              }}
            >
              <option value="MM/DD/YYYY">MM/DD/YYYY</option>
              <option value="DD/MM/YYYY">DD/MM/YYYY</option>
              <option value="YYYY-MM-DD">YYYY-MM-DD</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCalendarSection = () => (
    <div className="space-y-8 relative">
      {/* Background Pattern & Floating Elements */}
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM5Q0EzQUYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0ibTM2IDM0IDIyLTIyIDQgMjIgNC0yIDAtMiAyLTQgMC0yem0wLTIyIDIwIDIwLTEyIDEyLTEyIDAgMC04IDEyLTEyem0yNCAyNCAxMi0xMiAwLTggMC0xMC00IDAgMCA0aC04djhoLTRsLTQgMCA0IDRoMTJ6bTAtMTYgOC04IDAgMCAwIDhoLTh6Ii8+PC9nPjwvZz48L3N2Zz4=')] opacity-10 pointer-events-none rounded-3xl"></div>
      <div className="absolute top-10 left-10 w-32 h-32 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob pointer-events-none"></div>
      <div className="absolute top-20 right-10 w-32 h-32 bg-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-2000 pointer-events-none"></div>
      <div className="absolute bottom-10 left-20 w-32 h-32 bg-indigo-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-4000 pointer-events-none"></div>

      {/* Header */}
      <div className="relative z-10 animate-fade-in-up">
        <h2 className="text-3xl font-extrabold mb-2 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
          {t('calendar.title')}
        </h2>
        <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
          {t('calendar.subtitle')}
        </p>
      </div>

      {calendarState.error && (
        <div className="relative z-10 p-4 bg-red-500/10 backdrop-blur-sm border-2 border-red-400/30 rounded-2xl animate-fade-in-up shadow-lg">
          <div className="flex items-center gap-3 text-red-600 dark:text-red-400">
            <AlertCircle className="h-5 w-5" />
            <span className="text-sm font-semibold">{calendarState.error}</span>
          </div>
        </div>
      )}

      {/* Connected Calendars - Only show when there are connections */}
      {calendarState.loading ? (
        <div className="relative z-10 bg-gradient-to-br from-white/80 to-white/60 dark:from-gray-800/80 dark:to-gray-800/60 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/20 dark:border-gray-700/20 shadow-2xl animate-fade-in-up">
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner className="w-8 h-8 text-purple-600" />
          </div>
        </div>
      ) : calendarState.connections.length > 0 && (
        <div className="relative z-10 bg-gradient-to-br from-white/80 to-white/60 dark:from-gray-800/80 dark:to-gray-800/60 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/20 dark:border-gray-700/20 shadow-2xl transition-all duration-500 hover:shadow-purple-500/10 hover:border-purple-400/30 animate-fade-in-up">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-3" style={{ color: 'var(--text-primary)' }}>
            <Calendar className="h-6 w-6 text-purple-600" />
            {t('calendar.connectedCalendars.title')}
          </h3>

          <div className="space-y-4">
            {calendarState.connections.map((connection, index) => (
              <div
                key={connection.id}
                className="p-6 bg-white/60 dark:bg-gray-700/60 backdrop-blur-lg rounded-2xl border-2 border-purple-200/30 dark:border-purple-700/30 shadow-lg hover:shadow-xl hover:border-purple-400/50 transition-all duration-300 hover:scale-[1.02] animate-fade-in-up"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div
                      className={`w-4 h-4 rounded-full shadow-lg animate-pulse ${
                        connection.status === 'connected'
                          ? 'bg-green-500'
                          : connection.status === 'error'
                            ? 'bg-red-500'
                            : connection.status === 'expired'
                              ? 'bg-yellow-500'
                              : 'bg-gray-400'
                      }`}
                    />
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <span className="font-bold text-lg" style={{ color: 'var(--text-primary)' }}>
                          {connection.display_name || connection.provider_email}
                        </span>
                        <span className="text-xs px-3 py-1 rounded-full font-semibold bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/50 dark:to-pink-900/50 text-purple-700 dark:text-purple-300 border border-purple-300/50">
                          {connection.provider}
                        </span>
                      </div>
                      <p className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
                        {connection.provider_email}
                      </p>
                      {connection.last_sync_at && (
                        <p className="text-xs mt-1 flex items-center gap-1" style={{ color: 'var(--text-muted)' }}>
                          <RefreshCw className="h-3 w-3" />
                          {t('calendar.settings.lastSync', { date: new Date(connection.last_sync_at).toLocaleString() })}
                        </p>
                      )}
                      {connection.sync_error && (
                        <p className="text-xs text-red-600 dark:text-red-400 mt-1 font-medium">
                          {t('calendar.status.error')}: {connection.sync_error}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleSyncCalendar(connection.id)}
                      className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105 flex items-center gap-2"
                    >
                      <RefreshCw className="h-4 w-4" />
                      {t('calendar.actions.sync')}
                    </button>
                    <button
                      onClick={() => handleDisconnectCalendar(connection.id)}
                      className="px-4 py-2 bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-300 hover:scale-105 flex items-center gap-2"
                    >
                      <Trash2 className="h-4 w-4" />
                      {t('calendar.actions.disconnect')}
                    </button>
                  </div>
                </div>

                {/* Connection Settings */}
                <div className="mt-6 pt-6 border-t-2 border-purple-200/30 dark:border-purple-700/30">
                  <h4 className="text-sm font-bold mb-4 text-purple-700 dark:text-purple-300">
                    {t('calendar.connect.title')}
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center justify-between p-3 bg-white/50 dark:bg-gray-800/50 rounded-xl border border-purple-200/30">
                      <label className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {t('calendar.settings.syncEvents')}
                      </label>
                      <Toggle
                        checked={connection.sync_events}
                        onChange={(checked) =>
                          handleUpdateConnection(connection.id, { sync_events: checked })
                        }
                        size="sm"
                      />
                    </div>
                    <div className="flex items-center justify-between p-3 bg-white/50 dark:bg-gray-800/50 rounded-xl border border-purple-200/30">
                      <label className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {t('calendar.settings.syncReminders')}
                      </label>
                      <Toggle
                        checked={connection.sync_reminders}
                        onChange={(checked) =>
                          handleUpdateConnection(connection.id, { sync_reminders: checked })
                        }
                        size="sm"
                      />
                    </div>
                    <div className="flex items-center justify-between p-3 bg-white/50 dark:bg-gray-800/50 rounded-xl border border-purple-200/30">
                      <label className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {t('calendar.settings.autoCreateMeetings')}
                      </label>
                      <Toggle
                        checked={connection.auto_create_meetings}
                        onChange={(checked) =>
                          handleUpdateConnection(connection.id, { auto_create_meetings: checked })
                        }
                        size="sm"
                      />
                    </div>
                    <div className="flex items-center justify-between p-3 bg-white/50 dark:bg-gray-800/50 rounded-xl border border-purple-200/30">
                      <label className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                        {t('calendar.settings.enabled')}
                      </label>
                      <Toggle
                        checked={connection.is_enabled}
                        onChange={(checked) =>
                          handleUpdateConnection(connection.id, { is_enabled: checked })
                        }
                        size="sm"
                      />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Connect New Calendar */}
      <div className="relative z-10 bg-gradient-to-br from-white/80 to-white/60 dark:from-gray-800/80 dark:to-gray-800/60 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/20 dark:border-gray-700/20 shadow-2xl transition-all duration-500 hover:shadow-purple-500/10 hover:border-purple-400/30 animate-fade-in-up">
        <h3 className="text-xl font-bold mb-6 flex items-center gap-3" style={{ color: 'var(--text-primary)' }}>
          <ExternalLink className="h-6 w-6 text-purple-600" />
          {t('calendar.connect.title')}
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <button
            onClick={() => handleConnectCalendar('google')}
            disabled={calendarState.connecting}
            className="group relative overflow-hidden p-8 bg-gradient-to-br from-blue-500 via-blue-600 to-blue-700 hover:from-blue-600 hover:via-blue-700 hover:to-blue-800 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 border-2 border-blue-400/30 hover:border-blue-300/50"
          >
            {/* Shine Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>

            <div className="relative flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 border border-white/30">
                  <span className="text-white font-bold text-3xl drop-shadow-lg">G</span>
                </div>
                <div className="text-left">
                  <div className="font-extrabold text-xl mb-1 text-white drop-shadow-md">
                    {t('calendar.connect.google')}
                  </div>
                  <div className="text-sm text-blue-100 font-medium">
                    {t('calendar.connect.googleDesc')}
                  </div>
                </div>
              </div>
              {calendarState.connecting ? (
                <LoadingSpinner className="w-6 h-6 text-white" />
              ) : (
                <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center group-hover:bg-white/30 transition-all duration-300">
                  <ExternalLink className="w-5 h-5 text-white group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-300" />
                </div>
              )}
            </div>
          </button>

          <button
            onClick={() => handleConnectCalendar('outlook')}
            disabled={calendarState.connecting}
            className="group relative overflow-hidden p-8 bg-gradient-to-br from-indigo-500 via-indigo-600 to-indigo-700 hover:from-indigo-600 hover:via-indigo-700 hover:to-indigo-800 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 border-2 border-indigo-400/30 hover:border-indigo-300/50"
          >
            {/* Shine Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>

            <div className="relative flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 border border-white/30">
                  <span className="text-white font-bold text-3xl drop-shadow-lg">O</span>
                </div>
                <div className="text-left">
                  <div className="font-extrabold text-xl mb-1 text-white drop-shadow-md">
                    {t('calendar.connect.outlook')}
                  </div>
                  <div className="text-sm text-indigo-100 font-medium">
                    {t('calendar.connect.outlookDesc')}
                  </div>
                </div>
              </div>
              {calendarState.connecting ? (
                <LoadingSpinner className="w-6 h-6 text-white" />
              ) : (
                <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center group-hover:bg-white/30 transition-all duration-300">
                  <ExternalLink className="w-5 h-5 text-white group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-300" />
                </div>
              )}
            </div>
          </button>
        </div>

        <div className="p-6 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-2xl border-2 border-blue-200/50 dark:border-blue-700/50 backdrop-blur-sm">
          <div className="flex items-start gap-3">
            <CheckCircle className="h-6 w-6 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <p className="font-bold text-base text-blue-800 dark:text-blue-200 mb-3">
                {t('calendar.connect.whatHappens')}
              </p>
              <ul className="text-blue-700 dark:text-blue-300 space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 font-bold">✓</span>
                  <span>{t('calendar.connect.benefit1')}</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 font-bold">✓</span>
                  <span>{t('calendar.connect.benefit2')}</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 font-bold">✓</span>
                  <span>{t('calendar.connect.benefit3')}</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-600 font-bold">✓</span>
                  <span>{t('calendar.connect.benefit4')}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const formatPrice = (price: string | number) => {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0,
    }).format(numPrice);
  };

  const handleRequestPlanChange = async () => {
    if (!selectedPlanForChange) return;

    try {
      await requestPlanChange({
        requested_plan_id: selectedPlanForChange,
        request_message: planChangeMessage || 'Plan change request from settings',
      });
      setShowPlanChangeModal(false);
      setSelectedPlanForChange(null);
      setPlanChangeMessage('');
      refetchRequests();
    } catch (error) {
      // Error handled by hook
    }
  };

  const handleCancelRequest = (requestId: number) => {
    setRequestToCancel(requestId);
    setShowCancelModal(true);
  };

  const confirmCancelRequest = async () => {
    if (!requestToCancel) return;

    try {
      const response = await planChangeRequestApi.cancelRequest(requestToCancel);
      if (response.success) {
        setShowCancelModal(false);
        setRequestToCancel(null);
        refetchRequests();
      }
    } catch (error) {
      console.error('Failed to cancel request:', error);
    }
  };

  const getRequestStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800"><Clock className="h-3 w-3 mr-1" />Pending</span>;
      case 'approved':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"><CheckCircle className="h-3 w-3 mr-1" />Approved</span>;
      case 'rejected':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"><AlertCircle className="h-3 w-3 mr-1" />Rejected</span>;
      case 'cancelled':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"><AlertCircle className="h-3 w-3 mr-1" />Cancelled</span>;
      default:
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">{status}</span>;
    }
  };

  const renderCompanyProfileSection = () => {
    const pendingRequest = requests.find(r => r.status === 'pending');
    const currentPlan = subscription?.plan;
    const isTrial = subscription?.is_trial || false;

    // If on trial, show ALL plans as conversion options (including Minimum)
    // Otherwise, show plans based on price comparison
    const higherPlans = plans.filter(p => {
      if (!currentPlan) return true;
      if (isTrial) {
        // On trial: show ALL plans as valid conversion options
        // (trial is temporary state, not a pricing tier)
        return true;
      }
      // Not on trial: show plans with higher price
      return parseFloat(p.price_monthly.toString()) > parseFloat(currentPlan.price_monthly.toString());
    });

    const lowerPlans = plans.filter(p => {
      if (!currentPlan || isTrial) return false; // No downgrade from trial
      return parseFloat(p.price_monthly.toString()) < parseFloat(currentPlan.price_monthly.toString());
    });

    // Features from higher-priced plans that current plan doesn't have
    const allPlanFeatures = higherPlanFeatures;

    return (
      <div className="space-y-8 relative">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiM5Q0EzQUYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJtMzYgMzQgMjItMjIgNCAyMiA0LTIgMC0yIDItNCAwLTJ6bTAtMjIgMjAgMjAtMTIgMTItMTIgMCAwLTggMTItMTJ6bTI0IDI0IDEyLTEyIDAtOCAwLTEwLTQgMCAwIDRoLTh2OGgtNGwtNCAwIDQgNGgxMnptMC0xNiA4LTggMCAwIDAgOGgtOHoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-10 pointer-events-none rounded-3xl"></div>

        {/* Floating Blobs */}
        <div className="absolute top-10 left-10 w-32 h-32 bg-amber-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob pointer-events-none"></div>
        <div className="absolute top-20 right-10 w-40 h-40 bg-yellow-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-2000 pointer-events-none"></div>
        <div className="absolute bottom-10 left-20 w-36 h-36 bg-orange-400 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-blob animation-delay-4000 pointer-events-none"></div>

        {/* Header */}
        <div className="relative z-10 animate-fade-in-up">
          <h2 className="text-3xl font-extrabold mb-2 bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
            {t('companyProfile.title')}
          </h2>
          <p className="text-base" style={{ color: 'var(--text-secondary)' }}>
            {t('companyProfile.subtitle')}
          </p>
        </div>

        {/* No Subscription - Show Available Plans */}
        {!subscription ? (
          <>
            <div className="relative animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
              <div className="bg-yellow-50/80 dark:bg-yellow-900/30 backdrop-blur-xl border-2 border-yellow-300/50 dark:border-yellow-600/50 rounded-3xl p-6 shadow-xl">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-12 h-12 rounded-2xl bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center shadow-lg">
                    <AlertCircle className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-yellow-800 dark:text-yellow-200 mb-1">
                      {t('companyProfile.noSubscription.title')}
                    </h3>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300">
                      {t('companyProfile.noSubscription.description')}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Available Plans */}
            <div className="relative animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border-2 border-amber-200/50 dark:border-amber-700/50 rounded-3xl p-8 shadow-2xl">
                <h3 className="text-2xl font-bold mb-2 bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                  {t('companyProfile.availablePlans.title')}
                </h3>
                <p className="text-sm mb-6" style={{ color: 'var(--text-secondary)' }}>
                  {t('companyProfile.availablePlans.subtitle')}
                </p>

                <div className="space-y-4">
                  {plans.map((plan, index) => (
                    <div key={plan.id} className="relative group animate-fade-in-up" style={{ animationDelay: `${0.3 + index * 0.1}s` }}>
                      <div className="bg-gradient-to-br from-white to-amber-50/50 dark:from-gray-800 dark:to-amber-900/20 border-2 border-amber-200/50 dark:border-amber-700/50 rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-[1.02]">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-semibold text-lg" style={{ color: 'var(--text-primary)' }}>
                          {plan.display_name}
                        </h4>
                        <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                          {plan.description}
                        </p>
                        <p className="text-2xl font-bold mt-2" style={{ color: 'var(--text-primary)' }}>
                          {formatPrice(plan.price_monthly)}
                          <span className="text-sm font-normal" style={{ color: 'var(--text-secondary)' }}>{t('companyProfile.availablePlans.perMonth')}</span>
                        </p>

                        {/* Show some features if available */}
                        {plan.max_users && (
                          <div className="mt-3 space-y-1">
                            <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                              • {t('companyProfile.features.upTo', { count: plan.max_users, item: t('companyProfile.features.users') })}
                            </p>
                            {plan.max_workflows && (
                              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                                • {t('companyProfile.features.upTo', { count: plan.max_workflows, item: t('companyProfile.features.workflows') })}
                              </p>
                            )}
                            {plan.max_exams && (
                              <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                                • {t('companyProfile.features.upTo', { count: plan.max_exams, item: t('companyProfile.features.exams') })}
                              </p>
                            )}
                          </div>
                        )}
                      </div>

                      <Button
                        onClick={() => {
                          setSelectedPlanForChange(plan.id);
                          setShowPlanChangeModal(true);
                        }}
                        className="ml-4 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white font-semibold px-6 py-2.5 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
                      >
                        {t('companyProfile.availablePlans.requestPlan')}
                      </Button>
                    </div>
                  </div>
                  </div>
                ))}
              </div>
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Compact Current Plan Overview */}
            <div className="relative animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
              <div className={`bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border-2 rounded-3xl p-6 shadow-xl ${subscription.is_trial ? 'border-amber-300/50 dark:border-amber-600/50' : 'border-blue-300/50 dark:border-blue-600/50'}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div>
                    <p className={`text-xs ${subscription.is_trial ? 'text-amber-600 dark:text-amber-400' : 'text-blue-600 dark:text-blue-400'}`}>
                      {subscription.is_trial ? t('companyProfile.currentPlan.trialPeriod') : t('companyProfile.currentPlan.title')}
                    </p>
                    <h3 className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>
                      {subscription.plan.display_name}
                      {subscription.is_trial && ` (${t('companyProfile.currentPlan.trial')})`}
                    </h3>
                    {subscription.is_trial && subscription.trial_end_date && (
                      <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                        {t('companyProfile.currentPlan.endsOn', { date: new Date(subscription.trial_end_date).toLocaleDateString() })}
                      </p>
                    )}
                  </div>
                  {!subscription.is_trial && (
                    <>
                      <div className="h-8 w-px bg-gray-300 dark:bg-gray-600"></div>
                      <div>
                        <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{t('companyProfile.currentPlan.price')}</p>
                        <p className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
                          {formatPrice(subscription.plan.price_monthly)}<span className="text-xs">{t('companyProfile.availablePlans.perMonth')}</span>
                        </p>
                      </div>
                      <div className="h-8 w-px bg-gray-300 dark:bg-gray-600"></div>
                      <div>
                        <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>{t('companyProfile.currentPlan.billing')}</p>
                        <p className="text-sm font-medium capitalize" style={{ color: 'var(--text-primary)' }}>
                          {subscription.billing_cycle}
                        </p>
                      </div>
                    </>
                  )}
                </div>
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                  subscription.is_trial
                    ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300'
                    : subscription.is_active
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                      : 'bg-gray-100 text-gray-800'
                }`}>
                  {subscription.is_trial ? `⏱ ${t('companyProfile.currentPlan.trial')}` : subscription.is_active ? `✓ ${t('companyProfile.currentPlan.active')}` : t('companyProfile.currentPlan.inactive')}
                </span>
              </div>
            </div>
            </div>

            {/* UPGRADE OPTIONS - EMPHASIZED */}
            {allPlanFeatures.length > 0 && higherPlans.length > 0 && (
              <div className="relative z-10 bg-gradient-to-br from-white/80 to-white/60 dark:from-gray-800/80 dark:to-gray-800/60 backdrop-blur-xl rounded-3xl p-8 border-2 border-white/20 dark:border-gray-700/20 shadow-2xl transition-all duration-500 hover:shadow-orange-500/10 hover:border-orange-400/30 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <h3 className="text-xl font-bold mb-6 flex items-center gap-3" style={{ color: 'var(--text-primary)' }}>
                  <ArrowUpRight className={`h-6 w-6 ${subscription.is_trial ? 'text-blue-600' : 'text-orange-600'}`} />
                  {subscription.is_trial ? t('companyProfile.upgrade.titleTrial') : t('companyProfile.upgrade.title')}
                </h3>
                <p className="text-sm mb-6" style={{ color: 'var(--text-secondary)' }}>
                  {subscription.is_trial
                    ? t('companyProfile.upgrade.subtitleTrial')
                    : t('companyProfile.upgrade.subtitle')}
                </p>

                <div className="grid md:grid-cols-2 gap-4 mb-6 md:auto-rows-fr">
                  {allPlanFeatures.slice(0, 6).map((feature, index) => (
                    <div key={index} className="flex items-start gap-3 p-4 bg-white dark:bg-gray-800 rounded-lg border-2 border-orange-200 dark:border-orange-700 shadow-sm h-full">
                      <div className="h-6 w-6 rounded-full bg-orange-100 dark:bg-orange-900/50 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <AlertCircle className="h-4 w-4 text-orange-600 dark:text-orange-400" />
                      </div>
                      <div className="flex-1 flex flex-col">
                        <p className="font-semibold text-base" style={{ color: 'var(--text-primary)' }}>{feature.display_name}</p>
                        {feature.description && (
                          <p className="text-sm mt-1 flex-1" style={{ color: 'var(--text-secondary)' }}>{feature.description}</p>
                        )}
                        <p className="text-xs font-medium text-orange-600 dark:text-orange-400 mt-2">
                          ✨ {t('companyProfile.upgrade.availableIn', { plan: feature.planName })}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>

                {!pendingRequest && higherPlans.length > 0 && (
                  <div className="flex gap-3 mt-6">
                    {higherPlans.map(plan => (
                      <Button
                        key={plan.id}
                        onClick={() => {
                          setSelectedPlanForChange(plan.id);
                          setShowPlanChangeModal(true);
                        }}
                        className={`flex-1 py-6 text-lg font-bold shadow-lg hover:shadow-xl transition-all ${
                          subscription.is_trial
                            ? 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700'
                            : 'bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700'
                        }`}
                      >
                        <ArrowUpRight className="h-6 w-6 mr-2" />
                        {subscription.is_trial ? t('companyProfile.upgrade.buttonTrial', { plan: plan.display_name }) : t('companyProfile.upgrade.button', { plan: plan.display_name })}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Current Features - Compact with Premium Indicators */}
            <div className="relative animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
              <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border-2 border-green-200/50 dark:border-green-700/50 rounded-3xl p-6 shadow-xl">
              <h3 className="text-base font-semibold mb-3 flex items-center gap-2" style={{ color: 'var(--text-primary)' }}>
                <CheckCircle className="h-5 w-5 text-green-600" />
                {t('companyProfile.features.title', { plan: subscription.plan.display_name })}
              </h3>
              <div className="grid md:grid-cols-3 gap-2 md:auto-rows-fr">
                {subscription.plan.features?.map((feature) => {
                  // Premium feature = NOT in minimum plan
                  const isPremiumFeature = !minimumPlanFeatureIds.has(feature.id);

                  return (
                    <div
                      key={feature.id}
                      className={`flex items-center gap-2 p-2 rounded border h-full ${
                        isPremiumFeature
                          ? 'bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-900/30 dark:to-amber-900/30 border-orange-300 dark:border-orange-700'
                          : 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                      }`}
                    >
                      <CheckCircle className={`h-4 w-4 flex-shrink-0 ${isPremiumFeature ? 'text-orange-600' : 'text-green-600'}`} />
                      <div className="flex-1 min-w-0 flex flex-col justify-center">
                        <p className={`text-sm font-medium ${
                          isPremiumFeature
                            ? 'text-orange-900 dark:text-orange-100'
                            : 'text-green-900 dark:text-green-100'
                        }`}>
                          {feature.display_name}
                        </p>
                        {isPremiumFeature && (
                          <span className="inline-flex items-center gap-1 text-xs font-semibold text-orange-600 dark:text-orange-400 mt-1">
                            <Star className="h-3 w-3" />
                            {t('companyProfile.upgrade.premiumOnly')}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
            </div>

            {/* Downgrade Option (if available) */}
            {lowerPlans.length > 0 && !pendingRequest && (
              <div className="relative animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border-2 border-gray-200/50 dark:border-gray-700/50 rounded-3xl p-6 shadow-xl">
                <h3 className="text-lg font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                  {t('companyProfile.downgrade.title')}
                </h3>
                <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
                  {t('companyProfile.downgrade.subtitle')}
                </p>
                <div className="flex gap-2">
                  {lowerPlans.map(plan => (
                    <Button
                      key={plan.id}
                      onClick={() => {
                        setSelectedPlanForChange(plan.id);
                        setShowPlanChangeModal(true);
                      }}
                      variant="outline"
                      className="flex items-center gap-2"
                    >
                      <ArrowDownRight className="h-4 w-4" />
                      {t('companyProfile.downgrade.button', { plan: plan.display_name })}
                    </Button>
                  ))}
                </div>
              </div>
              </div>
            )}

            {/* Pending Request Alert */}
            {pendingRequest && (
              <div className="relative animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
                <div className="bg-yellow-50/80 dark:bg-yellow-900/30 backdrop-blur-xl border-2 border-yellow-300/50 dark:border-yellow-600/50 rounded-3xl p-6 shadow-xl">
                <div className="flex items-start gap-3">
                  <Clock className="h-6 w-6 text-yellow-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg text-yellow-800 dark:text-yellow-200">
                      Plan Change Request Pending
                    </h4>
                    <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-2">
                      Your request to change to <strong>{pendingRequest.requested_plan?.display_name}</strong> is awaiting system admin approval.
                    </p>
                    {pendingRequest.request_message && (
                      <div className="mt-3 p-3 bg-yellow-100 dark:bg-yellow-900/40 rounded-lg">
                        <p className="text-xs font-medium text-yellow-800 dark:text-yellow-200 mb-1">Your Message:</p>
                        <p className="text-sm text-yellow-700 dark:text-yellow-300">
                          {pendingRequest.request_message}
                        </p>
                      </div>
                    )}
                    <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-3">
                      Requested on {new Date(pendingRequest.created_at).toLocaleDateString()}
                    </p>
                    <Button
                      variant="outline"
                      onClick={() => handleCancelRequest(pendingRequest.id)}
                      className="mt-4 text-red-600 border-red-300 hover:bg-red-50 dark:text-red-400 dark:border-red-700 dark:hover:bg-red-900/20"
                    >
                      Cancel Request
                    </Button>
                  </div>
                </div>
              </div>
              </div>
            )}

            {/* Request History */}
            {requests.length > 0 && (
              <div className="relative animate-fade-in-up" style={{ animationDelay: '0.6s' }}>
                <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl border-2 border-gray-200/50 dark:border-gray-700/50 rounded-3xl p-6 shadow-xl">
                <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
                  Request History
                </h3>
                <div className="space-y-3">
                  {requests.map((request) => (
                    <div key={request.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium" style={{ color: 'var(--text-primary)' }}>
                          {request.current_plan?.display_name} → {request.requested_plan?.display_name}
                        </p>
                        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                          {new Date(request.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      {getRequestStatusBadge(request.status)}
                    </div>
                  ))}
                </div>
              </div>
              </div>
            )}
          </>
        )}

        {/* Plan Change Request Modal */}
        {showPlanChangeModal && selectedPlanForChange && (
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <Card className="max-w-md w-full p-6">
              <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
                Request Plan Change
              </h3>
              <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>
                Selected plan: <strong>{plans.find(p => p.id === selectedPlanForChange)?.display_name}</strong>
              </p>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--text-primary)' }}>
                  Message to Admin (optional)
                </label>
                <textarea
                  value={planChangeMessage}
                  onChange={(e) => setPlanChangeMessage(e.target.value)}
                  placeholder="Why do you need this plan change?"
                  rows={3}
                  className="w-full p-3 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800"
                  style={{ color: 'var(--text-primary)' }}
                />
              </div>

              <div className="flex gap-2">
                <Button onClick={handleRequestPlanChange} className="flex-1">
                  Submit Request
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowPlanChangeModal(false);
                    setSelectedPlanForChange(null);
                    setPlanChangeMessage('');
                  }}
                >
                  Cancel
                </Button>
              </div>
            </Card>
          </div>
        )}

        {/* Cancel Request Confirmation Modal */}
        {showCancelModal && requestToCancel && (
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <Card className="max-w-md w-full p-6">
              <div className="flex items-start gap-3 mb-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                  <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Cancel Plan Change Request
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                    Are you sure you want to cancel this plan change request? This action cannot be undone.
                  </p>
                </div>
              </div>

              <div className="flex gap-2 mt-6">
                <Button
                  onClick={confirmCancelRequest}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white"
                >
                  Yes, Cancel Request
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowCancelModal(false);
                    setRequestToCancel(null);
                  }}
                  className="flex-1"
                >
                  Keep Request
                </Button>
              </div>
            </Card>
          </div>
        )}
      </div>
    );
  };

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
      case 'calendar':
        return renderCalendarSection();
      case 'company-profile':
        return renderCompanyProfileSection();
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
      <style jsx global>{`
        html, body {
          overflow: hidden !important;
          height: 100vh;
        }
      `}</style>
      <div className="h-[calc(100vh-80px)] -mx-6 -mb-6 overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex-shrink-0 px-6 pt-6">
          <div className="flex items-center justify-between mb-6">
            <div></div>

            <div className="flex items-center gap-4">
              {state.error && <p className="text-red-600 text-sm">{state.error}</p>}
              {state.autoSaving && (
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <LoadingSpinner className="w-4 h-4" />
                  <span>Saving...</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 min-h-0 px-6 pb-6">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full">
          {/* Sidebar Navigation */}
          <div className="space-y-2 overflow-y-auto pr-2 scrollbar-thin">
            {sections.map((section) => {
              const IconComponent = section.icon;
              const isActive = state.activeSection === section.id;

              return (
                <button
                  key={section.id}
                  onClick={() =>
                    setState((prev) => ({
                      ...prev,
                      activeSection: section.id as
                        | 'account'
                        | 'security'
                        | 'notifications'
                        | 'calendar'
                        | 'preferences',
                    }))
                  }
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
          <div className="lg:col-span-3 overflow-y-auto scrollbar-thin">
            <Card className="p-8">{renderCurrentSection()}</Card>
          </div>
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
