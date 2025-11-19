# app/database/models/exercicio.py
# Mapeia a tabela EXERCICIO

from sqlalchemy import Column, Integer, String, Text
from app.database.base import Base


class Exercicio(Base):
    __tablename__ = "exercicios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(Text, nullable=True)
    tipo = Column(String, nullable=True)  # Ex: cardio, força, flexibilidade
    nivel = Column(String, nullable=True)  # Ex: iniciante, intermediário, avançado
    video_url = Column(String, nullable=True)
