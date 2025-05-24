'use client';

import { useState, useEffect } from 'react';
import { Song, apiService } from '../lib/api';
import Link from 'next/link';

interface SongDetailProps {
  songId: number;
}

export default function SongDetail({ songId }: SongDetailProps) {
  const [song, setSong] = useState<Song | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSong();
  }, [songId]);

  const loadSong = async () => {
    try {
      setLoading(true);
      const data = await apiService.getSong(songId);
      setSong(data);
    } catch (err) {
      setError('Failed to load song details');
      console.error('Error loading song:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>;
  }

  if (error || !song) {
    return <div className="text-red-500 text-center">{error || 'Song not found'}</div>;
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <nav className="flex" aria-label="Breadcrumb">
        <ol className="inline-flex items-center space-x-1 md:space-x-3">
          <li className="inline-flex items-center">
            <Link href="/" className="text-gray-700 hover:text-blue-600">
              Home
            </Link>
          </li>
          <li>
            <div className="flex items-center">
              <span className="mx-2 text-gray-400">/</span>
              <Link href="/songs" className="text-gray-700 hover:text-blue-600">
                Songs
              </Link>
            </div>
          </li>
          <li aria-current="page">
            <div className="flex items-center">
              <span className="mx-2 text-gray-400">/</span>
              <span className="text-gray-500">{song.name}</span>
            </div>
          </li>
        </ol>
      </nav>

      {/* Song Details */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold">
            {song.name}
            {song.file_date === 'Album Track' && (
              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                Official Album Track
              </span>
            )}
          </h1>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Era</dt>
                  <dd className="mt-1 text-sm text-gray-900">{song.era || <em>Unknown</em>}</dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">Categories</dt>
                  <dd className="mt-1">
                    {song.primary_tab_name && song.primary_tab_name !== "Unknown" ? (
                      <div className="space-y-2">
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
                            <span className="text-sm font-medium text-gray-500">Additional Categories:</span>
                            <div className="mt-1">
                              {song.other_tab_names.map((tab) => (
                                <span key={tab} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 mr-1">
                                  {tab}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <em>Unknown</em>
                    )}
                  </dd>
                </div>

                {song.subsection_name && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Subsection</dt>
                    <dd className="mt-1 text-sm text-gray-900">{song.subsection_name}</dd>
                  </div>
                )}

                <div>
                  <dt className="text-sm font-medium text-gray-500">Type</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {song.type && song.type !== "NaN" && song.type !== "nan" ? song.type : ''}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">Quality</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {song.quality && song.quality !== "NaN" && song.quality !== "nan" ? song.quality : ''}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">Track Length</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {song.track_length && song.track_length !== "NaN" && song.track_length !== "nan" ? song.track_length : ''}
                  </dd>
                </div>

                {song.display_album_name && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Album</dt>
                    <dd className="mt-1 text-sm text-gray-900">{song.display_album_name}</dd>
                  </div>
                )}

                {song.display_track_number && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Album Track #</dt>
                    <dd className="mt-1 text-sm text-gray-900">{song.display_track_number}</dd>
                  </div>
                )}

                <div>
                  <dt className="text-sm font-medium text-gray-500">Leak Date</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {song.leak_date && song.leak_date !== "NaN" && song.leak_date !== "nan" ? song.leak_date : ''}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">File</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {song.file_date && song.file_date !== "NaN" && song.file_date !== "nan" ? song.file_date : ''}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">Available Length</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {song.available_length && song.available_length !== "NaN" && song.available_length !== "nan" ? song.available_length : ''}
                  </dd>
                </div>
              </dl>
            </div>

            {/* Audio Preview Section */}
            {(song.preview_url || song.preview_file_exists) && (
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  {song.is_froste_link ? (
                    <>Full Track Preview <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">music.froste.lol</span></>
                  ) : song.is_pillowcase_link ? (
                    <>Full Track Preview <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">pillowcase.su</span></>
                  ) : song.is_krakenfiles_link ? (
                    <>Full Track Preview <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">krakenfiles.com</span></>
                  ) : (
                    '30-Second Preview'
                  )}
                </h3>

                <div className="space-y-4">
                  {song.preview_file_exists && (
                    <div>
                      <audio
                        controls
                        className="w-full"
                        src={`${song.preview_audio_url}?t=${Date.now()}`}
                      >
                        Your browser does not support the audio element.
                      </audio>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-2">
                    <button
                      className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                        song.is_froste_link
                          ? 'bg-blue-600 hover:bg-blue-700'
                          : song.is_pillowcase_link
                          ? 'bg-yellow-600 hover:bg-yellow-700'
                          : song.is_krakenfiles_link
                          ? 'bg-green-600 hover:bg-green-700'
                          : 'bg-gray-600 hover:bg-gray-700'
                      }`}
                      onClick={() => {
                        // TODO: Implement play with duration limit
                        window.open(song.preview_audio_url, '_blank');
                      }}
                    >
                      {song.is_froste_link ? (
                        <>Play from music.froste.lol</>
                      ) : song.is_pillowcase_link ? (
                        <>Play from pillowcase.su</>
                      ) : song.is_krakenfiles_link ? (
                        <>Play from krakenfiles.com</>
                      ) : (
                        <>Play Preview</>
                      )}
                    </button>

                    {song.direct_audio_url && song.direct_audio_url !== song.preview_audio_url && (
                      <button
                        className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                        onClick={() => {
                          // TODO: Implement play with duration limit
                          window.open(song.direct_audio_url, '_blank');
                        }}
                      >
                        Alt Method
                      </button>
                    )}

                    {song.original_source_url && (
                      <a
                        href={song.original_source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                      >
                        Open Source
                      </a>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Notes Section */}
          {song.notes && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-2">Notes</h3>
              <div className="prose max-w-none">
                {song.notes.split('\n').map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 