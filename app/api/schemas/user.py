# app/api/schemas/user.py
# Modelos Pydantic (validação de dados)

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    nome: str
    idade: int | None = None
    altura: int | None = None  # em cm
    peso: int | None = None  # em kg
    local_treino: str | None = None
    frequencia_semana: str | None = None
    objetivo: str | None = None


class UserResponse(BaseModel):
    id: int
    nome: str
    idade: int | None
    altura: int | None
    peso: int | None
    local_treino: str | None
    frequencia_semana: str | None
    objetivo: str | None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nome: str | None = None
    idade: int | None = None
    altura: int | None = None
    peso: int | None = None
    local_treino: str | None = None
    frequencia_semana: str | None = None
    objetivo: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None