import { useMemo } from 'react';
import { useAuth } from '@/contexts/AuthContext';

// Role constants (must match backend role names exactly)
export const USER_ROLES = {
  CANDIDATE: 'candidate',
  RECRUITER: 'member', // Backend merged recruiter/employer into "member"
  EMPLOYER: 'member',  // Backend merged recruiter/employer into "member"
  MEMBER: 'member',    // New unified role
  COMPANY_ADMIN: 'admin',
  SYSTEM_ADMIN: 'system_admin',
} as const;

export type UserRoleType = (typeof USER_ROLES)[keyof typeof USER_ROLES];

/**
 * Hook for detecting user's primary role and role-based permissions
 */
export function useUserRole() {
  const { user } = useAuth();

  const roleInfo = useMemo(() => {
    if (!user || !user.roles || user.roles.length === 0) {
      return {
        primaryRole: null,
        roles: [],
        isCandidate: false,
        isRecruiter: false,
        isEmployer: false,
        isCompanyAdmin: false,
        isSystemAdmin: user?.is_admin || false,
        hasRole: (roleName: string) => false,
      };
    }

    const roleNames = user.roles.map((r) => r.role.name);
    const primaryRole = roleNames[0] || null;

    return {
      primaryRole,
      roles: roleNames,
      isCandidate: roleNames.includes(USER_ROLES.CANDIDATE),
      isRecruiter: roleNames.includes(USER_ROLES.RECRUITER),
      isEmployer: roleNames.includes(USER_ROLES.EMPLOYER),
      isCompanyAdmin: roleNames.includes(USER_ROLES.COMPANY_ADMIN),
      isSystemAdmin: user.is_admin || roleNames.includes(USER_ROLES.SYSTEM_ADMIN),
      hasRole: (roleName: string) => roleNames.includes(roleName),
    };
  }, [user]);

  return roleInfo;
}
