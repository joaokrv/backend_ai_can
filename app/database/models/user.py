from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from app.database.base import Base

class User(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "aican"}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True, unique=True)
    hash_senha = Column(String, nullable=False)
    idade = Column(Integer, nullable=True)
    altura = Column(Float, nullable=True)
    peso = Column(Float, nullable=True)
    local_treino = Column(String, nullable=True)
    objetivo = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    sexo = Column(String(2), nullable=True)
    dias_disponiveis = Column(ARRAY(String(10)), nullable=True)
    duracao_sessao = Column(Integer, nullable=True)
    restricoes_alimentares = Column(ARRAY(String(30)), nullable=True)
    lesoes_cuidados = Column(Text, nullable=True)
    nivel_experiencia = Column(String(20), nullable=True)
    onboarding_completo = Column(Boolean, nullable=False, default=False, server_default="false")
    aceite_termos_at = Column(DateTime(timezone=True), nullable=True)
    aceite_termos_versao = Column(String(10), nullable=True)
