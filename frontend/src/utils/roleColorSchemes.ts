/**
 * Role-based color schemes for the sidebar
 * Each role has a unique color scheme to provide visual identity
 */

import type { ColorScheme } from '@/types/ui';

export const roleColorSchemes: Record<string, ColorScheme> = {
  system_admin: {
    // Deep red theme for system admins
    background: 'bg-red-950',
    backgroundOverlay: 'bg-red-900/30',
    border: 'border-red-700/30',
    headerBackground: 'bg-red-900/50',

    brandBackground: 'bg-red-600',
    brandAccent: 'bg-red-500',

    textPrimary: 'text-white',
    textSecondary: 'text-red-200/80',

    buttonBorder: 'border-red-600/30 hover:border-red-500/50',
    buttonHover: 'hover:bg-red-800/50',
    buttonActive: 'bg-red-600',

    avatarBackground: 'bg-red-600',
    avatarRing: 'ring-red-600/50',

    activeIndicator: 'bg-red-300',
    activeIndicatorShadow: 'shadow-red-300/50',

    statusIndicator: 'bg-red-400',
    statusIndicatorShadow: 'shadow-red-400/50',
  },

  admin: {
    // Deep green theme for company admins
    background: 'bg-green-950',
    backgroundOverlay: 'bg-green-900/30',
    border: 'border-green-700/30',
    headerBackground: 'bg-green-900/50',

    brandBackground: 'bg-green-600',
    brandAccent: 'bg-green-500',

    textPrimary: 'text-white',
    textSecondary: 'text-green-200/80',

    buttonBorder: 'border-green-600/30 hover:border-green-500/50',
    buttonHover: 'hover:bg-green-800/50',
    buttonActive: 'bg-green-600',

    avatarBackground: 'bg-green-600',
    avatarRing: 'ring-green-600/50',

    activeIndicator: 'bg-green-300',
    activeIndicatorShadow: 'shadow-green-300/50',

    statusIndicator: 'bg-green-400',
    statusIndicatorShadow: 'shadow-green-400/50',
  },

  member: {
    // Deep blue theme for members
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

  candidate: {
    // Deep orange theme for candidates
    background: 'bg-orange-950',
    backgroundOverlay: 'bg-orange-900/30',
    border: 'border-orange-700/30',
    headerBackground: 'bg-orange-900/50',

    brandBackground: 'bg-orange-600',
    brandAccent: 'bg-orange-500',

    textPrimary: 'text-white',
    textSecondary: 'text-orange-200/80',

    buttonBorder: 'border-orange-600/30 hover:border-orange-500/50',
    buttonHover: 'hover:bg-orange-800/50',
    buttonActive: 'bg-orange-600',

    avatarBackground: 'bg-orange-600',
    avatarRing: 'ring-orange-600/50',

    activeIndicator: 'bg-orange-300',
    activeIndicatorShadow: 'shadow-orange-300/50',

    statusIndicator: 'bg-orange-400',
    statusIndicatorShadow: 'shadow-orange-400/50',
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
  const rolePriority = ['system_admin', 'admin', 'member', 'candidate'];

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
