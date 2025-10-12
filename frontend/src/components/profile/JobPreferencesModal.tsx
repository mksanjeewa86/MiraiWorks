'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import type { JobPreference, JobPreferenceCreate, JobPreferenceUpdate } from '@/types/profile';
import { JobSearchStatus, SalaryPeriod } from '@/types/profile';

interface JobPreferencesModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: JobPreferenceCreate | JobPreferenceUpdate) => Promise<void>;
  jobPreferences?: JobPreference | null;
  mode: 'create' | 'edit';
}

export default function JobPreferencesModal({
  isOpen,
  onClose,
  onSave,
  jobPreferences,
  mode,
}: JobPreferencesModalProps) {
  const t = useTranslations('profile');
  const [saving, setSaving] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    desired_job_types: '',
    desired_salary_min: '',
    desired_salary_max: '',
    salary_currency: 'USD',
    salary_period: 'yearly',
    willing_to_relocate: false,
    preferred_locations: '',
    work_mode_preferences: '',
    available_from: '',
    notice_period_days: '',
    job_search_status: 'not_looking',
    preferred_industries: '',
    preferred_company_sizes: '',
    other_preferences: '',
  });

  // Initialize form with existing data when editing
  useEffect(() => {
    if (isOpen && jobPreferences && mode === 'edit') {
      setFormData({
        desired_job_types: jobPreferences.desired_job_types || '',
        desired_salary_min: jobPreferences.desired_salary_min?.toString() || '',
        desired_salary_max: jobPreferences.desired_salary_max?.toString() || '',
        salary_currency: jobPreferences.salary_currency || 'USD',
        salary_period: jobPreferences.salary_period || 'yearly',
        willing_to_relocate: jobPreferences.willing_to_relocate || false,
        preferred_locations: jobPreferences.preferred_locations || '',
        work_mode_preferences: jobPreferences.work_mode_preferences || '',
        available_from: jobPreferences.available_from || '',
        notice_period_days: jobPreferences.notice_period_days?.toString() || '',
        job_search_status: jobPreferences.job_search_status || 'not_looking',
        preferred_industries: jobPreferences.preferred_industries || '',
        preferred_company_sizes: jobPreferences.preferred_company_sizes || '',
        other_preferences: jobPreferences.other_preferences || '',
      });
    } else if (isOpen && mode === 'create') {
      // Reset form for create mode
      setFormData({
        desired_job_types: '',
        desired_salary_min: '',
        desired_salary_max: '',
        salary_currency: 'USD',
        salary_period: 'yearly',
        willing_to_relocate: false,
        preferred_locations: '',
        work_mode_preferences: '',
        available_from: '',
        notice_period_days: '',
        job_search_status: 'not_looking',
        preferred_industries: '',
        preferred_company_sizes: '',
        other_preferences: '',
      });
    }
  }, [isOpen, jobPreferences, mode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const dataToSave: JobPreferenceCreate | JobPreferenceUpdate = {
        desired_job_types: formData.desired_job_types || null,
        desired_salary_min: formData.desired_salary_min ? parseInt(formData.desired_salary_min) : null,
        desired_salary_max: formData.desired_salary_max ? parseInt(formData.desired_salary_max) : null,
        salary_currency: formData.salary_currency,
        salary_period: formData.salary_period,
        willing_to_relocate: formData.willing_to_relocate,
        preferred_locations: formData.preferred_locations || null,
        work_mode_preferences: formData.work_mode_preferences || null,
        available_from: formData.available_from || null,
        notice_period_days: formData.notice_period_days ? parseInt(formData.notice_period_days) : null,
        job_search_status: formData.job_search_status,
        preferred_industries: formData.preferred_industries || null,
        preferred_company_sizes: formData.preferred_company_sizes || null,
        other_preferences: formData.other_preferences || null,
      };

      await onSave(dataToSave);
      onClose();
    } catch (error) {
      console.error('Error saving job preferences:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {mode === 'create' ? 'Set Job Preferences' : t('jobPreferences.edit')}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Job Search Status - Most Important */}
          <div className="space-y-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-700">
            <Label htmlFor="job_search_status" className="text-base font-semibold">
              {t('jobPreferences.form.jobSearchStatus')} *
            </Label>
            <Select
              value={formData.job_search_status}
              onValueChange={(value) => setFormData({ ...formData, job_search_status: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={JobSearchStatus.ACTIVELY_LOOKING}>
                  {t('jobPreferences.status.actively_looking')}
                </SelectItem>
                <SelectItem value={JobSearchStatus.OPEN_TO_OPPORTUNITIES}>
                  {t('jobPreferences.status.open_to_opportunities')}
                </SelectItem>
                <SelectItem value={JobSearchStatus.NOT_LOOKING}>
                  {t('jobPreferences.status.not_looking')}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Desired Job Types */}
          <div className="space-y-2">
            <Label htmlFor="desired_job_types">{t('jobPreferences.form.desiredJobTypes')}</Label>
            <Input
              id="desired_job_types"
              value={formData.desired_job_types}
              onChange={(e) => setFormData({ ...formData, desired_job_types: e.target.value })}
              placeholder="Full-time, Part-time, Contract, Freelance"
            />
            <p className="text-xs text-gray-500">Comma-separated list</p>
          </div>

          {/* Salary Expectations */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="desired_salary_min">{t('jobPreferences.form.desiredSalaryMin')}</Label>
              <Input
                id="desired_salary_min"
                type="number"
                value={formData.desired_salary_min}
                onChange={(e) => setFormData({ ...formData, desired_salary_min: e.target.value })}
                placeholder="50000"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="desired_salary_max">{t('jobPreferences.form.desiredSalaryMax')}</Label>
              <Input
                id="desired_salary_max"
                type="number"
                value={formData.desired_salary_max}
                onChange={(e) => setFormData({ ...formData, desired_salary_max: e.target.value })}
                placeholder="100000"
              />
            </div>
          </div>

          {/* Currency and Period */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="salary_currency">{t('jobPreferences.form.salaryCurrency')}</Label>
              <Select
                value={formData.salary_currency}
                onValueChange={(value) => setFormData({ ...formData, salary_currency: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="USD">USD</SelectItem>
                  <SelectItem value="JPY">JPY</SelectItem>
                  <SelectItem value="EUR">EUR</SelectItem>
                  <SelectItem value="GBP">GBP</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="salary_period">{t('jobPreferences.form.salaryPeriod')}</Label>
              <Select
                value={formData.salary_period}
                onValueChange={(value) => setFormData({ ...formData, salary_period: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={SalaryPeriod.YEARLY}>{t('jobPreferences.salaryPeriod.yearly')}</SelectItem>
                  <SelectItem value={SalaryPeriod.MONTHLY}>{t('jobPreferences.salaryPeriod.monthly')}</SelectItem>
                  <SelectItem value={SalaryPeriod.HOURLY}>{t('jobPreferences.salaryPeriod.hourly')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Work Mode Preferences */}
          <div className="space-y-2">
            <Label htmlFor="work_mode_preferences">{t('jobPreferences.form.workModePreferences')}</Label>
            <Input
              id="work_mode_preferences"
              value={formData.work_mode_preferences}
              onChange={(e) => setFormData({ ...formData, work_mode_preferences: e.target.value })}
              placeholder="Remote, Hybrid, Onsite"
            />
            <p className="text-xs text-gray-500">Comma-separated list</p>
          </div>

          {/* Preferred Locations */}
          <div className="space-y-2">
            <Label htmlFor="preferred_locations">{t('jobPreferences.form.preferredLocations')}</Label>
            <Input
              id="preferred_locations"
              value={formData.preferred_locations}
              onChange={(e) => setFormData({ ...formData, preferred_locations: e.target.value })}
              placeholder="Tokyo, Osaka, Remote"
            />
            <p className="text-xs text-gray-500">Comma-separated list</p>
          </div>

          {/* Willing to Relocate */}
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="willing_to_relocate"
              checked={formData.willing_to_relocate}
              onChange={(e) => setFormData({ ...formData, willing_to_relocate: e.target.checked })}
              className="h-4 w-4 rounded border-gray-300"
            />
            <Label htmlFor="willing_to_relocate" className="font-normal cursor-pointer">
              {t('jobPreferences.form.willingToRelocate')}
            </Label>
          </div>

          {/* Availability */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="available_from">{t('jobPreferences.form.availableFrom')}</Label>
              <Input
                id="available_from"
                type="date"
                value={formData.available_from}
                onChange={(e) => setFormData({ ...formData, available_from: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="notice_period_days">{t('jobPreferences.form.noticePeriodDays')}</Label>
              <Input
                id="notice_period_days"
                type="number"
                value={formData.notice_period_days}
                onChange={(e) => setFormData({ ...formData, notice_period_days: e.target.value })}
                placeholder="30"
              />
            </div>
          </div>

          {/* Preferred Industries */}
          <div className="space-y-2">
            <Label htmlFor="preferred_industries">{t('jobPreferences.form.preferredIndustries')}</Label>
            <Input
              id="preferred_industries"
              value={formData.preferred_industries}
              onChange={(e) => setFormData({ ...formData, preferred_industries: e.target.value })}
              placeholder="Technology, Finance, Healthcare"
            />
            <p className="text-xs text-gray-500">Comma-separated list</p>
          </div>

          {/* Preferred Company Sizes */}
          <div className="space-y-2">
            <Label htmlFor="preferred_company_sizes">{t('jobPreferences.form.preferredCompanySizes')}</Label>
            <Input
              id="preferred_company_sizes"
              value={formData.preferred_company_sizes}
              onChange={(e) => setFormData({ ...formData, preferred_company_sizes: e.target.value })}
              placeholder="Startup, SME, Enterprise"
            />
            <p className="text-xs text-gray-500">Comma-separated list</p>
          </div>

          {/* Other Preferences */}
          <div className="space-y-2">
            <Label htmlFor="other_preferences">{t('jobPreferences.form.otherPreferences')}</Label>
            <Textarea
              id="other_preferences"
              value={formData.other_preferences}
              onChange={(e) => setFormData({ ...formData, other_preferences: e.target.value })}
              placeholder={t('jobPreferences.form.otherPreferencesPlaceholder')}
              rows={4}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={onClose} disabled={saving}>
              {t('actions.cancel')}
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? t('actions.saving') : t('jobPreferences.form.save')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
