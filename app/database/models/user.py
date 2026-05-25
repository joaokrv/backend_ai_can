# app/database/models/user.py
# Mapeia a tabela USUARIO

from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from app.database.base import Base


class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True, unique=True)
    hash_senha = Column(String, nullable=False)
    idade = Column(Integer, nullable=True)
    altura = Column(Float, nullable=True)  # em cm (suporta decimais: 175.5)
    peso = Column(Float, nullable=True)  # em kg (suporta decimais: 80.3)
    local_treino = Column(String, nullable=True)  # academia, casa, parque, etc.
    objetivo = Column(String, nullable=True)  # emagrecimento, hipertrofia, etc.
    is_active = Column(Boolean, nullable=False, default=True)

    sexo = Column(String(2), nullable=True)  # "M", "F", "O", "N"
    dias_disponiveis = Column(ARRAY(String(10)), nullable=True)  # ["segunda", "terca", ...]
    duracao_sessao = Column(Integer, nullable=True)  # minutos
    restricoes_alimentares = Column(ARRAY(String(30)), nullable=True)  # ["lactose", "gluten", ...]
    lesoes_cuidados = Column(Text, nullable=True)  # descrição de lesões/limitações
    nivel_experiencia = Column(String(20), nullable=True)  # "iniciante", "intermediario", "avancado"
    onboarding_completo = Column(Boolean, nullable=False, default=False, server_default="false")
    aceite_termos_at = Column(DateTime(timezone=True), nullable=True)  # quando aceitou os termos
    aceite_termos_versao = Column(String(10), nullable=True)  # versão dos termos aceitos
