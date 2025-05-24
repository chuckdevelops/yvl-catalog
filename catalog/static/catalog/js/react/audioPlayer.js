import React, { useState, useRef, useEffect, forwardRef } from 'react';
import ReactDOM from 'react-dom';
import './audioPlayer.css';

// Utility function for merging classNames conditionally
const cn = (...classes) => {
  return classes.filter(Boolean).join(' ');
};

const AudioPlayer = forwardRef(({ 
  audioUrl, 
  songName, 
  sourceType, 
  onError, 
  showAlternativeButton, 
  alternativeUrl,
  variant = 'default',
  size = 'default',
  glassmorphism = false,
  limitDuration = false,
  maxDuration = 20,
  className,
  ...props
}, ref) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  
  const audioRef = useRef(null);
  const progressBarRef = useRef(null);
  
  // Setup forwarded ref
  useEffect(() => {
    if (ref) {
      if (typeof ref === 'function') {
        ref(audioRef.current);
      } else {
        ref.current = audioRef.current;
      }
    }
  }, [ref]);
  
  // Add timestamp to URL for cache busting
  const formattedUrl = () => {
    const timestamp = new Date().getTime();
    // Don't modify the URL if it's null or undefined
    if (!audioUrl) return '';
    return audioUrl.includes('?') ? `${audioUrl}&t=${timestamp}` : `${audioUrl}?t=${timestamp}`;
  };
  
  // Set up audio element and event listeners
  useEffect(() => {
    const audio = audioRef.current;
    
    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
      setLoading(false);
      
      // Handle duration limiting
      if (limitDuration && audio.currentTime >= maxDuration) {
        audio.pause();
        setIsPlaying(false);
      }
    };
    
    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
      setLoading(false);
    };
    
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleError = (e) => {
      console.error('Audio error:', e);
      setError(true);
      setLoading(false);
      if (onError) onError(e);
    };
    
    // Register event listeners
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('error', handleError);
    audio.addEventListener('waiting', () => setLoading(true));
    audio.addEventListener('playing', () => setLoading(false));
    
    // Set volume
    audio.volume = volume;
    
    return () => {
      // Clean up event listeners
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('error', handleError);
      audio.removeEventListener('waiting', () => setLoading(true));
      audio.removeEventListener('playing', () => setLoading(false));
    };
  }, [audioUrl, volume, onError, limitDuration, maxDuration]); // Re-run when audioUrl, volume, or duration settings change
  
  // Format time in MM:SS
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };
  
  // Handle play/pause
  const togglePlayPause = () => {
    const audio = audioRef.current;
    
    if (!audio) {
      console.error('Audio element reference is null');
      return;
    }
    
    if (isPlaying) {
      audio.pause();
    } else {
      console.log('Attempting to play audio:', audio.src);
      // Force load if needed
      if (audio.networkState === 0 || audio.networkState === 3) {
        console.log('Reloading audio source');
        audio.load();
      }
      
      audio.play()
        .then(() => {
          console.log('Audio playback started successfully');
        })
        .catch(err => {
          console.error('Playback error:', err);
          setError(true);
          
          // Try to provide more details
          if (audio.error) {
            console.error('Audio error code:', audio.error.code);
            console.error('Audio error message:', audio.error.message);
          }
        });
    }
  };
  
  // Handle clicking on the progress bar
  const handleProgressClick = (e) => {
    const audio = audioRef.current;
    const progressBar = progressBarRef.current;
    
    if (progressBar && audio) {
      const rect = progressBar.getBoundingClientRect();
      const clickPosition = (e.clientX - rect.left) / rect.width;
      audio.currentTime = clickPosition * audio.duration;
    }
  };
  
  // Handle volume change
  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    audioRef.current.volume = newVolume;
  };
  
  // Use alternative URL if provided
  const useAlternativeUrl = () => {
    if (alternativeUrl) {
      setError(false);
      setLoading(true);
      
      // Add timestamp to URL
      const timestamp = new Date().getTime();
      const url = alternativeUrl.includes('?') ? 
        `${alternativeUrl}&t=${timestamp}` : 
        `${alternativeUrl}?t=${timestamp}`;
      
      audioRef.current.src = url;
      audioRef.current.load();
      audioRef.current.play().catch(err => {
        console.error('Alternative playback error:', err);
        setError(true);
      });
    }
  };

  // Determine container classes based on variant and size
  const containerClasses = cn(
    'player-container',
    variant !== 'default' && variant,
    size !== 'default' && size,
    glassmorphism && 'glass',
    className
  );
  
  return (
    <div className="react-audio-player" {...props}>
      {/* Hidden HTML5 audio element */}
      <audio 
        ref={audioRef}
        src={formattedUrl()}
        preload="metadata"
        crossOrigin="anonymous"
      >
        <source src={formattedUrl()} type="audio/mpeg" />
        Your browser does not support the audio element.
      </audio>
      
      {/* Custom player UI */}
      <div className={containerClasses}>
        {/* Play/Pause button */}
        <button 
          className={`play-button ${isPlaying ? 'playing' : ''}`}
          onClick={togglePlayPause}
          disabled={loading && !isPlaying}
          aria-label={isPlaying ? 'Pause' : 'Play'}
        >
          {loading && !isPlaying ? (
            <span className="loading-spinner"></span>
          ) : isPlaying ? (
            <i className="fas fa-pause"></i>
          ) : (
            <i className="fas fa-play"></i>
          )}
        </button>
        
        {/* Song info */}
        <div className="song-info">
          <div className="song-name">{songName}</div>
          <div className="source-badge">
            {sourceType === 'krakenfiles' && <span className="badge krakenfiles">krakenfiles.com</span>}
            {sourceType === 'froste' && <span className="badge froste">music.froste.lol</span>}
            {sourceType === 'pillowcase' && <span className="badge pillowcase">pillowcase.su</span>}
            {sourceType === 'preview' && <span className="badge preview">30-Second Preview</span>}
          </div>
        </div>
        
        {/* Time display */}
        <div className="time-display">
          <span className="current-time">{formatTime(currentTime)}</span>
          <span className="duration-separator">/</span>
          <span className="duration">{formatTime(duration)}</span>
        </div>
        
        {/* Progress bar */}
        <div 
          className="progress-container" 
          ref={progressBarRef}
          onClick={handleProgressClick}
        >
          <div 
            className="progress-bar" 
            style={{ width: `${(currentTime / duration) * 100}%` }}
          />
          <div 
            className="progress-handle"
            style={{ left: `${(currentTime / duration) * 100}%` }}
          />
        </div>
        
        {/* Volume control */}
        <div className="volume-container">
          <i className={`volume-icon fas ${
            volume === 0 ? 'fa-volume-mute' :
            volume < 0.5 ? 'fa-volume-down' : 'fa-volume-up'
          }`}></i>
          <input 
            type="range" 
            min="0" 
            max="1" 
            step="0.05" 
            value={volume}
            onChange={handleVolumeChange}
            className="volume-slider"
            aria-label="Volume"
          />
        </div>
        
        {/* Error message and alternative button */}
        {error && (
          <div className="error-message">
            <i className="fas fa-exclamation-triangle"></i> Error loading audio.
            {showAlternativeButton && alternativeUrl && (
              <button className="alt-method-btn" onClick={useAlternativeUrl}>
                Try Alternative Method
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
});

AudioPlayer.displayName = 'AudioPlayer';

// Enhanced Audio Player with additional variants
const EnhancedAudioPlayer = forwardRef(({ 
  variant = 'default',
  size = 'default',
  glassmorphism = false,
  limitDuration = false,
  maxDuration = 20,
  ...props 
}, ref) => {
  return (
    <AudioPlayer
      ref={ref}
      variant={variant}
      size={size}
      glassmorphism={glassmorphism}
      limitDuration={limitDuration}
      maxDuration={maxDuration}
      {...props}
    />
  );
});

EnhancedAudioPlayer.displayName = 'EnhancedAudioPlayer';

// Find all audio player containers and replace with React components
document.addEventListener('DOMContentLoaded', () => {
  // Find elements with a specific data attribute
  const playerContainers = document.querySelectorAll('[data-react-audio-player]');
  
  console.log('Found', playerContainers.length, 'audio player containers');
  
  playerContainers.forEach(container => {
    const audioUrl = container.dataset.audioUrl;
    const songName = container.dataset.songName || 'Unknown Song';
    const sourceType = container.dataset.sourceType || 'preview';
    const alternativeUrl = container.dataset.alternativeUrl || '';
    const variant = container.dataset.variant || 'default';
    const size = container.dataset.size || 'default';
    const glassmorphism = container.dataset.glassmorphism === 'true';
    const limitDuration = container.dataset.limitDuration === 'true';
    const maxDuration = parseInt(container.dataset.maxDuration || '20', 10);
    
    console.log('Mounting React Audio Player with URL:', audioUrl);
    console.log('Song name:', songName);
    console.log('Source type:', sourceType);
    console.log('Variant:', variant);
    console.log('Duration limit enabled:', limitDuration);
    
    try {
      // First, clear any existing content
      while (container.firstChild) {
        container.removeChild(container.firstChild);
      }
      
      ReactDOM.render(
        <EnhancedAudioPlayer 
          audioUrl={audioUrl}
          songName={songName}
          sourceType={sourceType}
          showAlternativeButton={!!alternativeUrl}
          alternativeUrl={alternativeUrl}
          variant={variant}
          size={size}
          glassmorphism={glassmorphism}
          limitDuration={limitDuration}
          maxDuration={maxDuration}
        />,
        container
      );
      console.log('Audio player mounted successfully');
    } catch (error) {
      console.error('Error mounting audio player:', error);
      // Provide a fallback
      container.innerHTML = `
        <div class="alert alert-warning">
          <strong>Error loading enhanced player.</strong> Using fallback player:
        </div>
        <audio controls preload="metadata" class="w-100">
          <source src="${audioUrl}" type="audio/mpeg">
          Your browser does not support the audio element.
        </audio>
      `;
    }
  });
});

// Export for explicit usage
export { AudioPlayer, EnhancedAudioPlayer };
export default EnhancedAudioPlayer;