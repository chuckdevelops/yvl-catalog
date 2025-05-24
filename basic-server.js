const http = require('http');
const fs = require('fs');
const path = require('path');
const PORT = 4176; // Changed port

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

// Create a very basic static file server
const server = http.createServer((req, res) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  
  // Parse URL to get pathname
  let pathname = req.url;
  
  // Remove query string if present
  if (pathname.includes('?')) {
    pathname = pathname.split('?')[0];
  }
  
  // Handle root request - serve a list of available HTML files
  if (pathname === '/') {
    listHtmlFiles(res);
    return;
  }
  
  // Direct file serving - no React, no routing
  const filePath = path.join(__dirname, pathname);
  
  // Check if file exists
  fs.access(filePath, fs.constants.F_OK, (err) => {
    if (err) {
      console.log(`File not found: ${filePath}`);
      res.writeHead(404);
      res.end('File not found');
      return;
    }
    
    // Check if it's a directory
    fs.stat(filePath, (err, stats) => {
      if (err) {
        res.writeHead(500);
        res.end('Server Error');
        return;
      }
      
      if (stats.isDirectory()) {
        // List directory contents
        listDirectoryContents(filePath, pathname, res);
        return;
      }
      
      // It's a file, serve it
      serveFile(filePath, res);
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
    
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(data);
    console.log(`Served: ${filePath}`);
  });
}

function listHtmlFiles(res) {
  // Find all HTML files in the project for easy navigation
  fs.readdir(__dirname, { withFileTypes: true }, (err, entries) => {
    if (err) {
      res.writeHead(500);
      res.end('Error listing files');
      return;
    }
    
    let html = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Simple File Server</title>
          <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 10px 0; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .file { background: #f0f0f0; padding: 5px 10px; border-radius: 3px; }
            .dir { background: #e0e0ff; padding: 5px 10px; border-radius: 3px; }
          </style>
        </head>
        <body>
          <h1>Simple File Server</h1>
          <h2>Directories</h2>
          <ul>
    `;
    
    // Add directories
    entries.filter(entry => entry.isDirectory())
      .forEach(dir => {
        html += `<li><a class="dir" href="/${dir.name}/">${dir.name}/</a></li>`;
      });
    
    html += `</ul><h2>HTML Files</h2><ul>`;
    
    // Add HTML files
    entries.filter(entry => entry.isFile() && entry.name.endsWith('.html'))
      .forEach(file => {
        html += `<li><a class="file" href="/${file.name}">${file.name}</a></li>`;
      });
    
    html += `
          </ul>
          <h2>Other Files</h2>
          <ul>
    `;
    
    // Add other key files
    entries.filter(entry => entry.isFile() && !entry.name.endsWith('.html') && 
                 (entry.name.endsWith('.js') || entry.name.endsWith('.css') || entry.name.endsWith('.mp3')))
      .forEach(file => {
        html += `<li><a class="file" href="/${file.name}">${file.name}</a></li>`;
      });
    
    html += `
          </ul>
        </body>
      </html>
    `;
    
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(html);
  });
}

function listDirectoryContents(dirPath, urlPath, res) {
  fs.readdir(dirPath, { withFileTypes: true }, (err, entries) => {
    if (err) {
      res.writeHead(500);
      res.end('Error listing directory');
      return;
    }
    
    let html = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Directory: ${urlPath}</title>
          <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #333; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 10px 0; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .file { background: #f0f0f0; padding: 5px 10px; border-radius: 3px; }
            .dir { background: #e0e0ff; padding: 5px 10px; border-radius: 3px; }
            .back { display: inline-block; margin-bottom: 20px; }
          </style>
        </head>
        <body>
          <h1>Directory: ${urlPath}</h1>
          <a class="back" href="/">Back to Home</a>
          <ul>
    `;
    
    // Add parent directory link if not at root
    if (urlPath !== '/') {
      const parentPath = urlPath.split('/').slice(0, -2).join('/') + '/';
      html += `<li><a class="dir" href="${parentPath}">..</a> (Parent Directory)</li>`;
    }
    
    // Add directories first
    entries.filter(entry => entry.isDirectory())
      .forEach(dir => {
        const link = `${urlPath}${dir.name}/`;
        html += `<li><a class="dir" href="${link}">${dir.name}/</a></li>`;
      });
    
    // Then add files
    entries.filter(entry => entry.isFile())
      .forEach(file => {
        const link = `${urlPath}${file.name}`;
        html += `<li><a class="file" href="${link}">${file.name}</a></li>`;
      });
    
    html += `
          </ul>
        </body>
      </html>
    `;
    
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(html);
  });
}

server.listen(PORT, () => {
  console.log(`Basic file server running at http://localhost:${PORT}`);
  console.log(`This server simply serves static files without any React or routing.`);
});