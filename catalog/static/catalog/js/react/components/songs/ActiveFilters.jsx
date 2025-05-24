import React from 'react';
import { X } from 'lucide-react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';

const FilterBadge = ({ label, value, onRemove }) => {
  return (
    <Badge variant="secondary" className="mr-2 mb-2 bg-white/10 text-white flex items-center gap-1">
      <span>{label}: {value}</span>
      <button 
        onClick={onRemove}
        className="ml-1 rounded-full hover:bg-white/20 transition-colors p-0.5"
        aria-label={`Remove ${label} filter`}
      >
        <X className="h-3 w-3" />
      </button>
    </Badge>
  );
};

const ActiveFilters = ({
  eraFilter,
  typeFilter,
  tabFilter,
  qualityFilter,
  producerFilter,
  featuresFilter,
  yearFilter,
  popularityFilter,
  activeFilters,
  setEraFilter,
  setTypeFilter,
  setTabFilter,
  setQualityFilter,
  setProducerFilter,
  setFeaturesFilter,
  setYearFilter,
  setPopularityFilter,
  clearFilters,
}) => {
  if (activeFilters === 0) {
    return null;
  }

  return (
    <div className="mb-4 flex flex-wrap items-center">
      <div className="mr-2 text-sm text-white/70 mb-2">Active filters:</div>
      
      <div className="flex flex-wrap flex-1">
        {eraFilter && (
          <FilterBadge 
            label="Era" 
            value={eraFilter} 
            onRemove={() => setEraFilter('')} 
          />
        )}
        
        {typeFilter && (
          <FilterBadge 
            label="Type" 
            value={typeFilter} 
            onRemove={() => setTypeFilter('')} 
          />
        )}
        
        {tabFilter && (
          <FilterBadge 
            label="Tab" 
            value={tabFilter} 
            onRemove={() => setTabFilter('')} 
          />
        )}
        
        {qualityFilter && (
          <FilterBadge 
            label="Quality" 
            value={qualityFilter} 
            onRemove={() => setQualityFilter('')} 
          />
        )}
        
        {producerFilter && (
          <FilterBadge 
            label="Producer" 
            value={producerFilter} 
            onRemove={() => setProducerFilter('')} 
          />
        )}
        
        {featuresFilter && (
          <FilterBadge 
            label="Features" 
            value={featuresFilter} 
            onRemove={() => setFeaturesFilter('')} 
          />
        )}
        
        {yearFilter && (
          <FilterBadge 
            label="Year" 
            value={yearFilter} 
            onRemove={() => setYearFilter('')} 
          />
        )}
        
        {popularityFilter && (
          <FilterBadge 
            label="Popularity" 
            value={popularityFilter} 
            onRemove={() => setPopularityFilter('')} 
          />
        )}
      </div>
      
      <Button 
        variant="ghost" 
        size="sm" 
        onClick={clearFilters}
        className="mb-2 text-white/80 hover:text-white hover:bg-white/10"
      >
        Clear All
      </Button>
    </div>
  );
};

export default ActiveFilters;