# app/api/schemas/user.py

from pydantic import BaseModel, EmailStr, Field, field_validator
from app.core.password_policy import validate_password
from app.core.sanitizers import safe_nome, safe_lesoes, safe_item_nome
from app.api.schemas.enums import (
    Sexo, DiaSemana, RestricaoAlimentar, NivelExperiencia,
    ObjetivoTreino, LocalTreino,
)

_OBJETIVO_ENUM_VALUES = {v.value for v in ObjetivoTreino}
_LOCAL_ENUM_VALUES = {v.value for v in LocalTreino}


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=10, max_length=128)
    nome: str = Field(..., min_length=2, max_length=100)
    idade: int | None = None
    altura: float | None = None
    peso: float | None = None
    local_treino: str | None = None
    objetivo: str | None = None
    aceite_termos: bool = Field(..., description="Usuário deve aceitar os termos de uso")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return validate_password(v)

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, v: str) -> str:
        return safe_nome(v, field_name="nome")

    @field_validator("aceite_termos")
    @classmethod
    def deve_aceitar_termos(cls, v: bool) -> bool:
        if not v:
            raise ValueError("É necessário aceitar os termos de uso para criar conta")
        return v


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nome: str
    idade: int | None
    altura: float | None
    peso: float | None
    local_treino: str | None
    objetivo: str | None
    is_active: bool
    sexo: str | None = None
    dias_disponiveis: list[str] | None = None
    duracao_sessao: int | None = None
    restricoes_alimentares: list[str] | None = None
    lesoes_cuidados: str | None = None
    nivel_experiencia: str | None = None
    onboarding_completo: bool = False
    aceite_termos_versao: str | None = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nome: str | None = Field(None, min_length=2, max_length=100)
    idade: int | None = Field(None, ge=11, le=110)
    altura: float | None = Field(None, gt=50, lt=300)
    peso: float | None = Field(None, gt=20, lt=300)
    sexo: Sexo | None = None
    dias_disponiveis: list[DiaSemana] | None = None
    duracao_sessao: int | None = Field(None, ge=15, le=300)
    restricoes_alimentares: list[RestricaoAlimentar] | None = None
    lesoes_cuidados: str | None = Field(None, max_length=500)
    nivel_experiencia: NivelExperiencia | None = None
    objetivo: str | None = Field(None, max_length=100)
    local_treino: str | None = Field(None, max_length=100)

    @field_validator("nome")
    @classmethod
    def validate_nome(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return safe_nome(v, field_name="nome")

    @field_validator("lesoes_cuidados")
    @classmethod
    def validate_lesoes(cls, v: str | None) -> str | None:
        return safe_lesoes(v)

    @field_validator("objetivo")
    @classmethod
    def validate_objetivo(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if v in _OBJETIVO_ENUM_VALUES:
            return v
        return safe_item_nome(v)

    @field_validator("local_treino")
    @classmethod
    def validate_local_treino(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if v in _LOCAL_ENUM_VALUES:
            return v
        return safe_item_nome(v)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    username: str | None = None
