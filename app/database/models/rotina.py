from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Rotina(Base):
    __tablename__ = "rotinas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(Text, nullable=True)
    usuario_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relações
    dias = relationship("DiaTreino", back_populates="rotina", cascade="all, delete-orphan")
    sugestoes_nutricionais = relationship("Refeicao", back_populates="rotina", cascade="all, delete-orphan")


class DiaTreino(Base):
    __tablename__ = "dias_treino"

    id = Column(Integer, primary_key=True, index=True)
    rotina_id = Column(Integer, ForeignKey("rotinas.id"), nullable=False, index=True)
    identificacao = Column(String, nullable=False)
    foco_muscular = Column(String, nullable=True)
    ordem = Column(Integer, nullable=True)

    rotina = relationship("Rotina", back_populates="dias")
    exercicios = relationship("RotinaExercicio", back_populates="dia", cascade="all, delete-orphan")


class RotinaExercicio(Base):
    __tablename__ = "rotina_exercicios"

    id = Column(Integer, primary_key=True, index=True)
    dia_id = Column(Integer, ForeignKey("dias_treino.id"), nullable=False, index=True)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"), nullable=True)
    nome = Column(String, nullable=False)
    series = Column(String, nullable=True)
    repeticoes = Column(String, nullable=True)
    descanso_segundos = Column(Integer, nullable=True)
    detalhes_execucao = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    ordem = Column(Integer, nullable=True)

    dia = relationship("DiaTreino", back_populates="exercicios")
    exercicio = relationship("Exercicio")
