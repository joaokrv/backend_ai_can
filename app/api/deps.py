from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core import security
from app.database.models.user import User
from app.database.base import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login" if hasattr(settings, "API_V1_STR") else "/api/v1/auth/login"
)


def rate_limit_key_ip_user(request: Request, user_id: int | None = None) -> str:
    """
    Gera chave de rate limit que combina IP + user_id (quando autenticado).
    Para endpoints públicos, usa apenas IP.
    Para endpoints autenticados, combina IP + user_id para limitar por usuário.

    Exemplos:
    - GET /login (público): "192.168.1.1"
    - POST /sugestao (autenticado): "192.168.1.1:42"

    Args:
        request: FastAPI Request object
        user_id: ID do usuário autenticado (None para endpoints públicos)

    Returns:
        Chave de rate limiting (string)
    """
    ip = get_remote_address(request)
    if user_id is not None:
        return f"{ip}:{user_id}"
    return ip


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


TokenDep = Annotated[str, Depends(reusable_oauth2)]
SessionDep = Annotated[Session, Depends(get_db)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = payload.get("sub")
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.query(User).filter(User.email == token_data).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
