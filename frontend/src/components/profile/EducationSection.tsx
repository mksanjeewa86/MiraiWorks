'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import ProfileSectionWrapper from './ProfileSectionWrapper';
import ConfirmationModal from './ConfirmationModal';
import type { Education } from '@/types/profile';
import { GraduationCap, Calendar, Award, BookOpen, Edit2, Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import { updateEducation } from '@/api/profile';

interface EducationSectionProps {
  educations: Education[];
  isLoading?: boolean;
  onAdd?: () => void;
  onEdit?: (education: Education) => void;
  onDelete?: (id: number) => void;
  readOnly?: boolean;
  isOwnProfile?: boolean;
}

export default function EducationSection({
  educations,
  isLoading = false,
  onAdd,
  onEdit,
  onDelete,
  readOnly = false,
  isOwnProfile = false,
}: EducationSectionProps) {
  const t = useTranslations('profile');
  const [draggedItem, setDraggedItem] = useState<number | null>(null);
  const [dragOverItem, setDragOverItem] = useState<number | null>(null);
  const [localEducations, setLocalEducations] = useState(educations);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{ isOpen: boolean; id: number | null }>({
    isOpen: false,
    id: null,
  });

  // Update local state when educations prop changes
  useEffect(() => {
    setLocalEducations(educations);
  }, [educations]);

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

    const newEducations = [...localEducations];
    const draggedEdu = newEducations[draggedItem];

    // Remove dragged item and insert at new position
    newEducations.splice(draggedItem, 1);
    newEducations.splice(dragOverItem, 0, draggedEdu);

    // Update display order
    const updatedEducations = newEducations.map((edu, index) => ({
      ...edu,
      display_order: index,
    }));

    setLocalEducations(updatedEducations);
    setDraggedItem(null);
    setDragOverItem(null);

    // Update backend with new order
    try {
      await Promise.all(
        updatedEducations.map((edu) =>
          updateEducation(edu.id, { display_order: edu.display_order })
        )
      );
    } catch (error) {
      console.error('Failed to update education order:', error);
      // Revert on error
      setLocalEducations(educations);
    }
  };

  const handleDragLeave = () => {
    setDragOverItem(null);
  };

  const calculateDuration = (startDate: string | null, endDate: string | null) => {
    if (!startDate || !endDate) return null;

    const start = new Date(startDate);
    const end = new Date(endDate);

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
      title={t('education.title')}
      onAdd={!readOnly ? onAdd : undefined}
      addButtonText={t('education.add')}
      isEmpty={localEducations.length === 0}
      emptyMessage={t('education.noEducation')}
      isLoading={isLoading}
      sectionId="education"
      showPrivacyToggle={true}
      isOwnProfile={isOwnProfile}
      readOnly={readOnly}
      privacyKey="show_education"
    >
      <div className="space-y-4">
        {localEducations.map((edu, index) => (
          <div
            key={edu.id}
            draggable={!readOnly && localEducations.length > 1}
            onDragStart={(e) => handleDragStart(e, index)}
            onDragOver={(e) => handleDragOver(e, index)}
            onDragEnd={handleDragEnd}
            onDragLeave={handleDragLeave}
            className={`group relative flex gap-4 bg-white dark:bg-gray-800 rounded-xl p-5 border-2 ${
              draggedItem === index
                ? 'border-purple-400 opacity-50'
                : dragOverItem === index
                ? 'border-purple-400 border-dashed'
                : 'border-gray-200 dark:border-gray-700'
            } ${!readOnly && localEducations.length > 1 ? 'cursor-move hover:shadow-lg hover:border-gray-300 dark:hover:border-gray-600' : ''}`}
          >
            {/* Timeline Dot */}
            <div className="flex-shrink-0 flex flex-col items-center">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-md">
                <GraduationCap className="h-5 w-5 text-white" />
              </div>
              {index !== localEducations.length - 1 && (
                <div className="w-0.5 h-full min-h-[40px] bg-gradient-to-b from-purple-300 to-transparent dark:from-purple-700 mt-2" />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                    {edu.institution_name}
                  </h3>
                  <div className="flex items-center gap-2 mb-1">
                    <BookOpen className="h-4 w-4 text-purple-600 dark:text-purple-400 flex-shrink-0" />
                    <p className="text-base font-semibold text-gray-700 dark:text-gray-300">
                      {edu.degree_type} {t('education.degreeIn')} {edu.field_of_study}
                    </p>
                  </div>
                  {(edu.start_date || edu.end_date) && (
                    <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        <span>
                          {edu.start_date && formatDate(edu.start_date)}
                          {edu.start_date && edu.end_date && ' - '}
                          {edu.end_date && formatDate(edu.end_date)}
                        </span>
                      </div>
                      {calculateDuration(edu.start_date, edu.end_date) && (
                        <>
                          <span className="text-gray-400">•</span>
                          <span className="font-medium">
                            {calculateDuration(edu.start_date, edu.end_date)}
                          </span>
                        </>
                      )}
                    </div>
                  )}
                </div>

                {/* Edit and Delete buttons */}
                {!readOnly && (
                  <div className="flex gap-2 ml-4">
                    {onEdit && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onEdit(edu);
                        }}
                        className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-purple-100 dark:hover:bg-purple-900/30 hover:text-purple-600 dark:hover:text-purple-400"
                        title={t('actions.edit')}
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                    )}
                    {onDelete && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteConfirmation({ isOpen: true, id: edu.id });
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
                {edu.graduation_year && (
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 text-sm font-medium">
                    <GraduationCap className="h-3 w-3" />
                    {t('education.classOf')} {edu.graduation_year}
                  </span>
                )}
                {edu.gpa && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 text-sm font-medium">
                    {t('education.gpa')}: {edu.gpa}
                    {edu.gpa_max && `/${edu.gpa_max}`}
                  </span>
                )}
              </div>

              {/* Honors and Awards */}
              {edu.honors_awards && (
                <div className="flex items-start gap-2 mb-3 p-3 rounded-lg bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 border border-yellow-200 dark:border-yellow-700">
                  <Award className="h-4 w-4 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-yellow-900 dark:text-yellow-100 leading-relaxed">
                    {edu.honors_awards}
                  </p>
                </div>
              )}

              {/* Description */}
              {edu.description && (
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                  {edu.description}
                </p>
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
        title="Delete Education"
        description="Are you sure you want to delete this education entry? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
      />
    </ProfileSectionWrapper>
  );
}
