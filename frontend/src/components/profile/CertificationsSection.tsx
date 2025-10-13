'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import ProfileSectionWrapper from './ProfileSectionWrapper';
import ConfirmationModal from './ConfirmationModal';
import type { Certification } from '@/types/profile';
import { Award, Calendar, ExternalLink, Shield, Edit2, Trash2 } from 'lucide-react';
import { format, isPast } from 'date-fns';
import { updateCertification } from '@/api/profile';

interface CertificationsSectionProps {
  certifications: Certification[];
  isLoading?: boolean;
  onAdd?: () => void;
  onEdit?: (certification: Certification) => void;
  onDelete?: (id: number) => void;
  readOnly?: boolean;
  isOwnProfile?: boolean;
}

export default function CertificationsSection({
  certifications,
  isLoading = false,
  onAdd,
  onEdit,
  onDelete,
  readOnly = false,
  isOwnProfile = false,
}: CertificationsSectionProps) {
  const t = useTranslations('profile');
  const [draggedItem, setDraggedItem] = useState<number | null>(null);
  const [dragOverItem, setDragOverItem] = useState<number | null>(null);
  const [localCertifications, setLocalCertifications] = useState(certifications);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{ isOpen: boolean; id: number | null }>({
    isOpen: false,
    id: null,
  });

  // Update local state when certifications prop changes
  useEffect(() => {
    setLocalCertifications(certifications);
  }, [certifications]);

  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    try {
      return format(new Date(dateString), 'MMM yyyy');
    } catch {
      return dateString;
    }
  };

  const isExpired = (expiryDate: string | null, doesNotExpire: boolean) => {
    if (doesNotExpire || !expiryDate) return false;
    try {
      return isPast(new Date(expiryDate));
    } catch {
      return false;
    }
  };

  const handleDragStart = (e: React.DragEvent, index: number) => {
    if (readOnly || localCertifications.length <= 1) return;
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

    const newCertifications = [...localCertifications];
    const draggedCert = newCertifications[draggedItem];

    // Remove dragged item and insert at new position
    newCertifications.splice(draggedItem, 1);
    newCertifications.splice(dragOverItem, 0, draggedCert);

    // Update display order
    const updatedCertifications = newCertifications.map((cert, index) => ({
      ...cert,
      display_order: index,
    }));

    setLocalCertifications(updatedCertifications);
    setDraggedItem(null);
    setDragOverItem(null);

    // Update backend with new order
    try {
      await Promise.all(
        updatedCertifications.map((cert) =>
          updateCertification(cert.id, { display_order: cert.display_order })
        )
      );
    } catch (error) {
      console.error('Failed to update certification order:', error);
      // Revert on error
      setLocalCertifications(certifications);
    }
  };

  const handleDragLeave = () => {
    setDragOverItem(null);
  };

  return (
    <ProfileSectionWrapper
      title={t('certifications.title')}
      onAdd={!readOnly ? onAdd : undefined}
      addButtonText={t('certifications.add')}
      isEmpty={localCertifications.length === 0}
      emptyMessage={t('certifications.noCertifications')}
      isLoading={isLoading}
      sectionId="certifications"
      showPrivacyToggle={true}
      isOwnProfile={isOwnProfile}
      readOnly={readOnly}
      privacyKey="show_certifications"
    >
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {localCertifications.map((cert, index) => {
          const expired = isExpired(cert.expiry_date, cert.does_not_expire);

          return (
            <div
              key={cert.id}
              draggable={!readOnly && localCertifications.length > 1}
              onDragStart={(e) => handleDragStart(e, index)}
              onDragOver={(e) => handleDragOver(e, index)}
              onDragEnd={handleDragEnd}
              onDragLeave={handleDragLeave}
              className={`group relative flex gap-3 bg-white dark:bg-gray-800 rounded-xl border-2 p-4 ${
                draggedItem === index
                  ? 'border-amber-400 opacity-50'
                  : dragOverItem === index
                  ? 'border-amber-400 border-dashed'
                  : expired
                  ? 'border-red-200 dark:border-red-800'
                  : 'border-gray-200 dark:border-gray-700'
              } ${!readOnly && localCertifications.length > 1 ? 'cursor-move hover:shadow-lg hover:border-gray-300 dark:hover:border-gray-600' : ''}`}
            >
              {/* Certificate Icon */}
              <div className="flex-shrink-0">
                {cert.certificate_image_url ? (
                  <img
                    src={cert.certificate_image_url}
                    alt={cert.certification_name}
                    className="w-12 h-12 rounded-lg object-cover"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-md">
                    <Award className="h-6 w-6 text-white" />
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                {/* Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <h4 className="text-base font-bold text-gray-900 dark:text-white line-clamp-2 mb-1">
                      {cert.certification_name}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-1">
                      {cert.issuing_organization}
                    </p>
                  </div>

                  {/* Edit and Delete buttons */}
                  {!readOnly && (
                    <div className="flex gap-1 ml-2">
                      {onEdit && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onEdit(cert);
                          }}
                          className="p-1.5 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-amber-100 dark:hover:bg-amber-900/30 hover:text-amber-600 dark:hover:text-amber-400"
                          title={t('actions.edit')}
                        >
                          <Edit2 className="h-3.5 w-3.5" />
                        </button>
                      )}
                      {onDelete && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteConfirmation({ isOpen: true, id: cert.id });
                          }}
                          className="p-1.5 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-red-100 dark:hover:bg-red-900/30 hover:text-red-600 dark:hover:text-red-400"
                          title="Delete"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      )}
                    </div>
                  )}
                </div>

                {/* Meta Info */}
                <div className="flex flex-wrap items-center gap-2 text-xs">
                  {/* Status Badge */}
                  {cert.does_not_expire ? (
                    <span className="inline-flex items-center px-2 py-0.5 rounded bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 font-medium">
                      Active
                    </span>
                  ) : expired ? (
                    <span className="inline-flex items-center px-2 py-0.5 rounded bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 font-medium">
                      Expired
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 font-medium">
                      Valid
                    </span>
                  )}

                  {/* Issue Date */}
                  {cert.issue_date && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium">
                      <Calendar className="h-3 w-3" />
                      {formatDate(cert.issue_date)}
                    </span>
                  )}

                  {/* Credential ID */}
                  {cert.credential_id && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 font-medium font-mono text-[10px]">
                      <Shield className="h-3 w-3" />
                      {cert.credential_id}
                    </span>
                  )}

                  {/* Credential URL */}
                  {cert.credential_url && (
                    <a
                      href={cert.credential_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 font-medium hover:bg-blue-100 dark:hover:bg-blue-900/40"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <ExternalLink className="h-3 w-3" />
                      View
                    </a>
                  )}
                </div>
              </div>
            </div>
          );
        })}
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
        title="Delete Certification"
        description="Are you sure you want to delete this certification? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
      />
    </ProfileSectionWrapper>
  );
}
