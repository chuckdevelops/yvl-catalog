#\!/usr/bin/env python3

import http.server
import socketserver

# Configure the server
PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map.update({
    '.mp3': 'audio/mpeg',
})

print(f"Starting simple HTTP server at http://localhost:{PORT}/")
print("This server will directly serve MP3 files without Django middleware")
print("Open your browser to http://localhost:8080/ to test all audio files")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
