const http = require('http');
const fs = require('fs');
const path = require('path');
const PORT = 4173;

const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.mp3': 'audio/mpeg',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2'
};

// Create a server with detailed logging
const server = http.createServer((req, res) => {
  console.log(`\n${new Date().toISOString()} - ${req.method} ${req.url}`);
  
  // Parse URL to get pathname
  let pathname = req.url;
  
  // Handle API requests with mock data
  if (pathname.startsWith('/api/')) {
    console.log(`Handling API request: ${pathname}`);
    res.setHeader('Content-Type', 'application/json');
    
    if (pathname === '/api/home/') {
      console.log('Returning mock home data');
      res.writeHead(200);
      res.end(JSON.stringify({
        stats: {
          total_songs: 432,
          distinct_eras: 8,
          sheet_tabs: [
            { id: 1, name: "V1", icon: "🔴", count: 78 },
            { id: 2, name: "V2", icon: "🟠", count: 120 },
            { id: 3, name: "WLR", icon: "🟣", count: 64 }
          ]
        },
        recent_songs: Array(10).fill(null).map((_, i) => ({
          id: i + 1,
          name: `Example Song ${i + 1}`,
          producer: "Producer Example",
          era: "V2",
          preview_file_exists: true,
          preview_audio_url: '/sample-audio.mp3'
        }))
      }));
      return;
    }
    
    if (pathname.startsWith('/api/songs/')) {
      console.log('Returning mock song data');
      res.writeHead(200);
      res.end(JSON.stringify({
        id: 1,
        name: "Example Song",
        producer: "Metro Boomin",
        era: "V2",
        preview_file_exists: true,
        preview_audio_url: '/sample-audio.mp3'
      }));
      return;
    }
    
    console.log('Unknown API endpoint, returning 404');
    res.writeHead(404);
    res.end(JSON.stringify({ error: "API endpoint not found" }));
    return;
  }
  
  // If requesting the root, serve the react app
  if (pathname === '/') {
    pathname = '/index.html';
    console.log('Redirecting / to /index.html');
  }
  
  // For SPA routes, serve index.html
  if (pathname.startsWith('/list') || pathname.startsWith('/home')) {
    pathname = '/index.html';
    console.log(`SPA route detected, serving index.html instead of ${req.url}`);
  }
  
  // If no specific file requested, try the landing page
  if (pathname === '/landing' || pathname === '/landing/') {
    pathname = '/landing.html';
    console.log('Redirecting to landing page');
  }
  
  // Construct the file path in the dist directory
  const filePath = path.join(__dirname, 'dist', pathname);
  console.log(`Attempting to serve: ${filePath}`);
  
  // Check if the file exists
  fs.stat(filePath, (err, stats) => {
    if (err) {
      console.error(`File not found: ${filePath}`);
      console.log(`Falling back to landing.html`);
      
      // If file doesn't exist, serve the landing page
      const fallbackPath = path.join(__dirname, 'dist', 'landing.html');
      fs.readFile(fallbackPath, (err, data) => {
        if (err) {
          console.error(`Even fallback not found: ${fallbackPath}`);
          res.writeHead(500);
          res.end('Server Error: Could not find even the fallback page.');
          return;
        }
        
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(data);
      });
      return;
    }
    
    if (!stats.isFile()) {
      console.error(`Not a file: ${filePath}`);
      res.writeHead(404);
      res.end('Not a file');
      return;
    }
    
    // Get the file extension
    const ext = path.extname(filePath);
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    console.log(`Serving ${filePath} with content type ${contentType}`);
    
    // Read the file
    fs.readFile(filePath, (err, data) => {
      if (err) {
        console.error(`Error reading file: ${err.message}`);
        res.writeHead(500);
        res.end('Server Error: Could not read file');
        return;
      }
      
      // Add CORS headers
      res.writeHead(200, { 
        'Content-Type': contentType,
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
      });
      res.end(data);
      console.log(`Successfully served ${filePath}`);
    });
  });
});

server.listen(PORT, () => {
  console.log(`Debug server running at http://localhost:${PORT}`);
  console.log(`You can also try http://127.0.0.1:${PORT}`);
  console.log(`\nAvailable pages:`);
  console.log(`- http://localhost:${PORT}/landing.html (Landing page)`);
  console.log(`- http://localhost:${PORT}/standalone.html (HTML version)`);
  console.log(`- http://localhost:${PORT}/index.html (React app)`);
  console.log(`\nAPI endpoints:`);
  console.log(`- http://localhost:${PORT}/api/home/ (Home data)`);
  console.log(`- http://localhost:${PORT}/api/songs/ (Song list)`);
});