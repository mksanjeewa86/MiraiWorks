'use client';

import { useTranslations } from 'next-intl';
import ProfileSectionWrapper from './ProfileSectionWrapper';
import type { Education } from '@/types/profile';
import { GraduationCap, Calendar, Award, BookOpen, Edit2 } from 'lucide-react';
import { format } from 'date-fns';

interface EducationSectionProps {
  educations: Education[];
  isLoading?: boolean;
  onAdd?: () => void;
  onEdit?: (education: Education) => void;
  readOnly?: boolean;
  isOwnProfile?: boolean;
}

export default function EducationSection({
  educations,
  isLoading = false,
  onAdd,
  onEdit,
  readOnly = false,
  isOwnProfile = false,
}: EducationSectionProps) {
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
      title={t('education.title')}
      onAdd={!readOnly ? onAdd : undefined}
      addButtonText={t('education.add')}
      isEmpty={educations.length === 0}
      emptyMessage={t('education.noEducation')}
      isLoading={isLoading}
      sectionId="education"
      showPrivacyToggle={true}
      isOwnProfile={isOwnProfile}
      readOnly={readOnly}
      privacyKey="show_education"
    >
      <div className="space-y-4">
        {educations.map((edu, index) => (
          <div
            key={edu.id}
            className="group relative bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 transition-all duration-300 hover:shadow-xl hover:border-purple-300 dark:hover:border-purple-600 hover:-translate-y-1"
          >
            {/* Timeline connector */}
            {index !== educations.length - 1 && (
              <div className="absolute left-[52px] top-full w-0.5 h-4 bg-gradient-to-b from-purple-500 to-transparent" />
            )}

            {/* Edit button */}
            {!readOnly && onEdit && (
              <button
                onClick={() => onEdit(edu)}
                className="absolute top-4 right-4 p-2 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-purple-50 dark:hover:bg-purple-900/30 hover:text-purple-600 dark:hover:text-purple-400"
                title={t('actions.edit')}
              >
                <Edit2 className="h-4 w-4" />
              </button>
            )}

            <div className="flex gap-4">
              {/* Institution logo */}
              <div className="flex-shrink-0">
                {edu.institution_logo_url ? (
                  <img
                    src={edu.institution_logo_url}
                    alt={edu.institution_name}
                    className="w-16 h-16 rounded-xl object-cover shadow-sm ring-2 ring-gray-100 dark:ring-gray-700"
                  />
                ) : (
                  <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-md">
                    <GraduationCap className="h-8 w-8 text-white" />
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                {/* Institution name */}
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1 line-clamp-1">
                  {edu.institution_name}
                </h3>

                {/* Degree information */}
                <div className="flex items-center gap-2 mb-3">
                  <BookOpen className="h-4 w-4 text-purple-600 dark:text-purple-400 flex-shrink-0" />
                  <p className="text-base font-semibold text-gray-700 dark:text-gray-300 line-clamp-1">
                    {edu.degree_type} {t('education.degreeIn')} {edu.field_of_study}
                  </p>
                </div>

                {/* Meta info */}
                <div className="flex flex-wrap gap-3 text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {/* Date range */}
                  {(edu.start_date || edu.end_date) && (
                    <div className="flex items-center gap-1.5 bg-gray-50 dark:bg-gray-700/50 px-3 py-1.5 rounded-lg">
                      <Calendar className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                      <span className="font-medium">
                        {edu.start_date && formatDate(edu.start_date)}
                        {edu.start_date && edu.end_date && ' - '}
                        {edu.end_date && formatDate(edu.end_date)}
                      </span>
                    </div>
                  )}

                  {/* Graduation year */}
                  {edu.graduation_year && (
                    <div className="flex items-center gap-1.5 bg-purple-50 dark:bg-purple-900/20 px-3 py-1.5 rounded-lg">
                      <GraduationCap className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                      <span className="font-medium text-purple-700 dark:text-purple-300">
                        {t('education.classOf')} {edu.graduation_year}
                      </span>
                    </div>
                  )}

                  {/* GPA */}
                  {edu.gpa && (
                    <div className="flex items-center gap-1.5 bg-green-50 dark:bg-green-900/20 px-3 py-1.5 rounded-lg">
                      <span className="font-medium text-green-700 dark:text-green-300">
                        {t('education.gpa')}: {edu.gpa}
                        {edu.gpa_max && `/${edu.gpa_max}`}
                      </span>
                    </div>
                  )}
                </div>

                {/* Honors and awards */}
                {edu.honors_awards && (
                  <div className="flex items-start gap-2 mb-4 p-3 rounded-lg bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 border border-yellow-200 dark:border-yellow-700">
                    <Award className="h-5 w-5 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-yellow-900 dark:text-yellow-100 leading-relaxed">
                      {edu.honors_awards}
                    </p>
                  </div>
                )}

                {/* Description */}
                {edu.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed whitespace-pre-line">
                    {edu.description}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </ProfileSectionWrapper>
  );
}
