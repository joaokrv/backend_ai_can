import functools
import logging
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


def handle_db_errors(operacao: str):
    """Decorator que captura SQLAlchemyError, faz rollback e retorna 500.
    Uso: @handle_db_errors("salvar feedback")"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            session = kwargs.get("session")
            try:
                return func(*args, **kwargs)
            except HTTPException:
                raise
            except SQLAlchemyError as e:
                if session:
                    session.rollback()
                logger.error(f"Erro de banco em {operacao}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erro ao {operacao}",
                )
        return wrapper
    return decorator
