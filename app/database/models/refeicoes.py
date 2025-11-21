# app/database/models/refeicoes.py
# Mapeia a tabela REFEIÇÕES

from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey
from app.database.base import Base
from sqlalchemy.orm import relationship


class Refeicao(Base):
    __tablename__ = "refeicoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, unique=True, index=True)
    custo_estimado = Column(String, nullable=True)  # Ex: baixo, médio, alto
    tipo = Column(
        String, nullable=True
    )  # Ex.: "pre" ou "pos" (pré-treino / pós-treino)
    nivel = Column(String, nullable=True)  # Ex.: "economica", "equilibrada", "premium"
    ingredientes = Column(JSON, nullable=False)  # Lista de ingredientes como JSON array
    link_receita = Column(String, nullable=True)  # URL para a receita detalhada
    explicacao = Column(
        Text, nullable=True
    )  # Explicação sobre a refeição e seus benefícios
    rotina_id = Column(Integer, ForeignKey("rotinas.id"), nullable=True)
    rotina = relationship("Rotina", back_populates="sugestoes_nutricionais")
