/**
 * Profile API client functions
 */

import { API_ENDPOINTS } from './config';
import { makeAuthenticatedRequest } from './apiClient';
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
  JobPreference,
  JobPreferenceCreate,
  JobPreferenceUpdate,
  ProfileCompleteness,
} from '@/types/profile';

// ================== WORK EXPERIENCE ==================

export const getWorkExperiences = async (): Promise<WorkExperience[]> => {
  const response = await makeAuthenticatedRequest<WorkExperience[]>(
    API_ENDPOINTS.PROFILE.WORK_EXPERIENCE,
    {
      method: 'GET',
    }
  );
  return response.data;
};

export const createWorkExperience = async (
  data: WorkExperienceCreate
): Promise<WorkExperience> => {
  const response = await makeAuthenticatedRequest<WorkExperience>(
    API_ENDPOINTS.PROFILE.WORK_EXPERIENCE,
    {
      method: 'POST',
      body: JSON.stringify(data),
    }
  );
  return response.data;
};

export const getWorkExperience = async (id: number): Promise<WorkExperience> => {
  const response = await makeAuthenticatedRequest<WorkExperience>(
    API_ENDPOINTS.PROFILE.WORK_EXPERIENCE_BY_ID(id),
    {
      method: 'GET',
    }
  );
  return response.data;
};

export const updateWorkExperience = async (
  id: number,
  data: WorkExperienceUpdate
): Promise<WorkExperience> => {
  const response = await makeAuthenticatedRequest<WorkExperience>(
    API_ENDPOINTS.PROFILE.WORK_EXPERIENCE_BY_ID(id),
    {
      method: 'PUT',
      body: JSON.stringify(data),
    }
  );
  return response.data;
};

export const deleteWorkExperience = async (id: number): Promise<void> => {
  await makeAuthenticatedRequest<void>(API_ENDPOINTS.PROFILE.WORK_EXPERIENCE_BY_ID(id), {
    method: 'DELETE',
  });
};

// ================== EDUCATION ==================

export const getEducations = async (): Promise<Education[]> => {
  const response = await makeAuthenticatedRequest<Education[]>(API_ENDPOINTS.PROFILE.EDUCATION, {
    method: 'GET',
  });
  return response.data;
};

export const createEducation = async (data: EducationCreate): Promise<Education> => {
  const response = await makeAuthenticatedRequest<Education>(API_ENDPOINTS.PROFILE.EDUCATION, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response.data;
};

export const getEducation = async (id: number): Promise<Education> => {
  const response = await makeAuthenticatedRequest<Education>(
    API_ENDPOINTS.PROFILE.EDUCATION_BY_ID(id),
    {
      method: 'GET',
    }
  );
  return response.data;
};

export const updateEducation = async (id: number, data: EducationUpdate): Promise<Education> => {
  const response = await makeAuthenticatedRequest<Education>(
    API_ENDPOINTS.PROFILE.EDUCATION_BY_ID(id),
    {
      method: 'PUT',
      body: JSON.stringify(data),
    }
  );
  return response.data;
};

export const deleteEducation = async (id: number): Promise<void> => {
  await makeAuthenticatedRequest<void>(API_ENDPOINTS.PROFILE.EDUCATION_BY_ID(id), {
    method: 'DELETE',
  });
};

// ================== SKILLS ==================

export const getSkills = async (category?: string): Promise<Skill[]> => {
  const url = category
    ? `${API_ENDPOINTS.PROFILE.SKILLS}?category=${encodeURIComponent(category)}`
    : API_ENDPOINTS.PROFILE.SKILLS;

  const response = await makeAuthenticatedRequest<Skill[]>(url, {
    method: 'GET',
  });
  return response.data;
};

export const createSkill = async (data: SkillCreate): Promise<Skill> => {
  const response = await makeAuthenticatedRequest<Skill>(API_ENDPOINTS.PROFILE.SKILLS, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response.data;
};

export const getSkill = async (id: number): Promise<Skill> => {
  const response = await makeAuthenticatedRequest<Skill>(API_ENDPOINTS.PROFILE.SKILLS_BY_ID(id), {
    method: 'GET',
  });
  return response.data;
};

export const updateSkill = async (id: number, data: SkillUpdate): Promise<Skill> => {
  const response = await makeAuthenticatedRequest<Skill>(API_ENDPOINTS.PROFILE.SKILLS_BY_ID(id), {
    method: 'PUT',
    body: JSON.stringify(data),
  });
  return response.data;
};

export const deleteSkill = async (id: number): Promise<void> => {
  await makeAuthenticatedRequest<void>(API_ENDPOINTS.PROFILE.SKILLS_BY_ID(id), {
    method: 'DELETE',
  });
};

// ================== CERTIFICATIONS ==================

export const getCertifications = async (): Promise<Certification[]> => {
  const response = await makeAuthenticatedRequest<Certification[]>(
    API_ENDPOINTS.PROFILE.CERTIFICATIONS,
    {
      method: 'GET',
    }
  );
  return response.data;
};

export const createCertification = async (data: CertificationCreate): Promise<Certification> => {
  const response = await makeAuthenticatedRequest<Certification>(
    API_ENDPOINTS.PROFILE.CERTIFICATIONS,
    {
      method: 'POST',
      body: JSON.stringify(data),
    }
  );
  return response.data;
};

export const getCertification = async (id: number): Promise<Certification> => {
  const response = await makeAuthenticatedRequest<Certification>(
    API_ENDPOINTS.PROFILE.CERTIFICATIONS_BY_ID(id),
    {
      method: 'GET',
    }
  );
  return response.data;
};

export const updateCertification = async (
  id: number,
  data: CertificationUpdate
): Promise<Certification> => {
  const response = await makeAuthenticatedRequest<Certification>(
    API_ENDPOINTS.PROFILE.CERTIFICATIONS_BY_ID(id),
    {
      method: 'PUT',
      body: JSON.stringify(data),
    }
  );
  return response.data;
};

export const deleteCertification = async (id: number): Promise<void> => {
  await makeAuthenticatedRequest<void>(API_ENDPOINTS.PROFILE.CERTIFICATIONS_BY_ID(id), {
    method: 'DELETE',
  });
};

// ================== PROJECTS ==================

export const getProjects = async (): Promise<Project[]> => {
  const response = await makeAuthenticatedRequest<Project[]>(API_ENDPOINTS.PROFILE.PROJECTS, {
    method: 'GET',
  });
  return response.data;
};

export const createProject = async (data: ProjectCreate): Promise<Project> => {
  const response = await makeAuthenticatedRequest<Project>(API_ENDPOINTS.PROFILE.PROJECTS, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response.data;
};

export const getProject = async (id: number): Promise<Project> => {
  const response = await makeAuthenticatedRequest<Project>(
    API_ENDPOINTS.PROFILE.PROJECTS_BY_ID(id),
    {
      method: 'GET',
    }
  );
  return response.data;
};

export const updateProject = async (id: number, data: ProjectUpdate): Promise<Project> => {
  const response = await makeAuthenticatedRequest<Project>(
    API_ENDPOINTS.PROFILE.PROJECTS_BY_ID(id),
    {
      method: 'PUT',
      body: JSON.stringify(data),
    }
  );
  return response.data;
};

export const deleteProject = async (id: number): Promise<void> => {
  await makeAuthenticatedRequest<void>(API_ENDPOINTS.PROFILE.PROJECTS_BY_ID(id), {
    method: 'DELETE',
  });
};

// ================== JOB PREFERENCES ==================

export const getJobPreferences = async (): Promise<JobPreference> => {
  const response = await makeAuthenticatedRequest<JobPreference>(
    API_ENDPOINTS.PROFILE.JOB_PREFERENCES,
    {
      method: 'GET',
    }
  );
  return response.data;
};

export const createJobPreferences = async (data: JobPreferenceCreate): Promise<JobPreference> => {
  const response = await makeAuthenticatedRequest<JobPreference>(
    API_ENDPOINTS.PROFILE.JOB_PREFERENCES,
    {
      method: 'POST',
      body: JSON.stringify(data),
    }
  );
  return response.data;
};

export const updateJobPreferences = async (data: JobPreferenceUpdate): Promise<JobPreference> => {
  const response = await makeAuthenticatedRequest<JobPreference>(
    API_ENDPOINTS.PROFILE.JOB_PREFERENCES,
    {
      method: 'PUT',
      body: JSON.stringify(data),
    }
  );
  return response.data;
};

// ================== PROFILE COMPLETENESS ==================

export const getProfileCompleteness = async (): Promise<ProfileCompleteness> => {
  const response = await makeAuthenticatedRequest<ProfileCompleteness>(
    API_ENDPOINTS.PROFILE.COMPLETENESS,
    {
      method: 'GET',
    }
  );
  return response.data;
};
