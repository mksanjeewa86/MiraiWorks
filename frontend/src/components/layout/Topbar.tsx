'use client';

import NotificationDropdown from '@/components/notifications/NotificationDropdown';
import { useAuth } from '@/contexts/AuthContext';
import type { TopbarProps } from '@/types/components';
import { LogOut, Settings, User, ChevronDown } from 'lucide-react';
import { useEffect, useState, useRef } from 'react';
import { ROUTES } from '@/routes/config';
import { useLocaleRouter } from '@/hooks/useLocaleRouter';
import { getRoleColorScheme } from '@/utils/roleColorSchemes';

export default function Topbar({ pageTitle, pageDescription }: TopbarProps = {}) {
  const { user, logout } = useAuth();
  const router = useLocaleRouter();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Get color scheme based on user role
  const colorScheme = getRoleColorScheme(user?.roles);

  // Listen for sidebar state from localStorage
  useEffect(() => {
    const checkSidebarState = () => {
      const saved = localStorage.getItem('sidebarCollapsed');
      setSidebarCollapsed(saved === 'true');
    };

    checkSidebarState();

    // Listen for storage changes
    window.addEventListener('storage', checkSidebarState);

    // Custom event for immediate updates
    window.addEventListener('sidebarStateChanged', checkSidebarState);

    return () => {
      window.removeEventListener('storage', checkSidebarState);
      window.removeEventListener('sidebarStateChanged', checkSidebarState);
    };
  }, []);

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getUserDisplayName = () => {
    if (!user) return 'User';
    return `${user.first_name} ${user.last_name}`.trim() || user.email;
  };

  const getUserInitials = () => {
    if (!user) return 'U';
    const first = user.first_name?.[0] || '';
    const last = user.last_name?.[0] || '';
    return (first + last).toUpperCase() || user.email[0].toUpperCase();
  };

  const handleProfileClick = () => {
    router.push(ROUTES.PROFILE);
  };

  const handleSettingsClick = () => {
    router.push(ROUTES.SETTINGS);
  };

  return (
    <header
      className="sticky top-0 z-40 w-full border-b"
      style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)' }}
    >
      <div
        className={`flex items-center justify-between py-3 px-4 transition-all duration-300 ${sidebarCollapsed ? 'lg:ml-16' : 'lg:ml-64'}`}
      >
        {/* Left side - Page Info */}
        <div className="flex flex-col">
          {pageTitle && (
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">{pageTitle}</h1>
          )}
          {pageDescription && (
            <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">{pageDescription}</p>
          )}
        </div>

        {/* Center - Empty space */}
        <div className="flex-1"></div>

        {/* Right side */}
        <div className="flex items-center space-x-3">
          {/* Notifications */}
          <NotificationDropdown />

          {/* User menu */}
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors group"
              aria-label="User menu"
              data-testid="user-menu"
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${colorScheme.brandAccent} shadow-md`}
              >
                {getUserInitials()}
              </div>
              <span className="hidden md:inline text-sm font-medium text-gray-700 dark:text-gray-200">
                {getUserDisplayName()}
              </span>
              <ChevronDown className={`h-4 w-4 text-gray-500 dark:text-gray-400 transition-transform ${isUserMenuOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown */}
            {isUserMenuOpen && (
              <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                {/* Header */}
                <div className={`relative overflow-hidden ${colorScheme.background}`}>
                  {/* Background Overlay */}
                  <div className={`absolute inset-0 ${colorScheme.backgroundOverlay}`}></div>

                  {/* Animated Pattern Overlay */}
                  <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djQtNCAzNmgtNHY0LTQtMzZoNHYzNnoiLz48L2c+PC9nPjwvc3ZnPg==')] opacity-30"></div>

                  {/* Content */}
                  <div className="relative p-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-14 h-14 ${colorScheme.brandAccent} rounded-xl flex items-center justify-center shadow-lg`}>
                        <span className={`text-xl font-bold ${colorScheme.textPrimary}`}>
                          {getUserInitials()}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`text-base font-bold ${colorScheme.textPrimary} truncate`}>
                          {getUserDisplayName()}
                        </p>
                        <p className={`text-xs ${colorScheme.textSecondary} truncate`}>
                          {user?.email}
                        </p>
                        {user?.roles && user.roles.length > 0 && (
                          <div className="mt-1 flex flex-wrap gap-1">
                            {user.roles.slice(0, 2).map((userRole, index) => (
                              <span
                                key={index}
                                className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colorScheme.activeIndicator} text-white shadow-sm`}
                              >
                                {userRole.role.name}
                              </span>
                            ))}
                            {user.roles.length > 2 && (
                              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colorScheme.buttonHover} ${colorScheme.textSecondary}`}>
                                +{user.roles.length - 2}
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Menu Items */}
                <div className="p-2">
                  <button
                    onClick={() => {
                      handleProfileClick();
                      setIsUserMenuOpen(false);
                    }}
                    className={`w-full flex items-center gap-3 px-4 py-3 ${colorScheme.buttonHover} rounded-xl transition-all duration-200 group`}
                  >
                    <div className={`w-9 h-9 ${colorScheme.brandAccent} rounded-lg flex items-center justify-center transition-transform group-hover:scale-110`}>
                      <User className={`h-4 w-4 ${colorScheme.textPrimary}`} />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">Profile</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">View and edit your profile</p>
                    </div>
                  </button>

                  <button
                    onClick={() => {
                      handleSettingsClick();
                      setIsUserMenuOpen(false);
                    }}
                    className={`w-full flex items-center gap-3 px-4 py-3 mt-1 ${colorScheme.buttonHover} rounded-xl transition-all duration-200 group`}
                  >
                    <div className={`w-9 h-9 ${colorScheme.brandAccent} rounded-lg flex items-center justify-center transition-transform group-hover:scale-110`}>
                      <Settings className={`h-4 w-4 ${colorScheme.textPrimary}`} />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">Settings</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">Manage your preferences</p>
                    </div>
                  </button>

                  <div className="h-px bg-gray-200 dark:bg-gray-700 my-2"></div>

                  <button
                    onClick={() => {
                      logout();
                      setIsUserMenuOpen(false);
                    }}
                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-all duration-200 group"
                    data-testid="logout-button"
                  >
                    <div className="w-9 h-9 bg-red-100 dark:bg-red-900/30 rounded-lg flex items-center justify-center transition-transform group-hover:scale-110">
                      <LogOut className="h-4 w-4 text-red-600 dark:text-red-400" />
                    </div>
                    <div className="flex-1 text-left">
                      <p className="text-sm font-semibold text-red-700 dark:text-red-400">Logout</p>
                      <p className="text-xs text-red-600/70 dark:text-red-400/70">Sign out of your account</p>
                    </div>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
