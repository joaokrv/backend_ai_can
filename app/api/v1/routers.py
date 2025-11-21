# app/api/v1/routers.py
# Agrega todos os endpoints (rotas)

from fastapi import APIRouter
from app.api.v1.endpoints import treino

router = APIRouter()

# Inclui as rotas de treino/sugestão
router.include_router(treino.router, prefix="/sugestao", tags=["sugestao"])
