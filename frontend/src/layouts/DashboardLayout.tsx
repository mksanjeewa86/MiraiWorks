import React from 'react';
import { Outlet } from 'react-router-dom';

export default function DashboardLayout() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="flex">
        {/* Sidebar placeholder */}
        <div className="w-64 bg-white shadow-md">
          <div className="p-4">
            <h2 className="text-lg font-semibold">MiraiWorks</h2>
            <p className="text-sm text-gray-600">Dashboard</p>
          </div>
        </div>
        
        {/* Main content */}
        <div className="flex-1">
          <div className="p-8">
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  );
}