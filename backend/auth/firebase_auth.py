"""
Serviço de autenticação Firebase
"""
import os
import json
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from datetime import datetime

# Inicializar Firebase Admin
def initialize_firebase() -> bool:
    """
    Inicializar Firebase Admin SDK
    """
    try:
        if firebase_admin._apps:
            return True
        # Configurações do Firebase a partir das variáveis de ambiente
        required_envs = [
            "FIREBASE_PROJECT_ID",
            "FIREBASE_PRIVATE_KEY_ID",
            "FIREBASE_PRIVATE_KEY",
            "FIREBASE_CLIENT_EMAIL",
            "FIREBASE_CLIENT_ID",
            "FIREBASE_TOKEN_URI",
        ]
        if not all(os.getenv(k) for k in required_envs):
            # Sem config: não inicializa em serverless por padrão
            return False
        firebase_config = {
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL", ""),
        }
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        return True
    except Exception:
        return False

# Não inicializa na importação para evitar crash em serverless sem envs

# Security scheme
security = HTTPBearer()

async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verificar token do Firebase e retornar dados do usuário
    """
    try:
        # Inicialização preguiçosa
        if not firebase_admin._apps:
            ok = initialize_firebase()
            if not ok:
                raise HTTPException(status_code=503, detail="Firebase não configurado")
        # Verificar token do Firebase
        decoded_token = firebase_auth.verify_id_token(credentials.credentials)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

async def get_current_user(
    token_data: dict = Depends(verify_firebase_token),
    db: Session = Depends(get_db)
) -> User:
    """
    Obter usuário atual a partir do token Firebase
    """
    firebase_uid = token_data.get("uid")
    if not firebase_uid:
        raise HTTPException(status_code=401, detail="UID não encontrado no token")
    
    # Buscar usuário no banco
    user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
    
    if not user:
        # Criar novo usuário se não existir
        user = create_user_from_firebase_token(token_data, db)
    
    # Atualizar último login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user

def create_user_from_firebase_token(token_data: dict, db: Session) -> User:
    """
    Criar novo usuário a partir dos dados do token Firebase
    """
    user = User(
        firebase_uid=token_data.get("uid"),
        email=token_data.get("email"),
        name=token_data.get("name"),
        photo_url=token_data.get("picture"),
        last_login=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

def get_user_by_firebase_uid(firebase_uid: str, db: Session) -> User:
    """
    Buscar usuário por Firebase UID
    """
    return db.query(User).filter(User.firebase_uid == firebase_uid).first()

def update_user_gmail_credentials(user: User, credentials: dict, db: Session):
    """
    Atualizar credenciais do Gmail do usuário
    """
    user.gmail_credentials = credentials
    user.gmail_connected = True
    user.gmail_last_sync = datetime.utcnow()
    db.commit()
    return user

def disconnect_user_gmail(user: User, db: Session):
    """
    Desconectar Gmail do usuário
    """
    user.gmail_credentials = None
    user.gmail_connected = False
    user.gmail_last_sync = None
    db.commit()
    return user
