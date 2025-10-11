/**
 * User-type based color schemes for the sidebar
 * Matches the Choice Cards colors from the landing page
 * - Employer: Purple/Pink theme
 * - Recruiter: Blue/Cyan theme
 * - Candidate: Green/Teal theme
 */

import type { ColorScheme } from '@/types/ui';

export const userTypeColorSchemes: Record<string, ColorScheme> = {
  employer: {
    // Purple/Pink theme for employers (matching landing page)
    background: 'bg-gradient-to-br from-purple-950 via-purple-900 to-pink-950',
    backgroundOverlay: 'bg-gradient-to-br from-purple-900/30 to-pink-900/30',
    border: 'border-purple-700/30',
    headerBackground: 'bg-purple-900/50',

    brandBackground: 'bg-gradient-to-br from-purple-600 to-pink-600',
    brandAccent: 'bg-gradient-to-br from-purple-500 to-pink-500',

    textPrimary: 'text-white',
    textSecondary: 'text-purple-200/80',

    buttonBorder: 'border-purple-600/30 hover:border-purple-400/50',
    buttonHover: 'hover:bg-gradient-to-br hover:from-purple-800/50 hover:to-pink-800/50',
    buttonActive: 'bg-gradient-to-br from-purple-600 to-pink-600',

    avatarBackground: 'bg-gradient-to-br from-purple-600 to-pink-600',
    avatarRing: 'ring-purple-500/50',

    activeIndicator: 'bg-purple-300',
    activeIndicatorShadow: 'shadow-purple-300/50',

    statusIndicator: 'bg-purple-400',
    statusIndicatorShadow: 'shadow-purple-400/50',
  },

  recruiter: {
    // Blue/Cyan theme for recruiters (matching landing page)
    background: 'bg-gradient-to-br from-blue-950 via-blue-900 to-cyan-950',
    backgroundOverlay: 'bg-gradient-to-br from-blue-900/30 to-cyan-900/30',
    border: 'border-blue-700/30',
    headerBackground: 'bg-blue-900/50',

    brandBackground: 'bg-gradient-to-br from-blue-600 to-cyan-600',
    brandAccent: 'bg-gradient-to-br from-blue-500 to-cyan-500',

    textPrimary: 'text-white',
    textSecondary: 'text-blue-200/80',

    buttonBorder: 'border-blue-600/30 hover:border-blue-400/50',
    buttonHover: 'hover:bg-gradient-to-br hover:from-blue-800/50 hover:to-cyan-800/50',
    buttonActive: 'bg-gradient-to-br from-blue-600 to-cyan-600',

    avatarBackground: 'bg-gradient-to-br from-blue-600 to-cyan-600',
    avatarRing: 'ring-blue-500/50',

    activeIndicator: 'bg-blue-300',
    activeIndicatorShadow: 'shadow-blue-300/50',

    statusIndicator: 'bg-blue-400',
    statusIndicatorShadow: 'shadow-blue-400/50',
  },

  candidate: {
    // Green/Teal theme for candidates (matching landing page)
    background: 'bg-gradient-to-br from-green-950 via-green-900 to-teal-950',
    backgroundOverlay: 'bg-gradient-to-br from-green-900/30 to-teal-900/30',
    border: 'border-green-700/30',
    headerBackground: 'bg-green-900/50',

    brandBackground: 'bg-gradient-to-br from-green-600 to-teal-600',
    brandAccent: 'bg-gradient-to-br from-green-500 to-teal-500',

    textPrimary: 'text-white',
    textSecondary: 'text-green-200/80',

    buttonBorder: 'border-green-600/30 hover:border-green-400/50',
    buttonHover: 'hover:bg-gradient-to-br hover:from-green-800/50 hover:to-teal-800/50',
    buttonActive: 'bg-gradient-to-br from-green-600 to-teal-600',

    avatarBackground: 'bg-gradient-to-br from-green-600 to-teal-600',
    avatarRing: 'ring-green-500/50',

    activeIndicator: 'bg-green-300',
    activeIndicatorShadow: 'shadow-green-300/50',

    statusIndicator: 'bg-green-400',
    statusIndicatorShadow: 'shadow-green-400/50',
  },
};

// Default color scheme (fallback)
export const defaultColorScheme: ColorScheme = userTypeColorSchemes.candidate;

/**
 * Map database roles to user types
 * @param userRoles - Array of user roles
 * @returns User type: 'employer', 'recruiter', or 'candidate'
 */
function mapRoleToUserType(userRoles?: Array<{ role: { name: string } }>): 'employer' | 'recruiter' | 'candidate' {
  if (!userRoles || userRoles.length === 0) {
    return 'candidate';
  }

  // Check if user has candidate role
  const isCandidate = userRoles.some((userRole) => userRole.role.name === 'candidate');
  if (isCandidate) {
    return 'candidate';
  }

  // Check if user has employer roles (admin or system_admin)
  const isEmployer = userRoles.some((userRole) =>
    userRole.role.name === 'admin' || userRole.role.name === 'system_admin'
  );
  if (isEmployer) {
    return 'employer';
  }

  // Default to recruiter for members and other roles
  return 'recruiter';
}

/**
 * Get the color scheme for a specific user based on their type
 * @param userRoles - Array of user roles
 * @returns ColorScheme object for the user's type
 */
export function getRoleColorScheme(userRoles?: Array<{ role: { name: string } }>): ColorScheme {
  const userType = mapRoleToUserType(userRoles);
  return userTypeColorSchemes[userType] || defaultColorScheme;
}

/**
 * Get the user type display name
 * @param userRoles - Array of user roles
 * @returns User type display name: 'Employer', 'Recruiter', or 'Candidate'
 */
export function getRoleDisplayName(userRoles?: Array<{ role: { name: string } }>): string {
  const userType = mapRoleToUserType(userRoles);

  switch (userType) {
    case 'employer':
      return 'Employer';
    case 'recruiter':
      return 'Recruiter';
    case 'candidate':
      return 'Candidate';
    default:
      return 'User';
  }
}

/**
 * Get the user type-specific brand icon background
 * @param userRoles - Array of user roles
 * @returns CSS class for brand icon background
 */
export function getRoleBrandBackground(userRoles?: Array<{ role: { name: string } }>): string {
  const scheme = getRoleColorScheme(userRoles);
  return scheme.brandBackground;
}
