'use client';

import { useState } from 'react';
import { useAudioPlayer } from '../hooks/useAudioPlayer';

interface AlbumProps {
  id: string;
  title: string;
  imageUrl: string;
  previewUrl: string;
}

export default function Album({ id, title, imageUrl, previewUrl }: AlbumProps) {
  const [isSpinning, setIsSpinning] = useState(false);
  const [isTemporarySpinning, setIsTemporarySpinning] = useState(false);
  const { playSong, pauseSong } = useAudioPlayer();

  const handleMouseEnter = () => {
    setIsSpinning(true);
  };

  const handleMouseLeave = () => {
    setIsSpinning(false);
  };

  const handleClick = () => {
    if (isSpinning) {
      pauseSong();
      setIsSpinning(false);
    } else {
      playSong(id, previewUrl);
      setIsSpinning(true);
    }
  };

  return (
    <div
      className="relative w-64 h-64 cursor-pointer"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={handleClick}
    >
      <img
        src={imageUrl}
        alt={title}
        className={`w-full h-full object-cover transition-transform duration-1000 ${
          isSpinning ? 'animate-spin' : ''
        }`}
      />
      <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 opacity-0 hover:opacity-100 transition-opacity">
        <h3 className="text-white text-xl font-bold">{title}</h3>
      </div>
    </div>
  );
}
