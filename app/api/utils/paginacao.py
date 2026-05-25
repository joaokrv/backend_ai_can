from typing import TypeVar, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def normalizar_paginacao(page: int, limit: int, max_limit: int = 50, default_limit: int = 10) -> tuple[int, int, int]:
    """Normaliza page/limit e retorna (page, limit, offset)."""
    if page < 1:
        page = 1
    if limit < 1 or limit > max_limit:
        limit = default_limit
    offset = (page - 1) * limit
    return page, limit, offset


def calcular_paginas(total: int, limit: int) -> int:
    """Calcula numero total de paginas (sempre >=1)."""
    return (total + limit - 1) // limit if total > 0 else 1
