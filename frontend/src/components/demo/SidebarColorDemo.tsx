'use client';

import React, { useState } from 'react';
import { roleColorSchemes } from '@/utils/roleColorSchemes';

/**
 * Demo component to showcase different sidebar color schemes for each user role
 * This is a development utility to visualize the color schemes
 */
export default function SidebarColorDemo() {
  const [selectedRole, setSelectedRole] = useState<string>('super_admin');

  const roles = Object.keys(roleColorSchemes);
  const colorScheme = roleColorSchemes[selectedRole];

  return (
    <div className="p-8 bg-gray-100 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Sidebar Color Schemes by Role</h1>

        {/* Role Selector */}
        <div className="mb-8">
          <label className="block text-sm font-medium text-gray-700 mb-2">Select User Role:</label>
          <select
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
            className="block w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            {roles.map((role) => (
              <option key={role} value={role}>
                {role.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {/* Color Scheme Preview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Sidebar Preview */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Sidebar Preview</h2>
            <div
              className={`w-64 h-96 ${colorScheme.background} ${colorScheme.border} border rounded-lg overflow-hidden`}
            >
              {/* Header */}
              <div className={`p-4 border-b ${colorScheme.border} ${colorScheme.headerBackground}`}>
                <div className="flex items-center space-x-2">
                  <div
                    className={`w-8 h-8 rounded-lg ${colorScheme.brandBackground} flex items-center justify-center`}
                  >
                    <span className={`${colorScheme.textPrimary} font-bold text-sm`}>M</span>
                  </div>
                  <span className={`text-lg font-bold ${colorScheme.textPrimary}`}>MiraiWorks</span>
                </div>
              </div>

              {/* Navigation Items */}
              <div className="p-4 space-y-3">
                {/* Active Item */}
                <div
                  className={`px-4 py-2 h-10 rounded-xl ${colorScheme.buttonActive} ${colorScheme.textPrimary} shadow-lg flex items-center`}
                >
                  <div className={`p-2 rounded-lg bg-white/20 mr-3`}>
                    <div className="w-4 h-4 bg-white rounded"></div>
                  </div>
                  <span className="text-sm font-semibold">Dashboard</span>
                  <div className="ml-auto">
                    <div
                      className={`w-2 h-2 rounded-full ${colorScheme.activeIndicator} shadow-lg animate-pulse`}
                    ></div>
                  </div>
                </div>

                {/* Inactive Items */}
                <div
                  className={`px-4 py-2 h-10 rounded-xl ${colorScheme.textSecondary} border ${colorScheme.buttonBorder} flex items-center`}
                >
                  <div className={`p-2 rounded-lg ${colorScheme.brandAccent} mr-3`}>
                    <div className={`w-4 h-4 ${colorScheme.textPrimary} rounded`}></div>
                  </div>
                  <span className="text-sm font-semibold">Messages</span>
                </div>

                <div
                  className={`px-4 py-2 h-10 rounded-xl ${colorScheme.textSecondary} border ${colorScheme.buttonBorder} flex items-center`}
                >
                  <div className={`p-2 rounded-lg ${colorScheme.brandAccent} mr-3`}>
                    <div className={`w-4 h-4 ${colorScheme.textPrimary} rounded`}></div>
                  </div>
                  <span className="text-sm font-semibold">Settings</span>
                </div>
              </div>

              {/* User Info */}
              <div
                className={`absolute bottom-0 left-0 right-0 p-4 border-t ${colorScheme.border} ${colorScheme.headerBackground}`}
              >
                <div
                  className={`flex items-center space-x-3 p-3 rounded-xl ${colorScheme.headerBackground} border ${colorScheme.buttonBorder}`}
                >
                  <div
                    className={`w-10 h-10 rounded-full ${colorScheme.avatarBackground} flex items-center justify-center ${colorScheme.textPrimary} text-sm font-bold`}
                  >
                    U
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-semibold ${colorScheme.textPrimary} truncate`}>
                      Test User
                    </p>
                    <p className={`text-xs ${colorScheme.textSecondary} truncate font-medium`}>
                      {selectedRole.replace('_', ' ').toUpperCase()}
                    </p>
                  </div>
                  <div
                    className={`w-2 h-2 rounded-full ${colorScheme.statusIndicator} shadow-lg animate-pulse`}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Color Palette */}
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900">Color Palette</h2>
            <div className="grid grid-cols-1 gap-3">
              {Object.entries(colorScheme).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded ${value} border border-gray-300`}></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{key}</p>
                    <p className="text-xs text-gray-500 font-mono">{value}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Role Comparison */}
        <div className="mt-12">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">All Role Previews</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {roles.map((role) => {
              const scheme = roleColorSchemes[role];
              return (
                <div key={role} className="text-center">
                  <div
                    className={`w-full h-32 ${scheme.background} ${scheme.border} border rounded-lg mb-2 relative overflow-hidden`}
                  >
                    <div className={`absolute inset-0 ${scheme.backgroundOverlay}`}></div>
                    <div
                      className={`absolute top-2 left-2 w-6 h-6 rounded ${scheme.brandBackground}`}
                    ></div>
                    <div
                      className={`absolute bottom-2 left-2 right-2 h-6 ${scheme.buttonActive} rounded`}
                    ></div>
                  </div>
                  <p className="text-sm font-medium text-gray-900">
                    {role.replace('_', ' ').toUpperCase()}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
