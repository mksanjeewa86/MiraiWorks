'use client';

import {
  LayoutDashboard,
  Briefcase,
  MessageSquare,
  Calendar,
  CheckSquare,
  Video,
  FileText,
  Settings,
  Users,
  Building2,
  X,
  ChevronLeft,
  User,
  Menu,
  GitBranch,
} from 'lucide-react';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import type { SidebarProps, NavItem } from '@/types/components';
import { getRoleColorScheme, getRoleDisplayName } from '@/utils/roleColorSchemes';

const navigationItems: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin', 'super_admin'],
    color: 'bg-blue-600',
    lightColor: 'bg-blue-500',
  },
  {
    name: 'Jobs',
    href: '/jobs',
    icon: Briefcase,
    roles: ['candidate'],
    color: 'bg-emerald-600',
    lightColor: 'bg-emerald-500',
  },
  {
    name: 'Positions',
    href: '/positions',
    icon: Briefcase,
    roles: ['employer', 'company_admin'],
    color: 'bg-emerald-600',
    lightColor: 'bg-emerald-500',
  },
  {
    name: 'Workflows',
    href: '/workflows',
    icon: GitBranch,
    roles: ['employer', 'company_admin'],
    color: 'bg-violet-600',
    lightColor: 'bg-violet-500',
  },
  {
    name: 'Candidates',
    href: '/candidates',
    icon: Users,
    roles: ['recruiter', 'company_admin'],
    color: 'bg-purple-600',
    lightColor: 'bg-purple-500',
  },
  {
    name: 'Messages',
    href: '/messages',
    icon: MessageSquare,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin', 'super_admin'],
    color: 'bg-orange-600',
    lightColor: 'bg-orange-500',
  },
  {
    name: 'Calendar',
    href: '/calendar',
    icon: Calendar,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin'],
    color: 'bg-red-600',
    lightColor: 'bg-red-500',
  },
  {
    name: 'Todos',
    href: '/todos',
    icon: CheckSquare,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin', 'super_admin'],
    color: 'bg-lime-600',
    lightColor: 'bg-lime-500',
  },
  {
    name: 'Interviews',
    href: '/interviews',
    icon: Video,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin'],
    color: 'bg-indigo-600',
    lightColor: 'bg-indigo-500',
  },
  {
    name: 'Resume',
    href: '/resumes',
    icon: FileText,
    roles: ['candidate'],
    color: 'bg-teal-600',
    lightColor: 'bg-teal-500',
  },
  {
    name: 'Profile',
    href: '/profile',
    icon: User,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin', 'super_admin'],
    color: 'bg-pink-600',
    lightColor: 'bg-pink-500',
  },
  {
    name: 'Companies',
    href: '/companies',
    icon: Building2,
    roles: ['super_admin'],
    color: 'bg-amber-600',
    lightColor: 'bg-amber-500',
  },
  {
    name: 'Users',
    href: '/users',
    icon: Users,
    roles: ['super_admin', 'company_admin'],
    color: 'bg-cyan-600',
    lightColor: 'bg-cyan-500',
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin', 'super_admin'],
    color: 'bg-gray-600',
    lightColor: 'bg-gray-500',
  },
];

export default function Sidebar({
  isOpen,
  isCollapsed,
  onClose,
  onToggleCollapse,
  isMobile,
}: SidebarProps) {
  const { user } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  // Get role-based color scheme
  const colorScheme = getRoleColorScheme(user?.roles);
  const roleDisplayName = getRoleDisplayName(user?.roles);

  // Filter navigation items based on user role
  const allVisibleItems = navigationItems.filter((item) => {
    if (!user?.roles?.length) return false;
    return user.roles.some((userRole) => item.roles.includes(userRole.role.name));
  });

  // Separate main navigation from settings/profile
  const mainNavItems = allVisibleItems.filter(
    (item) => item.name !== 'Settings' && item.name !== 'Profile'
  );
  const settingsItem = allVisibleItems.find((item) => item.name === 'Settings');
  const profileItem = allVisibleItems.find((item) => item.name === 'Profile');

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard' || pathname === '/';
    }
    return pathname?.startsWith(href) ?? false;
  };

  const sidebarClasses = `
    fixed left-0 z-50 border-r top-0 h-screen
    transition-all duration-300 ease-in-out
    ${isMobile ? 'w-64' : isCollapsed ? 'w-16' : 'w-64'}
    ${isMobile && !isOpen ? '-translate-x-full' : 'translate-x-0'}
    lg:translate-x-0
  `;

  return (
    <>
      {/* Mobile overlay */}
      {isMobile && isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`${sidebarClasses} ${colorScheme.background} ${colorScheme.border}`}
        data-testid="sidebar"
        data-collapsed={isCollapsed}
        data-mobile={isMobile}
        onClick={(e) => {
          // Prevent any accidental sidebar clicks from triggering collapse
          if (e.target === e.currentTarget) {
            e.stopPropagation();
          }
        }}
      >
        <div className="flex flex-col h-full relative overflow-hidden">
          {/* Subtle background overlay */}
          <div
            className={`absolute inset-0 ${colorScheme.backgroundOverlay} pointer-events-none`}
          />
          <div className="relative z-10 flex flex-col h-full overflow-hidden">
            {/* Header */}
            <div
              className={`flex items-center justify-between p-4 border-b ${colorScheme.border} ${colorScheme.headerBackground}`}
            >
              {!isCollapsed ? (
                <>
                  {/* MiraiWorks brand when expanded */}
                  <button
                    onClick={() => router.push('/')}
                    className={`flex items-center space-x-2 ${colorScheme.buttonHover} rounded-lg p-2 transition-colors duration-200`}
                  >
                    <div
                      className={`w-8 h-8 rounded-lg ${colorScheme.brandBackground} flex items-center justify-center`}
                    >
                      <span className={`${colorScheme.textPrimary} font-bold text-sm`}>M</span>
                    </div>
                    <span className={`text-lg font-bold ${colorScheme.textPrimary}`}>
                      MiraiWorks
                    </span>
                  </button>

                  {/* Collapse button when expanded */}
                  <div className="flex items-center space-x-2">
                    {!isMobile && (
                      <button
                        onClick={onToggleCollapse}
                        className={`p-2 rounded-lg transition-all duration-200 ${colorScheme.buttonHover} border ${colorScheme.buttonBorder} w-10 h-10 flex items-center justify-center`}
                        aria-label="Collapse sidebar"
                      >
                        <ChevronLeft
                          className={`h-4 w-4 ${colorScheme.textSecondary} hover:${colorScheme.textPrimary} flex-shrink-0`}
                        />
                      </button>
                    )}
                    {isMobile && (
                      <button
                        onClick={onClose}
                        className={`p-2 rounded-lg transition-all duration-200 lg:hidden ${colorScheme.buttonHover} border ${colorScheme.buttonBorder}`}
                        aria-label="Close sidebar"
                      >
                        <X
                          className={`h-4 w-4 ${colorScheme.textSecondary} hover:${colorScheme.textPrimary}`}
                        />
                      </button>
                    )}
                  </div>
                </>
              ) : (
                <>
                  {/* Hamburger menu when collapsed */}
                  <button
                    onClick={onToggleCollapse}
                    className={`p-2 rounded-lg transition-all duration-200 ${colorScheme.buttonHover} border ${colorScheme.buttonBorder} w-10 h-10 flex items-center justify-center mx-auto`}
                    aria-label="Expand sidebar"
                  >
                    <Menu
                      className={`h-4 w-4 ${colorScheme.textSecondary} hover:${colorScheme.textPrimary} flex-shrink-0`}
                    />
                  </button>
                </>
              )}
            </div>

            {/* Navigation */}
            <nav
              className={`flex-1 flex flex-col overflow-hidden ${isCollapsed ? 'px-2 py-4 items-center' : 'p-4'} min-h-0`}
            >
              {/* Main navigation items */}
              <div
                className={`${isCollapsed ? 'flex flex-col items-center space-y-3' : 'space-y-3'}`}
              >
                {mainNavItems.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.href);

                  return (
                    <button
                      key={item.name}
                      type="button"
                      onClick={(e) => {
                        // Prevent any bubbling and default behavior
                        e.stopPropagation();
                        e.preventDefault();

                        // Navigate immediately
                        router.push(item.href);

                        // Close mobile sidebar if open
                        if (isMobile) {
                          onClose();
                        }
                      }}
                      className={`
                      group flex items-center transition-all duration-300 transform hover:scale-105 text-sm font-medium relative cursor-pointer w-full border-0 bg-transparent
                      ${
                        isCollapsed
                          ? 'p-2 justify-center hover:scale-105 w-10 h-10 rounded-lg'
                          : 'px-4 py-2 h-10 rounded-xl'
                      }
                      ${
                        active
                          ? `${colorScheme.buttonActive} ${colorScheme.textPrimary} shadow-lg shadow-black/20`
                          : `${colorScheme.textSecondary} ${colorScheme.buttonHover} hover:${colorScheme.textPrimary} border ${colorScheme.buttonBorder}`
                      }
                    `}
                      title={isCollapsed ? item.name : undefined}
                    >
                      <div
                        className={`
                      flex-shrink-0 transition-all duration-300 transform flex items-center justify-center
                      ${isCollapsed ? 'w-8 h-8 rounded-md min-w-8' : 'p-2 rounded-lg'}
                      ${
                        active
                          ? `bg-white/20 ${isCollapsed ? 'bg-white/30 shadow-md' : ''}`
                          : `${colorScheme.brandAccent} group-hover:scale-110 group-hover:rotate-6`
                      }
                    `}
                      >
                        <Icon
                          className={`
                        h-4 w-4 transition-all duration-300 transform flex-shrink-0
                        ${
                          active
                            ? `${colorScheme.textPrimary} animate-pulse`
                            : `${colorScheme.textPrimary} group-hover:${colorScheme.textPrimary} group-hover:scale-110 group-hover:-rotate-12`
                        }
                      `}
                        />
                      </div>

                      {!isCollapsed && (
                        <span className="ml-3 truncate font-semibold">{item.name}</span>
                      )}

                      {/* Active indicator with glow effect */}
                      {active && !isCollapsed && (
                        <div className="ml-auto">
                          <div
                            className={`w-2 h-2 rounded-full ${colorScheme.activeIndicator} shadow-lg ${colorScheme.activeIndicatorShadow} animate-pulse`}
                          />
                        </div>
                      )}

                      {/* Hover effect indicator */}
                      {!active && !isCollapsed && (
                        <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                          <div
                            className={`w-1.5 h-1.5 rounded-full ${colorScheme.activeIndicator}/60`}
                          />
                        </div>
                      )}

                      {/* Collapsed hover indicator */}
                      {!active && isCollapsed && (
                        <div className="absolute -right-0.5 -top-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                          <div
                            className={`w-2 h-2 rounded-full ${colorScheme.activeIndicator}/60`}
                          />
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>

              {/* Bottom navigation items */}
              <div
                className={`${isCollapsed ? 'flex flex-col items-center space-y-3' : 'space-y-3'} mt-auto`}
              >
                {/* Profile */}
                {profileItem && (
                  <button
                    key={profileItem.name}
                    type="button"
                    onClick={(e) => {
                      // Prevent any bubbling and default behavior
                      e.stopPropagation();
                      e.preventDefault();

                      // Navigate immediately
                      router.push(profileItem.href);

                      // Close mobile sidebar if open
                      if (isMobile) {
                        onClose();
                      }
                    }}
                    className={`
                    group flex items-center transition-all duration-300 transform hover:scale-105 text-sm font-medium relative cursor-pointer w-full border-0 bg-transparent
                    ${
                      isCollapsed
                        ? 'p-2 justify-center hover:scale-105 w-10 h-10 rounded-lg'
                        : 'px-4 py-2 h-10 rounded-xl'
                    }
                    ${
                      isActive(profileItem.href)
                        ? `${colorScheme.buttonActive} ${colorScheme.textPrimary} shadow-lg shadow-black/20`
                        : `${colorScheme.textSecondary} ${colorScheme.buttonHover} hover:${colorScheme.textPrimary} border ${colorScheme.buttonBorder}`
                    }
                  `}
                    title={isCollapsed ? profileItem.name : undefined}
                  >
                    <div
                      className={`
                    flex-shrink-0 transition-all duration-300 transform flex items-center justify-center
                    ${isCollapsed ? 'w-8 h-8 rounded-md min-w-8' : 'p-2 rounded-lg'}
                    ${
                      isActive(profileItem.href)
                        ? `bg-white/20 ${isCollapsed ? 'bg-white/30 shadow-md' : ''}`
                        : `${colorScheme.brandAccent} group-hover:scale-110 group-hover:rotate-6`
                    }
                  `}
                    >
                      <profileItem.icon
                        className={`
                      h-4 w-4 transition-all duration-300 transform flex-shrink-0
                      ${
                        isActive(profileItem.href)
                          ? `${colorScheme.textPrimary} animate-pulse`
                          : `${colorScheme.textPrimary} group-hover:${colorScheme.textPrimary} group-hover:scale-110 group-hover:-rotate-12`
                      }
                    `}
                      />
                    </div>

                    {!isCollapsed && (
                      <span className="ml-3 truncate font-semibold">{profileItem.name}</span>
                    )}

                    {/* Active indicator with glow effect */}
                    {isActive(profileItem.href) && !isCollapsed && (
                      <div className="ml-auto">
                        <div
                          className={`w-2 h-2 rounded-full ${colorScheme.activeIndicator} shadow-lg ${colorScheme.activeIndicatorShadow} animate-pulse`}
                        />
                      </div>
                    )}

                    {/* Hover effect indicator */}
                    {!isActive(profileItem.href) && !isCollapsed && (
                      <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <div
                          className={`w-1.5 h-1.5 rounded-full ${colorScheme.activeIndicator}/60`}
                        />
                      </div>
                    )}

                    {/* Collapsed hover indicator */}
                    {!isActive(profileItem.href) && isCollapsed && (
                      <div className="absolute -right-0.5 -top-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <div className={`w-2 h-2 rounded-full ${colorScheme.activeIndicator}/60`} />
                      </div>
                    )}
                  </button>
                )}

                {/* Settings */}
                {settingsItem && (
                  <button
                    key={settingsItem.name}
                    type="button"
                    onClick={(e) => {
                      // Prevent any bubbling and default behavior
                      e.stopPropagation();
                      e.preventDefault();

                      // Navigate immediately
                      router.push(settingsItem.href);

                      // Close mobile sidebar if open
                      if (isMobile) {
                        onClose();
                      }
                    }}
                    className={`
                    group flex items-center transition-all duration-300 transform hover:scale-105 text-sm font-medium relative cursor-pointer w-full border-0 bg-transparent
                    ${
                      isCollapsed
                        ? 'p-2 justify-center hover:scale-105 w-10 h-10 rounded-lg'
                        : 'px-4 py-2 h-10 rounded-xl'
                    }
                    ${
                      isActive(settingsItem.href)
                        ? `${colorScheme.buttonActive} ${colorScheme.textPrimary} shadow-lg shadow-black/20`
                        : `${colorScheme.textSecondary} ${colorScheme.buttonHover} hover:${colorScheme.textPrimary} border ${colorScheme.buttonBorder}`
                    }
                  `}
                    title={isCollapsed ? settingsItem.name : undefined}
                  >
                    <div
                      className={`
                    flex-shrink-0 transition-all duration-300 transform flex items-center justify-center
                    ${isCollapsed ? 'w-8 h-8 rounded-md min-w-8' : 'p-2 rounded-lg'}
                    ${
                      isActive(settingsItem.href)
                        ? `bg-white/20 ${isCollapsed ? 'bg-white/30 shadow-md' : ''}`
                        : `${colorScheme.brandAccent} group-hover:scale-110 group-hover:rotate-6`
                    }
                  `}
                    >
                      <settingsItem.icon
                        className={`
                      h-4 w-4 transition-all duration-300 transform flex-shrink-0
                      ${
                        isActive(settingsItem.href)
                          ? `${colorScheme.textPrimary} animate-pulse`
                          : `${colorScheme.textPrimary} group-hover:${colorScheme.textPrimary} group-hover:scale-110 group-hover:-rotate-12`
                      }
                    `}
                      />
                    </div>

                    {!isCollapsed && (
                      <span className="ml-3 truncate font-semibold">{settingsItem.name}</span>
                    )}

                    {/* Active indicator with glow effect */}
                    {isActive(settingsItem.href) && !isCollapsed && (
                      <div className="ml-auto">
                        <div
                          className={`w-2 h-2 rounded-full ${colorScheme.activeIndicator} shadow-lg ${colorScheme.activeIndicatorShadow} animate-pulse`}
                        />
                      </div>
                    )}

                    {/* Hover effect indicator */}
                    {!isActive(settingsItem.href) && !isCollapsed && (
                      <div className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <div
                          className={`w-1.5 h-1.5 rounded-full ${colorScheme.activeIndicator}/60`}
                        />
                      </div>
                    )}

                    {/* Collapsed hover indicator */}
                    {!isActive(settingsItem.href) && isCollapsed && (
                      <div className="absolute -right-0.5 -top-0.5 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <div className={`w-2 h-2 rounded-full ${colorScheme.activeIndicator}/60`} />
                      </div>
                    )}
                  </button>
                )}
              </div>
            </nav>

            {/* User info (collapsed state) */}
            {isCollapsed && user && (
              <div
                className={`px-2 py-4 border-t ${colorScheme.border} ${colorScheme.headerBackground} flex justify-center`}
              >
                <div
                  className={`w-10 h-10 rounded-full ${colorScheme.avatarBackground} flex items-center justify-center ${colorScheme.textPrimary} text-sm font-bold shadow-lg ring-2 ${colorScheme.avatarRing} flex-shrink-0`}
                >
                  {user.first_name?.[0] || user.email[0].toUpperCase()}
                </div>
              </div>
            )}

            {/* User info (expanded state) */}
            {!isCollapsed && user && (
              <div className={`p-4 border-t ${colorScheme.border} ${colorScheme.headerBackground}`}>
                <div
                  className={`flex items-center space-x-3 p-3 rounded-xl ${colorScheme.headerBackground} border ${colorScheme.buttonBorder} ${colorScheme.buttonHover} transition-all duration-200`}
                >
                  <div
                    className={`w-12 h-12 rounded-full ${colorScheme.avatarBackground} flex items-center justify-center ${colorScheme.textPrimary} text-sm font-bold shadow-lg ring-2 ${colorScheme.avatarRing}`}
                  >
                    {user.first_name?.[0] || user.email[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-semibold ${colorScheme.textPrimary} truncate`}>
                      {`${user.first_name} ${user.last_name}`.trim() || 'User'}
                    </p>
                    <p className={`text-xs ${colorScheme.textSecondary} truncate font-medium`}>
                      {roleDisplayName}
                    </p>
                  </div>
                  <div
                    className={`w-2 h-2 rounded-full ${colorScheme.statusIndicator} shadow-lg ${colorScheme.statusIndicatorShadow} animate-pulse`}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
