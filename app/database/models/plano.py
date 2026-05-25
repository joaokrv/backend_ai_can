from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base

class Plano(Base):
    __tablename__ = "planos"
    __table_args__ = {"schema": "aican"}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    usuario_id = Column(
        Integer,
        ForeignKey("aican.usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String(20), nullable=False, default="ativo", server_default="ativo", index=True)
    explicacao_ia = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relações
    dias = relationship(
        "PlanoDia", back_populates="plano", cascade="all, delete-orphan"
    )
    refeicoes = relationship(
        "PlanoRefeicao", back_populates="plano", cascade="all, delete-orphan"
    )

    @property
    def sugestoes_nutricionais(self):
        return self.refeicoes

class PlanoDia(Base):
    __tablename__ = "plano_dias"
    __table_args__ = {"schema": "aican"}

    id = Column(Integer, primary_key=True, index=True)
    plano_id = Column(Integer, ForeignKey("aican.planos.id"), nullable=False, index=True)
    identificacao = Column(String, nullable=False)
    foco_muscular = Column(String, nullable=True)
    ordem = Column(Integer, nullable=True)

    plano = relationship("Plano", back_populates="dias")
    exercicios = relationship(
        "PlanoExercicio", back_populates="dia", cascade="all, delete-orphan"
    )

class PlanoExercicio(Base):
    __tablename__ = "plano_exercicios"
    __table_args__ = {"schema": "aican"}

    id = Column(Integer, primary_key=True, index=True)
    dia_id = Column(Integer, ForeignKey("aican.plano_dias.id"), nullable=False, index=True)
    nome = Column(String, nullable=False)
    series = Column(String, nullable=True)
    repeticoes = Column(String, nullable=True)
    descanso_segundos = Column(Integer, nullable=True)
    detalhes_execucao = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
    ordem = Column(Integer, nullable=True)

    dia = relationship("PlanoDia", back_populates="exercicios")
