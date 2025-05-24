
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';

interface SearchBarProps {
  searchTerm: string;
  setSearchTerm: (value: string) => void;
}

const SearchBar = ({ searchTerm, setSearchTerm }: SearchBarProps) => {
  return (
    <div className="relative mb-4">
      <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
        <Search className="h-4 w-4 text-white/50" />
      </div>
      <Input
        type="text"
        placeholder="Search by song name, era, producer, or features..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="bg-black/80 border-white/20 text-white placeholder:text-white/50 pl-10"
      />
    </div>
  );
};

export default SearchBar;
