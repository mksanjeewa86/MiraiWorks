/**
 * Role-based color schemes for the sidebar
 * Each role has a unique color scheme to provide visual identity
 */

import type { ColorScheme } from '@/types/ui';

export const roleColorSchemes: Record<string, ColorScheme> = {
  admin: {
    // Deep purple/violet theme for super admins
    background: 'bg-violet-950',
    backgroundOverlay: 'bg-violet-900/30',
    border: 'border-violet-700/30',
    headerBackground: 'bg-violet-900/50',

    brandBackground: 'bg-violet-600',
    brandAccent: 'bg-violet-500',

    textPrimary: 'text-white',
    textSecondary: 'text-violet-200/80',

    buttonBorder: 'border-violet-600/30 hover:border-violet-500/50',
    buttonHover: 'hover:bg-violet-800/50',
    buttonActive: 'bg-violet-600',

    avatarBackground: 'bg-violet-600',
    avatarRing: 'ring-violet-600/50',

    activeIndicator: 'bg-violet-300',
    activeIndicatorShadow: 'shadow-violet-300/50',

    statusIndicator: 'bg-violet-400',
    statusIndicatorShadow: 'shadow-violet-400/50',
  },

  hr_manager: {
    // Deep blue theme for company admins
    background: 'bg-blue-950',
    backgroundOverlay: 'bg-blue-900/30',
    border: 'border-blue-700/30',
    headerBackground: 'bg-blue-900/50',

    brandBackground: 'bg-blue-600',
    brandAccent: 'bg-blue-500',

    textPrimary: 'text-white',
    textSecondary: 'text-blue-200/80',

    buttonBorder: 'border-blue-600/30 hover:border-blue-500/50',
    buttonHover: 'hover:bg-blue-800/50',
    buttonActive: 'bg-blue-600',

    avatarBackground: 'bg-blue-600',
    avatarRing: 'ring-blue-600/50',

    activeIndicator: 'bg-blue-300',
    activeIndicatorShadow: 'shadow-blue-300/50',

    statusIndicator: 'bg-blue-400',
    statusIndicatorShadow: 'shadow-blue-400/50',
  },

  recruiter: {
    // Deep emerald/green theme for company users
    background: 'bg-emerald-950',
    backgroundOverlay: 'bg-emerald-900/30',
    border: 'border-emerald-700/30',
    headerBackground: 'bg-emerald-900/50',

    brandBackground: 'bg-emerald-600',
    brandAccent: 'bg-emerald-500',

    textPrimary: 'text-white',
    textSecondary: 'text-emerald-200/80',

    buttonBorder: 'border-emerald-600/30 hover:border-emerald-500/50',
    buttonHover: 'hover:bg-emerald-800/50',
    buttonActive: 'bg-emerald-600',

    avatarBackground: 'bg-emerald-600',
    avatarRing: 'ring-emerald-600/50',

    activeIndicator: 'bg-emerald-300',
    activeIndicatorShadow: 'shadow-emerald-300/50',

    statusIndicator: 'bg-emerald-400',
    statusIndicatorShadow: 'shadow-emerald-400/50',
  },

  candidate: {
    // Deep cyan/teal theme for candidates
    background: 'bg-cyan-950',
    backgroundOverlay: 'bg-cyan-900/30',
    border: 'border-cyan-700/30',
    headerBackground: 'bg-cyan-900/50',

    brandBackground: 'bg-cyan-600',
    brandAccent: 'bg-cyan-500',

    textPrimary: 'text-white',
    textSecondary: 'text-cyan-200/80',

    buttonBorder: 'border-cyan-600/30 hover:border-cyan-500/50',
    buttonHover: 'hover:bg-cyan-800/50',
    buttonActive: 'bg-cyan-600',

    avatarBackground: 'bg-cyan-600',
    avatarRing: 'ring-cyan-600/50',

    activeIndicator: 'bg-cyan-300',
    activeIndicatorShadow: 'shadow-cyan-300/50',

    statusIndicator: 'bg-cyan-400',
    statusIndicatorShadow: 'shadow-cyan-400/50',
  },
};

// Default color scheme (fallback)
export const defaultColorScheme: ColorScheme = roleColorSchemes.candidate;

/**
 * Get the color scheme for a specific user role
 * @param userRoles - Array of user roles
 * @returns ColorScheme object for the user's primary role
 */
export function getRoleColorScheme(userRoles?: Array<{ role: { name: string } }>): ColorScheme {
  if (!userRoles || userRoles.length === 0) {
    return defaultColorScheme;
  }

  // Priority order for roles (highest to lowest)
  const rolePriority = ['admin', 'hr_manager', 'recruiter', 'candidate'];

  // Find the highest priority role
  for (const priority of rolePriority) {
    const hasRole = userRoles.some((userRole) => userRole.role.name === priority);
    if (hasRole && roleColorSchemes[priority]) {
      return roleColorSchemes[priority];
    }
  }

  // Fallback to the first role if no priority match
  const firstRole = userRoles[0]?.role?.name;
  return roleColorSchemes[firstRole] || defaultColorScheme;
}

/**
 * Get the role display name with proper formatting
 * @param userRoles - Array of user roles
 * @returns Formatted role name
 */
export function getRoleDisplayName(userRoles?: Array<{ role: { name: string } }>): string {
  if (!userRoles || userRoles.length === 0) {
    return 'USER';
  }

  const primaryRole = userRoles[0]?.role?.name || 'user';
  return primaryRole.replace('_', ' ').toUpperCase();
}

/**
 * Get the role-specific brand icon background
 * @param userRoles - Array of user roles
 * @returns CSS class for brand icon background
 */
export function getRoleBrandBackground(userRoles?: Array<{ role: { name: string } }>): string {
  const scheme = getRoleColorScheme(userRoles);
  return scheme.brandBackground;
}
