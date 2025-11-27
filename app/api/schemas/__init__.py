# app/api/schemas/__init__.py

from app.api.schemas.user import UserCreate, UserResponse, UserUpdate, Token, TokenData
from app.api.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    PreferenciasUsuario,
    FeedbackStats
)
from app.api.schemas.exercicio import (
    ExercicioCreate,
    ExercicioResponse,
    ExercicioUpdate,
)
from app.api.schemas.plano import (
    PlanoCreate,
    PlanoResponse,
    PlanoUpdate,
    PlanoDiaCreate,
    PlanoDiaResponse,
    PlanoExercicioCreate,
    PlanoExercicioResponse,
    PlanoRefeicaoCreate,
    PlanoRefeicaoResponse,
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
    "PreferenciasUsuario",
    "FeedbackStats",
    # Exercicio
    "ExercicioCreate",
    "ExercicioResponse",
    "ExercicioUpdate",
    # Plano
    "PlanoCreate",
    "PlanoResponse",
    "PlanoUpdate",
    "PlanoDiaCreate",
    "PlanoDiaResponse",
    "PlanoExercicioCreate",
    "PlanoExercicioResponse",
    "PlanoRefeicaoCreate",
    "PlanoRefeicaoResponse",
    # Refeicao
    "RefeicaoCreate",
    "RefeicaoResponse",
    "RefeicaoUpdate",
]
