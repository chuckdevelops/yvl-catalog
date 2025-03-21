import React, { useState } from 'react';
import { Badge } from './Badge';
import { AudioPlayer } from './AudioPlayer';
import Link from 'next/link';

export const SongCard = ({ song }) => {
  const [isPlaying, setIsPlaying] = useState(false);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="song-card">
      <div className="song-card-header">
        <Link href={`/songs/${song.id}`}>
          <h3 className="song-title">{song.name}</h3>
        </Link>
        <div className="song-meta">
          <span className="song-era">{song.era || 'Unknown'}</span>
          {song.preview_url && (
            <button 
              className="play-button" 
              aria-label={isPlaying ? 'Pause' : 'Play'} 
              onClick={handlePlayPause}
            >
              <i className={`fas fa-${isPlaying ? 'pause' : 'play'}`}></i>
            </button>
          )}
        </div>
      </div>
      <div className="song-categories">
        {song.primary_tab_name && (
          <Badge variant="primary">{song.primary_tab_name}</Badge>
        )}
        {song.emoji_tab_names?.map(tab => (
          <Badge key={tab} variant="secondary">{tab}</Badge>
        ))}
      </div>
      {song.preview_url && isPlaying && (
        <div className="audio-container">
          <AudioPlayer 
            url={song.preview_url} 
            onEnded={() => setIsPlaying(false)} 
          />
        </div>
      )}
      <style jsx>{`
        .song-card {
          border-radius: 8px;
          overflow: hidden;
          background-color: var(--bg-surface, white);
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          transition: transform 0.2s, box-shadow 0.2s;
          padding: 1rem;
          margin-bottom: 1rem;
        }
        
        .song-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .song-card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 0.75rem;
        }
        
        .song-title {
          margin: 0;
          font-size: 1.1rem;
          font-weight: 600;
          color: var(--text-base, #121212);
        }
        
        .song-meta {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .song-era {
          font-size: 0.8rem;
          color: var(--text-muted, #666);
        }
        
        .play-button {
          background: none;
          border: none;
          color: var(--c-primary, #333);
          cursor: pointer;
          padding: 0.25rem;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background-color 0.2s;
        }
        
        .play-button:hover {
          background-color: rgba(0,0,0,0.05);
        }
        
        .song-categories {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 0.75rem;
        }
        
        .audio-container {
          margin-top: 0.75rem;
        }
      `}</style>
    </div>
  );
};