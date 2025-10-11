'use client';

import {
  LayoutDashboard,
  Briefcase,
  MessageSquare,
  Calendar,
  CheckSquare,
  Video,
  FileText,
  Users,
  Building2,
  X,
  ChevronLeft,
  Menu,
  GitBranch,
  BookOpen,
} from 'lucide-react';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useMySubscription } from '@/hooks/useSubscription';
import type { SidebarProps, NavItem } from '@/types/components';
import { getRoleColorScheme, getRoleDisplayName } from '@/utils/roleColorSchemes';
import { useTranslations, useLocale } from 'next-intl';
import { ROUTES } from '@/routes/config';
import { useLocaleRouter } from '@/hooks/useLocaleRouter';

const navigationItems: NavItem[] = [
  {
    name: 'dashboard',
    href: ROUTES.DASHBOARD,
    icon: LayoutDashboard,
    roles: ['candidate', 'member', 'admin', 'system_admin'],
    color: 'bg-blue-600',
    lightColor: 'bg-blue-500',
  },
  {
    name: 'jobs',
    href: ROUTES.JOBS.BASE,
    icon: Briefcase,
    roles: ['candidate', 'system_admin'],
    color: 'bg-emerald-600',
    lightColor: 'bg-emerald-500',
  },
  {
    name: 'positions',
    href: ROUTES.POSITIONS.BASE,
    icon: Briefcase,
    roles: ['member', 'admin', 'system_admin'],
    color: 'bg-emerald-600',
    lightColor: 'bg-emerald-500',
  },
  {
    name: 'workflows',
    href: ROUTES.WORKFLOWS.BASE,
    icon: GitBranch,
    roles: ['member', 'admin', 'system_admin'],
    color: 'bg-violet-600',
    lightColor: 'bg-violet-500',
  },
  {
    name: 'candidates',
    href: ROUTES.CANDIDATES.BASE,
    icon: Users,
    roles: ['member', 'admin', 'system_admin'],
    color: 'bg-purple-600',
    lightColor: 'bg-purple-500',
  },
  {
    name: 'messages',
    href: ROUTES.MESSAGES.BASE,
    icon: MessageSquare,
    roles: ['candidate', 'member', 'admin', 'system_admin'],
    color: 'bg-orange-600',
    lightColor: 'bg-orange-500',
  },
  {
    name: 'calendar',
    href: ROUTES.CALENDAR.BASE,
    icon: Calendar,
    roles: ['candidate', 'member', 'admin', 'system_admin'],
    color: 'bg-red-600',
    lightColor: 'bg-red-500',
  },
  {
    name: 'todos',
    href: ROUTES.TODOS.BASE,
    icon: CheckSquare,
    roles: ['candidate', 'member', 'admin', 'system_admin'],
    color: 'bg-lime-600',
    lightColor: 'bg-lime-500',
  },
  {
    name: 'interviews',
    href: ROUTES.INTERVIEWS.BASE,
    icon: Video,
    roles: ['candidate', 'member', 'admin', 'system_admin'],
    color: 'bg-indigo-600',
    lightColor: 'bg-indigo-500',
  },
  {
    name: 'resume',
    href: ROUTES.RESUMES.BASE,
    icon: FileText,
    roles: ['candidate', 'system_admin'],
    color: 'bg-teal-600',
    lightColor: 'bg-teal-500',
  },
  {
    name: 'exams',
    href: ROUTES.EXAMS.BASE,
    icon: BookOpen,
    roles: ['candidate', 'member', 'admin', 'system_admin'],
    color: 'bg-rose-600',
    lightColor: 'bg-rose-500',
    requiredFeature: 'view_exams', // Requires exam feature
  },
  {
    name: 'companies',
    href: ROUTES.COMPANIES.BASE,
    icon: Building2,
    roles: ['admin', 'system_admin'],
    color: 'bg-amber-600',
    lightColor: 'bg-amber-500',
  },
  {
    name: 'users',
    href: ROUTES.USERS.BASE,
    icon: Users,
    roles: ['admin', 'system_admin'],
    color: 'bg-cyan-600',
    lightColor: 'bg-cyan-500',
  },
  {
    name: 'adminExams',
    href: ROUTES.ADMIN.EXAMS.BASE,
    icon: BookOpen,
    roles: ['admin', 'system_admin'],
    color: 'bg-fuchsia-600',
    lightColor: 'bg-fuchsia-500',
    requiredFeature: 'exam_management', // Requires exam management feature
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
  const router = useLocaleRouter();
  const t = useTranslations('common.nav');
  const locale = useLocale();

  // Only fetch subscription for company users (not candidates)
  const isCandidate = user?.roles?.some((userRole) => userRole.role.name === 'candidate');
  const { subscription } = useMySubscription({
    enabled: !isCandidate // Only run for non-candidate users
  });

  // Get role-based color scheme
  const colorScheme = getRoleColorScheme(user?.roles);
  const roleDisplayName = getRoleDisplayName(user?.roles);

  // Get available feature names from subscription
  const availableFeatures = subscription?.plan?.features?.map(f => f.name) || [];

  // Filter navigation items based on user role AND feature access
  const allVisibleItems = navigationItems.filter((item) => {
    if (!user?.roles?.length) return false;

    // Check role access
    const hasRoleAccess = user.roles.some((userRole) => item.roles.includes(userRole.role.name));
    if (!hasRoleAccess) return false;

    // Check feature access if requiredFeature is specified
    if (item.requiredFeature) {
      // System admins and candidates bypass feature checks
      const isSystemAdmin = user.roles.some((userRole) => userRole.role.name === 'system_admin');
      const isCandidate = user.roles.some((userRole) => userRole.role.name === 'candidate');

      if (!isSystemAdmin && !isCandidate) {
        // For company users (members/admins), check subscription features
        return availableFeatures.includes(item.requiredFeature);
      }
    }

    return true;
  });

  // Use all visible items in the same navigation section
  const mainNavItems = allVisibleItems;

  const isActive = (href: string) => {
    const localeHref = `/${locale}${href}`;
    if (href === ROUTES.DASHBOARD) {
      return pathname === localeHref || pathname === `/${locale}` || pathname === `/${locale}/`;
    }
    return pathname?.startsWith(localeHref) ?? false;
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
                    onClick={() => router.push(ROUTES.HOME)}
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
              className={`flex-1 flex flex-col min-h-0 ${isCollapsed ? 'px-2' : 'px-4'}`}
            >
              {/* Scrollable main navigation items */}
              <div
                className={`flex-1 overflow-y-auto overflow-x-hidden py-4 ${
                  isCollapsed ? 'scrollbar-hide' : 'scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-transparent hover:scrollbar-thumb-gray-500'
                }`}
                style={{
                  scrollbarWidth: isCollapsed ? 'none' : 'thin',
                  msOverflowStyle: isCollapsed ? 'none' : 'auto',
                }}
              >
                <div
                  className={`${isCollapsed ? 'flex flex-col items-center space-y-2' : 'space-y-2'}`}
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

                        // Navigate immediately (locale prefix added automatically by useLocaleRouter)
                        router.push(item.href);

                        // Close mobile sidebar if open
                        if (isMobile) {
                          onClose();
                        }
                      }}
                      className={`
                      group flex items-center transition-all duration-200 text-sm font-medium relative cursor-pointer w-full border-0 bg-transparent flex-shrink-0
                      ${
                        isCollapsed
                          ? 'p-2 justify-center w-10 h-10 rounded-lg hover:scale-105'
                          : 'px-3 py-2.5 h-11 rounded-xl hover:translate-x-1'
                      }
                      ${
                        active
                          ? `${colorScheme.buttonActive} ${colorScheme.textPrimary} shadow-lg shadow-black/10`
                          : `${colorScheme.textSecondary} ${colorScheme.buttonHover} hover:${colorScheme.textPrimary} border ${colorScheme.buttonBorder}`
                      }
                    `}
                      title={isCollapsed ? t(item.name) : undefined}
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
                        <span className="ml-3 truncate font-semibold">{t(item.name)}</span>
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
