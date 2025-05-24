import React from 'react';
import { createRoot } from 'react-dom/client';
import './styles/index.css';

// Filter Toggle Component
function FilterToggle({ showFilters, setShowFilters }) {
  return (
    <div className="mb-4">
      <button 
        className="btn btn-glass hover-scale flex items-center gap-2" 
        onClick={() => setShowFilters(!showFilters)}
      >
        <span>
          {showFilters ? 
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 9l-7 7-7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            : 
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M5 12h14M5 5h14M5 19h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          }
        </span>
        {showFilters ? 'Hide Filters' : 'Show Filters'}
      </button>
    </div>
  );
}

// Filter Panel Component
function FilterPanel({ filters, showFilters, onApplyFilters }) {
  if (!showFilters) return null;

  const currentFilters = filters.current_filters || {};

  const handleSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const formValues = {
      era: formData.get('era'),
      sheet_tab: formData.get('sheet_tab'),
      quality: formData.get('quality'),
      type: formData.get('type'),
      producer: formData.get('producer'),
      q: formData.get('q')
    };
    onApplyFilters(formValues);
  };

  return (
    <div className="card glass slide-up mb-6 card-glow rounded-md">
      <div className="card-header">
        <h2 className="text-xl font-bold">Filter Songs</h2>
        <div className="flex items-center">
          <span className="badge badge-glass">Advanced Filter</span>
        </div>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Era filter */}
          <div className="form-group">
            <label htmlFor="era" className="form-label flex items-center">
              <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <circle cx="12" cy="12" r="4" stroke="currentColor" strokeWidth="2"/>
              </svg>
              Era
            </label>
            <select 
              id="era" 
              name="era" 
              className="form-control"
              defaultValue={currentFilters.era || ''}
            >
              <option value="">All Eras</option>
              {(filters.eras || []).map(era => (
                era && <option key={era} value={era}>{era}</option>
              ))}
            </select>
          </div>
          
          {/* Sheet Tab filter */}
          <div className="form-group">
            <label htmlFor="sheet_tab" className="form-label flex items-center">
              <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <path d="M12 8v8M8 12h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Sheet Tab
            </label>
            <select 
              id="sheet_tab" 
              name="sheet_tab" 
              className="form-control"
              defaultValue={currentFilters.sheet_tab || ''}
            >
              <option value="">All Tabs</option>
              {(filters.sheet_tabs || []).map(tab => (
                <option key={tab.id} value={tab.id}>{tab.name}</option>
              ))}
            </select>
          </div>
          
          {/* Quality filter */}
          <div className="form-group">
            <label htmlFor="quality" className="form-label flex items-center">
              <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" stroke="currentColor" strokeWidth="2"/>
                <path d="M15 8h-6v4h4v4h-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Quality
            </label>
            <select 
              id="quality" 
              name="quality" 
              className="form-control"
              defaultValue={currentFilters.quality || ''}
            >
              <option value="">All Qualities</option>
              {(filters.qualities || []).map(quality => (
                quality && <option key={quality} value={quality}>{quality}</option>
              ))}
            </select>
          </div>
          
          {/* Type filter */}
          <div className="form-group">
            <label htmlFor="type" className="form-label flex items-center">
              <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 11h18M12 3v18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Type
            </label>
            <select 
              id="type" 
              name="type" 
              className="form-control"
              defaultValue={currentFilters.type || ''}
            >
              <option value="">All Types</option>
              {(filters.types || []).map(type => (
                type && <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>
          
          {/* Producer filter */}
          <div className="form-group">
            <label htmlFor="producer" className="form-label flex items-center">
              <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 3h6m-3-2v4m5 1a7 7 0 11-10 0" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <path d="M8 21h8M12 12v9" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Producer
            </label>
            <select 
              id="producer" 
              name="producer" 
              className="form-control"
              defaultValue={currentFilters.producer || ''}
            >
              <option value="">All Producers</option>
              {(filters.top_producers || []).map(producer => (
                <option key={producer} value={producer}>{producer}</option>
              ))}
            </select>
          </div>
          
          {/* Search query */}
          <div className="form-group">
            <label htmlFor="q" className="form-label flex items-center">
              <svg className="w-4 h-4 mr-2" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              Search
            </label>
            <input 
              type="text" 
              id="q" 
              name="q" 
              className="form-control" 
              placeholder="Search songs, producers, features..."
              defaultValue={currentFilters.query || ''}
            />
          </div>
          
          <div className="flex justify-between col-span-full mt-4 gap-3">
            <button 
              type="button" 
              className="btn btn-glass hover-scale"
              onClick={() => window.location.href = '/catalog/songs/'}
            >
              Clear Filters
            </button>
            <button type="submit" className="btn btn-red hover-scale">
              Apply Filters
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Song Table Component
function SongTable({ songs }) {
  if (!songs || songs.length === 0) {
    return (
      <div className="text-center p-4 darker-glass rounded-md">
        <h2 className="text-xl font-bold mb-2">No songs found</h2>
        <p>Try adjusting your filters</p>
      </div>
    );
  }

  // Handle song click - go to song detail page
  const handleSongClick = (songId) => {
    window.location.href = `/catalog/songs/${songId}/`;
  };
  
  // Format song type for display
  const formatType = (type) => {
    if (!type) return '';
    switch (type.toLowerCase()) {
      case 'cdq': return 'CDQ';
      case 'lq': return 'LQ';
      case 'studio session': return 'Studio Session';
      case 'snippet': return 'Snippet';
      default: return type;
    }
  };

  return (
    <div className="card glass scale-in card-glow rounded-md overflow-hidden">
      <div className="card-header">
        <h2 className="text-xl font-bold">Songs</h2>
        <span className="badge badge-red">{songs.length} songs</span>
      </div>
      <div className="card-body p-0">
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead className="darker-glass">
              <tr>
                <th className="text-white/90">Name</th>
                <th className="text-white/90 hidden md:table-cell">Era</th>
                <th className="text-white/90 hidden md:table-cell">Sheet Tab</th>
                <th className="text-white/90 hidden sm:table-cell">Type</th>
                <th className="text-white/90 hidden lg:table-cell">Quality</th>
                <th className="text-white/90 hidden sm:table-cell">Leak Date</th>
              </tr>
            </thead>
            <tbody>
              {songs.map(song => (
                <tr 
                  key={song.id} 
                  onClick={() => handleSongClick(song.id)}
                  className="hover-scale hover:bg-white/5 border-white/20 transition-all"
                  style={{ cursor: 'pointer' }}
                >
                  <td>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{song.name}</span>
                    </div>
                    <div className="md:hidden mt-1 space-y-1">
                      <div className="text-xs text-white/70">
                        {song.era || <em className="text-white/50">Unknown Era</em>}
                      </div>
                      <div className="text-xs text-white/70">
                        {formatType(song.type)} • {song.quality}
                      </div>
                    </div>
                  </td>
                  <td className="text-white/90 hidden md:table-cell">
                    <div className="badge badge-primary">{song.era || 'Unknown'}</div>
                  </td>
                  <td className="text-white/90 hidden md:table-cell">
                    {song.primary_tab_name || 'Unknown'}
                  </td>
                  <td className="text-white/90 hidden sm:table-cell">
                    <div className="badge badge-glass">{formatType(song.type)}</div>
                  </td>
                  <td className="text-white/90 hidden lg:table-cell">{song.quality || ''}</td>
                  <td className="text-white/90 hidden sm:table-cell">{song.leak_date || ''}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// Main App Component
function App({ songs, filters }) {
  const [showFilters, setShowFilters] = React.useState(false);
  
  // Handle applying filters
  const handleApplyFilters = (filterValues) => {
    // Build URL with filter parameters
    const searchParams = new URLSearchParams();
    
    Object.entries(filterValues).forEach(([key, value]) => {
      if (value) {
        searchParams.set(key, value);
      }
    });
    
    // Navigate to filtered URL
    window.location.href = `/catalog/songs/?${searchParams.toString()}`;
  };
  
  return (
    <div className="container fade-in px-4 py-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <div className="flex flex-wrap items-center justify-between mb-2">
          <h1 className="text-3xl font-bold uppercase text-glow">Playboi Carti Catalog</h1>
          <a 
            href="/catalog/songs/" 
            className="btn btn-glass hover-scale ml-2"
          >
            <svg className="w-4 h-4 mr-2 inline-block" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 4L4 8l8 4 8-4-8-4z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
              <path d="M4 12l8 4 8-4M4 16l8 4 8-4" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"/>
            </svg>
            Standard View
          </a>
        </div>
        <div className="flex flex-wrap items-center justify-between">
          <p className="opacity-70">Explore the complete collection of songs</p>
          <div className="flex items-center gap-2 mt-2 sm:mt-0">
            <div className="badge badge-primary">
              {songs.length} Songs
            </div>
            {Object.values(filters.current_filters || {}).some(v => v) && (
              <div className="badge badge-red">
                Filtered Results
              </div>
            )}
          </div>
        </div>
      </div>
      
      <FilterToggle 
        showFilters={showFilters} 
        setShowFilters={setShowFilters} 
      />
      
      <FilterPanel 
        filters={filters} 
        showFilters={showFilters} 
        onApplyFilters={handleApplyFilters} 
      />
      
      <SongTable songs={songs} />
      
      {/* Pagination */}
      {filters.pagination && filters.pagination.total_pages > 1 && (
        <div className="flex justify-between items-center mt-4 p-4 glass card-glow rounded-md">
          <div className="text-white/80">
            Page {filters.pagination.current_page} of {filters.pagination.total_pages}
          </div>
          <div className="flex gap-3">
            <button 
              className="btn btn-glass hover-scale"
              disabled={filters.pagination.current_page === 1}
              onClick={() => {
                const url = new URL(window.location);
                url.searchParams.set('page', filters.pagination.current_page - 1);
                window.location.href = url.toString();
              }}
            >
              <svg className="w-4 h-4 mr-1" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M15 18l-6-6 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Previous
            </button>
            <button 
              className="btn btn-glass hover-scale"
              disabled={filters.pagination.current_page === filters.pagination.total_pages}
              onClick={() => {
                const url = new URL(window.location);
                url.searchParams.set('page', filters.pagination.current_page + 1);
                window.location.href = url.toString();
              }}
            >
              Next
              <svg className="w-4 h-4 ml-1" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 18l6-6-6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// Initialize React App
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('react-song-list-container');
  
  if (!container) {
    console.error('React container not found!');
    return;
  }
  
  try {
    // Parse data from data attributes
    const songsJson = container.getAttribute('data-songs');
    const filtersJson = container.getAttribute('data-filters');
    
    let songs = [];
    let filters = {};
    
    try {
      if (songsJson) songs = JSON.parse(songsJson);
      if (filtersJson) filters = JSON.parse(filtersJson);
    } catch (parseError) {
      console.error('Error parsing JSON data:', parseError);
    }
    
    // Render React component
    const root = createRoot(container);
    root.render(
      <React.StrictMode>
        <App songs={songs} filters={filters} />
      </React.StrictMode>
    );
    
  } catch (error) {
    console.error('Error initializing React app:', error);
    container.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
  }
});