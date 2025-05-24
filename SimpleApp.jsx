import React, { useState } from 'react';

// A very simple React app to test if React rendering works
const SimpleApp = () => {
  const [count, setCount] = useState(0);
  
  return (
    <div style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto', color: 'white' }}>
      <h1 style={{ marginBottom: '1rem' }}>Simple React App</h1>
      <p>This is a basic React component to test if React is working correctly.</p>
      
      <div style={{ 
        background: '#1f2937', 
        padding: '1.5rem', 
        borderRadius: '0.5rem',
        marginTop: '2rem'
      }}>
        <p>You clicked the button {count} times</p>
        <button 
          onClick={() => setCount(count + 1)}
          style={{
            background: '#3b82f6',
            color: 'white',
            padding: '0.5rem 1rem',
            borderRadius: '0.25rem',
            border: 'none',
            cursor: 'pointer',
            marginTop: '1rem'
          }}
        >
          Click me
        </button>
      </div>
      
      <div style={{ marginTop: '2rem' }}>
        <h2>Navigation</h2>
        <ul style={{ listStyleType: 'none', padding: 0 }}>
          <li style={{ marginBottom: '0.5rem' }}>
            <a 
              href="/landing.html" 
              style={{ color: '#60a5fa', textDecoration: 'none' }}
            >
              Go to Landing Page
            </a>
          </li>
          <li style={{ marginBottom: '0.5rem' }}>
            <a 
              href="/standalone.html" 
              style={{ color: '#60a5fa', textDecoration: 'none' }}
            >
              Go to Standalone HTML Version
            </a>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default SimpleApp;