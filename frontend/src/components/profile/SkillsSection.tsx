'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import ProfileSectionWrapper from './ProfileSectionWrapper';
import ConfirmationModal from './ConfirmationModal';
import type { Skill } from '@/types/profile';
import { Award, Clock, Edit2, Star, TrendingUp, Trash2, Zap } from 'lucide-react';
import { updateSkill } from '@/api/profile';

interface SkillsSectionProps {
  skills: Skill[];
  isLoading?: boolean;
  onAdd?: () => void;
  onEdit?: (skill: Skill) => void;
  onDelete?: (id: number) => void;
  readOnly?: boolean;
  showCategory?: boolean;
  isOwnProfile?: boolean;
}

export default function SkillsSection({
  skills,
  isLoading = false,
  onAdd,
  onEdit,
  onDelete,
  readOnly = false,
  showCategory = true,
  isOwnProfile = false,
}: SkillsSectionProps) {
  const t = useTranslations('profile');
  const [draggedItem, setDraggedItem] = useState<{ id: number; category: string } | null>(null);
  const [dragOverItem, setDragOverItem] = useState<{ id: number; category: string } | null>(null);
  const [localSkills, setLocalSkills] = useState(skills);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{ isOpen: boolean; id: number | null }>({
    isOpen: false,
    id: null,
  });

  // Update local state when skills prop changes
  useEffect(() => {
    setLocalSkills(skills);
  }, [skills]);

  // Group skills by category
  const groupedSkills = localSkills.reduce((acc, skill) => {
    const category = skill.category || 'Other';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(skill);
    return acc;
  }, {} as Record<string, Skill[]>);

  const handleDragStart = (e: React.DragEvent, skillId: number, category: string) => {
    if (readOnly) return;
    setDraggedItem({ id: skillId, category });
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, skillId: number, category: string) => {
    e.preventDefault();
    if (!draggedItem || readOnly) return;
    // Only allow drop within same category
    if (draggedItem.category !== category) return;
    setDragOverItem({ id: skillId, category });
  };

  const handleDragEnd = async () => {
    if (!draggedItem || !dragOverItem || draggedItem.id === dragOverItem.id || readOnly) {
      setDraggedItem(null);
      setDragOverItem(null);
      return;
    }

    // Only reorder within same category
    if (draggedItem.category !== dragOverItem.category) {
      setDraggedItem(null);
      setDragOverItem(null);
      return;
    }

    const category = draggedItem.category;
    const categorySkills = groupedSkills[category];

    const draggedIndex = categorySkills.findIndex(s => s.id === draggedItem.id);
    const dropIndex = categorySkills.findIndex(s => s.id === dragOverItem.id);

    if (draggedIndex === -1 || dropIndex === -1) {
      setDraggedItem(null);
      setDragOverItem(null);
      return;
    }

    // Reorder within category
    const newCategorySkills = [...categorySkills];
    const [removed] = newCategorySkills.splice(draggedIndex, 1);
    newCategorySkills.splice(dropIndex, 0, removed);

    // Update display order for category skills
    const updatedCategorySkills = newCategorySkills.map((skill, index) => ({
      ...skill,
      display_order: index,
    }));

    // Merge back into all skills
    const newSkills = localSkills.map(skill => {
      const updated = updatedCategorySkills.find(s => s.id === skill.id);
      return updated || skill;
    });

    setLocalSkills(newSkills);
    setDraggedItem(null);
    setDragOverItem(null);

    // Update backend with new order for affected skills
    try {
      await Promise.all(
        updatedCategorySkills.map((skill) =>
          updateSkill(skill.id, { display_order: skill.display_order })
        )
      );
    } catch (error) {
      console.error('Failed to update skill order:', error);
      // Revert on error
      setLocalSkills(skills);
    }
  };

  const handleDragLeave = () => {
    setDragOverItem(null);
  };

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
      isEmpty={localSkills.length === 0}
      emptyMessage={t('skills.noSkills')}
      isLoading={isLoading}
      sectionId="skills"
      showPrivacyToggle={true}
      isOwnProfile={isOwnProfile}
      readOnly={readOnly}
      privacyKey="show_skills"
    >
      <div className="space-y-8">
        {Object.entries(groupedSkills).map(([category, categorySkills]) => (
          <div key={category}>
            {/* Category Header */}
            <div className="flex items-center gap-2 mb-4 pb-2 border-b-2 border-gray-200 dark:border-gray-700">
              <TrendingUp className="h-5 w-5 text-teal-600 dark:text-teal-400" />
              <h4 className="text-lg font-bold text-gray-900 dark:text-white">
                {category}
              </h4>
              <span className="ml-auto text-sm font-semibold px-3 py-1 rounded-full bg-teal-50 dark:bg-teal-900/20 text-teal-700 dark:text-teal-300">
                {categorySkills.length} {categorySkills.length === 1 ? 'skill' : 'skills'}
              </span>
            </div>

            {/* Skills Grid - 3 columns */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {categorySkills.map((skill) => {
                const proficiencyColors = getProficiencyColor(skill.proficiency_level);
                const proficiencyPercentage = getProficiencyPercentage(skill.proficiency_level);
                const isDragging = draggedItem?.id === skill.id;
                const isDropTarget = dragOverItem?.id === skill.id;

                return (
                  <div
                    key={skill.id}
                    draggable={!readOnly && categorySkills.length > 1}
                    onDragStart={(e) => handleDragStart(e, skill.id, category)}
                    onDragOver={(e) => handleDragOver(e, skill.id, category)}
                    onDragEnd={handleDragEnd}
                    onDragLeave={handleDragLeave}
                    className={`group relative bg-white dark:bg-gray-800 rounded-xl p-4 border-2 ${
                      isDragging
                        ? 'border-teal-400 opacity-50'
                        : isDropTarget
                        ? 'border-teal-400 border-dashed'
                        : 'border-gray-200 dark:border-gray-700'
                    } ${!readOnly && categorySkills.length > 1 ? 'cursor-move hover:shadow-lg hover:border-gray-300 dark:hover:border-gray-600' : ''}`}
                  >
                    {/* Edit and Delete buttons */}
                    {!readOnly && (
                      <div className="absolute top-3 right-3 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        {onEdit && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onEdit(skill);
                            }}
                            className="p-1.5 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-teal-100 dark:hover:bg-teal-900/30 hover:text-teal-600 dark:hover:text-teal-400"
                            title={t('actions.edit')}
                          >
                            <Edit2 className="h-3.5 w-3.5" />
                          </button>
                        )}
                        {onDelete && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setDeleteConfirmation({ isOpen: true, id: skill.id });
                            }}
                            className="p-1.5 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-900/30 hover:text-red-600 dark:hover:text-red-400"
                            title="Delete"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </button>
                        )}
                      </div>
                    )}

                    {/* Skill Icon */}
                    <div className="flex items-start gap-3 mb-3">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-teal-500 to-cyan-600 flex items-center justify-center shadow-md">
                          <Zap className="h-5 w-5 text-white" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h5 className="text-base font-bold text-gray-900 dark:text-white line-clamp-2">
                          {skill.skill_name}
                        </h5>
                      </div>
                    </div>

                    {/* Progress Bar */}
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
                            className={`h-full bg-gradient-to-r ${proficiencyColors.bg}`}
                            style={{ width: `${proficiencyPercentage}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="flex flex-wrap gap-1.5">
                      {skill.years_of_experience !== null && skill.years_of_experience !== undefined && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-xs font-medium">
                          <Clock className="h-3 w-3" />
                          {skill.years_of_experience}y
                        </span>
                      )}
                      {skill.endorsement_count > 0 && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-yellow-50 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-300 text-xs font-medium">
                          <Award className="h-3 w-3" />
                          {skill.endorsement_count}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmationModal
        isOpen={deleteConfirmation.isOpen}
        onClose={() => setDeleteConfirmation({ isOpen: false, id: null })}
        onConfirm={() => {
          if (deleteConfirmation.id && onDelete) {
            onDelete(deleteConfirmation.id);
          }
        }}
        title="Delete Skill"
        description="Are you sure you want to delete this skill? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
      />
    </ProfileSectionWrapper>
  );
}
