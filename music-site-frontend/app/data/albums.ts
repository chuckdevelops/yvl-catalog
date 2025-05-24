export interface Album {
  id: string;
  title: string;
  imageUrl: string;
  previewUrl: string;
}

export const albums: Album[] = [
  {
    id: '1',
    title: 'Playboi Carti',
    imageUrl: '/images/albums/playboi-carti.jpg',
    previewUrl: '/audio/playboi-carti.mp3'
  },
  {
    id: '2',
    title: 'Die Lit',
    imageUrl: '/images/albums/die-lit.jpg',
    previewUrl: '/audio/die-lit.mp3'
  },
  {
    id: '3',
    title: 'Whole Lotta Red',
    imageUrl: '/images/albums/whole-lotta-red.jpg',
    previewUrl: '/audio/whole-lotta-red.mp3'
  }
]; 