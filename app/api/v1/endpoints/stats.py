from fastapi import APIRouter, HTTPException, status, Request
from sqlalchemy import func, case
from datetime import date, datetime, timezone, timedelta
from typing import Optional
from app.api import deps
from app.api.schemas.stats import StatsResponse, PeriodoStats
from app.database.models.plano import Plano
from app.database.models.feedback import Feedback
from app.core.limiter import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

JANELA_MAXIMA_DIAS = 730  # 2 anos


def _add_months(d: date, months: int) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    return d.replace(year=year, month=month, day=1)


@router.get("", response_model=StatsResponse)
@limiter.limit("30/minute")
def obter_stats(
    request: Request,
    current_user: deps.CurrentUser,
    session: deps.SessionDep,
    inicio: Optional[date] = None,
    fim: Optional[date] = None,
):
    hoje = date.today()

    if fim is None:
        fim = hoje
    if inicio is None:
        inicio = _add_months(hoje.replace(day=1), -5)

    if inicio > fim:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="inicio deve ser anterior a fim",
        )

    if (fim - inicio).days > JANELA_MAXIMA_DIAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Janela maxima permitida e {JANELA_MAXIMA_DIAS} dias",
        )

    inicio_dt = datetime(inicio.year, inicio.month, inicio.day, tzinfo=timezone.utc)
    fim_dt = datetime(fim.year, fim.month, fim.day, 23, 59, 59, tzinfo=timezone.utc)

    # date_trunc via SQLAlchemy ORM — consistencia com resto do codebase
    periodo_planos = func.to_char(func.date_trunc("month", Plano.created_at), "YYYY-MM").label("periodo")
    planos_rows = (
        session.query(periodo_planos, func.count(Plano.id).label("count"))
        .filter(
            Plano.usuario_id == current_user.id,
            Plano.created_at >= inicio_dt,
            Plano.created_at <= fim_dt,
        )
        .group_by(periodo_planos)
        .all()
    )

    periodo_fb = func.to_char(func.date_trunc("month", Feedback.created_at), "YYYY-MM").label("periodo")
    feedbacks_rows = (
        session.query(
            periodo_fb,
            func.sum(case((Feedback.gostou == True, 1), else_=0)).label("positivos"),
            func.sum(case((Feedback.gostou == False, 1), else_=0)).label("negativos"),
        )
        .filter(
            Feedback.usuario_id == current_user.id,
            Feedback.created_at >= inicio_dt,
            Feedback.created_at <= fim_dt,
        )
        .group_by(periodo_fb)
        .all()
    )

    planos_map = {r.periodo: int(r.count) for r in planos_rows}
    feedbacks_map = {r.periodo: (int(r.positivos or 0), int(r.negativos or 0)) for r in feedbacks_rows}

    series = []
    cursor = inicio.replace(day=1)
    fim_mes = fim.replace(day=1)
    while cursor <= fim_mes:
        periodo = cursor.strftime("%Y-%m")
        pos, neg = feedbacks_map.get(periodo, (0, 0))
        series.append(PeriodoStats(
            periodo=periodo,
            planos_gerados=planos_map.get(periodo, 0),
            feedbacks_positivos=pos,
            feedbacks_negativos=neg,
        ))
        cursor = _add_months(cursor, 1)

    total_planos = sum(p.planos_gerados for p in series)
    total_feedbacks = sum(p.feedbacks_positivos + p.feedbacks_negativos for p in series)

    logger.info(f"Stats: user_id={current_user.id}, periodos={len(series)}")

    return StatsResponse(
        series=series,
        total_planos=total_planos,
        total_feedbacks=total_feedbacks,
        periodo_inicio=inicio.isoformat(),
        periodo_fim=fim.isoformat(),
    )
