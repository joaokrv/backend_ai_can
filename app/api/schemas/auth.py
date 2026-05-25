# app/api/schemas/auth.py
"""Schemas para endpoints de autenticação (refresh, logout)"""

from pydantic import BaseModel, Field, field_validator


class RefreshRequest(BaseModel):
    """Payload de POST /auth/refresh"""
    refresh_token: str = Field(..., min_length=32, max_length=128)


class LogoutRequest(BaseModel):
    """Payload de POST /auth/logout"""
    refresh_token: str = Field(..., min_length=32, max_length=128)


class LogoutAllResponse(BaseModel):
    """Resposta de POST /auth/logout-all"""
    revoked_sessions: int
    message: str = "Todas as sessões foram encerradas"


class SessionInfo(BaseModel):
    """Informação de uma sessão ativa (refresh token)"""
    id: int
    user_agent: str | None
    ip_address: str | None
    created_at: str  # ISO 8601
    expires_at: str  # ISO 8601
    is_current: bool = False  # marcado True se for o token usado na request atual


class ChangePasswordRequest(BaseModel):
    """Payload de POST /auth/change-password"""
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=10, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password_strength(cls, v: str) -> str:
        from app.core.password_policy import validate_password
        return validate_password(v)


class DeleteAccountRequest(BaseModel):
    """Payload de DELETE /auth/me"""
    password: str = Field(..., min_length=1, max_length=128)
