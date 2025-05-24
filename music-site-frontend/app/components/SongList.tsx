'use client';

import { useState, useEffect } from 'react';
import { Song, SongFilters, apiService } from '../lib/api';
import Link from 'next/link';

export default function SongList() {
  const [songs, setSongs] = useState<Song[]>([]);
  const [filters, setFilters] = useState<SongFilters>({});
  const [eras, setEras] = useState<string[]>([]);
  const [sheetTabs, setSheetTabs] = useState<{ id: string; name: string }[]>([]);
  const [qualities, setQualities] = useState<string[]>([]);
  const [types, setTypes] = useState<string[]>([]);
  const [topProducers, setTopProducers] = useState<string[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSongs();
  }, [filters]);

  const loadSongs = async () => {
    try {
      setLoading(true);
      const response = await apiService.getSongs(filters);
      setSongs(response.songs);
      setEras(response.eras);
      setSheetTabs(response.sheet_tabs);
      setQualities(response.qualities);
      setTypes(response.types);
      setTopProducers(response.top_producers);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to load songs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key: keyof SongFilters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Era</label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              value={filters.era || ''}
              onChange={(e) => handleFilterChange('era', e.target.value)}
            >
              <option value="">All Eras</option>
              {eras.map((era) => (
                <option key={era} value={era}>{era}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Sheet Tab</label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              value={filters.sheet_tab || ''}
              onChange={(e) => handleFilterChange('sheet_tab', e.target.value)}
            >
              <option value="">All Tabs</option>
              {sheetTabs.map((tab) => (
                <option key={tab.id} value={tab.id}>{tab.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Quality</label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              value={filters.quality || ''}
              onChange={(e) => handleFilterChange('quality', e.target.value)}
            >
              <option value="">All Qualities</option>
              {qualities.map((quality) => (
                <option key={quality} value={quality}>{quality}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Type</label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              value={filters.type || ''}
              onChange={(e) => handleFilterChange('type', e.target.value)}
            >
              <option value="">All Types</option>
              {types.map((type) => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Producer</label>
            <select
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              value={filters.producer || ''}
              onChange={(e) => handleFilterChange('producer', e.target.value)}
            >
              <option value="">All Producers</option>
              {topProducers.map((producer) => (
                <option key={producer} value={producer}>{producer}</option>
              ))}
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">Search</label>
            <input
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="Search songs, producers, features..."
              value={filters.q || ''}
              onChange={(e) => handleFilterChange('q', e.target.value)}
            />
          </div>
        </div>

        <div className="mt-4 flex gap-2">
          <button
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            onClick={() => loadSongs()}
          >
            Apply Filters
          </button>
          {(filters.era || filters.quality || filters.type || filters.sheet_tab || filters.producer || filters.q) && (
            <button
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              onClick={clearFilters}
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Results */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold">Results</h2>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
            {total} songs found
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Era</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sheet Tab</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quality</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Leak Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-sm text-gray-500">
                    Loading...
                  </td>
                </tr>
              ) : songs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-4 text-center text-sm text-gray-500">
                    No songs match your filters.
                  </td>
                </tr>
              ) : (
                songs.map((song) => (
                  <tr key={song.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link href={`/song/${song.id}`} className="text-indigo-600 hover:text-indigo-900">
                        {song.name}
                        {(song.preview_url || song.preview_file_exists) && (
                          <span className="ml-2 text-indigo-500" title="Has audio preview">♪</span>
                        )}
                      </Link>
                      {song.file_date === 'Album Track' && (
                        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          Official Album Track
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {song.era || <em>Unknown</em>}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {song.primary_tab_name && song.primary_tab_name !== "Unknown" ? (
                        <div className="space-y-1">
                          <div>
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                              {song.primary_tab_name}
                            </span>
                            {song.emoji_tab_names.map((tab) => (
                              <span key={tab} className="ml-1 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                {tab}
                              </span>
                            ))}
                          </div>
                          {song.other_tab_names && song.other_tab_names.length > 0 && (
                            <div>
                              {song.other_tab_names.map((tab) => (
                                <span key={tab} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 mr-1">
                                  {tab}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      ) : (
                        <em>Unknown</em>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {song.type && song.type !== "NaN" && song.type !== "nan" ? song.type : ''}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {song.quality && song.quality !== "NaN" && song.quality !== "nan" ? song.quality : ''}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {song.leak_date && song.leak_date !== "NaN" && song.leak_date !== "nan" ? song.leak_date : ''}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {song.notes ? (
                        <button
                          className="text-indigo-600 hover:text-indigo-900"
                          onClick={() => {
                            // TODO: Implement notes modal
                            alert(song.notes);
                          }}
                        >
                          View Notes
                        </button>
                      ) : (
                        <em>No notes</em>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
} 