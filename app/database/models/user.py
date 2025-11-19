# app/database/models/user.py
# Mapeia a tabela USUARIO

from sqlalchemy import Column, Integer, String
from app.database.base import Base


class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True) 
    nome = Column(String, nullable=False)
    idade = Column(Integer, nullable=True)
    altura = Column(Integer, nullable=True)  # em cm
    peso = Column(Integer, nullable=True)    # em kg
    local_treino = Column(String, nullable=True) # academia, casa, parque, etc.
    frequencia_semana = Column(String, nullable=True)  # 2x por semana, 3x por semana, etc.
    objetivo = Column(String, nullable=True)  # emagrecimento, hipertrofia, etc.