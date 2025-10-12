'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui';
import type { WorkExperience, WorkExperienceCreate, WorkExperienceUpdate } from '@/types/profile';
import { X } from 'lucide-react';

interface WorkExperienceModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: WorkExperienceCreate | WorkExperienceUpdate) => Promise<void>;
  onDelete?: (id: number) => Promise<void>;
  experience?: WorkExperience;
  mode: 'create' | 'edit';
}

export default function WorkExperienceModal({
  isOpen,
  onClose,
  onSave,
  onDelete,
  experience,
  mode,
}: WorkExperienceModalProps) {
  const [formData, setFormData] = useState<WorkExperienceCreate>({
    company_name: '',
    position_title: '',
    employment_type: 'Full-time',
    location: '',
    start_date: '',
    end_date: null,
    is_current: false,
    description: '',
    skills: '',
    company_logo_url: null,
    display_order: 0,
  });
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (experience && mode === 'edit') {
      setFormData({
        company_name: experience.company_name,
        position_title: experience.position_title,
        employment_type: experience.employment_type,
        location: experience.location,
        start_date: experience.start_date,
        end_date: experience.end_date,
        is_current: experience.is_current,
        description: experience.description,
        skills: experience.skills,
        company_logo_url: experience.company_logo_url,
        display_order: experience.display_order,
      });
    } else {
      setFormData({
        company_name: '',
        position_title: '',
        employment_type: 'Full-time',
        location: '',
        start_date: '',
        end_date: null,
        is_current: false,
        description: '',
        skills: '',
        company_logo_url: null,
        display_order: 0,
      });
    }
  }, [experience, mode, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaving(true);

    try {
      await onSave(formData);
      onClose();
    } catch (err: any) {
      console.error('Failed to save work experience:', err);
      setError(err.message || 'Failed to save work experience');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof WorkExperienceCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleDelete = async () => {
    if (!experience?.id || !onDelete) return;

    const confirmed = confirm('Are you sure you want to delete this work experience? This action cannot be undone.');
    if (!confirmed) return;

    setDeleting(true);
    setError(null);

    try {
      await onDelete(experience.id);
      onClose();
    } catch (err: any) {
      console.error('Failed to delete work experience:', err);
      setError(err.message || 'Failed to delete work experience');
    } finally {
      setDeleting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
              {mode === 'create' ? 'Add Work Experience' : 'Edit Work Experience'}
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
              {/* Company Name */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Company Name *
                </label>
                <input
                  type="text"
                  required
                  className="input w-full"
                  value={formData.company_name}
                  onChange={(e) => handleChange('company_name', e.target.value)}
                />
              </div>

              {/* Position Title */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Position Title *
                </label>
                <input
                  type="text"
                  required
                  className="input w-full"
                  value={formData.position_title}
                  onChange={(e) => handleChange('position_title', e.target.value)}
                />
              </div>

              {/* Employment Type */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Employment Type
                </label>
                <select
                  className="input w-full"
                  value={formData.employment_type || ''}
                  onChange={(e) => handleChange('employment_type', e.target.value)}
                >
                  <option value="Full-time">Full-time</option>
                  <option value="Part-time">Part-time</option>
                  <option value="Contract">Contract</option>
                  <option value="Freelance">Freelance</option>
                  <option value="Internship">Internship</option>
                </select>
              </div>

              {/* Location */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Location
                </label>
                <input
                  type="text"
                  className="input w-full"
                  value={formData.location || ''}
                  onChange={(e) => handleChange('location', e.target.value)}
                  placeholder="e.g., San Francisco, CA"
                />
              </div>

              {/* Start Date */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Start Date *
                </label>
                <input
                  type="date"
                  required
                  className="input w-full"
                  value={formData.start_date}
                  onChange={(e) => handleChange('start_date', e.target.value)}
                />
              </div>

              {/* End Date */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  End Date
                </label>
                <input
                  type="date"
                  className="input w-full"
                  value={formData.end_date || ''}
                  onChange={(e) => handleChange('end_date', e.target.value || null)}
                  disabled={formData.is_current}
                />
              </div>

              {/* Currently Working */}
              <div className="md:col-span-2">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.is_current}
                    onChange={(e) => {
                      handleChange('is_current', e.target.checked);
                      if (e.target.checked) {
                        handleChange('end_date', null);
                      }
                    }}
                  />
                  <span className="text-sm" style={{ color: 'var(--text-primary)' }}>
                    I currently work here
                  </span>
                </label>
              </div>

              {/* Description */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Description
                </label>
                <textarea
                  className="input w-full"
                  rows={4}
                  value={formData.description || ''}
                  onChange={(e) => handleChange('description', e.target.value)}
                  placeholder="Describe your responsibilities and achievements..."
                />
              </div>

              {/* Skills */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Skills Used
                </label>
                <input
                  type="text"
                  className="input w-full"
                  value={formData.skills || ''}
                  onChange={(e) => handleChange('skills', e.target.value)}
                  placeholder="Separate skills with commas (e.g., Python, React, SQL)"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-between gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              {/* Delete button (only in edit mode) */}
              {mode === 'edit' && onDelete && experience?.id && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleDelete}
                  disabled={saving || deleting}
                  className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  {deleting ? 'Deleting...' : 'Delete'}
                </Button>
              )}

              {/* Spacer for alignment when no delete button */}
              {!(mode === 'edit' && onDelete && experience?.id) && <div />}

              <div className="flex gap-3">
                <Button type="button" variant="outline" onClick={onClose} disabled={saving || deleting}>
                  Cancel
                </Button>
                <Button type="submit" disabled={saving || deleting}>
                  {saving ? 'Saving...' : mode === 'create' ? 'Add Experience' : 'Save Changes'}
                </Button>
              </div>
            </div>
          </form>
        </div>
      </div>
  );
}
