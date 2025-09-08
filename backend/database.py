"""
Configuração do banco de dados com SQLAlchemy
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# URL do banco de dados
# Em ambientes serverless (Vercel), o filesystem é read-only, exceto /tmp
# Portanto, use /tmp por padrão para SQLite quando nenhuma URL é fornecida
default_sqlite_path = "sqlite:////tmp/email_agent.db"
DATABASE_URL = os.getenv("DATABASE_URL", default_sqlite_path)

# Se estiver usando SQLite com caminho relativo, redirecionar para /tmp
if DATABASE_URL.startswith("sqlite") and ("///./" in DATABASE_URL or DATABASE_URL.endswith("email_agent.db")):
    DATABASE_URL = default_sqlite_path

# Criar engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

def get_db():
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Criar todas as tabelas
    """
    Base.metadata.create_all(bind=engine)
