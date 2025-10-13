'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import type { Certification, CertificationCreate, CertificationUpdate } from '@/types/profile';
import { X, Award } from 'lucide-react';

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

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent
        closeButton={false}
        className="flex flex-col h-[90vh] max-h-[90vh] w-full max-w-4xl md:max-w-3xl overflow-hidden rounded-3xl border border-slate-200 bg-white text-slate-900 shadow-[0_30px_80px_-20px_rgba(15,23,42,0.2)]"
      >
        <DialogHeader className="flex-shrink-0 px-6 pt-6">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-amber-100 text-amber-600">
                  <Award className="h-5 w-5" />
                </span>
                <div>
                  <DialogTitle className="text-xl font-semibold text-slate-900">
                    {mode === 'create' ? 'Add Certification' : 'Edit Certification'}
                  </DialogTitle>
                  <DialogDescription className="text-sm text-slate-500">
                    {mode === 'create'
                      ? 'Add professional certifications and credentials to your profile.'
                      : 'Update your certification details and credentials.'}
                  </DialogDescription>
                </div>
              </div>
            </div>
            <DialogClose className="rounded-lg border border-slate-200 p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-700">
              <X className="h-4 w-4" />
            </DialogClose>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="flex flex-1 flex-col min-h-0">
          <div className="flex-1 overflow-y-auto px-6 py-6 min-h-0">
            <div className="space-y-8">
              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
                  {error}
                </div>
              )}

              <div className="grid gap-6 rounded-2xl border border-slate-200 bg-slate-50 p-6">
                {/* Certification Name */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Certification Name *
                  </label>
                  <input
                    type="text"
                    required
                    className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                    value={formData.certification_name}
                    onChange={(e) => handleChange('certification_name', e.target.value)}
                    placeholder="e.g., AWS Certified Solutions Architect"
                  />
                </div>

                {/* Issuing Organization */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Issuing Organization *
                  </label>
                  <input
                    type="text"
                    required
                    className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                    value={formData.issuing_organization}
                    onChange={(e) => handleChange('issuing_organization', e.target.value)}
                    placeholder="e.g., Amazon Web Services"
                  />
                </div>

                {/* Issue Date & Expiry Date */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Issue Date
                    </label>
                    <input
                      type="date"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.issue_date || ''}
                      onChange={(e) => handleChange('issue_date', e.target.value || null)}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Expiry Date
                    </label>
                    <input
                      type="date"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.expiry_date || ''}
                      onChange={(e) => handleChange('expiry_date', e.target.value || null)}
                      disabled={formData.does_not_expire}
                    />
                  </div>
                </div>

                {/* Does Not Expire */}
                <div>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.does_not_expire}
                      onChange={(e) => {
                        handleChange('does_not_expire', e.target.checked);
                        if (e.target.checked) {
                          handleChange('expiry_date', null);
                        }
                      }}
                      className="h-4 w-4 rounded border-slate-300"
                    />
                    <span className="text-sm font-medium text-slate-700">
                      This certification does not expire
                    </span>
                  </label>
                </div>

                {/* Credential ID & Credential URL */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Credential ID
                    </label>
                    <input
                      type="text"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.credential_id || ''}
                      onChange={(e) => handleChange('credential_id', e.target.value || null)}
                      placeholder="e.g., ABC123XYZ"
                    />
                    <p className="text-xs text-slate-500 mt-1">
                      Optional verification code
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Credential URL
                    </label>
                    <input
                      type="url"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.credential_url || ''}
                      onChange={(e) => handleChange('credential_url', e.target.value || null)}
                      placeholder="https://..."
                    />
                    <p className="text-xs text-slate-500 mt-1">
                      Link to verify certification
                    </p>
                  </div>
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Description
                  </label>
                  <textarea
                    className="w-full border border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2 focus-visible:ring-blue-500"
                    rows={3}
                    value={formData.description || ''}
                    onChange={(e) => handleChange('description', e.target.value || null)}
                    placeholder="Additional details about the certification..."
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Add relevant details about what this certification covers
                  </p>
                </div>
              </div>
            </div>
          </div>

          <DialogFooter className="flex-shrink-0 gap-3 border-t border-slate-200 bg-white px-6 py-4">
            <div className="flex w-full items-center justify-end gap-3">
              <Button
                type="button"
                variant="ghost"
                onClick={onClose}
                disabled={saving}
                className="min-w-[120px] border border-slate-300 bg-white text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={saving}
                className="min-w-[160px] bg-blue-600 text-white shadow-lg shadow-blue-500/30 hover:bg-blue-600/90"
              >
                {saving ? 'Saving...' : mode === 'create' ? 'Add Certification' : 'Save Changes'}
              </Button>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
