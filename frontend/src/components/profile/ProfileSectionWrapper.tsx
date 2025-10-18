import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/Button';
import { Plus, Edit } from 'lucide-react';
import type { ReactNode } from 'react';
import SectionPrivacyToggle from './SectionPrivacyToggle';

interface ProfileSectionWrapperProps {
  title: string;
  children: ReactNode;
  onAdd?: () => void;
  onEdit?: () => void;
  addButtonText?: string;
  editButtonText?: string;
  isEmpty?: boolean;
  emptyMessage?: string;
  isLoading?: boolean;
  className?: string;
  sectionId?: string;
  showPrivacyToggle?: boolean;
  isOwnProfile?: boolean;
  readOnly?: boolean;
  privacyKey?: 'show_work_experience' | 'show_education' | 'show_skills' | 'show_certifications' | 'show_projects' | 'show_resume';
}

export default function ProfileSectionWrapper({
  title,
  children,
  onAdd,
  onEdit,
  addButtonText = 'Add',
  editButtonText = 'Edit',
  isEmpty = false,
  emptyMessage = 'No items yet',
  isLoading = false,
  className,
  sectionId,
  showPrivacyToggle = false,
  isOwnProfile = false,
  readOnly = false,
  privacyKey,
}: ProfileSectionWrapperProps) {
  if (isLoading) {
    return (
      <Card className={className} id={sectionId ? `section-${sectionId}` : undefined}>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="loading-skeleton" style={{ width: '100%', height: '60px' }} />
            <div className="loading-skeleton" style={{ width: '100%', height: '60px' }} />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={`${className} transition-all duration-300`} id={sectionId ? `section-${sectionId}` : undefined}>
      <CardHeader className="mb-4">
        <div className="flex items-center justify-between">
          <CardTitle>{title}</CardTitle>
          <div className="flex items-center gap-3">
            {/* Privacy Toggle */}
            {showPrivacyToggle && privacyKey && isOwnProfile && (
              <SectionPrivacyToggle
                sectionKey={privacyKey}
                isOwnProfile={isOwnProfile}
                readOnly={readOnly}
              />
            )}

            {/* Action Buttons */}
            <div className="flex gap-2">
              {onEdit && (
                <button
                  onClick={onEdit}
                  className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 text-sm font-semibold hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 hover:shadow-md transition-all duration-300 hover:-translate-y-0.5"
                >
                  <Edit className="h-4 w-4" />
                  <span>{editButtonText}</span>
                </button>
              )}
              {onAdd && (
                <button
                  onClick={onAdd}
                  className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-sm font-semibold shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5"
                >
                  <Plus className="h-4 w-4" />
                  <span>{addButtonText}</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isEmpty ? (
          <div className="text-center py-12">
            <div className="mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 mb-4">
                <Plus className="h-8 w-8 text-gray-400 dark:text-gray-500" />
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">
                {emptyMessage}
              </p>
            </div>
            {onAdd && (
              <button
                onClick={onAdd}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-sm font-semibold shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
              >
                <Plus className="h-5 w-5" />
                <span>{addButtonText}</span>
              </button>
            )}
          </div>
        ) : (
          children
        )}
      </CardContent>
    </Card>
  );
}
