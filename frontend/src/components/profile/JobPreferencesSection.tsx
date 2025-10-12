'use client';

import { useTranslations } from 'next-intl';
import ProfileSectionWrapper from './ProfileSectionWrapper';
import type { JobPreference } from '@/types/profile';
import { Briefcase, DollarSign, MapPin, Calendar, Building2, Target } from 'lucide-react';

interface JobPreferencesSectionProps {
  jobPreferences: JobPreference | null;
  isLoading?: boolean;
  onEdit?: () => void;
  readOnly?: boolean;
  isOwnProfile?: boolean;
}

export default function JobPreferencesSection({
  jobPreferences,
  isLoading = false,
  onEdit,
  readOnly = false,
  isOwnProfile = false,
}: JobPreferencesSectionProps) {
  const t = useTranslations('profile');

  const isEmpty = !jobPreferences || !jobPreferences.job_search_status;

  const formatSalary = (min: number | null, max: number | null, currency: string, period: string) => {
    if (!min && !max) return null;
    const periodText = t(`jobPreferences.salaryPeriod.${period}` as any);
    if (min && max) {
      return `${currency} ${min.toLocaleString()} - ${max.toLocaleString()} (${periodText})`;
    } else if (min) {
      return `${currency} ${min.toLocaleString()}+ (${periodText})`;
    } else if (max) {
      return `Up to ${currency} ${max.toLocaleString()} (${periodText})`;
    }
    return null;
  };

  const parseList = (str: string | null): string[] => {
    if (!str) return [];
    return str.split(',').map(item => item.trim()).filter(Boolean);
  };

  return (
    <ProfileSectionWrapper
      title={t('jobPreferences.title')}
      onEdit={!readOnly && isOwnProfile ? onEdit : undefined}
      editButtonText={t('jobPreferences.edit')}
      isEmpty={isEmpty}
      emptyMessage={t('jobPreferences.noPreferences')}
      isLoading={isLoading}
      sectionId="job-preferences"
      showPrivacyToggle={false}
      isOwnProfile={isOwnProfile}
      readOnly={readOnly}
    >
      {jobPreferences && (
        <div className="space-y-6">
          {/* Job Search Status - Prominent Display */}
          <div className="flex items-center justify-center p-6 rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-2 border-blue-200 dark:border-blue-700">
            <div className="text-center">
              <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-lg font-bold shadow-lg">
                <Target className="h-6 w-6" />
                <span>{t(`jobPreferences.status.${jobPreferences.job_search_status}` as any)}</span>
              </div>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {/* Desired Job Types */}
            {jobPreferences.desired_job_types && parseList(jobPreferences.desired_job_types).length > 0 && (
              <div className="p-5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30">
                    <Briefcase className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
                      {t('jobPreferences.form.desiredJobTypes')}
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {parseList(jobPreferences.desired_job_types).map((type, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-sm font-medium border border-blue-200 dark:border-blue-700"
                        >
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Salary Expectations */}
            {(jobPreferences.desired_salary_min || jobPreferences.desired_salary_max) && (
              <div className="p-5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900/30">
                    <DollarSign className="h-5 w-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
                      Salary Expectations
                    </h4>
                    <p className="text-base font-medium text-gray-900 dark:text-white">
                      {formatSalary(
                        jobPreferences.desired_salary_min,
                        jobPreferences.desired_salary_max,
                        jobPreferences.salary_currency,
                        jobPreferences.salary_period
                      )}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Work Mode Preferences */}
            {jobPreferences.work_mode_preferences && parseList(jobPreferences.work_mode_preferences).length > 0 && (
              <div className="p-5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/30">
                    <Building2 className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
                      {t('jobPreferences.form.workModePreferences')}
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {parseList(jobPreferences.work_mode_preferences).map((mode, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 rounded-full bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 text-sm font-medium border border-purple-200 dark:border-purple-700"
                        >
                          {mode}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Preferred Locations */}
            {jobPreferences.preferred_locations && parseList(jobPreferences.preferred_locations).length > 0 && (
              <div className="p-5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-orange-100 dark:bg-orange-900/30">
                    <MapPin className="h-5 w-5 text-orange-600 dark:text-orange-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
                      {t('jobPreferences.form.preferredLocations')}
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {parseList(jobPreferences.preferred_locations).map((location, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 rounded-full bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300 text-sm font-medium border border-orange-200 dark:border-orange-700"
                        >
                          {location}
                        </span>
                      ))}
                    </div>
                    {jobPreferences.willing_to_relocate && (
                      <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        ✓ Willing to relocate
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Availability */}
            {(jobPreferences.available_from || jobPreferences.notice_period_days) && (
              <div className="p-5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
                    <Calendar className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
                      Availability
                    </h4>
                    {jobPreferences.available_from && (
                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-1">
                        <span className="font-medium">Available from:</span>{' '}
                        {new Date(jobPreferences.available_from).toLocaleDateString()}
                      </p>
                    )}
                    {jobPreferences.notice_period_days && (
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        <span className="font-medium">Notice period:</span>{' '}
                        {jobPreferences.notice_period_days} days
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Preferred Industries */}
            {jobPreferences.preferred_industries && parseList(jobPreferences.preferred_industries).length > 0 && (
              <div className="p-5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow md:col-span-2">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-teal-100 dark:bg-teal-900/30">
                    <Target className="h-5 w-5 text-teal-600 dark:text-teal-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
                      {t('jobPreferences.form.preferredIndustries')}
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {parseList(jobPreferences.preferred_industries).map((industry, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 rounded-full bg-teal-50 dark:bg-teal-900/20 text-teal-700 dark:text-teal-300 text-sm font-medium border border-teal-200 dark:border-teal-700"
                        >
                          {industry}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Preferred Company Sizes */}
            {jobPreferences.preferred_company_sizes && parseList(jobPreferences.preferred_company_sizes).length > 0 && (
              <div className="p-5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow md:col-span-2">
                <div className="flex items-start gap-3">
                  <div className="p-2 rounded-lg bg-cyan-100 dark:bg-cyan-900/30">
                    <Building2 className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
                      {t('jobPreferences.form.preferredCompanySizes')}
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {parseList(jobPreferences.preferred_company_sizes).map((size, idx) => (
                        <span
                          key={idx}
                          className="px-3 py-1 rounded-full bg-cyan-50 dark:bg-cyan-900/20 text-cyan-700 dark:text-cyan-300 text-sm font-medium border border-cyan-200 dark:border-cyan-700"
                        >
                          {size}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Other Preferences */}
            {jobPreferences.other_preferences && (
              <div className="p-5 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow md:col-span-2">
                <h4 className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2">
                  {t('jobPreferences.form.otherPreferences')}
                </h4>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                  {jobPreferences.other_preferences}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </ProfileSectionWrapper>
  );
}
