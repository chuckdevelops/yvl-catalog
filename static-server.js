const http = require('http');
const fs = require('fs');
const path = require('path');
const PORT = 4174; // Changed port to avoid conflict

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

// Create a basic static file server
const server = http.createServer((req, res) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  
  // Parse URL to get pathname
  let pathname = req.url;
  
  // Remove query string if present
  if (pathname.includes('?')) {
    pathname = pathname.split('?')[0];
  }
  
  // Handle root request
  if (pathname === '/') {
    pathname = '/debug.html'; // Default to debug.html for testing
  }
  
  // Look in different directories for files
  const publicPath = path.join(__dirname, 'public', pathname);
  const distPath = path.join(__dirname, 'dist', pathname);
  const rootPath = path.join(__dirname, pathname.substring(1)); // Remove leading slash
  
  // Try to serve from public directory first
  fs.access(publicPath, fs.constants.F_OK, (publicErr) => {
    if (!publicErr) {
      serveFile(publicPath, res);
      return;
    }
    
    // Next, try dist directory
    fs.access(distPath, fs.constants.F_OK, (distErr) => {
      if (!distErr) {
        serveFile(distPath, res);
        return;
      }
      
      // Finally, try root directory
      fs.access(rootPath, fs.constants.F_OK, (rootErr) => {
        if (!rootErr) {
          serveFile(rootPath, res);
          return;
        }
        
        // File not found in any location
        console.log(`File not found: ${pathname}`);
        res.writeHead(404);
        res.end('File not found');
      });
    });
  });
});

function serveFile(filePath, res) {
  // Get the file extension
  const ext = path.extname(filePath);
  const contentType = MIME_TYPES[ext] || 'application/octet-stream';
  
  // Read and serve the file
  fs.readFile(filePath, (err, data) => {
    if (err) {
      console.error(`Error reading file: ${filePath}`, err);
      res.writeHead(500);
      res.end('Server Error');
      return;
    }
    
    // Add CORS headers for development
    res.writeHead(200, {
      'Content-Type': contentType,
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    
    res.end(data);
    console.log(`Served: ${filePath}`);
  });
}

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
  console.log(`You can also try http://127.0.0.1:${PORT}`);
  console.log(`\nTry accessing:`);
  console.log(`- http://localhost:${PORT}/debug.html`);
  console.log(`- http://localhost:${PORT}/index.html`);
  console.log(`- http://localhost:${PORT}/public/debug.html`);
});