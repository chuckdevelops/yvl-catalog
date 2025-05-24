'use client';

import React, { useEffect, useRef } from 'react';
import { useSearch } from '../context/SearchContext';
import { useRouter } from 'next/navigation';

const SearchModal: React.FC = () => {
  const { 
    isSearchOpen, 
    searchQuery, 
    searchResults, 
    closeSearch, 
    setSearchQuery 
  } = useSearch();
  const searchInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  // Focus search input when modal opens
  useEffect(() => {
    if (isSearchOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isSearchOpen]);

  // Close modal on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isSearchOpen) {
        closeSearch();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [closeSearch, isSearchOpen]);

  // Handle result click
  const handleResultClick = (id: string) => {
    router.push(`/song/${id}`);
    closeSearch();
  };

  // Don't render anything if search is not open
  if (!isSearchOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-start justify-center pt-20 px-4 backdrop-blur-sm">
      {/* Close button */}
      <button 
        onClick={closeSearch}
        className="absolute top-6 right-6 text-gray-400 hover:text-white"
        aria-label="Close search"
      >
        <i className="fas fa-times text-xl"></i>
      </button>

      <div className="w-full max-w-3xl">
        {/* Search input */}
        <div className="relative mb-8">
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search songs, producers, features..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-gray-900 text-white border-b-2 border-accent py-4 pl-12 pr-4 text-xl focus:outline-none"
          />
          <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-accent text-xl"></i>
        </div>

        {/* Search results */}
        <div className="bg-gray-900 rounded-lg overflow-hidden">
          {searchQuery.trim() !== '' && (
            <div className="px-4 py-3 border-b border-gray-800">
              <span className="text-gray-400">
                {searchResults.length} result{searchResults.length !== 1 ? 's' : ''} found
              </span>
            </div>
          )}

          <div className="max-h-[60vh] overflow-y-auto">
            {searchResults.length > 0 ? (
              <ul className="divide-y divide-gray-800">
                {searchResults.map((song) => (
                  <li 
                    key={song.id} 
                    className="px-4 py-3 hover:bg-gray-800 cursor-pointer transition-colors"
                    onClick={() => handleResultClick(song.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-medium text-lg">{song.name}</h3>
                        <p className="text-gray-400 text-sm">
                          {song.era} • {song.producer}
                          {song.features.length > 0 && ` • ft. ${song.features.join(', ')}`}
                        </p>
                      </div>
                      <div>
                        <span className="px-2 py-1 text-xs bg-accent bg-opacity-20 text-accent rounded-full">
                          {song.type}
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              searchQuery.trim() !== '' && (
                <div className="px-4 py-12 text-center text-gray-500">
                  <i className="fas fa-search-minus text-3xl mb-3"></i>
                  <p>No results found for "{searchQuery}"</p>
                  <p className="text-sm mt-2">Try different keywords or check for typos</p>
                </div>
              )
            )}
            
            {searchQuery.trim() === '' && (
              <div className="px-4 py-12 text-center text-gray-500">
                <i className="fas fa-search text-3xl mb-3"></i>
                <p>Start typing to search</p>
                <p className="text-sm mt-2">Search by song name, producer, features, or lyrics</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SearchModal; 