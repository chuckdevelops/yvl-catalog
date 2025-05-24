
import React from 'react';
import { FilterX, Disc, Volume2, Info, Music, Tag, Star, Calendar, Clock } from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';

interface FilterPanelProps {
  eraFilter: string;
  typeFilter: string;
  tabFilter: string;
  qualityFilter: string;
  producerFilter: string;
  featuresFilter: string;
  yearFilter: string;
  popularityFilter: string;
  uniqueEras: string[];
  uniqueTypes: string[];
  uniqueTabs: string[];
  uniqueQualities: string[];
  uniqueProducers: string[];
  uniqueFeatures: string[];
  uniqueYears: string[];
  uniquePopularity: string[];
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

// Format song type for display
const formatType = (type: string) => {
  switch (type.toLowerCase()) {
    case 'cdq':
      return 'CDQ';
    case 'lq':
      return 'LQ';
    case 'studio session':
      return 'Studio Session';
    case 'snippet':
      return 'Snippet';
    default:
      return type;
  }
};

const FilterPanel: React.FC<FilterPanelProps> = ({
  eraFilter,
  typeFilter,
  tabFilter,
  qualityFilter,
  producerFilter,
  featuresFilter,
  yearFilter,
  popularityFilter,
  uniqueEras,
  uniqueTypes,
  uniqueTabs,
  uniqueQualities,
  uniqueProducers,
  uniqueFeatures,
  uniqueYears,
  uniquePopularity,
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
}) => {
  return (
    <Card className="bg-black border border-white/20 text-white scale-in">
      <CardHeader>
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-white">Filters</h2>
          {activeFilters > 0 && (
            <Button onClick={clearFilters} variant="outline" size="sm" className="border-white/20 text-white hover:bg-white/10">
              <FilterX className="mr-2 h-4 w-4" />
              Clear All Filters
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Era Filter */}
          <div className="space-y-2">
            <Label htmlFor="era-filter" className="flex items-center">
              <Disc className="mr-2 h-4 w-4" />
              Era
            </Label>
            <Select value={eraFilter} onValueChange={setEraFilter}>
              <SelectTrigger id="era-filter" className="bg-black border-white/20 text-white">
                <SelectValue placeholder="All Eras" />
              </SelectTrigger>
              <SelectContent className="bg-black border-white/20 text-white">
                <SelectItem value="all-eras">All Eras</SelectItem>
                {uniqueEras.map(era => (
                  <SelectItem key={era} value={era}>{era}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Type Filter */}
          <div className="space-y-2">
            <Label htmlFor="type-filter" className="flex items-center">
              <Volume2 className="mr-2 h-4 w-4" />
              Type
            </Label>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger id="type-filter" className="bg-black border-white/20 text-white">
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent className="bg-black border-white/20 text-white">
                <SelectItem value="all-types">All Types</SelectItem>
                {uniqueTypes.map(type => (
                  <SelectItem key={type} value={type}>{formatType(type)}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Sheet Tab Filter */}
          <div className="space-y-2">
            <Label htmlFor="tab-filter" className="flex items-center">
              <Info className="mr-2 h-4 w-4" />
              Sheet Tab
            </Label>
            <Select value={tabFilter} onValueChange={setTabFilter}>
              <SelectTrigger id="tab-filter" className="bg-black border-white/20 text-white">
                <SelectValue placeholder="All Tabs" />
              </SelectTrigger>
              <SelectContent className="bg-black border-white/20 text-white">
                <SelectItem value="all-tabs">All Tabs</SelectItem>
                {uniqueTabs.map(tab => (
                  <SelectItem key={tab} value={tab}>{tab}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Quality Filter */}
          <div className="space-y-2">
            <Label htmlFor="quality-filter" className="flex items-center">
              <Music className="mr-2 h-4 w-4" />
              Quality
            </Label>
            <Select value={qualityFilter} onValueChange={setQualityFilter}>
              <SelectTrigger id="quality-filter" className="bg-black border-white/20 text-white">
                <SelectValue placeholder="All Qualities" />
              </SelectTrigger>
              <SelectContent className="bg-black border-white/20 text-white">
                <SelectItem value="all-qualities">All Qualities</SelectItem>
                {uniqueQualities.map(quality => (
                  <SelectItem key={quality} value={quality}>{quality}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Producer Filter */}
          <div className="space-y-2">
            <Label htmlFor="producer-filter" className="flex items-center">
              <Tag className="mr-2 h-4 w-4" />
              Producer
            </Label>
            <Select value={producerFilter} onValueChange={setProducerFilter}>
              <SelectTrigger id="producer-filter" className="bg-black border-white/20 text-white">
                <SelectValue placeholder="All Producers" />
              </SelectTrigger>
              <SelectContent className="bg-black border-white/20 text-white">
                <SelectItem value="all-producers">All Producers</SelectItem>
                {uniqueProducers.map(producer => (
                  <SelectItem key={producer} value={producer}>{producer}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Features Filter */}
          <div className="space-y-2">
            <Label htmlFor="features-filter" className="flex items-center">
              <Star className="mr-2 h-4 w-4" />
              Features
            </Label>
            <Select value={featuresFilter} onValueChange={setFeaturesFilter}>
              <SelectTrigger id="features-filter" className="bg-black border-white/20 text-white">
                <SelectValue placeholder="All Features" />
              </SelectTrigger>
              <SelectContent className="bg-black border-white/20 text-white">
                <SelectItem value="all-features">All Features</SelectItem>
                <SelectItem value="null">No Features</SelectItem>
                {uniqueFeatures.map(feature => (
                  <SelectItem key={feature} value={feature}>{feature}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Year Filter */}
          <div className="space-y-2">
            <Label htmlFor="year-filter" className="flex items-center">
              <Calendar className="mr-2 h-4 w-4" />
              Year
            </Label>
            <Select value={yearFilter} onValueChange={setYearFilter}>
              <SelectTrigger id="year-filter" className="bg-black border-white/20 text-white">
                <SelectValue placeholder="All Years" />
              </SelectTrigger>
              <SelectContent className="bg-black border-white/20 text-white">
                <SelectItem value="all-years">All Years</SelectItem>
                {uniqueYears.map(year => (
                  <SelectItem key={year} value={year}>{year}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Popularity Filter */}
          <div className="space-y-2">
            <Label htmlFor="popularity-filter" className="flex items-center">
              <Clock className="mr-2 h-4 w-4" />
              Popularity
            </Label>
            <Select value={popularityFilter} onValueChange={setPopularityFilter}>
              <SelectTrigger id="popularity-filter" className="bg-black border-white/20 text-white">
                <SelectValue placeholder="All Popularity Levels" />
              </SelectTrigger>
              <SelectContent className="bg-black border-white/20 text-white">
                <SelectItem value="all-popularity">All Popularity Levels</SelectItem>
                {uniquePopularity.map(pop => (
                  <SelectItem key={pop} value={pop}>{pop}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default FilterPanel;
