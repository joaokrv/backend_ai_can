# app/api/v1/endpoints/treino.py
# Rotas de sugestão (o coração da aplicação)

from fastapi import APIRouter, HTTPException, status
from app.api.schemas.sugestao import SugestaoCreate
from app.services.ia_agent import generate_training_plan
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Gerar plano de treino personalizado",
    description="Recebe dados do usuário e gera plano de treino com IA"
)
async def obter_sugestao(dados: SugestaoCreate):
    try:
        logger.info(
            f"Gerando plano para {dados.nome}: "
            f"{dados.idade}a, {dados.peso}kg, {dados.altura}cm, "
            f"{dados.disponibilidade}x/sem, {dados.local.value}, {dados.objetivo.value}"
        )
        
        plano = generate_training_plan(
            nome=dados.nome,
            altura=dados.altura,
            peso=dados.peso,
            idade=dados.idade,
            disponibilidade=dados.disponibilidade,
            local=dados.local.value,
            objetivo=dados.objetivo.value
        )
        
        logger.info(f"Plano gerado com sucesso para {dados.nome}")
        
        return {
            "plano": plano,
            "status": "sucesso",
            "mensagem": f"Plano '{plano.get('nome_da_rotina')}' criado para {dados.nome}"
        }
        
    except ValueError as e:
        logger.warning(f"Validação falhou: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao processar requisição: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao processar requisição. Tente novamente."
        )
