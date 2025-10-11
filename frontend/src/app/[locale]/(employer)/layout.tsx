import React from 'react';
import WebsiteHeader from '@/components/website/WebsiteHeader';
import WebsiteFooter from '@/components/website/WebsiteFooter';

export default function EmployerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <WebsiteHeader siteType="employer" />
      <main className="flex-grow">{children}</main>
      <WebsiteFooter siteType="employer" />
    </div>
  );
}
