# app/core/security.py

import hashlib
import secrets
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash pré-computado para garantir que bcrypt execute mesmo quando o email não existe (anti-timing-attack)
DUMMY_HASH = pwd_context.hash("dummy-password-for-timing-protection-do-not-use")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_refresh_token() -> str:
    """Gera token opaco de 64 chars (~256 bits de entropia).
    Não é JWT — apenas string aleatória que será armazenada (hash) no banco."""
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    """SHA-256 hex do refresh token — usado para lookup e armazenamento no banco.
    Não usamos bcrypt aqui pois precisamos de lookup determinístico (mesmo token → mesmo hash)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

