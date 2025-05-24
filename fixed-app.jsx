import React from 'react';
import { HashRouter as Router, Routes, Route, Link } from 'react-router-dom';

// Simple Home component
const Home = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-white mb-6">Carti Catalog Dashboard</h1>
    
    {/* Stats Section */}
    <section className="mb-8">
      <h2 className="text-xl font-semibold text-white mb-4">Statistics</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 shadow">
          <div className="flex items-start">
            <div className="text-2xl mr-2">🎵</div>
            <div>
              <h3 className="text-gray-400 text-sm font-medium">Total Songs</h3>
              <p className="text-white text-2xl font-bold">432</p>
              <p className="text-gray-400 text-xs mt-1">Tracks in database</p>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 shadow">
          <div className="flex items-start">
            <div className="text-2xl mr-2">📅</div>
            <div>
              <h3 className="text-gray-400 text-sm font-medium">Distinct Eras</h3>
              <p className="text-white text-2xl font-bold">8</p>
              <p className="text-gray-400 text-xs mt-1">Unique time periods</p>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 shadow">
          <div className="flex items-start">
            <div className="text-2xl mr-2">📁</div>
            <div>
              <h3 className="text-gray-400 text-sm font-medium">Collections</h3>
              <p className="text-white text-2xl font-bold">6</p>
              <p className="text-gray-400 text-xs mt-1">Curated song groups</p>
            </div>
          </div>
        </div>
      </div>
    </section>
    
    {/* Recent Songs Section */}
    <section>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-white">Recent Songs</h2>
        <Link to="/songs" className="text-blue-400 hover:text-blue-300 text-sm">
          View All →
        </Link>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {/* Song Card 1 */}
        <div className="bg-gray-800 rounded-lg overflow-hidden shadow hover:shadow-md transition-all">
          <div className="p-4">
            <h3 className="text-white font-medium truncate">Example Song 1</h3>
            <div className="flex flex-wrap gap-1 mt-1">
              <span className="px-2 py-0.5 bg-blue-900 text-blue-100 rounded text-xs">V2</span>
              <span className="px-2 py-0.5 bg-green-900 text-green-100 rounded text-xs">CDQ</span>
            </div>
            <p className="text-gray-400 text-sm mt-2 truncate">
              Prod. Metro Boomin • Feat. Lil Uzi Vert
            </p>
          </div>
          
          <div className="bg-gray-900 p-2">
            <audio 
              controls 
              className="w-full h-8" 
              src="/sample-audio.mp3"
              preload="none"
            >
              Your browser does not support the audio element.
            </audio>
          </div>
          
          <Link 
            to="/songs/1"
            className="block text-center bg-gray-900 text-blue-400 py-2 text-sm hover:bg-gray-700 transition-colors"
          >
            View Details
          </Link>
        </div>
        
        {/* Song Card 2 */}
        <div className="bg-gray-800 rounded-lg overflow-hidden shadow hover:shadow-md transition-all">
          <div className="p-4">
            <h3 className="text-white font-medium truncate">Example Song 2</h3>
            <div className="flex flex-wrap gap-1 mt-1">
              <span className="px-2 py-0.5 bg-blue-900 text-blue-100 rounded text-xs">WLR</span>
              <span className="px-2 py-0.5 bg-green-900 text-green-100 rounded text-xs">HQ</span>
            </div>
            <p className="text-gray-400 text-sm mt-2 truncate">
              Prod. Pierre Bourne
            </p>
          </div>
          
          <div className="bg-gray-900 p-2">
            <audio 
              controls 
              className="w-full h-8" 
              src="/sample-audio.mp3"
              preload="none"
            >
              Your browser does not support the audio element.
            </audio>
          </div>
          
          <Link 
            to="/songs/2"
            className="block text-center bg-gray-900 text-blue-400 py-2 text-sm hover:bg-gray-700 transition-colors"
          >
            View Details
          </Link>
        </div>
      </div>
    </section>
  </div>
);

// Simple Songs List component
const SongsList = () => (
  <div className="container mx-auto px-4 py-8">
    <h1 className="text-3xl font-bold text-white mb-6">Song Library</h1>
    
    <div className="bg-gray-800 rounded-lg p-4 shadow">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-900">
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Song</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Era</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Quality</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody>
            {[1, 2, 3, 4, 5].map((id) => (
              <tr key={id} className="border-b border-gray-800 hover:bg-gray-900 transition-colors">
                <td className="px-4 py-3">
                  <div className="flex items-center">
                    <button className="mr-3 text-gray-400 hover:text-white transition-colors" aria-label="Play">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                        <path d="M8 5.14v14l11-7-11-7z" />
                      </svg>
                    </button>
                    <div>
                      <div className="font-medium text-white">Example Song {id}</div>
                      <div className="text-sm text-gray-400">Prod. Metro Boomin</div>
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 bg-blue-900 text-blue-100 rounded text-xs">V2</span>
                </td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 bg-green-900 text-green-100 rounded text-xs">CDQ</span>
                </td>
                <td className="px-4 py-3 text-right">
                  <Link to={`/songs/${id}`} className="text-blue-400 hover:text-blue-300 transition-colors">
                    Details
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </div>
);

// Simple Song Detail component
const SongDetail = () => (
  <div className="container mx-auto px-4 py-8">
    <nav className="mb-6">
      <Link to="/songs" className="text-blue-400 hover:text-blue-300 flex items-center gap-1">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to Song List
      </Link>
    </nav>

    <header className="mb-8">
      <h1 className="text-3xl font-bold text-white mb-2">Example Song</h1>
      <div className="flex flex-wrap gap-2 mb-4">
        <span className="px-2 py-0.5 bg-blue-900 text-blue-100 rounded text-xs">V2</span>
        <span className="px-2 py-0.5 bg-green-900 text-green-100 rounded text-xs">CDQ</span>
        <span className="px-2 py-0.5 bg-purple-900 text-purple-100 rounded text-xs">Studio</span>
      </div>
    </header>

    {/* Audio Preview */}
    <div className="bg-gray-800 p-4 rounded-lg mb-8">
      <h2 className="text-lg font-medium text-white mb-3">Audio Preview</h2>
      <audio 
        controls 
        className="w-full" 
        src="/sample-audio.mp3"
      >
        Your browser does not support the audio element.
      </audio>
    </div>

    {/* Song Details */}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
      <div className="bg-gray-800 p-4 rounded-lg">
        <h2 className="text-lg font-medium text-white mb-4">Details</h2>
        
        <div className="grid grid-cols-1 gap-4">
          <div>
            <h3 className="text-sm font-medium text-gray-400">Producer</h3>
            <p className="text-white">Metro Boomin</p>
          </div>
          
          <div>
            <h3 className="text-sm font-medium text-gray-400">Features</h3>
            <p className="text-white">Lil Uzi Vert</p>
          </div>
        </div>
      </div>
      
      <div className="bg-gray-800 p-4 rounded-lg">
        <h2 className="text-lg font-medium text-white mb-4">Additional Information</h2>
        
        <div className="grid grid-cols-1 gap-4">
          <div>
            <h3 className="text-sm font-medium text-gray-400">Track Length</h3>
            <p className="text-white">3:42</p>
          </div>
          
          <div>
            <h3 className="text-sm font-medium text-gray-400">Available Length</h3>
            <p className="text-white">Full</p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

// Main App component
const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gray-900 text-white">
        <nav className="bg-gray-800 px-4 py-3 shadow">
          <div className="container mx-auto flex justify-between items-center">
            <div className="text-xl font-bold">Carti Catalog</div>
            <div className="flex space-x-4">
              <Link to="/" className="hover:text-blue-400 transition-colors">Home</Link>
              <Link to="/songs" className="hover:text-blue-400 transition-colors">Song Library</Link>
            </div>
          </div>
        </nav>
        
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/songs" element={<SongsList />} />
            <Route path="/songs/:id" element={<SongDetail />} />
            <Route path="*" element={<Home />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;