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
import type { Project, ProjectCreate, ProjectUpdate } from '@/types/profile';
import { X, FolderGit2 } from 'lucide-react';

interface ProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: ProjectCreate | ProjectUpdate) => Promise<void>;
  project?: Project;
  mode: 'create' | 'edit';
}

export default function ProjectModal({
  isOpen,
  onClose,
  onSave,
  project,
  mode,
}: ProjectModalProps) {
  const [formData, setFormData] = useState<ProjectCreate>({
    project_name: '',
    description: null,
    role: null,
    technologies: null,
    project_url: null,
    github_url: null,
    image_urls: null,
    start_date: null,
    end_date: null,
    display_order: 0,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (project && mode === 'edit') {
      setFormData({
        project_name: project.project_name,
        description: project.description,
        role: project.role,
        technologies: project.technologies,
        project_url: project.project_url,
        github_url: project.github_url,
        image_urls: project.image_urls,
        start_date: project.start_date,
        end_date: project.end_date,
        display_order: project.display_order,
      });
    } else {
      setFormData({
        project_name: '',
        description: null,
        role: null,
        technologies: null,
        project_url: null,
        github_url: null,
        image_urls: null,
        start_date: null,
        end_date: null,
        display_order: 0,
      });
    }
  }, [project, mode, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSaving(true);

    try {
      await onSave(formData);
      onClose();
    } catch (err: any) {
      console.error('Failed to save project:', err);
      setError(err.message || 'Failed to save project');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: keyof ProjectCreate, value: any) => {
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
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 text-purple-600">
                  <FolderGit2 className="h-5 w-5" />
                </span>
                <div>
                  <DialogTitle className="text-xl font-semibold text-slate-900">
                    {mode === 'create' ? 'Add Project' : 'Edit Project'}
                  </DialogTitle>
                  <DialogDescription className="text-sm text-slate-500">
                    {mode === 'create'
                      ? 'Showcase your projects and technical achievements.'
                      : 'Update your project details and accomplishments.'}
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
                {/* Project Name */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Project Name *
                  </label>
                  <input
                    type="text"
                    required
                    className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                    value={formData.project_name}
                    onChange={(e) => handleChange('project_name', e.target.value)}
                    placeholder="e.g., E-commerce Platform"
                  />
                </div>

                {/* Role */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Your Role
                  </label>
                  <input
                    type="text"
                    className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                    value={formData.role || ''}
                    onChange={(e) => handleChange('role', e.target.value || null)}
                    placeholder="e.g., Lead Developer, Designer"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Specify your role in the project
                  </p>
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Description
                  </label>
                  <textarea
                    className="w-full border border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2 focus-visible:ring-blue-500"
                    rows={4}
                    value={formData.description || ''}
                    onChange={(e) => handleChange('description', e.target.value || null)}
                    placeholder="Describe the project, your contributions, and achievements..."
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Highlight key features and your impact
                  </p>
                </div>

                {/* Technologies */}
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    Technologies Used
                  </label>
                  <input
                    type="text"
                    className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                    value={formData.technologies || ''}
                    onChange={(e) => handleChange('technologies', e.target.value || null)}
                    placeholder="React, Node.js, MongoDB"
                  />
                  <p className="text-xs text-slate-500 mt-1">
                    Separate with commas
                  </p>
                </div>

                {/* Project URL & GitHub URL */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Project URL
                    </label>
                    <input
                      type="url"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.project_url || ''}
                      onChange={(e) => handleChange('project_url', e.target.value || null)}
                      placeholder="https://project-demo.com"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      GitHub URL
                    </label>
                    <input
                      type="url"
                      className="w-full border-slate-300 bg-white text-slate-900 rounded-md px-3 py-2"
                      value={formData.github_url || ''}
                      onChange={(e) => handleChange('github_url', e.target.value || null)}
                      placeholder="https://github.com/username/project"
                    />
                  </div>
                </div>

                {/* Start Date & End Date */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                    <p className="text-xs text-slate-500 mt-1">
                      Leave blank if ongoing
                    </p>
                  </div>
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
                {saving ? 'Saving...' : mode === 'create' ? 'Add Project' : 'Save Changes'}
              </Button>
            </div>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
