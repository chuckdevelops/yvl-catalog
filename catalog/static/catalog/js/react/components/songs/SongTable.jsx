import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ChevronDown, 
  ChevronUp, 
  Disc, 
  Info, 
  Volume2, 
  Tag, 
  Calendar, 
  Clock, 
  Music,
  Play
} from 'lucide-react';
import { cn, formatType } from '../../lib/utils';
import { Badge } from '../ui/badge';
import { useAudio } from '../../hooks/useAudio';

const SongTable = ({ 
  songs, 
  sortField, 
  sortDirection, 
  handleSort 
}) => {
  const { playAudio, pauseAudio, activeAudioId } = useAudio();
  
  const getSortIcon = (field) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? 
      <ChevronUp className="h-3 w-3 ml-1" /> : 
      <ChevronDown className="h-3 w-3 ml-1" />;
  };

  const handlePlayClick = (song, e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (activeAudioId === song.id) {
      pauseAudio();
    } else if (song.preview_url) {
      playAudio(song.id, song.preview_url);
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead className="bg-black/60">
          <tr className="border-b border-white/20">
            <th className="text-left p-3 text-white font-medium">
              <div className="flex items-center cursor-pointer" onClick={() => handleSort('name')}>
                <Music className="mr-2 h-4 w-4" />
                <span>Name</span>
                {getSortIcon('name')}
              </div>
            </th>
            <th className="text-left p-3 text-white font-medium hidden md:table-cell">
              <div className="flex items-center cursor-pointer" onClick={() => handleSort('era')}>
                <Disc className="mr-2 h-4 w-4" />
                <span>Era</span>
                {getSortIcon('era')}
              </div>
            </th>
            <th className="text-left p-3 text-white font-medium hidden md:table-cell">
              <div className="flex items-center">
                <Info className="mr-2 h-4 w-4" />
                <span>Sheet Tab</span>
              </div>
            </th>
            <th className="text-left p-3 text-white font-medium hidden sm:table-cell">
              <div className="flex items-center cursor-pointer" onClick={() => handleSort('type')}>
                <Volume2 className="mr-2 h-4 w-4" />
                <span>Type</span>
                {getSortIcon('type')}
              </div>
            </th>
            <th className="text-left p-3 text-white font-medium hidden lg:table-cell">Quality</th>
            <th className="text-left p-3 text-white font-medium hidden md:table-cell">
              <div className="flex items-center cursor-pointer" onClick={() => handleSort('producer')}>
                <Tag className="mr-2 h-4 w-4" />
                <span>Producer</span>
                {getSortIcon('producer')}
              </div>
            </th>
            <th className="text-left p-3 text-white font-medium hidden lg:table-cell">
              <div className="flex items-center cursor-pointer" onClick={() => handleSort('year')}>
                <Calendar className="mr-2 h-4 w-4" />
                <span>Year</span>
                {getSortIcon('year')}
              </div>
            </th>
            <th className="text-left p-3 text-white font-medium hidden sm:table-cell">
              <div className="flex items-center cursor-pointer" onClick={() => handleSort('leak_date')}>
                <Clock className="mr-2 h-4 w-4" />
                <span>Leak Date</span>
                {getSortIcon('leak_date')}
              </div>
            </th>
          </tr>
        </thead>
        
        <tbody>
          {songs.map((song) => (
            <tr 
              key={song.id} 
              className={cn(
                "border-b border-white/10 hover:bg-white/5 transition-colors", 
                activeAudioId === song.id ? "bg-white/10" : ""
              )}
            >
              <td className="p-3">
                <div className="flex items-center gap-3">
                  <button 
                    className={cn(
                      "w-8 h-8 flex items-center justify-center rounded-full border border-white/20",
                      activeAudioId === song.id ? "bg-white text-black" : "text-white hover:bg-white/10",
                      !song.preview_url && "opacity-50 cursor-not-allowed"
                    )}
                    onClick={(e) => song.preview_url && handlePlayClick(song, e)}
                    disabled={!song.preview_url}
                    title={song.preview_url ? "Play preview" : "No preview available"}
                  >
                    <Play className="h-4 w-4" />
                  </button>
                  
                  <div>
                    <Link 
                      to={`/songs/${song.id}`} 
                      className="text-white hover:text-white/80 transition-colors font-medium"
                    >
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
                  </div>
                </div>
              </td>
              
              <td className="p-3 hidden md:table-cell">
                {song.era ? (
                  <Badge variant="outline" className="bg-black/60 border-white/20">
                    {song.era}
                  </Badge>
                ) : (
                  <em className="text-white/50">Unknown</em>
                )}
              </td>
              
              <td className="p-3 hidden md:table-cell">
                {song.primary_tab_name && song.primary_tab_name !== "Unknown" ? (
                  <div>
                    <Badge variant="secondary" className="bg-white/10 text-white">
                      {song.primary_tab_name}
                    </Badge>
                    {song.subsection_name && (
                      <div className="mt-1">
                        <small className="text-white/70">{song.subsection_name}</small>
                      </div>
                    )}
                  </div>
                ) : (
                  <em className="text-white/50">Unknown</em>
                )}
              </td>
              
              <td className="p-3 hidden sm:table-cell">
                <Badge>
                  {formatType(song.type)}
                </Badge>
              </td>
              
              <td className="p-3 hidden lg:table-cell text-white/90">{song.quality}</td>
              
              <td className="p-3 hidden md:table-cell text-white/90">
                {song.producer || <em className="text-white/50">Unknown</em>}
              </td>
              
              <td className="p-3 hidden lg:table-cell text-white/90">
                {song.year || <em className="text-white/50">Unknown</em>}
              </td>
              
              <td className="p-3 hidden sm:table-cell text-white/90">{song.leak_date}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SongTable;