
import React from 'react';
import { Button } from '@/components/ui/button';
import { Grid2X2, List } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ViewToggleProps {
  view: 'list' | 'grid';
  onViewChange: (view: 'list' | 'grid') => void;
}

const ViewToggle: React.FC<ViewToggleProps> = ({ view, onViewChange }) => {
  return (
    <div className="flex items-center gap-2 bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-1">
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onViewChange('list')}
        className={cn(
          "rounded-md flex items-center gap-1.5 px-2.5 py-1.5 h-8 text-xs",
          view === 'list'
            ? "bg-white/10 text-white"
            : "text-white/60 hover:text-white hover:bg-white/5"
        )}
      >
        <List className="h-3.5 w-3.5" />
        <span>List</span>
      </Button>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => onViewChange('grid')}
        className={cn(
          "rounded-md flex items-center gap-1.5 px-2.5 py-1.5 h-8 text-xs",
          view === 'grid'
            ? "bg-white/10 text-white"
            : "text-white/60 hover:text-white hover:bg-white/5"
        )}
      >
        <Grid2X2 className="h-3.5 w-3.5" />
        <span>Grid</span>
      </Button>
    </div>
  );
};

export default ViewToggle;
