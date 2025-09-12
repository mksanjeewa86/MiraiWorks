'use client';

import { Settings, User, LogOut, Menu } from 'lucide-react'
import { useRouter } from 'next/navigation'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { useAuth } from '@/contexts/AuthContext'
import Brand from '@/components/common/Brand'
import SearchInput from '@/components/common/SearchInput'
import NotificationDropdown from '@/components/notifications/NotificationDropdown'
import type { TopbarProps } from '@/types/components'

export default function Topbar({ onMenuClick }: TopbarProps) {
  const { user, logout } = useAuth()
  const router = useRouter()

  const handleSearch = (query: string) => {
    console.log('Search:', query)
    // TODO: Implement global search
  }

  const getUserDisplayName = () => {
    if (!user) return 'User'
    return `${user.first_name} ${user.last_name}`.trim() || user.email
  }

  const getUserInitials = () => {
    if (!user) return 'U'
    const first = user.first_name?.[0] || ''
    const last = user.last_name?.[0] || ''
    return (first + last).toUpperCase() || user.email[0].toUpperCase()
  }

  const handleProfileClick = () => {
    router.push('/profile')
  }

  const handleSettingsClick = () => {
    router.push('/settings')
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b" style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border-color)' }}>
      <div className="flex items-center justify-between px-4 py-3">
        {/* Left side */}
        <div className="flex items-center space-x-4">
          <button
            onClick={onMenuClick}
            className="p-2 rounded-2xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Toggle menu"
            data-testid="menu-toggle-button"
          >
            <Menu className="h-5 w-5 text-gray-600 dark:text-gray-300" />
          </button>
          
          <Brand className="hidden sm:flex" />
          <Brand className="sm:hidden" showText={false} />
        </div>

        {/* Center - Search */}
        <div className="flex-1 max-w-md mx-4">
          <SearchInput 
            placeholder="Search everything..." 
            onSearch={handleSearch}
          />
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-3">
          {/* Notifications */}
          <NotificationDropdown />


          {/* User menu */}
          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild>
              <button 
                className="flex items-center space-x-2 p-2 rounded-2xl hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="User menu"
                data-testid="user-menu"
              >
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium" style={{ backgroundColor: 'var(--brand-primary)' }}>
                  {getUserInitials()}
                </div>
                <span className="hidden md:inline text-sm font-medium text-gray-700 dark:text-gray-200">
                  {getUserDisplayName()}
                </span>
              </button>
            </DropdownMenu.Trigger>
            
            <DropdownMenu.Portal>
              <DropdownMenu.Content 
                className="min-w-[200px] bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-xl z-50 p-2"
                sideOffset={5}
              >
                <div className="px-3 py-2 border-b border-gray-100 dark:border-gray-700">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{getUserDisplayName()}</p>
                  <p className="text-xs text-muted-500">{user?.email}</p>
                </div>
                
                <DropdownMenu.Item 
                  className="flex items-center space-x-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-xl cursor-pointer"
                  onClick={handleProfileClick}
                >
                  <User className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-700 dark:text-gray-200">Profile</span>
                </DropdownMenu.Item>
                
                <DropdownMenu.Item 
                  className="flex items-center space-x-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-xl cursor-pointer"
                  onClick={handleSettingsClick}
                >
                  <Settings className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-700 dark:text-gray-200">Settings</span>
                </DropdownMenu.Item>
                
                <DropdownMenu.Separator className="h-px bg-gray-200 dark:bg-gray-700 my-1" />
                
                <DropdownMenu.Item 
                  className="flex items-center space-x-2 p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl cursor-pointer"
                  onClick={logout}
                  data-testid="logout-button"
                >
                  <LogOut className="h-4 w-4 text-red-500" />
                  <span className="text-sm text-red-700 dark:text-red-400">Logout</span>
                </DropdownMenu.Item>
              </DropdownMenu.Content>
            </DropdownMenu.Portal>
          </DropdownMenu.Root>
        </div>
      </div>
    </header>
  )
}