'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui';
import type { Education, EducationCreate, EducationUpdate } from '@/types/profile';
import { X } from 'lucide-react';

interface EducationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: EducationCreate | EducationUpdate) => Promise<void>;
  education?: Education;
  mode: 'create' | 'edit';
}

export default function EducationModal({
  isOpen,
  onClose,
  onSave,
  education,
  mode,
}: EducationModalProps) {
  const [formData, setFormData] = useState<EducationCreate>({
    institution_name: '',
    degree_type: "Bachelor's Degree",
    field_of_study: '',
    start_date: null,
    end_date: null,
    graduation_year: null,
    gpa: null,
    gpa_max: null,
    honors_awards: null,
    description: null,
    institution_logo_url: null,
    display_order: 0,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (education && mode === 'edit') {
      setFormData({
        institution_name: education.institution_name,
        degree_type: education.degree_type,
        field_of_study: education.field_of_study,
        start_date: education.start_date,
        end_date: education.end_date,
        graduation_year: education.graduation_year,
        gpa: education.gpa,
        gpa_max: education.gpa_max,
        honors_awards: education.honors_awards,
        description: education.description,
        institution_logo_url: education.institution_logo_url,
        display_order: education.display_order,
      });
    } else {
      setFormData({
        institution_name: '',
        degree_type: "Bachelor's Degree",
        field_of_study: '',
        start_date: null,
        end_date: null,
        graduation_year: null,
        gpa: null,
        gpa_max: null,
        honors_awards: null,
        description: null,
        institution_logo_url: null,
        display_order: 0,
      });
    }
  }, [education, mode, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaving(true);

    try {
      await onSave(formData);
      onClose();
    } catch (err: any) {
      console.error('Failed to save education:', err);
      setError(err.message || 'Failed to save education');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof EducationCreate, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold" style={{ color: 'var(--text-primary)' }}>
              {mode === 'create' ? 'Add Education' : 'Edit Education'}
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
              {/* Institution Name */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Institution Name *
                </label>
                <input
                  type="text"
                  required
                  className="input w-full"
                  value={formData.institution_name}
                  onChange={(e) => handleChange('institution_name', e.target.value)}
                />
              </div>

              {/* Degree Type */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Degree Type *
                </label>
                <select
                  required
                  className="input w-full"
                  value={formData.degree_type}
                  onChange={(e) => handleChange('degree_type', e.target.value)}
                >
                  <option value="High School">High School</option>
                  <option value="Associate Degree">Associate Degree</option>
                  <option value="Bachelor's Degree">Bachelor's Degree</option>
                  <option value="Master's Degree">Master's Degree</option>
                  <option value="Doctorate (PhD)">Doctorate (PhD)</option>
                  <option value="MBA">MBA</option>
                  <option value="Certificate">Certificate</option>
                  <option value="Diploma">Diploma</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              {/* Field of Study */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Field of Study *
                </label>
                <input
                  type="text"
                  required
                  className="input w-full"
                  value={formData.field_of_study}
                  onChange={(e) => handleChange('field_of_study', e.target.value)}
                  placeholder="e.g., Computer Science"
                />
              </div>

              {/* Start Date */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Start Date
                </label>
                <input
                  type="date"
                  className="input w-full"
                  value={formData.start_date || ''}
                  onChange={(e) => handleChange('start_date', e.target.value || null)}
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
                />
              </div>

              {/* Graduation Year */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Graduation Year
                </label>
                <input
                  type="number"
                  className="input w-full"
                  value={formData.graduation_year || ''}
                  onChange={(e) => handleChange('graduation_year', e.target.value ? parseInt(e.target.value) : null)}
                  placeholder="e.g., 2024"
                  min="1950"
                  max="2050"
                />
              </div>

              {/* GPA */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  GPA
                </label>
                <input
                  type="number"
                  step="0.01"
                  className="input w-full"
                  value={formData.gpa || ''}
                  onChange={(e) => handleChange('gpa', e.target.value ? parseFloat(e.target.value) : null)}
                  placeholder="e.g., 3.85"
                />
              </div>

              {/* GPA Max */}
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  GPA Scale
                </label>
                <input
                  type="number"
                  step="0.01"
                  className="input w-full"
                  value={formData.gpa_max || ''}
                  onChange={(e) => handleChange('gpa_max', e.target.value ? parseFloat(e.target.value) : null)}
                  placeholder="e.g., 4.00"
                />
              </div>

              {/* Honors & Awards */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--text-primary)' }}>
                  Honors & Awards
                </label>
                <textarea
                  className="input w-full"
                  rows={2}
                  value={formData.honors_awards || ''}
                  onChange={(e) => handleChange('honors_awards', e.target.value || null)}
                  placeholder="List any honors, awards, or achievements..."
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
                  placeholder="Additional details about your education..."
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <Button type="button" variant="outline" onClick={onClose} disabled={saving}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                {saving ? 'Saving...' : mode === 'create' ? 'Add Education' : 'Save Changes'}
              </Button>
            </div>
          </form>
        </div>
      </div>
  );
}
