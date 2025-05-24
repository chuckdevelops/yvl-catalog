
import { Filter, FilterX, ChevronUp, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Collapsible,
  CollapsibleTrigger,
  CollapsibleContent
} from "@/components/ui/collapsible";

interface FilterToggleProps {
  isFilterExpanded: boolean;
  activeFilters: number;
  children: React.ReactNode;
}

const FilterToggle = ({ 
  isFilterExpanded, 
  activeFilters,
  children 
}: FilterToggleProps) => {
  return (
    <Collapsible className="space-y-2 mb-6">
      <CollapsibleTrigger asChild>
        <Button 
          variant="outline" 
          className="w-full border-white/20 text-white hover:bg-white/10 flex items-center justify-center"
        >
          {isFilterExpanded ? <FilterX className="mr-2 h-4 w-4" /> : <Filter className="mr-2 h-4 w-4" />}
          {isFilterExpanded ? 'Hide Filters' : 'Show Filters'}
          {activeFilters > 0 && (
            <Badge className="ml-2 bg-white text-black">{activeFilters}</Badge>
          )}
          {isFilterExpanded ? <ChevronUp className="ml-2 h-4 w-4" /> : <ChevronDown className="ml-2 h-4 w-4" />}
        </Button>
      </CollapsibleTrigger>
      
      <CollapsibleContent className="space-y-2">
        {children}
      </CollapsibleContent>
    </Collapsible>
  );
};

export default FilterToggle;
