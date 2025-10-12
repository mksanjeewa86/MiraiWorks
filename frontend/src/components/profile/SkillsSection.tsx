'use client';

import { useTranslations } from 'next-intl';
import ProfileSectionWrapper from './ProfileSectionWrapper';
import type { Skill } from '@/types/profile';
import { Award, Clock, Edit2, Star, TrendingUp } from 'lucide-react';

interface SkillsSectionProps {
  skills: Skill[];
  isLoading?: boolean;
  onAdd?: () => void;
  onEdit?: (skill: Skill) => void;
  readOnly?: boolean;
  showCategory?: boolean;
  isOwnProfile?: boolean;
}

export default function SkillsSection({
  skills,
  isLoading = false,
  onAdd,
  onEdit,
  readOnly = false,
  showCategory = true,
  isOwnProfile = false,
}: SkillsSectionProps) {
  const t = useTranslations('profile');

  // Group skills by category
  const groupedSkills = skills.reduce((acc, skill) => {
    const category = skill.category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(skill);
    return acc;
  }, {} as Record<string, Skill[]>);

  const getProficiencyPercentage = (level: string | null): number => {
    switch (level?.toLowerCase()) {
      case 'expert':
        return 100;
      case 'advanced':
        return 75;
      case 'intermediate':
        return 50;
      case 'beginner':
        return 25;
      default:
        return 0;
    }
  };

  const getProficiencyColor = (level: string | null) => {
    switch (level?.toLowerCase()) {
      case 'expert':
        return {
          bg: 'from-purple-500 to-pink-600',
          text: 'text-purple-700 dark:text-purple-300',
          light: 'bg-purple-50 dark:bg-purple-900/20',
        };
      case 'advanced':
        return {
          bg: 'from-blue-500 to-cyan-600',
          text: 'text-blue-700 dark:text-blue-300',
          light: 'bg-blue-50 dark:bg-blue-900/20',
        };
      case 'intermediate':
        return {
          bg: 'from-green-500 to-emerald-600',
          text: 'text-green-700 dark:text-green-300',
          light: 'bg-green-50 dark:bg-green-900/20',
        };
      case 'beginner':
        return {
          bg: 'from-gray-400 to-gray-600',
          text: 'text-gray-700 dark:text-gray-300',
          light: 'bg-gray-50 dark:bg-gray-900/20',
        };
      default:
        return {
          bg: 'from-gray-400 to-gray-600',
          text: 'text-gray-700 dark:text-gray-300',
          light: 'bg-gray-50 dark:bg-gray-900/20',
        };
    }
  };

  return (
    <ProfileSectionWrapper
      title={t('skills.title')}
      onAdd={!readOnly ? onAdd : undefined}
      addButtonText={t('skills.add')}
      isEmpty={skills.length === 0}
      emptyMessage={t('skills.noSkills')}
      isLoading={isLoading}
      sectionId="skills"
      showPrivacyToggle={true}
      isOwnProfile={isOwnProfile}
      readOnly={readOnly}
      privacyKey="show_skills"
    >
      <div className="space-y-6">
        {showCategory ? (
          // Grouped by category
          Object.entries(groupedSkills).map(([category, categorySkills]) => (
            <div key={category}>
              {/* Category header with icon */}
              <div className="flex items-center gap-2 mb-4 pb-2 border-b border-gray-200 dark:border-gray-700">
                <TrendingUp className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                <h4 className="text-base font-bold text-gray-900 dark:text-white">
                  {category}
                </h4>
                <span className="ml-auto text-xs font-semibold px-2 py-1 rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                  {categorySkills.length} {categorySkills.length === 1 ? 'skill' : 'skills'}
                </span>
              </div>

              {/* Skills grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {categorySkills.map((skill) => {
                  const proficiencyColors = getProficiencyColor(skill.proficiency_level);
                  const proficiencyPercentage = getProficiencyPercentage(skill.proficiency_level);

                  return (
                    <div
                      key={skill.id}
                      className="group relative bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 transition-all duration-300 hover:shadow-lg hover:border-blue-300 dark:hover:border-blue-600 hover:-translate-y-0.5"
                    >
                      {/* Edit button */}
                      {!readOnly && onEdit && (
                        <button
                          onClick={() => onEdit(skill)}
                          className="absolute top-3 right-3 p-1.5 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-blue-50 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-400"
                          title={t('actions.edit')}
                        >
                          <Edit2 className="h-3.5 w-3.5" />
                        </button>
                      )}

                      {/* Skill name */}
                      <div className="flex items-start gap-2 mb-3">
                        <Star className={`h-5 w-5 mt-0.5 flex-shrink-0 ${proficiencyColors.text}`} />
                        <h5 className="text-base font-bold text-gray-900 dark:text-white line-clamp-2">
                          {skill.skill_name}
                        </h5>
                      </div>

                      {/* Progress bar */}
                      {skill.proficiency_level && (
                        <div className="mb-3">
                          <div className="flex items-center justify-between mb-1.5">
                            <span className={`text-xs font-semibold ${proficiencyColors.text}`}>
                              {skill.proficiency_level}
                            </span>
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              {proficiencyPercentage}%
                            </span>
                          </div>
                          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                            <div
                              className={`h-full bg-gradient-to-r ${proficiencyColors.bg} transition-all duration-500 ease-out`}
                              style={{ width: `${proficiencyPercentage}%` }}
                            />
                          </div>
                        </div>
                      )}

                      {/* Metadata */}
                      <div className="flex flex-wrap gap-2">
                        {skill.years_of_experience !== null && skill.years_of_experience !== undefined && (
                          <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                            <Clock className="h-3.5 w-3.5" />
                            <span className="text-xs font-medium">
                              {t('skills.yearsOfExperience', { years: skill.years_of_experience })}
                            </span>
                          </div>
                        )}
                        {skill.endorsement_count > 0 && (
                          <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300">
                            <Award className="h-3.5 w-3.5" />
                            <span className="text-xs font-medium">
                              {t('skills.endorsements', { count: skill.endorsement_count })}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))
        ) : (
          // Flat list with modern card design
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {skills.map((skill) => {
              const proficiencyColors = getProficiencyColor(skill.proficiency_level);
              const proficiencyPercentage = getProficiencyPercentage(skill.proficiency_level);

              return (
                <div
                  key={skill.id}
                  className="group relative bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 transition-all duration-300 hover:shadow-lg hover:border-blue-300 dark:hover:border-blue-600 hover:-translate-y-0.5"
                >
                  {/* Edit button */}
                  {!readOnly && onEdit && (
                    <button
                      onClick={() => onEdit(skill)}
                      className="absolute top-3 right-3 p-1.5 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-blue-50 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-400"
                      title={t('actions.edit')}
                    >
                      <Edit2 className="h-3.5 w-3.5" />
                    </button>
                  )}

                  {/* Skill name */}
                  <div className="flex items-start gap-2 mb-3">
                    <Star className={`h-5 w-5 mt-0.5 flex-shrink-0 ${proficiencyColors.text}`} />
                    <h5 className="text-base font-bold text-gray-900 dark:text-white line-clamp-2">
                      {skill.skill_name}
                    </h5>
                  </div>

                  {/* Progress bar */}
                  {skill.proficiency_level && (
                    <div className="mb-3">
                      <div className="flex items-center justify-between mb-1.5">
                        <span className={`text-xs font-semibold ${proficiencyColors.text}`}>
                          {skill.proficiency_level}
                        </span>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {proficiencyPercentage}%
                        </span>
                      </div>
                      <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full bg-gradient-to-r ${proficiencyColors.bg} transition-all duration-500 ease-out`}
                          style={{ width: `${proficiencyPercentage}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Metadata */}
                  <div className="flex flex-wrap gap-2">
                    {skill.years_of_experience !== null && skill.years_of_experience !== undefined && (
                      <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300">
                        <Clock className="h-3.5 w-3.5" />
                        <span className="text-xs font-medium">
                          {t('skills.yearsOfExperience', { years: skill.years_of_experience })}
                        </span>
                      </div>
                    )}
                    {skill.endorsement_count > 0 && (
                      <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300">
                        <Award className="h-3.5 w-3.5" />
                        <span className="text-xs font-medium">
                          {t('skills.endorsements', { count: skill.endorsement_count })}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </ProfileSectionWrapper>
  );
}
