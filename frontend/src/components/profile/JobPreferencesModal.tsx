'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Briefcase, X } from 'lucide-react';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/input';
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
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent
        closeButton={false}
        className="flex flex-col h-[90vh] max-h-[90vh] w-full max-w-4xl md:max-w-3xl overflow-hidden rounded-3xl border border-slate-200 bg-white text-slate-900 shadow-[0_30px_80px_-20px_rgba(15,23,42,0.2)]"
      >
        <DialogHeader className="flex-shrink-0 px-6 pt-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                  <Briefcase className="h-5 w-5" />
                </span>
                <div>
                  <DialogTitle className="text-xl font-semibold text-slate-900">
                    {mode === 'create' ? 'Set Job Preferences' : 'Edit Job Preferences'}
                  </DialogTitle>
                  <DialogDescription className="text-sm text-slate-500">
                    {mode === 'create'
                      ? 'Define your career goals and preferences to help recruiters find the right opportunities.'
                      : 'Update your job search preferences and career goals.'}
                  </DialogDescription>
                </div>
              </div>
            </div>
            <DialogClose className="rounded-lg border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700">
              <X className="h-4 w-4" />
            </DialogClose>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-1 flex-col min-h-0">
          <div className="flex-1 overflow-y-auto px-6 py-6 min-h-0">
            <div className="space-y-8">
              {/* Main Section */}
              <div className="grid gap-6 rounded-2xl border border-slate-200 bg-slate-50 p-6">
                {/* Job Search Status - Most Important */}
                <div className="space-y-2">
                  <label htmlFor="job_search_status" className="text-sm font-medium text-slate-700">
                    {t('jobPreferences.form.jobSearchStatus')} *
                  </label>
                  <Select
                    value={formData.job_search_status}
                    onValueChange={(value) => setFormData({ ...formData, job_search_status: value })}
                  >
                    <SelectTrigger className="border-slate-300 bg-white text-slate-900">
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
                  <p className="text-xs text-slate-500">Let recruiters know your current availability</p>
                </div>

                {/* Desired Job Types */}
                <div className="space-y-2">
                  <label htmlFor="desired_job_types" className="text-sm font-medium text-slate-700">
                    {t('jobPreferences.form.desiredJobTypes')}
                  </label>
                  <Input
                    id="desired_job_types"
                    value={formData.desired_job_types}
                    onChange={(e) => setFormData({ ...formData, desired_job_types: e.target.value })}
                    placeholder="Full-time, Part-time, Contract, Freelance"
                  />
                  <p className="text-xs text-slate-500">Comma-separated list</p>
                </div>

                {/* Salary Expectations */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label htmlFor="desired_salary_min" className="text-sm font-medium text-slate-700">
                      {t('jobPreferences.form.desiredSalaryMin')}
                    </label>
                    <Input
                      id="desired_salary_min"
                      type="number"
                      value={formData.desired_salary_min}
                      onChange={(e) => setFormData({ ...formData, desired_salary_min: e.target.value })}
                      placeholder="50000"
                    />
                  </div>
                  <div className="space-y-2">
                    <label htmlFor="desired_salary_max" className="text-sm font-medium text-slate-700">
                      {t('jobPreferences.form.desiredSalaryMax')}
                    </label>
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
                    <label htmlFor="salary_currency" className="text-sm font-medium text-slate-700">
                      {t('jobPreferences.form.salaryCurrency')}
                    </label>
                    <Select
                      value={formData.salary_currency}
                      onValueChange={(value) => setFormData({ ...formData, salary_currency: value })}
                    >
                      <SelectTrigger className="border-slate-300 bg-white text-slate-900">
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
                    <label htmlFor="salary_period" className="text-sm font-medium text-slate-700">
                      {t('jobPreferences.form.salaryPeriod')}
                    </label>
                    <Select
                      value={formData.salary_period}
                      onValueChange={(value) => setFormData({ ...formData, salary_period: value })}
                    >
                      <SelectTrigger className="border-slate-300 bg-white text-slate-900">
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
                  <label htmlFor="work_mode_preferences" className="text-sm font-medium text-slate-700">
                    {t('jobPreferences.form.workModePreferences')}
                  </label>
                  <Input
                    id="work_mode_preferences"
                    value={formData.work_mode_preferences}
                    onChange={(e) => setFormData({ ...formData, work_mode_preferences: e.target.value })}
                    placeholder="Remote, Hybrid, Onsite"
                  />
                  <p className="text-xs text-slate-500">Comma-separated list</p>
                </div>

                {/* Preferred Locations */}
                <div className="space-y-2">
                  <label htmlFor="preferred_locations" className="text-sm font-medium text-slate-700">
                    {t('jobPreferences.form.preferredLocations')}
                  </label>
                  <Input
                    id="preferred_locations"
                    value={formData.preferred_locations}
                    onChange={(e) => setFormData({ ...formData, preferred_locations: e.target.value })}
                    placeholder="Tokyo, Osaka, Remote"
                  />
                  <p className="text-xs text-slate-500">Comma-separated list</p>
                </div>

                {/* Willing to Relocate */}
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="willing_to_relocate"
                    checked={formData.willing_to_relocate}
                    onChange={(e) => setFormData({ ...formData, willing_to_relocate: e.target.checked })}
                    className="h-4 w-4 rounded border-slate-300"
                  />
                  <label htmlFor="willing_to_relocate" className="text-sm font-medium text-slate-700 cursor-pointer">
                    {t('jobPreferences.form.willingToRelocate')}
                  </label>
                </div>

                {/* Availability */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label htmlFor="available_from" className="text-sm font-medium text-slate-700">
                      {t('jobPreferences.form.availableFrom')}
                    </label>
                    <Input
                      id="available_from"
                      type="date"
                      value={formData.available_from}
                      onChange={(e) => setFormData({ ...formData, available_from: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <label htmlFor="notice_period_days" className="text-sm font-medium text-slate-700">
                      {t('jobPreferences.form.noticePeriodDays')}
                    </label>
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
                  <label htmlFor="preferred_industries" className="text-sm font-medium text-slate-700">
                    {t('jobPreferences.form.preferredIndustries')}
                  </label>
                  <Input
                    id="preferred_industries"
                    value={formData.preferred_industries}
                    onChange={(e) => setFormData({ ...formData, preferred_industries: e.target.value })}
                    placeholder="Technology, Finance, Healthcare"
                  />
                  <p className="text-xs text-slate-500">Comma-separated list</p>
                </div>

                {/* Preferred Company Sizes */}
                <div className="space-y-2">
                  <label htmlFor="preferred_company_sizes" className="text-sm font-medium text-slate-700">
                    {t('jobPreferences.form.preferredCompanySizes')}
                  </label>
                  <Input
                    id="preferred_company_sizes"
                    value={formData.preferred_company_sizes}
                    onChange={(e) => setFormData({ ...formData, preferred_company_sizes: e.target.value })}
                    placeholder="Startup, SME, Enterprise"
                  />
                  <p className="text-xs text-slate-500">Comma-separated list</p>
                </div>

                {/* Other Preferences */}
                <div className="space-y-2">
                  <label htmlFor="other_preferences" className="text-sm font-medium text-slate-700">
                    {t('jobPreferences.form.otherPreferences')}
                  </label>
                  <Textarea
                    id="other_preferences"
                    value={formData.other_preferences}
                    onChange={(e) => setFormData({ ...formData, other_preferences: e.target.value })}
                    placeholder={t('jobPreferences.form.otherPreferencesPlaceholder')}
                    rows={4}
                    className="border border-slate-300 bg-white text-slate-900 focus-visible:ring-blue-500"
                  />
                </div>
              </div>
            </div>
          </div>

          <DialogFooter className="flex-shrink-0 gap-3 border-t border-slate-200 bg-white px-6 py-4">
            <Button
              type="button"
              variant="ghost"
              disabled={saving}
              onClick={onClose}
              className="min-w-[120px] border border-slate-300 bg-white text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              loading={saving}
              className="min-w-[160px] bg-blue-600 text-white shadow-lg shadow-blue-500/30 hover:bg-blue-600/90"
            >
              {saving ? 'Saving...' : mode === 'create' ? 'Create Preferences' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
