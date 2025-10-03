import type { PageInfo } from '@/types/pages';

export const PAGE_INFO_MAP: Record<string, PageInfo> = {
  // Dashboard routes
  '/dashboard': {
    title: 'Dashboard',
    description: 'Welcome back! Monitor your activities and key metrics.',
  },
  '/': {
    title: 'Dashboard',
    description: 'Welcome back! Monitor your activities and key metrics.',
  },

  // Job routes
  '/jobs': {
    title: 'Jobs',
    description: 'Browse and apply for available job opportunities.',
  },
  '/positions': {
    title: 'Positions',
    description: 'Manage your job postings and recruitment activities.',
  },

  // User management routes
  '/candidates': {
    title: 'Candidates',
    description: 'Review and manage candidate applications and profiles.',
  },
  '/users': {
    title: 'Users',
    description: 'Manage system users and their permissions.',
  },

  // Communication routes
  '/messages': {
    title: 'Messages',
    description: 'Communicate with candidates, recruiters, and team members.',
  },

  // Scheduling routes
  '/calendar': {
    title: 'Calendar',
    description: 'Schedule and manage interviews and important events.',
  },
  '/interviews': {
    title: 'Interviews',
    description: 'Conduct and manage video interviews with candidates.',
  },

  // Document routes
  '/resumes': {
    title: 'Resume',
    description: 'Manage your resume and professional documents.',
  },

  // Company management routes
  '/companies': {
    title: 'Companies',
    description: 'Manage company profiles and organizational settings.',
  },

  // Account routes
  '/profile': {
    title: 'Profile',
    description: 'Manage your personal information and account settings.',
  },
  '/settings': {
    title: 'Settings',
    description: 'Configure your preferences and application settings.',
  },

  // Admin routes
  '/admin': {
    title: 'Admin Dashboard',
    description: 'Monitor and manage the entire platform.',
  },
  '/admin/dashboard': {
    title: 'System Admin Dashboard',
    description: 'Welcome back, System Admin! Monitor and manage the entire platform.',
  },
  '/admin/users': {
    title: 'User Management',
    description: 'Manage all system users and their access permissions.',
  },
  '/admin/companies': {
    title: 'Company Management',
    description: 'Oversee all companies and their organizational structures.',
  },
  '/admin/settings': {
    title: 'System Settings',
    description: 'Configure global system settings and preferences.',
  },
};

export function getPageInfo(pathname: string): PageInfo {
  // Try exact match first
  if (PAGE_INFO_MAP[pathname]) {
    return PAGE_INFO_MAP[pathname];
  }

  // Try to find a matching pattern
  for (const [path, info] of Object.entries(PAGE_INFO_MAP)) {
    if (pathname.startsWith(path) && path !== '/') {
      return info;
    }
  }

  // Default fallback
  return {
    title: 'Page',
    description: 'Navigate through the application.',
  };
}
