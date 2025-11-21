# app/database/models/feedback.py
# Mapeia a tabela FEEDBACK

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from app.database.base import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    exercicio_id = Column(Integer, ForeignKey("exercicios.id"), nullable=False)
    gostou = Column(Boolean, nullable=False)
    comentario = Column(Text, nullable=True)
