'use client';

import React, { useEffect, useRef } from 'react';

interface AudioPlayerProps {
  songId: string;
  previewUrl: string;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ songId, previewUrl }) => {
  const audioRef = useRef<HTMLAudioElement>(null);
  const playerId = `preview-player-${songId}`;
  const statusId = `${playerId}-status`;
  
  useEffect(() => {
    // This will run once when the component mounts
    // It will add the audio player element to the DOM so the existing JS can find it
    
    // Access the global audio manager if it's been loaded
    const initAudioPlayer = () => {
      if (typeof window !== 'undefined' && 'AudioPlayerManager' in window) {
        // @ts-ignore - AudioPlayerManager is loaded from an external script
        const audioManager = window.audioPlayerManager || new window.AudioPlayerManager();
        
        if (audioRef.current) {
          // Force a reload to make sure the player is initialized
          audioRef.current.load();
          
          // Register this player with the audio manager
          audioManager.registerPlayer(audioRef.current);
          
          // Listen for play event to dispatch songPlay event
          audioRef.current.addEventListener('play', () => {
            // Dispatch a custom event with the song ID
            window.dispatchEvent(new CustomEvent('songPlay', { 
              detail: { songId }
            }));
          });
        }
      }
    };
    
    // Initialize after a short delay to ensure external scripts are loaded
    const timeoutId = setTimeout(initAudioPlayer, 500);
    
    return () => {
      clearTimeout(timeoutId);
    };
  }, [songId]);
  
  // Function to handle play button click
  const handlePlay = () => {
    if (typeof window !== 'undefined' && 'AudioPlayerManager' in window) {
      // @ts-ignore - AudioPlayerManager is loaded from an external script
      const audioManager = window.audioPlayerManager || new window.AudioPlayerManager();
      audioManager.playAudio(playerId, previewUrl);
      
      // Dispatch a custom event with the song ID
      window.dispatchEvent(new CustomEvent('songPlay', { 
        detail: { songId }
      }));
    } else {
      // Fallback if audio manager isn't loaded
      if (audioRef.current) {
        audioRef.current.play();
      }
    }
  };
  
  return (
    <div className="audio-player-wrapper">
      {/* This is the audio element that your existing JS will control */}
      <audio 
        ref={audioRef} 
        id={playerId} 
        data-player-id={playerId} 
        controls 
        preload="metadata" 
        className="w-full"
      >
        <source id={`${playerId}-source`} src={previewUrl} type="audio/mpeg" />
        Your browser does not support the audio element.
      </audio>
      
      {/* Status display for audio loading/errors */}
      <div id={statusId} className="text-sm text-gray-400 mt-1" style={{ display: 'none' }}></div>
      
      {/* Custom player controls */}
      <div className="mt-4 flex space-x-2">
        <button 
          onClick={handlePlay}
          className="bg-accent hover:bg-opacity-80 text-white px-4 py-2 rounded-md transition-colors flex items-center"
        >
          <i className="fas fa-play mr-2"></i> Play Preview
        </button>
        
        <a 
          href={previewUrl} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors flex items-center"
        >
          <i className="fas fa-external-link-alt mr-2"></i> Open Source
        </a>
      </div>
    </div>
  );
};

export default AudioPlayer; 