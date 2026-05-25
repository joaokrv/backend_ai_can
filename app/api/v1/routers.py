# app/api/v1/routers.py

from fastapi import APIRouter
from app.api.v1.endpoints import treino, auth, feedback, planos, stats, catalogo, export

router = APIRouter()

router.include_router(treino.router, prefix="/sugestao", tags=["sugestao"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
router.include_router(planos.router, prefix="/planos", tags=["planos"])
router.include_router(stats.router, prefix="/stats", tags=["stats"])
router.include_router(catalogo.router, prefix="/catalogo", tags=["catalogo"])
router.include_router(export.router, prefix="/planos", tags=["export"])
