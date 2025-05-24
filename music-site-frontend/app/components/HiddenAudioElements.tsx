'use client';

import React, { useEffect } from 'react';
import { Song } from '../lib/data';

interface HiddenAudioElementsProps {
  songs: Song[];
}

/**
 * Creates hidden audio elements for all songs with previews
 * This allows the AudioPlayerManager to play song previews directly from the music list
 * without having to navigate to the song detail page
 */
const HiddenAudioElements: React.FC<HiddenAudioElementsProps> = ({ songs }) => {
  useEffect(() => {
    // Initialize audio player manager if available
    if (typeof window !== 'undefined' && 'AudioPlayerManager' in window) {
      // @ts-ignore - AudioPlayerManager is loaded from an external script
      const audioManager = window.audioPlayerManager;
      if (audioManager && typeof audioManager.refreshPlayers === 'function') {
        setTimeout(() => {
          audioManager.refreshPlayers();
        }, 500);
      }
    }
  }, [songs]);

  return (
    <div style={{ display: 'none' }}>
      {songs.filter(song => song.hasPreview).map(song => (
        <audio 
          key={song.id}
          id={`preview-player-${song.id}`}
          data-player-id={`preview-player-${song.id}`}
          controls
          preload="none"
        >
          <source 
            id={`preview-player-${song.id}-source`} 
            src={song.previewUrl} 
            type="audio/mpeg" 
          />
          Your browser does not support the audio element.
        </audio>
      ))}
    </div>
  );
};

export default HiddenAudioElements; 