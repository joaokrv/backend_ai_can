# app/database/models/__init__.py
from app.database.models.user import User
from app.database.models.exercicio import Exercicio
from app.database.models.feedback import Feedback
from app.database.models.refeicoes import Refeicao
from app.database.models.rotina import Rotina, DiaTreino, RotinaExercicio

__all__ = [
	"User",
	"Exercicio",
	"Feedback",
	"Refeicao",
	"Rotina",
	"DiaTreino",
	"RotinaExercicio",
]
