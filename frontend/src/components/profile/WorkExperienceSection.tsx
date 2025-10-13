'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import ProfileSectionWrapper from './ProfileSectionWrapper';
import ConfirmationModal from './ConfirmationModal';
import type { WorkExperience } from '@/types/profile';
import { Building2, Calendar, MapPin, Edit2, Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import { updateWorkExperience } from '@/api/profile';

interface WorkExperienceSectionProps {
  experiences: WorkExperience[];
  isLoading?: boolean;
  onAdd?: () => void;
  onEdit?: (experience: WorkExperience) => void;
  onDelete?: (id: number) => void;
  readOnly?: boolean;
  isOwnProfile?: boolean;
}

export default function WorkExperienceSection({
  experiences,
  isLoading = false,
  onAdd,
  onEdit,
  onDelete,
  readOnly = false,
  isOwnProfile = false,
}: WorkExperienceSectionProps) {
  const t = useTranslations('profile');
  const [draggedItem, setDraggedItem] = useState<number | null>(null);
  const [dragOverItem, setDragOverItem] = useState<number | null>(null);
  const [localExperiences, setLocalExperiences] = useState(experiences);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{ isOpen: boolean; id: number | null }>({
    isOpen: false,
    id: null,
  });

  // Update local state when experiences prop changes
  useEffect(() => {
    setLocalExperiences(experiences);
  }, [experiences]);

  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    try {
      return format(new Date(dateString), 'MMM yyyy');
    } catch {
      return dateString;
    }
  };

  const handleDragStart = (e: React.DragEvent, index: number) => {
    if (readOnly) return;
    setDraggedItem(index);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    if (draggedItem === null || readOnly) return;
    setDragOverItem(index);
  };

  const handleDragEnd = async () => {
    if (draggedItem === null || dragOverItem === null || draggedItem === dragOverItem || readOnly) {
      setDraggedItem(null);
      setDragOverItem(null);
      return;
    }

    const newExperiences = [...localExperiences];
    const draggedExp = newExperiences[draggedItem];

    // Remove dragged item and insert at new position
    newExperiences.splice(draggedItem, 1);
    newExperiences.splice(dragOverItem, 0, draggedExp);

    // Update display order
    const updatedExperiences = newExperiences.map((exp, index) => ({
      ...exp,
      display_order: index,
    }));

    setLocalExperiences(updatedExperiences);
    setDraggedItem(null);
    setDragOverItem(null);

    // Update backend with new order
    try {
      await Promise.all(
        updatedExperiences.map((exp) =>
          updateWorkExperience(exp.id, { display_order: exp.display_order })
        )
      );
    } catch (error) {
      console.error('Failed to update work experience order:', error);
      // Revert on error
      setLocalExperiences(experiences);
    }
  };

  const handleDragLeave = () => {
    setDragOverItem(null);
  };

  const calculateDuration = (startDate: string, endDate: string | null, isCurrent: boolean) => {
    const start = new Date(startDate);
    const end = isCurrent ? new Date() : endDate ? new Date(endDate) : new Date();

    const months = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());
    const years = Math.floor(months / 12);
    const remainingMonths = months % 12;

    if (years === 0) {
      return `${remainingMonths} ${remainingMonths === 1 ? 'mo' : 'mos'}`;
    } else if (remainingMonths === 0) {
      return `${years} ${years === 1 ? 'yr' : 'yrs'}`;
    } else {
      return `${years} ${years === 1 ? 'yr' : 'yrs'} ${remainingMonths} ${remainingMonths === 1 ? 'mo' : 'mos'}`;
    }
  };

  return (
    <ProfileSectionWrapper
      title={t('experience.title')}
      onAdd={!readOnly ? onAdd : undefined}
      addButtonText={t('experience.add')}
      isEmpty={localExperiences.length === 0}
      emptyMessage={t('experience.noExperience')}
      isLoading={isLoading}
      sectionId="work_experience"
      showPrivacyToggle={true}
      isOwnProfile={isOwnProfile}
      readOnly={readOnly}
      privacyKey="show_work_experience"
    >
      <div className="space-y-4">
        {localExperiences.map((exp, index) => (
          <div
            key={exp.id}
            draggable={!readOnly && localExperiences.length > 1}
            onDragStart={(e) => handleDragStart(e, index)}
            onDragOver={(e) => handleDragOver(e, index)}
            onDragEnd={handleDragEnd}
            onDragLeave={handleDragLeave}
            className={`group relative flex gap-4 bg-white dark:bg-gray-800 rounded-xl p-5 border-2 ${
              draggedItem === index
                ? 'border-blue-400 opacity-50'
                : dragOverItem === index
                ? 'border-blue-400 border-dashed'
                : 'border-gray-200 dark:border-gray-700'
            } ${!readOnly && localExperiences.length > 1 ? 'cursor-move hover:shadow-lg hover:border-gray-300 dark:hover:border-gray-600' : ''}`}
          >
            {/* Timeline Dot */}
            <div className="flex-shrink-0 flex flex-col items-center">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-md">
                <Building2 className="h-5 w-5 text-white" />
              </div>
              {index !== localExperiences.length - 1 && (
                <div className="w-0.5 h-full min-h-[40px] bg-gradient-to-b from-blue-300 to-transparent dark:from-blue-700 mt-2" />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                    {exp.position_title}
                  </h3>
                  <p className="text-base font-semibold text-gray-700 dark:text-gray-300 mb-1">
                    {exp.company_name}
                  </p>
                  <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      <span>
                        {formatDate(exp.start_date)} - {exp.is_current ? t('experience.present') : formatDate(exp.end_date)}
                      </span>
                    </div>
                    <span className="text-gray-400">•</span>
                    <span className="font-medium">
                      {calculateDuration(exp.start_date, exp.end_date, exp.is_current)}
                    </span>
                  </div>
                </div>

                {/* Edit and Delete buttons */}
                {!readOnly && (
                  <div className="flex gap-2 ml-4">
                    {onEdit && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onEdit(exp);
                        }}
                        className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-blue-100 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-400"
                        title={t('actions.edit')}
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                    )}
                    {onDelete && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteConfirmation({ isOpen: true, id: exp.id });
                        }}
                        className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-900/30 hover:text-red-600 dark:hover:text-red-400"
                        title="Delete"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Meta Tags */}
              <div className="flex flex-wrap gap-2 mb-3">
                {exp.employment_type && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-sm font-medium">
                    {exp.employment_type}
                  </span>
                )}
                {exp.location && (
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 text-sm font-medium">
                    <MapPin className="h-3 w-3" />
                    {exp.location}
                  </span>
                )}
              </div>

              {/* Description */}
              {exp.description && (
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed mb-3 whitespace-pre-line">
                  {exp.description}
                </p>
              )}

              {/* Skills */}
              {exp.skills && (
                <div className="flex flex-wrap gap-2">
                  {exp.skills.split(',').map((skill, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-3 py-1 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-medium"
                    >
                      {skill.trim()}
                    </span>
                  ))}
                </div>
              )}
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
        title="Delete Work Experience"
        description="Are you sure you want to delete this work experience? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
      />
    </ProfileSectionWrapper>
  );
}
