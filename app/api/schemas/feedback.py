# app/api/schemas/feedback.py
"""Schemas para sistema de feedback de exercícios e refeições."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FeedbackCreate(BaseModel):
    """Schema para criar feedback de exercício ou refeição."""
    
    item_nome: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Nome do exercício ou refeição",
        examples=["Supino Reto", "Frango Grelhado"]
    )
    gostou: bool = Field(
        ...,
        description="Se o usuário gostou (true) ou não gostou (false)"
    )
    comentario: Optional[str] = Field(
        None,
        max_length=500,
        description="Comentário opcional explicando o feedback"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_nome": "Supino Reto",
                "gostou": False,
                "comentario": "Sinto desconforto  no ombro direito"
            }
        }


class FeedbackResponse(BaseModel):
    """Schema de resposta após salvar feedback."""
    
    id: int
    usuario_id: int
    tipo: str  # 'exercicio' ou 'refeicao'
    item_nome: str
    gostou: bool
    comentario: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PreferenciasUsuario(BaseModel):
    """Schema agregado de preferências do usuário."""
    
    exercicios: dict[str, list[str]] = Field(
        default_factory=lambda: {"gostou": [], "nao_gostou": []},
        description="Exercícios que o usuário gostou e não gostou"
    )
    refeicoes: dict[str, list[str]] = Field(
        default_factory=lambda: {"gostou": [], "nao_gostou": []},
        description="Refeições que o usuário gostou e não gostou"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "exercicios": {
                    "gostou": ["Agachamento Livre", "Rosca Direta"],
                    "nao_gostou": ["Supino Reto", "Leg Press"]
                },
                "refeicoes": {
                    "gostou": ["Omelete de Claras"],
                    "nao_gostou": ["Frango Grelhado", "Peixe"]
                }
            }
        }


class FeedbackStats(BaseModel):
    """Estatísticas de feedback para análise."""
    
    total_feedbacks: int
    total_positivos: int
    total_negativos: int
    taxa_satisfacao: float =  Field(description="Percentual de feedbacks positivos")
    exercicios_mais_rejeitados: list[str] = []
    refeicoes_mais_rejeitadas: list[str] = []
