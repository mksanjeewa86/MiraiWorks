'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import ProfileSectionWrapper from './ProfileSectionWrapper';
import ConfirmationModal from './ConfirmationModal';
import type { Project } from '@/types/profile';
import { Code, ExternalLink, Github, Calendar, Layers, Edit2, Trash2 } from 'lucide-react';
import { format } from 'date-fns';
import { updateProject } from '@/api/profile';

interface ProjectsSectionProps {
  projects: Project[];
  isLoading?: boolean;
  onAdd?: () => void;
  onEdit?: (project: Project) => void;
  onDelete?: (id: number) => void;
  readOnly?: boolean;
  isOwnProfile?: boolean;
}

export default function ProjectsSection({
  projects,
  isLoading = false,
  onAdd,
  onEdit,
  onDelete,
  readOnly = false,
  isOwnProfile = false,
}: ProjectsSectionProps) {
  const t = useTranslations('profile');
  const [draggedItem, setDraggedItem] = useState<number | null>(null);
  const [dragOverItem, setDragOverItem] = useState<number | null>(null);
  const [localProjects, setLocalProjects] = useState(projects);
  const [deleteConfirmation, setDeleteConfirmation] = useState<{ isOpen: boolean; id: number | null }>({
    isOpen: false,
    id: null,
  });

  // Update local state when projects prop changes
  useEffect(() => {
    setLocalProjects(projects);
  }, [projects]);

  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    try {
      return format(new Date(dateString), 'MMM yyyy');
    } catch {
      return dateString;
    }
  };

  const handleDragStart = (e: React.DragEvent, index: number) => {
    if (readOnly || localProjects.length <= 1) return;
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

    const newProjects = [...localProjects];
    const draggedProject = newProjects[draggedItem];

    // Remove dragged item and insert at new position
    newProjects.splice(draggedItem, 1);
    newProjects.splice(dragOverItem, 0, draggedProject);

    // Update display order
    const updatedProjects = newProjects.map((project, index) => ({
      ...project,
      display_order: index,
    }));

    setLocalProjects(updatedProjects);
    setDraggedItem(null);
    setDragOverItem(null);

    // Update backend with new order
    try {
      await Promise.all(
        updatedProjects.map((project) =>
          updateProject(project.id, { display_order: project.display_order })
        )
      );
    } catch (error) {
      console.error('Failed to update project order:', error);
      // Revert on error
      setLocalProjects(projects);
    }
  };

  const handleDragLeave = () => {
    setDragOverItem(null);
  };

  return (
    <ProfileSectionWrapper
      title={t('projects.title')}
      onAdd={!readOnly ? onAdd : undefined}
      addButtonText={t('projects.add')}
      isEmpty={localProjects.length === 0}
      emptyMessage={t('projects.noProjects')}
      isLoading={isLoading}
      sectionId="projects"
      showPrivacyToggle={true}
      isOwnProfile={isOwnProfile}
      readOnly={readOnly}
      privacyKey="show_projects"
    >
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {localProjects.map((project, index) => {
          const images = project.image_urls ? project.image_urls.split(',').map(url => url.trim()) : [];
          const technologies = project.technologies ? project.technologies.split(',').map(tech => tech.trim()) : [];

          return (
            <div
              key={project.id}
              draggable={!readOnly && localProjects.length > 1}
              onDragStart={(e) => handleDragStart(e, index)}
              onDragOver={(e) => handleDragOver(e, index)}
              onDragEnd={handleDragEnd}
              onDragLeave={handleDragLeave}
              className={`group relative flex gap-3 bg-white dark:bg-gray-800 rounded-xl border-2 p-4 ${
                draggedItem === index
                  ? 'border-indigo-400 opacity-50'
                  : dragOverItem === index
                  ? 'border-indigo-400 border-dashed'
                  : 'border-gray-200 dark:border-gray-700'
              } ${!readOnly && localProjects.length > 1 ? 'cursor-move hover:shadow-lg hover:border-gray-300 dark:hover:border-gray-600' : ''}`}
            >
              {/* Project Icon/Image */}
              <div className="flex-shrink-0">
                {images.length > 0 && images[0] ? (
                  <div className="relative">
                    <img
                      src={images[0]}
                      alt={project.project_name}
                      className="w-12 h-12 rounded-lg object-cover"
                    />
                    {/* Image count badge */}
                    {images.length > 1 && (
                      <div className="absolute -top-1 -right-1 flex items-center justify-center w-5 h-5 rounded-full bg-indigo-600 text-white text-[10px] font-bold shadow-md">
                        {images.length}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 via-indigo-600 to-purple-700 flex items-center justify-center shadow-md">
                    <Code className="h-6 w-6 text-white" />
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                {/* Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <h4 className="text-base font-bold text-gray-900 dark:text-white line-clamp-2 mb-1">
                      {project.project_name}
                    </h4>
                    {project.role && (
                      <p className="text-sm text-indigo-600 dark:text-indigo-400 line-clamp-1">
                        {project.role}
                      </p>
                    )}
                  </div>

                  {/* Edit and Delete buttons */}
                  {!readOnly && (
                    <div className="flex gap-1 ml-2">
                      {onEdit && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onEdit(project);
                          }}
                          className="p-1.5 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/30 hover:text-indigo-600 dark:hover:text-indigo-400"
                          title={t('actions.edit')}
                        >
                          <Edit2 className="h-3.5 w-3.5" />
                        </button>
                      )}
                      {onDelete && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteConfirmation({ isOpen: true, id: project.id });
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
                <div className="flex flex-wrap items-center gap-2 text-xs mb-3">
                  {/* Date range */}
                  {(project.start_date || project.end_date) && (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium">
                      <Calendar className="h-3 w-3" />
                      {project.start_date && formatDate(project.start_date)}
                      {project.start_date && project.end_date && ' - '}
                      {project.end_date && formatDate(project.end_date)}
                    </span>
                  )}

                  {/* Technologies */}
                  {technologies.length > 0 && (
                    <>
                      {technologies.slice(0, 3).map((tech, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-2 py-0.5 rounded-full bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 text-blue-700 dark:text-blue-300 font-semibold border border-blue-200 dark:border-blue-700"
                        >
                          {tech}
                        </span>
                      ))}
                      {technologies.length > 3 && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 font-semibold">
                          +{technologies.length - 3}
                        </span>
                      )}
                    </>
                  )}
                </div>

                {/* Description */}
                {project.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2 leading-relaxed">
                    {project.description}
                  </p>
                )}

                {/* Links */}
                <div className="flex gap-2">
                  {project.project_url && (
                    <a
                      href={project.project_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 font-medium hover:bg-blue-100 dark:hover:bg-blue-900/40"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <ExternalLink className="h-3 w-3" />
                      View
                    </a>
                  )}
                  {project.github_url && (
                    <a
                      href={project.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium hover:bg-gray-100 dark:hover:bg-gray-600"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Github className="h-3 w-3" />
                      Code
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
        title="Delete Project"
        description="Are you sure you want to delete this project? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
      />
    </ProfileSectionWrapper>
  );
}
