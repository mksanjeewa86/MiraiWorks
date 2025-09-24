import React from 'react';
import WebsiteHeader from './WebsiteHeader';
import WebsiteFooter from './WebsiteFooter';
import type { WebsiteLayoutProps } from '@/types/components';

const WebsiteLayout = ({ children }: WebsiteLayoutProps) => {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <WebsiteHeader />
      <main className="flex-grow">{children}</main>
      <WebsiteFooter />
    </div>
  );
};

export default WebsiteLayout;
