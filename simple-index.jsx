import React from 'react';
import ReactDOM from 'react-dom/client';
import SimpleApp from './SimpleApp.jsx';
import './index.css';

// Simple logging to verify initialization
console.log('Simple React application is initializing...');

// Create the root and render the App
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <SimpleApp />
  </React.StrictMode>
);