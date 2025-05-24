
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { FitPicsFilters } from '@/types/fitpics';
import { eras, picTypes, qualities } from '@/data/fitpics';

interface FitPicsFiltersProps {
  filters: FitPicsFilters;
  onFilterChange: (name: keyof FitPicsFilters, value: string | number) => void;
  onClearFilters: () => void;
}

const FitPicsFilterComponent = ({ 
  filters, 
  onFilterChange, 
  onClearFilters 
}: FitPicsFiltersProps) => {
  return (
    <Card className="mb-6">
      <CardContent className="pt-6">
        <h3 className="text-xl font-semibold mb-4">Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label htmlFor="era-filter" className="block text-sm font-medium mb-2">Era</label>
            <Select
              value={filters.era}
              onValueChange={(value) => onFilterChange('era', value)}
            >
              <SelectTrigger id="era-filter">
                <SelectValue placeholder="All Eras" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Eras</SelectItem>
                {eras.map(era => (
                  <SelectItem key={era} value={era}>{era}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label htmlFor="type-filter" className="block text-sm font-medium mb-2">Type</label>
            <Select
              value={filters.type}
              onValueChange={(value) => onFilterChange('type', value)}
            >
              <SelectTrigger id="type-filter">
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {picTypes.map(type => (
                  <SelectItem key={type} value={type}>{type}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label htmlFor="quality-filter" className="block text-sm font-medium mb-2">Quality</label>
            <Select
              value={filters.quality}
              onValueChange={(value) => onFilterChange('quality', value)}
            >
              <SelectTrigger id="quality-filter">
                <SelectValue placeholder="All Qualities" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Qualities</SelectItem>
                {qualities.map(quality => (
                  <SelectItem key={quality} value={quality}>{quality}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label htmlFor="search" className="block text-sm font-medium mb-2">Search</label>
            <Input
              id="search"
              value={filters.query}
              onChange={(e) => onFilterChange('query', e.target.value)}
              placeholder="Search fit pics..."
            />
          </div>
          
          <div className="md:col-span-4 flex items-center gap-2 mt-2">
            <Button onClick={() => onFilterChange('page', 1)}>Apply Filters</Button>
            {(filters.era || filters.type || filters.quality || filters.query) && (
              <Button variant="outline" onClick={onClearFilters}>Clear Filters</Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default FitPicsFilterComponent;
