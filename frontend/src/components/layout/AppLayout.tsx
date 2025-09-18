'use client';

import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import Topbar from './Topbar'
import Sidebar from './Sidebar'
import { getPageInfo } from '@/utils/pageInfo'
import type { AppLayoutProps } from '@/types/components'

export default function AppLayout({ children, pageTitle, pageDescription }: AppLayoutProps) {
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(true) // Start with true for desktop
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    // Initialize from localStorage immediately
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('sidebarCollapsed')
      return saved === 'true'
    }
    return false
  })
  const [isMobile, setIsMobile] = useState(false)


  // Check for mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024) // lg breakpoint
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])


  // Auto-collapse sidebar on mobile
  useEffect(() => {
    if (isMobile) {
      setSidebarCollapsed(false) // Always expanded when opened on mobile
      setSidebarOpen(false) // Closed by default on mobile
    } else {
      // Restore desktop sidebar state
      setSidebarOpen(true) // Always open on desktop
    }
  }, [isMobile])

  const handleMenuClick = () => {
    if (isMobile) {
      setSidebarOpen(!sidebarOpen)
    } else {
      setSidebarCollapsed(!sidebarCollapsed)
    }
  }

  const handleSidebarClose = () => {
    setSidebarOpen(false)
  }

  const handleSidebarToggleCollapse = () => {
    const newCollapsed = !sidebarCollapsed
    setSidebarCollapsed(newCollapsed)
    localStorage.setItem('sidebarCollapsed', newCollapsed.toString())

    // Dispatch custom event to notify topbar
    window.dispatchEvent(new Event('sidebarStateChanged'))
  }


  // Get page information from pathname, allow props to override
  const pathPageInfo = getPageInfo(pathname)
  const finalPageTitle = pageTitle || pathPageInfo.title
  const finalPageDescription = pageDescription || pathPageInfo.description

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Topbar pageTitle={finalPageTitle} pageDescription={finalPageDescription} />
      
      <div className="flex">
        <Sidebar
          isOpen={sidebarOpen}
          isCollapsed={sidebarCollapsed}
          onClose={handleSidebarClose}
          onToggleCollapse={handleSidebarToggleCollapse}
          isMobile={isMobile}
        />
        
        <main className={`
          flex-1 min-h-screen transition-all duration-300
          ${!isMobile && !sidebarCollapsed ? 'lg:ml-64' : !isMobile && sidebarCollapsed ? 'lg:ml-16' : 'ml-0'}
        `}>
          <div className="px-6 pb-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}