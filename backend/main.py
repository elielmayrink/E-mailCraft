from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from datetime import datetime
from dotenv import load_dotenv
from models.classifier import EmailClassifier
from models.response_generator import ResponseGenerator
from utils.text_processor import TextProcessor
from integrations.gmail_service import GmailService
from database import get_db, create_tables
from auth.firebase_auth import get_current_user, verify_firebase_token
from models.user import User

# Carregar variáveis de ambiente do arquivo config.env
load_dotenv('config.env')

app = FastAPI(title="Email Classification API", version="1.0.0", root_path="/api")

# CORS middleware para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir frontend estático em /frontend
frontend_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.isdir(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")

# Inicializar banco de dados (tolerante a falhas em ambiente serverless)
try:
    create_tables()
except Exception as e:
    # Evitar derrubar a função em produção; logs aparecem nos logs do provedor
    print(f"[init] Aviso: falha ao criar tabelas: {e}")

# Inicializar componentes (será feito nas funções)
classifier = None
response_generator = None
text_processor = None
gmail_service = None

def get_components():
    """Inicializa os componentes se necessário"""
    global classifier, response_generator, text_processor, gmail_service
    if classifier is None:
        classifier = EmailClassifier()
    if response_generator is None:
        response_generator = ResponseGenerator()
        # Configurar cliente Gemini no classificador se disponível
        if hasattr(response_generator, 'gemini_client') and response_generator.gemini_client:
            classifier.set_gemini_client(response_generator.gemini_client)
    if text_processor is None:
        text_processor = TextProcessor()
    if gmail_service is None:
        gmail_service = GmailService()
    # Garantir sincronização do cliente Gemini mesmo em chamadas subsequentes
    if hasattr(response_generator, 'gemini_client') and response_generator.gemini_client:
        classifier.set_gemini_client(response_generator.gemini_client)
    return classifier, response_generator, text_processor

@app.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obter informações do usuário atual"""
    return {
        "user": current_user.to_dict(),
        "status": "authenticated"
    }

@app.post("/auth/verify-token")
async def verify_token(
    token_data: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
):
    """Verificar token Firebase e criar/atualizar usuário no banco"""
    try:
        from auth.firebase_auth import get_user_by_firebase_uid, create_user_from_firebase_token
        
        # Buscar usuário existente
        user = get_user_by_firebase_uid(token_data.get("uid"), db)
        
        if not user:
            # Criar novo usuário
            user = create_user_from_firebase_token(token_data, db)
        else:
            # Atualizar último login
            user.last_login = datetime.utcnow()
            db.commit()
            db.refresh(user)
        
        return {
            "valid": True,
            "user": {
                "uid": token_data.get("uid"),
                "email": token_data.get("email"),
                "name": token_data.get("name"),
                "picture": token_data.get("picture")
            },
            "db_user": user.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar usuário: {str(e)}")

@app.post("/gmail/connect")
async def connect_gmail(
    credentials: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Conectar Gmail do usuário"""
    try:
        from auth.firebase_auth import update_user_gmail_credentials
        update_user_gmail_credentials(current_user, credentials, db)
        return {
            "status": "connected",
            "message": "Gmail conectado com sucesso"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao conectar Gmail: {str(e)}")

@app.post("/gmail/disconnect")
async def disconnect_gmail(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Desconectar Gmail do usuário"""
    try:
        from auth.firebase_auth import disconnect_user_gmail
        disconnect_user_gmail(current_user, db)
        return {
            "status": "disconnected",
            "message": "Gmail desconectado com sucesso"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao desconectar Gmail: {str(e)}")

@app.get("/gmail/status")
async def gmail_status(current_user: User = Depends(get_current_user)):
    """Verificar status da conexão Gmail"""
    return {
        "connected": current_user.gmail_connected,
        "last_sync": current_user.gmail_last_sync.isoformat() if current_user.gmail_last_sync else None
    }

@app.get("/gmail/auth-url")
async def gmail_auth_url(current_user: User = Depends(get_current_user)):
    """Obter URL de autorização do Gmail"""
    try:
        from google_auth_oauthlib.flow import Flow
        
        # Configuração OAuth2 para Gmail
        client_config = {
            "web": {
                "client_id": os.getenv("GMAIL_CLIENT_ID"),
                "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
                "project_id": os.getenv("GMAIL_PROJECT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [os.getenv("GMAIL_REDIRECT_URI", "http://localhost:8002/gmail/oauth2callback")]
            }
        }
        
        SCOPES = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.modify",
        ]
        
        flow = Flow.from_client_config(client_config, SCOPES)
        flow.redirect_uri = os.getenv("GMAIL_REDIRECT_URI", "http://localhost:8002/gmail/oauth2callback")
        
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
            state=current_user.firebase_uid  # Usar Firebase UID como state
        )
        
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar URL de autorização: {str(e)}")

@app.get("/gmail/oauth2callback")
async def gmail_oauth2_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """Callback do OAuth2 do Gmail"""
    try:
        if error:
            raise HTTPException(status_code=400, detail=f"Erro na autorização: {error}")
        
        if not code or not state:
            raise HTTPException(status_code=400, detail="Código de autorização ou state não fornecidos")
        
        # Buscar usuário pelo Firebase UID (state)
        from auth.firebase_auth import get_user_by_firebase_uid
        user = get_user_by_firebase_uid(state, db)
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Configuração OAuth2 para Gmail
        client_config = {
            "web": {
                "client_id": os.getenv("GMAIL_CLIENT_ID"),
                "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
                "project_id": os.getenv("GMAIL_PROJECT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "redirect_uris": [os.getenv("GMAIL_REDIRECT_URI", "http://localhost:8002/gmail/oauth2callback")]
            }
        }
        
        SCOPES = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.modify",
        ]
        
        from google_auth_oauthlib.flow import Flow
        flow = Flow.from_client_config(client_config, SCOPES)
        flow.redirect_uri = os.getenv("GMAIL_REDIRECT_URI", "http://localhost:8002/gmail/oauth2callback")
        
        # Trocar código por tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Converter credenciais para formato armazenável
        gmail_credentials = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
            "type": "authorized_user"
        }
        
        # Atualizar usuário no banco de dados
        from auth.firebase_auth import update_user_gmail_credentials
        update_user_gmail_credentials(user, gmail_credentials, db)
        
        # Retornar página HTML que redireciona automaticamente
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gmail Conectado</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    text-align: center;
                    padding: 50px;
                    background-color: #f5f5f5;
                }}
                .success {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                }}
                .loading {{
                    font-size: 18px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="success">
                <h2>✅ Gmail Conectado com Sucesso!</h2>
                <p>Suas credenciais foram salvas e você já pode usar o sistema.</p>
            </div>
            <div class="loading">
                <p>Redirecionando para a aplicação...</p>
                <p>Se não for redirecionado automaticamente, <a href="http://localhost:8001/">clique aqui</a></p>
            </div>
            <script>
                setTimeout(function() {{
                    window.location.href = "http://localhost:8001/";
                }}, 3000);
            </script>
        </body>
        </html>
        """)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no callback OAuth2: {str(e)}")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Página inicial com interface simples"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Classification System</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #0056b3; }
            .result { margin-top: 20px; padding: 15px; border-radius: 4px; }
            .productive { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .unproductive { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
        </style>
    </head>
    <body>
        <h1>📧 Sistema de Classificação de Emails</h1>
        <div class="container">
            <form id="emailForm">
                <div class="form-group">
                    <label for="emailText">Texto do Email:</label>
                    <textarea id="emailText" rows="10" placeholder="Cole aqui o conteúdo do email..."></textarea>
                </div>
                <div class="form-group">
                    <label for="emailFile">Ou faça upload de um arquivo (.txt ou .pdf):</label>
                    <input type="file" id="emailFile" accept=".txt,.pdf">
                </div>
                <button type="submit">Classificar Email</button>
            </form>
            <div id="result" class="result" style="display: none;"></div>
        </div>
        
        <script>
            document.getElementById('emailForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const resultDiv = document.getElementById('result');
                const emailText = document.getElementById('emailText').value;
                const emailFile = document.getElementById('emailFile').files[0];
                
                if (!emailText && !emailFile) {
                    alert('Por favor, insira o texto do email ou faça upload de um arquivo.');
                    return;
                }
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = 'Processando...';
                
                try {
                    let response;
                    if (emailFile) {
                        const formData = new FormData();
                        formData.append('file', emailFile);
                        response = await fetch('/classify-file', {
                            method: 'POST',
                            body: formData
                        });
                    } else {
                        response = await fetch('/classify-text', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ text: emailText })
                        });
                    }
                    
                    const data = await response.json();
                    
                    if (data.category === 'Produtivo') {
                        resultDiv.className = 'result productive';
                    } else {
                        resultDiv.className = 'result unproductive';
                    }
                    
                    resultDiv.innerHTML = `
                        <h3>Categoria: ${data.category}</h3>
                        <p><strong>Resposta Sugerida:</strong></p>
                        <p>${data.response}</p>
                    `;
                } catch (error) {
                    resultDiv.className = 'result';
                    resultDiv.innerHTML = 'Erro ao processar o email. Tente novamente.';
                }
            });
        </script>
    </body>
    </html>
    """

@app.post("/classify-text")
async def classify_text(data: dict):
    """Classifica email a partir de texto"""
    try:
        text = data.get("text", "")
        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Texto do email é obrigatório")
        
        # Obter componentes
        classifier, response_generator, text_processor = get_components()
        
        # Processar texto
        processed_text = text_processor.process(text)
        
        # Classificar
        classification_result = classifier.predict(processed_text)
        category = classification_result["category"]
        
        # Gerar resposta
        response = response_generator.generate(category, processed_text)
        
        return {
            "category": category,
            "response": response,
            "confidence": classification_result["confidence"],
            "method": classification_result["method"],
            "model_info": classification_result["model_info"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar email: {str(e)}")

@app.post("/classify-file")
async def classify_file(file: UploadFile = File(...)):
    """Classifica email a partir de arquivo"""
    try:
        # Verificar tipo de arquivo
        if not file.filename.endswith(('.txt', '.pdf')):
            raise HTTPException(status_code=400, detail="Apenas arquivos .txt e .pdf são suportados")
        
        # Obter componentes
        classifier, response_generator, text_processor = get_components()
        
        # Ler conteúdo do arquivo
        content = await file.read()
        
        # Processar arquivo
        text = text_processor.process_file(content, file.filename)
        
        # Classificar
        classification_result = classifier.predict(text)
        category = classification_result["category"]
        
        # Gerar resposta
        response = response_generator.generate(category, text)
        
        return {
            "category": category,
            "response": response,
            "confidence": classification_result["confidence"],
            "method": classification_result["method"],
            "model_info": classification_result["model_info"],
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")



@app.post("/test-ai")
async def test_ai(data: dict):
    """Teste simples da IA (Gemini API)"""
    try:
        from google import genai
        
        # Obter API key
        api_key = os.getenv("google_studio_key")
        if not api_key:
            return {"error": "API key não configurada"}
        
        # Criar cliente Gemini
        client = genai.Client(api_key=api_key)
        
        # Fazer uma pergunta simples
        question = data.get("question", "Diga apenas 'Olá, IA funcionando!' em português")
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=question
        )
        
        result = response.text
        
        return {
            "status": "success",
            "question": question,
            "answer": result,
            "model": "gemini-2.5-flash"
        }
        
    except Exception as e:
        return {"error": f"Erro: {str(e)}"}

@app.post("/configure-ai")
async def configure_ai(data: dict):
    """Configura API key da IA (Gemini)"""
    try:
        # Garantir que os componentes estejam inicializados
        global classifier, response_generator
        classifier, response_generator, _ = get_components()
        api_key = data.get("api_key", "")
        if not api_key:
            raise HTTPException(status_code=400, detail="API key é obrigatória")
        
        success = response_generator.set_gemini_key(api_key)
        if success:
            # Propagar imediatamente para o classificador
            if hasattr(response_generator, 'gemini_client') and response_generator.gemini_client:
                classifier.set_gemini_client(response_generator.gemini_client)
            return {"status": "success", "message": "IA configurada com sucesso!"}
        else:
            raise HTTPException(status_code=500, detail="Erro ao configurar IA")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    try:
        # Verificar acesso básico ao banco
        _ = next(get_db())
        return {"status": "healthy", "message": "API funcionando corretamente"}
    except Exception as e:
        # Retornar 500 com detalhe mínimo para ajudar debug em prod
        raise HTTPException(status_code=500, detail=f"Health check falhou: {str(e)}")


@app.get("/gmail/preview")
async def gmail_preview(
    limit: int = 5,
    current_user: User = Depends(get_current_user)
):
    try:
        # Verificar se o usuário tem Gmail conectado
        if not current_user.gmail_connected or not current_user.gmail_credentials:
            raise HTTPException(status_code=400, detail="Gmail não conectado. Conecte sua conta Gmail primeiro.")
        
        # Criar serviço Gmail com credenciais do usuário
        gmail_service = GmailService(user_credentials=current_user.gmail_credentials)
        
        if not gmail_service.ensure_authenticated():
            raise HTTPException(status_code=400, detail="Falha na autenticação Gmail. Reconecte sua conta Gmail.")

        classifier, response_generator, text_processor = get_components()
        
        try:
            messages = gmail_service.list_unread_messages(max_results=limit)
        except Exception as e:
            # Se for erro de credenciais inválidas, retornar erro específico
            if "invalid_grant" in str(e):
                raise HTTPException(
                    status_code=400, 
                    detail="Credenciais do Gmail inválidas. Conecte sua conta Gmail novamente."
                )
            raise e
        previews = []
        for m in messages:
            full = gmail_service.get_message_full(m["id"])
            if not full:
                continue
            fields = gmail_service.extract_email_fields(full)
            processed = text_processor.process(fields["text"]) if fields["text"] else ""
            cls = classifier.predict(processed)
            reply = response_generator.generate(cls["category"], processed)
            previews.append({
                "id": fields["id"],
                "threadId": fields["threadId"],
                "from": fields["from"],
                "subject": fields["subject"],
                "snippet": processed[:280],
                "category": cls["category"],
                "confidence": cls["confidence"],
                "method": cls["method"],
                "model_info": cls["model_info"],
                "suggested_response": reply,
            })
        return {"items": previews, "count": len(previews)}
    except HTTPException:
        raise
    except Exception as e:
        msg = str(e)
        if msg.startswith("OAUTH_LINK::"):
            return {"auth_url": msg.replace("OAUTH_LINK::", "", 1)}
        raise HTTPException(status_code=500, detail=f"Erro no preview do Gmail: {msg}")


@app.post("/gmail/send")
async def gmail_send(
    data: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        # Verificar se o usuário tem Gmail conectado
        if not current_user.gmail_connected or not current_user.gmail_credentials:
            raise HTTPException(status_code=400, detail="Gmail não conectado. Conecte sua conta Gmail primeiro.")
        
        # Criar serviço Gmail com credenciais do usuário
        gmail_service = GmailService(user_credentials=current_user.gmail_credentials)
        if not gmail_service.ensure_authenticated():
            raise HTTPException(status_code=400, detail="Falha na autenticação Gmail. Reconecte sua conta Gmail.")

        to_email = data.get("to")
        subject = data.get("subject", "")
        body = data.get("body", "")
        thread_id = data.get("threadId")
        if not to_email or not body:
            raise HTTPException(status_code=400, detail="Campos obrigatórios: to, body")

        ok = gmail_service.send_reply(to_email=to_email, subject=subject, body=body, thread_id=thread_id)
        if ok:
            return {"status": "sent"}
        else:
            raise HTTPException(status_code=500, detail="Falha ao enviar email")
    except HTTPException:
        raise
    except Exception as e:
        msg = str(e)
        if msg.startswith("OAUTH_LINK::"):
            return {"auth_url": msg.replace("OAUTH_LINK::", "", 1)}
        raise HTTPException(status_code=500, detail=f"Erro no envio do Gmail: {msg}")

@app.post("/gmail/mark-read")
async def gmail_mark_read(
    data: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        # Verificar se o usuário tem Gmail conectado
        if not current_user.gmail_connected or not current_user.gmail_credentials:
            raise HTTPException(status_code=400, detail="Gmail não conectado. Conecte sua conta Gmail primeiro.")
        
        # Criar serviço Gmail com credenciais do usuário
        gmail_service = GmailService(user_credentials=current_user.gmail_credentials)
        if not gmail_service.ensure_authenticated():
            raise HTTPException(status_code=400, detail="Falha na autenticação Gmail. Reconecte sua conta Gmail.")

        message_id = data.get("messageId")
        if not message_id:
            raise HTTPException(status_code=400, detail="Campo obrigatório: messageId")

        ok = gmail_service.mark_as_read(message_id)
        if ok:
            return {"status": "marked_as_read"}
        else:
            raise HTTPException(status_code=500, detail="Falha ao marcar como lido")
    except HTTPException:
        raise
    except Exception as e:
        msg = str(e)
        if msg.startswith("OAUTH_LINK::"):
            return {"auth_url": msg.replace("OAUTH_LINK::", "", 1)}
        raise HTTPException(status_code=500, detail=f"Erro ao marcar como lido: {msg}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
