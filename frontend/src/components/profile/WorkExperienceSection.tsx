'use client';

import { useTranslations } from 'next-intl';
import ProfileSectionWrapper from './ProfileSectionWrapper';
import type { WorkExperience } from '@/types/profile';
import { Building2, Calendar, MapPin, Briefcase, Edit2 } from 'lucide-react';
import { format } from 'date-fns';

interface WorkExperienceSectionProps {
  experiences: WorkExperience[];
  isLoading?: boolean;
  onAdd?: () => void;
  onEdit?: (experience: WorkExperience) => void;
  readOnly?: boolean;
  isOwnProfile?: boolean;
}

export default function WorkExperienceSection({
  experiences,
  isLoading = false,
  onAdd,
  onEdit,
  readOnly = false,
  isOwnProfile = false,
}: WorkExperienceSectionProps) {
  const t = useTranslations('profile');

  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    try {
      return format(new Date(dateString), 'MMM yyyy');
    } catch {
      return dateString;
    }
  };

  return (
    <ProfileSectionWrapper
      title={t('experience.title')}
      onAdd={!readOnly ? onAdd : undefined}
      addButtonText={t('experience.add')}
      isEmpty={experiences.length === 0}
      emptyMessage={t('experience.noExperience')}
      isLoading={isLoading}
      sectionId="work_experience"
      showPrivacyToggle={true}
      isOwnProfile={isOwnProfile}
      readOnly={readOnly}
      privacyKey="show_work_experience"
    >
      <div className="space-y-4">
        {experiences.map((exp, index) => (
          <div
            key={exp.id}
            className="group relative bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 transition-all duration-300 hover:shadow-xl hover:border-blue-300 dark:hover:border-blue-600 hover:-translate-y-1"
          >
            {/* Timeline connector */}
            {index !== experiences.length - 1 && (
              <div className="absolute left-[52px] top-full w-0.5 h-4 bg-gradient-to-b from-blue-500 to-transparent" />
            )}

            {/* Edit button */}
            {!readOnly && onEdit && (
              <button
                onClick={() => onEdit(exp)}
                className="absolute top-4 right-4 p-2 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-blue-50 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-400"
                title={t('actions.edit')}
              >
                <Edit2 className="h-4 w-4" />
              </button>
            )}

            <div className="flex gap-4">
              {/* Company logo */}
              <div className="flex-shrink-0">
                {exp.company_logo_url ? (
                  <img
                    src={exp.company_logo_url}
                    alt={exp.company_name}
                    className="w-16 h-16 rounded-xl object-cover shadow-sm ring-2 ring-gray-100 dark:ring-gray-700"
                  />
                ) : (
                  <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-md">
                    <Building2 className="h-8 w-8 text-white" />
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                {/* Position title */}
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1 line-clamp-1">
                  {exp.position_title}
                </h3>

                {/* Company name */}
                <p className="text-base font-semibold text-gray-700 dark:text-gray-300 mb-3 line-clamp-1">
                  {exp.company_name}
                </p>

                {/* Meta info */}
                <div className="flex flex-wrap gap-3 text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {/* Date range */}
                  <div className="flex items-center gap-1.5 bg-gray-50 dark:bg-gray-700/50 px-3 py-1.5 rounded-lg">
                    <Calendar className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                    <span className="font-medium">
                      {formatDate(exp.start_date)} - {exp.is_current ? t('experience.present') : formatDate(exp.end_date)}
                    </span>
                  </div>

                  {/* Employment type */}
                  {exp.employment_type && (
                    <div className="flex items-center gap-1.5 bg-blue-50 dark:bg-blue-900/20 px-3 py-1.5 rounded-lg">
                      <Briefcase className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                      <span className="font-medium text-blue-700 dark:text-blue-300">
                        {exp.employment_type}
                      </span>
                    </div>
                  )}

                  {/* Location */}
                  {exp.location && (
                    <div className="flex items-center gap-1.5 bg-purple-50 dark:bg-purple-900/20 px-3 py-1.5 rounded-lg">
                      <MapPin className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                      <span className="font-medium text-purple-700 dark:text-purple-300">
                        {exp.location}
                      </span>
                    </div>
                  )}
                </div>

                {/* Description */}
                {exp.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed mb-4 whitespace-pre-line">
                    {exp.description}
                  </p>
                )}

                {/* Skills tags */}
                {exp.skills && (
                  <div className="flex flex-wrap gap-2">
                    {exp.skills.split(',').map((skill, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center px-3 py-1 rounded-full bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 text-blue-700 dark:text-blue-300 text-xs font-semibold border border-blue-200 dark:border-blue-700 hover:shadow-md transition-shadow"
                      >
                        {skill.trim()}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </ProfileSectionWrapper>
  );
}
