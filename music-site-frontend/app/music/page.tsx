'use client';

import React, { useState, useMemo } from 'react';
import Layout from '../components/Layout';
import { songs } from '../lib/data';
import HiddenAudioElements from '../components/HiddenAudioElements';

export default function MusicPage() {
  // State for filters
  const [filters, setFilters] = useState({
    era: '',
    sheetTab: '',
    quality: '',
    type: '',
    producer: '',
    search: ''
  });
  
  // State for view mode (table or grid)
  const [viewMode, setViewMode] = useState('table');
  
  // Current page for pagination
  const [currentPage, setCurrentPage] = useState(1);
  const songsPerPage = 10;
  
  // Handle filter change
  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Reset to first page when filters change
    setCurrentPage(1);
  };
  
  // Apply filters to songs
  const filteredSongs = useMemo(() => {
    return songs.filter(song => {
      // Era filter
      if (filters.era && song.era !== filters.era) return false;
      
      // Sheet tab filter
      if (filters.sheetTab && !song.categories.includes(filters.sheetTab)) return false;
      
      // Quality filter
      if (filters.quality && song.quality !== filters.quality) return false;
      
      // Type filter
      if (filters.type && song.type !== filters.type) return false;
      
      // Producer filter
      if (filters.producer && song.producer !== filters.producer) return false;
      
      // Search filter (check name, producer, and features)
      if (filters.search) {
        const searchTerm = filters.search.toLowerCase();
        const nameMatch = song.name.toLowerCase().includes(searchTerm);
        const producerMatch = song.producer.toLowerCase().includes(searchTerm);
        const featuresMatch = song.features.some(
          feature => feature.toLowerCase().includes(searchTerm)
        );
        
        if (!nameMatch && !producerMatch && !featuresMatch) return false;
      }
      
      return true;
    });
  }, [filters]);
  
  // Get current songs for pagination
  const indexOfLastSong = currentPage * songsPerPage;
  const indexOfFirstSong = indexOfLastSong - songsPerPage;
  const currentSongs = filteredSongs.slice(indexOfFirstSong, indexOfLastSong);
  
  // Calculate total pages
  const totalPages = Math.ceil(filteredSongs.length / songsPerPage);
  
  // Change page
  const paginate = (pageNumber: number) => setCurrentPage(pageNumber);
  
  // Reset all filters
  const clearFilters = () => {
    setFilters({
      era: '',
      sheetTab: '',
      quality: '',
      type: '',
      producer: '',
      search: ''
    });
    setCurrentPage(1);
  };

  return (
    <Layout>
      <div className="container mx-auto px-4">
        {/* Hidden audio elements for direct playback */}
        <HiddenAudioElements songs={songs} />
        
        <h1 className="text-4xl font-display uppercase tracking-wider mb-8">Music Catalog</h1>
        
        {/* Filters Card */}
        <div className="card mb-8">
          <h2 className="text-xl font-medium mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Era Filter */}
            <div className="mb-4">
              <label htmlFor="era" className="block text-sm font-medium text-gray-400 mb-2">
                Era
              </label>
              <select 
                id="era" 
                name="era"
                value={filters.era}
                onChange={handleFilterChange}
                className="w-full bg-gray-900 text-white border border-gray-700 rounded-md px-3 py-2 focus:outline-none focus:border-gray-500"
              >
                <option value="">All Eras</option>
                <option value="Whole Lotta Red">Whole Lotta Red</option>
                <option value="Die Lit">Die Lit</option>
                <option value="Self Titled">Self Titled</option>
                <option value="WLR V1">WLR V1</option>
                <option value="WLR V2">WLR V2</option>
              </select>
            </div>
            
            {/* Sheet Tab Filter */}
            <div className="mb-4">
              <label htmlFor="sheetTab" className="block text-sm font-medium text-gray-400 mb-2">
                Sheet Tab
              </label>
              <select 
                id="sheetTab" 
                name="sheetTab"
                value={filters.sheetTab}
                onChange={handleFilterChange}
                className="w-full bg-gray-900 text-white border border-gray-700 rounded-md px-3 py-2 focus:outline-none focus:border-gray-500"
              >
                <option value="">All Tabs</option>
                <option value="Released">Released</option>
                <option value="Unreleased">Unreleased</option>
                <option value="Popular">Popular</option>
                <option value="Snippets">Snippets</option>
              </select>
            </div>
            
            {/* Quality Filter */}
            <div className="mb-4">
              <label htmlFor="quality" className="block text-sm font-medium text-gray-400 mb-2">
                Quality
              </label>
              <select 
                id="quality" 
                name="quality"
                value={filters.quality}
                onChange={handleFilterChange}
                className="w-full bg-gray-900 text-white border border-gray-700 rounded-md px-3 py-2 focus:outline-none focus:border-gray-500"
              >
                <option value="">All Qualities</option>
                <option value="CDQ">CDQ</option>
                <option value="HQ">HQ</option>
                <option value="LQ">LQ</option>
              </select>
            </div>
            
            {/* Type Filter */}
            <div className="mb-4">
              <label htmlFor="type" className="block text-sm font-medium text-gray-400 mb-2">
                Type
              </label>
              <select 
                id="type" 
                name="type"
                value={filters.type}
                onChange={handleFilterChange}
                className="w-full bg-gray-900 text-white border border-gray-700 rounded-md px-3 py-2 focus:outline-none focus:border-gray-500"
              >
                <option value="">All Types</option>
                <option value="Album Track">Album Track</option>
                <option value="Leak">Leak</option>
                <option value="Snippet">Snippet</option>
              </select>
            </div>
            
            {/* Producer Filter */}
            <div className="mb-4">
              <label htmlFor="producer" className="block text-sm font-medium text-gray-400 mb-2">
                Producer
              </label>
              <select 
                id="producer"
                name="producer"
                value={filters.producer}
                onChange={handleFilterChange}
                className="w-full bg-gray-900 text-white border border-gray-700 rounded-md px-3 py-2 focus:outline-none focus:border-gray-500"
              >
                <option value="">All Producers</option>
                <option value="F1lthy">F1lthy</option>
                <option value="Art Dealer">Art Dealer</option>
                <option value="Richie Souf">Richie Souf</option>
                <option value="Pierre Bourne">Pierre Bourne</option>
                <option value="Metro Boomin">Metro Boomin</option>
                <option value="Wheezy">Wheezy</option>
                <option value="TM88">TM88</option>
                <option value="Maaly Raw">Maaly Raw</option>
                <option value="Jetsonmade">Jetsonmade</option>
              </select>
            </div>
            
            {/* Search Filter */}
            <div className="mb-4">
              <label htmlFor="search" className="block text-sm font-medium text-gray-400 mb-2">
                Search
              </label>
              <div className="relative">
                <input 
                  type="text" 
                  id="search" 
                  name="search"
                  value={filters.search}
                  onChange={handleFilterChange}
                  placeholder="Search songs, producers, features..."
                  className="w-full bg-gray-900 text-white border border-gray-700 rounded-md pl-10 pr-3 py-2 focus:outline-none focus:border-gray-500"
                />
                <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500"></i>
              </div>
            </div>
          </div>
          
          <div className="flex flex-wrap gap-3 mt-2">
            <button onClick={clearFilters} className="btn btn-secondary">Clear Filters</button>
          </div>
        </div>
        
        {/* Results Card */}
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-medium">Results</h2>
            <span className="bg-accent bg-opacity-90 text-white px-3 py-1 rounded-full text-sm">
              {filteredSongs.length} songs found
            </span>
          </div>
          
          {/* Toggle view buttons */}
          <div className="flex justify-end mb-4">
            <div className="flex border border-gray-700 rounded-md overflow-hidden">
              <button 
                onClick={() => setViewMode('table')} 
                className={`px-3 py-1.5 text-sm ${viewMode === 'table' ? 'bg-gray-800 text-white' : 'bg-gray-900 text-gray-400'}`}
              >
                <i className="fas fa-table-list mr-1"></i> Table
              </button>
              <button 
                onClick={() => setViewMode('grid')} 
                className={`px-3 py-1.5 text-sm ${viewMode === 'grid' ? 'bg-gray-800 text-white' : 'bg-gray-900 text-gray-400'}`}
              >
                <i className="fas fa-grid-2 mr-1"></i> Grid
              </button>
            </div>
          </div>
          
          {/* Table View */}
          {viewMode === 'table' && (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-800">
                    <th className="text-left py-4 px-4 font-medium text-gray-400">Name</th>
                    <th className="text-left py-4 px-4 font-medium text-gray-400">Era</th>
                    <th className="text-left py-4 px-4 font-medium text-gray-400">Sheet Tab</th>
                    <th className="text-left py-4 px-4 font-medium text-gray-400">Type</th>
                    <th className="text-left py-4 px-4 font-medium text-gray-400">Quality</th>
                    <th className="text-left py-4 px-4 font-medium text-gray-400">Leak Date</th>
                    <th className="text-left py-4 px-4 font-medium text-gray-400">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {/* Song Rows */}
                  {currentSongs.length > 0 ? (
                    currentSongs.map((song) => (
                      <tr key={song.id} className="border-b border-gray-800 hover:bg-gray-900">
                        <td className="py-4 px-4">
                          <div className="flex items-center">
                            <a href={`/song/${song.id}`} className="hover:text-accent transition-colors">
                              {song.name}
                            </a>
                            {song.hasPreview && (
                              <i className="fas fa-music text-accent ml-2" title="Has audio preview"></i>
                            )}
                            {song.type === 'Album Track' && (
                              <span className="ml-2 px-2 py-0.5 text-xs bg-gray-700 text-white rounded-full">
                                Official
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-4 px-4">{song.era}</td>
                        <td className="py-4 px-4">
                          <div className="flex flex-wrap gap-1">
                            {song.categories.map((category, idx) => (
                              <span key={idx} className="px-2 py-0.5 text-xs bg-accent text-white rounded-full">
                                {category}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="py-4 px-4">{song.type}</td>
                        <td className="py-4 px-4">{song.quality}</td>
                        <td className="py-4 px-4">{song.leakDate}</td>
                        <td className="py-4 px-4">
                          <div className="flex space-x-2">
                            <button 
                              className="text-gray-400 hover:text-white" 
                              title="Play"
                              onClick={() => {
                                if (typeof window !== 'undefined' && 'AudioPlayerManager' in window) {
                                  // @ts-ignore - AudioPlayerManager is loaded from an external script
                                  const audioManager = window.audioPlayerManager;
                                  if (audioManager && song.previewUrl) {
                                    audioManager.playAudio(`preview-player-${song.id}`, song.previewUrl);
                                  }
                                }
                              }}
                            >
                              <i className="fas fa-play"></i>
                            </button>
                            <a href={`/song/${song.id}`} className="text-gray-400 hover:text-white" title="View Details">
                              <i className="fas fa-info-circle"></i>
                            </a>
                          </div>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={7} className="py-8 text-center text-gray-500">
                        No songs found matching your filters. Try adjusting your criteria.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
          
          {/* Grid View */}
          {viewMode === 'grid' && (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {currentSongs.length > 0 ? (
                currentSongs.map((song) => (
                  <div key={song.id} className="bg-gray-900 rounded-lg overflow-hidden group">
                    <div className="h-32 bg-gray-800 flex items-center justify-center relative">
                      <span className="text-4xl text-accent opacity-50 group-hover:opacity-30 transition-opacity">
                        <i className="fas fa-music"></i>
                      </span>
                      
                      {/* Hover overlay */}
                      <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          className="bg-accent rounded-full w-10 h-10 flex items-center justify-center mr-2"
                          onClick={() => {
                            if (typeof window !== 'undefined' && 'AudioPlayerManager' in window) {
                              // @ts-ignore - AudioPlayerManager is loaded from an external script
                              const audioManager = window.audioPlayerManager;
                              if (audioManager && song.previewUrl) {
                                audioManager.playAudio(`preview-player-${song.id}`, song.previewUrl);
                              }
                            }
                          }}
                        >
                          <i className="fas fa-play text-white"></i>
                        </button>
                        <a 
                          href={`/song/${song.id}`} 
                          className="bg-gray-700 rounded-full w-10 h-10 flex items-center justify-center"
                        >
                          <i className="fas fa-info-circle text-white"></i>
                        </a>
                      </div>
                    </div>
                    
                    <div className="p-4">
                      <h3 className="font-medium text-lg mb-1 truncate">
                        <a href={`/song/${song.id}`} className="hover:text-accent transition-colors">
                          {song.name}
                        </a>
                      </h3>
                      <p className="text-gray-400 text-sm">{song.era}</p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-gray-500">{song.type}</span>
                        <span className="text-xs px-2 py-0.5 bg-accent bg-opacity-20 text-accent rounded-full">
                          {song.quality}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-full py-8 text-center text-gray-500">
                  No songs found matching your filters. Try adjusting your criteria.
                </div>
              )}
            </div>
          )}
          
          {/* Pagination */}
          {filteredSongs.length > 0 && (
            <div className="mt-8 flex justify-center">
              <nav className="flex items-center space-x-1">
                <button 
                  className={`px-3 py-2 rounded-md border border-gray-700 ${currentPage === 1 ? 'text-gray-600 cursor-not-allowed' : 'text-gray-400 hover:bg-gray-800'}`}
                  onClick={() => currentPage > 1 && paginate(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  <i className="fas fa-chevron-left"></i>
                </button>
                
                {/* Generate page numbers */}
                {Array.from({ length: Math.min(5, totalPages) }).map((_, index) => {
                  // Calculate page number to display (show pages around current page)
                  let pageNum = index + 1;
                  if (totalPages > 5 && currentPage > 3) {
                    pageNum = Math.min(currentPage - 2 + index, totalPages);
                    if (currentPage + 2 > totalPages) {
                      pageNum = totalPages - 4 + index;
                    }
                  }
                  
                  return (
                    <button 
                      key={pageNum} 
                      className={`px-3 py-2 rounded-md ${pageNum === currentPage ? 'bg-accent text-white' : 'border border-gray-700 text-gray-400 hover:bg-gray-800'}`}
                      onClick={() => paginate(pageNum)}
                    >
                      {pageNum}
                    </button>
                  );
                })}
                
                <button 
                  className={`px-3 py-2 rounded-md border border-gray-700 ${currentPage === totalPages ? 'text-gray-600 cursor-not-allowed' : 'text-gray-400 hover:bg-gray-800'}`}
                  onClick={() => currentPage < totalPages && paginate(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  <i className="fas fa-chevron-right"></i>
                </button>
              </nav>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
} 