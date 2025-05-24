#!/usr/bin/env python
"""Basic socket test to see if we can run a server at all."""
import socket
import time

def run_server():
    try:
        # Create a socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Attempt to bind to localhost on port 8050
            s.bind(('127.0.0.1', 8050))
            
            # Set socket options
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Listen for connections
            s.listen(1)
            print(f"Server is listening on 127.0.0.1:8050")
            
            # Set a timeout of 30 seconds
            s.settimeout(30)
            
            try:
                # Accept a connection
                conn, addr = s.accept()
                print(f"Connected by {addr}")
                
                # Send a simple response and close
                with conn:
                    conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 13\r\n\r\nHello, World!")
                
                print("Connection handled")
            except socket.timeout:
                print("Timed out waiting for connection")
                
            print("Test completed")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_server()