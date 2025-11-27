# app/database/base.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy import MetaData

Base = declarative_base(metadata=MetaData(schema="aican"))

engine = create_engine(
    settings.DATABASE_URL, connect_args={"options": "-c search_path=aican"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from app.database.models.user import User
from app.database.models.plano import Plano, PlanoDia, PlanoExercicio
from app.database.models.catalogo_exercicio import CatalogoExercicio
from app.database.models.nutricao import PlanoRefeicao, CatalogoRefeicao

def get_db():
    """Dependência para obter uma sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
