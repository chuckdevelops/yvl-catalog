'use client';

import Album from './Album';
import { albums } from '../data/albums';

const AlbumGrid = () => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
      {albums.map((album) => (
        <Album
          key={album.id}
          id={album.id}
          title={album.title}
          imageUrl={album.imageUrl}
          previewUrl={album.previewUrl}
        />
      ))}
    </div>
  );
};

export default AlbumGrid;
