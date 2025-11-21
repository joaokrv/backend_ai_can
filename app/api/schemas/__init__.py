# app/api/schemas/__init__.py
# Exportar todos os schemas

from app.api.schemas.user import UserCreate, UserResponse, UserUpdate, Token, TokenData
from app.api.schemas.feedback import FeedbackCreate, FeedbackResponse
from app.api.schemas.exercicio import (
    ExercicioCreate,
    ExercicioResponse,
    ExercicioUpdate,
)
from app.api.schemas.rotina import (
    RotinaCreate,
    RotinaResponse,
    RotinaUpdate,
    DiaTreinoCreate,
    DiaTreinoResponse,
    RotinaExercicioCreate,
    RotinaExercicioResponse,
)
from app.api.schemas.refeicao import RefeicaoCreate, RefeicaoResponse, RefeicaoUpdate

__all__ = [
    # User
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "Token",
    "TokenData",
    # Feedback
    "FeedbackCreate",
    "FeedbackResponse",
    # Exercicio
    "ExercicioCreate",
    "ExercicioResponse",
    "ExercicioUpdate",
    # Rotina
    "RotinaCreate",
    "RotinaResponse",
    "RotinaUpdate",
    "DiaTreinoCreate",
    "DiaTreinoResponse",
    "RotinaExercicioCreate",
    "RotinaExercicioResponse",
    # Refeicao
    "RefeicaoCreate",
    "RefeicaoResponse",
    "RefeicaoUpdate",
]
