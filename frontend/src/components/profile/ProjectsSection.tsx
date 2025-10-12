'use client';

import { useTranslations } from 'next-intl';
import ProfileSectionWrapper from './ProfileSectionWrapper';
import type { Project } from '@/types/profile';
import { Code, ExternalLink, Github, Calendar, Image as ImageIcon, Edit2, Layers } from 'lucide-react';
import { format } from 'date-fns';

interface ProjectsSectionProps {
  projects: Project[];
  isLoading?: boolean;
  onAdd?: () => void;
  onEdit?: (project: Project) => void;
  readOnly?: boolean;
  isOwnProfile?: boolean;
}

export default function ProjectsSection({
  projects,
  isLoading = false,
  onAdd,
  onEdit,
  readOnly = false,
  isOwnProfile = false,
}: ProjectsSectionProps) {
  const t = useTranslations('profile');

  const formatDate = (dateString: string | null) => {
    if (!dateString) return null;
    try {
      return format(new Date(dateString), 'MMM yyyy');
    } catch {
      return dateString;
    }
  };

  return (
    <ProfileSectionWrapper
      title={t('projects.title')}
      onAdd={!readOnly ? onAdd : undefined}
      addButtonText={t('projects.add')}
      isEmpty={projects.length === 0}
      emptyMessage={t('projects.noProjects')}
      isLoading={isLoading}
      sectionId="projects"
      showPrivacyToggle={true}
      isOwnProfile={isOwnProfile}
      readOnly={readOnly}
      privacyKey="show_projects"
    >
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {projects.map((project) => {
          const images = project.image_urls ? project.image_urls.split(',').map(url => url.trim()) : [];
          const technologies = project.technologies ? project.technologies.split(',').map(tech => tech.trim()) : [];

          return (
            <div
              key={project.id}
              className="group relative bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden transition-all duration-300 hover:shadow-2xl hover:-translate-y-2 hover:border-blue-300 dark:hover:border-blue-600"
            >
              {/* Edit button */}
              {!readOnly && onEdit && (
                <button
                  onClick={() => onEdit(project)}
                  className="absolute top-3 right-3 z-10 p-2 rounded-lg bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm text-gray-600 dark:text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity hover:bg-blue-50 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-400 shadow-lg"
                  title={t('actions.edit')}
                >
                  <Edit2 className="h-4 w-4" />
                </button>
              )}

              {/* Project image with overlay */}
              {images.length > 0 && images[0] ? (
                <div className="relative h-52 overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-900 dark:to-gray-800">
                  <img
                    src={images[0]}
                    alt={project.project_name}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                  {/* Gradient overlay */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                  {/* Image count badge */}
                  {images.length > 1 && (
                    <div className="absolute bottom-3 right-3 flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-black/70 backdrop-blur-sm text-white">
                      <Layers className="h-3.5 w-3.5" />
                      <span className="text-xs font-semibold">{images.length}</span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="relative h-52 bg-gradient-to-br from-blue-500 via-indigo-600 to-purple-700 flex items-center justify-center">
                  <Code className="h-16 w-16 text-white opacity-80" />
                </div>
              )}

              {/* Content */}
              <div className="p-5">
                {/* Project name and role */}
                <div className="mb-3">
                  <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-1 line-clamp-2 min-h-[3.5rem]">
                    {project.project_name}
                  </h4>
                  {project.role && (
                    <p className="text-sm font-semibold text-blue-600 dark:text-blue-400 line-clamp-1">
                      {project.role}
                    </p>
                  )}
                </div>

                {/* Date range */}
                {(project.start_date || project.end_date) && (
                  <div className="flex items-center gap-2 mb-3 px-3 py-1.5 rounded-lg bg-gray-50 dark:bg-gray-700/50 w-fit">
                    <Calendar className="h-4 w-4 text-gray-500 dark:text-gray-400" />
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                      {project.start_date && formatDate(project.start_date)}
                      {project.start_date && project.end_date && ' - '}
                      {project.end_date && formatDate(project.end_date)}
                    </span>
                  </div>
                )}

                {/* Description */}
                {project.description && (
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-3 leading-relaxed">
                    {project.description}
                  </p>
                )}

                {/* Technologies */}
                {technologies.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {technologies.slice(0, 4).map((tech, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center px-2.5 py-1 rounded-full bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 text-blue-700 dark:text-blue-300 text-xs font-semibold border border-blue-200 dark:border-blue-700"
                      >
                        {tech}
                      </span>
                    ))}
                    {technologies.length > 4 && (
                      <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs font-semibold">
                        +{technologies.length - 4}
                      </span>
                    )}
                  </div>
                )}

                {/* Divider */}
                <div className="h-px bg-gradient-to-r from-transparent via-gray-300 dark:via-gray-600 to-transparent mb-4" />

                {/* Links */}
                <div className="flex gap-2">
                  {project.project_url && (
                    <a
                      href={project.project_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-sm font-semibold transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <ExternalLink className="h-4 w-4" />
                      View
                    </a>
                  )}
                  {project.github_url && (
                    <a
                      href={project.github_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 text-sm font-semibold transition-all duration-300 hover:shadow-md hover:-translate-y-0.5 ${
                        project.project_url ? '' : 'flex-1'
                      }`}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Github className="h-4 w-4" />
                      {project.project_url ? '' : 'Code'}
                    </a>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </ProfileSectionWrapper>
  );
}
