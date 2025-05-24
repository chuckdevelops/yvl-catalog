
import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronDown, ChevronUp, Disc, Info, Volume2, Tag, Calendar, Clock } from 'lucide-react';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

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

interface Song {
  id: number;
  name: string;
  era: string;
  primary_tab_name: string;
  subsection_name: string | null;
  type: string;
  quality: string;
  leak_date: string;
  producer: string | null;
  features: string | null;
  year: string;
  popularity: string;
}

interface SongTableProps {
  songs: Song[];
  sortField: string;
  sortDirection: string;
  handleSort: (field: string) => void;
}

const SongTable = ({ 
  songs, 
  sortField, 
  sortDirection, 
  handleSort 
}: SongTableProps) => {
  const getSortIcon = (field: string) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? <ChevronUp className="h-3 w-3 ml-1" /> : <ChevronDown className="h-3 w-3 ml-1" />;
  };

  return (
    <>
      {songs.length > 0 ? (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader className="bg-black/60">
              <TableRow className="border-white/20">
                <TableHead className="text-white cursor-pointer" onClick={() => handleSort('name')}>
                  <div className="flex items-center">
                    <span>Name</span>
                    {getSortIcon('name')}
                  </div>
                </TableHead>
                <TableHead className="text-white hidden md:table-cell cursor-pointer" onClick={() => handleSort('era')}>
                  <div className="flex items-center">
                    <Disc className="mr-1 h-4 w-4" />
                    <span>Era</span>
                    {getSortIcon('era')}
                  </div>
                </TableHead>
                <TableHead className="text-white hidden md:table-cell">
                  <div className="flex items-center">
                    <Info className="mr-1 h-4 w-4" />
                    <span>Sheet Tab</span>
                  </div>
                </TableHead>
                <TableHead className="text-white hidden sm:table-cell cursor-pointer" onClick={() => handleSort('type')}>
                  <div className="flex items-center">
                    <Volume2 className="mr-1 h-4 w-4" />
                    <span>Type</span>
                    {getSortIcon('type')}
                  </div>
                </TableHead>
                <TableHead className="text-white hidden lg:table-cell">Quality</TableHead>
                <TableHead className="text-white hidden md:table-cell cursor-pointer" onClick={() => handleSort('producer')}>
                  <div className="flex items-center">
                    <Tag className="mr-1 h-4 w-4" />
                    <span>Producer</span>
                    {getSortIcon('producer')}
                  </div>
                </TableHead>
                <TableHead className="text-white hidden lg:table-cell cursor-pointer" onClick={() => handleSort('year')}>
                  <div className="flex items-center">
                    <Calendar className="mr-1 h-4 w-4" />
                    <span>Year</span>
                    {getSortIcon('year')}
                  </div>
                </TableHead>
                <TableHead className="text-white hidden sm:table-cell cursor-pointer" onClick={() => handleSort('leak_date')}>
                  <div className="flex items-center">
                    <Clock className="mr-1 h-4 w-4" />
                    <span>Leak Date</span>
                    {getSortIcon('leak_date')}
                  </div>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {songs.map((song) => (
                <TableRow 
                  key={song.id} 
                  className="hover-scale hover:bg-white/5 border-white/20 transition-all"
                >
                  <TableCell>
                    <Link to={`/songs/${song.id}`} className="text-white hover:text-white/80 transition-colors font-medium">
                      {song.name}
                    </Link>
                    <div className="md:hidden mt-1 space-y-1">
                      <div className="text-xs text-white/70">
                        {song.era || <em className="text-white/50">Unknown Era</em>}
                        {song.producer && <span> • {song.producer}</span>}
                      </div>
                      <div className="text-xs text-white/70">
                        {formatType(song.type)} • {song.quality}
                        {song.features && <span> • ft. {song.features}</span>}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="text-white/90 hidden md:table-cell">
                    {song.era ? (
                      <Badge variant="outline" className="bg-black/60 border-white/20">
                        {song.era}
                      </Badge>
                    ) : (
                      <em className="text-white/50">Unknown</em>
                    )}
                  </TableCell>
                  <TableCell className="hidden md:table-cell">
                    {song.primary_tab_name && song.primary_tab_name !== "Unknown" ? (
                      <div>
                        <span className="text-white">{song.primary_tab_name}</span>
                        {song.subsection_name && (
                          <div>
                            <small className="text-white/70">{song.subsection_name}</small>
                          </div>
                        )}
                      </div>
                    ) : (
                      <em className="text-white/50">Unknown</em>
                    )}
                  </TableCell>
                  <TableCell className="text-white/90 hidden sm:table-cell">
                    <Badge className="bg-white/10 text-white hover:bg-white/15">
                      {formatType(song.type)}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-white/90 hidden lg:table-cell">{song.quality}</TableCell>
                  <TableCell className="text-white/90 hidden md:table-cell">
                    {song.producer || <em className="text-white/50">Unknown</em>}
                  </TableCell>
                  <TableCell className="text-white/90 hidden lg:table-cell">
                    {song.year || <em className="text-white/50">Unknown</em>}
                  </TableCell>
                  <TableCell className="text-white/90 hidden sm:table-cell">{song.leak_date}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center p-10 text-center">
          <div className="text-white/50 mb-4">No songs found matching your filters</div>
        </div>
      )}
    </>
  );
};

export default SongTable;
