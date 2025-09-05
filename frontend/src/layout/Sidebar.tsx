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
  ChevronRight
} from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useContext } from 'react'
import { AuthContext } from '../contexts/AuthContext'

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
    roles: ['candidate', 'recruiter', 'employer', 'company_admin']
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
  const { user } = useContext(AuthContext)
  const location = useLocation()

  // Filter navigation items based on user role
  const visibleItems = navigationItems.filter(item => 
    user?.role && item.roles.includes(user.role)
  )

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return location.pathname === '/dashboard' || location.pathname === '/'
    }
    return location.pathname.startsWith(href)
  }

  const sidebarClasses = `
    fixed lg:relative top-0 left-0 z-40 h-screen bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 
    transition-all duration-300 ease-in-out
    ${isMobile ? 'w-64' : isCollapsed ? 'w-16' : 'w-64'}
    ${isMobile && !isOpen ? '-translate-x-full' : 'translate-x-0'}
    ${!isMobile && isOpen ? 'block' : isMobile ? 'block' : 'hidden lg:block'}
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

      <aside className={sidebarClasses}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800">
            {!isCollapsed && (
              <span className="text-lg font-semibold text-gray-900 dark:text-white">
                Navigation
              </span>
            )}
            
            <div className="flex items-center space-x-2">
              {!isMobile && (
                <button
                  onClick={onToggleCollapse}
                  className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
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
                  className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors lg:hidden"
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
                  to={item.href}
                  onClick={isMobile ? onClose : undefined}
                  className={`
                    group flex items-center px-3 py-2.5 rounded-2xl text-sm font-medium transition-all duration-200
                    ${active 
                      ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400' 
                      : 'text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800'
                    }
                  `}
                  title={isCollapsed ? item.name : undefined}
                >
                  <Icon className={`
                    h-5 w-5 flex-shrink-0 transition-colors
                    ${active 
                      ? 'text-primary-600 dark:text-primary-400' 
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
                    <div className="ml-auto w-2 h-2 bg-primary-600 dark:bg-primary-400 rounded-full" />
                  )}
                </Link>
              )
            })}
          </nav>

          {/* User info (collapsed state) */}
          {isCollapsed && user && (
            <div className="p-4 border-t border-gray-200 dark:border-gray-800">
              <div className="flex items-center justify-center">
                <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  {user.first_name?.[0] || user.email[0].toUpperCase()}
                </div>
              </div>
            </div>
          )}

          {/* User info (expanded state) */}
          {!isCollapsed && user && (
            <div className="p-4 border-t border-gray-200 dark:border-gray-800">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-primary-500 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  {user.first_name?.[0] || user.email[0].toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {`${user.first_name} ${user.last_name}`.trim() || 'User'}
                  </p>
                  <p className="text-xs text-muted-500 truncate">
                    {user.role?.replace('_', ' ').toUpperCase()}
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