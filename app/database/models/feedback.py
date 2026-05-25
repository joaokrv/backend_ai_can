from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.database.base import Base


class Feedback(Base):
    __tablename__ = "feedbacks"
    __table_args__ = (
        UniqueConstraint("usuario_id", "tipo", "item_nome", name="uq_feedback_user_tipo_item"),
        {"schema": "aican"},
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("aican.usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    tipo = Column(String(20), nullable=False, index=True)
    item_nome = Column(String(255), nullable=False, index=True)
    gostou = Column(Boolean, nullable=False)
    comentario = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
