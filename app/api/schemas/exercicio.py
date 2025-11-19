# app/api/schemas/exercicio.py
from pydantic import BaseModel
from typing import Optional


class ExercicioBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    nivel: Optional[str] = None
    video_url: Optional[str] = None


class ExercicioCreate(ExercicioBase):
    pass


class ExercicioUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    nivel: Optional[str] = None
    video_url: Optional[str] = None


class ExercicioResponse(ExercicioBase):
    id: int

    class Config:
        from_attributes = True
