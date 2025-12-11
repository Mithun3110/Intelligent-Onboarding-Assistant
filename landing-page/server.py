"""
Simple HTTP Server for Landing Page
Serves the beautiful landing page and redirects to Streamlit app
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import webbrowser
from pathlib import Path

class LandingPageHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            landing_page = Path(__file__).parent / 'index.html'
            with open(landing_page, 'rb') as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()

    def end_headers(self):
        # Enable CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

if __name__ == '__main__':
    # Change to landing page directory
    os.chdir(Path(__file__).parent)
    
    PORT = 8000
    SERVER = HTTPServer(('localhost', PORT), LandingPageHandler)
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   🚀  GitLab Onboarding Assistant Landing Page          ║
    ║                                                          ║
    ║   Landing Page:  http://localhost:{PORT}                  ║
    ║   Streamlit App: http://localhost:8502                  ║
    ║                                                          ║
    ║   Press Ctrl+C to stop the server                       ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Open in browser
    import threading
    import time
    def open_browser():
        time.sleep(1)
        webbrowser.open(f'http://localhost:{PORT}')
    
    threading.Thread(target=open_browser, daemon=True).start()
    
    try:
        SERVER.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✨ Server stopped. Thanks for using GitLab Onboarding Intelligence!")
        exit(0)
