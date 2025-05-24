
import React from 'react';
import { Link } from 'react-router-dom';
import { Music, Headphones, Calendar } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

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

interface SongGridProps {
  songs: Song[];
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

const SongGrid: React.FC<SongGridProps> = ({ songs }) => {
  if (songs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-10 text-center">
        <div className="text-white/50 mb-4">No songs found matching your filters</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-2">
      {songs.map((song) => (
        <Link 
          key={song.id} 
          to={`/songs/${song.id}`}
          className="group"
        >
          <div className="bg-black/60 border border-white/10 hover:border-white/20 rounded-lg overflow-hidden hover:shadow-lg transition-all duration-300 hover:scale-[1.03] h-full flex flex-col">
            <div className="bg-white/5 p-6 flex items-center justify-center">
              <div className="w-24 h-24 rounded-full bg-black border border-white/10 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <Music className="w-12 h-12 text-white/70 group-hover:text-white transition-colors" />
              </div>
            </div>
            
            <div className="p-4 flex flex-col flex-grow">
              <h3 className="text-white font-medium text-lg mb-1 group-hover:text-gradient transition-all duration-300">{song.name}</h3>
              
              <div className="flex flex-wrap gap-2 mt-2 mb-3">
                {song.era && (
                  <Badge variant="outline" className="bg-white/5 border-white/20 text-xs text-white/90">
                    {song.era}
                  </Badge>
                )}
                <Badge className="bg-white/10 text-white hover:bg-white/15 text-xs">
                  {formatType(song.type)}
                </Badge>
                {song.quality && (
                  <Badge variant="outline" className="bg-black/60 border-white/20 text-xs text-white/90">
                    {song.quality}
                  </Badge>
                )}
              </div>
              
              <div className="text-xs text-white/70 space-y-2 mt-auto">
                {song.producer && (
                  <div className="flex items-center gap-1.5">
                    <Headphones className="w-3 h-3" />
                    <span>{song.producer}</span>
                  </div>
                )}
                {song.features && (
                  <div className="flex items-center gap-1.5">
                    <span>ft. {song.features}</span>
                  </div>
                )}
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-3 h-3" />
                  <span>{song.year || 'Unknown'}</span>
                </div>
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
};

export default SongGrid;
