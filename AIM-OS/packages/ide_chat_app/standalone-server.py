#!/usr/bin/env python3
"""
Standalone HTTP Server for AIM-OS Dashboard Panel
Serves the React UI outside of Cursor for browser testing

Usage:
    python standalone-server.py [--port PORT] [--build-dir DIR]

Options:
    --port PORT     Port to serve on (default: 3001)
    --build-dir DIR Directory containing built React UI (default: dist)
"""

import http.server
import socketserver
import os
import sys
import argparse
from pathlib import Path
from urllib.parse import urlparse

class StandaloneHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler to serve React UI with proper MIME types and CORS"""
    
    def __init__(self, *args, build_dir='dist', **kwargs):
        self.build_dir = Path(build_dir)
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for cross-origin requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.end_headers()
    
    def translate_path(self, path):
        """Translate URL path to file system path"""
        # Parse the path
        parsed = urlparse(path)
        path = parsed.path
        
        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]
        
        # If requesting root or standalone.html, serve standalone.html
        if path == '' or path == 'standalone.html' or path == 'index.html':
            standalone_path = Path(__file__).parent / 'standalone.html'
            if standalone_path.exists():
                return str(standalone_path)
            # Fallback to dist/index.html if standalone.html doesn't exist
            return str(self.build_dir / 'index.html')
        
        # Check if file exists in build directory
        build_path = self.build_dir / path
        if build_path.exists() and build_path.is_file():
            return str(build_path)
        
        # Check in parent directory (for assets, etc.)
        parent_path = Path(__file__).parent / path
        if parent_path.exists() and parent_path.is_file():
            return str(parent_path)
        
        # Default to build directory
        return str(self.build_dir / path)

def create_handler(build_dir):
    """Create request handler with build directory"""
    def handler(*args, **kwargs):
        return StandaloneHTTPRequestHandler(*args, build_dir=build_dir, **kwargs)
    return handler

def main():
    parser = argparse.ArgumentParser(description='Standalone HTTP Server for AIM-OS Dashboard')
    parser.add_argument('--port', type=int, default=3001, help='Port to serve on (default: 3001)')
    parser.add_argument('--build-dir', type=str, default='dist', help='Build directory (default: dist)')
    args = parser.parse_args()
    
    # Check if build directory exists
    build_path = Path(args.build_dir)
    if not build_path.exists():
        print(f"❌ Error: Build directory '{args.build_dir}' does not exist!")
        print(f"   Please build the React UI first:")
        print(f"   cd packages/ide_chat_app")
        print(f"   npm run build")
        sys.exit(1)
    
    # Change to package directory
    package_dir = Path(__file__).parent
    os.chdir(package_dir)
    
    # Create handler
    handler = create_handler(args.build_dir)
    
    # Start server
    try:
        with socketserver.TCPServer(("", args.port), handler) as httpd:
            print("=" * 60)
            print("🚀 AIM-OS Dashboard Standalone Server")
            print("=" * 60)
            print(f"📦 Build directory: {build_path.absolute()}")
            print(f"🌐 Server running at: http://localhost:{args.port}")
            print(f"📄 Dashboard URL: http://localhost:{args.port}/standalone.html")
            print("=" * 60)
            print("Press Ctrl+C to stop the server")
            print("=" * 60)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ Error: Port {args.port} is already in use!")
            print(f"   Try a different port: python standalone-server.py --port 3002")
        else:
            print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

