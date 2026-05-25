from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.database.base import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = ({"schema": "aican"},)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("aican.usuarios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token_hash = Column(String(64), nullable=False, unique=True, index=True)

    family_id = Column(String(36), nullable=False, index=True)

    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
