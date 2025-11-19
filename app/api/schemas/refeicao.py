# app/api/schemas/refeicao.py
from pydantic import BaseModel
from typing import Optional, List


class RefeicaoBase(BaseModel):
    nome: str
    tipo: Optional[str] = None  # "pre" ou "pos"
    nivel: Optional[str] = None  # "economica", "equilibrada", "premium"
    ingredientes: List[str]
    custo_estimado: Optional[str] = None
    link_receita: Optional[str] = None
    explicacao: Optional[str] = None


class RefeicaoCreate(RefeicaoBase):
    rotina_id: Optional[int] = None


class RefeicaoUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    nivel: Optional[str] = None
    ingredientes: Optional[List[str]] = None
    custo_estimado: Optional[str] = None
    link_receita: Optional[str] = None
    explicacao: Optional[str] = None


class RefeicaoResponse(RefeicaoBase):
    id: int
    rotina_id: Optional[int] = None

    class Config:
        from_attributes = True
