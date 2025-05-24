#!/usr/bin/env python
"""
Simple HTTP server to test if we can serve content on a port.
This doesn't use Django, just Python's built-in HTTP server.
"""

import http.server
import socketserver

PORT = 8020
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Test Server Working</h1><p>This is a simple Python HTTP server.</p></body></html>")
        else:
            super().do_GET()

def main():
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Serving at http://0.0.0.0:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()