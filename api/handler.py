"""
Handler alternativo para Vercel - compatibilidade máxima
"""
import json
import os
from urllib.parse import urlparse, parse_qs

def handler(request, context):
    """
    Handler de baixo nível compatível com Vercel
    """
    try:
        # Extrair informações da requisição
        method = request.get('method', 'GET')
        path = request.get('path', '/')
        
        # Log básico para debug
        print(f"Request: {method} {path}")
        
        # Roteamento simples
        if path == '/api/health' or path == '/health':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'healthy',
                    'message': 'API funcionando via handler direto!',
                    'method': method,
                    'path': path,
                    'handler': 'handler.py'
                })
            }
        
        elif path == '/api/debug' or path == '/debug':
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'debug',
                    'message': 'Debug endpoint funcionando!',
                    'environment': {
                        'VERCEL': os.getenv('VERCEL'),
                        'PYTHON_VERSION': os.getenv('PYTHON_VERSION'),
                    },
                    'request_info': {
                        'method': method,
                        'path': path,
                        'headers': request.get('headers', {}),
                    },
                    'handler': 'handler.py'
                })
            }
        
        elif path in ['/', '/api/', '/api']:
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'status': 'ok',
                    'message': 'Handler alternativo funcionando!',
                    'available_endpoints': [
                        '/api/health',
                        '/api/debug',
                        '/api/'
                    ],
                    'handler': 'handler.py'
                })
            }
        
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'error': 'Endpoint não encontrado',
                    'path': path,
                    'available_endpoints': ['/api/health', '/api/debug', '/api/'],
                    'handler': 'handler.py'
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'error': 'Erro interno do servidor',
                'details': str(e),
                'handler': 'handler.py'
            })
        }
