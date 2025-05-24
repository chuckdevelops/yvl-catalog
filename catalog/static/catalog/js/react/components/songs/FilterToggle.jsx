import React from 'react';
import { Button } from '../ui/button';

const FilterToggle = ({ showFilters, setShowFilters }) => {
  return (
    <div className="mb-4">
      <Button
        variant="glass"
        className="carti-hover-effect"
        onClick={() => setShowFilters(!showFilters)}
      >
        {showFilters ? 'Hide Filters' : 'Show Filters'}
      </Button>
    </div>
  );
};

export default FilterToggle;