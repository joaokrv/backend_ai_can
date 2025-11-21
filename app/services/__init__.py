"""Services Package

Contém toda a lógica de negócio da aplicação.
"""

from app.services.ia_agent import generate_training_plan
from app.services.coleta_dados import (
    salvar_exercicios_e_refeicoes,
    obter_estatisticas_coleta,
)

__all__ = [
    "generate_training_plan",
    "salvar_exercicios_e_refeicoes",
    "obter_estatisticas_coleta",
]
