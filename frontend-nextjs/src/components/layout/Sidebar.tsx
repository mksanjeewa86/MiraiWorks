'use client';

import { 
  LayoutDashboard, 
  Briefcase, 
  MessageSquare, 
  Calendar, 
  Video,
  FileText, 
  Settings,
  Users,
  Building2,
  X,
  ChevronLeft,
  ChevronRight,
  User
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'

interface SidebarProps {
  isOpen: boolean
  isCollapsed: boolean
  onClose: () => void
  onToggleCollapse: () => void
  isMobile: boolean
}

interface NavItem {
  name: string
  href: string
  icon: React.ComponentType<{ className?: string }>
  roles: string[]
}

const navigationItems: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin', 'super_admin']
  },
  {
    name: 'Jobs',
    href: '/jobs',
    icon: Briefcase,
    roles: ['candidate']
  },
  {
    name: 'Positions',
    href: '/positions',
    icon: Briefcase,
    roles: ['employer', 'company_admin']
  },
  {
    name: 'Candidates',
    href: '/candidates',
    icon: Users,
    roles: ['recruiter', 'company_admin']
  },
  {
    name: 'Messages',
    href: '/messages',
    icon: MessageSquare,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin', 'super_admin']
  },
  {
    name: 'Calendar',
    href: '/calendar',
    icon: Calendar,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin']
  },
  {
    name: 'Interviews',
    href: '/interviews',
    icon: Video,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin']
  },
  {
    name: 'Resume',
    href: '/resumes',
    icon: FileText,
    roles: ['candidate']
  },
  {
    name: 'Profile',
    href: '/profile',
    icon: User,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin', 'super_admin']
  },
  {
    name: 'Companies',
    href: '/companies',
    icon: Building2,
    roles: ['recruiter', 'super_admin']
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    roles: ['candidate', 'recruiter', 'employer', 'company_admin', 'super_admin']
  }
]

export default function Sidebar({ 
  isOpen, 
  isCollapsed, 
  onClose, 
  onToggleCollapse, 
  isMobile 
}: SidebarProps) {
  const { user } = useAuth()
  const pathname = usePathname()

  // Filter navigation items based on user role
  const visibleItems = navigationItems.filter(item => {
    if (!user?.roles?.length) return false
    return user.roles.some(userRole => item.roles.includes(userRole.role.name))
  })

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard' || pathname === '/'
    }
    return pathname?.startsWith(href) ?? false
  }

  const sidebarClasses = `
    fixed left-0 z-40 border-r
    transition-all duration-300 ease-in-out
    ${isMobile ? 'top-0 h-screen' : 'top-16 h-[calc(100vh-4rem)]'}
    ${isMobile ? 'w-64' : isCollapsed ? 'w-16' : 'w-64'}
    ${isMobile && !isOpen ? '-translate-x-full' : 'translate-x-0'}
    lg:translate-x-0
  `

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
        className={sidebarClasses} 
        style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)' }}
        data-testid="sidebar"
        data-collapsed={isCollapsed}
        data-mobile={isMobile}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4" style={{ borderBottom: '1px solid var(--border-color)' }}>
            {!isCollapsed && (
              <span className="text-lg font-semibold text-gray-900 dark:text-white">
                Navigation
              </span>
            )}
            
            <div className="flex items-center space-x-2">
              {!isMobile && (
                <button
                  onClick={onToggleCollapse}
                  className="p-1.5 rounded-lg transition-colors hover:bg-gray-100 dark:hover:bg-gray-800" style={{ backgroundColor: 'transparent' }}
                  aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
                >
                  {isCollapsed ? (
                    <ChevronRight className="h-4 w-4 text-gray-500" />
                  ) : (
                    <ChevronLeft className="h-4 w-4 text-gray-500" />
                  )}
                </button>
              )}
              
              {isMobile && (
                <button
                  onClick={onClose}
                  className="p-1.5 rounded-lg transition-colors lg:hidden hover:bg-gray-100 dark:hover:bg-gray-800" style={{ backgroundColor: 'transparent' }}
                  aria-label="Close sidebar"
                >
                  <X className="h-4 w-4 text-gray-500" />
                </button>
              )}
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
            {visibleItems.map((item) => {
              const Icon = item.icon
              const active = isActive(item.href)
              
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={isMobile ? onClose : undefined}
                  className={`
                    group flex items-center px-3 py-2.5 rounded-2xl text-sm font-medium transition-all duration-200
                    ${active 
                      ? 'text-brand-primary' 
                      : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                    }
                  `}
                  style={active ? { backgroundColor: 'rgba(108, 99, 255, 0.1)' } : undefined}
                  title={isCollapsed ? item.name : undefined}
                >
                  <Icon className={`
                    h-5 w-5 flex-shrink-0 transition-colors
                    ${active 
                      ? 'text-brand-primary' 
                      : 'text-gray-500 dark:text-gray-400 group-hover:text-gray-700 dark:group-hover:text-gray-200'
                    }
                  `} />
                  
                  {!isCollapsed && (
                    <span className="ml-3 truncate">
                      {item.name}
                    </span>
                  )}
                  
                  {/* Active indicator */}
                  {active && (
                    <div className="ml-auto w-2 h-2 rounded-full" style={{ backgroundColor: 'var(--brand-primary)' }} />
                  )}
                </Link>
              )
            })}
          </nav>

          {/* User info (collapsed state) */}
          {isCollapsed && user && (
            <div className="p-4" style={{ borderTop: '1px solid var(--border-color)' }}>
              <div className="flex items-center justify-center">
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium" style={{ backgroundColor: 'var(--brand-primary)' }}>
                  {user.first_name?.[0] || user.email[0].toUpperCase()}
                </div>
              </div>
            </div>
          )}

          {/* User info (expanded state) */}
          {!isCollapsed && user && (
            <div className="p-4" style={{ borderTop: '1px solid var(--border-color)' }}>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-medium" style={{ backgroundColor: 'var(--brand-primary)' }}>
                  {user.first_name?.[0] || user.email[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {`${user.first_name} ${user.last_name}`.trim() || 'User'}
                  </p>
                  <p className="text-xs text-muted-500 truncate">
                    {user.roles?.[0]?.role?.name?.replace('_', ' ').toUpperCase()}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </aside>
    </>
  )
}