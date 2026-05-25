from pydantic import BaseModel
from typing import List, Optional


class PeriodoStats(BaseModel):
    periodo: str
    planos_gerados: int
    feedbacks_positivos: int
    feedbacks_negativos: int


class StatsResponse(BaseModel):
    series: List[PeriodoStats]
    total_planos: int
    total_feedbacks: int
    periodo_inicio: str
    periodo_fim: str
