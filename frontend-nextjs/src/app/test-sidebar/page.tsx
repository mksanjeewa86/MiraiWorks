'use client';

import { useState } from 'react';
import AppLayout from '@/components/layout/AppLayout';

export default function TestSidebarPage() {
  const [debugInfo, setDebugInfo] = useState({
    windowWidth: 0,
    sidebarElement: false,
    sidebarVisible: false,
    sidebarStyles: {}
  });

  const checkSidebar = () => {
    const sidebar = document.querySelector('[data-testid="sidebar"]');
    const windowWidth = window.innerWidth;
    
    if (sidebar) {
      const styles = window.getComputedStyle(sidebar);
      const rect = sidebar.getBoundingClientRect();
      
      setDebugInfo({
        windowWidth,
        sidebarElement: true,
        sidebarVisible: rect.width > 0 && rect.height > 0,
        sidebarStyles: {
          display: styles.display,
          visibility: styles.visibility,
          transform: styles.transform,
          width: styles.width,
          height: styles.height,
          position: styles.position,
          top: styles.top,
          left: styles.left,
          zIndex: styles.zIndex
        }
      });
    } else {
      setDebugInfo({
        windowWidth,
        sidebarElement: false,
        sidebarVisible: false,
        sidebarStyles: {}
      });
    }
  };

  return (
    <AppLayout>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">Sidebar Debug Test</h1>
        
        <button 
          onClick={checkSidebar}
          className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Check Sidebar Status
        </button>

        <div className="bg-gray-100 p-4 rounded-lg">
          <h2 className="text-lg font-semibold mb-2">Debug Information:</h2>
          <pre className="text-sm">{JSON.stringify(debugInfo, null, 2)}</pre>
        </div>

        <div className="mt-4 p-4 bg-yellow-100 rounded">
          <p><strong>Instructions:</strong></p>
          <ol className="list-decimal list-inside mt-2 space-y-1">
            <li>Click "Check Sidebar Status" button</li>
            <li>Look for sidebar element in DOM</li>
            <li>Check if sidebar is visible</li>
            <li>Try clicking the menu button in the topbar</li>
          </ol>
        </div>

        <div className="mt-4 p-4 bg-green-100 rounded">
          <p><strong>Expected behavior:</strong></p>
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Sidebar should be visible on desktop (width ≥ 1024px)</li>
            <li>Menu button should toggle sidebar collapse/expand</li>
            <li>On mobile, sidebar should be hidden by default</li>
          </ul>
        </div>
      </div>
    </AppLayout>
  );
}