"""Database Package

Contém configuração do banco de dados e modelos SQLAlchemy.
"""

from app.database.base import Base, engine, get_db

__all__ = ["Base", "engine", "get_db"]
