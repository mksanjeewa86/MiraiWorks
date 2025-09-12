'use client';

import { useState, useEffect, ReactNode } from 'react'
import Topbar from './Topbar'
import Sidebar from './Sidebar'
import type { AppLayoutProps } from '@/types/components'

export default function AppLayout({ children }: AppLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
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
      const savedCollapsed = localStorage.getItem('sidebarCollapsed')
      setSidebarCollapsed(savedCollapsed === 'true')
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
  }


  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <Topbar 
        onMenuClick={handleMenuClick}
      />
      
      <div className="flex">
        <Sidebar
          isOpen={sidebarOpen}
          isCollapsed={sidebarCollapsed}
          onClose={handleSidebarClose}
          onToggleCollapse={handleSidebarToggleCollapse}
          isMobile={isMobile}
        />
        
        <main className={`
          flex-1 min-h-[calc(100vh-4rem)] transition-all duration-300
          ${!isMobile && !sidebarCollapsed ? 'lg:ml-64' : !isMobile && sidebarCollapsed ? 'lg:ml-16' : 'ml-0'}
        `}>
          <div className="p-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}