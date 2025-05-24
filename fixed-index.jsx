import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './fixed-app.jsx';
import './index.css';

// Simple logging to verify that the script is executing
console.log('React application is initializing from fixed index...');

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', () => {
  const rootElement = document.getElementById('root');
  
  if (rootElement) {
    // Create the root and render the App
    const root = ReactDOM.createRoot(rootElement);
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    );
    console.log('React app rendered successfully');
  } else {
    console.error('Could not find root element to mount React app');
  }
});