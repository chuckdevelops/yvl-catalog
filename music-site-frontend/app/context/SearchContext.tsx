'use client';

import React, { createContext, useState, useContext, ReactNode } from 'react';
import { Song, songs } from '../lib/data';

interface SearchContextType {
  isSearchOpen: boolean;
  searchQuery: string;
  searchResults: Song[];
  openSearch: () => void;
  closeSearch: () => void;
  setSearchQuery: (query: string) => void;
  performSearch: (query: string) => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const SearchProvider = ({ children }: { children: ReactNode }) => {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Song[]>([]);

  const openSearch = () => setIsSearchOpen(true);
  const closeSearch = () => {
    setIsSearchOpen(false);
    // Clear search query when closing
    setSearchQuery('');
  };

  const performSearch = (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    const term = query.toLowerCase();
    const results = songs.filter(song => {
      // Search in name
      if (song.name.toLowerCase().includes(term)) return true;
      
      // Search in producer
      if (song.producer.toLowerCase().includes(term)) return true;
      
      // Search in features
      if (song.features.some(feature => feature.toLowerCase().includes(term))) return true;
      
      // Search in lyrics if available
      if (song.lyrics && song.lyrics.toLowerCase().includes(term)) return true;
      
      // Search in notes if available
      if (song.notes && song.notes.toLowerCase().includes(term)) return true;
      
      return false;
    });

    setSearchResults(results);
  };

  // Update search when searchQuery changes
  React.useEffect(() => {
    performSearch(searchQuery);
  }, [searchQuery]);

  return (
    <SearchContext.Provider
      value={{
        isSearchOpen,
        searchQuery,
        searchResults,
        openSearch,
        closeSearch,
        setSearchQuery,
        performSearch
      }}
    >
      {children}
    </SearchContext.Provider>
  );
};

export const useSearch = () => {
  const context = useContext(SearchContext);
  if (context === undefined) {
    throw new Error('useSearch must be used within a SearchProvider');
  }
  return context;
}; 