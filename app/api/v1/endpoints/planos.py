from fastapi import APIRouter, status, Request
from app.api import deps
from app.database.models.plano import Plano
from app.api.schemas.plano import PlanoDetailResponse, PlanoSummaryResponse, PaginatedPlanosResponse
from app.api.utils.paginacao import normalizar_paginacao, calcular_paginas
from app.api.utils.db_errors import handle_db_errors
from app.services.plano_service import get_plano_or_403, get_plano_detalhado_or_403
from app.api.schemas.enums import StatusPlano
from app.core.limiter import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=PaginatedPlanosResponse)
@limiter.limit("30/minute")
def listar_planos(
    request: Request,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
    page: int = 1,
    limit: int = 10,
):
    page, limit, offset = normalizar_paginacao(page, limit, max_limit=50, default_limit=10)

    base_query = session.query(Plano).filter(Plano.usuario_id == current_user.id)
    total = base_query.count()
    planos = base_query.order_by(Plano.created_at.desc()).offset(offset).limit(limit).all()

    return PaginatedPlanosResponse(
        itens=[
            PlanoSummaryResponse(
                id=p.id,
                nome=p.nome,
                status=p.status,
                created_at=p.created_at.isoformat() if p.created_at else None,
            )
            for p in planos
        ],
        total=total,
        pagina=page,
        limite=limit,
        paginas=calcular_paginas(total, limit),
    )



@router.put("/{plano_id}/ativar", response_model=PlanoDetailResponse)
@limiter.limit("10/minute")
@handle_db_errors("ativar plano")
def ativar_plano(
    request: Request,
    plano_id: int,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    plano = get_plano_detalhado_or_403(plano_id, current_user.id, session)

    session.query(Plano).filter(
        Plano.usuario_id == current_user.id,
        Plano.status == StatusPlano.ATIVO.value,
    ).update({"status": StatusPlano.ARQUIVADO.value}, synchronize_session=False)

    plano.status = StatusPlano.ATIVO.value
    session.commit()
    session.refresh(plano)

    logger.info(f"Plano reativado: plano_id={plano_id}, user_id={current_user.id}")
    return plano

@router.get("/{plano_id}", response_model=PlanoDetailResponse)
@limiter.limit("30/minute")
def obter_plano(
    request: Request,
    plano_id: int,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    return get_plano_detalhado_or_403(plano_id, current_user.id, session)


@router.delete("/{plano_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
@handle_db_errors("deletar plano")
def deletar_plano(
    request: Request,
    plano_id: int,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    plano = get_plano_or_403(plano_id, current_user.id, session)
    session.delete(plano)
    session.commit()
    logger.info(f"Plano deletado: plano_id={plano_id}, user_id={current_user.id}")
