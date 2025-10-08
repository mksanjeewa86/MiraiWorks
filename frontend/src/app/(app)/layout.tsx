import React from 'react';

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // This layout wraps all authenticated app pages
  // The actual AppLayout component with sidebar is used per-page via ProtectedRoute
  return <>{children}</>;
}
