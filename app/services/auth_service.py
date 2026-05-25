"""Service de autenticacao - gerenciamento de refresh tokens com rotacao e deteccao de roubo"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.database.models.refresh_token import RefreshToken
from app.database.models.user import User

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _persist_refresh_token(
    *,
    user_id: int,
    family_id: str,
    request: Request | None,
    session: Session,
) -> str:
    """Gera novo refresh token, persiste seu hash no banco, retorna o token em texto puro."""
    token = security.generate_refresh_token()
    token_hash = security.hash_refresh_token(token)
    expires_at = _now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    user_agent = None
    ip_address = None
    if request is not None:
        user_agent = (request.headers.get("user-agent") or "")[:255] or None
        ip_address = request.client.host if request.client else None

    db_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        family_id=family_id,
        expires_at=expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    session.add(db_token)
    session.flush()
    return token


def issue_token_pair(user: User, session: Session, request: Request | None) -> dict:
    """Gera par (access + refresh) para um novo login.
    Cria uma nova family_id."""
    family_id = str(uuid.uuid4())

    refresh_token = _persist_refresh_token(
        user_id=user.id,
        family_id=family_id,
        request=request,
        session=session,
    )

    access_token = security.create_access_token(
        {"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    session.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


def rotate_refresh_token(raw_token: str, session: Session, request: Request | None) -> dict:
    """Valida refresh token, detecta roubo e gera novo par.

    Logica de deteccao de roubo:
    - Se o token existe e esta revogado -> toda a familia e comprometida -> revoga tudo
    - Se o token nao existe -> token invalido/forjado
    - Se o token esta expirado -> 401
    """
    # Cleanup inline: remover tokens muito antigos (>30 dias apos expiracao)
    _cleanup_expired_tokens(session)

    token_hash = security.hash_refresh_token(raw_token)
    db_token: Optional[RefreshToken] = (
        session.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash)
        .with_for_update()  # lock para evitar race condition em rotacao concorrente
        .first()
    )

    if db_token is None:
        logger.warning("Tentativa de refresh com token inexistente/forjado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalido",
        )

    # Deteccao de roubo: token revogado sendo reusado
    if db_token.revoked_at is not None:
        logger.warning(
            f"REUTILIZACAO de refresh token detectada - "
            f"user_id={db_token.user_id}, family_id={db_token.family_id}. "
            "Revogando toda a familia."
        )
        _revoke_family(db_token.family_id, session)
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token comprometido. Por seguranca, todas as sessoes foram encerradas. Faca login novamente.",
        )

    expires_at = db_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < _now():
        logger.info(f"Refresh token expirado - user_id={db_token.user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expirado. Faca login novamente.",
        )

    user = session.query(User).filter(User.id == db_token.user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario invalido",
        )

    db_token.revoked_at = _now()
    session.flush()

    new_refresh = _persist_refresh_token(
        user_id=user.id,
        family_id=db_token.family_id,
        request=request,
        session=session,
    )

    new_access = security.create_access_token(
        {"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    session.commit()

    logger.info(f"Refresh token rotacionado - user_id={user.id}, family_id={db_token.family_id}")

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


def revoke_refresh_token(raw_token: str, session: Session) -> None:
    """Revoga um refresh token especifico (logout do dispositivo atual)."""
    token_hash = security.hash_refresh_token(raw_token)
    db_token = (
        session.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash)
        .first()
    )
    if db_token is None or db_token.revoked_at is not None:
        # Idempotente - nao falha se ja foi revogado
        return

    db_token.revoked_at = _now()
    session.commit()
    logger.info(f"Refresh token revogado (logout) - user_id={db_token.user_id}")


def revoke_all_user_tokens(user_id: int, session: Session) -> int:
    """Revoga TODOS os refresh tokens do usuario (logout-all).
    Retorna quantos tokens foram revogados."""
    now = _now()
    count = (
        session.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        .update({"revoked_at": now}, synchronize_session=False)
    )
    session.commit()
    logger.info(f"Logout-all: {count} sessoes revogadas - user_id={user_id}")
    return count


def _revoke_family(family_id: str, session: Session) -> None:
    """Revoga todos os tokens de uma familia (usado em deteccao de roubo)."""
    now = _now()
    session.query(RefreshToken).filter(
        RefreshToken.family_id == family_id,
        RefreshToken.revoked_at.is_(None),
    ).update({"revoked_at": now}, synchronize_session=False)


def _cleanup_expired_tokens(session: Session) -> None:
    """Remove tokens cujo expires_at ja passou ha mais de 1 dia.
    Mantem tokens recem-expirados por 1 dia para fins de auditoria/debug."""
    cutoff = _now() - timedelta(days=1)
    deleted = (
        session.query(RefreshToken)
        .filter(RefreshToken.expires_at < cutoff)
        .delete(synchronize_session=False)
    )
    if deleted > 0:
        logger.debug(f"Cleanup: {deleted} refresh tokens expirados removidos")

def revoke_refresh_token_by_id(token_id: int, user_id: int, session: Session) -> None:
    """Revoga um refresh token especifico por ID, verificando ownership."""
    token = session.query(RefreshToken).filter(
        RefreshToken.id == token_id,
        RefreshToken.user_id == user_id,
    ).first()
    if token:
        token.revoked_at = _now()
        session.commit()