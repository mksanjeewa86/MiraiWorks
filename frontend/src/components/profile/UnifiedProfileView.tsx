'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useAuth } from '@/contexts/AuthContext';
import { useUserRole } from '@/hooks/useUserRole';
import { isSectionVisible } from '@/lib/profileVisibility';
import ProfileCompletenessCard from './ProfileCompletenessCard';
import RecruiterProfileView from './RecruiterProfileView';
import EmployerProfileView from './EmployerProfileView';
import WorkExperienceSection from './WorkExperienceSection';
import EducationSection from './EducationSection';
import SkillsSection from './SkillsSection';
import CertificationsSection from './CertificationsSection';
import ProjectsSection from './ProjectsSection';
import WorkExperienceModal from './WorkExperienceModal';
import EducationModal from './EducationModal';
import SkillModal from './SkillModal';
import CertificationModal from './CertificationModal';
import ProjectModal from './ProjectModal';
import {
  getWorkExperiences,
  getEducations,
  getSkills,
  getCertifications,
  getProjects,
  createWorkExperience,
  updateWorkExperience,
  deleteWorkExperience,
  createEducation,
  updateEducation,
  deleteEducation,
  createSkill,
  updateSkill,
  deleteSkill,
  createCertification,
  updateCertification,
  deleteCertification,
  createProject,
  updateProject,
  deleteProject,
} from '@/api/profile';
import type {
  WorkExperience,
  WorkExperienceCreate,
  WorkExperienceUpdate,
  Education,
  EducationCreate,
  EducationUpdate,
  Skill,
  SkillCreate,
  SkillUpdate,
  Certification,
  CertificationCreate,
  CertificationUpdate,
  Project,
  ProjectCreate,
  ProjectUpdate,
} from '@/types/profile';
import { AlertCircle } from 'lucide-react';
import type { PrivacySettings } from '@/api/privacy';

interface UnifiedProfileViewProps {
  userId?: number;
  isOwnProfile?: boolean;
  readOnly?: boolean;
  privacySettings?: PrivacySettings | null;
}

export default function UnifiedProfileView({
  userId,
  isOwnProfile = true,
  readOnly = false,
  privacySettings = null,
}: UnifiedProfileViewProps) {
  const t = useTranslations('profile');
  const { primaryRole, isSystemAdmin, isCompanyAdmin } = useUserRole();
  const { user } = useAuth();

  // State for all profile sections
  const [workExperiences, setWorkExperiences] = useState<WorkExperience[]>([]);
  const [educations, setEducations] = useState<Education[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [certifications, setCertifications] = useState<Certification[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);

  // Loading states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal states
  const [workExpModal, setWorkExpModal] = useState<{ isOpen: boolean; mode: 'create' | 'edit'; item?: WorkExperience }>({ isOpen: false, mode: 'create' });
  const [educationModal, setEducationModal] = useState<{ isOpen: boolean; mode: 'create' | 'edit'; item?: Education }>({ isOpen: false, mode: 'create' });
  const [skillModal, setSkillModal] = useState<{ isOpen: boolean; mode: 'create' | 'edit'; item?: Skill }>({ isOpen: false, mode: 'create' });
  const [certificationModal, setCertificationModal] = useState<{ isOpen: boolean; mode: 'create' | 'edit'; item?: Certification }>({ isOpen: false, mode: 'create' });
  const [projectModal, setProjectModal] = useState<{ isOpen: boolean; mode: 'create' | 'edit'; item?: Project }>({ isOpen: false, mode: 'create' });

  // Fetch all profile data
  useEffect(() => {
    const fetchProfileData = async () => {
      if (!isOwnProfile && !userId) {
        setError('User ID is required for viewing other profiles');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        // Fetch all profile sections in parallel
        const [workExpData, eduData, skillsData, certsData, projectsData] = await Promise.all([
          getWorkExperiences().catch(() => []),
          getEducations().catch(() => []),
          getSkills().catch(() => []),
          getCertifications().catch(() => []),
          getProjects().catch(() => []),
        ]);

        setWorkExperiences(workExpData);
        setEducations(eduData);
        setSkills(skillsData);
        setCertifications(certsData);
        setProjects(projectsData);
      } catch (err: any) {
        console.error('Error fetching profile data:', err);
        setError(err.message || 'Failed to load profile data');
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, [userId, isOwnProfile]);

  // Work Experience Handlers
  const handleAddWorkExperience = () => {
    setWorkExpModal({ isOpen: true, mode: 'create' });
  };

  const handleEditWorkExperience = (experience: WorkExperience) => {
    setWorkExpModal({ isOpen: true, mode: 'edit', item: experience });
  };

  const handleSaveWorkExperience = async (data: WorkExperienceCreate | WorkExperienceUpdate) => {
    if (workExpModal.mode === 'create') {
      const newExp = await createWorkExperience(data as WorkExperienceCreate);
      setWorkExperiences([...workExperiences, newExp]);
    } else if (workExpModal.item) {
      const updated = await updateWorkExperience(workExpModal.item.id, data as WorkExperienceUpdate);
      setWorkExperiences(workExperiences.map(exp => exp.id === updated.id ? updated : exp));
    }
  };

  const handleDeleteWorkExperience = async (id: number) => {
    await deleteWorkExperience(id);
    setWorkExperiences(workExperiences.filter(exp => exp.id !== id));
  };

  // Education Handlers
  const handleAddEducation = () => {
    setEducationModal({ isOpen: true, mode: 'create' });
  };

  const handleEditEducation = (education: Education) => {
    setEducationModal({ isOpen: true, mode: 'edit', item: education });
  };

  const handleSaveEducation = async (data: EducationCreate | EducationUpdate) => {
    if (educationModal.mode === 'create') {
      const newEdu = await createEducation(data as EducationCreate);
      setEducations([...educations, newEdu]);
    } else if (educationModal.item) {
      const updated = await updateEducation(educationModal.item.id, data as EducationUpdate);
      setEducations(educations.map(edu => edu.id === updated.id ? updated : edu));
    }
  };

  const handleDeleteEducation = async (id: number) => {
    try {
      await deleteEducation(id);
      setEducations(educations.filter(edu => edu.id !== id));
    } catch (err) {
      console.error('Failed to delete education:', err);
    }
  };

  // Skill Handlers
  const handleAddSkill = () => {
    setSkillModal({ isOpen: true, mode: 'create' });
  };

  const handleEditSkill = (skill: Skill) => {
    setSkillModal({ isOpen: true, mode: 'edit', item: skill });
  };

  const handleSaveSkill = async (data: SkillCreate | SkillUpdate) => {
    if (skillModal.mode === 'create') {
      const newSkill = await createSkill(data as SkillCreate);
      setSkills([...skills, newSkill]);
    } else if (skillModal.item) {
      const updated = await updateSkill(skillModal.item.id, data as SkillUpdate);
      setSkills(skills.map(s => s.id === updated.id ? updated : s));
    }
  };

  const handleDeleteSkill = async (id: number) => {
    try {
      await deleteSkill(id);
      setSkills(skills.filter(skill => skill.id !== id));
    } catch (err) {
      console.error('Failed to delete skill:', err);
    }
  };

  // Certification Handlers
  const handleAddCertification = () => {
    setCertificationModal({ isOpen: true, mode: 'create' });
  };

  const handleEditCertification = (certification: Certification) => {
    setCertificationModal({ isOpen: true, mode: 'edit', item: certification });
  };

  const handleSaveCertification = async (data: CertificationCreate | CertificationUpdate) => {
    if (certificationModal.mode === 'create') {
      const newCert = await createCertification(data as CertificationCreate);
      setCertifications([...certifications, newCert]);
    } else if (certificationModal.item) {
      const updated = await updateCertification(certificationModal.item.id, data as CertificationUpdate);
      setCertifications(certifications.map(cert => cert.id === updated.id ? updated : cert));
    }
  };

  const handleDeleteCertification = async (id: number) => {
    try {
      await deleteCertification(id);
      setCertifications(certifications.filter(cert => cert.id !== id));
    } catch (err) {
      console.error('Failed to delete certification:', err);
    }
  };

  // Project Handlers
  const handleAddProject = () => {
    setProjectModal({ isOpen: true, mode: 'create' });
  };

  const handleEditProject = (project: Project) => {
    setProjectModal({ isOpen: true, mode: 'edit', item: project });
  };

  const handleSaveProject = async (data: ProjectCreate | ProjectUpdate) => {
    if (projectModal.mode === 'create') {
      const newProj = await createProject(data as ProjectCreate);
      setProjects([...projects, newProj]);
    } else if (projectModal.item) {
      const updated = await updateProject(projectModal.item.id, data as ProjectUpdate);
      setProjects(projects.map(proj => proj.id === updated.id ? updated : proj));
    }
  };

  const handleDeleteProject = async (id: number) => {
    try {
      await deleteProject(id);
      setProjects(projects.filter(proj => proj.id !== id));
    } catch (err) {
      console.error('Failed to delete project:', err);
    }
  };

  // Determine effective role for visibility checks
  const effectiveRole = isSystemAdmin ? 'System Admin' : isCompanyAdmin ? 'Company Admin' : primaryRole;

  // Determine which sections are visible based on role AND privacy settings
  const showCompleteness = isSectionVisible('completeness_indicator', effectiveRole, isOwnProfile);
  const showWorkExperience = isSectionVisible('work_experience', effectiveRole, isOwnProfile) &&
    (isOwnProfile || !privacySettings || privacySettings.show_work_experience);
  const showEducation = isSectionVisible('education', effectiveRole, isOwnProfile) &&
    (isOwnProfile || !privacySettings || privacySettings.show_education);
  const showSkills = isSectionVisible('skills', effectiveRole, isOwnProfile) &&
    (isOwnProfile || !privacySettings || privacySettings.show_skills);
  const showCertifications = isSectionVisible('certifications', effectiveRole, isOwnProfile) &&
    (isOwnProfile || !privacySettings || privacySettings.show_certifications);
  const showProjects = isSectionVisible('projects', effectiveRole, isOwnProfile) &&
    (isOwnProfile || !privacySettings || privacySettings.show_projects);

  if (error) {
    return (
      <div className="flex items-center gap-2 p-4 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400">
        <AlertCircle className="h-5 w-5" />
        <span>{error}</span>
      </div>
    );
  }

  // Route to role-specific profile view based on role and company type

  // System Admin: Use default view with minimal sections
  if (isSystemAdmin) {
    // Admin profile - just basic info
    // Sections are controlled by visibility flags
    return (
      <>
        <div className="space-y-6">
          {/* Admin profile - basic info only, no candidate sections */}
          {!showWorkExperience &&
            !showEducation &&
            !showSkills &&
            !showCertifications &&
            !showProjects &&
            !showCompleteness && (
              <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  System Admin Profile - Basic information only
                </p>
              </div>
            )}
        </div>
      </>
    );
  }

  // Company Admin: Use default view with minimal sections
  if (isCompanyAdmin) {
    // Admin profile - just basic info
    return (
      <>
        <div className="space-y-6">
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Company Admin Profile - Basic information only
            </p>
          </div>
        </div>
      </>
    );
  }

  // Member role: Route based on company type
  if (primaryRole === 'member' && user?.company) {
    if (user.company.type === 'recruiter') {
      return (
        <>
          <RecruiterProfileView
            userId={userId}
            isOwnProfile={isOwnProfile}
            readOnly={readOnly}
          />
        </>
      );
    }

    if (user.company.type === 'employer') {
      return (
        <>
          <EmployerProfileView
            userId={userId}
            isOwnProfile={isOwnProfile}
            readOnly={readOnly}
          />
        </>
      );
    }
  }

  // Default: Candidate profile view (or fallback for members without company)
  return (
    <>
      <div className="space-y-6">
        {/* Profile Completeness Card */}
        {showCompleteness && <ProfileCompletenessCard />}

        {/* Work Experience Section */}
        {showWorkExperience && (
          <WorkExperienceSection
            experiences={workExperiences}
            isLoading={loading}
            readOnly={readOnly}
            isOwnProfile={isOwnProfile}
            onAdd={!readOnly ? handleAddWorkExperience : undefined}
            onEdit={!readOnly ? handleEditWorkExperience : undefined}
            onDelete={!readOnly ? handleDeleteWorkExperience : undefined}
          />
        )}

        {/* Education Section */}
        {showEducation && (
          <EducationSection
            educations={educations}
            isLoading={loading}
            readOnly={readOnly}
            isOwnProfile={isOwnProfile}
            onAdd={!readOnly ? handleAddEducation : undefined}
            onEdit={!readOnly ? handleEditEducation : undefined}
            onDelete={!readOnly ? handleDeleteEducation : undefined}
          />
        )}

        {/* Skills Section */}
        {showSkills && (
          <SkillsSection
            skills={skills}
            isLoading={loading}
            readOnly={readOnly}
            isOwnProfile={isOwnProfile}
            onAdd={!readOnly ? handleAddSkill : undefined}
            onEdit={!readOnly ? handleEditSkill : undefined}
            onDelete={!readOnly ? handleDeleteSkill : undefined}
          />
        )}

        {/* Certifications Section */}
        {showCertifications && (
          <CertificationsSection
            certifications={certifications}
            isLoading={loading}
            readOnly={readOnly}
            isOwnProfile={isOwnProfile}
            onAdd={!readOnly ? handleAddCertification : undefined}
            onEdit={!readOnly ? handleEditCertification : undefined}
            onDelete={!readOnly ? handleDeleteCertification : undefined}
          />
        )}

        {/* Projects Section */}
        {showProjects && (
          <ProjectsSection
            projects={projects}
            isLoading={loading}
            readOnly={readOnly}
            isOwnProfile={isOwnProfile}
            onAdd={!readOnly ? handleAddProject : undefined}
            onEdit={!readOnly ? handleEditProject : undefined}
            onDelete={!readOnly ? handleDeleteProject : undefined}
          />
        )}

        {/* Empty state if no sections are visible */}
        {!showWorkExperience &&
          !showEducation &&
          !showSkills &&
          !showCertifications &&
          !showProjects &&
          !showCompleteness && (
            <div className="text-center py-12">
              <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
                {t('emptyStates.noProfileData')}
              </p>
            </div>
          )}
      </div>

      {/* All Modals */}
      <WorkExperienceModal
        isOpen={workExpModal.isOpen}
        onClose={() => setWorkExpModal({ isOpen: false, mode: 'create' })}
        onSave={handleSaveWorkExperience}
        onDelete={handleDeleteWorkExperience}
        experience={workExpModal.item}
        mode={workExpModal.mode}
      />

      <EducationModal
        isOpen={educationModal.isOpen}
        onClose={() => setEducationModal({ isOpen: false, mode: 'create' })}
        onSave={handleSaveEducation}
        education={educationModal.item}
        mode={educationModal.mode}
      />

      <SkillModal
        isOpen={skillModal.isOpen}
        onClose={() => setSkillModal({ isOpen: false, mode: 'create' })}
        onSave={handleSaveSkill}
        skill={skillModal.item}
        mode={skillModal.mode}
      />

      <CertificationModal
        isOpen={certificationModal.isOpen}
        onClose={() => setCertificationModal({ isOpen: false, mode: 'create' })}
        onSave={handleSaveCertification}
        certification={certificationModal.item}
        mode={certificationModal.mode}
      />

      <ProjectModal
        isOpen={projectModal.isOpen}
        onClose={() => setProjectModal({ isOpen: false, mode: 'create' })}
        onSave={handleSaveProject}
        project={projectModal.item}
        mode={projectModal.mode}
      />
    </>
  );
}
