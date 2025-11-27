from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Plano(Base):
    __tablename__ = "planos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    usuario_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relações
    dias = relationship(
        "PlanoDia", back_populates="plano", cascade="all, delete-orphan"
    )
    refeicoes = relationship(
        "PlanoRefeicao", back_populates="plano", cascade="all, delete-orphan"
    )


class PlanoDia(Base):
    __tablename__ = "plano_dias"

    id = Column(Integer, primary_key=True, index=True)
    plano_id = Column(Integer, ForeignKey("planos.id"), nullable=False, index=True)
    identificacao = Column(String, nullable=False)  # Ex: "Dia A"
    foco_muscular = Column(String, nullable=True)
    ordem = Column(Integer, nullable=True)

    plano = relationship("Plano", back_populates="dias")
    exercicios = relationship(
        "PlanoExercicio", back_populates="dia", cascade="all, delete-orphan"
    )


class PlanoExercicio(Base):
    __tablename__ = "plano_exercicios"

    id = Column(Integer, primary_key=True, index=True)
    dia_id = Column(Integer, ForeignKey("plano_dias.id"), nullable=False, index=True)    
    nome = Column(String, nullable=False)
    series = Column(String, nullable=True)
    repeticoes = Column(String, nullable=True)
    descanso_segundos = Column(Integer, nullable=True)
    detalhes_execucao = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    ordem = Column(Integer, nullable=True)

    dia = relationship("PlanoDia", back_populates="exercicios")
