# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routers import router as v1_router
from app.core.config import settings
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Configurar rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AICan - Treino IA API",
    description="API para geração de planos de treino personalizados com IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Adicionar rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5500",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "http://192.168.1.42:5500",
        "https://aican-yile.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.error(f"IntegrityError: {exc}")
    return JSONResponse(
        status_code=409,
        content={"detail": "Conflito de dados. Verifique se o item já existe."},
    )

@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError):
    logger.error(f"OperationalError: {exc}")
    return JSONResponse(
        status_code=503,
        content={"detail": "Erro de conexão com o banco de dados. Tente novamente mais tarde."},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
