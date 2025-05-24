
import React, { createContext, useState, useEffect, useRef } from 'react';

interface AudioContextType {
  playAudio: (id: string, url: string) => void;
  pauseAudio: () => void;
  activeAudioId: string | null;
}

export const AudioContext = createContext<AudioContextType>({
  playAudio: () => {},
  pauseAudio: () => {},
  activeAudioId: null
});

interface AudioProviderProps {
  children: React.ReactNode;
}

const AudioProvider = ({ children }: AudioProviderProps) => {
  const [activeAudioId, setActiveAudioId] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioElement = audioRef.current;

  useEffect(() => {
    // Create audio element
    if (!audioRef.current) {
      audioRef.current = new Audio();
      
      // Add event listeners
      const audio = audioRef.current;
      
      audio.addEventListener('error', handleAudioError);
      audio.addEventListener('stalled', handleAudioStall);
      
      // Clean up on unmount
      return () => {
        audio.removeEventListener('error', handleAudioError);
        audio.removeEventListener('stalled', handleAudioStall);
        audio.pause();
      };
    }
  }, []);
  
  // Handle document visibility changes
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && audioElement) {
        audioElement.pause();
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [audioElement]);

  const handleAudioError = () => {
    console.error('[AudioProvider] Audio error:', audioElement?.error);
    
    // Try to fix the URL if there's an error
    if (audioElement && audioElement.src) {
      const fixedUrl = fixAudioUrl(audioElement.src);
      if (fixedUrl !== audioElement.src) {
        console.log('[AudioProvider] Trying alternate URL:', fixedUrl);
        audioElement.src = fixedUrl;
        audioElement.load();
        audioElement.play().catch(err => {
          console.error('[AudioProvider] Still failed after URL fix:', err);
        });
      }
    }
  };
  
  const handleAudioStall = () => {
    console.warn('[AudioProvider] Audio playback stalled');
    
    // Similar approach to error handling - try an alternative URL
    if (audioElement && audioElement.src) {
      const fixedUrl = fixAudioUrl(audioElement.src);
      if (fixedUrl !== audioElement.src) {
        audioElement.src = fixedUrl;
        audioElement.load();
        audioElement.play().catch(console.error);
      }
    }
  };
  
  // Function to fix problematic audio URLs
  const fixAudioUrl = (url: string): string => {
    if (url.includes('/audio-serve/')) {
      // Extract filename from the URL
      const filenamePart = url.split('/audio-serve/')[1]?.split('?')[0];
      
      if (filenamePart) {
        // Check if it's a UUID
        const uuidMatch = filenamePart.match(/^([0-9a-f-]{8}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{4}-[0-9a-f-]{12})\.mp3$/i);
        
        if (uuidMatch) {
          // Use direct media URL with UUID
          const uuid = uuidMatch[1];
          return `/media/previews/${uuid}.mp3?t=${Math.floor(Date.now()/1000)}`;
        } else {
          // For non-UUID formats, still try direct media path
          return `/media/previews/${filenamePart}?t=${Math.floor(Date.now()/1000)}`;
        }
      }
    }
    
    // If no changes needed or can't parse, return the original
    return url;
  };

  const playAudio = (id: string, url: string) => {
    if (!audioRef.current) return;
    
    // Add cache-busting parameter
    const timestamp = Math.floor(Date.now() / 1000);
    const audioUrl = url.includes('?') 
      ? `${url}&t=${timestamp}` 
      : `${url}?t=${timestamp}`;
    
    // Use our URL fixer to ensure the best format
    const fixedUrl = fixAudioUrl(audioUrl);
    
    console.log(`[AudioProvider] Playing audio for ${id}:`, fixedUrl);
    
    const audio = audioRef.current;
    
    // If this is a different audio than what's currently playing
    if (activeAudioId !== id || audio.src !== fixedUrl) {
      audio.src = fixedUrl;
      audio.load();
    }
    
    // Play the audio
    audio.play()
      .then(() => {
        setActiveAudioId(id);
        console.log('[AudioProvider] Playback started successfully');
      })
      .catch(e => {
        console.error('[AudioProvider] Error playing audio:', e);
      });
  };

  const pauseAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setActiveAudioId(null);
    }
  };

  return (
    <AudioContext.Provider value={{ playAudio, pauseAudio, activeAudioId }}>
      {children}
    </AudioContext.Provider>
  );
};

export default AudioProvider;
