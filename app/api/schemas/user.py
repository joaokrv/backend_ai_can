# app/api/schemas/user.py
# Modelos Pydantic (validação de dados)

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nome: str
    idade: int | None = None
    altura: float | None = None  # em cm
    peso: float | None = None  # em kg
    local_treino: str | None = None
    frequencia_semana: str | None = None
    objetivo: str | None = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nome: str
    idade: int | None
    altura: float | None
    peso: float | None
    local_treino: str | None
    frequencia_semana: str | None
    objetivo: str | None
    is_active: bool

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nome: str | None = None
    idade: int | None = None
    altura: float | None = None
    peso: float | None = None
    local_treino: str | None = None
    frequencia_semana: str | None = None
    objetivo: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
