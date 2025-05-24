import { useState, useEffect, useRef, useContext, createContext } from 'react';

// Create a context for audio playback
const AudioContext = createContext({
  playAudio: () => {},
  pauseAudio: () => {},
  activeAudioId: null,
  isPlaying: false,
  duration: 0,
  currentTime: 0,
  progress: 0,
});

// Audio provider component that manages audio state
export const AudioProvider = ({ children }) => {
  const [activeAudioId, setActiveAudioId] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [progress, setProgress] = useState(0);
  
  const audioRef = useRef(null);
  
  useEffect(() => {
    // Create audio element if it doesn't exist
    if (!audioRef.current) {
      audioRef.current = new Audio();
      
      // Set up event listeners
      const audio = audioRef.current;
      
      audio.addEventListener('loadedmetadata', () => {
        setDuration(audio.duration);
      });
      
      audio.addEventListener('timeupdate', () => {
        setCurrentTime(audio.currentTime);
        setProgress((audio.currentTime / audio.duration) * 100);
      });
      
      audio.addEventListener('ended', () => {
        setIsPlaying(false);
        setProgress(0);
        setCurrentTime(0);
      });
      
      audio.addEventListener('error', (e) => {
        console.error('Audio playback error:', e);
        setIsPlaying(false);
      });
      
      // Clean up on unmount
      return () => {
        audio.pause();
        audio.src = '';
        
        audio.removeEventListener('loadedmetadata', () => {});
        audio.removeEventListener('timeupdate', () => {});
        audio.removeEventListener('ended', () => {});
        audio.removeEventListener('error', () => {});
      };
    }
  }, []);
  
  // Handle document visibility changes (pause when tab is hidden)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && audioRef.current && isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [isPlaying]);
  
  // Function to play audio
  const playAudio = (id, url) => {
    if (!audioRef.current) return;
    
    const audio = audioRef.current;
    
    // If this is a different audio than what's currently playing
    if (activeAudioId !== id || audio.src !== url) {
      // Add cache-busting parameter
      const timestamp = Math.floor(Date.now() / 1000);
      const audioUrl = url.includes('?') 
        ? `${url}&t=${timestamp}` 
        : `${url}?t=${timestamp}`;
      
      audio.src = audioUrl;
      audio.load();
    }
    
    audio.play()
      .then(() => {
        setActiveAudioId(id);
        setIsPlaying(true);
      })
      .catch(e => {
        console.error('Error playing audio:', e);
        setIsPlaying(false);
      });
  };
  
  // Function to pause audio
  const pauseAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };
  
  // Function to seek to a specific time
  const seekTo = (percent) => {
    if (audioRef.current && duration) {
      const newTime = (percent / 100) * duration;
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
      setProgress(percent);
      
      // Resume playback if it was playing
      if (isPlaying) {
        audioRef.current.play();
      }
    }
  };
  
  return (
    <AudioContext.Provider
      value={{
        playAudio,
        pauseAudio,
        seekTo,
        activeAudioId,
        isPlaying,
        duration,
        currentTime,
        progress,
      }}
    >
      {children}
    </AudioContext.Provider>
  );
};

// Custom hook to use the audio context
export const useAudio = () => {
  const context = useContext(AudioContext);
  
  if (!context) {
    throw new Error('useAudio must be used within an AudioProvider');
  }
  
  return context;
};