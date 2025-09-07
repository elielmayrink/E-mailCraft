import os
import base64
import logging
from typing import List, Dict, Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow


logger = logging.getLogger(__name__)


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


class GmailService:
    """Wrapper simples para operações essenciais do Gmail no MVP."""

    def __init__(self, credentials_dir: str = None):
        # Resolve diretório de credenciais de forma independente do CWD
        # 1) Variável de ambiente GMAIL_CREDENTIALS_DIR (opcional)
        # 2) backend/credentials relativo a este arquivo
        # 3) credentials (quando rodando a partir de backend/)
        if credentials_dir:
            self.credentials_dir = credentials_dir
        else:
            env_dir = os.getenv("GMAIL_CREDENTIALS_DIR")
            if env_dir:
                self.credentials_dir = env_dir
            else:
                base_backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
                candidate1 = os.path.join(base_backend_dir, "credentials")  # backend/credentials
                candidate2 = os.path.join(os.getcwd(), "credentials")      # credentials (cwd=backend)
                self.credentials_dir = candidate1 if os.path.isdir(candidate1) else candidate2
        os.makedirs(self.credentials_dir, exist_ok=True)
        self.token_path = os.path.join(self.credentials_dir, "token.json")
        self.service = None
        
        # Gmail OAuth credentials from environment variables
        self.client_id = os.getenv("GMAIL_CLIENT_ID")
        self.client_secret = os.getenv("GMAIL_CLIENT_SECRET")
        self.project_id = os.getenv("GMAIL_PROJECT_ID")
        self.redirect_uri = os.getenv("GMAIL_REDIRECT_URI", "http://localhost")

    def ensure_authenticated(self) -> bool:
        try:
            creds = None
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    from google.auth.transport.requests import Request
                    creds.refresh(Request())
                else:
                    # Check if we have environment variables for OAuth
                    if not all([self.client_id, self.client_secret]):
                        raise FileNotFoundError(
                            "Credenciais Gmail não encontradas. Configure GMAIL_CLIENT_ID e GMAIL_CLIENT_SECRET no arquivo .env"
                        )
                    
                    # Create OAuth flow from environment variables
                    client_config = {
                        "installed": {
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "project_id": self.project_id,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "redirect_uris": [self.redirect_uri]
                        }
                    }
                    
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                    # Tentar servidor local sem abrir navegador; se falhar, retornar URL de autorização
                    try:
                        creds = flow.run_local_server(open_browser=False, port=0)
                    except Exception:
                        auth_url, _ = flow.authorization_url(
                            access_type="offline",
                            include_granted_scopes="true",
                            prompt="consent",
                        )
                        # Prefixo especial para o endpoint capturar e retornar ao cliente
                        raise RuntimeError(f"OAUTH_LINK::{auth_url}")

                with open(self.token_path, "w") as token:
                    token.write(creds.to_json())

            self.service = build("gmail", "v1", credentials=creds)
            return True
        except Exception as e:
            logger.error(f"Falha na autenticação Gmail: {e}")
            return False

    def list_unread_messages(self, max_results: int = 5) -> List[Dict]:
        if not self.service:
            raise RuntimeError("Serviço Gmail não autenticado")
        try:
            response = (
                self.service.users()
                .messages()
                .list(userId="me", q="is:unread", maxResults=max_results)
                .execute()
            )
            return response.get("messages", [])
        except HttpError as e:
            logger.error(f"Erro ao listar mensagens: {e}")
            return []

    def get_message_full(self, message_id: str) -> Optional[Dict]:
        if not self.service:
            raise RuntimeError("Serviço Gmail não autenticado")
        try:
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )
            return msg
        except HttpError as e:
            logger.error(f"Erro ao obter mensagem {message_id}: {e}")
            return None

    @staticmethod
    def _extract_payload_text(payload: Dict) -> str:
        # Prefere text/plain; fallback para text/html (sem sanitização pesada neste MVP)
        def decode_part(body_data: str) -> str:
            try:
                return base64.urlsafe_b64decode(body_data.encode("UTF-8")).decode(
                    "utf-8", errors="ignore"
                )
            except Exception:
                return ""

        mime_type = payload.get("mimeType", "")
        body = payload.get("body", {})
        data = body.get("data")

        if mime_type == "text/plain" and data:
            return decode_part(data)

        if mime_type == "multipart/alternative" or mime_type.startswith("multipart"):
            parts = payload.get("parts", [])
            plain = ""
            html = ""
            for p in parts:
                p_type = p.get("mimeType", "")
                p_body = p.get("body", {}).get("data")
                if p_type == "text/plain" and p_body:
                    plain = decode_part(p_body)
                elif p_type == "text/html" and p_body:
                    html = decode_part(p_body)
            return plain or html

        if mime_type == "text/html" and data:
            return decode_part(data)

        return ""

    def extract_email_fields(self, message: Dict) -> Dict:
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        subject = ""
        from_addr = ""
        for h in headers:
            name = h.get("name", "").lower()
            if name == "subject":
                subject = h.get("value", "")
            if name == "from":
                from_addr = h.get("value", "")
        text = self._extract_payload_text(payload)
        return {
            "id": message.get("id"),
            "threadId": message.get("threadId"),
            "subject": subject,
            "from": from_addr,
            "text": text,
        }

    def send_reply(self, to_email: str, subject: str, body: str, thread_id: Optional[str] = None) -> bool:
        if not self.service:
            raise RuntimeError("Serviço Gmail não autenticado")
        try:
            from email.mime.text import MIMEText

            message = MIMEText(body)
            message["to"] = to_email
            message["subject"] = f"Re: {subject}" if not subject.lower().startswith("re:") else subject

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_kwargs = {"userId": "me", "body": {"raw": raw_message}}
            if thread_id:
                create_kwargs["body"]["threadId"] = thread_id

            sent = self.service.users().messages().send(**create_kwargs).execute()
            logger.info(f"Mensagem enviada: {sent.get('id')}")
            return True
        except HttpError as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False

    def mark_as_read(self, message_id: str) -> bool:
        """Marca mensagem como lida (remove label UNREAD)"""
        if not self.service:
            raise RuntimeError("Serviço Gmail não autenticado")
        try:
            logger.info(f"Tentando marcar mensagem {message_id} como lida...")
            # Remove o label UNREAD da mensagem
            result = self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]}
            ).execute()
            logger.info(f"Mensagem {message_id} marcada como lida. Resultado: {result}")
            return True
        except HttpError as e:
            logger.error(f"Erro ao marcar mensagem como lida: {e}")
            logger.error(f"Detalhes do erro: {e.error_details}")
            return False


