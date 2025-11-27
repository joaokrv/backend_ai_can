from sqlalchemy import Column, Integer, String, Text
from app.database.base import Base

class CatalogoExercicio(Base):
    __tablename__ = "catalogo_exercicios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    grupo_muscular = Column(String, nullable=True)
    descricao = Column(Text, nullable=True)
    video_url = Column(String, nullable=True)
