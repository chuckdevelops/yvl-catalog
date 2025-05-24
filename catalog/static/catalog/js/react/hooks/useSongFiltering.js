import { useState, useEffect, useMemo } from 'react';

export const useSongFiltering = (initialSongs = []) => {
  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [eraFilter, setEraFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [tabFilter, setTabFilter] = useState('');
  const [qualityFilter, setQualityFilter] = useState('');
  const [producerFilter, setProducerFilter] = useState('');
  const [featuresFilter, setFeaturesFilter] = useState('');
  const [yearFilter, setYearFilter] = useState('');
  const [popularityFilter, setPopularityFilter] = useState('');
  
  // Sort state
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');
  
  // UI state
  const [isFilterExpanded, setIsFilterExpanded] = useState(false);
  
  // Calculate active filters count
  const activeFilters = useMemo(() => {
    let count = 0;
    if (searchTerm) count++;
    if (eraFilter) count++;
    if (typeFilter) count++;
    if (tabFilter) count++;
    if (qualityFilter) count++;
    if (producerFilter) count++;
    if (featuresFilter) count++;
    if (yearFilter) count++;
    if (popularityFilter) count++;
    return count;
  }, [
    searchTerm, 
    eraFilter, 
    typeFilter, 
    tabFilter, 
    qualityFilter, 
    producerFilter, 
    featuresFilter, 
    yearFilter, 
    popularityFilter
  ]);
  
  // Extract unique values for filter options
  const uniqueEras = useMemo(() => {
    const eras = new Set();
    initialSongs.forEach(song => {
      if (song.era) eras.add(song.era);
    });
    return Array.from(eras).sort();
  }, [initialSongs]);
  
  const uniqueTypes = useMemo(() => {
    const types = new Set();
    initialSongs.forEach(song => {
      if (song.type) types.add(song.type);
    });
    return Array.from(types).sort();
  }, [initialSongs]);
  
  const uniqueTabs = useMemo(() => {
    const tabs = new Set();
    initialSongs.forEach(song => {
      if (song.primary_tab_name) tabs.add(song.primary_tab_name);
    });
    return Array.from(tabs).sort();
  }, [initialSongs]);
  
  const uniqueQualities = useMemo(() => {
    const qualities = new Set();
    initialSongs.forEach(song => {
      if (song.quality) qualities.add(song.quality);
    });
    return Array.from(qualities).sort();
  }, [initialSongs]);
  
  const uniqueProducers = useMemo(() => {
    const producers = new Set();
    initialSongs.forEach(song => {
      if (song.producer) producers.add(song.producer);
    });
    return Array.from(producers).sort();
  }, [initialSongs]);
  
  const uniqueFeatures = useMemo(() => {
    const features = new Set();
    initialSongs.forEach(song => {
      if (song.features) {
        song.features.split(',').forEach(feature => {
          features.add(feature.trim());
        });
      }
    });
    return Array.from(features).sort();
  }, [initialSongs]);
  
  const uniqueYears = useMemo(() => {
    const years = new Set();
    initialSongs.forEach(song => {
      if (song.year) years.add(song.year);
    });
    return Array.from(years).sort((a, b) => b - a); // Sort years descending
  }, [initialSongs]);
  
  const uniquePopularity = useMemo(() => {
    const popularities = new Set();
    initialSongs.forEach(song => {
      if (song.popularity) popularities.add(song.popularity);
    });
    return Array.from(popularities).sort();
  }, [initialSongs]);
  
  // Filter and sort songs
  const filteredAndSortedSongs = useMemo(() => {
    // First, apply all filters
    let result = initialSongs.filter(song => {
      // Search term filter (search in multiple fields)
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        const nameMatch = song.name?.toLowerCase().includes(searchLower);
        const producerMatch = song.producer?.toLowerCase().includes(searchLower);
        const featuresMatch = song.features?.toLowerCase().includes(searchLower);
        const noteMatch = song.notes?.toLowerCase().includes(searchLower);
        
        if (!nameMatch && !producerMatch && !featuresMatch && !noteMatch) {
          return false;
        }
      }
      
      // Era filter
      if (eraFilter && song.era !== eraFilter) {
        return false;
      }
      
      // Type filter
      if (typeFilter && song.type !== typeFilter) {
        return false;
      }
      
      // Tab filter
      if (tabFilter && song.primary_tab_name !== tabFilter) {
        return false;
      }
      
      // Quality filter
      if (qualityFilter && song.quality !== qualityFilter) {
        return false;
      }
      
      // Producer filter
      if (producerFilter && song.producer !== producerFilter) {
        return false;
      }
      
      // Features filter
      if (featuresFilter && (!song.features || !song.features.toLowerCase().includes(featuresFilter.toLowerCase()))) {
        return false;
      }
      
      // Year filter
      if (yearFilter && song.year !== yearFilter) {
        return false;
      }
      
      // Popularity filter
      if (popularityFilter && song.popularity !== popularityFilter) {
        return false;
      }
      
      // If passed all filters
      return true;
    });
    
    // Then, apply sorting
    result.sort((a, b) => {
      // Handle null values
      const aValue = a[sortField] ?? '';
      const bValue = b[sortField] ?? '';
      
      // Compare the values
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        if (sortDirection === 'asc') {
          return aValue.localeCompare(bValue);
        } else {
          return bValue.localeCompare(aValue);
        }
      } else {
        // If not strings, do simple comparison
        if (sortDirection === 'asc') {
          return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
        } else {
          return bValue < aValue ? -1 : bValue > aValue ? 1 : 0;
        }
      }
    });
    
    return result;
  }, [
    initialSongs,
    searchTerm,
    eraFilter,
    typeFilter,
    tabFilter,
    qualityFilter,
    producerFilter,
    featuresFilter,
    yearFilter,
    popularityFilter,
    sortField,
    sortDirection
  ]);
  
  // Function to handle sorting
  const handleSort = (field) => {
    if (sortField === field) {
      // Toggle direction if already sorting by this field
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new field and default to ascending
      setSortField(field);
      setSortDirection('asc');
    }
  };
  
  // Function to toggle filter panel
  const toggleFilters = () => {
    setIsFilterExpanded(!isFilterExpanded);
  };
  
  // Function to clear all filters
  const clearFilters = () => {
    setSearchTerm('');
    setEraFilter('');
    setTypeFilter('');
    setTabFilter('');
    setQualityFilter('');
    setProducerFilter('');
    setFeaturesFilter('');
    setYearFilter('');
    setPopularityFilter('');
  };
  
  // Auto-expand filters if any are active
  useEffect(() => {
    if (activeFilters > 0 && !isFilterExpanded) {
      setIsFilterExpanded(true);
    }
  }, [activeFilters, isFilterExpanded]);
  
  return {
    // Filter states
    searchTerm,
    setSearchTerm,
    eraFilter,
    setEraFilter,
    typeFilter,
    setTypeFilter,
    tabFilter,
    setTabFilter,
    qualityFilter,
    setQualityFilter,
    producerFilter,
    setProducerFilter,
    featuresFilter,
    setFeaturesFilter,
    yearFilter,
    setYearFilter,
    popularityFilter,
    setPopularityFilter,
    
    // Sort states
    sortField,
    sortDirection,
    
    // UI states
    isFilterExpanded,
    setIsFilterExpanded,
    
    // Derived data
    activeFilters,
    filteredAndSortedSongs,
    uniqueEras,
    uniqueTypes,
    uniqueTabs,
    uniqueQualities,
    uniqueProducers,
    uniqueFeatures,
    uniqueYears,
    uniquePopularity,
    
    // Actions
    clearFilters,
    toggleFilters,
    handleSort
  };
};