from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class CatalogoExercicioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    grupo_muscular: Optional[str] = None
    descricao: Optional[str] = None
    video_url: Optional[str] = None


class PaginatedCatalogoExerciciosResponse(BaseModel):
    itens: List[CatalogoExercicioResponse]
    total: int
    pagina: int
    limite: int
    paginas: int


class CatalogoRefeicaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    tipo: Optional[str] = None
    nivel: Optional[str] = None
    ingredientes: Optional[List[str]] = None
    custo_estimado: Optional[str] = None
    explicacao: Optional[str] = None
    calorias: Optional[int] = None
    proteina_g: Optional[float] = None
    carboidrato_g: Optional[float] = None
    gordura_g: Optional[float] = None
    macros_estimados: bool = True


class PaginatedCatalogoRefeicoesResponse(BaseModel):
    itens: List[CatalogoRefeicaoResponse]
    total: int
    pagina: int
    limite: int
    paginas: int
