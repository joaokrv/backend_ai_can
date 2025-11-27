# app/database/models/feedback.py
# Mapeia a tabela FEEDBACK para exercícios e refeições

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from datetime import datetime
from app.database.base import Base


class Feedback(Base):
    """
    Modelo de feedback para exercícios e refeições.
    Permite ao usuário avaliar itens e o sistema usa isso para personalização.
    """
    __tablename__ = "feedbacks"
    __table_args__ = {"schema": "aican"}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("aican.usuarios.id"), nullable=False, index=True)
    tipo = Column(String(20), nullable=False, index=True)
    item_nome = Column(String(255), nullable=False, index=True)
    gostou = Column(Boolean, nullable=False)
    comentario = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
