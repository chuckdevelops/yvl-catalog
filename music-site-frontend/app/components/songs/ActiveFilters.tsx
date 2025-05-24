
import { X } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface ActiveFiltersProps {
  eraFilter: string;
  typeFilter: string;
  tabFilter: string;
  qualityFilter: string;
  producerFilter: string;
  featuresFilter: string;
  yearFilter: string;
  popularityFilter: string;
  activeFilters: number;
  setEraFilter: (value: string) => void;
  setTypeFilter: (value: string) => void;
  setTabFilter: (value: string) => void;
  setQualityFilter: (value: string) => void;
  setProducerFilter: (value: string) => void;
  setFeaturesFilter: (value: string) => void;
  setYearFilter: (value: string) => void;
  setPopularityFilter: (value: string) => void;
  clearFilters: () => void;
}

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
  clearFilters
}: ActiveFiltersProps) => {
  if (activeFilters === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {eraFilter && (
        <Badge className="bg-white/10 text-white hover:bg-white/15 flex items-center gap-1 pr-1">
          <span>Era: {eraFilter}</span>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-5 w-5 p-0 hover:bg-white/20 rounded-full"
            onClick={() => setEraFilter('')}
          >
            <X className="h-3 w-3" />
          </Button>
        </Badge>
      )}
      {typeFilter && (
        <Badge className="bg-white/10 text-white hover:bg-white/15 flex items-center gap-1 pr-1">
          <span>Type: {typeFilter}</span>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-5 w-5 p-0 hover:bg-white/20 rounded-full"
            onClick={() => setTypeFilter('')}
          >
            <X className="h-3 w-3" />
          </Button>
        </Badge>
      )}
      {tabFilter && (
        <Badge className="bg-white/10 text-white hover:bg-white/15 flex items-center gap-1 pr-1">
          <span>Tab: {tabFilter}</span>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-5 w-5 p-0 hover:bg-white/20 rounded-full"
            onClick={() => setTabFilter('')}
          >
            <X className="h-3 w-3" />
          </Button>
        </Badge>
      )}
      {qualityFilter && (
        <Badge className="bg-white/10 text-white hover:bg-white/15 flex items-center gap-1 pr-1">
          <span>Quality: {qualityFilter}</span>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-5 w-5 p-0 hover:bg-white/20 rounded-full"
            onClick={() => setQualityFilter('')}
          >
            <X className="h-3 w-3" />
          </Button>
        </Badge>
      )}
      {producerFilter && (
        <Badge className="bg-white/10 text-white hover:bg-white/15 flex items-center gap-1 pr-1">
          <span>Producer: {producerFilter}</span>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-5 w-5 p-0 hover:bg-white/20 rounded-full"
            onClick={() => setProducerFilter('')}
          >
            <X className="h-3 w-3" />
          </Button>
        </Badge>
      )}
      {featuresFilter && (
        <Badge className="bg-white/10 text-white hover:bg-white/15 flex items-center gap-1 pr-1">
          <span>Features: {featuresFilter === "null" ? "None" : featuresFilter}</span>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-5 w-5 p-0 hover:bg-white/20 rounded-full"
            onClick={() => setFeaturesFilter('')}
          >
            <X className="h-3 w-3" />
          </Button>
        </Badge>
      )}
      {yearFilter && (
        <Badge className="bg-white/10 text-white hover:bg-white/15 flex items-center gap-1 pr-1">
          <span>Year: {yearFilter}</span>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-5 w-5 p-0 hover:bg-white/20 rounded-full"
            onClick={() => setYearFilter('')}
          >
            <X className="h-3 w-3" />
          </Button>
        </Badge>
      )}
      {popularityFilter && (
        <Badge className="bg-white/10 text-white hover:bg-white/15 flex items-center gap-1 pr-1">
          <span>Popularity: {popularityFilter}</span>
          <Button 
            variant="ghost" 
            size="icon" 
            className="h-5 w-5 p-0 hover:bg-white/20 rounded-full"
            onClick={() => setPopularityFilter('')}
          >
            <X className="h-3 w-3" />
          </Button>
        </Badge>
      )}
      {activeFilters > 1 && (
        <Button
          variant="outline"
          size="sm"
          className="bg-transparent border-white/20 text-white hover:bg-white/10 text-xs h-7"
          onClick={clearFilters}
        >
          Clear All
        </Button>
      )}
    </div>
  );
};

export default ActiveFilters;
