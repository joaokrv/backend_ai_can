# app/api/schemas/sugestao.py
"""Schemas para requisições de sugestão de treino e planos"""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class LocalTreino(str, Enum):
    """Locais de treino permitidos"""
    ACADEMIA = "academia"
    CASA = "casa"
    AR_LIVRE = "arLivre"


class ObjetivoTreino(str, Enum):
    """Objetivos de treino permitidos"""
    PERDER_PESO = "perder"
    GANHAR_PESO = "ganhar"
    HIPERTROFIA = "hipertrofia"


class SugestaoCreate(BaseModel):
    """Schema para requisição de sugestão de treino"""
    
    nome: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nome completo do usuário"
    )
    altura: float = Field(
        ...,
        gt=50,
        lt=300,
        description="Altura em centimetros (entre 50cm e 300cm)"
    )
    peso: float = Field(
        ...,
        gt=20,
        lt=500,
        description="Peso em kg (entre 20kg e 500kg)"
    )
    idade: int = Field(
        ...,
        ge=11,
        le=110,
        description="Idade em anos (entre 11 e 110 anos)"
    )
    disponibilidade: int = Field(
        ...,
        ge=1,
        le=7,
        description="Quantas vezes por semana pode treinar (1-7)"
    )
    local: LocalTreino = Field(
        ...,
        description="Local onde vai treinar (academia, casa, arLivre)"
    )
    objetivo: ObjetivoTreino = Field(
        ...,
        description="Objetivo principal do treino (perder peso, ganhar peso, hipertrofia)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "João Silva",
                "altura": 175,
                "peso": 80,
                "idade": 30,
                "disponibilidade": 3,
                "local": "academia",
                "objetivo": "hipertrofia"
            }
        }
