# app/database/models/refresh_token.py
"""Modelo de Refresh Token — armazena tokens hasheados com tracking de família para detecção de roubo"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.database.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("aican.usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # SHA-256 hex do token (nunca armazenar o token em texto puro)
    token_hash = Column(String(64), nullable=False, unique=True, index=True)

    # UUID que agrupa tokens da mesma "família" (cadeia de rotação)
    # Detecta roubo: se um token antigo da família reaparece, toda a família é revogada
    family_id = Column(String(36), nullable=False, index=True)

    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Metadata forense (útil para /auth/sessions)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)  # 45 chars = IPv6 max
