# app/core/config.py
# Configurações do ambiente (.env)

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente"""
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Cerebras AI API
    CEREBRAS_API_KEY: str
    
    # Environment
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        validate_assignment = True
        case_sensitive = False


settings = Settings()
