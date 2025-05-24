'use client';

import { useEffect, useState } from 'react';
import { MediaItem, apiService } from '../lib/api';

export default function MediaPage() {
  const [mediaItems, setMediaItems] = useState<MediaItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'art' | 'interview' | 'fit_pic' | 'social_media'>('art');

  useEffect(() => {
    const fetchMediaItems = async () => {
      try {
        const data = await apiService.getMediaItems(activeTab);
        setMediaItems(data);
      } catch (err) {
        setError('Failed to fetch media items');
        console.error('Error fetching media items:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMediaItems();
  }, [activeTab]);

  if (loading) {
    return <div className="flex justify-center items-center min-h-screen">Loading...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center">{error}</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Media</h1>
      
      <div className="mb-6">
        <div className="flex space-x-4 border-b">
          <button
            onClick={() => setActiveTab('art')}
            className={`px-4 py-2 ${
              activeTab === 'art'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Art
          </button>
          <button
            onClick={() => setActiveTab('interview')}
            className={`px-4 py-2 ${
              activeTab === 'interview'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Interviews
          </button>
          <button
            onClick={() => setActiveTab('fit_pic')}
            className={`px-4 py-2 ${
              activeTab === 'fit_pic'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Fit Pics
          </button>
          <button
            onClick={() => setActiveTab('social_media')}
            className={`px-4 py-2 ${
              activeTab === 'social_media'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Social Media
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mediaItems.map((item) => (
          <div key={item.id} className="bg-white rounded-lg shadow overflow-hidden">
            <img
              src={item.url}
              alt={item.title}
              className="w-full h-48 object-cover"
            />
            <div className="p-4">
              <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
              {item.description && (
                <p className="text-gray-600 text-sm">{item.description}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 