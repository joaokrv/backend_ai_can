# app/api/v1/routers.py

from fastapi import APIRouter
from app.api.v1.endpoints import treino, auth, feedback

router = APIRouter()

router.include_router(treino.router, prefix="/sugestao", tags=["sugestao"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
