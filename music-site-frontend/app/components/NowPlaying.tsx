'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Song, songs } from '../lib/data';

const NowPlaying: React.FC = () => {
  const [currentSong, setCurrentSong] = useState<Song | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Listen for custom event when a song starts playing
    const handleSongPlay = (event: Event) => {
      const customEvent = event as CustomEvent;
      const songId = customEvent.detail?.songId;
      
      if (songId) {
        const song = songs.find(s => s.id === songId);
        if (song) {
          setCurrentSong(song);
          setIsPlaying(true);
          setIsVisible(true);
        }
      }
    };

    // Listen for audio events from existing player
    const handleAudioPlayPause = () => {
      if (typeof window !== 'undefined' && 'AudioPlayerManager' in window) {
        // @ts-ignore - AudioPlayerManager is loaded from an external script
        const audioManager = window.audioPlayerManager;
        if (audioManager && audioManager.activePlayer) {
          // Check if any player is currently playing
          setIsPlaying(true);
        } else {
          setIsPlaying(false);
        }
      }
    };

    // Custom event for when a song is played
    window.addEventListener('songPlay', handleSongPlay);
    
    // Set up interval to check active player status
    const interval = setInterval(handleAudioPlayPause, 1000);

    return () => {
      window.removeEventListener('songPlay', handleSongPlay);
      clearInterval(interval);
    };
  }, []);

  // If no song is playing or the player is hidden, don't render
  if (!currentSong || !isVisible) return null;

  // Control functions
  const togglePlay = () => {
    if (typeof window !== 'undefined' && 'AudioPlayerManager' in window) {
      // @ts-ignore - AudioPlayerManager is loaded from an external script
      const audioManager = window.audioPlayerManager;
      if (audioManager && audioManager.activePlayer) {
        if (isPlaying) {
          audioManager.activePlayer.pause();
          setIsPlaying(false);
        } else {
          audioManager.activePlayer.play();
          setIsPlaying(true);
        }
      }
    }
  };

  const closePlayer = () => {
    setIsVisible(false);
    if (typeof window !== 'undefined' && 'AudioPlayerManager' in window) {
      // @ts-ignore - AudioPlayerManager is loaded from an external script
      const audioManager = window.audioPlayerManager;
      if (audioManager && audioManager.activePlayer) {
        audioManager.activePlayer.pause();
      }
    }
  };

  return (
    <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 w-full max-w-md z-40">
      <div className="bg-gray-900 bg-opacity-95 backdrop-blur-md border border-gray-800 rounded-lg shadow-xl p-3 flex items-center">
        {/* Song info */}
        <div className="flex-grow">
          <Link href={`/song/${currentSong.id}`} className="font-medium hover:text-accent transition-colors">
            {currentSong.name}
          </Link>
          <p className="text-xs text-gray-400">
            {currentSong.producer}
            {currentSong.features.length > 0 && ` • ft. ${currentSong.features.join(', ')}`}
          </p>
        </div>
        
        {/* Controls */}
        <div className="flex items-center space-x-3">
          <button 
            onClick={togglePlay}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-accent text-white"
          >
            <i className={`fas ${isPlaying ? 'fa-pause' : 'fa-play'}`}></i>
          </button>
          
          <Link 
            href={`/song/${currentSong.id}`}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-gray-800 text-white"
          >
            <i className="fas fa-info-circle"></i>
          </Link>
          
          <button 
            onClick={closePlayer}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-gray-800 text-white"
          >
            <i className="fas fa-times"></i>
          </button>
        </div>
      </div>
    </div>
  );
};

export default NowPlaying; 