# app/api/schemas/plano.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


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


class PlanoExercicioCreate(BaseModel):
    nome: str
    series: Optional[str] = None
    repeticoes: Optional[str] = None
    descanso_segundos: Optional[int] = None
    detalhes_execucao: Optional[str] = None
    video_url: Optional[str] = None
    exercicio_id: Optional[int] = None
    ordem: Optional[int] = None


class PlanoExercicioResponse(PlanoExercicioCreate):
    id: int
    dia_id: int
    exercicio: Optional[ExercicioResponse] = None

    class Config:
        from_attributes = True


class PlanoDiaCreate(BaseModel):
    identificacao: str
    foco_muscular: Optional[str] = None
    ordem: Optional[int] = None
    exercicios: List[PlanoExercicioCreate] = []


class PlanoDiaResponse(BaseModel):
    id: int
    identificacao: str
    foco_muscular: Optional[str] = None
    ordem: Optional[int] = None
    exercicios: List[PlanoExercicioResponse] = []

    class Config:
        from_attributes = True


class PlanoRefeicaoCreate(BaseModel):
    nome: str
    tipo: Optional[str] = None
    nivel: Optional[str] = None
    ingredientes: List[str]
    custo_estimado: Optional[str] = None
    link_receita: Optional[str] = None
    explicacao: Optional[str] = None
    plano_id: Optional[int] = None


class PlanoRefeicaoResponse(PlanoRefeicaoCreate):
    id: int
    calorias: Optional[int] = None
    proteina_g: Optional[float] = None
    carboidrato_g: Optional[float] = None
    gordura_g: Optional[float] = None
    macros_estimados: bool = False

    class Config:
        from_attributes = True


class PlanoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    usuario_id: Optional[int] = None
    dias_de_treino: List[PlanoDiaCreate] = []
    sugestoes_nutricionais: Optional[List[PlanoRefeicaoCreate]] = None


class PlanoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    usuario_id: Optional[int] = None
    status: str = "ativo"
    explicacao_ia: Optional[str] = None
    dias: List[PlanoDiaResponse] = []
    sugestoes_nutricionais: List[PlanoRefeicaoResponse] = []
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class PlanoSummaryResponse(BaseModel):
    id: int
    nome: str
    status: str = "ativo"
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class PaginatedPlanosResponse(BaseModel):
    itens: List[PlanoSummaryResponse]
    total: int
    pagina: int
    limite: int
    paginas: int


class PlanoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    dias_de_treino: Optional[List[PlanoDiaCreate]] = None
    sugestoes_nutricionais: Optional[List[PlanoRefeicaoCreate]] = None


class PlanoDetailResponse(PlanoResponse):
    """Resposta completa com todos os detalhes do plano."""
    pass


class PlanoIAResponse(BaseModel):
    """Resposta do endpoint de geração de plano com IA."""
    plano: dict
    status: str
    mensagem: str
