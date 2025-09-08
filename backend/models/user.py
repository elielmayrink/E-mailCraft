from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func

try:
    from database import Base
except ImportError:
    from backend.database import Base

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=True)
    photo_url = Column(String(500), nullable=True)
    # Gmail
    gmail_credentials = Column(JSON, nullable=True)  # Credenciais do Gmail
    gmail_connected = Column(Boolean, default=False)
    gmail_last_sync = Column(DateTime, nullable=True)
    
    # Preferências do usuário
    preferences = Column(JSON, nullable=True)  # Preferências do usuário
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', firebase_uid='{self.firebase_uid}')>"

    def to_dict(self):
        """
        Converter usuário para dicionário
        """
        return {
            "id": self.id,
            "firebase_uid": self.firebase_uid,
            "email": self.email,
            "name": self.name,
            "photo_url": self.photo_url,
            "gmail_connected": self.gmail_connected,
            "gmail_last_sync": self.gmail_last_sync.isoformat() if self.gmail_last_sync else None,
            "preferences": self.preferences,
            "is_active": self.is_active,
            "is_premium": self.is_premium,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
