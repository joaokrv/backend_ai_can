from sqlalchemy import Column, Integer, String, Text, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from app.database.base import Base

class PlanoRefeicao(Base):
    __tablename__ = "plano_refeicoes"

    id = Column(Integer, primary_key=True, index=True)
    plano_id = Column(Integer, ForeignKey("planos.id"), nullable=False, index=True)
    
    nome = Column(String(255), nullable=False, index=True)
    custo_estimado = Column(String, nullable=True)
    tipo = Column(String, nullable=True)  # pre_treino, pos_treino
    nivel = Column(String, nullable=True)  # economica, equilibrada, premium
    
    ingredientes = Column(ARRAY(String), nullable=True)
    
    link_receita = Column(String, nullable=True)
    explicacao = Column(Text, nullable=True)

    plano = relationship("Plano", back_populates="refeicoes")


class CatalogoRefeicao(Base):
    __tablename__ = "catalogo_refeicoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), unique=True, index=True, nullable=False)
    custo_estimado = Column(String, nullable=True)
    tipo = Column(String, nullable=True)
    nivel = Column(String, nullable=True)
    ingredientes = Column(ARRAY(String), nullable=True)
    link_receita = Column(String, nullable=True)
    explicacao = Column(Text, nullable=True)
