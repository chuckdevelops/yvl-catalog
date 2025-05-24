'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useSearch } from '../context/SearchContext';

const MobileNav: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { openSearch } = useSearch();

  const handleSearchClick = () => {
    setIsOpen(false); // Close mobile menu
    openSearch(); // Open search modal
  };

  return (
    <div className="md:hidden">
      {/* Mobile menu button */}
      <button 
        className="text-white" 
        aria-label="Menu"
        onClick={() => setIsOpen(!isOpen)}
      >
        <i className={`fas ${isOpen ? 'fa-times' : 'fa-bars'} text-xl`}></i>
      </button>
      
      {/* Mobile menu - conditionally shown */}
      <div 
        className={`bg-black bg-opacity-95 absolute w-full left-0 py-4 px-4 transition-all duration-300 ease-in-out ${
          isOpen 
            ? 'max-h-96 opacity-100 top-16 border-b border-gray-800 z-40' 
            : 'max-h-0 opacity-0 top-10 overflow-hidden -z-10'
        }`}
      >
        <div className="flex flex-col space-y-4">
          <Link 
            href="/" 
            className="nav-link"
            onClick={() => setIsOpen(false)}
          >
            Home
          </Link>
          <Link 
            href="/music" 
            className="nav-link"
            onClick={() => setIsOpen(false)}
          >
            Music
          </Link>
          <Link 
            href="/media" 
            className="nav-link"
            onClick={() => setIsOpen(false)}
          >
            Media
          </Link>
          <Link 
            href="/coming-soon" 
            className="nav-link"
            onClick={() => setIsOpen(false)}
          >
            Coming Soon
          </Link>
          
          <button 
            onClick={handleSearchClick}
            className="flex items-center text-gray-400 hover:text-white transition-colors py-2"
          >
            <i className="fas fa-search mr-2"></i>
            Search
          </button>
        </div>
      </div>
    </div>
  );
};

export default MobileNav; 