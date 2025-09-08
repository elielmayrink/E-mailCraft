"""
Servidor local para testar a API usando BaseHTTPRequestHandler
"""
import sys
from pathlib import Path
from http.server import HTTPServer
from app import handler

def run_local_server(port=8002):
    """Executar servidor local para testes"""
    print(f"🚀 Iniciando servidor local na porta {port}")
    print(f"📍 Acesse: http://localhost:{port}/api/health")
    print(f"📍 API completa: http://localhost:{port}/api/")
    print(f"📍 Debug: http://localhost:{port}/api/debug")
    print()
    print("Endpoints disponíveis:")
    print("GET  /api/health - Health check")
    print("GET  /api/debug - Debug info")
    print("GET  /api/ - Lista de endpoints")
    print("GET  /api/auth/me - Auth info")
    print("GET  /api/gmail/status - Gmail status")
    print("POST /api/classify-text - Classificar email")
    print("POST /api/auth/verify-token - Verificar token")
    print()
    print("Pressione Ctrl+C para parar")
    
    try:
        server = HTTPServer(('localhost', port), handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado")
        server.server_close()

if __name__ == "__main__":
    # Permitir especificar porta como argumento
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
    run_local_server(port)
