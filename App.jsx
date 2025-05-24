import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './Home.jsx';
import List from './List.jsx';

// Simple fallback component for debugging
const Fallback = () => (
  <div className="p-8">
    <h1 className="text-2xl font-bold mb-4">Fallback Page</h1>
    <p>This is a simple fallback page for debugging.</p>
    <div className="mt-4">
      <Link to="/" className="text-blue-400 hover:underline mr-4">Go to Home</Link>
      <Link to="/list" className="text-blue-400 hover:underline">Go to List</Link>
    </div>
  </div>
);

const App = () => {
  // Add error boundary to catch and display rendering errors
  try {
    return (
      <Router>
        <div className="min-h-screen bg-gray-900 text-white">
          <nav className="bg-gray-800 px-4 py-3 shadow">
            <div className="container mx-auto flex justify-between items-center">
              <div className="text-xl font-bold">Carti Catalog</div>
              <div className="flex space-x-4">
                <Link to="/" className="hover:text-blue-400 transition-colors">Home</Link>
                <Link to="/list" className="hover:text-blue-400 transition-colors">Song Library</Link>
              </div>
            </div>
          </nav>
          
          <main>
            <Routes>
              <Route path="/" element={<Fallback />} />
              <Route path="/home" element={<Home />} />
              <Route path="/list" element={<List />} />
              <Route path="*" element={<Fallback />} />
            </Routes>
          </main>
        </div>
      </Router>
    );
  } catch (error) {
    console.error('Error rendering App:', error);
    return (
      <div className="p-8 bg-gray-900 text-white min-h-screen">
        <h1 className="text-2xl font-bold mb-4">Error Rendering App</h1>
        <p className="text-red-400">{error.message}</p>
        <pre className="mt-4 bg-gray-800 p-4 rounded overflow-auto">
          {error.stack}
        </pre>
      </div>
    );
  }
};

export default App;