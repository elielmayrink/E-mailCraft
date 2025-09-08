import json
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {
            'message': 'Hello from Vercel Python!',
            'path': self.path,
            'status': 'success'
        }
        self.wfile.write(json.dumps(response).encode())
        return
