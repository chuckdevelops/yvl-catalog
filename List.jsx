import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, Link } from 'react-router-dom';
import apiService from './apiService';

const Badge = ({ text, type = "default", onClick = null }) => {
  const baseClasses = "inline-flex text-xs rounded px-2 py-1";
  const typeClasses = {
    default: "bg-gray-700 text-gray-200",
    era: "bg-blue-900 text-blue-100",
    quality: "bg-green-900 text-green-100",
    type: "bg-purple-900 text-purple-100",
    tab: "bg-yellow-900 text-yellow-100",
    filter: "bg-gray-800 text-gray-200 border border-gray-700"
  };
  
  const classes = `${baseClasses} ${typeClasses[type] || typeClasses.default}`;
  
  if (onClick) {
    return (
      <button 
        className={`${classes} hover:opacity-80 transition-opacity flex items-center gap-1`}
        onClick={onClick}
      >
        {text}
        <span className="ml-1">×</span>
      </button>
    );
  }
  
  return <span className={classes}>{text}</span>;
};

const SongRow = ({ song, onPlay }) => {
  return (
    <tr className="border-b border-gray-800 hover:bg-gray-900 transition-colors">
      <td className="px-4 py-3">
        <div className="flex items-center">
          {song.preview_file_exists && (
            <button 
              onClick={() => onPlay(song)}
              className="mr-3 text-gray-400 hover:text-white transition-colors"
              aria-label="Play preview"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24" 
                fill="currentColor" 
                className="w-5 h-5"
              >
                <path d="M8 5.14v14l11-7-11-7z" />
              </svg>
            </button>
          )}
          <div>
            <div className="font-medium text-white">{song.name}</div>
            <div className="text-sm text-gray-400">
              {song.producer && `Prod. ${song.producer}`}
              {song.features && song.producer && " • "}
              {song.features && `Feat. ${song.features}`}
            </div>
          </div>
        </div>
      </td>
      <td className="px-4 py-3">
        {song.era && <Badge text={song.era} type="era" />}
      </td>
      <td className="px-4 py-3">
        {song.quality && <Badge text={song.quality} type="quality" />}
      </td>
      <td className="px-4 py-3">
        {song.type && <Badge text={song.type} type="type" />}
      </td>
      <td className="px-4 py-3">
        {song.primary_tab_name && <Badge text={song.primary_tab_name} type="tab" />}
      </td>
      <td className="px-4 py-3 text-right">
        <Link 
          to={`/list?id=${song.id}`}
          className="inline-block text-blue-400 hover:text-blue-300 transition-colors"
        >
          Details
        </Link>
      </td>
    </tr>
  );
};

const AudioPlayer = ({ song, onClose }) => {
  if (!song) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 border-t border-gray-800 p-3">
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center">
          <button 
            onClick={onClose}
            className="mr-3 text-gray-400 hover:text-white transition-colors"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24" 
              fill="currentColor" 
              className="w-5 h-5"
            >
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
            </svg>
          </button>
          <div>
            <div className="font-medium text-white">{song.name}</div>
            <div className="text-sm text-gray-400">
              {song.producer && `Prod. ${song.producer}`}
            </div>
          </div>
        </div>
        <div className="flex-grow mx-6">
          <audio 
            controls
            autoPlay
            className="w-full" 
            src={song.preview_audio_url}
          >
            Your browser does not support the audio element.
          </audio>
        </div>
        <div className="text-sm text-gray-400">
          Preview
        </div>
      </div>
    </div>
  );
};

const FilterPanel = ({ filters, currentFilters, onApplyFilter, onRemoveFilter }) => {
  return (
    <div className="bg-gray-800 rounded-lg p-4 sticky top-4">
      <h2 className="text-lg font-medium text-white mb-4">Filters</h2>
      
      {/* Active filters */}
      {Object.entries(currentFilters).some(([key, value]) => value && key !== 'pagination') && (
        <div className="mb-4">
          <h3 className="text-sm font-medium text-gray-400 mb-2">Active Filters</h3>
          <div className="flex flex-wrap gap-2">
            {currentFilters.era && (
              <Badge 
                text={`Era: ${currentFilters.era}`} 
                type="filter" 
                onClick={() => onRemoveFilter('era')}
              />
            )}
            {currentFilters.quality && (
              <Badge 
                text={`Quality: ${currentFilters.quality}`} 
                type="filter" 
                onClick={() => onRemoveFilter('quality')}
              />
            )}
            {currentFilters.type && (
              <Badge 
                text={`Type: ${currentFilters.type}`} 
                type="filter" 
                onClick={() => onRemoveFilter('type')}
              />
            )}
            {currentFilters.sheet_tab && (
              <Badge 
                text={`Collection: ${filters.sheet_tabs.find(t => t.id === parseInt(currentFilters.sheet_tab))?.name || 'Unknown'}`} 
                type="filter" 
                onClick={() => onRemoveFilter('sheet_tab')}
              />
            )}
            {currentFilters.query && (
              <Badge 
                text={`Search: ${currentFilters.query}`} 
                type="filter" 
                onClick={() => onRemoveFilter('query')}
              />
            )}
            
            <button 
              className="text-xs text-red-400 hover:text-red-300 transition-colors"
              onClick={() => onRemoveFilter('all')}
            >
              Clear All
            </button>
          </div>
        </div>
      )}
      
      {/* Search */}
      <div className="mb-4">
        <label htmlFor="search" className="block text-sm font-medium text-gray-400 mb-1">
          Search
        </label>
        <div className="flex">
          <input
            type="text"
            id="search"
            className="bg-gray-700 text-white rounded-l px-3 py-2 w-full focus:outline-none focus:ring-1 focus:ring-blue-500"
            placeholder="Song name, producer..."
            value={currentFilters.query || ''}
            onChange={(e) => onApplyFilter('query', e.target.value)}
          />
          <button
            className="bg-blue-600 text-white px-4 rounded-r hover:bg-blue-700 transition-colors"
            onClick={() => {/* Search already applied on input change */}}
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24" 
              fill="currentColor" 
              className="w-5 h-5"
            >
              <path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Filter sections */}
      <div className="space-y-4">
        {/* Era filter */}
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-2">Era</h3>
          <div className="max-h-32 overflow-y-auto space-y-1">
            {filters.eras && filters.eras.map(era => (
              <div key={era} className="flex items-center">
                <input
                  type="radio"
                  id={`era-${era}`}
                  name="era"
                  className="mr-2"
                  checked={currentFilters.era === era}
                  onChange={() => onApplyFilter('era', era)}
                />
                <label htmlFor={`era-${era}`} className="text-sm text-gray-300">
                  {era}
                </label>
              </div>
            ))}
          </div>
        </div>
        
        {/* Quality filter */}
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-2">Quality</h3>
          <div className="max-h-32 overflow-y-auto space-y-1">
            {filters.qualities && filters.qualities.map(quality => (
              <div key={quality} className="flex items-center">
                <input
                  type="radio"
                  id={`quality-${quality}`}
                  name="quality"
                  className="mr-2"
                  checked={currentFilters.quality === quality}
                  onChange={() => onApplyFilter('quality', quality)}
                />
                <label htmlFor={`quality-${quality}`} className="text-sm text-gray-300">
                  {quality}
                </label>
              </div>
            ))}
          </div>
        </div>
        
        {/* Type filter */}
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-2">Type</h3>
          <div className="max-h-32 overflow-y-auto space-y-1">
            {filters.types && filters.types.map(type => (
              <div key={type} className="flex items-center">
                <input
                  type="radio"
                  id={`type-${type}`}
                  name="type"
                  className="mr-2"
                  checked={currentFilters.type === type}
                  onChange={() => onApplyFilter('type', type)}
                />
                <label htmlFor={`type-${type}`} className="text-sm text-gray-300">
                  {type}
                </label>
              </div>
            ))}
          </div>
        </div>
        
        {/* Collection filter */}
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-2">Collection</h3>
          <div className="max-h-48 overflow-y-auto space-y-1">
            {filters.sheet_tabs && filters.sheet_tabs.map(tab => (
              <div key={tab.id} className="flex items-center">
                <input
                  type="radio"
                  id={`tab-${tab.id}`}
                  name="sheet_tab"
                  className="mr-2"
                  checked={currentFilters.sheet_tab === tab.id.toString()}
                  onChange={() => onApplyFilter('sheet_tab', tab.id.toString())}
                />
                <label htmlFor={`tab-${tab.id}`} className="text-sm text-gray-300">
                  {tab.name}
                </label>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

const Pagination = ({ pagination, onPageChange }) => {
  const { current_page, total_pages } = pagination;
  
  const renderPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    
    let startPage = Math.max(1, current_page - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(total_pages, startPage + maxVisiblePages - 1);
    
    // Adjust if at the end
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    // First page
    if (startPage > 1) {
      pages.push(
        <button
          key="1"
          className="px-3 py-1 rounded text-sm text-gray-300 hover:bg-gray-700 transition-colors"
          onClick={() => onPageChange(1)}
        >
          1
        </button>
      );
      if (startPage > 2) {
        pages.push(
          <span key="ellipsis1" className="px-2 text-gray-500">…</span>
        );
      }
    }
    
    // Page numbers
    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          className={`px-3 py-1 rounded text-sm ${
            i === current_page
              ? 'bg-blue-600 text-white'
              : 'text-gray-300 hover:bg-gray-700'
          } transition-colors`}
          onClick={() => onPageChange(i)}
        >
          {i}
        </button>
      );
    }
    
    // Last page
    if (endPage < total_pages) {
      if (endPage < total_pages - 1) {
        pages.push(
          <span key="ellipsis2" className="px-2 text-gray-500">…</span>
        );
      }
      pages.push(
        <button
          key={total_pages}
          className="px-3 py-1 rounded text-sm text-gray-300 hover:bg-gray-700 transition-colors"
          onClick={() => onPageChange(total_pages)}
        >
          {total_pages}
        </button>
      );
    }
    
    return pages;
  };
  
  if (total_pages <= 1) return null;
  
  return (
    <div className="flex justify-center items-center my-6 gap-1">
      <button
        className="px-3 py-1 rounded text-sm text-gray-300 hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        onClick={() => onPageChange(current_page - 1)}
        disabled={current_page === 1}
      >
        ← Prev
      </button>
      
      <div className="flex items-center mx-2">
        {renderPageNumbers()}
      </div>
      
      <button
        className="px-3 py-1 rounded text-sm text-gray-300 hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        onClick={() => onPageChange(current_page + 1)}
        disabled={current_page === total_pages}
      >
        Next →
      </button>
    </div>
  );
};

const List = () => {
  const location = useLocation();
  const [data, setData] = useState({ songs: [], filters: { pagination: { current_page: 1, total_pages: 1 } } });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentFilters, setCurrentFilters] = useState({});
  const [currentPlaying, setCurrentPlaying] = useState(null);

  // Parse query parameters
  const parseQueryParams = useCallback(() => {
    const searchParams = new URLSearchParams(location.search);
    const params = {};
    
    for (const [key, value] of searchParams.entries()) {
      params[key] = value;
    }
    
    return params;
  }, [location.search]);

  // Fetch data from API
  const fetchData = useCallback(async (filters = {}) => {
    setLoading(true);
    try {
      const jsonData = await apiService.getSongs(filters);
      setData(jsonData);
      setCurrentFilters(jsonData.filters.current_filters);
    } catch (err) {
      console.error('Error fetching data:', err);
      const errorDetails = apiService.handleApiError(err);
      setError(errorDetails.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Apply filter and update URL
  const handleApplyFilter = useCallback((key, value) => {
    setCurrentFilters(prev => {
      const newFilters = { ...prev, [key]: value };
      
      // If changing filters, reset to page 1
      if (key !== 'page') {
        newFilters.page = 1;
      }
      
      // Update URL
      const queryParams = new URLSearchParams();
      Object.entries(newFilters).forEach(([k, v]) => {
        if (v) queryParams.append(k, v);
      });
      
      const newUrl = `${location.pathname}?${queryParams.toString()}`;
      window.history.pushState(null, '', newUrl);
      
      // Fetch new data
      fetchData(newFilters);
      
      return newFilters;
    });
  }, [fetchData, location.pathname]);

  // Remove filter
  const handleRemoveFilter = useCallback((key) => {
    setCurrentFilters(prev => {
      const newFilters = { ...prev };
      
      if (key === 'all') {
        // Clear all filters except pagination
        Object.keys(newFilters).forEach(k => {
          if (k !== 'pagination') delete newFilters[k];
        });
      } else {
        delete newFilters[key];
      }
      
      // Update URL
      const queryParams = new URLSearchParams();
      Object.entries(newFilters).forEach(([k, v]) => {
        if (v && k !== 'pagination') queryParams.append(k, v);
      });
      
      const newUrl = `${location.pathname}?${queryParams.toString()}`;
      window.history.pushState(null, '', newUrl);
      
      // Fetch new data
      fetchData(newFilters);
      
      return newFilters;
    });
  }, [fetchData, location.pathname]);

  // Change page
  const handlePageChange = useCallback((page) => {
    handleApplyFilter('page', page);
  }, [handleApplyFilter]);

  // Handle song play
  const handlePlay = useCallback((song) => {
    setCurrentPlaying(song);
  }, []);

  // Initial setup on component mount
  useEffect(() => {
    const initialFilters = parseQueryParams();
    setCurrentFilters(initialFilters);
    fetchData(initialFilters);
  }, [fetchData, parseQueryParams]);

  if (loading && !data.songs.length) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full border-t-transparent" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-900 text-white p-4 rounded">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-white">Song Library</h1>
        <Link to="/" className="text-blue-400 hover:text-blue-300">
          ← Back to Dashboard
        </Link>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filter sidebar */}
        <div className="lg:col-span-1">
          <FilterPanel 
            filters={data.filters} 
            currentFilters={currentFilters}
            onApplyFilter={handleApplyFilter}
            onRemoveFilter={handleRemoveFilter}
          />
        </div>
        
        {/* Song list */}
        <div className="lg:col-span-3">
          {/* Results info */}
          <div className="flex justify-between items-center mb-4">
            <p className="text-gray-400">
              Showing {data.filters.pagination?.total_items ? 
                `${Math.min(data.filters.pagination.items_per_page * (data.filters.pagination.current_page - 1) + 1, 
                  data.filters.pagination.total_items)} - 
                  ${Math.min(data.filters.pagination.items_per_page * data.filters.pagination.current_page, 
                  data.filters.pagination.total_items)} 
                  of ${data.filters.pagination.total_items}` 
                : '0'} songs
            </p>
          </div>
          
          {/* Song table */}
          <div className="bg-gray-800 rounded-lg overflow-hidden shadow">
            {data.songs && data.songs.length > 0 ? (
              <table className="min-w-full">
                <thead>
                  <tr className="bg-gray-900">
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Song</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Era</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Quality</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Type</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Collection</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider"></th>
                  </tr>
                </thead>
                <tbody>
                  {data.songs.map(song => (
                    <SongRow 
                      key={song.id} 
                      song={song} 
                      onPlay={handlePlay}
                    />
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-6 text-center text-gray-400">
                <p>No songs found matching your filters.</p>
                <button 
                  className="mt-2 text-blue-400 hover:text-blue-300"
                  onClick={() => handleRemoveFilter('all')}
                >
                  Clear all filters
                </button>
              </div>
            )}
          </div>
          
          {/* Pagination */}
          {data.filters.pagination && (
            <Pagination 
              pagination={data.filters.pagination} 
              onPageChange={handlePageChange}
            />
          )}
        </div>
      </div>
      
      {/* Audio player (fixed at bottom) */}
      <AudioPlayer 
        song={currentPlaying} 
        onClose={() => setCurrentPlaying(null)}
      />
    </div>
  );
};

export default List;