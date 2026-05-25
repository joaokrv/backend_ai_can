from sqlalchemy import Column, Integer, String, Text, ForeignKey, ARRAY, Float, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base

class PlanoRefeicao(Base):
    __tablename__ = "plano_refeicoes"
    __table_args__ = {"schema": "aican"}

    id = Column(Integer, primary_key=True, index=True)
    plano_id = Column(Integer, ForeignKey("aican.planos.id"), nullable=False, index=True)

    nome = Column(String(255), nullable=False, index=True)
    custo_estimado = Column(String, nullable=True)
    tipo = Column(String, nullable=True)
    nivel = Column(String, nullable=True)

    ingredientes = Column(ARRAY(String), nullable=True)

    link_receita = Column(String, nullable=True)
    explicacao = Column(Text, nullable=True)

    calorias = Column(Integer, nullable=True)
    proteina_g = Column(Float, nullable=True)
    carboidrato_g = Column(Float, nullable=True)
    gordura_g = Column(Float, nullable=True)
    macros_estimados = Column(Boolean, nullable=False, default=True, server_default="true")

    plano = relationship("Plano", back_populates="refeicoes")

class CatalogoRefeicao(Base):
    __tablename__ = "catalogo_refeicoes"
    __table_args__ = {"schema": "aican"}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), unique=True, index=True, nullable=False)
    custo_estimado = Column(String, nullable=True)
    tipo = Column(String, nullable=True)
    nivel = Column(String, nullable=True)
    ingredientes = Column(ARRAY(String), nullable=True)
    link_receita = Column(String, nullable=True)
    explicacao = Column(Text, nullable=True)

    calorias = Column(Integer, nullable=True)
    proteina_g = Column(Float, nullable=True)
    carboidrato_g = Column(Float, nullable=True)
    gordura_g = Column(Float, nullable=True)
    macros_estimados = Column(Boolean, nullable=False, default=True, server_default="true")
