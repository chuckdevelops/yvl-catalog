'use client';

import React from 'react';
import Link from 'next/link';
import MobileNav from './MobileNav';
import { useSearch } from '../context/SearchContext';

const Navigation: React.FC = () => {
  const { openSearch } = useSearch();

  return (
    <nav className="w-full bg-black bg-opacity-80 backdrop-blur-md py-4 border-b border-gray-800 fixed top-0 z-50">
      <div className="container mx-auto px-4 flex items-center justify-between">
        <Link href="/" className="font-display text-2xl text-white uppercase tracking-wider">
          Carti Catalog
        </Link>
        
        <div className="hidden md:flex items-center space-x-8">
          <Link href="/" className="nav-link">Home</Link>
          <Link href="/music" className="nav-link">Music</Link>
          <Link href="/media" className="nav-link">Media</Link>
          <Link href="/coming-soon" className="nav-link flex items-center">
            <span className="text-accent">Coming Soon</span>
          </Link>
        </div>
        
        <div className="flex items-center space-x-4">
          <button 
            onClick={openSearch}
            className="flex items-center text-gray-400 hover:text-white transition-colors"
            aria-label="Search"
          >
            <i className="fas fa-search mr-2"></i>
            <span className="hidden md:inline">Search</span>
          </button>
          
          {/* Mobile Navigation */}
          <MobileNav />
        </div>
      </div>
      
      {/* Mobile menu - hidden by default */}
      <div className="hidden bg-black bg-opacity-95 absolute w-full left-0 py-4 px-4 md:hidden">
        <div className="flex flex-col space-y-4">
          <Link href="/" className="nav-link">Home</Link>
          <Link href="/music" className="nav-link">Music</Link>
          <Link href="/media" className="nav-link">Media</Link>
          <Link href="/coming-soon" className="nav-link">Coming Soon</Link>
          
          <div className="relative mt-4">
            <input 
              type="text" 
              placeholder="Search" 
              className="w-full bg-gray-900 text-white border border-gray-700 rounded-full pl-10 pr-4 py-2 focus:outline-none focus:border-gray-500"
            />
            <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500"></i>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation; 