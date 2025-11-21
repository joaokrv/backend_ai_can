"""AICan App - Aplicação de IA para geração de planos de treino personalizados

Este pacote contém toda a lógica da aplicação.
"""

from app.services.ia_agent import generate_training_plan
from app.core.config import settings

__all__ = [
    "generate_training_plan",
    "settings",
]
