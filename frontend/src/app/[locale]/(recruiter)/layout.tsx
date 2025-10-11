import React from 'react';
import WebsiteHeader from '@/components/website/WebsiteHeader';
import WebsiteFooter from '@/components/website/WebsiteFooter';

export default function RecruiterLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <WebsiteHeader siteType="recruiter" />
      <main className="flex-grow">{children}</main>
      <WebsiteFooter siteType="recruiter" />
    </div>
  );
}
