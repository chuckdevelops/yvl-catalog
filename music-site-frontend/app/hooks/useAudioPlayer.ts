'use client';

import { useState, useEffect } from 'react';

interface AudioPlayerManagerInterface {
  playAudio: (playerId: string, url: string) => void;
  pauseAudio: () => void;
  stopAudio: () => void;
  refreshPlayers: () => void;
  registerPlayer: (player: HTMLAudioElement) => void;
  activePlayer?: HTMLAudioElement;
  activeSongId?: string;
}

declare global {
  interface Window {
    audioPlayerManager?: AudioPlayerManagerInterface;
    AudioPlayerManager?: any;
  }
}

export const useAudioPlayer = () => {
  const [isReady, setIsReady] = useState(false);
  const [currentPlayingId, setCurrentPlayingId] = useState<string | null>(null);
  
  useEffect(() => {
    // Check if the audio player manager is loaded
    const checkManager = () => {
      if (typeof window !== 'undefined' && window.audioPlayerManager) {
        setIsReady(true);
        return true;
      }
      return false;
    };
    
    // If not loaded immediately, set up polling
    if (!checkManager()) {
      const interval = setInterval(() => {
        if (checkManager()) {
          clearInterval(interval);
        }
      }, 500);
      
      return () => clearInterval(interval);
    }
    
    // Listen for the custom event that tells us when a song starts playing
    const handleSongPlay = (event: Event) => {
      const customEvent = event as CustomEvent;
      const songId = customEvent.detail?.songId;
      
      if (songId) {
        setCurrentPlayingId(songId);
      }
    };
    
    window.addEventListener('songPlay', handleSongPlay);
    
    return () => {
      window.removeEventListener('songPlay', handleSongPlay);
    };
  }, []);
  
  const playSong = (songId: string, previewUrl: string) => {
    if (!isReady || !window.audioPlayerManager) return;
    
    const playerId = `preview-player-${songId}`;
    window.audioPlayerManager.playAudio(playerId, previewUrl);
    
    // Update current playing ID
    setCurrentPlayingId(songId);
    
    // Dispatch the event for other components
    window.dispatchEvent(new CustomEvent('songPlay', { 
      detail: { songId }
    }));
  };
  
  const pauseSong = () => {
    if (!isReady || !window.audioPlayerManager) return;
    
    window.audioPlayerManager.pauseAudio();
    // We don't clear currentPlayingId here because pausing 
    // doesn't mean the song is no longer selected
  };
  
  const stopSong = () => {
    if (!isReady || !window.audioPlayerManager) return;
    
    window.audioPlayerManager.stopAudio();
    setCurrentPlayingId(null);
  };
  
  return {
    isReady,
    currentPlayingId,
    playSong,
    pauseSong,
    stopSong
  };
}; 