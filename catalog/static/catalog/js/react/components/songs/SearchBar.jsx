import React, { useState } from 'react';
import { Search, X } from 'lucide-react';

const SearchBar = ({ searchTerm, setSearchTerm }) => {
  const [localSearchTerm, setLocalSearchTerm] = useState(searchTerm || '');

  const handleSubmit = (e) => {
    e.preventDefault();
    setSearchTerm(localSearchTerm);
  };

  const clearSearch = () => {
    setLocalSearchTerm('');
    setSearchTerm('');
  };

  return (
    <form 
      onSubmit={handleSubmit} 
      className="relative mb-4 glass rounded-lg overflow-hidden"
    >
      <div className="flex items-center px-4 py-2">
        <Search className="h-5 w-5 text-white opacity-70" />
        <input
          type="text"
          placeholder="Search songs, producers, features..."
          className="flex-1 bg-transparent border-0 outline-none focus:ring-0 text-white px-3 py-2"
          value={localSearchTerm}
          onChange={(e) => setLocalSearchTerm(e.target.value)}
        />
        {localSearchTerm && (
          <button
            type="button"
            onClick={clearSearch}
            className="text-white/70 hover:text-white"
            aria-label="Clear search"
          >
            <X className="h-5 w-5" />
          </button>
        )}
        <button
          type="submit"
          className="ml-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-md transition-colors"
        >
          Search
        </button>
      </div>
    </form>
  );
};

export default SearchBar;