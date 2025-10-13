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
import type { Education, EducationCreate, EducationUpdate } from '@/types/profile';
import { X, GraduationCap } from 'lucide-react';

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
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-green-100 text-green-600">
                  <GraduationCap className="h-5 w-5" />
                </span>
                <div>
                  <DialogTitle className="text-xl font-semibold text-slate-900">
                    {mode === 'create' ? 'Add Education' : 'Edit Education'}
                  </DialogTitle>
                  <DialogDescription className="text-sm text-slate-500">
                    {mode === 'create'
                      ? 'Add your educational background and academic achievements.'
                      : 'Update your education details and academic information.'}
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
                {/* Institution Name */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Institution Name *
                  </label>
                  <input
                    type="text"
                    required
                    className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                    value={formData.institution_name}
                    onChange={(e) => handleChange('institution_name', e.target.value)}
                  />
                </div>

                {/* Degree Type & Field of Study */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Degree Type *
                    </label>
                    <select
                      required
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
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

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Field of Study *
                    </label>
                    <input
                      type="text"
                      required
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.field_of_study}
                      onChange={(e) => handleChange('field_of_study', e.target.value)}
                      placeholder="e.g., Computer Science"
                    />
                  </div>
                </div>

                {/* Start Date, End Date & Graduation Year */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Start Date
                    </label>
                    <input
                      type="date"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.start_date || ''}
                      onChange={(e) => handleChange('start_date', e.target.value || null)}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      End Date
                    </label>
                    <input
                      type="date"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.end_date || ''}
                      onChange={(e) => handleChange('end_date', e.target.value || null)}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Graduation Year
                    </label>
                    <input
                      type="number"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.graduation_year || ''}
                      onChange={(e) => handleChange('graduation_year', e.target.value ? parseInt(e.target.value) : null)}
                      placeholder="e.g., 2024"
                      min="1950"
                      max="2050"
                    />
                  </div>
                </div>

                {/* GPA & GPA Scale */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      GPA
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.gpa || ''}
                      onChange={(e) => handleChange('gpa', e.target.value ? parseFloat(e.target.value) : null)}
                      placeholder="e.g., 3.85"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      GPA Scale
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.gpa_max || ''}
                      onChange={(e) => handleChange('gpa_max', e.target.value ? parseFloat(e.target.value) : null)}
                      placeholder="e.g., 4.00"
                    />
                  </div>
                </div>

                {/* Honors & Awards */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Honors & Awards
                  </label>
                  <textarea
                    className="w-full border border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2 focus-visible:ring-blue-500"
                    rows={2}
                    value={formData.honors_awards || ''}
                    onChange={(e) => handleChange('honors_awards', e.target.value || null)}
                    placeholder="List any honors, awards, or achievements..."
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Include Dean's List, scholarships, or academic awards
                  </p>
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
                    placeholder="Additional details about your education..."
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Add relevant coursework, projects, or activities
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
                {saving ? 'Saving...' : mode === 'create' ? 'Add Education' : 'Save Changes'}
              </Button>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
