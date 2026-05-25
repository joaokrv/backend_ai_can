# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente"""

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # token curto — limitado em caso de vazamento
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # sessão semanal com rotação

    # Gemini AI API
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_DAILY_LIMIT: int = 200  # Limite diário de chamadas (free tier: 250 RPD)

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500,https://aican-yile.onrender.com"

    # Environment
    DEBUG: bool = False

    # Terms & Legal
    TERMS_VERSION: str = "1.0"

    @field_validator("CORS_ORIGINS")
    @classmethod
    def cors_no_wildcard(cls, v: str) -> str:
        if "*" in v.split(","):
            raise ValueError("CORS_ORIGINS nao pode conter wildcard '*' em producao")
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_min_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY deve ter no mínimo 32 caracteres")
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string em lista de origens"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        validate_assignment = True
        case_sensitive = False


settings = Settings()
