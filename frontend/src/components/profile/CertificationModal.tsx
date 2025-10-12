'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui';
import type { Certification, CertificationCreate, CertificationUpdate } from '@/types/profile';
import { X } from 'lucide-react';

interface CertificationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: CertificationCreate | CertificationUpdate) => Promise<void>;
  certification?: Certification;
  mode: 'create' | 'edit';
}

export default function CertificationModal({
  isOpen,
  onClose,
  onSave,
  certification,
  mode,
}: CertificationModalProps) {
  const [formData, setFormData] = useState<CertificationCreate>({
    certification_name: '',
    issuing_organization: '',
    issue_date: null,
    expiry_date: null,
    does_not_expire: false,
    credential_id: null,
    credential_url: null,
    certificate_image_url: null,
    description: null,
    display_order: 0,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (certification && mode === 'edit') {
      setFormData({
        certification_name: certification.certification_name,
        issuing_organization: certification.issuing_organization,
        issue_date: certification.issue_date,
        expiry_date: certification.expiry_date,
        does_not_expire: certification.does_not_expire,
        credential_id: certification.credential_id,
        credential_url: certification.credential_url,
        certificate_image_url: certification.certificate_image_url,
        description: certification.description,
        display_order: certification.display_order,
      });
    } else {
      setFormData({
        certification_name: '',
        issuing_organization: '',
        issue_date: null,
        expiry_date: null,
        does_not_expire: false,
        credential_id: null,
        credential_url: null,
        certificate_image_url: null,
        description: null,
        display_order: 0,
      });
    }
  }, [certification, mode, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaving(true);

    try {
      await onSave(formData);
      onClose();
    } catch (err: any) {
      console.error('Failed to save certification:', err);
      setError(err.message || 'Failed to save certification');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof CertificationCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
              {mode === 'create' ? 'Add Certification' : 'Edit Certification'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {error && (
              <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-red-600 dark:text-red-400 text-sm">
                {error}
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Certification Name */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Certification Name *
                </label>
                <input
                  type="text"
                  required
                  className="input w-full"
                  value={formData.certification_name}
                  onChange={(e) => handleChange('certification_name', e.target.value)}
                  placeholder="e.g., AWS Certified Solutions Architect"
                />
              </div>

              {/* Issuing Organization */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Issuing Organization *
                </label>
                <input
                  type="text"
                  required
                  className="input w-full"
                  value={formData.issuing_organization}
                  onChange={(e) => handleChange('issuing_organization', e.target.value)}
                  placeholder="e.g., Amazon Web Services"
                />
              </div>

              {/* Issue Date */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Issue Date
                </label>
                <input
                  type="date"
                  className="input w-full"
                  value={formData.issue_date || ''}
                  onChange={(e) => handleChange('issue_date', e.target.value || null)}
                />
              </div>

              {/* Expiry Date */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Expiry Date
                </label>
                <input
                  type="date"
                  className="input w-full"
                  value={formData.expiry_date || ''}
                  onChange={(e) => handleChange('expiry_date', e.target.value || null)}
                  disabled={formData.does_not_expire}
                />
              </div>

              {/* Does Not Expire */}
              <div className="md:col-span-2">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.does_not_expire}
                    onChange={(e) => {
                      handleChange('does_not_expire', e.target.checked);
                      if (e.target.checked) {
                        handleChange('expiry_date', null);
                      }
                    }}
                  />
                  <span className="text-sm" style={{ color: 'var(--text-primary)' }}>
                    This certification does not expire
                  </span>
                </label>
              </div>

              {/* Credential ID */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Credential ID
                </label>
                <input
                  type="text"
                  className="input w-full"
                  value={formData.credential_id || ''}
                  onChange={(e) => handleChange('credential_id', e.target.value || null)}
                  placeholder="e.g., ABC123XYZ"
                />
              </div>

              {/* Credential URL */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Credential URL
                </label>
                <input
                  type="url"
                  className="input w-full"
                  value={formData.credential_url || ''}
                  onChange={(e) => handleChange('credential_url', e.target.value || null)}
                  placeholder="https://..."
                />
              </div>

              {/* Description */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Description
                </label>
                <textarea
                  className="input w-full"
                  rows={3}
                  value={formData.description || ''}
                  onChange={(e) => handleChange('description', e.target.value || null)}
                  placeholder="Additional details about the certification..."
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button type="button" variant="outline" onClick={onClose} disabled={saving}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? 'Saving...' : mode === 'create' ? 'Add Certification' : 'Save Changes'}
              </Button>
            </div>
          </form>
        </div>
      </div>
  );
}
