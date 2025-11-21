# app/api/schemas/rotina.py
from pydantic import BaseModel
from typing import List, Optional


class ExercicioBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    nivel: Optional[str] = None
    video_url: Optional[str] = None


class ExercicioResponse(ExercicioBase):
    id: int

    class Config:
        from_attributes = True


class RotinaExercicioCreate(BaseModel):
    nome: str
    series: Optional[str] = None
    repeticoes: Optional[str] = None
    descanso_segundos: Optional[int] = None
    detalhes_execucao: Optional[str] = None
    video_url: Optional[str] = None
    exercicio_id: Optional[int] = None
    ordem: Optional[int] = None


class RotinaExercicioResponse(RotinaExercicioCreate):
    id: int
    dia_id: int
    exercicio: Optional[ExercicioResponse] = None

    class Config:
        from_attributes = True


class DiaTreinoCreate(BaseModel):
    identificacao: str
    foco_muscular: Optional[str] = None
    ordem: Optional[int] = None
    exercicios: List[RotinaExercicioCreate] = []


class DiaTreinoResponse(BaseModel):
    id: int
    identificacao: str
    foco_muscular: Optional[str] = None
    ordem: Optional[int] = None
    exercicios: List[RotinaExercicioResponse] = []

    class Config:
        from_attributes = True


class RefeicaoCreate(BaseModel):
    nome: str
    tipo: Optional[str] = None  # "pre" ou "pos"
    nivel: Optional[str] = None  # "economica", "equilibrada", "premium"
    ingredientes: List[str]
    custo_estimado: Optional[str] = None
    link_receita: Optional[str] = None
    explicacao: Optional[str] = None
    rotina_id: Optional[int] = None


class RefeicaoResponse(RefeicaoCreate):
    id: int

    class Config:
        from_attributes = True


class RotinaCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    usuario_id: Optional[int] = None
    dias_de_treino: List[DiaTreinoCreate] = []
    sugestoes_nutricionais: Optional[List[RefeicaoCreate]] = None


class RotinaResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    usuario_id: Optional[int] = None
    dias: List[DiaTreinoResponse] = []
    sugestoes_nutricionais: List[RefeicaoResponse] = []
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class RotinaUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    dias_de_treino: Optional[List[DiaTreinoCreate]] = None
    sugestoes_nutricionais: Optional[List[RefeicaoCreate]] = None


class RotinaDetailResponse(RotinaResponse):
    """Resposta completa com todos os detalhes da rotina."""

    pass
