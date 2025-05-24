import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import apiService from './apiService';

// Modal component for download options
const DownloadModal = ({ isOpen, onClose, songName, downloadUrl, songId }) => {
  if (!isOpen) return null;
  
  const [preparing, setPreparing] = useState(false);
  const [instructions, setInstructions] = useState('');
  
  const handleDownload = () => {
    window.open(downloadUrl, '_blank');
    onClose();
  };
  
  const handleAddToLocalFiles = async (service) => {
    try {
      setPreparing(true);
      // Call the API service to prepare the file for the streaming service
      const result = await apiService.prepareForStreamingService(songId, service);
      setInstructions(result.instructions);
    } catch (error) {
      console.error(`Error preparing for ${service}:`, error);
      alert(`Error preparing for ${service}. Please try again later.`);
    } finally {
      setPreparing(false);
    }
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full">
        <h3 className="text-xl font-bold text-white mb-4">Download Options</h3>
        
        {instructions ? (
          <div>
            <p className="text-gray-300 mb-4">Instructions for {songName}:</p>
            <div className="bg-gray-700 p-4 rounded mb-4">
              <p className="text-white whitespace-pre-line">{instructions}</p>
            </div>
            <button 
              onClick={onClose}
              className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded w-full"
            >
              Done
            </button>
          </div>
        ) : (
          <>
            <p className="text-gray-300 mb-4">What would you like to do with "{songName}"?</p>
            
            <div className="grid grid-cols-1 gap-3 mb-4">
              <button 
                onClick={handleDownload}
                className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded"
                disabled={preparing}
              >
                Download MP3
              </button>
              
              <button 
                onClick={() => handleAddToLocalFiles('Spotify')}
                className="bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded flex items-center justify-center gap-2"
                disabled={preparing}
              >
                {preparing ? 'Preparing...' : <span>Add to Spotify Local Files</span>}
              </button>
              
              <button 
                onClick={() => handleAddToLocalFiles('Apple Music')}
                className="bg-pink-600 hover:bg-pink-700 text-white py-2 px-4 rounded flex items-center justify-center gap-2"
                disabled={preparing}
              >
                {preparing ? 'Preparing...' : <span>Add to Apple Music</span>}
              </button>
            </div>
            
            <div className="flex justify-end">
              <button 
                onClick={onClose}
                className="text-gray-400 hover:text-white"
                disabled={preparing}
              >
                Cancel
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

const Badge = ({ text, type = "default" }) => {
  const baseClasses = "inline-flex text-xs rounded px-2 py-1";
  const typeClasses = {
    default: "bg-gray-700 text-gray-200",
    era: "bg-blue-900 text-blue-100",
    quality: "bg-green-900 text-green-100",
    type: "bg-purple-900 text-purple-100",
    tab: "bg-yellow-900 text-yellow-100"
  };
  
  return <span className={`${baseClasses} ${typeClasses[type] || typeClasses.default}`}>{text}</span>;
};

const SongDetail = () => {
  const [searchParams] = useSearchParams();
  const songId = searchParams.get('id');
  const [song, setSong] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const fetchSongDetail = async () => {
      if (!songId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const data = await apiService.getSongDetails(songId);
        setSong(data);
      } catch (err) {
        console.error('Error fetching song details:', err);
        const errorDetails = apiService.handleApiError(err);
        setError(errorDetails.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSongDetail();
  }, [songId]);

  if (!songId) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-900 bg-opacity-30 text-yellow-200 p-4 rounded">
          <p>Please select a song to view details.</p>
        </div>
      </div>
    );
  }

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
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-900 text-white p-4 rounded">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!song) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-900 text-white p-4 rounded">
          <p>Song not found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <nav className="mb-6">
        <Link to="/list" className="text-blue-400 hover:text-blue-300 flex items-center gap-1">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Song List
        </Link>
      </nav>

      <header className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">{song.name}</h1>
        <div className="flex flex-wrap gap-2 mb-4">
          {song.era && <Badge text={song.era} type="era" />}
          {song.quality && <Badge text={song.quality} type="quality" />}
          {song.type && <Badge text={song.type} type="type" />}
          {song.primary_tab_name && <Badge text={song.primary_tab_name} type="tab" />}
        </div>
      </header>

      {/* Audio Preview */}
      {song.preview_file_exists && (
        <div className="bg-gray-800 p-4 rounded-lg mb-8">
          <h2 className="text-lg font-medium text-white mb-3">Audio Preview</h2>
          <audio 
            controls 
            className="w-full" 
            src={song.preview_audio_url}
          >
            Your browser does not support the audio element.
          </audio>
          
          <div className="mt-4">
            <button 
              onClick={() => setIsModalOpen(true)}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded"
            >
              Download Song
            </button>
          </div>
        </div>
      )}
      
      {/* Download Modal */}
      <DownloadModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        songName={song?.name || ''}
        songId={songId}
        downloadUrl={song?.preview_audio_url || ''} // In a real app, this would be the full song URL
      }

      {/* Song Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div className="bg-gray-800 p-4 rounded-lg">
          <h2 className="text-lg font-medium text-white mb-4">Details</h2>
          
          <div className="grid grid-cols-1 gap-4">
            {song.producer && (
              <div>
                <h3 className="text-sm font-medium text-gray-400">Producer</h3>
                <p className="text-white">{song.producer}</p>
              </div>
            )}
            
            {song.features && (
              <div>
                <h3 className="text-sm font-medium text-gray-400">Features</h3>
                <p className="text-white">{song.features}</p>
              </div>
            )}
            
            {song.leak_date && (
              <div>
                <h3 className="text-sm font-medium text-gray-400">Leak Date</h3>
                <p className="text-white">{song.leak_date}</p>
              </div>
            )}
            
            {song.file_date && (
              <div>
                <h3 className="text-sm font-medium text-gray-400">File Date</h3>
                <p className="text-white">{song.file_date}</p>
              </div>
            )}
          </div>
        </div>
        
        <div className="bg-gray-800 p-4 rounded-lg">
          <h2 className="text-lg font-medium text-white mb-4">Additional Information</h2>
          
          <div className="grid grid-cols-1 gap-4">
            {song.track_length && (
              <div>
                <h3 className="text-sm font-medium text-gray-400">Track Length</h3>
                <p className="text-white">{song.track_length}</p>
              </div>
            )}
            
            {song.available_length && (
              <div>
                <h3 className="text-sm font-medium text-gray-400">Available Length</h3>
                <p className="text-white">{song.available_length}</p>
              </div>
            )}
            
            {song.secondary_tab_names && song.secondary_tab_names.length > 0 && (
              <div>
                <h3 className="text-sm font-medium text-gray-400">Collections</h3>
                <div className="flex flex-wrap gap-1 mt-1">
                  {song.secondary_tab_names.map((tab, index) => (
                    <Badge key={index} text={tab} type="tab" />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Notes Section */}
      {song.notes && (
        <div className="bg-gray-800 p-4 rounded-lg">
          <h2 className="text-lg font-medium text-white mb-3">Notes</h2>
          <p className="text-gray-300 whitespace-pre-line">{song.notes}</p>
        </div>
      )}
    </div>
  );
};

export default SongDetail;