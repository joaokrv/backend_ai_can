from typing import Any, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.core.limiter import limiter

from app.core import security
from app.core.config import settings
from app.database.models.user import User
from app.api import deps
from app.api.schemas.user import UserCreate, UserResponse, Token, UserUpdate
from app.api.schemas.auth import RefreshRequest, LogoutRequest, LogoutAllResponse, SessionInfo, ChangePasswordRequest, DeleteAccountRequest
from app.database.models.refresh_token import RefreshToken
from app.services import auth_service

import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/login", response_model=Token)
@limiter.limit("5/minute;20/hour")
def login_access_token(
    request: Request,
    session: deps.SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """Login com email/senha. Retorna par (access_token + refresh_token)."""
    user = session.query(User).filter(User.email == form_data.username).first()

    # Timing-safe: sempre executar verify_password para equalizar tempo de resposta
    hash_to_check = user.hash_senha if user else security.DUMMY_HASH
    password_ok = security.verify_password(form_data.password, hash_to_check)

    if not user or not password_ok or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    return auth_service.issue_token_pair(user=user, session=session, request=request)


@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")
def refresh_access_token(
    request: Request,
    payload: RefreshRequest,
    session: deps.SessionDep,
) -> Any:
    """Rotaciona o refresh token: invalida o anterior e emite um novo par."""
    return auth_service.rotate_refresh_token(
        raw_token=payload.refresh_token,
        session=session,
        request=request,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/hour")
def logout(
    request: Request,
    payload: LogoutRequest,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    """Revoga o refresh token do dispositivo atual."""
    auth_service.revoke_refresh_token(raw_token=payload.refresh_token, session=session)


@router.post("/logout-all", response_model=LogoutAllResponse)
@limiter.limit("5/hour")
def logout_all(
    request: Request,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
) -> Any:
    """Revoga TODAS as sessoes do usuario (todos os dispositivos)."""
    count = auth_service.revoke_all_user_tokens(user_id=current_user.id, session=session)
    return LogoutAllResponse(revoked_sessions=count)


@router.post("/register", response_model=UserResponse)
@limiter.limit("3/hour")
def register_user(
    request: Request,
    *,
    session: deps.SessionDep,
    user_in: UserCreate,
) -> Any:
    user = session.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O usuario com esse email ja existe no sistema",
        )

    user = User(
        email=user_in.email,
        hash_senha=security.get_password_hash(user_in.password),
        nome=user_in.nome,
        idade=user_in.idade,
        altura=user_in.altura,
        peso=user_in.peso,
        local_treino=user_in.local_treino,
        objetivo=user_in.objetivo,
        is_active=True,
        aceite_termos_at=datetime.now(timezone.utc),
        aceite_termos_versao=settings.TERMS_VERSION,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
@limiter.limit("60/minute")
def read_users_me(request: Request, current_user: deps.CurrentUser) -> Any:
    return current_user


@router.get("/sessions", response_model=List[SessionInfo])
@limiter.limit("30/minute")
def list_sessions(
    request: Request,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
) -> Any:
    """Lista todas as sessoes ativas do usuario (refresh tokens nao revogados e nao expirados)."""
    now = datetime.now(timezone.utc)
    tokens = (
        session.query(RefreshToken)
        .filter(
            RefreshToken.user_id == current_user.id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        )
        .order_by(RefreshToken.created_at.desc())
        .all()
    )

    return [
        SessionInfo(
            id=t.id,
            user_agent=t.user_agent,
            ip_address=t.ip_address,
            created_at=t.created_at.isoformat() if t.created_at else "",
            expires_at=t.expires_at.isoformat() if t.expires_at else "",
        )
        for t in tokens
    ]


@router.delete("/sessions/{token_id}", status_code=204)
@limiter.limit("20/minute")
def revoke_session(
    request: Request,
    token_id: int,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
) -> None:
    """Revoga uma sessao especifica pelo ID do refresh token."""
    token = session.query(RefreshToken).filter(
        RefreshToken.id == token_id,
        RefreshToken.user_id == current_user.id,
        RefreshToken.revoked_at.is_(None),
    ).first()
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sessao nao encontrada")
    auth_service.revoke_refresh_token_by_id(token_id=token_id, user_id=current_user.id, session=session)
    logger.info(f"Sessao revogada: token_id={token_id}, user_id={current_user.id}")

_REQUIRED_ONBOARDING = [
    "sexo", "idade", "altura", "peso", "objetivo",
    "local_treino", "dias_disponiveis", "duracao_sessao", "nivel_experiencia",
]


@router.put("/me", response_model=UserResponse)
@limiter.limit("10/minute")
def update_me(
    request: Request,
    *,
    user_in: UserUpdate,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
) -> Any:
    """Atualiza perfil do usuario. Apenas campos enviados (nao-None) sao alterados."""
    update_data = user_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.onboarding_completo = all(
        getattr(current_user, f) not in (None, [])
        for f in _REQUIRED_ONBOARDING
    )

    session.commit()
    session.refresh(current_user)
    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/hour")
def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
) -> None:
    """Troca a senha do usuario e revoga todas as sessoes abertas."""
    if not security.verify_password(payload.current_password, current_user.hash_senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )

    if security.verify_password(payload.new_password, current_user.hash_senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A nova senha deve ser diferente da atual",
        )

    current_user.hash_senha = security.get_password_hash(payload.new_password)
    session.commit()

    auth_service.revoke_all_user_tokens(user_id=current_user.id, session=session)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("3/hour")
def delete_me(
    request: Request,
    payload: DeleteAccountRequest,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
) -> None:
    """Exclui permanentemente a conta do usuario (hard delete com CASCADE)."""
    if not security.verify_password(payload.password, current_user.hash_senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta",
        )

    user_id = current_user.id
    auth_service.revoke_all_user_tokens(user_id=user_id, session=session)
    session.delete(current_user)
    session.commit()

    logger.info(f"Conta deletada permanentemente - user_id={user_id}")