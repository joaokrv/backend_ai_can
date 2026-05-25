from fastapi import APIRouter, status, HTTPException, Request
from sqlalchemy import func, case
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.api import deps
from app.api.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    PreferenciasUsuario,
    FeedbackStats,
    PaginatedFeedbacksResponse,
    DeleteFeedbackResponse,
)
from app.api.schemas.enums import TipoFeedback
from app.api.utils.paginacao import normalizar_paginacao, calcular_paginas
from app.api.utils.db_errors import handle_db_errors
from app.services.feedback_service import agrupar_feedbacks
from app.database.models.feedback import Feedback
from app.core.limiter import limiter
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _upsert_feedback(tipo: TipoFeedback, feedback: FeedbackCreate, user_id: int, session) -> Feedback:
    existing = session.query(Feedback).filter(
        Feedback.usuario_id == user_id,
        Feedback.tipo == tipo.value,
        Feedback.item_nome == feedback.item_nome,
    ).first()

    if existing:
        existing.gostou = feedback.gostou
        existing.comentario = feedback.comentario
        session.commit()
        session.refresh(existing)
        return existing

    try:
        record = Feedback(
            usuario_id=user_id,
            tipo=tipo.value,
            item_nome=feedback.item_nome,
            gostou=feedback.gostou,
            comentario=feedback.comentario,
            created_at=datetime.now(timezone.utc),
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
    except IntegrityError as e:
        logger.exception(f"IntegrityError no upsert de feedback: user_id={user_id}, tipo={tipo.value}, item_nome={feedback.item_nome!r}, erro={e.orig!r}")
        session.rollback()
        # Concurrent request created the record first; fetch and update
        existing = session.query(Feedback).filter(
            Feedback.usuario_id == user_id,
            Feedback.tipo == tipo.value,
            Feedback.item_nome == feedback.item_nome,
        ).first()
        if existing:
            existing.gostou = feedback.gostou
            existing.comentario = feedback.comentario
            session.commit()
            session.refresh(existing)
            return existing
        raise HTTPException(status_code=500, detail="Erro ao registrar avaliacao. Tente novamente.")


@router.post("/{tipo}", response_model=FeedbackResponse, status_code=status.HTTP_200_OK)
@limiter.limit("30/minute")
def criar_feedback(
    request: Request,
    tipo: TipoFeedback,
    feedback: FeedbackCreate,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    result = _upsert_feedback(tipo, feedback, current_user.id, session)
    logger.info(f"Feedback upsert: user_id={current_user.id}, tipo={tipo.value}, gostou={feedback.gostou}")
    return result


@router.get("/me", response_model=PaginatedFeedbacksResponse)
@limiter.limit("60/minute")
def listar_feedbacks(
    request: Request,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
    page: int = 1,
    limit: int = 20,
    tipo: Optional[TipoFeedback] = None,
    gostou: Optional[bool] = None,
):
    page, limit, offset = normalizar_paginacao(page, limit, max_limit=100, default_limit=20)
    query = session.query(Feedback).filter(Feedback.usuario_id == current_user.id)
    if tipo is not None:
        query = query.filter(Feedback.tipo == tipo.value)
    if gostou is not None:
        query = query.filter(Feedback.gostou == gostou)
    total = query.count()
    itens = query.order_by(Feedback.created_at.desc()).offset(offset).limit(limit).all()
    return PaginatedFeedbacksResponse(
        itens=itens, total=total, pagina=page, limite=limit, paginas=calcular_paginas(total, limit)
    )


@router.get("/me/preferencias", response_model=PreferenciasUsuario)
@limiter.limit("60/minute")
def listar_preferencias(
    request: Request,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    base = agrupar_feedbacks(current_user.id, session)
    return PreferenciasUsuario(
        exercicios={"gostou": base["exercicios_gostou"], "nao_gostou": base["exercicios_nao_gostou"]},
        refeicoes={"gostou": base["refeicoes_gostou"], "nao_gostou": base["refeicoes_nao_gostou"]},
    )


@router.delete("/me/all", response_model=DeleteFeedbackResponse, status_code=status.HTTP_200_OK)
@limiter.limit("5/hour")
@handle_db_errors("deletar feedbacks em massa")
def deletar_todos_feedbacks(
    request: Request,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
    tipo: Optional[TipoFeedback] = None,
    gostou: Optional[bool] = None,
):
    query = session.query(Feedback).filter(Feedback.usuario_id == current_user.id)
    if tipo is not None:
        query = query.filter(Feedback.tipo == tipo.value)
    if gostou is not None:
        query = query.filter(Feedback.gostou == gostou)
    count = query.count()
    query.delete()
    session.commit()
    logger.info(f"Feedbacks deletados em massa: user_id={current_user.id}, count={count}")
    return DeleteFeedbackResponse(deleted=count)


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
@handle_db_errors("deletar feedback")
def deletar_feedback(
    request: Request,
    feedback_id: int,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    feedback = session.query(Feedback).filter(
        Feedback.id == feedback_id,
        Feedback.usuario_id == current_user.id,
    ).first()
    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback nao encontrado")
    session.delete(feedback)
    session.commit()
    logger.info(f"Feedback deletado: id={feedback_id}, user_id={current_user.id}")


@router.get("/stats", response_model=FeedbackStats)
@limiter.limit("30/minute")
def obter_estatisticas(
    request: Request,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
):
    totais = session.query(
        func.count(Feedback.id).label("total"),
        func.sum(case((Feedback.gostou == True, 1), else_=0)).label("positivos"),
    ).filter(Feedback.usuario_id == current_user.id).one()

    total = totais.total or 0
    positivos = int(totais.positivos or 0)
    taxa = round((positivos / total * 100), 2) if total > 0 else 0.0

    def top5(tipo_val: TipoFeedback, gostou_val: bool) -> list[str]:
        rows = session.query(Feedback.item_nome).filter(
            Feedback.usuario_id == current_user.id,
            Feedback.tipo == tipo_val.value,
            Feedback.gostou == gostou_val,
        ).order_by(Feedback.created_at.desc()).limit(5).all()
        return [r[0] for r in rows]

    return FeedbackStats(
        total_feedbacks=total,
        total_positivos=positivos,
        total_negativos=total - positivos,
        taxa_satisfacao=taxa,
        exercicios_mais_rejeitados=top5(TipoFeedback.EXERCICIO, False),
        exercicios_mais_curtidos=top5(TipoFeedback.EXERCICIO, True),
        refeicoes_mais_rejeitadas=top5(TipoFeedback.REFEICAO, False),
        refeicoes_mais_curtidas=top5(TipoFeedback.REFEICAO, True),
    )