import React from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '../ui/card';
import { Button } from '../ui/button';
import { buildUrl } from '../../lib/utils';

const FilterPanel = ({ filters, showFilters }) => {
  // Get current filter values
  const { current_filters } = filters;
  
  // Apply filters handler
  const handleApplyFilters = (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    
    // Build URL with params
    const params = {
      era: formData.get('era'),
      sheet_tab: formData.get('sheet_tab'),
      quality: formData.get('quality'),
      type: formData.get('type'),
      producer: formData.get('producer'),
      q: formData.get('q'),
      react: 'true', // Keep the React version
    };
    
    // Navigate to the URL with filters
    window.location.href = buildUrl('/catalog/songs/', params);
  };
  
  // Clear filters handler
  const handleClearFilters = () => {
    window.location.href = buildUrl('/catalog/songs/', { react: 'true' });
  };
  
  if (!showFilters) {
    return null;
  }

  return (
    <Card className="mb-6 carti-slide-up carti-glass-darker">
      <CardHeader>
        <CardTitle>Filter Songs</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleApplyFilters} className="grid gap-4 md:grid-cols-3">
          {/* Era filter */}
          <div className="flex flex-col space-y-1.5">
            <label htmlFor="era" className="text-sm font-medium">
              Era
            </label>
            <select
              id="era"
              name="era"
              className="rounded-md border border-white/10 bg-black/20 px-3 py-2"
              defaultValue={current_filters.era}
            >
              <option value="">All Eras</option>
              {filters.eras.map((era) => (
                era && (
                  <option key={era} value={era}>
                    {era}
                  </option>
                )
              ))}
            </select>
          </div>
          
          {/* Sheet Tab filter */}
          <div className="flex flex-col space-y-1.5">
            <label htmlFor="sheet_tab" className="text-sm font-medium">
              Sheet Tab
            </label>
            <select
              id="sheet_tab"
              name="sheet_tab"
              className="rounded-md border border-white/10 bg-black/20 px-3 py-2"
              defaultValue={current_filters.sheet_tab}
            >
              <option value="">All Tabs</option>
              {filters.sheet_tabs.map((tab) => (
                <option key={tab.id} value={tab.id}>
                  {tab.name}
                </option>
              ))}
            </select>
          </div>
          
          {/* Quality filter */}
          <div className="flex flex-col space-y-1.5">
            <label htmlFor="quality" className="text-sm font-medium">
              Quality
            </label>
            <select
              id="quality"
              name="quality"
              className="rounded-md border border-white/10 bg-black/20 px-3 py-2"
              defaultValue={current_filters.quality}
            >
              <option value="">All Qualities</option>
              {filters.qualities.map((quality) => (
                quality && (
                  <option key={quality} value={quality}>
                    {quality}
                  </option>
                )
              ))}
            </select>
          </div>
          
          {/* Type filter */}
          <div className="flex flex-col space-y-1.5">
            <label htmlFor="type" className="text-sm font-medium">
              Type
            </label>
            <select
              id="type"
              name="type"
              className="rounded-md border border-white/10 bg-black/20 px-3 py-2"
              defaultValue={current_filters.type}
            >
              <option value="">All Types</option>
              {filters.types.map((type) => (
                type && (
                  <option key={type} value={type}>
                    {type}
                  </option>
                )
              ))}
            </select>
          </div>
          
          {/* Producer filter */}
          <div className="flex flex-col space-y-1.5">
            <label htmlFor="producer" className="text-sm font-medium">
              Producer
            </label>
            <select
              id="producer"
              name="producer"
              className="rounded-md border border-white/10 bg-black/20 px-3 py-2"
              defaultValue={current_filters.producer}
            >
              <option value="">All Producers</option>
              {filters.top_producers.map((producer) => (
                <option key={producer} value={producer}>
                  {producer}
                </option>
              ))}
            </select>
          </div>
          
          {/* Search query */}
          <div className="flex flex-col space-y-1.5">
            <label htmlFor="q" className="text-sm font-medium">
              Search
            </label>
            <input
              type="text"
              id="q"
              name="q"
              className="rounded-md border border-white/10 bg-black/20 px-3 py-2"
              placeholder="Search songs, producers, features..."
              defaultValue={current_filters.query}
            />
          </div>
          
          <div className="col-span-full flex justify-end gap-2 mt-4">
            <Button 
              type="button" 
              variant="outline"
              onClick={handleClearFilters}
            >
              Clear Filters
            </Button>
            <Button type="submit" variant="carti">
              Apply Filters
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default FilterPanel;