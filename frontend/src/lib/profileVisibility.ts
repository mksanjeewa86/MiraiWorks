/**
 * Profile section visibility utility
 * Determines which profile sections should be visible based on user role
 */

import { USER_ROLES, type UserRoleType } from '@/hooks/useUserRole';

export type ProfileSection =
  | 'basic_info'
  | 'work_experience'
  | 'education'
  | 'skills'
  | 'certifications'
  | 'projects'
  | 'job_preferences'
  | 'profile_picture'
  | 'completeness_indicator';

export interface ProfileVisibilityConfig {
  sections: {
    [K in ProfileSection]: boolean;
  };
  detailLevel: 'full' | 'moderate' | 'minimal';
}

/**
 * Get profile visibility configuration based on viewing user's role
 * @param viewerRole - The role of the user viewing the profile
 * @param isOwnProfile - Whether the user is viewing their own profile
 * @returns ProfileVisibilityConfig
 */
export function getProfileVisibility(
  viewerRole: string | null,
  isOwnProfile: boolean = false
): ProfileVisibilityConfig {
  // System Admin / Company Admin: Basic info only (even for own profile)
  if (viewerRole === USER_ROLES.SYSTEM_ADMIN || viewerRole === USER_ROLES.COMPANY_ADMIN) {
    return {
      detailLevel: isOwnProfile ? 'moderate' : 'full',
      sections: {
        basic_info: true,
        work_experience: false, // Admins don't need candidate sections
        education: false,
        skills: false,
        certifications: false,
        projects: false,
        job_preferences: false,
        profile_picture: true,
        completeness_indicator: false,
      },
    };
  }

  // Member role (Recruiter/Employer): Profile based on company context
  // Backend merged recruiter and employer into "member" role
  if (viewerRole === USER_ROLES.MEMBER || viewerRole === USER_ROLES.RECRUITER || viewerRole === USER_ROLES.EMPLOYER) {
    return {
      detailLevel: isOwnProfile ? 'full' : 'moderate',
      sections: {
        basic_info: true,
        work_experience: !isOwnProfile, // Only show when viewing others
        education: !isOwnProfile,
        skills: !isOwnProfile,
        certifications: !isOwnProfile,
        projects: false,
        job_preferences: false,
        profile_picture: true,
        completeness_indicator: false,
      },
    };
  }

  // Candidate role: Full profile with all candidate sections
  if (viewerRole === USER_ROLES.CANDIDATE || isOwnProfile) {
    return {
      detailLevel: 'full',
      sections: {
        basic_info: true,
        work_experience: true,
        education: true,
        skills: true,
        certifications: true,
        projects: true,
        job_preferences: isOwnProfile, // Only show for own profile
        profile_picture: true,
        completeness_indicator: isOwnProfile,
      },
    };
  }

  // Default (no role or unknown role): Minimal view
  return {
    detailLevel: 'minimal',
    sections: {
      basic_info: true,
      work_experience: false,
      education: false,
      skills: false,
      certifications: false,
      projects: false,
      job_preferences: false,
      profile_picture: true,
      completeness_indicator: false,
    },
  };
}

/**
 * Check if a specific section should be visible
 * @param section - The profile section to check
 * @param viewerRole - The role of the user viewing the profile
 * @param isOwnProfile - Whether the user is viewing their own profile
 * @returns boolean
 */
export function isSectionVisible(
  section: ProfileSection,
  viewerRole: string | null,
  isOwnProfile: boolean = false
): boolean {
  const config = getProfileVisibility(viewerRole, isOwnProfile);
  return config.sections[section];
}

/**
 * Get list of visible sections
 * @param viewerRole - The role of the user viewing the profile
 * @param isOwnProfile - Whether the user is viewing their own profile
 * @returns ProfileSection[]
 */
export function getVisibleSections(
  viewerRole: string | null,
  isOwnProfile: boolean = false
): ProfileSection[] {
  const config = getProfileVisibility(viewerRole, isOwnProfile);
  return (Object.keys(config.sections) as ProfileSection[]).filter(
    (section) => config.sections[section]
  );
}
