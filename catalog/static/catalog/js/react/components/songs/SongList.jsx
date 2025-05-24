import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { formatType, truncateText, filterAIBadge } from '../../lib/utils';
import FilterPanel from './FilterPanel';
import FilterToggle from './FilterToggle';

const SongList = ({ songs, filters }) => {
  const [showFilters, setShowFilters] = useState(false);

  // Pagination handlers
  const handlePageChange = (page) => {
    const currentUrl = new URL(window.location.href);
    currentUrl.searchParams.set('page', page);
    window.location.href = currentUrl.toString();
  };

  // View song details handler
  const viewSongDetails = (songId) => {
    window.location.href = `/catalog/songs/${songId}/`;
  };

  return (
    <div className="carti-fade-in">
      <header className="mb-6">
        <h1 className="text-3xl font-bold carti-heading carti-text-glow mb-2">
          Songs Catalog <span className="carti-text-red">*</span>
        </h1>
        <p className="text-white/70">
          Browse {filters.pagination.total_items} songs in the catalog
        </p>
      </header>

      {/* Filters toggle button */}
      <FilterToggle showFilters={showFilters} setShowFilters={setShowFilters} />

      {/* Filters panel */}
      <FilterPanel 
        filters={filters} 
        showFilters={showFilters} 
      />

      {/* Song table */}
      <Card className="w-full overflow-hidden carti-scale-in">
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>Results</CardTitle>
            <Badge variant="carti">
              {filters.pagination.total_items} songs found
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-black/30">
                <tr className="border-b border-white/10">
                  <th className="px-4 py-3 text-left">Name</th>
                  <th className="px-4 py-3 text-left">Era</th>
                  <th className="px-4 py-3 text-left">Sheet Tab</th>
                  <th className="px-4 py-3 text-left">Type</th>
                  <th className="px-4 py-3 text-left">Quality</th>
                  <th className="px-4 py-3 text-left">Leak Date</th>
                  <th className="px-4 py-3 text-left">Notes</th>
                </tr>
              </thead>
              <tbody>
                {songs.length > 0 ? (
                  songs.map((song) => (
                    <tr 
                      key={song.id} 
                      className="border-b border-white/5 hover:bg-white/5 cursor-pointer"
                      onClick={() => viewSongDetails(song.id)}
                    >
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <span>{song.name}</span>
                          {(song.preview_url || song.has_playable_link) && (
                            <span className="text-red-500" title="Has audio preview">
                              ♪
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">{song.era || 'Unknown'}</td>
                      <td className="px-4 py-3">
                        <div className="flex flex-wrap gap-1">
                          {song.primary_tab_name && song.primary_tab_name !== "Unknown" && (
                            <Badge variant="glass">{song.primary_tab_name}</Badge>
                          )}
                          {filterAIBadge(song.emoji_tab_names, song.name).map((tab, index) => (
                            <Badge key={index} variant="emoji">{tab}</Badge>
                          ))}
                          {song.other_tab_names && song.other_tab_names.map((tab, index) => (
                            <Badge key={index} variant="secondary">{tab}</Badge>
                          ))}
                        </div>
                      </td>
                      <td className="px-4 py-3">{formatType(song.type)}</td>
                      <td className="px-4 py-3">{song.quality || ''}</td>
                      <td className="px-4 py-3">{song.leak_date || ''}</td>
                      <td className="px-4 py-3">
                        {song.notes ? (
                          <div className="text-xs text-white/70">
                            {truncateText(song.notes, 30)}
                          </div>
                        ) : (
                          <span className="text-white/40">No notes</span>
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={7} className="px-4 py-3 text-center">
                      No songs match your filters.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {filters.pagination.total_pages > 1 && (
            <div className="flex items-center justify-center mt-6 gap-2">
              <Button
                variant="glass"
                size="sm"
                onClick={() => handlePageChange(1)}
                disabled={!filters.pagination.has_previous}
              >
                «
              </Button>
              <Button
                variant="glass"
                size="sm"
                onClick={() => handlePageChange(filters.pagination.previous_page)}
                disabled={!filters.pagination.has_previous}
              >
                ‹
              </Button>
              
              <span className="px-4 py-2 carti-glass rounded-md">
                Page {filters.pagination.current_page} of {filters.pagination.total_pages}
              </span>
              
              <Button
                variant="glass"
                size="sm"
                onClick={() => handlePageChange(filters.pagination.next_page)}
                disabled={!filters.pagination.has_next}
              >
                ›
              </Button>
              <Button
                variant="glass"
                size="sm"
                onClick={() => handlePageChange(filters.pagination.total_pages)}
                disabled={!filters.pagination.has_next}
              >
                »
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SongList;