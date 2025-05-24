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

const server = http.createServer((req, res) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  
  // Parse URL to get pathname
  let pathname = req.url;
  
  // Handle routes for SPA
  if (pathname.startsWith('/list') || pathname.startsWith('/home') || pathname === '/') {
    pathname = '/index.html';
  }
  
  // Serve directly from dist directory
  let filePath = path.join(__dirname, 'dist', pathname);
  
  // Check if the file exists
  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (err) {
      // If file doesn't exist, serve index.html for SPA routing
      filePath = path.join(__dirname, 'dist', 'index.html');
    }
    
    // Get the file extension
    const ext = path.extname(filePath);
    
    // Set the content type based on file extension
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    
    // Read the file
    fs.readFile(filePath, (err, data) => {
      if (err) {
        console.error(`Error reading file: ${filePath}`, err);
        res.writeHead(500);
        res.end('Server Error');
        return;
      }
      
      // Send the response
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    });
  });
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log(`You can also try http://127.0.0.1:${PORT}`);
});