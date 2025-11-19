# app/api/schemas/feedback.py
from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    usuario_id: int
    exercicio_id: int
    gostou: bool
    comentario: str | None = None


class FeedbackResponse(BaseModel):
    id: int
    usuario_id: int
    exercicio_id: int
    gostou: bool
    comentario: str | None

    class Config:
        from_attributes = True
