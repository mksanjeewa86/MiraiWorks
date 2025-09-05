'use client'
import { useState } from 'react';
import Link from 'next/link';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <header className="header">
      <div className="container">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold text-primary">MiraiWorks</h1>
            </div>
          </div>

          <nav className="hidden md:block">
            <div className="ml-10 flex items-center space-x-8">
              <Link href="/" className="nav-link">Home</Link>
              <Link href="/jobs" className="nav-link">Jobs</Link>
              <Link href="/about" className="nav-link">About</Link>
              <Link href="/services" className="nav-link">Services</Link>
              <Link href="/contact" className="nav-link">Contact</Link>
            </div>
          </nav>

          <div className="hidden md:block">
            <div className="ml-4 flex items-center space-x-4">
              <button className="btn btn-primary">
                Post Job
              </button>
            </div>
          </div>

          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="text-secondary-dark p-2 transition-colors"
              aria-label="Toggle menu"
            >
              <svg className="h-6 w-6" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                {isMenuOpen ? (
                  <path d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {isMenuOpen && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 border-t border-gray-200">
              <Link href="/" className="nav-link block">Home</Link>
              <Link href="/jobs" className="nav-link block">Jobs</Link>
              <Link href="/about" className="nav-link block">About</Link>
              <Link href="/services" className="nav-link block">Services</Link>
              <Link href="/contact" className="nav-link block">Contact</Link>
              <button className="btn btn-primary w-full">
                Post Job
              </button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;