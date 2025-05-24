import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiService from './apiService';

const StatsCard = ({ title, value, icon, description }) => (
  <div className="bg-gray-800 rounded-lg p-4 shadow hover:shadow-md transition-shadow">
    <div className="flex items-start">
      <div className="text-2xl mr-2">{icon}</div>
      <div>
        <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
        <p className="text-white text-2xl font-bold">{value}</p>
        {description && <p className="text-gray-400 text-xs mt-1">{description}</p>}
      </div>
    </div>
  </div>
);

const SongCard = ({ song }) => (
  <div className="bg-gray-800 rounded-lg overflow-hidden shadow hover:shadow-md transition-all hover:scale-[1.01]">
    <div className="p-4">
      <h3 className="text-white font-medium truncate">{song.name}</h3>
      <div className="flex flex-wrap gap-1 mt-1">
        {song.era && (
          <span className="text-xs bg-blue-900 text-blue-100 rounded px-2 py-0.5">
            {song.era}
          </span>
        )}
        {song.quality && (
          <span className="text-xs bg-green-900 text-green-100 rounded px-2 py-0.5">
            {song.quality}
          </span>
        )}
      </div>
      <p className="text-gray-400 text-sm mt-2 truncate">
        {song.producer && `Prod. ${song.producer}`}
        {song.features && song.producer && " • "}
        {song.features && `Feat. ${song.features}`}
      </p>
    </div>
    
    {song.preview_file_exists && (
      <div className="bg-gray-900 p-2">
        <audio 
          controls 
          className="w-full h-8" 
          src={song.preview_audio_url}
          preload="none"
        >
          Your browser does not support the audio element.
        </audio>
      </div>
    )}
    
    <Link 
      to={`/list?id=${song.id}`}
      className="block text-center bg-gray-900 text-blue-400 py-2 text-sm hover:bg-gray-700 transition-colors"
    >
      View Details
    </Link>
  </div>
);

const Home = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Fetching home data from API...');
        const jsonData = await apiService.getHomeData();
        console.log('Data received:', jsonData);
        setData(jsonData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        const errorDetails = apiService.handleApiError(err);
        console.error('Error details:', errorDetails);
        setError(errorDetails.message);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full border-t-transparent" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900 text-white p-4 rounded">
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-white mb-6">Carti Catalog Dashboard</h1>
      
      {/* Stats Section */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatsCard 
            title="Total Songs" 
            value={data.stats.total_songs} 
            icon="🎵" 
            description="Tracks in our database" 
          />
          <StatsCard 
            title="Distinct Eras" 
            value={data.stats.distinct_eras} 
            icon="📅" 
            description="Unique time periods" 
          />
          <StatsCard 
            title="Collections" 
            value={data.stats.sheet_tabs.length} 
            icon="📁" 
            description="Curated song groups" 
          />
        </div>
      </section>

      {/* Collections Section */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">Collections</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {data.stats.sheet_tabs.slice(0, 6).map(tab => (
            <Link 
              key={tab.id} 
              to={`/list?sheet_tab=${tab.id}`}
              className="flex items-center gap-3 bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors"
            >
              <div className="text-2xl">{tab.icon}</div>
              <div>
                <h3 className="text-white font-medium">{tab.name}</h3>
                <p className="text-gray-400 text-sm">{tab.count} tracks</p>
              </div>
            </Link>
          ))}
        </div>
        <div className="text-center mt-4">
          <Link 
            to="/list" 
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors"
          >
            View All Collections
          </Link>
        </div>
      </section>

      {/* Recent Songs Section */}
      <section>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">Recent Songs</h2>
          <Link to="/list" className="text-blue-400 hover:text-blue-300 text-sm">
            View All →
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {data.recent_songs.slice(0, 8).map(song => (
            <SongCard key={song.id} song={song} />
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;