#!/usr/bin/env python3
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8080):
    web_dir = os.path.join(os.path.dirname(__file__), 'webapp')
    os.chdir(web_dir)
    
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    print(f"Web application available at: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
