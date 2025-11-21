# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routers import router as v1_router
from app.core.config import settings
import logging

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AICan - Treino IA API",
    description="API para geração de planos de treino personalizados com IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5500",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "http://192.168.1.42:5500",
        "https://frontend_ai_can.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(v1_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """Endpoint de health check"""
    return {"status": "online", "service": "AICan API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check():
    """Verifica se a API está funcionando"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
