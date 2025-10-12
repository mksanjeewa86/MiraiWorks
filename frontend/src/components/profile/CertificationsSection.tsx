'use client';

import { useTranslations } from 'next-intl';
import ProfileSectionWrapper from './ProfileSectionWrapper';
import type { Certification } from '@/types/profile';
import { Award, Calendar, ExternalLink, AlertCircle, Shield, Edit2, CheckCircle2, XCircle } from 'lucide-react';
import { format, isPast } from 'date-fns';

interface CertificationsSectionProps {
  certifications: Certification[];
  isLoading?: boolean;
  onAdd?: () => void;
  onEdit?: (certification: Certification) => void;
  readOnly?: boolean;
  isOwnProfile?: boolean;
}

export default function CertificationsSection({
  certifications,
  isLoading = false,
  onAdd,
  onEdit,
  readOnly = false,
  isOwnProfile = false,
}: CertificationsSectionProps) {
  const t = useTranslations('profile');

  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
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

  return (
    <ProfileSectionWrapper
      title={t('certifications.title')}
      onAdd={!readOnly ? onAdd : undefined}
      addButtonText={t('certifications.add')}
      isEmpty={certifications.length === 0}
      emptyMessage={t('certifications.noCertifications')}
      isLoading={isLoading}
      sectionId="certifications"
      showPrivacyToggle={true}
      isOwnProfile={isOwnProfile}
      readOnly={readOnly}
      privacyKey="show_certifications"
    >
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {certifications.map((cert) => {
          const expired = isExpired(cert.expiry_date, cert.does_not_expire);

          return (
            <div
              key={cert.id}
              className={`group relative bg-white dark:bg-gray-800 rounded-xl border p-5 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 ${
                expired
                  ? 'border-red-200 dark:border-red-800 bg-gradient-to-br from-white to-red-50 dark:from-gray-800 dark:to-red-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-yellow-300 dark:hover:border-yellow-600'
              }`}
            >
              {/* Edit button */}
              {!readOnly && onEdit && (
                <button
                  onClick={() => onEdit(cert)}
                  className="absolute top-3 right-3 p-1.5 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-yellow-50 dark:hover:bg-yellow-900/30 hover:text-yellow-600 dark:hover:text-yellow-400"
                  title={t('actions.edit')}
                >
                  <Edit2 className="h-3.5 w-3.5" />
                </button>
              )}

              {/* Status badge */}
              <div className="absolute top-3 left-3">
                {cert.does_not_expire ? (
                  <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300">
                    <CheckCircle2 className="h-3 w-3" />
                    <span className="text-xs font-semibold">Active</span>
                  </div>
                ) : expired ? (
                  <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300">
                    <XCircle className="h-3 w-3" />
                    <span className="text-xs font-semibold">Expired</span>
                  </div>
                ) : (
                  <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">
                    <Shield className="h-3 w-3" />
                    <span className="text-xs font-semibold">Valid</span>
                  </div>
                )}
              </div>

              {/* Certificate badge/image */}
              <div className="flex justify-center mb-4 mt-8">
                {cert.certificate_image_url ? (
                  <img
                    src={cert.certificate_image_url}
                    alt={cert.certification_name}
                    className="w-20 h-20 rounded-xl object-cover shadow-md ring-2 ring-gray-100 dark:ring-gray-700"
                  />
                ) : (
                  <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-yellow-400 via-amber-500 to-orange-600 flex items-center justify-center shadow-lg">
                    <Award className="h-10 w-10 text-white" />
                  </div>
                )}
              </div>

              {/* Certification name */}
              <h4 className="text-base font-bold text-gray-900 dark:text-white text-center mb-2 line-clamp-2 min-h-[3rem]">
                {cert.certification_name}
              </h4>

              {/* Issuing organization */}
              <p className="text-sm font-semibold text-center text-gray-600 dark:text-gray-400 mb-4 line-clamp-1">
                {cert.issuing_organization}
              </p>

              {/* Divider */}
              <div className="h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent mb-4" />

              {/* Metadata */}
              <div className="space-y-2">
                {/* Issue date */}
                {cert.issue_date && (
                  <div className="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                    <Calendar className="h-4 w-4 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                    <span className="font-medium">
                      Issued {formatDate(cert.issue_date)}
                    </span>
                  </div>
                )}

                {/* Expiry status */}
                {cert.does_not_expire ? (
                  <div className="flex items-center gap-2 text-xs text-green-600 dark:text-green-400">
                    <CheckCircle2 className="h-4 w-4 flex-shrink-0" />
                    <span className="font-medium">No expiration date</span>
                  </div>
                ) : cert.expiry_date && (
                  <div className={`flex items-center gap-2 text-xs ${
                    expired ? 'text-red-600 dark:text-red-400' : 'text-gray-600 dark:text-gray-400'
                  }`}>
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <span className="font-medium">
                      {expired
                        ? `${t('certifications.expired')} ${formatDate(cert.expiry_date)}`
                        : `${t('certifications.expires', { date: formatDate(cert.expiry_date) ?? cert.expiry_date })}`
                      }
                    </span>
                  </div>
                )}

                {/* Credential ID */}
                {cert.credential_id && (
                  <div className="flex items-start gap-2 text-xs">
                    <Shield className="h-4 w-4 text-purple-600 dark:text-purple-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <span className="text-gray-500 dark:text-gray-500 font-medium">ID:</span>{' '}
                      <span className="text-gray-700 dark:text-gray-300 font-mono break-all">
                        {cert.credential_id}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* Credential URL */}
              {cert.credential_url && (
                <a
                  href={cert.credential_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-4 flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 text-blue-700 dark:text-blue-300 text-sm font-semibold border border-blue-200 dark:border-blue-700 hover:shadow-md transition-all duration-300 hover:-translate-y-0.5"
                  onClick={(e) => e.stopPropagation()}
                >
                  <ExternalLink className="h-4 w-4" />
                  {t('certifications.viewCredential')}
                </a>
              )}
            </div>
          );
        })}
      </div>
    </ProfileSectionWrapper>
  );
}
