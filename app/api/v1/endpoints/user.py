# app/api/v1/endpoints/user.py
# Rotas de usuário (cadastro, login)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.schemas.user import UserCreate, UserResponse
from app.database.base import get_db
from app.services.user_service import create_user, authenticate_user
from app.core.security import create_access_token

router = APIRouter()
