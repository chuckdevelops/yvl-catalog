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
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.mp3': 'audio/mpeg',
  '.mp4': 'video/mp4',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.otf': 'font/otf',
  '.eot': 'application/vnd.ms-fontobject'
};

// Create a simple HTTP server
const server = http.createServer((req, res) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  
  // Parse URL to get pathname
  let pathname = req.url;
  
  // Handle SPA routes
  if (pathname === '/' || 
      !pathname.includes('.') || 
      pathname.startsWith('/list') || 
      pathname.startsWith('/home')) {
    pathname = '/index.html';
  }
  
  // Full path to the requested file
  let filePath = path.join(__dirname, 'dist', pathname);
  
  // Check if file exists and serve it
  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      // Fall back to index.html for client-side routing
      filePath = path.join(__dirname, 'dist', 'index.html');
    }
    
    // Get file extension to determine content type
    const ext = path.extname(filePath);
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    
    // Read and serve the file
    fs.readFile(filePath, (err, data) => {
      if (err) {
        console.error(`Error reading file: ${filePath}`, err);
        res.writeHead(500);
        res.end('Internal Server Error');
        return;
      }
      
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    });
  });
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log(`You can also try http://127.0.0.1:${PORT}`);
});