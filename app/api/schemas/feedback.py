from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from app.core.sanitizers import safe_item_nome, safe_comentario
from app.api.schemas.enums import TipoFeedback


class FeedbackCreate(BaseModel):
    item_nome: str = Field(..., min_length=2, max_length=255)
    gostou: bool
    comentario: Optional[str] = Field(None, max_length=500)

    @field_validator("item_nome")
    @classmethod
    def validate_item_nome(cls, v: str) -> str:
        return safe_item_nome(v)

    @field_validator("comentario")
    @classmethod
    def validate_comentario(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return safe_comentario(v, max_length=500)


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    tipo: TipoFeedback
    item_nome: str
    gostou: bool
    comentario: Optional[str]
    created_at: datetime


class PreferenciasUsuario(BaseModel):
    exercicios: dict[str, list[str]] = Field(
        default_factory=lambda: {"gostou": [], "nao_gostou": []}
    )
    refeicoes: dict[str, list[str]] = Field(
        default_factory=lambda: {"gostou": [], "nao_gostou": []}
    )


class FeedbackStats(BaseModel):
    """Estatisticas binarias (count sempre 1 devido a UniqueConstraint last-wins).
    Top items rejeitados/curtidos sao apenas listas dos 5 mais recentes."""
    total_feedbacks: int
    total_positivos: int
    total_negativos: int
    taxa_satisfacao: float
    exercicios_mais_rejeitados: List[str] = []
    exercicios_mais_curtidos: List[str] = []
    refeicoes_mais_rejeitadas: List[str] = []
    refeicoes_mais_curtidas: List[str] = []


class PaginatedFeedbacksResponse(BaseModel):
    itens: List[FeedbackResponse]
    total: int
    pagina: int
    limite: int
    paginas: int


class DeleteFeedbackResponse(BaseModel):
    deleted: int
