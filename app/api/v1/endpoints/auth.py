from typing import Any
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.database.models.user import User
from app.api import deps
from app.api.schemas.user import UserCreate, UserResponse, Token

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(
    session: deps.SessionDep, form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = session.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hash_senha):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email ou senha incorreta"
        )
    elif not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            {"sub": user.email}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserResponse)
def register_user(
    *,
    session: deps.SessionDep,
    user_in: UserCreate,
) -> Any:
    user = session.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O usuário com esse email já existe no sistema",
        )
    
    user = User(
        email=user_in.email,
        hash_senha=security.get_password_hash(user_in.password),
        nome=user_in.nome,
        idade=user_in.idade,
        altura=user_in.altura,
        peso=user_in.peso,
        local_treino=user_in.local_treino,
        frequencia_semana=user_in.frequencia_semana,
        objetivo=user_in.objetivo,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: deps.CurrentUser) -> Any:
    return current_user
