"""
Handler alternativo para Vercel - compatibilidade máxima
"""
import json
import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    """
    Handler de baixo nível compatível com Vercel usando BaseHTTPRequestHandler
    """
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = self.path
            
            # Log básico para debug
            print(f"Request: GET {path}")
            
            # Determinar resposta baseada no path
            if path in ['/health', '/api/health']:
                response_data = {
                    'status': 'healthy',
                    'message': 'API funcionando via handler BaseHTTPRequestHandler!',
                    'path': path,
                    'handler': 'handler.py'
                }
            elif path in ['/debug', '/api/debug']:
                response_data = {
                    'status': 'debug',
                    'message': 'Debug endpoint funcionando!',
                    'environment': {
                        'VERCEL': os.getenv('VERCEL'),
                        'PYTHON_VERSION': os.getenv('PYTHON_VERSION'),
                    },
                    'path': path,
                    'handler': 'handler.py'
                }
            elif path in ['/', '/api/', '/api']:
                response_data = {
                    'status': 'ok',
                    'message': 'Handler BaseHTTPRequestHandler funcionando!',
                    'available_endpoints': ['/health', '/debug', '/'],
                    'handler': 'handler.py'
                }
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_data = {
                    'error': 'Endpoint não encontrado',
                    'path': path,
                    'available_endpoints': ['/health', '/debug', '/'],
                    'handler': 'handler.py'
                }
                self.wfile.write(json.dumps(error_data).encode())
                return
            
            # Enviar resposta de sucesso
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_data = {
                'error': 'Erro interno do servidor',
                'details': str(e),
                'handler': 'handler.py'
            }
            self.wfile.write(json.dumps(error_data).encode())
