"""
API principal usando BaseHTTPRequestHandler - compatível com Vercel
Migração completa da funcionalidade original
"""
import json
import os
import sys
import traceback
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# Configurar paths para importar módulos do backend
current_file = Path(__file__).resolve()
api_root = current_file.parent
project_root = api_root.parent
backend_root = project_root / "backend"

# Adicionar paths necessários ao sys.path
paths_to_add = [str(backend_root), str(project_root), str(api_root)]
for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# Importar módulos do backend com fallback
try:
    # Tentar importação relativa primeiro
    from models.classifier import EmailClassifier
    from models.response_generator import ResponseGenerator
    from utils.text_processor import TextProcessor
    from integrations.gmail_service import GmailService
    from database import get_db, create_tables
    from auth.firebase_auth import get_current_user, verify_firebase_token
    from models.user import User
    print("✅ Imports relativos bem-sucedidos")
except ImportError as e:
    print(f"❌ Falha no import relativo: {e}")
    # Fallback para imports absolutos
    try:
        from backend.models.classifier import EmailClassifier
        from backend.models.response_generator import ResponseGenerator
        from backend.utils.text_processor import TextProcessor
        from backend.integrations.gmail_service import GmailService
        from backend.database import get_db, create_tables
        from backend.auth.firebase_auth import get_current_user, verify_firebase_token
        from backend.models.user import User
        print("✅ Imports absolutos bem-sucedidos")
    except ImportError as e2:
        print(f"❌ Falha no import absoluto: {e2}")
        # Usar placeholders se imports falharem
        EmailClassifier = None
        ResponseGenerator = None
        TextProcessor = None
        GmailService = None

class handler(BaseHTTPRequestHandler):
    """
    Handler principal da API usando BaseHTTPRequestHandler
    """
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            path = self.path
            parsed_url = urlparse(path)
            route = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            print(f"GET Request: {route}")
            
            # Normalizar rota (remover prefixo /api se presente)
            if route.startswith('/api'):
                route = route[4:]  # Remove '/api'
            if not route:
                route = '/'
            
            # Roteamento para endpoints GET
            if route == '/health':
                self._handle_health()
            elif route == '/debug':
                self._handle_debug()
            elif route == '/':
                self._handle_root()
            elif route == '/auth/me':
                self._handle_auth_me()
            elif route == '/gmail/status':
                self._handle_gmail_status()
            elif route == '/gmail/auth-url':
                self._handle_gmail_auth_url()
            elif route == '/gmail/oauth2callback':
                self._handle_gmail_oauth_callback(query_params)
            elif route == '/gmail/preview':
                self._handle_gmail_preview(query_params)
            else:
                self._send_error(404, f"Endpoint não encontrado: {route}")
                
        except Exception as e:
            self._send_error(500, f"Erro interno: {str(e)}", traceback.format_exc())
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            path = self.path
            parsed_url = urlparse(path)
            route = parsed_url.path
            
            # Ler dados do corpo da requisição
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8')) if post_data else {}
            except json.JSONDecodeError:
                data = {}
            
            print(f"POST Request: {route}")
            
            # Normalizar rota (remover prefixo /api se presente)
            if route.startswith('/api'):
                route = route[4:]  # Remove '/api'
            if not route:
                route = '/'
            
            # Roteamento para endpoints POST
            if route == '/classify-text':
                self._handle_classify_text(data)
            elif route == '/classify-file':
                self._handle_classify_file()
            elif route == '/test-ai':
                self._handle_test_ai(data)
            elif route == '/configure-ai':
                self._handle_configure_ai(data)
            elif route == '/auth/verify-token':
                self._handle_verify_token(data)
            elif route == '/gmail/connect':
                self._handle_gmail_connect(data)
            elif route == '/gmail/disconnect':
                self._handle_gmail_disconnect()
            elif route == '/gmail/send':
                self._handle_gmail_send(data)
            elif route == '/gmail/mark-read':
                self._handle_gmail_mark_read(data)
            else:
                self._send_error(404, f"Endpoint não encontrado: {route}")
                
        except Exception as e:
            self._send_error(500, f"Erro interno: {str(e)}", traceback.format_exc())
    
    def _send_json_response(self, data, status_code=200):
        """Enviar resposta JSON"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _send_error(self, status_code, message, details=None):
        """Enviar resposta de erro"""
        error_data = {
            'error': message,
            'status_code': status_code,
            'path': self.path
        }
        if details and os.getenv('DEBUG'):
            error_data['details'] = details
        self._send_json_response(error_data, status_code)
    
    # Handlers específicos dos endpoints
    def _handle_health(self):
        """Health check endpoint"""
        try:
            # Tentar verificar acesso ao banco se possível
            db_status = "unknown"
            if 'get_db' in globals():
                try:
                    next(get_db())
                    db_status = "connected"
                except:
                    db_status = "error"
            
            self._send_json_response({
                'status': 'healthy',
                'message': 'API funcionando corretamente via BaseHTTPRequestHandler!',
                'components': {
                    'database': db_status,
                    'email_classifier': EmailClassifier is not None,
                    'response_generator': ResponseGenerator is not None,
                    'text_processor': TextProcessor is not None,
                    'gmail_service': GmailService is not None
                },
                'handler': 'app.py'
            })
        except Exception as e:
            self._send_error(500, f"Health check falhou: {str(e)}")
    
    def _handle_debug(self):
        """Debug endpoint"""
        self._send_json_response({
            'status': 'debug',
            'environment': {
                'VERCEL': os.getenv('VERCEL'),
                'PYTHON_VERSION': os.getenv('PYTHON_VERSION'),
                'DEBUG': os.getenv('DEBUG'),
            },
            'paths': {
                'backend_root': str(backend_root),
                'project_root': str(project_root),
                'api_root': str(api_root)
            },
            'imports': {
                'EmailClassifier': EmailClassifier is not None,
                'ResponseGenerator': ResponseGenerator is not None,
                'TextProcessor': TextProcessor is not None,
                'GmailService': GmailService is not None
            },
            'message': 'Debug endpoint funcionando!',
            'handler': 'app.py'
        })
    
    def _handle_root(self):
        """Root endpoint"""
        self._send_json_response({
            'status': 'ok',
            'message': 'Email Classification API funcionando!',
            'title': 'Email Classification API',
            'version': '1.0.0',
            'features': {
                'email_classification': 'Funcional',
                'firebase_auth': 'Demonstração',
                'gmail_integration': 'Demonstração',
                'ai_integration': 'Demonstração'
            },
            'available_endpoints': {
                'GET': {
                    '/health': 'Health check completo',
                    '/debug': 'Informações de debug',
                    '/auth/me': 'Informações do usuário autenticado',
                    '/gmail/status': 'Status da conexão Gmail',
                    '/gmail/auth-url': 'URL de autorização Gmail',
                    '/gmail/preview': 'Preview de emails Gmail',
                    '/gmail/oauth2callback': 'Callback OAuth Gmail'
                },
                'POST': {
                    '/classify-text': 'Classificar texto de email',
                    '/test-ai': 'Testar integração IA',
                    '/configure-ai': 'Configurar IA',
                    '/auth/verify-token': 'Verificar token Firebase',
                    '/gmail/connect': 'Conectar Gmail',
                    '/gmail/disconnect': 'Desconectar Gmail',
                    '/gmail/send': 'Enviar email via Gmail',
                    '/gmail/mark-read': 'Marcar email como lido'
                }
            },
            'notes': {
                'production_ready': ['classify-text', 'health', 'debug'],
                'demo_mode': ['firebase_auth', 'gmail_integration', 'ai_integration'],
                'configuration_required': [
                    'Firebase Admin SDK credentials',
                    'Gmail OAuth credentials',
                    'Gemini AI API key'
                ]
            },
            'handler': 'app.py'
        })
    
    def _handle_classify_text(self, data):
        """Classificar texto de email"""
        try:
            text = data.get("text", "")
            if not text or not text.strip():
                self._send_error(400, "Texto do email é obrigatório")
                return
            
            # Verificar se componentes estão disponíveis
            if not all([EmailClassifier, ResponseGenerator, TextProcessor]):
                self._send_error(503, "Componentes de classificação não disponíveis")
                return
            
            # Inicializar componentes
            classifier = EmailClassifier()
            response_generator = ResponseGenerator()
            text_processor = TextProcessor()
            
            # Processar texto
            processed_text = text_processor.process(text)
            
            # Classificar
            classification_result = classifier.predict(processed_text)
            category = classification_result["category"]
            
            # Gerar resposta
            response = response_generator.generate(category, processed_text)
            
            self._send_json_response({
                "category": category,
                "response": response,
                "confidence": classification_result["confidence"],
                "method": classification_result["method"],
                "model_info": classification_result["model_info"]
            })
            
        except Exception as e:
            self._send_error(500, f"Erro ao processar email: {str(e)}")
    
    def _handle_test_ai(self, data):
        """Teste da IA"""
        try:
            question = data.get("question", "Diga apenas 'Olá, IA funcionando!' em português")
            
            self._send_json_response({
                "status": "success",
                "question": question,
                "answer": "Olá, IA funcionando! (modo de demonstração)",
                "model": "demo-mode",
                "note": "API key necessária para IA real"
            })
            
        except Exception as e:
            self._send_error(500, f"Erro no teste de IA: {str(e)}")
    
    def _handle_configure_ai(self, data):
        """Configurar IA"""
        try:
            api_key = data.get("api_key", "")
            if not api_key:
                self._send_error(400, "API key é obrigatória")
                return
            
            self._send_json_response({
                "status": "success", 
                "message": "IA configurada com sucesso! (demonstração)",
                "note": "Implementação completa requer configuração adequada"
            })
            
        except Exception as e:
            self._send_error(500, f"Erro ao configurar IA: {str(e)}")
    
    # Endpoints de autenticação Firebase
    def _handle_auth_me(self):
        """Obter informações do usuário atual"""
        try:
            # Implementação simplificada - em produção requer header Authorization
            # Por enquanto, retorna informações de debug
            self._send_json_response({
                "error": "Token de autorização necessário",
                "message": "Inclua 'Authorization: Bearer <token>' no header",
                "status": "authentication_required",
                "endpoint": "/auth/me"
            }, 401)
        except Exception as e:
            self._send_error(500, f"Erro na autenticação: {str(e)}")
    
    def _handle_verify_token(self, data):
        """Verificar token Firebase e criar/atualizar usuário no banco"""
        try:
            # Implementação simplificada para demonstração
            token = data.get("token") or data.get("idToken")
            if not token:
                self._send_error(400, "Token Firebase é obrigatório")
                return
            
            # Em produção, aqui verificaríamos o token com Firebase Admin
            # Por enquanto, retornamos resposta de sucesso simulada
            self._send_json_response({
                "valid": True,
                "user": {
                    "uid": "demo_user_uid",
                    "email": "demo@example.com", 
                    "name": "Demo User",
                    "picture": None
                },
                "db_user": {
                    "id": 1,
                    "firebase_uid": "demo_user_uid",
                    "email": "demo@example.com",
                    "name": "Demo User",
                    "created_at": "2024-01-01T00:00:00Z"
                },
                "note": "Modo demonstração - configuração Firebase necessária para produção"
            })
        except Exception as e:
            self._send_error(500, f"Erro ao verificar token: {str(e)}")
    
    def _handle_gmail_status(self):
        """Verificar status da conexão Gmail"""
        try:
            # Implementação simplificada para demonstração
            self._send_json_response({
                "connected": False,
                "last_sync": None,
                "message": "Gmail não conectado - use /gmail/auth-url para conectar",
                "note": "Modo demonstração - credenciais OAuth necessárias para produção"
            })
        except Exception as e:
            self._send_error(500, f"Erro ao verificar status Gmail: {str(e)}")
    
    def _handle_gmail_auth_url(self):
        """Obter URL de autorização do Gmail"""
        try:
            # Implementação simplificada para demonstração
            client_id = os.getenv("GMAIL_CLIENT_ID")
            if not client_id:
                self._send_json_response({
                    "error": "Configuração OAuth Gmail não encontrada",
                    "message": "Configure GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET e GMAIL_REDIRECT_URI",
                    "required_env_vars": [
                        "GMAIL_CLIENT_ID",
                        "GMAIL_CLIENT_SECRET", 
                        "GMAIL_REDIRECT_URI"
                    ]
                }, 503)
                return
            
            # URL de exemplo - em produção seria gerada dinamicamente
            demo_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&redirect_uri=REDIRECT_URI&response_type=code&scope=gmail.readonly gmail.send gmail.modify&access_type=offline&prompt=consent"
            
            self._send_json_response({
                "auth_url": demo_auth_url,
                "note": "URL de demonstração - configuração OAuth necessária para produção"
            })
        except Exception as e:
            self._send_error(500, f"Erro ao gerar URL de autorização: {str(e)}")
    
    def _handle_gmail_oauth_callback(self, query_params):
        """Callback do OAuth2 do Gmail"""
        try:
            code = query_params.get('code', [None])[0]
            state = query_params.get('state', [None])[0]
            error = query_params.get('error', [None])[0]
            
            if error:
                self._send_error(400, f"Erro na autorização: {error}")
                return
                
            if not code or not state:
                self._send_error(400, "Código de autorização ou state não fornecidos")
                return
            
            # Em produção, aqui trocaria o code por tokens e salvaria no banco
            self._send_json_response({
                "status": "success",
                "message": "Autorização Gmail recebida com sucesso!",
                "code": code,
                "state": state,
                "note": "Modo demonstração - implementação completa OAuth necessária"
            })
        except Exception as e:
            self._send_error(500, f"Erro no callback OAuth2: {str(e)}")
    
    def _handle_gmail_preview(self, query_params):
        """Preview de emails Gmail"""
        try:
            limit = int(query_params.get('limit', [5])[0])
            
            # Dados de demonstração
            demo_emails = [
                {
                    "id": "demo_email_1",
                    "threadId": "demo_thread_1",
                    "from": "demo@example.com",
                    "subject": "Solicitação de suporte técnico",
                    "snippet": "Preciso de ajuda com o sistema de pagamento...",
                    "category": "Produtivo",
                    "confidence": 0.9,
                    "method": "demo",
                    "model_info": "Classificação de demonstração",
                    "suggested_response": "Obrigado pelo contato. Nossa equipe técnica analisará sua solicitação."
                },
                {
                    "id": "demo_email_2", 
                    "threadId": "demo_thread_2",
                    "from": "cliente@example.com",
                    "subject": "Obrigado pelo atendimento",
                    "snippet": "Muito obrigado pelo excelente atendimento...",
                    "category": "Improdutivo",
                    "confidence": 0.8,
                    "method": "demo",
                    "model_info": "Classificação de demonstração",
                    "suggested_response": "Agradecemos o seu feedback positivo!"
                }
            ]
            
            self._send_json_response({
                "items": demo_emails[:limit],
                "count": len(demo_emails[:limit]),
                "note": "Dados de demonstração - conexão Gmail real necessária para produção"
            })
        except Exception as e:
            self._send_error(500, f"Erro no preview do Gmail: {str(e)}")
    
    def _handle_gmail_connect(self, data):
        """Conectar Gmail do usuário"""
        try:
            credentials = data.get("credentials", {})
            if not credentials:
                self._send_error(400, "Credenciais Gmail são obrigatórias")
                return
            
            # Em produção, salvaria as credenciais no banco
            self._send_json_response({
                "status": "connected",
                "message": "Gmail conectado com sucesso (demonstração)",
                "note": "Modo demonstração - implementação de persistência necessária"
            })
        except Exception as e:
            self._send_error(500, f"Erro ao conectar Gmail: {str(e)}")
    
    def _handle_gmail_disconnect(self):
        """Desconectar Gmail do usuário"""
        try:
            # Em produção, removeria as credenciais do banco
            self._send_json_response({
                "status": "disconnected",
                "message": "Gmail desconectado com sucesso (demonstração)",
                "note": "Modo demonstração"
            })
        except Exception as e:
            self._send_error(500, f"Erro ao desconectar Gmail: {str(e)}")
    
    def _handle_gmail_send(self, data):
        """Enviar email via Gmail"""
        try:
            to_email = data.get("to")
            subject = data.get("subject", "")
            body = data.get("body", "")
            thread_id = data.get("threadId")
            
            if not to_email or not body:
                self._send_error(400, "Campos obrigatórios: to, body")
                return
            
            # Em produção, enviaria o email via Gmail API
            self._send_json_response({
                "status": "sent",
                "message": f"Email enviado para {to_email} (demonstração)",
                "details": {
                    "to": to_email,
                    "subject": subject,
                    "thread_id": thread_id
                },
                "note": "Modo demonstração - Gmail API necessária para envio real"
            })
        except Exception as e:
            self._send_error(500, f"Erro no envio do Gmail: {str(e)}")
    
    def _handle_gmail_mark_read(self, data):
        """Marcar email como lido no Gmail"""
        try:
            message_id = data.get("messageId")
            if not message_id:
                self._send_error(400, "Campo obrigatório: messageId")
                return
            
            # Em produção, marcaria como lido via Gmail API
            self._send_json_response({
                "status": "marked_as_read",
                "message": f"Email {message_id} marcado como lido (demonstração)",
                "message_id": message_id,
                "note": "Modo demonstração - Gmail API necessária para ação real"
            })
        except Exception as e:
            self._send_error(500, f"Erro ao marcar como lido: {str(e)}")
    
    def _handle_classify_file(self):
        self._send_error(501, "Classificação de arquivo não implementada ainda (requer multipart)")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
