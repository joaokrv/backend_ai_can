# app/api/v1/routers.py

from fastapi import APIRouter
from app.api.v1.endpoints import treino

router = APIRouter()

router.include_router(treino.router, prefix="/sugestao", tags=["sugestao"])
