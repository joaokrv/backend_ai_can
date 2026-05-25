from fastapi import APIRouter, Request
from sqlalchemy import or_
from typing import Optional
from app.api import deps
from app.api.schemas.catalogo import (
    CatalogoExercicioResponse,
    PaginatedCatalogoExerciciosResponse,
    CatalogoRefeicaoResponse,
    PaginatedCatalogoRefeicoesResponse,
)
from app.api.utils.paginacao import normalizar_paginacao, calcular_paginas
from app.database.models.catalogo_exercicio import CatalogoExercicio
from app.database.models.nutricao import CatalogoRefeicao
from app.core.limiter import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/exercicios", response_model=PaginatedCatalogoExerciciosResponse)
@limiter.limit("60/minute")
def listar_exercicios(
    request: Request,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
    q: Optional[str] = None,
    grupo_muscular: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
):
    page, limit, offset = normalizar_paginacao(page, limit, max_limit=100, default_limit=20)

    query = session.query(CatalogoExercicio)
    if q:
        query = query.filter(CatalogoExercicio.nome.ilike(f"%{q}%"))
    if grupo_muscular:
        query = query.filter(CatalogoExercicio.grupo_muscular.ilike(f"%{grupo_muscular}%"))

    total = query.count()
    itens = query.order_by(CatalogoExercicio.nome).offset(offset).limit(limit).all()

    logger.info(f"Catalogo exercicios: user_id={current_user.id}, q={q}, total={total}")
    return PaginatedCatalogoExerciciosResponse(
        itens=itens,
        total=total,
        pagina=page,
        limite=limit,
        paginas=calcular_paginas(total, limit),
    )


@router.get("/refeicoes", response_model=PaginatedCatalogoRefeicoesResponse)
@limiter.limit("60/minute")
def listar_refeicoes(
    request: Request,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
    q: Optional[str] = None,
    tipo: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
):
    page, limit, offset = normalizar_paginacao(page, limit, max_limit=100, default_limit=20)

    query = session.query(CatalogoRefeicao)
    if q:
        query = query.filter(CatalogoRefeicao.nome.ilike(f"%{q}%"))
    if tipo:
        query = query.filter(CatalogoRefeicao.tipo == tipo)

    total = query.count()
    itens = query.order_by(CatalogoRefeicao.nome).offset(offset).limit(limit).all()

    logger.info(f"Catalogo refeicoes: user_id={current_user.id}, q={q}, tipo={tipo}, total={total}")
    return PaginatedCatalogoRefeicoesResponse(
        itens=itens,
        total=total,
        pagina=page,
        limite=limit,
        paginas=calcular_paginas(total, limit),
    )
